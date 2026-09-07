#!/bin/bash
# yunshu-toggle.sh —— 按需开关 EagleYun 云枢管控(个人电脑临时办公用)
# 用法:  sudo ./yunshu-toggle.sh on|off|status
#   on   : 干活前打开(内网/零信任访问需要它)
#   off  : 干完关掉,私人时间不采集
#   status: 看当前是否在跑
#
# 它有两个特权守护互相看门(servicemanager + helper),只停一个会被
# 另一个秒级复活。off 先 disable 两个、再一起 bootout、杀进程,最后连
# 前台 App 一起收掉;on 反向恢复。不删不改文件,可逆。

DAEMON_SM=com.eagleyun.sase.servicemanager
DAEMON_HP=com.eagleyun.sase.helper
PLIST_SM=/Library/LaunchDaemons/com.eagleyun.sase.servicemanager.plist
PLIST_HP=/Library/LaunchDaemons/com.eagleyun.sase.helper.plist
AGENT_PLIST=/Library/LaunchAgents/com.eagleyun.endpoint.agent.plist
APP=/Applications/Yunshu.app
# 当前图形登录用户(sudo 或 图形授权 下都能正确取到)
REAL_UID=$(stat -f%u /dev/console)

need_root() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "请用 sudo 运行:  sudo $0 $1"; exit 1
  fi
}

status() {
  if pgrep -f /opt/.yunshu/YunshuManager.app >/dev/null 2>&1; then
    echo "云枢状态: 运行中 ●  (pid: $(pgrep -f /opt/.yunshu/YunshuManager.app | tr '\n' ' '))"
  else
    echo "云枢状态: 已停止 ○"
  fi
}

stop() {
  need_root off
  echo "→ 停止云枢:先禁用两个守护,阻断互相复活..."
  launchctl disable system/$DAEMON_HP 2>/dev/null
  launchctl disable system/$DAEMON_SM 2>/dev/null
  echo "→ 踢出 launchd 守护..."
  launchctl bootout system/$DAEMON_HP 2>/dev/null
  launchctl bootout system/$DAEMON_SM 2>/dev/null
  launchctl bootout "gui/$REAL_UID/com.eagleyun.endpoint.agent" 2>/dev/null
  echo "→ 收掉前台 App 与残留进程..."
  # 动态踢掉用户会话里所有 eagleyun 图形任务(前台 App 的 label 带随机数字后缀)
  for lbl in $(launchctl asuser "$REAL_UID" launchctl list 2>/dev/null | awk '/eagleyun|yunshu/{print $3}'); do
    launchctl bootout "gui/$REAL_UID/$lbl" 2>/dev/null
  done
  pkill -9 -f /opt/.yunshu 2>/dev/null
  pkill -9 -f "Yunshu.app" 2>/dev/null
  pkill -9 -f com.eagleyun 2>/dev/null
  sleep 2; status
}

start() {
  need_root on
  echo "→ 启动云枢:重新启用并加载两个守护..."
  launchctl enable system/$DAEMON_SM 2>/dev/null
  launchctl enable system/$DAEMON_HP 2>/dev/null
  launchctl bootstrap system "$PLIST_SM" 2>/dev/null
  launchctl bootstrap system "$PLIST_HP" 2>/dev/null
  [ -f "$AGENT_PLIST" ] && launchctl bootstrap "gui/$REAL_UID" "$AGENT_PLIST" 2>/dev/null
  echo "→ 拉起前台 App..."
  [ -d "$APP" ] && sudo -u "#$REAL_UID" open -a "$APP" 2>/dev/null
  sleep 2; status
}

case "$1" in
  on|start)  start ;;
  off|stop)  stop ;;
  status|"") status ;;
  *) echo "用法: sudo $0 {on|off|status}"; status ;;
esac
