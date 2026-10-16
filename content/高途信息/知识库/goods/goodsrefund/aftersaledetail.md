# 售后管理 / 售后详情（aftersaledetail）

## 定位

| 项 | 值 |
|---|---|
| 入口 | 售后管理列表「查看详情」（`src/pages/GoodsRefund/components/UniversalRefund/config.js:341`），也可从订单退款抽屉跳入（`src/pages/OrderManage/prodetail/Payinfo/RefundDrawer.js:408`） |
| 路由 | `/ark/app-goods/goodsrefund/aftersaledetail/:afterSaleNumber/:type/:orderItemNumber`（`config/routes.js:240-244`，wrapper `@/wrappers/ordermanage`） |
| 前端仓库 | gaotu-fe-goodsmanage（见 [_page.md](_page.md)） |
| 页面组件 | `src/pages/GoodsRefund/AfterSaleDetail/index.js`；底部 tab「审核记录 / 调课调班记录」`src/pages/GoodsRefund/components/AfterSaleBottomTab/index.jsx` |
| 后端主服务 | after-sales（`AfterSaleManagementController` `/afterSale/b`、`RetrieveManagementController` `/afterSale/b/`、`AfterSaleTransferController` `/afterSale/b/transfer/`） |

本页未抓包，接口清单来自代码。

## 接口清单

`GR/` = `src/pages/GoodsRefund/`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 controller | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面 | `POST /afterSale/b/detail` | `queryDetailInfo` | `GR/AfterSaleDetail/index.js:52`（`GR/service.js:83`） | `AfterSaleManagementController.java:148` | B端获取售后详情 [1069146] | 读 |
| 进页面 | `POST /afterSale/b/refund/detail` | `getRefundDetail` | `GR/AfterSaleDetail/index.js:53`（`GR/service.js:89`） | `AfterSaleManagementController.java:188` | 退款详情 [1069171] | 读 |
| 「取消售后」→ 确定 | `POST /afterSale/b/cancel` | `cancelAfterSale` | `GR/AfterSaleDetail/index.js:64`（`GR/service.js:19`），按钮 `GR/components/AfterSaleOrderInfo/index.js:74` | `AfterSaleManagementController.java:161` | B端取消售后 [1069215] | 写 |
| 「处理审核（挽单）」→ 提交 | `POST /afterSale/b/retrieveOrder` | `retrieveOrder` | `GR/components/saveOrder/index.js:60`（`GR/components/saveOrder/service.js:3`），按钮 `AfterSaleOrderInfo/index.js:90` | `RetrieveManagementController.java:57` | B端-处理挽单 [1069162] | 写 |
| 审核记录「更换处理人」→ 输入邮箱前缀 | `POST /afterSale/b/searchEmployee` | `getProcessor` | `GR/components/AfterSaleRecord/components/ChangeProcessor.js:120`（`GR/service.js:35`） | `AfterSaleManagementController.java:154` | 按邮箱前缀匹配员工 [1069204] | 读 |
| 「更换处理人」→ 确定 | `POST /afterSale/b/changeProcessor` | `changeProcessor` | `ChangeProcessor.js:86`（`GR/service.js:27`） | `RetrieveManagementController.java:40` | B端-更换处理人 [1069218] | 写 |
| 切到「调课调班记录」tab | `POST /afterSale/b/transfer/getAfterSaleTransferRecordsLink` | `getAfterSaleTransferRecordsLink` | `GR/components/TransferRecord/index.jsx:53`（`src/services/afterSale.js:20`），body `{orderNumber}` | `AfterSaleTransferController.java:97` | 调课调班链路 [1069181] | 读 |
| 实物「查看退货单」 | `POST /express-management/refundInfoToBoss` 等 | 同 [_page.md](_page.md) | `GR/components/ReturnOrder.js:66` | express-management（未追） | — | 读 |

### 入参

