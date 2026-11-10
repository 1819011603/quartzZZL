#!/usr/bin/env node
/**
 * seedx-gateway-proxy —— 独立版 AI Coding 网关代理（跨平台，Node >= 18，无第三方依赖）。
 *
 * 目的：不依赖 seedx daemon / skills / 流程，复刻 seedx 的“取网关授权 + 本地注入”链路，
 * 让 claude / codex 走 AI Coding 网关（ai-coding.baijia.com），凭据由本代理自动刷新。
 *
 * 原理（对齐 seedx shared/gateway-token.ts + shared/agent-proxy.ts）：
 *   1. 用「seed 登录长票」POST /seedx/resource/manage/service/ctl/gateway-token/refresh，
 *      拿到网关授权 { token(act.…), expiresAt, headerName, anthropicBaseUrl, openaiBaseUrl }；
 *   2. 本地起 HTTP 服务，把 claude/codex 的请求剥掉自带凭据、注入 headerName=token，
 *      流式转发到对应上游 base（claude→anthropicBaseUrl，codex→openaiBaseUrl）；
 *   3. 授权将过期或上游回 401 时自动刷新一次再重试。
 *
 * 用法：
 *   SEEDX_TOKEN=<seed登录长票> node seedx-gateway-proxy.mjs
 *   # 或让它读 seedx 的凭据文件（默认 ~/.seedx-workspace/credentials.json）：
 *   node seedx-gateway-proxy.mjs
 *
 *   node seedx-gateway-proxy.mjs --check   # 只取一次授权并打印，不起服务（自检用）
 *
 * 环境变量：
 *   SEEDX_TOKEN           seed 登录长票（不给则读 credentials 文件）
 *   SEEDX_CREDENTIALS     credentials.json 路径（默认 ~/.seedx-workspace/credentials.json）
 *   SEEDX_SERVER_URL      seed 服务端（默认取 credentials.serverUrl，否则 https://seed.baijia.com）
 *   SEEDX_PREFIX_RESOURCE 资源服务前缀（默认 /seedx/resource/manage/service）
 *   SEEDX_PROXY_HOST      监听地址（默认 127.0.0.1）
 *   SEEDX_PROXY_PORT      监听端口（默认 8787）
 *   SEEDX_REFRESH_AHEAD_S 提前多少秒刷新（默认 300）
 *
 * cc-switch / claude / codex 指向本代理（token 填任意非空占位，真凭据由代理注入）：
 *   claude: ANTHROPIC_BASE_URL=http://127.0.0.1:8787   ANTHROPIC_AUTH_TOKEN=seedx-local-proxy
 *   codex : base_url=http://127.0.0.1:8787 (wire_api=responses)   OPENAI_API_KEY=seedx-local-proxy
 * 单端口按路径路由：/v1/messages* → anthropic；其余 → openai。
 * 需要强制指定时加请求头 x-seedx-upstream: anthropic | openai。
 */

