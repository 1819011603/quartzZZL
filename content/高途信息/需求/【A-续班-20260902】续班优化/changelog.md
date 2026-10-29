---
title: 【A-续班-20260902】续班优化 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

---

## 2026-10-29 C 端分支合 release 并重发 dev-3（提测准备）

复用发布编排 **24038**（C端支持膨胀券）。用户要求 C 端分支先合 `origin/release` 再重发后提测。已推送：cart `feature-xuban-c-cart-addons` `30e7ccb9`→**`44e82e61`**（真合并；带入 `41fc524a` product-server-client 1.5.11 定版、`de2f693a` UserRenewalClazzExample、`3e1e366c` 扩科 release 合并）；order 同分支 `6a36d7a4b5`→**`50681b7073`**（fast-forward，分支提交本就已在 release）。5 后端重建发布 `test-gtbg-dev-3`（流水线 cart `1319574`、order `1319575`、order_task `1319577`、order-ad `1319578`、order-b `1319579`，均 SUCCESS），全部到目标版本且 Eureka UP。order/order-ad/order-b 首启因测试库 `Too many connections` 失败、重启后自愈（非代码问题）。自验通过：dev-3 券 8014（大班 availableScope=六年级语文 / 小班=一年级数学，price=10000，recommendType=3）与组合 51 正常展示。24038 前端 8 服务产物参数已补齐（`gaotu_m`/`tutu` 真镜像，其余占位 1），前端 8 站点本次未部署；同时把 5 后端的提测产物刷新为合并后镜像（cart `...-44e82e61-...`、order 四部署 `...-50681b70-...`），避免提测跑合并前代码。遗留：青舟「提测」步骤未见可调接口。

## 2026-10-26 dev-1当前批次完整回归

按用户最新要求集中dev-1验证23819。12个后端实际SHA/UP、101项本地测试、真实权限矩阵55项、AI业务19项、手填正反恢复、扩科正式保存与推荐、组合检索/数量/算价通过。新增会员组合27分测试支付432723431179944012及三个子单由独立DB回查确认；未续归因真实模型handle2并落库1950/type5。运行时配置、完整流程、手填与隔离购物车已恢复，没有发布Apollo或合并release。Chrome连接已恢复，扩科表单保存回显/必填及AI四项页面门控通过；B端页面仍有销售过滤少228条、会员/实物类型未知及页签顺序三处差异，T-23继续进行中，支付样本不代表班课归属/退款已验。飞书上线方案及P0需以本轮范围和基线补充，不拿旧全关配置覆盖现值。

## 2026-10-26 AI 模块部门开关口径改为「最具体部门优先」（TAPD 1122531521001484125）

唐稳反馈「组织节点 `66707677944472576` 未配 `user_portrait`，`moduleSwitch` 仍返回 true」。原实现为**并集继承**（老师主岗路径任一段命中即生效 = 本部门及下属部门），父部门 `6816343048455168` 配了 `user_portrait`，子部门即便只配了其他模块也照继承 → true。

**2026-10-26 用户拍板改口径（推翻上面的并集结论）**：改为「**子部门单独配置优先（覆盖父部门）；子部门未配置则继承最近的已配置父部门**」——即取老师部门路径上**最深命中**的那个配置部门，只用它这一份模块清单。方向与产品 GAIA 层「子覆盖父」一致。

实现：student-data `AiModuleSwitchService` 的 renewal / refund 匹配改为 `effectiveDeptModules`（最深段优先），commit `ebd93de9b`（分支 `feature-xuban-expand-exclude`），单测 32 项全过，部署 dev-1 待验。生效后 177071（叶子 `66707677944472576` 未配 user_portrait）→ `user_portrait=false`。

影响：PROD 两个 key 现未配置（未配=全量放开）→ 上线后行为不变，仅配置后按新口径；TAPD 1122531521001484125 由「不解决」改回跟踪。

## 2026-10-22 C 端购物车空老师参数

用户限定只改后端、前端不修改。promotion生成的基础链接已含 `seller_id=null`，cart在参数转换阶段失败；cart局部兼容已完成。进一步核实tangwen01当前CAS132658→employee8645正常，旧教师记录仍status1，认证层按账号/类型取首条且未限定当前employee，student-center据此取到离职身份CAS120805，promotion查空后直接拼null。按用户最新指示当前仅补教师启用状态筛选，撤回直接返回登录CAS的改动；旧教师仍启用，故上游身份问题未闭环，不能把当前CAS映射误判为缺失。

## 2026-10-21 当前范围与验收依据

用户明确以最新 PRD 为准、Banshan 仅参考，并要求在发布编排 23819 的核心流程和 P0 用例中补入下单优化（快速加购组合商品）。最终口径替代早期“不做快速加购”的决定；续班确认表最新 PRD 仍标注不做。指定 P0 文档 WpNuwpXLqi5JsskcmXFcwT2dnkg 原位修订。

## 2026-10-21（退费根因接口恢复：撤回 497479d3b 的删除）

### 🤖 Claude
- **冲突暴露**：飞书反馈 `/bgwApi/component/student-center/roster/refund/reasonType` **404**（金瑞琳报、张泽灵问用途）。根因 = 10-15 `497479d3b` 判「前端全局零调用」删了该展示接口 + `RefundService` 查询逻辑（约 200 行），但**前端已恢复的退费根因模块调的正是它**；`5c1465e57` 又连带删了其残留（`RefundService` 的 `Sets` import、`RefundEnumComponent#querySubRefundReasonName`）。与 T-13「不下线、纳入模块化」口径冲突 → 两边一合必空态。
- **决定**：**恢复接口**（而非重建）。`git revert 497479d3b` → `RefundController.reasonType` + `RefundService.reasonType/buildCommIdMap/transReasonType/summaryReasonType/queryDialog` + `RefundReasonTypeVO` 全部补回；再补回 5c1465e57 的两处残留；门控注释订正为 fail-open 口径（与其余退款接口一致），模块 code `refund_root_cause`。
- **提交**：student-center `9cd9c9f88`（`feature-xuban-expand-exclude`）已 push；`mvn8 -DskipTests compile` 通过。
- **部署验证**：青舟流水线 `1307906` → `test-gtbg-dev-1` **SUCCESS**；读回 `POST https://test-fuwu.baijia.com/bgwApi/component/student-center/roster/refund/reasonType` → **HTTP 200 / code 0 / data []**（无该学员 AI 摘要，正常空态）→ **404 已消除**（traceId `dce5fb3c-...`）。

---

## 2026-10-21（CASE-014 补齐：小班计划 → 排除大班在读）

