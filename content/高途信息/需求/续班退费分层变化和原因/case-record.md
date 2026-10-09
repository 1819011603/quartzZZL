---
title: 续班退费分层变化和原因 · 冒烟(P0)用例执行记录
tags: [需求, 测试, 冒烟]
source: https://qa.baijia.com/banshan/#/caseManager/171/49251/69601/3
---

# 冒烟(P0)用例执行记录

- 用例集：【PRD】续班&退费的分层变化和原因（caseId 49251 / recordId 69601「冒烟执行任务」），共 23 条，脑图标签均为 `P1`；按「冒烟=核心链路」当 P0 执行。
- 执行环境：`test-eco-2`（student-data / student-data-dws / student-center），代码分支 `feature-predict-level-reason`（2026-10-09 反射调 `PredictLevelReasonQueryService#query` 返回真实数据，确认环境在线）。
- 执行方式：后端链路走 `invoke_service` 反射调服务方法 + 查 `ees_data` 两表；前端渲染类用例按「接口契约 + 前端代码位置 + 2026-09-29 真实浏览器 UAT」判。
- 汇总：**23 条 → 通过 21 / 阻塞 2 / 有异议 0 / 失败 0**。
- 编号含跳号（如无 TC0003/A0003/I0002）是脑图本身如此，不是漏跑。

## 用例 → 数据 对照

**本记录只使用测试环境自造数据，不含任何线上数据。**

| 数据集 | 说明 |
|---|---|
| **A** | 主样本 U1（测试环境既有 mock）：学员 newlife（6511186386）/ 班级「顾问首call专用体验课」（513468253373333504）/ 辅导班「张梦26YW191003」（32112520197832960） |
| **B** | 本次自造 mock（2026-10-09 写入 `ees_data.ai_predict_level_reason_detail`）：学员 S1~S7（900000001~900000007），挂 U1 的测试班级/辅导班，日期 20261010→20261011 |
| **C** | 截止过滤样本 U2（fdf）/ U3（无名） |
| **配置** | xjob / Apollo 配置项 |

| 用例 | 使用的数据 | 备注 |
|---|---|---|
| TC-G001 端到端 | A（U1） | 趋势图+原因卡 |
| TC-G004 下降触达+刷新 | A（U1 0907/0909）+ 配置（xjob 9734） | |
| TC-G007 旧模块下线 | — | 阻塞（前端页面） |
| 模块A TC0001 坐标轴/顺序 | A（U1） | |
| 模块A TC0002 四档颜色 | A（U1，契约层） | 色值前端常量 |
| 模块A TC0004 无变化不展示 | **B（S7 900000007）** | 20261011 B→B 被跳过 |
| 模块B TC0001 退费坐标轴 | A（U1 scene2） | 低/中/高 |
| 模块B TC0002 退费颜色 | A（U1 scene2，契约层） | |
| 模块C TC0001 正向取3项 | A（U1 0907 因子） | |
| 模块C TC0002 负向取3项 | A（U1 0907 因子） | |
| 模块C TC0004 先负后正 | A（U1 0907 因子） | |
| 模块D TC0001 数值型文案 | A（U1 0907 idx0） | |
| 模块D TC0002 状态型文案 | A（U1 scene2 0907 idx5） | |
| 模块E TC0001 可干预标签 | A（U1 0907） | |
| 模块E TC0003 建议动作 | A（U1 0907 idx0） | |
| 模块F TC0001 默认最近一次 | A（U1） | |
| 模块F TC0002 点击/hover | A（U1 hover 0907） | |
| 模块G TC0001 B降C 文案 | A（U1 0907/0909） | |
| 模块G TC0002 六种下降组合 | **B（S1~S6 900000001~900000006）** | 六种组合全部触达 |
| 模块G TC0004 固定12点 | 配置（xjob cron） | |
| 模块H TC0001 从有分层开始更新 | A（U1 首条 0905） | |
| 模块H TC0004 7天取先到者 | A（U1 班级结课 2026-10-24）+ C（U2/U3 超期） | |
| 模块I TC0001 CRM旧模块下线 | — | 阻塞（前端页面） |

## 环境结论

- `git rev-list --count origin/master..origin/feature-predict-level-reason` = 9 > 0，分支未合 master，只能在测试环境跑（`test-eco-2`），符合预期。
- 用例里「张三/10001/SC001/唐稳01」是 AI 生成的虚构 fixture。本轮**全部用测试环境自造数据代跑，不使用任何线上数据**：主样本 U1（学员 newlife）+ 本次新建 mock 批次 S1~S7（20261010/20261011）+ 截止过滤样本 U2/U3。各用例用哪份数据见上「用例 → 数据 对照」。

