---
title: 【A-续班-20260902】续班优化 · 任务板
tags: [需求, 任务]
---

# 当前任务板

## 排期（2026-10-12 更新 · 王永诗按业务节点分两批）

| 批次 | 内容 | 评审 / 反讲 | 整体联调 | 提测 | 上线 |
|---|---|---|---|---|---|
| 第一批 | 问卷匹配优化（product-server + teacher-tool）、小班主讲数据（**无需开发**）、TT字段（独立需求） | — | — | — | **10-13** |
| 第二批 | 扩科【推荐排除】、AI 模块配置化 | 09-18 / 09-22 | **10-20** | **10-22** | **10-27** |
| 本批新增 | 下单优化（快速加购组合商品；续班确认表仍不做） | — | — | — | — |

原「一起上线」排期作废。「AI 模块配置化」本无业务节点，2026-10-12 随第二批并到同一节点（评审 09-18 / 反讲 09-22 / 联调 10-20 / 提测 10-22 / 上线 10-27）。

**TAPD 迭代「【A-续班-20260902】续班优化」（id `1122531521001014934`）已按此对齐**：第二批各 story 的「自测 = 10-19、联调 = 10-20 ~ 10-22（提测日有线）」，开发任务收口到 10-16；快速加购组合商品已由用户于 2026-10-21 纳入本批，历史排期和 TAPD 任务需按当前范围复核。TT字段（途途APP）是单独的小需求，跟踪文件是 [[TT字段-途途APP活跃时间]]（纯配置，测试环境已验证，线上待配）。

## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 代码定位：问卷匹配优化 | 已完成 | — | 结论见 README 子需求1 |
| T-02 | 代码定位：主讲数据+下单优化 | 已完成 | — | 结论见 README 子需求2 |
| T-03 | 代码定位：扩科推荐优化 | 已完成 | — | 结论见 README 子需求3 |
| T-04 | 代码定位：数据落表 | 已完成 | — | 结论见 README 子需求4；需数仓侧确认落表方式才能继续 |
| T-05 | 代码定位：AI模块配置化 | 已完成 | — | 结论见 README 子需求5 |
| T-06 | 【问卷匹配】product-server 改动（ComputeParams 扩字段/解析前移、3 条 plan 级规则、Apollo 7 档顺序） | 已完成 | — | 已部署 `test-gtbg-dev-3`，7 档逻辑反射实测 6 例全过（见 [[verify]]）；无绑定号收敛本批不做。**2026-10-08 用户定：跨班兜底恢复 master 原样 `get(0)`**（`92f1a5234`，dev-3 复测 N1 userId 跨班 → 归属本人 B 班），原「去兜底」作废 |
| T-07 | 【问卷匹配】重试 Job `dealNotExistedComputeUser` 加「重试次数」标记 | 已完成 | — | `questionnaire_record.retry_count`（TEST DDL 已加）+ `no.compute.user.max.retry.count:3`；未归属记录累加、达阈值不再重试。2026-09-24 E2E：连跑 4 次 0→1→2→3 后不再选中（见 [[verify]]「T-07」）；2026-09-24 修正重试条件 `manual_user_id != 0` → `= 0`（`f549f4070`），dev-3 E2E 通过 |
| T-08 | 【问卷匹配】teacher-tool 明细改动 | 已完成 | — | 不加续班计划列；改派不做。改为**新增调课调班消费者**（见 T-09） |
| T-09 | 【问卷匹配】调课调班同步（明细 + 花名册状态） | 已完成 | — | v2 单一入口 + 3 轮对抗复审（不可靠重试判断、teacher-tool 重复复制、原班无问卷短路+null 兼容），均已 E2E 验证，见 [[verify]]「先填后调缺陷修复」+「第三轮」 |
| T-10 | 【扩科推荐】新增【推荐排除】：product-server 配置 + student-data 计算侧过滤 + cart 推荐适配 | 已完成 | — | 分支 `feature-xuban-expand-exclude`。B/C 端真实入口 E2E 已验证；修掉 cart fastjson SnakeCase 致 Feign 恒空的真 bug（`96e334b8`）。**2026-10-12：老计划 `excludeMode` 为空 → B 端回显兜底 `0`（兼容、不刷数，product-server `2d8ae7ccb`）**。**2026-10-14：补「在读」学年+学期过滤（PRD 明确「与当前课程相同学年+学期」，原实现漏了 → 会过度排除）；cart 透出当前课程学年/学期、student-data 按学年学期过滤（小班表 OES→CES 转换，缺失/复合学期保守不排除）**（student-data `f1817c92d` / cart `7794a329`）。详见 [[verify]]「第二批」 |

