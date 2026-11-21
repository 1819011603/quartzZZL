# GPS首call任务 · 完成标志里「学员备注」保存了还是未完成

> **只解决**：任务详情弹窗「完成任务标志」里学员备注（或学习情况等字段项）一直是灰的，老师反馈"重新编辑保存过了还是未完成"。
> 「任务没生成/查不到」走 [`1v1首call任务没生成或查不到.md`](1v1首call任务没生成或查不到.md)，与本文无关。

## 完成标志是什么

- 弹窗里的每一项 = fairy `platform_subtask` 表的一行（UI 经 `MyTaskServiceImpl` 读 DB，不是读 ES）。
- 子任务由任务规则配置生成：`first_call_task.task_rule_config`（JSON）里 `taskFinishCondition.requiredFieldList`，如 `["studentName","gender","grade","studentRemark"]` + 通话规则。**转班/换班后新班命中另一条规则，完成项列表就会变多**（如规则 15 要求姓名/性别/年级/学员备注+通话）。
- 字段编码见 fairy `RequiredFieldEnum`：studentRemark=学员备注、subjectScore=学习情况、phoneCall=电话沟通。

## 「学员备注」完成判定口径（fairy `TaskBizService#getTaskEffectiveField`）

查 fairy 库（cluster `gaotu-crm-prod` / cluster_id 211 / db `gaotu`）`student_communicate_comment_record`：

- 条件：`user_id = 学员 AND account_id = 任务老师 AND comment_type = 0 AND isdel = 0`，任一条 comment 非空即完成。
- `comment_type` 枚举（fairy `CommunicateCommentType`）：**0=备注(REMARK，唯一算完成)**、1=沟通(CONNECT)、2=寄语(LETTER)。
- **按 (学员, 老师) 维度**：老辅导班链路 accountId 取当前辅导班班主任解析出的 accountId（即任务 account_id）；1v1 容器链路取任务 accountId。换了老师/班级，旧老师名下的备注不算数。
- 老链路（首call）**不限保存时间**；只有日常回访（task_generate_rule_type=日常回访）才过滤任务窗口。时间窗口影响的是主任务「按期/过期完成」，不是备注字段本身。

## 为什么"保存了还是未完成"（本次实锤根因）

老师保存的入口不同，落库的 `comment_type` 不同：

| 保存入口 | 落库 comment_type | 算不算学员备注完成 |
|---|---|---|
| 任务抽屉/学情保存里的**学员备注字段**（走 MDM `/studentRemark/edit`，`StudentRemarkServiceImpl.saveStudentRemark` 写 type=0，保存后发 `FROM_COMMENT_DONE` 事件刷新子任务+ES） | 0 | ✅ |
| 学情页/**通话摘要**等「沟通记录」框（`LearnSituationServiceImpl#createOrUpdateStudentCommunicateCommentRecord`） | 1 | ❌ 永远不算 |

所以"重新编辑保存过了还是灰的"第一优先查：**保存的是不是沟通记录框**。

## 排查 SQL（prod，cluster 211）

```sql
-- 1. 任务与规则（看 requiredFieldList 里有没有 studentRemark）
SELECT task_code, subclazz_number, user_id, account_id, first_call_status, start_time, expired_time, task_rule_config
FROM gaotu.first_call_task WHERE user_id = <userId> ORDER BY create_time DESC;

-- 2. 子任务当前状态（弹窗数据源；studentRemark=1 即页面显示未完成）
SELECT field_key, task_status, finished_time, update_time FROM gaotu.platform_subtask
WHERE task_code = '<taskCode>';

-- 3. 判定数据：该 (学员, 任务account_id) 名下有没有 type=0 非空备注（没有=必然未完成，不是bug）
SELECT id, account_id, comment_type, LEFT(comment,40), channel, isdel, create_time
FROM gaotu.student_communicate_comment_record
WHERE user_id = <userId> AND create_time >= '<任务开始前一天>' ORDER BY create_time DESC;
```

- 第 3 步只有 `comment_type=1` → 根因即「保存的是沟通记录」。让老师在**学员备注字段**里填写保存即可（必须以任务老师本人账号操作，写进 account_id=任务 account_id）。
- 有 `comment_type=0` 但子任务还是灰 → 看 `platform_subtask.update_time` 是否停留在创建时刻（刷新滞后），触发实时刷新：打开任务列表页会走 `checkFirstCallStatusNew` 对比并触发 `firstCallStatusUpdate`，或查 fairy 日志 `checkFirstCallStatusNew 状态不一致触发更新`。
- 注意子任务可能正常、主任务因过期被置「过期未完成」——字段亮了也不改过期事实。

## 已知原因与判据

| 现象 | 根因 | 判据 |
|---|---|---|
| 反复保存还是灰 | 保存的是沟通记录（comment_type=1），完成判定只认 type=0 | `student_communicate_comment_record` 该 (user, task.account_id) 只有 type=1 |
| 转班后完成项突然变多 | 新班命中另一条任务规则（requiredFieldList 更多） | `first_call_task.task_rule_config` 对比新旧任务 |
| 换了班主任后备注不算 | 判定按 (学员， 任务老师) 维度，旧老师备注不迁移 | type=0 记录的 account_id ≠ 任务 account_id |
| 子任务灰但数据齐 | 状态刷新滞后（无人打开页面/事件丢失） | `platform_subtask.update_time` 停在创建时刻；实时口径已是完成 |
