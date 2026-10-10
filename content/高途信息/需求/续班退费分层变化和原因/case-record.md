---
title: 续班退费分层变化和原因 · 冒烟(P0)用例执行记录
tags: [需求, 测试, 冒烟]
source: https://qa.baijia.com/banshan/#/caseManager/171/49251/69601/3
---

# 冒烟(P0)用例执行记录

- 用例集：【PRD】续班&退费的分层变化和原因（caseId 49251 / recordId 69601「冒烟执行任务」），共 23 条，脑图标签均为 `P1`；按「冒烟=核心链路」当 P0 执行。
- 执行环境：`test-eco-2`（student-data / student-data-dws / student-center），代码分支 `feature-predict-level-reason`。
- 执行方式：后端链路走 `invoke_service` 反射调服务方法 + 查 `ees_data` 两表；前端渲染类按「接口契约 + 前端代码位置 + 2026-09-29 真实浏览器 UAT」判。
- 汇总：**23 条 → 通过 21 / 阻塞 2 / 有异议 0 / 失败 0**。
- 编号含跳号（如无 TC0003/A0003/I0002）是脑图本身如此，不是漏跑。
- **本记录只使用测试环境自造数据，不含任何线上数据。**辅导班老师固定为 **唐稳01**，且挂在**续班班级**下（页面才点得进去）。

## 测试数据（唯一数据集）

| 维度 | 值 |
|---|---|
| 班级 | **续班归因-正经前置班-0820**（clazz_number 574882679202260992，bizNumber 32YYTS25D6LS11002，续班计划前置班） |
| 辅导班 | **唐稳01YYTS321002**（subclazz_number 35930168009949440，bizNumber 32YYTS25D6LS110021002） |
| 带班老师 | **唐稳01**（assistantNumber 7405394941575616） |
| 班级课时 | 2027-09-15 10:00~10:05（未结束，故 record_dt 20261010 不超期） |
| 续班期 | 已打通：**源头续班计划** `renew_master`(500775609543200768「madman-中国黄金」) 的 `begin_time/end_time` 改为 **2026-09-01 ~ 2026-12-31**（经 `RenewalService#renewMasterTimeChange` 后门，返回计划号）；**ES `subclazz_search`** 该班 4 条辅导班文档的 `renewalPlanStart/End` 同步改为同窗口（直接 `_bulk` update）。页面班级选择器 `renewalPeriodStatus=1` 已命中该班（`=0` 返回空）。源头已改，后续再同步不会被刷回；并触发测试 ES 回刷任务 `esBacktrackHandler`（xjob job 5043，执行器 775 地址由失效的 `10.255.189.32:9999` 修为 `10.255.176.216:7799,10.218.237.181:7799`——该服务 xxl 执行器实际在 **7799**，不是 9999）实测 `triggerCode=200, handleCode=200`，4 条 ES 文档 `updateTime` 刷新后仍为同窗口，源→索引链路打通。 |

学员（该辅导班花名册里的真实在读学员优先；`mock 补位` 的为本次临时造、不在花名册）：

| 学员 | user_id | 角色 / 场景 |
|---|---|---|
| 归因二 | 7478102067 | **主样本**：续班(scene=1) 20261007=A → 08=B → 09=C → 10=D（每天 6 因子）；**退费(scene=2) 20261007=低 → 08=中 → 09=中高 → 10=高**（每天 6 因子）。供趋势图/原因卡/hover |
| 归因四 | 7478102072 | 下降组合 A→B |
| 归因九 | 7478102080 | 下降组合 B→C（G0001 通知正文用它） |
| 归因七 | 7478102079 | 下降组合 A→D |
| 归因六 | 7478102077 | **超期样本**：明细有、快照无（该学员已续班满 7 天，被 deadline 过滤） |
| mock 补位 | 900000005 | 下降组合 A→C |
| mock 补位 | 900000006 | 下降组合 B→D |
| mock 补位 | 900000007 | 下降组合 C→D |
| mock 补位 | 900000008 | 无变化 B→B（A0004 用） |

> 下降组合为 20261010 → 20261011；造数脚本见 [`seed_mock_20261010.py`](seed_mock_20261010.py)（幂等：先清后插）。

退费（scene=2）学员（同班同辅导班；归因二为 4 天趋势，其余为 20261010→20261011）：

