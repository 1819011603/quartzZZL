#!/usr/bin/env node
/**
 * sync-ccswitch.mjs —— 把 cc-switch 的 “seedx网关” provider 自动同步到本地代理（幂等、跨平台、零依赖）。
 *
 * 每次运行做三件事：
 *   1. 拉取网关当前配置：GET {seed}/seedx/resource/manage/service/ctl/gateway-models?agentKind=...
 *      （打印当前 codex/claude 可用模型，便于发现“有变化”）；
 *   2. 确保 cc-switch 里 claude / codex 各有一条 “seedx网关” provider 指向本地代理
 *      （缺则按现有同类 provider 的结构克隆新增；有则只改 base_url / 占位 key / 指定 model）；
 *   3. **只碰名为 “seedx网关” 的条目**，其它 provider（公司/公司新的…）一律不动。
 *
 * 用法：
 *   node sync-ccswitch.mjs                 # 同步一次
 *   node sync-ccswitch.mjs --dry-run       # 只看会改什么，不写库
 *   node sync-ccswitch.mjs --watch         # 常驻：先同步一次，之后每 SEEDX_SYNC_INTERVAL_S 秒再同步（默认 3600）
 *   SEEDX_CODEX_MODEL=gpt-6.1-sol node sync-ccswitch.mjs   # 顺带把 codex 默认模型设成它
 *
 * 环境变量：
 *   SEEDX_PROXY_HOST/PORT  本地代理地址（默认 127.0.0.1 / 8787）——要和 seedx-gateway-proxy 一致
 *   CC_SWITCH_DB           cc-switch 数据库路径（默认 ~/.cc-switch/cc-switch.db）
 *   SEEDX_CREDENTIALS      seed 凭据文件（默认 ~/.seedx-workspace/credentials.json）/ SEEDX_TOKEN
 *   SEEDX_SERVER_URL       默认取凭据里的 serverUrl，否则 https://seed.baijia.com
 *   SEEDX_CODEX_MODEL      可选：把 codex provider 的默认 model 设成它
 *   SEEDX_SYNC_INTERVAL_S  --watch 的同步间隔秒（默认 3600，最小 60）
 *
 * 定时跑：`--watch` 自带常驻定时（推荐）；或挂到系统计划任务（每小时/每天一次皆可）。cc-switch 没在跑时写库最稳。
 */