| T-11 | 【AI 配置化】部门→模块开关（Apollo，不接 GAIA）：student-data 配置+匹配服务+分析侧（续班5/6、退费5、续班1/2/3圈选实时+历史）+ feign 透出；student-center 展示侧 | 已完成 | — | 分支 `feature-xuban-expand-exclude`（student-data + student-center，均已 push：`c91d5cd66`/`7b9215766`，口径修正 `12e41da47`/`84ec1b732`）。**口径**：部门 = 老师（二讲）虚拟组织架构主岗路径，按 `_` 分段精确命中；模块 code 续班 `1-8`、退费 `tutoring/learning/satisfaction/refund_root_cause/service_suggestion/prediction`；**灰度语义（`24be1d776`/`a3a4d7cb5`）：未配置=全量放开，配置后只放开命中部门；展示侧不可判定（无登录态/查询异常/结果缺该模块）一律 fail-open**。配置 key `renewal.ai.dept.module.switch` / `refund.ai.dept.module.switch`；feign `POST /feign/ai/module/switch/query`。2026-09-29 dev-1 补验通过：① arthas 无 web 上下文直调 → `true`（fail-open）；② 真实 HTTP 入口（登录态 177071）配不匹配部门（两个不同值）→ `data:{}`（拦截生效，未被 fail-open 误放行）；③ 配 177071 真实部门 `6816343048455168` → 返回完整数据（正对照）；验证完 Apollo 已改回原值 `{"97349606689168923":[1..8]}` 并读回确认 |

| T-12 | 【AI 配置化】前端对齐：新增模块开关表接口 `POST ai/moduleSwitch`（14 key）+ 各数据接口兜底（evaluateQuery 7 / managerEvaluate 写 8 / analysis→service_suggestion 返空对象 / refund edit→manual_reason / reason/detail 5/6）+ 枚举补 code `9`/`manual_reason` | 已完成 | — | 分支 `feature-xuban-expand-exclude`（student-center `7d74dbf8f` / student-data `6ae6bc798`，均已 push、部署 `test-gtbg-dev-1` eureka UP）。与前端反讲《续班优化 202609-前端反讲》定稿一致。单测 student-center 5 条全过。**挂起**：`ai/clazzUser/predictLevelReason`（续班 9 / 退费 prediction）门控——该接口在 `feature-predict-level-reason`，待其上线、需求5 合流后补。详见 [[verify]]「AI 模块开关表接口」 |

| T-13 | 【AI 配置化】退费根因（`refund_root_cause`）——**定：不替换、不下线，纳入 AI 模块化配置** | 已完成 | — | **2026-10-21 用户定**：放弃「替换成意向预测 / 加 Apollo 开关下线」方案，**功能保持不变**，把 `refund_root_cause`（连同 `satisfaction`）配成可配置 AI 模块、加入开关表下发名单。**后端已改并 push（student-center `2bac261cc`，`AiModuleSwitchQueryService.REFUND_MODULE_CODES` 5→7 项；单测 `AiModuleSwitchQueryServiceTest` 5/5 过）**。前端分支 `feature-renewal-20260922` 会展示（`REFUND_CODE.ROOT_CAUSE='refund_root_cause'`）。**（原 2026-10-20「加 Apollo 开关控制下线」方案作废）**。**2026-10-21 追加：展示接口 `/roster/refund/reasonType` 曾被 `497479d3b` 当死代码删除（连带 `5c1465e57` 删残留），与「不下线」冲突致 404 → 已 `git revert 497479d3b` 恢复并补回残留（student-center `9cd9c9f88`，已 push、编译通过；青舟流水线 1307906 → dev-1 SUCCESS，接口读回 HTTP 200 空态、**404 消除**）**。PROD 后端分析侧仍在跑（2026-10-19 日志 `currentTaskEnum=REFUND_ROOT_CAUSE`、`handleCode=2`）。 |

## R- 反讲整改项

