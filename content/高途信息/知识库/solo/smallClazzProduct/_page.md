# 小班课商品大全（smallClazzProduct/overview）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-solo master 代码整理；后端对照 course-center。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-solo/smallClazzProduct/overview` |
| 基座 | OES ark → 子应用 app-solo（chunk `p__SmallClazzProduct__list__overview`） |
| 前端仓库 | gaotu-fe-solo `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/gaotu-fe-solo`（master，本地 `~/IdeaProjects/WebProject/gaotu-fe-solo`；青舟 serviceCode `baijia.gt.ecommerce.fe.gaotu-fe-solo`） |
| 前端路由 | `config/routes.js:56-60` → `src/pages/SmallClazzProduct/list/overview/index.tsx`，无 wrapper；`?hideLayout=true` 时全屏嵌入（商品大全 iframe 用） |
| 兄弟路由 | `routes.js:51-72` 的「小班课商品管理」`/smallClazzProduct/list`、「创建商品」`/create/:type`、「编辑商品」`/:handleType/:type` **全被注释**，当前只有 overview 一个页面在用。`list/manage`、`create`、`edit` 目录代码仍在但不可达 |
| 后端服务 | 前端写 `/bgwApi/course-center/b/...`，`src/app.js:46-61` 拦截器把 `/bgwApi` 之后的部分拼到基座 `ApiRoot`；网关按 `/course-center` 前缀路由到青舟 appId `course-center`（gapm-appid `course-center-b`），后端 controller 路径是 `/b/...`（在 `course-center-webcourse` 模块） |

## tab 列表

无 tab。单页：查询表单 + 表格（`BaseProductList`）+「自定义列」+ 行操作「复制销售链接」弹窗。

## 页面级接口

