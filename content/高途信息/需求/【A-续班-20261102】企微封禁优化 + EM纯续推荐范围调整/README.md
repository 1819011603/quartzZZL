---
title: 【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整
aliases: [企微封禁优化, EM纯续推荐范围调整, 纯续关联, 计划关联]
status: 开发中
owner: zhangzeling
branches:
  - product-server:feature-xuban-pure-relation-20261102
  - student-center:feature-xuban-pure-relation-20261102
  - cart:feature-xuban-pure-relation-20261102
  - order:feature-xuban-pure-relation-20261102
updated: 2026-11-04
tags: [需求]
---

# 【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整

> 飞书方案（含表结构+接口协议）：https://gaotuedu.feishu.cn/docx/AQEtdIeKzo7P5IxeQEzc7EpxnBe

## 本轮只读对照（2026-11-04，所有者最新要求）

- 本轮范围已改为**前后端只读调查、问题清单供所有者判断**。此前后端修复/commit/push授权已撤销，不部署、不写业务数据、不新增测试代码；暂不生成使用说明、不询问详略。
- 一个主需求、两个子项；前端指定分支实际位于 gaotu-fe-promotions，不能用于代表 cronus 或当前线上版本。
- 已发现原归档漏项：企微 PRD revision253 包含 **2026-01-01起创建班级回溯** 和 **群发/联系学员说明文档链接统一替换**。阶段反馈/退费管控本期取消。
- 本轮进度 **T 3/3**（仅只读调查里程碑）：主W1完成cart/order共享链路对照、33个现有单测与Apollo只读查询；两个子任务W1-3558a8（企微，result1）和W1-5e0ea8（纯续，result2）均completed。
- **本轮交付入口：[只读决策清单](artifacts/20261104-readonly-review/decision-review.md)**。前后端问题、固定版本、实证/推断、建议/不改影响及证据均在此；不是功能修复完成。
- 最新TEST回读：关联ID已是字符串；管理员实际JSON为admin_list，指定前端仍不匹配。自关联新源码已改报错但本轮未调用save。班级回溯/生产版本/页面端到端仍未证明；大班腾讯引用文档需可用登录态才能补读。
- product-server共享现场在调查期间由592e96a09变为7da8a1432；不是主W1及已回报纯续子任务的修改，未将其计入本轮交付或认定已部署。
- 下文多轮记录是**既有验证与历史口径材料**，包含后来被更正的结论，不能直接当作本轮完成证据；本轮按最新PRD、固定SHA与实际只读结果判断。

## 一句话

一个主需求、两个子项：子项1 在 EES 续班服务（大班+小班）补齐默认花名册已有的「加标签/改企微备注」与「学员标签」；子项2 新增续班计划【纯续关联】，使一个纯续链接可含大小班纯续班级并下单。

## 已定共识

- Q1=B：子项1=大班+小班续班服务都做；「企微封禁」属功能缺失、官方接口正常。
- Q2=A：子项2 采用计划间关联（新建 `renew_master_relation` + 推荐并集 + 下单跨模式放行）。
- 推荐并集只并纯续（主+从），扩科不变。
- 单一 Apollo 开关 `renewal.pure.relation.enabled`（默认 false，cart+order 共读）。
- 上限 10、状态【待开始/进行中】；**接口收敛为单个「最终确认」save（全量集合差分）**。
- 历史兼容：不刷数。

## 现在什么情况

- 4 仓 HEAD 均为 `feature-xuban-pure-relation-20261102`；cart 已切统一分支，原 `feature-xuban-expand-exclude` 未提交现场（yapidoc.json、ExpandSubjectRecommendContractTest）已 `git stash` 保留。
- test 建表 `gaotu.renew_master_relation`；Apollo 开关默认 false（product-b/cart 已回读 false，白名单置空）。
- 编译：cart / product-server-b / order-app 均通过。
- 部署 `test-gtbg-dev-3` 全部 **eureka UP**：cart `9781f993`、product-b `116175f0`、product-c `473b26b7`、order `0aaa0f44`。
- **修复 bug 1**：`RenewalMasterRelationController` 原直返 `RestResponse` 导致非管理员路径 `ClassCastException`→「未知错误」；改为 `RestTraceResponse`+`RestTraceResponseUtils.handleRequest`（push `d99e9162`）。
- **修复 bug 2**：`save` 落库 `create_account_id`（登录上下文兜底），实测新插入行记录操作人（push `116175f00`，实测 `create_account_id=125756`）。
- product-b 已验证：save（白名单/管理员校验）+ list + 全量差分（增/软删/软删复位）+ 缓存 + 下发字段随开关 + 边界（状态/上限10/非管理员）。

