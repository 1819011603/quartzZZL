# 「到底被哪层过滤了」怎么算 · 含 2026-09-10 实测

> **这份文档的重点是算法，不是那几个数字。** 每次要重新算，照「§2 计算步骤」走一遍即可。
> 脚本在 [scripts/](scripts/)，实测数据见 §3。

---

## 1. 拦截层模型（先理解结构，再看怎么数）

班级 Job 的调用链（[RenewalReasonTaskService.java:146](../../../../IdeaProjects/JavaProject/student-data/student-data-service/src/main/java/com/gaotu/student/data/app/service/syncdata/ai/renewal/RenewalReasonTaskService.java)）：

```
每行任务(ai_renewal_attribution_follow_clazz_task)
   │
   ├─① inScope(task)                        ← 4 个子判据，短路
   │     ├ is_renew_user_clazz = 0          → reject，打日志
   │     ├ 创建时间早于阈值                  → reject，打日志
   │     ├ 班级/课程查不到                   → reject，打日志
   │     └② needHandle(clazzDO, courseDO)   → 过滤器链，每个 reject 打 "rejected by X, tag: Y"
   │
   ├─③④⑤ inProduceWindow(clazz, course)     ← 3 个子判据，短路
   │     ├ clazzEnded          → "clazz ended"
   │     ├ !hasPostCourse      → "no post course"
   │     └ !formalRenewalStarted → "formal renewal not started"
   │
   └─⑥ dispatchClazzUsers(clazz)
         ├ 抢锁失败 → "clazz is running, skip"
         └ 成功    → "dispatched, clazzNumber: X, userCount: N"
```

**三条关键性质，决定了怎么数：**

1. **短路**：一个班只会命中一个原因 → 各原因的班级集合**两两无交集**，可以直接相加。
2. **只有 reject 才打日志**，通过某一层是**静默的** → 不能靠「某层日志条数」推算通过量，
   只能用「总数 − 各 reject 数」倒推，或数最后的 `dispatched`。
3. **`handle_status=1` 不代表分析过**：被收窄掉的班也会 `markSuccess`
   （注释「班级被收窄掉…也算处理完成，否则会被每次任务反复扫到」），
   所以 Job 汇总里的 `success: N` **不能当作有效处理量**。

---

## 2. 计算步骤（复算照这个走）

### Step 0：拿分母

```sql
-- cluster_id 336, ees_data
SELECT COUNT(*) AS total_rows,
       COUNT(DISTINCT clazz_number) AS distinct_clazz,   -- 应与 total 相等，否则有重复行
       SUM(is_renew_user_clazz = 0) AS renew0
FROM ees_data.ai_renewal_attribution_follow_clazz_task
WHERE create_time >= '<日期> 00:00:00' AND create_time < '<次日> 00:00:00';
```

> 这张表**每天 00:25 被离线侧全量重刷**，所以「当天创建的行数」就是当天 Job 的分母。

### Step 1：定位 Job 线程名（**最容易出错的一步**）

日志里 `CommonRuleFilter` 的 reject **不只 Job 在打**，售后侧接口（TID `after-sales.*`、
线程 `http-nio-*`）也在大量打。**不锁线程 = 数字全错。**

线程名每天不同，从启动日志取：
```
queryStr: messages: "processPendingTasksInBatches | start"
```
2026-09-10 是 `Thread-3919`，TID `student-data.2458177.17889732002850001`。

`scripts/harvest_job_logs.py` 已自动做这一步。

### Step 2：把该线程当天全部日志捞下来

```bash
python3 scripts/harvest_job_logs.py --date 2026-09-10
# → /tmp/job_lines.json （2026-09-10 实测 8,107 行）
```

⚠️ **不要用 MCP 的 `grep` 参数统计**：`grep` 是**客户端**过滤，服务端只先拉
`scanLimit`（上限 100）条，等于从 100 条样本里数数，**结论必错**。
必须用 `queryStr` 做**服务端**过滤 + `offset` 翻页到枯竭
（判枯竭：连续 3 页 0 条；正常结尾是「若干满页 + 1 个残页 + 空页」）。

### Step 3：本地按原因分类计数

```bash
python3 scripts/tally_reasons.py --expect <Step0 的 total_rows>
```

正则与拦截层的对应关系（脚本里的 `REASONS` 表）：

| 层 | 日志正则 |
|-|-|
| ① `is_renew_user_clazz=0` | `not renew user clazz, clazzNumber: (\d+)` |
| ① 创建时间早于阈值 | `created too early, clazzNumber: (\d+)` |
| ① 班级查不到 | `inScope \| clazz not found, clazzNumber: (\d+)` |
| ① 课程查不到 | `course not found, clazzNumber: (\d+)` |
| ② `needHandle` 过滤链 | `rejected by \w+, tag: \w+, clazzNumber: (\d+)` |
| ③ 班级已结课 | `clazz ended, clazzNumber: (\d+)` |
| ④ 无后置课程 | `no post course, clazzNumber: (\d+)` |
| ⑤ 正式续班未开始 | `formal renewal not started, clazzNumber: (\d+)` |
| ⑥ 抢锁失败 | `clazz is running, skip, clazzNumber: (\d+)` |
| ✅ 实际投递 | `dispatched, clazzNumber: (\d+), userCount: (\d+)` |