### 🤖 Claude
- **CASE-014 端到端补齐 + 实跑通过**（`test-gtbg-dev-1`）。补齐半成品小班计划 `dcg-小班扩科排除-计划`（`586116340522184704`，type=2）：① 扩科节点 `586116659463352321`(type=6) `ext_config.excludeMode=1`（2026-10-20 当时 B端保存未落 excludeMode，曾直写数据库；2026-10-21 已验证 HTTP 保存 0/1，此旧现象不再代表当前版本，见 [[verify]] 2026-10-22 核对）；② 扩科商品 grade 16→11（对齐后置年级，否则扩科恒空）；③ 学员 `7658127801` 向前置小班课下单（`orderItem 432249582456931136`，6004 已支付）。后置小班课 `18314034380997207` + 续班关系本已存在。
- **实跑**：读侧 `listOtherModeInReadSubjects(7658127801,2,2026,"C")=[5]` ✅；cart 7 参 `getRenewalDetail` excludeMode=1 → 扩科**只出英语**、**语文被排除** ✅，=0 → 语文恢复 ✅。与 CASE-001 对称。详见 [[verify]] / 飞书 CASE-014 段。
- **坑（沉淀）**：cart 端到端须调 **7 参重载** `getRenewalDetail(...)`（`RenewalService:217`）才加载扩科配置；5 参重载（`:960`）不加载。product-server `listFeignMasterProcess` 只回 type=3 节点，扩科配置由 `buildCartAndExpandSubjectConfig` 单独拼。
- 遗留：`计划2` / `1020扩科小班` 仍空壳，未动。
- **补充 · 纯续补齐**：扩科排除好后 cart/B端只有扩科英语、无纯续数学。根因两处（dcg 半成品）：① 后置小班课 `18314034380997207` 没建商品 SKU（只建课+班）→ 后置班过不了 `saleStatus=40` 过滤 → `create_uniform_product` 补建 GPS 统一商品（6004，SKU=`586097025945298944`）；② 计划推荐节点 `renewal_link.product_type=2` → cart `renewalConfig.productType≠6004` → 纯续候选恒空，改为 **6004**。复跑 cart/B端 = 纯续数学 + 扩科英语 ✅。**排查要点**：小班纯续三件齐（后置班商品 SKU 40 / `renewal_link.product_type=6004` / course-center 续班关系）。

---

## 2026-10-21 最终补录（人工执行卡与发布编排实测）

详见 [[本次工作记录-20261021]]。20条case已补账号、班/辅导班、学员及关系、配置、操作和可见预期；53个执行场景保留。技能已固定人工优先规范，审计73条路由通过。发布编排实际执行一次，后端汇总57%，准出未执行、总门禁未过；历史79条告警仍未处理。DWS/GPS配置类型错误已补部署并验证UP/真实Bean/新pod无解析错误。AI及cart核心缺口已补验、临时数据配置恢复；未重算平台，不声明上线放行。


### 第二轮平台覆盖率已验证

21:25:57重算后：product92.11%（39333）、data81.44%（39334）、center83.43%（39335）、cart82.45%（39336）、order83.80%（39337）；后端汇总81%已通过，未改阈值或业务排除。前端空计划保护真实补验后单独重算中。准出未执行，不能据此声称生产放行。无关历史告警已停止处理，未经明确要求不建缺陷；三条误登记TAPD已置不解决，但天玑status2恢复操作未生效，7条分类残留已如实写在线文档。技能审计errors0/warnings0、75条路由0失败。


### 最终平台覆盖率

最终平台结果：后端汇总81%、前端汇总97%，两项覆盖率门禁均通过。后端product92.11%、student-data81.44%、center83.43%、cart82.45%、order83.80%；前端promotions97.91%（39331）、cronus100%（7/7，39338）。全部为新报告实际值，未改阈值或业务排除。准出仍未执行，USER_CASE/ALARM等其他门禁不等于通过。按用户要求，无关历史告警不处理、不新增缺陷。

Cronus补测走真实小班页面：唐稳01/tangwen01登录→清空续班计划→非续班期且不限本人→班级“测试触达”494625569468663808→学员5661436125“接口自动化测试”→下单，显示“缺少续班计划号，无法下单，请先选择续班计划”，不打开下单容器；两次均通过。完成后已恢复专用数学班、续班计划及7658127801，无订单/支付/购物车写入。

## 2026-10-20（退费 AI 模块依赖澄清 + 新建《退费 AI 模块依赖关系与灰度口径（待产品决策）》）

### 🤖 Claude
- 按代码实证澄清退费 AI 模块依赖：编排 `并行(tutoring/learning/satisfaction) → JOIN → 串行(refund_root_cause → service_suggestion)`；`refund_root_cause`/`service_suggestion` **触发上强依赖**三个并行模块全部完成（T+1 还等 `refundPredictionStatus.isSyncTaskFinish`）；**数据上** `refund_root_cause` 吃三并行 + prediction + 手填，`service_suggestion` 吃 `refund_root_cause`；`prediction`/`manual_reason` 独立。证据：`RefundReasonProcessManager`、`RefundReasonServiceImpl`/`RefundSuggestionServiceImpl`、student-center `RefundController`。
- `653bf30ef`（10-15）后模块关闭 = **跳过但视为完成**（handleCode 0→1），可按模块独立灰度；但**未解除依赖**、且配置为**部门级**（Apollo 非空则未配部门 AI 全关）。
- 新建飞书《退费 AI 模块依赖关系与灰度口径（待产品决策）》node `KR3RwV16gi6zf9km55cclT79nhf`（obj `Hq3KdB5GNo57XZx3dE9cnSJtn9w`，父=需求总入口），列 6 条待产品拍板。已回写 [[links]] + README。
- **退费根因加 Apollo 开关（默认不下线）（[[tasks]] T-13，待办）**：产品定「前端已删、后端加开关可配置下线，**默认不下线、保持现状**」。前端已删（aianalysisinformations 不调 `/roster/refund/reasonType`；student-center `497479d3` 删接口）；**PROD 后端仍在跑**——2026-10-19 日志实证 `RefundReasonProcessManager executeTask currentTaskEnum=REFUND_ROOT_CAUSE`、`RefundReasoningService 退费归因分析…reasoningEnum=REFUND_ROOT_CAUSE`、`handleCode=2`（镜像 `release-8e0938d2-20261019160601`，受 `refund.ai.gray.clazzNumbers` 白名单约束）。**方案（不删死代码，便于回退）**：student-data 加 Apollo 开关 `refund.reason.root-cause.enable`（**默认 `true`=不下线**），配 `false` 时 `RefundReasoningService` 命中 `REFUND_ROOT_CAUSE` 按「跳过但视为完成」返回 `handleCode=1`（同 `653bf30ef` 口径，不连累同流程）；END 编排/枚举不动。分支 `feature-xuban-expand-exclude`。
- **Apollo 现状澄清（订正 2026-10-20 早前误读）**：本需求（部门→模块开关）**未上线**，PROD **无** `renewal.ai.dept.module.switch` / `refund.ai.dept.module.switch`（不是「未配置=全量放开」）；两 key 仅存在于 TEST，现值：`renewal={"97349606689168923":[1..8],"6816343048455168":[1..9]}`、`refund={"6816343048455168":[tutoring,learning,satisfaction,refund_root_cause,service_suggestion,prediction,manual_reason]}`（TEST 里 `refund_root_cause` 仍开着）。
- **C-01 修复 + T-13 取消（2026-10-20 晚）**：cart 扩科排除「当前课程」学年学期**改取前置课**（原取后置课，与 PRD 不符）——cart `ResolveCurrentPreCourse`（取 `renewalPreCourseDTO.getCourseNumbers()`→`recommendContext.getCourseDTO`），提交 `4724b384`，`mvn8` 编译通过、部署 `test-gtbg-dev-1` eureka UP、验证通过（数学在读=春→排除；excludeMode=0→恢复）。**T-13 退费根因开关取消**（用户定不需要，本地代码已删，student-data 工作区还原）。补充验证：CASE-005 历史计划 excludeMode 空→无排除 ✅、CASE-012 B端下单推荐 `recommendProductList`=纯续+扩科 ✅。**已知既有口径**：小班在读表写入侧 `OdsSmallRenewalSubjectSyncService` 只过滤正价课+赠课订单，`未过滤 成人/纯预售` → 与 PRD 在读范围有出入（既有数据管道，非本次代码）。

