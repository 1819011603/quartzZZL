# 课程类订单 · 小班课订单 tab（miniclass）

> 2026-10-09 前端 gaotu-fe-goodsmanage master 代码整理（这个 tab 没抓包）；后端对照 order（order-b）。页面级接口见 [_page.md](_page.md)。

## 组件

- tab 内容：`src/pages/OrderManage/list/index.js:1069` `miniclassList` → `src/components/OrderList`（orderType=`miniclass`），权限标签 `oes_menu_order_PrivateClazz_list_`
- 列表请求同 [soloclazz.md](soloclazz.md)，只是 `productType=6004`；上红框没填条件时不发请求
- OES 配置 `useOrderJson.js:286-294`：表头「创建订单 / 创建门店订单 / 插班报名」（插班报名跳 `/ordermanage/createOrder?...&orderType=insert`）；行按钮「详情 / 修改地址 / 调课调班」

## 接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 查询/翻页（有搜索项时） | `POST /orderComponent/orderItemFieldSearch`，body `{condition:{productType:6004,...}, pager}` | `queryOrderItemList` | `src/components/OrderList/modules/BaseList.tsx:95,243`（`src/components/OrderList/services.ts:68`） | order-b | 实物订单搜索接口 [947633] | 读 |
| 行「详情」 | 不发请求，跳 `/ordermanage/prodetail/{orderItemNumber}` | `newItemDom` | `src/pages/OrderManage/list/index.js:803` | — | — | — |
| 行「修改地址」/「调课调班」 | 同 [normal.md](normal.md) | — | `src/pages/OrderManage/detail/OrderStep/ModifyAddress/index.js`、`src/pages/OrderManage/component/TransferClazz/` | order-b / after-sales | [947342] / [1069148] | 写 |

## 关键表

同 [soloclazz.md](soloclazz.md)「关键表」：ES 订单项宽表 + MySQL `gaotu.order_item` 兜底；聚合时另外读小班课扩展（`OrderItemScExtRepository`，具体表名**未细追**）。列表接口不写表；改地址写哪些表见 [normal.md](normal.md)。

## 青舟接口详情页

- [POST /orderComponent/orderItemFieldSearch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947633&appId=order-b.gaotu100.com&branchName=release) id=947633