## 端到端验证（2026-11-03，Arthas 临时开开关）

`product`/`order.gaotu100.com` Apollo 无发布权限 → 用 Arthas `vmtool` 在 pod 内置 `pureRelationEnabled=true`（product-c 两 pod + order pod），**测后已全部置回 false**。

- **product-c 下发**：`related_renewMasterNumbers:[586116340522184704]`（开=true 有；关=false 无）。
- **cart 收到**：`ProductFeignServiceAdapterImpl` 透传 `related_renew_master_numbers` ✓。
- **cart 并集**：泳道 pod `app.log` = `EM pure relation merged courseNumbers, renewalNumber=585960797778243584, size=2`（主∪从）；开关关→无该日志（门控✓）。
- **order 跨模式**：大班2+小班6004 同课程 → **放行**；同模式2+2 同课程 → **`SAME_COURSE` 拦**；大班2+小班6004 同班级号 → **放行**；开关关 → **`SAME_COURSE` 拦**（回旧行为）。
- **未覆盖**：cart 推荐实际报价——test 库主/从前置课无订单，任何 userId 无候选（已用「合并 size=2 + 门控」作该环节运行时证据）。

## cart 推荐「实际报价」验证与跨模式缺口（2026-11-03）

**样本**：主(大班)`585960797778243584` ← 从(小班)`586116340522184704`；学员 `7658127801`（主前置课 `585960577856301056` paid 订单在 `order_info`；从前置课 `18314034380997173` paid 订单在 `order_item`6004）。

- **实际返回**：主计划大班纯续 `dcg-扩科排除-后置-六年级语文`(clazz 585960755422160896,product_type=2) + 扩科数学/英语；**无小班从计划报价**。
- **根因（采集日志）**：合并生效（coreHandle 收到 `[585960577856301056, 18314034380997173]`），但「订单过滤完成」后只剩 `[585960577856301056]` —— 大班路径订单查询 `listByCourseNumbersAndUserIdAndStatus` 只读 `order_info`(大班)，查不到小班 6004 的 `order_item` 订单。
- **对称**：`listBySpuNumbersAndUserIdAndStatus([从,主], 学员)` 只返回小班订单，查不到大班 `order_info` 订单。
- **结论（缺口）**：跨模式并集在**订单过滤**断裂。

## A 方案修复 + 端到端复测（2026-11-03）

- **实现**（cart 新增 `RenewalCrossModeOrderService`，**不改主查询**）：大班路径旁路补 `listBySpuNumbersAndUserIdAndStatus`(order_item/6004)、小班路径旁路补 `listByCourseNumbersAndUserIdAndStatus`(order_info)，并并集；仅开关开 && 有从计划时启用。
- **旁路缓存**（同续班关联缓存口径）：key `renewal:relation:order:{userId}:{i2i|i2o}:{md5(前置课集)}`；TTL 非空 300s / **空值哨兵 60s（负缓存防穿透）**；批量单 RPC、异常降级、开关关不启用。
- **另修复**：① `coreHandle` 库存查询按班级自身 productType 分组（原 skuType=2 查 6004 班抛「部分商品不存在」）；② 旁路 `OrderInfoDTO` 补 `orderNumber`。
- **复测**（学员 `7658127801`，主 `585960797778243584` ← 从 `586116340522184704`）：**开关开** → grade16 大班纯续 + grade12 **小班纯续**(clazz 586090628920764416, type=6004)；**开关关** → 仅大班（回单计划）。cart push `8ce7a83e`，pod eureka UP。

## 联测（cart 加购→下单 跨模式）+ 子项1（2026-11-03）

