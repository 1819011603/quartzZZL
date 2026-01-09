
要找到 [raw.githubusercontent.com](http://raw.githubusercontent.com/) 的 IP 地址，你可以在终端使用以下命令来进行 DNS 查询：

bash复制代码

`nslookup raw.githubusercontent.com`

这将返回 [raw.githubusercontent.com](http://raw.githubusercontent.com/) 对应的 IP 地址。一旦你获得了 IP 地址，你可以将其添加到你的 hosts 文件中，以便手动映射域名到 IP 地址。

在 macOS 或 Linux 中，hosts 文件通常位于 /etc/hosts，在 Windows 中，它位于 C:\Windows\System32\drivers\etc\hosts。你可以用文本编辑器打开这个文件，然后在文件末尾添加一行类似于以下格式的内容：

复制代码

`192.30.253.112 raw.githubusercontent.com`

将 IP 地址替换为你查询到的实际 IP 地址。保存文件后，你应该能够使用这个手动映射的 IP 地址来访问 [raw.githubusercontent.com](http://raw.githubusercontent.com/)。

请注意，在进行此操作之前，请确保你理解了修改 hosts 文件可能带来的潜在风险，并且只从受信任的来源获取 IP 地址。此外，如果 [raw.githubusercontent.com](http://raw.githubusercontent.com/) 的 IP 地址发生了变化，你可能需要定期更新 hosts 文件。