---

## 2026-10-14（第二批收口：扩科「在读」补学年学期 + AI 门控漏网 + 清理）

### 🤖 Claude（对照 PRD 逐条核 diff 后修复）
- **扩科「推荐排除」在读口径补学年+学期（真缺陷）**：PRD 明确「在读范围 = **与当前课程相同学年+学期**、且授课模式/上课形式线上/非赠课/订单未全部退款/专题系列课/非纯预售/非成人」。原实现只按授课模式取对方模式在读、**漏了学年学期**，会把其它学期的历史在读学科当「在读」→ **过度排除推荐**。修复：
  - cart：`CourseDTO` 补映射 `schoolYearId/schoolTermId`（course-center `CourseVO` 本就有，原 `getSimpleCourseDTO` 未映射）；`ExpandSubjectRecommendService` 取当前（前置）课程学年+学期，经 `OtherModeInReadSubjectReq` 传给 student-data。
  - student-data：`RenewalInReadSubjectService` 按当前课程学年+学期过滤在读行；**学期格式差异**——课程学期是 OES(C/X/Q/D)，大班在读表即 OES、小班在读表是 CES(1/2/3/4)，故查小班表时把课程学期 OES→CES 转换；学年/学期缺失或无法映射（如复合学期 CU）时**保守返回空（不排除）**，避免过度排除。
  - 单测：student-data `RenewalInReadSubjectServiceTest` 13 条（含跨学年/学期剔除、OES→CES 转换、缺失降级、复合学期不排除）、cart `ExpandSubjectRecommendServiceTest` 7 条，全过。
- **AI 门控漏网**：`/roster/refund/reason`（手填退费原因展示数据 = `manual_reason` 模块）**未门控**，关闭模块后前端隐藏但接口仍返；已按 `manual_reason` 门控，关闭返空对象（防旧前端白屏）。student-center `479817691`。
- **AI 分析侧性能**：灰度未开始（部门配置为空）时也每条事件调 `resolveAssistantOrgPaths`（含 ACL），新增 `isRenewalGrayStarted/isRefundGrayStarted`，5 处分析侧调用点短路，避免无谓调用。student-data `f1817c92d`。
- **清理**：cart / product-server 误提交的 `.run/bridge-remote-*.run.xml`（含 pod IP）移出仓库并 gitignore；订正 `filterByOperationMode` 注释（行为是「宁可多排除」）、`AiModuleSwitchClient` javadoc（未配置=true 而非 false）。
- 提交：student-data `f1817c92d` / cart `7794a329` / student-center `479817691` / product-server `c1b9225ef`（均 `feature-xuban-expand-exclude`，已 push）。
- **仍待确认（未擅自改）**：① `refund_root_cause` 门控 `/reasonType` 但它不在下发名单 → 灰度后恒返空（Q-03，随前端基线下线？）；② `levelReasonAndHistory`（分层原因/变化）未门控，属另一需求；③ `RefundPredictionService` 对「风险升高通知」按 prediction 门控，是否算写侧；④ 复合学期（CU/QD…）课程的在读匹配降级为不排除，是否可接受。

---

## 2026-10-13（上线准备：问卷匹配 + 调课同步，发布计划 23716）

### 🤖 Claude
- 范围 = 发布计划 **23716**，5 个后端服务（teacher-tool / product-b / product-task / student-data / student-data-dws）。PROD 实地读回后补两个前置工单：
  - **DDL 工单 146826**：`ALTER TABLE questionnaire_record ADD COLUMN retry_count int(11) NOT NULL DEFAULT '0' COMMENT '未匹配重试次数'`（cluster 71 `gaotu-center-prod`，来自 `jdbc.gaotu.url`；Inception ok——带 `AFTER is_del` 报 warning，去掉后 ok）。须先于 product-task 上线（xjob 10160 每 10 分钟跑，缺列报错）。
  - **MQ 工单 90538**：PROD group `GID_student-data_renewal_questionnaire_transfer_prod`，**挂实例 `gaotu`(MQ_INST_..._Bay8En7I)** 而非默认 `gaotu-fuwu-prod`——因为订阅的 topic `gaotu_after_sale_event_prod` 就在该实例（发送/消费必须同实例）；状态 pending（直属leader审批）。
- **teacher-tool-api 定版**：`1.0.29-SNAPSHOT` → `1.0.29` RELEASE（deploy 到 Nexus releases，metadata 可见）；teacher-tool-service、student-data-client 两处依赖同步切 `1.0.29`，编译通过（TT/SD 均 EXIT=0），已 commit + push（teacher-tool `0d03f708`、student-data `f308ea83`）。
- PROD 复核：course-setting `compute.rule.name.list`/`all.share.questionnaire.renewal` 均未配（走代码默认 7 档）；student-data `after.sale.event.topic=gaotu_after_sale_event_prod`；`renewal.questionnaire.transfer.consumer.group` 未配（待 group 审批后配，否则用测试组名默认值）。
- **重试上限决策（2026-10-13，用户定）**：`no.compute.user.max.retry.count` **保持默认 3**——不改 Apollo、不降 xjob 频次。依据：实测 PROD `gaotu.questionnaire_record` 全表 85.65 万行、未归属（`computed=0 & manual=0`）4,595（0.54%）、**近 3 天未归属 = 0**；若加到 432（覆盖满 3 天窗口），续班高峰（历史峰值 16.5 万/天）会把匹配链路负载放大近 1 倍 → 否决。重试作用仅限「兜瞬时 RPC 抖动 + 补迟到数据」，外部不变则重跑多少次都一样。
- **两个澄清（2026-10-13）**：① 重试选择条件 `manual_user_id != 0 → = 0`（`f549f4070`）**确是修 bug**——原条件只挑「手工绑定过但自动没算出」的记录，普通未归属（`manual=0`）从不重试，与 job 注释/意图矛盾；② 该 key 的 Apollo **appId 是 product-b / product-task**（青舟 `apolloId`，按部署注入的 `app.id`），`course-setting` 只是工程 `app.name`。
- 待办：三仓提 MR（→release）；group/DDL 审批后配 Apollo `renewal.questionnaire.transfer.consumer.group`；发版按 teacher-tool → product-b → product-task → student-data 顺序。

---

## 2026-10-12（代码规范审查：5 仓 diff 对照「开发防返工检查」）

### 🤖 Claude
- 对 5 个 feature 分支 diff（student-data / product-server / teacher-tool / student-center / cart）按「开发防返工检查」（前置 / 契约 / 兼容 / 幂等 / 关键值配置化）审了一遍。**结论：整体规范**——开关 / 幂等 / 契约基本都做了 Apollo 化 + 兼容。**建议改**项已改并部署，**必改 / 需确认**项进 [[tasks]] Q- 待办。
- **建议改（已改 + 已部署）**：
  - product-server `63fd5b757`：重试批量大小 `500` 硬编码 → 外置 Apollo `no.compute.user.retry.batch.size`（默认 500）；删死字段 `ComputeParams.renewalNumber`（只 set 未 get）。部署 `test-gtbg-dev-3`（**product-task**）eureka UP。
  - cart `f18f9f52`：删 `pom.xml` 里指向错误 artifact 的误导注释（`ces-teach-product-api` 并非 `RenewalInReadSubjectClient` 契约）。部署 `test-gtbg-dev-1` eureka UP。
