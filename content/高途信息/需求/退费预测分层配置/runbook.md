---
title: 退费预测分层配置 · 排障手册
tags: [需求, runbook]
---

# 排障手册

> 收到"某班 AI 预测退费意向异常/高危占比离谱"这类反馈时，照本文档执行，不用现场摸索。

## 问题现象

花名册页面"AI预测退费意向"列，某个班级里绝大部分学生被标"高"（高危退费），业务/带班老师反馈数据异常。

**已发生两次真实案例：**

1. **案例1（2026-09-08）**：班级 `31SXTS26QK4X11005`（付乐乐带班），110人中92人"高危"（83.6%）。
   根因：H业务线/精品班学部/秋季班/**stage=3**/高一 这个组合缺细分阈值配置。
2. **案例2（2026-09-11）**：班级 `33DLTS26QX6P11001`，1789人中1599人"高危"（89.4%）。
   根因：**stage=4** 这个阶段，H业务线下全部4个学部（本地化大班/清北班/精品班/菁英班）在
   "秋季班"这个学期都只有粗粒度兜底配置（`grade='defaultGrade'`），没有任何年级细分，
   兜底阈值本身门槛过低（如 score>0.16 就判高危），导致大量高三学生被误判。

两次案例的共同模式：**配置缺哪个组合，查询就静默退化到粗粒度兜底档，不报错不告警**，
业务侧只能靠人肉发现数据异常来反馈。

## 数据链路（核心表和代码）

- `ees_data.ai_refund_prediction_results`（cluster_id=336, PROD, `gaotu-student-dynamic-prod` 集群）：
  算法侧产出的预测分数与档位存储表。关键字段：`user_number` / `clazz_number` / `subclazz_number` /
  `prediction_score` / `prediction_level` / `stage` / `course_first_level_department_name` /
  `performance_second_level_department_name` / `school_term_name` / `grade` / `student_type` /
  `updated_time`
- `ees_data.predict_intent_config`：阈值配置表。按 `scene`（1续班/2退费）+
  `course_first_level_department_name` + `course_second_level_department_name` +
  `school_term_name` + `stage` + `grade` + `student_type` 定位一段 `intent_config`
  （JSON 数组 `[{code,start,end}]` 的分档区间）。查不到精确组合时会用
  `grade='defaultGrade'` / `student_type='defaultStudentType'` 的兜底行。
- 代码（`student-data-service` 模块）：
  - `com.gaotu.student.data.util.RenewalComponent#refreshRefundResultIntentRecord`：
    重算入口，读配置、比对分数落哪个区间、设置 `predictionLevel`
  - `com.gaotu.student.data.util.PredictIntentComponent#getIntentConfig`：
    配置查询 + 本地缓存（Caffeine，300s）；查不到精确配置会退化到
    `predictIntentConfigService.listDefaultByInfo`
  - `com.gaotu.student.data.infrastructure.dao.service.impl.PredictIntentConfigServiceImpl`：
    `listByInfo`（精确）/ `listDefaultByInfo`（兜底）两级查询
- 代码（`student-data-dws` 模块）：
  - `com.gaotu.student.data.dws.job.sync.SyncRefundResultHandler`（JobHandler，
    归属青舟服务 `student-data-dws`）：按 `ai_refund_prediction_results.updated_time`
    时间范围分页扫描、重算、`updateBatchById` 写回，每条记录同步发 MQ（`ai_refund_intent_update`
    topic）驱动下游
- 代码（`student-data-facade` 模块）：
  - `com.gaotu.student.data.facade.mq.dws.renewal.DwsRefundIntentConsumer`：消费 MQ，
    调 `AdsSubclazzUserSyncUpdateService.handleForLargeByDimensionMap` 写入 ES 索引
    `ads_large_subclazz_user_index`（ES bean `eesServeClient`，Apollo host key
    `ees.serve.es.cluster.host`，PROD host `es-cn-smw4b9m200004w3hn.elasticsearch.aliyuncs.com`）
  - ES 字段：`aiRefundIntentScoreResult`（档位1-4）/ `aiRefundIntentScore`（原始分数）/ `refundStage`

## 排查步骤（SOP）

1. **拿到班级 bizNumber**（如 `31SXTS26QK4X11005`），查 `course_center.clazz`
   （cluster_id=317，`gaotu-course-prod`）的 `biz_number` 字段拿到 `number`（即 `clazz_number`）。
2. **用 `clazz_number` 查 `ees_data.ai_refund_prediction_results`，`GROUP BY subclazz_number`**
   找到具体班级对应的 `subclazz_number`。⚠️ 一个 `clazz`（课程）下可能挂很多个 `subclazz`
   （平行班），要用 `subclazz_number` 精确定位，只用 `clazz_number` 会把同门课下所有
   平行班的数据都混进来。
3. 按 `subclazz_number`（或 `clazz_number`，视反馈的班级粒度而定）
   `GROUP BY course_first_level_department_name, course_second_level_department_name,
   school_term_name, stage, grade, student_type, prediction_level`，看是哪个组合、
   哪个档位集中异常。
