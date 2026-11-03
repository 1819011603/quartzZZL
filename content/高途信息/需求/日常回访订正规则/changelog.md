---
title: 日常回访订正规则（GPS 1v1） · 决策摘要
tags: [需求, 决策]
---

# 决策摘要

> 只记会影响后续设计判断的理由，不记流水账。**日期倒序（最新在前）。**

## 2026-11-03｜AICR 两条 high 修复 + 上线项落定（DDL/Apollo/xjob/表对齐）
- **AICR #779 两条 high（`ClazzTypeFeignServiceImpl#getTeachProductTypeMap` L604-607 / L632-635）**：owner 判定**真 bug、改**。修复口径：下游**业务失败（`isSuccess=false`/null）→ 抛 `BusinessException` 交调度重试**（对齐 `getCreateTimeOrThrow` L182-185 及 #18001 严格口径）；**成功但空数据 → 跳过**。补 4 个单测（失败/null 抛异常、空数据跳过），9/9 通过、BUILD SUCCESS；push 远端 HEAD `07da7ae45`。**注意：release 已含旧（含 bug）代码，需经 MR !1805(release) 再合入该修复。**
- **DDL 工单 147777（prod）已 EXECUTED**：`gaotu.first_call_task_1v1` 加 `execution_seq`/`task_dedup_owner` 生成列 + 唯一键 `uq_owner_user_rule_execution`，drop `uq_number`（cluster 211 gaotu-crm-prod）。回读 prod 唯一键 = PRIMARY + uq_owner_user_rule_execution。
- **Apollo PROD** 新增 3 key 已发布（releaseKey `20261103101642-188a560667e40670`）：`taskPlatform.dailyVisit1v1.allowedProductTypes=[2]`、`taskPlatform.dailyVisit1v1.create.batch.size=100`、`taskPlatform.dailyVisit.filterStoppedStudents=false`。
- **prod xjob**：新建 `DailyVisit1v1ScheduleJob` jobId **13157**（group 314，cron `0 0 * * * ?`，**默认已停止**）；上线时启本 job、停老 `DailyVisitScheduleJob`(10680)，二者不同时调度。
- **test 表结构对齐 prod**：删除 test 多余的 `uq_task_code`（`ALTER TABLE ... DROP INDEX uq_task_code`，已执行回读）；test 唯一键现与 prod 一致。（test 另有 6 个普通索引 idx_* prod 无，未在本次授权范围，待确认。）
- **MQ**：本需求**未新增**任何 topic/group；`GID_student-data_dailyVisit_subclazzQuit_prod`、`GID_gps_user_container_fairy_firstCall_group_prod` 生产均已存在且在线 → **无需申请**。
- **旧 MR** !1788(student-data)/!1101(fairy)：web/接口关闭被 CSRF 422（试 3 次），改由 owner 页面手动关。

## 2026-11-03｜filterLegacyUsers 属本需求、保留；MR 指向正式分支
- owner 明确：老链路 `DailyVisitScheduleJob.filterTaskUsers → DailyVisitEligibilityService.filterLegacyUsers`（生成前调 `validateDailyVisit` 资格）**属本需求范围，保留**；旧「老链路生成逻辑不动」口径以本条为准。
- owner 明确：本特性唯一新增 SNAPSHOT 依赖 `service-dock-api` 改 `1.0.11-RELEASE`（已编译 BUILD SUCCESS、push `2852ce84a`）。
- 分支规范：正式交付分支 = `feature-1v1-daily-visit-{job,task}`；`feat/1v1-daily-visit-{job,task}` 为旧分支（被正式分支完全包含、0 独有提交）。因 GitLab 不能就地改 MR 源分支，**关旧开新**：
  - student-data 新 MR **!1805**（`feature-1v1-daily-visit-job → release`）；旧 **!1788**（`feat/... → release`）待关。
  - fairy 新 MR **!1103**（`feature-1v1-daily-visit-task → release`）；旧 **!1101**（`feat/... → release`）待关。

## 2026-11-02｜统计沟通不需要回访任务（GLUE 补任务=错方向）
- 「统计 10.25–11.2 的沟通」直接查通话表 `first_call_user_call_record`（account_id/user_id/call_time/call_duration）按 `call_time` 过滤即可，**与回访任务无关**。
- 写 Java GLUE 直接往 `first_call_task(_1v1)` 伪造覆盖 10.25–11.2 的任务：窗覆盖后通话判定会通过（`DailyVisitCallRecordFilter`/`isWithinTaskPeriod`），但需再触发计数、绕过校验、维护唯一键/防重/子任务/ES/MQ，风险高、真实性差 → 不推荐。

