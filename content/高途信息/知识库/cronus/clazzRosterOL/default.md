# 班级花名册 / 花名册（clazzRosterOL · tabKey=default）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/clazzRosterOL?tabKey=default` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/roster/index.js` |
| tab 组件 | `src/pages/clazzRosterOnLine/`（默认视图，组件 `@/pages/clazzRosterOnLine`） |
| 主 service 文件 | `src/services/clazzRosterOL.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（config / gray / schema）见 [_page.md](./_page.md)。

## 接口清单

### 1. 主列表 / 行内编辑

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/筛选/翻页/排序 | `getList` | `/component/student-center/studentClazz/largeClazzList` | `src/services/clazzRosterOL.js:30` | student-center | `/studentClazz/largeClazzList` | [POST]/largeClazzList [30663] | **主列表数据**（`scene=clazzRosterOL`） |
| 总数超上限 | `getLargeClazzListCount` | `/component/student-center/studentClazz/largeClazzList/count` | `src/services/clazzRosterOL.js:4` | student-center | `/studentClazz/largeClazzList/count` | [POST]/largeClazzList/count [30664] | 单独取真实总数 |
| 行内编辑保存 | `updateList` | `/component/student-center/studentClazz/edit` | `src/services/clazzRosterOL.js:41` | student-center | `/studentClazz/edit` | [POST]/edit [30662] | 保存单元格修改（`scene=clazzRosterOL`） |

### 2. 权限 / 灰度 / 配置

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | `getGrayStatus` | `/component/student-center/study/data/gray` | `src/services/studentProfile.js:41` | student-center | `/study/data/gray` | 学员详情灰度 [47244] | 决定学员档案新旧版 |
| 进页面 | `getGrayService` | `/component/student-center/roster/gray` | `src/pages/roster/grayscale/index.js:13` | student-center | `/roster/gray` | 判断灰度逻辑 [668688] | AI 试炼场发报告等开关（见 [_page.md](./_page.md)） |
| 进页面 | `getSendReportAccess` | `/teacher-tool/report/roster/power` | `src/services/clazzRosterOL.js:189` | teacher-tool | `/report/roster/power` | 花名册发送报告按钮权限 [43800] | 底部批量「发报告」入口 |
| 进页面 | `getExamCollectionAccess` | `/student-center/roster/button/gray` | `src/services/clazzRosterOL.js:350` | student-center | `/roster/button/gray` | 默认花名册按钮灰度 [1244681] | 学校考试收集入口 |
| 进页面 | `getYearSelectConfig` | `/component/student-center/roster/yearSelectConfig` | `src/services/clazzRosterOL.js:208` | student-center | `/roster/yearSelectConfig` | 获取年份选择配置 [3884942] | 班级创建年份筛选 |
| 进页面 | `getDefaultFilterValue` | `/component/student-center/filter/defaultValueByScene` | `src/services/clazzRosterOL.js:212` | student-center | `/filter/defaultValueByScene` | 筛选项默认值 [38825] | 班级/期默认筛选值 |
| 改自定义列 | `setPersonalConfig` | `/gaiaCenter/scene/personal/config/edit` | `src/services/metadata.js:22` | gaia-center | `/scene/personal/config/edit` | [POST]/scene/personal/config/edit [39622] | 保存列配置 |

### 3. 视图数量 / 操作列

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 视图 Tab | `queryViewCount` | `/component/student-center/studentClazz/largeClazzList/views/count` | `src/services/clazzRosterOL.js:279` | student-center | `/studentClazz/largeClazzList/views/count` | [POST]/largeClazzList/views/count [220890] | 各视图人数 |
| 合同预览 | `getContractTemplate` | `/api/contract/b/previewContractTemplate` | `src/services/clazzRosterOL.js:157` | contract-server | `/api/contract/b/previewContractTemplate` | 新学员列表预览合同模板 [1281230] | 操作列-合同预览 |
| 复制合同链接 | `getCopyContractUrl` | `/api/contract/b/copyContractUrl` | `src/services/clazzRosterOL.js:165` | contract-server | `/api/contract/b/copyContractUrl` | 新学员列表复制链接 [1281206] | 操作列-复制合同链接 |
| 复制权益链接 | `getEquityUrl` | `/component/student-center/studentClazz/getEquityUrl` | `src/services/clazzRosterOL.js:173` | student-center | `/studentClazz/getEquityUrl` | 获取权益领取链接 [30678] | 操作列-复制权益领取链接 |
| 编辑考试分数 | `getSubjectList` | `/bgwApi/component/student-center/studentClazz/getSubject` | `src/services/clazzRosterOL.js:272` | student-center | `/studentClazz/getSubject` | [POST]/getSubject [49398] | 新增考试分数弹窗取学科 |

### 4. 单元格悬浮 / 点击 / 弹窗

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 今日动态 | `getStudentBehavior` | `/fairy/student-center/studentBehavior/list` | `src/services/clazzRosterOL.js:14` | student-center | `/studentBehavior/list` | 查看学员今日动态 [30610] | 今日动态列 |
| 今日动态已读 | `changeBehaviorStatus` | `/fairy/student-center/studentBehavior/change/behaviorStatus` | `src/services/clazzRosterOL.js:22` | student-center | `/studentBehavior/change/behaviorStatus` | 更改学员具体行为已读状态 [30609] | 标记已读 |
| 亲密度 | `getIntimacyDetail` | `/component/student-center/studentClazz/intimacyHover` | `src/services/clazzRosterOL.js:67` | student-center | `/studentClazz/intimacyHover` | 获取学员亲密度 [30665] | 亲密度 hover |
| 亲密度弹窗 | `getIntimacy` | `/component/student-center/studentDynamic/intimacy` | `src/services/clazzRosterOL.js:59` | student-center | `/studentDynamic/intimacy` | 学员动态最近亲密度展示 [30614] | 亲密度抽屉 |
| 最近看课时间 | `getRecentListenSituation` | `/component/student-center/studentClazz/recentLessonSituation` | `src/services/clazzRosterOL.js:51` | student-center | `/studentClazz/recentLessonSituation` | 获取学员最近看课进度条 [30675] | 最近看课时间/最近课节悬浮 |
| 课中答题 | `getUserLiveQuestionDetail` | `/component/student-center/studentClazz/getUserLiveQuestionDetail` | `src/services/clazzRosterOL.js:286` | student-center | `/studentClazz/getUserLiveQuestionDetail` | 获取学员在该课节下的直播答题数据 [129974] | 直播答题悬浮 |
| 课后答题 | `getUserExerciseDetail` | `/component/student-center/studentClazz/getUserExerciseDetail` | `src/services/clazzRosterOL.js:294` | student-center | `/studentClazz/getUserExerciseDetail` | 获取学员在该课节下的课后练习数据 [129975] | 课后练习悬浮 |
| 线上考试 | `getUserExamDetail` | `/component/student-center/studentClazz/getUserExamDetail` | `src/services/clazzRosterOL.js:302` | student-center | `/studentClazz/getUserExamDetail` | 获取学员在该课节下的考试数据 [129976] | 考试状态悬浮 |
| 最近考试分数 | `getScore` | `/component/student-center/studentClazz/recentExamHover` | `src/services/clazzRosterOL.js:181` | student-center | `/studentClazz/recentExamHover` | 获取考试成绩 [30666] | 最近考试分数悬浮 |
| 学员标签弹窗 | `getStudentTags` | `/fairy/student-center/subclazz/learnSituation/getAllStudentTags` | `src/services/actions.js:36` | student-center | `/subclazz/learnSituation/getAllStudentTags` | 获取所有学员标签 [30692] | 标签弹窗选项 |
| 保存学员标签 | `saveStudentTags` | `/component/student-center/batchOperate/tag/save` | `src/services/actions.js:44` | student-center | `/batchOperate/tag/save` | 批量操作-学员标签保存 [30688] | 标签弹窗保存 |
| 智能英语 | `getUserIntelligentEnglishDetail` | `/component/student-center/aiEnglish/detail` | `src/services/clazzRosterOL.js:357` | student-center | `/aiEnglish/detail` | [POST]/detail [2232086] | 智能英语悬浮 |
| AI 试炼场单元格 | `getAiPracticeHover` | `/component/student-center/studentClazz/aiPracticeHover` | `src/services/clazzRosterOL.js:318` | student-center | `/studentClazz/aiPracticeHover` | 获取 AI 试炼场 Hover 数据 [4882739] | AI 试炼场 hover |
| AI 试炼场筛选 | `getLatestAiPracticeLessons` | `/component/student-center/studentClazz/latestAiPracticeLessons` | `src/services/clazzRosterOL.js:326` | student-center | `/studentClazz/latestAiPracticeLessons` | 获取 AI 试炼场最近课节列表 [4882738] | AI 试炼场筛选 |
| 直播发言明细 | `getLiveCommentDetail` | `/component/student-center/liveSpeak/clazz/speakContent/list` | `src/services/clazzRosterOL.js:364` | student-center | `/liveSpeak/clazz/speakContent/list` | 班级维度-发言明细 [2232087] | 直播发言抽屉 |

### 5. 筛选组件（听课 / 考试）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 听课情况筛选 | `getListBeginClazzLessons` | `/component/student-center/studentClazz/listBeginClazzLessons` | `src/services/clazzRosterOL.js:310` | student-center | `/studentClazz/listBeginClazzLessons` | 获取该班级已开课课节 [129972] | `ListenStatusFilter`/`LiveAnswerStatusFilter`/`ExerciseStatusFilter` 课节下拉 |
| 线上考试筛选 | `getListAllExam` | `/component/student-center/studentClazz/listAllExam` | `src/services/clazzRosterOL.js:334` | student-center | `/studentClazz/listAllExam` | 获取班级下所有考试 [129973] | `ExamStatusFilter` 考试下拉 |

> 共享组件（`@coeus/render` schema、`@coeus/business` 的 `ExamScoreSubmit`、`@coeus/feature`、`BatchActionBar`、`OperateButton`、`Attendance`、`LastFollowContentEdit`、`EditWrapper`、`WechatBatchSending`、`ClazzAndPeriodSearch`、`AccountNameFilter`、`PagerToolTip`、`HaboTabStayReport`、`@gaotu/reach-widget`、`@feitu/wecom` 等）另有接口，被多页面复用，待单独归档。学员档案抽屉见 `@/pages/StudentProfile`。

## 青舟接口详情页

- [POST /studentClazz/largeClazzList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30663&appId=student-center&branchName=release)
- [POST /studentClazz/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30662&appId=student-center&branchName=release)
- [POST /studentClazz/largeClazzList/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30664&appId=student-center&branchName=release)
- [POST /studentClazz/largeClazzList/views/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=220890&appId=student-center&branchName=release)
- [GET /study/data/gray](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=47244&appId=student-center&branchName=release)
- [GET /report/roster/power](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=43800&appId=teacher-tool&branchName=release)
