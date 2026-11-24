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
> 2026-11-24 机制与方案更新：Dify平台继续存在，可优先评估复用其独立检索API；旧文“必须自建/结构化过滤等价/平台无可用检索”的推断不再作为结论。生产前置检索与TEST废弃工具多轮不得混用。详见 artifacts/expanded-refund/kb-platform-reuse-plan.md。


> **2026-11-24 最新裁决**：允许合理格式差异，以核心指令、业务数据、约束及业务作用保留为准。已有单次场景样本可接受TEST替换；素养NPS实收已补齐。历史“不完全一致”仅是字面差异记录，不代表不通过；4个知识库应用仍保留Dify。详见 [最新逐场景裁决](artifacts/expanded-scope/semantic-acceptance.md)。



# 续班使用的dify下线

> **本目录导航**：[`links.md`](links.md) 链接中心 · [`tasks.md`](tasks.md) 任务板 · [`changelog.md`](changelog.md) 决策摘要 · [`verify.md`](verify.md) 验证手册
> 技术方案在飞书（见 [`links.md`](links.md)），本地不留副本。续接这个需求：读完本文件即可。

## 一句话

把 student-data 用到的 Dify AI 应用（`platform_type=1`，`dify-open.baijia.com`）——**续班 + 退费**——
统一迁到公司大模型网关（caller/场景 `gps-ai`）；用 Apollo 按应用可独立切换新旧链路，
**先功能替换，验证通过后再做代码下线**。

## 需求摘要

- **要解决的问题**：续班、退费的 AI 应用跑在待下线的 Dify 上，需要收敛到统一的大模型网关链路。
- **给谁用**：续班 AI（用户画像 / 沟通摘要 / 沟通建议 / 服务建议 / 分层原因）+ 退费 AI（根因 / NPS / 旅程 / 课程体验 / 降退费服务建议）。
- **核心改动**：新增 Apollo **按应用（`ai_agent`）粒度的链路开关**：命中走 LLM 网关
  （复用已上线的 `LlmGatewayAccessor`，`platform_type=2`），未命中原样走 Dify；每个应用可单独切、可单独回滚。
- **判定做完的标准**：每个目标应用都能经 Apollo 独立切到新链路且功能正常；全量切换并稳定后，
  代码移除 Dify 路径（代码切换阶段）。
- **明确不做**：本期不迁与 AI 无关的链路；`我家子涵最近学的怎么样` 归属待定，暂不纳入；**`生成沟通建议-高中/素养`（= 问题建议-高中/素养）保留 Dify、不迁**。
  - **原因**：这两个应用在 Dify 上是 `agent-chat + function_call` 且**绑定了 Dify 知识库（dataset）**——Dify 把知识库**注册成一个工具**交给模型，**由模型运行时自己发起检索**（Dify 做向量检索 + rerank，命中片段回灌）；**知识不在提示词里，而在「运行时检索」这一步**。而迁移目标（公司 LLM 网关）是**标准单次 chat completion**（只发 `system`+`user`，**无工具/检索**）→ 直接切会**丢掉知识库检索、属有损替换**。其余应用是否对等仍须核对实际提示词、参数及工作流处理；无知识库不能证明切换无损。
  - **可后续替代**：知识库实为 **Teable 结构化话术表**（高中 ~10.4 万字 / 素养 ~4.8K 字），可用 student-data 既有 `TableApiDataHolder`「按问题类型+课程取话术 → 拼 prompt」等价复刻（不需向量库），但须**单独立项**。评估见 [`artifacts/dify-kb-eval.md`](artifacts/dify-kb-eval.md)。**本期这 2 个不下线，Dify 不能完全下线**。

## 已定共识

