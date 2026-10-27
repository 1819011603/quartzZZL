---
title: 逐字段对比明细（test）
tags: [需求, 对比]
---

# 逐应用「Dify vs 网关」逐字段对比明细（test，2026-10-27）

方法：桥调 `compareAiApplication(app, userQuery, "test", {clazzNumber,userId})`，**同一输入**串行跑两侧，取两侧原始响应；清洗（去 think/代码围栏）后解析 JSON，**逐字段路径**比对。
样本：续班 clazz `500775385189890048` / user `7404351741`；退费用 mock 内容当 `userQuery`。

## 1. 结果总览

| 应用 | Dify | 网关 | JSON 结构 | 字段完全相同率 | 文本相似度 |
|-|-|-|-|-|-|
| 用户画像-test | `message` | `doubao-seed-2.0-lite` | 同（3 字段） | 0/3 = 0% | — |
| 沟通摘要-test | `message` | `doubao-seed-2.0-lite` | 同（1） | 0/1 = 0% | 0.36 |
| 生成沟通建议-高中 | `message` | `doubao-seed-2.0-lite` | 同（5） | 2/5 = 40% | — |
| 生成沟通建议-素养 | `message` | `doubao-seed-2.0-lite` | 同（5） | 2/5 = 40% | — |
| 服务SOP分析 | `message` | `doubao-seed-2.0-lite` | 同（41） | 8/41 = 20% | — |
| 预测分层原因 | `message` | `doubao-seed-2.0-lite` | 均纯文本 | — | 0.46 |
| 退费根因分析 | `message`（带 think） | `deepseek-flash` | 同（11） | 未逐字段（Dify 含 think） | 0.05 |
| 退费旅程分析 | `message`（带 think） | `deepseek-flash` | 同 | — | 0.06 |
| 退费课程体验分析 | `message`（带 think） | `deepseek-flash` | 同 | — | 0.08 |
| 退费NPS分析 | `message` | `deepseek-flash` | 均纯文本 | — | 0.20 |
| 素养服务建议 | `message`（带 think） | `deepseek-flash` | 同 | — | 0.05 |
| 降退费服务建议 | `message` | `deepseek-flash` | 同（3） | 1/3 = 33% | — |

## 2. 结论

- **结构层（JSON 字段名 / 层级）：全部一致** → 下游解析不受影响（这是关键信号）。
- **内容层：差异大**。字段完全相同率 0~40%、文本相似度 0.05~0.46——自由文本（总结/建议/原文）措辞不同，属正常（模型不同 + 随机性）。
- **枚举/分类字段也有差异**，需重点看（可能影响前端映射）：
  - 生成沟通建议-高中：`problemTypeName` Dify=`时间异议` / 网关=`未开课学员课前提醒`；`strategy` Dify=`灵活调课适配` / 网关=`课前温馨提醒`
  - 生成沟通建议-素养：`problemTypeName` Dify=`调课需求处理` / 网关=`调课咨询`
  - 服务SOP分析：`sopAnalysisItemList` 条数不同（Dify 7 / 网关 8）、`score` 不同（1 vs 3）
- **Dify 侧普遍带 `think` 思考块、篇幅更长**；网关更干净（续班带 `json_object` 出纯 JSON）。

## 3. 请求参数差异（同 trace 实证）

traceId `9e84dced-3614-499e-80b7-b1fb0bb0ca4d.0.3`（退费根因分析）：
- 外呼：Dify→`/dify/api/v1/chat-messages`；网关→`/v1/chat/completions`
- `ai_application_call_task_result.actual_query` 两条（同一应用、同输入）：
  - 网关那条（len 6651）：`system` = **完整提示词**（`gateway_core_prompt`）+ JSON 输出要求
  - Dify 那条（len 2109）：`system` = **标签「退费根因分析」** + JSON 输出要求；**完整指令由 Dify 内部另加**
- 即：两侧**最终给模型的指令内容大致等价**（都含完整指令 + JSON schema），但**来源/措辞不同**，且**模型不同**（Dify 内部模型 vs 网关 `deepseek-v4.1-flash-1017`）。

## 4. 更严的验收建议

1. 固定一批样本（含边界：未开课/无数据/多原因）；
2. 只对**枚举/分类字段**（`problemTypeName`/`strategy`/`category`/`reasonJudgeType`/`score`）定命中率门槛（如语义一致 ≥80%）；
3. 文案类字段接受措辞差异，只校验「非空 + 结构合法 + 关键约束（字数/占位符）」。

## 5. 线上真实案例对比（prod Dify vs 网关）

用**线上真实调用**同输入对比（消除 test 数据差异）：

- 案例：`entry_key` 尾 `...-v5`（学员 `7650003008`，班级 `545548561373222912`，辅导班 `35873565594092032`），prod `ai_application_call_task_result.id=75006117`。
- 做法：取该行 `actual_query`（发给 Dify 的输入）+ `result`（Dify 答案）；用**同一输入**打网关（test-llm，`deepseek-v4.1-flash-1017`），对比。

