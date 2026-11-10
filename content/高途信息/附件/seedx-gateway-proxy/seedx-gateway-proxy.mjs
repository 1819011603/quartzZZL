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
import { loadConfig, ensureLocalToken } from "./config.mjs";

const ENV = process.env;
const CFG = loadConfig();
const PREFIX_RESOURCE = ENV.SEEDX_PREFIX_RESOURCE ?? "/seedx/resource/manage/service";
const REFRESH_PATH = `${PREFIX_RESOURCE}/ctl/gateway-token/refresh`;
const PREFIX_IDENTITY = ENV.SEEDX_PREFIX_IDENTITY ?? "/seedx/identity/manage/service";
const PROXY_HOST = CFG.proxyHost;
const PROXY_PORT = CFG.proxyPort; // claude / Anthropic 协议
const CODEX_PORT = CFG.codexPort; // codex / OpenAI 协议
const LOCAL_TOKEN = ensureLocalToken(); // 本地鉴权：客户端凭据必须等于它
const LEGACY_TOKEN = "seedx-local-proxy"; // 兼容老配置的占位值
const ALLOW_LEGACY = CFG.allowLegacyToken !== false;
const CONNECT_TIMEOUT_MS = Math.max(1, Number(CFG.upstreamConnectTimeoutSec ?? 15)) * 1000;
const IDLE_TIMEOUT_MS = Math.max(5, Number(CFG.upstreamIdleTimeoutSec ?? 180)) * 1000;
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

const CRED_PATH = CFG.credentialsPath || join(homedir(), ".seedx-workspace", "credentials.json");

