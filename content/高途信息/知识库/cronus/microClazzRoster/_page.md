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

## 关键点（直调复现）

- 两个 tab 的列表接口都在 **student-center**（网关前缀 `/bgwApi/component/student-center`）：花名册 `/smallClazz/clazzStudentList`、续班服务 `/roster/small/renewal/page`。
- 直调**必带请求头 `b_client`**（本页在 **EES 端** → `b_client: EES`）：缺头 → `{"code":42,"msg":"调用staff失败"}`（`SmallClazzUserPermissionFilterService` 走 staff 权限查询）。
- 页面**按登录老师权限过滤** → 复现前必须先 `cosplay_login` 成该二讲/主讲，否则只出本人可见数据（常见 0 条）。
- 必带 `route.sceneVersionNumber`（决定可见字段），否则返回字段为空。

## 注意点

- **`b_client` 不是固定值**：随页面所属端变化——**EES 页面（小班课花名册 / 续班服务）= `EES`**，GPS 页面（prism 我的班级等）= `GPS`。`LoginInfoFilter` 只对 `/gps`、`/node-instance` 前缀自动兜底 `GPS`，`/smallClazz`、`/roster` 不在其中，**必须手动带**。⚠️ 曾因本文档写死 `B_client: GPS` 而在 EES 页直调报 42，已按线上真实请求改为 `EES`。
- 环境：线上 host `fuwu.baijia.com`（`traffic-env: prod`），测试 `test-fuwu.baijia.com`。
- `invoke_http` 工具目前**不支持自定义请求头**，直调这些页面接口要用代理 curl 带 `-H 'b_client: EES'`（见各 tab 文档的复现模板）。
