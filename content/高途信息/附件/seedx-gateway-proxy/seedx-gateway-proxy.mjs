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
import { execFile } from "node:child_process";
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
const REFRESH_AHEAD_S = Number(ENV.SEEDX_REFRESH_AHEAD_S ?? CFG.refreshAheadSec ?? 300);
const REFRESH_TIMEOUT_MS = 10_000;
const MAX_BODY_BYTES = 64 * 1024 * 1024;

// ── claude 额度用尽 → 自动改用 codex(gpt) 模型 ──────────────────────
// 网关支持在 claude(anthropic) 协议下用 codex 的 gpt 模型（额度计到 gpt 策略）。
// 开启后：轮询「个人额度」，claude 策略用尽时把 anthropic 请求的 model 改写成 fallbackCodexModel。
const FALLBACK_ON = CFG.claudeFallbackCodex === true;
const FALLBACK_MODEL = String(CFG.fallbackCodexModel || "gpt-6.1-sol");
const FALLBACK_MAP = CFG.fallbackCodexMap && typeof CFG.fallbackCodexMap === "object" ? CFG.fallbackCodexMap : {};
const FALLBACK_ACTIVE = FALLBACK_ON || CFG.claudeForceCodex === true; // 自动(用尽) 或 手动强制 任一生效即接管
const FORCE_CODEX = CFG.claudeForceCodex === true; // 手动切换：claude 一律改走 codex(gpt)
const QUOTA_URL = String(CFG.quotaUrl || "");
const QUOTA_PROXY = String(CFG.quotaProxy || "");
const QUOTA_INTERVAL_MS = Math.max(15, Number(CFG.quotaCheckSec ?? 60)) * 1000;
let quota = { at: 0, ok: false, remainingUsd: null, usageRatio: null, limitUsd: null, spentUsd: null, resetAt: null };

/** 经本地 mitmproxy（注入 Cookie）取一次个人额度；失败返回 null。 */
function fetchQuotaOnce() {
  return new Promise((resolve) => {
    if (!QUOTA_URL) return resolve(null);
    const args = ["-sk", "--max-time", "15"];
    if (QUOTA_PROXY) args.push("-x", QUOTA_PROXY);
    args.push(QUOTA_URL,
      "-H", "accept: */*", "-H", "content-type: application/json",
      "-H", "ingress-traffic-env: test-gtbg-dev-3", "-H", "traffic-env: test-eco-7");
    execFile("curl", args, { maxBuffer: 4 * 1024 * 1024 }, (err, stdout) => {
      if (err) return resolve(null);
      try { resolve(JSON.parse(stdout)); } catch { resolve(null); }
    });
  });
}

async function refreshQuota() {
  const q = await fetchQuotaOnce();
  if (!q || !Array.isArray(q.policies)) { quota.at = Date.now(); return; }
  const cl = q.policies.find((p) => p.policy === "claude" || /claude/i.test(String(p.name || "")));
  if (!cl) { quota.at = Date.now(); return; }
  quota = {
    at: Date.now(), ok: true,
    remainingUsd: typeof cl.remaining_usd === "number" ? cl.remaining_usd : null,
    usageRatio: typeof cl.usage_ratio === "number" ? cl.usage_ratio : null,
    limitUsd: typeof cl.limit_usd === "number" ? cl.limit_usd : null,
    spentUsd: typeof cl.spent_usd === "number" ? cl.spent_usd : null,
    resetAt: (q.period && q.period.reset_at) || null,
  };
  log(`[quota] claude 剩 $${quota.remainingUsd ?? "?"}/$${quota.limitUsd ?? "?"}（用量 ${((quota.usageRatio ?? 0) * 100).toFixed(1)}%），窗口重置 ${quota.resetAt || "?"}`);
}

/** claude 是否该切到 codex(gpt)：额度用尽（remaining<=0 或 ratio>=1）；额度未知返回 false。 */
function claudeShouldFallback() {
  if (!quota.ok) return false;
  if (quota.remainingUsd != null) return quota.remainingUsd <= 0;
  if (quota.usageRatio != null) return quota.usageRatio >= 1;
  return false;
}

/** claude 模型 → 目标 codex(gpt) 模型：精确名优先，其次按关键词（opus/sonnet…），最后默认。 */
function resolveFallbackModel(model) {
  if (typeof FALLBACK_MAP[model] === "string") return FALLBACK_MAP[model];
  const lower = String(model).toLowerCase();
  for (const [k, v] of Object.entries(FALLBACK_MAP)) {
    if (typeof v === "string" && k && lower.includes(String(k).toLowerCase())) return v;
  }
  return FALLBACK_MODEL;
}

/** anthropic 请求体里 model 是 claude-* → 改写成映射的 codex 模型，返回新 body 或 null。
 *  requireExhausted=true：仅在「轮询判定 claude 已用尽」时改写（请求前置）；
 *  requireExhausted=false：无条件改写（用于「请求真撞到额度错误」时的反应式回退重试）。 */
function rewriteToCodex(buf, requireExhausted) {
  if (!FALLBACK_ACTIVE || !buf || !buf.length) return null;
  let obj;
  try { obj = JSON.parse(buf.toString("utf8")); } catch { return null; }
  if (!obj || typeof obj.model !== "string" || !/^claude/i.test(obj.model)) return null;
  if (requireExhausted && !FORCE_CODEX && !claudeShouldFallback()) return null;
  const from = obj.model;
  obj.model = resolveFallbackModel(from);
  log(`[fallback] 模型 ${from} → ${obj.model}（改走 gpt/codex 额度）`);
  return Buffer.from(JSON.stringify(obj), "utf8");
}

