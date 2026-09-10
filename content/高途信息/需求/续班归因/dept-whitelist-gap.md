# 「课程部门不在白名单」1,318 个班是怎么回事 · 2026-09-10

> 承接 [filter-analysis-2026-09-10.md](filter-analysis-2026-09-10.md) 的第②层。
> 疑问：离线 SQL 已经按部门圈过了，为什么 Java 侧还说「不在白名单」？

## 结论：两侧用的是**两套不同的部门口径**，没有对齐

| | 离线圈选 SQL | Java `CommonRuleFilter` 第 1 条 |
|-|-|-|
| 数据源 | `service_dw.dim_service_clazz_df` | `CourseDO.departmentIdPaths`（课程中心主数据） |
| 字段 | `course_first/second/third_level_department_**name**` | 部门 **ID** 路径，如 `10019197/10019736/10019802` |
| 判据 | 中文名匹配（`'综合素养学部'`、`'精品班学部'`…） | `path.contains(白名单ID)` |
| 配置位置 | 离线任务 SQL 里硬编码 | Apollo `renewal.ai.sync.course.department.list` |

**离线放进任务表的班 ⊅ Java 白名单允许的班**，两边各改各的，于是一半的班灌进来又被挡掉。

## 白名单当前值（PROD）

Apollo `student-data / PROD / application`：
```
renewal.ai.sync.course.department.list = 10013518,10019477,10019479,10014349,10016655,10021063,30001264
```
只有 7 个部门 ID。

## 实测对照

**通过的**（`departmentIdPaths` 命中白名单）：

| 课程 | departmentIdPaths | 命中 |
|-|-|-|
| 【2026秋季】高一语文目标一本班 | `10000683/10013429/`**`10013518`** | 精品班/规划系统 |
| 【2026秋季】高二化学目标双一流班 | `10000683/10013429/`**`10013518`** | 同上 |
| 【2026秋上】Level9数理思维BS | `10020216/10020218/`**`10021063`** | TT / V学部 |

**被拒的 1,318 个，全部是「素养类」**（412 个不同课程，抽样全中）：

| 课程分类 | departmentIdPaths | 举例 |
|-|-|-|
| 小学素养 / 剑桥之星 | `10019197/10019599/10019649` | 【2026暑】剑桥之星Lv3、Lv5A |
| 初中素养 / 卓越双语 | `10019197/10019736/10019802` | 【2026秋二轮】卓越双语7阶 |
| 初中素养 / 思维逻辑 | `10019197/10019736/10019932` | 【2026寒】思维与逻辑Level 9 ZJ |
| 脑力 / 脑力速记 | `10019197/10019599/10019649` | 【2026寒】双语新思辩（L1） |
| 高中预科 / 语文规划系统 | `10000683/10013414/10014236` | 【菁英】9阶语文领航衔接班 |

**关键点：一级部门 `10019197`（素养类）整个不在白名单里。**
离线 SQL 的第一个大分支正是要圈这批人：

```sql
course_first_level_department_name in ('KM业务线','EM业务线')
AND course_second_level_department_name = '综合素养学部'
...
OR (course_first_level_department_name = 'EM业务线'
    AND course_second_level_department_name in ('素养小学学部','素养初中学部'))
```

**离线把「综合素养学部 / 素养小学学部 / 素养初中学部」都圈进来了，
但 Java 白名单里没有对应的部门 ID** —— 这就是 1,318 的来源。

另外 `10000683/10013414/10014236`（高中预科/衔接班）也被拒：
同属 `10000683` 这棵树，但白名单只放行了 `10013518` 这一个子部门，
`10013414` 分支下的衔接班进不来。

## 这是 bug 还是预期？

**取决于业务意图，需要产品确认**，两种可能：

1. **灰度未放开** —— 归因功能当前只对精品班/TT 开放，素养类还没上。
   那么离线 SQL 圈太宽了，白灌 1,318 行任务进来，每天多跑一遍无效循环。
2. **配置漏配** —— 素养类本该做归因，但 Apollo 白名单没同步加 ID。
   那么这 1,318 个班是**真正的漏跑**，功能对素养类学部完全没生效。

**判断方法**：看 PRD 里归因功能的目标学部范围。若包含素养类 → 属②，要补白名单。

## 怎么补（如果确认要放开）

需要拿到素养类部门在**课程中心主数据**里的部门 ID，加进 Apollo：

```
renewal.ai.sync.course.department.list = <原值>,10019197
```

⚠️ 判据是 `path.contains(id)` 的**子串包含**，加一级部门 ID `10019197`
会放行其下全部子部门。要精细控制就加三级 ID（如 `10019649`、`10019802`、`10019932`）。
⚠️ Apollo 改完**只是草稿，必须在后台点发布**才生效。

## 复现方法

```bash
# 1. 捞 Job 日志并统计（见 scripts/）
python3 scripts/harvest_job_logs.py --date 2026-09-10
python3 scripts/tally_reasons.py --expect 2621

# 2. 取被部门拒的 courseNumber
python3 - <<'EOF'
import json,re
msgs=json.load(open('/tmp/job_lines.json'))
cs={m.group(2) for s in msgs
    if (m:=re.search(r"department_not_in_whitelist, clazzNumber: (\d+), courseNumber: (\d+)",s))}
print(len(cs)); open('/tmp/dept_courses.txt','w').write("\n".join(sorted(cs)))
EOF

# 3. 查这些课程的 departmentIdPaths（baijia-invoke MCP，一次传多个）
#    com.gaotu.student.data.client.acl.CourseSyncAclService#listByNumbersFromCache
#    params: [["<courseNumber>", ...]]  traffic_env: prod

# 4. 与 Apollo 白名单比对
#    apollo_get_key student-data PROD renewal.ai.sync.course.department.list
```

> ⚠️ `baijia_invoke.py` 不能像 `qingzhou_log.py` 那样直接 import 跑
> （它的 `from mcp.server import Server` 没有 try/except，本机 python3 没装 mcp 会 ImportError），
> 只能走 MCP 工具调用。
