---
title: seedx 网关代理（让 claude / codex 走 AI Coding 网关）
tags:
  - 高途信息
  - AI Coding
  - seedx
  - 代理
date: 2026-11-10
---

# seedx 网关代理（让 claude / codex 走 AI Coding 网关）

> 目标：**不依赖 seedx daemon / 它的 skill 与流程**，也能让 `claude` / `codex` 走「AI Coding 网关」那套链路（计费主体是自然人、按人算额度），凭据自动续期；**Windows 与 macOS 都支持**（Node.js 跨平台，seedx 本身不能在 Windows 用）。
> 手段：一个本地 HTTP 代理 —— 用 seed 登录长票换取「网关授权」，注入到请求里再转发到网关。脚本见同目录 `附件/seedx-gateway-proxy/`。
> 兼容：**Claude Code**、**Codex CLI**（认 `~/.codex/auth.json`）与 **Codex 桌面 app / app-server**（认 provider 里的 `experimental_bearer_token`）都覆盖。

## 一、两种「请求 AI」的方式
| | 直连 sub2api 集群 | 走 AI Coding 网关（本文方案） |
|---|---|---|
| base_url | `https://sub2apiN-lan.baijia.com` | `https://ai-coding.baijia.com` |
| 鉴权 | `x-api-key: sk-<个人真实key>` | `x-api-key: <网关授权 act.…>`（按人、短命） |
| 中间层 | 无 | 网关每请求择优（个人 key 挂了回落备用集群、换 key 重试） |
| 用量归属 | 不一定计入网关额度 | 按人汇总，吃**本人费控额度** |
| 客户端持有 | 直接持有真实 key | 只持有本地占位 key（凭据在代理里注入） |

- `qingzhou_private_token`（如 `usage_html?qingzhou_private_token=…`）**不是请求 AI 的方式**，只用于查用量报表（拿它调青舟天眼换 username）。
- `credentials.json` 里的 `token` 是 **seed 平台登录长票**（CAS 登录换来）；网关授权 `act.…` 是拿长票换来的短命凭据。

## 二、原理（复刻 seedx 的 `gateway-token.ts` + `agent-proxy.ts`）
1. **取授权**：`POST {seed}/seedx/resource/manage/service/ctl/gateway-token/refresh`，头 `Authorization: Bearer <长票>`，body `{}`
   → 返回 `{ token(act.…), expiresAt, headerName(x-api-key), anthropicBaseUrl, openaiBaseUrl, issuedAt }`
2. **本地代理（单端口 8787）**：claude / codex 都打到 `127.0.0.1:8787`；代理剥掉客户端自带凭据、注入 `headerName`=`token`，流式转发到上游，**按路径区分协议**：
   - `/v1/messages*` → `anthropicBaseUrl`（Claude）
   - `/responses`、`/chat/completions*` → `openaiBaseUrl`（Codex，base 已含 `/v1`，会归一避免 `/v1/v1`）
   - 其余按端口默认（8787 默认 anthropic）
3. **续期**：启动刷一次 → 后台每 60s 检查、距过期 < `refreshAheadSec`（默认 300s）就续 → 上游 401 再刷一次；**每次刷新都现读 `credentials.json`**（长票换了自动跟上）。授权落盘缓存（重启不丢）。
4. **超时**：上游无响应 120s、空闲 300s —— 兜住死 keep-alive / 换网卡住，不再死等几分钟。
5. **错误兼容（claude / codex 共用）**：上游 `401`/`403` 都按"授权/权限类"处理 → **刷新一次授权再重试**；日志标注「401 授权无效·已过期 / 403 无权限·无订阅（如 `SUBSCRIPTION_NOT_FOUND`）」；拿不到授权回 `503`（可读文案）。
6. **本地鉴权**：客户端凭据须等于 `localToken`（首次自动生成随机串），否则 401；`allowLegacyToken=true` 时**额外兼容老占位值 `seedx-local-proxy`**（不破坏既有配置）。

网关侧其它端点（都用长票 Bearer）：`GET .../ctl/gateway-models?agentKind=codex|claude`（当前可用模型清单）。

