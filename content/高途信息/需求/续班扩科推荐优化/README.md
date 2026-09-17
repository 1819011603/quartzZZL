---
title: 续班扩科推荐优化
aliases: []
status: 需求评审
owner: zhangzeling
branches:
updated: 2026-09-17
tags: [需求]
---

# 续班扩科推荐优化

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[changelog|📜 决策摘要]]
> 技术方案在飞书反讲文档里（见 [[links]]），本地不留副本。
> 续接这个需求：读完本文件即可。

## 一句话

续班计划新增【推荐排除】配置项，避免大小班在读学员因授课模式未隔离被推荐已在读学科的扩科，减少误退费和重复缴费。

## 需求摘要

- **要解决的问题**：大小班在读学员数据未隔离，会出现"大班在读数学，扩科推荐还推数学"这类错误推荐，导致学员误退费重新缴费、客诉。
- **给谁用**：B端顾问/二讲（推荐链接、下单推荐范围），C端学员（报名页推荐商品）。
- **核心改动**：
  1. 续班计划新增扩科配置项【推荐排除】：枚举【无排除】/【排除不同授课模式在读】。
  2. 无排除：保持现状（按后置课程年级匹配扩科推荐年级）。
  3. 排除不同授课模式在读：在现状基础上，前置大班课排除该学员在读的小班课学科，前置小班课排除在读的大班课学科；"在读"范围有明确的班级筛选条件（同学年学期、授课模式匹配、线上、非赠课、订单未全退、专题课/系列课、非纯预售、非成人业务）。
  4. 影响范围：B端(大班课/小班课续班服务的推荐链接批量/单项/通用链接、下单-推荐范围) + C端(报名页推荐商品)。
- **判定做完的标准**：待反讲后补充。
- **明确不做**：历史续班计划数据回溯为【无排除】，不重新计算历史扩科推荐结果。

## 已定共识

- 新增枚举配置【推荐排除】，默认值为空（扩科推荐为"是"时可编辑），历史数据回溯为【无排除】（2026-09-05 PRD）。
- "在读"范围的具体筛选条件已在PRD中明确（同学年学期+授课模式+线上+非赠课+订单未全退+专题课系列课+非纯预售+非成人）（2026-09-05 PRD）。
- "在读判断"可复用 `SubclazzStudentBizFeignService#listSubclazzStudentsByUserIds` 按`clazzRoomType`过滤，PRD多条件"在读"定义需新建组合过滤器（2026-09-17 代码定位）。

## 现在什么情况

| | |
|---|---|
| 阶段 | 需求评审 |
| 进度 | T 1/1 · R 0/0 · C 0/0 |
| 部署泳道 | 未部署 |
| 当前卡点 | 无 |
| 最近更新 | 2026-09-17：收到 PRD，代码定位进行中 |

## 下一步

1. 参与初评，确认设计草案（`SubclazzStudentBizFeignService`已支持按授课模式过滤在读学员，可直接复用）。
2. 确认C端报名页推荐商品接口归属（推测在promotion仓库，需要单独去该仓库确认，本轮未接触）。
3. 确认"下单推荐范围"过滤具体在哪个Controller（推测promotion或product-server）。
4. 产出反讲文档。

## 待确认

- [ ] 推荐链接、下单推荐范围、C端报名页分别归属哪个仓库 —— B端推荐链接在student-center，C端报名页和下单推荐范围推测在promotion仓库，需去该仓库确认
- [ ] 跨仓库改动是否都由本人负责（参考 [[../续班预报名使用膨胀券/README|续班预报名膨胀券]] 类似情况，那次004-xuban-pre需求除student-data外全是本人负责） —— 等确认

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| 外部主数据服务（product-server，不在给定两仓库） | — | `com.gaotu.clientv4.renwal.dto.ExpandSubjectConfigDTO`（扩科配置本体：`expandSubject`/`forceBuy`/`allowDuplicate`/`beginTime`/`endTime`/`recommendList`），本次新增【推荐排除】枚举字段最可能落在这里 |
| student-center | 待定 | `student-center-adapter/.../acl/RenewalMasterAclService#getExpandSubjectConfig`（+Impl，Redis缓存）；`web/.../RenewalContentConfigController#getConfig`（返回`expandSubjectEnabled`）；推荐链接：`domain/service/roster/content/RenewalRecommendStrategy`（大班）、`SmallRenewalService`/`SmallRenewalController`（小班）；实际短链生成转发至`student-center-adapter/.../acl/adapter/PromotionRecommendLinkAdapter`（Feign到`PROMOTION-B.GAOTU100.COM`） |
| student-data | 待定 | 年级匹配核心：大班`domain/service/impl/RenewalInfoServiceImpl`（`calGradeRenewalInfo`/`groupGradeCurrentRenewalSubjectMap`），小班`domain/small/SmallRenewalSubjectService#calRenewalInfo`——这两处是新增"排除不同授课模式在读"过滤条件最可能要改的地方；在读查询可复用`infrastructure/acl/SubclazzStudentBizFeignService#listSubclazzStudentsByUserIds(userIds, clazzRoomType, status)`；业务类型字段：`client/acl/model/CourseDO#bizType`（1中小学/2成人） |
| 待确认（推测 promotion / product-server） | — | C端报名页推荐商品接口、下单页选品过滤，两仓库均未找到，需单独确认 |

## 设计草案

- 【推荐排除】枚举加在 `ExpandSubjectConfigDTO`（product-server侧，本次改动会跨仓库）。
- "排除不同授课模式在读"的过滤逻辑加在 student-data 的 `RenewalInfoServiceImpl`/`SmallRenewalSubjectService` 计算续班/扩科科目集合处，调用 `SubclazzStudentBizFeignService#listSubclazzStudentsByUserIds` 按`clazzRoomType`查另一种授课模式的在读班级，再排除对应学科。
- "在读"的多条件定义（专题课系列课、非纯预售、非成人等）需要新建一个组合过滤器（参考`CommonRuleFilter`风格），不能只用现成的`status`字段判断。

## 上线影响面

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 否（预计） | |
| ES | 待定 | |
| MySQL DDL | 是（预计） | 续班计划新增【推荐排除】配置字段 |
| MQ | 否 | |
| 代课接口权限 | 待定 | |

## 必须知道的坑

- 