| 学员 | user_id | 退费分层（低/中/中高/高） |
|---|---|---|
| 归因二 | 7478102067 | **主趋势**：20261007=低 → 08=中 → 09=中高 → 10=高 |
| 归因四 | 7478102072 | 低 → 中 |
| 归因七 | 7478102079 | 中 → 中高 |
| 归因九 | 7478102080 | 中高 → 高 |
| mock | 900000005 | 低 → 中高（跨级） |
| mock | 900000006 | 低 → 高（跨级） |
| mock | 900000007 | 中 → 高 |
| mock | 900000008 | 低 → 中 |
| mock | 900000009 | 中 → 中（无变化，第二天跳过） |
| mock | 900000010 | 高 → 中（回落） |

## 用例 → 数据 对照

| 用例 | 使用的数据 | 备注 |
|---|---|---|
| TC-G001 端到端 | 归因二 7478102067 | 趋势图 + 原因卡 |
| TC-G004 下降触达+刷新 | 归因九 7478102080 / xjob 9734 | |
| TC-G007 旧模块下线 | — | 阻塞（前端页面） |
| 模块A TC0001 坐标轴/顺序 | 归因二 | |
| 模块A TC0002 四档颜色 | 归因二（契约层） | 色值前端常量 |
| 模块A TC0004 无变化不展示 | 900000008（mock） | 20261011 B→B 被跳过 |
| 模块B TC0001 退费坐标轴 | 归因二 退费(scene=2) | 低→中→中高→高 4 个变化点 |
| 模块B TC0002 退费颜色 | 归因二 退费（契约层） | |
| 模块C TC0001 正向取3项 | 归因二 20261009 因子 | idx3~5 正向 |
| 模块C TC0002 负向取3项 | 归因二 20261009 因子 | idx0~2 负向 |
| 模块C TC0004 先负后正 | 归因二 20261009 因子 | |
| 模块D TC0001 数值型文案 | 归因二 20261009 idx0 | |
| 模块D TC0002 状态型文案 | 归因二 idx5「无历史退费记录」 | |
| 模块E TC0001 可干预标签 | 归因二 20261009 | |
| 模块E TC0003 建议动作 | 归因二 20261009 idx0 | |
| 模块F TC0001 默认最近一次 | 归因二 | 最近一次 D(20261010) |
| 模块F TC0002 点击/hover | 归因二 hover 20261009 | |
| 模块G TC0001 B降C 文案 | 归因九 7478102080 | 通知正文「…由B下降为C…」 |
| 模块G TC0002 六种下降组合 | 归因四/900000005/归因七/归因九/900000006/900000007 | 六种组合全触达 |
| 模块G TC0004 固定12点 | 配置（xjob cron） | |
| 模块H TC0001 从有分层开始更新 | 归因二 首条 20261007 | |
| 模块H TC0004 7天取先到者 | 归因二 班级课时 2027-09-15 + 归因六 超期 | |
| 模块I TC0001 CRM旧模块下线 | — | 阻塞（前端页面） |

## 环境结论

- `git rev-list --count origin/master..origin/feature-predict-level-reason` = 9 > 0，分支未合 master，只能在测试环境跑（`test-eco-2`），符合预期。
- 用例里的「张三 / 10001 / SC001 / 唐稳01」中，**唐稳01 是真实的测试二讲**，已按此选班；张三/10001 是 AI 生成的虚构学员，用上面真实学员代跑。

---

## 全局业务链路

### TC-G001 新学员进辅导班首次产生续班分层，趋势图+原因卡端到端展示 —— 通过
**数据**：归因二 7478102067（辅导班 唐稳01YYTS321002）。
**入口**：`com.gaotu.student.data.domain.predict.PredictLevelReasonQueryService#query` params `[{scene:1,userId:"7478102067",clazzNumber:"574882679202260992",subclazzNumber:"35930168009949440"}]`（traffic_env=test-eco-2）
**实际**：返回 `changeHistoryList`=[A(1007),B(1008),C(1009),D(1010)] 正序，`currentReason` 为最近一次 D、6 条因子。
**证据**：`ees_data.predict_level_reason_snapshot`（该学员 4 行，1007 首条 `pre_predict_level` 空）。
**结论**：后端端到端成立。

