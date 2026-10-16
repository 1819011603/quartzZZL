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

### 入参

- `POST /orderComponent/orderFieldSearch`（`OrderComponentController#orderFieldSearch`，DTO `com.gaotu.app.search.request.impl.OrderComplexSearchRequest`，`OrderComponentController.java:104`）：
  - `user` (String, 可选) — 用户姓名/手机号，逗号分隔
  - `orderNumberList` (List&lt;String&gt;, 可选) — 订单号（DTO 声明为 String 列表，内部转 Long）
  - `payNumberList` (List&lt;String&gt;, 可选) — 批次单号
  - `orderStatus` (String, 可选) — 订单状态（筛选值单值，如 `"2"`）
  - `createTimeRange` (TimeRange, 可选) — `{startTime:Long, endTime:Long}`（毫秒时间戳）
  - `expressNo` (String, 可选) — 快递单号
  - `openCourseList` (List&lt;Integer&gt;, 可选) — 1-非公开课 / 2-公开课；**课程订单 tab 默认传 `["2"]`**
  - `courseName` (String, 可选) — 课程名
  - `clazzBizNumber` (String, 可选) — 班级 BizNumber
  - `subclazzNumberList` (List&lt;Long&gt;, 可选) — 辅导班 Number（非 biz）
  - `payRecordNumber` (String, 可选) — 支付业务编号（`@MustLong`）
  - `categoryIdPath` (String, 可选) — 品类路径
  - `courseCategoryIds` (List&lt;Integer&gt;, 可选) — 课程类型
  - `pager` (Pager, 可选) — 分页 `{pageNum,pageSize,count}`（前端 `paginationToPager` 拼）
  - ⚠️ 多个字段标 `@OnesHaveRequired`：**至少需命中其一**（user/orderNumberList/payNumberList/expressNo/courseName/clazzBizNumber/subclazzNumberList/payRecordNumber），否则校验报 `ONES_HAVE_PARAMETER_ERROR`（`OrderComplexSearchRequest.java:116-131`）
  - 前端字段映射（`OL/utils.tsx:102-202` + `OL/constants.tsx:347-353`）：`orderTime`→`createTimeRange`、`orderNumber`→`orderNumberList`（逗号/空格拆分数组），其余同名透传
- `POST /express-management/invoice/queryExpressInvoiceByOrderNumbers`：**后端 DTO 未定位**（express-management 仓库本地不存在）；前端入参：`{orderNumbers: string[], type: number}`（实物订单传 `type:6`，其它 `0`；`OL/components/ExpressDetailTable/index.tsx:31`）
- `GET /express-management/queryExpressInfo`：**后端 DTO 未定位**；前端入参：`{logisticCode, shipperCode, addressId}`（`OL/components/ExpressDetailTable/index.tsx:55`）
- `GET /express-management/queryPickUpCode`：**后端 DTO 未定位**；前端入参：`{logisticCode, shipperCode, sensitive:boolean}`（`OL/components/QueryCodeButton/index.tsx:25,40`）
- `POST /component/student-center/userSecret/getBaseInfo`（`UserSecretController#getUserSecretBaseInfo`，DTO `com.gaotu.yunying.student.center.domain.model.usersecret.SecretUserIdRequest`，`UserSecretController.java:38`）：
  - `userId` (Long, **必填**，为空返回"参数错误")
  - `typeList` (List&lt;Integer&gt;, **必填**) — 取用类型：1 mobile / 2 wechatNo / 3 备用手机号
  - `entranceUrl` (String, 可选) — 查询页面全路径 url
  - `reason` (String, 可选) — 解密原因
  - 前端传 `{typeList:[1], userId}`（`OL/columnsConfig.tsx:119-121`）
- `POST /component/student-center/userSecret/getAddress`（`UserSecretController#getUserSecretAddress`，DTO `SecretAddressIdRequest`，`UserSecretController.java:52`）：
  - `addressId` (Long, **必填**)
  - `typeList` (List&lt;Integer&gt;, **必填**) — 1 mobile / 2 详细地址
  - `entranceUrl` (String, 可选)、`reason` (String, 可选)
  - 前端传 `{typeList:[2], addressId}`（`OL/columnsConfig.tsx:119-121`）
- `POST /orderComponent/queryAllWaitSendItem`（`OrderComponentController#queryAllWaitSendItem`，DTO `BaseComponentRequest<AllWaitSentItemCommand>`，`OrderComponentController.java:228`）：
  - `command.orderItemNumber` (Long, **必填**) — 订单项号
  - `command.employeeId` (String, 服务端注入) — Controller 从 cookie `uid` 取值覆写（`:229-231`）
  - 前端传 `{command:{orderItemNumber}}`（`OM/detail/OrderStep/ModifyAddress/index.js:346`）
