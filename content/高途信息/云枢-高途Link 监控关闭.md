---
title: 云枢 / 高途Link 监控关闭（保留 VPN）
tags:
  - 高途信息
  - 工作机
  - 安全
date: 2026-09-07
---

# 云枢 / 高途Link 监控关闭（保留 VPN）

> 目标：在个人电脑上，关闭公司客户端「云枢 / 高途Link」的监控 / DLP 功能，**只保留 VPN（网络连接）**，且全部改动**可逆**。
> 手段：把监控相关的 DLL / EXE 改名为 `.disabled`（不删除），需要时可一键改回。

## 一、这是什么软件

- 产品：**GoTuLink（高途Link）** —— 企业零信任 + DLP 终端管控客户端。
  - 主体：`YunShu.exe` / `YunShuNacTool.exe`，签名公司 **Hangzhou Eagle Cloud Security（杭州鹰云安全）**。
- 内嵌：**向日葵（Sunlogin）远程控制 SDK**，签名公司 **上海贝锐信息科技（Oray）**。
  - 文件描述直接写着「向日葵SDK」「SDK被控端桌面Agent程序」「向日葵远程控制」。
- 安装位置：
  - `C:\Program Files\YunShu` —— 主程序 + VPN 隧道 + 向日葵 SDK
  - `C:\Program Files\YunShu Plugin` —— DLP / 监控插件

## 二、组件分类

### 保留（VPN 及必要功能）

| 文件 | 作用 |
| --- | --- |
| `wintun.dll` | WireGuard 虚拟网卡（VPN 核心） |
| `libtunnel32.dll` / `libtunnel32-win7.dll` | VPN 隧道 |
| `YunShu.exe` / `YunShuLauncher.exe` | 主程序 / 启动器 |
| `YunShuNacTool.exe` + `EgNac*` / `CcDot1x` / `CcEap*` | 网络准入 NAC / 802.1x |
| `node.dll`、`libcurl`/`libssl`/`libcrypto`/`zlib` | 运行时 / 网络库 |
| `CcDiskLocker.dll` / `YunShu CryptDisk.exe` | 加密盘（**动它可能打不开加密数据，保留**） |

### 保留（按个人要求：向日葵远程控制不动）

- `slsdk.dll`、`SLDesktopAgent.exe`、整个 `C:\Program Files\YunShu\plugins\`（`sl-client-*` / `sl-control-*`：远程屏幕 / 摄像头 / 麦克风 / 文件 / 命令行 / RDP / SSH）

### 关闭（DLP / 监控，位于 `YunShu Plugin`）

| 文件 / 目录 | 作用 |
| --- | --- |
| `CcMoniter.dll` | 监控主模块 |
| `CcFfmpeg.exe` | 录屏编码 |
| `CcWaterMark*` / `CcFileWatermark.exe` / `CcFileWaterShell*` / `FileWaterMark*` | 屏幕 / 文件水印溯源 |
| `CcProcess.dll` | 进程监控 |
| `CcBrowser.dll` / `CcBrowserPluginManager.dll` | 浏览器监控 |
| `CcDetect.dll` / `CcSoftManage.dll` | 环境检测 / 软件清单 |
| `CcInject*` | 注入 |
| `CcOwl.exe` | 监控 Agent |
| `CcEtw.dll` | 事件追踪 ETW |
| `ImLocate.dll` | 定位 |
| `libChannelSense.dll` | IM 通道识别 |
| `Packet.dll` / `wpcap.dll` | 抓包 |
| `OutlookAddin32/64.dll` / `OutlookPlugin32/64.dll` | 邮件监控 |
| `YunShu dpengine.exe` | DLP 数据防护引擎 |
| `YunShu ScreenLock.exe` | 锁屏 |
| `scanlib\`（目录） | OCR 内容扫描（含 PP-OCRv5 模型） |
| `channel_model\`（目录） | 微信 / 企业微信截图识别模型 |
| `ScriptEngine\`（目录） | 服务端远程下发脚本执行 |

## 三、为什么「关了又自启」

客户端有**自我保护**，是它反复重启的根因：

- `YunShuService`（`YunShu.exe /Service`）常驻服务；
- `AMSProtectedService` —— 基于 **ELAM 的受保护进程（PPL）**，位于 `YunShu Plugin\tbprotect\elam_ppl\`；
- `BzProtect.sys` —— 「Protect Driver」内核自保护驱动；
- `YunShuUpdater.exe` / `YunShu Repair.exe` / `patch.exe` —— 自修复 / 更新，会把改名的文件**还原**。

**因此：正常模式下改名 / 停服务多半会「访问被拒绝」。** 可靠做法是进 **安全模式**（保护驱动 / ELAM 服务不加载）后再执行。

## 四、脚本

桌面：`云枢-关闭监控.bat`（**GBK 编码**保存，避免中文 cmd 乱码 / 吞字节；不要用 `chcp 65001`）。

菜单：

- `[1]` 关闭监控插件（保留 VPN，可恢复）
- `[2]` 恢复监控插件（改回原名）
- `[3]` 完全关闭云枢（含 VPN，仅本次，重启自启）
- `[0]` 退出

原理：`taskkill` 结束监控进程 → 把上表文件 / 目录 `ren` 成 `*.disabled`；恢复即反向 `ren` 回来。

## 五、使用步骤

1. **进安全模式**：按住 `Shift` 点【重启】→ 疑难解答 → 高级选项 → 启动设置 → 重启 → 开机按 `4`。
2. 安全模式里双击桌面 `云枢-关闭监控.bat` → 允许管理员 → 输 `1` 回车 → 看到一排 `[OK]` 即成功。
3. 重启回正常模式，检查两件事：
   - VPN 还能不能连（能连即成功）；
   - `*.disabled` 有没有被「修复 / 更新」还原。

## 六、注意（风险）

- **VPN 可能被判「不合规」而断网**：零信任 / NAC 客户端可能检测到被改动后拒绝放行。无法事先确定，所以脚本保持**可逆**——VPN 断了就跑 `[2] 恢复`。
- **可能被还原**：`YunShuUpdater` / `Repair` 会还原改名文件。要「长期生效」需再禁用更新 / 修复程序，但那一步会加大「被判不合规断网」的风险，需自行权衡。
- 本文档与脚本仅用于**个人自有电脑**上关闭对本人的监控。

## 附：脚本全文

```bat
@echo off
setlocal enableextensions enabledelayedexpansion
title 云枢/高途Link 监控开关（保留VPN）

