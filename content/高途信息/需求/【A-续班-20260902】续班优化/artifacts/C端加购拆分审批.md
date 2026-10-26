---
title: C端膨胀券与组合加购拆分审批
updated: 2026-10-26
tags: [需求, 审批]
---

# C端膨胀券与组合加购拆分审批

状态：**本地待审批**。用户要求“先别提交，给我审批”。拆分代码没有commit、push，24038没有保存。503恢复操作由用户另行授权，独立记录在文末。

## 审批对象

当前`feature-xuban-expand-exclude`先上线，保留扩科推荐、AI模块化及B端下单。把本批新增C端膨胀券/组合加购及配套详情、算价、独立6003适配、勾选记忆移出，后续由24038发布。

| 仓库 | 当前分支的本地修改 | 新分支 |
|---|---|---|
| cart | 撤去bdba9e90之后C端增量，单独保留a6978058中的扩科有效订单signUp修复；扩科排除/前置课学年学期/Feign兼容/sellerId=null兼容保留 | feature-xuban-c-cart-addons，当前本地保存a6978058完整代码；worktree为/private/tmp/cart-c-addons-20261026 |
| order | 不撤代码，共享组合详情/数量/券校验仍供B端使用 | feature-xuban-c-cart-addons，本地指向0aec823154，与当前分支相同 |
| student-data/student-center/product-server、前端与GAIA组件 | 本轮无代码改动 | 不额外创建分支 |

撤去的是本批C端增强，不下线release已有的组合/预报名券能力。切年级记忆属于本批配套增量，当前分支恢复原先切年级清选择的行为；新分支保留记忆行为。既有选择记录不刷、不清。

## 实际diff与保留依据

cart原C端增量涉及11个生产代码文件、4个测试文件及2个仓内说明文件。主要是RenewalService、RenewalPriceService、RenewalDataService、加购已购构建器、请求/返回字段及选择Repository。拆除后相对bdba9e90，生产代码只多出独立保留的38行扩科已报名修复。

`a6978058`同时含“扩科已报名”和“组合已报名”两种行为，不能整提交revert。product-server的B端recommendProductList调用cart的renewalCart，并按signUp剔除已购推荐，因此保留applyExpandSignUp；组合已报名回退随C端新增实现保存在新分支。

order的组合详情由B端ContinuClazzOrder调用`/orderComponent/order/cart/detail`，确认页/预校验也有共享入口。因此保留order当前分支全部改动；24038中的order新分支作为C端共享依赖。

- 当前分支可审查补丁：[cart-remove-c-addons.patch](/tmp/xuban-c-split-review/cart-remove-c-addons.patch)
- 保留修复的新增测试：[RenewalExpandSignUpTest.java](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalExpandSignUpTest.java)
- C端恢复补丁：[cart-restore-c-addons.patch](/tmp/xuban-c-split-review/cart-restore-c-addons.patch)

## Git继承安排（审批后才执行）

1. 当前cart分支提交拆除差异，记为R；只纳入本次文件，原有未跟踪ExpandSubjectRecommendContractTest保持原样、不代为提交。
2. C端新分支继承R，再恢复保存的C端差异并提交为S。此时新分支相对当前分支有独立C端提交，后续合入release能真正带回功能。
3. 推送当前cart分支和cart/order两个新分支，核远端SHA和upstream。order当前分支无需新提交。

不能只留一个指向旧HEAD的备份分支：当前分支拆除提交上线后，旧HEAD已是release祖先，直接merge备份可能显示无变更，C端能力不会恢复。

## 24038变更预览（未保存）