- `POST /order/boss/facade/changeAddress`（`BossController#changeAddress`，DTO `com.gaotu.app.boss.facade.model.ChangeAddressRequest`，`BossController.java:114`）：
  - `userId` (Long, **必填**)、`name` (String, **必填**, ≤10 字)、`mobile` (String, **必填**)、`province`/`city`/`area` (String, **必填**)、`address` (String, **必填**, 5~60 字)
  - `provinceId`/`cityId`/`areaId` (Integer, 可选)
  - `orderNumbers` (List&lt;Long&gt;, 可选) — 课程订单号
  - `orderItemNumbers` (List&lt;Long&gt;, 可选) — 实物订单项号
  - `orderCommodityNumbers` (List&lt;Long&gt;, 可选) — 实物 number
  - `giveawayOrders` (List&lt;GiveawayOrders&gt;, 可选) — 赠品单，元素 `{orderCommodityNumber, type}`（`OM/detail/OrderStep/ModifyAddress/index.js:281-303`）
- `POST /afterSale/b/transfer/preview/basic`（`AfterSaleTransferController#afterSaleTransferPreview`，DTO `com.gaotu.lvyue.aftersales.domain.model.transfer.TransferBasicRequest`，`AfterSaleTransferController.java:74`）：
  - `orderItemNumber` (Long, **必填**)、`originalSkuNumber` (Long, **必填**)、`originalSkuType` (Integer, **必填**)、`targetSkuType` (Integer, **必填**)
  - `targetSkuNumber` (Long, 可选) / `targetSubClazzNumber` (Long, 可选) — 二者至少填一个
  - `isBatchTransfer` (Boolean, 可选)
- `POST /afterSale/b/transfer/preview/calculate`（`AfterSaleTransferController#afterSaleTransferCalculate`，DTO `TransferCalculateRequest`，`AfterSaleTransferController.java:80`）：
  - `orderItemNumber` (Long)、`targetSkuNumber` (Long)、`productSkuPrice` (Long, 必填)、`targetTotalHours` (String)、`remainPrice` (Long, 必填)、`remainHours` (String)、`promotionPrice` (Long)、`transferOutHours` (String)、`transferInHours` (String)、`isPromotion` (Boolean, 必填)、`joinClass` (Boolean, 默认 false)
- `POST /afterSale/b/transfer/submit`（`AfterSaleTransferController#afterSaleSubmit`，DTO `AfterSaleTransferSubmitRequest extends AfterSaleSubmitRequest`，`AfterSaleTransferController.java:58`）：
  - 业务主键：`orderItemNumber`、`transferOrderNumber` (Long, **必填**)、`transferSkuNumber`/`skuNumber` (Long, **必填**)、`originalSkuPrice` (Long, **必填**)、`transferSkuType`/`skuType` (Integer)、`amount` (BigDecimal, 一对一调入课时)
  - 金额：`price`/`refundPrice`/`transferPrice`/`transferInPrice`/`transferOutPrice`/`advicePrice`/`promotionPrice`/`skuPrice`/`manualPrice` (Long, 分)
  - 类型/开关：`afterSaleType` (Integer, 调课固定传 `3`)、`transferType` (Integer 0相等/1多退/2少补)、`forceEqual` (Boolean)、`isPromotion` (Boolean)、`isNeedDelivery`/`isSendMessage` (Boolean)、`joinClass` (Boolean)、`couponRecycleFlag` (Boolean)、`transferUnit` (String)、`transferReasonCode` (Integer)、`transferReasonDetail`/`expandDesc` (String)、`addressId` (Long)、`targetSubClazzNumber` (Long)、`mark` (int)
  - OBS-6 钱包抵扣：`walletDeductEnabled` (Boolean)、`walletDeductAmount` (Long, 分)（`TransferClazz/index.jsx:235-238`）
  - 退差退款方式（继承父类）：`refundMethod` (Integer 1原路/2非原路/3退钱包)
  - 审批：`transferAuditInfo` (TransferAuditInfo)
  - 完整前端组参见 `OM/component/TransferClazz/index.jsx:174-283`
- `POST /afterSale/b/transfer/getPayInfo`（`AfterSaleTransferController#getPayInfo`，DTO `AfterSalePayInfoRequest`，`AfterSaleTransferController.java:87`）：
  - `afterSaleNumber` (Long, 可选) — 售后单号（前端轮询传 `{afterSaleNumber}`，`TransferClazz/index.jsx:108`）
