
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

![[../../壁纸/附件/mitmproxy 2.zip]]
![[../../壁纸/附件/cursor_token_updater.zip]]