| 编号 | 整改项 | 状态 | 谁提的 | 备注 |
|---|---|---|---|---|
| R-01 | 反讲按 `origin/master` 全量核验代码位置（4 组并行 ~90 处），订正 8 处并升 v0.4 | 已完成 | 我 | 见反讲「变更历史 v0.4」 |
| R-02 | 反讲：目标/Non-goals 归位、子需求2 口径统一（无需开发）、问卷匹配 DDL 否→是、移除不存在的 `predictLevelReason`、补《发问卷整体技术方案》7 项现状/风险 | 已完成 | 我 | 同上 |
| R-03 | 新建《待产品确认清单》21 条（按 5 子需求分组，可直接转发产品） | 已完成 | 用户 | https://gaotuedu.feishu.cn/docx/L2yrdOPEAoIOMux1JLXcGtR4nde |
| R-04 | 线上核实 Apollo：`compute.rule.name.list`、`all.share.questionnaire.renewal` | 已完成 | 我 | appId `course-setting`；PROD/TEST 均**未配置**（走代码默认：4 规则 / `all.share=true`）；`share.questionnaire.renewal.numbers` PROD 有 2 个号、TEST=`[]`（明细见 [[changelog]]） |

## C- case 联调问题

| 编号 | 问题 | 状态 | 对应 case | 备注 |
|---|---|---|---|---|
| C-01 | **【扩科排除】cart 取「当前课程」学年学期取错（与 PRD 不符）——已确认改为取「前置课」** | 已完成 | CASE-001 | PRD：当前课程=续班花名册选择的班级（**前置课**）；原 cart 按**后置课**学期过滤（前置=C/春、后置=X/夏 → 用 X）。**2026-10-20 已改**（cart `4724b384`，分支 feature-xuban-expand-exclude）：`RenewalService` 新增 `resolveCurrentPreCourse`（取 `renewalPreCourseDTO.getCourseNumbers()`→`recommendContext.getCourseDTO` 的前置课学年+学期）传入 `ExpandSubjectRecommendService`；后置课仍用于年级匹配。已部署 `test-gtbg-dev-1`（eureka UP）并验证：数学在读=春 → **数学被排除** ✅、excludeMode=0 → 数学恢复 ✅。详情见 [[verify]]。 |

## 阻塞详情

### T-04（数据落表子需求，非阻塞当前任务板项，仅提示后续开发前置条件）
- **卡在**：落表方式未定（MQ推送 or 数仓侧binlog直拉）
- **需要谁**：数仓侧
- **可以先做**：其他4个子需求的评审和设计可并行推进，不受此阻塞

## Q- 代码规范审查待办（2026-10-12 · 按「开发防返工检查」审 5 仓 diff）

> **2026-10-14 追加（对照 PRD 逐条核 diff）**：修复 3 项已闭环 —— ①【扩科】在读补「与当前课程相同学年+学期」（真缺陷，见 T-10）；②【AI】`/roster/refund/reason` 按 `manual_reason` 门控（漏网）；③【AI】分析侧灰度未开始时短路部门解析（性能）。另清理 `.run` 误提交文件、订正 2 处注释/Javadoc。**仍待确认**：Q-03（`refund_root_cause` 门控 `/reasonType` 但不下发 → 灰度后恒空）、`levelReasonAndHistory` 是否门控（属另一需求）、`RefundPredictionService` 通知门控是否算写侧、复合学期课程在读匹配降级为不排除是否可接受。
>
> 5 个 feature 分支 diff 对照规范（前置/契约/兼容/幂等/关键值配置化）审出的项。**待确认/待点头**，未擅自动。
>
> ✅ 同轮「**建议改**」已改并部署：product-server 批量 `500` 外置 Apollo + 删死字段 `renewalNumber`（`63fd5b757` → dev-3）、cart 删误导注释（`f18f9f52` → dev-1）；详见 [[changelog]] 2026-10-12 审查条。
>
> ✅ 「**必改**」Q-06 / Q-07 / Q-08 / Q-09 / Q-10 已改并部署、eureka UP（student-center `5ba12b10`→dev-1、cart `3594af88`→dev-1、product-server `9a9b4350`→dev-3/product-task）。
>
> ⏸ **Q-11 已闭环**：2 个调试接口（`testRenewalQuestionnaireTransfer*`）已于 2026-10-13 删除（`a5fc17adf`，在 release）。
>
> ⚠️ **遗留（非本需求，来自 release 的其它特性）**：student-data-dws `UserTeacherMqTestController`（`/inner/test/userTeacher/*`）、student-data-gps `NodeDetailMqTestController` 仍是「临时代码，上线前删除」；dws 会随发布计划 23716 上线，需其归属方处理或确认是否带上线。

