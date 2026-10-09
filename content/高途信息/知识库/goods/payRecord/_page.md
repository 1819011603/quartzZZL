# 付款记录（payRecord）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-goodsmanage master 代码整理；后端对照 order（order-b）、gaotu-ols。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-goods/payRecord/list` |
| 基座 | OES ark → 子应用 app-goods |
| 前端仓库 | gaotu-fe-goodsmanage `http://git.baijia.com/gaotu-ctech/gaotu-fe-goodsmanage`（master，本地 `~/IdeaProjects/WebProject/gaotu-fe-goodsmanage`；青舟 serviceCode `baijia.gaotu.Business.fe.gaotu-fe-goods`） |
| 前端路由 | `config/routes.js:352-358` → `src/pages/OrderManage/list/index.js`，wrapper `olscampus`，**路由没配 access** |
| 同组件复用 | 和 [课程类订单](../normalOrdermanage/_page.md)、[非课程类订单](../ordermanage/_page.md) 是同一个组件；本页 = `PARRECORD_BLOCK`（`list/index.js:65`） |
| 后端主服务 | `/orderComponent/*` → gapm-appid `order-b-gaotu100-com` → 青舟 appId `order-b.gaotu100.com`（仓库 **order**，`OrderComponentController`） |

## tab 列表

只有一个 tab「付款记录」（orderType=`batch`，批次单 = 一次支付 payNumber）。显示条件（`useOrderJson.js:356-368`）：有 `gaotu_boss_p_order_` / `gaotu_boss_p_soloclazz_order` / `oes_menu_order_clazzHourPackage_` / `gaotu_boss_p_physical_order` / `oes_menu_order_listener_` / `oes_menu_order_correctionCard_` 任一标签。都没有就整页显示空。

- 列表组件 `src/components/OrderList/modules/BatchOrderList.tsx`（`list/index.js:900` `batchList`）；每一行可以展开看子订单
- 搜索项（`src/components/OrderList/constants.tsx:206`）：下单时间、支付编号、学员、商品名称、商品 ID（skuNumber）、班级 ID、付款记录编号；下红框是订单状态
- **没有默认搜索项**，搜索条件全空时前端直接返回空（`BatchOrderList.tsx:75`），所以只点「查询」看不到列表请求
- 表头按钮（`useOrderJson.js:306-312`）：「创建订单 / 创建门店订单」；行按钮「取消订单 / 付款二维码 / 修改付款计划」；子订单行「详情 / 修改地址」

## 页面级接口

