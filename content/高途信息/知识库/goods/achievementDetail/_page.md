# 业绩看板（achievementDetail）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-goodsmanage master 代码整理；后端对照 performance-attribution。

后端本地仓库当时停在分支 `feature-fix-judge-reason-scene-tiebreak`（`9c93fc7b8`），不是 master，行号可能和 master 有小偏差。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-goods/achievementDetail` |
| 基座 | OES ark → 子应用 app-goods（chunk `p__Achievement__index`） |
| 前端仓库 | gaotu-fe-goodsmanage `http://git.baijia.com/gaotu-ctech/gaotu-fe-goodsmanage`（master `7e4c4bc`，本地 `~/IdeaProjects/WebProject/gaotu-fe-goodsmanage`） |
| 前端路由 | `config/routes.js:279-286`「业绩看板」→ `src/pages/Achievement/index.tsx`，wrapper `@/wrappers/statistics`，权限 `canAchievementDetail`（`src/access.js:6`，tag `gaotu_goods_p_achievement_detail`） |
| 判单过程 | 同页抽屉 `src/pages/Achievement/ProcessDrawer/index.js` → `src/pages/Achievement/OrderProcess/index.js`（独立路由 `/achievementDetail/orderProcess/:orderNumber` 已注释，`config/routes.js:287-291`） |
| 后端服务 | 网关前缀 `/performance` → 青舟 appId `performance-attribution`（仓库 **performance-attribution**，`PerformanceKanbanCourseController` / `PerformanceKanbanPhysicalController` / `PerformanceStatisticsController`） |

前缀常量：`src/pages/Achievement/service/index.ts:4-7` `type` 仅 dev 为 `/bgwApi`，线上为空。

## tab 列表

| tab（key） | 文件 | 组件 |
|---|---|---|
| 订单明细（课程）[（运营）]（`set`，默认） | [course.md](course.md) | `src/pages/Achievement/AchieveDetail.tsx` + `SearchHeader/index.tsx` |
| 订单明细（商品）[（运营）]（`Physical`；OLS 叫「商品业绩」） | [physical.md](physical.md) | `src/pages/Achievement/Physical/index.tsx` |
| 业绩统计（`list`） | [statistics.md](statistics.md) | `src/pages/Achievement/statistics/index.tsx` |

tab 名后缀「（运营）」由 `gaotu_boss_p_clazz_detail_maintainer` / `gaotu_boss_p_physical_detail_maintainer`（OLS 为 `ols_opt_*_detail_maintainer`）决定（`index.tsx:18-30`），运营角色可查「无归属」业绩。

## 页面级接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（app 启动即初始化的全局 model） | `GET /intranet-rpc/course-setting/feign/options/bff/list?fields=all` | `getCommonDictionary` | `src/models/useBffSelectItem.js:11`（`src/services/goodsManage.js:13`） | course-setting | 共享字典 | 读 |
| 进页面（wrapper statistics，枚举为空） | `GET /performance/management/attributionType/list` | `getPerformanceTypeList` | `src/wrappers/statistics.js:13` → `src/models/statisticsEnum.js:7`（`src/pages/Achievement/service/index.ts:34`） | performance-attribution | 业绩类型/状态枚举 [37002] | 读 |
| 进课程 tab（SearchHeader mount） | `GET /course-setting/b/course/category/tree` | `getCategoryList` | `src/pages/Achievement/SearchHeader/index.tsx:154` → `src/models/useCategoryList.js:18`（`src/services/physicalGoods.js:13`） | course-setting | 共享字典（品类树） | 读 |
| 枚举返回后自动查 / 查询 / 翻页 | `POST /performance/management/attribution/list` | `getPerformanceList` | `src/pages/Achievement/AchieveDetail.tsx:89`（`service/index.ts:41`） | performance-attribution | 查询业绩 [36994] | 读 |

各 tab 内接口（导出、归属人搜索、判单过程、商品明细、业绩统计）见对应 tab 文件。

## 关键表（`gaotu_stat` 库）

| 表 | 含义 | 涉及接口 |
|---|---|---|
| `gaotu_stat.performance_order_attribution_total` | 课程订单业绩归属汇总（归属人邮箱前缀、业绩类型、交易状态/类型、课程/班级、交易时间） | `attribution/list`、`attribution/export`、`judge/reason/transfer`；业绩统计走 ADB 同名表 |
| `gaotu_stat.performance_physical_attribution` | 商品（实物等）业绩归属 | `attribution/physical/list`、`physical/export`、业绩统计 |
| `gaotu_stat.performance_attribution_judge_reason` | 判单过程记录 | `judge/result`、`judge/reason/*` |
| `gaotu_stat.performance_attribution_credentials` / `performance_physical_attribution_credentials` | 判单凭证 | `judge/result` |

`attributionType/list` 只返回代码枚举（`AttributionTypeEnum` / `AttributionStatusEnum`），不查表。所有 mapper XML 在 `performance-attribution-infrastructure/src/main/resources/mapper/gaotustat/`（MySQL 数据源 `GaotuStatDataSourceConfiguration`）；`mapper/analyticdb/` 是 ADB 数据源（`GaotuStatAdbDataSourceConfiguration`，key `jdbc.gaotu_stat.adb.*`）。不读 ES。

## 排查提示

- 业绩表查不到这单 / 归属人为空 / 排行榜为 0 / 判单没跑 → 先看工单案例库 [业绩归因](../../../工单/续班与业绩/业绩归因/README.md)（`查不到归属人.md`、`判单正常但排行榜显示0.md`、`判单开关溯源与回溯补数据.md`）
- 判单开关在 [判单配置](../../yunfan/newJudgeConfig/_page.md)
- 能看到哪些人的业绩：OES（header `B_client` 非 OLS，`bClient=1`）且 Apollo `permission.staff.switch=true`（默认）时走 staff 主岗下属邮箱前缀；否则走门神（menshen）部门树 + 品类权限，见 [course.md](course.md)

## 青舟接口详情页

- [GET /performance/management/attributionType/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37002&appId=performance-attribution&branchName=release) id=37002
- [POST /performance/management/attribution/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36994&appId=performance-attribution&branchName=release) id=36994
