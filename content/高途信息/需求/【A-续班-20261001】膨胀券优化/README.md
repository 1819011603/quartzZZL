---
title: 【A-续班-20261001】膨胀券优化
aliases: [膨胀券预报名优化-推荐和外显抵扣金额, 膨胀券预报名优化, 小班课学员人数上限修改]
status: 需求评审
owner: zhangzeling
branches:
  - product-server:feature-xuban-20261001
  - promotion:feature-xuban-20261001
  - promotion-management:feature-xuban-20261001
  - student-center:feature-xuban-20261001
  - cart:feature-xuban-20261001
  - teacher-tool:feature-xuban-20261001
updated: 2026-10-29
tags: [需求]
---

# 【A-续班-20261001】膨胀券优化

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[changelog|📜 决策摘要]]
> 技术方案在飞书（见 [[links]]），本地不留副本。
> 续接这个需求：读完本文件即可。

## 一句话

**这是 1 个需求、含 2 个子需求**（同批评审、共用统一分支 `feature-xuban-20261001`）：①膨胀券预报名推荐范围放宽为「后置年级全学科券」并新增业务可填的「C 端外显抵扣金额」；②辅导班小班课可选学员上限 15→32，并在工具箱「家长会/小班课/自习室」新增「学员ID批量精确搜索」。

## 需求摘要

> 只写当前最终口径。

- **模块① 膨胀券预报名优化-推荐和外显抵扣金额**（P0）：
  - 要解决的问题：预报名券推荐范围不符合业务预期（业务要「推荐后置年级全部膨胀券」）；外宣抵扣金额需业务手填（非系统算出的真实抵扣）。
  - 核心改动：`PreOrderCouponIntersectService` 交集由「年级+学科成对」改为「按年级匹配」+ 补【售卖中】过滤；**新增独立【C 端外显抵扣金额】字段**（业务手填，与【抵扣金额】并列、不共用；promotion 新增 DB 列），C 端样式配置**新增配套开关、与【抵扣金额】开关二选一**；下单页/C 端按配置展示。
  - 明确不做：不改券本体售卖/配置；**下单页的券集合是否随新规则变化尚待产品确认**（见 [[links]] 方案① §8.1）。
- **模块② 小班课（小灶课/辅导班小班课）学员人数上限修改**：
  - 要解决的问题：H 精品班要上「主讲直播 + 二讲直播 1V32」课程品类，现有 1V15 小灶课（工具箱-小班课）无法达成全覆盖；工具箱选学员不支持按学员ID批量精确搜索。
  - 核心改动：小灶课可选人数上限 15→32（新建/编辑 + 关联校验全部主/从小灶课上限 ≤32）；工具箱「家长会/小班课/自习室」三页面搜索新增学员ID批量精确搜索 + 文案统一。**主链路 = teacher-tool `ParentsMeetServiceImpl`**。
  - 明确不做：不改直播教室容量（直播端已支持 1V32）；不改既有姓名/手机号搜索口径；非辅导班（1V6 等）人数额度不变；**本需求不涉及 GPS 小班课**。
- **判定做完的标准**：模块① 扩科场景推荐到后置年级全学科券、【C 端外显抵扣金额】边界值/双开关互斥/为 0 不展示均符合、下单页与预警链路行为回归一致；模块② 新建/编辑小班课选 32 人成功、33 人拦截，小灶课关联含上限 >32 的主/从小灶课拦截，三页面按多个学员ID精确命中、文案正确。

## 已定共识

> 硬约束：改代码前先扫一眼。每条一句话说完，只保留最终口径；必要理由放 changelog。

