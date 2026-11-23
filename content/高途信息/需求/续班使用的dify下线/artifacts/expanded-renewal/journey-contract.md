# 旅程已解决原因字段归属

只读代码历史/归档证据；基线91012878d，无业务调用或写配置。

## 结论与建议
resolvedRefundReasonList是既有业务概念和模型契约，不是本次Dify迁移首次引入。当前迁移新提示词确实比本轮旧Dify实收多出该要求，因此仍属于本次两路输入不对等；“字段早已有”不能消除实收差异。但不建议直接删合法字段，也不建议在此次迁移顺手扩张业务消费。

建议保留已有模型字段和归档模板。主Worker应把“对齐当前旧Dify实收”和“恢复历史模板要求”明确为两个不同目标：若本次要求严格对等，应仅为实际旧应用选用对应有效模板，而非全局删除该字段；若保留历史模板增强，则明确记录行为变化，补有已解决原因的数据验证，不能标记为纯迁移无行为变化。当前证据不足以认定旧Dify为何不含字段（旧应用/历史模板/发布漂移），不据猜测删除。

## 历史归属
- ec295156c85f54c3a46c8b4668fc0d4039acb8cf，作者日期2025-10-27，提交日期2025-10-28，“feat: 退费旅程添加返回实体字段”：给AiReasonTutoringResult加入List<AiResolvedRefundReasonItem> resolvedRefundReasonList，并新增分类/摘要/原文结构。
- git merge-base --is-ancestor确认该提交已在迁移前基线3e2b681fa中。
- 3e2b681fa至91012878的refundless目录diff为空。因此该消费/模型行为不是迁移代码新增。
- 本迁移首个访问覆盖提交61b79d05d日期2026-10-27；比上述字段实体晚约一年。
- 需求归档dify-refund-prompts/精品退费旅程.pre_prompt.txt与素养退费旅程.pre_prompt.txt逐字一致（2482字符），均有已解决原因要求及resolvedRefundReasonList三个子字段。
- quartz归档提交addb267c，2026-10-27 19:00:15保存上述Dify模板。注意归档时间与迁移启动同日，不能仅凭归档时间声称它一定是当前线上生效版本。
- expanded-refund/exact-旅程-test-1.json的system完整包含上述2482字符归档模板；旧prod实收不含resolvedRefundReasonList。这支持新提示词来自历史归档，而非本轮凭空追加。原始精确差异见expanded-refund/exact-旅程-system.diff。

历史命令证据journey-history-evidence.txt。

## 当前消费是否依赖
RefundTutoringServiceImpl.saveReasoningResult（约158行）将响应反序列化为AiReasonTutoringResult，因此可接收该字段；但随后只把tutoringSummary、tutoringItems复制到AiReasonTutoringResultDTO，另补uniqueIdMap并保存sceneValue。DTO本身只有这三个字段，未包含resolvedRefundReasonList。

所以当前旅程最终sceneValue不会因为新增该字段而保存它；字段缺失也未见该路径强制校验。新增要求仍会影响模型注意力、耗时以及其他输出，不能称“未消费所以无风险”。

不要混淆单条沟通链路：RefundChatResultService约434行确实复制同名resolvedRefundReasonList到RefundAnalyzeEESAmendResult；AiAnalysisCommResult.toString也把已解决原因加入后续文本。这是另一个已有消费路径，不证明旅程AiReasonTutoringResult字段已被最终DTO消费。此次不修改任一路径。

## 边界
已确认历史代码归属、归档来源以及当前部署消费代码。未找到独立PRD/TAPD原文，不能替业务宣布字段已经下线或要求恢复；未对生产调用，未修改旅程模板。请主Worker据“严格等价还是保留增强”决定下一步，避免盲删既有行为。
