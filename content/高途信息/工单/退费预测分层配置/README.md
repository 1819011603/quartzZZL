# 退费预测分层配置工单记录

同一模块的案例按日期倒序写在本文件。通用配置覆盖检查、SQL、Arthas 回溯方法统一维护在 `student-data/.claude/skills/refund-intent-threshold-debug/SKILL.md`。

## 2026-09-11 高考地理决胜班 89.37% 学生被标为高危退费

### 检索信息

- 状态：待处理
- 关键词：AI预测退费意向，高危退费，批量误判，predict_intent_config，stage=4，defaultGrade，秋季班，高三
- 关键 ID：班级 `33DLTS26QX6P11001`，clazz_number `545524684567900160`

### 反馈信息

- 反馈人 / 反馈渠道：荆雅兰转发陶苗苗留言，飞书群聊，王永诗处理
- 涉及对象：【2026秋季】高考地理目标决胜班，1789 人中 1599 人被标“AI预测退费意向：高”

### 结论

不是代码 bug，是系统性配置缺口。`predict_intent_config` 在 `stage=4`、H 业务线四个学部的秋季班均只有 `defaultGrade` 粗粒度兜底，没有年级细分阈值；兜底阈值 `score > 0.16` 偏严，导致高三学生大批误判。

### 关键证据

- 按 department/stage/grade 分组后，`stage=4`、高三记录共 1607 条，几乎全部是 `level=4`。
- 配置覆盖检查确认 H 业务线四个学部在该学期、stage 和年级组合下均无精确配置。

### 决策与进展

推动算法/数据侧补齐 H 业务线四个学部的秋季班、`stage=4` 年级细分阈值。截至本记录尚未补齐；配置完成前不执行回溯。

### 涉及系统

- 仓库 / 服务：`student-data`
- 代码 / 数据：`RenewalComponent#refreshRefundResultIntentRecord`、`PredictIntentConfigServiceImpl#listByInfo`、`#listDefaultByInfo`；`ees_data.predict_intent_config`、`ees_data.ai_refund_prediction_results`（cluster_id=336，PROD）
- 排查 runbook：`student-data/.claude/skills/refund-intent-threshold-debug/SKILL.md`

---

## 2026-09-08 付乐乐班 83.6% 学生被标为高危退费

### 检索信息

- 状态：已解决
- 关键词：AI预测退费意向，高危退费，批量误判，predict_intent_config，stage=2，stage=3，高一，回溯
- 关键 ID：班级 `31SXTS26QK4X11005`，clazz_number `551189826087448576`，subclazz_number `35957125251465472`

### 反馈信息

- 反馈人 / 反馈渠道：王永诗、杨梦园、付乐乐、荆雅兰，飞书群聊转发
- 涉及对象：【2026秋季】高一数学目标领航班，110 人中 92 人被标“AI预测退费意向：高”

### 结论

不是代码 bug，是配置缺口。`predict_intent_config` 缺少 H 业务线、精品班学部、秋季班、`stage=2/3`、高一的年级细分阈值，系统静默退化到粗粒度兜底档。

### 关键证据

- 原始分层分布为 92/110 高危。
- 配置补齐并按显式区间完成回溯后，该班高危降到 8/97，DB 与 ES 一致。
- 首次使用默认参数只覆盖当天，仍遗留 4 条历史记录；显式指定 `20260815` 至 `20260908` 后覆盖完成。

### 决策与进展

算法侧已于当日 19:43 补齐配置，并使用 `SyncRefundResultHandler#execute` 回溯约 56 万条记录，验证完成。

### 涉及系统

- 仓库 / 服务：`student-data`、`student-data-dws`、`student-data-facade`
- 代码 / 数据：`SyncRefundResultHandler`、`DwsRefundIntentConsumer`、ES 索引 `ads_large_subclazz_user_index`
- 排查 runbook：`student-data/.claude/skills/refund-intent-threshold-debug/SKILL.md`