## 三、文件（附件 `附件/seedx-gateway-proxy/`）
| 文件 | 作用 |
|---|---|
| `start.mjs` | **一键启动 + 控制面板**（同时拉起下面两个，挂了自动重启） |
| `seedx-gateway-proxy.mjs` | 代理本体（取授权 + 注入 + 转发 + 续期 + 本地鉴权；带 `[req]` 日志） |
| `sync-ccswitch.mjs` | 幂等同步 cc-switch 的 `seedx网关` provider + 拉取模型清单；`--watch` 常驻 |
| `config.mjs` | 配置读写（`~/.seedx-gateway-proxy/config.json`） |
| `panel.html` | 控制面板页面 |
| `start.cmd` | **Windows 双击启动** |
| `start-macos.command` | **macOS 双击启动** |
| `install-autostart-windows.cmd` / `uninstall-autostart-windows.cmd` | Windows 登录自启注册/注销（`schtasks`） |
| `com.gaotu.seedx-gateway-proxy.plist` | macOS 开机自启用的 LaunchAgent |

## 四、使用
```bash
cd ~/seedx-gateway-proxy
node start.mjs                 # 一键启动 + 控制面板（http://127.0.0.1:8790）
node start.mjs --headless      # 只常驻、不起面板
node seedx-gateway-proxy.mjs --check      # 只取一次网关授权并打印（自检）
node sync-ccswitch.mjs            # 同步一次 cc-switch
node sync-ccswitch.mjs --watch    # 常驻同步（默认每小时）
```
**双击启动**：Windows 双击 `start.cmd`；macOS 双击 `start-macos.command`（首次右键→打开 绕过 Gatekeeper）。
**前置**：把 seedx 的 `credentials.json` 放到默认路径（Win：`C:\Users\<你>\.seedx-workspace\`；mac/linux：`~/.seedx-workspace/`），或设 `SEEDX_TOKEN`、或在面板填 `credentialsPath`。

## 五、控制面板（http://127.0.0.1:8790）
- 运行状态：代理/同步进程、**网关授权剩余时间**、**seed 长票有效性**、本地 `localToken`（可复制）。
- 设置：`proxyHost / proxyPort(=codexPort，默认都 8787) / controlPort / refreshAheadSec / codexModel / 同步间隔 / 凭据路径 / serverUrl / usageUrl / 同步开关 / 兼容老凭据开关`。
- 按钮：保存并应用、重启代理/同步、全部重启、立即同步 cc-switch、检查长票、停/启。
- **用量看板**快捷跳转（今天 / 近 2 / 近 7 / 近 30 天）→ `ai.baijia.com/ai-service/usage?dim=coding&g=day&…`。
- 实时日志（最近 200 行）。

## 六、cc-switch 配置（运行 `node sync-ccswitch.mjs` 会自动写好，名为 `seedx网关`，不改动其它 provider）
- **claude** provider：
  ```json
  { "env": { "ANTHROPIC_BASE_URL": "http://127.0.0.1:8787", "ANTHROPIC_AUTH_TOKEN": "<localToken>" } }
  ```
- **codex** provider：
  ```json
  { "auth": { "OPENAI_API_KEY": "<localToken>" },
    "config": "model_provider = \"OpenAI\"\nmodel = \"gpt-6-astra\"\n\n[model_providers.OpenAI]\nname = \"OpenAI\"\nbase_url = \"http://127.0.0.1:8787\"\nwire_api = \"responses\"\nrequires_openai_auth = false\nexperimental_bearer_token = \"<localToken>\"\n" }
  ```
  - `experimental_bearer_token` 是给 **Codex 桌面 app（app-server）** 用的——它靠这个字段发凭据、不看 auth.json；`sync-ccswitch.mjs` 会自动写上，同时给 **Codex CLI** 兜底写 `~/.codex/auth.json`。
  - `<localToken>` 见控制面板「本地凭据」；`allowLegacyToken` 开着时老的 `seedx-local-proxy` 也认。
  - cc-switch 库路径默认 `~/.cc-switch/cc-switch.db`；Windows 下若不同，用环境变量 `CC_SWITCH_DB` 指定。
  - codex 可用模型（网关）：`gpt-6.1-sol` / `gpt-6.1-terra` / `gpt-6-sol` / `gpt-6-astra` / `gpt-6-luna`；claude 侧另有 `claude-opus-5-5` / `claude-sonnet-5-5` / `claude-haiku-5-5` / `claude-fable-5-1`。

## 七、开机自启
- **macOS**：LaunchAgent `~/Library/LaunchAgents/com.gaotu.seedx-gateway-proxy.plist`（`RunAtLoad` + `KeepAlive`，跑 `start.mjs`，日志 `~/seedx-gateway-proxy/launchd.out.log`）。
  ```bash
  launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.gaotu.seedx-gateway-proxy.plist  # 启用
  launchctl print "gui/$(id -u)/com.gaotu.seedx-gateway-proxy" | grep -E 'state|pid'              # 看状态
  launchctl kickstart -k "gui/$(id -u)/com.gaotu.seedx-gateway-proxy"                            # 重启
  launchctl bootout "gui/$(id -u)/com.gaotu.seedx-gateway-proxy"                                 # 暂停
  ```
- **Windows**：双击 `install-autostart-windows.cmd`（`schtasks` 建"登录时"任务）；卸载跑 `uninstall-autostart-windows.cmd`。

## 八、验证是否生效
1. 进程在跑：`pgrep -fl "start.mjs|seedx-gateway-proxy.mjs|sync-ccswitch.mjs"`；监听端口：`lsof -nP -iTCP:8787 -sTCP:LISTEN`。
2. cc-switch 有两条 `seedx网关`：`sqlite3 ~/.cc-switch/cc-switch.db "SELECT app_type,name,is_current FROM providers WHERE name='seedx网关';"`。
3. 代理能转发（**免费**）：
   ```bash
   TOK=$(python3 -c "import json;print(json.load(open('$HOME/.seedx-gateway-proxy/config.json')).get('localToken',''))")
   curl -s http://127.0.0.1:8787/v1/models -H "x-api-key: $TOK" -w '%{http_code}\n'   # → 200
   ```
   日志出现 `[req] anthropic GET /v1/models -> 200`。
4. cc-switch 切到 `seedx网关`，跑一次 `claude -p "say ok"` / `codex exec "say ok"`，日志出现 `[req] anthropic POST /v1/messages -> 200` / `[req] openai POST /responses -> 200`（**这步花额度**）。
5. 额度归属：`seedx status` 或那张 `usage_html` 页面看是否算到本人名下。

## 九、配置项（`~/.seedx-gateway-proxy/config.json`）
`proxyHost`(127.0.0.1) / `proxyPort`(8787) / `codexPort`(8787，与 proxyPort 同 = 单端口) / `controlPort`(8790) / `localToken`(自动生成) / `allowLegacyToken`(true) / `refreshAheadSec`(300) / `upstreamConnectTimeoutSec`(120) / `upstreamIdleTimeoutSec`(300) / `syncCcSwitch`(true) / `syncIntervalSec`(3600) / `codexModel`(gpt-6-astra) / `credentialsPath`(空=默认) / `serverUrl`(空=取凭据) / `usageUrl`。env 可覆盖（如 `SEEDX_PROXY_PORT`）。

## 十、注意事项 / 坑
- **网关授权 TTL(3600s) 是 admin 服务端定的**（`sub2api.token.ttlSeconds`），代理只是使用、**改不了**；能调的是**提前续期** `refreshAheadSec`（不是改 TTL）。
- 只自动续**网关授权**；**seed 登录长票本身不自动续**（失效要重登），但代理会现读文件、且启动时用 `/auth/me` 校验并告警。
- 首字节超时别设太小：简单模型请求也可能十几秒到几十秒才回；设太小会把正常请求误杀成 502（已默认 120s）。
- 走网关即**吃本人费控额度**，并计入按人用量；额度用完后按「自助加油包 / 等时段重置」处理。
- **Codex 桌面 app 报 `application network permission was revoked`**：它直连私网 IP 需要 macOS「本地网络」权限；改走本代理（`127.0.0.1` 回环不需要该权限）即可绕开；若仍报，去「系统设置 → 隐私与安全性 → 本地网络」给 Codex 打开。
- **兼容矩阵**：Claude Code（`ANTHROPIC_*`）、Codex CLI（`~/.codex/auth.json`）、Codex 桌面 app（`experimental_bearer_token`）——客户端凭据统一用 `localToken`。
- 网关支持的头名/域名/模型是服务端下发的，代理每次刷新都读最新，**网关变化无需改 cc-switch**。
- plist 里写的是 **nvm 的 node 绝对路径**（`.../v22.21.1/bin/node`）——升级 Node 大版本要同步改。
- 脚本**不含任何密钥**（`localToken` 自动生成、存 `config.json`）。

## 十一、错误对照（无授权 / 无权限时各端报什么）
**网关 / 平台侧**（claude、codex 共用同一条网关）：
- `401` —— 授权无效 / 未授权；
- `403 SUBSCRIPTION_NOT_FOUND` —— 无订阅 / 无权限（admin `service.py:3296`）。

**seedx 端侧语义（本代理据此兼容）**：
- 拿不到授权 → `503` + 文案「seedx 网关授权不可用：确认 daemon 在线 / 已登录 / 服务端已配网关」；
- 上游 `401` → 刷新一次再**原样**回应（`agent-proxy.ts`）；
- daemon 待命连接 `401` → 提示执行 `seedx login`。

**agent 自身**：
- claude：系统帧 `cloud_credential_error`；`.zshrc` 里 export 的 `ANTHROPIC_AUTH_TOKEN` 也会撞 401；
- codex：`Auth required` / `not logged in` / `Sign in to ChatGPT`；`application network permission was revoked`（macOS 本地网络权限）。

**本代理的处理**：上游 `401` / `403` → **刷新授权 + 重试一次**；拿不到授权 → `503`；本地凭据不对 → `401`（用 `localToken`，`allowLegacyToken` 开启时也认 `seedx-local-proxy`）。

## 十二、换授权接口 & 网关调用示例（实测脱敏）

### 1. 换授权（gateway-token refresh）
- **URL**：`POST {serverUrl}/seedx/resource/manage/service/ctl/gateway-token/refresh`
- **方法**：`POST`，`content-type: application/json`，body `{}`
- **长票从哪取、放哪**：取 `~/.seedx-workspace/credentials.json` 的 **`token`** 字段（seed 登录长票）；放**请求头 `Authorization: Bearer <长票>`**。同文件的 `serverUrl` 决定 server base（缺省回退 `https://seed.baijia.com`）。
- **成功响应**（`200`）：
```json
{
  "token": "act.eyJ…<TOKEN>",           // ★ 网关凭据：值本身就是 bearer，直接用（x-api-key 场景不再拼 "Bearer "）
  "headerName": "x-api-key",            // ★ 发往上游的 header 名（用它作会话头，值=token）
  "expiresAt": "2026-11-12T06:47:25Z",  // ★ 过期时间（UTC；TTL 由 admin sub2api.token.ttlSeconds 定）
  "anthropicBaseUrl": "https://ai-coding.baijia.com",  // ★ Claude/Anthropic 上游 base（不含 /v1）
  "openaiBaseUrl": "https://ai-coding.baijia.com/v1",  // ★ Codex/OpenAI 上游 base（已含 /v1）
  "issuedAt": "2026-11-12T05:47:25.155224086Z"
}
```
  > **模型清单不在这条响应里**——另走 `gateway-models`（见 3）。
