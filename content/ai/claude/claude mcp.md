```bash
# 关
claude mcp remove rocketmq-apply -s user
claude mcp remove qiwei-sidebar -s user
# 要用时加回
claude mcp add rocketmq-apply -s user -- /Users/gaotu/.local/mcp-servers/venv/bin/python /Users/gaotu/.local/mcp-servers/rocketmq_apply.py
claude mcp add qiwei-sidebar  -s user -- /Users/gaotu/.local/mcp-servers/venv/bin/python /Users/gaotu/.local/mcp-servers/qiwei_sidebar.py
```

