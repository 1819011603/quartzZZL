---
title: 【A-续班-20260902】续班优化
aliases: [续班优化(秋季批), 续班问卷匹配优化, 续班退费AI模块配置化, 续班退费数据落表, 小班续班主讲数据下单优化, 续班扩科推荐优化]
status: 需求评审
owner: zhangzeling
branches:
updated: 2026-09-18
tags: [需求]
---

# 【A-续班-20260902】续班优化

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[changelog|📜 决策摘要]]
> 技术方案在飞书反讲文档里（见 [[links]]），本地不留副本。
> 飞书需求总入口：https://gaotuedu.feishu.cn/wiki/Qox8wFcmHiXBgnkxFBtcd82gnsh （子页面「问卷匹配优化：匹配逻辑现状·改动方案·风险」）
> 续接这个需求：读完本文件即可。

## 一句话

付星/马胜一次性打包转发初评的5个续班优化子需求：问卷匹配优化、退费/续班AI模块配置化、数据落表、主讲数据+下单优化、扩科推荐优化。

## 需求摘要

5个子项，PRD 均 V1.0 / 2026-09-05，优先级按下面顺序：

| 优先级 | 子需求 | 一句话 | 子项P级 |
|---|---|---|---|
| 1 | [问卷匹配优化](#子需求1-问卷匹配优化) | 问卷匹配范围收紧+6级匹配优先级规则+调课调班同步问卷数据 | 匹配逻辑优化 未标 / 调课调班同步 P1 |
| 2 | [主讲数据+下单优化](#子需求2-小班续班主讲数据下单优化) | 续班服务按角色(主讲/班主任)展示数据；快速加购组合商品；续班确认表 | 主讲数据 P0 / 加购组合商品 P0 / 续班确认表 P1 |
| 3 | [扩科推荐优化](#子需求3-续班扩科推荐优化) | 续班计划新增【推荐排除】，避免大小班在读学员被错误推荐已在读学科 | — |
| 4 | [数据落表](#子需求4-续班退费数据落表) | 续班/退费数据落表到大数据支持导数分析 | — |
| 5 | [AI模块配置化](#子需求5-续班退费ai模块配置化) | 续班AI/退费AI按部门配置功能模块开关，降本 | — |

- **给谁用**：主讲、班主任(二讲)；学部运营（数据落表供其导数分析）。
- **判定做完的标准**：5个子需求各自评审通过、反讲、开发、上线，以子需求粒度跟踪（见 [[tasks]]）。
- **明确不做**：所有子需求历史数据均不回溯/不重算（各子需求已定共识里逐条注明）。

## 已定共识

- 5个子需求彼此独立，互不依赖，可并行推进，不要求同批上线（2026-09-17 拆分归档时确认，如需求方另有说明再更正）。
- 问卷匹配优化：问卷匹配范围调整为【问卷+续班计划+班级+辅导老师】，问卷和续班计划必须完全匹配；历史数据不回溯（2026-09-05 PRD）。
- 问卷匹配·调课调班同步：前提是班级A/B绑定同一份续班问卷（不同问卷不共享）；填过问卷则A/B两班明细（2条，按班级信息区分）+花名册都展示，先填后调/先调后填均成立；全程未填则A/B都无数据。备注 P1（2026-09-05 PRD）。
- AI模块配置化：未配置的模块要同时做到"前端不可用+AI不分析"，不是只隐藏前端；续班AI 8个 + 退费AI 6个，共14个模块（2026-09-05 PRD）。
- 数据落表：续班落表覆盖大小班课，退费落表仅大班课（2026-09-05 PRD）。
- 主讲数据+下单：角色数据权限**仅小班适用**——主讲展示主讲数据、班主任展示班主任数据、双角色展示主讲数据；大班花名册没有主讲字段（只有班主任/销售）。小班现状是"主讲 OR 班主任(+岗位标签)"合并可见范围、数据可见范围无角色分支（2026-09-05 PRD / 2026-09-17 代码定位）。
- 主讲数据+下单：快速加购组合商品(P0)、续班确认表(P1) 在 master 全仓**均不存在，属新功能**；续班确认表各项金额口径由电商提供（2026-09-05 PRD / 2026-09-17 代码定位）。
- 扩科推荐优化：【推荐排除】默认空，仅扩科推荐为【是】时可编辑；若需回溯则历史数据按【无排除】处理（PRD 为条件句，当前口径是不回溯）；PRD"在读"8 个条件中 5 个已有现成过滤器可复用，仅"授课模式/上课形式线上/订单未全部退款"3 项需新建（2026-09-05 PRD / 2026-09-17 代码定位）。

## 现在什么情况

| | |
|---|---|
| 阶段 | 需求评审 |
| 进度 | T 5/9（代码定位完成，问卷匹配 4 项开发待办）· R 0/0 · C 0/0 |
| 部署泳道 | 未部署 |
| 当前卡点 | 数据落表需数仓侧先定落表方式（本仓已有直连 Doris 先例，不止 MQ 一条路）；续班确认表金额口径需电商侧确认；扩科"在读"过滤的3个条件需新建过滤器 |
| 最近更新 | 2026-09-18：定位到真正匹配实现在 product-server（规则链+跨班兜底），补 teacher-tool 明细表结论，订正调课调班同步现状；已登记跨班错配分析文档 |

## 下一步

1. 参与初评：按上面优先级顺序过一遍5个子需求的设计草案（各子需求小节里）。
2. 【数据落表】找数仓侧确认落表方式：MQ推送 / binlog直拉 / 直连 Doris(SelectDB) Stream Load（本仓已有先例），这决定要不要开发。
3. 【主讲数据+下单】找电商侧确认续班确认表各项金额口径（PRD 备注"各项金额由电商提供"）。
4. 【扩科推荐】【主讲数据+下单】确认跨仓库(cart/product-server/order/reach-service)改动由哪个团队承接。
5. 产出反讲文档（可能按子需求拆分，也可能合并一份，视TAPD拆story方式而定）。

## 待确认

- [ ] 【数据落表】落表方式：MQ推送 / binlog直拉 / 直连 Doris —— 需数仓侧确认
- [ ] 【数据落表】"续班服务所有字段"/"退费管控所有字段"具体清单，含GAIA动态字段如何落表 —— 等细评
- [ ] 【主讲数据+下单】续班确认表各项金额口径（PRD 备注"各项金额由电商提供"） —— 等电商侧补充
- [ ] 【扩科推荐】"授课模式/上课形式线上/订单未全部退款"3 个条件的在读数据源与口径 —— 等细评
- [ ] 【主讲数据+下单】小班花名册列表页权限的具体账号字段名来自 DB 配置(`EsGaiaMapping`)，代码不可见，是否含主讲字段 —— 未验证
- [ ] 【问卷匹配】调班事件源已存在(topic `gaotu_subclazz_student_event_test` + `TAG_Subclazz_Transfer`，student-data 已消费)，student-center `SyncSubclazzStudentListener` 未订阅该 tag —— 改造方式待定（补订阅 vs 新建）
- [ ] 【问卷匹配】**调课调班同步由谁承接**：product-server 不消费调班事件、`QuestionnaireRecordDao` 无"按 computedUserId+questionnaireNumber 查记录"方法（`page()` 只支持 bizId/recordId/clazzNumbers/questionnaireNumbers）；若由 product-server 承接需新增 consumer + DAO 方法，否则依赖 student-data —— 待评审定
- [ ] 【问卷匹配】**明细 A、B 两行的 fan-out 在 student-data**，不在 product-server/teacher-tool 手上；student-data 不改则"调课同步"做不完整 —— 待确认承接
- [ ] 【问卷匹配】teacher-tool `user_questionnaire_record` **是否加 `renewal_number` 列**：问卷↔续班计划当前 1:1、`project_number` 已隐含计划，建议不加；若评审坚持硬校验则需 DDL 工单 —— 待评审
- [ ] 【问卷匹配】**同名/亲属手机号歧义无解**：链接不带"人"，同名或一号多孩时任何算法只能猜（取 userId 小）；范围扩大到计划级会放大同名歧义面，靠算法无法归零 —— 需产品决策（待认领/改派/一人一链）
- [ ] 【问卷匹配】**重试 Job 放大**：改"不唯一→0"后 `dealNotExistedComputeUser` 会重复重跑同一批未匹配记录（3 天窗口内），需同步加"终态未匹配/重试次数"标记 —— 待细评
- [ ] 【问卷匹配】product-server plan 级姓名规则要扫计划内全部班级学员（班内版已 2000/批 scroll），建议改走 `listByStudentName`(限100)+计划过滤，性能待压测 —— 待细评
- [ ] 【问卷匹配】群发场景（一次几百人提交）压测：MQ 5 线程有序消费 + 每条最坏 11-12 次串行 RPC —— 待测试
- [ ] 【问卷匹配】规则改动影响**所有续班问卷匹配（大班+小班）**，回归范围要覆盖两仓两侧 —— 待测试确认
- [ ] 【AI模块配置化】student-center 那份 `RenewalAiCommSceneConfigService` 无 `@ApolloJsonValue` 部门 Map，需新增；配置粒度(部门整体 vs 细分到年级/学科)、关闭后历史数据隐藏还是保留可查 —— 等细评

## 涉及的代码

以下按子需求列出关键位置。本需求**尚无分支**，两个主仓库当前 checkout 在 `feature-xuban-pre`（属另一需求「膨胀券预报名」），下表结论取自 `origin/master`。分支建好后回填上方 `branches:` 与下表。主仓库路径：`/Users/gaotu/IdeaProjects/JavaProject/student-data`、`.../student-center`；另涉及 `.../product-server`、`.../cart`、`.../order`、`.../reach-service`。

### 子需求1 问卷匹配优化

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| student-data | 未建 | `infrastructure/acl/QuestionnaireAclService`(+Impl) 封装问卷中心调用；`app/service/syncdata/RenewalQuestionnaireStatusServiceV2`(`buildData:73` 写 `renewalQuestionnaireStatus`) 计算花名册字段；**问卷状态刷新共有 4 条路径**，`facade/mq/renewal/RenewalQuestionnaireConsumer`（topic `gaotu_product_renew_master_event_test`，三个 tag 全是续班计划/前置课程变更、无调班）只是其中之一，另有 `DwsRenewalQuestionnaireConsumer`(topic `product-renewal-questionnaire-record-event-test`)、`AdsLessonUserMultipleOrderConsumer`(触达回执 `reachSceneCode=renewal_send_question`)、`SubclazzUserBcpJobTemplate`(定时 basicQuery 重算 + `repairData` 直写 `ads_large_subclazz_user_index`)；`infrastructure/dao/entity/StudentSubclazzQuestionnaire` 是**孤立实体**（字段 userId/clazzNumber/subclazzNumber/teacherNumber/accountId/paperId），全仓零引用、无 Mapper/DDL，**不是实际落库路径** |
| student-center | 未建 | `domain/service/roster/RenewalService#queryQuestionnaireInfo:1925`（调 `questionnaireFeignAdapter.match()`，Redis key `QUESTIONNAIRE_MATCH_KEY + renewalPlanId + ":" + clazzNumber`）是入口**之一**，另一入口 `#questionnaireTitles:566` → `RenewalQuestionnaireAclServiceImpl#queryQuestionnaireMatchResult:67-73`（同调 match，无缓存）；`#getRenewalPlanId:1902`（一班级绑多续班计划直接抛异常）；**多次提交去重在 `#pageQuestionnaire:746`（`:782` 用 `toMap(RenewalQuestionnaire::getUserId,...,(v1,v2)->v1)`）**，不是 `#pageQueryQuestionnaire:889`；`job/mq/consumer/ons/questionnaireListener`（问卷提交，topic `gaotu_questionnaire_add_answer_test`）；`StudentQuestionnaireBehaviorListener`（问卷完成，topic `teacher_tool_questionnaire_finish_test`） |
| **product-server**（=Feign 的 `product-b`，真正匹配实现） | 未建 | ①**绑定层** `domain/service/renewal/questionnaire/QuestionnaireService#match:928`：按 `clazzNumber→courseNumber` + `renewalNumber` 查 `renew_master_course_relation` 取 `questionnaireNumber`，返回 bizId+name（`matchResult:962` 无 project 名，student-data 侧用这个）。②**记录归属层** `QuestionnaireRecordService#dealCDSMsg:145`：`ComputeUserService#compute:21` 按 Apollo `compute.rule.name.list`（默认 `[originUserRuleService,mobileRuleService,nameRuleService,relationIdService]`）顺序跑规则，**全部限定在链接绑定班级内**：`OriginUserRuleService`(CDS userId∈班级学员)、`MobileRuleService`(报名手机号∈班级)、`NameRuleService`(姓名∈班级，同名取 userId 小)、`RelationIdService`(亲属手机号∈班级，取 userId 小)。③**跨班兜底** `QuestionnaireRecordService#dealNotExistedComputeUserId:253`：把 originUserId/手机号反查(`.get(0)`)/亲属ID/姓名模糊查询(limit 20) 混成一个 userId 集合 → 查这些人在问卷前置课下的小班 → 按 `assistantNumber.accountId == bindData.accountId` 选班，**选不到就 `subclazzDTOS.get(0)` 取第一个**(:322-325)；开关 `across.clazz.questionnaire.submit.switch:122`。这正是飞书那篇「跨班错配」文档描述的根因。④问卷记录经 MQ `product-renewal-questionnaire-record-event-test` 发出 |
| **teacher-tool** | `feature-xuban-multi-clazz` | 问卷明细存储 `user_questionnaire_record`（字段 `questionnaire_id/type/user_id/clazz_number/project_number/account_id/questionnaire_group_id`，**无续班计划字段**）；查询 `UserQuestionnaireRecordDaoImpl#pageQuestionnaireInfoMultiByClazz:147` → `UserQuestionnaireRecordMapper.xml#queryRecordsMultiByClazz:114`，SQL 过滤维度 = `type + project_number(问卷bizId) + clazz_number + user_id`（「问卷+班级」硬校验，「辅导老师」由 student-center 传本人带班 userId 范围实现，**无续班计划条件**）；`QuestionnaireServiceImpl#bindUserQuestionnaire:232`/`manualQuestionnaireRecordUser`(product-server) 手工绑定**只能改 user、不能改 clazz** |

**设计草案**：匹配范围收紧 = 在 product-server 记录归属层把「续班计划」变成硬约束、并把 `dealNotExistedComputeUserId` 的"混候选取第一个"替换成 PRD 的**确定性 6 级优先级**（现状 4 条规则全部"班级内"，新规则每条再拆"同班级/同续班计划"两级：(1)(2)手机号、(3)(4)姓名、(5)(6)亲属手机号，最高优仍是 CDS userId=班级学员 userId）。`ComputeUserService` 的 Apollo 规则链天然支持插拔，可新增 plan 级规则或给规则加 scope 参数。绑定层 `QuestionnaireService#match` 已按 renewalNumber 过滤，无需大改。调课调班同步**不需要新建事件**：调班事件源已存在（topic `gaotu_subclazz_student_event_test` + `TAG_Subclazz_Transfer`），student-data `SubclazzUserSyncConsumer:116` 已在消费但只刷 `renewalStateStatus/renewalSubject/renewalExpansionSubject`（`transferInsertFieldNames:82`），**未刷问卷字段**；student-center `SyncSubclazzStudentListener` 只订阅 Enter/Quit、未订阅 Transfer。要做的是：调班后对旧班(A)+新班(B)分别重算/回写续班问卷字段（ES `renewalQuestionnaireStatus`/`renewalQuestionnaireSubmitTime`），并让 teacher-tool 明细在 A、B 各出一行（现有 `DwsRenewalQuestionnaireConsumer#sendTeacherToolQuestionMsg:544` 已按 share clazz 拆多行+mock uniqueBizId 去重，可复用）。注意A/B必须绑定同一问卷才共享。
**可 0 开发止血**：`across.clazz.questionnaire.submit.switch:false` 即可停用"取第一个"兜底，提交落 `computedUserId=0` 的未匹配记录（`clazzNumber` 仍是链接班，明细可按 `queryNotMatched` 展示并手工绑定）——即需求"收紧范围"的最小可用形态。
**多班 fan-out 已存在**：`getShareCourseNumbers:513` 只取同一 `renewMasterNumber` 下的 preCourseNumbers，下游按 `shareCourseNumbers`+`queryShareSubclazzList` 刷所有同计划同问卷班级的状态/花名册，所以"同计划多班都匹配"的下游链路基本现成，主要缺口在"匹配到谁"与调班后旧班(A)的回写。

**改动清单（2026-09-18 确认 product-server + teacher-tool 归我）**：

*product-server（主改动，P0）*
1. `model/ComputeParams` 加 `renewalNumber` + `planCourseNumbers`（计划内同问卷前置课程）。
2. `QuestionnaireRecordService#dealCDSMsg:145`：**把 questionnaire→processConfig→renewalNumber、renewMasterCourseRelation→preCourseNumbers 的解析前移到 `compute` 之前**（现解析在 :171-177，compute 在 :164），再 set 进 computeParams；`dealCDSMsgList:599` 批量组装处同样补。
3. 新增 3 条 plan 级规则（手机号/姓名/亲属手机号），查范围用 `ClazzDistributionFeignService#listSubclazzStudentByCourseNumbersAndUserId(planCourseNumbers, userId)`（已存在）；**建议抽 `AbstractUserRuleService`**，现有 3 条班内规则与 3 条 plan 级规则只差"查范围"，避免 6 个重复类。
4. `ComputeUserService` Apollo `compute.rule.name.list` 默认值改 6 级顺序（规则是"命中即从待算集合移除"，顺序即优先级，天然满足 PRD）。
5. **兜底 `dealNotExistedComputeUserId` 的 `subclazzDTOS.get(0)` 必须去掉**：6 级规则覆盖跨班后，改"不唯一→不置人(computedUserId=0)"或直接删除该方法；`dealCDSMsg:165` + `dealCDSMsgList:631` 两个调用点同步。
6. `dealNotExistedQuestionBindNumber:378` 无绑定号路径：把跨 `bizId` 的 preCourseNumbers 收敛到该问卷所属续班计划（满足"续班计划完全匹配"）。
7. 明细 A/B 两行的 fan-out 在 student-data，product-server 不改结构（保证 `computedUserId` 正确 + `shareCourseNumbers` 全计划即可）。

*teacher-tool（次改动，按评审结论定）*
1. **是否加 `renewal_number` 列**：问卷↔续班计划当前 1:1、`project_number` 已隐含计划，**建议不加列**（加则要 DDL + model + MQ DTO 透传 + `QuestionnaireConsumer` 写入）。
2. **改派（跨班改）能力**（需求缺口，建议本期补）：`QuestionnaireServiceImpl#bindUserQuestionnaire:232` 只改 `user_id`，加改 `clazz_number` 并同步同 `questionnaire_group_id` 的其余行；`UserQuestionnaireRecordDaoImpl` 加 update。
3. 明细查询 `queryRecordsMultiByClazz` 已有 `queryNotMatched`，未匹配可查可绑，无需改；A/B 两行只依赖 student-data 发来 B 的行。

**调课调班同步的归属待定**：product-server **不消费**调班事件（已核实），`QuestionnaireRecordDao` 也没有"按 computedUserId+questionnaireNumber 查记录"的方法（`page()` 只支持 bizId/recordId/clazzNumbers/questionnaireNumbers）。若由 product-server 承接需新增 consumer + DAO 方法；**建议放 student-data**（它已消费 `TAG_Subclazz_Transfer`）。详见待确认。

**性能评估（2026-09-18，需压测验证）**：

- **最高风险：重试 Job 被未匹配记录淹没**。`dealNotExistedComputeUser:534`（XXL-Job `QuestionnaireRecordComputeHandler`）每轮捞 `computedUserId=0` 且 3 天内的记录，按 100/批、16 线程**重跑整条规则链**。现在这些记录被兜底强行匹配掉；改成"不唯一→0"后它们**永远匹配不上**（歧义是确定性的），每轮重复处理同一批直到 3 天过期，且规则链从 4 条→7 条（单条成本 ×1.75）。→ **必须同步改造重试策略**（加"已重试/终态未匹配"标记跳过，或限次数/缩短窗口），否则稳定负载和下游 RPC 量显著上升。
- **每条提交 RPC 数上升且串行**。`compute` 是顺序 for + "命中即移除"：正常（手机号命中）只跑 1-2 条；最坏（全不中）现状约 7-8 次 RPC，加 3 条 plan 级后约 11-12 次。`QuestionnaireRecordConsumer` 仅 5 线程有序消费，**群发场景（一次几百人同时提交）会排队**。→ 高命中率规则放前；plan 级规则用 Apollo 单独开关；压测群发 500 并发。
- **plan 级姓名规则最贵**。班内 `NameRuleService` 是"scroll 班级学员(2000/批) + `listByUserIds`(最多 2000)"，本就重（且现实现命中失败即 return，实际只扫首页 2000，是既有正确性缺陷，别照抄）。plan 级若按班遍历 → N 班 × 重查询。→ 改用 `userAclService.listByStudentName`（限 100）先拿候选 userId，再按计划课程过滤；或设上限/降级。
- **不贵的部分**：绑定层 `match` 不变；teacher-tool 查询不变；plan 级手机号/亲属号用 `listSubclazzStudentByCourseNumbersAndUserId`（500/批，计划课程数通常 <500 = 1 次/候选人），候选集小，成本可控。
- **兜底开关是天然灰度**：`compute.rule.name.list` 在 Apollo，可单独开关/重排任一条规则，性能劣化时无需发版即可降级。

### 子需求2 小班续班主讲数据+下单优化

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| student-center | 未建 | `domain/service/small/SmallFilterComponentServiceImpl#buildOneSelfQuery:623`（主讲 nested OR 班主任 nested）；`#buildAllQuery:636`（**三重 OR**：主讲 nested OR 班主任 nested OR 岗位标签 `mainTeacherPostTag`/`assistantPostTag` wildcard）；`domain/service/roster/small/SmallRenewalService#statistic:618`→私有 `queryStatisticStudents:634`（`:637-638` should 合并 `assistantAccountId`/`mainTeacherAccountIds`）、`#searchUser:783`（`:794-795` 同）；`domain/service/roster/RosterService#getMyUserIds:55`（**老版大班**花名册，仅 `assistantAccountId`，纯班主任视角）；小班花名册列表页权限走 `SmallClazzUserPermissionFilterService#build:47-110`（字段名来自 DB 配置，**代码不可见**） |
| student-data | 未建 | ES 宽表 `domain/smallclazz/model/WideSmallClazzEsModel`：`mainTeacherList`(:42，内部类 `MainTeacher`:248) 由 **`WideSmallClazzTeachingBinder#bindTeaching`:87/:129** 绑定；`assistantList`(:45，内部类 `Assistant`:219) 由 `WideSmallClazzSubClazzBinder`:171/:195 绑定（**两者不是同一个 Binder**）；MySQL 落库层 `infrastructure/dao/entity/DwsFuwuUserClazz` 只有 `assistant_account_id`、无主讲字段 |
| order（加购写操作） | 未建 | 快速加购组合商品的写购物车落点：`order-controller/.../controller/cart/CartController`(`/b/cart/addCart`) → `order-app/.../app/cart/CartService#addCart:150` → `CombinedProductCartHelper`；加购后 `BCartPublishListener`(topic `order_b_cart_event_test`) 被 student-data `CartEventConsumer` 消费 |
| product-server（商品范围查询） | 未建 | 组合商品范围查询（学年/学期/部门/年级/科目 + `upStatus` 非未上架）：`ProductEsDao:181-220`、`IProductService#combineProductSpuSearchFromEs`、内部 Feign 出口 `CombinedProductFeignController#searchNoAuth`(`POST /feign/combinedProduct/searchSpuNoAuth`) |
| 已有但非适配器 | 未建 | student-data `app/service/CartEventService`（**含真实业务逻辑**，不是 Feign ACL）：`processCartEvent:79` 查购物车→算 `renewalShopSubject`→写 ES；`queryCartSubjects:124/151`、`resolveCombineProductClazzNumbers:241`。真正的 ACL 适配器只有 `OrderBCartAdapter`、`CartTokenAdapter`、`OrderPromotionAdapter`(×2) |

**设计草案**：改造方向是权限判断处先查登录人在该班级上的角色（`mainTeacherList`/`assistantList`），再决定返回主讲维度还是班主任维度指标，而非简单 should 合并。新增指标字段的计算应加在 `DataQueryServiceV2` 实现（如 `SmallClazzUserRenewalSubjectQueryService#buildData`）并同步 Apollo `ads.sync.small.clazz.user.insert/update.fieldNames`——`AdsSmallClazzUserOrderedService` 只是 ES 写入器(`docAsUpsert`)、`DwsSmallClazzUserService` 只是字段筛选转发器，**都不是计算处**；`SmallRenewalService` 侧聚合分支在 `queryStatisticStudents:634` + `calculateSmallRenewalStat:710`。快速加购组合商品(P0) 是新功能：范围查询落 product-server、加购写购物车落 order。续班确认表(P1) 改动面：student-center `domain/service/contentReport/`（新增 `ContentReportType` 值 + 新 Strategy，复用 `PersonalReport` 的截图/导出/触达骨架）+ 导出中心(`ContentProductExportSerivce#generateResultFileDO:120` 压缩包) + 触达(`ReachPortalController#mixCreate`、`ReachMixCreateBiz`；真正微信助手群发在 **reach-service** `ReportContentHandler`)；student-data 侧无对应实现。

### 子需求3 续班扩科推荐优化

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| product-server | 未建 | `com.gaotu.clientv4.renwal.dto.ExpandSubjectConfigDTO`（包名 renwal 拼写如此；字段 `expandSubject`/`forceBuy`/`allowDuplicate`/`beginTime`/`endTime`/`recommendList`），本次新增【推荐排除】枚举字段最可能落在这里 |
| student-center | 未建 | `student-center-adapter/.../acl/RenewalMasterAclService#getExpandSubjectConfig:35`（Impl:62，Redis 缓存）；`web/.../RenewalContentConfigController#getConfig:62`（`:89` 返回 `expandSubjectEnabled`）；推荐链接：**大班+小班都在 `domain/service/roster/content/RenewalRecommendStrategy`**（大班 `:37`，小班 `#buildSmallClazzPureRenewalUrls:150`，入口 `:85`）——`SmallRenewalService`/`SmallRenewalController` 是小班**花名册/统计/校验**，与推荐链接无关；短链转发至 `student-center-adapter/.../acl/adapter/PromotionRecommendLinkAdapter`（Feign `PROMOTION-B.GAOTU100.COM`） |
| student-data | 未建 | 年级匹配核心：大班 `domain/service/impl/RenewalInfoServiceImpl#calGradeRenewalInfo:82/:103`、`#groupGradeCurrentRenewalSubjectMap:167`；小班 `domain/small/SmallRenewalSubjectService#calRenewalInfo:61/:79`、内部 `#calRenewalSubjectInfo:245`。在读查询可复用 `infrastructure/acl/SubclazzStudentBizFeignService#listSubclazzStudentsByUserIds:76`；业务类型 `client/acl/model/CourseDO#bizType`（1中小学/2成人） |
| cart（C端/B端推荐与选品） | 未建 | C端报名页推荐商品：`cart-controller/.../RenewalController`(`web/renewal/`) → `cart-app/.../renewal/RenewalService#getRenewalDetail:217`（扩科商品 `ExpandSubjectRecommendService#recommend`、去重 `RecommendMergeService#merge`）；下单页选品过滤：`RenewalService#productSelect:2573`/`#productList`。product-server 的 `recommendClazzList`/`recommendProductList` 是 **B端(/b/)** |

**设计草案**：【推荐排除】枚举加在 `ExpandSubjectConfigDTO`（product-server 侧，跨仓库改动）。过滤逻辑加在 student-data 的 `RenewalInfoServiceImpl#groupGradeCurrentRenewalSubjectMap`/`SmallRenewalSubjectService#calRenewalSubjectInfo` 计算续班/扩科科目集合处。PRD"在读"8 条件中，非成人/专题课系列课/不含赠课等标签/非纯预售**已有现成过滤器可复用**（`DwsRenewalSubjectConsumer#checkFilter`、`BackClazzUserSubjectService#isValidClazz`），"相同学年+学期"由 `RenewalInfoServiceImpl#queryYearTermGradeKey` 分组 key 实现；**仅"授课模式、上课形式线上、订单未全部退款"3 项需新建**（可仿 `CommonRuleFilter` 风格）。C端/B端推荐与选品过滤在 cart，需一并适配。

### 子需求4 续班退费数据落表

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| student-data | 未建 | **推数仓有两条既有模式**：**(a) MQ 推送**——`student-data-dws` 模块 `job/sync/Sync*Handler.java` 系列（`SyncRenewalLiftResultHandler`、`SyncRefundResultHandler` 等）：定时扫 MySQL(按 update_time)→加工→发 MQ，下游数仓订阅落 ODS/DWS；**(b) 直连 Doris(SelectDB) Stream Load 直写**——`infrastructure/dao/service/impl/DorisStreamLoadService`(+`DorisStreamInfoLoadService`/`DorisStreamLoadGenericService`)，调用方 `facade/job/dashboard/{RenewalDashBoardHandler,RefundDashBoardHandler,RefundInfoDashBoardHandler}`，写库 `student_data_renewal`。**无 Hive/ODPS 直写先例**（Hive 只作上游同步源出现在注释里） |
| student-center | 未建 | 未发现直连数仓写表代码；历史 commit `b84a09cbf feat: 落表`（`StudentLearnRecordServiceImpl`）模式是 **Kafka 消费上游(`StudentLearnDetailConsumer`, topic `gaotu_play_record_merge_test`) → 落自己 MySQL 表(`student_learn_record`) → 发 ONS/RocketMQ(`OnsMqProducer`, topic `student_data_learn_record_test`)**，Kafka 是入口不是出口 |

**设计草案**：续班数据模型是 ES 索引 `ads_large_subclazz_user_index`（大班）+ `ads_small_clazz_user`（小班），字段分散在约 170+ 个 `DataQueryServiceV2` 实现（student-data 171 个、student-center 约 100 个），是宽表+GAIA动态字段体系。退费数据模型是 student-center 16 个 `Refund*VO` + `RefundService`，加 student-data 侧 `ai_refund_*`(6 张) 及 `RefundApply`(`gaotu.refund_apply`)/`RefundIntentInfo`/`SubclazzRefundProcessSnapshot`。落表可走 (a) 或 (b) 任一既有模式，**但要先经数仓侧确认协议（topic/schema 或 Doris 表结构），这是最优先要确认的问题**。

### 子需求5 续班退费AI模块配置化

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| student-data | 未建 | 续班AI：`app/service/syncdata/ai/renewal/`（`RenewalAiCommSceneConfigService`、`RenewalReasonQueryService`、`RenewalReasonTaskService`）、`domain/renewal/reasoning/impl/`（`RenewalUnrenewedReasonServiceImpl`/`RenewalRenewedReasonServiceImpl`）、`app/service/enums/ai/AiAppSceneEnum`（1用户画像/2沟通摘要/3沟通建议评分/4服务建议评分/5未续跟进/6已续总结）；退费AI：`domain/refundless/`（`reasoning/impl/RefundReasonServiceImpl`、`predict/RefundPredictionService`、`reasoning/impl/RefundExperienceServiceImpl`、`RefundUserNpsServiceImpl`）、`facade/job/refundless/RefundAnalysisHandler`（`@JobHandler("refundAnalysisHandler")` XXL-Job） |
| student-center | 未建 | 续班AI展示：`web/api/ai/RenewalClazzUserController`、`RenewalReasonController`、`UserFeedbackController`、`domain/service/ai/impl/AiClazzUserPortraitServiceImpl`，落表 `ai_app_clazz_user_*`；退费AI展示：`web/api/RefundController`、`AiRefundAnalysisController`、`domain/service/impl/AiRefundAnalysisServiceImpl`。**可参考的部门级配置模式**：student-data 的 `RenewalAiCommSceneConfigService:72-73` 用 `@ApolloJsonValue("${renewal.ai.select.dept.config:{}}") Map<部门code, RenewalAiCommSceneConfig>`；**student-center 同名类(:22)没有 `@ApolloJsonValue`**（只有 `@Value` 的 List/Boolean）。`UnificationSwitchService` 是"总开关+模块开关"两级（非按部门） |

**设计草案**：新增 Apollo 配置 `Map<部门code, Set<模块枚举>>`（`@ApolloJsonValue`），扩展 `AiAppSceneEnum` 思路，给续班AI、退费AI各自模块建枚举。"部门"取"课程所在的主数据部门"code（字符串数字，如 `10012667`）；**查中文名实际走 `MedusaSyncAclService#getDepartmentPathNameByNumber`（student-data-client，调用点两仓 `ComprehensiveDepartmentFilter:56`），不是 `TeachDepartmentAclService`（那个用于 GPS 组 `departmentIds`→名称）**。生效点两处都要改：student-data 分析侧（未配置模块不跑分析，省成本）+ student-center 展示侧（未配置模块前端不可见/接口拒绝）。

## 上线影响面

| 子需求 | Apollo | ES | MySQL DDL | MQ | 代课接口权限 |
|---|---|---|---|---|---|
| 问卷匹配优化 | 待定(可能新增 plan 级规则开关) | 是(花名册续班问卷字段需在调班时重算) | 否(teacher-tool 表无续班计划字段，若硬约束需加列) | 否(调班事件已存在且 student-data 已消费，需扩 `transferInsertFieldNames` 重算问卷字段) | 待定 |
| 主讲数据+下单优化 | 待定 | 待定(统计指标字段) | 待定 | 待定 | 待定 |
| 扩科推荐优化 | 否(预计) | 待定 | 待定(product-server 侧续班计划新增【推荐排除】字段) | 否 | 待定 |
| 数据落表 | 待定 | 待定 | 待定 | 待定(走MQ新增；走Doris直写则无) | 否 |
| AI模块配置化 | 是(预计，部门→模块开关Map) | 待定 | 待定 | 否 | 否 |

## 必须知道的坑

- 数据落表**不是只有 MQ 一条路**：student-data 已有直连 Doris(SelectDB) Stream Load 直写先例（`DorisStreamLoadService` + `*DashBoardHandler`），别默认"只能发 MQ"。
- 跨仓库范围比想象大：除 student-data/student-center 外，还有 **product-server**(扩科配置+组合商品范围查询)、**order**(B端加购写购物车)、**cart**(C端推荐商品+选品过滤)、**reach-service**(微信助手群发)。
- "主讲数据"只针对**小班**：大班花名册没有主讲字段（只有 `assistantAccountId` 或 `assistantAccountId OR salesAccountId`），改权限别按两仓对称去估。
- 调班事件**已存在**（`gaotu_subclazz_student_event_test` + `TAG_Subclazz_Transfer`，student-data 已在消费），student-center 只是 `SyncSubclazzStudentListener` 没订阅该 tag——不要当成要新建事件。
- 快速加购组合商品、续班确认表是**全新功能**，在现有代码里找不到"要改的地方"；续班确认表照抄 `ContentReportType.PERSONAL_REPORT`（阶段汇总报告）那套骨架。
- `StudentSubclazzQuestionnaire` 是**零引用孤立实体**，别当它是问卷落库表去改。
