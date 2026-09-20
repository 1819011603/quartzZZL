---
title: 【A-续班-20260902】续班优化
aliases: [续班优化(秋季批), 续班问卷匹配优化, 续班退费AI模块配置化, 续班退费数据落表, 小班续班主讲数据下单优化, 续班扩科推荐优化]
status: 需求评审
owner: zhangzeling
branches:
updated: 2026-09-21
tags: [需求]
---

# 【A-续班-20260902】续班优化

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[changelog|📜 决策摘要]] · [问卷匹配-DDD建模方案.md](问卷匹配-DDD建模方案.md)
> 技术方案（现状 / 方案对比 / 详细设计 / 接口 / 风险）在飞书反讲里，见 [[links]]；本文件只留当前结论和指针。
> 飞书：需求总入口 https://gaotuedu.feishu.cn/wiki/Qox8wFcmHiXBgnkxFBtcd82gnsh → **技术反讲（子需求 1/2/3/5）https://gaotuedu.feishu.cn/wiki/EC45wOefUi0buMkO7O0cipp9nEc**
> 续接这个需求：读完本文件即可。

## 一句话

付星/马胜一次性打包转发的 5 个续班优化子需求。

## 需求摘要

5 个子项，PRD 均 V1.0 / 2026-09-05：

| 优先级 | 子需求 | 一句话 | 子项P级 |
|---|---|---|---|
| 1 | 问卷匹配优化 | 匹配范围收紧 + 7 档匹配优先级 + 调课调班同步问卷数据 | 匹配逻辑 未标 / 调课同步 P1 |
| 2 | 小班续班适配主讲 | 小班续班服务按角色(主讲/班主任)展示数据；下单优化不做 | 主讲 P0 |
| 3 | 扩科推荐优化 | 续班计划新增【推荐排除】，避免跨授课模式重复推荐 | — |
| 4 | 数据落表 | 续班/退费数据落表供导数分析 | — |
| 5 | AI 模块配置化 | 续班/退费 AI 按部门配置模块开关，降本 | — |

- **给谁用**：主讲、班主任(二讲)；学部运营（数据落表）。
- **判定做完的标准**：本批 4 个子需求各自评审、反讲、开发、上线，按子需求粒度跟踪（见 [[tasks]]）。
- **明确不做**：本批做 1/2/3/5；**子需求4(数据落表)不做**；子需求2 的**下单优化不做**（只做"适配主讲"）。所有子需求历史数据**不回溯 / 不重算**。

## 已定共识

- 5 个子需求彼此独立、可并行，不要求同批上线（2026-09-17）。
- **问卷匹配**：范围 = 问卷 + 续班计划 + 班级 + 辅导老师；**问卷与续班计划必须完全匹配**，班级 / 辅导老师不做强校验；规则为 **7 档优先级**（同班 / 同计划 × 手机号 → 姓名 → 亲属手机号），**多命中取学员 ID 小的**；历史不回溯。
- **调课调班同步**：前提是 A/B 两班绑定同一份续班问卷；要**新增消费** `gaotu_after_sale_event_test` + tag `TRANSFER_TOUCH_EVENT`（现只有 reach-service 消费）。
- **AI 模块配置化**：未配置的模块要**同时做到"前端不可用 + AI 不分析"**（2026-09-18 产品确认为隐藏）；续班 AI 8 个 + 退费 AI 6 个（清单按 PRD）。
- **数据落表**：续班覆盖大小班课、退费仅大班课（本批不做，仅登记）。
- **主讲适配**：仅小班；**主讲（含双角色）按班级维度、仅班主任按辅导班维度**；现状 OR 合并**已等于** PRD 口径，**很可能无需开发**（待评审确认）；下单优化不做。
- **扩科推荐**：问题根源 = 扩科班级 / 商品不区分大小班可随意选，导致跨授课模式重复推荐；**【推荐排除】** = 扩科推荐为【是】时可编辑、默认空、单选，枚举【无排除】/【排除不同授课模式在读】；"在读"8 条件中 5 项有现成过滤器，仅"授课模式 / 上课形式线上 / 订单未全部退款"3 项需新建；当前不回溯。

## 现在什么情况

