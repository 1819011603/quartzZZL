# 班级大全（clazzEncyclopedia）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-goodsmanage master 代码整理；后端对照 course-center。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-goods/clazzEncyclopedia` |
| 基座 | OES ark → 子应用 app-goods |
| 前端仓库 | gaotu-fe-goodsmanage `http://git.baijia.com/gaotu-ctech/gaotu-fe-goodsmanage`（master，本地 `~/IdeaProjects/WebProject/gaotu-fe-goodsmanage`） |
| 前端路由 | `config/routes.js:174` → `src/pages/ClazzEncyclopedia/index.js`，wrappers `@/wrappers/clazzManage`、`@/wrappers/channelcode`（**没有** cityData，但抓包里仍有地区接口，推断来自 umi 全局 model 或缓存，未确认） |
| 组件 | `<ClazzManage isEncyclopedia/>`（`index.js:11`）→ 复用班级管理 `src/pages/ClazzManage/components/index.js`（下称 `I`） |
| 后端服务 | 网关前缀 `/course-center` → 青舟 appId `course-center`（gapm-appid `course-center-b`，`AdminClazzController`） |

## 与班级管理的差异（`isEncyclopedia=true`）

- 列表接口换成 `list/search/fullAuth`（`I:242`），后端 `authFilter=false`：**不按本人数据权限过滤**，只保留 `@DataRight`（学段/学科/品类）
- 没有顶部按钮（`I:2038`）、没有勾选（`I:2108`）
- 行内只有「销售链接」「销售二维码」（`I:1431`，后者仅 OLS），未发布时置灰；已设废行显示 `--`
- 展开辅导班表的写操作全部隐藏（`Subclazz/index.js:514,530,567,572,699`）
- 自定义列/搜索项 key 加 `_ENCY` 后缀（`src/pages/ClazzManage/config.js:341,351,513`），和班级管理是两套配置

## tab 列表

无 tab。

## 页面级接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（wrapper clazzManage） | `GET /course-center/b/common/dictionary/all`、`/department/tree`、`/category/tree`、`/dictionary/allConfigurable` | `getDictionary` 等 | `src/models/clazzManage.js:101`（`src/services/clazzManage.js:13,33,27,53`） | course-center | 共享字典 [31330]/[31497]/[31498]/[31331] | 读 |
| 进页面（wrapper channelcode） | `POST /promotionManagement/activity/getChannelCodeConfig` | `getChannelList` | `src/models/useChannelCode.js:15`（`src/services/goodsManage.js:284`） | promotionmanagement | 渠道码配置 [62088] | 读 |
| 进页面（umi 全局 model） | `GET /intranet-rpc/course-setting/feign/options/bff/list?fields=all` | `getCommonDictionary` | `src/models/useBffSelectItem.js:11`（`src/services/goodsManage.js:12`） | course-setting | bff 选项字典 | 读 |
| 进页面 | `GET /course-center/b/common/productLine/tree` | `getProductLine` | `I:187`、`src/pages/ClazzManage/SearchHead/index.js:40` | course-center | 产品线树 [31496] | 读 |
| 进页面（抓包有） | `GET https://internal-area-api.genshuixue.com/api/areas/getLevelList?levelId=1` | `getAreaList` | `src/models/useCity.js:6`（`src/services/clazzManage.js:45`） | 外部地区服务 | — | 读 |
| 搜索项「校区」挂载 | `POST /course-center/b/campus/search` | `getCampusList` | `src/components/Clazz/CampusSelect/index.js:54` → `src/models/useCampusList.js:15` | course-center | 校区搜索 [未找到] | 读 |
| 进页面/查询/翻页 | `POST /course-center/b/clazz/list/search/fullAuth` | `getFullClazzList` | `I:242`，调用 `I:319`（`src/pages/ClazzManage/services/index.js:17`） | course-center | 列表搜索-班级大全 [31448] | 读 |
| 自定义列 加载/增删改/设默认 | `POST /course-center/b/columns/*` | `getAllConfig` 等 | `I:2233-2250`（`src/services/userColumnConfig.js`） | course-center | [31193]/[31197]/[31196]/[31195]/[31194]/[31198] | 读/写 |
| 行内「销售链接」→ 生成短链 | `POST /product-b/b/product/bff/sellLink` | `getShortLink` | `I:1440` → `src/pages/GoodsManage/components/SaleUrlModal`（`src/services/goodsManage.js:47`） | product-b，未追 | — | 写（生成） |
| 「销售链接」/「销售二维码」打开（按条件） | `POST /course-setting/source/create` | `getSource` | `SaleUrlModal`（`b_client==='EES'`）、`SaleQRModal`（`src/services/goodsManage.js:60`） | course-setting，未追 | — | 写 |
| 展开行 | `POST /distribution-management/subclazz/management/listSubclazzByClazzNumber` | `getSubClazzList` | `src/pages/ClazzManage/Subclazz/index.js:65` | clazz-distribution-management | [31660] | 读 |
| 展开行「学员列表」 | `POST /course-center/b/clazzHour/userListCheck` | `userListCheck` | `Subclazz/index.js:135` | course-center | [31561] | 读 |

### 入参

> 以 course-center / product-server / clazz-distribution-management 源码为准（2026-10-16 定位）。`Pager`（`entity/common/Pager.java:29-37`）= `pageSize`/`current`/`total`（Integer, 可选）。