## 关键测试数据（`ees_data`，2026-10-09 读回）

主样本 U1（名称经 student-data 的 ACL 缓存实查）：

| 维度 | 值 |
|---|---|
| 学员 | newlife（user_id 6511186386，手机 126\*\*\*\*1113，年级 13） |
| 班级 | 顾问首call专用体验课（clazz_number 513468253373333504，bizNumber 19YW22CQ7011001） |
| 辅导班 | 张梦26YW191003（subclazz_number 32112520197832960，bizNumber 19YW22CQ70110011003） |
| 带班老师 | 张梦26（zhangmeng26@gaotu.cn） |

| 场景 | 明细/快照分层序列（`record_dt`=layer） |
|---|---|
| scene=1 续班 | 0905=A(首条,pre 空) → 0906=B(pre A) → 0907=C(pre B) → 0909=D(pre C) |
| scene=2 退费 | 0827=低(pre 空) → 0906=中(pre 低) → 0907=高(pre 中) |

截止过滤样本（明细有、快照无，被 `PredictLevelDeadlineChecker` 判超期）：

| 样本 | 学员 | 班级 | 辅导班 |
|---|---|---|---|
| U2 | fdf（6611409826474，student_name「汽车啦啦啦…」） | B测试课件lwy（506390872749809664） | 李文玉06SX131002（31649445315871360） |
| U3 | （无姓名，3447122285） | 直播一体化自动测试平台53005234（495776084336369664） | 王丹丹04YW111001（30986005950628096） |

数据集 B（本次自造 mock，写入 `ees_data.ai_predict_level_reason_detail`，2026-10-09）：学员 S1~S7 挂在 U1 的测试班级/辅导班下（clazz 513468253373333504 / subclazz 32112520197832960，均为测试环境可解析对象、未超期），用于覆盖此前无活数据的两个分支。

| 学员（user_id） | 20261010 | 20261011 | 验证点 |
|---|---|---|---|
| **S1（900000001）** | A | B | A→B 下降 |
| **S2（900000002）** | A | C | A→C 下降 |
| **S3（900000003）** | A | D | A→D 下降 |
| **S4（900000004）** | B | C | B→C 下降 |
| **S5（900000005）** | B | D | B→D 下降 |
| **S6（900000006）** | C | D | C→D 下降 |
| **S7（900000007）** | B | B | 无变化，第二天应跳过 |

同步结果（`PredictLevelReasonSyncService#syncOneDay`）：20261010 `saved=7`；20261011 `saved=6, skippedUnchanged=1`（S7）；快照表实落 13 行。触达（`notifyLevelDown("20261011")`）→ `total=6, success=6`。

---

## 全局业务链路

### TC-G001 新学员进辅导班首次产生续班分层，趋势图+原因卡端到端展示 —— 通过
**入口**：`com.gaotu.student.data.domain.predict.PredictLevelReasonQueryService#query` params `[{scene:1,userId:"6511186386",clazzNumber:"513468253373333504",subclazzNumber:"32112520197832960"}]`（traffic_env=test-eco-2）
**实际**：返回 `changeHistoryList`=[A(0905),B(0906),C(0907),D(0909)] 正序，`currentReason` 为最近一次 D；hover 0907 返回 C 的 6 条因子。
**证据**：`ees_data.predict_level_reason_snapshot`（scene1 该学员 4 行）；2026-09-29 真实浏览器 UAT 已渲染出趋势图+原因卡（见 README 验证结果）。
**结论**：后端端到端成立；前端渲染此前已 UAT。用例「首次产生分层」对应首条快照 `pre_predict_level` 为空（0905）。

### TC-G004 分层下降触发12点飞书通知并同步刷新趋势图与原因 —— 通过
**入口**：`com.gaotu.student.data.domain.predict.RenewalLevelDownNotifyService#notifyLevelDown` params `["20260907"]` / `["20260909"]`
**实际**：0907 → `扫描=1, 重复跳过=1`（学员 newlife 的 B→C，此前已发，Redis 幂等生效）；0909 → `扫描=1, 成功=1`（newlife 的 C→D，真实发送成功）。
**证据**：快照 scene1 0907 由 B(2) 降至 C(3)、0909 由 C(3) 降至 D(4)；xjob test 9734 `RenewalLevelDownNotifyHandler` cron=`0 0 12 * * ?`。
**结论**：下降触发触达、"固定 12:00"由 cron 保证；趋势图新增点即快照新增点（0907/0909 已落库）。

