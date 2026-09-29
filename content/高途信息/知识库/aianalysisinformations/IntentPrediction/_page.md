# 学员详情页 · AI 分析 tab（GAIA 微组件 AiAnalysisInformations）— 页面级

## 定位

| 项 | 值 |
|---|---|
| 挂载方式 | GAIA 微组件（不是独立路由页面），由宿主页（如 `cronus/clazzRosterOL` 点开学员详情抽屉）通过 `gaiaCenter/widget/detail` 动态加载 |
| 组件名 | `AiAnalysisInformations`（GAIA 展示名"AI 分析"） |
| 组件仓库 | `aianalysisinformations` `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/gaia-widget-submodule/aianalysisinformations` |
| GAIA projectId | `14312` |
| 组件加载地址（test） | `https://gtoss.gsxcdn.com/gaia-widget/test/<version>/AiAnalysisInformations.js`（无泳道概念，test/prod 各一份共享构建，不按 eco-N 隔离） |
| 如何确认当前挂的是哪个版本 | `POST /bgwApi/component/gaia-center/widget/detail` body `{"name":"AiAnalysisInformations"}`，返回 `currentVersion` + `url` |
| 如何找到对应源码分支 | 查该仓库 `package.json` 的 `version` 字段，跟 `currentVersion` 对上的分支就是当前线上代码（2026-09-29 实测：`feature-refund-reason-20260825` 分支 `0.0.54-alpha.1` 与线上一致） |

## 子模块（本组件内的 tab-in-tab）

| 目录 | 说明 |
|---|---|
| `src/components/IntentPrediction/` | 续班/退费"意向预测"：分层变化趋势图（`LevelTrendChart`）+ 分层原因卡（`FactorCard`），2026-09 新增，见本文件 |
| `src/tabs/renewal/` | 续班分析（沟通记录 `Components/Communication`、续班归因 `Components/RenewalReason` 等） |
| `src/tabs/refund/` | 退费分析（状态项 `Components/StateItems` 等；`Components/RootCause` 已在本分支删除下线） |

## 接口清单：IntentPrediction（意向预测/分层变化）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 说明 |
|---|---|---|---|---|---|---|
| 进 tab | `fetchPredictLevelReason` | `/bgwApi/component/student-center/ai/clazzUser/predictLevelReason` | `src/components/IntentPrediction/service.ts` | student-center → Feign 转发 student-data `/feign/predict/levelReason` | `/ai/clazzUser/predictLevelReason` | 首屏拿趋势图全部变化点 + 最近一次原因卡 |
| hover 历史节点 | `fetchPredictLevelReason`（带 `recordDt`） | 同上 | 同上 | 同上 | 同上 | 传 `recordDt`（毫秒时间戳，取自趋势图节点）查那一天的原因卡 |

- 请求体：`{scene, userId, clazzNumber, subclazzNumber, recordDt?}`；`scene` 1=续班 2=退费，同一接口两个场景共用，靠 `scene` 分流。
- 前端字段契约（`types.ts`）与后端 DTO（`student-data` `LevelReasonFactorDTO`/`PredictLevelReasonResponse`）**逐字段对齐**：`factorName`/`featureCode`/`category`/`importance` 是前端声明但故意不展示/选填的字段，后端不发送也不影响渲染（详见前端 `service.ts` 注释）。
- **2026-09-29 实测状态**：真实登录用户（无自定义 `traffic-env` 头）访问该接口返回 **404**——不是前端问题，是后端 `student-data`/`student-center` 该功能分支只发布在测试泳道 `test-eco-2`，release/base 池还没有这个 Controller 方法。要联调必须显式带 `traffic-env: test-eco-2` 走 `test-fuwu.baijia.com/bgwApi/student-center/...`（不经过 `component` 前缀那条真实前端路径）。

## 排查提示

- **AI 分析 tab 打开后续班/退费预测卡片不显示 / 报错** → 先看 `/ai/clazzUser/predictLevelReason` 是不是 404（大概率是后端功能分支没发布到当前访问的泳道，不是前端 bug）。
- **卡片显示但因子内容少一项** → 后端 `reason` 为空的因子整条丢弃（PRD 既定行为），不是前端漏渲染。
- **想确认线上/测试当前跑的是哪版代码** → 查 `gaia-center/widget/detail` 返回的 `currentVersion`，去仓库对应 tag/分支的 `package.json` 核对。

## 关联需求归档

- [续班退费分层变化和原因](../../../需求/续班退费分层变化和原因/README.md)