import { DatabaseSync } from "node:sqlite";
import { readFileSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { loadConfig, proxyUrl, ensureLocalToken } from "./config.mjs";

const ENV = process.env;
const CFG = loadConfig();
const PROXY = proxyUrl(CFG);
const CLAUDE_URL = `http://${CFG.proxyHost}:${CFG.proxyPort}`;
const CODEX_URL = `http://${CFG.proxyHost}:${CFG.codexPort}`;
const LOCAL_TOKEN = ensureLocalToken();
const NAME = "seedx网关";
const DB_PATH = ENV.CC_SWITCH_DB || join(homedir(), ".cc-switch", "cc-switch.db");
const CRED_PATH = CFG.credentialsPath || join(homedir(), ".seedx-workspace", "credentials.json");
const DRY = process.argv.includes("--dry-run");

const PREFIX_RESOURCE = ENV.SEEDX_PREFIX_RESOURCE ?? "/seedx/resource/manage/service";

function log(...a) {
  console.log(new Date().toISOString(), ...a);
}

function readSeed() {
  if (CFG.seedToken) return { token: CFG.seedToken, serverUrl: CFG.serverUrl };
  try {
    const c = JSON.parse(readFileSync(CRED_PATH, "utf8"));
    return { token: c.token, serverUrl: CFG.serverUrl || c.serverUrl };
  } catch {
    return {};
  }
}

async function fetchModels(serverUrl, token, agentKind) {
  try {
    const res = await fetch(`${serverUrl}${PREFIX_RESOURCE}/ctl/gateway-models?agentKind=${agentKind}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return undefined;
    const b = await res.json();
    return Array.isArray(b?.models) ? b.models.map((m) => m.id) : undefined;
  } catch {
    return undefined;
  }
}

// ── cc-switch 库操作 ────────────────────────────────────────────────
function ensureProvider(db, appType, transform, templateMeta) {
  const cur = db.prepare("SELECT id, settings_config, meta FROM providers WHERE app_type=? AND name=?").get(appType, NAME);
  if (cur) {
    const orig = JSON.parse(cur.settings_config);
    const next = transform(structuredClone(orig));
    // 归一化比对（忽略键顺序/空格），语义没变就不写库
    if (JSON.stringify(next) === JSON.stringify(orig)) {
      log(`[${appType}] ${NAME} 已是最新，未改动`);
      return;
    }
    if (!DRY) db.prepare("UPDATE providers SET settings_config=? WHERE id=?").run(JSON.stringify(next), cur.id);
    log(`[${appType}] ${NAME} ${DRY ? "将更新" : "已更新"}`);
    return;
  }
  // 新增：从同类现有 provider 复制结构（保留 permissions / plugins 等），只覆盖业务字段
  const tmpl = db
    .prepare("SELECT settings_config, meta FROM providers WHERE app_type=? AND name<>? ORDER BY is_current DESC LIMIT 1")
    .get(appType, NAME);
  const base = tmpl ? JSON.parse(tmpl.settings_config) : {};
  const next = transform(base);
  const id = globalThis.crypto.randomUUID();
  if (!DRY) {
    db.prepare(
      `INSERT INTO providers
        (id,app_type,name,settings_config,website_url,category,created_at,sort_index,notes,icon,icon_color,meta,is_current,cost_multiplier,limit_daily_usd,limit_monthly_usd,provider_type,in_failover_queue)
       VALUES (?,?,?,?,NULL,NULL,?,NULL,NULL,NULL,NULL,?,0,'1.0',NULL,NULL,NULL,0)`,
    ).run(id, appType, NAME, JSON.stringify(next), Date.now(), tmpl?.meta ?? templateMeta ?? "{}");
  }
  log(`[${appType}] ${NAME} ${DRY ? "将新增" : "已新增"}（结构克隆自 ${tmpl ? "现有同类 provider" : "空模板"}）`);
}

function setClaudeProxy(cfg) {
  cfg.env = { ...(cfg.env || {}), ANTHROPIC_BASE_URL: CLAUDE_URL, ANTHROPIC_AUTH_TOKEN: LOCAL_TOKEN };
  return cfg;
}

function setCodexProxy(cfg, model) {
  cfg.auth = { ...(cfg.auth || {}), OPENAI_API_KEY: LOCAL_TOKEN };
  let toml = cfg.config || 'model_provider = "OpenAI"\n\n[model_providers.OpenAI]\nname = "OpenAI"\nbase_url = ""\nwire_api = "responses"\nrequires_openai_auth = false\n';
  toml = toml.replace(/(base_url\s*=\s*)"[^"]*"/, `$1"${CODEX_URL}"`);
  if (model) toml = toml.replace(/^model = ".*"$/m, `model = "${model}"`);
  cfg.config = toml;
  return cfg;
}

async function syncOnce() {
  const { token, serverUrl } = readSeed();
  const SERVER = (serverUrl || "https://seed.baijia.com").replace(/\/+$/, "");

  if (token) {
    const [codexModels, claudeModels] = await Promise.all([
      fetchModels(SERVER, token, "codex"),
      fetchModels(SERVER, token, "claude"),
    ]);
    log(`网关当前 codex 模型：${codexModels ? codexModels.join(", ") : "(取不到，忽略)"}`);
    log(`网关当前 claude 模型：${claudeModels ? claudeModels.join(", ") : "(取不到，忽略)"}`);
  } else {
    log("未读到 seed 凭据，跳过模型清单拉取（仍会同步 provider）");
  }

  if (!existsSync(DB_PATH)) {
    log(`cc-switch 数据库不存在：${DB_PATH}（先启动一次 CC Switch 生成后再跑）`);
    return false;
  }
  // 每轮重新开库：cc-switch 可能中途重写该文件，避免持旧句柄
  const db = new DatabaseSync(DB_PATH);
  try {
    const model = CFG.codexModel ? String(CFG.codexModel).trim() : undefined;
    ensureProvider(db, "claude", setClaudeProxy);
    ensureProvider(db, "codex", (cfg) => setCodexProxy(cfg, model));
  } finally {
    db.close();
  }

  log(`本地代理地址：${PROXY}`);
  log(DRY ? "dry-run：未写库" : "同步完成（未触碰其它 provider）");
  return true;
}

async function main() {
  const watch = process.argv.includes("--watch");
  await syncOnce();
  if (!watch) return;

  const intervalS = Math.max(60, Number(CFG.syncIntervalSec ?? 3600));
  log(`--watch 进入常驻：每 ${intervalS}s 同步一次（Ctrl+C 退出）`);
  const timer = setInterval(() => {
    void syncOnce().catch((e) => log("同步失败:", e.message));
  }, intervalS * 1000);
  process.on("SIGINT", () => {
    log("收到 SIGINT，退出 --watch");
    clearInterval(timer);
    process.exit(0);
  });
  // 常驻
  await new Promise(() => {});
}

main().catch((e) => {
  log("同步失败:", e.message);
  process.exit(1);
});
