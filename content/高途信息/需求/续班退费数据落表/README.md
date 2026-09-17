---
title: 续班退费数据落表
aliases: []
status: 需求评审
owner: zhangzeling
branches:
updated: 2026-09-17
tags: [需求]
---

# 续班退费数据落表

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[changelog|📜 决策摘要]]
> 技术方案在飞书反讲文档里（见 [[links]]），本地不留副本。
> 续接这个需求：读完本文件即可。

## 一句话

把续班服务数据（大小班课）和退费管控数据（大班课）落表到大数据，支持业务导数分析。

## 需求摘要

- **要解决的问题**：不同分层学员的续班/退费创新性业务动作不适合系统直接支持，一般由学部运营线下推进，需要运营能实时导数分析续班/退费情况。
- **给谁用**：学部运营（大数据导数分析）。
- **核心改动**：
  1. 续班数据：续班服务全部字段，覆盖大小班课，落表到大数据。
  2. 退费数据：退费管控全部字段，仅大班课，落表到大数据。
- **判定做完的标准**：待反讲后补充。
- **明确不做**：未提及范围外内容，待细评确认。

## 已定共识

- 续班落表覆盖大小班课，退费落表仅大班课（2026-09-05 PRD）。

## 现在什么情况

| | |
|---|---|
| 阶段 | 需求评审 |
| 进度 | T 1/1 · R 0/0 · C 0/0 |
| 部署泳道 | 未部署 |
| 当前卡点 | 无 |
| 最近更新 | 2026-09-17：收到 PRD，代码定位进行中 |

## 下一步

1. **先找数仓侧确认这次是"MQ推送给ETL消费落表"还是"数仓直接开离线binlog/canal权限自己拉"** —— 如果是后者，本仓库可能完全不用改代码，这是决定要不要开发的前提问题，优先级最高。
2. 若确认要走MQ推送，参考 `SyncRenewalLiftResultHandler` 等既有 `job/sync/Sync*Handler.java` 模式新建定时任务。
3. 确认续班服务、退费管控具体要落表的字段清单（"所有字段"需要在细评时定具体口径，且续班花名册字段是GAIA动态字段配置体系，不是编译期固定字段，落表方案要考虑这点）。
4. 参与初评。

## 待确认

- [ ] **最优先**：落表方式，MQ推送 or 数仓侧binlog直接拉取 —— 需数仓侧确认
- [ ] "续班服务所有字段"、"退费管控所有字段"的具体清单，考虑GAIA动态字段如何落表 —— 等细评

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| student-data | 待定 | 现有落表/推数仓模式均为**MQ推送**，无本仓库直连数仓写Hive/ODPS表的先例；可参考 `student-data-dws` 模块 `job/sync/Sync*Handler.java` 系列（如 `SyncRenewalLiftResultHandler.java`、`SyncRefundResultHandler.java`）：定时扫MySQL(按update_time)→加工→发MQ，下游数仓订阅落ODS/DWS表 |
| student-center | 待定 | 未发现直连数仓写表代码；唯一相关历史 commit `b84a09cbf feat: 落表`（`StudentLearnRecordServiceImpl`）也是落自己MySQL表+发Kafka模式 |

## 设计草案

- 续班数据模型：ES索引 `ads_large_subclazz_user_index`（大班）+ `ads_small_clazz_user`（小班），字段分散在多个 `*QueryServiceV2` 里，是宽表+GAIA动态字段体系，字段量级几十到上百，无法用单个Java类衡量。
- 退费数据模型：`student-center` 的多个 `Refund*VO`（`RefundAnalysisVO`/`RefundReasonVO`/`RefundStatistic`/`RefundEvaluateVO`/`RefundStageVO`等）拼成完整画像；`student-data` 侧 `AiRefund*` MySQL表（10-20字段级别）。
- 建议方案：新增一个类似 `SyncRenewalLiftResultHandler` 的定时任务，把ES花名册全字段（续班）和拼装后的Refund*VO全字段（退费）序列化发一条MQ消息，由数仓侧订阅落ODS表；不新建数仓Hive/ODPS表结构（本仓库不管）。**但这个方案要先经数仓侧确认协议（topic/schema）**。

## 上线影响面

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 待定 | |
| ES | 待定 | |
| MySQL DDL | 待定 | |
| MQ | 待定 | 若走binlog同步可能不涉及；若主动推送可能新增MQ |
| 代课接口权限 | 否 | |

## 必须知道的坑

- 