- 新链路统一走公司大模型网关，caller/场景 = `gps-ai`（2026-10-27）
- 用 **Apollo 按应用（`ai_agent`）独立可切换**新旧链路，不靠改库；每个都能单独配置走新还是老（2026-10-27）
- **分两阶段**：先功能替换（Dify 路径保留），验证 OK 后再代码切换（2026-10-27）
- 测试环境**先切一个**（试点：`用户画像/沟通摘要-test`）验证，通过后再全量（2026-10-27）
- **退费 AI 也在范围**（2026-10-27）
- 新链路**直接复用**现有 `LlmGatewayAccessor`（`llm.baijia.com`，OpenAI 兼容）（2026-10-27）

## 切换对象：Dify 应用清单

prod `ees_data.ai_agent`（`platform_type=1`）：

**续班**

| 应用（智能体） | number | 场景 | 原 Dify 模型 |
|-|-|-|-|
| 用户画像 | 256917438512284672 | 用户画像 | doubao-seed-2-0-lite-260428 |
| 沟通摘要 | 257085994022484992 | 沟通摘要 | doubao-seed-2-0-lite-260428 |
| 问题建议-高中 | 256918735665808384 | 沟通建议 | doubao-seed-2-0-lite-260428 |
| 问题建议-素养 | 256918818763359232 | 沟通建议 | doubao/Doubao-Seed-1-6 |
| 服务SOP分析 | 256919048417231872 | 服务建议 | doubao-seed-2-0-lite-260428 |
| 续班分层原因分析-高中 | 263057785613229056 | 分层原因 | doubao/Doubao-1-5-pro-32k |
| 续班分层原因分析-素养 | 263080101791455232 | 分层原因 | doubao/Doubao-1-5-pro-32k |

**退费**

| 应用（智能体） | number | 原 Dify 模型 |
|-|-|-|
| 退费根因分析(素养学部) | 261424983727715328 | deepseek-v4-flash-0731 |
| 退费根因分析(精品班学部) | 256995079971961856 | deepseek-v4-flash-0731 |
| 退费NPS分析(素养学部) | 261424755557579776 | deepseek-v4-flash-0731 |
| 退费NPS分析(精品班学部) | 256995228385317888 | deepseek/DeepSeek-R1-250528 |
| 退费旅程分析(素养学部) | 261425291830803456 | deepseek-v4-flash-0731 |
| 退费旅程分析(精品班学部) | 256994902246699008 | deepseek-v4-flash-0731 |
| 退费课程体验分析(素养学部) | 261425172233344000 | deepseek-v4-flash-0731 |
| 退费课程体验分析(精品班学部) | 256994989452607488 | deepseek/DeepSeek-R1-250528 |
| 降退费服务建议（素养学部） | 261424592068814848 | deepseek-v4-flash-0731（工作流 LLM 节点） |
| 降退费服务建议（精品班学部） | 256995156763347968 | deepseek/DeepSeek-R1-250528（工作流 LLM 节点） |

