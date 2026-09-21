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
> 飞书：需求总入口 https://gaotuedu.feishu.cn/wiki/Qox8wFcmHiXBgnkxFBtcd82gnsh → **技术反讲（子需求 1/2/3/5）https://gaotuedu.feishu.cn/wiki/EC45wOefUi0buMkO7O0cipp9nEc** → **待产品确认清单（21 条，可直接转发产品）https://gaotuedu.feishu.cn/docx/L2yrdOPEAoIOMux1JLXcGtR4nde**
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
| 最近更新 | 2026-09-21：**按 `origin/master` 全量核验反讲全部代码位置（4 组并行、约 90 处）**，反讲升 v0.4 订正 8 处（`UnificationSwitchService` 实际在 student-center、subtract :236-238、`refactorMainTeacherStudentInfo` 无角色分支、移除 origin/master 不存在的 `predictLevelReason`、`ProcessController`/`NodeExtConfigVO` 行号偏移、teacher-tool 查询条件、退款口径位置、`DwsRenewalQuestionnaireConsumer` 消费在 :187）；目标/Non-goals 归位；子需求2 统一为「现状 OR 已满足 PRD、本批无需开发」；问卷匹配 MySQL DDL 由否改是；补《发问卷整体技术方案》7 项现状/风险。新建**《待产品确认清单》21 条**（见 [[links]]） |

## 下一步

1. 参与初评：按优先级过 5 个子需求的设计草案（飞书反讲）。
2. 【数据落表】找数仓侧确认落表方式：MQ 推送 / binlog 直拉 / 直连 Doris Stream Load（本仓有先例）。
3. 【扩科推荐】确认跨仓(cart / product-server / order / reach-service)改动承接方；"在读"3 个条件的数据源与口径。
4. 【问卷匹配】确认调课调班同步承接方与旧班 A 的来源。
5. 【AI 配置化】定部门 key 口径与"不展示"落到的接口 / 字段。

## 已定（2026-09-21 产品 / 数据确认）

- ✅ 【下单优化】本期**不做**（快速加购组合商品 P0、续班确认表 P1 均不做）。
- ✅ 【主讲适配】**确认无需开发**（现状 OR 合并已等于 PRD 分角色口径）；统计口径为**实时**（《小班课字段+指标》指标页 6-9 行）。
- ✅ 【问卷匹配】同名 / 一号多孩**不做产品侧解法**，按 PRD 7 档规则实现。
- ✅ 【问卷匹配】「改派（改班级）」**不用做**（王永诗：手工绑定维持现状，只改学员）。
- ✅ 【问卷匹配】「同一手机号多次提交只展示最新」**EES 已有**（teacher-tool `QuestionnaireConsumer#handleRenewalQuestion` 按 userId+clazzNumber+type+questionnairePhone 查旧记录，finishTime 更晚才覆盖）。
- ✅ 【问卷匹配】问卷明细「班级名称 / 班级ID」字段**已有**；teacher-tool **不加**「续班计划」列。
- ✅ 【扩科推荐】【推荐排除】为**新增配置**（不与【纯续和扩科是否重复推荐】合并）；粒度 = **续班计划级**。
- ✅ 【扩科推荐】下单页选品 + B 端 `POST /product-b/b/renewMaster/recommendProductList` + C 端接口**均按「纯续+扩科推荐范围」展示**。
- ✅ 【扩科推荐】「在读」口径：**复用 student-data 现有 + 补 2 条** —— 现有在读科目链路已覆盖 非成人 / 专题系列课 / 不含赠课标签 / 非纯预售（`OdsSmallRenewalSubjectSyncService:189-221`、`DwsRenewalSubjectConsumer#checkFilter`、`BackClazzUserSubjectService#isValidClazz`），相同学年学期靠 `yearTermGrade` 分组、授课模式靠数据源（小班在读科目来自小班课在班）；**但「上课形式为线上(operationMode)」与「订单未全部退款」现有链路没有，需补**（退款状态现网有 {6,10} / {6} 两套，需统一）。
- ✅ 【AI 配置化】配置入口**先用 Apollo 后端配置**（先搞简单点，GAIA 页面后续再议）：续班 / 退费各一个 `Map<虚拟架构部门, Set<模块>>`，如 `{虚拟架构部门A:[1,2,3], 虚拟架构部门B:[1,2,3,4,5]}`；部门 key = **整条部门路径 contains**。
- ✅ 【AI 配置化】「用户反馈」「主管点评」**算 AI 模块**；无需枚举映射；关闭模块后历史数据按**隐藏**处理。
- ✅ 【AI 配置化】「不展示」落点 = 前端仓 `ees/aianalysisinformations`（分支 `feature-refund-reason-20260825`）：沟通建议 `/component/student-center/problem/fulfillProblem/overview`、服务建议 `/component/student-center/fulfillSop/overview`、退费 tab 接口（`src/tabs/refund/*`），入参统一 `{ userId, clazzNumber, subclazzNumber }`。
- ✅ 【AI 配置化】部门→模块配置放 **student-center 的 Apollo**（`compute.rule.name.list` 是问卷匹配的、仍需在 product 公共 namespace `gt.product-public-app` 新增）。
- ✅ 【跨仓承接方】product-server / teacher-tool 的改动**归本团队**。
- ✅ 【问卷匹配】调课调班同步**由 student-data 承接**（扩 `DwsAfterSaleSyncConsumer` 加 `TRANSFER_TOUCH_EVENT` 分支）；旧班 A 来自报文 `LlsTransferCourseMessageDto.originalOrderInfo.clazzNumber`。
- ✅ 【扩科推荐】就是**加个过滤**：**扩科推荐本来就在 cart 算**（`ExpandSubjectRecommendService#recommend`，小班 :32 / 大班 :69，只按年级匹配），这次就在这两个重载里**加一个「排除对方授课模式在读学科」的过滤**。product-server 的 `recommendProductList` 只是把 cart 结果转成 B 端列表，cart 改完自动同步；**student-data 的扩科科目 subtract 只服务花名册「大小班扩课科目」字段，不用动**。