import { createServer, request as httpRequest, Agent as HttpAgent } from "node:http";
import { request as httpsRequest, Agent as HttpsAgent } from "node:https";
import { readFileSync, writeFileSync, mkdirSync, renameSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const ENV = process.env;
const PREFIX_RESOURCE = ENV.SEEDX_PREFIX_RESOURCE ?? "/seedx/resource/manage/service";
const REFRESH_PATH = `${PREFIX_RESOURCE}/ctl/gateway-token/refresh`;
const PREFIX_IDENTITY = ENV.SEEDX_PREFIX_IDENTITY ?? "/seedx/identity/manage/service";
const PROXY_HOST = ENV.SEEDX_PROXY_HOST ?? "127.0.0.1";
const PROXY_PORT = Number(ENV.SEEDX_PROXY_PORT ?? 8787);
const REFRESH_AHEAD_S = Number(ENV.SEEDX_REFRESH_AHEAD_S ?? 300);
const REFRESH_TIMEOUT_MS = 10_000;
const MAX_BODY_BYTES = 64 * 1024 * 1024;

// 网关授权落盘缓存：重启不丢、resource 暂时不可用时仍可续用（对齐 seedx gateway-token-cache）。
const CACHE_PATH = ENV.SEEDX_TOKEN_CACHE || join(homedir(), ".seedx-gateway-proxy", "token.json");

function loadCachedGateway() {
  try {
    const t = JSON.parse(readFileSync(CACHE_PATH, "utf8"));
    if (t && typeof t.token === "string" && t.token) return t;
  } catch {
    /* 无缓存 */
  }
  return undefined;
}

function saveCachedGateway(t) {
  try {
    mkdirSync(join(homedir(), ".seedx-gateway-proxy"), { recursive: true });
    const tmp = `${CACHE_PATH}.tmp`;
    writeFileSync(tmp, JSON.stringify(t, null, 2), { encoding: "utf8", mode: 0o600 });
    renameSync(tmp, CACHE_PATH);
  } catch {
    /* 缓存写失败不影响主流程 */
  }
}

// 剥掉客户端自带凭据/连接级头，凭据由代理注入（与 seedx agent-proxy 同口径）。
const STRIPPED_REQUEST_HEADERS = new Set([
  "authorization",
  "x-api-key",
  "x-seed-credential",
  "proxy-authorization",
  "host",
  "content-length",
  "connection",
  "transfer-encoding",
  "expect",
  "keep-alive",
]);
const STRIPPED_RESPONSE_HEADERS = new Set(["connection", "keep-alive", "transfer-encoding"]);

function log(...a) {
  console.log(new Date().toISOString(), ...a);
}

const CRED_PATH = ENV.SEEDX_CREDENTIALS || join(homedir(), ".seedx-workspace", "credentials.json");

/** 每次现读 seed 登录长票：在别处重登 / credentials.json 被更新时自动拉到新值（对齐 seedx gateway-acquire）。 */
function readSeed() {
  if (ENV.SEEDX_TOKEN) return { token: ENV.SEEDX_TOKEN, serverUrl: ENV.SEEDX_SERVER_URL };
  try {
    const c = JSON.parse(readFileSync(CRED_PATH, "utf8"));
    return { token: c.token, serverUrl: c.serverUrl || ENV.SEEDX_SERVER_URL };
  } catch (e) {
    return { error: `无法读取 seed 凭据（${CRED_PATH}）：${e.message}` };
  }
}

const seed0 = readSeed();
if (seed0.error || !seed0.token) {
  log(seed0.error || "seed 凭据缺 token");
  log("请设置 SEEDX_TOKEN，或把 seedx 的 credentials.json 放到该路径。");
  process.exit(2);
}
const SERVER_URL = (seed0.serverUrl || "https://seed.baijia.com").replace(/\/+$/, "");

// ── 网关授权：持有 + single-flight 刷新 ───────────────────────────────
let gateway = loadCachedGateway(); // { token, expiresAt, headerName, anthropicBaseUrl, openaiBaseUrl }
let inflight = undefined;
if (gateway) log(`已加载落盘缓存授权 token=${gateway.token.slice(0, 12)}… 过期=${gateway.expiresAt}`);

/** 校验 seed 登录长票是否仍被服务端认可（401 = 失效）；失败只告警，不阻断。 */
async function checkLongTicket() {
  try {
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), REFRESH_TIMEOUT_MS);
    const res = await fetch(`${SERVER_URL}${PREFIX_IDENTITY}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${readSeed().token}` },
      signal: ac.signal,
    }).finally(() => clearTimeout(timer));
    if (res.status === 401) log("⚠️ seed 登录长票已失效（/auth/me 401）：请重新登录 seed 后更新 SEEDX_TOKEN/credentials.json");
    else log(`seed 登录长票校验：HTTP ${res.status}`);
  } catch (e) {
    log(`seed 登录长票校验跳过（${e.message}）`);
  }
}