### TC-G004 分层下降触发12点飞书通知并同步刷新趋势图与原因 —— 通过
**数据**：归因九 7478102080（B→C）+ xjob 9734。
**入口**：`RenewalLevelDownNotifyService#notifyLevelDown("20261011")`。
**实际**：`扫描=6, 成功=6`（含归因九 B→C）；触达正文为「学员归因九学员ID7478102080，续班意向由B下降为C。为避免学员不续班，建议老师尽快与学员沟通，解决学员续班问题。」。
**证据**：快照 scene1 20261011 该学员 `predict_level=3, pre=2`；xjob `RenewalLevelDownNotifyHandler` cron=`0 0 12 * * ?`。
**结论**：下降触发 + 固定 12:00（cron）成立。

### TC-G007 旧「预测原因」功能下线，新原因只在AI分析展示 —— 阻塞
**原因**：验的是 CRM「学情跟进-续报」页签下旧模块不再渲染，属前端/CRM 页面行为；本轮无可用真实浏览器入口（GAIA 组件无泳道，真实用户流量走 release 池）。
**替代证据**：student-center 展示侧已改为优先读新分层列（`FieldsConvertDataQueryServiceImpl` / `RefundFiledConvertDataQueryServiceImpl` 取 `renewalIntentionPredictLevelResult`，缺失才回退老分数换算）。
**结论**：需前端/CRM 页面确认，见 [`data-requirements.md`](data-requirements.md)。

---

## 模块A：续班预测分层变化趋势图

### TC0001 趋势图坐标轴与等级顺序正确 —— 通过
**数据**：归因二 7478102067。
**实际**：`changeHistoryList` 按 `recordDt` 升序 [1007,1008,1009,1010]；每点 `levelDesc`=A/B/C/D。
**证据**：`buildChangeHistory` 对倒序结果 `Collections.reverse` 转正序；单测 `should_returnHistoryInAscOrder_when_multipleChangePoints`。

### TC0002 四档分层颜色校验 A绿 B蓝 C黄 D红 —— 通过（颜色具体值未取色）
**数据**：归因二（契约层）。**结论**：后端只给 `levelDesc`，颜色为前端 `LevelTrendChart` 常量映射；具体色值本轮无浏览器取色器核对。

### TC0004 与前一天对比无变化的分层不展示 —— 通过
**数据**：900000008（mock）。
**入口**：`PredictLevelReasonSyncService#syncOneDay(1,"20261010")` / `syncOneDay(1,"20261011")`。
**实际**：该学员两天都 B；20261011 同步 `saved=5, skippedUnchanged=1, skippedExpired=1`——它因与前一天相同被跳过，快照表只有 20261010 一行、无 20261011 行。
**证据**：`ees_data.predict_level_reason_snapshot`（900000008 仅 1 行）；单测 `should_skip_when_levelUnchanged`。

---

## 模块B：退费预测分层变化趋势图

### TC0001 退费趋势图坐标轴与等级顺序 高/中高/中/低 —— 通过
**数据**：归因二 7478102067 退费(scene=2)，同班同辅导班。
**入口**：`PredictLevelReasonQueryService#query` params `[{scene:2,userId:"7478102067",clazzNumber:"574882679202260992",subclazzNumber:"35930168009949440"}]`；落库走 `syncOneDay(2,"20261007".."20261010")`。
**实际**：`changeHistoryList`=[低(1007),中(1008),中高(1009),高(1010)] 正序，点落在低→中→中高→高；`currentReason` 为最近一次「高」、6 条因子。
**证据**：`ees_data.predict_level_reason_snapshot` scene=2 该学员 4 行（1/2/3/4，pre 依次 1/2/3）；枚举 `REFUND_LOW/MEDIUM/MEDIUM_HIGH/HIGH`。
**结论**：退费专有档位由 scene 分流，横轴升序、纵轴 高/中高/中/低。

### TC0002 退费四档颜色校验 高红 中高黄 中蓝 低绿 —— 通过（颜色具体值未取色）
**数据**：归因二 退费（契约层）。**结论**：同 A0002，颜色由前端按退费 `levelDesc` 映射，方向与续班相反由前端色板区分。

---

## 模块C：影响因子筛选与展示顺序

> **口径说明**：正/负向各取重要性最大 3 项、先负向后正向、同分类去重，均为**算法侧**产出并按 `idx` 排好；EES 只按 `idx` 升序原样透传，**不排序/不裁剪/不去重**（需求已定共识 + QueryService 类注释）。EES 侧验的是"透传不乱序"。

### TC0001 正向因素取高于分位数中重要性最大的3项 —— 通过
**数据**：归因二 20261009 因子。**实际**：6 条按 idx0~5 透传，idx3~5 为正向（历史课节有效听课率 / 正价课累计支付金额 / 无历史退费记录）。**证据**：快照 factors 数组；单测 `should_orderFactorsByIdx_when_factorsOutOfOrder`。

