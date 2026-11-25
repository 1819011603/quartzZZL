# 非知识库替换能力逐场景结论

2026-11-25，仅本地证据及commit差异复核，未调用业务、修改配置、部署或更新飞书。

**13个非知识库场景均有TEST生成及请求证据，支持按已验证输入/配置替换；没有发现必须依赖Dify知识库或工具编排的残余能力缺口。不能表述为所有生产业务入口、全部输入和异常分支已完整等价验收。** 未生产上线不否定已验证能力，随机输出逐字相同也不是验收要求。

## 逐场景判断

以下代码验证版本均为263ba48a；环境test-gtbg-dev-1。八历史项本次更新了参数与当前实收，不只是旧版本成功记录。47b3dcb7的适用边界见下节。

|非知识库场景|可替换判断/证据层次|已验证样本入口范围|具体未覆盖点|证据|
|---|---|---|---|---|
|用户画像|可，历史旧messages与当前新实收相等，参数修正通过|ACL直调syncRequestTask，动态生成与真实数据读取|正式PROD应用独立配置全量验收、前台触发链未全覆盖|A/画像，trace 708865b6-5d42-41bf-b5c1-54635a17c682.0.3|
|沟通摘要|可，messages相等及当前参数通过|ACL普通动态入口；TEST与画像共agent，生产独立agent|生产独立agent差异不能用TEST共agent替代|A/摘要，9d831ba2-fc93-46d7-82ee-f1797aea5696.0.3|
|服务SOP分析|可，V2原actualQueryPrompt完整保留，messages/参数通过|ACL syncRequestTaskV2，已组装prompt|完整业务自动触发→老师查询→头发送只分段取证|A/SOP V2，c2b1755e-1ceb-4859-8488-423c73f52b03.0.3|
|分层原因高中|可，历史样本完整messages/参数通过|普通动态入口，固定班级/学员/辅导班样本|TEST default样本不等于所有正式高中配置/特征分支覆盖|A/分层修正后，63916e95-985f-4407-9f8e-00ae2ae61438.0.3|
|分层原因素养|可，独立配置与生成成功，完整旧prompt/新messages逐字相等|普通动态入口；旧TEST Console持久化实际prompt8414字|未取得旧提供商最终HTTP全部非messages参数；非真实素养学员全链回放|B，9a5b2c21-e465-45fb-b0c4-e24f46a18140.0.3|
|退费根因精品|可，旧新messages/当前参数通过|普通执行器，短合成query、空context|不是退款工单自动取数/触发全链|A/退费根因，aa02540f-30a8-40cd-816d-138168507e69.0.3|
|退费根因素养|可，独立旧新messages及指定参数相等，替代模型已实跑|线上配置复制到真正TEST Dify；新执行器合成输入|非旧模型原名原样回放；非真实素养业务自动取数|C/素养根因，1b812e6a-3ef7-4399-b2e4-47b2d5f88b15.0.3|
|退费旅程精品|可，历史TEST样本messages/当前参数通过|普通执行器、显式合成业务query|历史TEST内core/后处理与正式模板不同；不能将历史模板直接覆盖正式当前模板|A/旅程，29931ca8-4a04-4b89-827e-e1accb0afa33.0.3；D旅程差异|
|退费旅程素养|可，独立替代模型旧新messages/指定参数相等|线上配置复制到TEST、同合成输入|未证明所有生产取数分支；不同模型输出不要求一致|C/素养旅程，7c633ac1-66ed-4e74-9634-ab8ce0bcf9cb.0.3|
|退费课程体验精品|可，旧新messages/当前参数通过|普通执行器、显式合成query|不是全量课程学习数据自动查询与业务触发验收|A/课程体验，3a622047-d7a6-469d-89f5-778770a36f1f.0.3|
|退费课程体验素养|可，独立替代模型旧新messages/指定参数相等|线上配置复制到TEST、同合成输入|非真实素养学员端到端全链|C/素养体验，f018e314-4756-49c3-9660-7c2b6d216317.0.3|
|退费NPS精品|可，旧新messages/当前参数通过|普通执行器、合成query|未全覆盖真实NPS数据为空/多班级等业务取数分支|A/NPS，db72f1f1-90c6-458a-a8f0-047bfdf501c1.0.3|
|退费NPS素养|可，独立旧消息基线及当前参数/真实老师费用头证据|TEST迁移副本；V2请求健康检查与既有严格参数验证|不将V2检查称原普通业务全入口；生产模板321字不能套精品473字|E；当前成功48a884ad-d5ec-4ac1-85dc-26aa542fdf37.0.3|

