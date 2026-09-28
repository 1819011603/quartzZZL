# 班级花名册（clazzRosterOL）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/cronus/clazzRosterOL` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 cronus（`/crm/micro-cronus`） |
| epic 路由 | `epic/src/routes.ts`：`/cronus/clazzRosterOL`（`microApp: cronus`，`name: 班级花名册`） |
| cronus 路由 | `cronus/config/routes.js`：`/clazzRosterOL` → `src/pages/roster/index.js` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |

## tab 列表

`src/pages/roster/index.js` 读 URL `tabKey`（合法值 `default | stageFeedback | refundPrevention | continuationService`，无/非法回退 `default`）：

| tabKey | 中文名 | 组件 | 文档 |
|---|---|---|---|
| `default` | 花名册 | `@/pages/clazzRosterOnLine` | 待补 |
| `stageFeedback` | 阶段反馈 | `./StageFeedback` | 待补 |
| `refundPrevention` | 退费管控 | `./RefundPrevention` | 待补 |
| `continuationService` | 续班服务 | `./ContinuationService`（灰度回退到 `./ContinuationServiceLegacy`） | [continuationService.md](./continuationService.md) |

## 页面级接口（所有 tab 共用，进页面即调）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | 内联 request | `/bgwApi/component/student-center/roster/renewal/config` | `src/pages/roster/index.js:21` | student-center | `/roster/renewal/config` | 续班配置 | 决定续班服务走新版还是 Legacy（`multiToSingleRollback`） |
| 进页面 | `getGrayService` | `/component/student-center/roster/gray` | `src/pages/roster/grayscale/index.js:13` | student-center | `/roster/gray` | 判断灰度逻辑 | 控制 tab（续班服务/退费管控）是否可见 |
| 进页面 | `getSchema`（`@coeus/render`） | coeus 低代码 schema | `src/models/continuationService.js` 等 | coeus/render | — | — | 拉表格列/筛选 schema |
