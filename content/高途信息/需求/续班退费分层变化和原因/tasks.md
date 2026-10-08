---
title: 续班退费分层变化和原因 · 任务板
tags: [需求, 任务]
---

# 当前任务板

## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 代码实现：同步 job、触达 job、查询服务和 Feign、student-center 接口 | 已完成 | — | student-data `f48c81f08`，student-center `1cb4e1b5f`（2026-09-07） |
| T-02 | 用 mock 数据跑通「同步 job → 快照表 → 查询接口」 | 已完成 | — | 2026-09-29 在 test-eco-2 验证通过（含 student-center 真实用户接口），见 verify.md「验证结果」 |
| T-03 | 按算法真表对齐 Entity 和字段 | 已完成 | — | 算法真表 `u_strategy.dwd_user_test_service_renew_lift_reason_df_df` 已确认；`AiPredictLevelReasonDetail`/DDL/同步服务已改完，student-data `b5b4601e9`（2026-09-29） |
| T-04 | 用 mock 数据验证 12:00 触达 job | 已完成 | — | 2026-09-29 验证：飞书消息实收（截图确认），Redis 幂等生效 |
| T-05 | 上线配置：线上 DDL 工单、Apollo、两个 xjob、代课权限登记、api 定版 RELEASE | 待办 | — | 提测前做 |
| T-06 | 快照表字段精简（删 `predict_score`/`model_version`/`status`）+ 班级索引 + 按班级回溯桥方法 | 已完成 | — | 代码已改、编译+单测通过、已 push 并发 test-eco-2。见 [[changelog]] 2026-10-08 |
| T-07 | `ai_predict_level_reason_detail` 加业务唯一键 `(user_number,clazz_number,subclazz_number,type,dt)`（让天工重复同步去重） | 待办（卡确认同步写入模式） | 需先确认天工那条同步任务的写入模式是 upsert 还是 insert | 同步任务 = 天工 **taskId 47772**（名字取错成 `ees_data.ai_renewal_attribution_follow_clazz_task_sync`，creator=zhangzeling，位于 **项目31 / 数据开发 / 续班&退费分层原因和跟进**；**nezhaId=67399**）。判据：① 若 upsert → 先清历史重复行，再提 test+prod DDL 工单加键；② 若纯 insert 追加 → 先把同步改成 upsert 再建键（否则重跑会 `Duplicate entry` 报错）。EES 侧无需改（`predict_level_reason_snapshot` 已幂等）。⚠️ 待确认写入模式：天工 getTask 只回基本信息；哪吒 `nezha.baijia.com` 的 API 从无头浏览器/代理连不通（`/api/cas/getAuth`、`/api/project/listProjects`、`/api/task/getTask` 全 pending）。明天用已登录浏览器打开哪吒任务 67399 看一眼「写入模式」，或走能进哪吒的网络。 |

## 完成判据

- T-02 落点：无代码改动（合入 release 后部署 test-eco-2）→ xjob 执行 `SyncPredictLevelReasonHandler`，参数 `1,20260905,20260907`，再执行 `2,20260906,20260907`，然后查 `ees_data.predict_level_reason_snapshot`；调 `/feign/predict/levelReason` 返回变化点与原因卡 → **已达标**（U1/scene 隔离验证通过；U2/U3 因真实花名册状态已超截止期被正确过滤，见 verify.md 说明，不算失败）。
- T-03 落点：`AiPredictLevelReasonDetail` Entity、`doc/xuban/predict_level_reason.sql` → 用算法真表某天的分区跑同步 job，丢弃率 <10%，快照表有数据 → **已达标**（本次是 mock 数据非真表分区，字段结构已按真表对齐；等算法真表数据落库后需再跑一次真实分区验证丢弃率）。
- T-04 落点：无 → xjob 执行 `RenewalLevelDownNotifyHandler`，参数 `20260907` → **已达标**（override 邮箱 `zhangzeling@gaotu.cn` 实收 U1 的下降通知；重复触发验证 Redis 幂等生效）。
- T-05 落点：DDL 工单、Apollo PROD、xjob PROD、sd.baijia.com 代课权限 → 线上逐项读回：表存在、Apollo 已发布、job 存在但调度关闭、接口已登记 31 → 不达标先按 release-config-check 对比分支 diff。
- T-07 落点：确认天工 taskId 47772 的写入模式后——若 upsert：清 `ai_predict_level_reason_detail` 重复行 → 提 test+prod DDL 工单 `ADD UNIQUE KEY uk_user_clazz_subclazz_type_dt(user_number,clazz_number,subclazz_number,type,dt)` → 触发同步两次验证「第二次不报错、行数不涨」；不达标先确认同步是否真的是 upsert。