> 模型取自 Dify 应用配置（`provider=langgenius/openai_api_compatible`），取法与完整应用 id 见 [`verify.md`](verify.md#dify-控制台服务-api查应用与模型)。`我家子涵最近学的怎么样` 对应 Dify 应用「二讲回复」，不在本期范围。

test 环境对应应用见 [`verify.md`](verify.md)。

当前完整结论见 [迁移审查交付](artifacts/expanded-scope/review-result.md)。

飞书说明：[具体遗漏了什么、已修正什么](https://gaotuedu.feishu.cn/docx/EWI6dsdvPokck0xy89ccJDuEnhg)（已全文回读）。

## 本轮有效范围（所有者最新决定）

有前置知识库的暂不替换：问题建议高中/素养、降退费服务建议精品/素养，4个生产应用保留Dify，不建设替代检索。原17项减去这4项，本轮无知识库目标13个生产应用，归为画像、摘要、SOP、分层、退费根因、旅程、课程体验、NPS共8类；TEST素养服务建议不再列入可替换白名单。

本轮验收聚焦同输入的新旧LiteLLM完整prompt/messages：文本、业务数据、角色包装分别比较；输入一致即可收束，不追加输出质量或提供商HTTP一致性门槛。知识库检索缺口已移出本轮阻塞，生产发布仍未授权。

## 现在什么情况

| | |
|---|---|
| 阶段 | 开发中 |
| 进度 | T 6/14 · R 0/0 · C 0/0 |
| 部署泳道 | `student-data=test-gtbg-dev-1`，commit `6909717c`，流水线 `1360348`（主Worker确认Eureka UP；Java端到端验证进行中） |
| 当前状态 | 已完成测试环境对等性审查与逐场景裁决；SOP V2输入一致，其余场景保留具体差异。生产只读，未授权发布 |
| 最近更新 | 2026-11-23：TEST知识库场景已恢复Dify并复验；逐场景LiteLLM输入裁决已收束。SOP V2完整messages一致；画像/摘要/分层正文一致但角色包装不同；退费根因、旅程、课程体验、NPS精品均有明确差异；素养NPS副本已补双侧实收，按最新业务作用保留口径接受TEST替换。详见[审查交付](artifacts/expanded-scope/review-result.md)与[当前prompt交接](artifacts/expanded-scope/current-prompt-handoff.md)。 |

完整逐点状态见 [覆盖与迁移实践](artifacts/expanded-scope/coverage.md)。

TEST 可替换场景的实际生效配置、版本和 trace 汇总见 [TEST交付](artifacts/expanded-scope/test-replacement-delivery.md)。

## 当前结论与剩余边界

本轮已按所有者最新决定收束为 13 个无前置知识库的生产目标应用、8 类场景；问题建议高中/素养与降退费精品/素养共 4 个生产应用保留 Dify。SOP V2 在测试 fixture 上完整 messages 逐字段一致；画像、摘要、分层仅指令与业务正文逐字一致，角色包装不同；退费根因、旅程、课程体验、NPS 精品存在已定位的标签、位置、换行或模板版本差异；素养 NPS 已补齐TEST副本双侧LiteLLM实收，共用trace `8c802dc4-ed69-4533-b63a-3851e20bb83d.0.3`；业务正文一致，主指令末尾换行与user包装差异已定位，按最新口径接受TEST替换。见 [最新裁决](artifacts/expanded-scope/semantic-acceptance.md)。

不一致的主要来源是旧 Dify 的 flat prompt 与网关真实 system/user 分层，以及 Dify 工作流/模板的额外处理；有正文保留证据的场景不因包装差异盲改。旅程当前生产模板的“已解决退费原因”字段属于既有合法增强，不能为对齐落后 TEST 模板删除。

剩余事项属于后续生产发布前置：生产 `ai_application.gateway_core_prompt` DDL、路由与 Apollo 配置按依赖发布；本轮没有生产修改、代码下线或质量/供应商 HTTP 验收。

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/student-data | feature-xuban-dify-offline | 新增 `domain/ai/core/agentaccess/AiAgentPlatformTypeResolver`（Apollo 覆盖）；改 `domain/ai/core/AiApplicationExecutor`（2 处解析处接覆盖）；访问层 `AiModelAccessorRouter`/`DifyAgentAccessor`/`LlmGatewayAccessor`；续班触发 `app.service.syncdata.ai.renewal.*`、`dws/job/sync/SyncRenewalLiftReasonHandler`；退费触发 `domain/refundless/*` |

## 上线影响面

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 是 | `ai.agent.accessor.override.map`（json map：`ai_agent.number` → `{name, platformType, model, params}`），默认 `{}` |
| ES | 否 | |
| MySQL DDL | 是 | prod `ai_application` 加列 `gateway_core_prompt`（DDL 工单，T-11a）；`prompt_config` 不动 |
| MQ | 否 | |
| 代课接口权限 | 否 | |

## 必须知道的坑

- 续班归因（新链路）已在用 gateway caller `gps-ai`——student-data 的 `llm.gateway.api-key` 落在 **`gps-ai`** 这个 caller 上，不是 `student-data-ai`；改网关侧路由要认这个 caller。
- 切换**不靠改 `ai_agent.platform_type`**：用 Apollo 开关（运行时可切、可单应用回滚）；库值改动属于代码切换阶段。
- Dify 与网关提示词形态不同：Dify 收扁平文本 query，网关走 OpenAI messages；`AiApplicationExecutor` 按平台类型自动选（网关走 messages），切平台后无需改提示词拼装。
- 未显式传 `model` 的应用走网关 `llm.gateway.default-model` 兜底（test 未配则用代码默认 `claude-sonnet-5`）——试点若不指定模型，需确认该模型在 `gps-ai` test 路由可用。

## 原需求与调用次数复核（2026-11-23）

原始17个生产应用，问题建议高中/素养与降退费精品/素养共4个明确保留Dify，本轮目标13个不变；15是第一次排除问题建议两项后的中间口径，13是再排除降退费两学部后的当前口径，四项并集包含原明确不迁的两项。详见 [计数口径](artifacts/expanded-scope/scope-reconciliation.md)。本轮TEST10样本不是生产10/15/17项通过。9个旧/新各单次；仅TEST通用降退费旧2次、新1次，已核实它绑定【废弃】agent-chat。

生产精品/素养降退费目标为已发布advanced-chat：代码提取→知识检索→单LLM生成。不是两轮LLM；仍需迁移前置检索与context注入。撤回此前把TEST废弃两轮外推生产的口径；生产检索缺口依据已发布图而非TEST两轮。重试/compare双路/不同阶段不算内部多轮。

可支持TEST单次替换试验：画像、摘要、SOP V2、修正后的分层、课程体验、NPS本模板、修正后的素养服务建议本模板。根因弱样本与旅程指令差异不能列业务验收通过。生产学部与流程准入未全验，尤其素养TEST一次不代表生产可去掉检索。

详见[调用次数与证据](artifacts/expanded-scope/call-count-evidence.md)、[原材料对照](artifacts/expanded-renewal/source-scope.md)、[生产与废弃绑定](artifacts/expanded-refund/deprecated-binding.md)。本次未改路由/代码/生产；知识库保留决定已落实，未建设替代检索。


## 知识库测试进展（2026-11-24）
隔离Console检索→TEST模型已跑通；随后真正TEST Service API已用TEST dataset Bearer成功检索4条话术（dataset `0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce`），不再是“TEST服务凭证尚缺”。生产原库空间权限与服务身份仍需分别核实，不代表正式替换。

代码 `87124f42` 新增TEST检索服务，`6909717c`补充检索阈值；流水线1360348已由主Worker确认Eureka UP。Java新入口端到端验证仍进行中，旧手工trace不能替代该结果。隔离agent/application为`1795457739670155`/`1795457739670157`，完整system1390字符；TEST/default/application实际releaseKey为`20261124021612-188aa6ecfba6968e`（以发布回读证据为准）。

生产原dataset `86233d1a-bddf-4a15-a229-c90b6a061c57`关联空间`spczjG62GXkZ0ZSOBYS`；当前zhangzeling空间列表正常返回且不含目标空间，直接空间读取403。key列表按创建人过滤，个人可见0不等于生产没有key。最新授权允许生产知识库受控检索及必要TEST配置，生产数据/权限/配置/路由仍不写，生产模型不调用；域名/dataset环境假设正在核实，暂不宣称接通。见 [权限与服务接入](artifacts/expanded-refund/kb-service-auth-investigation.md)、[TEST配置交付](artifacts/expanded-refund/kb-service-config-delivery.md)。

生产目标受控探测补证：真实生产域名+原dataset使用现有TEST dataset token返回401 `Access token is invalid`；尚无获授权生产凭据，不改TEST Apollo为已知无效组合。该错误与个人Console缺空间权限是不同层次。证据：[环境凭据探测](artifacts/expanded-refund/kb-test-retrieval/prod-target-test-credential-probe.json)。