`list/` = `src/pages/SmallClazzProduct/list/`；`SaleUrlModal/` = `src/components/SaleUrlModal/`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 子应用启动（全局 model，任何页面都会发） | `GET /bgwApi/course-center/b/config/getDynamicConfig` | `getDynamicConfig` | `src/models/dynamicConfig.ts:29,44`（`src/services/dynamicConfig.ts:24`） | course-center | 动态配置 [2652064] | 读 |
| 进页面（字典为空时） | `GET /bgwApi/course-center/b/common/dictionary/all` | `getDictionary` | `list/component/BaseProductList.tsx:45-48` → `src/models/clazzManage.js:73`（`src/services/clazzManage.js:4`） | course-center | 共享字典 [31330] | 读 |
| 同上 | `GET /bgwApi/course-center/b/common/department/tree` | `getNewDepartment` | 同上（`src/services/clazzManage.js:17`） | course-center | 共享字典·部门树 [31497] | 读 |
| 同上 | `GET /bgwApi/course-center/b/common/category/tree` | `getNewTree` | 同上（`src/services/clazzManage.js:11`） | course-center | 共享字典·品类树 [31498] | 读 |
| 同上 | `GET /bgwApi/course-center/b/common/dictionary/allConfigurable` | `getDefaultCourseConfig` | 同上（`src/services/clazzManage.js:23`） | course-center | 共享字典·可配置项 [31331] | 读 |
| 进页面（「商品规格」筛选项渲染） | `GET /bgwApi/course-center/b/productAttr/list/specification` | `getSpecificationOptions` | `src/components/SearchComponents/SpecificationSearch/index.tsx:36` → `hooks.ts:17`（`src/services/smallClazzProduct.ts:30`） | course-center | 获取商品规格列表 [1867605] | 读 |
| 进页面（表格自定义列） | `POST /course-center/b/columns/getAllConfig` | `getAllConfig` | `list/overview/index.tsx:31` → `src/hooks/useEditColumnsProps.js:38`（`src/services/userColumnConfig.ts:97`），`key=18750529034377751` | course-center | 页面全量列配置 [31193] | 读 |
| 同上 | `POST /course-center/b/columns/getUserConfig` | `getUserConfig` | `src/hooks/useEditColumnsProps.js:39`（`src/services/userColumnConfig.ts:104`） | course-center | 用户列配置 [31197] | 读 |
| 进页面/查询/翻页 | `POST /bgwApi/course-center/b/teach/commodity/clazz/list` body `{pager, ...筛选}` | FeituData `fetch` | `list/overview/index.tsx:63` → `list/component/BaseProductList.tsx:63-71` | course-center | 班级大全列表 [1611515] | 读 |
| 自定义列「新增方案」 | `POST /course-center/b/columns/addUserConfig` | `addUserConfig` | `src/hooks/useEditColumnsProps.js:44`（`src/services/userColumnConfig.ts:111`） | course-center | 新增用户列配置 [31196] | 写 |
| 自定义列「删除方案」 | `POST /course-center/b/columns/deleteUserConfig` | `delUserConfig` | `src/hooks/useEditColumnsProps.js:40`（`src/services/userColumnConfig.ts:118`） | course-center | 删除用户列配置 [31195] | 写 |
| 自定义列「保存修改」 | `POST /course-center/b/columns/setUserConfig` | `updateUserConfig` | `src/hooks/useEditColumnsProps.js:48`（`src/services/userColumnConfig.ts:125`） | course-center | 修改用户列配置 [31194] | 写 |
| 自定义列「设为默认」 | `POST /course-center/b/columns/changeDefaultUserConfig` | `changeDefaultConfig` | `src/hooks/useEditColumnsProps.js:49`（`src/services/userColumnConfig.ts:132`），body `{pageConfigKey, userConfigNumber}` | course-center | 切换默认列配置 [31198] | 写 |
| 行「复制销售链接」打开弹窗（仅已发布商品可点） | `POST /promotionManagement/activity/getChannelCodeConfig` | `getChannelList` | `SaleUrlModal/useSaleUrlModal.ts:65-68` → `src/models/useChannelCode.ts:35`（`src/services/common.ts:3`） | promotionmanagement.gaotu100.com | 渠道码配置 [62088] | 读 |
| 弹窗内生成/复制链接 | `POST /product-b/b/product/sellLinkWithSource` body `{sellUrl, channelCode, sourceDto, type}` | `generateLink` | `SaleUrlModal/useSaleUrlModal.ts:106,186`（`SaleUrlModal/service.ts:41`） | product-b（未确认落到哪个后端，青舟另有 `product.gaotu100.com` 同名接口 1578579） | 生成带来源销售链接 [2734150] | 读（生成短链，是否落库未确认） |

> 弹窗里的原始链接 `urlList` 不另调接口，直接取列表行 `teachCommodityDto.urlList`（`list/component/useSaleUrlModal.tsx:55`），由 `clazz/list` 后端拼好。
> `list/service.ts` 里的发布/撤销/开停售（`/b/teach/commodity/update/status`）、删除（`/b/teach/commodity/delete`）只被 `list/manage` 用，overview 传了 `useOperations:false`，**本页没有商品写操作**。
> 自定义列的 columns 接口不带 `/bgwApi`，抓包里也是 `/course-center/b/columns/*`，经拦截器同样拼 `ApiRoot`。

## 关键表

链路（列表）：`TeachCommodityController#listClazz`（`course-center-webcourse/.../controller/manager/teachcommodity/TeachCommodityController.java:142`，类 `@RequestMapping("/b/teach")` :42）→ `TeachCommodityQueryServiceImpl#listQuery`（`course-center-domain/.../service/teachcommodity/impl/TeachCommodityQueryServiceImpl.java:191`）：

1. **先查 ES** 拿商品编号分页：`WideTeachCommodityRepository#findByCondition` → `WideTeachCommodityDao`（`course-center-domain/.../teachcommodity/wide/WideTeachCommodityDao.java:34`），索引名 Apollo `wide.teachCommodity.es.indexName`（appId `course-center-webcourse`，namespace `gt.course-center-public`）：**test=`teach_product_search_test_v1`，prod=`teach_product_search_prod`**。筛选条件全部走 ES（模糊词、开课时间、商品名/ID、品类、教学产品名/ID、班型、部门、规格）。分页总数也来自 ES。
2. 再按编号回 MySQL 补详情（`covertToTeachCommodityListResponseList` :426），并调多个下游 Feign。