| 编号 | 仓 | 位置 | 类别 | 事项 |
|---|---|---|---|---|
| Q-01 | product-server | `ComputeUserService.java:18` | 灰度 | `compute.rule.name.list` 代码默认 4 档→7 档 = 计划级匹配的灰度开关。**已自查：PROD（course-setting/product/product-task/product-b 的 application）均未配置 → 走代码默认 7 档，计划级匹配一上线即全量生效**；要不要先灰度由产品口径定 |
| Q-02 | product-server | `QuestionnaireRecordService.java:574/603` | DDL/并发 | **已自查**：① PROD `gaotu.questionnaire_record`（cluster 71）**无 `retry_count` 列 → 上线前必须提 DDL**（工单 146826 已提并 EXECUTED）；② PROD Job `QuestionnaireRecordComputeHandler`（cron `5 2/10 * * * ?`）**block=丢弃后续调度 → 不会重叠执行，并发无问题**；③ **重试上限保持默认 3**（2026-10-13 用户定：未归属近 3 天=0、加 432 会在高峰放大负载 ~1x，否决；见 [[changelog]]） |
| Q-03 | student-center | `RefundController.java:200` | 口径 | `refund_root_cause` 后端门控但不在下发名单 → 前端空模块；确认口径。**→ 2026-10-21 已定：不下线、纳入模块化，`refund_root_cause`（+`satisfaction`）加入开关表下发名单**（见 T-13），空模块问题消除 |
| Q-04 | student-center | 展示侧 vs 分析侧 | 口径 | 部门口径不同（展示侧=登录老师部门 / 分析侧=班级二辅部门）。**已查：T-11 已记录该差异（分析侧按班级二辅主岗）→ 预期** |
| Q-05 | cart | `pom.xml` `product-server-client` | 上线 | 钉 `1.5.9-SNAPSHOT`，提测前换正式包 |
| Q-06 | student-center | `RefundController.java:100` | 兼容/影响面 | `manual_reason` 门控卡死整段通用写接口 `roster/refund/edit`（误伤改名/备注/跟进，多入口不一致）；建议收窄到 `refundReason`/`refundIntent` |
| Q-07 | student-center | `RefundController.java:211` + `RenewalClazzUserController.java:160/172` | 兼容 | 关闭时返回 `null` → 旧前端读字段白屏；建议与同 diff 的 `analysis()` 一致返回空对象 |
| Q-08 | cart | `cart-client/pom.xml:65-68` | 兼容 | GMQ 挪位置时丢了原有 2 个 slf4j 排除（`log4j-over-slf4j`/`slf4j-log4j12`） |
| Q-09 | cart | `cart-client/pom.xml:38/58、42/62` | 构建 | 同一依赖声明两次（`ces-teach-product-api` 一处无版本、一处 `1.0.13-RELEASE`） |
| Q-10 | product-server | `QuestionnaireRecordService.java:637/650` | 契约/影响面 | `planCourseNumbersCache` 只用 `questionnaireNumber` 做 key，缺 `projectNumber` → 跨 project 复用错结果，算错计划级匹配范围 |
| Q-11 | student-data | `InnerBackController.java` + `LoginInfoFilter.java` | 风险/上线 | ✅ **已完成**（`a5fc17adf`，2026-10-13，在 release）：删除 `testRenewalQuestionnaireTransferConsumer/Sync` 两个 TEMP 接口 + `LoginInfoFilter` 放行白名单 |

## 2026-10-23 C 端加购适配

| 编号 | 任务 | 状态 | 证据/要求 |
|---|---|---|---|
| T-16 | 正式续班8014展示、选择、算价及订单链路 | 进行中 | cart 12cba6a9已部署并真实HTTP通过；order 253be420已生单/取消，停售负向暴露canCreate券上下文缺口，补丁复测中。见verify.md与膨胀券适配说明 |

## 完成判据