- **进 [[tasks]] Q- 待办（未擅动，待确认 / 点头）**：Q-01 计划级匹配灰度（`compute.rule.name.list` 默认 4→7 档）、Q-02 `retry_count` PROD DDL + job 并发、Q-03 `refund_root_cause` 半截门控、Q-04 展示 / 分析侧部门口径、Q-05 cart `product-server-client` SNAPSHOT、Q-06 `RefundController` 用 `manual_reason` 卡死整段通用写接口、Q-07 关闭返 `null` 白屏、Q-08 cart-client GMQ 丢 slf4j 排除、Q-09 cart 依赖重复声明、Q-10 `planCourseNumbersCache` key 缺 `projectNumber`。
- **必改（已改 + 已部署，eureka UP）**：
  - student-center `5ba12b10`（dev-1）：`RefundController` 退费 `edit` 门控由「整段卡片」收窄为**只拦 `refundReason`/`refundIntent`**（原会把同一通用编辑接口的改名/备注/跟进一起拒掉，且多入口行为不一致）；模块关闭返**空对象**而非 `null`（`course` + `RenewalClazzUserController` 用户画像/沟通摘要 2 处，防旧版前端白屏）。
  - cart `3594af88`（dev-1）：`cart-client/pom.xml` **恢复 GMQ 的 slf4j 排除**（`log4j-over-slf4j`/`slf4j-log4j12`）+ **删掉重复声明的 `course-center-client`/`ces-teach-product-api`**。
  - product-server `9a9b4350`（dev-3/product-task）：`planCourseNumbersCache` key **补 `projectNumber`**（同问卷号在不同 project 下解析的前置课程不同，原 key 会跨 project 复用错结果）。
- **暂不改（Q-11）**：student-data `InnerBackController` 的 2 个调试接口是给**提测覆盖率门禁（发布编排 23716）**加的、标注「上线前删除」——现在删会掉覆盖率卡提测，**留到上线前删**（[[tasks]] Q-11 盯着）。
- **评估后缓改（未动）**：product-server「两处计划内前置课程解析统一」「`NamePlanRuleService` 先 limit 20 再按范围过滤」、student-center「模块 code 集中」——涉及行为 / 框架，待确认。

---

## 2026-10-12（二）（开关表 5/6 合并 + 写拦下沉 + 意向预测例外）

### 👤 我（用户定）
- **「已续/未续跟进」PRD 里是 1 个模块**：开关表对外把 5/6 两个 key 合并为单 key `5`（值 = 后端模块 5「未续跟进」‖ 6「已续总结」任一开启）；续班对外 key 变 `1,2,3,4,5,7,8,9`（共 **13 key**）。后端分析仍是 scene 5/6 两个场景，不合并。
- **意向预测（续班 9 / 退费 prediction）**：读侧按模块门控（`predictLevelReason`、开关表 key `9`/`prediction`）；写侧（含回溯）是「算法真表 → Sync job 落库 + 刷 ES」的数据管道、不挂模块门控（**写全量**），**不需要专门回溯**。旧意向预测链路（`SyncRenewalLiftSnapshotHandler` 等旧 xjob）已停用。
- 历史续班计划 `excludeMode` 有默认值（现状即默认），无需刷数。
- **扩科老数据兼容不刷数**：`excludeMode` 存 `node_config.ext_config`（JSON，非列）；推荐侧 `excludeMode != 1`（含 null）即不排除、行为同上线前；产品要「老计划打开即【无排除】」→ 在 B 端回显处对 null 兜底为 `0`（`ProcessService#convertNodeConfigVO`，product-server `2d8ae7ccb`），**不刷数**。

### 🤖 Claude
- 扩科老数据兼容（回显兜底 `0`）：product-server `2d8ae7ccb`，桥调 `convertNodeConfigVO`（含 `expandSubject/forceBuy`、不含 `excludeMode`）→ 回显 `excludeMode:0` ✅；product / product-task / product-b 已部署 dev-1。
- `manual_reason` 写拦下沉到通用编辑入口 `StageFeedBackService#edit`（bizName=refundReason/refundIntent），覆盖 `/roster/refund|stageFeedback|renewal|examAnalysis/edit` 4 个入口（原只在 `RefundController`）；`/user/feedback` 读写一致（写也按 7 拦）；`/roster/refund/course` 关闭返空对象。
- student-center `40e5f24a7`（单测 5/5 过、已 push）；student-data **撤销**「scene 30→9 / `RenewalLiftReasonHandle` 门控」——那两处是旧死链路。

---

## 2026-10-12（AI 配置化·开关表接口：前端对齐 + 数据接口兜底）

### 🤖 Claude
- 与前端反讲《续班优化 202609-前端反讲》（jinruilin）定稿对齐：新增 **`POST ai/moduleSwitch`**（无入参，按登录老师判定），下发 **14 key**——续班 `1..9`（新增 `9=意向预测`，枚举补 `INTENTION_PREDICTION(9)`）、退费 `service_suggestion/prediction/manual_reason(新增)/learning/tutoring`（枚举补 `manual_reason`）；`refund_root_cause`、`satisfaction` **不下发**（前者随前端基线分支下线、后者无前端展示模块）。bizType=1/2 各调一次 `queryModuleSwitch`（`moduleCodes` 传空）后过滤。
- 语义：**一部门未配 / 登录缺失 / 查询异常 / 缺 key 一律 `true`（fail-open）**，与前端「key 缺失或请求失败按 true」一致。注：origin 上 `a3a4d7cb5`（`AI 模块开关查询改为 fail-open`）已改同一文件+加测试，本轮**以远端为准**，只保留新增的开关表方法，避免覆盖（另补开关表单测 2 条）。
- 数据接口兜底（防旧版前端/直调）：`evaluateQuery` 用户反馈按 **7**（关→`[]`）、`managerEvaluate` 写按 **8** 拒绝、`/roster/refund/analysis` 改按 **`service_suggestion`** 且关闭返 **`{}`**（原返 `null` 旧版前端白屏）、`/roster/refund/edit` 写按 **`manual_reason`** 拒绝、`ai/renewal/reason/detail` 按 `reasonType` 看 **5/6**。
- **挂起**：`ai/clazzUser/predictLevelReason`（续班 `9` / 退费 `prediction`）门控——该接口在**另一分支** `feature-predict-level-reason`（独立需求「分层变化与分层原因」），用户定「两需求不同批上线，等 predict 上线、需求5 合流后补」。
- 提交/部署/自验：student-center `7d74dbf8f`（push）、student-data `6ae6bc798`（push，`feature-xuban-expand-exclude`）；部署 `test-gtbg-dev-1` 双 pod eureka UP；真实入口 `POST /component/student-center/ai/moduleSwitch` 返回 14 key，与 student-data 原始判定一致（登录 177071：renewal 全 `false`、refund `manual_reason:false` 其余 `true`）。

---

## 2026-10-10

