---
title: 续班退费分层变化和原因 · 任务板
tags: [需求, 任务]
---

# 当前任务板

## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 代码实现：同步 job、触达 job、查询服务和 Feign、student-center 接口 | 已完成 | — | student-data `f48c81f08`，student-center `1cb4e1b5f`（2026-09-07） |
| T-02 | 用 mock 数据跑通「同步 job → 快照表 → 查询接口」 | 待办 | — | 快照表目前为空；2026-09-28 已合入 release（student-data `9589ca6fe`，student-center `254f157f6`） |
| T-03 | 按算法真表对齐 Entity 和字段 | 阻塞 | 算法真表未确认 | 当前表名和字段是 EES 自己拟定的 |
| T-04 | 用 mock 数据验证 12:00 触达 job | 待办 | — | 依赖 T-02 写好快照数据 |
| T-05 | 上线配置：线上 DDL 工单、Apollo、两个 xjob、代课权限登记、api 定版 RELEASE | 待办 | — | 提测前做 |

## 阻塞详情

### T-03
- **卡在**：用户 2026-09-28 说算法真表已 ready，但表名 / 库还没拿到。
- **需要谁**：梓淳 / yuyong
- **可以先做**：T-02、T-04 继续用 mock 表跑。

## 完成判据

- T-02 落点：无代码改动（合入 release 后部署 test-eco-2）→ xjob 执行 `SyncPredictLevelReasonHandler`，参数 `1,20260905,20260907`，再执行 `2,20260906,20260907`，然后查 `ees_data.predict_level_reason_snapshot`：scene=1 有 7 条、scene=2 有 2 条；调 `/ai/clazzUser/predictLevelReason`（数据见 verify）返回 3 个变化点，原因卡有 6 条因子，idx=2 和 idx=5 的 suggestAction 为空 → 不达标先查 xjob joblog 的丢弃计数，以及 pod 是否 eureka UP。
- T-03 落点：`AiPredictLevelReasonDetail` Entity、`doc/xuban/predict_level_reason.sql` → 用算法真表某天的分区跑同步 job，丢弃率 <10%，快照表有数据 → 不达标先查 joblog 里的丢弃原因分布。
- T-04 落点：无 → xjob 执行 `RenewalLevelDownNotifyHandler`，参数 `20260907`，override 邮箱只收到 U1、U2 两条通知，U3（分层回升）不发 → 不达标先查 Redis `predict:level:down:notify:*` 幂等 key 是否残留。
- T-05 落点：DDL 工单、Apollo PROD、xjob PROD、sd.baijia.com 代课权限 → 线上逐项读回：表存在、Apollo 已发布、job 存在但调度关闭、接口已登记 31 → 不达标先按 release-config-check 对比分支 diff。