/** 每次现读 seed 登录长票：在别处重登 / credentials.json 被更新时自动拉到新值（对齐 seedx gateway-acquire）。 */
function readSeed() {
  if (CFG.seedToken) return { token: CFG.seedToken, serverUrl: CFG.serverUrl };
  try {
    const c = JSON.parse(readFileSync(CRED_PATH, "utf8"));
    return { token: c.token, serverUrl: CFG.serverUrl || c.serverUrl };
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

/** 取客户端凭据：Authorization: Bearer 或 x-api-key。 */
function clientCredential(req) {
  const m = /^bearer\s+(.+)$/i.exec(String(req.headers["authorization"] || ""));
  if (m) return m[1].trim();
  const xk = req.headers["x-api-key"];
  return typeof xk === "string" ? xk.trim() : "";
}

function sendUpstream(target, method, headers, body) {
  return new Promise((resolve, reject) => {
    const isHttps = target.protocol === "https:";
    const make = isHttps ? httpsRequest : httpRequest;
    let settled = false;
    const req = make(target, { method, headers, agent: isHttps ? httpsAgent : httpAgent }, (res) => {
      settled = true;
      clearTimeout(connectTimer);
      resolve({ res, req });
    });
    // 建连/首字节超时：拿不到响应头就中止，避免死等（keep-alive 死连接、换网卡住）
    const connectTimer = setTimeout(() => {
      if (!settled) req.destroy(new Error(`上游 ${CONNECT_TIMEOUT_MS}ms 无响应`));
    }, CONNECT_TIMEOUT_MS);
    // 收到响应后的空闲超时：两次数据间隔过久也中止（SSE 正常会不断有数据）
    req.setTimeout(IDLE_TIMEOUT_MS, () => req.destroy(new Error(`上游 ${IDLE_TIMEOUT_MS}ms 空闲超时`)));
    req.once("error", (e) => {
      clearTimeout(connectTimer);
      if (!settled) reject(e);
    });
    req.end(body);
  });
}

/** 端口默认协议 + 路径协议标记的兼容：老配置里 codex 会打 8787 的 /responses。 */
function resolveWhich(portDefault, pathname) {
  if (pathname.startsWith("/v1/messages")) return "anthropic";
  if (/(^|\/)responses$/.test(pathname) || /\/chat\/completions$/.test(pathname)) return "openai";
  return portDefault;
}

function makeHandler(portDefault) {
  return async function handle(req, res) {
    const pathname = new URL(req.url, "http://x").pathname;
    const which = resolveWhich(portDefault, pathname);
    // 本地鉴权：凭据须等于 localToken；兼容期内也认老占位值
    const cred = clientCredential(req);
    const authed = cred === LOCAL_TOKEN || (ALLOW_LEGACY && cred === LEGACY_TOKEN);
    if (LOCAL_TOKEN && !authed) {
      res.writeHead(401, { "content-type": "application/json" });
      res.end(
        JSON.stringify({ type: "error", error: { type: "seedx_local_unauthorized", message: "本地代理凭据不正确（见面板 localToken）" } }),
      );
      return;
    }

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
        JSON.stringify({ type: "error", error: { type: "seedx_gateway_unavailable", message: "拿不到网关授权：请检查 seed 长票是否有效" } }),
      );
      return;
    }

    const baseFor = (t) => (which === "anthropic" ? t.anthropicBaseUrl : t.openaiBaseUrl);
    const buildHeaders = (t) => {
      const out = {};
      const injectedLower = t.headerName.toLowerCase();
      for (const [k, v] of Object.entries(req.headers)) {
        if (v === undefined) continue;
        const lk = k.toLowerCase();
        if (STRIPPED_REQUEST_HEADERS.has(lk) || lk === injectedLower || lk.startsWith("x-seedx-")) continue;
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
      return sendUpstream(new URL(baseFor(t) + path), req.method ?? "POST", buildHeaders(t), body);
    };

    let a;
    try {
      a = await attempt(token);
      if (a.res.statusCode === 401) {
        a.res.resume();
        const fresh = await refreshGatewayToken();
        if (fresh && fresh.token !== token.token) {
          token = fresh;
          a = await attempt(fresh);
        }
      }
    } catch (e) {
      const code = /超时/.test(e.message) ? 504 : 502;
      res.writeHead(code, { "content-type": "application/json" });
      res.end(JSON.stringify({ type: "error", error: { type: "seedx_gateway_unreachable", message: String(e.message) } }));
      return;
    }

    const { res: up } = a;
    log(`[req] ${which} ${req.method} ${pathname} -> ${up.statusCode}`);
    const outHeaders = {};
    for (const [k, v] of Object.entries(up.headers)) {
      if (v === undefined || STRIPPED_RESPONSE_HEADERS.has(k.toLowerCase())) continue;
      outHeaders[k] = v;
    }
    res.writeHead(up.statusCode ?? 502, outHeaders);
    res.flushHeaders?.();
    up.on("error", () => {
      if (!res.writableEnded) res.destroy();
    });
    res.on("close", () => up.destroy());
    up.pipe(res);
  };
}

function listen(port, which) {
  const server = createServer((req, res) => {
    void makeHandler(which)(req, res).catch((e) => {
      log(`代理异常(${which}): ${e.message}`);
      if (!res.headersSent) res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: String(e.message) }));
    });
  });
  server.on("error", (e) => {
    log(`监听 ${port} 失败：${e.code || e.message}（端口被占用或非法）`);
    process.exit(1); // 交给 supervisor 退避重启，不再静默死循环
  });
  server.listen(port, PROXY_HOST, () => log(`监听 http://${PROXY_HOST}:${port}（${which}）`));
}

function main() {
  log(`seed 服务端: ${SERVER_URL}；本地鉴权 token=${LOCAL_TOKEN.slice(0, 8)}…`);
  // 两个协议端口；相同则只监听一次（单端口），靠路径识别
  const listeners = [{ port: PROXY_PORT, which: "anthropic" }];
  if (CODEX_PORT !== PROXY_PORT) listeners.push({ port: CODEX_PORT, which: "openai" });
  for (const l of listeners) listen(l.port, l.which);
  log(`监听：${listeners.map((l) => `${l.port}(${l.which})`).join("、")}`);
  void checkLongTicket();
  refreshGatewayToken();
  const timer = setInterval(() => {
    if (tokenExpiringSoon()) void refreshGatewayToken();
  }, 60_000);
  timer.unref?.();
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