### 🤖 Claude
- 【调课同步】定位两处缺失（ES 花名册「提交时间」「预报名科目」）：① 真实售后调课完成只发 `SUCCESS_EVENT`+`TRANSFER_SUCCESS_EVENT`，`TRANSFER_TOUCH_EVENT` 仅当 `after_sale_transfer_record.need_touch=1` 才发（`TransferCoreService:474`），而 student-data consumer 只订阅后者 → 同步根本没触发；② 即使触发，`writeCommitStatus` 也只写状态(+提交时间)，从不写意向派生字段；且意向按 (clazzNumber,userId) 存、新班无意向行。
- 决策（用户定）：consumer 的 `tag` 改 Apollo 可配 `renewal.questionnaire.transfer.event.tags`，**实际代码默认只订 `TRANSFER_SUCCESS_EVENT`**（`48ff645e2`，`296cf844` 幂等 TTL 5s）；调课时把原班 `renewal_intent_info` 行复制到新班（幂等）；`writeCommitStatus` 一并回写意向派生字段。student-data `af1ca55d1`（feature-xuban-match-opt），已部署 test（envInfoId 2）。
- 造数坑（重要）：acl 桥发事件必须用「3 个字符串参数 + body 传 JSON 字符串」；传 `[topic, [tag], {object}]` 会被桥匹配到 `(String,String,String)` 重载，tag 变 `[TAG]`(带方括号)、body 变 `Map.toString()`，消费端 tag 不匹配收不到（2026-10-10 实测踩中）。
- 【提测核查】飞书《提测 P0 用例》doc 来源是**已停用**的 banshan 49607（23 条）；现行维护集是 **49647**（功能用例 record 70798 = 77 项，已执行 32、约 36 未执行）。提测编排 23716 仍挂 49607 → 需 QA 确认并迁 49647。
- 【提测核查】base `test` 泳道已跑 feature 分支（student-data `296cf844`/teacher-tool `9c98a14a`/product-task `35f2a80e`）。桥直调 `syncAfterTransfer` 复制明细成功；但 `FuwuOnsMqProducer` 发**合成**调课事件（SUCCESS tag）2 次均未被消费 → 与 playbook 的「MQ 断点」一致，E/G 模块在 test 须走真实售后。doc §四「发 TRANSFER_TOUCH_EVENT / 不带泳道也行」已过时（现默认只订 `TRANSFER_SUCCESS_EVENT`）。详见 [[verify]]「提测 P0 用例核查」。

---

## 2026-10-08（问卷匹配三仓 diff 复核 + 桥方法单测/端到端抽测）

### 🤖 Claude
- 【问卷匹配】按 `feature-xuban-match-opt` 三仓 vs `origin/master` 逐项核对需求，并用 product-b 桥复测（详见 [[verify]]「全量 diff 复核 + 桥方法单测」）：7 档顺序（**计划级手机号先于班内姓名**）、多命中取最小 ID、跨班兜底 `get(0)`、计划级姓名精确匹配、调课同步同班短路/必填校验均通过。
- **分支携带项（用户 2026-10-08 确认保留）**：student-data 分支含 `70c32f0f1 fix(presale-coupon): 膨胀券未配置预报名活动降为 warn`（`PresaleCouponServiceImpl`），与问卷匹配无关、仅在该分支；**明确保留，不作为问题**。其余 3 仓 30 个文件均属问卷匹配 / 调课同步。
- 小瑕疵：`ComputeParams.renewalNumber` 赋值后无规则读取（死字段）；`student-data-client` 依赖 `teacher-tool-api` 升 `1.0.29-SNAPSHOT`（上线前须定版发 RELEASE）。

## 2026-09-23（AI 模块配置化：部门口径修正 + 扩科真 bug；下午：四项补验 + 花名册顺序风险订正）

### 👤 我
- 【AI 配置化】部门口径由「课程部门」改为**老师（二讲）主岗虚拟组织架构部门**：PRD 要「本部门及下属配置了，二讲才可用」，用课程部门会让同课程下别的部门老师也可见、不隔离。展示侧取登录老师，分析侧取该班辅导老师。
- 【AI 配置化】~~未配置 = 关闭~~ → 2026-09-24 用户订正为**灰度语义**：配置为空 = 全量放开，配了部门才按部门灰度；开关不可判定 fail-open。
- 【扩科】选品 `productSelect` **不需要**排除过滤（反讲原「选品也按排除范围」口径作废）。

### 🤖 Claude
- 实测 `StaffDto.mainPostOrgPathFromRoot` 是 **`_` 分隔的 org number**（accountId `177071` → `12345_4959407036876800_6816343048455168_66707677944472576`），`matchDept` 分隔符 `/`→`_`、保持分段精确匹配（防数字 id 前缀误命中）。
- student-data `12e41da47` / student-center `84ec1b732` 已部署 `test-gtbg-dev-3` 并验证：门控（命中/未命中）、分析侧 E2E（`handleCode=2`）、展示侧真实入口全过，见 [[verify]]「部门口径修正」。
- 修掉扩科 cart→student-data Feign 因 cart fastjson 全局 SnakeCase 致请求体发 `user_id`、恒返回空的真 bug（`96e334b8`，**线上同样会坏**）。
- **补验**：退费归因 E2E、退费预测 E2E 均过；调课调班真发 MQ 端到端 + 幂等过；圈选侧门控函数级过。
- **订正结论（花名册顺序）**：`renewalQuestionnaireStatus` 在小班花名册宽表 `ads_small_clazz_user`，由**问卷回收事件消费者直接写**；实测小班花名册回溯 `BackAdsSmallClazzUserHandler` **不重算**该字段（插明细+回溯后仍为 2）→ 先填后调时 B 的状态**不会自动更新**，是**真实顺序风险**。原「宽表重建时会推导成 COMMIT」的说法未证实，作废。
- **R-04 线上 Apollo 核实**：appId `course-setting`；PROD/TEST 均未配置 `compute.rule.name.list`（走代码默认 4 规则）与 `all.share.questionnaire.renewal`（默认 `true`）；`share.questionnaire.renewal.numbers` PROD=`[16091330849213120,15927198832724032]`、TEST=`[]`。

---

## 2026-09-21（反讲 v0.4 全量核验 + 产品口径确认）

### 🤖 Claude
- **反讲按 `origin/master` 全量核验**（4 组并行 subagent、~90 处 path:line），升 v0.4 订正 8 处：`UnificationSwitchService` 实际在 student-center、`RenewalInfoServiceImpl` 最终 subtract 为 :236-238、`refactorMainTeacherStudentInfo` 无角色分支、`QuestionnaireRecordService:171-177` 是 DB 查询非"解析"、`ProcessController`/`NodeExtConfigVO` 行号偏移、`DwsRenewalQuestionnaireConsumer` 消费在 :187、退款口径两套都在 student-data、**移除 origin/master 不存在的 `predictLevelReason`**。
- 补「目标」正文并把误置于 Non-goals 的目标条目归位；子需求2 统一为「现状 OR 已满足 PRD、本批无需开发」；问卷匹配 MySQL DDL 由「否」改「是」；补《发问卷整体技术方案》7 项现状/风险（归因在 product-task、`compute.rule.name.list` 线上未配置、共享开关默认 true 短路、扇出各班意向可能不同、`recordId` 缺唯一索引、兜底表无人读、前置课程列表三口径）。
- 新建飞书**《待产品确认清单》**（21 条，按 5 子需求分组）https://gaotuedu.feishu.cn/docx/L2yrdOPEAoIOMux1JLXcGtR4nde ，挂在需求总入口下。

