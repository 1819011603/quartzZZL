# 售后管理（goodsrefund）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-goodsmanage master 代码整理；后端对照 after-sales（master `41c2f5e`）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-goods/goodsrefund`（`?tabKey=clazz/goods/listener/inquiry`） |
| 基座 | OES ark → 子应用 app-goods |
| 前端仓库 | gaotu-fe-goodsmanage `http://git.baijia.com/gaotu-ctech/gaotu-fe-goodsmanage`（master `7e4c4bc`，本地 `~/IdeaProjects/WebProject/gaotu-fe-goodsmanage`） |
| 前端路由 | `config/routes.js:231-238`「售后管理（新）」→ `src/pages/GoodsRefund/index.js`，wrapper `@/wrappers/ordermanage` + `@/wrappers/olscampus`，权限 `canPhysicalGoodsRefund`（`src/access.js:38`，tag `gaotu_boss_p_physical_goods_refund`） |
| 详情子路由 | `config/routes.js:240-244` `/goodsrefund/aftersaledetail/:afterSaleNumber/:type/:orderItemNumber` → `src/pages/GoodsRefund/AfterSaleDetail/index.js`，见 [aftersaledetail.md](aftersaledetail.md) |
| 后端主服务 | 网关前缀 `/afterSale` → 青舟 appId `after-sales`（仓库 **after-sales** `http://git.baijia.com/gaotu/lvyue/after-sales`，`AfterSaleManagementController` / `AfterSaleCommonController` / `RetrieveManagementController` / `AfterSaleTransferController`） |

前缀常量：`src/services/universally.js:6` `COMPONENT = isBoss() ? '' : '/component'`，`isBoss()`（`src/utils/utils.js:350`）判断 host 含 `mi.gaotu100.com`，所以在 OES 下 `/afterSale/common/dictionary` 无前缀。`src/services/physicalOrder.js:16` `baseOlsApi` 仅 dev 环境为 `/olsApi`。

## tab 列表

四个 tab 共用 `src/pages/GoodsRefund/components/UniversalRefund/index.js`（`goodsType` 区分），差别只在默认 `skuTypeList`（`UniversalRefund/index.js:20-25`，SKU_TYPE 定义见 `src/pages/GoodsRefund/config.js:10`）和列配置（`UniversalRefund/config.js` `COLUMNS_CONFIG`），接口完全一样，所以不拆 tab 文件。

| tab（key） | 默认 skuTypeList | 可见条件（`index.js:24-30`） |
|---|---|---|
| 课程售后（clazz） | `[2, 6003, 7001, 6004, 8027]`（班课/1v1/课时包/小班课/OMO课时包） | `PRODUCT_CLAZZ_REFUND` 或 `OLS_OPT_AFTER_SALE_CLAZZ_TAB` |
| 实物售后（goods） | `[50]` | 非 OLS 且 `PRODUCT_GOODS_REFUND` |
| 其它商品售后（listener） | `productTypeEnum` 中未禁用项（`UniversalRefund/config.js:122`） | 非 OLS 且 `PRODUCT_LISTENER_REFUND` / `OES_CORRECT_REFUND_MENU` |
| 售后查询（inquiry） | 不传，后端用 Apollo `aftersale.product.type.config` 并集兜底；不自动查询（`autoSearch=false`） | 非 OLS 且 `OES_OPT_AFTER_SALES_INQUIRY` |

右上角「售后手册」入口（`src/components/AfterSaleHandbookEntry/index.jsx:17`）只是 `window.open` 文档，不调接口。

## 页面级接口