> 每个未闭环任务「怎样才算完成」的可检查判据；完成一项删一行，全部闭环后本节为空。

---

## P- 待产品确认（第二批 · 2026-10-14，可直接转产品）

> 代码已按现状实现，以下需产品拍口径；拍完再决定是否改代码。

### P-01 ✅ 已定（2026-10-15，产品口径）：「相同学期」= 学期值相等，学期是一整体单位、**不拆分**

- **产品口径（2026-10-15 定）**：课程「学期」取值 = 春季 / 暑假 / 秋季 / 寒假 / 循环班 / 全年班 / 暑秋 / 寒春。**「相同学期」就是学期值相等**；学期是**一个学季、整体单位**，**不拆分**（暑秋 ≠ 暑、≠ 秋）。单季的 `C/X/Q/D`(OES) ↔ `1/2/3/4`(CES) 只是**同一含义的不同枚举写法**（春季↔1、秋季↔3…），按含义等价。
- **代码已按此实现**（2026-10-15，student-data `e448d0a7`/`f4cf0770`）：学期只做**整值相等**比较，**不再因复合学期换算不出直接返回空**；大班→小班方向接受「课程学期原值」或其「CES 等价」（单季）；小班→大班方向按原值相等（复合可同值命中）。
- **数据现状（业务接受，先不处理）**：小班在读表 `dws_small_clazz_user_subject.school_term_id` **只存 `1/2/3/4`**（写表时复合学期换算不出 CES 会落空），所以「**当前课程=大班 且 学期是复合**」时，小班表没有同值可比 → 不排除。**逻辑正确，属小班表存不下复合学期的数据限制**（要生效得让写表链路把小班复合学期也落库）。
- 备查（大班在读表现状）：复合学期码约占 28%（`dws_fuwu_clazz_user_subject` 107万/381万行），实测含 `CU/CD/QU/QD/R/Y/X-Q/D-C`。

### P-02 ✅ 已确认（2026-10-15，按前端发布分支 master）：退费根因前端已下线 → 后端 `/reasonType` 死代码

- **前端发布分支**：`aianalysisinformations` 本仓**无 release 分支**（只有 `master` + 若干 feature），**master 即主干/发布**，head `0685c9b4`。
- 前端 `src/tabs/refund/` 只调 `/roster/refund/{analysis, reason, course, stage, edit, evaluate, gray}`，**不调 `/roster/refund/reasonType`**；全仓（master + feature 分支）无「根因 / rootCause / satisfaction / 满意度」。→ **退费根因已下线**。
- **✅ 已删（2026-10-15，student-center `497479d3`）**：`RefundController.reasonType` + `RefundService.reasonType/buildCommIdMap/transReasonType/summaryReasonType/queryDialog` + `RefundReasonTypeVO`（前端全局零调用）。
- **保留** `RefundAiModuleEnum.REFUND_ROOT_CAUSE`：**分析侧「退费根因」模块还在**（`RefundReasoningEnum.REFUND_ROOT_CAUSE` 在退费归因 END 节点、被 `RefundReasonProcessManager` 使用），该枚举被 `allModuleCodes` 引用，非纯死代码。
- **PRD 模块对照（2026-10-15）**：PRD 已把「AI预测退费原因」标注 **【已下线】** → 退费实际 **5** 个模块（退费分析/意向预测/手填退费原因/课程体验/退费沟通旅程）。与前端页面（aianalysisinformations `src/tabs/refund`）一致，**对得上**。
- **⚠️ 2026-10-21 更新（PRD 改动 + 决策反转）**：PRD《续班&退费优化：AI分析模块配置化》已改为「AI预测退费原因【前端下线、后端没下线】」，组合二另标「待定，能否替换成意向预测」；**产品 2026-10-21 定：不替换、不下线，纳入 AI 模块化配置**（`refund_root_cause` + `satisfaction` 下发，见 T-13）。前端分支 `feature-renewal-20260922` 会展示该模块 → 上文「退费根因已下线」的表述作废（**仅指老的展示分支 `master`/`feature-refund-reason-20260825`**）。

### P-03 ✅ 已确认（2026-10-15，按 release 代码全量核）：`levelReasonAndHistory` **不是死代码**（cronus 花名册在用）→ 保留