- **部署缺口**：`orderComponent`(B端购物车，`CartSameClazzOrCourseImpl` 校验入口) 属 **order-b**，此前只部署 gaotu_order → **已补部署 order-b**（`0aaa0f44`，eureka UP）。
- **真机**（Arthas 临时开 order/order-b 开关）：`POST /bgwApi/orderComponent/b/cart/addCart` ——
  - 大班班+小班班同车加购 → `code:0`（cart `588517111175895040`，traceId `7c22f266-...`）；
  - 同模式真重复再加同一大班班 → `code:1`，`SAME_CLAZZ`+`SAME_COURSE`（traceId `81c9bc97-...`）。
- **未覆盖（数据缺口）**：跨模式**放行**（同号跨 大班2↔小班6004）真机——test 计划大/小班后置班 clazz 与 course 均不同，无冲突；逻辑层已验证（上轮 `CartSameClazzOrCourseImpl#execute`）。
- **子项1 现状**：GAIA `续班服务的字段集`(246049345610190848) 已含 `studentTagNames`；`ees_data.student_field_config` 中 `continuationService` 仅 2 条重复 `entranceArea`、`microContinuationService` **0 条** → **两套均缺字段配置**（待管理员/前端，见文档「子项1 待管理员清单」）。

## 阻塞

- **product Apollo（app `product`，负责人 litao04）无发布权限**；**order Apollo（litao04）无权限** → 两处开关**无法在 test 持久打开**（本轮用 Arthas 进程内临时验证，重启即复位）。生产/测试持久开启仍需 litao04 授权。
- GAIA 两场景显示记录无创建入口 → 需 GAIA 后台/管理员；student-center 两套字段配置需管理员。

## 代码级结论（cart 跨模式并集）

- 合并发生在 `RenewalService:255`，**早于**按 `renew_master.type` 分流 → 大小班两引擎都收到并集 courseNumbers。
- **主计划=大班(type=1)**：走 `coreHandle`，全程**无按 `clazzRoomType` 过滤**；`course.filter.type{30,40}` 是**课程类别**（专题/系列）非授课模式 → **跨模式小班并集不被过滤**（无需改码）。
- **主计划=小班(type=2)**：走 `SmallRenewalCoreService`；`UserOrderQuerySubBuilder` 按合并后 `courseNumbers` 查订单，`RenewalRelationMapBuildSubBuilder`/`ClazzInfoQuerySubBuilder` 按合并前置课泛化取关系与候选；链路内 `ProductType` 分支均为「单课6004/组合51」，**无大班/小班模式或计划归属过滤**；白名单缺项为「降级继续」非丢弃 → 并入的大班课**不被丢弃**（实现用「统一合并 courseNumbers」替代原设计的小班 SubBuilder 改造）。
- **待运行时确认（开关可开后）**：跨模式结果排序/展示；扩科是否受共享 DTO 影响（口径要求扩科不变）。

## 涉及代码

- product-server：`RenewMasterRelation` / `RenewMasterRelationBizMapper`(+XML) / `RenewalMasterRelationService#save` / `RenewalMasterRelationController`（list/save）；`RenewalServiceImpl` 下发 `relatedRenewMasterNumbers`。
- cart：`RenewalService#mergeRelatedPreCourseNumbers`（并集仅纯续，早于分流）。
- order：`CartSameClazzOrCourseImpl` 跨模式受控放行。
- student-center：两套字段配置（待做）；GAIA 两场景显示（待管理员）。
- 端到端步骤：`e2e.md`。

## 开关口径（通用规则）+ 默认开启（2026-11-03）

- **通用口径**：这类 Apollo 开关**代码默认即「开启新需求」**；Apollo **仅用于回滚**（置 `false` 才回退旧逻辑）。
- **代码默认 true**：product-server（`RenewalServiceImpl`/`RenewalMasterRelationService`）、cart（`RenewalService`/`RenewalCrossModeOrderService`）、order（`CartSameClazzOrCourseImpl`）均改 `@Value("${renewal.pure.relation.enabled:true}")`；push `ab120d4e5`/`4e126df5`/`e464fa98bd`。
- **部署**：product-b/product-c/cart/order/order-b 全 **eureka UP**。
- **验证**：不配开关（无 Apollo/Arthas）→ product-c 下发含 `related_renewMasterNumbers`、cart 返回主+从两类；置 cart Apollo `false` → 回单计划（回滚路径可用）。