4. 定位到具体的（业务线, 学部, 学期, stage, 年级, 新老生）组合后，去 `predict_intent_config`
   表按这些字段查是否有精确匹配的行；没有精确行时再看有没有 `grade='defaultGrade'` 的兜底行，
   兜底行的阈值区间是否明显不合理（比如某档区间过窄）。
5. **判断缺配置的范围**：不要只看单个班，按 `stage`（或 `school_term_name`）分组统计
   "有多少组合只有 `defaultGrade` 兜底行、多少组合有年级细分行"，确认是"单个组合缺"
   还是"整个 stage/学期维度系统性缺"（案例2就是后者，横跨4个学部）。参考 SQL：
   ```sql
   SELECT course_first_level_department_name, course_second_level_department_name, school_term_name,
     SUM(CASE WHEN grade='defaultGrade' THEN 1 ELSE 0 END) AS default_rows,
     SUM(CASE WHEN grade!='defaultGrade' THEN 1 ELSE 0 END) AS grade_specific_rows
   FROM ees_data.predict_intent_config
   WHERE stage = '<目标stage>'
   GROUP BY course_first_level_department_name, course_second_level_department_name, school_term_name;
   ```
6. **找业务/算法侧把缺失的阈值配置补上** —— 这一步不是 EES/研发能自己决定阈值数值的，
   必须人工介入。
7. **配置补上后，回溯重算存量数据**：
   - 优先走 `xjob-admin` skill 在 XXL-Job 管理台手动触发 `SyncRefundResultHandler`
     （推荐，比反射调用更规范）；`xjob-admin` 用不了才退回 `pod-terminal` + arthas 反射调用：
     ```
     vmtool -x 3 --action getInstances --className com.gaotu.student.data.dws.job.sync.SyncRefundResultHandler \
       --express "instances[0].execute(...)"
     ```
     ⚠️ OGNL 静态方法调用要用 `@Full.Class.Name@method(args)` 语法，不能直接 `Class.method()`
     （直接写会报 `NoSuchPropertyException`）。传较长的 JSON 参数时，建议先用
     `printf '%s' '<json>' > /tmp/xxx.json` 写到容器里的文件，express 里用
     `new java.lang.String(@java.nio.file.Files@readAllBytes(new java.io.File('/tmp/xxx.json').toPath()))`
     读取，避免在 shell/arthas 里多层转义引号出错。
   - **参数格式**：空/blank → 按 `updated_time` 只回溯"今天"；JSON
     `{"startTime":"yyyyMMdd","endTime":"yyyyMMdd"}` → 按时间范围回溯。
     ⚠️ **这个 job 不支持按班级/学部过滤，只能按时间范围**。要回溯历史存量，
     必须显式传更宽的 `startTime`/`endTime`，否则会漏掉 `updated_time` 不在范围内的历史记录
     （案例1教训：默认只扫"今天"漏了4条历史记录，后来补跑 `20260815~20260908` 才补全）。
   - **耗时预估**：该 job 单线程逐条同步发 MQ，速度取决于命中记录总量和实际批次大小。
     ⚠️ **不要用"前几页的速率"乘以"假设的批次大小"去估算总耗时** —— 案例1曾错误套用
     另一次运行日志里"100条/页"的批次大小，导致预估17小时，实际当次运行是1000条/页，
     只用了约2小时。正确做法：等 job 跑完后查日志里 `execute success, total processed: N`，
     或从 `Processing page N` 的最终页数反推 `总条数/N ≈ 实际批次大小`，不要跨运行套用数字。
8. **验证**：数据库（`ai_refund_prediction_results.prediction_level`）+ ES
   （`ads_large_subclazz_user_index` 的 `aiRefundIntentScoreResult`）双重核实。
   - 用 `es-apply` skill 的 `dsl` 子命令跑聚合确认分布：
     ```
     python3 es_workorder.py dsl --instance-id es-cn-smw4b9m200004w3hn --method GET \
       --path /ads_large_subclazz_user_index/_search \
       --body '{"size":0,"query":{"term":{"subclazzNumber":<目标subclazz>}},
                "aggs":{"levels":{"terms":{"field":"aiRefundIntentScoreResult"}}}}'
     ```
   - 对比修复前后的档位分布（1低/2中/3中高/4高 各多少人），确认"高"档人数明显下降到合理水平。

## 已知坑 / 注意事项

- **ES 只能走 `es-apply` skill 的 SRE 路径查 PROD，不能用 `es-aliyun` MCP**（会 502，
  502 不代表索引不存在或集群故障，是用错通道）。
- `mysql-query` 工具首次用某张表要先 `mysql_locate_cluster` 拿 `cluster_id` + `db_name`。
- 这套阈值配置机制是**按学期（`school_term_name`）滚动配的**，换季（如冬季班/寒假班）时
  如果算法侧没有提前把新学期的配置配全，大概率会复现同样问题 —— **这是系统性风险，
  不是一次性事件**，换季前应主动核对配置是否配全。
- 真正的根治方案是 `feature-predict-level-reason` 分支（commit `2f979dcd8`）的重构，
  把分层判断完全交给算法侧产出、不再由 EES 侧查阈值表现算；但截至 2026-09-12
  还没合并上线，当前只能靠"发现问题 → 推动补配置 → 手动回溯"这套流程兜底。
