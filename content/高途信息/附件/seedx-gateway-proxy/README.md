# seedx 网关代理（claude / codex 走 AI Coding 网关）

一个本地代理，让 `claude`、`codex` 走 AI Coding 网关那套链路（按人计费、自动续期凭据），**不依赖 seedx 的 daemon / skill / 流程**。**Windows 与 macOS 都支持**（Node.js 跨平台，零第三方依赖）。

## 文件
| 文件 | 说明 |
|---|---|
| `start.mjs` | **一键启动 + 控制面板**（同时拉起代理与同步，挂了自动重启） |
| `seedx-gateway-proxy.mjs` | 代理本体（取网关授权 + 注入 + 转发 + 续期 + 本地鉴权） |
| `sync-ccswitch.mjs` | 幂等同步 cc-switch 的 `seedx网关` provider + 拉取模型清单；`--watch` 常驻 |
| `config.mjs` | 配置读写（`~/.seedx-gateway-proxy/config.json`） |
| `panel.html` | 控制面板页面 |
| `start.cmd` | **Windows 双击启动** |
| `start-macos.command` | **macOS 双击启动** |
| `install-autostart-windows.cmd` / `uninstall-autostart-windows.cmd` | Windows 登录自启注册/注销 |
| `com.gaotu.seedx-gateway-proxy.plist` | macOS 开机自启（LaunchAgent） |

## 环境要求
- **Node.js ≥ 18**（`node:sqlite` 需 22+，`sync-ccswitch.mjs` 依赖它；建议直接用 22 LTS）。
- 能访问公司内网 `seed.baijia.com` / `ai-coding.baijia.com`。

## 快速开始
1. 拿到 **seed 登录长票**：把 seedx 的 `credentials.json` 放到默认路径
   - macOS/Linux：`~/.seedx-workspace/credentials.json`
   - Windows：`C:\Users\<你>\.seedx-workspace\credentials.json`
   - 或设环境变量 `SEEDX_TOKEN` / 在面板里填 `credentialsPath`。
2. 启动（任选其一）：
   - **双击** `start.cmd`（Windows）/ `start-macos.command`（macOS）；
   - 或命令行 `node start.mjs`。
3. 打开控制面板 **http://127.0.0.1:8790**（代理端口默认 **8787**）。

## cc-switch 配置（运行 `node sync-ccswitch.mjs` 会自动写好，名为 `seedx网关`）
- **claude** provider：
  ```json
  { "env": { "ANTHROPIC_BASE_URL": "http://127.0.0.1:8787", "ANTHROPIC_AUTH_TOKEN": "<localToken>" } }
  ```
- **codex** provider：
  ```json
  { "auth": { "OPENAI_API_KEY": "<localToken>" },
    "config": "model_provider = \"OpenAI\"\nmodel = \"gpt-6-astra\"\n\n[model_providers.OpenAI]\nname = \"OpenAI\"\nbase_url = \"http://127.0.0.1:8787\"\nwire_api = \"responses\"\nrequires_openai_auth = false\nexperimental_bearer_token = \"<localToken>\"\n" }
  ```
  - `experimental_bearer_token` 是给 **Codex 桌面 app（app-server）** 用的（它靠这个字段发凭据，不看 auth.json）；`sync-ccswitch.mjs` 会自动写上。
  - `<localToken>` 见控制面板「本地凭据」；`allowLegacyToken` 开着时老的 `seedx-local-proxy` 也认。
  - cc-switch 库路径默认 `~/.cc-switch/cc-switch.db`；Windows 下若不同，用环境变量 `CC_SWITCH_DB` 指定。

