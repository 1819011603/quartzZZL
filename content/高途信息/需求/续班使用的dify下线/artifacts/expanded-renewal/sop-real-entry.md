# SOP真实V2执行器补验

2026-11-23，代码基线91012878d692119e79fb7d14baa1bab594c9534d，TEST test-gtbg-dev-1。未改公共配置或代码。已完成真实历史fixture经实际业务使用的syncRequestTaskV2双路重放；不是generate外围完整业务流程验收。

## 结论
两侧LiteLLM实收均为单条user，内容与同一fixture **13647字符逐字相等**。包含核心长指令、上下文以及“下面是已知的SOP服务要求”中的问卷、家长会等具体服务规则，无长指令丢失。此前compare普通入口的system/user差异不能直接套用于SOP实际V2路径。

|路径|traceId|结果|
|-|-|-|
|Dify，PROD/SLS/app查下游|315c294d-dbc3-4d8f-adc6-e036ad96d1e1.0.3|单user，全文相等，10项SOP|
|迁移，TEST/SLS/app查下游|2b757fa1-ac59-4cbd-aac5-1260f6bcba8a.0.3|单user，全文相等，10项SOP|

业务调用均经TEST桥，只读PROD日志。仅service=litellm的Chat_completion request作实收依据。

## fixture及证据
TEST ees_data.ai_application_call_task_result中应用256327049255322624、actual_query包含已知SOP要求的最新记录，entry_key=290324465057804288。完整原文sop-v2-fixture.json。两个请求均原样使用此actual_query，分别platformType=1/2；入口AiApplicationExecutor#syncRequestTaskV2。context为测试样本，但V2提示词不重新生成，不能把fixture历史用户等同本次context用户。

sop-v2-{1,2}-request.json/headers.txt/response.json保留调用；logs.txt保留日志及response usage；received.json为实收，sop-v2-verification.json记录逐字比较、角色、参数、usage、解析项数。

## 剩余参数差异
Dify实收model=doubao/Doubao-Seed-1-6、stream=true、有user；新路model=doubao-seed-2-0-lite-260428、response_format=json_object、stop=[]、max_tokens=8192，无显式stream/user。模型别名是否最终落同一路由须结合redirect配置，当前全文相等不能证明模型参数等价。

两侧均有推理消耗：旧reasoning_tokens=1764，新1896；旧prompt_tokens=7646，新7777。提示词逐字一致而token数不同，不能据token数断言提示词丢失。completion_tokens分别2717/2782，未达到新路8192上限。

## 结果与边界
去think和代码围栏后，两侧均可JSON解析，sopAnalysisItemList各10项；证明此fixture结构兼容，不证明随机输出逐项质量等价。完整响应供复核。

实际代码AiSopAnalysisGenerator.generate先buildUserQuery（读取知识表），DynamicPromptGenerator.generate生成actualQueryPrompt，再syncRequestTaskV2；执行器executeCoreLogicV2使用AiPromptPayload.ofFlat，不重新拆分system/user。本次重放覆盖该V2核心执行和真实长提示词传递，不覆盖部门选择、二讲账号门槛、MD5去重、知识表实时读取、generate最终档案写回。没有为双路切换修改公共Apollo，也未调用generate更新履约档案；调用正常产生TEST AI调用任务记录。

## 调用时间与后续归属
- 路径1 LiteLLM实收时间：2026-11-23 19:29:00,818（日志时间，中国时区）。参数以sop-v2-1-received.json为准。
- 路径2 LiteLLM实收时间：2026-11-23 19:29:01,243（日志时间，中国时区）。参数以sop-v2-2-received.json为准。
后续thinking配置核实及可能的TEST修改/复验由W1-d5f701负责。本轮不重跑，不将后续配置变化追溯为此次调用的参数。