async function fetchGatewayToken() {
  const url = `${SERVER_URL}${REFRESH_PATH}`;
  const tok = readSeed().token; // 每次刷新都现读，长票换了自动跟上
  if (!tok) throw new Error("seed 凭据缺 token（credentials.json 未登录？）");
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), REFRESH_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { Authorization: `Bearer ${tok}`, "content-type": "application/json" },
      body: "{}",
      signal: ac.signal,
    });
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${body.slice(0, 200)}`);
    }
    const t = await res.json();
    for (const k of ["token", "headerName", "expiresAt", "anthropicBaseUrl", "openaiBaseUrl"]) {
      if (typeof t[k] !== "string" || t[k].trim() === "") throw new Error(`回包缺字段 ${k}`);
    }
    return {
      token: t.token,
      headerName: t.headerName,
      expiresAt: t.expiresAt,
      anthropicBaseUrl: t.anthropicBaseUrl.replace(/\/+$/, ""),
      openaiBaseUrl: t.openaiBaseUrl.replace(/\/+$/, ""),
      issuedAt: t.issuedAt || "",
    };
  } finally {
    clearTimeout(timer);
  }
}

function refreshGatewayToken() {
  if (inflight) return inflight;
  inflight = (async () => {
    try {
      const t = await fetchGatewayToken();
      gateway = t;
      saveCachedGateway(t);
      log(`网关授权已更新 token=${t.token.slice(0, 12)}… header=${t.headerName} 过期=${t.expiresAt}`);
      return t;
    } catch (e) {
      if (gateway) log(`刷新网关授权失败：${e.message}（沿用缓存授权，到期=${gateway.expiresAt}）`);
      else log(`刷新网关授权失败：${e.message}（无可用授权）`);
      return undefined;
    } finally {
      inflight = undefined;
    }
  })();
  return inflight;
}

function tokenExpiringSoon() {
  if (!gateway) return true;
  const t = Date.parse(gateway.expiresAt);
  return Number.isFinite(t) && t - Date.now() < REFRESH_AHEAD_S * 1000;
}

async function currentGatewayToken() {
  if (tokenExpiringSoon()) {
    const fresh = await refreshGatewayToken();
    if (fresh) return fresh;
  }
  return gateway;
}

// ── 本地代理 ─────────────────────────────────────────────────────────
const httpAgent = new HttpAgent({ keepAlive: true });
const httpsAgent = new HttpsAgent({ keepAlive: true });

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on("data", (c) => {
      size += c.length;
      if (size > MAX_BODY_BYTES) {
        reject(new Error("payload too large"));
        req.destroy();
        return;
      }
      chunks.push(c);
    });
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

function pickUpstream(pathname, headerOverride) {
  if (headerOverride === "anthropic" || headerOverride === "openai") return headerOverride;
  return pathname.startsWith("/v1/messages") ? "anthropic" : "openai";
}

function sendUpstream(target, method, headers, body) {
  return new Promise((resolve, reject) => {
    const isHttps = target.protocol === "https:";
    const make = isHttps ? httpsRequest : httpRequest;
    const req = make(target, { method, headers, agent: isHttps ? httpsAgent : httpAgent }, (res) =>
      resolve({ res, req }),
    );
    req.once("error", reject);
    req.end(body);
  });
}

async function handle(req, res) {
  let body;
  try {
    body = await readBody(req);
  } catch (e) {
    res.writeHead(413, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: e.message }));
    return;
  }

  let token = gateway;
  if (tokenExpiringSoon()) token = (await currentGatewayToken()) ?? gateway;
  if (!token) {
    res.writeHead(503, { "content-type": "application/json" });
    res.end(
      JSON.stringify({
        type: "error",
        error: { type: "seedx_gateway_unavailable", message: "拿不到网关授权：请检查 seed 长票是否有效" },
      }),
    );
    return;
  }

  const parsed = new URL(req.url, "http://localhost");
  const which = pickUpstream(parsed.pathname, String(req.headers["x-seedx-upstream"] || "").toLowerCase());
  const base = which === "anthropic" ? token.anthropicBaseUrl : token.openaiBaseUrl;

  const buildHeaders = (t) => {
    const out = {};
    const injectedLower = t.headerName.toLowerCase();
    for (const [k, v] of Object.entries(req.headers)) {
      if (v === undefined) continue;
      const lk = k.toLowerCase();
      if (STRIPPED_REQUEST_HEADERS.has(lk) || lk === injectedLower) continue;
      out[k] = v;
    }
    out[t.headerName] = t.token;
    out["content-length"] = String(body.length);
    return out;
  };

  const attempt = async (t) => {
    // openai base 已含 /v1：客户端若也带 /v1 前缀就剥掉，避免 /v1/v1；anthropic base 不含 /v1，原样拼。
    let path = req.url;
    if (which === "openai" && path.startsWith("/v1/")) path = path.slice(3);
    const target = new URL(base + path);
    return sendUpstream(target, req.method ?? "POST", buildHeaders(t), body);
  };

  let a;
  try {
    a = await attempt(token);
    if (a.res.statusCode === 401) {
      a.res.resume();
      const fresh = await refreshGatewayToken();
      if (fresh && fresh.token !== token.token) a = await attempt(fresh);
    }
  } catch (e) {
    res.writeHead(502, { "content-type": "application/json" });
    res.end(JSON.stringify({ type: "error", error: { type: "seedx_gateway_unreachable", message: String(e.message) } }));
    return;
  }

  const { res: up } = a;
  log(`[req] ${req.method} ${parsed.pathname} -> ${which} ${up.statusCode}${req.headers["x-seedx-upstream"] ? " (forced)" : ""}`);
  const outHeaders = {};
  for (const [k, v] of Object.entries(up.headers)) {
    if (v === undefined || STRIPPED_RESPONSE_HEADERS.has(k.toLowerCase())) continue;
    outHeaders[k] = v;
  }
  res.writeHead(up.statusCode ?? 502, outHeaders);
  res.flushHeaders?.();
  up.pipe(res);
}

function main() {
  const server = createServer((req, res) => {
    void handle(req, res).catch((e) => {
      log("代理异常", e);
      if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: String(e.message) }));
    });
  });
  server.listen(PROXY_PORT, PROXY_HOST, () => {
    log(`seedx-gateway-proxy 监听 http://${PROXY_HOST}:${PROXY_PORT}`);
    log(`seed 服务端: ${SERVER_URL}`);
    log("cc-switch 指向本地址即可（token 填任意占位，如 seedx-local-proxy）。Ctrl+C 退出。");
    void checkLongTicket();
    refreshGatewayToken();
    // 定时刷新：距过期 < REFRESH_AHEAD_S 就续一次，即使没请求也保持有效
    const timer = setInterval(() => {
      if (tokenExpiringSoon()) void refreshGatewayToken();
    }, 60_000);
    timer.unref?.();
  });
}

if (ENV.SEEDX_CHECK === "1" || process.argv.includes("--check")) {
  const t = await fetchGatewayToken().catch((e) => {
    log("取授权失败:", e.message);
    process.exit(1);
  });
  console.log(JSON.stringify({ serverUrl: SERVER_URL, ...t, token: t.token.slice(0, 20) + "…" }, null, 2));
} else {
  main();
}