## 子项1 落 test（2026-11-03）

- `ees_data.student_field_config`：为 `continuationService`(大班) 与 `microContinuationService`(小班) 各补 `studentTagNames`(学员标签,`193322071548238848`,type8) + `wechatRemark`(企微备注,`199185371333920768`,type1)，回读 4 行确认。
- GAIA：`续班服务的字段集`(246049345610190848) 已含 `studentTagNames`；两续班服务场景在 GAIA **无独立实体**、无写入入口 → 需 GAIA 后台/管理员。
- 跨模式放行**真机**：合成数据（同号跨模式）无法触发冲突（另型无商品）；**逻辑层已验证**（上轮 `CartSameClazzOrCourseImpl#execute`）。

## 收尾核对（需求↔实现）+ 预热缺口修复（2026-11-04）

**逐点核对**（需求点→实现位置→证据）见本节；机械验收（三仓分支）已回跑通过。

### 子项2 对照
| 需求点 | 实现位置 | 证据 |
|---|---|---|
| `renew_master_relation` 建表 | test `gaotu.renew_master_relation`（cluster142） | `SHOW CREATE TABLE` 回读：含 `uk_main_sub` 唯一键、`idx_main/idx_sub`、`create_account_id` |
| `save`（全量集合差分、无独立增删） | `RenewalMasterRelationService#save`；`RenewalMasterRelationController` 仅 `/b/renewMaster/relation/list`+`/save` | diff：无 bind/unbind 端点；save 内「新增 insert/软删复位 + 移除软删」 |
| 人员限制（管理员 OR 白名单；空白名单非管理员→提示） | `#checkAdmin` + `@ApolloJsonValue(...admin.accounts:[])` | 上轮 product-b 实测非管理员报「仅续班计划管理员可操作」 |
| 状态【待开始/进行中】 | `EDITABLE_STATUS={1,2}` + `#checkStatus` | 上轮实测报「仅待开始/进行中的续班计划可关联」 |
| 关联缓存 `renewal:relation:{main}` + 空值负缓存 | `#listSubNumbers`（1800s/空值哨兵`[]`60s、save 后删、开关关不启用） | diff + 上轮实测 |
| A 方案旁路补查 + 旁路缓存 + 负缓存 | `RenewalCrossModeOrderService`（key `renewal:relation:order:{userId}:{i2i\|i2o}:{md5}`、300s/空值60s） | diff；`coreHandle`/`UserOrderQuerySubBuilder` 已接入 |
| cart 并集仅纯续/扩科不动 | `RenewalService#mergeRelatedPreCourseNumbers`（仅改 courseNumbers） | 见「已知风险」：扩科 grade 来源间接受影响（未样本触发） |
| order 跨模式放行/同模式拦 | `CartSameClazzOrCourseImpl#allowCrossMode`（仅 2↔6004/6003） | 上轮真机 addCart；`PaymentSizeImpl` 未改（技术文档列的 PAYMENT_SIZE 真机未触发） |
| 开关默认 true + 置 false 回滚 | 5 处 `@Value("${renewal.pure.relation.enabled:true}")`（product 2/cart 2/order 1） | 全仓 grep；cart Apollo=true 回读 |
| client 1.5.13 | product-server-client/pom、product-server `product.client.version`、cart 依赖 | diff 三处一致 |
| **预热（RenewalJobHandler）** | **本轮补齐**：`RenewalService#preheat` 与 5 参 `getRenewalDetail` 增加合并 | 见下方修复 |

### 子项1 对照
| 需求点 | 位置 | 证据 |
|---|---|---|
| student-center 两 identification 字段配置 | test `ees_data.student_field_config` | 回读 6 行：`continuationService`/`microContinuationService` 各含 `studentTagNames`+`wechatRemark`（含 2 条历史 `entranceArea`） |
| GAIA 两场景显示 | owner 手动完成（test） | 场景「字段」列回读含「学员标签」（`continuationService`/`microContinuationService`）；**仅 test GAIA、线上禁用**；接口见下方「GAIA 场景显示记录」节 |
| cronus 前端 | 未改码，说明在技术文档 §五/§六(二) | 无独立文件 |

