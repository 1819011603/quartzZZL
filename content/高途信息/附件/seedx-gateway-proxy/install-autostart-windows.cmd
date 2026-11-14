@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "NODE="
for /f "delims=" %%i in ('where node') do set "NODE=%%i"
if "%NODE%"=="" goto NONODE
schtasks /Create /TN "seedx-gateway-proxy" /TR "wscript.exe \"%~dp0start-hidden.vbs\"" /SC ONLOGON /RL LIMITED /F
if errorlevel 1 goto FAILED
echo 已创建登录自启任务（静默，不弹窗口）：seedx-gateway-proxy
goto DONE

:NONODE
echo 未找到 node，请先安装 Node.js 18+ 并加入 PATH。
echo 也可在「任务计划程序」手动添加：登录时运行 node "%~dp0start.mjs"
goto DONE

:FAILED
echo 创建失败。可改用「任务计划程序」手动添加：登录时运行 wscript "%~dp0start-hidden.vbs"

:DONE
pause