| | |
|---|---|
| 阶段 | 需求评审 |
| 进度 | T 5/10（代码定位完成；问卷匹配 4 项 + 扩科 1 项待办）· R 0/0 · C 0/0 |
| 部署泳道 | 未部署 |
| 当前卡点 | 数据落表需数仓侧定落表方式；扩科"在读"3 个条件需新建过滤器；跨仓承接方未定 |
| 最近更新 | 2026-09-21：README 瘦身（详细设计归飞书反讲）+ tasks 补「完成判据」；飞书反讲订正（补 Non-goals / 验收判据 / 交付门禁；AI 部门口径按 PRD 改「虚拟架构部门」；修正 compute 行号等） |

## 下一步

1. 参与初评：按优先级过 5 个子需求的设计草案（飞书反讲）。
2. 【数据落表】找数仓侧确认落表方式：MQ 推送 / binlog 直拉 / 直连 Doris Stream Load（本仓有先例）。
3. 【扩科推荐】确认跨仓(cart / product-server / order / reach-service)改动承接方；"在读"3 个条件的数据源与口径。
4. 【问卷匹配】确认调课调班同步承接方与旧班 A 的来源。
5. 【AI 配置化】定部门 key 口径与"不展示"落到的接口 / 字段。

## 待确认

- [ ] 【数据落表】落表方式（MQ / binlog / 直连 Doris）—— 数仓侧
- [ ] 【数据落表】"续班 / 退费所有字段"清单，含 GAIA 动态字段如何落表 —— 需 PRD 提供清楚
- [ ] 【扩科推荐】"授课模式 / 上课形式线上 / 订单未全部退款"3 条件的数据源与口径 —— 细评
- [ ] 【扩科推荐】排除过滤收口层（student-data 计算侧 vs cart 推荐侧）—— 评审
- [ ] 【扩科推荐】下单页选品是否同排除集过滤 —— 评审
- [ ] 【主讲适配】是否确认无需开发（现状 OR 已等于 PRD 分角色口径）—— 数据侧 + 评审
- [ ] 【主讲适配】小班花名册列表页权限账号字段来自 DB 表 `es_query_config`(type=5)，线上配置未验证 —— 线上确认
- [ ] 【问卷匹配】调课调班同步承接方（product-server 新建 consumer+DAO vs 扩 student-data `DwsAfterSaleSyncConsumer`）+ 旧班 A 来源 —— 评审
- [ ] 【问卷匹配】teacher-tool 是否加 `renewal_number` 列（建议不加）；改派能力是否本期补 —— 评审
- [ ] 【问卷匹配】同名 / 亲属手机号歧义的产品解法（待认领 / 改派 / 一人一链）—— 产品
- [ ] 【问卷匹配】重试 Job 本期是否同批改造（加终态未匹配标记）—— 评审
- [ ] 【问卷匹配】规则改动影响大班 + 小班全部匹配，回归范围待确认 —— 测试
- [ ] 【AI 配置化】部门 key 口径（PRD 写「虚拟架构部门」；圈选侧用整条路径 contains、归因侧用二级部门 code）—— 评审
- [ ] 【AI 配置化】"不展示"要落到哪些接口 / 字段 —— 产品 + 前端
- [ ] 跨仓承接方：product-server / teacher-tool 是否归本团队 —— 评审

## 涉及的代码

本需求**尚无分支**，主仓当前 checkout 在 `feature-xuban-pre`（属另一需求），下表结论取自 `origin/master`。主仓路径 `/Users/gaotu/IdeaProjects/JavaProject/{student-data,student-center}`；另涉及 product-server / cart / order / reach-service / teacher-tool / clazz-distribution-server。完整 `path:line` 见飞书反讲「详细设计」。

