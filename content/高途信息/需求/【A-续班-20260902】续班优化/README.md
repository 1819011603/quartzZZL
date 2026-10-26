---
title: 【A-续班-20260902】续班优化
aliases: [续班优化(秋季批), 续班问卷匹配优化, 续班退费AI模块配置化, 续班退费数据落表, 小班续班主讲数据下单优化, 续班扩科推荐优化]
status: 上线准备
owner: zhangzeling
branches:
  - product-server:feature-xuban-match-opt
  - student-data:feature-xuban-match-opt
  - teacher-tool:feature-xuban-match-opt
  - student-center:feature-xuban-expand-exclude
  - student-data:feature-xuban-expand-exclude
  - order:feature-xuban-expand-exclude
  - cart:feature-xuban-expand-exclude
  - product-server:feature-xuban-expand-exclude
  - gaotu-fe-promotions:feature-xuban-202610
  - aianalysisinformations:feature-renewal-20260922
  - continu-clazz-order:feature-renewal-20260922
updated: 2026-10-23
tags: [需求]
---

# 【A-续班-20260902】续班优化

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[verify|🧪 验证手册]] · [[changelog|📜 决策摘要]] · [问卷匹配-DDD建模方案.md](问卷匹配-DDD建模方案.md) · [问卷匹配-改动前链路.md](问卷匹配-改动前链路.md) · [问卷匹配-case回归-20261008.md](问卷匹配-case回归-20261008.md)
> 技术方案（现状 / 方案对比 / 详细设计 / 接口 / 风险）在飞书反讲里，见 [[links]]；本文件只留当前结论和指针。
> 飞书：需求总入口 https://gaotuedu.feishu.cn/wiki/Qox8wFcmHiXBgnkxFBtcd82gnsh → **技术反讲（子需求 1/2/3/5）https://gaotuedu.feishu.cn/wiki/EC45wOefUi0buMkO7O0cipp9nEc** → **待产品确认清单（21 条，可直接转发产品）https://gaotuedu.feishu.cn/docx/L2yrdOPEAoIOMux1JLXcGtR4nde** → **上线方案（问卷匹配+调课同步）https://gaotuedu.feishu.cn/wiki/JBsywJOuiijDT9k3MD7cFyl8n9b** → **上线方案（扩科推荐+AI 模块配置化）https://gaotuedu.feishu.cn/wiki/KSDfwlojaipDqWkUcbfckjnwnyd**（对应青舟发布计划 23819，泳道 test-gtbg-dev-1）
> 续接这个需求：读完本文件即可。

## 一句话

付星/马胜一次性打包转发的 5 个续班优化子需求。

## 需求摘要

5 个子项，PRD 均 V1.0 / 2026-09-05：

| 优先级 | 子需求      | 一句话                            | 子项P级              |
| --- | -------- | ------------------------------ | ----------------- |
| 1   | 问卷匹配优化   | 匹配范围收紧 + 7 档匹配优先级 + 调课调班同步问卷数据 | 匹配逻辑 未标 / 调课同步 P1 |
| 2   | 小班续班适配主讲 | 小班续班服务按角色(主讲/班主任)展示数据；快速加购组合商品纳入本批（2026-10-21 用户确认）   | 主讲 P0             |
| 3   | 扩科推荐优化   | 续班计划新增【推荐排除】，避免跨授课模式重复推荐       | —                 |
| 4   | 数据落表     | 续班/退费数据落表供导数分析                 | —                 |
| 5   | AI 模块配置化 | 续班/退费 AI 按部门配置模块开关，降本          | —                 |

- **给谁用**：主讲、班主任(二讲)；学部运营（数据落表）。
- **判定做完的标准**：本批 4 个子需求各自评审、反讲、开发、上线，按子需求粒度跟踪（见 [[tasks]]）。
- **范围**：本批做 1/2/3/5；子需求4(数据落表)和续班确认表不做；子需求2 的快速加购组合商品纳入本批（2026-10-21 用户确认）。所有子需求历史数据**不回溯 / 不重算**。

## 已定共识

