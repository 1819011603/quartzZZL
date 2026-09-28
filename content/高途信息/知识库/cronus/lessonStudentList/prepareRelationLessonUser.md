# 课节学员 / 关联课节（lessonStudentList · bs=prepareRelationLessonUser）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonStudentList?ln=<课节号>&scn=<辅导班号>&cn=<班级号>&bs=prepareRelationLessonUser` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lessonStudent/index.js` |
| tab 组件 | `src/pages/lessonStudent/RelatedLesson/`（`./RelatedLesson`） |
| 主 service 文件 | `src/services/studentLessonPrepare.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（gray / scene count / 课节 / updateList / 自定义列）见 [_page.md](./_page.md)。仅大班课（`lessonType=normal`）展示。支持 `rangeType`（1=全部关联课节学员）。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页/排序 | `getRelationLessonUserList` | `/bgwApi/component/student-center/lesson/prepare/relation/user/page` | `src/services/studentLessonPrepare.js:76`（调用 `src/pages/lessonStudent/RelatedLesson/index.js:209`） | student-center | `/lesson/prepare/relation/user/page` | [POST]/relation/user/page [4882733] | **主列表数据**（学员维度） |
| 总数超上限 | `getRelationLessonUserCount` | `/bgwApi/component/student-center/lesson/prepare/relation/user/count` | `src/services/studentLessonPrepare.js:83`（调用 `.../RelatedLesson/index.js:240`） | student-center | `/lesson/prepare/relation/user/count` | [POST]/relation/user/count [4882737] | 精确总数兜底（学员维度） |
| 进页面（催到课灰度/WS） | `getGrayService` | `GET /component/student-center/lesson/prepare/attendance-remind/switch` | `src/services/studentLessonPrepare.js:72`（调用 `.../RelatedLesson/index.js:460`） | student-center | `/lesson/prepare/attendance-remind/switch` | [GET]/attendance-remind/switch [2623715] | 决定是否连 WebSocket 实时刷新 |
| 推荐连麦 | `liveRecommendCreate` | `/component/student-center/liveRecommend/create` | `src/services/lesson.js:10`（调用 `.../RelatedLesson/index.js:508`） | student-center | `/liveRecommend/create` | [POST]/create [444969] | 单元格切换推荐连麦（按行取课节/子班） |
| 触达/短信前置校验 | `getLessonBeforeValidation` | `/component/student-center/lesson/prepare/operate/validation` | `src/services/lessonPrepare.js:40`（调用 `.../RelatedLesson/components/{ReachBusinessWithContext,ReachReport}/index.jsx`） | student-center | `/lesson/prepare/operate/validation` | [POST]/operate/validation [1159247] | 发短信/触达校验 |

## 青舟接口详情页

- [POST /lesson/prepare/relation/user/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4882733&appId=student-center&branchName=release)
- [POST /lesson/prepare/relation/user/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4882737&appId=student-center&branchName=release)
- [GET /lesson/prepare/attendance-remind/switch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2623715&appId=student-center&branchName=release)
- [POST /lesson/prepare/operate/validation](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159247&appId=student-center&branchName=release)
