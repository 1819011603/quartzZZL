# AI 分析 / 退费（tabKey=refund）

## 定位

| 项 | 值 |
|---|---|
| 前端仓库 | aianalysisinformations |
| tab 组件 | `src/tabs/refund/index.tsx` |
| 后端主服务 | student-center（网关前缀 `component/student-center`） |
| 入参 | `{userId, clazzNumber, subclazzNumber}`（比续班多传 `subclazzNumber`） |

> 页面级（灰度/needAnalyze/activated）见 [_page.md](./_page.md)。意向预测子模块见 [intentPrediction.md](./intentPrediction.md)。

## 接口清单

### 1. 退费分析（预测/手填退费意向）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 进 tab | `useUserSchema` | `/component/student-center/roster/refund/analysis` | `src/tabs/refund/hooks/useData.tsx` | 返回字段：`aiRefundIntent`/`aiRefundIntentDesc`（预测退费意向）、`refundIntent`/`refundIntentDesc`（手填）、`studentSubStatus`（学员辅导班状态）、`afterSaleStatus`（退款单状态）、`afterSaleNumber`+`clazzBizNumber`（售后单跳转）、`serviceSuggestion`（服务建议，空则「暂无服务建议」） |

### 2. 手填退费原因

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 进 tab | `useRefundReason` | `/component/student-center/roster/refund/reason` | 同上 | 返回 `refundReason` + `refundReasonSource`（1=AI 生成走 markdown 渲染，2=二讲编辑走纯文本） |
| 保存 | `updateRefundReason` | `/component/student-center/roster/refund/edit` | `src/tabs/refund/index.tsx` | body 含 `identification:'refundPrevention'`、`bizName:'refundReason'` |

### 3. 课程体验

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 进 tab | `useFeatures` | `/component/student-center/roster/refund/course` | `src/tabs/refund/hooks/useData.tsx` | 返回 `courseAttributes`（文案） |
| 查看学习数据（近半年） | `useRecentPerformance` | `/component/student-center/course/experience/statistics` | 同上 | 返回 `data.list[]`；有内存缓存（按 `userId-clazzNumber-subclazzNumber` 做 key，参数不变不重新请求） |

### 4. 退费沟通旅程

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 说明 |
|---|---|---|---|---|
| 进 tab | `getUserExperienceData` | `/bgwApi/component/student-center/roster/refund/stage` | `src/tabs/refund/Components/Istinerary/service.ts` | 情绪变化通话数据；`level` 后端 1~5，前端换算成 `6-level` 展示（值越大代表越高） |

### 5. 分析等待（AnalyzeWaiting，退费专用接口，跟续班不共用）

| 触发 | 前端调用路径 | 说明 |
|---|---|---|
| 首次进 tab | `/component/student-center/ai/refund/refreshSop` | 触发分析 |
| 轮询 | `/component/student-center/ai/refund/analysis/time` | 查进度 |

> 注意：跟续班侧的 `ai/renew/refreshSop`（`/process` 结尾）路径**不一样**，是两套接口。

## 本分支下线的内容

- `src/tabs/refund/Components/RootCause/`（AI 预测退费原因模块）已在 `feature-refund-reason-20260825` 分支删除下线，改由 [intentPrediction.md](./intentPrediction.md) 的分层原因卡承接。

## 排查提示

- **退费分析卡片全是 `--`** → `roster/refund/analysis` 返回是否为空（预期兜底，非 bug）
- **手填退费原因显示异常（markdown 渲染错乱）** → 看 `refundReasonSource` 是不是被后端写错
- **退费沟通旅程无内容** → `roster/refund/stage` 返回是否为空数组
