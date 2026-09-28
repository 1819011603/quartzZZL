# 班级花名册 / 阶段反馈（clazzRosterOL · tabKey=stageFeedback）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/clazzRosterOL?tabKey=stageFeedback` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/roster/index.js` |
| tab 组件 | `src/pages/roster/StageFeedback/` |
| 主 service 文件 | `src/services/stageFeedback.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（config / gray / schema）见 [_page.md](./_page.md)。

## 接口清单

### 1. 列表数据（进页面 + 筛选 / 翻页 / 排序）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/筛选 | `getStageFeedbackList` | `/bgwApi/component/student-center/roster/stageFeedback/page` | `src/services/stageFeedback.js:19` | student-center | `/roster/stageFeedback/page` | [POST]/stageFeedback/page [668681] | **主列表数据** |
| 总数超上限 | `getListCount` | `/bgwApi/component/student-center/roster/stageFeedback/count` | `src/services/stageFeedback.js:27` | student-center | `/roster/stageFeedback/count` | [POST]/stageFeedback/count [668679] | total 触达上限时单独取真实值 |
| 行内编辑保存 | `updateList` | `/bgwApi/component/student-center/roster/stageFeedback/edit` | `src/services/stageFeedback.js:35` | student-center | `/roster/stageFeedback/edit` | [POST]/stageFeedback/edit [668685] | 保存单元格修改 |
| 进页面 | `getDefaultValueService` | `/bgwApi/component/student-center/roster/stageFeedback/defaultValue` | `src/services/stageFeedback.js:3` | student-center | `/roster/stageFeedback/defaultValue` | 获取阶段反馈场景默认值 [668680] | GlobalSearch 默认值 |
| 顶部指标 | `getSubclazzStatistic` | `/bgwApi/component/student-center/roster/stageFeedback/subclazz/statistic` | `src/services/stageFeedback.js:43` | student-center | `/roster/stageFeedback/subclazz/statistic` | [POST]/stageFeedback/subclazz/statistic [735861] | 阶段反馈数据指标卡片 |

### 2. 课节快捷筛选

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 打开课节选择器 | `getLessonCount` | `/bgwApi/component/student-center/roster/clazzLesson/count` | `src/services/stageFeedback.js:11` | student-center | `/roster/clazzLesson/count` | [POST]/clazzLesson/count [668683] | 正式/赠课课节数 |
| 打开课节选择器 | `getClazzLessonList` | `/bgwApi/component/student-center/roster/clazzLesson/list` | `src/services/stageFeedback.js:66` | student-center | `/roster/clazzLesson/list` | [POST]/clazzLesson/list [943814] | 课节列表（自定义课节） |

### 3. 单元格悬浮 / 点击（复用 clazzRosterOL 花名册单元格组件）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 今日动态 | `getStudentBehavior` | `/fairy/student-center/studentBehavior/list` | `src/services/clazzRosterOL.js:14` | student-center | `/studentBehavior/list` | 查看学员今日动态 [30610] | 今日动态列 |
| 今日动态已读 | `changeBehaviorStatus` | `/fairy/student-center/studentBehavior/change/behaviorStatus` | `src/services/clazzRosterOL.js:22` | student-center | `/studentBehavior/change/behaviorStatus` | 更改学员具体行为已读状态 [30609] | 标记已读 |
| 听课情况 | `getRecentListenSituation` | `/component/student-center/studentClazz/recentLessonSituation` | `src/services/clazzRosterOL.js:51` | student-center | `/studentClazz/recentLessonSituation` | 获取学员最近看课进度条 [30675] | 最近课节悬浮 |
| 课中答题 | `getUserLiveQuestionDetail` | `/component/student-center/studentClazz/getUserLiveQuestionDetail` | `src/services/clazzRosterOL.js:286` | student-center | `/studentClazz/getUserLiveQuestionDetail` | 获取学员在该课节下的直播答题数据 [129974] | 直播答题悬浮 |
| 课后答题 | `getUserExerciseDetail` | `/component/student-center/studentClazz/getUserExerciseDetail` | `src/services/clazzRosterOL.js:294` | student-center | `/studentClazz/getUserExerciseDetail` | 获取学员在该课节下的课后练习数据 [129975] | 课后练习悬浮 |

> 共享组件（`@coeus/render` 的 `TableRenderPro` schema、`PagerToolTip`、`ConfigAbleComponents`、`WrongBook`、`ReachReport`、`ReportWidget`、`SendCoins`、`DownLoadCorrections`、`SendCustomReport`、`AccountNameFilter`、`DailyExerciseStatus(Filter)`、`LastFollowContentEdit` 等）接口另见公共组件文档。

## 青舟接口详情页

- [POST /roster/stageFeedback/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=668681&appId=student-center&branchName=release)
- [POST /roster/stageFeedback/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=668685&appId=student-center&branchName=release)
- [POST /roster/stageFeedback/defaultValue](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=668680&appId=student-center&branchName=release)
- [POST /roster/stageFeedback/subclazz/statistic](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=735861&appId=student-center&branchName=release)
- [POST /roster/clazzLesson/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=668683&appId=student-center&branchName=release)
- [POST /roster/clazzLesson/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=943814&appId=student-center&branchName=release)
