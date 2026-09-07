#!/bin/bash
# yunshu-gui.sh —— 给 Alfred / 双击 用:弹出 macOS 图形授权框,以 root 跑 yunshu-toggle.sh
# 用法: yunshu-gui.sh on|off|status
ACTION="${1:-status}"
TOGGLE="$HOME/yunshu-toggle.sh"

# status 不需要 root,直接跑并把结果弹通知
if [ "$ACTION" = "status" ]; then
  RESULT="$("$TOGGLE" status 2>&1)"
  osascript -e "display notification \"$RESULT\" with title \"云枢管控\""
  echo "$RESULT"
  exit 0
fi

# on/off 需要 root:弹图形密码框,授权后以 root 执行
RESULT=$(osascript -e "do shell script \"'$TOGGLE' $ACTION\" with administrator privileges" 2>&1)
osascript -e "display notification \"$RESULT\" with title \"云枢管控 · $ACTION\""
echo "$RESULT"
