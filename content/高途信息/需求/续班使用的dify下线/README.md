---
title: 续班使用的dify下线
aliases: [续班dify下线, 退费dify下线, 续班退费dify下线, 续班AI去dify, dify下线, 续班AI切换大模型网关]
status: 开发中
owner: zhangzeling
branches:
  - student-data:feature-xuban-dify-offline
repos:
  - student-data
updated: 2026-11-24
tags: [需求]
---

# 续班Dify迁移：当前验证结果


## 最新五项要求（strict-v2，覆盖此前参数保留口径）

以下为当前工作契约；下方既有验证保留为历史成果，不能据此继续保留与最新要求冲突的参数。本段仅登记需求/状态，不代表前四项新实施已完成。

|项|当前要求|本轮状态/边界|
|---|---|---|
|1 参数|response_format需要json_object可单独新增；max_tokens、stream、thinking按旧实收严格对齐，旧没有则不写|待负责实现者完成TEST代码/配置及实收；覆盖此前8192/非流式/显式thinking保留差异口径，区分入口实收与后续路由注入|
|2 费用身份|新链路必须带x-tech-ai-user-id用于分钱，追溯旧Dify真实来源并正确传递|已核实旧费用头来自强制查询后的Account.name，旧user UUID来自EndUser.id，两者不同；gongxuemeng样本映射已核实；各应用缺省费用主体不同，已取证，Java合流与TEST头实收仍待完成，见[身份取证](artifacts/comparison/strict-v2-cost-identity.md)|
|3 模型|model必须对齐，查清旧别名到真实目标映射并入表|允许只读线上配置/容器；PROD/TEST旧名映射已只读核实，见[模型证据](artifacts/comparison/strict-v2-model-map.md)；已证先按旧名鉴权再redirect；三条旧别名授权被管理入口拒绝（模型不存在或已下线），原14路由回读未变，严格旧名实收受阻，见[失败与回读](artifacts/comparison/strict-v2-route-change/report.md)|
|4 messages|保持system/user内容、角色、顺序、包装严格相等，不回切Dify|已有成果复用；本轮受参数/实现影响部分需复验，输出不要求相同|
|5 降退费tools|调查正式工作流及工具执行机制，给迁移方案|只读方案已完成：[tools与检索契约](artifacts/comparison/strict-v2-tools-plan.md)。正式降退费优先固定前置检索；仅tools声明不足，四知识库不自动切换|

生产只读，不改数据/代码/配置/路由/权限，不生成或上线；前四项由主Worker统筹TEST实施，第五项只调查方案。原库Console当前可读不等于Service API身份已获权；旧401/403不再泛化。

## 知识库列表最新事实

2026-11-24知识库列表纠正：本次Console列表total=2、has_more=false，与截图一致，分别是TEST-dify-migration-20261124-isolated（30a822a4-32f5-49e8-b497-eaad5f8280de，economy、app_count=0）和降退费服务建议话术库（86233d1a-bddf-4a15-a229-c90b6a061c57，high_quality）；原库列表及详情均成功，当前关联spcAm3oupwKuWRMD8UV与spczjG62GXkZ0ZSOBYS两个空间，旧“当前不可见/必须先给旧空间授权”已不适用。响应x-env=production、gapm-appid=dify-api支持生产标识API，两个test头和Cookie的优先级尚无证据，不能按名称或头认定TEST；共享平台30a822库也不是Java E2E的test-dify-open独立TEST库0105aec9，内容、索引和服务身份未证对等。related-apps五条按UUID去重为三个应用（含正式高中/素养workflow及废弃agent）；素养发布工作流确实绑定原86233库，并使用top_k=4、rerank=false，不能误套库级top_k=3、rerank=true、full_text_search默认。当前无需因旧403直接换库或改权限；仍需核实的是后端Service API对应token的身份、tenant及空间授权，Console Cookie可见不能替代Bearer授权，历史401只说明当次TEST token对该目标无效，不证明所有生产token不存在。本轮仅只读核查，未检索生成或修改凭据、权限、路由，四知识库应用继续Dify。

证据：[本次只读列表](artifacts/comparison/kb-console-current/request-evidence.json)、[路由边界核查](artifacts/comparison/kb-console-route-review.md)。

## 三参数最终收尾（2026-11-24）

TEST新链路9个样本（含SOP真实V2）均完成最新实收：stop字段删除后与旧请求省略一致，完整messages仍相等，finish_reason均stop。根因和旅程同时删除enable_thinking，旧新请求均省略；删除后仍分别有1070/1812 reasoning tokens，直接说明删除不等于关闭思考，供应商有效默认仍未验证。