`UR/` = `src/pages/GoodsRefund/components/UniversalRefund/`；`GR/` = `src/pages/GoodsRefund/`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（app 启动即初始化的全局 model） | `GET /intranet-rpc/course-setting/feign/options/bff/list?fields=all` | `getCommonDictionary` | `src/models/useBffSelectItem.js:11`（`src/services/goodsManage.js:13`） | course-setting | 共享字典 | 读 |
| 进页面（wrapper olscampus，OES/OLS 且校区为空） | `POST /ols/w/campus/list` | `getOlsCampusList` | `src/wrappers/olscampus.js:30` → `src/models/useOlsCampus.js:19`（`src/services/physicalOrder.js:239`） | gaotu-ols | 共享字典（校区） | 读 |
| 进页面（wrapper ordermanage，字典为空） | `POST /afterSale/common/dictionary` | `dictionary` | `src/wrappers/ordermanage.js:19` → `src/models/orderEnum.js:26`（`src/services/universally.js:19`） | after-sales | 售后字典 [1069174] | 读 |
| 进 tab（非 inquiry 自动）/查询/翻页 | `POST /afterSale/b/afterSaleList`（OLS 用户走 `/afterSale/b/afterSaleList/offline`） | FeituData `fetch` | `UR/index.js:40,267`（`GR/service.js:43` 同 path 备用） | after-sales | B端售后列表(OES) [1069147] / (OLS) [1069211] | 读 |
| 进「售后查询」tab | `POST /product-b/b/product/productTypeTree/category/listTree` | `getProductTypeTree` | `UR/index.js:50`（`GR/service.js:103`） | product-b（未追后端） | 商品类型树 | 读 |
| 列表「查看退货单」（实物） | `POST /express-management/refundInfoToBoss` | `refundToBoss` | `GR/components/ReturnOrder.js:66`（`GR/service.js:63`） | express-management（未追后端） | 退货单明细 | 读 |
| 退货单弹窗内物流轨迹 | `POST /express-management/refund/queryExpressInfo` | `queryExpressInfo` | `GR/components/Trajectory.js:42`（`GR/service.js:73`） | express-management（未追后端） | 物流轨迹 | 读 |
| 列表「重新提交对公退款」→ 确定 | `POST /afterSale/b/resubmitPayeeInfo` | `reSubmitPayeeInfo` | `GR/components/PayeeInfo/index.js:32`（`GR/service.js:11`） | after-sales | 重新提交收款人信息 [1069202] | 写 |
| 列表「取消课程转移」→ 确定 | `POST /afterSale/b/transfer/accountSeparateCancel` | `cancelAccountSeparate` | `UR/index.js:138`（`GR/service.js:97`），body `{orderNumber}` | after-sales | 课程转移取消 [2761445] | 写 |
| 列表手机号「复制」明文 | `POST /component/student-center/userSecret/getBaseInfo`（`/component` 写死） | `getBaseInfo` | `src/components/InfoDesen/index.js:44`（`src/components/InfoDesen/service.js:20`），列 `UR/config.js:165` | student-center | 用户敏感信息 | 读 |
| 列表「查看详情」 | 跳 `/goodsrefund/aftersaledetail/...` | — | `UR/config.js:341` | — | 见 [aftersaledetail.md](aftersaledetail.md) | — |
| 列表「查看退款单」 | 跳 `/ordermanage/prodetail/{orderItemNumber}` | — | `UR/config.js:327` | — | 非本页 | — |
| 列表图片「查看」 | 无请求（图片预览） | — | `UR/config.js:274` | — | — | — |

入参示例（抓包）：`{"skuTypeList":[2,6003,7001,6004,8027],"pager":{...},"beginTime":...,"endTime":...,"campusNumberList":[]}`；默认时间是最近 30 天（`UR/index.js:192`），`timeRange` 在 `handleBefore`（`UR/index.js:145`）拆成 `beginTime/endTime`。

## 关键表（`after_sale` 库）

> 库名取自 mapper XML 里的 `after_sale.` 前缀（`after-sales-infrastructure/src/main/java/com/gaotu/lvyue/aftersales/infrastructure/repository/mapper/*.xml`），没核对数据源配置。不读 ES。

### afterSaleList 链路

`AfterSaleManagementController.java:61`（类 `@RequestMapping("/afterSale/b")`）`:78` → `AfterSaleForBServiceImpl#queryAfterSaleListByCondition:334`（下称 `B`）：

