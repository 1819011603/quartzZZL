---
title: 续班问卷匹配优化
aliases: []
status: 需求评审
owner: zhangzeling
branches:
updated: 2026-09-17
tags: [需求]
---

# 续班问卷匹配优化

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[changelog|📜 决策摘要]]
> 技术方案在飞书反讲文档里（见 [[links]]），本地不留副本。
> 续接这个需求：读完本文件即可。

## 一句话

优化续班问卷的匹配范围、匹配规则优先级，并解决调课调班后问卷数据不同步的问题。

## 需求摘要

- **要解决的问题**：
  1. 一个问卷挂多个班级时，学员填问卷可能被错误匹配到其他班级的同名/同号学员（问卷匹配范围过宽）。
  2. 学员先填问卷、后调课调班，问卷只展示在调课前的班级，调课后的班级看不到。
- **给谁用**：辅导老师/二讲（问卷明细、续班花名册的问卷字段）。
- **核心改动**：
  1. 问卷匹配范围收紧为【问卷+续班计划+班级+辅导老师】：问卷和续班计划必须完全匹配，班级和辅导老师不做强校验（按新匹配规则判断在读）。
  2. 匹配优先级：CDS userID+班级学员userID（最高优）→ 班级内手机号 → 计划内手机号 → 班级内姓名 → 计划内姓名 → 班级内亲属手机号 → 计划内亲属手机号；命中多个取学员ID小的。
  3. 同手机号多次提交只展示最新明细（不依赖CDS的限制，EES自己加）；不同手机号提交都展示。
  4. 调课调班后（A班绑定问卷同B班相同问卷）：问卷明细和续班花名册在A、B两班都展示该问卷数据。
- **判定做完的标准**：待反讲后补充验收标准。
- **明确不做**：历史数据不回溯。

## 已定共识

- 问卷匹配范围调整为【问卷+续班计划+班级+辅导老师】，问卷和续班计划必须完全匹配，班级/辅导老师不强校验（2026-09-05 PRD）。
- 历史数据不回溯（2026-09-05 PRD）。

## 现在什么情况

| | |
|---|---|
| 阶段 | 需求评审 |
| 进度 | T 1/1 · R 0/0 · C 0/0 |
| 部署泳道 | 未部署 |
| 当前卡点 | 无 |
| 最近更新 | 2026-09-17：收到 PRD，代码定位进行中 |

## 下一步

1. 参与初评：确认问卷匹配范围调整、匹配优先级规则、调课调班同步这三块的具体设计（草案见下方「设计草案」）。
2. 调课调班同步目前**没有现成的事件挂载点**（`RenewalQuestionnaireConsumer` 监听的是续班计划课程配置变更，不是学员调课调班），需要找 student-center 侧调课调班成功后发的 MQ topic 作为新增消费者的挂载点，或直接在调班流程里加同步调用。
3. 产出反讲文档。

## 待确认

- [ ] student-center 调课调班成功后是否已发 MQ 消息（topic 名）—— 需在 student-center 里进一步定位调班流程代码
- [ ] "同手机号多次提交只展示最新"这条限制加在哪层最合适（问卷回收落库时 vs 查询时去重）

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| student-data | feature-xuban-pre（待新建独立分支） | `infrastructure/acl/QuestionnaireAclService`(+Impl) 封装问卷中心调用；`app/service/syncdata/RenewalQuestionnaireStatusServiceV2` 计算花名册`renewalQuestionnaireStatus`字段；`facade/mq/renewal/RenewalQuestionnaireConsumer`（topic `gaotu_product_renew_master_event_test`）目前是唯一"问卷状态刷新"挂载点，但触发源是续班计划课程变更非调班；`infrastructure/dao/entity/StudentSubclazzQuestionnaire`（问卷与班级/辅导老师绑定落地表） |
| student-center | 待定 | `domain/service/roster/RenewalService#queryQuestionnaireInfo`（按班级+续班计划维度调用`questionnaireFeignAdapter.match()`，是当前"仅班级内匹配"逻辑入口，Redis缓存`QUESTIONNAIRE_MATCH_KEY+renewalPlanId+clazzNumber`）；`#getRenewalPlanId`（一个班级绑多个续班计划直接抛异常，改造时要注意）；`#pageQueryQuestionnaire`（按userId去重取`(v1,v2)->v1`，是本次要改的多次提交去重逻辑）；`job/mq/consumer/ons/questionnaireListener`（问卷提交消息入口，topic `gaotu_questionnaire_add_answer_test`）；`StudentQuestionnaireBehaviorListener`（问卷完成消息，topic `teacher_tool_questionnaire_finish_test`） |

## 设计草案

- **问卷匹配范围收紧**：改造点在 student-center `RenewalService#queryQuestionnaireInfo` 及其下游匹配逻辑，需要新增"按辅导老师"维度的判断（目前完全没有辅导老师维度的过滤）。
- **匹配优先级规则**：目前代码里**没有实现**按手机号/姓名匹配学员的6级优先级规则，是全新逻辑，需要新建一个匹配服务（可仿照 `CommonRuleFilter` 风格）。
- **调课调班同步**：需要新的事件驱动机制，参考 `RenewalQuestionnaireConsumer` 的写法（按`UserClazzDimension`调用 `AdsSubclazzUserSyncUpdateService`/`AdsSmallClazzUserSyncUpdateService` 直接更新ES宽表），但事件源要换成调班事件。

## 上线影响面

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 待定 | |
| ES | 待定 | 花名册"续班问卷"字段可能在ES |
| MySQL DDL | 待定 | |
| MQ | 待定 | 调班事件可能走MQ |
| 代课接口权限 | 待定 | |

## 必须知道的坑

- 