- 5 个子需求彼此独立、可并行，不要求同批上线（2026-09-17）。
- **问卷匹配**：范围 = 问卷 + 续班计划 + 班级 + 辅导老师；**问卷与续班计划必须完全匹配**，班级 / 辅导老师不做强校验；规则为 **7 档优先级**（同班 / 同计划 × 手机号 → 姓名 → 亲属手机号），**多命中取学员 ID 小的**；历史不回溯。
- **调课调班同步**：前提是 A/B 两班绑定同一份续班问卷；要**新增消费** `gaotu_after_sale_event_test` + tag `TRANSFER_TOUCH_EVENT`（现只有 reach-service 消费）。
- **AI 模块配置化**：未配置的模块要**同时做到"前端不可用 + AI 不分析"**（2026-09-18 产品确认为隐藏）；续班对外 8 个描述 key；退费对外 7 key（含内部依赖 satisfaction）；验收覆盖 PRD 单功能与组合一/二，根因不下线。
- **数据落表**：续班覆盖大小班课、退费仅大班课（本批不做，仅登记）。
- **主讲适配**：仅小班；**主讲（含双角色）按班级维度、仅班主任按辅导班维度**；现状 OR 合并**已等于** PRD 口径，**很可能无需开发**（待评审确认）；快速加购组合商品纳入本批（2026-10-21 用户确认）。
- **扩科推荐**：问题根源 = 扩科班级 / 商品不区分大小班可随意选，导致跨授课模式重复推荐；**【推荐排除】** = 扩科推荐为【是】时可编辑、默认空、单选，枚举【无排除】/【排除不同授课模式在读】；"在读"八条件逐调用链核实；小班读侧补齐与大班不同的课程资格缺口；当前不回溯。**历史续班计划 `excludeMode` 为空 → B 端回显兜底为 `0`（无排除）**，老计划打开即【无排除】、老师无需补选；推荐侧 `excludeMode != 1`（含 null）即不排除，行为与上线前一致 → **兼容，不刷数**（`ProcessService#convertNodeConfigVO`，2026-10-12）。

## 现在什么情况

> **2026-10-26 口径更正：切年级保留课程/券勾选，切回恢复**：按用户最新要求，`productSelectGrade` 只记录当前年级，不再删除 `user_renewal_clazz` 选择；`productList` 增加课程勾选态回填。cart `046533da` + `707cf664`，流水线 `1312764`/`1312811`，新 pod `cart-gaotu100-com-5874cd87bc-7x6z8` / `10.218.237.97` Eureka UP；JDK8 全仓编译、20 项测试通过。真实接口：选中课程 `585960755422160896` + 券 `578323391191220225`，切 grade11 后 productList 两者仍 select=1，切回 grade16 仍为1；验后已取消勾选。**原“切年级清空、切回不恢复”口径作废。** 前端仍只提交当前年级 payList，不跨年级下单。

> **2026-10-24 组合加购修复已部署 dev-1**：cart `7f298d68`（流水线 1312177）修复两处组合逻辑：大班路径组合展开子班参与 (年级,学科) 去重、组合取首个课程有效子项。新 pod `cart-gaotu100-com-64f5bcbb6b-v5h2t` / `10.218.236.158` Eureka UP；JDK8 全仓编译、19 项组合/券契约测试、10 项 Controller 测试通过；新 pod 真实调用 8014/组合/productList/price 回归正常。已构造真实去重样本：给组合 579426174109902848 临时加一个六年级语文子班，C 端 GET 中该组合被去重；删除临时子班行并清缓存后恢复原展示。6004 子项组合已构造实测通过：补邮寄地址后 createOrder status445「报名成功」，订单 432531877787599168，订单项含 6004「测试小班课商品2」，页面同时展示大班课；0 元测试单因课程已结课不可售后保留，SPU/SKU 与购物车已恢复。

> **2026-10-24 正式 C 页复验：后端通过、前端未发布，CASE-121/123/126 页面不通过；CASE-128 生单取消通过**：重核 dev-1 未变（cart `91964dcd` / order `5ab5476d`，Eureka UP）。后端接口仍返回 8014 完整 `availableScope`、51 组合、6003 详情，勾选/切年级清空接口侧正常。真实 `test-m/suggestShoppingCart` 实际加载 mweb master（CDN 资源 Last-Modified **2026-10-22 09:20 CST**），未含本需求前端改动：8014 不显示 `availableScope`、51 无“组合商品”标识、切年级后页面 `payList` 仍保留上一券（合计 0 但“去结算”可点）→ **前端发布后复验**。CASE-128 本次真实生单成功：后台 `createOrder` **2393ms / status0**（trace `eebafe36-c188-4787-8a35-0929acbe1cfd.0.3`），商品项 `432524642915189056`、pay `432524641841447232`；正常取消后 order-b 仓库读回 `orderStatus=3`。**未复现 ERR_ABORTED**，但前端 5s 全局超时缺口仍在（需超时提示 + 按订单列表查单恢复，禁止自动重试）。CASE-130 支付/退款后 signUp、CASE-131 口径已澄清为按 SKU 去重、不同 SKU 不合并（现实现符合）、CASE-133 命中优惠、CASE-134 真实冲突/考试仍待验。本轮**未改后端代码**，仅回填文档。证据见 [[verify]]。

