---
title: 续班使用的dify下线
aliases: [续班dify下线, 退费dify下线, 续班退费dify下线, 续班AI去dify, dify下线, 续班AI切换大模型网关]
status: 开发中
owner: zhangzeling
branches:
  - student-data:feature-xuban-dify-offline
repos:
  - student-data
updated: 2026-11-23
tags: [需求]
---

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

## 已确认的迁移阻断

生产降退费已发布工作流是前置检索加一个LLM节点；迁移缺前置检索与context注入。两轮工具调用仅实证于TEST废弃绑定，不能外推生产。证据：[检索遗漏](artifacts/expanded-refund/confirmed-retrieval-gap.json)，trace `81e849b4-d461-4fd0-910a-154368d68bc0.0.3`。其他退费场景仍在核对，不外推。

## 现在什么情况

| | |
|---|---|
| 阶段 | 开发中 |
| 进度 | T 6/14 · R 0/0 · C 0/0 |
| 部署泳道 | `student-data=test-gtbg-dev-1`，commit `91012878`，流水线 `1360042` |
| 当前卡点 | 扩大场景验证进行中；需合流 LiteLLM 实收差异、学部变体与工作流处理证据，尚不能判整体对等 |
| 最近更新 | 2026-11-23：两例实收提示词/参数差异已核对；TEST 画像/摘要 thinking.disabled、分层 text 格式已修正复验；SOP V2长指令逐字一致。退费逐字段实收已核对，降退费检索遗漏及模板残留正在处理；详细差异见 [审查报告](artifacts/expanded-diff/report.md)，续接见 [交接](artifacts/expanded-scope/handoff.md)。 |

完整逐点状态见 [覆盖与迁移实践](artifacts/expanded-scope/coverage.md)。

## 下一步

1. 完成其余续班与退费场景的双路实收对比，核对学部变体和 Dify 隐含工具/工作流处理。
2. 对运行确认的迁移问题作最小修正并同入口复验；共有质量问题单列，不归因迁移。
3. 汇总覆盖、风险与未覆盖项；生产发布不在本次授权范围。

## 待确认

- 功能替换稳定的观察窗口与放量节奏，留待生产发布阶段决定。
- 当前扩大验证未完成，不以代表样本或 JSON 可解析作为全量验收。

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

原始17个生产应用，问题建议高中/素养2个明确保留Dify，目标15个不变。本轮TEST10样本不是生产10/15/17项通过。9个旧/新各单次；仅TEST通用降退费旧2次、新1次，已核实它绑定【废弃】agent-chat。

生产精品/素养降退费目标为已发布advanced-chat：代码提取→知识检索→单LLM生成。不是两轮LLM；仍需迁移前置检索与context注入。撤回此前把TEST废弃两轮外推生产的口径；生产检索缺口依据已发布图而非TEST两轮。重试/compare双路/不同阶段不算内部多轮。

可支持TEST单次替换试验：画像、摘要、SOP V2、修正后的分层、课程体验、NPS本模板、修正后的素养服务建议本模板。根因弱样本与旅程指令差异不能列业务验收通过。生产学部与流程准入未全验，尤其素养TEST一次不代表生产可去掉检索。

详见[调用次数与证据](artifacts/expanded-scope/call-count-evidence.md)、[原材料对照](artifacts/expanded-renewal/source-scope.md)、[生产与废弃绑定](artifacts/expanded-refund/deprecated-binding.md)。本次未改路由/代码/生产，未选择保留或建设方案。