## 关键行为
- **单端口 8787**：claude 与 codex 都用它，按请求路径区分协议（`/v1/messages*`→Claude 上游，`/responses`→Codex 上游）。
- **本地鉴权**：客户端凭据须等于 `localToken`，否则 401；`allowLegacyToken=true`（默认）时**额外兼容老占位值 `seedx-local-proxy`**。
- **自动续期**：`act.` 网关授权有效期由服务端定（默认 1h）；代理在**距过期 < `refreshAheadSec`（默认 300s）**时提前续，每 60s 检查；并**每次现读 credentials.json**（长票换了自动跟上），落盘缓存重启不丢。
- **超时**：上游无响应 120s、空闲 300s（兜死 keep-alive / 换网卡住，不死等几分钟）。
- **错误兼容（claude / codex 共用）**：上游 `401`/`403` 都按"授权/权限类"处理 → 刷新一次授权再重试；日志标注「401 授权无效·已过期 / 403 无权限·无订阅（如 `SUBSCRIPTION_NOT_FOUND`）」；拿不到授权回 `503`（可读文案）。
- **claude 额度用尽 → 自动切 codex(gpt)**：面板 `claudeFallbackCodex` 开启后，代理每 `quotaCheckSec`(默认 60s) 经本地 **mitmproxy(8888)** 拉个人额度页；**claude 策略用尽**时把 `claude-*` 请求的 `model` 改写成 `fallbackCodexMap`/`fallbackCodexModel`（网关 Anthropic 端点**直接支持 gpt 模型**，额度计到 gpt 策略）。两条触发：**①前置**（轮询判定用尽，请求前就换）；**②反应式**（请求撞到 `402/403/429` 时改 gpt 再试一次，轮询没跟上也兜住）。依赖 mitmproxy 在跑。
  - **手动切换**（`claudeForceCodex`，默认关）：开了之后 **claude 一律改走 codex(gpt)**（忽略额度、立即生效），关掉即恢复。

## 常用命令
```bash
node start.mjs                 # 一键启动 + 面板
node start.mjs --headless      # 只常驻、不起面板
node seedx-gateway-proxy.mjs --check      # 只取一次网关授权并打印（自检）
node sync-ccswitch.mjs --dry-run          # 看会改 cc-switch 什么
node sync-ccswitch.mjs --watch            # 常驻同步（默认每小时）
```

## 控制面板（http://127.0.0.1:8790）
改端口 / `refreshAheadSec` / codex 模型 / 同步间隔、看运行状态（网关授权剩余、长票有效性、进程）、实时日志、一键同步 cc-switch、跳转用量看板。

## 开机自启
- **macOS**：`com.gaotu.seedx-gateway-proxy.plist` 放到 `~/Library/LaunchAgents/`，改里面 node 绝对路径后
  ```bash
  launchctl bootstrap "gui/$(id -u)" ~/Library/LaunchAgents/com.gaotu.seedx-gateway-proxy.plist
  ```
- **Windows**：双击 `install-autostart-windows.cmd`（用 `schtasks` 建"登录时"任务）；卸载跑 `uninstall-autostart-windows.cmd`。

## 验证
1. 面板顶部「运行状态」：代理/同步进程、网关授权剩余、长票有效性。
2. 免费自检：
   ```bash
   curl -s http://127.0.0.1:8787/v1/models -H "x-api-key: <localToken>" -w '%{http_code}\n'   # → 200
   ```
   日志出现 `[req] anthropic GET /v1/models -> 200`。
3. cc-switch 切到 `seedx网关`，跑一次 claude/codex，日志出现 `[req] anthropic POST /v1/messages -> 200` / `[req] openai POST /responses -> 200` 即通。

## 注意
- 自动续的是**网关授权**；**seed 登录长票不自动续**（失效需重新登录、更新 credentials.json）。
- 走网关会吃**本人费控额度**，并计入按人用量。
- macOS 自启 plist 里是 **node 绝对路径**（nvm 升级后要改）；Windows 自启用 `where node` 的结果。
- 脚本里**不含任何密钥**（`localToken` 自动生成、存 `~/.seedx-gateway-proxy/config.json`）。
- **Codex 桌面 app 报 `application network permission was revoked`**：它直连私网 IP 需要 macOS「本地网络」权限；走本代理（`127.0.0.1`）可绕开。若仍报，去「系统设置 → 隐私与安全性 → 本地网络」给 Codex 打开。