> **2026-10-23 晚 后端接口复验 + 生单实数**：重核 dev-1 版本未变（cart `91964dcd`、order `5ab5476d` 均 Eureka UP）。用反射桥/内部 Feign 真实复验 CASE-121/123/124/125/126/127/129/132/134：8014/组合/6003 展示、带与不带 `renewalNumber`、勾选幂等与切年级清空、新旧算价去重均通过；纯券预检跳过课程校验、数量2被拒。生单从真实 trace 读回后端端到端 **3245ms status0**（前端 5s 全局 axios 超时才是 `ERR_ABORTED` 原因）。**未复验（待验）**：CASE-130 支付/退款 signUp、CASE-122 多范围、CASE-131 同商品多SKU去重、CASE-133 命中优惠、CASE-134 真实冲突/考试负向、CASE-128 本轮生单取消——均因无学员登录态或需恢复前置数据，不标通过。前端 `gaotu-mweb` 现有分支未包含本需求改动（详见 verify.md）。证据见 [[verify]]。

> **2026-10-23 新增跨年级记忆已撤回，原行为真实复验通过**：cart 91964dcd已部署dev-1（流水线1311910，新Pod/Eureka UP）；JDK8全仓编译及17项测试通过。同年级课程/券保存、取消券不影响课程、切年级清空、切回不恢复、组合详情真实HTTP通过；原另一计划4条选择保持不变，年级恢复16。保留原8014适配及组合详情修复；前端文档已撤销记忆参数/全局跨年级清单要求，CASE-126按原行为验收。页面其他展示与生单超时仍待前端验证。

> **2026-10-23 C 端加购后端改造与部分接口实测完成，人工验收未完成**：cart `1357f368`（含8014及独立6003）、order `5ab5476dfb` 已部署 dev-1，新Pod/Eureka UP。独立6003详情/大小班展示、券多范围、勾选隔离、新旧算价、确认页、生单取消与停售负向均有真实接口证据；JDK8编译及cart13项/order4项契约测试通过。前端文档已回填并回读，测试数据恢复。兼容旧前端与既有灰度。独立6003缺口已补齐；组合首子项和券范围两处PRD文字差异继续按用户明确口径实现，见 [待办-膨胀券C端8014适配.md](待办-膨胀券C端8014适配.md)；trace见 [[verify]]。验收用例已补至飞书P0的CASE-121～134（14条现场执行卡），支付/退款后signUp、同productId多SKU去重、独立限购边界、命中优惠、混合课程负向、页面与完整灰度矩阵仍待真实验收，不宣称全部通过。

> **2026-10-22 本轮仅改后端（C-03已完成）**：cart `bdba9e90` 兼容既有请求 `sellerId=null`，10项测试通过，流水线1309368部署dev-1新pod UP；原请求已返回status=0，7项接口验证通过且推荐数据与原基线一致。前端未修改。**上游另已查明：tangwen01当前CAS132658→employee8645正常，但旧教师记录仍status1，认证层按账号/类型取首条指向离职员工2994/CAS120805，student-center优先取旧CAS，promotion再拼出null；C-04按最新指示仅补教师启用状态筛选，已撤回直接返回登录CAS的改动；该筛选不能排除本例status1旧记录，上游身份问题仍未闭环，详见verify.md。**

> **2026-10-22 CASE-108 增量修复**：退费分析卡的预测等级需跟随 `prediction` 开关。后端 `student-center 2cc0194a9` 已实现并通过7项测试，已部署test-gtbg-dev-1并真实接口回归；前端两处改法已给出、尚未修改，详见 [CASE-108 修复与前端改法](CASE-108-退费预测开关修复.md)。当前供用户查看的续班/退费页面与部门开关保持开启，待用户看完后再恢复临时配置。

