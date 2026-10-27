---
title: 续班使用的dify下线 · 任务板
tags: [需求, 任务]
---

# 当前任务板

> 状态：`待办` `进行中` `已完成` `阻塞` `已取消`

## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 从 `origin/release` 建分支 `feature-xuban-dify-offline` | 已完成 | — | `--no-track`，起点 `origin/release` |
| T-02 | 定切换粒度与测试环境首个试点应用 | 已完成 | — | 粒度 `ai_agent`；试点 `用户画像/沟通摘要-test`(255107338300556288)；复用 `LlmGatewayAccessor` |
| T-03 | Apollo 新增按应用链路开关并落地（命中走 LLM 网关 `gps-ai`） | 进行中 | — | `AiAgentPlatformTypeResolver` + 接入 `AiApplicationExecutor`；待编译 + 配 TEST Apollo + 部署 |
| T-04 | 测试环境切一个试点应用并验证功能 | 待办 | T-03 | 与 Dify 结果对齐，见 [`verify.md`](verify.md) |
| T-05 | 全量切换剩余续班 + 退费 Dify 应用并逐个验证 | 待办 | T-04 | prod 17 个应用，见 README 清单 |
| T-06 | 代码切换：收口 / 移除 Dify 路径 | 待办 | T-05 | 功能替换稳定后再做 |

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
- T-05 7 个续班应用全部切到新链路并逐个验证 → 判据：每个应用各有一次成功调用留痕
- T-06 Dify 路径移除后无引用 → 判据：全仓检索 `Dify`/`dify-open` 无续班调用残留