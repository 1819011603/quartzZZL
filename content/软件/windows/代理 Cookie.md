
	代理 Cookie 登录 
```
-s -k -x http://127.0.0.1:8888 
  
python3 /Users/gaotu/bridge/payload/cookie-agent/agent_cookie_proxy.py &





```

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "G:\cursorProject\pythonManage\chrome-extension\agent\start_windows_cookie_services.ps1"

```




### https不通 没有证书 

1. 导入 mitmproxy 证书到当前用户 Root：

```
certutil -user -addstore Root "G:\cursorProject\pythonManage\chrome-extension\agent\.mitmproxy-windows\mitmproxy-ca-cert.cer"
```

2. 再导入到本机 Root，可能需要管理员 PowerShell：

```
certutil -addstore Root "G:\cursorProject\pythonManage\chrome-extension\agent\.mitmproxy-windows\mitmproxy-ca-cert.cer"
```

3. 重开一个 PowerShell，再试：

```
curl.exe --ssl-no-revoke -I -L --max-time 20 -x http://127.0.0.1:8888 "https://www.bilibili.com/video
```