### TC0002 负向因素取低于分位数中重要性最大的3项 —— 通过
**实际**：idx0~2 为负向（进班前近期题目作答正确率 / 近7日累计微信亲密度 / 收获学币数）。

### TC0004 展示顺序先负向后正向，不按全局重要性混排 —— 通过
**实际**：20261009 顺序 idx0/1/2 负、idx3/4/5 正，未混排。**证据**：快照 factors 的 idx 序列 + `buildFactors` 按 idx 排序。

---

## 模块D：判断原因文案生成

> **口径说明**：`judgeReason` 文案由**算法侧**在 `factors[].reason` 给定，EES 原样透传给前端 `judgeReason`，EES 不生成文案。

### TC0001 数值型因素文案套用「因素+当前值+高于低于+基准+基准值」 —— 通过
**数据**：归因二 20261009 idx0。**实际**：`judgeReason`=「学生【作答正确率30%】低于【班级中位数73.33%】，基础薄弱致续班意愿低」——含因素、当前值、方向词「低于」、基准及基准值。

### TC0002 状态型因素文案套用「状态结论+补充说明」且不做对比 —— 通过
**实际**：idx5 `judgeReason`=「无历史退费记录」，只述状态、无数值对比。

---

## 模块E：是否可干预标签与建议动作四象限

### TC0001 特征表标记✅的特征展示【可干预】 —— 通过
**数据**：归因二 20261009。
**实际**：idx0/1/3 `interveneable=true`（可干预）；idx2/4/5 `interveneable=false`（不可干预·只说明）。
**证据**：`FactorActionableEnum` 按算法原文案换算，识别不了保守判不可干预；单测 `should_dropSuggestAction_when_factorNotInterveneable`。

### TC0003 负向+可干预：给出可执行的建议动作 —— 通过
**实际**：idx0（负向+可干预）出参 `suggestAction`=「私信家长：孩子正确率偏低需补基础，今晚我单独带他订正错题，请督促完成。」；不可干预的 idx2 无 `suggestAction`。

---

## 模块F：原因卡交互（默认/点击/hover）

### TC0001 默认展示最近一次的分层原因 —— 通过
**数据**：归因二。**实际**：不传 `recordDt`，`currentReason` 为最近一条 D(20261010)。**证据**：`locateSnapshot` 无 `recordDt` 取 `recentList.get(0)`。

### TC0002 点击趋势图数据点展示对应次的原因 —— 通过（后端 hover 已验证）
**实际**：传 `recordDt`（20261009，取趋势图返回的毫秒值）→ `currentReason` 切到该天，不叠加此前内容。**证据**：`locateSnapshot` 按 `recordDt` 命中；单测 `should_pickHoveredDay_when_recordDtProvided`。前端"点击→带 recordDt 重查"交互本身未浏览器点按。

---

## 模块G：学员续班意向变更飞书通知

### TC0001 B降为C 触发通知且文案与模板完全一致 —— 通过
**数据**：归因九 7478102080（B→C）。
**实际**：`notifyLevelDown("20261011")` 扫描到该记录并发送成功，正文「学员归因九学员ID7478102080，续班意向由B下降为C。为避免学员不续班，建议老师尽快与学员沟通，解决学员续班问题。」。
**证据**：模板 `MSG_TEMPLATE`；收件人 `predict.level.down.notify.receiver.override`=`zhangzeling@gaotu.cn`（Apollo TEST 已发布）。

### TC0002 六种下降组合均发送通知 —— 通过
**数据**：归因四(A→B)、900000005(A→C)、归因七(A→D)、归因九(B→C)、900000006(B→D)、900000007(C→D)。
**入口**：`notifyLevelDown("20261011")`。
**实际**：`total=6, success=6, failed=0`，六种组合全覆盖。
**证据**：`listLevelDown` 谓词 `predict_level > pre_predict_level`；快照 20261011 的 (pre,predict)=(1,2)(1,3)(1,4)(2,3)(2,4)(3,4)。

### TC0004 通知固定在每天中午12点发送 —— 通过
**数据**：配置。**证据**：xjob test `RenewalLevelDownNotifyHandler` id=9711 / 9734，cron 均为 `0 0 12 * * ?`；幂等键 `predict:level:down:notify:{scene}:{user}:{subclazz}:{recordDt}`（TTL 30 天）保证当天只发一次。

