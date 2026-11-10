@echo off
chcp 65001 >nul
schtasks /Delete /TN "seedx-gateway-proxy" /F
echo 已删除登录自启任务 seedx-gateway-proxy（若原本不存在会提示找不到）。
pause
