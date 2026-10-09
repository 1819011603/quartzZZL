# 课程类订单 · 课时包订单 tab（lessonpackage）

> 2026-10-09 前端 gaotu-fe-goodsmanage master 代码整理（这个 tab 没抓包）；后端对照 order（order-b）。页面级接口见 [_page.md](_page.md)。

## 组件

- tab 内容：`src/pages/OrderManage/list/index.js:1006` `lessonpackageList` → `src/components/OrderList`（orderType=`lessonpackage`），权限标签 `oes_menu_order_clazzHourPackage_`
- 列表请求同 [soloclazz.md](soloclazz.md)，只是 `productType=7001`；上红框没填条件时不发请求
- OES 配置 `useOrderJson.js:280-285`：表头「创建订单 / 创建门店订单」；行按钮只有「详情」

## 接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 查询/翻页（有搜索项时） | `POST /orderComponent/orderItemFieldSearch`，body `{condition:{productType:7001,...}, pager}` | `queryOrderItemList` | `src/components/OrderList/modules/BaseList.tsx:95,243`（`src/components/OrderList/services.ts:68`） | order-b | 实物订单搜索接口 [947633] | 读 |
| 行「详情」 | 不发请求，跳 `/ordermanage/prodetail/{orderItemNumber}` | `newItemDom` | `src/pages/OrderManage/list/index.js:803` | — | — | — |

## 关键表

同 [soloclazz.md](soloclazz.md)「关键表」：ES 订单项宽表（`index.orderItem.alias`）+ MySQL `gaotu.order_item` 兜底；聚合时另外读课时包扩展（`OrderItemHourPackageExtRepository`，具体表名**未细追**）。不写表。

## 青舟接口详情页

- [POST /orderComponent/orderItemFieldSearch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947633&appId=order-b.gaotu100.com&branchName=release) id=947633