/** 请求前置：claude 额度已用尽 → 改写为 codex 模型（避免请求先失败）。 */
function maybeRewriteToCodex(buf) {
  return rewriteToCodex(buf, true);
}

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

    // claude 额度用尽 → 自动把 claude-* 请求改写成 codex(gpt) 模型（网关支持 claude 协议调 gpt）。
    if (which === "anthropic" && CFG.claudeUpstream !== "llm") {
      const rewritten = maybeRewriteToCodex(body);
      if (rewritten) body = rewritten;
    }
    let usedFallback = false; // 反应式回退：请求撞到额度错误时改写成 gpt 重试，只用一次

    // claude 上游切换：claudeUpstream=llm 时，claude(anthropic) 直连 llm 网关，
    // 用配置里的凭据，不经过 seedx 网关（也不消耗 seedx 授权）。
    const useLlmClaude = which === "anthropic" && CFG.claudeUpstream === "llm";
    let token;
    if (useLlmClaude) {
      if (!CFG.llmClaudeToken) {
        res.writeHead(503, { "content-type": "application/json" });
        res.end(
          JSON.stringify({ type: "error", error: { type: "seedx_llm_claude_unconfigured", message: "claude 上游已切到 llm，但未配置 llmClaudeToken" } }),
        );
        return;
      }
      const llmBase = String(CFG.llmClaudeBaseUrl || "").replace(/\/+$/, "");
      token = {
        headerName: CFG.llmClaudeHeaderName || "x-api-key",
        token: CFG.llmClaudeToken,
        anthropicBaseUrl: llmBase,
        openaiBaseUrl: llmBase,
      };
    } else {
      token = gateway;
      if (tokenExpiringSoon()) token = (await currentGatewayToken()) ?? gateway;
      if (!token) {
        res.writeHead(503, { "content-type": "application/json" });
        res.end(
          JSON.stringify({ type: "error", error: { type: "seedx_gateway_unavailable", message: "拿不到网关授权：请检查 seed 长票是否有效" } }),
        );
        return;
      }
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
      out[t.headerName] = /^authorization$/i.test(t.headerName) ? `Bearer ${t.token}` : t.token;
      // llm 网关的 anthropic 端点需要版本头（客户端没带就补上）
      if (useLlmClaude && !out["anthropic-version"]) out["anthropic-version"] = CFG.llmClaudeAnthropicVersion || "2023-06-01";
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
      // 401/403 都当"授权/权限类"：可能是 token 过期或权限态变化 → 刷新一次重试
      // （llm 直连模式不刷新 seedx 授权，原样返回上游错误）
      if (!useLlmClaude && (a.res.statusCode === 401 || a.res.statusCode === 403)) {
        const code0 = a.res.statusCode;
        a.res.resume();
        const fresh = await refreshGatewayToken();
        if (fresh && fresh.token !== token.token) {
          token = fresh;
          a = await attempt(fresh);
        } else if (code0 === 403) {
          log(`[warn] 上游 403（授权未变）：疑似无权限/无订阅（如 SUBSCRIPTION_NOT_FOUND），原样返回`);
        }
      }
      // 反应式回退：claude 请求撞到额度/权限类错误（如 429 限流、402/403 额度不足）时，
      // 即使轮询还没判定用尽，也改写为 gpt 模型再试一次（网关支持 claude 协议调 gpt 模型）。
      if (
        which === "anthropic" &&
        FALLBACK_ON &&
        !useLlmClaude &&
        !usedFallback &&
        (a.res.statusCode === 402 || a.res.statusCode === 403 || a.res.statusCode === 429)
      ) {
        const forced = rewriteToCodex(body, false);
        if (forced) {
          a.res.resume();
          body = forced;
          usedFallback = true;
          log(`[fallback] 上游 ${a.res.statusCode} → 改写为 gpt 重试（claude 额度/权限受限）`);
          a = await attempt(token);
        }
      }
    } catch (e) {
      const code = /超时/.test(e.message) ? 504 : 502;
      res.writeHead(code, { "content-type": "application/json" });
      res.end(JSON.stringify({ type: "error", error: { type: "seedx_gateway_unreachable", message: String(e.message) } }));
      return;
    }

    const { res: up } = a;
    const hint =
      up.statusCode === 401 ? "（上游 401：授权无效/已过期）" : up.statusCode === 403 ? "（上游 403：无权限/无订阅）" : "";
    log(`[req] ${which} ${req.method} ${pathname} -> ${up.statusCode}${hint}`);
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
  if (FALLBACK_ON || FORCE_CODEX) {
    if (FALLBACK_ON) {
      void refreshQuota();
      const qt = setInterval(() => void refreshQuota(), QUOTA_INTERVAL_MS);
      qt.unref?.();
    }
    log(
      `claude→codex(gpt) 已启用：改写目标 ${FALLBACK_MODEL}` +
        (FALLBACK_ON ? `；额度用尽自动切（每 ${QUOTA_INTERVAL_MS / 1000}s 查额度）` : "") +
        (FORCE_CODEX ? "；**手动切换已开：claude 一律走 gpt（忽略额度）**" : ""),
    );
  }
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