- **aianalysisinformations（master / feature）**：不调 `ai/clazzUser/levelReasonAndHistory`；分层变化+分层原因走 `predictLevelReason`（`src/components/IntentPrediction/`，续班/退费共用按 `scene` 分流，已按 续班9 / 退费prediction 门控）。
- **但 cronus（花名册前端，master）在用**：`continuationService.js#getContinueClassPrediction`（注释「获取续班意向预测等级结果」）调 `/ai/clazzUser/levelReasonAndHistory`，用在 `ContinuationService` / `ContinuationServiceLegacy` 的「续班预测」列组件。
- **结论**：该接口**不是死代码，保留**；且它 = **续班意向预测** → **我挂的续班 9 门控口径正确** ✅。
- 另：aianalysisinformations master 未调开关表接口 `ai/moduleSwitch`（13 key）；前端是靠各数据接口返回空态来隐藏模块。

### P-04 上线前置（非产品，需 MR/发包授权）

- 四仓（product-server / student-data / student-center / cart）反向合 `release` 并复测；
- `product-server-client` `1.5.9-SNAPSHOT` → 发 `1.5.9` RELEASE；cart pom 切 RELEASE；
- `student-data-client` `0.0.52.5-SNAPSHOT` → 定版 RELEASE（student-center 依赖）。

### P-05 AI 部门开关：线上怎么配 + 不兼容点（2026-10-15）

**PROD 现状（读回）**：`renewal.ai.dept.module.switch` / `refund.ai.dept.module.switch` **均未配置** → 代码默认 `{}` → **全量放开**（AI 全开，与上线前一致）。✅

**线上怎么配**：
1. **不做灰度 → 保持不配**（全量放开，AI 全开，行为与上线前完全一致、零风险）。**推荐先这样。**
2. **要做部门灰度** → 配 `{"<老师主岗虚拟组织架构 orgNumber>":[模块code...]}`。⚠️ **一旦非空，未命中的部门 AI 全关**（续班/退费展示+分析全停），所以**必须把所有"要有 AI"的部门都列全**；部门 key = **老师（二讲）主岗虚拟组织架构 org number**（`_` 分段精确命中）。
   - 续班模块 code：`1`用户画像 `2`沟通概况 `3`沟通建议&评分 `4`服务建议&评分 `5`未续跟进 `6`已续总结 `7`用户反馈 `8`主管点评 `9`意向预测。
   - 退费模块 code：`tutoring` / `learning` / `satisfaction` / `refund_root_cause` / `service_suggestion` / `prediction` / `manual_reason`。

**不兼容 / 风险点（"看下有哪里不兼容的"）**：
1. 🔴 **配置非空但不全 → 未配部门 AI 全关**。本次 dev-1「续班 AI 分析打不开」就是这个：TEST 只配了 `97349606689168923`，登录老师部门 `6816343048455168` 不在里面 → 该部门续班模块全关 → `predictLevelReason`（模块9）返空。**灰度上线前必须确认要覆盖的部门清单。**
2. 🔴 **退费侧按模块灰度会打断分析流程（#2105）**：退费归因是「并行(退费旅程/课程体验/满意度) → JOIN → END(退费根因/服务建议)」编排，**模块关闭时 `handleCode=0` → 调度器在 START 节点直接把整个流程判 INVALID 结束** → 同流程里已开启的模块也不跑。**所以退费侧要么只做部门级「全开/全关」，要么先修代码（把"模块关闭"写成跳过日志、让流程继续）。**
3. ⚠️ **模块 9（意向预测）**：之前的 TEST 配置 `{"97349606689168923":[1..8]}` **不含 9** → 用 177071 测续班展示会"全关"（[[verify]] 已记）。灰度配置要记得带上 9。
4. ⚠️ **展示侧 / 分析侧部门口径不同**（展示取登录老师部门；分析取该班辅导老师部门）→ 可能出现「前端展示但 AI 不分析」或反之（2026-09-24 已定，非 bug，但要知道）。
5. ⚠️ **前端**：aianalysisinformations **未调**开关表 `ai/moduleSwitch`（靠各数据接口返空态隐藏模块）；**cronus 用 `levelReasonAndHistory`**（挂的是续班 9 门控）——即模块 9 关掉时，cronus 花名册的「续班预测」列也会没数据。

