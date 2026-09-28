# 课节学员 / 课后督学（lessonStudentList · bs=lessonAfterUser）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonStudentList?ln=<课节号>&scn=<辅导班号>&cn=<班级号>&bs=lessonAfterUser` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lessonStudent/index.js` |
| tab 组件 | `src/pages/lessonStudent/LessonAfter/`（`./LessonAfter`） |
| 主 service 文件 | `src/services/lessonAfterUser.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（gray / scene count / 课节 / updateList / 自定义列）见 [_page.md](./_page.md)。仅大班课（`lessonType=normal`）展示。课节列表页「课后督学」tab 点击列会跳转到本 tab（`bs=lessonAfterUser`）。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页/排序 | `getLessonAfterUserPageList` | `/component/student-center/lesson/after/user/page` | `src/services/lessonAfterUser.js:4`（调用 `src/pages/lessonStudent/LessonAfter/index.js:154`） | student-center | `/lesson/after/user/page` | [POST]/user/page [1159245] | **主列表数据** |
| 总数超上限 | `getPager` | `/component/student-center/lesson/after/user/count` | `src/services/lessonAfterUser.js:11`（调用 `.../LessonAfter/index.js:189`） | student-center | `/lesson/after/user/count` | [POST]/user/count [1159243] | 单独取真实总数 |
| 课节数据卡片 | `getLessonAfterUserStatistic` | `/component/student-center/lesson/after/statistic` | `src/services/lessonAfterUser.js:19`（调用 `.../LessonAfter/components/DataStaticToolCard/index.js:109`） | student-center | `/lesson/after/statistic` | [POST]/statistic [1159250] | 有效听课率/练习提交率等 |
| 去批改 | `getCorrectionUrl` | `/component/student-center/lesson/after/correctionUrl` | `src/services/lessonAfterUser.js:27`（调用 `.../LessonAfter/components/CorrectBtn/index.js:18`） | student-center | `/lesson/after/correctionUrl` | [POST]/correctionUrl [1159244] | 打开批改端 |
| 触达/短信前置校验 | `getLessonAfterValidation` | `/component/student-center/lesson/after/operate/validation` | `src/services/lessonAfter.js:18`（调用 `.../LessonAfter/components/{ReachBusinessWithContext,ReachReport}/index.jsx`） | student-center | `/lesson/after/operate/validation` | [POST]/operate/validation [1159249] | 发短信/触达校验 |
| 发课节指南前置校验 | `getPlaybackGuideStatus` | `/component/student-center/clazz/lesson/getPlaybackGuideStatus` | `src/services/lessonList.js:21`（调用 `.../LessonAfter/components/ReachReport/index.jsx:41`） | student-center | `/clazz/lesson/getPlaybackGuideStatus` | 获取回放指南状态 [30652] | `reportCode=lesson_guide_config` 时校验 |

## 青舟接口详情页

- [POST /lesson/after/user/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159245&appId=student-center&branchName=release)
- [POST /lesson/after/user/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159243&appId=student-center&branchName=release)
- [POST /lesson/after/statistic](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159250&appId=student-center&branchName=release)
- [POST /lesson/after/correctionUrl](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159244&appId=student-center&branchName=release)
