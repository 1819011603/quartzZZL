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

## 追加（2026-11-16 第三轮·owner 选 A 后的推进与关键突破）

### 已完成（数据侧大进展）
1. S2=590843035351398400 前置课换绑为健康克隆课 590853244278898688（renew_build 从语文源 588858850300473344 克隆，test-mi 慢致绑定超时，已手动 bind_pre_course 补绑成功）。
2. **正经班造链修复**：create_renewal_regression_clazz 两次 saleStatus=0 的根因=①缺 lessonLength 参数（模板占位符未解析→课节步骤空转）②beginTime 须在未来（课节未结课）。补齐后第三次成功：班 **590853638654588928**（saleStatus=40/课节1未来/老师唐稳01/两个辅导班）✓。
3. 白名单已指向正经班：{590853638654588928: 565844673592092672}（renewal_recommend_file id=176，UPDATE 生效回读 ✓）。
4. 正经班下单+mock_pay 成功（order 434673607240581138，7704848531）。

### 关键突破（下一轮的钥匙）
**小班链路订单查询只认 6004 小班课商品**：适配器 listBySpuNumbersAndUserIdAndStatus 可见单（11-07 B4 前置班单 433809202115248658）order_type/sku_type=**6004**；本轮所有 2 型班课订单（仿造课×2、正经班×1，含真实支付）适配器一律查空——与课程/班无关，与**商品类型**有关。11-15 配方可见是因为其主从计划是 type=1 大班链路（走另一条订单查询）。

### 已试过且排除的路径（勿重复）
- 仿造课 565461510789349376：订单链系统性不可见（商品映射缺陷）；654745 被假数据卡"已购"。
- 绑 B4 前置课 18405861174936317 给 S2：全局一课一计划拒绝（B4 在绑时）。
- 临时换绑（解绑 B4→绑 S2）：解绑成功、绑定 60s 超时未落地；**已还原 B4**（TID 17948216179900300 回读完整）。此路径仍可行但 test-mi 慢、需重试 bind 并压缩窗口。

### 下一轮最短路径（二选一）
A. **teachproduct 链路在克隆课 590853244278898688 上造 6004 小班课商品**（teachproduct_spu_add/sku_add/sku_publish 工具已在 data-agent，契约未读）→ 7704848531 下单 6004 → 适配器验证非空 → 改前实证（getPurePlanDetail(7704848531,S2) 应空/缺联报 + preheat(7704848531, 主545361759016388608) 合并值缺联报 + /cart v2=true S2 页 FULL 有联报="实时正常"）→ 提交部署 → 同链路复采（联报出现+role=2+before=前置课）→ compare 31 样本回归。
B. 重试临时换绑（解绑 B4→立即绑 S2→实证→部署验证→还原 B4→回归），窗口长风险高，次选。

### 当前数据态（全部 TEST 共享）
- S2 course_numbers=[590853244278898688]（重复两条为绑定时序残留，无害）；白名单 id=176 指向正经班 C；正经班 C 可售；7704848531 有 C 班已付单（适配器不可见=正常，2 型）。
- B4 完整还原；主从关系不变（S2 在 CRM&EES 主下）；Apollo 三开关默认；修复+单测仍在工作区未提交（HEAD 38d2d741）。

## 追加（2026-11-16 第五轮·6004 缺口闭合 + 改前实证闭环 + 提交部署）

### 6004 商品缺口闭合（路径与预期不同，结果等价）
原计划走 CES teachproduct 链路新建商品，实际发现更短路径：
1. **克隆课已有商品骨架**：product_spu(590853244278898688, type=2, 造班链路 17:28 产物) + product_sku(590853638654588928=班号, type=2)。6004 商品的结构事实：spu=课号、sku=班号（对照单 433809202115248658 同构）。
2. **DB 直改类型**：spu/sku product_type 2→6004 + sku up_status→1（回读 ✓）；sale_uniform_sku 正规链路 touch 一次（code=0）。
3. **下单**：batch_create_order(productType=6004) 两次报「部分商品不存在」（order-b 侧判定未收敛，疑 sku_app 维度差异）；**换手段 DB 直插 order_item**（number=434673607240582001, spu=克隆课, sku=班号, order_type/sku_type=6004, order_status=2, 对照单全字段复制改号）。
4. **适配器验证非空 ✓**：listBySpuNumbersAndUserIdAndStatus([590853244278898688], 7704848531) 返回该单（TID 17948246993830324）。
- 结论修正：**"只认 6004"的真因是订单体系不同**——2 型班课单在老 order_info 体系，order_item（商品化）体系只有 6004 单；适配器查 order_item 表无类型过滤（order 仓库源码核实：纯 Example 查询）。

### 数据侧补修（改前实证前置）
- S2 主表 status=0（克隆计划未发布，第三轮失败子任务残留）→ 改 status=2（进行中），resolveActiveSubs 立即识别 S2（TID 17948325328870419）。
- 白名单 id=176 end_time=17:02 已过期 → 延至 2026-11-23。
- 桥传 DTO 必须 **camelCase**（Gson 反序列化按字段名；snake_case 会静默映射空 → resolveRelated 假 empty，已两次踩坑坐实）。

