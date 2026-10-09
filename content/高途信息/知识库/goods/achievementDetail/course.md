# 业绩看板 / 订单明细（课程）（course）

## 定位

| 项 | 值 |
|---|---|
| tab | `/ark/app-goods/achievementDetail` 默认 tab `set`「订单明细（课程）」 |
| 前端仓库 | gaotu-fe-goodsmanage（见 [_page.md](_page.md)） |
| tab 组件 | `src/pages/Achievement/AchieveDetail.tsx`，筛选 `SearchHeader/index.tsx`，判单过程抽屉 `ProcessDrawer/index.js` → `OrderProcess/` |
| 后端主服务 | performance-attribution `PerformanceKanbanCourseController`（类 `@RequestMapping("/performance/management")`，`performance-attribution-web/.../web/controller/PerformanceKanbanCourseController.java:72`） |

## 接口清单

`A/` = `src/pages/Achievement/`；service 统一在 `A/service/index.ts`，判单过程在 `A/OrderProcess/services.js`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 controller | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进 tab | `GET /course-setting/b/course/category/tree` | `getCategoryList` | `A/SearchHeader/index.tsx:154`（`src/services/physicalGoods.js:13`） | course-setting | 共享字典 | 读 |
| 枚举返回后 / 查询 / 翻页 / 表头筛选 | `POST /performance/management/attribution/list` | `getPerformanceList` | `A/AchieveDetail.tsx:89,243,253,261`（`service/index.ts:41`） | `:113` | 查询业绩 [36994] | 读 |
| 「导出」 | `POST /performance/management/attribution/export` | `deport` | `A/AchieveDetail.tsx:303`（`service/index.ts:49`） | `:237` | 导出业绩 [37001] | 读（异步发邮件） |
| 归属人输入搜索 | `POST /performance/management/verify/employee` | `getBelongerList` | `A/SearchHeader/index.tsx:254`（`service/index.ts:10`） | `:396` | 校验归属人查询权限 [36999] | 读 |
| 列表「判单过程」→ 抽屉 | `POST /performance/management/judge/result` | `getJudgeResult` | `A/AchieveDetail.tsx:212` → `A/OrderProcess/index.js:44`（`OrderProcess/services.js:11`） | `:333` | 判单结果 [36998] | 读 |
| 抽屉内「调课信息」 | `POST /performance/management/judge/reason/transfer` | `getClazzChangeInfo` | `A/OrderProcess/components/ChangeClazzInfo/index.js:36`（`services.js:20`） | `:353` | 判单过程-调课信息 [36995] | 读 |
| 抽屉内「归属类型/归属人」 | `POST /performance/management/judge/reason/detail` | `getBelonging` | `A/OrderProcess/components/TypeAndOwner/index.js:67`（`services.js:29`） | `:373` | 判单过程-归属详情 [36996] | 读 |

`/performance/management/user/getUserSecretBaseInfo`（`service/index.ts:88`，后端 `:305`，id 36997）前端定义了但本 tab 没调用（`AchieveDetail.tsx:151` 脱敏组件已注释）。

## 链路与表

服务实现 `performance-attribution-domain/.../performancekanban/impl/PerformanceKanbanServiceImpl.java`（下称 `K`）。

