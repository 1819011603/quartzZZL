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

> 目标：**不依赖 seedx daemon / 它的 skill 与流程**，也能让 `claude` / `codex` 走「AI Coding 网关」那套链路（计费主体是自然人、按人算额度），且凭据自动刷新；跨平台（**能用在 Windows**，seedx 本身不能）。
> 手段：一个本地 HTTP 代理 —— 用 seed 登录长票换取「网关授权」，注入到请求里再转发到网关。脚本见同目录 `附件/seedx-gateway-proxy/`。

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
2. **本地代理**：claude/codex 请求打到 `127.0.0.1:8787`；代理剥掉客户端自带凭据，注入 `headerName`=`token`，流式转发到对应上游：
   - `/v1/messages*` → `anthropicBaseUrl`（claude）
   - 其余 → `openaiBaseUrl`（codex，base 已含 `/v1`，会归一避免 `/v1/v1`）
3. **刷新**：启动刷一次 → 后台每 60s 检查、距过期 <5min 续 → 上游 401 再刷一次；**每次刷新都现读 `credentials.json`**（长票换了自动跟上）。授权落盘缓存（重启不丢）。

网关侧其它端点（都用长票 Bearer）：`GET .../ctl/gateway-models?agentKind=codex|claude`（当前可用模型清单）。

## 三、文件（附件 `附件/seedx-gateway-proxy/`）
| 文件 | 作用 |
|---|---|
| `seedx-gateway-proxy.mjs` | 代理本体（取授权 + 注入 + 转发 + 每小时刷新；带 `[req]` 访问日志） |
| `sync-ccswitch.mjs` | 幂等同步 cc-switch 的 `seedx网关` provider + 拉取模型清单；`--watch` 常驻定时 |
| `start.mjs` | 一键启动：同时拉起上面两个，任一挂了自动重启 |
| `com.gaotu.seedx-gateway-proxy.plist` | macOS 开机自启用的 LaunchAgent |

## 四、使用
```bash
# 手动跑（前台）
cd ~/seedx-gateway-proxy && node start.mjs
# 自检：只取一次授权并打印
node seedx-gateway-proxy.mjs --check
# 同步 cc-switch（幂等）
node sync-ccswitch.mjs            # 一次
node sync-ccswitch.mjs --watch    # 常驻每小时
```

### cc-switch 配置（token 填占位，真凭据由代理注入）
- **claude** provider `settings_config`：
  ```json
  { "env": { "ANTHROPIC_BASE_URL": "http://127.0.0.1:8787", "ANTHROPIC_AUTH_TOKEN": "seedx-local-proxy" } }
  ```
- **codex** provider：
  ```json
  { "auth": { "OPENAI_API_KEY": "seedx-local-proxy" },
    "config": "model_provider = \"OpenAI\"\nmodel = \"gpt-6-astra\"\n\n[model_providers.OpenAI]\nname = \"OpenAI\"\nbase_url = \"http://127.0.0.1:8787\"\nwire_api = \"responses\"\nrequires_openai_auth = false\n" }
  ```
  - 新增的 provider 命名为 `seedx网关`，**不影响原有** `公司` / `公司新的`；切换时 `model_provider` 沿用 `OpenAI` 不变，只有 `base_url` 变。
  - codex 可用模型（网关）：`gpt-6.1-sol` / `gpt-6.1-terra` / `gpt-6-sol` / `gpt-6-astra` / `gpt-6-luna`；claude 侧另有 `claude-opus-5-5` / `claude-sonnet-5-5` / `claude-haiku-5-5` / `claude-fable-5-1`。

## 五、开机自启（macOS）
LaunchAgent：`~/Library/LaunchAgents/com.gaotu.seedx-gateway-proxy.plist`（`RunAtLoad` + `KeepAlive`，跑 `start.mjs`，日志 `~/seedx-gateway-proxy/launchd.out.log`）。
```bash
launchctl print "gui/$(id -u)/com.gaotu.seedx-gateway-proxy" | grep -E 'state|pid'   # 看状态
tail -f ~/seedx-gateway-proxy/launchd.out.log                                        # 看日志
launchctl bootout "gui/$(id -u)/com.gaotu.seedx-gateway-proxy"                       # 暂停
launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.gaotu.seedx-gateway-proxy.plist  # 重新启用
```
Windows 对应：任务计划程序（登录时）跑 `node ...\start.mjs`。

## 六、验证是否生效
1. 进程在跑：`pgrep -fl "seedx-gateway-proxy.mjs|sync-ccswitch.mjs"`。
2. cc-switch 有两条 `seedx网关`：`sqlite3 ~/.cc-switch/cc-switch.db "SELECT app_type,name,is_current FROM providers WHERE name='seedx网关';"`。
3. 代理能转发（**免费**）：`curl -s http://127.0.0.1:8787/v1/models -H 'x-api-key: seedx-local-proxy' -w '%{http_code}\n'` → 200，且日志出现 `[req] GET /v1/models -> openai 200`。
4. cc-switch 切到 `seedx网关`（claude/codex 各一），跑一次 `claude -p "say ok"` / `codex exec "say ok"`，日志出现 `[req] POST /v1/messages -> anthropic 200` / `POST /responses -> openai 200`（**这步花额度**）。
5. 额度归属：`seedx status` 或那张 `usage_html` 页面看是否算到本人名下。

## 七、注意事项 / 坑
- plist 里写的是 **nvm 的 node 绝对路径**（`.../v22.21.1/bin/node`）——升级 Node 大版本要同步改，否则自启失败。
- 只自动刷新**网关授权**（1h 那个 `act.…`）；**seed 登录长票本身不自动续**（要重登），但代理会现读文件、且启动时用 `/auth/me` 校验并告警。
- 走网关即**吃本人费控额度**，且会出现在按人用量里；额度用完后按「自助加油包 / 等时段重置」处理。
- 网关支持的头名/域名/模型是服务端下发的，代理每次刷新都读最新，**网关变化无需改 cc-switch**。
