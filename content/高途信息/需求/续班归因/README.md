---
title: 续班归因
aliases:
  - 未续归因
  - 已续归因
  - 未续归因和跟进
  - 未续归因和跟进+已续归因
  - 续班归因和跟进
  - renewalReason
  - unrenewedReasonAi
  - renewedReasonAi
  - 归因回归
  - banshan 48758
branches:
  - student-data: feature-xuban-ai
status: 已上线
repos:
  - student-data
updated: 2026-09-10
---

# 续班归因（未续归因和跟进 + 已续归因）

> **状态：已上线**（2026-09 上线，功能分支 `feature-xuban-ai` 已合入）
> 本目录取代原 skill `renewal-reason-regression`（已删除）。以后提到「续班归因 / 未续归因 / 已续归因 /
> renewalReason / 归因回归」，先读本目录。

## 一句话

对**未续班**学员用大模型分析未续原因 + 给跟进建议；对**已续班**学员用大模型总结已续原因。
结果落 `ees_data.ai_app_clazz_user_scene`，并同步到花名册 ES 供筛选。

## 链接

- 需求文档（PRD）：【PRD】未续归因和跟进+已续归因
- 技术方案：【续班优化】未续归因和跟进+已续归因
- TAPD 迭代：https://www.tapd.cn/tapd_fe/22531521/iteration/card/1122531521001014662?q=095ef2ff52bc60f5e881c83e43e109de
- 测试用例（banshan）：https://qa.baijia.com/banshan/#/case/caseList/171 （用例集 48758）
- 排期：技术反讲 2026-08-10 → 提测 → 上线（已完成）

## 相关文档

- [线上数据量盘点（2026-09-10）](data-volume-2026-09-10.md) —— 今日调用量、日趋势、口径与 SQL
- [核心口径与排查手册](runbook.md) —— 表结构 / ES 字段 / 反射入口 / 已知坑

## 主仓库

`student-data`，核心包 `com.gaotu.student.data.domain.renewal.reasoning`。

| 角色 | 类 |
|-|-|
| 班级级 Job | `facade/job/RenewalAttributionFollowClazzTaskHandler` |
| MQ 消费 | `facade/mq/renewal/RenewalReasonTaskConsumer`、`RenewalReasonRefreshConsumer` |
| HTTP 入口 | `facade/api/RenewalReasonController` → `POST /inner/renewal/reason/trigger` |
| 未续实现 | `domain/renewal/reasoning/impl/RenewalUnrenewedReasonServiceImpl` |
| 已续实现 | `domain/renewal/reasoning/impl/RenewalRenewedReasonServiceImpl` |
| 大模型接入 | `domain/ai/core/agentaccess/{LlmGatewayAccessor,DifyAgentAccessor,AiModelAccessorRouter}` |
