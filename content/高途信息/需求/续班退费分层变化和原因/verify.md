---
title: 续班退费分层变化和原因 · 验证手册
tags: [需求, 验证]
---

# 验证手册

## 环境

| 项 | 值 |
|---|---|
| 泳道 | test-eco-2（student-data / dws / student-center） |
| 数据库实例 | gaotu-polar-test-02（cluster_id 149）· `ees_data` |
| 开关 | `predict.level.reason.enable.all=true`，不开的话查询接口一律返回空结构 |

## 造好的测试数据

`ees_data.ai_predict_level_reason_detail` 里有手工造的 mock 数据，共 60 行（2026-09-28 查库确认仍在）。每组 6 条因子，idx 0~2 是负向、3~5 是正向；idx=2 和 idx=5 是不可干预；`model_version=stage4-mock-20260907`。

| scene | userId | clazzNumber | subclazzNumber | 分层序列 | 验什么 |
|---|---|---|---|---|---|
| 1 | 6511186386 | 513468253373333504 | 32112520197832960 | 0905=A / 0906=B / 0907=C | 趋势图主用例，触发触达（U1） |
| 1 | 6611409826474 | 506390872749809664 | 31649445315871360 | 0905=B / 0906=B / 0907=D | 无变化不落库、跨级下降（U2） |
| 1 | 3447122285 | 495776084336369664 | 30986005950628096 | 0906=C / 0907=B | 分层回升不触达（U3） |
| 2 | 6511186386 | 513468253373333504 | 32112520197832960 | 0906=中 / 0907=高 | 和续班用同一学员 × 辅导班，验证 scene 隔离 |

## 怎么调

1. xjob `SyncPredictLevelReasonHandler`，参数格式：空=全场景+昨天 / `scene` / `scene,dataDt` / `scene,startDt,endDt`
2. 预期快照表 scene=1 写 7 条、scene=2 写 2 条。
3. `POST /ai/clazzUser/predictLevelReason`，body 为 `{"scene":1,"userId":6511186386,"clazzNumber":513468253373333504,"subclazzNumber":32112520197832960}`；查 hover 历史时加 `recordDt`（毫秒时间戳，直接用趋势图返回的值）。
4. xjob `RenewalLevelDownNotifyHandler`，参数 `20260907`，预期只有 U1、U2 收到通知。
5. 验证前先确认新 pod 的 eurekaStatus=UP。

## 能验到哪一层

- ✅ 可验：同步聚合、变化点、截止过滤、查询编排、飞书触达（全部基于 mock）
- ❌ 验不了：分层是否可信、真实字段能否对上，要等算法真表（T-03）

## 新建的东西

| 类型 | 名称 | 位置 / 值 | 测试 | 线上 |
|---|---|---|---|---|
| 表 | `predict_level_reason_snapshot` | ees_data，DDL 见 `doc/xuban/predict_level_reason.sql` | 已建 | 待工单 |
| 表 | `ai_predict_level_reason_detail` | ees_data，算法表（EES 拟定） | 已建（mock） | 由算法侧提供 |
| xjob | `SyncPredictLevelReasonHandler` | student-data-dws | 未确认 | 待建 |
| xjob | `RenewalLevelDownNotifyHandler` | student-data，每天 12:00 | 未确认 | 待建 |
| Apollo | `predict.level.reason.enable.all` / `.enable.dept` | 联调 true；线上按学部白名单 | 未确认 | 待配 |
| Apollo | `predict.level.history.limit` | 10 | 未确认 | 待配 |
| Apollo | `predict.level.reason.deadline.days` | 7 | 未确认 | 待配 |
| Apollo | `predict.level.reason.sync.batch.size` | 1000 | 未确认 | 待配 |
| Apollo | `predict.level.down.notify.enable.all` | 联调 true | 未确认 | 待配 |
| Apollo | `predict.level.down.notify.receiver.override` | 联调填自己邮箱，**必填** | 未确认 | 不配 |
| Apollo | `predict.level.down.notify.idempotent.days` | 30 | 未确认 | 待配 |
| jar | student-data-api | 0.9.9.24-SNAPSHOT | 已发 | 待定版 RELEASE |
