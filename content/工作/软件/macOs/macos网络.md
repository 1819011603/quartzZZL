
重启网络




sudo ifconfig en0 down
sudo ifconfig en0 up

sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

# DHCP

- 打开“系统偏好设置”，可以通过点击屏幕右上角的苹果图标，然后选择“系统偏好设置”。
- 在系统偏好设置窗口中，点击“网络”。
- 在网络设置窗口左侧的网络连接列表中，选择你正在使用的网络连接，比如Wi-Fi或以太网。
- 在网络连接的右侧，点击“高级”按钮。
- 在高级设置窗口中，切换到“TCP/IP”选项卡。
- 点击“使用DHCP”旁边的“释放DHCP租约”按钮。
- 在释放租约后，点击“将DHCP租约分配给当前位置”。
- 点击“确定”来保存设置。
- 现在，你的macOS设备会向DHCP服务器请求新的IP地址