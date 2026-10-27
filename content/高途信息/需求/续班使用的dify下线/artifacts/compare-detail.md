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