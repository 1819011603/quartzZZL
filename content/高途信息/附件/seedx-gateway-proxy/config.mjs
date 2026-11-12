/**
 * config.mjs —— seedx 网关代理的配置读写（代理 / 同步 / 控制面板共用）。
 *
 * 配置来源优先级：**env > ~/.seedx-gateway-proxy/config.json > 默认值**。
 * 控制面板改的是 config.json；env 仅作高级覆盖。
 */

import { readFileSync, writeFileSync, mkdirSync, renameSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { randomBytes } from "node:crypto";

export const HOME_DIR = join(homedir(), ".seedx-gateway-proxy");
export const CONFIG_PATH = process.env.SEEDX_CONFIG || join(HOME_DIR, "config.json");

export const DEFAULTS = {
  proxyHost: "127.0.0.1",
  proxyPort: 8787, // claude（Anthropic 协议）监听端口
  codexPort: 8787, // codex（OpenAI 协议）端口；与 proxyPort 相同 = 单端口，靠路径识别协议
  controlPort: 8790,
  syncCcSwitch: true,
  syncIntervalSec: 3600,
  codexModel: "gpt-6-astra",
  // ── claude 上游切换 ──────────────────────────────────────────────
  claudeUpstream: "seed", // "seed"=走 seedx 网关（默认）；"llm"=直连 llm 网关
  llmClaudeBaseUrl: "https://test-llm.baijia.com", // llm 网关 Anthropic 原生 base（不含 /v1）
  llmClaudeToken: "", // llm 网关 claude 凭据（即 x-api-key 的值）
  llmClaudeHeaderName: "x-api-key", // 注入的鉴权头名：x-api-key 或 authorization
  llmClaudeAnthropicVersion: "2023-06-01", // 调 /v1/messages 需带的 anthropic-version
  // ── claude 额度用尽 → 自动改用 codex(gpt) 模型 ────────────────────
  // 网关支持在 claude(anthropic) 协议下用 codex 的 gpt 模型（额度计到 gpt 策略）。
  claudeFallbackCodex: false, // 开启后：claude 额度用尽时把 claude-* 请求的 model 改写成 fallbackCodexModel
  fallbackCodexModel: "gpt-6.1-sol", // 未命中映射时的默认改写目标
  fallbackCodexMap: {
    "claude-sonnet-5-5": "gpt-6.1-sol",
    "claude-opus-5-5": "gpt-6-astra",
    "sonnet": "gpt-6.1-sol",
    "opus": "gpt-6-astra"
  }, // claude 模型 → codex(gpt) 模型：先精确名，再按 opus/sonnet 关键词，最后用 fallbackCodexModel
  claudeForceCodex: false, // 手动切换：开启后 claude 请求一律改用 codex(gpt) 模型（忽略额度、立即生效），关掉即恢复
  quotaUrl: "", // 个人额度接口；默认空，请在 config.json / 面板填（含用户名，不入库）
  quotaProxy: "http://127.0.0.1:8888", // 取额度走本地 mitmproxy（自动注入 Cookie）
  quotaCheckSec: 60, // 额度刷新间隔（秒）
  credentialsPath: "", // 空 = 默认 ~/.seedx-workspace/credentials.json
  serverUrl: "", // 空 = 取 credentials.serverUrl，再否则 https://seed.baijia.com
  seedToken: "", // 一般留空（敏感）；留空则用 credentials
  localToken: "", // 本地鉴权 token：客户端请求凭据须等于它，否则 401（首次自动生成）
  allowLegacyToken: true, // 兼容老配置：额外接受占位值 "seedx-local-proxy"（重新切过 cc-switch 后可设 false）
  upstreamConnectTimeoutSec: 120, // 上游"无响应（未收到响应头）"超时。模型首字节可能较慢，别设太小；仅兜死连接
  upstreamIdleTimeoutSec: 300, // 上游"空闲"超时（收到响应后两次数据间隔）
  refreshAheadSec: 300, // 距网关授权过期还有这么久就提前续（越大越保险，越小越省刷新请求）
  usageUrl: "https://ai.baijia.com/ai-service/usage", // 面板「用量看板」跳转地址
};

/** 只读磁盘上的原始配置对象（不叠加默认/env），用于保存时合并。 */
export function readConfigFile() {
  try {
    const o = JSON.parse(readFileSync(CONFIG_PATH, "utf8"));
    return o && typeof o === "object" && !Array.isArray(o) ? o : {};
  } catch {
    return {};
  }
}

/** 生效配置 = 默认 + 文件 + env 覆盖。 */
export function loadConfig() {
  const cfg = { ...DEFAULTS, ...readConfigFile() };
  const E = process.env;
  if (E.SEEDX_PROXY_HOST) cfg.proxyHost = E.SEEDX_PROXY_HOST;
  if (E.SEEDX_PROXY_PORT) cfg.proxyPort = Number(E.SEEDX_PROXY_PORT) || cfg.proxyPort;
  if (E.SEEDX_CODEX_PORT) cfg.codexPort = Number(E.SEEDX_CODEX_PORT) || cfg.codexPort;
  if (E.SEEDX_CONTROL_PORT) cfg.controlPort = Number(E.SEEDX_CONTROL_PORT) || cfg.controlPort;
  if (E.SEEDX_SYNC_INTERVAL_S) cfg.syncIntervalSec = Number(E.SEEDX_SYNC_INTERVAL_S) || cfg.syncIntervalSec;
  if (E.SEEDX_SYNC_CCSWITCH) cfg.syncCcSwitch = E.SEEDX_SYNC_CCSWITCH !== "0";
  if (E.SEEDX_CREDENTIALS) cfg.credentialsPath = E.SEEDX_CREDENTIALS;
  if (E.SEEDX_SERVER_URL) cfg.serverUrl = E.SEEDX_SERVER_URL;
  if (E.SEEDX_CODEX_MODEL) cfg.codexModel = E.SEEDX_CODEX_MODEL;
  if (E.SEEDX_CLAUDE_UPSTREAM) cfg.claudeUpstream = E.SEEDX_CLAUDE_UPSTREAM;
  if (E.SEEDX_LLM_CLAUDE_BASE_URL) cfg.llmClaudeBaseUrl = E.SEEDX_LLM_CLAUDE_BASE_URL;
  if (E.SEEDX_LLM_CLAUDE_TOKEN) cfg.llmClaudeToken = E.SEEDX_LLM_CLAUDE_TOKEN;
  if (E.SEEDX_LLM_CLAUDE_HEADER) cfg.llmClaudeHeaderName = E.SEEDX_LLM_CLAUDE_HEADER;
  if (E.SEEDX_CLAUDE_FALLBACK_CODEX) cfg.claudeFallbackCodex = E.SEEDX_CLAUDE_FALLBACK_CODEX !== "0";
  if (E.SEEDX_FALLBACK_CODEX_MODEL) cfg.fallbackCodexModel = E.SEEDX_FALLBACK_CODEX_MODEL;
  if (E.SEEDX_CLAUDE_FORCE_CODEX) cfg.claudeForceCodex = E.SEEDX_CLAUDE_FORCE_CODEX !== "0";
  if (E.SEEDX_QUOTA_URL) cfg.quotaUrl = E.SEEDX_QUOTA_URL;
  if (E.SEEDX_QUOTA_PROXY) cfg.quotaProxy = E.SEEDX_QUOTA_PROXY;
  return cfg;
}

/** 合并写入 config.json（原子 + 0600）。返回合并后的文件内容。 */
export function saveConfig(partial) {
  const next = { ...readConfigFile(), ...partial };
  mkdirSync(HOME_DIR, { recursive: true });
  const tmp = `${CONFIG_PATH}.tmp`;
  writeFileSync(tmp, `${JSON.stringify(next, null, 2)}\n`, { encoding: "utf8", mode: 0o600 });
  renameSync(tmp, CONFIG_PATH);
  return next;
}

/** 代理地址（给 cc-switch / 日志用） */
export function proxyUrl(cfg = loadConfig()) {
  return `http://${cfg.proxyHost}:${cfg.proxyPort}`;
}

/** 本地鉴权 token：没有就生成一个随机值并落盘（所有客户端凭据都要等于它）。 */
export function ensureLocalToken() {
  const file = readConfigFile();
  if (typeof file.localToken === "string" && file.localToken.trim()) return file.localToken.trim();
  const tok = randomBytes(24).toString("hex");
  saveConfig({ localToken: tok });
  return tok;
}
