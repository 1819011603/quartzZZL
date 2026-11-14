@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 goto NONODE
echo seedx 网关代理启动中... 控制面板 http://127.0.0.1:8790 （Ctrl+C 退出）
node start.mjs
echo.
echo 进程已退出。
pause
exit /b 0

:NONODE
echo 未找到 node。请先安装 Node.js 18+ 并加入 PATH: https://nodejs.org/
pause
exit /b 1
