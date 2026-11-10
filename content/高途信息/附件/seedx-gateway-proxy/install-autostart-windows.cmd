@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
for /f "delims=" %%i in ('where node') do set "NODE=%%i" & goto :got
:got
if "%NODE%"=="" (
  echo 未找到 node，请先安装 Node.js ^>=18 并加入 PATH。
  pause
  exit /b 1
)
schtasks /Create /TN "seedx-gateway-proxy" /TR "\"%NODE%\" \"%~dp0start.mjs\"" /SC ONLOGON /RL LIMITED /F
if errorlevel 1 (
  echo 创建失败。可改用「任务计划程序」手动添加：登录时运行  "%NODE%" "%~dp0start.mjs"
) else (
  echo 已创建登录自启任务：seedx-gateway-proxy
)
pause
