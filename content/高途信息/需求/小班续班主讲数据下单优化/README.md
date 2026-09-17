---
title: 小班续班主讲数据+下单优化
aliases: []
status: 需求评审
owner: zhangzeling
branches:
updated: 2026-09-17
tags: [需求]
---

# 小班续班主讲数据+下单优化

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[changelog|📜 决策摘要]]
> 技术方案在飞书反讲文档里（见 [[links]]），本地不留副本。
> 续接这个需求：读完本文件即可。

## 一句话

小班课续班服务按登录人角色（主讲/班主任）展示对应维度的数据和统计指标，另有B端购物车/下单相关优化（细节待补充）。

## 需求摘要

- **要解决的问题**：小班课续班服务目前只按班主任视角展示数据，主讲老师看不到自己维度的续班数据；另外主讲端预报名/购物车下单体验有待优化（原文列了多项调研问题，本次PRD只展开了角色适配部分，购物车/下单部分描述不全）。
- **给谁用**：小班课主讲老师、班主任。
- **核心改动**：
  1. 续班服务按登录人在班级上的角色区分展示：主讲展示主讲数据，班主任展示班主任数据，同时具备两个角色展示主讲数据。
  2. 新增主讲角色统计指标（6-9行，具体清单见「小班课字段+指标」文档）。
  3. B端购物车/创建订单相关优化 —— PRD 只给了截图无文字说明，细节待补充。
- **判定做完的标准**：待反讲后补充。
- **明确不做**：待细评确认。

## 已定共识

- 角色数据权限规则：主讲展示主讲数据，班主任展示班主任数据，两者都有展示主讲数据（2026-09-05 PRD）。
- 花名册数据权限现状已查清：`SmallFilterComponentServiceImpl`/`SmallRenewalService` 目前是"主讲 OR 班主任"合并可见范围，没有角色区分展示逻辑（2026-09-17 代码定位）。

## 核心概念

- PRD 原文列了5个调研点（主讲数据P0、B端购物车P0、问卷展示已支持、预报名科目区分大小班已支持、正式报名金额确认表P1），但方案表格里只写了"续班服务功能适配主讲角色"一条，购物车/下单优化和金额确认表的具体方案需要找需求方补充。

## 现在什么情况

| | |
|---|---|
| 阶段 | 需求评审 |
| 进度 | T 0/2 · R 0/0 · C 0/0 |
| 部署泳道 | 未部署 |
| 当前卡点 | PRD 里"B端购物车/下单优化""正式报名金额确认表"只有截图没有文字方案，需要找需求方（付星/马胜）补充细节 |
| 最近更新 | 2026-09-17：收到 PRD，代码定位进行中 |

## 下一步

1. 参与初评，确认按角色拆分数据权限的设计草案（见下方）。
2. 找需求方确认"B端购物车/下单优化"和"正式报名金额确认表"的具体方案（当前PRD文字描述缺失，代码定位显示两仓库都不负责下单主流程，需先确认改动仓库范围）。
3. 产出反讲文档。

## 待确认

- [ ] B端购物车/下单优化具体方案 —— 等需求方补充；真正的订单/购物车逻辑在独立的order/cart服务（Feign name `ORDER-B.GAOTU100.COM`/`ORDER.GAOTU100.COM`），需确认具体仓库名
- [ ] 正式报名金额确认表具体方案（PRD标P1，只有截图） —— 等需求方补充

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| student-center | 待定 | `domain/service/small/SmallFilterComponentServiceImpl#buildOneSelfQuery/buildAllQuery`（用`nestedQuery("mainTeacherList"...)` should `nestedQuery("assistantList"...)`构造班级可见范围，是当前"OR合并"权限判断的核心改造点）；`domain/service/roster/small/SmallRenewalService#statistic/searchUser`（扁平权限字段`assistantAccountId`/`mainTeacherAccountIds`，同样是should合并）；`domain/service/roster/RosterService#getMyUserIds`（老版大班花名册，只用`assistantAccountId`，纯班主任视角） |
| student-data | 待定 | ES宽表模型 `domain/smallclazz/model/WideSmallClazzEsModel`：`mainTeacherList`（内部类`MainTeacher`）和`assistantList`（内部类`Assistant`）由`WideSmallClazzSubClazzBinder`绑定生成；MySQL落库层`infrastructure/dao/entity/DwsFuwuUserClazz`只有`assistant_account_id`，无主讲字段（主讲信息来自教师排课数据另一套来源，合并进ES） |
| 待确认（推测 order/cart 仓库） | — | 下单/购物车真实逻辑不在这两个仓库；`OrderBCartAdapter`/`CartEventService`（student-data）、`CartTokenAdapter`/`OrderPromotionAdapter`（student-center）只是Feign ACL适配器 |

## 设计草案

- 现状：`buildOneSelfQuery`/`SmallRenewalService` 权限判断是"主讲 OR 班主任"合并可见范围，没有角色区分展示。
- 改造方向：在权限判断处先查登录人在该班级上的角色（是否在`mainTeacherList`/`assistantList`），再决定返回主讲维度指标还是班主任维度指标，而不是简单should合并。
- 统计指标：`SmallRenewalService#statistic` 直接对ES(`ads_small_clazz_user`)做term/bool聚合实时算数字，新增主讲维度指标大概率要在上游 `syncdata/small/*` sync service（如`AdsSmallClazzUserOrderedService`、`DwsSmallClazzUserService`）加字段计算，再在`SmallRenewalService`加对应聚合分支。

## 上线影响面

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 待定 | |
| ES | 待定 | 续班服务统计指标可能涉及ES聚合 |
| MySQL DDL | 待定 | |
| MQ | 待定 | |
| 代课接口权限 | 待定 | |

## 必须知道的坑

- 
