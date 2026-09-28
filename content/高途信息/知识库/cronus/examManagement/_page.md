# 考试管理（examManagement）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/cronus/examManagement` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 cronus（`/crm/micro-cronus`） |
| cronus 路由 | `cronus/config/routes.js`：`/examManagement` → `./examManagement`（`src/pages/examManagement/index.js`） |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 主 service 文件 | `src/services/examManagement.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

## 接口清单

### 1. 列表 / 筛选（进页面 + 搜索 / 翻页 / 排序）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/搜索 | `FeituData fetch`（内联） | `/component/student-center/examManage/list` | `src/pages/examManagement/index.js:377` | student-center | `/examManage/list` | 考试列表 [506574] | **主列表数据** |
| 进页面/展开筛选 | `getDictionary` | `/component/student-center/base/student/dictionary` | `src/services/examManagement.js:4` | student-center | `/base/student/dictionary` | 获取字典枚举值及对应名称 [43944] | 考试类型枚举（`examManageTypes`） |
| 选带班老师 | `getPageAssistantTeacher` | `/component/student-center/studentClazz/pageAssistantTeacher` | `src/services/examManagement.js:14` | student-center | `/studentClazz/pageAssistantTeacher` | [POST]/pageAssistantTeacher [30677] | 带班老师下拉 |

### 2. 考试详情抽屉 — 考试统计

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 打开统计 Tab | `getExamAnswerOverview` | `/component/student-center/examManage/overview` | `src/services/examManagement.js:24` | student-center | `/examManage/overview` | 基础信息-考试概览 [506572] | 答题数据卡片 |
| 打开统计 Tab | `getExamScoreSpan` | `/component/student-center/examManage/scoreSpan` | `src/services/examManagement.js:34` | student-center | `/examManage/scoreSpan` | 基础信息-分数分布 [506573] | 成绩分布 |

### 3. 考试详情抽屉 — 学员作答

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 打开作答 Tab | `getAnsweredStudentList` | `/component/student-center/examManage/studentList` | `src/services/examManagement.js:44` | student-center | `/examManage/studentList` | 学员作答-列表 [506576] | 学员作答列表 |
| 点「报告」 | `getExamUrl` | `/component/student-center/exam/show/url` | `src/services/examManagement.js:55` | student-center | `/exam/show/url` | 获取报告链接 [47246] | 报告链接/版本 |
| 打开作答 Tab | `getReportStatusTree` | `/component/student-center/base/enum/offlineExam/reportStatusTree` | `src/services/examManagement.js:99` | student-center | `/base/enum/offlineExam/reportStatusTree` | 试卷状态枚举 [1415898] | 试卷状态筛选 |
| 查看手机号 | 内联 api 配置 | `/student-center/userSecret/getBaseInfo` | `src/pages/examManagement/components/AnsweredStudents/config.js:84` | student-center | `/userSecret/getBaseInfo` | 查询学员机密信息 [30733] | `EncryptText` 取手机号 |
| 下载报告长图 | `downloadLongPic` | `/fairy/longtu/gen` | `src/services/examManagement.js:89` | fairy.gaotu100.com | `/longtu/gen` | [GET]/gen [35410] | 报告下载长图 |

### 4. 考试详情抽屉 — 题目分析 / 试卷详情

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 打开题目分析 Tab | `getQuestionAnalysis` | `/component/student-center/examManage/questionList` | `src/services/examManagement.js:65` | student-center | `/examManage/questionList` | 题目分析-列表 [506571] | 题目分析列表 |
| 打开题目详情 | `getQuestionDetail` | `/component/student-center/examManage/question/studentList` | `src/services/examManagement.js:73` | student-center | `/examManage/question/studentList` | 题目分析详情 [506577] | 题目下学员列表 |
| 打开题目详情 | `getQuestionTemplate` | `/component/student-center/examManage/question/info` | `src/services/examManagement.js:81` | student-center | `/examManage/question/info` | 题目分析详情 [506570] | 题目/答题详情 |
| 打开试卷详情 Tab | `ExamPaperDetail`（iframe） | `https://mis.gaotu100.com/mis-exam/fairyExam` | `src/pages/examManagement/components/ExamPaperDetail/index.js:5` | mis-exam（外部页面） | — | — | 试卷详情 iframe |

> 共享组件（`@/components/AccountNameFilter`、`SearchSelect`、`ClazzPeriodSearch`、`BatchActionBar`、`WechatBatchSending`、`SearchForm`、`@coeus/render` 的 `WidgetRender`、`@gaotu/reach-widget` 的 `ThirdPartyReport`、`@feitu/wecom`、`@coeus/feature` 的 `Table` 等）另有接口，被多页面复用，待单独归档。学员档案抽屉见 `@/pages/StudentProfile`。

## 青舟接口详情页

- [POST /examManage/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=506574&appId=student-center&branchName=release)
- [POST /base/student/dictionary](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=43944&appId=student-center&branchName=release)
- [POST /studentClazz/pageAssistantTeacher](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30677&appId=student-center&branchName=release)
- [POST /examManage/overview](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=506572&appId=student-center&branchName=release)
- [POST /examManage/scoreSpan](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=506573&appId=student-center&branchName=release)
- [POST /examManage/studentList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=506576&appId=student-center&branchName=release)
- [POST /examManage/questionList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=506571&appId=student-center&branchName=release)
- [GET /examManage/question/info](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=506570&appId=student-center&branchName=release)
