# SOP服务规则与Dify检索边界补充

结论：不能因为代码出现“知识库配置”字样，就把SOP排除。本次SOP V2证据支持**业务端已读取并拼入的服务规则完整保留，旧新完整messages一致**。它与迁移会丢失的Dify额外dataset检索是两件事。按已验证样本，SOP无需因这份服务规则输入而排除，可沿输入一致口径收束。

## 已确认链路

部署提交91012878的`AiSopAnalysisGenerator`：
- `buildUserQuery`通过`tableApiDataHolder.getTableData(getKnowledgeBaseConfigByDepartment(...))`读取规则，拼入“##下面是已知的SOP服务要求”及JSON围栏；读取发生在student-data调用Dify或网关之前。
- `generate`先调用上述buildUserQuery，再`DynamicPromptGenerator.generate`生成完整flat，随后`syncRequestTaskV2(actualQueryPrompt,...)`。
- 两路V2均消费同一flat；此次迁移未删除上述规则取数逻辑。因此不能将其当作“绕开Dify后消失的前置dataset节点”。

## 实收直接证据

`expanded-renewal/sop-v2-1-received.json`（旧trace315c294d-dbc3-4d8f-adc6-e036ad96d1e1.0.3）和`sop-v2-2-received.json`（新trace2b757fa1-ac59-4cbd-aac5-1260f6bcba8a.0.3）：
- 都为单条真实user；content13647字符，完整messages逐字段相等，规范序列化15002字符。
- “下面是已知的SOP服务要求”在两侧content offset1368（0起始），其中规则正文随整段逐字符相等得到验证。
- 两侧实际请求均无tools；原始日志各观察一条Chat_completion request。旧请求未出现新请求缺失的额外dataset文本或工具结果。
- 证据覆盖真实历史fixture的V2核心执行；无需为补清知识库定义再重跑。

## 配置证据诚实边界

本轮可定位的既有`/private/tmp/dify-current-app.json`属于“续班AI-用户画像&沟通摘要-test”，不是SOP，**没有挪用它证明SOP dataset关闭**。现有SOP归档未找到可独立复核的完整model_config dataset配置快照，故不写“已核实SOP所有版本永远无dataset”。

这不推翻本样本的直接实收结论：旧新完整messages相等且无tools，服务规则没有因迁移丢失。缺少全量配置快照只是不能外推其他Dify版本/生产模板的边界，不新增为本次输入一致验收门槛。主Worker若已有SOP配置快照可附加引用，本子任务不泛查或新调业务。

## 对上一份报告的收敛

`prompt-current-renewal.md`中SOP“需判断是否排除”的备注现由本补充细化：**业务侧保留的规则取数本身不构成排除原因**；应排除的是Dify侧额外前置检索迁移后不再执行的场景。SOP此fixture可列输入一致；保留PROD当前模板未逐字验证这一原有边界，不引入输出质量门槛。
