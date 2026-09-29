# 学员详情页 · AI 分析 tab（GAIA 微组件 AiAnalysisInformations）— 页面级

## 定位

| 项 | 值 |
|---|---|
| 挂载方式 | GAIA 微组件（不是独立路由页面），由宿主页（如 `cronus/clazzRosterOL` 点开学员详情抽屉）通过 `gaiaCenter/widget/detail` 动态加载 |
| 组件名 | `AiAnalysisInformations`（GAIA 展示名"AI 分析"） |
| 组件仓库 | `aianalysisinformations` `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/gaia-widget-submodule/aianalysisinformations` |
| GAIA projectId | `14312` |
| 组件加载地址（test） | `https://gtoss.gsxcdn.com/gaia-widget/test/<version>/AiAnalysisInformations.js`（**无泳道概念**，test/prod 各一份共享构建，CDN 上没有 `test-eco-N` 路径，谁最后跑 `gaia release` 谁就是全体测试用户看到的版本） |
| 如何确认当前挂的是哪个版本 | `POST /bgwApi/component/gaia-center/widget/detail` body `{"name":"AiAnalysisInformations"}`，返回 `currentVersion` + `url` |
| 如何找到对应源码分支 | 查该仓库 `package.json` 的 `version` 字段，跟 `currentVersion` 对上的分支就是当前线上代码 |
| 后端主服务 | student-center（网关前缀 `component/student-center`），部分模块转发到 student-data |

## Tab 列表

| tabKey | 中文名 | 组件 | 文档 |
|---|---|---|---|
| `new-enrollment` | 学情沟通 | — | 待补 |
| `renewal` | 续班 | `src/tabs/renewal` | [renewal.md](./renewal.md) |
| `refund` | 退费 | `src/tabs/refund` | [refund.md](./refund.md) |

跨 tab 共用子模块：

| 子模块 | 说明 | 文档 |
|---|---|---|
| `src/components/IntentPrediction/` | 意向预测：分层变化趋势图 + 分层原因卡，续班/退费共用一套组件，只差 `scene` 常量 | [intentPrediction.md](./intentPrediction.md) |

## 展示逻辑分层（决定"看不看得到"，来自仓库自带文档 `docs/续班Tab-现有展示逻辑梳理.md`）

```
页面级
├── 第 1 层  灰度 gray/merge     → 决定渲染哪几个 tab
├── 第 2 层  needAnalyze         → 决定该 tab 整体是否可用
└── 第 3 层  参数缺失            → 前端唯一自主判断（缺 userId/clazzNumber）

Tab 级
└── 第 4 层  activated           → 不控制显隐，只控制轮询/埋点/extraContent；
                                    非激活 tab 的数据请求**不受影响**，切到别的 tab 时原 tab 的接口照样在请求

模块级
└── 无显隐条件，各模块无条件渲染，只有组件内部空态兜底（各模块判空口径不一，见各 tab 文档）
```

### 第 1 层：灰度

| 项 | 内容 |
|---|---|
| 接口 | `POST /bgwApi/component/student-center/ai/gray/merge` |
| 前端位置 | `src/AiAnalysis.tsx:78-103` |
| 返回 | `Record<string, boolean>`，key 为 tab key |
| 全部不可见时 | 渲染 Empty「您所带班级不在试用范围…」 |

### 第 2 层：needAnalyze

| 项 | 内容 |
|---|---|
| 接口 | `POST /component/student-center/ai/needAnalyze`，入参 `{userId, clazzNumber}`（退费侧多传 `subclazzNumber`） |
| 返回 | `{needAnalyze: boolean, hint: string}` |
| 不通过 | 整个 tab 渲染 Empty，文案用后端 `hint`（兜底「对应班级无法分析」） |
| 请求失败 | **放行**（`needAnalyze` 缺省当 true），不是拦截 |

## 全局现状（影响所有接口的排查判断）

- **错误与空态前端不区分**：`src/utils/request.ts` 的 `handleResponse` 对 `code!==0` 只 `message.error` 不 reject，各 hook 又只写 `.finally` 没 `.catch` —— **加载中/无数据/请求失败三种状态界面表现完全一样**，都是兜底文案。**排查空白/异常必须直接看接口返回，不能只看页面。**
- 枚举与配置（沟通类型、tab key 映射等）写死在前端，后端加新值前端不感知。

## 排查提示

- **整个 tab 看不到内容** → 先查 `ai/gray/merge` 有没有把这个 tab key 标 true。
- **tab 能看到但报"无法分析"** → 查 `ai/needAnalyze` 的 `needAnalyze`/`hint`。
- **某个模块空/报错** → 接口失败和真的没数据表现一样，直接抓包看该模块对应接口返回什么（各模块接口见 [renewal.md](./renewal.md) / [refund.md](./refund.md)）。
- **AI 分析模块整块消失（不是空态，是完全不渲染）** → 特指 [intentPrediction.md](./intentPrediction.md) 这类"接口失败就不挂载"的模块，跟上面"空态"是两种表现，别混淆。

## 关联需求归档

- [续班退费分层变化和原因](../../需求/续班退费分层变化和原因/README.md)
