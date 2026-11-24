# 旅程严格对齐：契约影响及13应用边界

核对：2026-11-24，代码56b53f3c5b7376e7f08ce4972f055d72cd7a9469。只读代码与归档；未修改代码、配置或调用业务。

## 结论

按最新owner口径，可由主Worker仅将TEST应用255733517892204544的gateway_core_prompt替换为pairs“旅程”旧侧实际system去掉末尾恰一个换行，再走当前网关复验。不是回切Dify，不改原core/后处理、不改其他应用。生成器会补回一个换行，不能用rstrip删掉多余空白。该动作与当前旅程持久化消费未见强制字段冲突；不需要以保留增强system作为例外或新门槛。

旧实收system字符数：2151；末尾换行已核对；其中没有resolvedRefundReasonList要求。配置值应为该字符串[:-1]，其余逐字保留。新调用须完整messages逐字对照，不能只检查user，也不能用旧32999155 trace替代新验证。

## resolved字段影响

| 项目 | 当前代码事实 | 本次影响 |
|---|---|---|
| 模型字段 | domain/refundless/model/AiReasonTutoringResult.java含resolvedRefundReasonList；历史归属见expanded-renewal/journey-contract.md | 保留模型字段，不删除既有能力定义 |
| 旅程解析 | reasoning/impl/RefundTutoringServiceImpl.java:158开始saveReasoningResult，将结果解析为AiReasonTutoringResult，仅检查结果对象非空 | 此路径未检查resolved字段必填；缺失不直接触发该字段校验失败 |
| 持久化 | 同方法只复制tutoringSummary、tutoringItems和查询得到的uniqueIdMap；AiReasonTutoringResultDTO只有这三项，sceneValue序列化DTO | 当前旅程sceneValue没有保存resolved字段，因此仅去掉生成要求不直接删除已存字段 |
| 另一消费链路 | analysis/RefundChatResultService.java:434复制同名字段到RefundAnalyzeEESAmendResult；AiAnalysisCommResult.toString会使用它 | 属单条沟通分析，不能混同旅程；本次不改其提示词、模型和消费 |
| 模型行为 | 旧system不要求“已解决原因”增强 | 输出注意力/旅程归纳可能变化，不能保证输出逐字相同；符合owner最新严格输入目标，无需新加输出质量门槛 |

## 13正式应用的覆盖边界

依据format-application-map.md：续班5项（画像、摘要、SOP、高中分层、素养分层）+退费8项（精品/素养各根因、旅程、体验、NPS）。4知识库继续排除，没有新增迁移场景。

- 已有7组messages相等证据复用；旅程补当前system严格相等即可；SOP V2复用已有相等证据，不重跑。
- 13项不是8个TEST样本一一对应：分层两个学部只独立验证一个TEST default样本；根因、旅程、体验各两学部仅一组同类TEST实收；NPS两种模板已有各自样本。因此有4个额外学部实例未单独实收，不能宣称13个生产应用逐一验证。
- 这些未独立实收的变体仍属于已实现两种包装，无证据要求第三种格式或新增代码。正文必须读各自原配置，不把一个学部业务正文复制给另一个。
- 正式旅程的原core为通用句且无后处理，历史TEST为“退费旅程分析”并有后处理；因此此次仅TEST外system对齐证明该旧TEST基准，不能顺推为正式旅程模板也已严格相等。生产未改，后续若扩展生产配置应选择对应旧应用基准；不阻塞本轮获准TEST验证。

核对来源：comparison/pairs.json、format-application-map.md、format-runs/56b53f3c5/final-summary.json；当前代码上述方法及DTO。新严格实收由主Worker执行并回写，本报告不冒称已经完成。
