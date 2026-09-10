# 会话日志 · 续班归因

## 2026-09-10
- 需求已上线。盘点线上数据量 → [data-volume-2026-09-10.md](data-volume-2026-09-10.md)。
  今日（截至 14:00）仅 **1 个班 / 4 个班级-学员** 调用大模型，4 次全为未续归因；
  已续归因 0 次。但班级级 Job 派发并处理了 **2,621 个班**（首次真正跑起来，01:00~01:02 全部完成），
  绝大多数班在进入大模型前被前置条件过滤，待逐层核对。
- 原 skill `renewal-reason-regression` 已删除，内容蒸馏为本目录的
  [runbook.md](runbook.md)（口径与坑）+ [README.md](README.md)。
  test-eco-7 的回归造数细节（固定测试班级/学员清单、逐条用例结论、造数需求）随需求上线一并废弃。
- 逐层核对「2,621 个班只出 1 个班」→ [filter-analysis-2026-09-10.md](filter-analysis-2026-09-10.md)。
  **四层拦截精确相加 = 2,621**：needHandle 部门白名单 1,326 / 班级已结课 990 /
  无后置课程 230 / `is_renew_user_clazz=0` 75。Job 全天 `dispatched` 0 条。
- ⚠️ 本次排查前后修正过两次错误结论，教训写进 filter-analysis 的「排查方法」一节：
  (1) MCP 的 `grep` 是客户端过滤、服务端只拉 100 条，**拿它统计必错**，要用 `queryStr` + `offset`；
  (2) 不锁 Job 线程名会把售后侧接口的 `CommonRuleFilter` reject 算进来。
  正确姿势是「一次性捞全该线程日志 + 本地统计 + 用任务表行数自检」，已固化成
  [scripts/harvest_job_logs.py](scripts/harvest_job_logs.py) 与
  [scripts/tally_reasons.py](scripts/tally_reasons.py)（已实跑验证，自检吻合）。
- 把「到底被哪层过滤了」的**计算逻辑**固化进
  [filter-analysis-2026-09-10.md](filter-analysis-2026-09-10.md)（重写，以算法为主、数字为辅）：
  §1 拦截层模型与三条决定数法的性质（短路→集合无交集可相加、只有 reject 打日志、
  `handle_status=1` 不等于分析过）、§2 五步计算步骤（拿分母 → 定位 Job 线程名 →
  捞全量日志 → 按正则分类去重计数 → **Σ 各层 + 投递数 == 分母 自检**）、§3 实测、§4 坑。
  正则与拦截层的对应表也写进文档，脚本改了要同步。
- 已按文档从零复跑一遍验证：8,107 行 → 75/1326/990/230，自检 `✅ 完全吻合`。

