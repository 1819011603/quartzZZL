# GPS首call任务 · 同老师/同班完成条件为什么会不一样（命中规则翻转）

> **只解决**：同一个班主任，不同批次生成的首call任务「完成条件」列表不一样（有的要资料四项+电话，有的只要电话）；转班/换班主任后要求突然变多或变少。
> 「学员备注保存了还是灰」走 [`首call完成标志学员备注未完成.md`](首call完成标志学员备注未完成.md)，与本文无关。

## 规则匹配机制（fairy 任务平台）

- 任务生成时**按班主任本人**匹配规则（`TaskRuleConfigBizServiceImpl#listMatchedRuleByAccountId`），不是按学员/班级。命中的规则 JSON 快照存在任务上（`first_call_task.task_rule_config`），之后规则改了也不影响已生成任务。
- 匹配两层（`isStaffMatchConfig`）：
  1. **虚拟组织架构**：取老师组织路径（从根节点 12345 展开的完整路径），与规则 `org_numbers` 有交集即命中；
  2. **角色标签**（可选）：规则配了 `role_labels`（如 `4-216` = 标签组4下的216号「二讲」）时，老师必须有该标签才算命中。
- 多条规则都命中时（`selectConfigByOrgProximity`）：**命中的组织节点在路径里更深（更靠近老师）的规则胜出；深度相同取 createTime 更早的规则**。因此勾在公司级大节点的规则是"兜底"，勾在老师所在小部门的规则会优先。

## 典型翻转场景（2026-11 实锤案例）

老师杨莹丹（accountId 184974）：

| 时间 | 角色标签 | 命中规则 | 完成条件 |
|---|---|---|---|
| 11-20 19:15 批次 | 学习顾问（无216） | 规则15「高途大班课首call规则」（勾在高途节点，无标签要求） | 姓名/性别/年级/学员备注/学习情况 + 通话1分钟 |
| 11-21 14:41 起 | 二讲（4-216 已授予） | 规则5「一对一二讲首call」（勾在班主任部 + 标签4-216，就近度更深） | 仅电话沟通10分钟 |

**规则配置本身没改**（rule5 update_time 2026-07-17、rule15 2026-03-04），变的是**老师的标签/组织**。同老师前后批次任务命中不同规则 = 标签或组织路径在两批次之间发生过变化。

## 排查步骤

1. **确认各批次任务快照的规则**（同一 account_id 不同 create_time 对比）：
   ```sql
   -- prod cluster 211
   SELECT task_code, subclazz_number, create_time, SUBSTRING(task_rule_config,1,80) AS rule_head
   FROM gaotu.first_call_task
   WHERE account_id = <老师accountId> AND create_time >= '<起始日>' ORDER BY create_time;
   ```
   `rule_head` 里 `"id":"15"` / `"id":"5"` 即命中的规则。
2. **对比两条规则的配置**（要求、勾的部门、标签）：
   ```sql
   SELECT id, task_rule_name, org_numbers, role_labels, task_finish_condition, update_time
   FROM gaotu.task_rule_config WHERE id IN (<规则id...>);
   ```
   `update_time` 未变 = 规则没改过，是老师侧变了。
3. **看老师当前组织路径与标签**（acl 桥，只读）：
   `com.gaotu.base.adapter.staff.StaffAdapter#listByAccountIdList`，params `[[<accountId>]]`；
   看 `orgPathFromRoot`（逐段对 org_numbers 算深度）和 `staffLabelGroupList`（角色标签组4）。
   当前路径下手动复算就近度即可复现命中的规则。
4. **标签/组织变更的时间点**：任务快照（有标签→没标签 或 反之）+ 当前状态对比即可锁定变更发生在哪两批之间；授予/调岗的准确时间在组织系统（mojito）侧， fairy 无现成表。

## 已知原因与判据

| 现象 | 根因 | 判据 |
|---|---|---|
| 同老师前后批次完成条件不同 | 角色标签授予/回收 或 组织调整，翻转了就近规则 | 规则 update_time 未变 + 任务快照规则 id 不同 |
| 转班后要求变多 | 新班主任部门命中要求更多的规则 | 新旧任务 task_rule_config 快照对比 |
| 业务要求统一口径 | 规则配置层面的部门/标签划分问题 | 找任务平台配置负责人调整 org_numbers/role_labels，不是改任务 |

## 批量修数（置完成）通道

- 老辅导班链路（first_call_task）用 student-center `FirstCallTaskServiceImpl#fixFirstCallTask(userId, subclazzNumber)`（acl 桥可调，crm 同库事务）：主任务置已完成（完成时间=过期前1小时）+ 状态记录六项全 true/有效首call + fairy_task 完成 + 发 MQ 刷 ES。
- **注意**：该接口**不更新 platform_subtask**，弹窗里未完成的格子会保持灰（展示残留，不影响完成与业绩口径）；也不要手工把子任务置完成——子任务(完成)与实时重算(未完成)不一致会触发 `checkFirstCallStatusNew` 重算，把主任务打回进行中。
- 1v1 容器链路（first_call_task_1v1）用 fairy `FirstCall1v1StatusCheckService#forceCompleteTask`（四张表一起写，见 1v1 runbook）。
