# 课节管理 / 关联课节（lessonList · bs=prepareRelationLesson）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonList?bs=prepareRelationLesson` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lesson/index.js` |
| tab 组件 | `src/pages/lesson/RelatedLesson/`（`./RelatedLesson`） |
| 主 service 文件 | `src/services/lessonPrepare.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（gray / scene count）见 [_page.md](./_page.md)。仅大班课（`lessonType=normal`）展示。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页/排序 | `getRelationLessonPage` | `/bgwApi/component/student-center/lesson/prepare/relation/page` | `src/services/lessonPrepare.js:62`（调用 `src/pages/lesson/RelatedLesson/index.js:96`） | student-center | `/lesson/prepare/relation/page` | [POST]/relation/page [4882731] | **主列表数据**（课节维度） |
| 总数超上限 | `getRelationLessonCount` | `/bgwApi/component/student-center/lesson/prepare/relation/count` | `src/services/lessonPrepare.js:69`（调用 `.../RelatedLesson/index.js:124`） | student-center | `/lesson/prepare/relation/count` | [POST]/relation/count [4882730] | 精确总数兜底（课节维度） |
| 听课链接 | `getClazzUrl` | `/component/student-center/clazz/lesson/getCourseUrl` | `src/services/lessonPrepare.js:25`（调用 `.../RelatedLesson/components/ListenLessonLink/index.js:26`） | student-center | `/clazz/lesson/getCourseUrl` | 获取课节复制链接 [30650] | App/H5/小程序听课链接 |

## 青舟接口详情页

- [POST /lesson/prepare/relation/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4882731&appId=student-center&branchName=release)
- [POST /lesson/prepare/relation/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4882730&appId=student-center&branchName=release)
- [POST /clazz/lesson/getCourseUrl](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30650&appId=student-center&branchName=release)
