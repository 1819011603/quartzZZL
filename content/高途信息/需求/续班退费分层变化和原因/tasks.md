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
| T-05 | 上线配置：线上 DDL 工单、Apollo、两个 xjob、代课权限登记、api 定版 RELEASE | 已完成 | — | 快照表 DDL 146755 已发布（PROD 表已建）；代课权限 31 已登记；Apollo PROD 已发布；api 定版 0.9.9.24-zzl-RELEASE 已发；代码已合并 release。 |
| T-08 | 上线当天执行：发 3 个服务镜像（student-data/dws/student-center）、停老 job 10413+10073、启新 job 12753+12754、飞书【ees助手】可用范围设「全员可用」、逐项读回验证 | 待办 | 依赖 SRE 发布快照表 DDL、天工明细表就绪 | 步骤见 [`上线方案.md`](上线方案.md) 二/七/十一/十三 |
| T-09 | 线上天工同步任务（源正式表 → `ees_data_prod`1479 / `ees_data.ai_predict_level_reason_detail`） | 已完成 | — | 目录 103709 新建 taskId **47936**/节点 **104349**，照搬 47772 只改源表名+datasource，读回一致。已发布（nezhaId **67730**）、每天 14:00；实测出数 renew+refund。 |
| T-10 | 明细表清理 job（保留 30 天） | 已完成 | — | xjob **12793**（GLUE_GROOVY/group 530），每天 03:00 `DELETE ai_predict_level_reason_detail WHERE dt<今天-30 LIMIT 2000`，快照不动；已实测 handleCode=200、已启动。 |
| T-06 | 快照表字段精简（删 `predict_score`/`model_version`/`status`）+ 班级索引 + 按班级回溯桥方法 | 已完成 | — | 代码已改、编译+单测通过、已 push 并发 test-eco-2。见 [[changelog]] 2026-10-08 |
| T-07 | `ai_predict_level_reason_detail` 加业务唯一键（天工去重） | 已完成 | — | PROD 表已有唯一键 **`uk_dt_user_clazz_sub_type(dt,user_number,clazz_number,subclazz_number,type)`**（`NON_UNIQUE=0`，实测）；天工 upsert 幂等已验证（多次跑行数不翻倍）。 |

## 完成判据

- T-02 落点：无代码改动（合入 release 后部署 test-eco-2）→ xjob 执行 `SyncPredictLevelReasonHandler`，参数 `1,20260905,20260907`，再执行 `2,20260906,20260907`，然后查 `ees_data.predict_level_reason_snapshot`；调 `/feign/predict/levelReason` 返回变化点与原因卡 → **已达标**（U1/scene 隔离验证通过；U2/U3 因真实花名册状态已超截止期被正确过滤，见 verify.md 说明，不算失败）。
- T-03 落点：`AiPredictLevelReasonDetail` Entity、`doc/xuban/predict_level_reason.sql` → 用算法真表某天的分区跑同步 job，丢弃率 <10%，快照表有数据 → **已达标**（本次是 mock 数据非真表分区，字段结构已按真表对齐；等算法真表数据落库后需再跑一次真实分区验证丢弃率）。
- T-04 落点：无 → xjob 执行 `RenewalLevelDownNotifyHandler`，参数 `20260907` → **已达标**（override 邮箱 `zhangzeling@gaotu.cn` 实收 U1 的下降通知；重复触发验证 Redis 幂等生效）。
- T-05 落点：DDL 工单、Apollo PROD、xjob PROD、sd.baijia.com 代课权限 → 线上逐项读回：表存在、Apollo 已发布、job 存在但调度关闭、接口已登记 31 → 不达标先按 release-config-check 对比分支 diff。
- T-07 落点：确认天工 taskId 47772 的写入模式后——若 upsert：清 `ai_predict_level_reason_detail` 重复行 → 提 test+prod DDL 工单 `ADD UNIQUE KEY uk_user_clazz_subclazz_type_dt(user_number,clazz_number,subclazz_number,type,dt)` → 触发同步两次验证「第二次不报错、行数不涨」；不达标先确认同步是否真的是 upsert。