### 接口 → 表

| 接口 | 后端入口 | 读 | 写 | 备注 |
|---|---|---|---|---|
| `teach/commodity/clazz/list` | `TeachCommodityController.java:142` → `TeachCommodityQueryServiceImpl#listQuery:191` | ES `teach_product_search_*`；`course_center.teach_commodity_detail`（`TeachCommodityDetailDao#listItemData:35`，`isdel=0`）；`course_center.teach_commodity_info`（逐条 `selectTeachCommodityInfoByNumber`，取发布/售卖状态）；`course_center.lesson_right_detail`、`course_center.handout_right_detail`（按 rightPackageNumber=商品编号）；`course_center.teach_lesson`；`course_center.clazz`（`ClazzReadRepositoryImpl#getByNumber:49`，用商品编号当班级编号查） | 无 | Feign：course-setting `getSkuAppV2`/`getSkuAppInfo`（上架/课显/订单/行课 APP，`CourseSettingRemoteServiceImpl.java:209,233`）、cart 库存 `StockServiceImpl#getCartInfo:49`、CES 教学产品 `TeachProductServiceImpl#pageTeachProduct:211`（**查不到教学产品的商品被直接过滤掉**，:465-471）、`IWhileListService#listWhiteByNumber`（督学白名单，jar `com.gaotu.clientv4.feign`，服务名未确认） |
| `productAttr/list/specification` | `AdminProductAttrController.java:52`（类 `/b/productAttr/` :27）→ `SettingProductAttrPoolServiceImpl#getSpecificationNames:25` → `SettingProductAttrPoolDao:246` | `course_center.product_attr_pool`（attr_type=商品规格、product_type=小班课、attr_status=ON、isdel=0） | 无 | 返回 attrName 去重 |
| `config/getDynamicConfig` | `ConfigController.java:53`（类 `/b/config/` :33） | 无表：Apollo `common.dynamic.confg`（缺省 `clazzOpenCount=50,teachProductCount=10,enableArrangeByNode=0`）+ Apollo `gps.arrange1v1.dept.config`（`GpsArrange1v1DeptConfigService#resolve:38`） | 无 | 本页不用其结果，是全局 model 顺带发的 |
| `columns/getAllConfig` | `UserCustomPageColumnsController.java:35`（类 `/b/columns/` :27）→ `PageColumnsConfigApplication#getByQuery:26` | `course_center.page_columns_config`（按主键 number=`18750529034377751`） | 无 | |
| `columns/getUserConfig` | `UserCustomPageColumnsController.java:61` → `UserCustomPageColumnsConfigApplication#query:53` | `page_columns_config`、`course_center.user_custom_page_columns_config`（employeeId + pageNumber） | 无 | 默认方案是代码拼的，不在表里 |
| `columns/addUserConfig` | `UserCustomPageColumnsController.java:54` → `#add:76` | 同上 | `user_custom_page_columns_config` INSERT；若新方案选中，把同页其他方案 UPDATE `selected=false` | 事务 + Redis 锁 `USER_PAGE_CONFIG+employeeId` |
| `columns/deleteUserConfig` | `UserCustomPageColumnsController.java:47` → `#delete:88` | 同上 | `user_custom_page_columns_config` UPDATE（逻辑删） | 默认方案不可删，只能删自己的 |
| `columns/setUserConfig` | `UserCustomPageColumnsController.java:40` → `#modify:99` | 同上 | `user_custom_page_columns_config` UPDATE | 事务 + Redis 锁 |
| `columns/changeDefaultUserConfig` | `UserCustomPageColumnsController.java:67` → `#select:110` | 同上 | `user_custom_page_columns_config` UPDATE 选中项 + 其余 `selected=false` | 事务 + Redis 锁 |
| `/b/common/*` 四个 | — | 共享字典 | — | 不展开 |

