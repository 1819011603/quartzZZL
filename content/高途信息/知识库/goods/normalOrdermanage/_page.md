# 课程类订单（normalOrdermanage）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-goodsmanage master 代码整理；后端对照 order（order-b）、gaotu-ols、product-server。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-goods/normalOrdermanage/list` |
| 基座 | OES ark → 子应用 app-goods |
| 前端仓库 | gaotu-fe-goodsmanage `http://git.baijia.com/gaotu-ctech/gaotu-fe-goodsmanage`（master，本地 `~/IdeaProjects/WebProject/gaotu-fe-goodsmanage`；青舟 serviceCode `baijia.gaotu.Business.fe.gaotu-fe-goods`） |
| 前端路由 | `config/routes.js:300-311` → `src/pages/OrderManage/list/index.js`，wrappers `olscampus` / `allOlsCampus` / `commondictory` / `clazzManage`，**路由上没配 access**（tab 级用 hasTag 控制） |
| 同组件复用 | 非课程类订单 `/ordermanage/list`、付款记录 `/payRecord/list` 也用这个组件，`list/index.js:62-83` 按路由正则区分 block；本页 = `CLAZZ_BLOCK` |
| 后端主服务 | 前端直接请求 `/orderComponent/*`（无前缀）→ gapm-appid `order-b-gaotu100-com` → 青舟 appId `order-b.gaotu100.com`（仓库 **order**，`OrderComponentController`） |

## tab 列表

tab 配置在 `src/pages/OrderManage/hooks/useOrderJson.js:370-388`（OES `ORDER_LIST.SHOWTAB[CLAZZ_BLOCK]`），每个 tab 按权限标签决定是否显示：

| tab | 文件 | orderType | 权限标签 | 列表接口 |
|---|---|---|---|---|
| 课程订单 | [normal.md](normal.md) | `normal` | `gaotu_boss_p_order_` / `gaotu_fairy_p_order_` / `gaotu_damai_order_manage` 任一 | `orderFieldSearch` |
| 一对一订单 | [soloclazz.md](soloclazz.md) | `soloclazz`（productType 6003） | `gaotu_boss_p_soloclazz_order` | `orderItemFieldSearch` |
| 课时包订单 | [lessonpackage.md](lessonpackage.md) | `lessonpackage`（7001） | `oes_menu_order_clazzHourPackage_` | `orderItemFieldSearch` |
| 小班课订单 | [miniclass.md](miniclass.md) | `miniclass`（6004） | `oes_menu_order_PrivateClazz_list_` | `orderItemFieldSearch` |

默认 tab 是 `normal`（`list/index.js:1212`）。列表组件是本地 `src/components/OrderList/`（由 feitu-business order-list 包拷贝过来），接口定义都在 `src/components/OrderList/services.ts`。

## 页面级接口（进页面即调，与 tab 无关）

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（wrapper olscampus） | `POST /ols/w/campus/list` | `getOlsCampusList` | `src/models/useOlsCampus.js:19`（`src/services/physicalOrder.js:239`），body `{campusStatus:0, pager:{pageSize:10000}}` | gaotu-ols | 校区列表 [36004] | 读 |
| 进页面（wrapper allOlsCampus） | `POST /ols/w/campus/all` | `getAllOlsCampusList` | `src/models/useOlsCampus.js:36`（`src/services/physicalOrder.js:246`） | gaotu-ols | 全部校区 [36007] | 读 |
| 进页面 | `POST /orderComponent/grayGroup/checkGrayGroup` | `useOrderCreationGuard` | `src/pages/OrderManage/list/hooks/useOrderCreationGuard.js:34`，body `{}` | order-b | 灰度组命中判断 [5304562] | 读 |
| 进页面（全局 umi model） | `GET /intranet-rpc/course-setting/feign/options/bff/list?fields=all` | `getCommonDictionary` | `src/models/useBffSelectItem.js:11`（`src/services/goodsManage.js:13`） | course-setting | 共享字典 [34362] | 读 |
| 进页面（wrapper commondictory） | `GET /course-center/b/common/dictionary/all` | `getCommonDictionary` | `src/models/useCommondictory.js:13`（`src/services/physicalOrder.js:231`） | course-center | 共享字典 | 读 |
| 进页面（wrapper commondictory） | `POST /course-setting/b/base/commonDictionary` | `getBaseCommonDictionary` | `src/models/useCommondictory.js:46`（`src/services/dictionary.js:8`） | course-setting | 共享字典 [34693] | 读 |
| 进页面（wrapper clazzManage） | `GET /course-center/b/common/dictionary/all`、`/category/tree`、`/department/tree`、`/dictionary/allConfigurable` | `doGetDictionary` | `src/models/clazzManage.js:101`（`src/services/clazzManage.js:14/28/34/53`） | course-center | 共享字典 | 读 |

各 tab 的列表/按钮/弹窗接口见 tab 文件。

### 入参

