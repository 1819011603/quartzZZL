# 退费预测分层配置工单记录

同一类反馈（花名册"AI预测退费意向"批量误判"高危"）都往这一份文件里加，按时间倒序，不再拆子目录/子文件。
可复用的排查方法（怎么定位缺配置组合、怎么用 arthas 回溯）不重复抄在这，见
`student-data` 仓库的 `.claude/skills/refund-intent-threshold-debug/SKILL.md`。

## 2026-09-11 高考地理决胜班89.37%学生被标"高危退费"

### 反馈信息

- 反馈人/渠道：荆雅兰转发陶苗苗留言，飞书群聊，@王永诗 处理
- 涉及对象：班级 33DLTS26QX6P11001（【2026秋季】高考地理目标决胜班），1789人中1599人(89.37%)
  被标"AI预测退费意向：高"

### 结论

不是 bug，是配置缺口。根因是 `predict_intent_config` 里 **stage=4 这个阶段，H业务线下全部4个
学部（本地化大班/清北班/精品班/菁英班）在"秋季班"这个当前学期都只有 `defaultGrade` 粗粒度兜底，
没有任何一个学部配了年级细分阈值**——比上次(见下一条案例)范围更大，是系统性缺口而非单班问题。
兜底阈值门槛偏严（score>0.16 即判高危），套到高三学生普遍偏高的分数区间上，大批误判。

### 决策

推动算法/数据侧补齐 H业务线4个学部 × 秋季班 × stage=4 的年级细分阈值配置；截至本条记录时**尚未
补齐**，配置补齐前不回溯（回溯了也没意义）。

### 排查过程摘要

反查 `clazz_number=545524684567900160` 后按 department/stage/grade 分组统计，定位到
stage=4/grade=高三 记录共1607条几乎全是 level=4；核对 `predict_intent_config` 确认该组合无精确
配置，进一步按 stage=4 统计全部业务线×学部×学期的配置覆盖度，确认是 H业务线全学部秋季班的系统性
缺口。方法与 SQL 见 skill。

### 涉及代码/服务

`student-data`：`RenewalComponent#refreshRefundResultIntentRecord`、
`PredictIntentConfigServiceImpl#listByInfo`/`#listDefaultByInfo`；数据表
`ees_data.predict_intent_config` / `ees_data.ai_refund_prediction_results`（cluster_id=336, PROD）

---

## 2026-09-08 付乐乐班83.6%学生被标"高危退费"

### 反馈信息

- 反馈人/渠道：王永诗/杨梦园/付乐乐/荆雅兰，飞书群聊转发
- 涉及对象：班级 31SXTS26QK4X11005（【2026秋季】高一数学目标领航班，付乐乐带班），110人中92人
  被标"AI预测退费意向：高"

### 结论

不是 bug，是配置缺口。根因是 `predict_intent_config` 缺 H业务线/精品班学部/秋季班/**stage=2、
stage=3**/高一 这个组合的年级细分阈值配置，静默退化到粗粒度兜底档。

### 决策

算法侧当天19:43已补齐该组合配置。补齐后触发回溯，修复线上数据。

### 排查过程摘要

反查 `clazz_number=551189826087448576→subclazz_number=35957125251465472`，确认分层分布异常
(92/110高危)。配置补齐后用 `pod-terminal`+arthas 反射调 `SyncRefundResultHandler#execute("")`
回溯，首次默认参数只回溯了"今天"，复查发现仍有4条历史存量记录(updated_time非今天)未覆盖，改用
显式区间 `{"startTime":"20260815","endTime":"20260908"}` 重新回溯全系统56万条记录（约2小时，
初次预估17小时是套用了另一次运行的批次大小算错的），复查确认该班高危降到8/97，DB与ES两侧一致。

### 涉及代码/服务

同上；回溯 job `student-data-dws` 的 `SyncRefundResultHandler`；MQ消费
`student-data-facade` 的 `DwsRefundIntentConsumer` → ES索引 `ads_large_subclazz_user_index`