`OL/` = `src/components/OrderList/`，`OM/` = `src/pages/OrderManage/`。test-mi 上 `isBoss()` 为 true，`hermesBoss` 前缀是空串。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（wrapper olscampus） | `POST /ols/w/campus/list` | `getOlsCampusList` | `src/models/useOlsCampus.js:19`（`src/services/physicalOrder.js:239`） | gaotu-ols | 校区列表 [36004] | 读 |
| 进页面 | `POST /orderComponent/grayGroup/checkGrayGroup` | `useOrderCreationGuard` | `OM/list/hooks/useOrderCreationGuard.js:34` | order-b | 灰度组命中判断 [5304562] | 读 |
| 进页面（全局 model） | `GET /intranet-rpc/course-setting/feign/options/bff/list` | `getCommonDictionary` | `src/models/useBffSelectItem.js:11`（`src/services/goodsManage.js:13`） | course-setting | 共享字典 [34362] | 读 |
| 查询/翻页（有搜索项时） | `POST /orderComponent/payFieldSearch` | `getBatchOrderList` | `OL/modules/BatchOrderList.tsx:85`（`OL/services.ts:40`） | order-b | 批次单信息搜索接口 [947749] | 读 |
| 展开某一行 | `POST /orderComponent/subOrder/list`，body `{command:{payNumber}}`（不带 pager） | `querySuborderList` | `OL/modules/BatchOrderList.tsx:60` → `OL/modules/BaseList.tsx:170`（`OL/services.ts:72`） | order-b | 批次单子订单列表接口 [947693] | 读 |
| 行「取消订单」 | `POST /order/cancel.do`，body `{orderNumber: payNumber}` | `cancelOrder`（OES `ORDER_LIST.CANCELORDERPATH`） | `OM/list/index.js:199,541`（`src/services/physicalOrder.js:36`） | hermes-boss 老接口（**未确认**，青舟搜不到；OLS/EES 用的是 order-b `/order/boss/facade/cancelOrder` [947494]） | — | 写 |
| 行「付款二维码」 | `POST /intranet-rpc/order-b/orderManagement/queryPaymentLink`，body `{payNumber}` | `getPaymentLink` | `OM/component/PayRQCode/PayContent/index.js:46`（`OM/prodetail/services.js:75`） | order-b | 查付款链接 [947688] | 读 |
| 二维码弹窗「去认领」→ 打开 | `GET /orderManagement/listAccountEntity`、`POST /order/boss/facade/feeControl/query` | `getPayeeEnum` / `feeQuery` | `OM/component/PayRQCode/FeeClaimModal/index.jsx:48,101`（`OM/list/service.js:8`、`FeeClaimModal/service.js:3`） | order-b | 收款主体 [947885] / 费控流水查询 [965576] | 读 |
| 二维码弹窗「去认领」→ 认领 | `POST /order/boss/facade/feeControl/claim` | `feeClaim` | `OM/component/PayRQCode/FeeClaimModal/index.jsx:164`（`FeeClaimModal/service.js:8`） | order-b | 费控认领 [965575] | 写 |
| 行「修改付款计划」→ 确定 | `POST /intranet-rpc/order/orderManagement/payPlan/modify` | `modifyPayPlan` | `OM/component/ChangePayPlan/index.jsx:60`（`src/services/physicalOrder.js:117`） | order-b | 修改付款计划 [947463] | 写 |
| 子订单「修改地址」 | `POST /orderComponent/queryAllWaitSendItem` → `POST /order/boss/facade/changeAddress` | `getOrderDeliveryDetail` / `getChangeAddress` | `OM/detail/OrderStep/ModifyAddress/index.js:29,74` | order-b | [947365] / [947342] | 读 / 写 |
| 子订单「详情」 | 不发请求；课程订单跳 `/ark/app-activity/orderManage/detail/{n}`，其它跳 `/ordermanage/prodetail/{n}` | `handleViewDetailFunc` | `OM/list/index.js:447`（`batchSubDom` :832） | — | — | — |
| 「创建订单 / 创建门店订单」 | 不发请求，跳 `/ordermanage/createOrder?sourceUrl=...` | `CreateOrderButton` | `OM/list/CreateOrderButton/index.js:109-141` | — | — | — |

## 关键表

### 接口 → 表

| 接口 | 后端位置 | 读表 | 写表（操作） | 备注 |
|---|---|---|---|---|
| `payFieldSearch` | `order-controller/.../search/OrderComponentController.java:90`（类 `/orderComponent` :55）→ `order-app/.../search/application/impl/PayFieldSearchApplication.java` → `.../search/service/impl/PayFieldSearchService.java` → `AbstractSearchService#doSearch:81` | **ES** 支付宽表 alias `index.pay.alias`（test 配置里是 `gaotu_order_wide_pay_search_rollover`，取自 `order-infrastructure/src/test/resources/application.properties:11`，**线上值未确认**），拿根 payNumber；MySQL 兜底 `gaotu.pay_info`（`PayInfoRepository#pageByAccurateQuery`）；聚合 provider 在 `polymerize/provider/pay/impl/`：`pay_info`、`order_info`、`order_item`、`pay_plan` / `pay_plan_item`、`pay_record`、`pay_coupon`、订单优惠、赠品、调课、运费、用户 | 无 | 开关 `search.pay.allowComplexSearch`（默认 true）/ `search.pay.coverLogic` |
| `subOrder/list` | `OrderComponentController.java:184` → `ComponentTobApplication#querySubOrderList:67` → `order-app/.../component/tob/pay/suborderlist/service/SubOrderListService.java:46` | `gaotu.order_info`（按 payNumber 取课程订单号 :49）、`gaotu.order_item`（按 payNumber 取订单项号 :52），再分别走订单 / 订单项聚合（同 `orderFieldSearch` / `orderItemFieldSearch` 的聚合部分） | 无 | 不走 ES |
| `payPlan/modify` | `order-controller/.../OrderManagementController.java:173`（类 `/orderManagement` :56）→ `order-domain/.../payplan/service/PayPlanService.java:411` → `order-domain/.../pay/service/BatchSaveOrderService.java:210` | `pay_info`、`pay_plan`、`pay_plan_item` | `gaotu.pay_plan_item` UPDATE（改已有期）+ 批量 INSERT（新增期） | — |
| `queryPaymentLink` | `OrderManagementController.java:162` → `bossPayApplication.getPaySuccessResult` | **未细追** | 无 | — |
| `feeControl/query` | `order-controller/.../boss/BossController.java:191`（类 `/order/boss/facade/` :60）→ `order-app/.../fee/service/FeeControlService.java:95` | Feign 费控服务 `FeeControlApiClient#queryPaymentDetail`；读 `fee_control_record`（:114） | `fee_control_record` save（:132，**具体操作未细看**） | 表名按 Repository 名推断，**未确认** |
| `feeControl/claim` | `BossController.java:202` → `FeeControlService`（:157-174） | `pay_record`（按 payNumber）等 | Feign `FeeControlApiClient#claim`；本地写哪些表**未细追** | — |
| `listAccountEntity` | `OrderManagementController.java:168` → `auditService.getAccountEntities` | **未细追**（大概率是配置） | 无 | — |
| `changeAddress` | `BossController.java:112` → `ModifyAddressService.java:211` | — | `order_info` / `order_info_commodity` / `order_item` / `pay_info` UPDATE 地址 id | 同 [课程订单](../normalOrdermanage/normal.md) |

