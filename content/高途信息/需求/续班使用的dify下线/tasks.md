---
title: 续班使用的dify下线 · 任务板
tags: [需求, 任务]
---

# 当前任务板

## 当前增量：TEST知识库替换实验（2026-11-25）

task_type=requirement。owner最新明确知识库也尝试替换；线上配置为复制来源，生产四应用保持Dify只约束生产。

|契约|成功条件|当前状态|
|---|---|---|
|KB-R1 旧链路基线|相关四场景线上配置映射明确，TEST副本同输入独立运行，完整下游请求有证据|进行中|
|KB-R2 实际替换|student-data TEST真实入口完成检索→拼装→生成，修正实际差异后同入口复验|进行中|
|KB-R3 对等判断|逐场景比较完整messages、角色顺序、model/stream/thinking/max_tokens及其他参数；随机输出不强求相同|待基线合流|
|KB-R4 交付|必要后端改动提交推送部署回读；原归档及飞书完整对照和边界更新|进行中|

生产dataset key与正式库检索已成功，直接复用；无待授权凭据。禁止生产业务生成、库内容修改、正式应用切换/上线。必要TEST配置、应用副本、后端修正和部署已授权。既有非知识库结果继续有效，不重跑无关项。


> 状态：`待办` `进行中` `已完成` `阻塞` `已取消`

## 最新五项要求（strict-v2，覆盖此前参数保留口径）

以下为当前工作契约；下方既有验证保留为历史成果，不能据此继续保留与最新要求冲突的参数。本段仅登记需求/状态，不代表前四项新实施已完成。

|项|当前要求|本轮状态/边界|
|---|---|---|
|1 参数|response_format需要json_object可单独新增；max_tokens、stream、thinking按旧实收严格对齐，旧没有则不写|待负责实现者完成TEST代码/配置及实收；覆盖此前8192/非流式/显式thinking保留差异口径，区分入口实收与后续路由注入|
|2 费用身份|新链路必须带x-tech-ai-user-id用于分钱，追溯旧Dify真实来源并正确传递|待身份链路证据及TEST验证，不能硬编码旧user或以动态身份为由留空|
|3 模型|model必须对齐，查清旧别名到真实目标映射并入表|允许只读线上配置/容器；实际模型映射与TEST对齐待负责者完成，不把入口名字差异或返回名当完整路由结论|
|4 messages|保持system/user内容、角色、顺序、包装严格相等，不回切Dify|已有成果复用；本轮受参数/实现影响部分需复验，输出不要求相同|
|5 降退费tools|调查正式工作流及工具执行机制，给迁移方案|只读方案已完成：[tools与检索契约](artifacts/comparison/strict-v2-tools-plan.md)。正式降退费优先固定前置检索；仅tools声明不足，四知识库不自动切换|

生产只读，不改数据/代码/配置/路由/权限，不生成或上线；前四项由主Worker统筹TEST实施，第五项只调查方案。原库Console当前可读不等于Service API身份已获权；旧401/403不再泛化。

## 三参数最终收尾（2026-11-24）

TEST新链路9个样本（含SOP真实V2）均完成最新实收：stop字段删除后与旧请求省略一致，完整messages仍相等，finish_reason均stop。根因和旅程同时删除enable_thinking，旧新请求均省略；删除后仍分别有1070/1812 reasoning tokens，直接说明删除不等于关闭思考，供应商有效默认仍未验证。

response_format按具体约束保留差异：画像/摘要/SOP保留JSON输出约束（不声称参数本身必不可缺）；分层保留已修复实际落值冲突的text。此项是明确保留，非笼统待建议。stop与两项enable_thinking请求省略已落实，不再停于建议。max_tokens/stream/user原边界不重开。

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



## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 从 `origin/release` 建分支 `feature-xuban-dify-offline` | 已完成 | — | `--no-track`，起点 `origin/release` |
| T-02 | 定切换粒度与测试环境首个试点应用 | 已完成 | — | 粒度 `ai_agent`；试点 `用户画像/沟通摘要-test`(255107338300556288)；复用 `LlmGatewayAccessor` |
| T-03 | Apollo 新增按应用链路开关并落地（命中走 LLM 网关 `gps-ai`） | 已完成 | — | 现为 `ai.agent.accessor.override.map`（`{name,platformType,model,params}`）+ `AiApplicationExecutor` 接入（commit `f0c58aaf`）；TEST Apollo 已发布 |
| T-04 | 测试环境切一个试点应用并验证功能 | 已完成 | — | 试点 `沟通摘要-test`：开关开=网关/关=Dify、模型=按应用指定、`params` 生效，均实测通过 |
| T-05 | 全量切换剩余续班 + 退费 Dify 应用并逐个验证 | 进行中 | — | 历史TEST样本保留；56b53f3c5已部署UP并完成八TEST实收：八例完整messages相等（旅程已补严格system对齐），SOP复用。4知识库保留Dify；13项按对应旧格式验收，不能以语义近似收尾 |
| T-06 | 代码切换：收口 / 移除 Dify 路径 | 待办 | T-05 | 功能替换稳定后再做 |
| T-07 | 每应用模型一一对应：按应用配 `model`/`params` + 网关加路由 | 已完成 | — | 映射全定：Doubao 旧系列→`doubao-seed-2-0-lite-260428`、R1→`deepseek-v4.1-flash-1017`；gps-ai test 加 2 条路由（37268/37270）；prod 路由已提工单 5546/5547 |
| T-08 | 退费提示词从 Dify 迁到 student-data（新链路用） | 已完成 | — | **test 已迁并复验**；承载列为 `ai_application.gateway_core_prompt`，prod 待迁 |
| T-09 | prod Apollo：补 `params` 并发布 | 待办 | T-13 | **prod 现置空 `{}`（全走老链路）**；**代码上线后**再发正式配置（现正式范围13个非知识库目标，须按应用映射另行核准；4知识库保留Dify） |
| T-10 | 按应用定返回格式 | 进行中 | — | 分层原因应输出文本，强制 JSON 已在有效样本复现差异；TEST 已改 text 并同入口复验；其他场景格式仍结合完整覆盖判断，不套用续班统一 JSON |
| T-11 | prod：`ai_application` 加 `gateway_core_prompt` 列 + 迁移退费提示词 | 待办 | — | 先提 DDL 工单加列（应用级，替代 prompt_config 方案）；再按获准范围写8个非知识库退费应用提示词（按学部取文件，NPS 素养≠精品）；2个降退费建议继续Dify |
| T-12 | prod 路由工单审批（gps-ai） | 待办 | — | 需 `doubao-seed-2-0-lite-260428`、**`deepseek-flash`**（替换已提的 5547 用 v4.1-1017） |
| T-13 | prod 代码发布 | 待办 | T-11,T-12 | 合 release / 发版；发布后按应用逐个 `compare` 复验 |
| T-14 | 迁移表 tab 状态同步（prod） | 待办 | T-13 | 表链接见 [`links.md`](links.md) |
| T-15 | 生成沟通建议-高中/素养：知识库检索替换 | 已取消 | — | **本期不迁，这两个保留 Dify**。原因：Dify 上为 agent-chat+function_call 且**绑定 Dify 知识库(dataset)**，运行时由模型自行检索（向量检索+rerank 回灌），**知识不在提示词里**；而网关是单次 chat completion、**无工具/检索** → 直接切属**有损**。可后续用 Teable 结构化话术复刻（须单独立项）。评估见 [`artifacts/dify-kb-eval.md`](artifacts/dify-kb-eval.md)；test 已撤其开关回到 Dify |

## R- 反讲整改项

| 编号 | 整改项 | 谁提的 | 状态 | 备注 |
|---|---|---|---|---|
|  |  |  |  |  |

## C- case 联调问题

| 编号 | 问题 | 对应 case | 状态 | 备注 |
|---|---|---|---|---|
|  |  |  |  |  |

## 完成判据

- T-02 切换粒度与试点应用确定并写入 README → 判据：README「待确认」对应项清空
- T-03 Apollo 开关读回确认已发布 → 判据：`apollo_get_key` 读回命中新 key
- T-04 测试环境试点应用走新链路且功能正常（含日志 traceId 证据）→ 判据：产出与 Dify 对齐、无报错
- T-05 按目标场景/学部变体核对新旧 LiteLLM 实收指令、角色、参数和消费契约；有效样本及反例有 trace，不以调用成功代替业务正确。知识库两应用保留 Dify；TEST 映射不能代替生产逐应用覆盖。
- T-07 每应用 `model`/`params` 落 Apollo 且 gps-ai 路由齐 → 判据：`apollo_get_key` 读回各应用配置、`callerRoute` 读回目标模型
- T-06 Dify 路径移除后无引用 → 判据：全仓检索 `Dify`/`dify-open` 无续班调用残留

- T-10 分层格式修正后，同有效样本返回直接原因文本，LiteLLM实收与Apollo发布值一致，其他agent配置保持不变。
- T-11 生产DDL回读目标列存在且退费应用提示词完整；当前只读查询缺列，不在本次生产写授权内。
- T-09/T-12/T-13/T-14 属后续生产发布阶段，须另获发布授权并按依赖顺序执行。
