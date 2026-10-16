# 学员档案 / 订单信息（OrderInfo）

> 2026-10-16 排查「学员档案点开订单信息，学员部分退款却显示『已退款』」问题整理。

## 问题结论：部分退款显示成「已退款」（根因在链路中段，不是前端漏映射）

业务现象：学员部分退款（仍在读），学员档案·订单信息列表却显示「已退款」。

链路（**第 2 步就把「部分退款」丢了**）：

1. **电商 order-b 的「订单状态码」本身有区分**：`OrderStatusEnums`（`order/order-api/.../orderinfo/enums/OrderStatusEnums.java`）`6=全部退款(已退款)` / `7=部分退款(部分退款)`。
2. 但 order-b 返回给学员档案接口的**不是状态码，是中文文案 `orderStatusName`**，且生成文案时就已合并（`order/order-app/.../search/service/convert/CommonSearchRequestConverter.java`）：
   - **订单级** `convertOrderStatusName`：`case PAID / PART_REFUND / TAIL_PAID: return "已支付"` —— **部分退款(7) 被当成「已支付」**；`FULL_REFUND / DEPOSIT_REFUND → "已退款"`。
   - **订单项级** `convertOrderItemStatusName`：只要有售后记录（`lastAfterSaleType != 0`）→ **一律 "已退款"**（全退/部分退不分；售后类型枚举：0 部分退款 / 1 退款退货 / 2 退款退课 / **7 部分退课时(部分退款)**）。
3. student-center 拿这个文案反查自己的枚举：`OrderStatusEnum.getByDesc(name)`（`OrderDomainWrapper.convertOrderRecordDO*`），而 student-center 的 `OrderStatusEnum`（`student-center-service/.../enums/OrderStatusEnum.java`）只有 5 档：`1 待付款 / 2 已支付 / 3 已取消 / 4 已退款 / 31 尾款待支付` —— **没有「部分退款」**。
4. 前端 GAIA 物料 `OrderInfoList`（`src/pages/utils/constant.ts`，CDN 包实测一致）同样只映射 `1/2/3/4/31`，无「部分退款」。

**结论**：区分全退/部分退的能力在 **order-b 生成状态文案时就没了**（订单级→并入「已支付」；订单项级→并入「已退款」），student-center 与前端物料两层都没有「部分退款」档位。**要区分必须从链路中段改**：order-b 透传状态码 `6/7`（或新增「部分退款」文案）→ student-center `OrderStatusEnum` 加档 → 前端 `OrderInfoList` 映射加档。截图那条（订单项级）因此显示「已退款」。

### 实测复现（2026-10-16）

**线上（prod）——截图那两条单，走订单项接口 `orderItemFieldSearch` 取到原始数据：**

```
POST /bgwApi/orderComponent/orderItemFieldSearch   (order-b, 网关 appId order-b.gaotu100.com)
body: {"condition":{"orderItemNumberList":["425838771470074810","425838771470075834"]},"pager":{"pageNum":1,"pageSize":10}}
```

| 订单号(订单项) | 实付 price | 已退 totalRefundPrice | lastSuccessAfterSalesType | 学员档案显示 | 正确定性 |
|---|---|---|---|---|---|
| 425838771470075834 | 218900(￥2189) | **21890(￥218.9)** | 7(部分退课时) | **已退款(4)** | ❌ 应为「部分退款」 |
| 425838771470074810 | 218900(￥2189) | 218900(￥2189) | 2 | 已退款(4) | ✅ 全额退款 |

→ **铁证**：订单项**只退了￥218.9/￥2189（部分退款，afterSaleType=7），学员档案却显示「已退款」**；而原始 `baseOrderItem.orderStatus` 两条都还是 **2（已支付）**。
订单项接口 `orderItemFieldSearch` 是 OES「订单管理」下钻用的，可按订单项号查到这两条（`orderFieldSearch` 按订单号查不到，因为它们不是 root 订单）。
（OES 各 tab 的搜索接口与 `productType` 见 [goods/normalOrdermanage/normal.md](../../goods/normalOrdermanage/normal.md)。）

**test 直连复现（订单级）**：test `gaotu.order_info` 里 `order_status=7` 的单 `4801762098081169408`（user `17634521020958`），调 `/ols/w/studentArchives/orderInfo` 返回 **`orderStatus=2`（已支付）**。

**接口返回的 `orderStatus` 值域恒为 `1/2/3/4/31`（student-center `OrderStatusEnum`），线上线下都拿不到电商原码 6/7。**

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

- 学员档案订单状态显示不对（如部分退款显示「已退款」/「已支付」）→ 见上方「问题结论」：接口返回的 `orderStatus` 是 1/2/3/4/31（**已被 order-b 文案 + student-center `getByDesc` 合并**），不是电商原码 6/7。
- 订单查不到 / 少数据 → student-center orderInfo 依赖 order-b `complexSearch/queryByUser`，看 order-b 侧是否返回。
- 订单列表的「订单概况」统计卡（累计支付金额 / 引流课订单数 / 正价课订单数…）来源未确认，疑似独立物料 / 线索域接口；需要时按店抓包补记。

## 青舟接口详情页

- [POST /ols/w/studentArchives/orderInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30624&appId=student-center&branchName=release) id=30624
- [POST /ols/w/studentArchives/orderInfo/skuTypeGroups](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4882736&appId=student-center&branchName=release) id=4882736
- [POST /feignService/order/complexSearch/queryByUser](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=947462&appId=order-b.gaotu100.com&branchName=release) id=947462（order-b）
