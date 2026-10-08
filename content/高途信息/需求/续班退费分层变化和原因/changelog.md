---
title: 续班退费分层变化和原因 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

---

## 2026-10-08 · ES 写回落地 + 上线方案

### 🤖 Claude
- **新链路写回花名册 ES（续班+退费）**：`PredictLevelReasonSyncService` 落库变化点后发 MQ——续班发 `renewal_lift_result_topic`（tag `renewal_lift_result`），消息**多带一个 `levelOnly=true` 标志位、不带分数**；退费发退费 topic（tag `ai_refund_intent_update`）只带 `aiRefundIntentScoreResult`。写回字段：续班 `renewalIntentionPredictLevelResult`、退费 `aiRefundIntentScoreResult`，**只写分层列**。
- **兼容/回退开关**：新增 `predict.level.reason.es.write.enable`（默认 true）gate 写回——置 false 时同步照常落库但不发 MQ，可秒级停写、无需发版回退老链路。老链路代码/消费端**一行未删**，老链路靠 `renewal.lift.result.consumer.open.switch` / `dws.refund.intent.switch` + 老 job 启停恢复。
- **消费端兼容（不改老逻辑）**：`RenewalLiftResultConsumer` 见 `levelOnly` 标志位时只写分层列、跳过分数非空校验；老消息不带该标志，行为不变。退费消费端 `DwsRefundIntentConsumer` 本就认 `aiRefundIntentScoreResult`，未改。
- **展示侧兼容**：student-center `FieldsConvertDataQueryServiceImpl` / `RefundFiledConvertDataQueryServiceImpl` 改为**优先读分层列、缺失回退分数换算**。
- **老链路要停的两个 job（2026-10-08 查 PROD）**：真正在跑的是 `SyncRenewalLiftSnapshotHandler`(10413, 530, `0 0 12 * * ?`) 和 `refundPredictionCheckHandler`(10073, 314, `0 0 6,9 * * ?`)；`SyncRenewalLiftResultHandler`/`SyncRenewalLiftReasonHandler`/`SyncRefundResultHandler` 早已停止。**注意别把 `SyncRefundResultHandler`（手动回溯入口）当日常 job。**
- 落点：student-data `d35b935e`、student-center `f389d1865`（单测 `b820460fd`）已发 **test-eco-2**，三服务 eureka UP。
- 验证：mock 明细 `layer=D` → 桥调 `syncOneDay(1,"20260909")` → 花名册 `renewalIntentionPredictLevelResult` 由 **3→4**、`updateTime` 推进；退费 `aiRefundIntentScoreResult` 实测写 `4`。转换单测 4 个全过。**xjob**：test 重建 `SyncPredictLevelReasonHandler`=9733 / `RenewalLevelDownNotifyHandler`=9734，指定泳道 pod 触发均 handleCode 200（9733 跑 `1,20260905,20260907` 后 ES 写回 3；9734 Redis 幂等重复跳过）；**PROD 已建 12753（group 530）/ 12754（group 314），均「已停止」待上线启用**。⚠️ 触发默认 `FIRST` 会打到 base pod（handler not found），泳道必须 `execute_address=<pod>`。

---

## 2026-10-08

### 🤖 Claude
- **快照表字段精简**（`predict_level_reason_snapshot`）：删除 `predict_score`、`model_version`、`status` 三列。依据：算法真表始终不下发预测分数与模型版本，两列 100% 为 NULL；`status` 无任何写 2（软删）的代码路径、恒为 1。
- **连带删死代码**：同步链路里依赖 `predict_score` 的「发 MQ（复用 `renewal_lift_result_topic`）刷 ES 花名册分数列」分支恒被跳过（算法不下发分数），连同 `sendRosterSyncMessage`、`renewalLiftResultTopic`、`fuwuOnsMqProducer` 一并删除；查询侧 `formatProbability` 与出参 `LevelReasonCardDTO.probabilityDesc` 同因删除。
- **新增索引（支持按班级回溯）**：`ai_predict_level_reason_detail` 加 `idx_clazz_type_dt(clazz_number,type,dt)`；快照表加 `idx_clazz_scene_dt(clazz_number,scene,record_dt)`。快照表原有唯一键 `uk_scene_user_subclazz_dt(scene,user_id,subclazz_number,record_dt)` 保持不变（天然防重复行，实测无重复行）。
- **新增桥可调方法** `PredictLevelReasonSyncService#backfillByClazz(clazzNumber, scene, dataDt)`：按班级把该场景某天的算法明细重跑一遍变化点落库，复用 job 的 `processBatch` 同一套逻辑（分组/校验/截止过滤/变化点判定/唯一键幂等），用于同步 job 漏跑或失败后的定点补数；返回可读统计串。经 acl 桥 `invoke_service` 调用。
- 落点：student-data `feature-predict-level-reason`，提交 `c3e190ef5` 已 push；**已发 test-eco-2**（student-data + student-data-dws，均 eureka UP）。验证：接口 `/feign/predict/levelReason` 返回 A→B/C 变化点+原因卡、`probabilityDesc` 已消失 ✅；同步 job 9710 新代码 handleCode 200、落库 21 ✅；桥调 `backfillByClazz` 被登录挡住（`rvoCode 3 登陆信息获取异常`，未验证，逻辑与 job 同源）。test 库 DDL 工单 **8083**（快照表删 3 列+加索引）、**8084**（明细表加班级索引）已提交，待 SRE 审批发布后生效。

---

## 2026-09-29

### 🤖 Claude
- 算法真表已确认：`u_strategy.dwd_user_test_service_renew_lift_reason_df_df`（Hive，分区 `dt`/`type`），经天工 1:1 同步到 `ees_data.ai_predict_level_reason_detail`；结构从「长表一行一因子」改为「一行一学员×辅导班×天」，分层在 `layer`，因子明细是 `factors` JSON 数组。T-03 解除阻塞。
- 在 test-eco-2 完成 mock 数据 → 快照表 → 查询接口 → 飞书触达的全链路验证：Apollo 7 个 key 已发布、飞书消息真实送达（截图确认）、Redis 幂等生效。T-02/T-04 视为完成。
- U2（无变化/跨级下降）、U3（分层回升）两个测试场景本次验不到：这两个学员是 2026-09-07 造的旧 fixture，三周后其真实花名册状态已过 7 天截止线，被 `PredictLevelDeadlineChecker` 正确判定超期跳过——这是业务逻辑按设计工作，不是缺陷，但意味着复用老 fixture 做「稳定态」类场景会随时间失效，以后要验这类分支得挑当前仍处于进行中状态的学员。

---

## 2026-09-04

### 🤖 Claude
- 最终采用 Hive 按天分区的长表（一行一个因子），替代早期「EES 期望宽表」草案，因为这是算法反讲确定的交付形态。
- 最终由 EES 自己发飞书触达，替代「消息盒子 + 企微 + 通知中心」，因为 PRD 变更，触达侧没有人力。
- 定了：EES 按算法给的 `idx` 升序透传、不做排序，因为算法已按 |SHAP| 排好序，而重要性数值没有单独的字段，EES 也无法自己重排。
