---
title: 续班使用的dify下线 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

---

## 2026-10-27

### 🤖 Claude

- 定为技术优化项（非业务需求），归档名沿用技术项表原名「续班使用的dify下线」
- 最终采用「Apollo 按应用独立切换 + 两阶段（先功能替换、后代码切换）」，替代「直接改 `ai_agent.platform_type`」的一次性做法——因为要能单应用灰度与随时回滚
- 新链路定为复用已上线的 `LlmGatewayAccessor`（caller/场景 `gps-ai`），续班归因已在走该 caller
- 建分支 `feature-xuban-dify-offline`（`--no-track`，起点 `origin/release`）
- 开关落点为新增 `AiAgentPlatformTypeResolver`（Apollo json map `ai.agent.platform.type.override.map`），在 `AiApplicationExecutor` 两处解析处接覆盖——不改库即可单应用切/回滚
- 范围扩到**退费 AI**（prod 共 17 个 Dify 应用：续班 7 + 退费 10），不再只续班
- 试点定为 test `用户画像/沟通摘要-test`（`ai_agent.number=255107338300556288`）

### 👤 我

- 给出技术项表链接 `https://gaotuedu.feishu.cn/sheets/LvFhsGY7UhTjbWtO7r9c6nkCnbS`（第 10 行）
- 给出 AI 应用平台链接 `https://os.baijia.com/apps`
- 明确：用 LLM 替换，都用 `https://ai.baijia.com/ai-service/access`、`gps-ai` 这个场景
- 确认：粒度用 `ai_agent`；试点用 `用户画像/沟通摘要-test`；复用现有 `LlmGatewayAccessor`；退费也在范围