| 子需求 | 仓库 | 关键入口 |
|---|---|---|
| 1 问卷匹配 | product-server（主改） | 绑定层 `QuestionnaireService#match`；记录归属层 `ComputeUserService#compute` + `QuestionnaireRecordService#dealCDSMsg`；兜底 `#dealNotExistedComputeUserId`（取第一个在 `:322-325`） |
| 1 问卷匹配 | student-data | `DwsRenewalQuestionnaireConsumer`（刷花名册字段 + fan-out 明细）；`RenewalQuestionnaireStatusServiceV2#buildData`；调课同步落点 `DwsAfterSaleSyncConsumer` |
| 1 问卷匹配 | teacher-tool | 明细表 `gaotu.user_questionnaire_record`（无续班计划字段）；`UserQuestionnaireRecordDaoImpl#pageQuestionnaireInfoMultiByClazz`；`QuestionnaireServiceImpl#bindUserQuestionnaire`（只改 user 不改 clazz） |
| 2 主讲适配 | student-center | 统计 `SmallRenewalService#queryStatisticStudents:634-638`、搜索 `#searchUser:794-795`、权限 `SmallClazzUserPermissionFilterService:71-84`、班级筛选 `SmallFilterComponentServiceImpl:632/664`（四处 OR） |
| 2 主讲适配 | student-data | ES `ads_small_clazz_user`：`assistantAccountId`(单值) / `mainTeacherAccountIds`(班级级派生) |
| 3 扩科推荐 | product-server | 配置 `ExpandSubjectConfigDTO` / `NodeExtConfigVO`；B 端 `ProcessController#edit/list`、`expandSubject/*` |
| 3 扩科推荐 | student-data | 扩科集合 subtract：大班 `RenewalInfoServiceImpl#groupGradeCurrentRenewalSubjectMap`、小班 `SmallRenewalSubjectService#getRenewalSubjectInfo` |
| 3 扩科推荐 | cart | 推荐 `ExpandSubjectRecommendService#recommend`、选品 `RenewalService#productSelect` |
| 5 AI 配置化 | student-data | 续班 `AiAppSceneEnum`(6) + 归因侧 per-dept 先例；退费 `RefundReasoningEnum`(5) + `RefundPredictionService`(1) |
| 5 AI 配置化 | student-center | 展示 `RenewalClazzUserController` / `RenewalReasonController` / `RefundController`；`RenewalAiCommSceneConfigService`（无 `@ApolloJsonValue`） |
| 4 数据落表（不做） | student-data | 两条既有模式：(a) MQ `job/sync/Sync*Handler`；(b) 直连 Doris Stream Load `DorisStreamLoadService` + `facade/job/dashboard/*DashBoardHandler` |

## 上线影响面

| 子需求 | Apollo | ES | MySQL DDL | MQ | 代课接口权限 | 跨团队 |
|---|---|---|---|---|---|---|
| 问卷匹配 | 是(7 档顺序 + 兜底开关) | 是(调班时重算问卷字段) | 否(teacher-tool 加列才需) | 是(新增消费 TRANSFER_TOUCH_EVENT) | 待定 | product-server / teacher-tool 归属待定 |
| 主讲适配 | 待定 | 待定 | 待定 | 否 | 待定 | 本团队(student-center 主改) |
| 扩科推荐 | 否(配置存 node_config) | 否 | 否(复用 renewal_expand_subject_recommend) | 否 | 待定 | product-server / cart 归属待定 |
| AI 配置化 | 是(部门→模块集合 Map) | 否 | 否 | 否 | 否 | 本团队 |
| 数据落表(不做) | 待定 | 待定 | 待定 | 待定 | 否 | 数仓侧 |

## 必须知道的坑

- 数据落表**不止 MQ 一条路**：student-data 已有直连 Doris Stream Load 先例（`DorisStreamLoadService` + `*DashBoardHandler`）。
- **别把 `TAG_Subclazz_Transfer` 当调课调班**：它是转辅导班（同班换辅导班 / 班主任，班级维度天然覆盖、无需额外处理）；真正的调课调班是 `gaotu_after_sale_event_test` + `TRANSFER_TOUCH_EVENT`。
- "主讲数据"只针对**小班**：大班花名册没有主讲字段（只有 `assistantAccountId`）。
- **主讲口径**：`mainTeacherAccountIds` 是**班级级**字段，主讲（含双角色）看到全班**正是 PRD 要的**；要"只看自己辅导班"的是**班主任**（单值 `assistantAccountId`）。
- `StudentSubclazzQuestionnaire` 是**零引用孤立实体**，不是问卷落库表。
- 跨仓库范围比想象大：product-server、order、cart、reach-service、teacher-tool。