**TEST 现值（本次还原，兼容之前灰度 + 覆盖测试部门）**：`renewal.ai.dept.module.switch={"97349606689168923":[1..8],"6816343048455168":[1..9]}`；`refund.ai.dept.module.switch={"6816343048455168":[全模块含 manual_reason]}`。

### P-06 模块对照 + 退费依赖关系 + 能否按模块灰度（2026-10-15）

**续班模块对照（PRD ↔ 后端 ↔ 前端）——对得上 ✅**
| PRD(8) | 后端 `RenewalAiModuleEnum`(9) | 前端 `tabs/renewal` |
|---|---|---|
| 续班用户画像 | 1 用户画像 | ✅ |
| 意向预测 | 9 意向预测（新链路） | ✅ |
| 沟通概况 | 2 沟通概况 | ✅ |
| 已续/未续跟进 | **5 未续跟进 + 6 已续总结**（合并为 1） | ✅ 续班归因（互斥、条件展示） |
| 沟通建议&评分 | 3 | ✅ |
| 服务建议&评分 | 4 | ✅ |
| 用户反馈 | 7 | ✅ |
| 主管点评 | 8 | ✅ |

**退费模块对照（PRD 6，其中「AI预测退费原因」已下线 → 实际 5）**
- PRD 5 = 退费分析 / 意向预测 / 手填退费原因 / 课程体验 / 退费沟通旅程 ↔ 前端 `tabs/refund` 一致 ✅。
- 后端 `RefundAiModuleEnum`(7) 比展示**多** `satisfaction`（满意度归因）/ `refund_root_cause`（退费根因）——是**分析侧内部模块**（PRD 展示清单里没有）。**→ 2026-10-21 改**：两者一并纳入模块化下发/展示（见 T-13）。

**退费依赖关系（线上正在跑）**
```
START（并行） 退费沟通旅程(tutoring) / 课程体验(learning) / 满意度归因(satisfaction)
      │ 三个全部完成
      ▼
    JOIN  →  END（串行）退费根因(refund_root_cause) / 服务建议(service_suggestion)
```
- **服务建议、退费根因 → 依赖「退费沟通旅程 + 课程体验 + 满意度」三个全部完成**。
- **意向预测（新链路）、手填退费原因 → 独立，无依赖**。

**能否单独对每个模块灰度**
- **续班**：各模块独立门控（圈选/归因/展示各自判断）→ **能**单独灰度。
- **退费**：改前**不能**（关一个并行模块 → START 节点把整条流程判 INVALID 终止 → 连累服务建议/退费根因）；**已修（`#2105`，student-data `653bf30e`）：模块关闭改为「跳过但继续流程」→ 现在能单独对每个模块灰度**。
- **E2E 验证（2026-10-15，dev-1，✅）**：测试辅导班 `31265963667882240`（辅导老师部门 `6816343048455168`）。① 配 `refund` 关掉 `satisfaction` → `isRefundModuleEnabled(部门,"satisfaction")=false`、`"learning"=true`（配置生效）；② 触发退费分析（`RefundReasonTaskService#refreshReasoning`）；③ 流程日志 `refresh292526594721867776`：`tutoring / learning / satisfaction / refund_root_cause / service_suggestion` **全部有记录** → **关掉 satisfaction 后 END 的「退费根因/服务建议」照跑**（改前会整条判无效、不跑）。验完已还原配置。
- **✅ 产品已确认（2026-10-15）**：退费「按模块灰度」的修复口径（模块关闭=跳过但让流程继续）**OK，按此实现**。
- TAPD（迭代 1122531521001014934）：开发条（扩科 3 条 + AI 2 条）**已完成**，自测 / 联调 **进行中**（2026-10-15 已置）。


## 本轮复核待闭环（2026-10-21，第二批）

| 编号 | 任务 | 状态 | 证据/要求 |
|---|---|---|---|
| T-14 | 扩科＋AI＋下单 PRD/diff 审计与 P0 编写 | 已完成 | 20条/53子场景已写飞书并逐批回读；23819关联下单story。仅审计交付，非生产准出 |
| T-15 | 第二批增量 P0 验收与确定缺陷修复 | 已完成 | 20条/53子场景执行记录回写；扩科/AI核心闭环、77项data测试、门控85.04%行覆盖；组合数量83fa4e0/alpha.4实测修复。原链接参数/模型格式风险及共用出口未逐页覆盖已明确，非生产准出；GAIA审批与PROD配置仍按上线方案 |