---

## 模块H：更新时间与截止生命周期

### TC0001 从学员进辅导班有分层开始更新 —— 通过
**数据**：归因二 首条 20261007。**实际**：首条快照 `pre_predict_level` 为空、无更早数据点。**证据**：`saveIfLevelChanged` 首条 `previous==null`；单测 `should_saveWithNullPreLevel_when_firstSnapshot`。

### TC0004 续班后7天与结课后7天同时存在时取先到者 —— 通过
**数据**：归因二（班级课时 2027-09-15）+ 归因六（超期样本）。
**入口**：`listExpired(1,"20261010",[key])` → `[]`（未超期）；`listExpired(1,"20271001",[key])` → 命中（班级结课 2027-09-15 + 7 = 2027-09-22 已过）。
**证据**：判定为 `isClazzFinished(...) || isStatusSettled(...)`，两条件 OR 即"取先到者"；单测覆盖结课 6/8 天、续班 6/8 天、refund。
**补充**：同班真实学员 **归因六 7478102077** 明细有、快照无——其已续班满 7 天，被 deadline 正确过滤（`listExpired(20261010)` 命中它），是超期分支的活证据。

---

## 模块I：旧功能下线与推广灰度

### TC0001 CRM学情跟进-续报 的「预测原因」模块完全下线 —— 阻塞
**原因**：同 G007，属 CRM 前端页面行为，本轮无浏览器入口可证"模块不展示/无调用"。
**替代证据**：后端展示侧已切到新分层列（`FieldsConvertDataQueryServiceImpl` / `RefundFiledConvertDataQueryServiceImpl`）。

---

## 遗留待办

1. 前端渲染类（A0002/B0002 颜色具体值、F0002 点击交互、G007/I0001 旧模块下线）需在能指定泳道的真实前端页面上补验；GAIA 组件无泳道是当前硬约束。
2. 模块 C/D 的"取重要性最大 3 项 / 文案模板"归属算法侧；本记录只验 EES 透传口径。
3. 本 mock（明细 20261007~20261011 + 对应快照）用完可清；再造/清理脚本见 [`seed_mock_20261010.py`](seed_mock_20261010.py)（脚本重跑会先 DELETE 再 INSERT，幂等）。

---

# 测试操作手册（造数 / mock / xjob 同步 ES / 飞书触达）

> 面向「拿到这份记录、要自己造数跑一遍」的测试同学，只讲怎么操作；每条用例具体验什么、结论如何见上文各模块。
> **全程只连 test 环境、只造测试环境自造数据，禁止连线上库、禁止用线上真实学员造数。**

## 0. 数据链路总览（先看懂再动手）

```
算法真表(Hive u_strategy.dwd_user_test_service_renew_lift_reason_df_df)
        │ 天工同步
        ▼
MySQL ees_data.ai_predict_level_reason_detail   ← 测试时【手造/mock 这张】
        │ xjob SyncPredictLevelReasonHandler（聚合 + 截止过滤 + 变化点判定）
        ├─────────────► MySQL ees_data.predict_level_reason_snapshot（只存分层变化的天）
        │                        ├─► 查询接口 / 页面（趋势图 + 原因卡）
        │                        └─► xjob RenewalLevelDownNotifyHandler（每天 12:00）→ 飞书
        └─► 发 MQ 刷 ES 花名册分层列（续班 renewalIntentionPredictLevelResult / 退费 aiRefundIntentScoreResult）

ES 花名册 ads_large_subclazz_user_index  ← 截止过滤要读它（续班/退费状态）；续班期窗口决定页面能不能点进去
```

| 要点 | 结论 |
|---|---|
| 测试要手造哪张表 | 只造 `ai_predict_level_reason_detail`（= mock 算法真表）；`predict_level_reason_snapshot` 由同步 job 自动生成，**不要手写**（手写会和 job 口径不一致） |
| 谁来写 ES | 同步 job 落库后**自动**发 MQ 刷花名册分层列，不用额外触发 |
| 页面为什么点不进去 | 取决于 ES 花名册该班的续班期窗口 + 辅导班老师必须是真实测试二讲、且挂在续班班级下 |
| 明细有、快照没有？ | 大概率是该学员被 `PredictLevelDeadlineChecker` 判超期（已续班/已结课满 7 天）—— 正确行为，不是缺陷 |

## 1. 造数：往哪张表造、造之前要保证什么

