# 小班课节学员（microLessonStudentList）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/cronus/microLessonStudentList?tln=<课节号>` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 cronus（`/crm/micro-cronus`） |
| epic 路由 | `epic/src/routes.ts`：`/cronus/microLessonStudentList`（`microApp: cronus`，`name: 小班课节学员`，`hideInMenu`，挂在 GPS 班课管理下） |
| cronus 路由 | `cronus/config/routes.js`：`/microLessonStudentList` → `src/pages/microLessonStudent/index.js` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |

## tab 列表

无 tab。`src/pages/microLessonStudent/index.js` 仅渲染单一 `default`（小班课）子组件，并读取 URL `tln`（课节名称，展示用）与 `tlnm`（标题）。

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | `getGrayService` | `/component/student-center/smallClazz/gray` | `src/pages/microLessonStudent/grayscale/index.js:11` | student-center | `/smallClazz/gray` | 判断灰度规则 [2044935] | 灰度开关（下发给 schema `auth`） |
| 列表/筛选/翻页/排序 | `getMicroLessonStudentList` | `/bgwApi/component/student-center/small-clazz/lesson/user/list` | `src/pages/microLessonStudent/Default/services.ts:43`（调用 `.../Default/index.js:111`） | student-center | `/small-clazz/lesson/user/list` | 小班课课节学员列表 [2044933] | **主列表数据** |
| 总数超上限 | `getListCount` | `/bgwApi/component/student-center/small-clazz/lesson/user/list/count` | `src/pages/microLessonStudent/Default/services.ts:50`（调用 `.../Default/index.js:64`） | student-center | `/small-clazz/lesson/user/list/count` | 小班课课节学员统计 [2044936] | 单独取真实总数 |
| 行内编辑保存 | `updateList` | `/component/student-center/studentClazz/edit` | `src/services/clazzRosterOL.js:41`（调用 `.../Default/index.js:289`） | student-center | `/studentClazz/edit` | [POST]/edit [30662] | 保存单元格修改（`scene=smallClazzRoster`） |
| hover 听课进度条 | `getSmallClazzLessonSituation` | `/bgwApi/component/student-center/smallClazz/lessonSituation` | `src/pages/microLessonStudent/Default/services.ts:227`（调用 `.../Default/components/ListenSituation/PopoverContent/index.js:28`） | student-center | `/smallClazz/lessonSituation` | 获取学员看课进度条 [2366331] | 听课情况进度条悬浮 |

## 共享组件

> 共享组件（`@coeus/render` schema / `getSchema`、`@/components/NavBack`、`@/components/PagerToolTip`、`@/pages/StudentProfile`、`@/pages/clazzRosterOnLine/components/ExamStatusFilter`、`ExamStatus`、`@/components/AttendanceProgressBar`、`@gaotu/reach-widget` 的 `CallPhone` 等）另有接口，被多页面复用，待单独归档。

## 青舟接口详情页

- [POST /smallClazz/gray](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044935&appId=student-center&branchName=release)
- [POST /small-clazz/lesson/user/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044933&appId=student-center&branchName=release)
- [POST /small-clazz/lesson/user/list/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044936&appId=student-center&branchName=release)
- [POST /studentClazz/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30662&appId=student-center&branchName=release)
- [POST /smallClazz/lessonSituation](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2366331&appId=student-center&branchName=release)