**按 clazzNumber 去重后计数**，不要数日志行数（同一班可能有重试行）。

### Step 4：自检（**这步不能省**）

```
Σ(各层 reject 班级数) + 实际投递班级数  ==  Step 0 的 total_rows
```

对不上就说明**还有没覆盖到的分支**，回去补正则，不要直接下结论。
`tally_reasons.py --expect` 会自动打 `✅ 完全吻合` 或 `⚠️ 差 N 个班没被解释`。

> 我第一次算就是栽在这：只数出 75+990+230=1,295，差 1,326 没解释，
> 却先下了「其余都通过窗口」的结论。是自检把漏掉的②那一层暴露出来的。

### Step 5（可选）：②层还要再往下拆

②只告诉你「被过滤器链拒了」，要知道是哪个过滤器、什么原因：

```
rejected by <过滤器类名>, tag: <原因tag>
```
`tally_reasons.py` 末尾会自动按 filter 和 tag 分组。
若大头是 `department_not_in_whitelist`，继续查 → [dept-whitelist-gap.md](dept-whitelist-gap.md)。

---

## 3. 2026-09-10 实测结果

分母：任务表当天 **2,621** 行（2,621 个不同班级，无重复）。

| # | 拦截层 | 判据 | 班级数 | 占比 |
|-|-|-|-|-|
| ① | `inScope` | `is_renew_user_clazz = 0` | 75 | 2.9% |
| ② | `needHandle` 过滤链 | 课程部门不在白名单等 | **1,326** | **50.6%** |
| ③ | `inProduceWindow` | **班级已结课** | **990** | **37.8%** |
| ④ | `inProduceWindow` | 无后置课程 | 230 | 8.8% |
| ⑤ | `inProduceWindow` | 正式续班未开始 | 0 | 0% |
| ⑥ | `dispatchClazzUsers` | 抢锁失败 | 0 | 0% |
| ✅ | — | **实际投递** | **0** | **0%** |

`75 + 1326 + 990 + 230 = 2621` ✅ 与分母完全吻合。

**「到底是 clazzEnded 还是 !hasPostCourse」：`clazz ended` 990，`no post course` 230，
前者是后者的 4.3 倍。但两者相加只占 46.6%，最大的一层是②的 50.6%。**

②的细分：

| 过滤器 | tag | 班级数 |
|-|-|-|
| `CommonRuleFilter` | `not_need_handle_department_not_in_whitelist` | **1,318** |
| `PremiumClazzDepartmentFilter` | `not_need_handle_premium_clazz_name_not_match` | 6 |
| `TsinghuaPekingClassDepartmentFilter` | `not_need_handle_summer_lesson_count_invalid` | 2 |

那 1,318 个全是素养类课程，是离线 SQL 与 Java 白名单口径不一致所致
→ [dept-whitelist-gap.md](dept-whitelist-gap.md)。

**当天 4 条归因不是 Job 产出的**（Job 投递数为 0），是老师打开花名册页面
(`fuwu.baijia.com/crm/cronus/lessonStudentList?cn=556596222882912256`) 触发的单学员路径
——该路径**不过** ①②③④ 这些收窄。

---

## 4. 其他坑

- **时间戳别写错年份**：`date` 一下再算。2026-09-10 00:00 = `1788969600`，05:00 = `1788987600`。
  我第一次按 2025 年算，查出来全空。
- **`mcpcli.py` 当前是坏的**：报 `AttributeError: 'Tool' object has no attribute 'name'`。
  绕过办法是直接 import 模块调 `call_tool`（`harvest_job_logs.py` 已这么做）。
- **`baijia_invoke.py` 不能直接 import**：它的 `from mcp.server import Server` 没有
  try/except，本机 python3 没装 `mcp` 会 ImportError（`qingzhou_log.py` 有 try/except 所以可以）。
  要查课程/班级信息只能走 MCP 工具调用。
- **服务层 INFO 日志在 TLS 查不到**，prod 只有 SLS。

## 5. 待确认

- [ ] **可观测性**：`processPendingTasksInBatches | finish` 目前只打 total/success/fail，
      建议补「实际投递班级数 + 各拦截原因计数」。否则每次都要这样捞 8,000 行日志才能算清楚，
      而 `success: 2621` 还会持续误导。
- [ ] 部门白名单挡掉一半（1,318 个素养类班）是漏配还是灰度未放开 → [dept-whitelist-gap.md](dept-whitelist-gap.md)
- [ ] 08-28~09-02 那 15,081 行 `handle_status=0` 是否补跑（Job 只处理当天创建的记录，不会自动补）