response_format按具体约束保留差异：画像/摘要/SOP保留JSON输出约束（不声称参数本身必不可缺）；分层保留已修复实际落值冲突的text。此项是明确保留，非笼统待建议。stop与两项enable_thinking请求省略已落实，不再停于建议。此历史验证不覆盖最新strict-v2：max_tokens/stream/费用身份须按顶部新契约继续对齐。

发布releaseKey `20261124134541-188aa6ecfba696dc`、`20261124134735-188a49b33afd483d`已完整回读。原飞书9场景表新请求和完整最终输出已更新，另外两知识库历史表原样保留；无新代码部署或生产修改，4知识库继续Dify。13正式应用不是13生产实例独立实收。

证据：[9例统一结果](artifacts/comparison/stop-alignment/summary.json)、[执行报告](artifacts/comparison/stop-alignment/report.md)、[最终配置回读](artifacts/comparison/stop-alignment/final-readback.txt)、[两参数裁决](artifacts/comparison/parameter-final-decisions.md)、[原表回读核验](artifacts/comparison/stop-alignment/doc-verification.json)。


## 旅程严格对齐最终结果（2026-11-24）

最新要求覆盖“旅程保留增强system例外”：仅TEST应用255733517892204544的gateway_core_prompt从2482改2150字，生成器追加换行后与旧实收2151字system相等。新trace `b83e29de-f629-4a5e-b864-588da89e26b4.0.3` 的完整messages、system、user均逐字相等，业务answer等于下游最终content，finish_reason=stop。其余七例及SOP证据复用，八TEST场景现均完整messages相等。

这是新网关链路配置数据修正，不是回切旧Dify应用：同trace GAPM有student-data outbound `/v1/chat/completions`，event为`litellm_proxy/deepseek-v4.1-flash`，与LiteLLM实收相互印证。代码仍56b53f3c5，无新commit或部署，未改路由/其他应用。移除的是该TEST提示词的resolved增强要求；旅程最终DTO未保存或强校验该字段，另一沟通分析链同名字段未改。

证据：[严格断言](artifacts/comparison/format-runs/56b53f3c5-journey-strict/旅程/strict-assertions.json)、[新链路证据](artifacts/comparison/format-runs/56b53f3c5-journey-strict/旅程/new-chain-evidence.json)、[契约影响](artifacts/comparison/journey-strict-impact.md)。13正式应用无新增格式类别，但4个学部实例未独立实收；不将八TEST样本称为全部生产验证。四知识库继续Dify，无生产修改。

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

证据：[统一结果](artifacts/comparison/format-runs/56b53f3c5/final-summary.json)、[业务响应回读](artifacts/comparison/format-runs/56b53f3c5/response-readback.json)、[覆盖配置未变](artifacts/comparison/format-overrides-preserved.json)、[部署UP](artifacts/comparison/format-deployment-ready.log)、[表格回读核验](artifacts/comparison/format-table-verification.json)。


## 比较对象与原表入口

同一业务数据分别经旧Dify及新网关，比较LiteLLM实际messages及最终content。旧路PROD日志与新路TEST日志是下游归属，不代表用了不同业务数据。参数差异独立展示，输出不同不强求对齐。

[飞书完整对照（revision67）](https://gaotuedu.feishu.cn/docx/EWI6dsdvPokck0xy89ccJDuEnhg)：八组新列已换为56b53f3c5本轮实收，完整输入输出和差异直接在原各表内；SOP V2复用既有完整输入相等结果，两个历史知识库样本仅供追溯。主要当前证据是本轮八场景实收，不再以91012878阶段差异作为当前状态。

## 实现与配置

56b53f3c5按应用恢复旧Dify消息形式：续班原flat单user，退费独立Dify system＋原应用flat user；SOP V2不变。TEST八应用格式配置已发布回读，releaseKey为20261124120843-188aa6ecfba696ce；流水线1361114部署UP且本轮实收已完成。此前全局单user尝试已撤销，不属于当前实现。

旅程已按最新要求在TEST新链路对齐旧实收system，原增强模板例外不再适用。正式应用映射见[13应用基准](artifacts/comparison/format-application-map.md)。生产DDL、发布与全量应用验证不属于此次TEST交付。

## 历史阶段与独立事项

revision56及91012878阶段曾记录“仅SOP user相等、其他场景包装不同”，对应旧实现；本轮八场景格式修复已覆盖该历史差异，当前结论以上方实收表为准。[旧配对](artifacts/comparison/pairs.json)、[旧差异审计](artifacts/comparison/user-diff-audit.json)保留追溯，不充当最新结果。

知识库Java隔离TEST接入6909717c已有独立成果，四个正式知识库应用仍保留Dify，不加入本轮格式迁移。生产凭据及空间授权调查见[接入证据](artifacts/expanded-refund/kb-service-e2e.md)和[权限调查](artifacts/expanded-refund/kb-service-auth-investigation.md)，不阻塞本轮非知识库格式结果。
