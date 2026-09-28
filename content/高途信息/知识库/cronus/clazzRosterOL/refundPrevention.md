# 班级花名册 / 退费管控（clazzRosterOL · tabKey=refundPrevention）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/clazzRosterOL?tabKey=refundPrevention` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/roster/index.js` |
| tab 组件 | `src/pages/roster/RefundPrevention/` |
| 主 service 文件 | `src/services/refundPrevention.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（config / gray / schema）见 [_page.md](./_page.md)。

## 数据来源（ES / 表）

| 接口 | 数据来源 | ES 集群 / 客户端 | 后端代码 |
|---|---|---|---|
| `/roster/refund/page`（主列表）、`/count`、`/default/page`、`/default/count`、`/subclazz/statistic` | ES 索引 **`ads_large_subclazz_user_index`** | `es-cn-smw4b9m200004w3hn.elasticsearch.aliyuncs.com:9200`（bean `studentSubclazzClient`） | `RefundService.page()/count()/subclazzStatistic()` |

> 与续班服务 tab **同一索引**（`ads_large_subclazz_user_index`），只是筛选/指标口径不同；**无独立 MySQL 表**。

## 接口清单

### 1. 列表数据（进页面 + 筛选 / 翻页 / 排序）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/筛选 | `getRefundPreventionList` | `/bgwApi/component/student-center/roster/refund/page` | `src/services/refundPrevention.js:5` | student-center | `/roster/refund/page` | 分页查询退费服务列表 [2552688] | **主列表数据** |
| 总数超上限 | `getListCount` | `/bgwApi/component/student-center/roster/refund/count` | `src/services/refundPrevention.js:41` | student-center | `/roster/refund/count` | 获取总数，当超过index配置最大count时使用 [2552696] | 单独取真实总数 |
| 默认视图 | `getRefundPreventionDefault` | `/bgwApi/component/student-center/roster/refund/default/page` | `src/services/refundPrevention.js:21` | student-center | `/roster/refund/default/page` | 分页查询退费服务列表 [2552679] | 默认筛选/视图列表 |
| 默认视图 | `getListCountDefault` | `/bgwApi/component/student-center/roster/refund/default/count` | `src/services/refundPrevention.js:49` | student-center | `/roster/refund/default/count` | 获取总数，当超过index配置最大count时使用 [2552687] | 默认视图总数 |
| 进页面 | `getDefaultValue` | `/bgwApi/component/student-center/roster/refund/defaultValue` | `src/services/refundPrevention.js:57` | student-center | `/roster/refund/defaultValue` | 获取GlobalSearch默认值接口 [2552678] | GlobalSearch 默认值 |
| 行内编辑保存 | `updateList` | `/bgwApi/component/student-center/roster/refund/edit` | `src/services/refundPrevention.js:13` | student-center | `/roster/refund/edit` | 编辑学生信息 [2552693] | 保存单元格修改 |

### 2. 顶部指标

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/切班 | `getRefundPreventionIndicator` | `/bgwApi/component/student-center/roster/refund/subclazz/statistic` | `src/services/refundPrevention.js:73` | student-center | `/roster/refund/subclazz/statistic` | 退费指标统计 [2552681] | 退费/风险占比卡片 |
| 默认视图 | `getRefundPreventionIndicatorDefault` | `/bgwApi/component/student-center/roster/refund/default/subclazz/statistic` | `src/services/refundPrevention.js:81` | student-center | `/roster/refund/default/subclazz/statistic` | 退费指标统计 [2552683] | 默认视图指标 |

### 3. 内联 / 复用组件接口

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 根因分类筛选 | 内联 api 配置 | `/component/student-center/base/enum/refund/refundReasonTree` | `src/pages/roster/RefundPrevention/custom/fields.js:406` | student-center | `/base/enum/refund/refundReasonTree` | 退费根因枚举 [2552685] | `SelectTreeFilter` 下拉树 |
| 听课情况筛选 | `getListBeginClazzLessons`（复用 `@/pages/clazzRosterOnLine/components/ListenStatusFilter`） | `/component/student-center/studentClazz/listBeginClazzLessons` | `src/services/clazzRosterOL.js:310` | student-center | `/studentClazz/listBeginClazzLessons` | 获取该班级已开课课节 [129972] | 听课情况筛选 |
| 最近看课时间 | `getRecentListenSituation`（复用 `@/pages/clazzRosterOnLine/components/RecentListenTime`） | `/component/student-center/studentClazz/recentLessonSituation` | `src/services/clazzRosterOL.js:51` | student-center | `/studentClazz/recentLessonSituation` | 获取学员最近看课进度条 [30675] | 最近看课时间列 |

> 共享组件（`@/components/CommunicationRecordsPopList`、`OverallIntimacy`、`CommunicateIntimacy`、`ServiceIntimacy`、`Intimacy`、`StatusTag`、`DataCard`、`AccountNameFilter`、`LastFollowContentEdit`、`PagerToolTip` 等）另有接口，被多页面复用，待单独归档。

## 青舟接口详情页

- [POST /roster/refund/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2552688&appId=student-center&branchName=release)
- [POST /roster/refund/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2552693&appId=student-center&branchName=release)
- [POST /roster/refund/default/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2552679&appId=student-center&branchName=release)
- [POST /roster/refund/subclazz/statistic](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2552681&appId=student-center&branchName=release)
- [POST /roster/refund/defaultValue](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2552678&appId=student-center&branchName=release)
- [GET /base/enum/refund/refundReasonTree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2552685&appId=student-center&branchName=release)
