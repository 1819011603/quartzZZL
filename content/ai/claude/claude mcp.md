```bash
# 关
claude mcp remove rocketmq-apply -s user
claude mcp remove qiwei-sidebar -s user
# 要用时加回
claude mcp add rocketmq-apply -s user -- /Users/gaotu/.local/mcp-servers/venv/bin/python /Users/gaotu/.local/mcp-servers/rocketmq_apply.py
claude mcp add qiwei-sidebar  -s user -- /Users/gaotu/.local/mcp-servers/venv/bin/python /Users/gaotu/.local/mcp-servers/qiwei_sidebar.py
```



```

/mcp                      打开交互面板，看全部 server + 连接状态，直接切
/mcp enable  <名字>        开
/mcp disable <名字>        关
/mcp enable  all          全开（省略名字默认就是 all）
/mcp reconnect            重连

```

![[../../壁纸/附件/Pasted image 20260817163604.png]]
```

改法（按收益排序，都不要求你少读代码）
在任务边界 /clear（省 ~75%）。改完一个 bug、发完一次布、结束一个排查 → clear。不是"少读代码"，是"别在一个会话里干完一整天"。727 轮那次显然是好几件事连在一起。

调换探索与动手的顺序，中间切一刀。如果流程是"查日志/跑 SQL 定位 → 改代码"，查完后 clear 一次，只把结论带进新会话。否则排查阶段那些日志噪音会被后面每一轮改代码重读。

合并 Bash 调用。1272 次里很多能一条命令干几件事。省的不是那一次的 1.5KB，是它之后被重读的几百次。（我这次分析自己就跑了太多次 strings，同样的毛病。）

探索类任务交给 subagent。15 个会话里 sidechain = 0 次，你从来没用过。全仓 grep 找符号这类噪音大、结论小的活，交给 Explore subagent，噪音留在 subagent 的上下文里，主会话只拿结论。但你配置里明确写了禁止我主动调 Agent——这条要你放开我才会用。
```