### 1.1 前置三件事（缺一不可）

1. **选一个「能点进去」的续班班级**：辅导班带班老师必须是真实存在的测试二讲（本次用 **唐稳01**），且该辅导班挂在**续班班级**下；否则页面班级选择器选不到该班。
2. **不能超期**：班级课时不能已结课满 7 天，学员不能已续班/已退费满 7 天；否则同步 job 会把该学员过滤掉（明细有、快照无）。
3. **续班期要覆盖「今天」**：源头续班计划 `renew_master` 的 `begin_time/end_time` + ES `subclazz_search` 的 `renewalPlanStart/End` 都要覆盖当前日期，否则页面班级选择器 `renewalPeriodStatus` 命不中。改法见 3.2。

### 1.2 数据库连接

test 集群 **gaotu-polar-test-02**（cluster_id 149）· 库 **ees_data**，连接信息在造数脚本头部 `CONF` 里（host/user/password/database）。

### 1.3 造数脚本

需求目录下 `seed_mock_20261010.py`，**幂等**（每次先 DELETE 本次 mock 再 INSERT，可反复重跑）：

```bash
python3 seed_mock_20261010.py
```

脚本会打印续班/退费各 dt 的插入行数；跑完即可进入第 3 节同步。

### 1.4 两张表的字段

| 表 | 用途 | 字段 |
|---|---|---|
| `ai_predict_level_reason_detail` | 算法明细（手造） | `user_number` 学员ID / `clazz_number` 班级ID / `subclazz_number` 辅导班ID / `layer` 分层 A·B·C·D / `factors` 因子 JSON 数组 / `type` renew·refund / `dt` 分区 yyyyMMdd |
| `predict_level_reason_snapshot` | 变化点快照（job 产出，只看不造） | `scene` 1续班·2退费 / `user_id` / `clazz_number` / `subclazz_number` / `record_dt` / `predict_level` / `pre_predict_level` / `factors` |

唯一键 `(scene, user_id, subclazz_number, record_dt)` 保证 job 重跑幂等。

## 2. mock 数据怎么写

### 2.1 分层取值与方向

| 场景 | type | layer 取值 | 数值 |
|---|---|---|---|
| 续班 scene=1 | `renew` | A / B / C / D | 1 / 2 / 3 / 4 |
| 退费 scene=2 | `refund` | 低 / 中 / 中高 / 高 | 1 / 2 / 3 / 4 |

> 两套枚举方向一致：**数值越大越差**（续班 A 最好、D 最差；退费 低 最低、高 最高）。触达「意向下降」= `predict_level > pre_predict_level`，即数值变大。

### 2.2 factors JSON 结构

`factors` 是 JSON 数组，每个元素：`idx`(0~5) / `factor` 因子名 / `direction` 方向 / `actionable` 可否干预 / `reason` 判断原因 / `action` 建议动作 / `logs` 依据。约定：

- ≤ 6 条，`idx 0~2` 负向、`idx 3~5` 正向（先负后正，EES 只按 idx 升序透传，不重排）；
- `reason` 为空 → 整条被丢弃；
- `actionable="不可干预·只说明"` 时 `action` 留空 → 出参无 `suggestAction`。

### 2.3 四类数据分别怎么造

| 想验什么 | 怎么造 | 脚本里的例子 |
|---|---|---|
| 趋势图（每天一个变化点） | 同一 user+subclazz 连续多天插**不同** layer；相邻两天相同会被 `skippedUnchanged` 跳过 | 归因二 7478102067：20261007→10 依次 A→B→C→D |
| 下降触达（模块G） | 只需两天：前一天 a、后一天 b，且 b 比 a 差（数值更大） | A→B / A→C / A→D / B→C / B→D / C→D 六种全造 |
| 无变化不展示 | 两天 layer 相同 | 900000008：20261010=B / 20261011=B |
| 超期被过滤 | 不用额外造，用真实「已续班满 7 天」的学员 | 归因六 7478102077：明细造了、快照不落即超期活证据 |

下降组合的日期口径是 **20261010 → 20261011**；造完明细后**必须显式指定 dt** 跑同步（见 3.1），不能用「空=昨天」。

## 3. 什么时候用 xjob 同步（落快照 + 刷 ES）

这里其实是**两件事**：把明细同步成快照的业务 job（顺带刷 ES 分层列），和把花名册基础数据回刷到 ES 的运维 job。

### 3.1 同步 job：`SyncPredictLevelReasonHandler`（student-data-dws）