### 👤 我（产品口径答复）
- 子需求1：①同名/一号多孩**不做产品侧解法**，按规则写；②改派**在问**→ 后经王永诗确认**不用做**（手工绑定维持现状）；③「同一手机号多次提交只展示最新」**EES 已有**（已核 teacher-tool `QuestionnaireConsumer#handleRenewalQuestion`）；④明细班级名称/ID 字段**已有**；⑤teacher-tool **不加**续班计划列。
- 子需求2：⑥下单优化本期**不做**；⑦主讲适配**确认无需开发**；⑧统计口径**实时**（《小班课字段+指标》指标页 6-9 行）。
- 子需求3：⑨【推荐排除】为**新增配置**（不合并）；⑩粒度 **续班计划级**；⑪下单页选品 + B 端 `recommendProductList` + C 端**均按「纯续+扩科推荐范围」展示**；⑫「在读」口径**不变**（只是推荐商品少几个），退款状态口径不变。
- 子需求5：⑯配置入口**先用 Apollo 后端配置**（先搞简单点）—— 续班/退费各一个 `Map<虚拟架构部门, Set<模块>>`（如 `{虚拟架构部门A:[1,2,3], 虚拟架构部门B:[1,2,3,4,5]}`）；王永诗曾建议用 GAIA 统一，用户 2026-09-21 定"先 Apollo，能按部门配就行"；⑰部门 key = **contains**；⑱「用户反馈」「主管点评」算 AI 模块；⑲无需枚举映射；⑳「不展示」落点 = 前端仓 `ees/aianalysisinformations`（分支 `feature-refund-reason-20260825`）的接口；㉑关闭模块后历史数据按**隐藏**。
- 子需求4（13-15 数据落表）：本批不做，仅登记，未答。

### 👤 我（飞书群 · 王永诗答复）
- 「问卷匹配规则改成续班计划维度，手工绑定只能改学员、不能改班级，要改吗」→ 王永诗：**不用**。
- 「AI 模块配置化要做新页面配权限，还是用 GAIA」→ 王永诗：**能用 GAIA 就用这个，统一**。
- 用户后续定：AI 配置入口**先用 Apollo 后端配置**（"先搞简单点"），GAIA 页面后续再议。

### 👤 我（内部 / 评审口径）
- 跨仓承接方：product-server / teacher-tool 改动**归本团队**。
- 调课调班同步承接方：**student-data**；旧班 A 来源 = 报文 `LlsTransferCourseMessageDto.originalOrderInfo.clazzNumber`（已核实该字段存在）。
- 【扩科】就是**加个过滤**，但位置订正：**扩科推荐本来就在 cart 算**（`ExpandSubjectRecommendService#recommend`，小班 :32 / 大班 :69，只按年级匹配）→ 过滤加在**这两个重载**里；`recommendProductList` 只是把 cart 结果转成 B 端列表。**student-data 的扩科科目 subtract 只服务花名册「大小班扩课科目」展示字段，不是推荐收口点**（此前反讲把它当推荐收口点，属误判，已订正）。
- 【扩科】深挖现状：cart 扩科算法 = 读扩科配置 → `collectStudentPostGrades` 取后置年级 → `studentPostGrades.contains(recommend.getGrade())` 年级匹配，**仅此一步**。**难点**：cart 现有 context **没有"在读学科"**（全仓无在班/在读查询），拿「对方模式在读学科」要么 cart 复刻 PRD 8 条件（口径漂移），要么由 student-data 透出（建议）。已把「现状算法 + 改动难点」写进反讲「详细设计·扩科推荐」。
- 【扩科】**「在读」口径核实（订正）**：PRD 9 条件里 student-data 现有在读科目链路只覆盖 6 条（非成人 / 专题系列课 / 不含赠课标签 / 非纯预售 / 相同学年学期靠 yearTermGrade 分组 / 授课模式靠数据源），**缺「上课形式为线上(operationMode)」与「订单未全部退款」2 条**（operationMode 过滤只在 student-data 别的链路有）。此前记"口径不变/均已具备"有误，已订正。
- 【扩科】**「在读科目」数据来源核实**：来自 **student-data 自己的表**（小班 `dws_small_clazz_user_subject`、大班 `dws_fuwu_clazz_user_subject`），查询走本地 DAO，不是调外部接口；表的原料才是外部的（进/退班 MQ `gaotu_subclazz_student_event_test` + 课程中心 + 订单）。→ 「对方模式在读学科」集合可由 student-data 直接透出给 cart。已写入反讲「详细设计·扩科推荐」。
- 【AI】部门→模块配置放 **student-center 的 Apollo**（问卷匹配的 `compute.rule.name.list` 仍需在 product 公共 namespace `gt.product-public-app` 新增）。
- 【问卷匹配】重试 Job = product-server `QuestionnaireRecordService#dealNotExistedComputeUser`（每轮重跑 3 天内 `computed_user_id=0` 记录）—— 是否同批改造仍待评审。
- 【AI】部门匹配**有现成先例**：`RenewalAiCommRealTimeSelectHandleService#getDeptAiConfig:214-224` 即 `departmentPath.contains(configKey)` + `@ApolloJsonValue Map`（部门取课程/班级 `courseDO.getDepartmentIdPaths().get(0)`）。待定：①用班级部门还是老师部门（展示侧要同口径）；②`contains` 子串匹配对数字部门 id 会前缀误命中，需带分隔符。已写入反讲「详细设计·AI」。
- 【扩科】在读科目表**可能不准 & 回溯手段**：表由 MQ+外部数据拼成（消息丢失/乱序、课程缓存过期、退款未同步、判定变更后未重算、is_del 不一致）。回溯：大班 `dws_fuwu_clazz_user_subject` → XXL-Job `BackClazzUserSubjectHandler`（按 clazzNumbers 或 beginId/endId）；小班 `dws_small_clazz_user_subject` → 手动接口 `/gps/manual/back/smallClazzUser/subject` 等（校验 `/gps/manual/check/smallClazzUser/subject`）。已写入反讲。
- 【扩科】风险应对**结论：加开关、不新写回溯逻辑** —— 配置本身即 per-计划开关，再加全局 Apollo 降级开关（脏数据一键回退【无排除】）；回溯沿用现成 Job/接口、不内联进推荐链路（C 端高频 + 口径重复）；要自动只做离线对账。已写入反讲「风险管理」。

### 🤖 Claude（订正产物）
- 飞书清单已按答复回填 ✅（1/3/4/5/6/7/8），并在顶部加「确认进度」callout；反讲「待确认项」#2/#3/#5 与 14-20 段同步回填。
- 本地 `README.md` 新增「已定（2026-09-21 产品/数据确认）」小节并从「待确认」移出已闭环项；`links.md` 登记清单文档；`tasks.md` 补 R-01~R-04。

---

## 2026-09-18（晚 · 扩科推荐重新纳入）

