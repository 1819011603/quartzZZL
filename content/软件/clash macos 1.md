这是一个非常好的技术问题。直接回答你的核心疑问：

**结论：不是真的。在 Cursor + 代理 + 复杂网络环境（尤其是配合 Proxifier）下，强制 HTTP/1.1 远比 HTTP/2 稳定。**

虽然 HTTP/2 理论速度更快（多路复用），但在经过 Proxifier 转发 -> Clash 加密 -> 节点转发 -> 防火墙过滤这一长串链路时，HTTP/2 的长连接极其容易因为“中间人”对协议解析的不一致而断开（即你之前遇到的 `Stream Error` 或 `Connection Reset`）。

**Proxifier + Clash 是 macOS 上解决 Cursor 代理问题的“终极方案”**，因为它能强制接管 Cursor 的流量，无视高途 Link VPN 的路由表。

以下是一份详细的 **macOS Proxifier + Clash 针对 Cursor 的分流配置文档**。

---

# macOS Proxifier + Clash + Cursor 分流配置指南

### 方案目标
1.  **强制接管**：让 Cursor 的流量不走公司 VPN 网关，强制走 Clash 代理。
2.  **解决回环**：防止本地工具调用（Localhost）死循环。
3.  **稳定性**：使用 SOCKS5 协议 + HTTP/1.1 策略，消除握手失败。

### 前置准备
*   **Clash Verge Rev** (已运行，假设 Mixed/SOCKS5 端口为 `7897`)。
*   **Proxifier for Mac** (需自行安装)。
*   **Cursor**。

---

### 第一步：Clash Verge Rev 设置
在 Proxifier 方案中，Clash 不需要开 TUN 模式，它只需要作为一个安静的 SOCKS5 服务端。

1.  **关闭 TUN Mode**：如果之前开了，可以关掉（Proxifier 代替了 TUN 的作用，且兼容性更好）。
2.  **检查端口**：记住 Settings 中的 **Mixed Port** (例如 `7897`)。
3.  **协议设置**：保持你之前设置的“强制 HTTP/1.1”脚本（见上文），或者确保节点本身支持 UDP。

---

### 第二步：Proxifier 核心配置 (关键)

打开 Proxifier，按顺序进行配置。

#### 1. 添加代理服务器 (Proxies)
*   点击图标栏的 **Proxies** 按钮。
*   点击 **Add...**。
*   **Address**: `127.0.0.1`
*   **Port**: `7897` (填你的 Clash 端口)
*   **Protocol**: 选择 **SOCKS Version 5** (不要选 HTTP)。
*   点击 OK，如果弹窗问是否设为默认，选 **No** (我们只要特定软件走代理)。

#### 2. 设置 DNS 解析 (Name Resolution)
这一步至关重要，防止 DNS 污染和 Cursor 无法解析域名。
*   点击菜单栏 **DNS**。
*   **取消勾选** "Detect DNS settings automatically"。
*   **勾选** "Resolve hostnames through proxy"。
*   保存。

#### 3. 配置分流规则 (Rules) - 最重要的一步
点击图标栏的 **Rules** 按钮。你需要添加 3 条规则，**顺序不能乱**（从上到下执行）：

**规则 A：放行本地流量 (防止死循环)**
*   **Name**: `Localhost Direct`
*   **Applications**: (留空)
*   **Target Hosts**: `localhost; 127.0.0.1; ::1; *.local`
*   **Target Ports**: (留空)
*   **Action**: **Direct** (直连)

**规则 B：接管 Cursor 流量**
*   **Name**: `Cursor Proxy`
*   **Applications**:
    *   点击 `+`，在 Applications 文件夹找到 `Cursor.app`。
    *   **进阶技巧**：为了保险，手动输入 `Cursor; cursor; node; rg` (包含 Cursor 主程序、帮助进程、node环境、ripgrep搜索工具)。
    * "Cursor.app";"Cursor";"Cursor Helper";"Cursor Helper (Renderer)";"Cursor Helper (GPU)";node;rg
    * ![[../壁纸/附件/Pasted image 20260119164015.png]]