REM ==== 自动以管理员身份重启 ====
net session >nul 2>&1
if %errorlevel% neq 0 (
  echo 需要管理员权限，正在重新以管理员身份启动...
  powershell -Command "Start-Process -Verb RunAs -FilePath '%~f0'"
  exit /b
)

set "A=C:\Program Files\YunShu"
set "B=C:\Program Files\YunShu Plugin"

:MENU
cls
echo   [1] 关闭监控插件  (保留VPN，可恢复)
echo   [2] 恢复监控插件  (改回原名)
echo   [3] 完全关闭云枢  (含VPN，仅本次，重启后会自启)
echo   [0] 退出
set /p CH=请输入选项并回车:
if "%CH%"=="1" goto DISABLE
if "%CH%"=="2" goto RESTORE
if "%CH%"=="3" goto STOPALL
if "%CH%"=="0" exit /b
goto MENU

:DISABLE
for %%P in ("YunShu dpengine.exe" "YunShu ScreenLock.exe" "CcOwl.exe" "CcFfmpeg.exe" "CcFileWatermark.exe" "aitools.exe") do taskkill /f /im %%~P >nul 2>&1
set OKN=0
set FAILN=0
set ACTION=ren
call :RUNLIST
echo 完成:  成功 !OKN!  失败 !FAILN!  (失败请进安全模式再运行)
pause
goto MENU

:RESTORE
set ACTION=unren
call :RUNLIST
pause
goto MENU

:STOPALL
net stop YunShuService >nul 2>&1
for %%P in ("YunShu.exe" "YunShuLauncher.exe" "YunShu Plugin.exe" "YunShu dpengine.exe" "YunShu ScreenLock.exe" "YunShu Message.exe" "YunShu Diagnosis.exe" "CcOwl.exe" "aitools.exe") do taskkill /f /im %%~P >nul 2>&1
pause
goto MENU

:RUNLIST
REM 向日葵(slsdk / SLDesktopAgent / plugins) 按要求保留，不处理
call :%ACTION% "%B%\CcMoniter.dll"
call :%ACTION% "%B%\CcFfmpeg.exe"
call :%ACTION% "%B%\CcWaterMark.dll"
call :%ACTION% "%B%\CcWaterMark-x64.dll"
call :%ACTION% "%B%\CcFileWatermark.exe"
call :%ACTION% "%B%\CcFileWaterShell.dll"
call :%ACTION% "%B%\CcFileWaterShell-x64.dll"
call :%ACTION% "%B%\FileWaterMark.dll"
call :%ACTION% "%B%\FileWaterMark-client-x64.dll"
call :%ACTION% "%B%\CcProcess.dll"
call :%ACTION% "%B%\CcBrowser.dll"
call :%ACTION% "%B%\CcBrowserPluginManager.dll"
call :%ACTION% "%B%\CcDetect.dll"
call :%ACTION% "%B%\CcSoftManage.dll"
call :%ACTION% "%B%\CcInject.dll"
call :%ACTION% "%B%\CcInject-x64.dll"
call :%ACTION% "%B%\CcOwl.exe"
call :%ACTION% "%B%\CcEtw.dll"
call :%ACTION% "%B%\ImLocate.dll"
call :%ACTION% "%B%\libChannelSense.dll"
call :%ACTION% "%B%\Packet.dll"
call :%ACTION% "%B%\wpcap.dll"
call :%ACTION% "%B%\OutlookAddin32.dll"
call :%ACTION% "%B%\OutlookAddin64.dll"
call :%ACTION% "%B%\OutlookPlugin32.dll"
call :%ACTION% "%B%\OutlookPlugin64.dll"
call :%ACTION% "%B%\YunShu dpengine.exe"
call :%ACTION% "%B%\YunShu ScreenLock.exe"
call :%ACTION% "%B%\scanlib"
call :%ACTION% "%B%\channel_model"
call :%ACTION% "%B%\ScriptEngine"
goto :eof

:ren
set "full=%~1"
if exist "%full%" ( ren "%full%" "%~nx1.disabled" 2>nul && ( echo   [OK]   %~nx1 & set /a OKN+=1 ) || ( echo   [失败] %~nx1 & set /a FAILN+=1 ) ) else ( if exist "%full%.disabled" ( echo   [已关] %~nx1 ) else ( echo   [无] %~nx1 ) )
goto :eof

:unren
set "full=%~1"
if exist "%full%.disabled" ( ren "%full%.disabled" "%~nx1" 2>nul && echo   [已恢复] %~nx1 ) else ( if exist "%full%" ( echo   [本就在] %~nx1 ) else ( echo   [无] %~nx1 ) )
goto :eof
```
