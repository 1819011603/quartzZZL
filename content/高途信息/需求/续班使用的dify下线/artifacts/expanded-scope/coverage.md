# 当前迁移审查覆盖与判据

## 旅程严格对齐最终结果（2026-11-24）

最新要求覆盖“旅程保留增强system例外”：仅TEST应用255733517892204544的gateway_core_prompt从2482改2150字，生成器追加换行后与旧实收2151字system相等。新trace `b83e29de-f629-4a5e-b864-588da89e26b4.0.3` 的完整messages、system、user均逐字相等，业务answer等于下游最终content，finish_reason=stop。其余七例及SOP证据复用，八TEST场景现均完整messages相等。

这是新网关链路配置数据修正，不是回切旧Dify应用：同trace GAPM有student-data outbound `/v1/chat/completions`，event为`litellm_proxy/deepseek-v4.1-flash`，与LiteLLM实收相互印证。代码仍56b53f3c5，无新commit或部署，未改路由/其他应用。移除的是该TEST提示词的resolved增强要求；旅程最终DTO未保存或强校验该字段，另一沟通分析链同名字段未改。

证据：[严格断言](../../artifacts/comparison/format-runs/56b53f3c5-journey-strict/旅程/strict-assertions.json)、[新链路证据](../../artifacts/comparison/format-runs/56b53f3c5-journey-strict/旅程/new-chain-evidence.json)、[契约影响](../../artifacts/comparison/journey-strict-impact.md)。13正式应用无新增格式类别，但4个学部实例未独立实收；不将八TEST样本称为全部生产验证。四知识库继续Dify，无生产修改。

## 前一轮实收记录（56b53f3c5；旅程例外已被上方严格结果覆盖）

TEST/test-gtbg-dev-1流水线1361114已部署UP，八场景新侧调用及LiteLLM实收核验完成：七例完整messages逐字相等；旅程user逐字相等，system恰等当前2482字模板加换行，保留resolvedRefundReasonList增强，与历史旧模板不同，不称完全相等。SOP V2复用既有完整输入一致证据。八业务answer均逐字等于下游最终content且stop；原9项model/platform/params覆盖完全未变。

13正式非知识库应用映射不等于八TEST样本覆盖全部生产应用；四知识库仍走Dify。本轮无生产修改；TEST新配置保留供后续验证，无临时监听或后台业务操作。

|场景|新trace|完整messages|
|---|---|---|
|画像|`dd182d47-b845-4135-80f2-f13575803a7e.0.3`|逐字相等|
|分层修正后|`e604b357-f357-4997-b28b-f3192b531eb8.0.3`|逐字相等|
|素养NPS|`5a814ae8-b8ae-4450-ada4-895a41d53463.0.3`|逐字相等|
|摘要|`62b40ff1-972a-4906-bd24-28e9486d4aa5.0.3`|逐字相等|
|退费根因|`f33b2e1d-019e-42d1-b97f-13e98c78c612.0.3`|逐字相等|
|旅程|`32999155-127f-418b-b073-600b6b159b6a.0.3`|user相等；system保留当前增强模板，与历史版本不同|
|课程体验|`6c006207-ade9-4800-b40a-a0db181b4c9c.0.3`|逐字相等|
|NPS|`b7f98851-b9b7-4395-89f9-39a63bbaeeef.0.3`|逐字相等|

完整旧新请求、user/system、最终输出及差异直接更新于原飞书各场景表，新版列已替换，SOP及两历史知识库表保留；revision67回读11表151代码块逐字一致（还原展示换行）。

证据：[统一结果](../../artifacts/comparison/format-runs/56b53f3c5/final-summary.json)、[业务响应回读](../../artifacts/comparison/format-runs/56b53f3c5/response-readback.json)、[覆盖配置未变](../../artifacts/comparison/format-overrides-preserved.json)、[部署UP](../../artifacts/comparison/format-deployment-ready.log)、[表格回读核验](../../artifacts/comparison/format-table-verification.json)。





## 历史覆盖（91012878阶段）

以下为历史TEST/test-gtbg-dev-1证据；不代表56b53f3c5新格式实收验证。当前完成状态以上方表为准。

|需求点|实现/核查|证据与缺口|
|---|---|---|
|仔细审查diff|11个后端文件及5项风险适用性|expanded-diff/report.md、risk-applicability.md；未盲改潜在风险|
|最下游输入对比|摘要、根因、画像、SOP compare、分层已取实收|逐字段对比；退费5场景双侧实收已取得，精确逐字段对照正在合流|
|真实入口差异|SOP V2重放13,647字相同|expanded-renewal/sop-real-entry.md；未覆盖外围选择/写回|
|Dify隐含处理|知识库两应用保留、旧模型重定向thinking已核实|画像已修disabled；分层也已修disabled，SOP Seed-1.6两侧有推理所以不改；降退费旧路dataset两轮已证实，新路遗漏；旅程样本无tools，不能混用证据|
|已确证修正|画像thinking、分层text|画像trace f059219f-2d7c-46c5-945e-fd3a9cdab509.0.3；分层dabc87b7-0a58-4682-ae04-e6cfa2b3224f.0.3；仅TEST|
|线上范围|Apollo未证实目标应用关闭|模块{}全放开、T+N关闭不能等同下线；未做逐app流量统计|
|发布依赖|生产缺gateway_core_prompt|prod-ddl-check.txt；开关关闭不能规避SQL列依赖；本次不发布|
|随机性判定|区分输入差异、格式契约、事实与文案|未作统计质量等价；共有多用户措辞不归因迁移|
|学部变体|历史TEST10应用不等同当前PROD13非知识库目标应用|NPS差异、独立映射和跨班数据仍须明确覆盖；不外推|

## 适用的迁移实践

1. 固定业务快照，在LiteLLM实收层比较消息角色、完整指令、动态数据与参数，再追重定向和默认值；不把actual_query当最终请求。
2. 保留真实业务入口。普通compare与V2可能构造不同消息，不能互相代替。
3. 按消费契约配置输出格式。原因文本不能统一强制JSON；清理围栏不等于提取对象字段。
4. 逐应用核对Dify工具、检索、工作流和多轮上下文；模型声称用工具不是执行证据。
5. 当前格式验收按对应旧Dify完整messages比较；历史质量观察保留，不新增输出逐字一致或统计质量门槛。
6. 配置按agent最小合并并回读，避免覆盖他人变更；保留单应用回滚。代码回滚不自动恢复已写数据。
7. 先DDL和提示词数据、再代码、最后开关；生产动作另行授权。未做长文本上限/耗时统计，不宣称性能等价。

旅程字段处置：保留resolvedRefundReasonList既有契约；旧Dify当前模板未要求而迁移归档模板要求，属于已记录的输入差异，不标完全对等。历史旅程DTO未复制该字段不是本次引入，不顺手修。

降退费数据源进展：Dify documents只读回读显示单个teable_import文档，源表tblf6HnwVYpJzy8wVlu，word_count24852，has_more=false。已确认源表存在，不代表当前服务已可读或检索等价；读取权限/分段/检索规则仍在核实。
