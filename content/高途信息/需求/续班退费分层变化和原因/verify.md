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

~~`ees_data.ai_predict_level_reason_detail` 里有手工造的 mock 数据，共 60 行~~ → **2026-09-29 重造**：算法真表 schema 确认后（`layer`/`factors`/`type` 单行结构），旧 60 行（`layer`/`factors`/`type` 全空）已清空，重新写入 10 行，覆盖下表 4 组场景。因子明细在 `factors` JSON 数组里（每组 6 条，idx 0~2 负向、3~5 正向，idx=2/5 不可干预），不再是独立行。

| scene | userId | clazzNumber | subclazzNumber | 分层序列（layer） | 验什么 | 2026-09-29 验证结果 |
|---|---|---|---|---|---|---|
| 1(renew) | 6511186386 | 513468253373333504 | 32112520197832960 | 0905=A / 0906=B / 0907=C | 趋势图主用例，触发触达（U1） | ✅ 全通过 |
| 1(renew) | 6611409826474 | 506390872749809664 | 31649445315871360 | 0905=B / 0906=B / 0907=D | 无变化不落库、跨级下降（U2） | ⚠️ 被截止时间过滤：该学员真实花名册状态已过 7 天线（旧 fixture，非缺陷），需换新学员重验 |
| 1(renew) | 3447122285 | 495776084336369664 | 30986005950628096 | 0906=C / 0907=B | 分层回升不触达（U3） | ⚠️ 同上，被截止时间过滤 |
| 2(refund) | 6511186386 | 513468253373333504 | 32112520197832960 | 0906=中 / 0907=高 | 和续班用同一学员 × 辅导班，验证 scene 隔离 | ✅ 全通过 |

## 怎么调

1. xjob `SyncPredictLevelReasonHandler`（test jobId=9710），参数格式：空=全场景+昨天 / `scene` / `scene,dataDt` / `scene,startDt,endDt`
2. 2026-09-29 实测：scene=1 参数 `1,20260905,20260907` 落库 3 条（仅 U1，U2/U3 被截止过滤）；scene=2 参数 `2,20260906,20260907` 落库 2 条（U1）。
3. 查询走 student-data 自己的 Feign `/feign/predict/levelReason`（student-center 的 `/ai/clazzUser/predictLevelReason` 是它的上层封装，本次未验证），body 为 `{"scene":1,"userId":"6511186386","clazzNumber":"513468253373333504","subclazzNumber":"32112520197832960"}`（大数字传字符串）；查 hover 历史时加 `recordDt`（毫秒时间戳，直接用趋势图返回的值）。2026-09-29 实测返回 3 个变化点、原因卡 6 条因子，idx=2/5 无 `suggestAction`，符合预期。
4. xjob `RenewalLevelDownNotifyHandler`（test jobId=9711），参数 `20260907`：2026-09-29 实测扫描=1、成功=1（仅 U1，因 U2 已被截止过滤，snapshot 里本来就没有它），override 邮箱实收飞书消息（截图确认）；重复触发验证 Redis 幂等生效（重复跳过=1）。
5. 验证前先确认新 pod 的 eurekaStatus=UP。
6. **按班级回溯补数**（job 漏跑 / 失败时用；2026-10-08 新增）：桥调 `PredictLevelReasonSyncService#backfillByClazz(clazzNumber, scene, dataDt)` —— 按班级把该场景某天的算法明细重跑一遍变化点落库，复用 job 同一套 `processBatch` 逻辑（分组 / 校验 / 截止过滤 / 变化点判定 / 唯一键幂等），可安全重复调用。走 acl 桥 `invoke_service`：
   - `service_method` = `com.gaotu.student.data.domain.predict.PredictLevelReasonSyncService#backfillByClazz`
   - `params` = `[clazzNumber(字符串), scene(1续班/2退费), dataDt("yyyyMMdd")]`，例 `["513468253373333504", 1, "20260922"]`（大数字传字符串）
   - 返回统计串（扫描行数 / 聚合组数 / 落库 / 超期跳过 / 丢弃…）；无该班级明细或参数非法返回 null
   - 依赖索引 `ai_predict_level_reason_detail.idx_clazz_type_dt(clazz_number,type,dt)`（2026-10-08 新增）
   - 例：`invoke_service project=student-data service_method=com.gaotu.student.data.domain.predict.PredictLevelReasonSyncService#backfillByClazz params=["513468253373333504",1,"20260922"] traffic_env=test-eco-2`
   - ⚠️ 补数写的是快照表 `predict_level_reason_snapshot`；若只是要看明细，直接查 `ai_predict_level_reason_detail WHERE clazz_number=...`
