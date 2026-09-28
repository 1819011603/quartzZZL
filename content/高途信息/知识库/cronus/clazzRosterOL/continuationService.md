# 班级花名册 / 续班服务（clazzRosterOL · tabKey=continuationService）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/clazzRosterOL?tabKey=continuationService` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/roster/index.js` |
| tab 组件 | `src/pages/roster/ContinuationService/`（灰度回退：`ContinuationServiceLegacy/`） |
| 主 service 文件 | `src/services/continuationService.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（config / gray / schema）见 [_page.md](./_page.md)。

## 接口清单

### 1. 列表数据（进页面 + 筛选 / 翻页 / 排序）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/筛选 | `getContinuationServiceList` | `/bgwApi/component/student-center/roster/renewal/page` | `src/services/continuationService.js:5` | student-center | `/roster/renewal/page` | 分页查询续班服务列表 [1995841] | **主列表数据** |
| 总数超上限 | `getListCount` | `/bgwApi/component/student-center/roster/renewal/count` | `src/services/continuationService.js:29` | student-center | `/roster/renewal/count` | 获取总数（超上限时用）[1995832] | total 触达上限时单独取真实值 |
| 默认视图 | `getContinuationServiceDefault` | `/bgwApi/component/student-center/roster/renewal/default/page` | `src/services/continuationService.js:21` | student-center | `/roster/renewal/default/page` | 分页查询续班服务列表 [1995828] | 默认筛选/视图列表 |
| 默认视图 | `getListCountDefault` | `/bgwApi/component/student-center/roster/renewal/default/count` | `src/services/continuationService.js:37` | student-center | `/roster/renewal/default/count` | 获取总数（超上限时用）[1995835] | 默认视图总数 |
| 进页面 | `getDefaultValue` | `/bgwApi/component/student-center/roster/renewal/defaultValue` | `src/services/continuationService.js:45` | student-center | `/roster/renewal/defaultValue` | 获取 GlobalSearch 默认值接口 [1995833] | 全局搜索默认值 |
| 进页面 | `getContinuationRound` | `/bgwApi/component/student-center/roster/renewal/getRenewalInfo` | `src/services/continuationService.js:53` | student-center | `/roster/renewal/getRenewalInfo` | 续班信息 [1995839] | 续班轮次信息 |
| 进页面 | `getContinuationIndicator` | `/bgwApi/component/student-center/roster/renewal/subclazz/statistic` | `src/services/continuationService.js:61` | student-center | `/roster/renewal/subclazz/statistic` | 续班指标统计 [1995842] | 顶部续班指标 |
| 默认视图 | `getContinuationIndicatorDefault` | `/bgwApi/component/student-center/roster/renewal/default/subclazz/statistic` | `src/services/continuationService.js:69` | student-center | `/roster/renewal/default/subclazz/statistic` | 续班指标统计 [1995840] | 默认视图指标 |

### 2. 编辑保存

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 行内编辑保存 | `updateList` | `/bgwApi/component/student-center/roster/renewal/edit` | `src/services/continuationService.js:13` | student-center | `/roster/renewal/edit` | 编辑学生信息 [1995834] | 保存单元格修改 |

### 3. 悬浮 / 单元格

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| hover 亲密度 | `getIntimacyDetail` | `/component/student-center/studentClazz/intimacyHover` | `src/services/continuationService.js:76` | student-center | `/studentClazz/intimacyHover` | 获取学员亲密度 [30665] | 亲密度悬浮详情 |
| hover 沟通记录 | `getRenewalReachCount` | `/bgwApi/component/student-center/roster/renewal/reach/record` | `src/services/continuationService.js:84` | student-center | `/roster/renewal/reach/record` | 续班沟通记录 [1995831] | 续班沟通记录悬浮 |
| hover 课程完成度 | `getCourseCompletion` | `/bgwApi/component/student-center/roster/renewal/intimacy/course` | `src/services/continuationService.js:92` | student-center | `/roster/renewal/intimacy/course` | 课程完成度 [1995836] | 课程完成度悬浮 |
| hover 服务亲密度 | `getServiceIntimacy` | `/bgwApi/component/student-center/roster/renewal/intimacy/service` | `src/services/continuationService.js:100` | student-center | `/roster/renewal/intimacy/service` | 服务亲密度 [1995830] | 服务亲密度悬浮 |
| 最近看课 | `getRecentListenSituation` | `/component/student-center/studentClazz/recentLessonSituation` | `src/services/clazzRosterOL.js:51` | student-center | `/studentClazz/recentLessonSituation` | 获取学员最近看课进度条 [30675] | 最近看课进度 |
| 推荐班级 | `recommendClazzList` | `/bgwApi/product-b/b/renewMaster/recommendClazzList` | `src/services/continuationService.js:107` | product-b | `/b/renewMaster/recommendClazzList` | 查询推荐班级列表 [2734275] | 创建订单推荐班级 |
| 判断续班班 | `checkClazzInRenewalPlan` | `/bgwApi/component/student-center/roster/renewal/judgeIsRenewalSubClazzNumber` | `src/services/continuationService.js:114` | student-center | `/roster/renewal/judgeIsRenewalSubClazzNumber` | 判断是否是续班辅导班 [2153606] | 校验班级是否在续班计划 |

### 4. 续班原因 / AI 预测（归因）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 续班意向预测 | `getContinueClassPrediction` | `/bgwApi/component/student-center/ai/clazzUser/levelReasonAndHistory` | `src/services/continuationService.js:122` | student-center | `/ai/clazzUser/levelReasonAndHistory` | 分层原因和变化记录 [2977228] | 续班意向预测等级 + 历史 |
| hover 归因详情 | `getRenewalReasonDetail` | `/bgwApi/component/student-center/ai/renewal/reason/detail` | `src/services/continuationService.js:130` | student-center | `/ai/renewal/reason/detail` | 续班归因详情 [5292053] | 未续跟进/已续总结原文 |
| 原因弹窗选项 | `getRenewalReasonOptions` | `/bgwApi/component/student-center/ai/renewal/reason/options` | `src/services/continuationService.js:138` | student-center | `/ai/renewal/reason/options` | 续班原因分类字典 [5292052] | 老师总结弹窗勾选项 |
| 保存原因 | `saveRenewalReasonManual` | `/bgwApi/component/student-center/ai/renewal/reason/manual/save` | `src/services/continuationService.js:146` | student-center | `/ai/renewal/reason/manual/save` | 保存老师填写的续班原因 [5292051] | 覆盖式保存 |

### 5. 问卷 / 报名 / 报告链接

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 发问卷 | `getQuestionInfo` | `/bgwApi/component/student-center/roster/renewal/sendQuestion/getQuestionInfo` | `src/services/continuationService.js:154` | student-center | `/roster/renewal/sendQuestion/getQuestionInfo` | 问卷信息获取 [3381630] | 续班问卷信息 |
| 校验问卷 | `sendQuestionValidate` | `/component/student-center/roster/renewal/sendQuestion/validate` | `.../QuestionnaireLink/service.js:15` | student-center | `/roster/renewal/sendQuestion/validate` | 发问卷前置校验 [1995843] | 校验续班问卷链接是否存在 |
| 续班报名校验 | `renewalOrderValidate` | `/component/student-center/roster/renewal/renewalOrder/validate` | `.../PureContinuation/service.js:19` | student-center | `/roster/renewal/renewalOrder/validate` | 续班报名前置校验 [2093628] | 创建订单前置校验 |
| 预报名校验 | `renewalOrderValidate` | `/component/student-center/roster/renewal/renewalPreRegistration/validate` | `.../PreRegistrationLink/service.js:19` | student-center | `/roster/renewal/renewalPreRegistration/validate` | 续班预报名前置校验 [2652063] | 预报名链接前置校验 |
| 报告链接 | `getReportUrl` | `/reachPortal/reportConfig/getReportUrl` | `.../{QuestionnaireLink,PureContinuation,PreRegistrationLink}/service.js` | reach-service | `/reachPortal/reportConfig/getReportUrl` | 获取预览或发送链接 [734494] | 通用报告链接 |
| 推荐主体 | `getRecommendAppInfo` | `/reachPortal/reportConfig/getRecommendAppInfo` | `.../PureContinuation/service.js:12` | reach-service | `/reachPortal/reportConfig/getRecommendAppInfo` | 获取主体 [2093624] | 推荐主体信息 |
| 预报名链接 | `getPreRegistrationLinkInfo` | `/reachPortal/reportConfig/getPreRegistrationLink` | `.../PreRegistrationLink/service.js:12` | reach-service | `/reachPortal/reportConfig/getPreRegistrationLink` | 预报名链接 [2652061] | 预报名链接信息 |
| 灰度开关 | `getGrayService` | `/product-b/b/renewMaster/configFlag` | `.../CreateOrder/gray.js:7` | product-b | `/b/renewMaster/configFlag` | 获取配置开关 [2734336] | 创建订单灰度 |

> 共享组件（`ReportWidget` / `ReachBusiness` / `QuestionnaireDetail` / `CustomSaleLink` / `QuickQueryV2` / `ReachReport` 等）另有接口，被多页面复用，待单独归档。

## 关键字段：主列表 `/roster/renewal/page`

- 请求 DTO：`com.gaotu.yunying.student.center.domain.model.roster.RenewalRosterListReq`
- 入参：`route.sceneVersionNumber`（场景版本号）、`quickFilter.*`（预报名意向/续班报告状态/预售状态/预售下单时间/续班下单时间）、`filter`（普通筛选 map）、`pager{current,pageSize,total}`、`orderItem{name,order}`
- 出参：`data.list[]` + `data.pager{total, approximateTotal}`

## 排查提示

- **列表为空 / 数量不对** → `/roster/renewal/page` 的 `filter`/`quickFilter`；total 触顶看 `/roster/renewal/count`。
- **续班指标不对** → `/roster/renewal/subclazz/statistic`。
- **续班原因/归因不对** → `ai/renewal/reason/{detail,options,manual/save}` + `ai/clazzUser/levelReasonAndHistory`。
- **亲密度/完成度 hover 无数据** → `studentClazz/intimacyHover`、`roster/renewal/intimacy/{course,service}`。
- **创建订单/预报名点不动** → `roster/renewal/{renewalOrder,renewalPreRegistration}/validate`。
- **tab 不显示** → `/roster/gray` + `/roster/renewal/config`（见 [_page.md](./_page.md)）。

## 青舟接口详情页

- [POST /roster/renewal/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1995841&appId=student-center&branchName=release)
- [POST /roster/renewal/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1995834&appId=student-center&branchName=release)
- [POST /roster/renewal/getRenewalInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1995839&appId=student-center&branchName=release)
- [POST /roster/renewal/subclazz/statistic](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1995842&appId=student-center&branchName=release)
- [POST /ai/renewal/reason/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5292053&appId=student-center&branchName=release)
- [POST /roster/gray](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=668688&appId=student-center&branchName=release)