## 2026-10-21 最终补录（人工执行卡与发布编排实测）

详见 [[本次工作记录-20261021]]。20条case已补账号、班/辅导班、学员及关系、配置、操作和可见预期；53个执行场景保留。技能已固定人工优先规范，审计73条路由通过。发布编排实际执行一次，后端汇总57%，准出未执行、总门禁未过；历史79条告警仍未处理。DWS/GPS配置类型错误已补部署并验证UP/真实Bean/新pod无解析错误。AI及cart核心缺口已补验、临时数据配置恢复；未重算平台，不声明上线放行。


### 第二轮平台覆盖率已验证

21:25:57重算后：product92.11%（39333）、data81.44%（39334）、center83.43%（39335）、cart82.45%（39336）、order83.80%（39337）；后端汇总81%已通过，未改阈值或业务排除。前端空计划保护真实补验后单独重算中。准出未执行，不能据此声称生产放行。无关历史告警已停止处理，未经明确要求不建缺陷；三条误登记TAPD已置不解决，但天玑status2恢复操作未生效，7条分类残留已如实写在线文档。技能审计errors0/warnings0、75条路由0失败。


### 最终平台覆盖率

最终平台结果：后端汇总81%、前端汇总97%，两项覆盖率门禁均通过。后端product92.11%、student-data81.44%、center83.43%、cart82.45%、order83.80%；前端promotions97.91%（39331）、cronus100%（7/7，39338）。全部为新报告实际值，未改阈值或业务排除。准出仍未执行，USER_CASE/ALARM等其他门禁不等于通过。按用户要求，无关历史告警不处理、不新增缺陷。

Cronus补测走真实小班页面：唐稳01/tangwen01登录→清空续班计划→非续班期且不限本人→班级“测试触达”494625569468663808→学员5661436125“接口自动化测试”→下单，显示“缺少续班计划号，无法下单，请先选择续班计划”，不打开下单容器；两次均通过。完成后已恢复专用数学班、续班计划及7658127801，无订单/支付/购物车写入。


## 2026-10-22 CASE-108 增量

| 编号 | 任务 | 状态 | 证据/要求 |
|---|---|---|---|
| C-02 | 退费分析卡预测等级跟随 prediction 开关 | 进行中 | 后端7测通过、流水线1309131部署UP并接口code0；前端待改。student-center `2cc0194a9`；详见 [[CASE-108-退费预测开关修复]]。不扩大到 cronus 列表；整项未闭环 |


## 2026-10-22 C 端购物车参数兼容

| 编号 | 任务 | 状态 | 证据/要求 |
|---|---|---|---|
| C-03 | cart 兼容旧页面的 `sellerId=null` | 已完成 | cart `bdba9e90`，10测通过；流水线1309368部署dev-1新pod UP，7项真接口验证通过，推荐数据与修复前省略sellerId的基线一致。前端未修改；此项仅cart兜底，上游身份错配及promotion空值拼链待处理（见verify）。 |


## 2026-10-22 链接生成身份修复

| 编号 | 任务 | 状态 | 证据/要求 |
|---|---|---|---|
| C-04 | student-center教师状态筛选及上游身份问题 | 进行中 | 按用户最新指定仅补候选教师status=1筛选及字段映射，撤回LoginInfo.casUid优先返回改动；测试待执行，尚未提交部署。旧教师仍status1，此筛选不代表上游身份问题已闭环，详见verify.md。 |

## 完成判据

- C-04：当前改动限RenewalContentCommonSupport账号候选流status=1筛选、TeacherInfoDO及TeacherServiceImpl映射；真实Feign/ACL测试验证停用/初始化/缺省状态排除与正常启用选值，失败先查下游baseInfo.status及DO映射。原seller_id=null根因另需员工身份一致性修复并用tangwen01推荐/预报名appInfo验证，不能仅凭教师状态筛选标记闭环。

- T-16：order CanCreateOrderForNeoService将配置券类型加载进ProductContext；dev-1上8014停售请求应拒绝，开售恢复后通过、超限数量拒绝，prepare限购字段与SKU一致；失败先看商品真实canBeSold与校验上下文productInfoDTOS。提交/部署前JDK8编译通过，更新前端对接文档并回读。
