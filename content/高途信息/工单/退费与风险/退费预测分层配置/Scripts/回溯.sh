#!/usr/bin/env bash
# 退费预测分层配置 · 回溯历史存量数据（配置补齐后才有意义）
# 前提：Scripts/排查.sql 第3、4步已确认目标组合精确配置已存在。
# 详细说明见同级 ../README.md「排查方法」一节。

SERVICE_CODE="baijia.gaotu.Business.counseling-workbench.student-data-dws"
POD_NAME="<先用下面这条列出来选一个>"
# python3 ~/.claude/skills/pod-terminal/pod_term.py pods --service-code "$SERVICE_CODE" --env prod

# 1. 参数写文件（避免多层转义），startTime/endTime 必须显式给，别用空参数（空参数只回溯"今天"）
python3 ~/.claude/skills/pod-terminal/pod_term.py exec --service-code "$SERVICE_CODE" --env prod \
  --pod-name "$POD_NAME" \
  --cmd "printf '%s' '{\"startTime\":\"yyyyMMdd\",\"endTime\":\"yyyyMMdd\"}' > /tmp/backfill_param.json"

# 2. arthas 反射调用，读文件传参
#    全类名 com.gaotu.student.data.dws.job.sync.SyncRefundResultHandler（注意 .sync 包）
#    OGNL 坑1：instances 是数组不是 List，取数量用 .length，用 .size() 会报 NoSuchMethodException
#    OGNL 坑2：静态方法必须写 @全限定类名@方法(...)，直接 ClassName.method() 会报 NoSuchPropertyException
python3 ~/.claude/skills/pod-terminal/pod_term.py arthas --service-code "$SERVICE_CODE" --env prod \
  --pod-name "$POD_NAME" \
  --command "vmtool -x 3 --action getInstances --className com.gaotu.student.data.dws.job.sync.SyncRefundResultHandler --express \"instances[0].execute(new java.lang.String(@java.nio.file.Files@readAllBytes(new java.io.File('/tmp/backfill_param.json').toPath())))\"" \
  --exec-timeout 590000 --stop
# 大概率在几百秒内超时报 "arthas state=INTERRUPTED"——只是客户端等待超时，job 仍在服务端继续跑，
# 不代表失败，不用重新触发。

# 3. 跟踪进度（app.log 单文件体积很大，实测要 tail -c 到 1~3 亿字节才够覆盖到最新进度）
python3 ~/.claude/skills/pod-terminal/pod_term.py exec --service-code "$SERVICE_CODE" --env prod \
  --pod-name "$POD_NAME" \
  --cmd "tail -c 100000000 /apps/srv/instance/app/log/app.log > /tmp/t.log; grep -o 'Processing page [0-9]*' /tmp/t.log | tail -1; grep -c 'execute success, total processed' /tmp/t.log; grep -c 'execute,Exception' /tmp/t.log" \
  --idle 6 --timeout 60
# 第二个数字（execute success）从0变>=1即完成；第三个数字（execute,Exception）非0即出错。
# 耗时参考：56万条记录、1000条/页共564页，实测约2小时——扩大范围前先从当次日志现读实际
# batch size（"record count: N"那行），别照抄上次数字估算。