*   **Target Hosts**: (留空)
*   **Target Ports**: (留空)
*   **Action**: **Proxy SOCKS5 127.0.0.1:7897** (选择刚才添加的代理)

**规则 C：默认规则 (Default)**
*   列表最底部的 `Default` 规则。
*   **Action**: **Direct** (保持其他软件正常走公司 VPN 或直连)。

---

### 第三步：Cursor 内部设置 (配合 Proxifier)

既然 Proxifier 已经在外部强制接管了流量，Cursor 内部就不要再填代理了，以免发生“代理套代理”的诡异问题。

1.  打开 Cursor 设置 (`Cmd + ,`)。
2.  搜索 `Proxy`。
3.  **Http: Proxy**: **清空** (留空)。
4.  **Http: Proxy Support**: `off` 或 `override` (设为 off 让它以为是直连，实际上被 Proxifier 劫持了)。
5.  **重要调整**：
    *   虽然 Proxifier 接管了，但为了防止 HTTP/2 在 Clash 里的兼容性问题，建议**依然保持 Network 为 http1.1**。
    *   如果 Cursor 有地方设置 `Http2`，请**禁用**。

---

### 第四步：验证是否生效

1.  打开 Proxifier 主界面，保持窗口可见。
2.  在 Cursor 里随便问 AI 一个问题。
3.  观察 Proxifier 的实时日志：
    *   你应该能看到 `Cursor` 进程发起的连接。
    *   目标是 `api.cursor.sh` 或 `copilot.microsoft.com` 等。
    *   状态应该是 **Sent/Received** 数据，且 Rule 显示为 `Cursor Proxy`。
    *   如果是红色文字 (Failed)，说明 Clash 没通；如果是蓝色/黑色，说明通了。

---

### 总结：为什么这套方案更强？

1.  **穿透性**：Proxifier 运行在应用层和传输层之间，比 VPN 的路由表优先级更高。即使高途 VPN 锁死了网关，Proxifier 也能把 Cursor 的包“偷”出来扔给 Clash。
2.  **SOCKS5 优势**：通过 Proxifier 走 SOCKS5，避免了 HTTP 代理复杂的 Header 处理，减少了 `SSL_ERROR` 的概率。
3.  **HTTP/1.1 策略**：配合你之前的“禁用 HTTP/2”操作，这套组合拳能保证：虽然不是最快的，但是是**绝对不会断连**的。






**是的，一定要重启 Cursor。**

而且不仅是简单的关闭再打开，建议按照以下步骤彻底重启，以确保 Proxifier 能完美接管流量：

### 为什么必须重启？
1.  **清除旧连接**：Cursor 底层（Chromium）维护着一个长连接池。如果你不重启，它还在尝试复用之前那些已经死掉或者走错路由（走了 VPN）的 TCP 连接，会导致依然报错。
2.  **让 Proxifier 注入**：Proxifier 最好的工作方式是在程序**启动的那一刻**就进行劫持。如果 Cursor 已经在运行，Proxifier 有时无法接管已经建立的网络上下文。
3.  **应用配置变更**：你刚才清空了 Cursor 内部的 `Http: Proxy` 设置，只有重启后，Cursor 才会停止自己找代理，乖乖被 Proxifier “绑架”。

### 推荐的重启姿势
1.  **完全退出 Cursor**：
    *   点击 Mac 顶部菜单栏 `Cursor` -> `Quit Cursor` (或 `Cmd + Q`)。
    *   *注意：不要只是点红叉关闭窗口，那样进程还在后台。*
2.  **观察 Proxifier**：
    *   确保 Proxifier 是运行状态（图标在）。
3.  **启动 Cursor**。
4.  **看一眼 Proxifier 的界面**：
    *   当你打开 Cursor 后，Proxifier 的列表里应该立刻跳出 `cursor` 或 `Cursor Helper` 的进程。
    *   如果是 **蓝色** 的字（Proxy SOCKS5 ...），说明接管成功！
    *   如果是 **黄色** 的字（Direct），说明规则没写对，还在直连。

**重启完再试一次，这次应该就稳了。**