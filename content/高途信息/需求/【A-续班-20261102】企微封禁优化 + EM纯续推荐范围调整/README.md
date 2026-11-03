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
updated: 2026-11-03
tags: [需求]
---

# 【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整

> 飞书方案（含表结构+接口协议）：https://gaotuedu.feishu.cn/docx/AQEtdIeKzo7P5IxeQEzc7EpxnBe

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
| GAIA 两场景显示 | owner 手动 | 归档 `tasks.md` T-4 |
| cronus 前端 | 未改码，说明在技术文档 §五/§六(二) | 无独立文件 |

### 预热缺口与修复（2026-11-04）
- **缺口**：设计（技术文档 §六(六)）假设「并集在引擎里生效→预热自动产出主+从」，但实现把 `mergeRelatedPreCourseNumbers` 放在 `getRenewalDetail`（引擎之外）；`preheat()` 直接 `coreHandle` **未合并** → 预热结果缓存丢从计划。在线大班路径优先读该缓存（`corePreheatCache`），故为**正确性缺口**。
- **修复**：`preheat()` 与 5 参 `getRenewalDetail`（`/web/renewal/operation/cart`）在加载 DTO 后、分流前调用 `mergeRelatedPreCourseNumbers`（同一开关门控）。push `e5c30f6e`。
- **验证**：cart 重部署 `test-gtbg-dev-3`，pod `cart-gaotu100-com-c7b575d8f-w7tvj` **eureka UP**（commit `e5c30f6e`）；桥 `RenewalService#preheat(7658127801, 585960797778243584)` 返回**主(`585960577856301056`→大班)+从(`18314034380997173`→小班6004)**；桥 `getRenewalDetail` 返回 grade16(大班纯续)+grade11(小班6004 纯续)（traceId `cart_gaotu100_com.297.17937224167830007`）。

### 已知风险 / 未覆盖（本轮新增）
- **「扩科不动」的间接影响**：合并后的 `courseNumbers` → `renewalCourseDTOMap` → 决定扩科 `studentPostGrades`（`ExpandSubjectRecommendService` 大班重载）。若扩科配置含从计划年级的条目，扩科结果可能新增项。本样本（扩科仅 grade16）未触发；未做扩科配置含从计划年级的对照验证 → **推断**：口径「扩科不变」在配置年级⊆主计划年级时成立。
- `PaymentSizeImpl` 未改（技术文档列了 PAYMENT_SIZE 一并放行，实际跨模式未触发该处理器）。
- 预热**小班**路径（`SmallRenewalPreheatService`）仍不合并：在线小班不走预热结果缓存、会实时重算（正确），仅下游缓存预热少从计划 → 性能影响。
