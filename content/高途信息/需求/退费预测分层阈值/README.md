---
title: 退费预测分层阈值配置
aliases:
  - AI预测退费意向
  - 退费管控
  - 高危退费
  - predict_intent_config
  - ai_refund_prediction_results
  - SyncRefundResultHandler
branches: []
status: 已上线
repos:
  - student-data
  - student-center
updated: 2026-09-12
---

# 退费预测分层阈值配置

## 一句话

花名册/退费管控页面"AI预测退费意向"批量误判"高危"，根因几乎总是
`ees_data.predict_intent_config` 里某个「业务线×学部×学期×stage×年级×新老生」组合缺阈值配置，
静默退化到粗粒度兜底、门槛偏严导致大批量误判。排查按「必须知道的坑」定位，回溯命令见
[`verify.md`](verify.md)。

## 需求摘要

算法侧对学员算出退费概率 `prediction_score`（0~1），EES 侧按 `predict_intent_config` 表里配置的
阈值区间把分数转成 1~4 档（低/中/中高/高），写入 `ees_data.ai_refund_prediction_results`，
再同步到花名册 ES 字段供业务运营筛选"高危退费"学员去跟进。`scene=1` 续班 / `scene=2` 退费共用同一套
存储和重算逻辑，本目录只跟"退费"（scene=2）这条线的两次误判事故，续班分层的独立问题不在此记录。

这套机制不属于 `feature-predict-level-reason`（另一个正在做、尚未合并的重构分支——那个分支打算把
分层判断整体挪到算法侧直接产出，从根上消除本目录记录的这类"配置漏配"问题）。

## 已定共识

- `scene=1`续班 / `scene=2`退费 共用 `predict_intent_config` 表和
  `RenewalComponent#refreshRefundResultIntentRecord` 重算逻辑，按 `scene` 分流，改动前先确认改的是哪个 scene
- 精确配置（部门+学期+stage+年级+学科+新老生）查不到时，**静默**退化到
  `defaultGrade`/`defaultStudentType` 兜底阈值，不报错不告警——这是本类问题反复出现、且不会自己被
  发现（只能靠业务人肉反馈）的根本原因
- 阈值是按「业务线×学部×学期×stage×年级×新老生」这个维度组合配的，每进入新学期或新 stage
  都可能出现某个组合被漏配
- 回溯只能用 XXL-Job `SyncRefundResultHandler`（`student-data-dws`，prod jobGroup=530/test=930），
  按 `updated_time` 时间范围扫全表，**不支持按班级/subclazz 过滤**——一次触发影响面是"这个时间窗口内
  更新过的全系统记录"，不是单个班

## 现在什么情况

两次真实事故：

1. **2026-09-08**：付乐乐班（31SXTS26QK4X11005，H业务线/精品班学部）110人中92人被标"高危"，
   根因是该学部秋季班 stage=2/3 缺年级细分配置。算法侧当天补齐配置后，已回溯并验证修复（见 changelog）。
2. **2026-09-11**：高考地理决胜班（33DLTS26QX6P11001，H业务线/精品班学部）1789人中1599人（89.37%）
   被标"高危"，根因是 stage=4。排查发现范围更大：**H业务线全部 4 个学部（本地化大班/清北班/精品班/
   菁英班）在当前学期"秋季班"，stage=4 全部只有 defaultGrade 兜底、没有任何年级细分配置**（对比
   寒假班/春季班/暑假班基本都配了）。**这一批截至本文档更新时尚未修复**，配置需算法侧补。

## 下一步

- [ ] 推动算法/数据侧把 H业务线 4 个学部 × 秋季班 × stage=4 的年级细分阈值补进
      `predict_intent_config`（至少覆盖 高一/高二/高三/初三 × 新生/老生）
- [ ] 配置补齐后，按 [`verify.md`](verify.md) 的回溯流程重新触发 `SyncRefundResultHandler`
      （scene=2，时间范围覆盖秋季班开课以来到当前）
