---
title: 续班退费分层变化和原因
aliases: [续班&退费的分层变化和原因, 分层变化和原因, predictLevelReason]
status: 联调中
owner: zhangzeling
branches:
  - student-data:feature-predict-level-reason
  - student-center:feature-predict-level-reason
  - aianalysisinformations:feature-refund-reason-20260825
updated: 2026-09-29
tags: [需求]
---

# 续班退费分层变化和原因

> **本目录导航**：[`links.md`](links.md) 链接中心 · [`tasks.md`](tasks.md) 当前任务板 · [`verify.md`](verify.md) 验证手册 · [`changelog.md`](changelog.md) 决策摘要
> 技术方案在飞书（见 links），本地不留副本。续接这个需求：读完本文件即可。

## 一句话

学员详情页展示续班 / 退费的预测分层变化趋势图和原因卡；续班意向下降时，每天 12:00 发飞书通知带班老师。数据来自算法表，由 xjob 同步落库。

## 需求摘要

- **要解决的问题**：老链路下，续班分层从 2026-07-07 起 100% 算不出来，原因文本基本都是兜底文案；退费有 25% 被归为「未知原因」。
- **给谁用**：带班老师（EES 学员详情 - AI 分析 - 续班 / 退费）
- **核心改动**：
  - 算法在 Hive 按天分区的长表里交付分层、因子和成品文案，EES 不再调用任何大模型。
  - xjob `SyncPredictLevelReasonHandler`（dws）按学员 × 辅导班 × 天聚合因子，只把分层有变化的天写入 `ees_data.predict_level_reason_snapshot`。
  - student-center 新增接口 `POST /ai/clazzUser/predictLevelReason`，返回趋势图和原因卡。
  - xjob `RenewalLevelDownNotifyHandler`：每天 12:00 扫当天续班分层下降的记录，发飞书通知。
- **判定做完的标准**：用真实算法数据，经 xjob 同步后能查到正确的变化点和原因卡，意向下降的学员能收到飞书通知。
- **明确不做**：算法模型调优、退费根因分类树改造、花名册新增筛选项。

## 已定共识

- ~~算法表是长表，一行一个因子~~ → **改口径（2026-09-29）**：算法真表 `u_strategy.dwd_user_test_service_renew_lift_reason_df_df`（Hive，分区 `dt`/`type`）经天工同步到 MySQL 后，一行即一个「学员 × 辅导班 × 天」，分层在 `layer`（A/B/C/D），因子明细是 `factors` JSON 数组（元素含 idx/factor/direction/actionable/reason/action/logs，≤6 条）。EES 按 `idx` 升序原样透传，不排序、不裁剪、不去重，这条不变。
- 算法真表不下发预测概率与模型版本，快照表这两列落空（2026-09-29）。
- 快照表只存变化点：和上一条比分层，相同就跳过；唯一键 `(scene,user_id,subclazz_number,record_dt)` 保证幂等（2026-09-04）。
- 截止时间：续班 / 退费 / 结课满 7 天停止更新，按 `record_dt` 判断，不按执行日（2026-09-04）。
- 触达走 EES 自己的飞书应用「ees 助手」，不走消息盒子、企微和通知中心（2026-09-04，PRD 变更）。
- 不可干预的因子不下发建议动作；某条因子 `reason` 为空时整条丢弃（2026-09-04）。
- 只下线续班老链路，新 job 上线当天停掉 3 个续班老 job；退费老链路这期不动（2026-09-04）。

## 现在什么情况

| | |
|---|---|
| 阶段 | 联调完成（同步 job → 快照表 → student-data Feign → student-center → **真实 EES 页面渲染出趋势图和原因卡**，全链路在 test-eco-2 端到端跑通，仅剩上线配置） |
| 进度 | T 4/5 · R 0/0 · C 0/0 |
| 部署泳道 | 2026-09-29 重新发了 test-eco-2（student-data + student-data-dws + student-center），eureka UP |
| 当前卡点 | 无阻塞；剩 T-05 上线配置（需合并发布到 release 池，真实用户默认流量才能看到） |
| 最近更新 | 2026-10-08：快照表字段精简 + 索引 + 按班级回溯方法——删 `predict_score`/`model_version`/`status` 三列与出参 `probabilityDesc`、删「发 MQ 刷 ES」死代码；`ai_predict_level_reason_detail` 加 `idx_clazz_type_dt`、快照表加 `idx_clazz_scene_dt`；新增桥可调 `PredictLevelReasonSyncService#backfillByClazz`（见 [[changelog]]、[[tasks]] T-06）。<br>2026-09-29：算法真表已确认（见上「已定共识」）；`AiPredictLevelReasonDetail`/DDL/同步服务已按新结构改完并合入 release、单测 23 个全过；test-eco-2 全链路验证通过，含真实浏览器页面截图确认（见下「验证结果」）；前端仓库/分支/接口已查明并记入知识库 |