- 本迭代为**本期在范围内的新需求**，两个子需求同批评审、一起做（2026-10-29）。
- **统一分支**：本需求 2 个子需求共用同一个分支名 **`feature-xuban-20261001`**，不按子需求拆分支（2026-10-29 所有者明确）。
- 统一分支已从**最新 `origin/release`** 建在 **6 个真实涉及仓库**：product-server / promotion / promotion-management / student-center / cart / teacher-tool；各分支 `ahead=0`、无 upstream（本地占位，未推远端）。
- 模块① **外显抵扣金额按 PRD（方向 A，所有者确认）**：**新增独立【C 端外显抵扣金额】字段**（与【抵扣金额】并列、不共用），配置页在抵扣金额列后新增该列（0–100000/两位小数/默认0/支持批量修改）；C 端样式配置**新增配套开关**，与【抵扣金额】开关**二选一**；下单页/C 端按配置展示。**promotion 需新增 DB 列（DDL 工单）**。（2026-10-29）
- 模块② **上限 15→32 直接全量、不需要灰度、不按业务线区分**；「小班预约EM改」无特殊含义；**学员 ID 搜索范围与现有搜索一致**（不额外限辅导班、不扩大范围）。（2026-10-29 产品/所有者答复）
- 模块②「小班课」= **小灶课 / 辅导班小班课（工具箱-小班课）**，不是 GPS 小班课；主链路在 teacher-tool（`ParentsMeetServiceImpl`）。
- **模块② 选学员搜索已定案在 teacher-tool**：工具箱（`boss-counselor` Toolbox）调 `/bgwApi/teacher-tool/manage/subclazz/studentList`（现仅手机号批量+姓名模糊，PRD 新增手机号后4位批量+学员ID批量精确）；**不在 student-center**（GPS/MyStudent 链路排除）。（2026-10-29 依据前端调用链定案）
- **ces-teach-product / course-center 不需改动**（教室形态上限默认已 32、排课随教室上限自动放宽，PRD 不涉及），已撤其统一分支。
- **student-data 无代码改动**，不建本需求分支（已删其两个旧占位分支；证据见「必须知道的坑」）。（2026-10-29 复核）
- 模块① 改动点均不在 student-data；模块② 改动点不在 student-data（均有类/行号证据）。
- 模块① 券推荐交集是唯一同源实现（发链接 / B 端下单弹窗 / C 端落地页三处共用），改口径必须只改一处（2026-10-29）。

## 现在什么情况

| | |
|---|---|
| 阶段 | 需求评审（技术方案已出，待评审） |
| 进度 | T 5/7 · R 0/0 · C 0/0 |
| 部署泳道 | 未部署 |
| 当前卡点 | 模块①：下单页的券是否随新推荐规则一起变未拍板、【待所有者确认】「膨胀券的，这次不用」边界 |
| 最近更新 | 2026-10-29：合并为「1 需求 + 2 子需求」；统一分支 `feature-xuban-20261001`（6 仓，基于最新 release；ces-teach-product/course-center 撤分支、student-data 无改动）；模块① 外显抵扣金额按**方向 A**（新增独立字段 + 二选一开关）定稿；模块② 产品答复（上限直接全量、不按业务线；ID 搜索范围同现有）落入方案②；模块② 选学员接口定案在 teacher-tool |

## 下一步

> **只列还没做的**。必须是能直接上手的动作，"继续推进"不算。

1. 模块①方案评审：拍板「下单页的券是否随新推荐规则一起变」（A 统一改一处 / B 按调用方分叉，方案推荐 A，见方案① §8.1）。
2. 与所有者/产品确认「膨胀券的，这次不用」的确切边界（方案① §8）。
3. 评审后按确认结论在统一分支 `feature-xuban-20261001` 建各仓 `specs/<迭代>/tech_spec.md`。

## 怎么验 / 新建的东西

> 环境、造好的测试数据、新建的表与 Apollo key → 见 [[links]] 两个模块技术方案「验证思路」节。
> 未部署、未造数据。

## 待确认

> 需求评审/反讲里没定的问题。定了就删掉，并在 changelog 记结论。

- [ ] （模块①）**下单页的券要不要跟着新推荐规则一起变**：A 统一改一处（下单页的券跟着变）/ B 按调用方分叉（下单页不变）—— 等产品；方案推荐 A。详见 [[links]] 方案① §8.1（含 `PreOrderCouponIntersectService#intersect` 被下单页/C 端/发链接三处共用的证据）
- [ ] （模块①）**【待所有者确认】**「膨胀券的，这次不用」的确切边界（模块①是否在本次范围，还是仅「EM 续班」形态不用）—— 等所有者/产品。详见方案① §8

## 涉及的代码

