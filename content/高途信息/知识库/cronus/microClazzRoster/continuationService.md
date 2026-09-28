# 小班课花名册 / 续班服务（microClazzRoster · tabKey=continuationService）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/microClazzRoster?tabKey=continuationService` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/microClazzRoster/index.jsx` |
| tab 组件 | `src/pages/microClazzRoster/ContinuationService/` |
| 主 service 文件 | `src/pages/microClazzRoster/ContinuationService/service.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级说明见 [_page.md](./_page.md)；花名册 tab 见 [default.md](./default.md)。

## 接口清单

### 1. 列表数据（进页面 + 筛选 / 翻页 / 排序）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/筛选/翻页 | `getContinuationServiceList` | `/bgwApi/component/student-center/roster/small/renewal/page` | `src/pages/microClazzRoster/ContinuationService/service.js:31` | student-center | `/roster/small/renewal/page` | 分页查询续班服务列表 [3151317] | **主列表数据** |
| 总数超上限 | `getListCount` | `/bgwApi/component/student-center/roster/small/renewal/count` | `src/pages/microClazzRoster/ContinuationService/service.js:39` | student-center | `/roster/small/renewal/count` | 获取总数，当超过index配置最大count时使用 [3151318] | total 触达上限时单独取真实值 |
| 默认视图列表 | `getContinuationServiceDefault` | `/bgwApi/component/student-center/roster/small/renewal/default/page` | `src/pages/microClazzRoster/ContinuationService/service.js:13` | student-center | `/roster/small/renewal/default/page` | 分页查询续班服务列表 [3151315] | 初始化默认数据 |
| 默认视图总数 | `getListCountDefault` | `/bgwApi/component/student-center/roster/small/renewal/default/count` | `src/pages/microClazzRoster/ContinuationService/service.js:47` | student-center | `/roster/small/renewal/default/count` | 获取总数，当超过index配置最大count时使用 [3151316] | 默认视图总数 |

### 2. 全局搜索 / 筛选

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | `getDefaultValue` | `/bgwApi/component/student-center/roster/small/renewal/defaultValue` | `src/pages/microClazzRoster/ContinuationService/service.js:22` | student-center | `/roster/small/renewal/defaultValue` | 获取GlobalSearch默认值接口 [3151314] | 全局搜索默认值（`useDefaultValue`） |
| 班级变更/进页面 | `getContinuationRound` | `/bgwApi/component/student-center/roster/small/renewal/getRenewalInfo` | `src/pages/microClazzRoster/ContinuationService/service.js:5` | student-center | `/roster/small/renewal/getRenewalInfo` | 续班信息 [3151313] | 续班轮次选项 |
| 进页面 | `getRenewalPlanList` | `/component/student-center/smallClazz/filter/renewalPlan/list` | `src/pages/microClazzRoster/ContinuationService/service.js:55` | student-center | `/smallClazz/filter/renewalPlan/list` | [POST]/renewalPlan/list [3876404] | 续班计划下拉（不依赖班级） |
| 续班计划变更 | `getClazzList` | `/component/student-center/smallClazz/filter/clazz/list` | `src/pages/microClazzRoster/ContinuationService/service.js:79` | student-center | `/smallClazz/filter/clazz/list` | [POST]/clazz/list [2044937] | 班级列表；`GlobalSearch` 的 `ClazzAndPeriodNg`（内联 `api.clazz`，`components/GlobalSearch/index.js:413`）调同一 path |

### 3. 续班数据指标 / 问卷明细

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 搜索后刷新指标 | `getMicroContinuationIndicator` | `/bgwApi/component/student-center/roster/small/renewal/statistic` | `src/pages/microClazzRoster/ContinuationService/service.js:87` | student-center | `/roster/small/renewal/statistic` | 续班统计数据（可续学员数、问卷提交率、问卷预报名/考虑/不预报率、订金预报名/未报名率） [3876403] | 顶部指标卡 |
| 默认指标 | `getMicroContinuationIndicatorDefault` | `/bgwApi/component/student-center/roster/small/renewal/default/statistic` | `src/pages/microClazzRoster/ContinuationService/service.js:117` | student-center | `/roster/small/renewal/default/statistic` | 续班统计数据（可续学员数、问卷提交率、问卷预报名/考虑/不预报率、订金预报名/未报名率） [3876402] | 初始化默认指标 |
| 点「问卷明细」 | `getQuestionInfo` | `/bgwApi/component/student-center/roster/renewal/sendQuestion/getQuestionInfo` | `src/pages/microClazzRoster/ContinuationService/service.js:147` | student-center | `/roster/renewal/sendQuestion/getQuestionInfo` | 问卷信息获取 [3381630] | 校验班级绑定的问卷 |
| 问卷明细搜学员 | `getSmallClazzStudentConstants` | `/bgwApi/component/student-center/roster/small/renewal/questionnaire/search/user` | `src/services/bindingStudents.ts:61` | student-center | `/roster/small/renewal/questionnaire/search/user` | 搜索用户 [3876405] | `QuestionnaireDetail` 绑定学员搜索 |

### 4. 编辑 / 下单 / 其他

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 行内编辑保存 | `updateStudentInfo` | `/component/student-center/studentClazz/edit` | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js:13`（`ContinuationService/index.js:17` 引用） | student-center | `/studentClazz/edit` | [POST]/edit [30662] | 保存单元格修改（场景 `microContinuationService`） |
| 批量改颜色/分层 | `batchEditStudentInfo` | `/component/student-center/studentClazz/batchEdit` | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js:54`（经 `hooks/useExtendComponents.js:6` 注册 `BatchColorEdit`） | student-center | `/studentClazz/batchEdit` | [POST]/batchEdit [2863102] | 底部「添加颜色/分层」 |
| 下单（非灰度） | `recommendClazzList` | `/bgwApi/product-b/b/renewMaster/recommendClazzList` | `src/services/continuationService.js:108`（`components/CreateOrder/index.jsx:7` 引用） | product-b | `/b/renewMaster/recommendClazzList` | 查询推荐班级列表 [2734275] | 创建订单推荐班级 |
| 下单灰度判断 | `getGrayService` | `/product-b/b/renewMaster/configFlag` | `src/pages/microClazzRoster/ContinuationService/components/CreateOrder/gray.js:7` | product-b | `/b/renewMaster/configFlag` | 获取配置开关 [2734336] | 决定走新下单 widget 还是推荐班级 |

### 5. 表格 schema

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | `getMetaData` → `getSchema`（`@coeus/render`） | coeus 低代码 schema | `src/models/microContinuationService.js:18` | coeus/render | — | — | 拉表格列 / 筛选 schema（`identification=microContinuationService`） |

> 共享组件（`ReachReportFilter`→`ReachReport`/`ReachReportNew`、`PersonalLink`→`CustomSaleLink`、`ReachBusiness`、`QuestionnaireDetail` 等）另有接口，被多页面复用，待单独归档。

## 青舟接口详情页

- [POST /roster/small/renewal/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151317&appId=student-center&branchName=release)
- [POST /roster/small/renewal/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151318&appId=student-center&branchName=release)
- [POST /roster/small/renewal/default/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151315&appId=student-center&branchName=release)
- [POST /roster/small/renewal/defaultValue](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151314&appId=student-center&branchName=release)
- [POST /roster/small/renewal/getRenewalInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151313&appId=student-center&branchName=release)
- [POST /roster/small/renewal/statistic](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3876403&appId=student-center&branchName=release)
- [POST /smallClazz/filter/renewalPlan/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3876404&appId=student-center&branchName=release)
- [POST /roster/renewal/sendQuestion/getQuestionInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3381630&appId=student-center&branchName=release)
- [POST /studentClazz/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30662&appId=student-center&branchName=release)
- [POST /b/renewMaster/recommendClazzList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734275&appId=product-b&branchName=release)
- [GET /b/renewMaster/configFlag](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734336&appId=product-b&branchName=release)