- `POST /ols/w/campus/list`（`CampusInfoController#list`，DTO `com.gaotu.ols.app.model.campusinfo.model.CampusListRequest`，`CampusInfoController.java:77`）：
  - `campusName` (String, 可选) — 校区名称（模糊）
  - `campusStatus` (Integer, 可选) — 校区状态；前端固定传 `0`
  - `pager` (Pager, **必填** `@NotNull`) — 分页参数；前端传 `{pageSize:10000}`（`src/models/useOlsCampus.js:19`）
- `POST /ols/w/campus/all`（`CampusInfoController#all`，无请求体，`CampusInfoController.java:85`）：
  - 无入参（无 `@RequestBody`；前端 `getAllOlsCampusList()` 不传参，`src/services/physicalOrder.js:245`）
- `POST /orderComponent/grayGroup/checkGrayGroup`（`GrayGroupController#checkGrayGroup`，DTO `com.gaotu.order.graygroup.request.GrayGroupCheckRequest`，`GrayGroupController.java:42`）：
  - `accountId` (Long, 可选) — 员工账号 ID；页面经网关调用可不传，服务端从 `BossFacadeThreadLocalHolder` 取（`GrayGroupController.java:47`）
  - `bClient` (String, 可选) — 客户端类型；优先取请求头 `b_client`，缺省才用 body（`GrayGroupController.java:48-49`）
  - 前端实际 body 为 `{}`（`src/pages/OrderManage/list/hooks/useOrderCreationGuard.js:34`）
- `GET /intranet-rpc/course-setting/feign/options/bff/list`：**后端 DTO 未定位**（course-setting 仓库本地不存在）；前端入参：query `{fields:'all'}`（`src/services/goodsManage.js:13`）
- `GET /course-center/b/common/dictionary/all`：无请求体（GET）——前端 `getCommonDictionary` 仅传 `data` 无 query（`src/services/physicalOrder.js:231`）
- `POST /course-setting/b/base/commonDictionary`：**后端 DTO 未定位**（course-setting 仓库本地不存在）；前端未传请求体（`src/services/dictionary.js:8`）
- `GET /course-center/b/common/dictionary/all`、`/course-center/b/common/category/tree`、`/course-center/b/common/department/tree`、`/course-center/b/common/dictionary/allConfigurable`：无请求体（GET；前端均不传参，`src/services/clazzManage.js:13-56`）

## 关键表

order-b 的三个搜索接口都是同一个套路（`order-app/.../search/service/search/AbstractSearchService.java:81` `doSearch`）：

1. **先查 ES 拿根编号**：`search.{order|orderItem|pay}.allowComplexSearch`（默认 true，test Apollo `order.gaotu100.com` 上 order 那个也是 true）为 true 时查 ES 宽表索引，只拿 number 列表 + 分页
2. ES 查不到、且带了订单号/支付号时，走 coverLogic 直接查 MySQL 兜底
3. **再按编号聚合**（Polymerize）：一批 provider 回 MySQL 和下游 Feign 补字段

| 索引（alias 配置 key） | 值 | 用于 |
|---|---|---|
| `index.order.alias` | test 配置里是 `gaotu_order_wide_order_search_rollover`（取自 `order-infrastructure/src/test/resources/application.properties:43`；test Apollo `order.gaotu100.com` 的 application / elasticsearch namespace 里都没有这个 key，**真实值未确认**） | 课程订单 `orderFieldSearch` + 价格聚合 |
| `index.orderItem.alias` | 推断是 `gaotu_order_wide_order_item_search_rollover`（代码 `order_item_new_alias` 的默认值，**未确认**） | 一对一 / 课时包 / 小班课 `orderItemFieldSearch` |

MySQL 都在 `gaotu` 库（test 环境 cluster 142 `gaotu_polar_test_03` 里查到 `order_info`、`order_info_ext`、`order_info_commodity`、`order_item`、`pay_info`、`pay_plan`、`pay_plan_item`；mapper XML 里表名不带库前缀，库名是按这个推出来的）。

## 排查提示

- 列表查不到 / 少单 → 先看 ES 宽表索引同步了没有（order-b 的 `RefreshOrderJob` 等任务）；带订单号查的时候 ES 没命中会自动走 MySQL 兜底，所以「订单号能查到、其它条件查不到」基本就是 ES 没同步
- 「创建单个订单」按钮弹拦截/引导 → `checkGrayGroup`，规则在 order Apollo `order.gray.group.rule.config`
- 课程订单 tab 默认带 `openCourseList=['2']`，所以进页面就会请求；其它 tab 上红框搜索项为空时前端直接返回空列表，不发请求

## 青舟接口详情页

- [POST /w/campus/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36004&appId=gaotu-ols&branchName=release) id=36004
- [POST /w/campus/all](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36007&appId=gaotu-ols&branchName=release) id=36007
- [POST /orderComponent/grayGroup/checkGrayGroup](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5304562&appId=order-b.gaotu100.com&branchName=release) id=5304562
- [GET /feign/options/bff/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=34362&appId=course-setting.gaotu100.com&branchName=release) id=34362
- [POST /b/base/commonDictionary](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=34693&appId=course-setting.gaotu100.com&branchName=release) id=34693