- `POST /order/separate/detail.do`：**后端 DTO 未定位**（hermes-boss 老链路，本地 mojito 现版本已无 `.do` 映射）；前端入参 `{orderNumber}`（`OM/component/CourseTransfer/index.jsx:30`）
- `POST /student/getNameByMobile.do`：**后端 DTO 未定位**（同上）；前端入参 `{key: 手机号}`（`OM/component/CourseTransfer/index.jsx:125`）
- `POST /afterSale/b/transfer/user/submit`（`AfterSaleTransferBetweenUserController#afterSaleSubmit`，DTO `com.gaotu.lvyue.aftersales.adapter.dto.OrderSeparateCreateRequest`，`AfterSaleTransferBetweenUserController.java:36`）：
  - `orderNumber` (Long, **必填**)、`mobile` (String, **必填**)、`needDelivery` (Boolean, **必填**)、`retainOriginRight` (Boolean, **必填**)、`price` (Long, **必填**, 少补价, 分)、`afterSaleNumber` (Long, 可选)
  - 前端传 `{price, mobile, orderNumber, needDelivery, retainOriginRight}`（`OM/component/CourseTransfer/index.jsx:84-90`）
- `POST /intranet-rpc/order-b/additional/batchUpdatesOrderNeedDelivery`（`OrderAdditionalController#batchUpdateOrderNeedDelivery`，DTO `com.gaotu.app.order.model.BatchChangeOrderDeliveryRequest`，`OrderAdditionalController.java:88`）：
  - `orderNumberList` (String, 可选) — 订单编号，英文逗号/空格分隔
  - `updateReason` (String, 可选)、`targetStatus` (Integer 0不发货/1发货)、`operateId` (Long)、`operateName` (String)
  - 前端传 `{targetStatus, updateReason, operateId, operateName, orderNumberList}`（`OM/component/ModifyDeliveryStatus.js:103-116`）
- `POST /intranet-rpc/order/orderManagement/order/prepare`（`OrderManagementController#getBossOrderPrepareInfo`，DTO `BossOrderPrepareRequest extends AbstractBossRequest`，`OrderManagementController.java:101`）：
  - `products` (List&lt;OrderProduct&gt;, 可选)、`giftProducts` (List&lt;OrderProduct&gt;, 可选)；父类 `sid` (String) 等
  - 前端传 `{products:[{productType:2, productNumber: clazzNumber}]}`（`OM/list/AddOrderDialog/index.js:428-435`）
- `POST /intranet-rpc/order-b/orderManagement/queryPaymentLink`（`OrderManagementController#queryPaymentLink`，DTO `com.gaotu.order.model.rpc.PaymentLinkRequest`，`OrderManagementController.java:163`）：
  - `payNumber` (String, **必填** `@NotNull`，且需可转 Long) — 批次单号
  - 前端传 `{payNumber}`（`OM/prodetail/services.js:75-79`）
- 「创建单个订单/联报订单」弹窗里其余接口（`/student/suggest/list`、`/student/address/list`、`/clazz/selectByKey`、`/clazz/selectSubclazzByClazzNumber`、`/activity/clazzset/getByKey`、`/activity/clazzset/getSubclazzByNumber`、`/order/coupon/list`、`/order/createOrder`）：**后端 DTO 未定位**（hermes-boss 老接口）。前端组参（`OM/list/AddOrderDialog/index.js:228-281`）：`createOrder` 传 `{clazzNumber, userVoucherNumbers[], appId, ignoreCheckAddress, valuation?, subclazzNumber[], userNumber|mobile, addressId|addresses[]}`；`getStudentList`/`getAddressList`/`getSuggest`/`getSubclazzByNumber`/`selectSubclazzByClazzNumber` 传 `{key}` 或 `{clazzNumber}`，`getByKey` 传 key，`getCouponListNew` 传 `{clazzNumber, userNumber}`

## 订单管理 4 个 tab 的列表接口（按 productType 区分，**查单必须选对 tab**）

OES「订单管理」下 4 个 tab：**课程订单 / 一对一订单 / 课时包订单 / 小班课订单**。

| tab（`ORDERTYPE`） | 中文 | 前端方法（`OL/services.ts`） | 接口 | `productType` |
|---|---|---|---|---|
| normal | 课程订单 | `getNormalOrderList` | `POST /orderComponent/orderFieldSearch`（订单级） | 2（大班课） |
| soloclazz | 一对一订单 | `queryOrderItemList` | `POST /orderComponent/orderItemFieldSearch` | **6003** |
| lessonpackage | 课时包订单 | `queryOrderItemList` | `POST /orderComponent/orderItemFieldSearch` | **7001** |
| miniclass | 小班课订单 | `queryOrderItemList` | `POST /orderComponent/orderItemFieldSearch` | **6004** |