1. 未传 skuType 时用 Apollo `aftersale.product.type.config` 兜底（:344），为空直接报「商品类型不可为空」。
2. OES：除 skuType/pager/skuTypeList/campusNumberList 外字段全空则直接返回空（:378-399）。OLS：按 header `user_info` 的 accountId 经 `StaffFacade#listCampusByAccountId`（staff 服务）收窄校区（:404-431）。
3. `getQueryConditionByRequest:1163` 组装条件；`userInfo` 先按手机号经用户服务（`StandardUserService`）换 userId。
4. 计数 `AfterSaleMapper.countByCondition`，查询 `searchByConditionAndPager`；开关 `searcherEESwitch` 开且带 `accountId`（EES 挽单人视角）时改走 `searchByConditionEES`/`countByConditionEES`（多 join `retrieve_apply`）。
5. `AfterSaleDomainServiceImpl#batchConstructAfterSaleBo:177` 批量补子表 + Feign：订单（order 服务 `AfterSaleRefundFeignClient#listByOrderNumbers`）、班级/课程（course-setting / course-center）。
6. `afterSaleListFillOutsideInfo` 开时补：用户姓名/脱敏手机（user 服务）、实物商品名（老商品 course-setting `IProductFeignService` clientv2 / 新商品中台 clientv3）、图片 URL（storage）、拼团（order 服务 `GrouponQueryApiFeignClient`）、OES 详情 URL。

### 接口 → 表

| 接口 | 读表 | 写表（操作） | 其它 |
|---|---|---|---|
| `afterSale/common/dictionary` | 无 | 无 | 枚举来自 Apollo `dictionary.product.enums`（`AbstractAfterSaleService.java:253`，方法 `:1077`） |
| `afterSaleList` / `afterSaleList/offline` | `after_sale`（s）join `after_sale_authority_management`（m，按 sku_number/order_item_number/campus_number 过滤）；EES 分支再 join `retrieve_apply`；补数读 `after_sale_order_item`、`after_sale_product`、`after_sale_ext`、`after_sale_item`、`after_sale_process_node`、`after_sale_process_log`、`after_sale_transfer_record`、`retrieve_apply` | 无 | Feign 见上；OLS 校区来自 staff |
| `resubmitPayeeInfo` | `after_sale` | `after_sale_process_log` INSERT、`after_sale_ext` 批量 INSERT（`B#resubmitPayeeInfo:696`，:716/:726） | Feign order `orderAuditApiFeignClient.submitCorporateOrderRefundAudit` 重新发起对公退款审核 |
| `transfer/accountSeparateCancel` | `after_sale_transfer_record`、`after_sale` | 经 `cancelDefaultTransferBetweenUser` 更新售后/转移记录状态（`B#accountSeparateCancel:1743` → `accountSeparateCancelWrite:1772`，具体 UPDATE 语句未逐条确认） | 先 Feign 查 `transferApplyQueryApi.listByOriginOrderNumber`，再 `defaultTransferFacade.accountSeparateCancel` 调下游取消转移 |

## 排查提示

- 列表整页 500：先看是否 sku_type 兜底为空 / `fillNewProductInfo` 补商品时 `Long.valueOf(null)`（`B:339-358` 注释写明了这个坑）
- 列表为空但确实有单：OES 除时间外全空会直接返回空（实际默认带 30 天时间所以一般不触发）；OLS 看账号可见校区（staff）；查 `after_sale_authority_management` 是否有该售后单且 `is_del=0`（列表是 inner join）
- 字典/状态下拉为空 → Apollo `dictionary.product.enums`
- 详情页审核/取消/挽单类问题见 [aftersaledetail.md](aftersaledetail.md)

## 青舟接口详情页

- [POST /afterSale/b/afterSaleList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069147&appId=after-sales&branchName=release) id=1069147
- [POST /afterSale/b/afterSaleList/offline](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069211&appId=after-sales&branchName=release) id=1069211
- [POST /afterSale/common/dictionary](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069174&appId=after-sales&branchName=release) id=1069174
- [POST /afterSale/b/resubmitPayeeInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069202&appId=after-sales&branchName=release) id=1069202
- [POST /afterSale/b/transfer/accountSeparateCancel](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2761445&appId=after-sales&branchName=release) id=2761445
