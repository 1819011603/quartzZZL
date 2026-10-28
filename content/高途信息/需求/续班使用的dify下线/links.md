---
title: 续班使用的dify下线 · 链接中心
tags: [需求, 链接]
---

# 链接中心

## 需求与方案

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 技术项梳理表 | 当前技术需求梳理（第 10 行 = 续班使用的dify下线） | https://gaotuedu.feishu.cn/sheets/LvFhsGY7UhTjbWtO7r9c6nkCnbS | 2026-10-27 |
| 技术方案 | 续班使用的dify下线（待建） | — | 2026-10-27 |
| PRD | 无（技术优化项，非业务需求） | — | 2026-10-27 |

## 平台 / 网关

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| AI 应用平台 | 应用列表（智能体 / 对话流） | https://os.baijia.com/apps | 2026-10-27 |
| AI 服务访问 | 大模型网关 access / caller 路由（caller = `gps-ai`） | https://ai.baijia.com/ai-service/access | 2026-10-27 |
| Dify 控制台（os.baijia.com 代理） | 团队应用列表 `…/dify/api/console/api/gt-apps?scope=team`；应用详情 `…/dify/api/console/api/apps/{app_id}` | https://os.baijia.com/dify/api/console/api | 2026-10-27 |
| Dify 服务 API | `/info`（用 `ai_agent.access_key` 返应用名，核对归属）；`/chat-messages`（业务调用） | https://dify-open.baijia.com/dify/api/v1 | 2026-10-27 |
| Dify 引擎 | 待下线的 Dify（续班现用） | https://dify-open.baijia.com/dify/api/v1 | 2026-10-27 |

## 开发与测试

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 提示词归档 | 退费 10 个 Dify 提示词（迁移用） | `artifacts/dify-refund-prompts/` | 2026-10-27 |
| 对比明细 | 逐应用 Dify vs 网关 字段级对比 | [`artifacts/compare-detail.md`](artifacts/compare-detail.md) | 2026-10-27 |
| 知识库替换评估 | 生成沟通建议（有知识库）替换评估 | [`artifacts/dify-kb-eval.md`](artifacts/dify-kb-eval.md) | 2026-10-27 |
| 网关模型映射 | LLM 网关 redirectToModelCode 映射表 | [`artifacts/llm-gateway-model-mapping.md`](artifacts/llm-gateway-model-mapping.md) | 2026-10-28 |
| **prod 交接待办** | 交接给其他 AI 执行的 prod 上线清单 | [`handoff.md`](handoff.md) | 2026-10-28 |
| 迁移表 | 续班退费Dify下线（sheet 新建 tab） | https://gaotuedu.feishu.cn/sheets/T9lhsNwL4hzovStIDVDcyy8znRf?sheet=Fn06qE | 2026-10-27 |
| MR | student-data !1796（feature-xuban-dify-offline → release） | https://git.baijia.com/gaotu/yunying_workbench/student-data/-/merge_requests/1796 | 2026-10-27 |
| 接口文档 | — | — | 2026-10-27 |

## 上线

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 上线checklist | — | — | 2026-10-27 |
| 发布计划 | — | — | 2026-10-27 |

## 跨会话检索锚点

- 飞书表格 token：`LvFhsGY7UhTjbWtO7r9c6nkCnbS`（当前技术需求梳理）
- 分支：`student-data:feature-xuban-dify-offline`
- 平台 caller/场景：`gps-ai`