## 2026-11-02｜生成基于跑时状态；任务有效期从生成时刻起算（不能统计 10.25–11.2）
- 生成基于**跑 job 那一刻**的容器/剩余课时/资格（代码：`DailyVisit1v1ScheduleJob.processAccount` 的 `queryContainerByAccountId`/`queryAvailableLessonCount` + `DailyVisitEligibilityService`；老链路 `AbstractScheduledTaskJob.processAccount` 同）。**不是 10.25 当天快照**；批号只是标签。
- 任务有效期 = 生成时刻 + `taskExpireHour`（config55=11h；实测 id1891-1898 start=2026-11-02 16:34:52、expired=2026-11-03 03:34:52）。通话只在 [start, expired] 内算有效（`DailyVisitCallRecordFilter.isCallInTaskPeriod`；fairy `TaskBizService.isWithinTaskPeriod`）→ **不能统计 10.25–11.2 的沟通**。
- 无「回填过去周期」口径。结论：要「10.25 批次号」可（传 `2026-10-25`）；要「按 10.25 当天状态 + 统计 10.25–11.2 沟通」不行。

## 2026-11-02｜批次号=年月_执行日序号；10.25 批次=202610_2（已实测）
- 执行日=25 生成 25 号批次；批次号 `execution_seq=年月_该执行日在配置执行日列表中的序号`。线上执行日 [10,25] → 10 号=…_1、**25 号=…_2 → 10.25 批次=202610_2**。
- 手动触发参数：只传 `25` 按**当前月**（11 月→202611_1）；要精确 10 月 25 日批次传完整日期 `2026-10-25`。
- 实测（test）：config55（执行日 10、25）触发参数 `2026-10-25` → 生成 **8 条**（execution_seq `202610_2`、execute_date 2026-10-25）；exec-log id=138。

## 2026-11-02｜生成口径 = 运行时当下；job 只按配置执行日跑（3 号实测）
- 日常回访任务生成依赖**跑的那一刻**的学员容器 + 剩余课时 + 资格（`AbstractScheduledTaskJob.processAccount`、`DailyVisit1v1ScheduleJob.processAccount/filterCandidates`、`DailyVisitEligibilityService`），**不是历史批次快照**。
- job 只在 config `taskFrequency`（执行日，1~28）命中时才跑；`executor_param` 只是把某天当执行日评估，**不能创造出配置里没有的执行日**。
- 线上执行日=10/25（无 3）→ 3 号跑=0 条。实测：test config55 执行日加 3 → 触发 → 命中执行日 2026-11-03、创建 8 条（毛萌 2 条），证明按当天状态生成。测试后 config55 已还原为 [25]。
- 注意：`execution_seq=yyyyMM_执行日在列表中的序号`；加更早的执行日会改序号排序，可能撞已跑批次被跳过。

## 2026-11-02｜上线准备
- 建 TAPD 免测需求 story `1122531521001397150`；建青舟免测发布编排 `24158`（fairy rank1 → student-data rank2；含 -dws/-gps 整仓）。

## 2026-11-02｜「转班/改派任务没了」根因 = 泳道未隔离（非代码 bug）
- 两例（老链路 王小品 7147120734、新链路 12509090003/7683682631）任务 `isdel=1` 系被**其它泳道跑旧代码的 pod** 消费同一 MQ 事件后删除（test 各泳道独立组各收一份、共享 DB）。
- 隔离 E2E（`ons_consume_verify` 只推给我们泳道组）证明：我们修复版消费转班/改派事件后任务 `isdel` 仍=0。

## 2026-10-30｜同老师多子产品也取下单最近
- 原实现只在「≥2 个不同班主任」时选举，同老师多子产品回退按 subProductId 最小 → 选错。放宽为「≥2 个可回访 1v1 子产品」均取下单最近（`b114af4b`）。

## 2026-10-29｜R2/R3：转退班不删任务
- owner 明确「转班不删除任务」。老链路消费者 `DailyVisitSubclazzQuitConsumer.consume()` 与 `DailyVisitTaskDeleteService.processQuitEvent()` 改 no-op；fairy 移除 `deleteDailyVisitTasks`。

## 2026-10-28｜GPS 规则落 student-data、老链路仅切开关
- 老链路 `DailyVisitScheduleJob` 按辅导班圈人，容器场景圈不到；新链路需按容器圈人，故新增 `DailyVisit1v1ScheduleJob` 落 student-data。
- 老链路代码不动：停课过滤仅由 Apollo `taskPlatform.dailyVisit.filterStoppedStudents`（默认 false）控制。
