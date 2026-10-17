# 续班归因

班级任务展开出的**学员级**续班原因归因（未续跟进 `unrenewedReasonAi` / 已续总结 `renewedReasonAi`）：大模型读沟通记录/问卷/预测数据，产出结构化 JSON，落 `ees_data.ai_app_clazz_user_scene` 并回写花名册 ES，供按原因筛选。这里记录它线上出问题时的排查（消费堆积、AI 调用失败、结果不对）。

核心包 `com.gaotu.student.data.domain.renewal.reasoning`；需求归档见 `需求/续班归因/`。

## 症状路由

| 症状（用户会怎么说） | 去哪 |
|---|---|
| 续班归因 MQ 堆积 / 消费组 `GID_student-data_renewal_reason_task_prod` 堆积高 / 天眼告警 | [`续班归因AI调用失败.md`](排查/续班归因AI调用失败.md) |

## 案例

| 日期 | 现象 | 状态 |
|---|---|---|
| 2026-10-17 | [AI调用失败导致MQ堆积](案例/2026-10-17-AI调用失败导致MQ堆积.md) | 已解决 |
