# 课节管理 / 默认（lessonList · bs=default）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/lessonList?bs=default` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/lesson/index.js` |
| tab 组件 | `src/pages/lesson/DefaultLessonList/`（`./DefaultLessonList`） |
| 主 service 文件 | `src/pages/lesson/DefaultLessonList/components/FormalLesson/services.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级接口（gray / scene count）见 [_page.md](./_page.md)。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 列表/筛选/翻页（大班课） | `getFormalLessonData` | `/component/student-center/clazz/lesson/formal/list` | `src/pages/lesson/DefaultLessonList/components/FormalLesson/services.js:4` | student-center | `/clazz/lesson/formal/list` | 正式课节列表 [30645] | **大班课主列表** |
| 列表/筛选/翻页（小灶课） | `getSmallLessonData` | `/bgwApi/component/student-center/clazz/lesson/parentsMeeting/list` | `.../FormalLesson/services.js:11` | student-center | `/clazz/lesson/parentsMeeting/list` | 小灶课课节列表 [30646] | **小灶课主列表**（`isSmallLesson`） |
| 总数 | `getFormalLessonList` | `/component/student-center/clazz/lesson/formal/list/count` | `.../FormalLesson/services.js:33` | student-center | `/clazz/lesson/formal/list/count` | [POST]/formal/list/count [1033509] | 大班课总数兜底 |
| 总数（小灶课） | `getParentsMeetingList` | `/component/student-center/clazz/lesson/parentsMeeting/list/count` | `.../FormalLesson/services.js:40` | student-center | `/clazz/lesson/parentsMeeting/list/count` | [POST]/parentsMeeting/list/count [1033507] | 小灶课总数兜底 |
| 操作列-进教室 | `getLiveUrl` | `/component/student-center/clazz/lesson/getNewLiveUrl` | `.../FormalLesson/services.js:18` | student-center | `/clazz/lesson/getNewLiveUrl` | (新系统)获取进入教室链接 [49401] | 跳转直播客户端 |
| 操作列-听课链接 | `getClazzUrl` | `/component/student-center/clazz/lesson/getCourseUrl` | `.../FormalLesson/services.js:25` | student-center | `/clazz/lesson/getCourseUrl` | 获取课节复制链接 [30650] | App/H5/小程序听课链接 |
| 自动触达任务抽屉 | `getTaskList` | `/component/student-center/clazz/lesson/reach/task/list` | `.../FormalLesson/components/AutoTaskDrawer/services.js:4` | student-center | `/clazz/lesson/reach/task/list` | 正式课节列表 [30653] | 触达任务列表（当前 `AutoTaskDrawer` 已注释，改用联邦组件 `AutoStrategyDrawer`） |

## 青舟接口详情页

- [POST /clazz/lesson/formal/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30645&appId=student-center&branchName=release)
- [POST /clazz/lesson/parentsMeeting/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30646&appId=student-center&branchName=release)
- [POST /clazz/lesson/getNewLiveUrl](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=49401&appId=student-center&branchName=release)
- [POST /clazz/lesson/getCourseUrl](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30650&appId=student-center&branchName=release)