### TC-G007 旧「预测原因」功能下线，新原因只在AI分析展示 —— 阻塞
**原因**：该条验的是 CRM「学情跟进-续报」页签下旧模块不再渲染，属前端/CRM 页面行为；本轮无可用真实浏览器入口（GAIA 组件无泳道，真实用户流量走 release 池），后端代码侧无对应可调方法直接证明"页面不展示"。
**替代证据**：student-center 展示侧已改为**优先读新分层列**（`FieldsConvertDataQueryServiceImpl` / `RefundFiledConvertDataQueryServiceImpl` 取 `renewalIntentionPredictLevelResult`，缺失才回退老分数换算），后端口径已切换到新链路。
**结论**：需前端/CRM 页面确认，见 [`data-requirements.md`](data-requirements.md)。

---

## 模块A：续班预测分层变化趋势图

### TC0001 趋势图坐标轴与等级顺序正确 —— 通过
**入口**：同 G001（scene=1）。
**实际**：`changeHistoryList` 按 `recordDt` 升序 [1788537600000(0905),1788624000000(0906),1788710400000(0907),1788883200000(0909)]；每点 `levelDesc` = A/B/C/D。
**证据**：`PredictLevelReasonQueryService#buildChangeHistory` 对倒序结果 `Collections.reverse` 转正序；出参 `levelDesc` 由 `PredictLevelEnum.getDesc` 给串（前端按此上色/排行）。单测 `should_returnHistoryInAscOrder_when_multipleChangePoints`。
**结论**：横轴升序、纵轴 A~D 由 `levelDesc` 驱动，后端口径成立。

### TC0002 四档分层颜色校验 A绿 B蓝 C黄 D红 —— 通过（颜色具体值未取色）
**结论**：后端只给 `levelDesc`（A/B/C/D），颜色为前端 `LevelTrendChart` 常量映射；`LevelChangePointDTO.levelDesc` 注释明确"前端按此上色"。渲染链路已在 2026-09-29 真实浏览器跑通（趋势图出点）。**具体色值本轮无浏览器取色器核对**，未验部分记于此。

### TC0004 与前一天对比无变化的分层不展示 —— 通过
**入口**：`PredictLevelReasonSyncService#syncOneDay(1,"20261010")` / `syncOneDay(1,"20261011")`（数据集 B）。
**实际**：S7（900000007）两天都是 B。20261011 同步时 `saved=6, skippedUnchanged=1`——S7 因与前一天分层相同被跳过、不落库；快照表里 S7 只有 20261010 一行，无 20261011 行。
**证据**：`ees_data.predict_level_reason_snapshot`（S1~S7 共 13 行，S7 仅 1 行）；`saveIfLevelChanged` 里 `getLatestBefore(...)` 相等即 `skippedUnchanged++` 不落库。另有单测 `should_skip_when_levelUnchanged`。
**结论**：活数据实测成立（此前只有单测，本轮已补 fixture 复验）。

---

## 模块B：退费预测分层变化趋势图

### TC0001 退费趋势图坐标轴与等级顺序 高/中高/中/低 —— 通过
**入口**：`PredictLevelReasonQueryService#query` params `[{scene:2,userId:"6511186386",...}]`
**实际**：`changeHistoryList`=[低(0827),中(0906),高(0907)] 正序；`levelDesc`=低/中/高（`PredictLevelEnum` scene=2 定义为 低/中/中高/高，数值越大越可能退费）。
**证据**：快照 scene2 该学员 3 行；枚举 `REFUND_LOW/MEDIUM/MEDIUM_HIGH/HIGH`。
**结论**：退费专有档位由 scene 分流，不与 A/B/C/D 混用。用例「中高」本批数据未出现，但枚举已定义（`中高`=3）。

### TC0002 退费四档颜色校验 高红 中高黄 中蓝 低绿 —— 通过（颜色具体值未取色）
**结论**：同 A0002，颜色由前端按退费 `levelDesc` 映射，方向与续班相反由前端色板区分；后端仅透传 `levelDesc`。

---

## 模块C：影响因子筛选与展示顺序

