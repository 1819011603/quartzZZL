# AI 分析 / 续班（tabKey=renewal）

## 定位

| 项 | 值 |
|---|---|
| 前端仓库 | aianalysisinformations |
| tab 组件 | `src/tabs/renewal/index.tsx` |
| 后端主服务 | student-center（网关前缀 `component/student-center`） |

> 页面级（灰度/needAnalyze/activated）见 [_page.md](./_page.md)。意向预测子模块见 [intentPrediction.md](./intentPrediction.md)。

## 接口清单

### 1. 续班用户画像

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 进 tab | `useUserSchema` | `/component/student-center/ai/clazzUser/userPortrait` | `hooks/useData.tsx:22`，组件 `src/components/UserSchema/index.tsx` | **没有整体空态**：后端返回 `{}` 时会渲染出一屏 `--`/"暂无…"（兜底文案总有值）；`summaryItems` 上限 6 项 |
| 标题栏评价 | — | `/component/student-center/ai/clazzUser/teacherEvaluate` | `UserSchema/TitleBar` | 默认接口，非本次重点 |

### 2. 沟通概况

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 进 tab | `useCommunication` | `/component/student-center/ai/clazzUser/commSummary` | `hooks/useData.tsx:88`，组件 `src/tabs/renewal/Components/Communication/index.tsx` | 前端按固定 4 个 tab（续班沟通/二讲日常沟通/二讲首call/顾问沟通）去后端 `commList` 里 find，找不到就占位「暂无此类沟通」；空态判断恒为 false，卡片级空态不出现 |

字段单位换算（`useData.tsx:118-138`）：`commSumTime` 秒→分钟；`commLatestTime` 毫秒时间戳→`YYYY-MM-DD HH:mm`；`commCount`→`N 次`。

### 3. 建议 & 评分（沟通 / 服务，同一组件两套接口）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 进 tab | `useSuggestionScore` | `/component/student-center/problem/fulfillProblem/overview` | `hooks/useData.tsx` | 沟通建议 & 评分：`solvedProblemList`/`highFrequencyProblemList`/`unSolveProblemList` |
| 进 tab | `useServiceScore` | `/component/student-center/fulfillSop/overview` | `hooks/useData.tsx:200-206` | 服务建议 & 评分：`completedSopList`/`uncompletedSopList` + `lastRefreshSopTimeMs`；前端做字段重命名 `sopMap`（`sopName`→`problemDescribe`，`sopDescription`→`communicationAdvice`） |

空态判断：三个建议列表全空 + `adviceCompleteStatusList` 全空 + `score` 为 0（注意 0 是 falsy，四个条件都满足才算空）。

### 4. 用户反馈 & 主管点评

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 进 tab | `useJudgement` | `/component/student-center/ai/clazzUser/evaluateQuery` | `hooks/useData.tsx:243`，组件 `src/components/Judgement/index.tsx` | **一个接口返回两个模块**：`userFeedbackList`（用户反馈，只读）+ `managerEvaluateList`（主管点评，可编辑） |
| 保存点评 | — | `/component/student-center/ai/clazzUser/managerEvaluate` | 同上 | 仅主管点评可写，最多 500 字，整卡替换编辑态 |

空态：`judgement.length > 0`（**唯一按预期生效的空态判断**）。

### 5. 分析等待（AnalyzeWaiting）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 首次进 tab | — | `/component/student-center/ai/renew/refreshSop` | `hooks/useRefreshSopPolling.tsx` | 触发后端跑分析 |
| 轮询（10s） | — | `/component/student-center/ai/renew/refreshSop/process` | 同上 | 返回 `{needShow, handleProcess:{handledStudentCount,totalStudentCount,remainTimeSeconds,studentStatus}}`；`needShow=false` 时触发刷新服务评分模块 |

### 6. 刷新按钮

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 点击刷新 | — | `/component/student-center/ai/renew/refreshAll` | `renewal/index.tsx:233-276` | 返回 `toastMessage` 则 toast 提示；仅 `activated` 时挂到 Tabs 右上角 |

## 排查提示

- **续班 tab 打不开/提示无法分析** → `ai/needAnalyze` 的 `hint`
- **画像一屏全是 `--`** → `ai/clazzUser/userPortrait` 返回是不是 `{}`（这是预期兜底，不是 bug）
- **沟通某个分类"暂无此类沟通"** → 后端 `commSummary` 的 `commList` 里没有对应 `type`
- **建议/评分不对** → 分别看 `problem/fulfillProblem/overview`（沟通）与 `fulfillSop/overview`（服务）
- **用户反馈/主管点评为空** → `ai/clazzUser/evaluateQuery` 返回两个 list 是否都是空
