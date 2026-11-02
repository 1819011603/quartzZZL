---
title: 日常回访订正规则（GPS 1v1）
aliases: [1v1日常回访, GPS日常回访, DailyVisit1v1, 日常回访]
status: 上线准备
owner: zhangzeling
branches:
  - student-data:feature-1v1-daily-visit-job
  - fairy:feature-1v1-daily-visit-task
updated: 2026-11-02
tags: [需求]
---

# 日常回访订正规则（GPS 1v1）

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[changelog|📜 决策摘要]] · [[verify|🧪 验证手册]]
> 技术方案/PRD 在飞书（见 [[links]]），本地不留副本。
> 续接这个需求：读完本文件即可。

## 一句话

按飞书 wiki（rev876「四、订正后的规则」）实现 GPS 1v1 日常回访任务生成（新链路走容器），并让**转班/改派/退费不删除**已生成的日常回访任务。

## 需求摘要

- **要解决的问题**：新 1v1 无辅导班、只有学员容器，老 job 按辅导班圈不到人；转退班 MQ 会删未完成回访任务；跨/同班主任多子产品选错子产品。
- **给谁用**：GPS 1v1 班主任（日常回访任务中心）。
- **核心改动**：
  - student-data 新增 `DailyVisit1v1ScheduleJob`（按老师起效容器圈人 → 调 fairy 落 `first_call_task_1v1`，ruleType=3）；
  - 新增 `DailyVisitEligibilityService`：走 service-dock `validateDailyVisit` 资格；GPS 仅 `productType=2`(1v1)；同/跨班主任均取**下单最近**子产品（课时包 createTime 最大，缺失降级容器 assignTime）；
  - R2/R3：`DailyVisitSubclazzQuitConsumer`、`DailyVisitTaskDeleteService` 改 no-op（老链路）；
  - fairy `FirstCall1v1SaveService` 移除改派/失效的日常回访删除。
- **判定做完的标准**：13 条规则实现 + 真实验证；转班/改派/退费**不删**任务（已隔离 E2E 验证）。
- **明确不做**：不改老链路的**生成**逻辑（仅切 Apollo 停课过滤开关）；不动 service-dock；本需求**未合并 release、未上生产**（等授权）。

## 已定共识

- GPS 规则落 student-data；R5b：GPS 仅 `productType=2`(1v1) 生成，Apollo `taskPlatform.dailyVisit1v1.allowedProductTypes` 默认 `[2]`（2026-10-28）
- **转班/改派不删除日常回访任务（R2/R3）**（2026-10-29）
- 老链路代码不动（仅 `taskPlatform.dailyVisit.filterStoppedStudents` 开关，默认 false）（2026-10-28）
- config55（test）改为对齐毛萌当前 org/role（2026-11-02）；这是 test 数据对齐，非代码改动
- 部署泳道统一 test-eco-3；service-dock 只读（不 push/不部署）

## 现在什么情况

| | |
|---|---|
| 阶段 | 上线准备 |
| 进度 | T 4/5 · R 1/2 · C 1/1（13/13 规则实现+验证 · 隔离 E2E 通过 · 待授权合并上线） |
| 部署泳道 | `student-data=test-eco-3`（pod `student-data-7d4566c5cd-gfv9v`, commit `b114af4b`）· `fairy=test-eco-3`（pod `fairy-gaotu100-com-784cbb7fcb-lkmhf`, `ed05a2df`）|
| 当前卡点 | 未授权合并 release / 未授权发布生产 |
| 最近更新 | 2026-11-02：建免测需求 TAPD story `1122531521001397150`；建发布编排 `24158`（免测，fairy→student-data）|

## 下一步

1. owner 确认上线时间后，按发布编排 `24158`（DDL→fairy→student-data）执行上线。
2. 上线时切 xjob：**停** `DailyVisitScheduleJob`（老），**启** `DailyVisit1v1ScheduleJob`（新），二者不同时调度。
3. 上线前逐项确认 [[verify]] 与上线 checklist 的配置（Apollo / DDL / MQ）。

## 怎么验 / 新建的东西

> 环境、测试数据、Apollo key、验证结论 → 见 [[verify|🧪 验证手册]]。

## 待确认

- [ ] 是否合并 release 并在生产启新 job（等 owner 授权）—— 等 owner
- [ ] 首call(ruleType=1)/ruleType=0 的 maomeng 测试数据是否清理 —— 等 owner
- [ ] AICR medium/low 是否处理 —— 等 owner

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/student-data | feature-1v1-daily-visit-job | `com.gaotu.student.data.domain.taskplatform.domain.service.DailyVisitEligibilityService`、`facade.job.taskplatform.DailyVisit1v1ScheduleJob`、`facade.mq.taskplatform.DailyVisitSubclazzQuitConsumer`、`domain.taskplatform.application.service.dailyvisit.DailyVisitTaskDeleteService` |
| /Users/gaotu/IdeaProjects/JavaProject/fairy | feature-1v1-daily-visit-task | `com.gaotu.task.service.FirstCall1v1SaveService`、`DailyVisit1v1TaskSaveService`、`database/20261023_1v1_daily_visit_task.sql`、`database/20261028_daily_visit_teacher_user_unique.sql` |

## 上线影响面

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 是 | student-data 新增 `taskPlatform.dailyVisit1v1.allowedProductTypes`(默认[2])、`taskPlatform.dailyVisit.filterStoppedStudents`(默认false)、`taskPlatform.dailyVisit1v1.create.batch.size`(默认100)；均为有默认值可选项，建议显式配置 |
| ES | 否 | 复用 `task_platform_main_task`，无新增索引/mapping |
| MySQL DDL | 是 | fairy `database/20261023_1v1_daily_visit_task.sql`、`20261028_daily_visit_teacher_user_unique.sql`（加 execution_seq / task_dedup_owner 生成列 + 唯一键），**必须先于 fairy 发布** |
| MQ | 是 | 新消费者组 `GID_student-data_dailyVisit_subclazzQuit_prod`（topic `gaotu_subclazz_student_event_prod`）、fairy `GID_gps_user_container_fairy_firstCall_group_prod` |
| 代课接口权限 | 否 | 无新增代课接口 |

## 必须知道的坑

- **test 环境多分支共享消费组**：开了「所有环境创建所有group」后各泳道是**独立消费组、各收一份**消息；旧分支 pod 也会消费同一事件并改**共享 DB** → 会误删任务。**线上单版本无此问题**；验证/上线后旧版本不再删。
- **老链路 vs 新链路**：老链路按辅导班圈人（`DailyVisitScheduleJob`），新链路按容器圈人（`DailyVisit1v1ScheduleJob`）；上线时二者不要同时调度。
- **fairy DDL 不回滚**：回滚应用代码可保留新唯一键/生成列；恢复旧索引前须重新检查子产品维度重复。
- **完成条件**：取 config `task_finish_condition`（新老一致）；config 为空则页面条件为空。