- [ ] 回溯后按 [`verify.md`](verify.md) 的核对方法确认 H业务线四学部 stage=4 高危占比恢复正常
- [ ] 建议把 `verify.md` §排查步骤 第 6 步的"配置覆盖度巡检 SQL"定期跑一次（尤其每次新学期/新
      stage 切换后），提前发现缺口，别等业务反馈

## 待确认

- 是否要把"配置缺失静默退化"改成"缺失即告警"（类似 `feature-predict-level-reason` 新链路已经做的
  "每类丢弃单独计数并输出 job 日志"）——目前只是发现问题，尚未推动改代码，需要产品/算法侧拍板

## 涉及的代码

- 重算逻辑：`student-data-service/src/main/java/com/gaotu/student/data/util/RenewalComponent.java#refreshRefundResultIntentRecord`
- 阈值查询与缓存：`student-data-service/src/main/java/com/gaotu/student/data/util/PredictIntentComponent.java#getIntentConfig`
- 阈值 DB 服务（精确/兜底两套查询）：`student-data-service/src/main/java/com/gaotu/student/data/infrastructure/dao/service/impl/PredictIntentConfigServiceImpl.java#listByInfo` / `#listDefaultByInfo`
- 回溯 job：`student-data-dws/src/main/java/com/gaotu/student/data/dws/job/sync/SyncRefundResultHandler.java`
- MQ 消费驱动 ES 更新：`student-data-facade/src/main/java/com/gaotu/student/data/facade/mq/dws/renewal/DwsRefundIntentConsumer.java`
- ES 写入服务：`student-data-service/src/main/java/com/gaotu/student/data/app/service/syncdata/AdsSubclazzUserSyncUpdateService.java`
  （索引 `ads_large_subclazz_user_index`，client bean `eesServeClient`）
- ES 字段来源查询：`student-data-service/src/main/java/com/gaotu/student/data/app/service/syncdata/RefundIntentInfoQueryServiceV2.java`
- 花名册展示字段：student-center `RefundFiledConvertDataQueryServiceImpl.java` + `RefundEnumComponent.java`（`aiRefundIntent` 字段，注意
  `RefundEnumComponent.java` 里有一处 `score==1` 硬编码判高危，排查时曾怀疑过但抽样验证过是无害的边界情况，不是本类问题的根因）

## 上线影响面

无代码上线，纯配置补齐 + 手动数据回溯操作。影响面是 PROD 的
`ees_data.ai_refund_prediction_results.prediction_level` 字段值，以及对应花名册 ES 展示。

## 必须知道的坑

- 配置缺失是**静默**的：某班/某 stage 出现大批量"高危"，先怀疑 `predict_intent_config` 缺该组合的
  精确配置，别先怀疑算法模型出错
- `SyncRefundResultHandler` 默认参数（空字符串）只回溯"今天"，历史存量记录会被漏——务必显式传
  `{"startTime":..,"endTime":..}` 覆盖足够宽的范围，别偷懒用空参数
- 这个 job 单线程逐页扫描 + 每条记录同步发一次 MQ，没有批量/异步优化，慢的瓶颈在
  `fuwuOnsMqProducer.sendNormalMessage` 这次同步网络调用上；56万条记录、1000条/页共564页，
  实测约2小时——评估耗时前先从当次日志读实际 batch size，别套用上一次运行的经验值（上次因此把
  耗时错估成17小时）
- 通过 `baijia-invoke` 的 `invoke_service` 桥调这个 job 容易碰到"未找到服务实现类"（因为 Bean 在
  `student-data-dws` 而不是主服务 `student-data`）或登录失效；改用 `pod-terminal` + arthas 反射调用
  更稳，具体命令见 [`verify.md`](verify.md)
- OGNL 反射坑：`instances` 是数组，取长度用 `.length` 不是 `.size()`；静态方法必须写
  `@全限定类名@方法(...)`，不能 `ClassName.method()`；带引号的 JSON 参数建议先用 `printf` 写到 pod
  里的文件，再用 `Files@readAllBytes` 读取，避免嵌套转义
- PROD ES 查询要走 `es-apply` skill 的 SRE `dsl` 通道，不能用 `es-aliyun` MCP（直连必 502）