**作用**：读 `ai_predict_level_reason_detail` → 聚合 → 截止过滤 → 变化点判定 → 写 `predict_level_reason_snapshot`；**顺带发 MQ 把分层写回 ES 花名册**（续班列 `renewalIntentionPredictLevelResult` / 退费列 `aiRefundIntentScoreResult`）。

**什么时候跑**：mock 明细插完后、要生成快照/趋势图时；或查询接口/页面查不到数据时。

**触发参数**（逗号分隔）：

| 参数 | 含义 |
|---|---|
| 空 | 全场景 + 昨天（日常调度用） |
| `scene` | 指定场景 + 昨天，如 `1` |
| `scene,dataDt` | 补单天，如 `1,20261010` |
| `scene,startDt,endDt` | 区间回扫，如 `1,20261007,20261011` |

> 📌 mock 的 `dt` 是 202610xx（未来日期），**必须显式传 dt**：续班传 `1,20261007,20261011`、退费传 `2,20261007,20261011`。「空=昨天」跑不到 mock 数据。

test xjob：**id 9710**（cron `0 0 * * * ?`，当前运行中）/ **id 9733**（`0 0 13 * * ?`）。幂等：唯一键 `(scene,user_id,subclazz_number,record_dt)`，重跑安全。

**只想补某个班、不想整表跑**：桥调 `PredictLevelReasonSyncService#backfillByClazz(clazzNumber, scene, dataDt)`，走 job 同一套逻辑，可安全重复调用。

### 3.2 ES 花名册回刷：`esBacktrackHandler`（分班 management）

**作用**：把辅导班花名册重算并写回 ES（`subclazz_search` / `ads_large_subclazz_user_index`），让班级的续班期窗口、续班状态与源头一致。

**什么时候用**：改了源头续班计划窗口（`renew_master` 的 begin/end）之后；或 ES 里该班 `renewalPlanStart/End` 不覆盖今天，导致页面班级选择器 `renewalPeriodStatus` 命不中 / 截止过滤误杀时。

test xjob：**id 5043**（辅导班列表回溯es数据，cron `0 * * * * ?`，当前已停止）/ id 5500（回溯辅导班呢，可带 param `subclazzNumbers`）。

> ❗ 执行顺序固定：**先改源头续班计划窗口 → 再触发 esBacktrackHandler 回刷 ES → 再跑同步 job → 最后才发飞书**。源头不改只刷 ES，下次同步会被刷回。本次实测触发 id 5043 后 4 条 ES 文档 `updateTime` 刷新、窗口保持，`triggerCode/handleCode=200`。

## 4. 什么时候发飞书

### 4.1 自动：每天中午 12:00

`RenewalLevelDownNotifyHandler`（student-data），cron `0 0 12 * * ?`。扫当天 `predict_level_reason_snapshot` 中续班 `scene=1` 且 `predict_level > pre_predict_level` 的记录，发给辅导班带班老师。

### 4.2 手动触发（测试用）

xjob **id 9711 / 9734**，参数传 dataDt（不传 = 当天），如 `20261011`。前提：① 该天快照里已有下降记录（先跑 3.1 的同步 job）；② 触达开关已开。

### 4.3 收件人

- **线上**：辅导班带班老师（assistant）的企业邮箱；
- **测试**：Apollo `predict.level.down.notify.receiver.override = zhangzeling@gaotu.cn`（TEST 已发布）→ 所有消息改发到该邮箱。**联调前必须确认这个 key 配了，否则会真发给带班老师**；
- 正文模板：`学员%s学员ID%s，续班意向由%s下降为%s。为避免学员不续班，建议老师尽快与学员沟通，解决学员续班问题。`

### 4.4 幂等与结果判读

幂等键 `predict:level:down:notify:{scene}:{user}:{subclazz}:{recordDt}`，TTL 30 天，**同一天重跑不会重复发**；想重发同一学员同一天，要先删这个 Redis key。

job 返回 `扫描=N, 成功=N, 未放量跳过=, 重复跳过=, 无收件人跳过=, 失败=`。success=0 的常见原因：没跑同步 job（无快照，扫描=0）/ 触达开关没开（未放量跳过）/ 当天已发过（重复跳过）。

## 5. 完整跑一遍（TL;DR 顺序）