- **长票过期 / 无效时**（`401`，纯文本）：
```
HTTP/1.1 401
content-type: text/plain

凭据无效
```

### 2. 网关直调示例（凭据值统一写成 `x-api-key: <TOKEN>`）
**Anthropic（Claude）**
```bash
curl -sS https://ai-coding.baijia.com/v1/messages \
  -H 'x-api-key: <TOKEN>' \
  -H 'anthropic-version: 2023-06-01' \
  -H 'content-type: application/json' \
  -d '{"model":"claude-sonnet-5-5","max_tokens":16,"messages":[{"role":"user","content":"ping"}]}'
```
**OpenAI（Codex）**——`/responses` 与 `/chat/completions` **实测都支持**：
```bash
# Codex 用这个
curl -sS https://ai-coding.baijia.com/v1/responses \
  -H 'x-api-key: <TOKEN>' -H 'content-type: application/json' \
  -d '{"model":"gpt-6.1-sol","input":"ping"}'

# 也支持
curl -sS https://ai-coding.baijia.com/v1/chat/completions \
  -H 'x-api-key: <TOKEN>' -H 'content-type: application/json' \
  -d '{"model":"gpt-6.1-sol","max_tokens":16,"messages":[{"role":"user","content":"ping"}]}'
```
> 走本地代理时同义：把 `https://ai-coding.baijia.com` 换成 `http://127.0.0.1:8787`（claude）/ 同端口（codex），`x-api-key` 换成 `localToken`——代理自己剥掉客户端凭据、注入网关 `headerName/token` 后转发。

