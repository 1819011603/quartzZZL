#!/usr/bin/env node
/**
 * start.mjs —— seedx 网关代理的一键启动 + 控制面板。
 *
 * 双击 Seedx网关.app（或 `node start.mjs`）即可：
 *   - 常驻拉起「代理 seedx-gateway-proxy.mjs」和「cc-switch 同步 sync-ccswitch.mjs --watch」；
 *   - 在本地控制面板 http://127.0.0.1:<controlPort>（默认 8790）里改设置、看状态/日志、启停重启；
 *   - 任一子进程挂了自动重启。
 *
 * 设置存在 ~/.seedx-gateway-proxy/config.json（见 config.mjs）；env 可覆盖。
 * 命令行仍可 `node start.mjs --headless`（不起面板，纯常驻）。
 */

import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { readFileSync, existsSync } from "node:fs";
import { randomBytes } from "node:crypto";
import { loadConfig, saveConfig, CONFIG_PATH, HOME_DIR, proxyUrl, ensureLocalToken } from "./config.mjs";

const DIR = dirname(fileURLToPath(import.meta.url));
const HEADLESS = process.argv.includes("--headless");
const PREFIX_IDENTITY = process.env.SEEDX_PREFIX_IDENTITY ?? "/seedx/identity/manage/service";
const PANEL_NONCE = randomBytes(16).toString("hex"); // 面板本地会话 nonce（挡跨站请求）

let shuttingDown = false;
const children = new Map(); // name -> { child, restarts, startedAt, spec }
const logs = [];
const LOG_CAP = 800;

function nowIso() {
  return new Date().toISOString();
}

function pushLog(tag, text) {
  for (const line of String(text).split("\n")) {
    if (line === "") continue;
    logs.push({ ts: nowIso(), tag, line });
  }
  if (logs.length > LOG_CAP) logs.splice(0, logs.length - LOG_CAP);
}

function relay(name, stream) {
  let buf = "";
  stream.on("data", (d) => {
    buf += d.toString();
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i);
      buf = buf.slice(i + 1);
      pushLog(name, line);
      process.stdout.write(`[${name}] ${line}\n`);
    }
  });
  stream.on("end", () => {
    if (buf) pushLog(name, buf);
  });
}

function stopChild(name) {
  const rec = children.get(name);
  if (!rec) return;
  children.delete(name);
  try {
    rec.child.kill("SIGTERM");
  } catch {
    /* ignore */
  }
}

function startChild(name, file, args = []) {
  stopChild(name);
  const child = spawn(process.execPath, [join(DIR, file), ...args], {
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, NODE_NO_WARNINGS: "1" },
  });
  const rec = { child, restarts: 0, startedAt: Date.now(), spec: { name, file, args } };
  children.set(name, rec);
  relay(name, child.stdout);
  relay(name, child.stderr);
  child.on("error", (e) => pushLog(name, `启动失败: ${e.message}`));
  child.on("exit", (code, sig) => {
    const cur = children.get(name);
    if (shuttingDown || !cur || cur.child !== child) return;
    pushLog(name, `退出(code=${code ?? "-"}, signal=${sig ?? "-"})，将重启`);
    const quick = Date.now() - cur.startedAt < 5000;
    cur.restarts = quick ? cur.restarts + 1 : 0;
    const delay = Math.min(quick ? 3000 * 2 ** Math.min(cur.restarts, 3) : 3000, 30000);
    setTimeout(() => {
      if (!shuttingDown && children.get(name)?.child === child) {
        startChild(name, file, args);
      }
    }, delay);
  });
  return child;
}

/** 按配置确保两个子进程该在的在、不该在的不在（幂等）。 */
function ensureChildren() {
  const cfg = loadConfig();
  if (!children.has("proxy")) startChild("proxy", "seedx-gateway-proxy.mjs");
  if (cfg.syncCcSwitch) {
    if (!children.has("sync")) startChild("sync", "sync-ccswitch.mjs", ["--watch"]);
  } else {
    stopChild("sync");
  }
}

function restartAll() {
  stopChild("proxy");
  stopChild("sync");
  ensureChildren();
}

// ── 状态 ────────────────────────────────────────────────────────────
let ticketStatus = { checked: false, ok: null, status: null, at: null };

