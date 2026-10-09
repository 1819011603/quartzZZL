# 课程类订单 · 一对一订单 tab（soloclazz）

> 2026-10-09 前端 gaotu-fe-goodsmanage master 代码整理（这个 tab 没抓包）；后端对照 order（order-b）。页面级接口见 [_page.md](_page.md)。课时包 / 小班课 tab 用的是同一个列表接口，只是 productType 不一样，见 [lessonpackage.md](lessonpackage.md)、[miniclass.md](miniclass.md)。

## 组件

- tab 内容：`src/pages/OrderManage/list/index.js:981` `soloClazzList` → `src/components/OrderList`（orderType=`soloclazz`），权限标签 `gaotu_boss_p_soloclazz_order`
- 列表请求走 `orderItemAysncFunc`（`OL/modules/BaseList.tsx:94`），body 是 `{condition:{...搜索项, productType:6003}, pager}`
- **上红框搜索项为空时前端直接返回空，不发请求**（`BaseList.tsx:232`），所以切到这个 tab 后不填条件点查询，抓包是看不到请求的
- OES 配置 `useOrderJson.js:313-320`：表头按钮「创建订单 / 创建门店订单」；行按钮「详情 / 修改地址 / 调课调班」（权限 `OES_OPT_AFTER_TURNCLAZZ`）

前缀约定同 [normal.md](normal.md)：`OL/` = `src/components/OrderList/`，`OM/` = `src/pages/OrderManage/`。

## 接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 查询/翻页（有搜索项时） | `POST /orderComponent/orderItemFieldSearch`，body `{condition:{productType:6003,...}, pager}` | `queryOrderItemList` | `OL/modules/BaseList.tsx:95,243`（`OL/services.ts:68`） | order-b | 实物订单搜索接口 [947633] | 读 |
| 行「详情」 | 不发请求，跳 `/ordermanage/prodetail/{orderItemNumber}`（实物订单详情页，详情页接口不在本页范围） | `newItemDom` | `OM/list/index.js:803` | — | — | — |
| 行「修改地址」 | `POST /orderComponent/queryAllWaitSendItem` → `POST /order/boss/facade/changeAddress` | 同 [normal.md](normal.md) | `OM/detail/OrderStep/ModifyAddress/index.js:29,74` | order-b | [947365] / [947342] | 读 / 写 |
| 行「调课调班」 | `/afterSale/b/transfer/*` | 同 [normal.md](normal.md) | `OM/component/TransferClazz/` | after-sales | [1069148] 等 | 读 + 写 |
| 物流列 / 小眼睛 | 同 [normal.md](normal.md) | — | `OL/components/ExpressDetailTable/index.tsx:31`、`OL/columnsConfig.tsx:103` | express-management / student-center | [46863] | 读 |

## 关键表

| 接口 | 后端位置 | 读表 | 写表（操作） | 备注 |
|---|---|---|---|---|
| `orderItemFieldSearch` | `order-controller/.../search/OrderComponentController.java:144`（类 `/orderComponent` :55）→ `order-app/.../search/application/impl/OrderItemSearchApplication.java` → `.../search/service/impl/OrderItemSearchService.java` → `AbstractSearchService#doSearch:81` | **ES** 订单项宽表 alias `index.orderItem.alias`（推断是 `gaotu_order_wide_order_item_search_rollover`，**未确认**），拿根订单项号；MySQL 兜底 `gaotu.order_item`（`OrderItemRepository#pageByAccurateQuery:222`，按 userId / orderItemNumber / orderType / skuNumber 查）；聚合补字段走 `CommonPolymerizeService` + `polymerize/provider/binder/claimer/impl/*`（订单项、订单项扩展、支付、支付计划、商品、用户、地址、物流、售后等） | 无 | 开关 `search.orderItem.allowComplexSearch`（默认 true）/ `search.orderItem.coverLogic` |

`/authority/orderItemFieldSearch`（`OrderComponentController.java:156`）只给 EES 用（`B_client` 必须是 `EES`），OES 不会调。

## 排查提示

- 一对一订单查不到 → 先确认搜索条件里有没有填值（没填就没发请求）；再用订单项号查一次，能查到就说明是 ES 宽表没同步

## 青舟接口详情页

- [POST /orderComponent/orderItemFieldSearch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947633&appId=order-b.gaotu100.com&branchName=release) id=947633
- [POST /orderComponent/authority/orderItemFieldSearch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947705&appId=order-b.gaotu100.com&branchName=release) id=947705（EES 专用）