### 3. 模型清单（`gateway-models`）
```bash
# 头用「seed 登录长票」Bearer（不是网关 token）
curl -sS "https://seed.baijia.com/seedx/resource/manage/service/ctl/gateway-models?agentKind=codex" \
  -H "Authorization: Bearer <长票>"
```
返回 `{"available": true, "models": [{"id","label","efforts":["low",…,"max"],"contextWindow":1048576}]}`；`agentKind=claude` 的清单是 codex 的**超集**（额外含 `claude-opus/sonnet/haiku-5-5`、`glm-5.3(-flash)` 等）。

## 十三、claude 切换 codex(gpt)（额度用尽自动 / 手动强制）
面板开关 **`claudeFallbackCodex`**（`panel.html`）。**claude 与 codex 是两条独立额度策略**（同一网关、按策略分池），所以 claude 用尽、codex 还有额度时，切过去是有效的。

**原理**：代理每 `quotaCheckSec`(默认 60s) 经**本地 mitmproxy(8888)** 拉个人额度页（`quotaUrl`，注入 Cookie）→ 取 `policies` 里 `policy==="claude"` 的策略 → `remaining_usd<=0` 即判定用尽 → 把 `claude-*` 请求的 `model` 改写成 `fallbackCodexMap`/`fallbackCodexModel`。
关键：**网关的 Anthropic 端点 `/v1/messages` 直接支持 gpt 模型**（实测 `model:gpt-6.1-sol` → 200，走 Anthropic 协议、计到 **gpt 策略**额度），所以切的是**模型**，不是协议/上游，客户端无感。