### 🤖 Claude
- 用户更正：**子需求3 扩科推荐要做**（此前误判为不做）。范围由 1/2/5 改为 **1/2/3/5**。
- 派 2 个只读 agent 重新探索扩科推荐，产出精确证据并补进反讲（现状 / 方案对比 / 详细设计 / 接口 / 影响面 / 风险 / 待确认）：
  - 配置侧：`ExpandSubjectConfigDTO`（product-server-client，字段 expandSubject/forceBuy/allowDuplicate/beginTime/endTime/recommendList）、B 端 `NodeExtConfigVO.extConfig`、表 `node_config.ext_config` + `renewal_expand_subject_recommend`；B 端 `ProcessController#edit/list/expandSubject*`。**三仓 grep `推荐排除/excludeSubject` 零命中 → 该字段不存在，需新建。**
  - 计算侧：student-data 扩科集合收口点 = 大班 `RenewalInfoServiceImpl#groupGradeCurrentRenewalSubjectMap`（最终 subtract）、小班 `SmallRenewalSubjectService#getRenewalSubjectInfo`（:474-483）。PRD「在读」8 条件中 5 项已有过滤器，仅「授课模式/上课形式线上/订单未全部退款」3 项需新建。
  - 推荐侧：cart `RenewalService#getRenewalDetail:217`→`ExpandSubjectRecommendService#recommend`（**仅按年级过滤**）；B 端 `recommendProductList`/`recommendClazzList` 结果来自 cart；**下单页选品与推荐不共用扩科逻辑**。
  - 短链：`recommendUrl` 短链实际走 REACH-SERVICE（README 原说 PROMOTION-B 只对 appInfo 成立）。
- 反讲补：标题/摘要改 1/2/3/5；新增子需求3 现状+方案+详细设计（各带 mermaid 图）；接口变更补扩科（`/product-b/b/renewal/process/edit` 保存、`/process/list` 查看回显、`expandSubject/*`、cart 推荐/选品、B 端 recommend*）；影响面加扩科行；风险/规避/待确认各补；变更历史加 v0.2；依赖的接口补 cart C 端推荐 + B 端老师推荐。
- 用户补充接口：C 端推荐 `GET /cart/web/renewal/cart`、B 端老师推荐 `POST /product-b/b/renewMaster/recommendProductList`、B 端 `POST /product-b/b/renewal/process/edit`（保存）与 `/process/list`（查看）也要改。

### 👤 我
- 「3 要做 我弄错了，再加一个，都改一下」；给出推荐链接、cart C 端 curl、B 端老师推荐接口、B 端 process/edit 接口；给出扩科 PRD 原文与链接（LYCYwqS7ziljApknUlbclPSrnzh），指出「扩科班级不区分大小班可随意选，所以才加配置」。

### 🤖 Claude（读 PRD 原文订正扩科口径）
- 读扩科 PRD 原文，解除歧义：**【推荐排除】不是手填清单，而是扩科推荐为【是】时可编辑、默认空、单选的枚举【无排除】/【排除不同授课模式在读】**；选后者按「不同授课模式在读学科」动态排除（当前课程大班→排小班在读学科；小班→排大班在读学科）。问题根源=扩科班级/商品不区分大小班可随意选。B端/C端按「纯续+扩科推荐范围」展示。
- 反讲订正：现状加问题根源与跨模式重复推荐；方案一改为 PRD 精确口径；详细设计改动点 1/2/4 重写、补 B端/C端展示适配；待确认 11 改为「过滤收口层」、12 改为「选品是否同过滤」，删除已解决的粒度/维度问题。

---

## 2026-09-18（晚）

### 🤖 Claude
- 产出【A-续班-20260902】续班优化 技术反讲（子需求 1/2/5 合并，评审前草案）：https://gaotuedu.feishu.cn/wiki/EC45wOefUi0buMkO7O0cipp9nEc（docx `GiqcdeCakoAsvfxH43accvD4nHf`）。含交接摘要、背景/名词/关联方、现状链路、方案对比（每子需求方案一/二+建议）、详细设计与 `path:line`、接口清单、影响面、风险、发布计划、待确认，7 张 mermaid 图。
- **位置规则（用户明确）**：反讲必须挂在**需求总入口 `Qox8wFcmHiXBgnkxFBtcd82gnsh`**（【A-续班-20260902】续班优化）下面，不是个人空间根目录。已写进 skill `tech-review-doc`。
- **删除此前 5 个「现状·改动·风险」子页面**（问卷匹配/主讲数据+下单/扩科推荐/数据落表/AI模块配置化）。核对出入：主讲页仍写"快速加购/续班确认表属新功能、要做"（实际下单优化不做、底层已存在）、权限字段名写成 `EsGaiaMapping`（实际 DB 表 `es_query_config`）；AI 页 8 模块清单与"6+2"口径不一致、"关闭后历史数据待定"（已定隐藏）。
- 建 skill `tech-review-doc` 并把「换会话能续接」「反讲挂原需求节点下」定为硬要求。

### 👤 我
- 要求：只做 1/2/5；写飞书技术反讲（一篇合并、评审前草案）；反讲要清晰、有图、有代码位置/接口/影响范围；换 AI 会话后能接住上下文；建一个专门写技术反讲的 skill；反讲要挂在原需求下面；旧的 5 个子页面可删。

---

## 2026-09-18（晚 · 代码深挖）

### 🤖 Claude
- **【主讲数据+下单】组合商品加购底层链路 master 已存在**（order `CombinedProductCartHelper`/`CartService#getProductInfos` 的 `COMBINE_PRODUCT` 分支、product-server `CombinedProductFeignController#searchNoAuth`/`ProductEsDao` 组合过滤、student-data `CartEventService#resolveCombineProductClazzNumbers`/`CartEventConsumer`），原"快速加购组合商品属全新功能"作废；"快速加购"具体新增什么待需求方明确。续班确认表确实无实现。
  - **【AI模块配置化】`AiAppSceneEnum` 仅 6 个(1-6)非 8 个**；退费侧 `RefundReasoningEnum` 5 个 + `RefundPredictionService` 1 个 = 6 个吻合。续班第 7/8 个模块 PRD 明细本地无存档。
- 同时核实接口/消息准确路径与行号（反讲素材）：`/feign/questionnaire/match`、teacher-tool `/feign/questionnaire/user/page/multiByClazz`、`/orderComponent/b/cart/addCart`、`ai/clazzUser/userPortrait` 等；product-server 确认不消费 `TRANSFER_TOUCH_EVENT`，student-data `DwsAfterSaleSyncConsumer` 只处理退费 tag。
- 待确认新增 5 项（快速加购定义、续班AI 8 模块清单、部门 key 口径、展示侧 type3/4 无接口、UserFeedbackController 归类）。
- 建 skill `tech-review-doc`：固化反讲骨架、接口七列表、影响面六项、图规范，并把「换会话能续接」定为硬要求（正文最前必须放交接摘要）。

### 👤 我
- 要求：只做 1/2/5 三个子需求；写飞书技术反讲（一篇合并、个人空间新建、评审前草案）；反讲要清晰、有图、有代码位置/接口/影响范围；换 AI 会话后能接住上下文；先派 agent 深挖代码再汇总问缺口；并建一个专门写技术反讲的 skill。

---

## 2026-09-18（下午）

