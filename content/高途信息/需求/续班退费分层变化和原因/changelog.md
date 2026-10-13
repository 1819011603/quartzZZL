---
title: 续班退费分层变化和原因 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

---

## 2026-10-13 · 触达与「续班AI（分层）学部白名单」拉齐（待办）

### 🤖 Claude
- **背景**：王永诗反馈——提醒（触达）本应与分层原因配套，分层在续班AI里、只给精品班等几个学部放开；EM 二讲来问，但没开通续班AI。问「有没有加限制」。
- **现状**：**没加限制**。PROD 展示 `predict.level.reason.enable.all=true` + 触达 `predict.level.down.notify.enable.all=true` 都是全量 → 触达发给所有带课老师。
- **机制**：`RenewalLevelDownNotifyService.isNotifyEnabled` 在**触达非全量 + dept 非空**时会 `return predictLevelReasonGrayService.isEnabled(clazz)` —— 即复用「展示（续班AI）」白名单。所以「只给开通续班AI的学部触达」**机制上已支持**，只要触达别设全量、且展示用学部白名单。
- **候选学部来源 key**（代码里找）：**`renewal.intention.predict.mapping.info`**（`RenewalComponent` `@ApolloJsonValue`；元素 `levelCode`=学部名_学期 或 部门id路径 → 分层阈值 stage/intentInfo）。PROD 里配了分层的学部：`H业务线_精品班学部`、`EM业务线_素养初中学部`、`EM业务线_综合素养学部`（+ 部门路径 `10000683/10013429_Q`、`10019197/10012667_Q`、`defaultLevel`）。同类 key：`renewal.intention.config.mapping.info`（学部→code）、`refund.intention.predict.mapping.info`（退费）。
- **口径不一致**：该配置的 levelCode 是**学部名**，而展示/触达 gray（`predict.level.reason.enable.dept`）判的是**部门 id 路径** → 拉齐需 ① 配上学部对应部门 id，或 ② 改 gray 读同一份学部配置。
- **待办**：见 T-11（需 PM 确认学部口径 + 选 ①/②）。**待确认**：王永诗说的「续班AI 学部」是否 = `renewal.intention.predict.mapping.info` 的 levelCode 清单。

---

## 2026-10-13 · 续班下降触达按场景配飞书机器人（【续班助手】）

### 🤖 Claude
- **需求**：马胜反馈【ees助手】是内部用的，对外触达要独立机器人；且以后**新增场景要能各自配机器人**（Apollo 配，不改代码）。
- **实现（分支 `feature-renewal-reason-editable`）**：新增通用**飞书机器人注册表** `LarkRobotClientRegistry`（`student-data-service/notice/config`）——按场景取机器人：
  - Apollo `lark.notice.robot.config`（JSON map）：`{"场景key":{"appId":"","appSecret":""}}`；
  - Apollo `lark.notice.robot.default.appId/appSecret`：默认机器人（未配场景用它）；
  - 都取不到 → 回退 `mqNoticeLarkClient`（内部【ees助手】）。
  - **Apollo 变更热生效**（`@ApolloJsonValue`/`@Value` 自动刷新，appId/secret 变了下次取用时重建 client），不用改代码、不用重启。
  - `RenewalLevelDownNotifyService` 改用 `getClient(SCENE_RENEWAL_DOWN)`。**只动这个触达**，`mqNoticeLarkClient`（BCP 等）未动、未配场景行为不变。
- **配置**：新机器人【续班助手】appId `cli_aa4755e8e9b8dcce` 已写入 Apollo `lark.notice.robot.config` 的 `renewalDown` 场景（**TEST + PROD 均已发布**）。
- **部署**：test-gtbg-dev-3（commit `da28ac03`，eureka UP）。⚠️ PROD 生效需先合 release + 发版。
- ⚠️ 待办：新机器人要像【ees助手】一样配 **`im:message` 权限 + 可用范围「全员可用」**，否则发不出。

---

## 2026-10-13 · 原因卡「不可干预」也下发建议动作

### 🤖 Claude
- **口径变更 + 做成 Apollo 开关**：产品要求**所有因子都下发建议动作**。`PredictLevelReasonQueryService` 原来 `setSuggestAction(interveneable ? factor.getAction() : null)`（不可干预→null），改为由**开关 `predict.level.reason.suggest.action.all.enable`**（默认 `false`）控制——`true` 时所有因子都透传原文案。**TEST/PROD Apollo 均已发布 `=true`**。单测覆盖开/关两种（`should_controlSuggestActionOfNotInterveneable_bySwitch`），5 个全过。
- 分支 `feature-predict-action-all`（基于 release）→ student-data **MR !1750**；已发 test-eco-2（commit `3a8859d7`，pod eureka UP）。接口验证：不可干预因子现在返回 `suggestAction`（mock 里为空串——mock 的不可干预因子本就无 action；PROD 都嘉怡那条有文案，会正常显示）。⚠️ 若算法某些不可干预因子确实没产出 action，仍会为空——需算法侧都给出文案。