> 完整 tab 枚举 `ORDERTYPE`（`OL/constants.tsx`）：normal / batch / coin / physical / batchsub / soloclazz / lessonpackage / listener / correctioncard / externalcompliance / miniclass / nonclazz / coupon。

**`productType` 全量**（`gaotu-fe-goodsmanage/src/pages/Product/config.js` `PRODUCT_TYPE`；order-b 后端 `ProductTypeEnums` 子集）：

| code | 含义 | code | 含义 |
|---|---|---|---|
| 2 | 大班课 | 7002 | 倾听师 |
| 23 | 联报 | 7003 | 批改次卡 |
| 50 | 单个实物商品 | 7004 | 外部履约商品 |
| 51 | 实物商品组合 | 6004 | 小班课 |
| 6003 | 1对1 | 8027 | OMO课时包 |
| 7001 | 课时包 | 8007 | 软件会员 |
| | | 8014 | 膨胀券 |

tab 与 `productType` 的绑定在前端表格组件里：`OM/component/ClazzTable→SOLOCLAZZ(6003)`、`LessonPackageTable→LESSONPACKAGE(7001)`、`MiniClassTable→MINICLASS(6004)`、`PhysicalTable→PHYSICAL(50)`、`UnionTable→UNION(23)`。

**`orderItemFieldSearch` 请求体**（`order-app/.../request/impl/OrderItemPageAbleComplexSearchRequest`，`condition` = `OrderItemComplexSearchCondition`）：

```json
{"condition":{"orderItemNumberList":["<订单号/订单项号>"],"productType":6003},"pager":{"pageNum":1,"pageSize":10,"count":0}}
```

- ⚠️ **同一个订单号只有一个 productType 能查到**（实测订单项 `425838771470075834`：`6003` 命中 count=1，`2/6004/7001/8027` 全 count=0）→ 排查/查单要按 tab（productType）逐个试。
- ⚠️ `orderFieldSearch` 的 `pager` 用 `{pageNum,pageSize}`（传 `current` 直接 `code=1`）；`orderItemFieldSearch` 的 `condition` 必须挂 `orderItemNumberList`（挂顶层报 `分页查询条件不能为空`）。
- 网关主机：prod `mi.gaotu100.com`、test `test-mi.gaotu100.com`；header `b_client: OES`。

**返回字段**（订单项）：`data.resultList[].baseOrderItem.orderStatus` = 订单项**原始状态码**（电商码 1/2/…）；`afterSalesInfo` = 退款明细：`hasRefunded`、`totalRefundPrice`（已退金额,分）、`lastSuccessAfterSalesType`（售后类型：0 部分退款 / 1 退款退货 / 2 退款退课 / **7 部分退课时(部分退款)**）。对比实付 `price` 即可判全退/部分退。

> ⚠️ 注意：OES 这里返回的是**原始状态码**（部分退款单的 `orderStatus` 仍可能是 2=已支付，退款在 `afterSalesInfo` 里），与**学员档案「订单信息」**返回的状态**不是一回事** —— 后者是 order-b 按文案合并过的，见 [cronus/StudentProfile/orderInfo.md](../../cronus/StudentProfile/orderInfo.md)。

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

## 关键字段：订单状态枚举（电商 order-b）

页面「订单状态」筛选（全部 / 待付款 / 已付款 / 已取消 / 已退款 / 尾款待付）与列表「订单状态」列都取 `orderStatus`，口径 = order-b `NeoOrderStatus`（`order/order-domain/.../domain/utils/NeoOrderStatus.java`）：

| code | msg | shownName |
|---|---|---|
| 1 | 待支付 | 待支付 |
| 2 | 已支付 | 已支付 |
| 3 | 已支付 | 已支付 |
| 4 | 手动取消 | 已取消 |
| 5 | 自动取消 | 已取消 |
| **6** | **已退款（全额退款）** | **已退款** |
| **7** | **部分退款** | **部分退款** |
| 8 | 定金已支付 | 等待付尾款 |
| 9 | 尾款已支付 | 尾款已支付 |
| 10 | 定金已退款 | 已退款 |

> **6 / 7 后端有区分**（全额退款 vs 部分退款）。学员档案「订单信息」tab 的订单状态同源，见 [cronus/StudentProfile/orderInfo.md](../../cronus/StudentProfile/orderInfo.md)。

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