- `GET /b/common/dictionary/all`、`/department/tree`、`/category/tree`、`/dictionary/allConfigurable`、`/productLine/tree`：GET，无请求体。
- `POST /promotionManagement/activity/getChannelCodeConfig`：**无请求体**（见 [班级管理页入参](../clazzManagePro/_page.md#入参)）。
- `GET /intranet-rpc/course-setting/feign/options/bff/list`（`com.gaotu.feign.OptionsService#getOptionsForNode`，`OptionsService.java:48`）：GET，`@RequestParam` `fields` (String, 可选，默认 `all`)；前端传 query `fields=all`。
- `GET https://internal-area-api.genshuixue.com/api/areas/getLevelList`：GET，query `levelId=1`（外部地区服务）。
- `POST /b/campus/search`（`CampusManagementController#search`，DTO `CampusSearchRequest`）：`campusName`(String)、`campusStatus`(Integer)、`pager`(Pager, 必填 `@NotNull`)。
- `POST /b/clazz/list/search/fullAuth`（`AdminClazzController#listWithoutAuthFilter:168`，DTO `ClazzListQueryRequest`）：字段与 [班级列表 `clazz/list/search`](../clazzManagePro/clazzList.md#入参) **完全一致**（同一个 DTO，只差 `authFilter=false`）。
- `POST /b/columns/*`：DTO 与 [课程管理页入参](../CourseManagePro/_page.md#入参) 一致（`PageConfigGetRequest` / `UserConfigListRequest` / `UserConfigAddRequest` / `UserConfigDeleteRequest` / `UserConfigModifyRequest` / `UserConfigSelectRequest`）。
- `POST /product-b/b/product/bff/sellLink`（product-server `ProductUtilController#sellLink:34`，DTO `com.gaotu.clientv4.request.ClazzSellUrlDto`）：`clazzUrl` (String, 可选) — 原始班级链接（须以 `http:`/`https:` 开头，否则 `parameterValidator()` 失败）。前端 `goodsManage.js:48` 传 `{clazzUrl: params.url}`，一致。
- `POST /course-setting/source/create`（`SourceContoller#create:27`，DTO `com.gaotu.model.request.source.CreateSourceRequest`，`CreateSourceRequest.java:14`）：`customerWayType`(Integer, 必填) — 获客方式、`name`(String, 必填) — 活动创建人邮箱前缀、`promoterId`(String, 必填) — 推广人员 id、`promoterName`(String, 必填)、`putPlanId`(String, 必填) — 活动 id、`putPlanName`(String, 必填) — 活动名称。
- `POST /distribution-management/subclazz/management/listSubclazzByClazzNumber`（distribution `SubclazzController#listSubclazzByClazzNumber:492`，DTO `ClazzNumberRequest`）：`clazzNumber` (Long, 必填 `@NotNull`)。
- `POST /b/clazzHour/userListCheck`（`AdminClazzHourController#userListCheck:54`，DTO `ClazzHourSubClazzCheckRequest`）：`subclazzNumber` (Long, 必填 `@NotNull`)。

## 关键表（`course_center` 库，test 集群 gaotu-course-test，cluster_id=153）

| 接口 | 后端 | 读 | 写 | ES / 其它 |
|---|---|---|---|---|
| clazz/list/search/fullAuth | `course-center-webcourse/.../controller/manager/clazz/AdminClazzController.java:165`（`@DataRight`，`fillSystemParamForListSearchRequest(request,true,...)`）→ `ClazzQueryServiceImpl#listQuery:363`（`authFilter=false`） | **ES 索引 `clazz_search`**（`ClazzEsDao.java:69`）；`clazz.query.es.switch=true` 时按命中 clazzNumber 回查 `course_center.clazz`；ES 异常或 `clazz.list.query.degradation=true` 走 DB | 无 | 与班级管理同一个 service，只差 `authFilter` 和系统参数 |
| columns/* | `UserCustomPageColumnsController.java:27` | `page_columns_config`、`user_custom_page_columns_config` | `user_custom_page_columns_config` | key 带 `_ENCY` |
| campus/search | `CampusManagementController.java:93` | `campus_info` | 无 | — |

## 排查提示

- 「班级管理里看不到、班级大全里能看到」→ 正常，大全不走本人数据权限（`authFilter=false`）
- 大全里查不到 → 同样先怀疑 ES `clazz_search`；学段/学科/品类权限（`@DataRight`）仍生效
- 班级大全的自定义列和班级管理不共享（key 后缀 `_ENCY`）

## 青舟接口详情页

- [POST /b/clazz/list/search/fullAuth](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31448&appId=course-center&branchName=release) id=31448
- [POST /promotionManagement/activity/getChannelCodeConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=62088&appId=promotionmanagement.gaotu100.com&branchName=release) id=62088
- [POST /b/columns/getAllConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31193&appId=course-center&branchName=release) id=31193
- [POST /b/columns/getUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31197&appId=course-center&branchName=release) id=31197
- [GET /b/common/productLine/tree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31496&appId=course-center&branchName=release) id=31496
- [POST /b/clazzHour/userListCheck](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31561&appId=course-center&branchName=release) id=31561
- [POST /subclazz/management/listSubclazzByClazzNumber](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31660&appId=clazz-distribution-management.gaotu100.com&branchName=release) id=31660