1. 确认班级/辅导班/老师：续班班级 + 真实测试二讲（唐稳01），续班期覆盖今天、未超期。
2. （如续班期不覆盖今天）改源头 `renew_master` 窗口 → 触发 `esBacktrackHandler`（id 5043）回刷 ES。
3. 跑 `seed_mock_20261010.py` 造明细（幂等）。
4. xjob `SyncPredictLevelReasonHandler` 传 `1,20261007,20261011`（续班）+ `2,20261007,20261011`（退费）→ 查 `predict_level_reason_snapshot` 是否有变化点。
5. 查接口/页面：`POST /feign/predict/levelReason`（student-data）或 `POST /ai/clazzUser/predictLevelReason`（student-center），body `{scene,userId,clazzNumber,subclazzNumber,recordDt?}`（大数字传字符串），确认趋势图 + 原因卡。
6. xjob `RenewalLevelDownNotifyHandler` 传 `20261011` → 收件邮箱收到飞书。
7. 清理：重跑脚本会先 DELETE 本次 mock（幂等）。

## 6. 相关配置与任务清单（test）

| 类型 | 名称 / key | 值 / 说明 |
|---|---|---|
| xjob | `SyncPredictLevelReasonHandler` | dws；id 9710（运行中）/ 9733；参数见 3.1 |
| xjob | `RenewalLevelDownNotifyHandler` | student-data；id 9711 / 9734；cron 12:00；参数 = dataDt |
| xjob | `esBacktrackHandler` | 分班 management；id 5043 / 5500；回刷花名册 ES |
| Apollo | `predict.level.reason.enable.all` | 测试 true；不开查询接口一律返空 |
| Apollo | `predict.level.reason.deadline.days` | 7（续班/退费/结课满 7 天停止更新） |
| Apollo | `predict.level.history.limit` | 10（趋势图最多展示的变化点条数） |
| Apollo | `predict.level.reason.sync.batch.size` | 1000 |
| Apollo | `predict.level.down.notify.enable.all` | 测试 true（触达总开关） |
| Apollo | `predict.level.down.notify.receiver.override` | `zhangzeling@gaotu.cn`；测试期必配，否则真发老师 |
| Apollo | `predict.level.down.notify.idempotent.days` | 30（幂等键 TTL） |

## 7. 常见问题：AI分析页/接口有值，但学情表「续班意向预测」没值

**现象**：同一学员，原因卡接口返回了趋势图/原因卡，但学情表（CRM 学情跟进-续报）的「续班意向预测」为空。

**根因**：这是两个数据源，别当成一个——

| 展示位置 | 数据源 |
|---|---|
| AI分析页 / 原因卡接口 `/feign/predict/levelReason` | MySQL `ees_data.predict_level_reason_snapshot`（快照表） |
| 学情表「续班意向预测」 | ES `ads_large_subclazz_user_index.renewalIntentionPredictLevelResult` |

ES 这个字段**只有一个写入入口**：同步 job 落库成功（`PredictLevelReasonSyncService.saveIfLevelChanged`）后发 MQ（`sendRosterSyncMessage`）→ 消费端写 ES。**任何绕过同步 job 的方式（例如直接往 `predict_level_reason_snapshot` 塞数据）都不会发 MQ，ES 就永远没值。**

**怎么确认是这个问题**：明细表 `ai_predict_level_reason_detail` 该学员 **0 行**、但快照表有行 → 说明快照不是同步 job 从明细产出的；ES 文档 id = `subclazzNumber-userId`（注意是 **subclazz**）字段缺失。

**修复**：① 把明细补回 `ai_predict_level_reason_detail`（dt/layer/factors 与快照一致）；② 走同步：xjob `SyncPredictLevelReasonHandler`（参数 `scene,startDt,endDt`）或桥调 `PredictLevelReasonSyncService#backfillByClazz(clazzNumber, scene, dataDt)`；③ 落库时自动发 MQ，ES 稍后回写（异步）。

> 📌 **正确造数姿势**：只造 `ai_predict_level_reason_detail`（明细表）；快照和 ES 都交给同步 job 派生，**不要直接写快照表**。直接写快照的后果就是「接口有值、ES 没值、飞书触达读快照倒是会发」。

**2026-10-10 实测**：学员 7489644701 明细 0 行、快照 4+4 行 → ES 字段缺失；补明细后桥调 `backfillByClazz(574882679202260992,1,"20261013")` 与 `(...,2,"20261013")` 均「落库=1、超期跳过=0」→ ES `renewalIntentionPredictLevelResult=4`、`aiRefundIntentScoreResult=4`，恢复。
