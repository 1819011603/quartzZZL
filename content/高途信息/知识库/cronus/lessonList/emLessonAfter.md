# 课节管理 / 课后督学（EM）（lessonList · bs=emLessonAfter）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonList?bs=emLessonAfter` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lesson/index.js` |
| tab 组件 | `src/pages/lesson/EmLessonAfter/`（`./EmLessonAfter`） |
| 主 service 文件 | `src/services/lessonAfter.js`（列表复用课后督学接口） |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（gray / scene count）见 [_page.md](./_page.md)。仅大班课（`lessonType=normal`）展示。列表接口与 `lessonAfter` tab 相同，仅 schema / 埋点不同。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页/排序 | `getLessonAfterPageList` | `/component/student-center/lesson/after/page` | `src/services/lessonAfter.js:3`（调用 `src/pages/lesson/EmLessonAfter/index.js:200`） | student-center | `/lesson/after/page` | [POST]/page [1159242] | **主列表数据** |
| 总数超上限 | `getPager` | `/component/student-center/lesson/after/count` | `src/services/lessonAfter.js:10`（调用 `.../EmLessonAfter/index.js:228`） | student-center | `/lesson/after/count` | [POST]/count [1159241] | 单独取真实总数 |

## 青舟接口详情页

- [POST /lesson/after/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159242&appId=student-center&branchName=release)
- [POST /lesson/after/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1159241&appId=student-center&branchName=release)
