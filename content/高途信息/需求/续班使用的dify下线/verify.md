---
title: 续班使用的dify下线 · 验证手册
tags: [需求, 验证]
---

# 验证手册

## 环境

| 项 | 值 |
|---|---|
| 泳道 | 未部署（待 T-03 落地后再定） |
| 依赖服务 | `student-data`（facade / service / dws） |
| 数据库 | `ees_data`（`ai_agent` / `ai_application`）；`mysql_query` 传 `ees_data.ai_agent` 自动定位 |

## 切换对象（test 环境，起于 2026-10-27 现查）

`ees_data.ai_agent`（`platform_type=1`，续班相关）：

| 应用（智能体） | number | 场景 | 关联 ai_application |
|-|-|-|-|
| 用户画像/沟通摘要-test | 255107338300556288 | 用户画像 + 沟通摘要 | 用户画像-test(255107395528688640) / 沟通摘要-test(255551371814636544) |
| 服务SOP分析 | 256325360053917696 | 服务建议 | 服务SOP分析(256327049255322624) |
| 素养服务建议 | 261423990261694464 | 服务建议 | 素养服务建议(261424322528162816) |
| 预测分层原因 | 262172718139452416 | 分层原因 | 预测分层原因(262173928596712448) |
| 问题建议-高中-豆包 | 255465773531663360 | 沟通建议 | 生成沟通建议-高中 等 |
| 问题建议-素养-豆包 | 255465673062353920 | 沟通建议 | — |
| 退费旅程分析 | 255733061835044864 | 退费旅程 | 退费旅程分析(255733517892204544) |
| 退费课程体验分析 | 255742622136547328 | 退费课程体验 | 退费课程体验分析(255742588441606144) |
| 退费根因分析 | 255743333766281216 | 退费根因 | 退费根因分析(255743373455931392) |
| 退费NPS分析 | 255743847351465984 | 退费NPS | 退费NPS分析(255743873725249536) |
| 降退费服务建议 | 255743632420648960 | 降退费服务建议 | 降退费服务建议(255743654696597504) |

新链路对照：`LLM网关-claude-sonnet-5`（prod 288169334962948096 / test 286798016992532480，`platform_type=2`）。

## 判定是否走了新链路（不看库，看留痕）

- `ees_data.ai_application_call_task` / `ai_application_call_task_result`：按 `ai_application_number` 看本次调用的平台与响应。
- 走 Dify：响应 `event=message` + UUID message_id；走网关：`event=litellm_proxy/...`、message_id 形如 `chatcmpl-...`。
- 服务端日志按 traceId 定位（`qingzhou-observe`）。

## Apollo 开关

| key | 默认 | 说明 |
|---|---|---|
| `ai.agent.platform.type.override.map` | `{}` | json map：`ai_agent.number`(字符串) → 目标 `platform_type`。命中即覆盖该应用的链路，未命中用库值 |

- 试点：TEST `application` 配 `{"255107338300556288": 2}` → `用户画像/沟通摘要-test` 走 LLM 网关。
- 读回：`apollo_get_key app_id=student-data env=TEST key=ai.agent.platform.type.override.map`（读**已发布**值）。

## 测试环境首个试点验证步骤（T-04）

1. 试点应用：`用户画像/沟通摘要-test`（`ai_agent.number=255107338300556288`）
2. Apollo TEST 配开关命中试点并发布；部署 `student-data`（泳道待定）到带该代码的镜像
3. 触发一次该应用的续班调用（走对应触发链路）
4. 校验：`ees_data.ai_application_call_task_result` 响应形态为网关（`chatcmpl-` / `event=litellm_proxy/...`）、业务产出与 Dify 一致、无报错
5. 反向验证：把开关改回（去掉该 key 或设 1）→ 回到 Dify（`event=message` + UUID）