> **2026-10-21 本轮核心验证及P0文档已完成，尚未生产准出。** 飞书20条用例已细化53个子场景，逐项列入口、数据、操作、预期、实测。扩科真实保存0/1→推荐3/2项、双向推荐、赠课/纯预售对照通过；AI画像预测泄漏和无归因编辑绕过已修并部署复验，续班与退费单模块/组合一二已有真实模型和落库对照。null配置修复已部署并9项运行时复验。下单历史支付/校验不扩大为本次新增；上线方案已同步12后端、2前端和2个GAIA组件发布。扩科边界和AI完整组合均已补齐；保留模型格式偶发失败及未逐页面点击的共用出口覆盖边界；测试预览seller参数问题已由C-03后端修复。

| | |
|---|---|
| 阶段 | **上线准备**（问卷匹配 + 调课同步 → 发布计划 23716，2026-10-13 起；见下「上线准备」） |
| 进度 | T 18/18 · R 4/4 · C 2/4；本轮审计与 P0 编写完成，增量验收与确定缺陷修复进行中，不可直接放行 |
| 部署泳道 | **`feature-xuban-match-opt` → `test-gtbg-dev-3`**（product-task / student-data / teacher-tool）；**`feature-xuban-expand-exclude` → `test-gtbg-dev-1`**（product-b / product / student-data / cart / student-center，2026-09-24 已迁完、均 eureka UP）。2026-09-24 用户定，两分支不再共用泳道 |
| 当前卡点 | 上线准备：🔴 DDL 工单 **146826**（`gaotu.questionnaire_record` 加 `retry_count`，待审批，须先于 product-task）、🔴 MQ 工单 **90538**（PROD group `GID_student-data_renewal_questionnaire_transfer_prod`，实例 `gaotu`，待审批）均待 SRE 审批；teacher-tool-api `1.0.29` RELEASE 已发、两处 pom 已切 RELEASE 并 push；Apollo `renewal.questionnaire.transfer.consumer.group` 待 group 审批后配（未配会走测试组名默认值）。 |
| 最近更新 | 2026-10-21：P0文档20条/53子场景及上线方案已写回；student-data f5540c121最新扩科空类型兼容修复32测通过、部署1308190已EurekaUP并7项实测通过；student-center 8cffd81c5已UP复验；promotions新版1308187已实际加载并页面必填/默认/保存回显通过。 |

## 上线准备（2026-10-13 · 发布计划 23716「问卷匹配 + 调课同步」）

范围 = 发布计划 **23716**，5 个后端服务：teacher-tool / product-b / product-task / student-data / **student-data-dws**（同 build，承载花名册回写消费者，别漏）。上线方案见 [[links]]（飞书《上线方案（问卷匹配+调课同步）》）。

**PROD 现状核查（2026-10-13 读回）**

| 上线项 | 现状 | 结论 |
|---|---|---|
| 代码 MR（三仓 → release） | 三仓 `feature-xuban-match-opt` 均领先 release、未合 | ⏳ 待提 MR |
| teacher-tool-api 定版 | 已发 **`1.0.29` RELEASE**（Nexus releases 可见）；teacher-tool-service、student-data-client 两处 pom 已切 `1.0.29`，已 push（teacher-tool `0d03f708`、student-data `f308ea83`） | ✅ |
| MySQL DDL `retry_count` | 工单 **146826**（sre.baijia.com，cluster 71 `gaotu-center-prod`，Inception ok）；PROD 仍 18 列无该列 | 🔴 待审批/发布 |
| MQ consumer group | 工单 **90538**（op.baijia.com）；实例 `gaotu`(Bay8En7I) 尚无该组 | 🔴 待审批（现 pending 直属leader审批） |
| Apollo student-data | `after.sale.event.topic=gaotu_after_sale_event_prod` ✅；`renewal.questionnaire.transfer.consumer.group` **未配** | 🔴 待 group 审批后配 |
| Apollo course-setting | `compute.rule.name.list`/`all.share.questionnaire.renewal` 均未配 → 走代码默认 7 档 ✅ | ✅ 无需动作 |
| ES / 代课权限 / xjob | 只写已有字段 / 仅内部 Feign / 不改配置 | ➖ 不涉及 |