### 表

| 表 | 库 | 含义 |
|---|---|---|
| ES 支付宽表 | ES（alias `index.pay.alias`） | 付款记录搜索，只拿 payNumber + 分页 |
| `pay_info` | gaotu | 支付单（批次单），一次付款一个 payNumber |
| `order_info` | gaotu | 课程订单（老实体），按 pay_number 关联 |
| `order_item` | gaotu | 订单项（新实体：实物 / 一对一 / 课时包 / 小班课等），按 pay_number 关联 |
| `pay_plan` / `pay_plan_item` | gaotu | 付款计划 / 分期（首付尾款） |
| `pay_record` | gaotu | 实际付款流水 |

库名说明：order 的 mapper XML 里表名不带库前缀，`gaotu` 是在 test 环境 cluster 142（`gaotu_polar_test_03`）里查到同名表推出来的。

## 排查提示

- 点「查询」没请求 → 正常，至少要填一个搜索条件
- 用支付编号能查到、其它条件查不到 → ES 支付宽表没同步（带 payNumber 时 ES 没命中会走 MySQL 兜底）
- 展开子订单为空 → 看 `subOrder/list`，它直接查 MySQL `order_info` / `order_item` 的 `pay_number`
- 取消订单报错 → OES 走的是 `/order/cancel.do`（hermes-boss 老链路），不是 order-b 的 `/order/boss/facade/cancelOrder`

## 青舟接口详情页

- [POST /orderComponent/payFieldSearch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947749&appId=order-b.gaotu100.com&branchName=release) id=947749
- [POST /orderComponent/subOrder/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947693&appId=order-b.gaotu100.com&branchName=release) id=947693
- [POST /orderManagement/queryPaymentLink](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947688&appId=order-b.gaotu100.com&branchName=release) id=947688
- [POST /orderManagement/payPlan/modify](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947463&appId=order-b.gaotu100.com&branchName=release) id=947463
- [GET /orderManagement/listAccountEntity](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947885&appId=order-b.gaotu100.com&branchName=release) id=947885
- [POST /order/boss/facade/feeControl/query](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=965576&appId=order-b.gaotu100.com&branchName=release) id=965576
- [POST /order/boss/facade/feeControl/claim](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=965575&appId=order-b.gaotu100.com&branchName=release) id=965575
- [POST /order/boss/facade/cancelOrder](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947494&appId=order-b.gaotu100.com&branchName=release) id=947494（OLS/EES 用，OES 不调）
- [POST /orderComponent/grayGroup/checkGrayGroup](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5304562&appId=order-b.gaotu100.com&branchName=release) id=5304562
- [POST /w/campus/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36004&appId=gaotu-ols&branchName=release) id=36004
