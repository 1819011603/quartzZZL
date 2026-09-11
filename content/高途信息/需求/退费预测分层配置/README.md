---
title: 退费预测分层配置
aliases:
  - AI预测退费意向
  - 退费分层阈值
  - predict_intent_config
  - 退费预测异常
branches:
  - student-data: release（当前线上跑的旧逻辑，无独立功能分支）
  - student-data: feature-predict-level-reason（重构分支，未合并，同一业务域）
status: 开发中
owner: zhangzeling
updated: 2026-09-12
tags: [需求, 排障, runbook]
---

# 退费预测分层配置

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 任务板]] · [[changelog|📜 会话日志]] · [[runbook|🛠 排障手册]]
> 这不是一个常规产品需求，是**一类反复出现的线上问题的排障归档**：花名册"AI预测退费意向"
> 显示异常（某班绝大部分学生被判"高危"）。已发生两次真实案例，根因都是阈值配置缺失。
> **续接排障时：先读本文件 + [[runbook]]，别现场翻代码摸索。**

## 一句话

`student-data` 线上现跑的"退费/续班分层预测"用一张 Apollo 之外的 MySQL 阈值配置表
（`ees_data.predict_intent_config`）按「业务线×学部×学期×stage×年级×学科×新老生」查分档区间，
**配置缺哪个组合就会静默退化成粗粒度兜底档，导致大批学生被误判高危**，且不会报错告警。

## 需求摘要

- **要解决的问题**：花名册"AI预测退费意向"列数据异常（某班几乎全员"高危"），业务/带班老师反馈
- **给谁用**：业务运营/带班老师看退费预警看板，据此重点跟进"高危"学生
- **核心改动**：本目录不改代码，是**排障方法论 + 两次真实案例的沉淀**；唯一可能的代码级动作是
  推动 `feature-predict-level-reason` 分支上线以根治这类问题
- **判定"做完"的标准**：不存在——这是持续性排障归档，只要旧逻辑还在线上跑，
  换季/换 stage 时就可能复现，本目录跟着累积案例
- **明确不做**：不在本目录决定阈值配置的具体数值（那是算法/数据侧的职责，EES 只负责发现问题和回溯执行）

## 已定共识

- 阈值配置查不到精确组合时会静默退化到 `grade='defaultGrade'` 兜底档，**不报错、不告警**，
  只能靠业务侧人肉发现数据异常反馈（2026-09-08 定）
- 缺失是按「学期」滚动的系统性风险，不是一次性事件；每次换季前应主动核对配置是否配全，
  但目前没有自动化校验机制（2026-09-11 定）
- 回溯用 `SyncRefundResultHandler` 这个 job，**不支持按班级/学部过滤，只能按 `updated_time` 时间范围**；
  回溯前必须显式给出覆盖问题记录的时间窗口，不能只用默认的"今天"（2026-09-08 定，见 [[runbook]]）
- 根治方案是 `feature-predict-level-reason`（commit `2f979dcd8`）重构，把分层判断完全交给算法侧
  产出、EES 不再本地查阈值表现算；但截至 2026-09-12 还未合并上线，不能当作当前的解决手段

## 现在什么情况

| | |
|---|---|
| 阶段 | 开发中（无独立开发任务，持续跟进配置补齐 + 视情况回溯） |
| 进度 | T 1/1（跟进 stage=4 配置补齐，见 [[tasks]]） |
| 当前卡点 | stage=4（H业务线 4 个学部 × 秋季班）阈值配置尚未补齐，等算法/数据侧配置 |
| 最近更新 | 2026-09-12 |

## 下一步

1. 跟进算法/数据侧把 stage=4（H业务线：本地化大班学部/清北班学部/精品班学部/菁英班学部 × 秋季班）
   的年级细分阈值配置补上（当前只有 `defaultGrade` 粗粒度兜底）
2. 配置补上后，用 [[runbook]] 里的回溯步骤，**限定 stage=4** 触发一次 `SyncRefundResultHandler`
   回溯（不用像案例1那样扫全量），并按 [[runbook]] 的验证步骤核实数据库 + ES 双侧修正

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/student-data | release（线上现跑逻辑） | `student-data-service` 模块 `com.gaotu.student.data.util.RenewalComponent#refreshRefundResultIntentRecord`、`com.gaotu.student.data.util.PredictIntentComponent#getIntentConfig`、`com.gaotu.student.data.infrastructure.dao.service.impl.PredictIntentConfigServiceImpl` |
| /Users/gaotu/IdeaProjects/JavaProject/student-data | release | `student-data-dws` 模块 `com.gaotu.student.data.dws.job.sync.SyncRefundResultHandler`（回溯 job） |
| /Users/gaotu/IdeaProjects/JavaProject/student-data | release | `student-data-facade` 模块 `com.gaotu.student.data.facade.mq.dws.renewal.DwsRefundIntentConsumer`（MQ→ES） |
| /Users/gaotu/IdeaProjects/JavaProject/student-data | feature-predict-level-reason（未合并，commit `2f979dcd8`） | 根治方案，把分层判断挪到算法侧产出，详见该分支自身 commit message |

## 上线影响面

> 本目录不涉及上线（不是待上线需求），此表格不适用，仅记录本目录真正动过的线上操作：

| 操作 | 涉及 | 说明 |
|---|---|---|
| Apollo | 否 | |
| ES | 否（只读查询验证，未写） | 用 es-apply skill 的 SRE 路径读 PROD |
| MySQL DDL | 否 | |
| MQ | 否（触发回溯 job 时会产生 MQ 消息，但不是本目录申请的资源） | |
| 代课接口权限 | 否 | |
| 生产数据回溯 | 是 | 详见 [[runbook]]，两次真实执行记录见 [[changelog]] |

## 必须知道的坑

- 一个 `clazz_number`（课程）下可能挂很多个 `subclazz_number`（平行班），排查具体班级问题
  **必须精确到 subclazz_number**，只按 clazz_number 查会把同门课下所有平行班的数据都混进来
- `SyncRefundResultHandler` 不支持按班级/学部过滤，只能按 `updated_time` 时间范围回溯；
  默认参数只扫"今天"，会漏掉历史存量记录（案例1实测漏了4条，见 [[changelog]] 2026-09-08）
- 该 job 单线程逐条同步发 MQ，耗时预估**必须现读当次日志的实际批次大小反推**，
  不能套用其他运行记录的批次大小估算（案例1曾因此把预估时间错算了 10 倍，见 [[changelog]]）
- PROD 的 ES 查询只能走 `es-apply` skill 的 SRE 路径，`es-aliyun` MCP 连 PROD 必 502