**发版顺序**：teacher-tool → product-b → product-task → student-data（-dws）；每个 eureka UP 再发下一个。**teacher-tool 必须先于 student-data**（两边 release 无 `/transfer/sync`，student-data 先上会 404 → 重试耗尽进死信）。product-task 必须在 DDL 之后。

## 下一步

1. 扩科成人/体验/线下、干净全退及全局开关对照已通过；部分退售后status1/process99已终态且仍[1]。
2. promotions新版全部页面配置规则已通过；大小班B/C推荐及手工加购服务已验。原测试推荐链接seller_id=null已由C-03后端兼容修复、7项接口复验通过。
3. AI学习/NPS真实模型与落库、圈选12测、隔离HTTP故障恢复3测已补齐；门控行覆盖85.04%。组合商品删除数量缓存缺陷83fa4e0已修，alpha.4真实删除/加回与19→20/20禁用、混合明细通过。
4. 可重放只读脚本、53子场景执行清单和证据已落qa-data-agent-service用例包；上线窗口再核最终head评审、部署产物和配置。
5. 上线窗口完成release合并复测、client定版、PROD配置及GAIA正式版本审批发布；问卷匹配批次23716继续按其独立DDL/MQ前置处理。

## 已定（2026-09-21 产品 / 数据确认）

