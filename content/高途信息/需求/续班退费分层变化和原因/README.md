---
title: 续班退费分层变化和原因
aliases: [续班&退费的分层变化和原因, 分层变化和原因, predictLevelReason]
status: 联调中
owner: zhangzeling
branches:
  - student-data:feature-predict-level-reason
  - student-center:feature-predict-level-reason
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
| 阶段 | 联调中（代码已写完，用 mock 数据联调，没跑通） |
| 进度 | T 1/5 · R 0/0 · C 0/0 |
| 部署泳道 | 2026-09-07 发过 test-eco-2，之后没再部署；pod 现在是什么状态未确认 |
| 当前卡点 | 用户说算法真表已 ready，但表名 / 库未知：测试库 ees_data 没有新表，飞书需求节点下 4 篇文档里也没写（T-03） |
| 最近更新 | 2026-09-28：两仓库已合入最新 origin/release 并 push（无冲突，编译通过，23 个单测通过）；测试库快照表为空 |

## 下一步

1. 拿到算法真表的表名和库，对比字段后改 `AiPredictLevelReasonDetail`。
2. 部署到 test-eco-2，预置 Apollo（见 [`verify.md`](verify.md)），xjob 手动触发 `SyncPredictLevelReasonHandler`，参数 `1,20260905,20260907`，核对快照表写入 7 条。

## 待确认

- [ ] 算法真表表名和字段 —— 等梓淳 / yuyong
- [ ] 分层和概率的真实来源，和因子数据是否同一个 dt —— 等上游算法
- [ ] 算法能否改成增量计算（全量 50 万学员要 2.31 天，T+1 / T+2 都做不到）—— 等产品和算法
- [ ] 退费原因卡本期是否只出趋势图 —— 等产品

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/student-data | feature-predict-level-reason | 同步 job：`student-data-dws/.../dws/job/sync/SyncPredictLevelReasonHandler`；触达 job：`student-data-facade/.../job/predict/RenewalLevelDownNotifyHandler`；领域：`student-data-service/.../domain/predict/`（`PredictLevelReasonSyncService`、`PredictLevelReasonQueryService`、`RenewalLevelDownNotifyService`、`PredictLevelDeadlineChecker`、`PredictLevelReasonGrayService`）；Feign：`PredictLevelReasonController`（`/feign/predict/levelReason`）；建表：`doc/xuban/predict_level_reason.sql` |
| /Users/gaotu/IdeaProjects/JavaProject/student-center | feature-predict-level-reason | `student-center-web/.../ai/RenewalClazzUserController`（`/ai/clazzUser/predictLevelReason`）、`student-center-adapter/.../acl/PredictLevelReasonAclService` |

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