---

## 2026-10-12 · 上线前准备（进行中）

### 🤖 Claude
- **上线切换（2026-10-12）**：student-data/dws 全量发布后——停老 job **10413** `SyncRenewalLiftSnapshotHandler` + **10073** `refundPredictionCheckHandler`（断源）、启新 job **12753**（同步 15:00）+ **12754**（触达 16:00）。**两个老 switch 没关**：读代码确认 `renewal.lift.result.consumer.open.switch` / `dws.refund.intent.switch` gate 的是**新旧共用**的 `RenewalLiftResultConsumer`（`levelOnly`）/ `DwsRefundIntentConsumer`（`aiRefundIntentScoreResult`）——置 false 会**断掉新链路的 ES 写回**，**更正了上线方案原「置 false」**。回溯用 job 12753：`1,20261007,20261011` + `2,20261003,20261009`。
- **明细表保留/清理（2026-10-12）**：明细 `ai_predict_level_reason_detail` 只增不减（实测 ~90MB/天 → 一个月几 GB），新增 **GLUE 清理 job**：`CleanPredictLevelReasonDetailJobHandler`（xjob **12793**，group 530，GLUE(Groovy)，每天 **03:00**，分批 `DELETE ... WHERE dt < 今天-30 LIMIT 2000`，**只清明细、快照表 `predict_level_reason_snapshot` 不动**），已启动、实测 handleCode=200。建前按 xjob-admin「先查重」确认无同类任务。**清理会影响回溯**：删了老天的明细，补那几天需先重跑天工任务（从 Hive 拉回）再跑 EES。**test 验证（2026-10-12）**：在 test 建测试 job 用 `execute_address=<test-eco-2 dws pod>:9999` 真跑，`handleCode=200`、`deleted=12`（`dt<20260912`），test 库对应行已清空——GLUE 编译/连接/删除全通。（踩坑：GLUE_GROOVY 界面标 "GLUE(Java)" 实为 Groovy 编译，Java 代码**续行以 `+` 开头**会报 `String.positive()`；改单行拼接后正常。）**另**：天工目标表有唯一键 `uk_dt_user_clazz_sub_type(dt,user_number,clazz_number,subclazz_number,type)`，`saveMode=upsert` 幂等 → 天工任务可重复执行（实测多次跑行数不翻倍），分区就绪与否可多跑几次补。
- **PROD 实测复核（与 10-10 一致）**：`ees_data` 两表都不存在；Apollo `predict.level.*` 10 个 key 全未配、老链路 3 switch 未配(默认 `true`)；xjob 12753/12754 已建已停止、10413/10073 运行中（**用户明确：老 job 明天上线当天再停，现在别动**）。
- **快照表 DDL 工单已提**：`ees_data.predict_level_reason_snapshot` PROD 建表 → 工单 **146755**（cluster 336 / `gaotu-student-dynamic-prod`），Inception warning（`id`/`create_time`/`update_time` 无注释，可继续），**待 SRE 审批发布**。明细表 `ai_predict_level_reason_detail` 及索引/唯一键由用户（天工侧）负责；**T-07 已定：按 upsert 口径带上 `uk_user_subclazz_type_dt`**。
- **Apollo PROD 已发布**（2026-10-12，releaseKey `20261012114830-188a560667e3eebb`）：8 个 key 落实——**全量放量** `predict.level.reason.enable.all=true`、`predict.level.down.notify.enable.all=true`；参数 `history.limit=10`、`reason.deadline.days=7`、`reason.sync.batch.size=1000`、`reason.roster.index=ads_large_subclazz_user_index`、`down.notify.idempotent.days=30`、`reason.es.write.enable=true`（后 6 个＝代码默认值，落地行为不变）。`predict.level.down.notify.receiver.override` 不配（发真实带课老师）；两个 `enable.dept` 不配（`enable.all=true` 已覆盖白名单）。读回确认 8 命中、override/dept 未命中。
- **代课权限已登记**：`student-center` `31:/ai/clazzUser/predictLevelReason`（读接口）2026-10-12。
- **api 定版已发（解决版本冲突）**：`0.9.9.24-RELEASE` 已被 Nexus 占用（09-07 发的旧内容）→ 定版发 **`student-data-api 0.9.9.24-zzl-RELEASE`**（2026-10-12 `mvn8 deploy` BUILD SUCCESS，GAV 已入 Nexus）。student-data 5 个 pom（api 自身 + service/facade/dws/gps 依赖）+ student-center-infrastructure 1 个 pom 依赖版本同步改为 `0.9.9.24-zzl-RELEASE`，已 push feature 分支。
- **合 release + 建 MR**：① 先把 `origin/release` 合入 `feature-predict-level-reason` 消冲突（student-data `fc2c27fba`、student-center `9fb66e2a4`，均无冲突）；② 再建 MR → `release`：**student-data [!1742](https://git.baijia.com/gaotu/yunying_workbench/student-data/-/merge_requests/1742)**、**student-center [!1468](https://git.baijia.com/gaotu/yunying_workbench/student-center/-/merge_requests/1468)**（均 open，2026-10-12）。⚠️ 注意：首次合并命令因分支被 worktree 占用、`&&` 误判，曾误合到 `feature-xuban-match-opt`，已 `git reset --hard ORIG_HEAD` 回退；正确的需求分支在 `.claude/worktrees/predict`。
- **xjob 调度调整（PROD）**：为**错开天工任务 14:00**，同步 12753 `0 0 13 * * ?` → **`0 0 15 * * ?`**；触达 12754 `0 0 12 * * ?` → **`0 0 16 * * ?`**（排在同步之后）。链条：天工 14:00 → EES 同步 15:00 → 触达 16:00。
- **线上天工同步任务已建（2026-10-12）**：区分测试 vs 线上——原 taskId **47772** 是**测试**任务（源 `dwd_user_test_service_renew_lift_reason_df_df` → datasource **1480** `ees_data_test`）。在**同目录 103709** 新建**线上**任务 taskId **47936 / 节点 104349**：源改为正式表 **`u_strategy.dwd_user_service_renew_refund_reason_df`** → datasource **1479**（`ees_data_prod`）库表 `ees_data.ai_predict_level_reason_detail`；其余照搬测试任务。读回一致。两张源表 DDL 完全一致（分区 dt+type），只改表名+目标库。**已发布并配调度**：nezhaId **67730**；`schedule-get` 读回 `scheduleType=1`(定点)、`timeUnit=2`(天)/`runInterval=1`、`firstRunTime=2026-10-13 14:00`、`nextRunTime=2026-10-13 00:00`（每天 14:00）。**实测（手动执行后查 PROD `ees_data.ai_predict_level_reason_detail`）**：renew + refund **都进了**（refund 20261003~09、renew 20261007~11），确认 `partitionField=dt=dt1` 即覆盖全部 `type` 子分区、无需为 type 另配。
- **默认数据日期口径改造（代码）**：原**同步默认「昨天」、触达默认「当天」**（日期错位，触达排在同步后也扫 0 条）。抽出共享 Apollo key **`predict.level.default.dt.offset.days`（默认 1=昨天）** 供两个 job 共用；新增 `PredictDefaultDtProvider`（`student-data-service/domain/predict`），`SyncPredictLevelReasonHandler` / `RenewalLevelDownNotifyHandler` 均引用。单测 3 个通过（`mvn8 -pl student-data-service -am test`）；student-data `cab3413fd` 已 push（MR !1742 更新）。TEST/PROD Apollo 均已发布该 key=1。**已发 test-eco-2**（student-data + dws，commit `cab3413f`，均 eureka UP）；自验：桥调 `PredictDefaultDtProvider#defaultDataDt` 返回 `20261011`（昨天）✅。

---

## 2026-10-10 · 造数正确姿势 + ES「续班意向预测」无值排查

### 🤖 Claude
- **现象**：学员 7489644701 原因卡接口有值，但学情表「续班意向预测」（ES `renewalIntentionPredictLevelResult`）为空。排查：明细表 `ai_predict_level_reason_detail` 该学员 **0 行**、快照表 **4+4 行** → 快照不是同步 job 从明细产出的，`sendRosterSyncMessage` 没触发 → ES 无值。（对照 mock 学员 7478102067 走了 job，ES=3。）
- **处置**：按快照把明细补回 `ai_predict_level_reason_detail`（8 行），桥调 `backfillByClazz(574882679202260992,1,"20261013")` / `(...,2,"20261013")`，各「落库=1、超期跳过=0」→ ES `renewalIntentionPredictLevelResult=4`、`aiRefundIntentScoreResult=4`，恢复。
- **口径**：**造数只造明细表 `ai_predict_level_reason_detail`；快照 `predict_level_reason_snapshot` 和 ES 都交给同步 job 派生。直接写快照会导致「接口有值、ES 没值」。** 落点：[[case-record]] 第 7 节 + 飞书 P0 文档《测试操作手册》第 7 节；README「必须知道的坑」加一条。

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