### 🤖 Claude
- 确认【问卷匹配优化】的 product-server + teacher-tool 改动归属给我，产出逐文件改动清单（见 README 子需求1「改动清单」）：product-server 7 项（ComputeParams 扩字段、解析前移、3 条 plan 级规则、Apollo 6 级顺序、去掉 `subclazzDTOS.get(0)`、无绑定号路径收敛计划、fan-out 留给 student-data）；teacher-tool 3 项（续班计划列按需、改派能力、明细查询无需改）。
- 关键结论「范围扩大能否匹配正确」：**能解决"人在同计划其他班"（调班/发错链接）+ 手机号精确匹配**；**不能解决同名/亲属手机号歧义**（取 userId 小仍是猜），范围越大歧义面越大。plan 级必须限定"同一问卷的课程"而非全计划课程，否则会匹配到不同问卷的班。
- 明确"改不了/改不全"的边界：①同名/一号多孩根因（输入信息不足，算法无解，需产品决策）；②存量错配按 PRD 不回溯；③明细 A/B 两行 fan-out 在 student-data，不在我手上；④调课调班同步若由 product-server 承接需新增 consumer + DAO 方法；⑤teacher-tool 加续班计划列需 DDL；⑥规则改动影响大班+小班全部续班问卷匹配，回归面大。
- **用户纠错并订正**：`TAG_Subclazz_Transfer` 是「转辅导班」（同班内换班主任，`SubclazzStudentMqDto.type=7`，消息只带一个 `clazzNumber` + old/new `subclazzNumber`），**不是** PRD 说的"班级 A 调课到班级 B"。真正的调课调班事件 = topic `gaotu_after_sale_event_test` + tag `TRANSFER_TOUCH_EVENT`（`LlsTransferCourseMessageDto`），目前**只有 reach-service 消费**（`TransferCourseClazzTriggerConsumer`，"只给触达使用"）；student-data `DwsAfterSaleSyncConsumer` 虽订了该 topic 但只处理退费 tag。故调课调班同步是**要新增消费**，此前"调班事件已存在且 student-data 已消费"的结论作废。已同步 README（设计草案/待确认/上线影响面/必须知道的坑）、飞书子页面、tasks T-09。
- 飞书 5 个子页面顶部各加一行跳转：「对应需求：<原始需求 wiki 节点>　所属需求文档：<需求总入口>」。
- 飞书导航补链接：①「需求」目录页写入指向需求文档【A-续班-20260902】续班优化的链接 + 子页面列表；②需求文档页追加「原始需求文档」区，列 5 个原始需求 wiki 节点 + 3 份参考 PRD + 跨班错配分析文档。
- 按用户要求完成 5 个子需求的飞书归档（个人空间）：建「需求」目录 → 把需求总入口移入 → 5 个子页面（问卷匹配 / 主讲数据+下单 / 扩科推荐 / 数据落表 / AI模块配置化）各写「现状·改动·风险·待办」。顺带**订正 links.md 里主讲/扩科/数据落表 3 个 wiki node token 互相错配**（node_token 与 document_id 对不上，已用 `wiki +node-get` 实测改正）。
- 按用户要求在飞书建档：父文档「【A-续班-20260902】续班优化」+ 子页面「问卷匹配优化：匹配逻辑现状·改动方案·风险」（写入匹配逻辑现状/改动方案/待办清单/风险点）。**注意落在个人空间 `my_library`（space 7485951460694425602）**——原需求 wiki 空间 `7521677387233722372` 无建节点权限（131006）。链接与 token 见 links。
- 同步本地：tasks.md 加 T-06~T-09（问卷匹配开发待办），links.md 加飞书入口与 token，README 导航加飞书总入口。
- 性能评估（3 个风险点）：①**重试 Job 放大**——`dealNotExistedComputeUser` 每轮重跑 `computedUserId=0` 且 3 天内的记录（100/批、16 线程），改"不唯一→0"后这批记录永远匹配不上、每轮重复处理，叠加规则链 4→7 条，负载上升，必须同步改造重试策略；②每条提交最坏 RPC 从 7-8 升到 11-12 且串行（`compute` 顺序 for，MQ 仅 5 线程），群发场景会排队；③plan 级姓名规则最贵（班内版已 scroll 2000/批 + listByUserIds），建议改走 `listByStudentName`(限100)+计划过滤。手机号/亲属号 plan 级成本可控（500/批，候选集小）；`compute.rule.name.list` 在 Apollo 可单独降级。
- 深挖【问卷匹配优化】现状：定位到真正匹配实现不在 student-data/student-center，而在 **product-server**（即 Feign 名 `product-b`）——绑定层 `QuestionnaireService#match:928`、记录归属层 `ComputeUserService` 规则链(`OriginUser`/`Mobile`/`Name`/`RelationId`，全部限定班级内)、跨班兜底 `QuestionnaireRecordService#dealNotExistedComputeUserId:253`（混候选取第一个 `subclazzDTOS.get(0)`）。订正原 README「6级规则本仓未实现需新建匹配服务」的表述：规则链已存在且 Apollo 可插拔，改造是扩规则而非从零新建。
- 补 teacher-tool 侧：明细表 `user_questionnaire_record` 无续班计划字段，查询 SQL 只按 `type+project_number+clazz_number+user_id` 过滤；手工绑定只能改 user 不能改 clazz。
- 调课调班同步订正：student-data `SubclazzUserSyncConsumer` 已消费 `TAG_Subclazz_Transfer`，但只刷续班状态/科目，未刷问卷字段。
- 用户提供飞书分析文档《续班问卷跨班错配问题：现状、成因与产品解法》，与代码结论互相印证（其描述的"扩范围+混候选+取第一个"即 `dealNotExistedComputeUserId`）；已登记 links。可借鉴点：根因论据、6级规则仅"少猜错"不能归零、"待认领+改派"与存量修复是需求未覆盖项。

### 👤 我
- 要求弄清【问卷匹配优化】的现状/改动/影响/代码改动，并提供此前写的跨班错配分析文档供借鉴。

---

## 2026-09-17

### 🤖 Claude
- 建档：付星/马胜在飞书一次性转发5个续班优化wiki链接，要求初评并记录需求。最初误判为5个独立需求分别建了5个目录，用户澄清"这五个需求是一个需求"后合并为单一目录 `续班优化(秋季批)`，旧名保留在 frontmatter `aliases` 里防止按旧目录名搜索时找不到。
- 5路 Explore agent 并行完成两仓库(student-data/student-center)代码定位，结论已整合进本文件「涉及的代码」按子需求分节呈现。
- 核对5份PRD原文后修正：子需求2补记续班确认表(P1)与快速加购组合商品(P0)、删去"等需求方补充方案"的失效待确认；扩科推荐历史数据口径改为条件句（当前不回溯）；补记调课调班同步前提与场景、各子项P级、PRD可点链接。
- 重跑两仓库代码定位核查（基准 `origin/master`，工作区在另一需求的 `feature-xuban-pre`）并抽查复核，订正 6 处关键结论：问卷状态刷新非唯一挂载点(共4条路径)、`StudentSubclazzQuestionnaire` 是零引用孤立实体、多次提交去重在 `pageQuestionnaire` 非 `pageQueryQuestionnaire`、`mainTeacherList` 由 `WideSmallClazzTeachingBinder` 绑定、`CartEventService` 是业务 Service 非 ACL 适配器、数据落表另有直连 Doris Stream Load 先例；并补实 C端推荐/选品在 cart、快速加购落 product-server+order、续班确认表改动面在 contentReport+reach-service。

### 👤 我
- 在飞书里转发5个续班优化需求wiki链接，要求初评并记录需求，同时看下应该怎么做、做下设计。
- 澄清：这五个需求是一个需求，文档只要记录在一个文件夹下。

- 2026-10-23：用户确认勾选行为与原商品一致，撤回新增跨年级记忆；原productSelectGrade清空本计划选择属于预期，保留组合详情修复和原8014适配。前端只按当前年级清单下单。