function gatewayStatus() {
  try {
    const t = JSON.parse(readFileSync(join(HOME_DIR, "token.json"), "utf8"));
    const ms = Date.parse(t.expiresAt) - Date.now();
    return {
      ok: true,
      headerName: t.headerName,
      expiresAt: t.expiresAt,
      secondsLeft: Math.round(ms / 1000),
      anthropicBaseUrl: t.anthropicBaseUrl,
      openaiBaseUrl: t.openaiBaseUrl,
    };
  } catch {
    return { ok: false };
  }
}

async function checkTicket() {
  const cfg = loadConfig();
  const credPath = cfg.credentialsPath || join(process.env.HOME || "", ".seedx-workspace", "credentials.json");
  let token = cfg.seedToken;
  let server = cfg.serverUrl;
  if (!token) {
    try {
      const c = JSON.parse(readFileSync(credPath, "utf8"));
      token = c.token;
      server = server || c.serverUrl;
    } catch (e) {
      ticketStatus = { checked: true, ok: false, status: `读不到凭据：${e.message}`, at: nowIso() };
      return ticketStatus;
    }
  }
  server = (server || "https://seed.baijia.com").replace(/\/+$/, "");
  if (!token) {
    ticketStatus = { checked: true, ok: false, status: "凭据缺 token", at: nowIso() };
    return ticketStatus;
  }
  try {
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), 8000);
    const res = await fetch(`${server}${PREFIX_IDENTITY}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: ac.signal,
    }).finally(() => clearTimeout(timer));
    ticketStatus = {
      checked: true,
      ok: res.status !== 401,
      status: res.status === 401 ? "已失效（需重新登录 seed）" : `有效（HTTP ${res.status}）`,
      at: nowIso(),
    };
  } catch (e) {
    ticketStatus = { checked: true, ok: null, status: `校验跳过（${e.message}）`, at: nowIso() };
  }
  return ticketStatus;
}

function statusPayload() {
  const cfg = loadConfig();
  const c = (name) => {
    const r = children.get(name);
    return r ? { running: true, pid: r.child.pid, restarts: r.restarts } : { running: false };
  };
  return {
    config: cfg,
    configPath: CONFIG_PATH,
    proxyUrl: proxyUrl(cfg),
    codexUrl: `http://${cfg.proxyHost}:${cfg.codexPort}`,
    localToken: ensureLocalToken(),
    gateway: gatewayStatus(),
    ticket: ticketStatus,
    proxy: c("proxy"),
    sync: c("sync"),
  };
}

// ── 控制服务器 ───────────────────────────────────────────────────────
function readBody(req) {
  return new Promise((resolve) => {
    let b = "";
    req.on("data", (d) => (b += d));
    req.on("end", () => resolve(b));
  });
}

const RESTART_PROXY_KEYS = ["proxyHost", "proxyPort", "codexPort", "credentialsPath", "seedToken", "serverUrl", "localToken", "upstreamConnectTimeoutSec", "upstreamIdleTimeoutSec"];
const RESTART_SYNC_KEYS = ["proxyHost", "proxyPort", "codexPort", "codexModel", "syncCcSwitch", "syncIntervalSec", "localToken"];

async function applyConfig(partial) {
  const before = loadConfig();
  saveConfig(partial);
  const after = loadConfig();
  const changed = (keys) => keys.some((k) => JSON.stringify(before[k]) !== JSON.stringify(after[k]));
  if (changed(RESTART_PROXY_KEYS)) stopChild("proxy");
  if (changed(RESTART_SYNC_KEYS)) stopChild("sync");
  ensureChildren(); // 按配置补齐（proxy 必起；sync 视 syncCcSwitch）
  return after;
}

function json(res, obj, code = 200) {
  const body = JSON.stringify(obj);
  res.writeHead(code, { "content-type": "application/json; charset=utf-8" });
  res.end(body);
}

function sameOriginOk(req) {
  const origin = req.headers["origin"];
  if (!origin) return true; // 非浏览器请求（无 Origin），CSRF 由 SameSite=Strict cookie 兜
  try {
    return new URL(origin).host === req.headers["host"];
  } catch {
    return false;
  }
}
function panelAuthed(req) {
  const cookie = String(req.headers["cookie"] || "");
  return new RegExp(`(?:^|;\\s*)seedx_panel=${PANEL_NONCE}(?:;|$)`).test(cookie);
}

