# 业绩归因 - 可续判定

## 2026-09-14 判断"可续"是否要求后置课程下已建班

### 检索信息

- 状态：已解决（代码阅读结论，未做实测班级验证）
- 关键词：可续、续班关系、后置课程、不可续-无续班关系、course_relation_map、can_renewal_status、renewalSignCore
- 关键 ID：无

### 反馈信息

- 反馈人 / 反馈渠道：内部排查（张泽玲）
- 涉及对象：performance-attribution 可续标记逻辑，非具体订单/班级案例

### 结论

不是 bug，是确认代码行为：判断某订单是否"可续"，只要求存在**续班关系配置**（course_relation_map 里 relation_type=1、以当前课程为前置课程、且 calculate_renewal_type≠2），**不要求后置课程（course_number）下已经实际创建班级**。后置课程下没有任何班级时，系统会因为查不到该学生在后置课程下的订单而正常判为"未购"，产出 `can_renewal_status=1`（可续-未续），不会报错、不会空跑，也不会被误判为 4（不可续-无续班关系）。

### 关键证据

- 判 4「不可续-无续班关系」的依据是课程中心课程信息（`courseQueryApiFeignClient.listByNumbers`），不查班级表 —— `AbstractRenewalSignStrategy.java:148-173`
- 取后置课程只查 `course_relation_map` 续班关系 + 续班类型标记过滤，不涉及 clazz 表 —— `RenewalSignTemplate.java:104-118`（取后置课程），`RenewalSignTemplate.java:188-208`（`filterNotCanRenewalCourse`）
- "已购/未购后置课程"判断查的是订单（按 afterCourseNumber 过滤用户订单），无订单则全部落入"未购"分支，正常出可续结果 —— `AbstractRenewalSignStrategy.java:245-290`（分组判断）、`AbstractRenewalSignStrategy.java:535-580`（`signNotBuyAfterCourse`）
- 唯一与班级相关的一处只是圈定订单查询范围（`getClazzNumbersByCourseNumbers`），后置课程无班级时只是少查到几个 clazzNumber，Feign 空结果直接返回空 list，不报错 —— `AbstractRenewalSignStrategy.java:220-233`，`RenewalSignRegularStrategy.java:227-234`
- 全链路（`RenewalSignTemplate.doSign` 全文 74-186 行）未发现"后置课程必须有班级/可报名班级"的校验分支

### 当前状态与处置

结论已通过两轮独立代码阅读交叉验证一致，未做真实订单实测。若后续遇到"后置课程未开班但仍报可续异常"的具体案例，需要用真实订单号跑一遍 `RenewalSignTemplate.doSign` 全链路日志核实。

### 涉及系统

- 仓库 / 服务：performance-attribution（performance-attribution-domain 模块）
- 代码 / 数据：
  - `RenewalSignTemplate.java`（取后置课程 104-118 行、过滤续班类型 188-208 行、doSign 主流程 74-186 行）
  - `AbstractRenewalSignStrategy.java`（renewalSignCore 139-290+ 行，判 4 逻辑 148-173 行，已购/未购判断 245-290 行，signNotBuyAfterCourse 535-580 行，getClazzNumbersByCourseNumbers 220-233 行）
  - `RenewalSignRegularStrategy.java`（227-234 行取订单，调课修正 correctNewLogicV2 519-643 行）
  - 表：`course_center.course_relation_map`（cluster 317，relation_type=1 续报课程、relation_number=前置课程、course_number=后置课程、calculate_renewal_type≠2）
- 排查 runbook：`/Users/gaotu/.claude/skills/attribution-judge-debug/references/can-renewal.md`；memory `project-can-renewal-debug-and-back-sop`