**两条触发**：
1. **前置**：轮询判定用尽 → 请求发出前就换模型（避免先失败）；
2. **反应式**：请求撞到 `402/403/429`（额度/限流/权限类）→ 即使轮询没跟上，也改写为 gpt **再试一次**（只一次，防循环）。

**手动切换（`claudeForceCodex`，默认关）**：开了之后 **claude 一律改走 codex(gpt)**——不看额度、立即生效（面板独立开关）；关掉即恢复自动逻辑（用尽/反应式）。面板改完保存即重启代理生效。

**依赖 / 注意**：①`mitmproxy`(:8888) 必须在跑，否则额度未知 → 不切；②`claudeUpstream=seed` 时才生效（`llm` 直连模式不切）；③映射默认 `claude-sonnet-5-5→gpt-6.1-sol`、`claude-opus-5-5→gpt-6-astra`，其余按 sonnet/opus 关键词，最后 `fallbackCodexModel`。

**实测**：quota 报 `remaining_usd=0` → `claude-sonnet-5-5` 请求被改写为 `gpt-6.1-sol` 且 200；假上游返 403 → 上游先收 `claude-opus-5-5`、再收 `gpt-6-astra`（反应式生效）；手动开(忽略额度) → 切 `gpt-6.1-sol`，手动关 → 不切。
