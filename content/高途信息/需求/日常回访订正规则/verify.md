---
title: 日常回访订正规则（GPS 1v1） · 验证手册
tags: [需求, 验证]
---

# 验证手册

## 环境

- 部署泳道：`test-eco-3`
  - student-data：pod `student-data-7d4566c5cd-gfv9v`（10.218.237.118），commit `b114af4b`
  - fairy：pod `fairy-gaotu100-com-784cbb7fcb-lkmhf`（10.218.236.217），commit `ed05a2df`
- DB：test cluster `gaotu=142`（`first_call_task` / `first_call_task_1v1`）
- ES：`task_platform_main_task`（cluster studentServe / TEST）
- xjob：jobGroup 688；新链路 job `9904`=`DailyVisit1v1ScheduleJob`、老链路 job `9906`=`DailyVisitScheduleJob`；`executor_param`=执行日(1~28)

## Apollo key

| app | key | 默认 | 说明 |
|---|---|---|---|
| student-data | `taskPlatform.dailyVisit1v1.allowedProductTypes` | `[2]` | GPS 仅 1v1(2) 生成 |
| student-data | `taskPlatform.dailyVisit.filterStoppedStudents` | `false` | 老链路停课过滤开关 |
| student-data | `taskPlatform.dailyVisit1v1.create.batch.size` | `100` | 建批大小 |
| student-data | `subclazz.student.event.topic` / `taskPlatform.dailyVisit.subclazzQuit.group` | — | PROD=`gaotu_subclazz_student_event_prod` / `GID_student-data_dailyVisit_subclazzQuit_prod` |
| fairy | `gps.user.container.firstCall.topic` / `...consume.group` | — | PROD=`gaotu_gps_user_container_event_prod` / `GID_gps_user_container_fairy_firstCall_group_prod` |

## MQ 链路（转退班 / 改派）

| 链路 | topic | consumer group | 服务 | tag |
|---|---|---|---|---|
| 老链路转退班 | `gaotu_subclazz_student_event_test`(prod `_prod`) | `GID_student-data_dailyVisit_subclazzQuit_test`(泳道后缀 `_test-eco-3`) | student-data | `TAG_SOLO_Subclazz_Quit` / `TAG_SOLO_Subclazz_Transfer` |
| 新链路改派/退容器 | `gaotu_gps_user_container_event_test`(prod `_prod`) | `GID_gps_user_container_fairy_firstCall_group_test`(泳道后缀 `_test-eco-3`) | fairy | `tag_gps_user_container_enter/quit/edit` |

## 已验证结论（2026-11-02）

- 13/13 规则实现并真实验证（老链路 job9906 回溯出毛萌 15 条；新链路 job9904 config55 出 3 条）。
- **转班/改派不删任务（隔离 E2E）**：用 `ons_consume_verify` 把真实事件只推给我们泳道消费组——
  - 老链路 msgId `0AFFB3E800010FAA3FED085DA68AE93D`（王小品转班）→ CR_SUCCESS，`first_call_task` id 4188157 `isdel` 仍=0；
  - 新链路 msgId `0AFFB3E800010FAA3FED084EE133E707`（7683682631 改派）→ CR_SUCCESS，`first_call_task_1v1` id 1852 `isdel` 仍=0。
- 对照：同一 msgId 被其它泳道旧 pod 消费 → 删任务（故 test 环境会「没了」）。

## 生成口径 / 执行日（3 号验证）

- 生成用**运行时当下**的学员容器 + 剩余课时 + 资格；job 只按 config `taskFrequency` 执行日跑（1~28），`executor_param` 指定“执行日”。
- 线上现执行日=10、25 → 3 号不生成；要 3 号生成需把 3 加进执行日。
- 实测（test，2026-11-02）：config55 临时加 3 → 触发 DailyVisit1v1ScheduleJob(param=3) → 命中执行日 2026-11-03、创建 8 条（批次 202611_2，毛萌 2 条 user 7687538900/7683682630）；exec-log id=136。测试后 config55 还原 [25]。

## 10.25 批次（按执行日=25）

- 批次号 = 年月_执行日在配置执行日列表中的序号；线上 [10,25] → 25 号批次 = `202610_2`（10 号 = 202610_1）。
- 手动触发只传 `25` 走当前月；精确生成 10 月 25 日批次传 `2026-10-25`。
- 实测（test，2026-11-02）：config55（执行日 10、25）触发 `2026-10-25` → 8 条 `execution_seq=202610_2`（id 1891-1898，account 101968×6 + 125756×2）；exec-log id=138。

## 测试遗留 / 已改动的 test 数据

- config55（test）org/role 已按毛萌当前对齐（org `6816343048455168,4959407036876800`、role `4-216`）。
- 毛萌(125756) 新链路 `first_call_task_1v1` r3 3 条（id 1850-1852）；老链路 `first_call_task` r3 15 条（id 4188146-4188160）。
- 为隔离验证，id 4188157 / 1852 的 DB `isdel` 复位为 0、ES `isdel` 同步为 false。
