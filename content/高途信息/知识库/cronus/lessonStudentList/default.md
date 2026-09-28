# 课节学员 / 默认（lessonStudentList · bs=default）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonStudentList?ln=<课节号>&scn=<辅导班号>&cn=<班级号>&bs=default` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lessonStudent/index.js` |
| tab 组件 | `src/pages/lessonStudent/Default/`（`./Default`） |
| 主 service 文件 | `src/pages/lessonStudent/Default/services.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（gray / scene count / 课节 / updateList）见 [_page.md](./_page.md)。`sl=1` 时走小灶课接口。

## 接口清单

### 1. 主列表 / 计数

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页（大班课） | `getlLessonStudentList` | `/component/student-center/lesson/user/list` | `src/pages/lessonStudent/Default/services.js:4`（调用 `.../Default/index.js:836`） | student-center | `/lesson/user/list` | [POST]/user/list [30714] | **主列表数据** |
| 列表/筛选/翻页（小灶课） | `getlSmallLessonStudentList` | `/component/student-center/lesson/parentsMeeting/user/list` | `.../Default/services.js:11`（调用 `.../Default/index.js:830`） | student-center | `/lesson/parentsMeeting/user/list` | [POST]/parentsMeeting/user/list [30715] | 小灶课主列表（`isSmallLesson`） |
| 总数（大班课） | `lessonUserCount` | `/component/student-center/lesson/user/list/count` | `.../Default/services.js:31`（调用 `.../Default/index.js:639`） | student-center | `/lesson/user/list/count` | [POST]/user/list/count [1033506] | 总数兜底 |
| 总数（小灶课） | `lessonUserParentMeetingCount` | `/component/student-center/lesson/parentsMeeting/user/list/count` | `.../Default/services.js:37`（调用 `.../Default/index.js:638`） | student-center | `/lesson/parentsMeeting/user/list/count` | [POST]/parentsMeeting/user/list/count [1033508] | 小灶课总数兜底 |
| 推荐连麦 | `liveRecommendCreate` | `/component/student-center/liveRecommend/create` | `.../Default/services.js:25`（调用 `.../Default/index.js:745`） | student-center | `/liveRecommend/create` | [POST]/create [444969] | 单元格切换推荐连麦 |
| 进页面 | `getGrayStatus` | `/component/student-center/study/data/gray` | `src/services/studentProfile.js:41`（调用 `.../Default/index.js:736`） | student-center | `/study/data/gray` | 学员详情灰度 [47244] | 决定学员档案走新版/学情抽屉 |

### 2. 单元格 / 操作

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 取消请假 | `cancelLeave` | `/component/student-center/clazz/lesson/cancel/leave` | `src/pages/lessonStudent/Default/components/AskForLeave/services.js:4`（调用 `.../AskForLeave/index.js:26`） | student-center | `/clazz/lesson/cancel/leave` | 取消请假 [30644] | 请假悬浮-取消请假 |
| 直播答题抽屉 | `getLiveQuizDetail` | `/fairy/subclazz/learnSituation/personal/v2/getLiveQuizDetail` | `.../Default/components/LivingAnswer/services.js:3`（调用 `.../LivingAnswer/index.js:34`） | fairy.gaotu100.com | `/subclazz/learnSituation/personal/v2/getLiveQuizDetail` | 学习数据-直播答题情况 [35064] | 直播答题 tab |
| 直播答题抽屉 | `getPersonalClazzLessonSituationDetail` | `/fairy/subclazz/learnSituation/personal/getPersonalClazzLessonSituationDetail` | `.../LivingAnswer/services.js:10`（调用 `.../LivingAnswer/index.js:60`） | fairy.gaotu100.com | `/subclazz/learnSituation/personal/getPersonalClazzLessonSituationDetail` | 学习数据-课节学习数据详情 [35060] | 直播答题 tab（获得荣誉/学币） |
| 课后练习 tab | `afterClassUrl` | `/fairy/subclazz/learnSituation/personal/getSubjectAndExerciseDetailUrl` | `src/pages/lessonStudent/components/AnswerPracticeDrawer/services.js:3`（调用 `.../AnswerPracticeDrawer/index.js:51`） | fairy.gaotu100.com | `/subclazz/learnSituation/personal/getSubjectAndExerciseDetailUrl` | 学习数据-学部信息和课后练习明细组件url [35062] | 答疑练习抽屉-课后练习 iframe |
| 直播发言 tab | `fetchLiveComments` | `/component/student-center/liveSpeak/lesson/speakContent/list` | `src/pages/lessonStudent/components/LiveCommentTable/services.ts:28`（调用 `.../LiveCommentTable/index.tsx:14`） | student-data | `/liveSpeak/lesson/speakContent/list` | [POST]/lesson/speakContent/list [30527] | 答疑练习抽屉-直播发言 |
| 查看报告 | `getVisitDetail` | `/bgwApi/component/student-center/report/getViewDuration` | `src/services/clazzRosterOL.js:224`（调用 `.../Default/components/ReportDetailModal/index.tsx:21`） | student-center | `/report/getViewDuration` | 获取报告查看时长 [30603] | 课节报告状态-查看报告弹窗 |

## 青舟接口详情页

- [POST /lesson/user/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30714&appId=student-center&branchName=release)
- [POST /lesson/user/list/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1033506&appId=student-center&branchName=release)
- [POST /clazz/lesson/cancel/leave](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30644&appId=student-center&branchName=release)
- [GET /study/data/gray](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=47244&appId=student-center&branchName=release)
- [POST /subclazz/learnSituation/personal/v2/getLiveQuizDetail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=35064&appId=fairy.gaotu100.com&branchName=release)
- [POST /liveSpeak/lesson/speakContent/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30527&appId=student-data&branchName=release)
