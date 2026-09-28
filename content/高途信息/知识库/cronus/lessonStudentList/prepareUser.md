# 课节学员 / 课前准备（lessonStudentList · bs=prepareUser）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonStudentList?ln=<课节号>&scn=<辅导班号>&cn=<班级号>&bs=prepareUser` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lessonStudent/index.js` |
| tab 组件 | `src/pages/lessonStudent/LessonPrepare/`（`./LessonPrepare`） |
| 主 service 文件 | `src/services/studentLessonPrepare.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（gray / scene count / 课节 / updateList / 自定义列）见 [_page.md](./_page.md)。仅大班课（`lessonType=normal`）展示。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页/排序 | `getStudentLessonPrepareList` | `/bgwApi/component/student-center/lesson/prepare/user/page` | `src/services/studentLessonPrepare.js:11`（调用 `src/pages/lessonStudent/LessonPrepare/index.js:203`） | student-center | `/lesson/prepare/user/page` | [POST]/user/page [980559] | **主列表数据** |
| 总数超上限 | `getPager` | `/bgwApi/component/student-center/lesson/prepare/user/count` | `src/services/studentLessonPrepare.js:19`（调用 `.../LessonPrepare/index.js:234`） | student-center | `/lesson/prepare/user/count` | [POST]/user/count [980563] | 单独取真实总数 |
| 进页面（催到课灰度/WS） | `getGrayService` | `GET /component/student-center/lesson/prepare/attendance-remind/switch` | `src/services/studentLessonPrepare.js:72`（调用 `.../LessonPrepare/index.js:454`） | student-center | `/lesson/prepare/attendance-remind/switch` | [GET]/attendance-remind/switch [2623715] | 决定是否连 WebSocket 实时刷新 |
| 推荐连麦 | `liveRecommendCreate` | `/component/student-center/liveRecommend/create` | `src/services/lesson.js:10`（调用 `.../LessonPrepare/index.js:501`） | student-center | `/liveRecommend/create` | [POST]/create [444969] | 单元格切换推荐连麦 |
| 课节数据卡片 | `getStudentLessonPrepareStatistic` | `/bgwApi/component/student-center/lesson/prepare/statistic` | `src/services/studentLessonPrepare.js:3`（调用 `.../LessonPrepare/components/LessonDataToolCard/index.js:67`） | student-center | `/lesson/prepare/statistic` | [POST]/statistic [980555] | 预出勤率/预习完成率等 |
| 触达/短信前置校验 | `getLessonBeforeValidation` | `/component/student-center/lesson/prepare/operate/validation` | `src/services/lessonPrepare.js:40`（调用 `.../LessonPrepare/components/{ReachBusinessWithContext,ReachReport}/index.jsx`） | student-center | `/lesson/prepare/operate/validation` | [POST]/operate/validation [1159247] | 发短信/触达校验 |
| hover 催到课记录 | `getRemindRecords` | `/bgwApi/component/student-center/lesson/prepare/attendRemind/record` | `src/services/studentLessonPrepare.js:34`（调用 `.../custom/render/RemindRecords/index.js:24`） | student-center | `/lesson/prepare/attendRemind/record` | [POST]/attendRemind/record [980544] | 待催到课悬浮记录 |
| hover 催预习记录 | `getPreviewRemindRecords` | `/bgwApi/component/student-center/lesson/prepare/previewRemind/record` | `src/services/studentLessonPrepare.js:41`（调用 `.../custom/render/PreviewRemindRecords/index.js:24`） | student-center | `/lesson/prepare/previewRemind/record` | [POST]/previewRemind/record [980561] | 待催预习悬浮记录 |

## 青舟接口详情页

- [POST /lesson/prepare/user/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=980559&appId=student-center&branchName=release)
- [POST /lesson/prepare/user/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=980563&appId=student-center&branchName=release)
- [GET /lesson/prepare/attendance-remind/switch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2623715&appId=student-center&branchName=release)
- [POST /lesson/prepare/statistic](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=980555&appId=student-center&branchName=release)
- [POST /lesson/prepare/attendRemind/record](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=980544&appId=student-center&branchName=release)