### 表

| 表 | 库 | 含义 |
|---|---|---|
| `teach_commodity_detail` | course_center | 教学商品（小班课 SKU）详情：number、teach_commodity_sale_json（含规格、主讲）、isdel |
| `teach_commodity_info` | course_center | 教学商品售卖信息：publish_status、sale_status、sale_type、end_sale_time、teach_product_number、clazz_type_number |
| `lesson_right_detail` / `handout_right_detail` | course_center | 商品权益包的课次权益 / 讲义权益（right_package_number = 商品编号） |
| `teach_lesson` | course_center | 教学课次 |
| `clazz` | course_center | 班级（bizNumber 即销售链接里的投放计划 ID） |
| `product_attr_pool` | course_center | 商品参数池（规格名下拉） |
| `page_columns_config` / `user_custom_page_columns_config` | course_center | 页面列配置 / 用户自定义列方案 |
| ES `teach_product_search_test_v1` / `teach_product_search_prod` | course-center `restHighLevelClient` | 教学商品宽表，列表检索与分页的唯一来源 |

注意：
- 库名取自 test 数据源 `jdbc.coursecenter.url`（`course_center`）和 mapper 包 `repository/coursecenter/auto`，没逐表核对线上分库。
- `WideTeachCommodityDao` 有降级开关 `wide.teachCommodity.es.search.demotion.switch`（缺省 2，Apollo 未配），降级行为在 jar `gaotu-blocks-es` 里，未确认。

## 排查提示

- 列表里搜不到某商品 / 总数不对 → 先查 ES `teach_product_search_*`（筛选全走 ES），再看 `teach_commodity_detail.isdel`；ES 有但 CES 教学产品查不到的会被静默过滤（日志 `查询教学产品信息失败`）
- 上架/课显/订单/行课 APP 列为空 → course-setting `getSkuAppV2`/`getSkuAppInfo`（有开关 `clazzSearchAppSkipSwitch` 会直接返回空）
- 「复制销售链接」灰掉 → `teachCommodityDto.publishStatus` 不是已发布；链接为空 → `clazz/list` 里 `dealAppUrlList` 拼 URL 失败（班级查不到时 catch 后只打 warn）
- 渠道下拉只有「全部/其他」→ `getChannelCodeConfig` 失败或返回非 0

## 青舟接口详情页

- [POST /b/teach/commodity/clazz/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1611515&appId=course-center&branchName=release) id=1611515
- [GET /b/productAttr/list/specification](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1867605&appId=course-center&branchName=release) id=1867605
- [GET /b/config/getDynamicConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2652064&appId=course-center&branchName=release) id=2652064
- [POST /b/columns/getAllConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31193&appId=course-center&branchName=release) id=31193
- [POST /b/columns/getUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31197&appId=course-center&branchName=release) id=31197
- [POST /b/columns/addUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31196&appId=course-center&branchName=release) id=31196
- [POST /b/columns/deleteUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31195&appId=course-center&branchName=release) id=31195
- [POST /b/columns/setUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31194&appId=course-center&branchName=release) id=31194
- [POST /b/columns/changeDefaultUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31198&appId=course-center&branchName=release) id=31198
- [POST /promotionManagement/activity/getChannelCodeConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=62088&appId=promotionmanagement.gaotu100.com&branchName=release) id=62088
- [POST product-b/b/product/sellLinkWithSource](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734150&appId=product-b&branchName=release) id=2734150
- 共享字典：[dictionary/all](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31330&appId=course-center&branchName=release) 31330 · [department/tree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31497&appId=course-center&branchName=release) 31497 · [category/tree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31498&appId=course-center&branchName=release) 31498 · [dictionary/allConfigurable](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31331&appId=course-center&branchName=release) 31331
