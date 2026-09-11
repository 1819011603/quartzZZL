# 退费预测分层阈值配置 — 验证手册

## 环境

- 只在 PROD 复现过，未知测试环境是否有对应数据
- MySQL：`ees_data.ai_refund_prediction_results` / `ees_data.predict_intent_config`，
  cluster_id=336（集群 `gaotu-student-dynamic-prod`），走 `mysql-query` skill，`env=prod`
- 班级 bizNumber → clazz_number：`course_center.clazz` 表，cluster_id=317，db=`course_center`
- ES：索引 `ads_large_subclazz_user_index`，client bean `eesServeClient`，对应 Apollo host key
  `ees.serve.es.cluster.host`（namespace `es`），PROD host
  `es-cn-smw4b9m200004w3hn.elasticsearch.aliyuncs.com`；**查询必须走 `es-apply` skill 的 SRE
  `dsl` 通道**，不能用 `es-aliyun` MCP（本机直连线上 ES 必 502）
- 触发回溯的服务：`student-data-dws`，青舟 serviceCode
  `baijia.gaotu.Business.counseling-workbench.student-data-dws`

## 排查步骤（拿到"某班高危退费占比异常"反馈时）

1. 反查 clazz_number：
   ```sql
   SELECT number, biz_number, name FROM course_center.clazz WHERE biz_number = '<班级ID>'
   ```
2. 查该 clazz 下的 subclazz（一个 clazz/课程可能对应很多个班/很多天历史快照，别直接拿
   clazz_number 统计分布，容易把别的班/别的天混进来）：
   ```sql
   SELECT subclazz_number, COUNT(*) FROM ees_data.ai_refund_prediction_results
   WHERE clazz_number = <上一步 number> GROUP BY subclazz_number ORDER BY COUNT(*) DESC
   ```
3. 按具体 subclazz_number 看分层分布：
   ```sql
   SELECT prediction_level, COUNT(*) FROM ees_data.ai_refund_prediction_results
   WHERE subclazz_number = <x> GROUP BY prediction_level
   ```
4. 抽几条高危记录，记下维度：
   ```sql
   SELECT user_number, prediction_score, prediction_level, stage,
          course_first_level_department_name, performance_second_level_department_name,
          school_term_name, grade, student_type
   FROM ees_data.ai_refund_prediction_results
   WHERE subclazz_number = <x> AND prediction_level = '4' LIMIT 10
   ```
5. 拿这些维度去配置表核对（先不带 grade 条件，看这个 部门+学期+stage 组合下全貌）：
   ```sql
   SELECT * FROM ees_data.predict_intent_config
   WHERE course_first_level_department_name = '<部门>'
     AND course_second_level_department_name = '<学部>'
     AND school_term_name = '<学期>' AND stage = '<stage>'
   ```
   只有 `grade='defaultGrade'` 的行、没有具体年级的行 → 就是缺配置。
6. 怀疑影响面不止一个班时，按 stage 统计整体覆盖度：
   ```sql
   SELECT course_first_level_department_name, course_second_level_department_name, school_term_name,
     SUM(CASE WHEN grade='defaultGrade' THEN 1 ELSE 0 END) AS default_rows,
     SUM(CASE WHEN grade!='defaultGrade' THEN 1 ELSE 0 END) AS grade_specific_rows
   FROM ees_data.predict_intent_config
   WHERE stage = '<stage>'
   GROUP BY course_first_level_department_name, course_second_level_department_name, school_term_name
   ```
   `grade_specific_rows = 0` 的组合就是缺配置的范围。

## 回溯操作（配置补齐后才有意义，配置没补齐回溯了也是白跑）

1. 找 prod pod：
   ```bash
   python3 ~/.claude/skills/pod-terminal/pod_term.py pods \
     --service-code baijia.gaotu.Business.counseling-workbench.student-data-dws --env prod
   ```
2. 把回溯参数写到 pod 的一个文件里（避免命令行里嵌套转义 JSON 双引号）：
   ```bash
   python3 ~/.claude/skills/pod-terminal/pod_term.py exec \
     --service-code baijia.gaotu.Business.counseling-workbench.student-data-dws --env prod \
     --pod-name <podName> \
     --cmd "printf '%s' '{\"startTime\":\"yyyyMMdd\",\"endTime\":\"yyyyMMdd\"}' > /tmp/backfill_param.json"
   ```
   时间范围建议覆盖"这学期开课日期"到"今天"。**别用空参数**——空参数只回溯"今天"，历史存量
   记录会被漏掉（2026-09-08 那次真实踩过，漏了4条）。