- ✅ 【下单优化】2026-10-21 用户确认快速加购组合商品纳入 23819；续班确认表仍按最新 PRD 标注不做。
- ✅ 【主讲适配】**确认无需开发**（现状 OR 合并已等于 PRD 分角色口径）；统计口径为**实时**（《小班课字段+指标》指标页 6-9 行）。
- ✅ 【问卷匹配】同名 / 一号多孩**不做产品侧解法**，按 PRD 7 档规则实现。
- ✅ 【问卷匹配】「改派（改班级）」**不用做**（王永诗：手工绑定维持现状，只改学员）。
- ✅ 【问卷匹配】「同一手机号多次提交只展示最新」**EES 已有**（teacher-tool `QuestionnaireConsumer#handleRenewalQuestion` 按 userId+clazzNumber+type+questionnairePhone 查旧记录，finishTime 更晚才覆盖）。
- ✅ 【问卷匹配】问卷明细「班级名称 / 班级ID」字段**已有**；teacher-tool **不加**「续班计划」列。
- ✅ 【扩科推荐】【推荐排除】为**新增配置**（不与【纯续和扩科是否重复推荐】合并）；粒度 = **续班计划级**。
- ✅ 【扩科推荐】B 端 `POST /product-b/b/renewMaster/recommendProductList` + C 端接口**按「纯续+扩科推荐范围」展示**；**「下单页选品」(`productSelect`，换班选品) 不需要排除过滤**（2026-09-23 定，反讲原「选品也按排除范围」口径作废）。
- ✅ 【扩科推荐】「在读」口径：**复用 student-data 现有 + 补 2 条** —— 现有在读科目链路已覆盖 非成人 / 专题系列课 / 不含赠课标签 / 非纯预售（`OdsSmallRenewalSubjectSyncService:189-221`、`DwsRenewalSubjectConsumer#checkFilter`、`BackClazzUserSubjectService#isValidClazz`），相同学年学期靠 `yearTermGrade` 分组、授课模式靠数据源（小班在读科目来自小班课在班）；**但「上课形式为线上(operationMode)」与「订单未全部退款」现有链路没有，需补**（退款状态现网有 {6,10} / {6} 两套，需统一）。
- ✅ 【AI 配置化】配置入口**先用 Apollo 后端配置**（先搞简单点，GAIA 页面后续再议）：续班 / 退费各一个 `Map<虚拟架构部门, Set<模块>>`，如 `{虚拟架构部门A:[1,2,3], 虚拟架构部门B:[1,2,3,4,5]}`；部门 key = 虚拟架构部门 org number，匹配 = **老师（二讲）主岗部门路径**任一段命中（本部门及下属）；展示侧取登录老师、分析侧取辅导老师（2026-09-23 修正，原「课程部门」口径作废）。
- ✅ 【AI 配置化】「用户反馈」「主管点评」**算 AI 模块**；无需枚举映射；关闭模块后历史数据按**隐藏**处理。
- ✅ 【AI 配置化】「不展示」落点 = 前端仓 `ees/aianalysisinformations`（分支 `feature-refund-reason-20260825`）：沟通建议 `/component/student-center/problem/fulfillProblem/overview`、服务建议 `/component/student-center/fulfillSop/overview`、退费 tab 接口（`src/tabs/refund/*`），入参统一 `{ userId, clazzNumber, subclazzNumber }`。
- ✅ 【AI 配置化】部门→模块配置放 **student-data 的 Apollo**（`renewal.ai.dept.module.switch` / `refund.ai.dept.module.switch`；展示侧 student-center 只透传登录老师 accountId 给 student-data 解析部门。注：`compute.rule.name.list` 是问卷匹配的、仍在 product 公共 namespace `gt.product-public-app`）。
- ✅ 【AI 配置化·开关表】（2026-10-12，与前端反讲对齐）：新增 `POST ai/moduleSwitch`（无入参，按登录老师判定），下发 **15 个 key**：续班 `1,2,3,4,5,7,8,9`（与 PRD 对齐——「已续/未续跟进」是 1 个模块，合并为单 key `5`，值 = 后端模块 5「未续跟进」‖ 6「已续总结」任一开启；`9=意向预测`）、退费 `service_suggestion/prediction/manual_reason/learning/tutoring/refund_root_cause/satisfaction`（**2026-10-21 改**：`refund_root_cause`、`satisfaction` 不再排除、一并下发——退费根因不替换·不下线、纳入模块化）。语义：**一部门未配 / 登录缺失 / 查询异常 / 缺 key 一律 `true`（fail-open）**，与前端「失败即展示」一致。数据接口兜底：`evaluateQuery` 用户反馈按 7 / 主管点评按 8、`managerEvaluate` 写按 8、`/roster/refund/analysis` 按 `service_suggestion`（关闭返 `{}` 不返 `null`）、通用编辑入口（`/roster/refund|stageFeedback|renewal|examAnalysis/edit`，`StageFeedBackService.edit`）写 `manual_reason` 管辖列（bizName=refundReason/refundIntent）时按 `manual_reason` 拦、`ai/renewal/reason/detail` 按 reasonType 看 5/6、`ai/clazzUser/predictLevelReason` 续班 9 / 退费 prediction（关返空对象）、`/user/feedback` 读写均按 7。**意向预测（续班 9 / 退费 prediction）**：读侧按模块门控（`predictLevelReason` 关返空对象、开关表下发 key `9`/`prediction`）；写侧（含回溯）是「算法真表 → Sync job 落库 + 刷 ES」的数据管道、**不挂模块门控（写全量）**，**不需要专门回溯**；旧意向预测链路（`SyncRenewalLiftSnapshotHandler` 等旧 xjob）已停用。
- ✅ 【跨仓承接方】product-server / teacher-tool 的改动**归本团队**。
- ✅ 【问卷匹配】调课调班同步**由 student-data 承接**（扩 `DwsAfterSaleSyncConsumer` 加 `TRANSFER_TOUCH_EVENT` 分支）；旧班 A 来自报文 `LlsTransferCourseMessageDto.originalOrderInfo.clazzNumber`。
- ✅ 【扩科推荐】就是**加个过滤**：**扩科推荐本来就在 cart 算**（`ExpandSubjectRecommendService#recommend`，小班 :32 / 大班 :69，只按年级匹配），这次就在这两个重载里**加一个「排除对方授课模式在读学科」的过滤**。product-server 的 `recommendProductList` 只是把 cart 结果转成 B 端列表，cart 改完自动同步；**student-data 的扩科科目 subtract 只服务花名册「大小班扩课科目」字段，不用动**。

## 待确认