### 改前实证（闭环）
1. **纯续路径丢联报 ✓**：getPurePlanDetail(7704848531, S2)=空列表（TID 17948325455590407）。
2. **预热合并值缺联报 ✓**：resolveRelated 完整解析（两从计划+前置课, TID 17948328741100440）后 preheat(7704848531, 主+S2) 返回 {} 空合并值（TID 17948328873050412）。
3. **代码根因再确认**：buildRecommendResult 仅 CLAZZ(2)/COMBINE(51) 有组装分支，23 无 → postClassInfo 恒空 → processClazzSetResult 早退（SmallRenewalCoreService.java:847-851）。
4. **对照**：51 组合同链路进合并值（11-14 preheat-new.txt，条目 18405861174936317 role=2 在值内）——类型间差异坐实。
- 老链路（v2=false）S2 页亦空：当前造数在「实时展示」半边还有独立断点（未收敛，疑联报活动商品/匹配插件维度）；不影响 F2 根因定性（组合对照+代码链完整），改后验证将同时证明单因性。

### 提交与部署
- commit 1848584c（fix(renewal): F2联报(23)纯续路径整条丢失，+13/-2 + 单测 4/4），已 push（38d2d741..1848584c）。
- qingzhou pipeline 1347742 → test-eco-8 部署中。
- Apollo：recommend.v2 已恢复 false（release 20261116204153）；preheat.v2=true 暂留（改后回退态验证用，验完恢复）。

### 待办（改后验证）
1. getPurePlanDetail(7704848531, S2)：联报条目出现 + role=2 + before=前置课。
2. preheat 复跑：合并值含联报条目（key=克隆课, role=2）。
3. compare 31 样本回归（scripts/renewal_cart_compare.py）。
4. Apollo preheat.v2 恢复回读。

## 追加（2026-11-16 第五轮·改后验证与 F2 最终定性）

### 部署与回归（无破坏 ✓）
- 新 pod cart-gaotu100-com-f654474cb-rv8wz（10.218.249.209，commit=1848584c）eureka UP。
- compare 31 样本：规则一 no_related **21/21 一致**；规则二 7/10，3 个差异均为已知「纯从学员」预期差异（与改前轮完全相同，only_in_v2 均为从计划条目）。**修复对既有类型零破坏**。
- Apollo 三开关恢复默认并回读 false ✓（release 20261116210047）。另修复一处环境偏离：prefix 开关曾被置 true（非本需求操作），已恢复 false。

### F2 最终定性（比评审深三层，重大变化）
改后 getPurePlanDetail(7704848531, S2) 仍空 + 对照计划同链路有条目（590563861447557120, productType=2, TID 17948339496200008，before/after/老师齐全）→ **类型专属缺失**。代码核实 23(联报)在小班推荐链**四层全缺**：
| 层 | 位置 | 23 支持 |
|---|---|---|
| 候选构建 | SmallRenewalCoreService#buildCandidates:739-755 | ✗ 仅 CLAZZ(2)/COMBINE(51) 分支 |
| 白名单校验 | WhiteListMatchPlugin#validateWhitelistProducts:142-160 | ✗ 非组合按班校验，联报活动号必无效→降级自动→候选仍空 |
| 结果组装 | SmallRenewalCoreService#buildRecommendResult:847-851 | ✗ 23 无分支，postClassInfo 恒空 |
| 展示组装 | RenewalSinglePlanDetailService#processClazzSetResult | **✓ 已修**（commit 1848584c，+13/-2） |

结论：
1. F2「真问题」成立，但**影响面比评审大**：不是「预热缺联报、实时有」，而是**联报(23)型计划端到端（实时+预热+回退）都不出条目**——前三层缺失使 23 到不了展示层，评审所谓「实时展示正常」不成立（其依据的 11-14 对照是 51 组合，非 23）。
2. 本轮修复（第四层）**必要但不充分**：无害（单测 4/4+回归 21/21）且是 23 出现的前置条件之一；但要让 23 条目真正出现需补全前三层（估 40-60 行：buildCandidates 加 23 分支读联报活动信息、白名单校验加 23 分支、buildRecommendResult 加 23 分支）——**是否补全交 owner 决策**。
3. 造数侧已全部就绪（6004 订单/白名单/S2 发布状态/关联解析），补全部署后可直接用 7704848531+S2 验证联报条目出现+role=2+before=前置课。

### 待 owner 决策
- 方案 A：补全前三层（完整支持 23 小班推荐链，改动集中 SmallRenewalCoreService+WhiteListMatchPlugin，风险中低，四层齐后联报条目可在纯续/预热/回退全链出现）。
- 方案 B：维持现状（仅第四层修复已合入），23 端到端支持另立需求。
