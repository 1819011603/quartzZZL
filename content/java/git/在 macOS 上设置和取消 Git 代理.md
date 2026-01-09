

1. **设置 HTTP 代理**: 要设置 HTTP 代理，请在终端中运行以下命令：
		git config --global http.proxy http://proxy_username:proxy_password@proxy_ip:proxy_port
2.  **检查代理设置**: 要检查代理设置是否正确，请在终端中运行以下命令：
		git config --global --get http.proxy
1. **取消 HTTP 代理**: 要取消 HTTP 代理，请在终端中运行以下命令：
		git config --global --unset http.proxy