- `POST /afterSale/b/detail`（`AfterSaleManagementController#detail`，DTO `AfterSaleDetailRequest`，`AfterSaleManagementController.java:148`）：
  - `orderItemNumber` (Long, 必填 `@NotNull`) — 订单项编号
  - `afterSaleNumber` (Long, 可选) — 售后单编号（申请售后后必传）
  - `refundNumber` (Long, 可选) — 退款申请 number（兼容历史退款数据）
  - 前端传 `{afterSaleNumber, orderItemNumber}`（`GR/AfterSaleDetail/index.js:52`）
- `POST /afterSale/b/refund/detail`（`AfterSaleManagementController#getRefundDetail`，DTO `AfterSaleDetailRequest` 同上，`AfterSaleManagementController.java:188`）：
  - 字段同 `detail`，实际只用 `orderItemNumber` 与 `afterSaleNumber`
- `POST /afterSale/b/cancel`（`AfterSaleManagementController#cancel`，DTO `AfterSaleNumberRequest`，`AfterSaleManagementController.java:161`）：
  - `afterSaleNumber` (Long, 必填 `@NotNull`) — 售后单编号
- `POST /afterSale/b/retrieveOrder`（`RetrieveManagementController#retrieveOrder`，DTO `RetrieveOrderRequest`，`RetrieveManagementController.java:57`）：
  - `afterSaleNumber` (Long, 必填) — 售后单号
  - `retrieveOrderSucess` (Boolean, 必填) — 挽单结果，不能为空
  - `remark` (String, 条件必填) — 备注；挽单成功且未填 `retrieveReasonDesc` 时必填，长度 15-200
  - `needChangePrice` (Boolean, 可选) — 是否改价，默认 false
  - `targetPrice` (String, 条件必填) — 改价后金额；`needChangePrice=true` 时必填且为数字
  - `retainEndInx` (Long, 可选) — 权益范围，> -1
  - `reason` (String, 条件必填) — 改价原因；`needChangePrice=true` 时必填，≤500 字
  - `retrieveReasonCode` (String, 可选) — 挽单原因编码
  - `retrieveReasonDesc` (String, 可选) — 挽单原因描述
  - 前端另传 `orderItemNumber`（DTO 无此字段，被忽略）（`GR/components/saveOrder/index.js:52-59`）
- `POST /afterSale/b/searchEmployee`（`AfterSaleManagementController#searchEmployee`，DTO `SearchEmployeeRequest`，`AfterSaleManagementController.java:154`）：
  - `key` (String, 可选) — 邮箱前缀
- `POST /afterSale/b/changeProcessor`（`RetrieveManagementController#changeProcessor`，DTO `ChangeProcessorRequest`，`RetrieveManagementController.java:40`）：
  - `afterSaleNumber` (Long, 必填) — 售后单号
  - `identityCode` (Integer, 必填) — 挽单人身份编码（须为一级/二级/三级挽单人枚举）
  - `accountId` (Long, 必填) — 目标挽单人账户 id
  - 前端传 `{afterSaleNumber, identityCode, accountId}`（`ChangeProcessor.js:81-85`）
- `POST /afterSale/b/transfer/getAfterSaleTransferRecordsLink`（`AfterSaleTransferController#getAfterSaleTransferRecordsLink`，DTO `AfterSaleTransferRecordChainRequest`，`AfterSaleTransferController.java:97`）：
  - `orderNumber` (Long, 可选) — 订单 number
  - 前端传 `{orderNumber: orderItemNumber}`（`GR/components/TransferRecord/index.jsx:53`）
- `POST /express-management/refundInfoToBoss`（express-management 仓库本地未克隆，**后端 DTO 未定位**；前端入参：`{afterSaleNumber}`，`GR/components/ReturnOrder.js:66-68`）：
  - `afterSaleNumber` — 售后单编号

## 关键表（`after_sale` 库）