- [ ] 【数据落表】落表方式（MQ / binlog / 直连 Doris）—— 数仓侧（本批不做，仅登记）
- [ ] 【数据落表】"续班 / 退费所有字段"清单，含 GAIA 动态字段如何落表 —— 需 PRD 提供清楚（本批不做）
- [ ] 【问卷匹配】规则改动影响大班 + 小班全部匹配，回归范围待确认 —— 测试
- [ ] **产品侧问题汇总见飞书《待产品确认清单》（已全部回填 ✅）** https://gaotuedu.feishu.cn/docx/L2yrdOPEAoIOMux1JLXcGtR4nde
- [ ] **退费 AI 模块依赖/灰度口径 6 条待产品拍板**（按模块灰度 / 关闭致上下文缺失 / 部门级配置语义 / T+1 依赖 prediction / 关闭展示形态 / manual_reason 写拦口径）→ 飞书《退费 AI 模块依赖关系与灰度口径（待产品决策）》 https://gaotuedu.feishu.cn/wiki/KR3RwV16gi6zf9km55cclT79nhf （2026-10-20）
- ✅ **退费根因（T-13，2026-10-21 已完成）**：**不替换、不下线，纳入 AI 模块化配置**（`refund_root_cause` + `satisfaction` 一并下发到开关表，`POST ai/moduleSwitch` 变 15 key）；**功能保持不变**。**后端已改并 push：student-center `2bac261cc`（`AiModuleSwitchQueryService.REFUND_MODULE_CODES` 5→7 项，单测 5/5 过）**；前端分支 `feature-renewal-20260922` 展示（`REFUND_CODE.ROOT_CAUSE='refund_root_cause'`）。**（原「替换成意向预测」「加 Apollo 开关下线」两个方案均作废）**。**2026-10-21 追加：展示接口 `/roster/refund/reasonType` 曾被 `497479d3b` 当死代码删除（飞书报 404，与「不下线」冲突）→ 已 `git revert 497479d3b` 恢复（含 5c1465e57 残留），student-center `9cd9c9f88` 已 push**。PROD 后端分析侧仍在跑（2026-10-19 日志 `currentTaskEnum=REFUND_ROOT_CAUSE`、`handleCode=2`）—— 见 [[tasks]] T-13

## 涉及的代码

本需求第一批已建分支（从 `origin/release`）：product-server / student-data / teacher-tool = `feature-xuban-match-opt`（student-center 的 TT 字段属另一需求，走 `feature-tutu-active-time`）。主仓路径 `/Users/gaotu/IdeaProjects/JavaProject/{student-data,student-center}`；另涉及 product-server / cart / order / reach-service / teacher-tool / clazz-distribution-server。完整 `path:line` 见飞书反讲「详细设计」。

| 子需求 | 仓库 | 关键入口 |
|---|---|---|
| 1 问卷匹配 | product-server（主改） | 绑定层 `QuestionnaireService#match`；记录归属层 `ComputeUserService#compute` + `QuestionnaireRecordService#dealCDSMsg`；兜底 `#dealNotExistedComputeUserId`（取第一个在 `:322-325`） |
| 1 问卷匹配 | student-data | `DwsRenewalQuestionnaireConsumer`（刷花名册字段 + fan-out 明细）；`RenewalQuestionnaireStatusServiceV2#buildData`；调课后花名册状态重算 `RenewalQuestionnaireTransferConsumer`（唯一订阅 `TRANSFER_TOUCH_EVENT` 的入口）+ `RenewalQuestionnaireTransferSyncService`（同步调 teacher-tool 复制明细 → 重算 → 写花名册）+ `QuestionnaireAclService#syncTransferQuestionnaire` |
| 1 问卷匹配 | teacher-tool | 明细同步 Feign 端点 `QuestionnaireFeignController#syncTransferQuestionnaire` → `QuestionnaireServiceImpl#syncTransferQuestionnaire`（幂等复制，被 student-data 同步调用，自己不再独立消费调课事件） |
| 1 问卷匹配 | teacher-tool | 明细表 `gaotu.user_questionnaire_record`（无续班计划字段）；`UserQuestionnaireRecordDaoImpl#pageQuestionnaireInfoMultiByClazz`；`QuestionnaireServiceImpl#bindUserQuestionnaire`（只改 user 不改 clazz） |
| 2 主讲适配 | student-center | 统计 `SmallRenewalService#queryStatisticStudents:634-638`、搜索 `#searchUser:794-795`、权限 `SmallClazzUserPermissionFilterService:71-84`、班级筛选 `SmallFilterComponentServiceImpl:632/664`（四处 OR） |
| 2 主讲适配 | student-data | ES `ads_small_clazz_user`：`assistantAccountId`(单值) / `mainTeacherAccountIds`(班级级派生) |
| 3 扩科推荐 | product-server | 配置 `ExpandSubjectConfigDTO` / `NodeExtConfigVO`；B 端 `ProcessController#edit/list`、`expandSubject/*` |
| 3 扩科推荐 | student-data | 扩科科目 subtract：大班 `RenewalInfoServiceImpl#groupGradeCurrentRenewalSubjectMap`、小班 `SmallRenewalSubjectService#getRenewalSubjectInfo` —— **仅写花名册「大小班扩课科目」字段，与推荐无关** |
| 3 扩科推荐 | cart | **推荐 `ExpandSubjectRecommendService#recommend`（小班 :32 / 大班 :69，排除过滤加这里）**、选品 `RenewalService#productSelect` |
| 5 AI 配置化 | student-data | `AiDeptModuleSwitchConfig`（Apollo Map）+ `AiModuleSwitchService`（部门路径解析/匹配）+ `RenewalAiModuleEnum`(9，含 `9=意向预测`) / `RefundAiModuleEnum`(7，含 `manual_reason`)；透出 `AiModuleSwitchController` |
| 5 AI 配置化 | student-center | `AiModuleSwitchQueryService`（登录老师 accountId → feign，fail-open；`queryModuleSwitchTable` 下发 13 key，续班 5/6 合并为单 key `5`）+ `AiModuleSwitchFeignClient` + `AiCommonController#moduleSwitch`（`POST ai/moduleSwitch`）；已接 `RenewalClazzUserController` / `UserFeedbackController` / `RefundController` / `RenewalReasonServiceImpl#queryDetail` / `StageFeedBackService#edit`（manual_reason 写拦）|
| 4 数据落表（不做） | student-data | 两条既有模式：(a) MQ `job/sync/Sync*Handler`；(b) 直连 Doris Stream Load `DorisStreamLoadService` + `facade/job/dashboard/*DashBoardHandler` |

