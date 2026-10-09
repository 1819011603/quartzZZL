# 课程类订单 · 课程订单 tab（normal）

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-goodsmanage master 代码整理；后端对照 order（order-b）。页面级接口见 [_page.md](_page.md)。

## 组件

- tab 内容：`src/pages/OrderManage/list/index.js:860` `normalList` → `src/components/OrderList`（orderType=`normal`）
- 下红框默认值 `openCourseList=['2']`（`src/components/OrderList/constants.tsx:312` `SELECTGROUPDEFAULT`），所以**进页面就会发列表请求**
- OES 配置 `useOrderJson.js:260-279`：表头按钮「创建单个订单 / 创建联报订单 / 创建订单 / 创建门店订单 / 批量修改发货状态」；行按钮「详情 / 父单详情 / 修改地址 / 调课调班 / 课程转移」
- OES 不开 `AUTHINTERFACECHANGE`，所以永远走 `orderFieldSearch`，不会走 `/authority/orderFieldSearch`（后端硬校验 `B_client=EES`）

前缀约定：`OL/` = `src/components/OrderList/`，`OM/` = `src/pages/OrderManage/`。test-mi 上 `isBoss()` 为 true，`hermesBoss`、`INTRANET_RPC`、`COMPONENT` 前缀都是空串（`src/utils/utils.js:350`）。

## 接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面/查询/翻页 | `POST /orderComponent/orderFieldSearch`，body `{openCourseList:["2"], pager, ...}` | `getNormalOrderList` | `OL/modules/BaseList.tsx:125,243`（`OL/services.ts:28`） | order-b | 订单信息搜索接口 [947972] | 读 |
| 「物流」列点击 | `POST /express-management/invoice/queryExpressInvoiceByOrderNumbers` | `getExpressDetail` | `OL/components/ExpressDetailTable/index.tsx:31`（`OL/services.ts:42`） | express-management | 物流发货单 [46863] | 读 |
| 物流弹窗查轨迹 / 取件码 | `GET /express-management/queryExpressInfo`、`GET /express-management/queryPickUpCode` | `queryExpressInfo` / `queryPickUpCode` | `OL/components/ExpressDetailTable/index.tsx:55`、`OL/components/QueryCodeButton/index.tsx:25`（`OL/services.ts:47,53`） | express-management | 未查 id | 读 |
| 手机号/地址「小眼睛」 | `POST /component/student-center/userSecret/getBaseInfo`、`.../getAddress` | `querySecretPhone` / `querySecretAddress` | `OL/columnsConfig.tsx:103,109`（`OL/services.ts:58,63`） | student-center | 未查 id | 读 |
| 行「详情」 | 不发请求，跳 `/ark/app-activity/orderManage/detail/{orderNumber}`（别的子应用） | `handleViewDetailFunc` | `OM/list/index.js:463` | — | — | — |
| 行「修改地址」→ 打开 | `POST /orderComponent/queryAllWaitSendItem` | `getOrderDeliveryDetail` | `OM/detail/OrderStep/ModifyAddress/index.js:29`（`src/services/physicalOrder.js:191`） | order-b | 获取待发货订单 [947365] | 读 |
| 行「修改地址」→ 确定 | `POST /order/boss/facade/changeAddress` | `getChangeAddress` | `OM/detail/OrderStep/ModifyAddress/index.js:74`（`OM/detail/service.js:8`） | order-b | 修改地址 [947342] | 写 |
| 行「调课调班」抽屉 | `POST /afterSale/b/transfer/preview/basic`、`/preview/calculate`、`/submit`、`/getPayInfo` | `getPreviewBasic` / `previewCalculate` / `transferSubmit` / `queryAfterSaleProgress` | `OM/component/TransferClazz/Preview/index.jsx:53`、`Operation/index.jsx:71`、`index.jsx:95,69`（`src/services/afterSale.js:11/47/29/38`） | after-sales | [1069172] / [1069159] / [1069148] / [1069212] | 读 + 写 |
| 行「课程转移」抽屉 | `POST /order/separate/detail.do`、`/student/getNameByMobile.do`、`/afterSale/b/transfer/user/submit` | `fetchCourseTransfer` / `fetchNameByMobile` / `fetchSeparateCreate` | `OM/component/CourseTransfer/index.jsx:30,125,84`（`OM/list/service.js:237,257,267`） | hermes-boss（前两个，**未确认**）/ after-sales | — / — / [1069149] | 读 + 写 |
| 「批量修改发货状态」 | `POST /intranet-rpc/order-b/additional/batchUpdatesOrderNeedDelivery` | `changeBatchOrderDelivery` | `OM/component/ModifyDeliveryStatus.js:56`（`OM/list/service.js:227`） | order-b | 批量修改订单发货状态 [947513] | 写 |
| 「创建单个订单」/「创建联报订单」弹窗 | `/student/suggest/list`、`/student/address/list`、`/clazz/selectByKey`、`/clazz/selectSubclazzByClazzNumber`、`/activity/clazzset/getByKey`、`/activity/clazzset/getSubclazzByNumber`、`/order/coupon/list`、`POST /intranet-rpc/order/orderManagement/order/prepare`、`/order/createOrder` | `getStudentList` 等 | `OM/list/AddOrderDialog/index.js:86-477`、`OM/list/AddActivityOrderDialog/index.js:87-507`（`OM/list/service.js`） | 大部分是 hermes-boss 老接口（**未确认**）；`order/prepare` 是 order-b [947421] | — | 读 + 写（下单） |
| 下单成功（价格>0）→ 付款二维码 | `POST /intranet-rpc/order-b/orderManagement/queryPaymentLink` | `getPaymentLink` | `OM/component/PayRQCode/PayContent/index.js:46`（`OM/prodetail/services.js:75`） | order-b | 查付款链接 [947688] | 读 |
| 「创建订单」/「创建门店订单」 | 不发请求，跳 `/ordermanage/createOrder?sourceUrl=...`；命中灰度先弹引导/拦截 | `CreateOrderButton` | `OM/list/CreateOrderButton/index.js:46-141` | — | — | — |

