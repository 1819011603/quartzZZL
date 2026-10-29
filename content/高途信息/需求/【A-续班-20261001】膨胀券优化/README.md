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
  - ces-teach-product:feature-xuban-20261001
  - course-center:feature-xuban-20261001
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
  - 核心改动：`PreOrderCouponIntersectService` 交集由「年级+学科成对」改为「按年级匹配」+ 补【售卖中】过滤；预报名活动商品新增「C 端外显抵扣金额」+ C 端样式二选一开关，并在下单/C 端展示。
  - 明确不做：下单页券列表范围不改；不改券本体售卖/配置。
- **模块② 小班课（小灶课/辅导班小班课）学员人数上限修改**：
  - 要解决的问题：H 精品班要上「主讲直播 + 二讲直播 1V32」课程品类，现有 1V15 小灶课（工具箱-小班课）无法达成全覆盖；工具箱选学员不支持按学员ID批量精确搜索。
  - 核心改动：小灶课可选人数上限 15→32（新建/编辑 + 关联校验全部主/从小灶课上限 ≤32）；工具箱「家长会/小班课/自习室」三页面搜索新增学员ID批量精确搜索 + 文案统一。**主链路 = teacher-tool `ParentsMeetServiceImpl`**。
  - 明确不做：不改直播教室容量（直播端已支持 1V32）；不改既有姓名/手机号搜索口径；非辅导班（1V6 等）人数额度不变；**本需求不涉及 GPS 小班课**。
- **判定做完的标准**：模块① 扩科场景推荐到后置年级全学科券、外显抵扣金额边界值/二选一互斥/0 不展示均符合、下单页与预警链路行为回归一致；模块② 新建/编辑小班课选 32 人成功、33 人拦截，小灶课关联含上限 >32 的主/从小班课拦截，三页面按多个学员ID精确命中、文案正确。

## 已定共识

> 硬约束：改代码前先扫一眼。每条一句话说完，只保留最终口径；必要理由放 changelog。

- 本迭代为**本期在范围内的新需求**，两个子需求同批评审、一起做（2026-10-29）。
- **统一分支**：本需求 2 个子需求共用同一个分支名 **`feature-xuban-20261001`**，不按子需求拆分支（2026-10-29 所有者明确）。
- 统一分支已从**最新 `origin/release`** 建在 **6 个真实涉及仓库**：product-server / promotion / promotion-management / student-center / cart / teacher-tool；各分支 `ahead=0`、无 upstream（本地占位，未推远端）。
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
| 进度 | T 3/5 · R 0/0 · C 0/0 |
| 部署泳道 | 未部署 |
| 当前卡点 | 模块①：下单页券列表口径未拍板；模块②：工具箱三页面选学员接口所属服务/仓库未确认 |
| 最近更新 | 2026-10-29：合并为「1 需求 + 2 子需求」；收敛为统一分支 `feature-xuban-20261001`（8 仓，基于最新 release，旧占位分支已清理，student-data 无改动）；两篇技术方案与本地归档同步统一分支口径 |

## 下一步

> **只列还没做的**。必须是能直接上手的动作，"继续推进"不算。

1. 模块①方案评审：拍板「下单页券列表口径」（改动仓库归属已按代码证据定，见「涉及的代码」）。
2. 模块②：与页面负责人核对工具箱「家长会/小班课/自习室」选学员接口所在服务/仓库（见 [[tasks]] T-02）。
3. 与产品确认模块①与 EM 续班的关系（背景备注，见 [[links]] 技术方案第 8 节）。
4. 评审后按确认结论在统一分支 `feature-xuban-20261001` 建各仓 `specs/<迭代>/tech_spec.md`。

## 怎么验 / 新建的东西

> 环境、造好的测试数据、新建的表与 Apollo key → 见 [[links]] 两个模块技术方案「验证思路」节。
> 未部署、未造数据。

## 待确认

> 需求评审/反讲里没定的问题。定了就删掉，并在 changelog 记结论。