## 上线影响面

| 子需求 | Apollo | ES | MySQL DDL | MQ | 代课接口权限 | 跨团队 |
|---|---|---|---|---|---|---|
| 问卷匹配 | 是(7 档顺序 + 兜底开关) | 是(调班时重算问卷字段) | 否(teacher-tool 加列才需) | 是(新增消费 TRANSFER_TOUCH_EVENT，**仅 student-data 侧**) | 待定 | product-server / teacher-tool 归属待定；**teacher-tool-api 需先发正式版**（当前 `1.0.29-SNAPSHOT`，上线前定版发 RELEASE、同步升级 student-data-client 依赖）；**上线顺序必须 teacher-tool 先于 student-data**：两仓 master 都没有 `/feign/questionnaire/user/transfer/sync`，student-data 先上会 404 → 重试耗尽（`maxReconsumeTimes` 默认 5）进死信丢消息（2026-09-24 复审订正，原「顺序无关」结论作废） |
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


## 2026-10-21 最终补录（人工执行卡与发布编排实测）

详见 [[本次工作记录-20261021]]。20条case已补账号、班/辅导班、学员及关系、配置、操作和可见预期；53个执行场景保留。技能已固定人工优先规范，审计73条路由通过。发布编排实际执行一次，后端汇总57%，准出未执行、总门禁未过；历史79条告警仍未处理。DWS/GPS配置类型错误已补部署并验证UP/真实Bean/新pod无解析错误。AI及cart核心缺口已补验、临时数据配置恢复；未重算平台，不声明上线放行。


### 第二轮平台覆盖率已验证

21:25:57重算后：product92.11%（39333）、data81.44%（39334）、center83.43%（39335）、cart82.45%（39336）、order83.80%（39337）；后端汇总81%已通过，未改阈值或业务排除。前端空计划保护真实补验后单独重算中。准出未执行，不能据此声称生产放行。无关历史告警已停止处理，未经明确要求不建缺陷；三条误登记TAPD已置不解决，但天玑status2恢复操作未生效，7条分类残留已如实写在线文档。技能审计errors0/warnings0、75条路由0失败。


### 最终平台覆盖率

最终平台结果：后端汇总81%、前端汇总97%，两项覆盖率门禁均通过。后端product92.11%、student-data81.44%、center83.43%、cart82.45%、order83.80%；前端promotions97.91%（39331）、cronus100%（7/7，39338）。全部为新报告实际值，未改阈值或业务排除。准出仍未执行，USER_CASE/ALARM等其他门禁不等于通过。按用户要求，无关历史告警不处理、不新增缺陷。

Cronus补测走真实小班页面：唐稳01/tangwen01登录→清空续班计划→非续班期且不限本人→班级“测试触达”494625569468663808→学员5661436125“接口自动化测试”→下单，显示“缺少续班计划号，无法下单，请先选择续班计划”，不打开下单容器；两次均通过。完成后已恢复专用数学班、续班计划及7658127801，无订单/支付/购物车写入。
