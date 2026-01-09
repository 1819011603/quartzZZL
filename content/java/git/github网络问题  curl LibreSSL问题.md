
## 步骤
1. 打开VPN
2. https://raw.githubusercontent.com/  失败 使用设置HOMEBREW_FORCE_BREWED_CURL为1
3. 非 https://raw.githubusercontent.com 网站失败， 关闭IPV6 networksetup -setv6off Wi-Fi


> curl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to raw.githubusercontent.com:443
Error: git-lfs: Failed to download resource "readline.rb"
Download failed: https://raw.githubusercontent.com/Homebrew/homebrew-core/4ce23575e17d6097d0c45bb65eaea6f611eb90a1/Formula/r/readline.rb


stackOverFlow:  https://stackoverflow.com/questions/48987512/ssl-connect-ssl-error-syscall-in-connection-to-github-com443


1. 设置HOMEBREW_FORCE_BREWED_CURL为1，默认为空字符串, 问题得到解决
```shell
 ⚙ gaotu@gaotudeMacBook-Pro-8  ~/Documents/日志  export | grep HOMEBREW_FORCE_BREWED_CURL
HOMEBREW_FORCE_BREWED_CURL=''
 ⚙ gaotu@gaotudeMacBook-Pro-8  ~/Documents/日志  export HOMEBREW_FORCE_BREWED_CURL=1
 ⚙ gaotu@gaotudeMacBook-Pro-8  ~/Documents/日志  export | grep HOMEBREW_FORCE_BREWED_CURL
HOMEBREW_FORCE_BREWED_CURL=1
```

> 原因： 
> HOMEBREW_FORCE_BREWED_CURL这个环境变量是用于指示Homebrew (一个在Mac上的软件包管理器)，强制使用Homebrew自己安装的cURL工具，而不是使用系统默认的cURL工具。
> cURL是一个基于libcurl的命令行工具，用于从或者向服务器传输数据，支持http，https，ftp等多种协议。
> 将这个环境变量设置为1可以确保使用的是最新的、包含所有特性的cURL工具，可能可以解决某些由于系统自带的cURL版本过低导致的问题。但是，这可能会导致系统中的其他依赖于老版本cURL的软件出现问题。


2. 关闭IPV6  这个没试验过
	1. 关闭： networksetup -setv6off Wi-Fi
	2. 开启IPV6： networksetup -setv6automatic Wi-Fi

	
	3. 关闭IPV6的缺点:
		1. 访问IPV6网络站点的能力会受到影响：如果某网站只支持IPV6访问，关闭了IPV6的设备将无法访问这个网站。
		2. 网络性能可能会降低：IPV6比IPV4具有更好的路由和自动配置能力，可以提高网络性能和稳定性。
		3. 增加网络安全风险：大部分现代防火墙和安全设备都针对IPV6做过优化处理，如果关闭IPV6，某些安全防护措施可能不能发挥作用。


4. 设置IP和域名绑定  <mark class="hltr-purple">效果不稳定</mark>
	1. nslookup raw.githubusercontent.com DNS查看IP地址
	2. sudo vim /etc/hosts   修改
			![[Pasted image 20240109165319.png]]

