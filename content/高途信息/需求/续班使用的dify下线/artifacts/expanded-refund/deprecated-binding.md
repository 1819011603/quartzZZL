# 降退费当前绑定与生产工作流复核

2026-11-23只读现查；没有生产推理、没有修改路由。此前将 TEST 81e 两轮直接外推生产的表述撤回；旅程两轮也不属于本结论。

## 绑定证据

通过 TEST Apollo JDBC 只读 ai_agent，用查询所得 access_key 在内存调用 Dify `/v1/info`（凭据不输出/落盘）：
- TEST agent `255743632420648960`、app `255743654696597504` → **【废弃】降退费服务建议**，mode `agent-chat`，描述“精品班学部——降退费服务建议”。Console id `spcAm3oupwKuWRMD8UV_c76ff517-b2a6-4476-8171-92af9364e344`。81e两轮话术检索证据只证明这条TEST绑定。

PROD DMS 查询 ai_application/ai_agent 后，在内存使用各agent凭据读取 `/v1/info`，当前确认：
| 生产应用 number | agent number | Dify /info 名称、mode | Console id后缀 |
|---|---|---|---|
|256995990719977472|256995156763347968|【高中】降退费服务建议分析工作流、advanced-chat|5c7ac7f6-af1d-4120-91a5-9a6485fd3d99|
|261424650482886656|261424592068814848|[素养]降退费服务建议分析工作流、advanced-chat|1043df8c-f3d3-44b3-accd-ec2051c0c4a3|
两个生产agent数据库platform_type均为1。Console完整id均加前缀 `spcAm3oupwKuWRMD8UV_`。

## 已发布生产路由

Apollo config-server `/configs/student-data/PROD/application` 当前已发布 `refund.reasoning.suggesstion.dept-agent`：
```json
{"10013429":256995990719977472,"default":256995990719977472,"10012667":261424650482886656,"10019736":261424650482886656}
```
注意map的value实际为 **application number**，不是agent number。默认及10013429命中精品；10012667/10019736命中素养；不是TEST废弃通用应用。该配置只证明路由目标，不证明线上流量/未被其他开关跳过。

## 两个已发布工作流均有检索，但只有一个LLM节点

读取 Console `GET /apps/{id}/workflows/publish`（不是draft）：
- 精品 version `2025-12-03 14:09:25.978047`
- 素养 version `2026-09-21 06:33:31.703225`
- 两者均五节点顺序：start → code → knowledge-retrieval → llm → answer；LLM节点数=1，未见agent工具循环节点。
- code从sys.query用正则抽取 `directReason` 和全部 `categoryName`；缺失置“暂无”，拼成 `退费直接原因:{directReason} 退费原因分类:{categoryNames}`。
- knowledge-retrieval使用code的refundReason，dataset_ids=`[86233d1a-bddf-4a15-a229-c90b6a061c57]`，retrieval_mode=multiple，top_k=4，reranking_enable=false。配置里虽保留gte-rerank-v2，但禁用，不得写为已执行rerank。
- LLM context.enabled=true，variable_selector指向检索节点result；因此知识检索先执行，再将结果送给唯一LLM。
- 精品模型deepseek/DeepSeek-R1-250528，temperature=0.7；素养模型deepseek-v4-flash-0731，temperature=0.7、enable_thinking=true。

原始证据：本目录 `binding-5c7ac7f6-af1d-4120-91a5-9a6485fd3d99-{app,published}.json`、`binding-1043df8c-f3d3-44b3-accd-ec2051c0c4a3-{app,published}.json`、废弃app同名文件。

## 对迁移判断的影响

生产目标不应列为“两次LLM调用场景”：当前已发布图为**前置知识检索+一次LLM生成**。但只迁LLM提示词仍遗漏确定的代码提取、top_k=4检索、context注入步骤；单次LLM不能等同无检索/可直接替换。TEST 81e废弃应用的两轮function calling不是生产工作流的实际执行证据。是否运行时有重试、某次检索命中多少、当前生产流量，未在本轮只读配置检查中证明。