| 接口 | 服务方法 | 读表 | 写表 | 其它 |
|---|---|---|---|---|
| attribution/list | `K#getOrderAttributionList:291` → OES 默认 `getOrderAttributionDtoListWithStaff:1599`（否则 `getOrderAttributionDtoListWithMenShen:1672`）→ `selectPerformanceOrderAttributionTwo:1971` → `convertToOrderAttributionDto:2101` | `gaotu_stat.performance_order_attribution_total`（`PerformanceOrderAttributionTotalMapper.xml` `getCount` / `getCountByForceIndex` / `getHasDataEmailPrefixList` / `selectList`） | 无 | Feign：teacher（员工）、staff（主岗下属邮箱，`PerformanceDashboardServiceImpl#queryMainJobEmailPrefixByStaff`）、student（手机号/姓名→userId、补学员信息）、course/clazz facade（课程/班级编号→number、补班级信息）；menshen 分支另调门神部门树 + 品类权限 |
| attribution/export | `K#getOrderAttributionExport:399` | 同 list（isExport=true） | 无 | 线程池异步，`PerformanceAttributionUtils#sendAttributionMail` 发邮件给当前登录人，返回「导出成功（最大1万条）」 |
| verify/employee | `K#verifyEmployeeByName:702` | 无 | 无 | teacher、menshen、staff `listStaffByAccountIdsWithDot`、`performanceDashboardService.hasManageLabel` |
| judge/result | `K#getOrderPerformanceJudgeResult:543` | `gaotu_stat.performance_attribution_credentials`、`performance_physical_attribution_credentials`、`performance_attribution_judge_reason` | 无 | — |
| judge/reason/transfer | `K#getOrderPerformanceTransferJudgeReason:619` | `performance_attribution_judge_reason`（`selectByOrderNumberAndScene`）、`performance_order_attribution_total`（`selectByOrderNumbersAndStatus`） | 无 | — |
| judge/reason/detail | `K#getOrderPerformanceJudgeReasonDetail:648` | `performance_attribution_judge_reason` | 无 | order facade（订单）、clazz facade |

关键入参：`typeList`（业绩类型，含「无归属」= `PerformanceTypeEnums.NONE`）、`roleSign`（0 运营 / 1 非运营）、`beginTime/endTime`（交易时间，endTime 截到当前时刻）、`categoryPaths`、`courseBizNumber`、`clazzBizNumber`（班级服务查不到时当作 OMO skuNumber 直接查）、`userParam`（手机号/姓名/userId）、`emailPrefixList`、`orderNumbers`。

数据权限：
- staff 分支（OES 默认）：只按 staff 主岗下属的邮箱前缀过滤；运营角色且没指定归属人时追加空前缀 `""` 查「无归属」。代码里**没用 `categoryPaths` 过滤课程**（`getCourseNumbersNoFilter:1890` 只处理 `courseBizNumber`），是否符合预期未确认。
- menshen 分支（OLS 或开关关）：controller `:135-151` 先做品类权限校验（`validateCategoryAccess:159`，运营角色），再查门神部门树。
- `courseNumber` 数量 ≥ `adbInLimit` 直接报「查询课程数量过多，请缩小查询范围」（`K:1998`）。

## 排查提示

- 列表里「判单过程」按钮不显示：`fillJudgeReasonDisplay:385`，需已支付状态且 `tradeTime >= performanceJudgeDisplayStartTime`（Apollo）
- 查不到某单 / 归属人为空：先查 `gaotu_stat.performance_order_attribution_total`，再看判单记录 `performance_attribution_judge_reason`；排查套路见 [业绩归因](../../../工单/续班与业绩/业绩归因/README.md)
- 导出没收到邮件：异步线程异常只打 `发送邮件出现异常！` 日志，接口仍返回成功

## 青舟接口详情页

- [POST /performance/management/attribution/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36994&appId=performance-attribution&branchName=release) id=36994
- [POST /performance/management/attribution/export](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37001&appId=performance-attribution&branchName=release) id=37001
- [POST /performance/management/verify/employee](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36999&appId=performance-attribution&branchName=release) id=36999
- [POST /performance/management/judge/result](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36998&appId=performance-attribution&branchName=release) id=36998
- [POST /performance/management/judge/reason/transfer](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36995&appId=performance-attribution&branchName=release) id=36995
- [POST /performance/management/judge/reason/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36996&appId=performance-attribution&branchName=release) id=36996
- [POST /performance/management/user/getUserSecretBaseInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36997&appId=performance-attribution&branchName=release) id=36997（未调用）
