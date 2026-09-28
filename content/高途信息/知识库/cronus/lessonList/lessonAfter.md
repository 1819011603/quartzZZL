# 课节管理 / 课后督学（lessonList · bs=lessonAfter）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonList?bs=lessonAfter` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lesson/index.js` |
| tab 组件 | `src/pages/lesson/LeesonAfter/`（`./LeesonAfter`） |
| 主 service 文件 | `src/services/lessonAfter.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（gray / scene count）见 [_page.md](./_page.md)。仅大班课（`lessonType=normal`）展示。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页/排序 | `getLessonAfterPageList` | `/component/student-center/lesson/after/page` | `src/services/lessonAfter.js:3`（调用 `src/pages/lesson/LeesonAfter/index.js:195`） | student-center | `/lesson/after/page` | [POST]/page [1159242] | **主列表数据** |
| 总数超上限 | `getPager` | `/component/student-center/lesson/after/count` | `src/services/lessonAfter.js:10`（调用 `.../LeesonAfter/index.js:223`） | student-center | `/lesson/after/count` | [POST]/count [1159241] | 单独取真实总数 |
| 发短信前置校验 | `getLessonAfterValidation` | `/component/student-center/lesson/after/operate/validation` | `src/services/lessonAfter.js:18`（调用 `.../LeesonAfter/components/Sms/index.js:21`） | student-center | `/lesson/after/operate/validation` | [POST]/operate/validation [1159249] | 发催回放/催回放校验 |
| 发课节指南前置校验 | `getPlaybackGuideStatus` | `/component/student-center/clazz/lesson/getPlaybackGuideStatus` | `src/services/lessonList.js:21`（调用 `.../LeesonAfter/components/SendLessonGuide/index.jsx:34`） | student-center | `/clazz/lesson/getPlaybackGuideStatus` | 获取回放指南状态 [30652] | 校验课节指南是否已生成 |
| 点击列跳转学员列表 | `getJumpParams` | `/component/student-center/lesson/prepare/jump` | `src/services/lessonPrepare.js:17`（调用 `.../LeesonAfter/hooks/useCustomEventDom.js:21`） | student-center | `/lesson/prepare/jump` | [POST]/jump [980564] | 生成跳转 `/lessonStudentList?bs=lessonAfterUser` 的 filter |

## 青舟接口详情页

- [POST /lesson/after/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159242&appId=student-center&branchName=release)
- [POST /lesson/after/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159241&appId=student-center&branchName=release)
- [POST /lesson/after/operate/validation](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159249&appId=student-center&branchName=release)
- [POST /clazz/lesson/getPlaybackGuideStatus](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30652&appId=student-center&branchName=release)