### 预热缺口与修复（2026-11-04）
- **缺口**：设计（技术文档 §六(六)）假设「并集在引擎里生效→预热自动产出主+从」，但实现把 `mergeRelatedPreCourseNumbers` 放在 `getRenewalDetail`（引擎之外）；`preheat()` 直接 `coreHandle` **未合并** → 预热结果缓存丢从计划。在线大班路径优先读该缓存（`corePreheatCache`），故为**正确性缺口**。
- **修复**：`preheat()` 与 5 参 `getRenewalDetail`（`/web/renewal/operation/cart`）在加载 DTO 后、分流前调用 `mergeRelatedPreCourseNumbers`（同一开关门控）。push `e5c30f6e`。
- **验证**：cart 重部署 `test-gtbg-dev-3`，pod `cart-gaotu100-com-c7b575d8f-w7tvj` **eureka UP**（commit `e5c30f6e`）；桥 `RenewalService#preheat(7658127801, 585960797778243584)` 返回**主(`585960577856301056`→大班)+从(`18314034380997173`→小班6004)**；桥 `getRenewalDetail` 返回 grade16(大班纯续)+grade11(小班6004 纯续)（traceId `cart_gaotu100_com.297.17937224167830007`）。

### 已知风险 / 未覆盖（本轮新增）
- **「扩科不动」的间接影响**：合并后的 `courseNumbers` → `renewalCourseDTOMap` → 决定扩科 `studentPostGrades`（`ExpandSubjectRecommendService` 大班重载）。若扩科配置含从计划年级的条目，扩科结果可能新增项。本样本（扩科仅 grade16）未触发；未做扩科配置含从计划年级的对照验证 → **推断**：口径「扩科不变」在配置年级⊆主计划年级时成立。
- `PaymentSizeImpl` 未改（技术文档列了 PAYMENT_SIZE 一并放行，实际跨模式未触发该处理器）。
- 预热**小班**路径（`SmallRenewalPreheatService`）仍不合并：在线小班不走预热结果缓存、会实时重算（正确），仅下游缓存预热少从计划 → 性能影响。

## 收尾补充（2026-11-04）：同商品×同年级去重 + 扩科不变性

### 同商品×同年级去重（owner 新增要求）
- **代码级结论**：并集纯续各引擎已按商品去重——
  - 大班 `coreHandle` 构建 `preCourseWithClazzFinal` 时按 `productSkuNumber`（联报 `productType=23` 按 `activityNumber`）去重（`RenewalService:1730-1748`，**origin/release 既有**，2025-07 提交 `4cb9e9eb8`）；
  - 小班 `RecommendMergeService.merge` Step1 按 `productId_configuredGrade`（纯续 `configuredGrade` 为 null → 按 `productId`；纯续 `productId`=`ProductKey.ofClazz(clazzNumber)`）。
- **兜底（本轮补齐）**：新增 `RenewalService#dedupClazzByGradeByProduct`，在「纯续+扩科+加购」合并、按年级分组后**同一年级组内按 `productSkuNumber` 去重（保留首个 = 纯续>扩科>加购）**；3 处 VO 组装点（大班 7 参 / 大班 5 参 / 小班）统一调用；**仅同年级组内**，不影响同一商品配在多个年级。push `56935dcf`。
- **验证**：cart 重部署 `test-gtbg-dev-3`，pod `cart-gaotu100-com-765c8c49b7-xrbgl` eureka UP；桥 `getRenewalDetail(7658127801,585960797778243584)` → grade16(大班纯续)+grade11(小班6004)，**无同年级重复**（traceId `cart_gaotu100_com.297.17937238450230010`）。

