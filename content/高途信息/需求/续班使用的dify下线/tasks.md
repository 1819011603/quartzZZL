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
| T-03 | Apollo 新增按应用链路开关并落地（命中走 LLM 网关 `gps-ai`） | 已完成 | — | 现为 `ai.agent.accessor.override.map`（`{name,platformType,model,params}`）+ `AiApplicationExecutor` 接入（commit `f0c58aaf`）；TEST Apollo 已发布 |
| T-04 | 测试环境切一个试点应用并验证功能 | 已完成 | — | 试点 `沟通摘要-test`：开关开=网关/关=Dify、模型=按应用指定、`params` 生效，均实测通过 |
| T-05 | 全量切换剩余续班 + 退费 Dify 应用并逐个验证 | 待办 | — | prod 17 个应用，见 README 清单 |
| T-06 | 代码切换：收口 / 移除 Dify 路径 | 待办 | T-05 | 功能替换稳定后再做 |
| T-07 | 每应用模型一一对应：按应用配 `model`/`params` + 网关加路由 | 已完成 | — | 映射全定：Doubao 旧系列→`doubao-seed-2-0-lite-260428`、R1→`deepseek-v4.1-flash-1017`；gps-ai test 加 2 条路由（37268/37270）；prod 路由并入 T-05 上线前做 |

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
- T-05 17 个应用（续班+退费）全部切到新链路并逐个验证 → 判据：每个应用各有一次成功调用留痕
- T-07 每应用 `model`/`params` 落 Apollo 且 gps-ai 路由齐 → 判据：`apollo_get_key` 读回各应用配置、`callerRoute` 读回目标模型
- T-06 Dify 路径移除后无引用 → 判据：全仓检索 `Dify`/`dify-open` 无续班调用残留