3. arthas 反射调用触发：
   ```bash
   python3 ~/.claude/skills/pod-terminal/pod_term.py arthas \
     --service-code baijia.gaotu.Business.counseling-workbench.student-data-dws --env prod \
     --pod-name <podName> \
     --command "vmtool -x 3 --action getInstances --className com.gaotu.student.data.dws.job.sync.SyncRefundResultHandler --express \"instances[0].execute(new java.lang.String(@java.nio.file.Files@readAllBytes(new java.io.File('/tmp/backfill_param.json').toPath())))\"" \
     --exec-timeout 590000 --stop
   ```
   - `instances` 是数组，取数量用 `.length`，不是 `.size()`（`.size()` 会报
     `NoSuchMethodException`）
   - 静态方法调用必须写 `@全限定类名@方法(...)`，不能直接 `ClassName.method()`（否则报
     `NoSuchPropertyException`）
   - 这条 HTTP 调用大概率会在 590s 超时报 `arthas state=INTERRUPTED`，**这只是客户端等待
     超时，job 本身仍在服务端 JVM 里继续跑**，不代表调用失败，也不需要重新触发
   - 通过 `baijia-invoke` 的 `invoke_service` 走 HTTP 桥调这个 job，容易碰到"未找到服务实现
     类"（Bean 实际在 `student-data-dws`，不在主服务 `student-data`）或 Cookie 登录失效；这
     条 arthas 路径更稳，优先用它
4. 跟踪进度（因为第 3 步的调用会超时断开，需要另外去看日志）：
   ```bash
   python3 ~/.claude/skills/pod-terminal/pod_term.py exec \
     --service-code baijia.gaotu.Business.counseling-workbench.student-data-dws --env prod \
     --pod-name <podName> \
     --cmd "tail -c 100000000 /apps/srv/instance/app/log/app.log > /tmp/t.log; grep -o 'Processing page [0-9]*' /tmp/t.log | tail -1; grep -c 'execute success, total processed' /tmp/t.log; grep -c 'execute,Exception' /tmp/t.log" \
     --idle 6 --timeout 60
   ```
   - `app.log` 单文件体积很大（几个G），实测要 `tail -c` 到 1~3 亿字节才够覆盖到最新进度，
     8MB/百万字节级别经常已经被冲掉了，看不到东西不代表 job 挂了
   - 第二个数字（`execute success, total processed` 出现次数）从 0 变成 ≥1 即完成；第三个
     数字（`execute,Exception` 次数）非0即出错，需要看异常栈
5. 耗时参考：56万条记录、1000条/页共564页，实测约2小时跑完（日志 `Processing page 564` 之后
   紧跟 `total processed: 563417`）。**扩大范围前，先从当次日志里现读实际 batch size**（找
   一行 `record count: N`），别照抄上一次的数字估算——上次因为套用了另一次运行看到的"100条/页"，
   把这次的耗时错估成17小时（实际约2小时）。

## 验证修复效果

- DB：
  ```sql
  SELECT prediction_level, COUNT(*) FROM ees_data.ai_refund_prediction_results
  WHERE subclazz_number = <x> GROUP BY prediction_level
  ```
- ES（走 `es-apply` skill 的 `dsl` 子命令）：
  ```bash
  python3 es_workorder.py dsl --instance-id es-cn-smw4b9m200004w3hn --method GET \
    --path /ads_large_subclazz_user_index/_search \
    --body '{"size":0,"query":{"term":{"subclazzNumber":<x>}},"aggs":{"levels":{"terms":{"field":"aiRefundIntentScoreResult"}}}}'
  ```
- 对比修复前后"高危(level=4)"占比是否回到合理水平（正常应是个位数到十几个百分点，不应该是
  80%~90% 这种量级）；DB 和 ES 两边聚合结果应该一致，不一致说明 MQ 消费(`DwsRefundIntentConsumer`)
  还没追上，等一等再查。

## 已知配置缺口快照

写作时（2026-09-12）的已知缺口见 [README.md](README.md)「现在什么情况」一节；这是会变化的状态，
用前先按上面「排查步骤」第 6 步的 SQL 重新查一遍确认现状，别直接信这份文档的旧记录。
