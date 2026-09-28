# 一对一花名册（onebyOneRoster）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/cronus/onebyOneRoster` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 cronus（`/crm/micro-cronus`） |
| epic 路由 | `epic/src/routes.ts`：`/cronus/onebyOneRoster`（`microApp: cronus`，`name: 一对一花名册`） |
| cronus 路由 | `cronus/config/routes.js`：`/onebyOneRoster` → `src/pages/onebyOneRoster/index.jsx` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/筛选/翻页/排序 | `getOnebyOneRosterList` | `/component/student-center/gps/my-student/roster/list` | `src/pages/onebyOneRoster/services/onebyOneRoster.ts:16` | student-center | `/my-student/roster/list` | 一对一花名册 [4556725] | **主列表数据** |
| 姓名行内编辑保存 | `updateStudentName` | `/component/student-center/studentClazz/edit` | `src/pages/onebyOneRoster/services/onebyOneRoster.ts:41` | student-center | `/studentClazz/edit` | [POST]/edit [30662] | 场景 `onebyOneRoster`，`bizName=studentName` |
| 进页面 | `getSchema`（`@coeus/render`） | coeus 低代码 schema | `src/pages/onebyOneRoster/hooks/useTableSchema.js:13` | coeus/render | — | — | 拉表格列 / 筛选 schema（`identification=onebyOneRoster`） |

> 共享组件（`ConfigAbleComponents` / `UrgeClazz`→`@gaotu/reach-widget` / `StudentProfile` / `CallPhone` 等）另有接口，被多页面复用，待单独归档。

## 青舟接口详情页

- [POST /my-student/roster/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4556725&appId=student-center&branchName=release)
- [POST /studentClazz/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30662&appId=student-center&branchName=release)
