# 退费预测分层配置工单记录

本模块当前只有一个配置覆盖类案例。通用排查与回溯 runbook 暂无有效 skill 入口；这里仅保留复核当前配置与处置范围所需的案例事实。

## 2026-09-11 H 业务线秋季班多班级集中标为高危退费

### 检索信息

- 状态：待处理
- 最后核验：2026-09-11
- 关键词：AI预测退费意向，高危退费，批量误判，predict_intent_config，defaultGrade，stage=2，stage=3，stage=4，高一，高三，秋季班
- 关键 ID：班级 `33DLTS26QX6P11001`、`31SXTS26QK4X11005`，clazz_number `545524684567900160`、`551189826087448576`，subclazz_number `35957125251465472`

### 反馈信息

- 反馈渠道：飞书群聊转发
- 涉及对象：【2026秋季】高考地理目标决胜班、【2026秋季】高一数学目标领航班

### 当前结论

不是代码 bug。`ees_data.predict_intent_config` 对 H 业务线秋季班的部分 stage/年级组合缺少精细阈值时，会退化到 `defaultGrade` 粗粒度兜底；不适配的兜底阈值会导致学生集中进入高危档。

### 关键证据

| 班级 | 配置范围与现象 | 当前结果 |
|---|---|---|
| 高考地理目标决胜班 `33DLTS26QX6P11001` | `stage=4`、高三；1789 人中 1599 人为高危，分组记录 1607 条且几乎全部 `level=4`；H 业务线四个学部没有对应年级精细阈值，使用 `score > 0.16` 的兜底档 | 待处理，最后核验时配置尚未补齐 |
| 高一数学目标领航班 `31SXTS26QK4X11005` | `stage=2/3`、高一；补配置前 110 人中 92 人为高危 | 已解决；补齐阈值并回溯后为 97 人中 8 人高危，DB 与 ES 一致 |

### 当前状态与处置

- `stage=4`：由算法/数据侧补齐 H 业务线四个学部秋季班的年级精细阈值；配置完成前不执行回溯。当前状态需以最新配置复核结果为准。
- `stage=2/3`：阈值已补齐，并通过 `SyncRefundResultHandler#execute` 完成约 56 万条记录回溯与结果验证。
- 回溯必须显式传入目标完整时间区间；该案例使用 `20260815` 至 `20260908`。默认参数只覆盖当天，不能作为历史数据已全部更新的验证信号。

### 涉及系统

- 仓库 / 服务：`student-data`、`student-data-dws`、`student-data-facade`
- 代码 / 数据：`RenewalComponent#refreshRefundResultIntentRecord`、`PredictIntentConfigServiceImpl#listByInfo`、`#listDefaultByInfo`、`SyncRefundResultHandler`、`DwsRefundIntentConsumer`；`ees_data.predict_intent_config`、`ees_data.ai_refund_prediction_results`（cluster_id `336`，PROD）、ES 索引 `ads_large_subclazz_user_index`
- 排查 runbook：暂无