async function handleControl(req, res) {
  const url = new URL(req.url, "http://localhost");
  const p = url.pathname;

  if (p === "/" || p === "/index.html") {
    const html = existsSync(join(DIR, "panel.html"))
      ? readFileSync(join(DIR, "panel.html"), "utf8")
      : "<h1>panel.html 缺失</h1>";
    res.writeHead(200, {
      "content-type": "text/html; charset=utf-8",
      "set-cookie": `seedx_panel=${PANEL_NONCE}; HttpOnly; SameSite=Strict; Path=/`,
    });
    res.end(html);
    return;
  }

  // 其余接口一律要求：同源 + 带面板 cookie（挡跨站/DNS-rebinding 改配置）
  if (!sameOriginOk(req) || !panelAuthed(req)) {
    return json(res, { error: "forbidden" }, 403);
  }

  if (p === "/api/status") return json(res, statusPayload());
  if (p === "/api/logs") {
    const n = Math.max(1, Math.min(Number(url.searchParams.get("n") || 200), LOG_CAP));
    return json(res, { logs: logs.slice(-n) });
  }
  if (p === "/api/config" && req.method === "POST") {
    let body;
    try {
      body = JSON.parse((await readBody(req)) || "{}");
    } catch {
      return json(res, { error: "请求体不是合法 JSON" }, 400);
    }
    const before = loadConfig();
    const after = await applyConfig(body);
    pushLog("panel", `配置已保存：${JSON.stringify(body)}`);
    if (before.controlPort !== after.controlPort) {
      // 面板端口变了：回完这次响应再重新绑定
      setTimeout(() => rebindControl(after.controlPort), 300);
      return json(res, { ok: true, config: after, note: `控制面板端口改为 ${after.controlPort}，请访问新地址` });
    }
    return json(res, { ok: true, config: after });
  }
  if (p === "/api/action" && req.method === "POST") {
    let body = {};
    try {
      body = JSON.parse((await readBody(req)) || "{}");
    } catch {
      /* ignore */
    }
    const a = body.action;
    if (a === "restart-all") restartAll();
    else if (a === "restart-proxy") startChild("proxy", "seedx-gateway-proxy.mjs");
    else if (a === "restart-sync") startChild("sync", "sync-ccswitch.mjs", ["--watch"]);
    else if (a === "stop-all") {
      stopChild("proxy");
      stopChild("sync");
    } else if (a === "start-all") ensureChildren();
    else if (a === "sync-now") {
      const child = spawn(process.execPath, [join(DIR, "sync-ccswitch.mjs")], {
        stdio: ["ignore", "pipe", "pipe"],
        env: { ...process.env, NODE_NO_WARNINGS: "1" },
      });
      relay("sync-once", child.stdout);
      relay("sync-once", child.stderr);
    } else if (a === "check-ticket") {
      await checkTicket();
    } else {
      return json(res, { error: `未知 action: ${a}` }, 400);
    }
    pushLog("panel", `执行动作：${a}`);
    return json(res, { ok: true, status: statusPayload() });
  }
  res.writeHead(404, { "content-type": "application/json" });
  res.end('{"error":"not found"}');
}

let controlServer;
function listenControl(port) {
  controlServer = createServer((req, res) => {
    handleControl(req, res).catch((e) => {
      pushLog("panel", `控制面板异常: ${e.message}`);
      if (!res.headersSent) json(res, { error: e.message }, 500);
    });
  });
  controlServer.on("error", (e) => {
    pushLog("panel", `控制面板监听失败(${port}): ${e.message}`);
  });
  controlServer.listen(port, "127.0.0.1", () => {
    console.log(`${nowIso()} 控制面板: http://127.0.0.1:${port}`);
  });
}
function rebindControl(port) {
  try {
    controlServer?.close();
  } catch {
    /* ignore */
  }
  setTimeout(() => listenControl(port), 200);
}

function shutdown() {
  if (shuttingDown) return;
  shuttingDown = true;
  console.log("\n正在停止…");
  for (const name of [...children.keys()]) stopChild(name);
  setTimeout(() => process.exit(0), 600);
}
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

// ── 主流程 ───────────────────────────────────────────────────────────
const cfg = loadConfig();
ensureChildren();
if (!HEADLESS) {
  listenControl(cfg.controlPort);
}
setInterval(() => void checkTicket().catch(() => {}), 60_000);
void checkTicket();
console.log(`${nowIso()} seedx 网关代理已启动（配置：${CONFIG_PATH}）`);
