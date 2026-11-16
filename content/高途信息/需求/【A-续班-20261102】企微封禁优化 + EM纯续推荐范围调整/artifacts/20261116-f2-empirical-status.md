# F2 联报修复——实证状态与中断交接（2026-11-16 晚）

## 代码分析结论（比评审更深一层，已代码级核实）

联报(23)在**纯续路径整体丢失**而非仅缺 beforeCourseNumber：`buildRecommendResult`(SmallRenewalCoreService:847-851) 只给 6004/51 填充信息，23 的 postClassInfo 恒 null；纯续路径（预热提取/B端纯续/从计划详情）不经过 `enrichRecommendResults`（只在主计划 FULL 路径调用，:2729-2747 补 23 的 postClassInfo）→ `processClazzSetResult`(:2176-2179) postClassInfo null 早退 → 条目不产出。对照：51 组合在 buildRecommendResult 即填 combineProductInfo（含 preCourseNumber），纯续路径完整（多轮运行时实证）。

推论修正评审 F2 表述：「页面有、预热无」在**大班主计划 A 页面**不成立——A 页实时从计划侧(RELATED_PURE)同样丢；「实时可展示」仅对小班主计划自己的 C 端 FULL 页面成立。真实缺口=**从计划联报在 V2 各链路（实时从计划侧+预热值+回退态）全丢**。

## 修复（已完成但按 owner 硬性要求未提交未部署）

- `RenewalSinglePlanDetailService#processClazzSetResult`：postClassInfo 为空（纯续路径特征）时降级用 `result.getCourseNumber()`（纯续路径=前置课号，未被 enrich 覆盖）组装，before/after=前置课（与 51 组合口径一致）；FULL 路径不动；老类不动。diff +13/-2 单方法。
- 单测 `ProcessClazzSetResultPurePathTest`（TestNG 4/4）：纯续产出联报 DTO(before=前置课)/缺前置课跳过/FULL 不变/extractFromDetail 提取成功。全量 558 跑测=基线 554+4，15 失败为既有 BCartQuerySubBuilderTest 反射问题。
- 影响面评估已闭环：merge 键唯一（validateNoSharedPreCourse 保证）；回退态普通主计划 processClazz 判空跳过（同 51 取舍）；联报型主计划入口 processClazzSet:1746-1749 判空跳过（已知边界，无 NPE）；B 端纯续小班主计划将新增联报展示（与旧小班链联报带前置课口径一致）；老代码对照：老类联报组装同样不设 before（线上行为），旧小班链联报带 before——修复向旧链口径对齐。

## 运行时实证（未闭环——卡在造数，非代码推断被推翻）

对照链有效：51 组合（用户 7704848531，订单可见）在纯续路径/预热合并值/实时 A 页全部出现 ✓——证明"订单可见时链路工作"。

联报链三条路径全卡在「学员在该前置课有**真实可见**订单」这一环：
1. QA 仿造课程 565461510789349376 的班 565461513358360576（saleStatus=50 可售）：两个用户（654745/7704848531）batch_create_order+mock_pay 均返回成功，但 **order 适配器 `listBySpuNumbersAndUserIdAndStatus([课程号], user) 恒空**、orderItemFieldSearch 按单号/支付号/用户均查无——该课程商品 SPU 映射疑似缺陷（订单 spu≠课程号或走桩管道）；654745 还被子任务的半假数据卡"已购买不可重复购买"。
2. 换绑 B4 前置课 18405861174936317（7704848531 有真实可见已付单 sku 589047959231029248）：被产品侧**全局一课一计划**拒绝（"不可绑定存在于其他续班计划中的前置课程"）。
3. `create_renewal_regression_clazz` 在仿造课程上建正经班 590852458012538880：建班/选师/发布步骤跑完但回读 saleStatus=0/课节 0（lesson 步骤返回 null），未达可售门槛，未继续。

已造成的 F2 专项数据（保留，登记 registry plan:590843035351398400）：
- S2=590843035351398400（type=2 小班 + productType=23 联报 + effective，白名单 renewal_recommend_file id=176：前置班 565461513358360576→活动 565844673592092672）
- 关联：DB 直插 renew_master_relation(590845108160000001) 挂 CRM&EES 主 545361759016388608 下（save API 因非管理员被拒；主计划 related 已含 S2，TID 17948199019270270）
- 待补：一个「订单对 order 适配器可见」的前置班+已付学员

## 下一步选项（待定）

A. 修 3 的造数链：排查 create_renewal_regression_clazz 的 lesson/发布步骤为何未生效（11-15 配方当时成功），建成可售班后下单即闭环；
B. 换课程：在新课程（renew_clone_plan/build 或已有可用课程）上重配 S2 前置课+正经班；
C. 请 QA 提供现成联报计划样本（QA 有 51 组合先例，23 联报可能也有现成配置）。
实证闭环后：提交部署修复 → 复采 getPurePlanDetail/preheat/A 页实时（预期联报出现+role=2）→ compare 31 样本回归 → 收尾。

## 状态

- Apollo 三开关已恢复默认并桥回读 false ✓（release 20261116172026）
- 工作区：修复+单测**未提交**（等实证）；HEAD 仍 38d2d741
- 分析项（F3/组合条目/从计划预热评估）已完成 → 见 20261116-review-doc-analysis.md 追加章节