## 验证结果（2026-09-29）

- Apollo 7 个 `predict.level.*` key 已在 TEST/default 发布并读回确认。
- Mock 数据：清空旧的 60 行残缺数据（`layer/factors/type` 全空），按新 schema 重造 10 行，覆盖 verify.md 的 4 组场景。
- `SyncPredictLevelReasonHandler`（scene=1,dt=20260905~07 与 scene=2,dt=20260906~07）触发成功，`handleCode=200`；快照表写入 5 条：
  - U1（6511186386）续班 A→B→C 3 个变化点，退费 中→高 2 个变化点，两个 scene 各自独立快照，**scene 隔离验证通过**。
  - U2（无变化/跨级下降）、U3（分层回升）两个场景**没能验到**：截止时间过滤用的是这两个学员在 ES 花名册里的**真实**续班/结课状态，这两个学员是 2026-09-07 造的旧 fixture，三周后真实状态已经过了 7 天截止线，被 `PredictLevelDeadlineChecker` 正确判定超期跳过（业务逻辑符合预期，不是缺陷）。要验这两个分支需要换成当前仍在读的新学员/辅导班，未来联调可重新挑。
- 查询接口 `/feign/predict/levelReason`（scene=1，U1）返回 3 个变化点、原因卡 6 条因子，idx=2/5（不可干预）正确无 `suggestAction`。
- `RenewalLevelDownNotifyHandler`（dataDt=20260907）：扫描=1、成功=1（U1 的 B→C 下降），飞书发到 `predict.level.down.notify.receiver.override` 配置的 `zhangzeling@gaotu.cn`；**收件人已在「ees助手-test」实收到消息**（"学员newlife学员ID6511186386，续班意向由B下降为C。为避免学员不续班，建议老师尽快与学员沟通，解决学员续班问题。"，截图确认），不止是 handleCode=200；重复触发同一天验证 Redis 幂等键生效（扫描=1、重复跳过=1）。
- **真实前端页面端到端验证通过**（2026-09-29，chrome-devtools 抓真实浏览器网络请求）：真实登录用户（代课李文玉老师，无自定义泳道头）在 EES 页面里点开 AI 分析 tab，前端组件 `IntentPrediction` 发出的请求 `POST /bgwApi/component/student-center/ai/clazzUser/predictLevelReason` 一开始返回 **404**（同页面其它兄弟接口全部 200，只有这条 404）。用 `qingzhou-observe.trace_tree` 查完整调用链证实：网关→teacher-tool 代课鉴权→student-center 每一跳 `trafficMarker` 都是 `"default"`，即请求走的是 release/base 池，没有走到只发了这条分支代码的 test-eco-2 pod。之后用户在真实浏览器请求里显式加上 `traffic-env: test-eco-2` 头重放，**页面正确渲染出趋势图（中→高两个点）和 6 条因子原因卡**，证实前后端链路本身完全没问题，只是真实用户默认流量拿不到这个头、需要等分支合并发布到 release 池。
- **前端代码已经写完并部署到测试环境**（2026-09-29 确认）：组件仓库 `gaotu-fe/gaotu-btech-fe/gaia-widget-submodule/aianalysisinformations`（GAIA 微组件 `AiAnalysisInformations`，即 EES 学员详情页"AI 分析" tab），分支 `feature-refund-reason-20260825`，核心代码在 `src/components/IntentPrediction/`（趋势图 `LevelTrendChart` + 原因卡 `FactorCard`）。该分支 `package.json` 版本 `0.0.54-alpha.1` 与测试环境当前实际加载的组件版本完全一致，说明**前端已经是最新代码，`USE_MOCK` 开关已经关掉在等真实后端**。前后端字段契约核对完全对齐（`factorName`/`featureCode`/`category`/`importance` 是前端故意不用/选填的字段，不是缺失）。**GAIA 前端组件没有泳道概念**（CDN 上只有 `gaia-widget/test/...` 一份共享构建，没有 `test-eco-N` 路径），跟后端按泳道隔离完全是两套机制。
- **mock 因子内容已按日期/场景做区分**（2026-09-29）：最初为了快速验证链路，5 条快照（U1 续班 3 天 + 退费 2 天）用的是同一份因子文案，hover 切换日期时内容完全一样；已重新造数让每天内容不同（如出勤率/作业完成率数值随分层恶化逐日下降），重跑同步 job 刷新快照表后，hover 查询不同 `recordDt` 确认返回不同因子内容。
- 额外补测：scene=2 查询、hover 按 `recordDt` 查历史快照（含内容随日期变化）、无数据学员返回空结构 `{"changeHistoryList":[]}`、同步 job 幂等重跑（不产生重复行）、xjob 参数三种格式（空/单 scene/scene+区间）——全部通过。
- xjob 已在 test 建好两个任务（`SyncPredictLevelReasonHandler` id=9710、`RenewalLevelDownNotifyHandler` id=9711），当前是「已停止」，等提测前再评估要不要常驻启动。
- 页面接口知识库已补全：`知识库/aianalysisinformations/`（`_page.md` 页面级分层逻辑、`renewal.md`/`refund.md` 全量接口清单、`intentPrediction.md` 本次新模块详情），供以后查工单直接用。

