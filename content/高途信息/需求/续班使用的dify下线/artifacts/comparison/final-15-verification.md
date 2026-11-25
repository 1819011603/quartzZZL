# 15场景TEST当前验证

范围13非知识库＋2降退费workflow，两个403问题建议排除。15项完整输入、输出、旧新HTTP和trace已汇总到final-15-comparisons.json；逐项复算messages均相等；有效thinking不能由入口省略字段推定，画像、摘要及两分层当前生产配置TEST基准有效thinking已闭合。当前代码47b3dcb7，普通链路复用263ba48a有效证据，不宣称最新版本全量重跑。

|项目|当前结论|证据|
|---|---|---|
|用户画像|当前生产目标模型TEST旧新messages相等，两侧推理开启1593/753|profile-direct-baseline/；新3fce4abd-3895-4b68-bb90-54777ac6d680.0.3|
|沟通摘要|完整messages相等，有效thinking相等；旧/新tokens 806/751|thinking-related/result.json；新trace 66c8b9fa-a1d0-4fa2-a305-6e24548ef9ce.0.3|
|服务SOP|messages逐字相等；非消息差异：model,response_format,user|final-15-comparisons.json；新trace c2b1755e-1ceb-4859-8488-423c73f52b03.0.3|
|高中分层|完整messages相等，有效thinking相等；旧/新tokens 0/0|thinking-related/result.json；新trace c08756d7-169f-4a84-89c3-1b825f63ac04.0.3|
|精品根因|messages逐字相等；非消息差异：model,user|final-15-comparisons.json；新trace aa02540f-30a8-40cd-816d-138168507e69.0.3|
|精品旅程|messages逐字相等；非消息差异：user|final-15-comparisons.json；新trace 1ae3e73d-c337-4b7e-9f88-4be4f6d580c2.0.3|
|精品课程体验|messages逐字相等；非消息差异：model,user|final-15-comparisons.json；新trace 3a622047-d7a6-469d-89f5-778770a36f1f.0.3|
|精品NPS|messages逐字相等；非消息差异：model,user|final-15-comparisons.json；新trace db72f1f1-90c6-458a-a8f0-047bfdf501c1.0.3|
|素养分层|完整messages相等，有效thinking相等；旧/新tokens 0/0|thinking-related/result.json；新trace 95d2fb8f-d462-4449-839e-b6123dca4b16.0.3|
|素养根因|messages逐字相等；非消息差异：user|final-15-comparisons.json；新trace 1b812e6a-3ef7-4399-b2e4-47b2d5f88b15.0.3|
|素养旅程|messages逐字相等；非消息差异：user|final-15-comparisons.json；新trace 7c633ac1-66ed-4e74-9634-ab8ce0bcf9cb.0.3|
|素养课程体验|messages逐字相等；非消息差异：user|final-15-comparisons.json；新trace f018e314-4756-49c3-9660-7c2b6d216317.0.3|
|素养NPS|messages逐字相等；非消息差异：user|final-15-comparisons.json；新trace 1eea85d3-3535-460e-995d-1b66df8f8956.0.3|
|高中降退费|messages逐字相等；非消息差异：user|final-15-comparisons.json；新trace dcec0f6e-0074-4169-b3b1-323e98187ba8.0.3|
|素养降退费|messages逐字相等；非消息差异：user|final-15-comparisons.json；新trace e04638d2-48f8-4937-a9e2-8102755c45ce.0.3|

四组thinking有限验收已闭合：画像1593/753开启、摘要806/751开启、两分层0/0关闭。分别沿当前生产生成配置TEST副本验证；画像摘要不保留实验disabled，两分层显式disabled保留旧别名有效行为。完整请求响应见profile-direct-baseline及thinking-related，历史实验只留底层证据。

参数差异明确保留：model为已核实替代映射；旧Dify user为EndUser标识，不复制；部分豆包新侧显式response_format=text而旧侧省略。不是全HTTP字节相等，也不要求随机输出逐字一致。

素养NPS正确证据为普通syncRequestTask trace 1eea85d3；此前acc2dcbd为V2错误包装反例，已退出当前矩阵。未为此修改代码配置。

退款自动身份：真实refundReasoningEvent trace 611aeb2f，未传RunUser，handleCode=2并返回answer/usage（906 tokens）。发送头gongxuemeng；watch完整body与同trace下游HTTP相等。watch MDC为空，使用完整body精确关联，不冒称MDC捕获。见refund-identity-association.json及退款原始证据。TEST fixture ees_data.service_nps_submit id30339441/nps_id7530633600362874300，已回读且被本次上下文消费。

SOP自动身份已同trace验证，完整HTTP见sop-auto-http.json。workflow代表性补证trace ec09563e：高中隔离库检索→生成成功、头gongxuemeng，watch与同traceHTTP全等；该入口显式runUser，不作为自动老师来源证明。素养workflow复用相同retrieveWorkflowAndComplete→LlmGatewayAccessor费用头路径，独立messages/参数对照仍使用其既有实测。

两workflow仅证明同隔离TEST库、同输入、替代模型的迁移行为；旧新模板都未把检索片段注入LLM消息，不代表生产召回等价或知识增强。生产未生成/切换/改知识内容。无新代码提交部署，无README飞书修改。Arthas已reset并stop，无在途操作。