## 关键表

### 接口 → 表

| 接口 | 后端位置 | 读表 | 写表（操作） | 备注 |
|---|---|---|---|---|
| `orderFieldSearch` | `order-controller/.../search/OrderComponentController.java:102`（类 `@RequestMapping("/orderComponent")` :55）→ `order-app/.../search/application/impl/OrderFieldSearchApplication.java` → `OrderFieldSearchService` → `AbstractSearchService#doSearch:81` | **ES** 订单宽表 alias `index.order.alias`（取根订单号 + 价格/退款 sum 聚合 :121）；MySQL 兜底 `gaotu.order_info`（`OrderInfoRepository#pageByAccurateQuery` / `listByNumbers` / `listByPayNumbers`）；聚合补字段：`order_info`、`order_info_ext`、`order_info_commodity`、`pay_info`、`pay_plan`、`pay_plan_item`、`pay_record`、订单标签、拼团、退款记录、调课记录等（provider 在 `order-app/.../search/service/polymerize/provider/order/impl/`）；Feign 补班级/老师/用户/商品/业绩归属 | 无 | `search.order.allowComplexSearch=false` 时整体改查 MySQL；后端要是关了复杂搜索，会把 `openCourseList` 置空（Controller :106） |
| `queryAllWaitSendItem` | `OrderComponentController.java:226` → `ComponentTobApplication#queryAllWaitSendItemResult:78` | 订单/订单项待发货信息（**表未细追**） | 无 | — |
| `changeAddress` | `order-controller/.../boss/BossController.java:112`（类 `/order/boss/facade/`）→ `order-app/.../boss/facade/service/BossOrderService.java:93` → `order-domain/.../pay/service/address/ModifyAddressService.java:211` | 先 Feign 物流服务校验能不能改（`UpdateAddressService.java:151,167,201`） | `order_info` UPDATE 地址 id；`order_info_commodity` UPDATE；`order_item` UPDATE；`pay_info` UPDATE 地址 id | 发 Spring 事件 `ModifyAddressEvent` |
| `batchUpdatesOrderNeedDelivery` | `order-controller/.../OrderAdditionalController.java:87`（类 `additional/`）→ `order-app/.../service/OrderAdditionalService.java:591` | `order_item`、`order_info`、`order_info_ext` | 课程订单：`order_info_ext` UPDATE `need_delivery`（`OrderInfoExtService#batchUpdateNeedDelivery`，事务 `orderTransactionManager`）；订单项：`order_item` UPDATE `need_delivery`；另记操作日志 `operateLogPrintService.batchOperateLog` | 发 `OrderInfoExtChangeEvent` |
| `checkGrayGroup` | `order-controller/.../graygroup/GrayGroupController.java:40`（类 `/orderComponent/grayGroup` :33）→ `order-app/.../graygroup/GrayGroupService.java` → `order-domain/.../graygroup/impl/GrayGroupRuleServiceImpl.java` | 无表：Apollo JSON `order.gray.group.rule.config` + Feign `StaffFeignServiceAdapter#getOrgsAndLabels(accountId)` 取组织/标签 | 无 | 请求体可以为空 |
| `order/prepare` / `queryPaymentLink` | `order-controller/.../OrderManagementController.java:100` / `:162`（类 `/orderManagement`） | **未细追** | 无 | — |

after-sales、express-management、student-center、hermes-boss 的接口不在本次追踪范围内。

## 排查提示

- 列表数据不对 → 先拿订单号查（订单号会走 MySQL 兜底）；订单号能查到、其它条件查不到 = ES 宽表没同步
- 头部「付款金额 / 退款金额」来自 ES sum 聚合（`price`、`refundPrice`），开关是 `order.field.search.agg.price.enable`
- 改地址失败 → 一般是物流已经发货了（`UpdateAddressService` 会调物流 Feign 判断）

## 青舟接口详情页

- [POST /orderComponent/orderFieldSearch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947972&appId=order-b.gaotu100.com&branchName=release) id=947972
- [POST /orderComponent/queryAllWaitSendItem](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947365&appId=order-b.gaotu100.com&branchName=release) id=947365
- [POST /order/boss/facade/changeAddress](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947342&appId=order-b.gaotu100.com&branchName=release) id=947342
- [POST /additional/batchUpdatesOrderNeedDelivery](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947513&appId=order-b.gaotu100.com&branchName=release) id=947513
- [POST /orderManagement/order/prepare](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947421&appId=order-b.gaotu100.com&branchName=release) id=947421
- [POST /orderManagement/queryPaymentLink](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947688&appId=order-b.gaotu100.com&branchName=release) id=947688
- [POST /afterSale/b/transfer/submit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069148&appId=after-sales&branchName=release) id=1069148
- [POST /afterSale/b/transfer/user/submit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069149&appId=after-sales&branchName=release) id=1069149
- [POST /express-management/invoice/queryExpressInvoiceByOrderNumbers](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=46863&appId=express-management.gaotu100.com&branchName=release) id=46863
