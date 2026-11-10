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
