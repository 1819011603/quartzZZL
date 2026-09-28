# 课节管理（lessonList）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/cronus/lessonList` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 cronus（`/crm/micro-cronus`） |
| epic 路由 | `epic/src/routes.ts`：`/cronus/lessonList`（`microApp: cronus`，`name: 课节管理`，`access: menu_fairy_course`） |
| cronus 路由 | `cronus/config/routes.js`：`/lessonList` → `src/pages/lesson/index.js` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |

## tab 列表

`src/pages/lesson/index.js` 读 URL 参数 `bs`（业务场景，合法值见 `components/BusinessScene/index.js` 的 `businessSceneEnum`；无/非法回退 `default`），另由 `lt`/`type` 决定课节类型（大班课 `normal` / 小灶课 `small`）：

| bs | 中文名 | 组件 | 文档 |
|---|---|---|---|
| `default` | 默认 | `./DefaultLessonList` | [default.md](./default.md) |
| `lessonprepare` | 课前准备 | `./LessonPrepare` | [lessonprepare.md](./lessonprepare.md) |
| `lessonAfter` | 课后督学 | `./LeesonAfter` | [lessonAfter.md](./lessonAfter.md) |
| `emLessonAfter` | 课后督学（EM） | `./EmLessonAfter` | [emLessonAfter.md](./emLessonAfter.md) |
| `prepareRelationLesson` | 关联课节 | `./RelatedLesson` | [prepareRelationLesson.md](./prepareRelationLesson.md) |

> `lessonAfter` 灰度未开而 `emLessonAfter` 已开时，`bs=lessonAfter` 会被改写为 `emLessonAfter`（见 `index.js:127`）。

## 页面级接口（所有 tab 共用）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | `lessonPrepareGrayService` | `/component/student-center/lesson/prepare/gray` | `src/pages/lesson/grayscale/index.js:11` | student-center | `/lesson/prepare/gray` | [POST]/gray [980560] | 课前准备 tab 是否展示 |
| 进页面 | `lessonAfterGrayService` | `/component/student-center/lesson/after/gray` | `src/pages/lesson/grayscale/index.js:25` | student-center | `/lesson/after/gray` | 灰度 [1159240] | 课后督学 tab 是否展示 |
| 进页面 | `relationLessonGrayService` | `/component/student-center/lesson/prepare/relation/gray` | `src/pages/lesson/grayscale/index.js:38` | student-center | `/lesson/prepare/relation/gray` | 关联课节 tab 灰度（复用课前准备灰度字段，额外返回 relationLesson）[4882732] | 关联课节 tab 是否展示 |
| tab 角标（60s 轮询） | `getCount` | `/bgwApi/component/student-center/lesson/prepare/scene/count` | `src/pages/lesson/components/BusinessScene/index.js:100`（service `src/services/lessonPrepare.js:31`） | student-center | `/lesson/prepare/scene/count` | [POST]/scene/count [980553] | 批量取各业务场景 tab 数量角标 |

## 共享组件

> 共享组件（`@/components/TableRender`、`@/components/LessonDetailDrawer`、`@/components/ReportModal`、`@/components/ClazzPeriodSearch`、`@/components/AccountNameFilter`、`@/components/PagerToolTip`、`@gaotu/reach-widget`、`@coeus/render` schema、联邦组件 `mf_iris` 的 `Duanxin`/`AutoStrategyDrawer` 等）另有接口，被多页面复用，待单独归档。