## 版本差异与复用依据

本地`git diff 263ba48a 47b3dcb7 --stat`仅2文件、122行新增：
- `DifyDatasetGatewayTestService.java`：新增TEST知识库固定工作流入口、refundQuery提取、模板渲染及请求DTO。
- `DifyDatasetWorkflowTest.java`：新增对应4项测试源码。

未改变AiApplicationExecutor、DynamicPromptGenerator、网关Accessor/Router及普通业务入口实现。因此263ba48a非知识库结果可作为47b3dcb7的回归依据；本轮没有运行测试，不能写“47b3dcb7全部13项实跑通过”。新增bean依赖的运行态、Apollo或数据库后续变动也不能仅靠git diff证明无影响。历史22项测试是既有证据，不宣称本轮重新执行。

263ba48a运行映射见`current-version-readback.json`：student-data-5f688c5bfb-xgx76，镜像feature-xuban-dify-offline-263ba48a-20261124152047，Running/UP。

## 参数与费用证据边界

八项当前实收stream=true、max_tokens/thinking省略，model保持；三项素养后续单独补thinking.enabled并保留deepseek-flash，旧新除Dify EndUser UUID外的比较字段相等，max_tokens/stop不传。不能复用早期三素养thinking省略的检查点作为最终参数结论。素养NPS有自己的thinking.enabled基准。

老师身份不再是未查明：Helper真实查询返回样本老师gongxuemeng，trace22169ac0-fb3e-458c-9123-451714b206ca.0.3；SOP源码自动获取路径、人工传RunUser、发送费用头是分段证据。八项watch/body关联有3项字节一致、5项终端乱码近似匹配，不当逐trace完整MDC实收。缺身份仍调用且无个人兜底沿用既有验证；不追计费账。

“12例”是八历史样本+四素养新增样本；素养NPS另有既有独立证据，合起来覆盖13个场景，不能把12误读为漏掉一个业务或12个全部入口验收。

## 可复查证据索引（相对本目录）

- A：`remaining-current-runs/summary.json`及`after/各场景/{invoke.json,received.json,sls.txt}`；`watch-trace-association.json`；`remaining-current-verification.md`后续完成段覆盖前面的历史未完成段。
- B：`suyang-old-tier-evidence-closure.md`、`suyang-old-tier-closure/comparison.json`及`old-messages.json`；新侧`remaining-current-runs/suyang/素养分层/received.json`。是真实持久化prompt而非模板重建。
- C：`suyang-copy-verification.md`、`suyang-copy-current/final-summary.json`、`remaining-current-runs/test-dify-old/`旧实收、`suyang-thinking-final/各场景/`新实收；仅替代模型deepseek-flash，独立agent参数发布已回读。
- D：`format-application-map.md`（完整13项PROD配置来源与格式差异）。角色类别可复用，模板正文必须使用各应用自己的配置。
- E：`format-samples/素养NPS-old-messages.json`、`strict-v2-model-map.md`、`strict-v2-cost-identity.md`、`remaining-current-probe/invoke-response.json`；普通messages基线、指定参数和当前健康检查不能混称同一次全链。

本轮只新增本报告；没有剩余外部取数动作，没有因未上线否认TEST能力，也没有把“可替换”扩张为生产全量切换许可。
