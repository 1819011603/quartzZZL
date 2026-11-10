#!/bin/bash
# macOS 双击启动：Finder 里双击本文件即可（首次可能需右键→打开 绕过 Gatekeeper）
cd "$(dirname "$0")" || exit 1
if ! command -v node >/dev/null 2>&1; then
  for p in /usr/local/bin/node /opt/homebrew/bin/node "$HOME/.nvm/versions/node"/*/bin/node; do
    [ -x "$p" ] && export PATH="$(dirname "$p"):$PATH" && break
  done
fi
echo "seedx 网关代理启动中…… 控制面板：http://127.0.0.1:8790 （Ctrl+C 退出）"
exec node start.mjs