- [ ] （模块①）下单页券列表是「页面范围不变但口径随推荐规则变」还是「连口径也不变」—— 等产品。**代码证据：`PreOrderCouponIntersectService#intersect` 被下单页/C 端/发链接三处共用**，若「下单页口径不变」则交集需按调用方分叉（见方案① §8）
- [ ] （模块①）「C 端外显抵扣金额」与「抵扣金额」样式二选一是否需要过渡期并存 —— 等产品
- [ ] （模块①）**【待所有者确认】**「膨胀券的，这次不用」的确切边界（模块①是否在本次范围，还是仅「EM 续班」形态不用）—— 等所有者/产品
- [ ] （模块②）「小班预约EM改」是否限 EM 业务线、上限 32 是否灰度 —— 等产品答
- [ ] （模块②）学员ID搜索是否含已在班学员、是否按辅导班范围限制 —— 等产品答

## 涉及的代码

| 仓库 | 分支 | 模块 | 关键位置 |
|---|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/product-server | feature-xuban-20261001 | ① | `PreOrderCouponIntersectService#intersect`（L345 `postPairs.contains(pairKey(grade,subject))` 现为年级+学科成对；L379/399-403 `isCouponInUse` 仅【使用中】）、`CStyleConfigVO`、`ProcessService` |
| /Users/gaotu/IdeaProjects/JavaProject/promotion | feature-xuban-20261001 | ① | `PreOrderActivityProduct*`（新增外显抵扣金额列） |
| /Users/gaotu/IdeaProjects/JavaProject/promotion-management | feature-xuban-20261001 | ① | `PreOrderActivityProductEditReq` / `PreOrderActivityDomainServiceImpl` |
| /Users/gaotu/IdeaProjects/JavaProject/student-center | feature-xuban-20261001 | ① | `PreOrderCouponController` / `PreOrderCouponVO`（`deductibleAmount` L32-33，新增「外显抵扣金额」字段展示）。**模块② 选学员搜索不在此仓**（已定案在 teacher-tool） |
| /Users/gaotu/IdeaProjects/JavaProject/cart | feature-xuban-20261001 | ① | `RegistrationService` / `PreRegistrationCouponAssembler`（L259-262 券抵扣金额），C 端下单/展示「外显抵扣金额」或「抵扣金额」 |
| /Users/gaotu/IdeaProjects/JavaProject/teacher-tool | feature-xuban-20261001 | ② | `ParentsMeetServiceImpl`：L180-181 `@ApolloJsonValue("${parentsMeeting.type.limit.map:{3:15;4:30}}")`、L273/347/1131 校验、L1122 `checkRelationStudentLimit`；`ParentsMeetErrorCode.STUDENT_EXCEED_RELATION_LIMIT`（L67 文案）；**选学员搜索 `ManageSubclazzController#/studentList`（L185）**（工具箱 boss-counselor 调 `/bgwApi/teacher-tool/manage/subclazz/studentList`） |
| /Users/gaotu/IdeaProjects/JavaProject/student-data | **无（不建分支）** | — | 已核：无 `externalDeduct`/`deductibleAmount`、无 `PreOrderCouponIntersect`/`listDisplayableCoupons`；家长会/小班课相关仅有 DWS ETL（`DwsParentMeetingUserInfoConsumer`、`DwsLessonUserRemindSyncConsumer` 等），与选人上限/ID 搜索无关 |
| /Users/gaotu/IdeaProjects/JavaProject/ces-teach-product | **不需改动（已撤分支）** | — | `NodeInstanceUserCountValidator` 教室形态上限默认 `{"4":32,"5":32}` 已是 32，本需求不改 |
| /Users/gaotu/IdeaProjects/JavaProject/course-center | **不需改动（已撤分支）** | — | `Clazz1vNArrangeAddBaseChecker` 排课随教室上限自动放宽，本需求不改 |

> 分支名同时写进上面 frontmatter 的 `branches:`，下个会话可 `rg -l "<分支名>" 需求根目录` 直接反查到本目录。

## 上线影响面

> 上线 checklist「三、配置明细」五项。**「不涉及」也要写出来**，空着无法区分"不涉及"和"漏了"。

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 是 | 模块② `parentsMeeting.type.limit.map`（teacher-tool）type3 15→32；`ces.nodeInstance.userCountLimit.roomTypeMaxCount` 核对生效环境；模块① 券状态白名单（沿用既有 key），灰度开关按需 |
| ES | 否 | |
| MySQL DDL | 是 | 模块① 预报名活动商品新增「外显抵扣金额」列（promotion 库）；若走 json ext 则无需；模块② 预计无 |
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