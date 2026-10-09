# 判单配置（newJudgeConfig）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu_yunfan_fe master 代码整理。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-yunfan/newJudgeConfig` |
| 基座 | OES ark → 子应用 app-yunfan（静态资源 `gtoss.gsxcdn.com/.../projects/gaotu_yunfan_fe/`，chunk `p__NewJudgeConfig`） |
| 前端仓库 | gaotu_yunfan_fe `http://git.baijia.com/gaotu-ctech/gaotu_yunfan_fe`（master，本地 `~/IdeaProjects/WebProject/gaotu_yunfan_fe`；青舟 serviceCode `baijia.gaotu.tech.fe-b.gaotu-fe-yunfan-web`） |
| 前端路由 | `config/routeConfig.js:263` → `src/pages/NewJudgeConfig/index.js`，wrapper `@/wrappers/clazzManage`，权限 `canNewJudgeConfig` |
| 后端服务 | 网关前缀 `/performance` → 青舟 appId `performance-attribution`（仓库 **performance-attribution**，`AttributionSettingController`） |

## tab 列表

| tab | 文件 | 组件 |
|---|---|---|
| 判单/分边开关 | [judgeOrderConfig.md](judgeOrderConfig.md) | `src/pages/JudgeOrderConfig/index.js` |
| 正价课续班配置 / 体验课续班配置 | [protectionPeriodConfig.md](protectionPeriodConfig.md) | `src/pages/NewJudgeConfig/UniversalPage.js`（pageType 1 / 2） |

tab 默认 key 是 `clazz`，不匹配任何 tab，antd 回退到第一个可见 tab（判单/分边开关）。哪些 tab 可见由权限标签决定：`canJudgeOrderConfig` / `canOriginPriceClazz` / `canDiscountClazz`。

## 页面级接口（wrapper clazzManage，进页面即调）

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 读/写 |
|---|---|---|---|---|---|
| 进页面 | `GET /course-center/b/common/dictionary/all` | `getDictionary` | `src/models/clazzManage.js:58`（`src/services/clazzManage.js:16`） | course-center | 读 |
| 进页面 | `GET /course-center/b/common/department/tree` | `getNewDepartment` | `src/models/clazzManage.js:58`（`src/services/clazzManage.js:29`） | course-center | 读 |
| 进页面 | `GET /course-center/b/common/category/tree` | `getNewTree` | `src/models/clazzManage.js:58`（`src/services/clazzManage.js:23`） | course-center | 读 |
| 进页面 | `GET /course-center/b/common/dictionary/allConfigurable` | `getDefaultCourseConfig` | `src/models/clazzManage.js:58`（`src/services/clazzManage.js:48`） | course-center | 读 |
