# 小班课花名册（microClazzRoster）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/cronus/microClazzRoster` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 cronus（`/crm/micro-cronus`） |
| epic 路由 | `epic/src/routes.ts`：`/cronus/microClazzRoster`（`microApp: cronus`，`name: 小班课花名册`） |
| cronus 路由 | `cronus/config/routes.js`：`/microClazzRoster` → `src/pages/microClazzRoster/index.jsx` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |

## tab 列表

`src/pages/microClazzRoster/index.jsx` 读 URL `tabKey`（合法值 `default | continuationService`，无/非法回退 `default`）：

| tabKey | 中文名 | 组件 | 文档 |
|---|---|---|---|
| `default` | 花名册 | `./DefaultRoster` | [default.md](./default.md) |
| `continuationService` | 续班服务 | `./ContinuationService` | [continuationService.md](./continuationService.md) |

## 页面级接口

无。`src/pages/microClazzRoster/index.jsx` 仅做 tab 切换、`tabKey` 回写 URL 与埋点上报（`habo` / `useFmpReport`），不发起后端业务请求；表格 schema 与列表数据均由各 tab 组件自行加载。