| 接口 | 服务方法 | 读表 | 写表（操作） | 其它 |
|---|---|---|---|---|
| detail | `AfterSaleForBServiceImpl#detail:732` → `UniversalProductPackager#packageDetailResponse:130` | 按 skuType 走不同 packager 配置，读 `after_sale` 及子表（未逐表确认） | 无 | Feign 订单/商品 |
| refund/detail | `AfterSaleForBServiceImpl#getAfterSaleRefundDetailList:1796` | 无本地表 | 无 | 只对 1v1（skuType 6003）且班级 `operationMode=LOCAL_LINE` 返回；退款项来自 order 服务 `refundItemQueryApiFeignClient.listByAfterSaleNumbers` |
| cancel | `AfterSaleForCServiceImpl#cancel:414`（Redis 锁 `CANCEL_AFTER_SALE_REDIS_LOCK`） | `after_sale`、`after_sale_item`、`retrieve_apply`、`retrieve_apply_his` | `retrieve_apply` UPDATE 为 TERMINATED（:576）；任务系统流程时 `retrieve_apply_his` UPDATE CANCELLED（:502）；`after_sale` UPDATE（:587）；`after_sale_process_log` 批量 INSERT（:588） | 售后单不存在且 `oldCancel` 开 → 走 order `cancelRefund`；改价/超额审批中撤回百川审批；Flowable `triggerUserTask` 推进流程 |
| retrieveOrder | `RetrieveServiceImpl#retrieveOrder:290`（三级部门走 `RetrieveServiceThreeLevelImpl#retrieveOrder:312`，选择器 `RetrieveServiceSelector`）；Redis 锁 `RETRIEVE_AFTER_SALE_REDIS_LOCK` | `after_sale`、`retrieve_apply` | `after_sale_process_log` INSERT/批量 INSERT；`retrieve_apply` UPDATE 状态（`updateStateByNumber`）；`after_sale_ext` INSERT / UPDATE end_idx；挽单成功时 `after_sale` UPDATE（`RetrieveServiceImpl.java:415-515`） | Flowable 流转（未逐行确认） |
| searchEmployee | `AfterSaleForBServiceImpl#searchEmployee:629` | 无 | 无 | cas `accountApiFacade.getSubAccounts` / `casApiFeignFacade.accountsFuzzy` + `employeeRemoteService.getEmployeeByCasUIds` |
| changeProcessor | `RetrieveServiceImpl#changeProcessor:204`（三级 `:212`） | `after_sale`、`retrieve_apply` | `retrieve_apply` UPDATE 挽单处理人（`updateRetrievePersonByIdAndStatus` / `updateThreeRetrievePersonByIdAndStatus`）；三级版另 `after_sale_process_log` 批量 INSERT | cas `accountApiFacade.getAccount` |
| getAfterSaleTransferRecordsLink | `AfterSaleTransferServiceImpl#getAfterSaleTransferRecordsLink:889` | `after_sale_transfer_record`、`after_sale` | 无 | — |

## 排查提示

- 取消售后报不可取消 → `validateCancel`：已上传退货单/已发起退款不可取消；前端按钮可用性见 `GR/config.js:29` `cancelDisabled`
- 挽单/改价卡住 → 看 `retrieve_apply.status` 与 `retrieve_apply_his`，以及 Flowable 流程实例 `after_sale.process_inst_id`
- 1v1 退款详情空 → 只有本地线下（LOCAL_LINE）1v1 才返回

## 青舟接口详情页

- [POST /afterSale/b/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069146&appId=after-sales&branchName=release) id=1069146
- [POST /afterSale/b/refund/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069171&appId=after-sales&branchName=release) id=1069171
- [POST /afterSale/b/cancel](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069215&appId=after-sales&branchName=release) id=1069215
- [POST /afterSale/b/retrieveOrder](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069162&appId=after-sales&branchName=release) id=1069162
- [POST /afterSale/b/searchEmployee](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069204&appId=after-sales&branchName=release) id=1069204
- [POST /afterSale/b/changeProcessor](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069218&appId=after-sales&branchName=release) id=1069218
- [POST /afterSale/b/transfer/getAfterSaleTransferRecordsLink](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1069181&appId=after-sales&branchName=release) id=1069181