## 待确认

- [ ] 【数据落表】落表方式（MQ / binlog / 直连 Doris）—— 数仓侧（本批不做，仅登记）
- [ ] 【数据落表】"续班 / 退费所有字段"清单，含 GAIA 动态字段如何落表 —— 需 PRD 提供清楚（本批不做）
- [ ] 【主讲适配】小班花名册列表页权限账号字段来自 DB 表 `es_query_config`(type=5)，线上配置未验证 —— 线上确认
- [ ] 【问卷匹配】重试 Job 本期是否同批改造（加终态未匹配标记）—— 即 product-server `QuestionnaireRecordService#dealNotExistedComputeUser`（每轮重跑 3 天内 `computed_user_id=0` 记录，100/批、16 线程），不同批会被反复重跑 —— 评审
- [ ] 【问卷匹配】规则改动影响大班 + 小班全部匹配，回归范围待确认 —— 测试
- [ ] 线上 Apollo 现状核实：`compute.rule.name.list` 是否未配置、共享开关 `all.share.questionnaire.renewal` 实际值 —— 本团队（线上）
- [ ] **产品侧问题汇总见飞书《待产品确认清单》（已全部回填 ✅）** https://gaotuedu.feishu.cn/docx/L2yrdOPEAoIOMux1JLXcGtR4nde

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
| 3 扩科推荐 | student-data | 扩科科目 subtract：大班 `RenewalInfoServiceImpl#groupGradeCurrentRenewalSubjectMap`、小班 `SmallRenewalSubjectService#getRenewalSubjectInfo` —— **仅写花名册「大小班扩课科目」字段，与推荐无关** |
| 3 扩科推荐 | cart | **推荐 `ExpandSubjectRecommendService#recommend`（小班 :32 / 大班 :69，排除过滤加这里）**、选品 `RenewalService#productSelect` |
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
- **续班后置（前置→后置关系）有缓存机制但线上关了**：cart `RenewalDataService#listRenewalMasterByRenewalNumber`（Guava+Redis），开关 `renewal.query.cache.enabled` 代码默认 true、**PROD 实查 = false** → 线上实时调 product-server、无缓存滞后；其余 cart 缓存（clazz/course）线上未配、默认 1800s 开启。
- **在读科目表可能不准，有回溯手段**：表是 MQ + 外部数据拼的（进/退班消息丢失/乱序、课程缓存过期、退款未同步、判定逻辑变更后老数据未重算、`is_del` 不一致）。回溯：**大班** `dws_fuwu_clazz_user_subject` → XXL-Job `BackClazzUserSubjectHandler`（`{"clazzNumbers":[...]}` 或 `{"beginId":..,"endId":..}`）；**小班** `dws_small_clazz_user_subject` → 手动接口 `POST /gps/manual/back/smallClazzUser/subject`、`/back/smallClazz`、`/back/smallRelationLargeClazzUser`、`/back/smallClazzUser`（校验用 `POST /gps/manual/check/smallClazzUser/subject`）。
- **扩科排除：加开关、不新写回溯逻辑** —— 配置本身即 per-计划开关（【无排除】），再加全局 Apollo 降级开关（如在读表脏时一键回退【无排除】）；回溯沿用在读科目表现成 Job/接口，**不内联进推荐链路**（C 端高频、且会重复实现口径）；若要自动只做离线对账。
- **AI 部门匹配有现成先例**：`RenewalAiCommRealTimeSelectHandleService#getDeptAiConfig:214-224` 就是 `departmentPath.contains(configKey)` + `@ApolloJsonValue Map`（部门取课程/班级的 `courseDO.getDepartmentIdPaths().get(0)`）。注意：①"用谁的部门"（班级部门 vs 老师部门）要定，展示侧要同口径；②`contains` 是子串匹配，数字部门 id 会前缀误命中（`1000005` 命中 `10000056`）。
- **在读科目数据来自 student-data 自己的表**（不是查询时调外部）：小班 `dws_small_clazz_user_subject`、大班 `dws_fuwu_clazz_user_subject`，再由 `calRenewalInfo`/`calGradeRenewalInfo` 算出；表的原料是外部（进/退班 MQ `gaotu_subclazz_student_event_test` + 课程中心 + 订单）。→ 「对方模式在读学科」集合可由 student-data 直接透出给 cart。
- **扩科推荐在 cart 算**（`ExpandSubjectRecommendService#recommend`，小班 :32 / 大班 :69，**只按年级匹配**）；`recommendProductList` 只是把 cart 结果转 B 端列表。**cart 没有"在读学科"数据**（全仓无在班/在读查询）→ 加排除过滤的**真正难点是"对方模式在读学科"从哪来**：建议由 student-data 透出（复用 `checkFilter`/`isValidClazz` 的 8 条件口径），cart 只做过滤；否则 cart 要复刻 8 条件、口径会漂移。
