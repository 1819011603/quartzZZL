# 2,621 个班为什么只出 1 个班的归因 · 2026-09-10

> 承接 [data-volume-2026-09-10.md](data-volume-2026-09-10.md) 的待确认项。
> 证据来源：prod SLS `app` 日志（窗口 2026-09-10 00:00~05:00）+ cluster 336 `ees_data`。

## 结论（三句话）

1. **今天班级 Job 一个学员都没投递出去。** 全天 `dispatchClazzUsers | dispatched` 日志
   **0 条**，2,621 个班全部在投递之前被两道班级级收窄挡掉。
2. **`handle_status=1` 不代表"分析过"**，只代表"这行处理完了"。被收窄掉的班也照样
   `markSuccess`，所以「2,621 全部处理成功」和「只有 1 个班有归因」并不矛盾。
3. **今天那 4 条归因不是 Job 产出的**，是老师打开花名册页面触发的单学员路径。

## 逐层核对结果

Job 的调用链是 `handleClazzTask` → `inScope`（班级属性）→ `inProduceWindow`（产出窗口）
→ `dispatchClazzUsers`（投递学员）。今天的实际拦截分布：

| 层 | 判据 | 今日结果 | 证据 |
|-|-|-|-|
| ① `inScope` 第一道 | `is_renew_user_clazz=0` 直接 reject | **75 个班**被挡 | DB 精确计数；日志 `inScope \| not renew user clazz` |
| ① `inScope` 其余 | 创建时间阈值 / 班级课程查不到 | **0 个班** | 这些 reject 日志今天一条都没有 |
| ① `needHandle` 过滤链 | 部门白名单/大班课/系列课/班名黑名单… | **0 个班**（Job 侧） | 见下「关于班名黑名单」 |
| ② `inProduceWindow` | **班级已结课** / **无后置课程** / 正式续班未开始 | **其余 2,546 个班**基本都挡在这里 | 日志 `inProduceWindow \| clazz ended` 与 `\| no post course` 大量出现，均来自 Job 线程 |
| ③ `dispatchClazzUsers` | 抢锁后投递 | **0 条 dispatched 日志** | 全天检索无 student-data 命中 |

**两个主要拦截原因（②这一层）**：
- `clazz ended` —— 班级正式课节已结束（`timeRangeForManagePage.endTime` < 当前时间）
- `no post course` —— 该课程没有绑后置课程，跑了也无处展示

这两条都是**代码里写明的预期行为**，不是 bug：
> 「窗口外跑出来的结果前端一律不展示，白烧模型额度，因此展开学员之前先按同一套口径挡一道」
> —— `RenewalReasonTaskService#handleClazzTask` 注释

9 月上旬秋季班已开课、大量春/暑班级结课，`clazz ended` 占比高符合业务节奏。

### 关于班名黑名单（修正之前的猜测）

[runbook.md](runbook.md) 里把「班名黑名单 `CommonRuleFilter`」列为首要怀疑，
**今天的数据不支持这个猜测**：Job 线程今天没有任何 `needHandle rejected by CommonRuleFilter` 日志。
日志里确实有大量 `CommonRuleFilter` + `department_not_in_whitelist` 的 reject，
但它们的 TID 是 `after-sales.*`、线程是 `http-nio-*`，属于**售后侧接口调用**，与本 Job 无关。
排查时务必按 **TID/线程** 区分，否则会把别的调用方的 reject 算到 Job 头上。

## 今天那 4 条归因的真实来源

班级 `556596222882912256`，4 个学员，12:03:50~12:04:18 集中产出。
同一时段日志显示老师在访问：

```
https://fuwu.baijia.com/crm/cronus/lessonStudentList?scn=35389283429646592&cn=556596222882912256
```

即**花名册页面触发的单学员归因路径**（不过 `inScope`/`inProduceWindow`），
与 01:00 的班级 Job 无关。这也解释了为什么该班在任务表里 09-10 那行是
`handle_status=1` 却没有对应的 Job 投递记录。

## 关于 08-28~09-02 那 15,081 行 `handle_status=0`

那几批（每天约 2,513 行）**从未被处理**：Job 只处理「当天创建」的记录
（`create-date-offset-days` 默认 0，且当天无数据时**不放宽到更早记录**，
注释写明是为了避免大数据延迟时把旧班重复分析一遍）。
所以那 1.5 万行是**设计上的历史遗留，不会自动补跑**，会永久停在 0。
要补跑得手动指定日期：Job 参数传 `20260902,500` 这种形式。

> 09-10 是这批任务里**第一次真正被处理**的一天，此前几批都因为没赶上当天窗口而搁置。

## 建议（未执行，待确认）

- [ ] **可观测性**：`processPendingTasksInBatches | finish` 目前只报 total/success/fail，
      建议补上「实际投递班级数 / 各拦截原因计数」，否则 `success: 2621` 会持续误导。
      现在要判断 Job 有没有真干活，只能去数 `dispatched` 日志。
- [ ] 确认 09-10 之前那 15,081 行是否需要按日期补跑，还是就此作废。
- [ ] 已续归因自 09-07 后无调用：结合「已续总结只在学员续班时触发」，
      需确认是没有新增续班，还是触发链路有问题。
