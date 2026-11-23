# 退费剩余场景扩大验证（TEST）

- 环境：`test-gtbg-dev-1`，`compareAiApplication` 串行双路，commit `91012878`；同一输入、`clazzNumber=500775385189890048`、`userId=7404351741`、`commTag=0`。
- 输入包含高中学部、春季数学班、学员李明、主讲王老师/辅导陈老师、两段带时间的沟通原文、正确率 85%→62%、课程体验 5/10、NPS 3/10、家长“考虑退费/增加答疑和针对性练习可能继续”。完整响应保存在本目录 1~5 JSON。

| 场景 | Dify messageId | 网关 messageId | 结果 |
|---|---|---|---|
| 退费旅程分析 | `cc31e065-40a1-4292-958d-30eda7c277b7` | `c9335c5b-42d6-4418-839e-760e051ce0d0` | 两侧成功；网关 `litellm_proxy/deepseek-v4.1-flash`，输出 tutoringSummary/tutoringItems |
| 退费课程体验分析 | `f5443e35-868e-4607-ad09-5b1cc573265d` | `c2512c21-8fea-48e7-b3e0-aaf9629cc7f4` | 两侧成功；输出 courseExperienceSummary |
| 退费NPS分析 | `2c46f2e3-d3ab-4d7c-b5ae-a7512886279d` | `fa98c35e-5d23-4b47-9e53-4f9773a64b1d` | 两侧成功；本班级分析与其他班级暂无数据均有返回 |
| 降退费服务建议 | `2abf8686-086f-4fd1-b92e-43b3bf101189` | `419e58d2-8b5f-49cb-998e-bb0b5c7e9096` | 两侧成功；网关 JSON 合法 |
| 素养服务建议 | `e1cc0e7d-a570-4b57-8273-1305e9297349` | `7dbd83e7-e8db-41c6-b7b6-806185e04371` | 两侧成功；网关 JSON 合法 |

## Dify 隐含处理与差异

降退费 Dify answer 明确出现两段 `<think>`，并写出 “Let me use the tool / query the tool”，说明旧工作流提示词要求工具/话术库处理；但 `compareAiApplication` 返回协议只有 `event/messageId/answer`，没有 `tool_calls`、工具消息或多轮 messages，因此本次证据只能确认 Dify 生成了工具调用意图，不能证明工具实际命中或返回了知识库内容。网关侧为单段 JSON answer，未见 tool_calls/tool message；迁移后工具能力若是业务必需，需在代码或网关链路另行实现/核对，不能把“无知识库内容”当作等价。

Dify 与网关均能读出班级、学员、老师、时间、原话及体验/NPS；结果内容有模型随机性和格式差异（Dify 常带 think，网关为纯 JSON），不能以文本完全相同判断等价。NPS 场景网关返回纯文本而非 JSON，符合该应用不应强制 `response_format=json_object` 的约束。

## 学部映射覆盖边界

已读取的迁移提示词归档：`artifacts/dify-refund-prompts/`。精品/素养的旅程、课程体验、退费根因三对文件逐行相同；降退费工作流仅多一行 `//`，无业务规则差异。TEST 实际验证的 6 个应用为通用“退费旅程/课程体验/NPS/降退费/素养服务建议”及退费根因（既有证据），而生产是五类场景各有精品、素养两个变体，共 10 个应用。故本轮 5 个调用覆盖每类至少一个 TEST 应用和一个高中样例，不能宣称生产 10 个变体全部通过；未直接验证的至少包括精品/素养各自的独立 ai_application 路由、应用级 prompt 是否逐个绑定，以及生产 10 个 app 的模型/参数配置。当前输入也没有真实沟通记录 ID/多班级数据，无法验证沟通记录查询、学部映射、跨班级 NPS 聚合。

## 风险结论

迁移主流程在 TEST 五场景均返回成功且语义字段可解析；主要风险是旧 Dify 工作流可能依赖工具/知识库/多轮上下文，而当前 compare 响应未暴露这些中间交互，需保留为未覆盖项。另有生产 10 变体未逐 app 验证、真实沟通 ID/跨班级数据未覆盖、模型输出随机性和 Dify think/网关纯 JSON 格式差异。

## LiteLLM TEST 实收日志（补证）

按网关响应 messageId 反查下游 TID，完整 SLS 原文保存为 `llm-full-*.log`。五条均有 LiteLLM `Chat_completion request` 与 `Response received by LiteLLM`，请求均为 `roles=[system,user]`、无 `tools` 字段、无 tool message；响应中 `tool_calls=null` 只是 OpenAI response 字段，不能证明发生工具调用。请求参数如下：

| messageId | LiteLLM TID | request model | max_tokens | temperature | system/user 长度 |
|---|---|---|---:|---:|---:|
| c9335c5b… | bfd44413-31f5-493d-904b-e670783ff2c4.0.3 | deepseek-flash（响应重定向 deepseek-v4.1-flash） | 8192 | 未传 | 3290/302 |
| c2512c21… | e02d7092-ee55-4e73-b731-b6f31ef2fb6e.0.3 | deepseek-flash（响应重定向 deepseek-v4.1-flash） | 8192 | 未传 | 2621/302 |
| fa98c35e… | d2003cc1-b573-4e1c-8918-d3a4d162fe62.0.3 | deepseek-flash（响应重定向 deepseek-v4.1-flash） | 8192 | 未传 | 473/302 |
| 419e58d2… | 81e849b4-d461-4fd0-910a-154368d68bc0.0.3 | deepseek-flash（响应重定向 deepseek-v4.1-flash） | 8192 | 未传 | 1613/302 |
| 7dbd83e7… | 5e258635-6bba-4358-bb49-8c6017142140.0.3 | deepseek-flash（响应重定向 deepseek-v4.1-flash） | 8192 | 0.7 | 1613/302 |

system prompt SHA-256 前 16 位依次为 `5e4cdf747536288a`（旅程）、`cd46c259f2fc4518`（课程体验）、`ad64c97078da1d28`（NPS）、`d0e57bd388f5dede`（降退费/素养服务，两者相同）。这确认网关实际收到应用级完整提示词；请求层没有 Dify 多轮工具调用或 tool 消息。旧侧现已按完整TID取得LiteLLM请求，逐字段对照以原始日志为依据。

## 当前原始日志核对结论

主Worker直接解析原始日志：降退费 `81e849b4-d461-4fd0-910a-154368d68bc0.0.3` 有两轮请求，第二轮回灌2条tool内容，长度1363/1152；新路无tools，确认检索遗漏。

退费旅程 `prod-tid-cc31e065-full.log` 只有1条LiteLLM请求，无tools，system为旅程指令。此前把降退费两轮证据用于旅程的结论错误，已删除。课程体验、NPS、素养服务建议各已取得1条旧侧请求，当前样本无tools；不外推全部线上流量。

旧侧完整请求已取得，不存在此前所称的已确认日志字段缺失。素养旧侧仅system，新侧system+user；精确正文与参数差异正在由原始日志独立提取，不以角色数量判断指令丢失。