## 下一步

1. T-05：线上 DDL 工单（`predict_level_reason_snapshot`）、Apollo PROD 配置、xjob PROD 建任务、代课接口权限登记 31、student-data-api 定版发 RELEASE。
2. 如果还要验 U2/U3 那两个分支（无变化不落库、分层回升不触达），换一批当前仍处于「未续班未结课」状态的学员/辅导班重新造 mock。

## 待确认

- [x] 算法真表表名和字段 —— 已确认：`u_strategy.dwd_user_test_service_renew_lift_reason_df_df`，经天工同步到 MySQL `ees_data.ai_predict_level_reason_detail`（2026-09-29）
- [ ] 分层和概率的真实来源，和因子数据是否同一个 dt —— 等上游算法（算法真表当前不下发概率，快照表 `predict_score`/`model_version` 落空）
- [ ] 算法能否改成增量计算（全量 50 万学员要 2.31 天，T+1 / T+2 都做不到）—— 等产品和算法
- [ ] 退费原因卡本期是否只出趋势图 —— 等产品

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/student-data | feature-predict-level-reason | 同步 job：`student-data-dws/.../dws/job/sync/SyncPredictLevelReasonHandler`；触达 job：`student-data-facade/.../job/predict/RenewalLevelDownNotifyHandler`；领域：`student-data-service/.../domain/predict/`（`PredictLevelReasonSyncService`、`PredictLevelReasonQueryService`、`RenewalLevelDownNotifyService`、`PredictLevelDeadlineChecker`、`PredictLevelReasonGrayService`）；Feign：`PredictLevelReasonController`（`/feign/predict/levelReason`）；建表：`doc/xuban/predict_level_reason.sql` |
| /Users/gaotu/IdeaProjects/JavaProject/student-center | feature-predict-level-reason | `student-center-web/.../ai/RenewalClazzUserController`（`/ai/clazzUser/predictLevelReason`）、`student-center-adapter/.../acl/PredictLevelReasonAclService` |
| `gaotu-fe/gaotu-btech-fe/gaia-widget-submodule/aianalysisinformations`（本机未克隆，走 GitLab API 查） | feature-refund-reason-20260825 | `src/components/IntentPrediction/`（`LevelTrendChart`、`FactorCard`、`service.ts`、`types.ts`）；GAIA 组件名 `AiAnalysisInformations`，projectId 14312；页面接口全量清单见知识库 `aianalysisinformations/` |

## 上线影响面

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 是 | `predict.level.*` 共 7 个 key，见 [`verify.md`](verify.md) |
| ES | 否 | 复用 `ads_large_subclazz_user_index`，不改结构 |
| MySQL DDL | 是 | `ees_data.predict_level_reason_snapshot`，线上走工单；算法表由算法侧建 |
| MQ | 否 | 复用 `renewal_lift_result_topic` |
| 代课接口权限 | 是 | `/ai/clazzUser/predictLevelReason` 是读接口，需要登记 31 |
| xxl-job | 是 | 新建 2 个 job；上线当天停 `SyncRenewalLiftSnapshotHandler` / `SyncRenewalLiftResultHandler` / `SyncRenewalLiftReasonHandler` |

## 必须知道的坑

- student-center 依赖 Nexus 上的 student-data-api jar。改了 api 模块要先 `mvn8 -pl student-data-api -DskipTests clean deploy`，否则 student-center 构建时报 package does not exist。
- 新老 job 共用同一个 topic 刷 ES，同时运行会导致 ES 字段被交替覆盖（老 job 写的是 null），所以上线当天必须停掉老 job。
- 联调前必须配置 `predict.level.down.notify.receiver.override`，否则会真的发给带班老师。