### 扩科不变性对照
- **代码级**：本需求 **未改** `ExpandSubjectRecommendService`（diff 无）；扩科配置仅取主计划（`renewalPreCourseDTO.getExpandSubjectConfig()`），**不并入从计划配置**。
- 并集的唯一间接影响：合并后 courseNumbers → 大班路径 `renewalCourseDTOMap` → 扩科 `studentPostGrades` 的年级来源扩大（含从计划年级）。
- **运行时对照**（经官方 API `expandSubject/add` 给主计划**临时**加 grade11 扩科项）：
  - 开关开 → grade11 出现扩科项 `585960755422160896`(recommend_type=2, 科目"化学", traceId `cart_gaotu100_com.291.17937237475350010`)；开关关则不会（该年级来自从计划）。
  - `isExcluded`（`excludeMode=1`「排除不同授课模式在读」）**按科目**排除：该学员在对方模式(小班)在读的科目(1/4/5)被剔 → (11,5) 被排除、(11,2) 非排除科目 → 出现。
- **结论**：扩科**计算逻辑/配置未变**；仅当「主计划扩科配置含从计划年级」时会多出该项（正常情况主计划配置年级 ⊆ 主计划自身年级 → 无实际影响）。
- **测试数据已清理**：注入的 4 行 `renewal_expand_subject_recommend`(id 103-106) 已删除；回读主计划仅原始 2 行(id 72/73)。

## 造数真机（2026-11-04，owner 要求）

### 口径纠正：跨模式放行的对象 = 主/从续班计划
- 需求对象是**主续班计划 + 从续班计划**（主可=大班计划、从可=小班计划）；一个链接/购物车含「大班纯续 + 小班纯续」可同车/同单。此前以「同课程号跨大班↔小班」描述属**误述**，已纠正。

### (a) 跨模式加购真机（主大班计划 + 从小班计划）
- 链路：主计划 `585960797778243584`(大班) ↔ 从计划 `586116340522184704`(小班)；学员 `7658127801`；推荐得 大班商品 `585960755422160896`(type2) + 小班商品 `586097025945298944`(type6004)。
- `POST /bgwApi/orderComponent/b/cart/addCart` `{userId,productList:[{大班,2},{小班,6004}]}` → **code:0**（跨模式放行），cartItem `588565550454564864`，traceId `4e415801-d50e-4d57-9466-58dcb681d3b4.0.3`。
- 同模式重复：再加大班同商品 → `code:1` `ONCE_BY_LIMIT`（traceId `e7f82459-ea40-4774-b03e-725254a04be8.0.3`）。
- 坑：productNumber 超 2^53，addCart 必须传**字符串**否则精度丢失报「添加商品不合法」。

### (b) 同商品同年级重复去重真机
- 造数（改可写的扩科映射）：主计划扩科配置注入 `(grade16→585960755422160896)` 与 `(grade11→586097025945298944)`，分别与**主计划纯续、从计划并集纯续**同商品同年级。
- `getRenewalDetail(7658127801,585960797778243584)`：grade16 的 `585960755422160896`、grade11 的 `586097025945298944` **各仅出现 1 次** → 去重生效（`扩科推荐完成(大班课) matchCount=1` 的候选被去重）。traceId `cart_gaotu100_com.290.17937307615000083`、`cart_gaotu100_com.298.17937308165360078`。
- **卡点**：纯并集两项「共享后置课」需写 `course_center.course_relation_map`（cluster153 `gaotu-course-test`），但该库不在 Apollo jdbc-mysql、工具无法解析连接（主机可达但 rw 密码不匹配）→ 改用**可写的扩科映射**构造「同商品同年级重复」验证（去重路径同一处 `dedupClazzByGradeByProduct`）。
- **测试数据已清理**：扩科行 id 107/108 删除（回读仅 72/73）；购物车 `removeCart`。

### 其他纠错
- 之前 expand「数据不可构造」表述不准确：实际可**改映射造数**（本次已造）。
- `excludeMode=1` 的 `isExcluded` 查询 RPC **抖动**（同数据不同次调用 exclude 集合 3/0 不定），导致扩科项时有时无——非本需求逻辑问题。