| | 线上 Dify（deepseek-v4-flash-0731） | 网关（deepseek-v4.1-flash-1017） |
|-|-|-|
| 条数 | 6 | 5 |
| 分类 | 400-2、300-3、200-2、500-1、800-1、700-5 | 300-3、400-2、500-1、400-3、200-2 |
| 核心原因 | 400-2、300-3（是） | 300-3、400-2（是） |

- **交集**：`200-2 / 300-3 / 400-2 / 500-1`（4 个）
- 线上独有：`700-5 / 800-1`；网关独有：`400-3`
- **核心原因一致**；边缘原因随模型不同小幅漂移。
- 复现脚本：`/tmp/cmp_prod.py`（prod 数据先落盘 `/tmp/prod_rows_clean.json`）。

**结论**：线上案例的核心退费原因对得上；分类集合有 1-2 条漂移，需业务确认可接受。

## 6. Dify（源）与我们直连网关的**代码级差异**（模型同名后仍低相似度的原因）

对同一模型（如退费 `deepseek`），Dify 与我们的调用仍有以下差别（源码 `api/core/agent/*`）：

| 差异点 | Dify 做法 | 我们的做法 |
|-|-|-|
| **模型参数** | 用应用配置的 `model_config.model.completion_params` 下发，如退费应用设了 **`enable_thinking: true`**、`stop: []`（`fc_agent_runner` → `invoke_llm(model_parameters=app_config.model_conf.parameters)`） | 只传 `model` + `max_tokens`，其余走网关默认 → **thinking 等参数不同** |
| **消息结构** | `_organize_prompt_messages` = `[system(pre_prompt)]` + `[user(我们发去的整段 flat prompt 文本)]` | `[system(gateway_core_prompt+JSON要求)]` + `[user(数据)]` |
| **agent 机制** | agent-chat + `function_call`，传 `tools`（即使空数组）、可 `max_iteration` 多轮 | 单次调用、不传 tools |
| **max_tokens** | `recalc_llm_max_tokens` 按上下文动态算 | 固定 8192 |
| **后处理** | `sensitive_word_avoidance` / moderation / annotation_reply 等开关 | 无（这些开关在部分应用是关的） |

> 最直接、可对齐的一项：**`completion_params`**（尤其 deepseek 的 `enable_thinking`）。在 Apollo override 的 `params` 里比照 Dify 应用的同名字段下发，相似度会显著提升。

### 已对齐的参数（配在 Apollo `ai.agent.accessor.override.map[].params`，按应用区分）
| 应用 | params |
|-|-|
| 用户画像/沟通摘要、服务SOP分析、预测分层原因 | `{"response_format":{"type":"json_object"},"stop":[]}` |
| 退费根因 / 退费旅程 / 降退费服务建议 | `{"enable_thinking":true,"stop":[]}` |
| 退费NPS / 退费课程体验 | `{"stop":[]}` |
| 素养服务建议 | `{"temperature":0.7,"enable_thinking":true}` |

### 对齐后相似度（test，同上输入）
| 应用 | 对齐前 | 对齐后 |
|-|-|-|
| 退费根因分析 | 0.228 | **0.531** |
| 用户画像-test | 0.36 | **0.598** |
| 服务SOP分析 | — | 0.246（长列表，条目措辞散，结构对齐即可） |

> 仍存的差异：**消息结构**（Dify `user`=我们发的整段 flat prompt/嵌套 JSON；我们 `user`=纯数据）、**agent 机制**（function_call/tools/多轮）、**动态 max_tokens**、LLM 随机性。列表型应用相似度天然偏低。

### 可核对项（各应用 Dify 的 completion_params）
- 退费根因/旅程/降退费（deepseek）：`{"enable_thinking": true, "stop": []}`
- 退费NPS/课程体验（旧 R1）：`{"stop": []}`
- 用户画像/沟通摘要、服务SOP（doubao）：`{"stop": []}`
- 素养服务建议（工作流）：`{"temperature": 0.7, "enable_thinking": true}`
### 更正 / 结论（2026-10-28）
- **「agent 机制(function_call/tools)不同」不成立**：扫描全部应用 `agent_mode.tools` **全为空**、`datasets` 仅 3 个（见下），没配就是空。收回该差异项。
- **隐藏能力扫描**（除知识库外无其它）：
  - `tools`=空；敏感词/注释/more_like_this/`gt_configs`=关；`completion_prompt_config` 对 agent-chat 不生效；`文件上传` enabled 但我们不传文件。
  - **`DATASET`(知识库) 仅 3 个**：【废弃】降退费服务建议、问题建议-素养、问题建议-高中（后两个=已保留的「生成沟通建议」；前者废弃态）。
- **消息结构对齐 Dify：试过、无收益、已回退**。同一应用相似度 0.37/0.55（两次）落在简单结构 0.53 的噪声区间内 → 剩余差异主要来自**模型随机性 + 措辞**，不是结构。
- **可补齐的参数已补齐**（`completion_params`：`enable_thinking`/`stop`/`temperature`，配在 Apollo 按应用区分）→ 退费根因相似度 0.228→0.531、用户画像 0.36→0.598。