7. **批量区间回溯**（算法一次性灌入多天 / 上线初始化用；2026-10-12 补）：用 **job 区间参数**把一段天一次跑完，**不要**用 `backfillByClazz`（那是单班级 × 单场景 × 单天补漏）。
   - 参数 `scene,startDt,endDt`，如 `1,20261001,20261012`（续班 / 退费各触发一次，`2,...`）；逐天**升序**处理，`buildRange` 上限 **400 天**。
   - **整段补、别跳天**：变化点基准是 `getLatestBefore(…record_dt)`，跳天补会让该条被当成首个变化点（`pre_predict_level=null`）、趋势图起点错位。
   - **目标天分区都要就绪**：`existsPartition` 逐天判，缺哪天那天跳过、整个 job 标 FAIL（已就绪的天已落库），补数后重跑即可（唯一键幂等）；不会产生半批数据。
   - 截止过滤按 `record_dt`（非执行日）判，补历史天**不会**被误判超期。
   - 生效判据：查 `ees_data.predict_level_reason_snapshot` 按 `record_dt` 分组计数，确认目标天都有变化点。
   - **2026-10-12 实测**：test 无 student-data xjob 任务、dws pod 直连 acl 桥被登录校验挡（`code 3`），故用 facade 桥逐天调 `PredictLevelReasonSyncService#syncOneDay` 验证多天引擎：`1,20261007/20261010/20261013` → saved 1 / 12 / 3、`failed=0`，逐天独立落库正常（区间循环与它同源）。

## 能验到哪一层

- ✅ 可验：同步聚合、变化点、截止过滤（**真实生效**，见 U2/U3）、查询编排、飞书触达（**飞书消息真实送达**，2026-09-29 已截图确认）
- ❌ 验不了：算法真表的真实分区数据丢弃率——本次仍是 mock 数据，等算法侧真实分区落库后需按真表 dt 重跑一次 `SyncPredictLevelReasonHandler` 核对丢弃率

## 新建的东西

| 类型 | 名称 | 位置 / 值 | 测试 | 线上 |
|---|---|---|---|---|
| 表 | `predict_level_reason_snapshot` | ees_data，DDL 见 `doc/xuban/predict_level_reason.sql` | 已建 | 待工单 |
| 表 | `ai_predict_level_reason_detail` | ees_data，算法真表 1:1 同步（`u_strategy.dwd_user_test_service_renew_lift_reason_df_df`） | 已建（结构已按真表对齐，本次仍是 mock 数据） | 由天工同步任务负责，需确认已建 |
| xjob | `SyncPredictLevelReasonHandler` | student-data-dws，test jobId=9710 | 已建（已停止，未排期） | 待建 |
| xjob | `RenewalLevelDownNotifyHandler` | student-data，每天 12:00，test jobId=9711 | 已建（已停止，未排期） | 待建 |
| Apollo | `predict.level.reason.enable.all` / `.enable.dept` | 联调 true；线上按学部白名单 | **已发布**（TEST/default，2026-09-29） | 待配 |
| Apollo | `predict.level.history.limit` | 10 | **已发布** | 待配 |
| Apollo | `predict.level.reason.deadline.days` | 7 | **已发布** | 待配 |
| Apollo | `predict.level.reason.sync.batch.size` | 1000 | **已发布** | 待配 |
| Apollo | `predict.level.down.notify.enable.all` | 联调 true | **已发布** | 待配 |
| Apollo | `predict.level.down.notify.receiver.override` | **2026-10-10 起 TEST 置空**（不覆盖，发辅导班真实带课老师邮箱）；此前为 `zhangzeling@gaotu.cn` | **已发布（置空）** | 不配 |
| Apollo | `predict.level.down.notify.idempotent.days` | 30 | **已发布** | 待配 |
| Apollo | `predict.level.default.dt.offset.days` | 1（同步/触达共用默认数据日期口径） | **已发布**（TEST，2026-10-12） | **已发布**（PROD，2026-10-12） |
| jar | student-data-api | 0.9.9.24-zzl-RELEASE | 已发 | **已发 RELEASE（2026-10-12 入 Nexus）** |
