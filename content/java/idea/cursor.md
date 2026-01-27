
快捷键

Option+Shift+O


### windows 

快捷键 

![[../../壁纸/附件/Pasted image 20260109231656.png]]



### mitmproxy  


```

# 1. 停止现有代理
cd C:\Users\Administrator\mitmproxy
.\stop_proxy.bat

# 2. 激活环境并启动带脚本的代理
conda activate mitmproxy-env
mitmweb -s cursor_rewrite.py --set confdir=C:\Users\Administrator\mitmproxy



$env:HTTP_PROXY="http://127.0.0.1:8080"; $env:HTTPS_PROXY="http://127.0.0.1:8080"
 .\cursor_token_updater.exe
```



```
# 取消代理环境变量
$env:HTTP_PROXY = ""
$env:HTTPS_PROXY = ""

# 或者使用 Remove-Item 完全删除
Remove-Item Env:HTTP_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue
```


```


$env:HTTP_PROXY="http://127.0.0.1:8080"; $env:HTTPS_PROXY="http://127.0.0.1:8080"

netsh winhttp set proxy 127.0.0.1:8080



cd C:\Users\Administrator\mitmproxy

.\start_proxy.bat

 .\stop_proxy.bat

重写逻辑在 C:\Users\Administrator\mitmproxy\cursor_rewrite.py
```

![[../../壁纸/附件/mitmproxy.zip]]
![[../../壁纸/附件/cursor_token_updater.zip]]

![[../../壁纸/附件/mitmproxy_mac.zip]]

###  macos

![[../../壁纸/附件/Pasted image 20260123174100.png]]
```

# 进入项目目录
cd /Users/gaotu/cursorProject/mitmproxy

# 启动代理
./start_proxy.sh

# 测试代理
./test_proxy.sh

# 停止代理
./stop_proxy.sh

# 安装证书 (首次 HTTPS 拦截需要)
./install_cert.sh

# 开启系统代理 (Wi-Fi)
networksetup -setwebproxy "Wi-Fi" 127.0.0.1 8080
networksetup -setsecurewebproxy "Wi-Fi" 127.0.0.1 8080

# 关闭系统代理
networksetup -setwebproxystate "Wi-Fi" off
networksetup -setsecurewebproxystate "Wi-Fi" off
```


```

open  /Users/gaotu/cursorProject/mitmproxy/cursor_accounts.json
open /Users/gaotu/cursorProject/mitmproxy/rewrite_rules.json

export https_proxy=http://127.0.0.1:8080 http_proxy=http://127.0.0.1:8080  all_proxy=socks5://127.0.0.1:8080

./cursor_token_updater_arm\ \(1\)


export https_proxy=http://127.0.0.1:7897 http_proxy=http://127.0.0.1:7897 all_proxy=socks5://127.0.0.1:7897
```


![[../../壁纸/附件/claude_code_updater_arm.zip]]

![[../../壁纸/附件/cursor_token_updater_arm (1).zip]]