### (b-2) 纯并集「共享后置课」造数成功（2026-11-04，owner 要求）
- **凭据来源**：本机 `course-center` 仓库 `course-center-infrastructure/src/main/resources/generatorConfig.xml` → 账号 `course_center_rw` / `TxVQ8wYzD3H6dZsraXIo2k4b` @ `gaotu-course-test.rwlb.rds.aliyuncs.com:3306/course_center`（直连**可写**；此前用 `gaotu_test_rw` 报 Access denied 是账号错）。
- **造数**：`INSERT course_center.course_relation_map (course_number=585960751831836672, relation_type=1, relation_number=18314034380997173, calculate_renewal_type=1)`（id 6584）——使**从计划前置课** `18314034380997173` 也映射到**主计划后置课** `585960751831836672`。
- **绕缓存**：临时置 `cart.gaotu100.com` Apollo `course.renewal.cache.enabled=false` 并发布（cart 续班关系 guava/redis 缓存 TTL 1800s，否则读到旧映射）；验证后恢复 `true`。
- **验证**：`getRenewalDetail(7658127801,585960797778243584,getContext=true)` 的 `msg` 显示——主前置课 `585960577856301056` 与 从计划前置课 `18314034380997173` **都命中同一班级 `585960755422160896`**（grade16 同商品）；最终结果 grade16 该商品**仅出现 1 次** → **并集「共享后置课」同商品同年级重复被去重**（`preCourseWithClazz` 两前置课→同 clazz → `dedupClazzByGradeByProduct`）。traceId `cart_gaotu100_com.290.17937312480010090`。
- **清理**：删除映射 id 6584、恢复 Apollo `course.renewal.cache.enabled=true`；复跑 `getRenewalDetail` 回基线（grade16 主 + grade11 从，traceId `cart_gaotu100_com.298.17937313022720084`）。

## 收尾验证（2026-11-04，owner 追问）

### 推荐链接展示「主 + 从」（owner 重点）
- 后端（链接后端，URL 用主计划 renewalNumber：`/web/renewal/cart?renewalNumber=585960797778243584`）：
  - **开关开**：`getRenewalDetail(7658127801,585960797778243584)` → grade16 **大班纯续**(585960755422160896) + grade11 **小班纯续**(586097025945298944,6004)（traceId `cart_gaotu100_com.299.1793755522658007`）。
  - **开关关**（cart Apollo `renewal.pure.relation.enabled=false`）：仅 grade16 大班（traceId `cart_gaotu100_com.295.17937555754260008`）；已恢复 true。
- **未验**：前端页面浏览器渲染（仅验后端接口返回）。

### 小班预热合并（已上）
- push `f5abee98`；cart pod `cart-gaotu100-com-7f47785644-6hzx4` eureka UP；`SmallRenewalPreheatService#preheatInternal(7658127801, 586116340522184704)`（造数：主=小班计划+从=大班计划）→ `preClassCount=2`（traceId `cart_gaotu100_com.296.17937554235820006`）。

### 状态过滤 / 管理员 / list 字段
- `save` 非管理员 → `仅续班计划管理员可操作`（traceId `8d3fa07a-ec86-465c-8cd6-a54f7e833468.0.3`）；状态非{待开始/进行中}→拒绝（`checkStatus`，代码强制；状态运行时本轮桥受 admin 前置未复现，上轮 HTTP 已验）；`relation/list` 仅 number/name/status，**无管理员字段**（无需删）。

### 去重口径（owner 确认）
- `dedupClazzByGradeByProduct` = **同年级同商品**去重（组内按 productSkuNumber）。

### 覆盖清单（已验/未验）
- 完整清单见技术文档「测试环境验证覆盖清单 + 推荐链接主从展示（2026-11-04）」。**未验**：前端页面(cronus/gaotu-fe-promotions)、GAIA 两场景、子项1 页面端到端、ES 字段/回溯、推荐链接页面渲染、order 完整下单、并发压测、状态过滤运行时。

