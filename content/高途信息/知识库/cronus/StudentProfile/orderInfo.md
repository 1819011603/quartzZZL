# 学员档案 / 订单信息（OrderInfo）

> 2026-10-16 排查「学员档案点开订单信息，学员部分退款却显示『已退款』」问题整理。

## 定位

| 项 | 值 |
|---|---|
| 入口 | 学员档案抽屉 → 「订单信息」tab（打开时 `activeKey=OrderInfo`）；各页面点学员都能进入 |
| 前端服务文件 | `cronus/src/pages/StudentProfile/services/orderInfo.js`（`getOrderInfo`） |
| 前端调用路径 | `POST /student-center/ols/w/studentArchives/orderInfo` |
| tab 内容 | 由 GAIA 远程物料渲染（cronus 内**无本地组件**）；列字段对齐后端 `OrderInfoVO` |
| 后端服务 | student-center |
| 后端 Controller | `OlsStudentArchivesController#orderInfo`（`student-center-web/.../web/api/OlsStudentArchivesController.java:148`，类 `@RequestMapping("/ols/")`） |
| 后端实现 | `OlsStudentArchivesBiz#orderInfo:953` → `OrderItemComplexSearchService#orderItemComplexSearch` |
| 数据源 | Feign → **order-b（电商）** `POST /feignService/order/complexSearch/queryByUser` |

> 入口传给抽屉的参数：`userId`；`RefundPrevention/components/OrderInfo` 只是用 `activeKey=OrderInfo` 打开本抽屉的跳板，本身不发请求。

## 接口清单

| 触发 | 前端调用路径 | 后端服务 | 后端 path | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|
| 打开订单信息 tab / 筛选 / 翻页 | `POST /student-center/ols/w/studentArchives/orderInfo` | student-center | `/ols/w/studentArchives/orderInfo` | PC端订单记录 [30624] | 读 |
| 订单筛选下拉（班级 / 商品类型） | `POST /student-center/ols/w/studentArchives/orderInfo/skuTypeGroups` | student-center | `/ols/w/studentArchives/orderInfo/skuTypeGroups` | 订单筛选-班级/商品类型下拉选项 [4882736] | 读 |
| （内部数据源，前端不直连） | — | order-b | `/feignService/order/complexSearch/queryByUser` | [947462] | 读 |

## 关键字段

- 出参 `OlsStudentArchives.OrderInfoVO`（`student-center-service/.../domain/model/OlsStudentArchives/OrderInfoVO.java`）：
  - `orderStatus`（Integer）**订单状态** — 口径 = 电商订单状态枚举（见下）
  - `orderNumber` 订单号 / `skuName`（商品信息列：班级名称/班级ID/课程类型）
  - `orderRealPrice` 订单金额 / `orderDiscountPrice` 抵扣 / `orderNeedPayPrice` 需实付（前端列「订单 / 抵扣 / 需实付」）
  - `attributionPerson` 业绩归属人 / `attributionType` 归属类型（拉新K12 等）
  - `createTime` 下单时间 / `paidTime` 支付时间 / `needDelivery` / `displayGroup`（1 班课风格 / 2 非班课风格）
- 入参 `OrderInfoRequest`：`userId`、`orderStatus[]`、`orderType[]`（1 校区 / 0 非校区）、`skuType[]`、`courseType[]`、`orderNumbers`、`pager`
- 落库/取数：student-center **不落业务表**，直接 Feign 调 order-b `complexSearch/queryByUser`

## 订单状态枚举（电商 order-b `NeoOrderStatus`，`order/order-domain/.../domain/utils/NeoOrderStatus.java`）

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

> **6 / 7 后端有区分**：接口返回的是两个不同整数（`shownName` 也分别给了「已退款」「部分退款」）。若页面把「部分退款(7)」显示成「已退款」，是**展示层把 6/7 映射成了同一文案**，不是电商没返回。

## 排查提示

- 学员档案订单状态显示不对（如部分退款显示「已退款」）→ 先抓 `/ols/w/studentArchives/orderInfo` 返回的 `orderStatus` 是 6 还是 7；后端已区分，问题多在展示层映射。
- 订单查不到 / 少数据 → student-center orderInfo 依赖 order-b `complexSearch/queryByUser`，看 order-b 侧是否返回。
- 订单列表的「订单概况」统计卡（累计支付金额 / 引流课订单数 / 正价课订单数…）来源未确认，疑似独立物料 / 线索域接口；需要时按店抓包补记。

## 青舟接口详情页

- [POST /ols/w/studentArchives/orderInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30624&appId=student-center&branchName=release) id=30624
- [POST /ols/w/studentArchives/orderInfo/skuTypeGroups](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4882736&appId=student-center&branchName=release) id=4882736
- [POST /feignService/order/complexSearch/queryByUser](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947462&appId=order-b.gaotu100.com&branchName=release) id=947462（order-b）