[青舟24038](https://qingzhou.baijia.com/#/publishArrangement/subPublishArrangement/publishPlan/detail?storyId=&pageNum=1&id=24038&action=edit)目前名称为“C端支持膨胀券”，已含8个mweb部署，前端分支`feature-renewal-cart-coupon-20261023`。现有前端服务与分支保留，追加以下5个后端部署（整仓覆盖）：

| 上线顺序 | serviceCode | 提测分支 | 上线分支 |
|---|---|---|---|
| 1 | gaotu_order | feature-xuban-c-cart-addons | release |
| 2 | gaotu_order_task | feature-xuban-c-cart-addons | release |
| 3 | baijia.gaotu.tech.trade.order-ad | feature-xuban-c-cart-addons | release |
| 4 | baijia.gaotu.tech.trade.order-b | feature-xuban-c-cart-addons | release |
| 5 | gaotu_cart | feature-xuban-c-cart-addons | release |

原8个前端部署保持相对顺序，排在后端之后。当前分支先上线，24038继承其公共能力。

| 环境字段 | 当前值 | 拟变更 |
|---|---|---|
| 后端提测stepInControlEnv | test-gtbg-dev-1 | test-gtbg-dev-3 |
| 前端提测feStepInControlEnv | test-gtbg-dev-1 | 保留 |
| 准出stepOutControlEnv | test | 保留 |

服务登记已通过qingzhou_update_release_plan的confirm=false预览。现有工具没有环境更新参数，已根据真实字段形成仅修改后端提测环境的本地预览；审批后需重读线上现值及structuredConfigInfo.configRows再合并保存，不能直接回放过期payload。新分支未推送、未构建，预览中提测产物“1”为占位。实际部署也尚未执行。

- 服务变更预览：[24038-dryrun.json](/tmp/xuban-plan-24038-dryrun.json)
- 泳道与新增服务摘要：[24038-preview.json](/tmp/xuban-c-split-review/24038-preview.json)

## 验证

- 当前cart：JDK8 reactor clean test成功（client/domain/infrastructure/app/controller）；新增有效订单状态及异常回退测试6项、MVC sellerId参数兼容10项通过。
- 当前cart：JUnitCore运行扩科推荐与真实Feign HTTP故障/恢复契约，共10项通过。原有未跟踪测试内容hash未变化。
- 新分支：保留C端生产代码与原HEAD逐文件相同；原C端契约及公共已报名测试共28项通过，JDK8 reactor编译通过。
- order生产代码与HEAD一致；本轮未改B端/前端代码。
- 本轮只证明本地编译/测试与diff边界，未部署、未证明dev-3运行链路已通过。

## 自审结果（2026-10-26）

- 拆除后相对bdba9e90，生产代码差异确实只剩扩科有效订单已报名判断；B端商品推荐使用该字段，保留有依据。
- order共享逻辑与HEAD完全相同，原有未跟踪测试hash未变；未发现本次拆分引入的阻断项。
- 24038本地payload曾缺少structuredConfigInfo。已从getStructureConfig读取并补入16行配置，避免审批后整体保存误清空已有配置；实际保存前仍需重新读取。
- 13个服务无重复，8个前端保留，后端提测dev-3、前端提测dev-1。提测产物占位及未完成环境回归仍是审批后事项。
- 新分支继承拆除提交、再以独立提交恢复C端的Git顺序必须执行，当前仍为本地备份分支，尚未执行提交。

## 503恢复（另行授权）

用户明确指定test-gtbg-dev-1，并要求“发布原镜像”“先保证能用”。product-b该泳道replicas=0、无Pod，Eureka无对应实例；网关路由正常。

已核对listWorkDeploy保存的原镜像为`feature-xuban-expand-exclude-c1b9225e-20261019094500`，无运行中构建。使用qingzhou_redeploy显式指定该镜像，青舟返回code=200。目标commit为`c1b9225eff85f60f0d52b4a5d162b8b91f3172ee`，恢复验证进行中。该操作没有提交或构建拆分代码，也没有保存24038。

恢复过程中发现原镜像启动被TEST/default共享Apollo配置阻断：`TestProductExemptPredicate.exempt.shopNumbers`的数组缺少开头`[`，导致TestProductExemptPredicate初始化失败，Spring上下文退出。已核对已发布值与草稿一致、无其他待发布项；仅补`[`且保留原六个门店号，已暂存草稿。发布预览仅此一项modified。因Apollo技能要求已有值变更先展示old→new并确认，已请求用户确认，尚未发布配置；接口恢复验证尚未通过。