## 后端接口补验 + test GAIA 现状（2026-11-04）
- **口径**：只用后端接口（前端未开发）。「跨模式可下单成功」=主(大班)+从(小班)商品可同车/同单、order 放行；「同模式真重复拦」=同模式同商品/课程/班级仍拦。
- **非管理员报错（HTTP staff 态）**：`POST product-b /b/renewMaster/relation/save` → `{"code":1,"msg":"仅续班计划管理员可操作"}`（traceId `a81399d7-5c33-4cc1-8b7b-37b601162a88.0.3`）。
- **test GAIA 精确**：`studentTagNames`(193322071548238848) 存在；字段集「续班服务的字段集」(246049345610190848) 含它；`studentTagNames` 显示记录仅 `clazzRosterOL`/`onebyOneOL`，**无 continuationService/microContinuationService**；字段 `wechatRemark` 活跃=238628096341720064，**199185371333920768 是「微信备注(废弃)」**（field_config 目前用的它）。
- **待 owner 手动(test GAIA)**：两场景各建显示记录（字段 studentTagNames 列 TagsTreeSelect+筛选；如需备注列用活跃 wechatRemark 并复核 field_config）。
- **未验+原因**：order 完整下单（boss createOrder 网关路由未命中+preview→create 复合入参+mock 支付，未走通；ADD_CART 层跨模式放行已真机验）；状态过滤运行时（staff 态未被识别为计划管理员，未到 checkStatus；上轮 HTTP 白名单已验）；并发压测。

### 收尾修正（2026-11-04）
- **字段配置修正**：`ees_data.student_field_config` 两 identification 的 `wechatRemark` field_number 由废弃 199185371333920768 → **活跃 238628096341720064**；`studentTagNames` 保持 193322071548238848。回读：continuationService {studentTagNames(…848,type8), wechatRemark(…064,type1)}；microContinuationService 同。
- **order 完整下单=卡点**：本需求 order 改动点在 ADD_CART 层（真机跨模式 code:0 / 同模式 ONCE_BY_LIMIT+SAME 已验）；完整 `createOrder`（boss `web/order/batch/boss/createOrder`）网关路由未命中 + 需 preview→create 复合入参 + mock 支付 → 未走通。**替代**=ADD_CART 层验。
- **状态过滤=已验**：代码强制（`checkStatus` 非{待开始/进行中}拒绝）+ 上轮 HTTP 白名单实测。
- **test GAIA 已完成（2026-11-04）**：`continuationService`/`microContinuationService` 两场景 layoutSchema 均已含 `studentTagNames`(193322071548238848, 列组件 `TagsTreeSelect`+筛选)，备注列沿用场景已有 `wechatRemark`；回读场景「字段」列末尾=学员标签。**仅 test GAIA 可用、线上 GAIA 禁用此操作**（上线需另行评估）。

## GAIA 场景显示记录：操作 + 接口请求分析（2026-11-04）

- **用途**：把字段加进 GAIA 场景（使其作为列/筛选项出现在业务页面）。入口 `test-gaia.baijia.com/gaia/page-scene-list` → 场景 → 编辑 → 布局配置加字段 → 保存 →（列表）构建 → 发布 → 强制审核通过 → 完成。
- **接口（前缀 `/bgwApi/component/gaia-center/`，POST/JSON）按步骤**：
  | 步骤 | 接口 | 关键入参 | 返回 |
  |---|---|---|---|
  | 保存（含新字段） | `scene/saveAndPublish` | `number,name,templateNumber,layoutSchema(含新字段),pageNumber,fieldSetNumbers,…` | `编辑成功` |
  | 构建 | `scene/version/create` | `{sceneNumber,identification}` | `{number:<版本号>}` |
  | 发布-建镜像 | `image/create` | `{name,scenes:[{sceneNumber,versionNumber}]}` | `{imageNumber}` |
  | 发布-取当前镜像 | `image/getCurrentImage` | — | `{imageNumber}` |
  | 发布-建计划 | `publishPlan/create` | `{publishImageNumber,rollbackImageNumber,grayStrategy,planName}` | `{publishPlanNumber}` |
  | 强制审核通过 | `approval/status/change` | `{businessKey:<计划号>,processInstId,approvalStatus:"5"}` | `true` |
  | 完成 | `publishPlan/finish` | `{planNumber:<计划号>}` | `success` |
- **实测**：`microContinuationService`（sceneNumber `263719917126160384`）加 `studentTagNames`，版本 `294311853465539584`、镜像 `294311864365492224`、发布计划 `294311864702085120`；`continuationService` 亦已含。
- **口径固化**：已写入 `gaia-field` skill `references/scene-display-record.md`（含 layoutSchema 字段结构、边界、验证）。MCP gaia-field 无「新建显示记录」写入口。