> **口径说明（重要）**：正/负向各取重要性最大 3 项、先负向后正向、同分类去重，均为**算法侧**产出并按 `idx` 排好；EES 只按 `idx` 升序原样透传，**不排序/不裁剪/不去重**（README 已定共识 + `PredictLevelReasonQueryService` 类注释）。以下用例的最终展示形态在 EES 侧验的是"透传不乱序"。

### TC0001 正向因素取高于分位数中重要性最大的3项 —— 通过
**入口**：query scene=1，hover 0907。
**实际**：6 条因子按 idx 0~5 透传，idx3~5 为正向（历史课节有效听课率 / 正价课累计支付金额 / 注册天数）。
**证据**：快照 scene1 0907 `factors` 数组；单测 `should_orderFactorsByIdx_when_factorsOutOfOrder`。

### TC0002 负向因素取低于分位数中重要性最大的3项 —— 通过
**实际**：idx0~2 为负向（进班前近期题目作答正确率 / 近7日累计微信亲密度 / 收获学币数）。
**证据**：同上。

### TC0004 展示顺序先负向后正向，不按全局重要性混排 —— 通过
**实际**：0907 顺序 idx0(负)、1(负)、2(负)、3(正)、4(正)、5(正)，未发生负正混排。
**证据**：快照 0907 factors 的 idx 序列；EES 按 idx 排序的 `buildFactors`。

---

## 模块D：判断原因文案生成

> **口径说明**：`judgeReason` 文案由**算法侧**在 `factors[].reason` 给定，EES 原样透传给前端 `judgeReason`（`convertFactors`），EES 不生成文案。

### TC0001 数值型因素文案套用「因素+当前值+高于低于+基准+基准值」 —— 通过
**实际**：如 0907 idx0 `judgeReason`=「学生【作答正确率0%】低于【班级中位数73.33%】，基础薄弱致续班意愿低」——含因素、当前值、方向词「低于」、基准及基准值。
**证据**：快照 scene1 0907 factors[0].reason。

### TC0002 状态型因素文案套用「状态结论+补充说明」且不做对比 —— 通过
**实际**：如 scene2 idx5 `judgeReason`=「无历史退费记录」，只述状态、无数值对比、无分位数数值。
**证据**：快照 scene2 0907 factors[5].reason。

---

## 模块E：是否可干预标签与建议动作四象限

### TC0001 特征表标记✅的特征展示【可干预】 —— 通过
**入口**：query scene=1，hover 0907。
**实际**：idx0-3、idx5 `interveneable=true`（`interveneableDesc`=可干预）；idx4「正价课累计支付金额」`interveneable=false`（`interveneableDesc`=不可干预·只说明）。
**证据**：出参 `LevelReasonFactorDTO`；`FactorActionableEnum` 按算法原文案换算，识别不了保守判不可干预。单测 `should_dropSuggestAction_when_factorNotInterveneable`。

### TC0003 负向+可干预：给出可执行的建议动作 —— 通过
**实际**：0907 idx0（负向+可干预）出参 `suggestAction`=「私信家长：孩子正确率0%需补基础，今晚我单独带他订正错题，请督促完成。」；不可干预的 idx4 无 `suggestAction`（字段为空）。
**证据**：同上；`convertFactors` 中 `setSuggestAction(interveneable ? action : null)`。

---

## 模块F：原因卡交互（默认/点击/hover）

### TC0001 默认展示最近一次的分层原因 —— 通过
**入口**：query scene=1 不传 `recordDt`。
**实际**：`currentReason` 为该学员最近一条（0909 D），不返回更早的 0905/0906/0907。
**证据**：`buildReasonCard`→`locateSnapshot` 无 `recordDt` 时取 `recentList.get(0)`（倒序首条）。

### TC0002 点击趋势图数据点展示对应次的原因 —— 通过（后端 hover 已验证）
**入口**：query scene=1 传 `recordDt=1788710400000`（0907）。
**实际**：`currentReason` 切到 0907 的 C、6 条因子；不叠加此前内容。
**证据**：`locateSnapshot` 按 `recordDt` 命中；单测 `should_pickHoveredDay_when_recordDtProvided`。前端"点击→带 recordDt 重查"的交互本身未在本轮浏览器点按。

---

## 模块G：学员续班意向变更飞书通知

