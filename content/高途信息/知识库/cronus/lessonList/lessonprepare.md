# 课节管理 / 课前准备（lessonList · bs=lessonprepare）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonList?bs=lessonprepare` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lesson/index.js` |
| tab 组件 | `src/pages/lesson/LessonPrepare/`（`./LessonPrepare`） |
| 主 service 文件 | `src/services/lessonPrepare.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（gray / scene count）见 [_page.md](./_page.md)。仅大班课（`lessonType=normal`）展示。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页/排序 | `getLessonPreparePage` | `/component/student-center/lesson/prepare/page` | `src/services/lessonPrepare.js:3`（调用 `src/pages/lesson/LessonPrepare/index.js:97`） | student-center | `/lesson/prepare/page` | [POST]/page [980558] | **主列表数据** |
| 总数超上限 | `getPager` | `/component/student-center/lesson/prepare/count` | `src/services/lessonPrepare.js:10`（调用 `.../LessonPrepare/index.js:125`） | student-center | `/lesson/prepare/count` | [POST]/count [980547] | 单独取真实总数 |
| 点击列跳转学员列表 | `getJumpParams` | `/component/student-center/lesson/prepare/jump` | `src/services/lessonPrepare.js:17`（调用 `.../LessonPrepare/hooks/useCustomEventDom.js:16`） | student-center | `/lesson/prepare/jump` | [POST]/jump [980564] | 生成跳转 `/lessonStudentList` 的 filter |
| 听课链接 | `getClazzUrl` | `/component/student-center/clazz/lesson/getCourseUrl` | `src/services/lessonPrepare.js:25`（调用 `.../LessonPrepare/components/ListenLessonLink/index.js:26`） | student-center | `/clazz/lesson/getCourseUrl` | 获取课节复制链接 [30650] | App/H5/小程序听课链接 |
| 发短信前置校验 | `getLessonBeforeValidation` | `/component/student-center/lesson/prepare/operate/validation` | `src/services/lessonPrepare.js:40`（调用 `.../LessonPrepare/components/BusinessSms/index.js:21`） | student-center | `/lesson/prepare/operate/validation` | [POST]/operate/validation [1159247] | 催到课/发出勤链接/催预习校验 |

## 青舟接口详情页

- [POST /lesson/prepare/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=980558&appId=student-center&branchName=release)
- [POST /lesson/prepare/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=980547&appId=student-center&branchName=release)
- [POST /lesson/prepare/jump](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=980564&appId=student-center&branchName=release)
- [POST /lesson/prepare/operate/validation](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159247&appId=student-center&branchName=release)
