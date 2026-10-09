# 非课程类订单（ordermanage）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-goodsmanage master 代码整理；后端对照 order（order-b）、gaotu-ols、product-server（product-server-b）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-goods/ordermanage/list` |
| 基座 | OES ark → 子应用 app-goods |
| 前端仓库 | gaotu-fe-goodsmanage `http://git.baijia.com/gaotu-ctech/gaotu-fe-goodsmanage`（master，本地 `~/IdeaProjects/WebProject/gaotu-fe-goodsmanage`；青舟 serviceCode `baijia.gaotu.Business.fe.gaotu-fe-goods`） |
| 前端路由 | `config/routes.js:292-299` → `src/pages/OrderManage/list/index.js`，wrapper `olscampus`，权限 `canNonClazzOrderList`（`src/access.js:107`，标签 `gaotu_boss_p_physical_order`） |
| 同组件复用 | 和 [课程类订单](../normalOrdermanage/_page.md)、[付款记录](../payRecord/_page.md) 是同一个组件；本页 = `NO_CLAZZ_BLOCK`（`list/index.js:70`，路由匹配不上时也走这个兜底） |
| 后端主服务 | `/orderComponent/*` → gapm-appid `order-b-gaotu100-com` → 青舟 appId `order-b.gaotu100.com`（仓库 **order**，`OrderComponentController`） |

## tab 列表

无 tab：`NO_CLAZZ_BLOCK` 直接渲染一个统一列表 `nonClazzList`（`list/index.js:922`，orderType=`nonclazz`），把实物 / 倾听师 / 批改次卡 / 外部履约 / 软件会员等合到一起，用「商品类型」筛选。

- 搜索项（`src/components/OrderList/constants.tsx:295`）：下单时间、订单号、学员、**商品类型**（级联，数据来自 product-b 类型树）、SKU 名称/ID、SPU 名称/ID；下红框只有订单状态
- **没有默认搜索项**，上红框全空时前端直接返回空列表（`BaseList.tsx:232`），所以抓包里只点「查询」看不到列表请求，要先填一个条件
- 表头按钮（`useOrderJson.js:343`）：「创建订单 / 创建门店订单」+「售后操作手册」入口
- 行按钮按每一行的 `baseOrderItem.orderType` 决定（`list/index.js:800` `newItemDom`）：实物（50）是「详情 / 修改地址」；倾听师 / 批改次卡 / 外部履约只有「详情」；8007 软件会员、8027 OMO 课时包是「详情 / 修改地址 / 调课调班」

## 页面级接口

`OL/` = `src/components/OrderList/`，`OM/` = `src/pages/OrderManage/`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（wrapper olscampus） | `POST /ols/w/campus/list` | `getOlsCampusList` | `src/models/useOlsCampus.js:19`（`src/services/physicalOrder.js:239`） | gaotu-ols | 校区列表 [36004] | 读 |
| 进页面 | `POST /orderComponent/grayGroup/checkGrayGroup` | `useOrderCreationGuard` | `OM/list/hooks/useOrderCreationGuard.js:34` | order-b | 灰度组命中判断 [5304562] | 读 |
| 进页面（全局 model） | `GET /intranet-rpc/course-setting/feign/options/bff/list` | `getCommonDictionary` | `src/models/useBffSelectItem.js:11`（`src/services/goodsManage.js:13`） | course-setting | 共享字典 [34362] | 读 |
| 进页面（「商品类型」下拉挂载） | `POST /bgwApi/product-b/b/product/productTypeTree/category/listTree`，body `{}` | `getProductTypeTree` | `OL/components/ProductTypeSelect/index.tsx:23`（`OL/services.ts:74`） | product-b | 获取商品类型树 [2734234] | 读 |
| 查询/翻页（有搜索项时） | `POST /orderComponent/orderItemFieldSearch`，body `{condition:{...搜索项}, pager}`（**不带 productType 固定值**，按「商品类型」筛选项传） | `queryOrderItemList` | `OL/modules/BaseList.tsx:204-208,243`（`OL/services.ts:68`） | order-b | 实物订单搜索接口 [947633] | 读 |
| 物流列点击 | `POST /express-management/invoice/queryExpressInvoiceByOrderNumbers`（实物订单传 `type:6`） | `getExpressDetail` | `OL/components/ExpressDetailTable/index.tsx:31` | express-management | 物流发货单 [46863] | 读 |
| 手机号/地址「小眼睛」 | `POST /component/student-center/userSecret/getBaseInfo`、`.../getAddress` | `querySecretPhone` / `querySecretAddress` | `OL/columnsConfig.tsx:103,109` | student-center | 未查 id | 读 |
| 行「详情」 | 不发请求，跳 `/ordermanage/prodetail/{orderItemNumber}`（实物订单详情页，不在本页范围） | `newItemDom` | `OM/list/index.js:803` | — | — | — |
| 行「修改地址」→ 打开 | `POST /orderComponent/queryAllWaitSendItem` | `getOrderDeliveryDetail` | `OM/detail/OrderStep/ModifyAddress/index.js:29`（`src/services/physicalOrder.js:191`） | order-b | 获取待发货订单 [947365] | 读 |
| 行「修改地址」→ 确定 | `POST /order/boss/facade/changeAddress` | `getChangeAddress` | `OM/detail/OrderStep/ModifyAddress/index.js:74`（`OM/detail/service.js:8`） | order-b | 修改地址 [947342] | 写 |
| 行「调课调班」（仅 8007/8027） | `/afterSale/b/transfer/preview/basic`、`/preview/calculate`、`/submit`、`/getPayInfo` | 同课程订单 | `OM/component/TransferClazz/` | after-sales | [1069172] / [1069159] / [1069148] / [1069212] | 读 + 写 |
| 「创建订单 / 创建门店订单」 | 不发请求，跳 `/ordermanage/createOrder?sourceUrl=...`；灰度命中先弹引导/拦截 | `CreateOrderButton` | `OM/list/CreateOrderButton/index.js:109-141` | — | — | — |
| 「重置」 | 不发请求，只清 dva 里缓存的筛选条件 | `onReset` | `OM/list/index.js:945` | — | — | — |