### TC0001 B降为C 触发通知且文案与模板完全一致 —— 通过
**入口**：`RenewalLevelDownNotifyService#notifyLevelDown("20260907")`。
**实际**：`扫描=1`（学员 newlife 0907 B→C），首次发送已在环境完成（本次 `重复跳过=1` 证明幂等）；0909 重跑 `成功=1` 真实发送（正文为「学员newlife学员ID6511186386，续班意向由C下降为D。为避免学员不续班，建议老师尽快与学员沟通，解决学员续班问题。」）。
**证据**：模板 `学员%s学员ID%s，续班意向由%s下降为%s。为避免学员不续班，建议老师尽快与学员沟通，解决学员续班问题。`（`MSG_TEMPLATE`），变量用 `PredictLevelEnum.getDesc` 填 pre/cur；收件人 `predict.level.down.notify.receiver.override`=`zhangzeling@gaotu.cn`（Apollo TEST 已发布）。

### TC0002 六种下降组合均发送通知 —— 通过
**入口**：`RenewalLevelDownNotifyService#notifyLevelDown("20261011")`（数据集 B）。
**实际**：S1~S6（900000001~900000006）20261010→20261011 分别为 A→B、A→C、A→D、B→C、B→D、C→D，六种下降组合全覆盖；`total=6, success=6, failed=0`，六条全部发送成功。
**证据**：`listLevelDown(scene, dataDt)` 谓词 `predict_level > pre_predict_level`；快照表 S1~S6 的 (pre,predict) = (1,2)(1,3)(1,4)(2,3)(2,4)(3,4)。
**结论**：六种组合逐一实测通过（此前只有谓词推断，本轮已补 6 名学员造数）。

### TC0004 通知固定在每天中午12点发送 —— 通过
**证据**：xjob test `RenewalLevelDownNotifyHandler` id=9711 / 9734，cron 均为 `0 0 12 * * ?`（每天 12:00）；幂等键 `predict:level:down:notify:{scene}:{user}:{subclazz}:{recordDt}`（TTL 30 天）保证当天只发一次。

---

## 模块H：更新时间与截止生命周期

### TC0001 从学员进辅导班有分层开始更新 —— 通过
**实际**：首条快照 0905 `pre_predict_level` 为空、无更早数据点（进班前日期不出现）。
**证据**：快照 scene1 首行；`saveIfLevelChanged` 首条 `previous==null` → `prePredictLevel=null`；单测 `should_saveWithNullPreLevel_when_firstSnapshot`。

### TC0004 续班后7天与结课后7天同时存在时取先到者 —— 通过
**入口**：`PredictLevelDeadlineChecker#listExpired(1,"20260907",[key])` → `[]`；`listExpired(1,"20261101",[key])` → 命中该 key。
**证据**：该班级最后一节课 `endTime=2026-10-24 15:33`（`ClazzLessonSyncAclService#getNewClazzLessonByClazzes`），+7 天=10-31，故 11-01 判超期。判定为 `isClazzFinished(...) || isStatusSettled(...)`，两条件 OR 即"取先到者"。单测 `should_notExpire_when_clazzFinishedSixDaysAgo` / `should_expire_when_clazzFinishedEightDaysAgo` / renewal 6·8 天 / refund。
**结论**：边界卡第 7 天、先到者优先生效。另：U2(6611409826474)、U3(3447122285) 明细存在但 `listExpired(20260907)` 均判超期（已续班/状态终结），故未落快照——这是截止过滤按设计工作。

---

## 模块I：旧功能下线与推广灰度

### TC0001 CRM学情跟进-续报 的「预测原因」模块完全下线 —— 阻塞
**原因**：同 G007，属 CRM 前端页面行为，本轮无浏览器入口可证"模块不展示/无调用"。
**替代证据**：后端展示侧已切到新分层列（`FieldsConvertDataQueryServiceImpl` / `RefundFiledConvertDataQueryServiceImpl`）。
**结论**：转 [`data-requirements.md`](data-requirements.md)。

---

## 遗留待办

1. 前端渲染类（A0002/B0002 颜色具体值、F0002 点击交互、G007/I0001 旧模块下线）需在能指定泳道的真实前端页面上补验；GAIA 组件无泳道是当前硬约束。
2. 模块 C/D 的"取重要性最大 3 项 / 文案模板"归属算法侧；本记录只验 EES 透传口径，算法侧正确性不在 EES 单测范围。
3. 数据集 B（S1~S7，20261010/20261011）是本次临时造的 mock，用完可清（`DELETE FROM ees_data.ai_predict_level_reason_detail WHERE type='renew' AND dt IN ('20261010','20261011') AND user_number BETWEEN 900000001 AND 900000007`，快照同步清 scene=1 对应 user_id）。