| 仓库 | 分支 | 模块 | 关键位置 |
|---|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/product-server | feature-xuban-20261001 | ① | `PreOrderCouponIntersectService#intersect`（L345 `postPairs.contains(pairKey(grade,subject))` 现为年级+学科成对；L379/399-403 `isCouponInUse` 仅【使用中】）、`CStyleConfigVO`、`ProcessService` |
| /Users/gaotu/IdeaProjects/JavaProject/promotion | feature-xuban-20261001 | ① | `PreOrderActivityProduct*`（**新增独立列 `external_deductible_amount`** 承载【C 端外显抵扣金额】）；**需 promotion 库 DDL 工单** |
| /Users/gaotu/IdeaProjects/JavaProject/promotion-management | feature-xuban-20261001 | ① | `PreOrderActivityProductEditReq` / `PreOrderActivityDomainServiceImpl` |
| /Users/gaotu/IdeaProjects/JavaProject/student-center | feature-xuban-20261001 | ① | `PreOrderCouponController` / `PreOrderCouponVO`（`deductibleAmount` L32-33；下单页券列表**新增【C 端外显抵扣金额】展示**）。**模块② 选学员搜索不在此仓**（已定案在 teacher-tool） |
| /Users/gaotu/IdeaProjects/JavaProject/cart | feature-xuban-20261001 | ① | `RegistrationService` / `PreRegistrationCouponAssembler`（L259-262）；C 端下单/展示【C 端外显抵扣金额】或【抵扣金额】 |
| /Users/gaotu/IdeaProjects/JavaProject/teacher-tool | feature-xuban-20261001 | ② | `ParentsMeetServiceImpl`：L180-181 `@ApolloJsonValue("${parentsMeeting.type.limit.map:{3:15;4:30}}")`、L273/347/1131 校验、L1122 `checkRelationStudentLimit`；`ParentsMeetErrorCode.STUDENT_EXCEED_RELATION_LIMIT`（L67 文案）；**选学员搜索 `ManageSubclazzController#/studentList`（L185）**（工具箱 boss-counselor 调 `/bgwApi/teacher-tool/manage/subclazz/studentList`） |
| /Users/gaotu/IdeaProjects/JavaProject/student-data | **无（不建分支）** | — | 已核：无 `externalDeduct`/`deductibleAmount`、无 `PreOrderCouponIntersect`/`listDisplayableCoupons`；家长会/小班课相关仅有 DWS ETL（`DwsParentMeetingUserInfoConsumer`、`DwsLessonUserRemindSyncConsumer` 等），与选人上限/ID 搜索无关 |
| /Users/gaotu/IdeaProjects/JavaProject/ces-teach-product | **不需改动（已撤分支）** | — | `NodeInstanceUserCountValidator` 教室形态上限默认 `{"4":32,"5":32}` 已是 32，本需求不改 |
| /Users/gaotu/IdeaProjects/JavaProject/course-center | **不需改动（已撤分支）** | — | `Clazz1vNArrangeAddBaseChecker` 排课随教室上限自动放宽，本需求不改 |

> 分支名同时写进上面 frontmatter 的 `branches:`，下个会话可 `rg -l "<分支名>" 需求根目录` 直接反查到本目录。

## 上线影响面

> 上线 checklist「三、配置明细」五项。**「不涉及」也要写出来**，空着无法区分"不涉及"和"漏了"。

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 是 | 模块② `parentsMeeting.type.limit.map`（teacher-tool）type3 15→32（直接全量，无需灰度）；模块① 券状态白名单（沿用既有 key） |
| ES | 否 | |
| MySQL DDL | 是 | 模块① promotion 预报名活动商品**新增独立列** `external_deductible_amount`（需 promotion 库 DDL 工单）；模块② 无 |
| MQ | 否 | |
| 代课接口权限 | 可能 | 两模块若有新 B 端点需登记 |

## 必须知道的坑

> 只写**不知道就会走错路**的。没有就删掉这一节。

- **模块① 交集是唯一同源实现**：`PreOrderCouponIntersectService` 被发链接 / B 端下单弹窗 / C 端落地页三处共用；改口径会影响三处，别只改一处。
- **模块① 券状态枚举**：`COUPON_STATUS_IN_USE = 1`（使用中），2 是已失效；本次需补【售卖中】过滤。
- **模块② 真正卡「15」的是 teacher-tool 的 `typeLimitMap`**，不是 ces-teach-product 的教室形态上限（默认已 32）；改错地方会导致「前端可选 32 但教室/后端仍按 15 卡」。
- **模块②「小班课」是 B 端工具箱的小灶课类型**（`ParentMeetingTypeEnum` type=3），即**小灶课/辅导班小班课**，不是学生端的 subclazz，也**不是 GPS 小班课**（`GpsGroupController` 等与本需求无关）；人数上限走 `parentsMeeting.type.limit.map`。
- **student-data 不在本次改动范围**：已核无相关代码（无外显抵扣/推荐交集；家长会/小班课相关仅 DWS ETL），两个旧占位分支已删，本需求不建分支。
- **分支基线漂移**：旧占位分支（`feature-xuban-presale-expand-opt` / `feature-small-clazz-limit-and-search`）中，product-server、student-center 基于**过期** release 头（如 product-server 旧 `a91c18697`，现 `548e8a8c7`）。统一分支已统一改为从**最新 `origin/release`** 建，别再从旧占位分支续。