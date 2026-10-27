---
title: 续班使用的dify下线
aliases: [续班dify下线, 退费dify下线, 续班退费dify下线, 续班AI去dify, dify下线, 续班AI切换大模型网关]
status: 开发中
owner: zhangzeling
branches:
  - student-data:feature-xuban-dify-offline
repos:
  - student-data
updated: 2026-10-27
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
- **明确不做**：本期不迁与 AI 无关的链路；`我家子涵最近学的怎么样` 归属待定，暂不纳入。

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

## 现在什么情况

| | |
|---|---|
| 阶段 | 开发中 |
| 进度 | T 5/10 · R 0/0 · C 0/0 |
| 部署泳道 | `student-data=test-gtbg-dev-1`（流水线 1316286） |
| 当前卡点 | 退费 10 个应用的**提示词在 Dify**（student-data `prompt_config.core_prompt` 只是「退费根因分析」这类标签），只改 Apollo 切网关会丢提示词 → 需先把 Dify 提示词搬进 student-data（续班 7 个提示词在 student-data，可直接切） |
| 最近更新 | 2026-10-27：**test 全验通过**——续班 5 + 退费 6（退费提示词已迁入 `core_prompt`），逐应用 Dify vs 网关对比见 [`verify.md`](verify.md#逐应用对比结果test2026-10-27)；退费NPS 不带 `params`（纯文本）；MR `!1796` |

## 下一步

1. 全量切剩余续班 + 退费应用（T-05）：**只改 Apollo**——在 `ai.agent.accessor.override.map` 里按 `ai_agent.number` 增条目 `{name, platformType:2, model, params}`，**无需改代码/发版**
2. 上线前把 gps-ai **prod** 路由补齐（`doubao-seed-2-0-lite-260428`、`deepseek-v4.1-flash-1017`；test 已有）
3. 功能替换稳定后，代码切换：收口/移除 Dify 路径（T-06）

## 待确认

- [ ] 退费 10 个应用的处理：先把 Dify 提示词迁进 student-data `prompt_config`，还是本期先只切续班 7 个？—— 等确认
- [ ] 「功能替换稳定」的观察窗口与放量节奏（全量一次性还是分批）

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/student-data | feature-xuban-dify-offline | 新增 `domain/ai/core/agentaccess/AiAgentPlatformTypeResolver`（Apollo 覆盖）；改 `domain/ai/core/AiApplicationExecutor`（2 处解析处接覆盖）；访问层 `AiModelAccessorRouter`/`DifyAgentAccessor`/`LlmGatewayAccessor`；续班触发 `app.service.syncdata.ai.renewal.*`、`dws/job/sync/SyncRenewalLiftReasonHandler`；退费触发 `domain/refundless/*` |

## 上线影响面

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 是 | `ai.agent.accessor.override.map`（json map：`ai_agent.number` → `{name, platformType, model, params}`），默认 `{}` |
| ES | 否 | |
| MySQL DDL | 否 | 不改表结构；代码切换阶段可能改 `ai_agent.platform_type`（数据变更非 DDL） |
| MQ | 否 | |
| 代课接口权限 | 否 | |

## 必须知道的坑

- 续班归因（新链路）已在用 gateway caller `gps-ai`——student-data 的 `llm.gateway.api-key` 落在 **`gps-ai`** 这个 caller 上，不是 `student-data-ai`；改网关侧路由要认这个 caller。
- 切换**不靠改 `ai_agent.platform_type`**：用 Apollo 开关（运行时可切、可单应用回滚）；库值改动属于代码切换阶段。
- Dify 与网关提示词形态不同：Dify 收扁平文本 query，网关走 OpenAI messages；`AiApplicationExecutor` 按平台类型自动选（网关走 messages），切平台后无需改提示词拼装。
- 未显式传 `model` 的应用走网关 `llm.gateway.default-model` 兜底（test 未配则用代码默认 `claude-sonnet-5`）——试点若不指定模型，需确认该模型在 `gps-ai` test 路由可用。
