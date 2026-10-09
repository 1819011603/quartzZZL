# 订单可续回溯（orderRecall）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu_yunfan_fe master 代码整理。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-yunfan/orderRecall` |
| 基座 | OES ark → 子应用 app-yunfan（chunk `p__OrderRecall`） |
| 前端仓库 | gaotu_yunfan_fe `http://git.baijia.com/gaotu-ctech/gaotu_yunfan_fe`（master，本地 `~/IdeaProjects/WebProject/gaotu_yunfan_fe`） |
| 前端路由 | `config/routeConfig.js:271` → `src/pages/OrderRecall/index.js`，权限 `canOrderTraceBack`（无 clazzManage wrapper，不调 course-center 字典） |
| 后端服务 | 网关前缀 `/performance` → 青舟 appId `performance-attribution`（`CanRenewalController`） |

## tab 列表

无 tab，单页表格 +「可续回溯」弹窗。

## 页面级接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 path | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面/查询/翻页/提交后刷新 | `POST /performance/management/get/order/canRenewal` | FeituData fetch | `src/pages/OrderRecall/index.js:41` | 同左 | 订单可续回溯记录 [36985] | 读 |
| 「可续回溯」→ 选文件 | `POST /performance/management/file/upload` | antd Upload action | `src/pages/OrderRecall/components/EditModal.js:141` → `src/pages/NewJudgeConfig/components/Upload.js:71` | 同左 | 文件上传 [36986] | 写 |
| 「可续回溯」→ 确定 | `POST /performance/management/upload/back/canRenewal/byOrder` | `getSubmit` | `src/pages/OrderRecall/components/EditModal.js:69`（`src/pages/OrderRecall/services.js:4`），body `{fid, url}` | 同左 | 按订单回溯可续 [36984] | 写 |

## 关键表（`gaotu_stat` 库）

| 表 | 含义 | 涉及接口 |
|---|---|---|
| `gaotu_stat.order_can_renewal_back` | 订单可续回溯任务记录（插入 + 状态流转） | `get/order/canRenewal`、`upload/back/canRenewal/byOrder` |
| `gaotu_stat.performance_regular_can_renewal_config` | 订单可续配置；回溯时读并更新 `can_renewal_time` | `upload/back/canRenewal/byOrder` |

`file/upload` 只存文件，不落业务表。

## 排查提示

- 学员不算可续分母 / 可续锁在别的订单 → 用这里按订单回溯；排查方法见工单案例库「业绩归因」相关条目

## 青舟接口详情页

- [POST /performance/management/get/order/canRenewal](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36985&appId=performance-attribution&branchName=release) id=36985
- [POST /performance/management/upload/back/canRenewal/byOrder](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36984&appId=performance-attribution&branchName=release) id=36984
- [POST /performance/management/file/upload](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36986&appId=performance-attribution&branchName=release) id=36986