## 关键表

### 接口 → 表

| 接口 | 后端位置 | 读表 | 写表（操作） | 备注 |
|---|---|---|---|---|
| `orderItemFieldSearch` | `order-controller/.../search/OrderComponentController.java:144`（类 `/orderComponent` :55）→ `order-app/.../search/application/impl/OrderItemSearchApplication.java` → `OrderItemSearchService` → `AbstractSearchService#doSearch:81` | **ES** 订单项宽表 alias `index.orderItem.alias`（推断是 `gaotu_order_wide_order_item_search_rollover`，**未确认**）；MySQL 兜底 `gaotu.order_item`（`OrderItemRepositoryImpl#pageByAccurateQuery:222`）；聚合 `CommonPolymerizeService` + `polymerize/provider/binder/claimer/impl/*` 补订单项 / 支付 / 商品 / 地址 / 物流 / 售后 | 无 | `search.orderItem.allowComplexSearch`（默认 true） |
| `listTree` | `product-server-b/.../controller/typetree/ProductTypeTreeController.java:53`（类 `/b/product/productTypeTree/category` :36） | `gaotu.product_type_tree`（`ProductTypeTreeMapper.xml`） | 无 | 网关前缀 `/bgwApi/product-b` |
| `campus/list` | `gaotu-ols-web/.../facade/api/CampusInfoController.java:75`（类 `/w/campus` :32，网关前缀 `/ols`）→ `gaotu-ols-service/.../app/service/CampusInfoAppService.java:597` | Feign 组织服务 `organizationAclService.listCampusByAccount`（当前账号有权限的校区）+ `course_center.campus_info`（`CampusInfoMapper.xml:22`） | 无 | — |
| `queryAllWaitSendItem` | `OrderComponentController.java:226` → `ComponentTobApplication#queryAllWaitSendItemResult:78` | **表未细追** | 无 | — |
| `changeAddress` | `order-controller/.../boss/BossController.java:112` → `BossOrderService.java:93` → `ModifyAddressService.java:211` | 先 Feign 物流服务校验 | `gaotu.order_info`、`order_info_commodity`、`order_item`、`pay_info` UPDATE 地址 id | 发 `ModifyAddressEvent` |
| `checkGrayGroup` | `GrayGroupController.java:40` | 无表，Apollo `order.gray.group.rule.config` + 员工组织 Feign | 无 | — |

### 表

| 表 | 库 | 含义 |
|---|---|---|
| ES 订单项宽表 | ES（alias 见上） | 订单项搜索，只用来拿 orderItemNumber 和分页 |
| `order_item` | gaotu | 订单项（实物 / 一对一 / 课时包 / 小班课 / 倾听师 等新实体），`order_type` 就是前端的 productType 值 |
| `product_type_tree` | gaotu | 商品类型三级树（product-server） |
| `campus_info` | course_center | 校区 |

库名说明：order 的 mapper XML 里表名不带库前缀，`gaotu` 是在 test 环境 cluster 142 里查到同名表推出来的；product / ols 的库名取自 mapper XML 前缀。

## 排查提示

- 点查询没反应 / 没请求 → 正常，必须先填一个上红框条件
- 商品类型下拉是空的 → 看 product-b `listTree`
- 查不到某个订单 → 用订单号查一次（会走 MySQL 兜底）；能查到说明 ES 宽表没同步
- 前端注释说「搜索项为空时走带权限接口」，但 OES 配置没开 `AUTHINTERFACECHANGE`，实际上**永远只调 `orderItemFieldSearch`**；`/authority/*` 只给 EES 用

## 青舟接口详情页

- [POST /orderComponent/orderItemFieldSearch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947633&appId=order-b.gaotu100.com&branchName=release) id=947633
- [POST /orderComponent/grayGroup/checkGrayGroup](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5304562&appId=order-b.gaotu100.com&branchName=release) id=5304562
- [POST product-b/b/product/productTypeTree/category/listTree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734234&appId=product-b&branchName=release) id=2734234
- [POST /w/campus/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36004&appId=gaotu-ols&branchName=release) id=36004
- [POST /orderComponent/queryAllWaitSendItem](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947365&appId=order-b.gaotu100.com&branchName=release) id=947365
- [POST /order/boss/facade/changeAddress](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947342&appId=order-b.gaotu100.com&branchName=release) id=947342
- [POST /orderComponent/authority/orderItemFieldSearch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947705&appId=order-b.gaotu100.com&branchName=release) id=947705（EES 专用，OES 不调）
