# AI 分析 / 意向预测（分层变化趋势图 + 分层原因卡）

跨 tab 共用子模块，续班（`renewal`）、退费（`refund`）两个 tab 都挂载，只差 `scene` 常量。页面级信息见 [_page.md](./_page.md)。

## 定位

| 项 | 值 |
|---|---|
| 前端代码位置 | `src/components/IntentPrediction/`（`LevelTrendChart` 趋势图 + `FactorCard` 原因卡） |
| 挂载位置 | 续班 tab：`src/tabs/renewal/index.tsx`；退费 tab：`src/tabs/refund/index.tsx`（`useIntentPrediction({scene, userId, clazzNumber, subclazzNumber})`） |
| 后端服务 | student-center → 转发 student-data `/feign/predict/levelReason` |

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端 path | 说明 |
|---|---|---|---|---|---|
| 进 tab | `fetchPredictLevelReason` | `/bgwApi/component/student-center/ai/clazzUser/predictLevelReason` | `service.ts` | `/ai/clazzUser/predictLevelReason` | 首屏拿趋势图全部变化点 + 最近一次原因卡 |
| hover 历史节点 | `fetchPredictLevelReason`（带 `recordDt`） | 同上 | 同上 | 同上 | 传 `recordDt`（毫秒时间戳，取自趋势图节点）查那一天的原因卡 |

- 请求体：`{scene, userId, clazzNumber, subclazzNumber, recordDt?}`；`scene` 1=续班 2=退费，同一接口两个场景共用，靠 `scene` 分流。
- 前端字段契约（`types.ts`）与后端 DTO（`student-data` `LevelReasonFactorDTO`/`PredictLevelReasonResponse`）**逐字段对齐**：`factorName`/`featureCode`/`category`/`importance` 是前端声明但故意不展示/选填的字段，后端不发送也不影响渲染（详见前端 `service.ts` 注释）。
- **失败即不挂载**：`adaptInitialView` 返回 `null`（请求失败，或趋势图一个点都没有）时整个模块不渲染，**不是空态、是彻底消失**——跟本目录其它模块"接口失败=兜底文案"的表现不一样，排查时别混淆。

## 已知问题（2026-09-29）

真实登录用户访问该接口返回 **404**。用 `qingzhou-observe` 的 `trace_tree` 查过完整调用链（网关 → teacher-tool 代课鉴权 → student-center），**每一跳 `trafficMarker` 都是 `"default"`**，证实请求走的是 release/base 池，不是任何测试泳道——GAIA 前端没有泳道概念（见 [_page.md](./_page.md)），但它转发到的 student-center 后端是有泳道的，这条功能分支的后端代码目前只发布在 `test-eco-2`，release 池还没有这个 Controller 方法。

要在真实浏览器里联调通，唯一办法是后端分支合并发布到 release 池；手工 curl 可以加 `traffic-env: test-eco-2` 头强制指定泳道，但真实浏览器请求不会自动带这个头。

## 排查提示

- **AI 分析 tab 打开后续班/退费预测卡片整块不显示** → 先看 `/ai/clazzUser/predictLevelReason` 是不是 404 或无数据（模块设计成失败就不挂载，页面上完全看不出痕迹）
- **卡片显示但因子内容少一项** → 后端 `reason`（对应前端 `judgeReason`）为空的因子整条丢弃（PRD 既定行为），不是前端漏渲染
- **想确认线上/测试当前跑的是哪版代码** → 查 `gaia-center/widget/detail` 返回的 `currentVersion`，去仓库对应分支的 `package.json` 核对

## 关联需求归档

- [续班退费分层变化和原因](../../需求/续班退费分层变化和原因/README.md)
