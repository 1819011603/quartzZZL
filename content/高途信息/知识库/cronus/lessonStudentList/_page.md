# 课节学员（lessonStudentList）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/cronus/lessonStudentList` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 cronus（`/crm/micro-cronus`） |
| epic 路由 | `epic/src/routes.ts`：`/cronus/lessonStudentList`（`microApp: cronus`，`name: 课节学员`，`hideInMenu`） |
| cronus 路由 | `cronus/config/routes.js`：`/lessonStudentList` → `src/pages/lessonStudent/index.js` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |

## URL 参数与数据源切换

`src/pages/lessonStudent/index.js` 从 URL 读取：

- `ln`/`lessonNum` 课节号、`scn`/`subClazzNum`/`subclazzNumber` 辅导班号、`cn`/`clazzNum`/`clazzNumber` 班级号；
- **`sl=1`** → `lessonType='small'`（小灶课），否则 `'normal'`（大班课）；请求课节详情时对应 `lessonType: sl ? 2 : 1`（1 大班课 / 2 小灶课）；
- **`bs=<业务场景>`** → 决定激活哪个 tab（见下表），跳转方在 `filter` 里带上 `bs`（如 `bs=lessonAfterUser`）；
- 小灶课（`sl=1`）只展示 `default` 场景，不展示业务场景 tab（`bigClazzLeson=false`）。

## tab 列表

`src/pages/lessonStudent/components/BusinessScene/index.js` 的 `businessSceneEnum`（`bs` 合法值，无/非法回退 `default`）：

| bs | 中文名 | 组件 | 文档 |
|---|---|---|---|
| `default` | 默认 | `./Default` | [default.md](./default.md) |
| `prepareUser` | 课前准备 | `./LessonPrepare` | [prepareUser.md](./prepareUser.md) |
| `lessonAfterUser` | 课后督学 | `./LessonAfter` | [lessonAfterUser.md](./lessonAfterUser.md) |
| `emLessonAfterUser` | 课后督学（EM） | `./EmLessonAfter` | [emLessonAfterUser.md](./emLessonAfterUser.md) |
| `prepareRelationLessonUser` | 关联课节 | `./RelatedLesson` | [prepareRelationLessonUser.md](./prepareRelationLessonUser.md) |

## 页面级接口（所有 tab 共用）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/切换课节 | `getLesson` | `/bgwApi/component/student-center/lesson/excerpt` | `src/services/studentLessonPrepare.js:26`（调用 `src/pages/lessonStudent/index.js:31`） | student-center | `/lesson/excerpt` | [POST]/excerpt [980556] | 顶部课节下拉/名称 |
| 进页面 | `lessonPrepareGrayService` | `/component/student-center/lesson/prepare/gray` | `src/pages/lessonStudent/grayscale/index.js:12` | student-center | `/lesson/prepare/gray` | [POST]/gray [980560] | 课前准备 tab 是否展示 |
| 进页面 | `lessonAfterGrayService` | `/component/student-center/lesson/after/gray` | `src/pages/lessonStudent/grayscale/index.js:26` | student-center | `/lesson/after/gray` | 灰度 [1159240] | 课后督学 tab 是否展示 |
| 进页面 | `relationLessonGrayService` | `/component/student-center/lesson/prepare/relation/gray` | `src/pages/lessonStudent/grayscale/index.js:39` | student-center | `/lesson/prepare/relation/gray` | 关联课节 tab 灰度（复用课前准备灰度字段，额外返回 relationLesson）[4882732] | 关联课节 tab 是否展示 |
| tab 角标（60s 轮询） | `getCount` | `/bgwApi/component/student-center/lesson/prepare/user/scene/count` | `src/services/studentLessonPrepare.js:64`（调用 `.../components/BusinessScene/index.js:102`） | student-center | `/lesson/prepare/user/scene/count` | [POST]/user/scene/count [980557] | 各业务场景 tab 数量角标 |
| 切换课节下拉搜索 | `getFilterLessonList` | `/component/student-center/filter/lesson/list` | `src/services/lesson.js:16`（调用 `.../components/Nav/LessonSelect/index.js:21`） | student-center | `/filter/lesson/list` | [POST]/lesson/list [1453277] | 顶部课节选择器 |
| 行内编辑保存（各 tab 共用） | `updateList` | `/bgwApi/component/student-center/lesson/prepare/user/edit` | `src/services/studentLessonPrepare.js:56` | student-center | `/lesson/prepare/user/edit` | [POST]/user/edit [980545] | 保存单元格修改（各 tab 各自的 `identification`） |
| hover 触达记录（跨 tab 自定义列） | `getReachRecords` | `/component/student-center/lesson/after/reach/record` | `src/services/lessonAfterUser.js:34`（调用 `.../custom/render/ReachRecordsPopList/index.js:33`） | student-center | `/lesson/after/reach/record` | [POST]/reach/record [1159254] | 触达记录悬浮 |
| hover 听课进度条（跨 tab 自定义列） | `getRecentListenSituation` | `/component/student-center/studentClazz/recentLessonSituation` | `src/services/clazzRosterOL.js:51`（调用 `.../custom/render/ListenSituationProcess/PopoverContent/index.js:28`） | student-center | `/studentClazz/recentLessonSituation` | 获取学员最近看课进度条 [30675] | 听课情况进度条悬浮 |

## 共享组件

> 共享组件（`@/components/TableRender`、`@/components/StudentProfile`、`@/components/StudentFile`、`@/components/WrongBook`、`@/components/DownLoadCorrections`、`@/components/BatchActionBar`、`@/components/OperateButton`、`@/components/ForLeave`、`@/components/Actions/component/Attendance`、`@/components/Actions/component/SendLessonReportNew`、`@gaotu/reach-widget`、`@coeus/render` schema、联邦组件 `mf_iris` 的 `CallPhone`/`Duanxin` 等）另有接口，被多页面复用，待单独归档。
