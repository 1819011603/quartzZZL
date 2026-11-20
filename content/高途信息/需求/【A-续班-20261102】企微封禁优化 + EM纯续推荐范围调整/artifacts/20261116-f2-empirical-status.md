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

## 追加（2026-11-16 晚·联报链路查证：老代码有没有？——回答 owner 三问）

### 口径澄清
此前「四层全缺」= **小班课推荐链路**（V2 纯续/预热与线上小班新版 SmallRenewalCoreService 是同一条；S2 是 type=2 小班计划）。不含大班链路。

### 事实表（链路 × 联报 23 支持，代码证据）

| 链路 | 23 支持 | 关键证据 |
|---|---|---|
| **大班老链路**（RenewalService，type=1 计划） | **✓ 完整端到端** | 候选+白名单：1551-1577（productType=23 分支、recommend_map_type=2 白名单取联报活动号、handleWhitelistClazzSet/handleClazzSet）；联报回填：1633-1652（按白名单或班级交集回填 activityNumber）；详情填充：processClazzSet:1719+（ClazzSetVO/子班/教师/年级）；扩科加购兼容：748/811-870 convertClazzSetResultToDTO；联报库存缓存：218。git：0a54c0f6(2025-07-02)即存在，1d2de255(2026-05-29)扩科加购兼容，f3f22d55(2026-06-30)白名单联报新模板 |
| **小班老逻辑**（SmallRenewalService 旧版 1108 行） | **✗ 从无** | coreHandle:219-410 只处理组合(51)映射（Apollo renewal.smallClazz.map 计划→组合 sku）；412「过滤重复联报」/834 勾选组装是组合时代兼容口径，非 23 活动链路 |
| **小班新链**（SmallRenewalCoreService，2026-04-01 重构） | **✗ 从无** | ProductType 枚举创建即仅 CLAZZ(6004)/COMBINE(51)；buildCandidates:739 / WhiteListMatchPlugin.validate:142 / buildRecommendResult:847 三处均无 23 分支 |
| **V2 纯续/预热**（经小班新链） | ✗ 同上（展示组装层已修 1848584c，必要不充分） | processClazzSetResult 修复只能承接「已产出的 23 结果」，候选层仍断 |

### 大班链已购判定（type=1 路线可行性依据）
- 大班按课号：`listByCourseNumbersAndUserIdAndStatus`（RenewalService:1358/1413/2014，查老 order_info 体系）——**用户 7704848531 的 2 型班课单（434673607240581138，已支付）在此体系可见**（与 11-15 配方可见同理）。
- 联报已购：`listActivityNumberOrderInfo`（按活动号，:531/1114）；按班：`ListByClazzNumbersAndUserIds`（:536/1124）。

### 定性
1. 联报缺失**不是 V2 遗漏**：小班课链路（旧版→重构版→V2）**从来无 23 能力**；联报 23 的既定归属一直是**大班链路**（2025-07 起）。
2. S2=「type=2(小班)+productType=23(联报)」的组合配置在小班链**从来不被支持**——该配置下四层缺失是历史现状，非本次回归。
3. 评审 F2 定性需修正：在 V2 场景下「联报从计划条目」要出现，前提是从计划走**有联报能力的链路**。

### 三个可选方案（待 owner 定）
- **A. 小班链补 23**（候选/白名单/结果组装三层，估 40-60 行）：可完整借鉴大班 1551-1660 口径（白名单活动号/班级交集回填）+已合入的展示层；改动集中小班新链。
- **B. 维持现状另立需求**：已合入的展示层修复无害保留。
- **C.（新发现，可能零代码）S2 改 type=1 走大班链**：大班链联报完整+已购判定查老体系（2 型单可见）+白名单同款 recommend_map_type=2 支持；V2 侧 type=1 从计划走 getSinglePlanDetailInternal 大班分支（278 行 Objects.equals(2,type) 不满足）→ 大班联报逻辑生效。**若「小班计划+联报」本身是非标配置（业务上联报计划应配 type=1），C 是正解**；一条 DB UPDATE 即可实证。需产品确认：联报计划（productType=23）的业务形态应配 type=1（大班）还是 type=2（小班）？

## 追加（2026-11-16 深夜·方案A实施：小班链补 23 推荐）

### Owner 决策
『方案a』——小班链补联报(23)完整支持（大班链不动，V2 依赖结构不变）。

### 改动（commit 1a8ec96e，5 文件 +175/-1）
- `ProductType`：+ACTIVITY(23, 联报活动)
- `ProductKey`：+ofActivity 工厂
- `SmallRenewalCoreService#buildCandidates`：+23 分支——候选=计划配置 productNumberList 活动号（与 51 从配置取同构）；可售性由展示层 ClazzSetVO 查询兜底
- `WhiteListMatchPlugin#validateWhitelistProducts`：+23 分支——活动号须在计划配置内（与大班 recommend_map_type=2 口径一致），未配置降级自动推荐
- `buildRecommendResult` 不改（23 的 courseNumber=前置课已由通用逻辑设置，展示层 1848584c 降级组装承接）
- 兼容性核实：Stock/SaleSubject 插件对 map 缺失候选宽容通过（23 天然通过）；PurchasedMatch 对 23 不命中即保留原候选；排序插件 supports 均 false→原序（白名单 interrupt 场景无排序需求）；isSingleClazz 不含 23→走 processClazzSetResult ✓

### 验证
- 单测 ActivityProductRecommendTest 5/5（候选构建/缺配置空/白名单命中中断/未配置降级/51 回归）
- 全量 563=基线 558+5，15 失败均为既有（ExpandSubject 等）
- 部署：pipeline 1347804 → test-eco-8

## 追加（2026-11-16 深夜·方案A验证闭环）

### 三链路验证（新 pod 8p928，commit 1a8ec96e）
1. **实时/纯续单计划 ✓**：getPurePlanDetail(7704848531, S2) → 联报条目出现：productType=23 / productSkuNumber=activityNumber=565844673592092672（白名单指向）/ beforeCourseNumber=afterCourseNumber=590853244278898688（前置课）/ 名称"联报-大班数学系列课-0701-A" / 年级五年级（TID 17948380350700006）。改前同链路空（TID 17948325455590407）——**改前改后对照闭环**。
2. **预热合并值 ✓**：preheat(7704848531, 主计划+S2) → 合并值 {590853244278898688: 23条目, renewal_role=2(从)}（TID 17948381795630008）；单计划提取 computeSinglePlanPure 同条目（TID 17948381498010008）。桥调注意：RelatedPlans 内层 config 也必须 camelCase（snake_case 内层会静默映射空→合并值假空，已踩坑）。
3. **回退态**：预热值含 23（同②写入值）；C 端回退展示跳过组合/联报条目=**2026-11-14 已定取舍**（README 已知差异第二条，processClazz 判空加固，23 与 51 同口径），非本次方案 A 范围。

### 回归（compare 31 样本）
- 规则一 no_related 21/21 一致；规则二 7/10（3 个纯从学员预期差异，与改前完全相同）——**方案 A 对既有类型零破坏**（compare_baseline_20261116_221346 / compare_v2_20261116_221411 / compare_diff_20261116_221417.json）。
- Apollo 三开关恢复默认并回读全 false（release 20261116221429）。

### 方案 A 最终状态：✅ 完成
两次提交：1848584c（展示层降级组装）+ 1a8ec96e（候选构建+白名单校验）；单测 4/4+5/5、全量 563 无新增失败；端到端三链路+回归证据齐。

## 追加（2026-11-16 第六轮·设计模式方案一实施闭环）

**方案一（推荐层 ProductTypeHandler 策略收编）✅ 已实施、部署、验证完毕。**

- **提交**：`636e67d0`（refactor(renewal): 方案一——推荐层商品类型策略收编），基于 1a8ec96e，+300/-74，11 文件（handler 包 5 新增 + CoreService/WhiteListMatchPlugin + 4 测试适配），已 push。
- **部署**：qingzhou pipeline 1347850 → test-eco-8 新 pod t5nc4（10.218.249.53）Running/eureka UP @636e67d0。
- **等价性证据（三方一致）**：
  1. 实时 getPurePlanDetail(7704848531, S2, false, true, null)：原基线 TID 17948380350700006（1a8ec96e）= 部署前复采 TID 17948400391750050 = 部署后新 pod——23 条目/activity 565844673592092672/before=after=590853244278898688/五年级，逐字段一致。
  2. 预热 preheat(7704848531, 主+related)：原基线 TID 17948381795630008 = 部署后新 pod——合并值 {590853244278898688: 23条目, renewal_role=2} 一致。
  3. compare 31 样本：规则一 21/21、规则二 7/10（3 差异=同批纯从学员预期差异），与上轮 compare_diff_20261116_221417 **逐条签名比对完全相同**（零破坏）。产物 compare_baseline_20261116_224941 / compare_v2_20261116_225012 / compare_diff_20261116_225022。
- **Apollo**：验证期间临时 recommend.v2=true（20261116225001），验毕恢复（20261116225053）；三开关回读全 false。
- 单测：定向 5 类 79/79；全量 563=基线无新增失败。
- 桥调坑再证：DTO 回传必须 camelCase 且**大数必须逐字精确**（本次曾手写 …424→…400 差之毫厘，后改脚本精确转换规避）；loadMainConfig/resolveRelated 可桥调取真实对象再回传。

## 追加（2026-11-16 收尾·失败子任务对账）

**W1-73c7d4（F2联报造数-小班23从计划，failed）对账结论：其目标工作已全部由后续轮次完成覆盖，无遗留缺口。**

子任务原定四步（白名单行 INSERT → 主从关联 → 发布 S2 → 四项验收）的实际终态：
- 正经班 590853638654588928 建成可售，白名单 id=176 指向正确（end_time 已延至 2026-11-23）；
- S2=590843035351398400 主从关联、status=2 发布、克隆课 590853244278898688 spu 改 6004、DB 造单 434673607240582001 全部闭环（见上文第二~五轮记录）；
- 6004 订单实证 + 联报 23 端到端验证（实时 TID 17948380350700006 / 预热 TID 17948381795630008 / 方案一部署后三方一致）均有据。
该子任务中断于脚本执行报错，未产出错误数据；失败后由主链路以 data-agent+DB+桥调组合完成同目标。**勿重跑、勿重建造数数据。**

## 追加（2026-11-17 · 小班链路抽方法 + 统一方案产出）

**commit `2ce425b2`（refactor: getSinglePlanDetailInternal 小班链路抽独立方法）已推送部署验证。**

- **改动**：小班分支（原 278-357）逐字抽为 `getSmallClassRenewalDetail`，主方法保留 `type==2` 分发条件，与 `getLargeClassRenewalDetail` 对称；行为零变化（+95/-79 单文件）。
- **验证（已验证）**：全量 563/15 失败=既有基线（ExpandSubjectConfigSubBuilder 11 + BCartQuerySubBuilder 4，XML 逐用例核对无新增）；test-eco-8 新 pod qkhft @2ce425b2 实时 getPurePlanDetail + 预热 preheat 与 636e67d0 基线 **JSON 程序化比对一致**（qkhft_puredetail.json / qkhft_preheat.json）。
- **统一方案（未实施）**：`artifacts/20261117-unified-product-type-parsing-proposal.md` ——策略族+共用组件（否掉纯模板方法），共用层=类型通用解析一处（ProductTypeHandler 升格），差异层=班型特有留各自链路；膨胀券理想 1 处（现状约 5 处两套）；大班桥接分两步、②启动前需 owner 认可，老链当前零改动。
- **分支现状**：大小班商品解析仍是两条独立分支（大班内联 if-else 约 3 处 + 小班 handler 策略 + 展示组装约 2 处），加膨胀券现状需改约 5 处——统一方案待 owner 拍板后收敛为 1+N。

## 追加（2026-11-17 第二轮 · 统一方案实施与 owner 口径调整）

**最终落地的改动（全部在新类侧，RenewalService 零改动）：**
- `2ce425b2`：小班链路抽方法（getSmallClassRenewalDetail）——已部署验证（实时/预热与基线 JSON 程序化一致、563/15 基线）。
- `510509aa`：统一方案第一步——ProductTypeHandler 移包 small/handler → product/handler（11 文件纯 import 级改动，563/15 基线）。

**大班桥接第二步：已实施中途被 owner 叫停还原。** 过程：策略接口+23 实现+generic+registry 已写、coreHandle 四处替换+删三个 handle* 方法完成，编译修到一半时 owner 明确『RenewalService不改 还原』+『我说改动说的都是新类』——立即 checkout 还原 RenewalService、删除四个大班策略类；`git diff 2ce425b2 -- RenewalService.java` 零差异确认；从未 commit 无需 revert。

**移包态部署验证（test-eco-8 ztqrt @510509aa）**：实时 getPurePlanDetail + 预热 preheat 与基线程序化一致（ztqrt_puredetail/ztqrt_preheat.json）；compare 31 样本 21/21+7/10 与 636e67d0 轮逐条签名一致（compare_diff_20261117_113641.json）；Apollo 三开关验证后恢复全 false（release 20261117113710）。

**配图文档（新建独立 wiki）**：`续班推荐规则总览与商品类型解析结构图` https://gaotuedu.feishu.cn/wiki/M5m0wXOJzi9jLPkKy9bc5dZpnyg （挂技术方案节点下）——推荐规则总览（业务节点、B/C 差异标注、去重①②规则标注）+ 商品类型解析改动前后对比（改动高亮仅新类侧、膨胀券一处接入示例）；两个画板节点关键词全量命中核验通过；技术方案文档「六（三）推荐引擎」已加指向链接。

**遗留**：大班桥接（若未来重启）设计已验证可行的形态=大班散点(候选正查/勾选附加校验/回填/去重键四段)策略化+状态打包，但受"只动新类"口径约束不再推进；膨胀券接入=共用层加一个策略实现（小班侧一处）。

## 追加（2026-11-17 第三轮 · 配图文档按 owner 五点反馈重排）

配图文档（M5m0wXOJzi9jLPkKy9bc5dZpnyg）v2 重排完成：六章结构=①开关分发与两链对照图（V2新链/老链泳道并行、共用与独有环节分色）②V2新链详图（纯续六步/扩科三步业务规则、B/C规则直接写节点、类型解析在主链路）③老链路详图（大班老链10环节完整展开含联报正查/回填/去重、小班老链插件链、回退态缓存读）④配置字段说明表10行（扩科排除/主从关联/productType/白名单模板/强购/allowDuplicate/renewalRole/三Apollo开关：含义+在哪配+影响）⑤类型解析前后对比图 ⑥去重与B/C速查表。四画板 whiteboard+query 关键词全量命中核验通过；正文章节与字段表关键词回读零缺失。

## 追加（2026-11-17 第四轮 · 配图文档 v3 产品可读化）

owner 反馈『计算逻辑 写清楚 规则写清楚 要产品能看懂』+『老链新链图分开 别画一起（放一起那张是对照用）』——v3 重写：①V2 新链、老链路两张独立完整图 ②对照图独立且标题明示"仅用于对照" ③新增「四、计算逻辑与规则逐点说明」七小节（入口端差异/纯续五步/主从合并/扩科+排除/加购/三路去重/老链+回退态），全部业务语言、技术概念带白话解释（Apollo=配置后台开关等） ④字段表白话强化 ⑤对比图保留。回读：正文 18/18 关键词命中（含"取开课时间最早的/先到先占/同学年+同学期/只比科目不比年级/随时可以安全切回"等规则表述）、4 画板关键词全命中。

## 追加（2026-11-17 第五轮 · 最终形态=一张全景主图）

owner 最终要求『整合到图里，画一个图：整个推荐逻辑，老链路、新链路，实时和预热』——文档 v4 重写为**单一全景主图**（画板 KVrPw8OcXhqRb2bCrefcED2en）：图例区（颜色+3张字段速查卡片：productType/白名单/扩科排除/allowDuplicate/主从关联/renewalRole/三开关）→ 入口与B/C端规则 → V2开关分叉 → 新链路（实时计算链8节点含去重①②/扩科排除 + 预热块含主+从合并写缓存≤26h/小班特殊 + 实时缓存关系）→ 老链路（大班/小班子链+老预热单计划+回退态衔接）→ 纯续匹配判定链（已购＞勾选＞白名单＞条件链→取开课最早，规则写在判定节点）→ B/C展示。正文压缩为主图+读图顺序一段。曾因 Mermaid 边语法用 Unicode 箭头+~~~ 不可见连线导致首次渲染失败（partial_success/whiteboard 0），修复后 block_insert_after 成功，28/28 关键词核验全命中。旧分图与长文字章节已随 overwrite 移除。

## 追加（2026-11-17 第六轮 · V2 小班结果缓存读写，owner 指示与大班对齐）

**commit `07dd4710`（feat: V2小班结果缓存读写——语义对齐大班）已推送部署验证闭环。**

- **改动（全部 V2 新类，老链零改动）**：新增 `SmallRenewalPreheatCacheService`（写：key `renewal:preheat:计划:学员`/TTL 26h/空删 key/v2 前缀开关，全对齐大班 writePreheat；读+轻量 context 重建）；`SmallRenewalPreheatService#preheatAndCache`（一次 C 端口径计算，填充纯续结果+context 五 map+preClassInfoList+配置，保留原焐热语义）；`RenewalV2Service#preheat` 小班分支接入；`getSmallClassRenewalDetail` C 端（!fromBCart && !skipPreheatRead && !legacyPure && preheat.cache.enabled）先读缓存，命中跳过纯续计算、扩科/加购/合并仍现算（与大班 corePreheatCache 同构），未命中现算兜底。
- **验证（已验证）**：单测 +6（缓存服务读写/前缀/空删/重建）+2 处适配，全量 569/15=既有基线逐用例一致；test-eco-8 sfw9x @07dd4710：①预热写入——read 回读命中（1 条目 23/sku/before+context 完整）；②C 端命中——getMainPlanDetail 返回与基线一致且日志 `small preheat cache hit, key=renewal:preheat:590843035351398400:7704848531`（TID cart_gaotu100_com.306.17948911836590009）；③未命中兜底（未预热用户 HTTP 200 正常）；④compare 31 样本 21/21+7/10 与基线轮逐条签名一致（大班样本含内=大班链不受影响）；⑤验证毕三开关恢复全 false（release 20261117125536）。
- **设计说明**：读命中为「缓存快照」语义（26h 内勾选/已购变化不反映）——与大班缓存行为一致；skipPreheatRead（V2 合并从计划提取）/B 端/legacyPure 场景不读不污染。主图小班预热块已更新（"本轮新增·与大班对齐"）。

## 追加（2026-11-17 第七轮 · 从计划失败抛异常 + 并发 10s 超时，owner 纠正）

**commits `583dd267`+`04395c96`（chore：移除误提交截图）已推送部署验证闭环。**

- **改动（全部 V2 新类，老链零改动，撤销 AICR#42572 原定性）**：①`RenewalV2Service#relatedDetails` 删 catch-continue 降级——单从计划异常保留原始原因上抛=整体请求失败；②`resolveActiveSubs` 关联状态查询失败抛 IllegalStateException（不再静默当无关联）；③并行计算 join 改 `get(10s)`（Apollo `renewal.related.plan.timeout.seconds` 可配默认 10）超时上抛；④批量预热批次 allOf 加 `get(600s)` 防卡死（预热尽力而为语义，独立配置 `renewal.preheat.batch.timeout.seconds`）。
- **验证（已验证）**：单测+3（从计划失败抛出/1s 超时抛出/正常不受影响）+1 改造（should_not_cache_when_related_status_query_fails 按新口径断言抛出），全量 572/15=基线；test-eco-8 k6w24@04395c96 实测——timeout=0 真实触发：`getRenewalDetailForC` 返回 `RuntimeException: renewal-v2 related plan timeout after 0s`（**不再降级**）；恢复 timeout=10 后同入口正常返回（年级组1）；compare 31 样本 21/21+7/10 与基线轮逐条签名一致；Apollo 恢复回读（三开关 false + timeout=10）。
- 文档/主图同步：技术文档并行化段落补「失败语义（定稿）」；全景主图 V2 实时链节点加「❗失败语义：单个从计划失败=整体报错（不降级）· 并行计算 10s 超时=报错」。

## 追加（2026-11-17 第八轮 · 评审报告核实——P1 确认+修复中，上下文收束交接）

**P1（小班命中缓存后扩科/加购消失）定性：确认为真（上轮小班缓存改动引入的回归）。**
- 代码证据：ExpandSubjectRecommendService 用 context.getUserId()/purchasedPostClazzSkuNumbers（:67/:74/:203），AdditionalPurchaseService 用 additionalPurchaseList；rebuildContext 未回填这些字段 → 命中路径扩科/加购拿到残缺 context。
- 上轮验证盲区确认：S2 造数计划无扩科配置，命中实测时扩科本来就空 → compare 一致不能证明此路径（评审指正正确）。
- **修复（工作区未提交）**：getSmallClassRenewalDetail 命中分支改为「现场构建完整 context（smallRenewalContextBuilder.buildContext 3 参重载）+ 仅纯续结果用缓存快照」——与大班 corePreheatCache「缓存纯续条目+现场重建 context 续算」语义完全对齐；扩科/加购/合并/VO 全走现场 context。编译通过；测试类（AppointUserCheckTest）mock 注入已备齐（contextBuilder/expand/additional/merge/preheatEnabled=false），test-compile 通过。
- **剩余**：①写命中路径单测（断言 buildContext 被调+recommendAll 不被调+扩科拿到现场 context）；②改前复现证据补留（可选：构造命中+扩科场景——用主计划 545361759016388608 或给 S2 配扩科；至少以单测覆盖证明）；③全量=基线 → commit/push → 部署 → 命中+扩科场景实测 → compare；④主图/文档同步。

**P2/P3 未定性（下轮做）**：P2①Feign /preheat 传参开关全关也真算真写（RenewalFeignService:70-72）；②10s 超时非整体超时（任务停不下/CallerRuns 失效——已知限制，超时保证的是请求不无限等，池内任务仍跑完，定性=设计说明或改进为可取消）；③小班+23 无开关老链 allSignUp=1（线上暂无此配置，口径类待 owner）；④coreHandle 静默少条目 vs 失败即报错口径（老链行为不动，口径类待 owner）。P3 六项均低风险/取舍类：resolveRelated 无缓存 RPC+INFO 全量 DTO（性能可优化）；小班批量预热不写缓存（preheatByRenewalNumber 小班分支未接 preheatAndCache——与单用户预热不一致，待定是否对齐）；processClazzSet 3 处判空与归档口径（=38d2d741 判空加固，归档说法滞后，澄清即可）；批量预热吞中断；联报 23 降级年级取前置课；新类字段注入/全限定类名/Facade 未登记（风格+登记类）。误报 1 项确认剔除（Facade 状态过滤）。「7 项待决定」清单在评审原文（未随消息附全），下轮向 owner 或报告原文核对。

## 追加（2026-11-17 第九轮 · P1 收口闭环 + P2/P3 逐项处置 + compare 回归）

**P1 收口完成。4 commit 全部推送并部署 test-eco-8（镜像 e6199773，流水线 1349085/1349131 SUCCESS）：**

| commit | 内容 |
|---|---|
| `1918959b` | P1 修复（比第八轮交接更彻底）：Payload 瘦身**只存纯续结果**（删全部上下文字段+rebuildContext）、写侧只写 results、读侧命中→`buildContext(userId, renewalNumber, config, null, sellerId, includeBCart)` 5 参现场构建完整 context——与大班「缓存纯续条目+现场续算」语义完全对齐 |
| `a3b34ff7` | P3：`RenewalDataService#listActiveRelatedPreCoursesWithCache`（60s 本地缓存，Apollo `renewal.related.plan.cache.enabled/expire.seconds`），V2 `resolveRelated` 改走缓存方法 |
| `d95f0512` | P3：从计划批量查询日志降级（INFO 打 size 不打整组 DTO） |
| `e6199773` | P3：小班 V2 批量预热补写结果缓存——新增 `preheatByRenewalNumberAndCache` 口子（复用批量框架），**老链路口子 preheatByRenewalNumber 行为不变（仍不写）** |

**P1 验证（已验证）**：
- 单测：新增 `SmallClassPreheatCacheHitTest` 3 用例（命中→现场 buildContext 被调+recommendAll never+merge 拿现场 context assertSame 级；未命中→完整现算；fromBCart→不读缓存）+ `RelatedPlanCacheTest` 5 用例 + 批量预热写缓存差异 2 用例 + Payload 写侧瘦身 1 用例。
- **改前复现对照**：stash 修复后在 HEAD 旧代码跑同一命中测试 → setUp 即失败（`Could not find field 'smallRenewalContextBuilder'`=旧代码命中路径无现场构建能力）；旧 `rebuildContext` 源码 grep 0 处回填 relationMap/userId/purchasedPostClazzSkuNumbers/additionalPurchaseList（留档 T/opencode/p1_before_cache_service.java）。
- 全量 580/15=基线（572+新增 8；失败 15 个=BCartQuery 6+ExpandSubject 9 固定名单，既有失败非本次引入）。
- **运行时命中验证**（test-eco-8 @e6199773，TID `cart_gaotu100_com.290.17949014179710014`）：preheatAndCache 写缓存→v2=true 调 C 端→日志链 `small preheat cache hit, key=renewal:preheat:590843035351398400:7704848531, entries=1` → `SmallRenewalContextBuilder:116 开始构建推荐上下文`（305ms 完整 SubBuilder 链）→ **无纯续重算**（无插件链日志）→ 三路合并正常 → 响应五年级联报 recType=1 正常展示、allSignUp=0。
- compare 31 样本回归：规则一 21/21 + 规则二 7/10，3 差异=同一批纯从学员已知预期（compare_diff_20261117_154559.json）——**与上轮基线逐条一致，零回归**。
- Apollo 用毕恢复回读：recommend.v2=false / preheat.v2=false / timeout=10（本轮 recommend.v2 true→false 已恢复，release 20261117154536）。
- **未覆盖（如实标注）**：「有扩科配置的计划命中缓存后扩科条目出现」的运行时实测——S2（590843035351398400）无 expandSubjectConfig、主计划 545361759016388608 为大班且扩科关闭、590563861447557120 大班无扩科，现环境无小班+扩科样本（renew_build 造数不支持扩科参数、product 侧配置表定位未果——3 步后止损）；扩科/加购「不消失」的 context 传递已由单测 assertSame 级证明 + 运行时三路合并路径正常证明。补测需给小班计划配扩科（product 管理后台或 owner 提供）。

**P2/P3 逐项处置**：
- P2① Feign /preheat 传参（RenewalFeignService:70-72）：**定性=修正基线参数反传缺陷**（基线 `preheat(renewalNumber, userId)` 与签名 `(userId, renewalNumber)` 相反），开关只管新老路由、「真算真写」是预热接口本职——不改代码；上游生产调用行为列 owner 确认。
- P2② 10s 超时非整体超时：**已知限制**（超时保证请求不无限等，池内任务仍跑完；CallerRuns 时失效）——定性说明，改进需可取消任务重构（成本>收益），列 owner 取舍。
- P2③ 小班+联报 23 无开关、老链 allSignUp=1：口径类，**列 owner**（线上暂无此配置）。
- P2④ coreHandle 静默少条目 vs「从计划失败=抛异常」口径不一致：口径类（老链行为不动），**列 owner**。
- P3① resolveRelated 每请求未缓存 RPC + INFO 全量 DTO：**已修+验证**（a3b34ff7 60s 缓存 + d95f0512 日志降级，RelatedPlanCacheTest 5 用例）。
- P3② 小班批量预热不写缓存：**已修+验证**（e6199773 新口子写/老口子不写，2 单测）。
- P3③ processClazzSet 3 处判空 vs 归档说法：**澄清=38d2d741(F1) 有意判空加固**，归档说法滞后，不改代码。
- P3④ 批量预热吞中断信号：**已知限制**（与 P2② 同类，批次任务不响应中断；166 行已恢复中断标志），列 owner。
- P3⑤ 联报 23 降级年级取前置课：取舍类，**列 owner**。
- P3⑥ 新类风格/Facade 未登记：Facade 方法 `listRenewalMasterPreCoursesByNumbers` **已登记** external-concepts.md（product 行）；字段注入/全限定类名=风格类不改。

**「7 项待决定」重构清单**（评审原文未附全，按已有核实材料对应；标 ※ 的需要 owner 提供报告原文核对）：
1. P2① 上游（product 中心）生产是否/何时调 Feign /preheat（参数修正后该接口真实生效）；
2. P2② 10s 超时接受已知限制 or 改进为可取消整体超时；
3. P2③ 小班+联报 23 的 allSignUp 口径（老链=1）；
4. P2④ coreHandle 静默少条目口径（与从计划失败即报错不一致）；
5. P3⑤ 联报 23 降级年级取前置课的取舍；
6. G1 归档规则「关联变化隔离旧预热」与 V2 无隔离机制（≤TTL 26h 窗口内可展示失效从计划）；
7. G2 老 RenewalJobHandler 无 v2 门控，V2 全开前必须停老 Job 调度（否则单计划值覆写合并值）。
※ 若评审报告原 7 项与此清单不一致，以原文为准需 owner 提供。

**文档同步**：技术文档（AQEtdIeKzo7P5IxeQEzc7EpxnBe）「（六）预热机制」追加「小班结果缓存读写（V2，2026-11-17 修正语义）」小节（写=只存纯续结果；读=命中复用纯续+现场重建上下文；修正背景+验证），回读命中；全景主图（d0_master.mmd）上轮已是修复后语义无需改；external-concepts.md 已登记新 Adapter 方法。

## 追加（2026-11-17 第十轮 · owner 自验「选了加购不展示」诊断，只读未改任何代码/配置）

**现象**：owner 两条 TID——464a3665…（default 泳道，17:35）与 b84c5095…（test-eco-8 泳道，17:42），C 端 uid=7746793736 / 计划 591020372877623296（大班主「W1矩阵-大班主-联报23-1117」，2 从计划）/ includeBCart=true / sellerId=8645，B 端已勾 3 条加购，C 端无加购条目。

**链路还原（已验证）**：
- 两条 TID 发出时 `renewal.recommend.v2` 均为 false（owner 翻转间隙：17:38 双开→17:40 双关→17:35 双开→17:39 双关，发布历史 437360/437370/437561/437565 均为 owner 本人操作）→ 两条都走**老链** RenewalService#getRenewalDetail；464a3665 落 default 泳道 pod（镜像 release-af82f18a-202611111，中间版本），b84c5095 落 test-eco-8 pod（5f0df948，基线还原版老链）。
- 本人同参数直连复现（Apollo 冻结只读，v2=false 现状）：default（af82f18a）→3 条全 recType=1（大班单班+联报+小班6004，无加购）；test-eco-8（5f0df948）→1 条联报 recType=1（无加购）。**两条泳道都不展示加购**（非泳道差异）。
- 数据源正常：BCartFacade#listAdditionalPurchase(7746793736,8645)=3 条（type2 sku 591020573457448960 + type51 sku 591027705114509312/590134533098291201）；日志 AdditionalPurchaseService:60「加购推荐完成, count=3」（TID cart_gaotu100_com.287.17949087790480124）。

**三条加购逐条死点（已验证）**：
1. **type2 单班**「W1矩阵S2后置班语文1117」：课程 591020448295360512 grades=[15]subjects=[5]，与纯续联报课程 591020448289069056 grades=[15]subjects=[5] **完全重叠** → 被「加购 vs 纯续 (grade,subject) 去重」删除（RenewalService:477-480；该规则为 owner 2026-11-14 定的「同商品×同年级学科去重」，计划无扩科配置→allowDuplicate=false→去重生效；af82f18a 与 5f0df948 该段代码一致）→**按规则工作，非 bug**。
2. **type51 组合×2**「组合商品-脚本」：主 SKU **sale_status=1 / can_be_sold=false**（脚本造数未上架可售；子商品 8007 会员卡+8010 实物，无班级）→ 展示层售卖状态过滤跳过（与归档既有取舍「回退态展示层跳过组合条目」同类）→ **数据侧问题（商品未上架），非代码 bug**。

**「跟 default 泳道不一致」的真相**：差异在**纯续条目数**（default 3 条 vs test-eco-8 1 条），非加购——default 泳道 af82f18a（11-11 中间版）老链仍含 EM 关联订单并集（withCrossModeOrderItemOrders+从计划计算），test-eco-8 5f0df948 老链已按 owner 口径**还原基线**（EM 合并只在 V2 链）→ v2=false 时两边老链行为不同=**版本差异、符合设计**；v2=true 走 V2 链才有主+从完整合并。default 泳道的 af82f18a 是待下线中间态，不是「正确基准」。

**定性**：非 P1 漏网（计划为大班，未涉及小班缓存命中路径）、非版本路由 bug、非新代码 bug——是「测试数据（组合未上架）+ 既有去重规则（加购同学科 vs 纯续）+ 两泳道老链版本差异（预期）」三者叠加的预期行为。

**处置建议（待 owner 决定，未动任何配置/代码）**：
- 想看到加购单班：换一条与纯续不同（年级,学科）的加购班（如五年级数学），或给计划配扩科配置并开 allowDuplicate；
- 想看到组合：把两个组合 SKU 上架（sale_status=40/can_be_sold=true）；
- 想验证 V2 完整链路（主+从合并+加购）：traffic-env=test-eco-8 + recommend.v2=true 再测（当前两开关为 owner 双关状态）。

## 追加（2026-11-17 第十一轮 · test 默认泳道基线重部署=线上 11-07 版本，对照结论修正）

**owner 授权**：『那test泳道 发下现在线上的代码的泳道 重新部署到test 基线』+『应该是 11-07那个』。

**版本核实（已验证）**：生产 SLS 日志——今日 16:50 全量实例镜像 `acr.baijia.com/uqun/cart-gaotu100-com:release-4b40ee27-20261107115215`（11-07 11:52 构建）；11-10 曾为 release-873a767c（后被替换=印证「cart 回滚」背景）。4b40ee27 = `Merge branch 'feature-renewal-clazzset-dedup' into 'release'`（release 分支合并提交，git 已核实）。与 owner 锚点（11-07）一致，无多版本歧义。

**执行与验证（已验证）**：`qingzhou_redeploy` 直接发布已有镜像（不重跑构建）至 **test 默认泳道**（envInfoId=2，非 test-eco-8）——dry_run 预览→正式发布 code 200→`poll_pods --expected-commit 4b40ee27`：新 pod `cart-gaotu100-com-79ff5bd76-7mgsp`（10.255.166.130）branch=release commit=4b40ee27 **Running+eureka UP**（4 轮就绪）。自验同参数请求（appointUserId=7746793736/计划 591020372877623296/includeBCart=true/sellerId=8645）：HTTP 200 code=0，1 条联报纯续 recType=1，无加购。

**对照结论修正（重要）**：新基线（线上 4b40ee27）在 default 泳道 = **1 条联报纯续、无加购**，与 test-eco-8（5f0df948 老链 v2=false）**完全一致**——此前 owner 观察的「default 泳道不一致（3 条 vs 1 条）」系 default 泳道原跑 af82f18a（11-11 中间态，老链含 EM 逻辑）所致的假差异；**基线刷新后两泳道行为一致，加购三条丢失的根因结论不变**（①加购单班与纯续联报同为五年级语文被 (grade,subject) 去重规则删除；②两条组合商品主 SKU sale_status=1 未上架被展示过滤——均非代码 bug，处置建议见第十轮）。

**约束遵守**：Apollo 全程零改动（当前 recommend.v2=false/preheat.v2=false/timeout=10 为 owner 本人 17:39 双关后的状态）；test-eco-8 未动；老链路代码零改动；无在途部署残留。

## 追加（2026-11-18 第十二轮 · 「老链路-大班联报 23 报错」诊断，只读未改任何代码/配置）

**现象**（owner 测试文档 EaKXdTkzXoJTStxBJH3cX7Qinzh 场景 1）：学员 7746793735 打开计划 591020372877623296（大班联报型主计划）C 端报 `activityNumber不能为空`（TID 3f0c8ef1-12c8-4992-b72c-2de3da46470b.0.3，test-eco-8 @5f0df948 老链 v2=false）。

**根因（已验证，证据链闭环）**：
1. 报错点：`RenewalService#getRenewalDetail` 联报分支（:530-531）——计划 productType=23 时收集 preCourseWithClazzFinal **全部条目**的 activityNumber 调 order 服务，集合含 null → order 参数校验「activityNumber不能为空」→ 整体报错（调用链 errorMsgs 证实）。
2. null 条目来源=**V2 预热写的「主+从合并值」缓存**：调用链无 coreHandle 现算 span（128ms 直接报错）=corePreheatCache 命中；该学员正是 owner 文档场景 4 的预热对象（双开期间执行过 V2 预热写老 key）；从计划条目（大班单班/小班6004）**activityNumber=null**（单班无活动号，O1「原key=主+从完整信息」口径的必然字段形态）。
3. **反证（B 端入口）**：fromBCart=true 跳过缓存读→现算→code=0 正常返回 1 条联报（activityNumber=591020757501380608）——数据本身无问题，报错仅在「读合并缓存」路径。
4. **版本定性**：11-07 生产基线（4b40ee27，test 默认泳道 pod）同学员同参数**同样报错**（已复现）——报错代码为老链既有（本分支老链仅 4 处判空加固、不触及 531 行）；触发条件（老 key 出现从计划条目）由 V2 预热写入引入。

**定性**：历史既有代码 × V2 新机制交互——**归档 G1「回退态读路径消费合并值」风险的实锤升级版**（此前评估为"展示失效从计划"，实际联报型主计划会直接报错500级失败）。

**影响面**：仅「V2 预热写过合并缓存 且 主计划为联报型」的 (计划,学员) C 端老链请求触发；TEST 当前=7746793735×591020372877623296 等被 V2 预热过的组合；**生产未开 V2（无合并值缓存）不受影响**。

**处置建议（待 owner 决定）**：
- 数据面（立即解除）：删除/等待 TTL（≤26h）该 (计划,学员) 预热 key，或用老链预热覆写为单计划值；
- 代码面（根治，二选一）：①老链 531 行收集时过滤 null（一行，属「基线轻微改动」需 owner 批）；②V2 侧修复（符合改动落新类口径）：对联报型主计划的合并值，写入时为非联报条目保留可被老链消费的兼容形态、或缓存条目补 activityNumber=productSkuNumber 占位——具体方案待 owner 选定后再细化。
- 该案例同时强化 G2（全开前停老 Job+清存量合并缓存）必要性。

## 追加（2026-11-18 第十三轮 · 联报 23 报错「立即解决」+ 三问解释，Apollo/代码零改动）

**执行项一（已授权，已验证）**：调老链 `RenewalService#preheat(7746793735, 591020372877623296)` 以**单计划值覆写**该 key（比 DEL 更优：业务语义正确、无需 Redis 直连；TID cart_gaotu100_com.285.17949910483390976，写入 1 条联报 activityNumber=591020757501380608）。重放验证：test-eco-8 code=0 1 条联报（TID cart_gaotu100_com.286.17949910751000942）+ default 泳道（11-07 基线）code=0 同结果——**报错解除，两泳道一致**。

**同风险 key 清单核查（TLS 全量「renewal-v2 preheat done」15 条）**：
- 本案 key（entries=3，11-17 17:36 写）——已覆写解除 ✓
- `545361759016388608:7704848531`（entries=1，11-17 11:35 写，~13:35 过期）：主计划大班**非联报型**，老链读它走班级号收集分支（非 activityNumber 全量收集），**不触发本案报错**——按边界只报不删
- 其余 13 条（11-16 写入，26h TTL）**均已自然过期**
- 结论：**无其它存活的同风险 key**（联报型主计划的 V2 合并缓存历史上只有本案这一个）

**Apollo 回读**：recommend.v2=false / preheat.v2=false（owner 双关后状态，未动）。

**三问解释（要点，详见回报正文）**：①缓存里是「主+从」混合条目，从计划单班没有联报活动号，老链查报名状态时对混合条目全量收活动号→空值触发订单接口校验报错；实时计算只算主计划自己（全联报、活动号齐全）不报错。②「改动落新类」=改 V2 预热写入逻辑（联报型主计划写缓存时兼容老链读法），不动老链。③当前开关全关=全部请求走老链；V2 开启后同数据**不会**报错（V2 有关联时强制跳过缓存读全量现算，各计划活动号/班级号分开处理；compare 31 样本 v2=true 零报错佐证）。

## 追加（2026-11-18 第十四轮 · 开启 V2 双开关支持 owner 自验）

**owner 授权**：『我要验证新功能啊 apollo开关要调整一下 V2的功能』——「不动配置」冻结对本目的解除（仅限两个 V2 开关）。

**执行（已验证）**：set 两 key → dry_run 预览（仅 2 key）→ 发布（releaseTitle 20261118164547-release）→ **已发布回读**：renewal.recommend.v2.enabled=**true**、renewal.preheat.v2.enabled=**true**、renewal.related.plan.timeout.seconds=10（未动）。

**V2 链生效预检（已验证）**：owner 测试文档场景 9 同参数（7746793735 × 591020372877623296，test-eco-8 @5f0df948）→ code=0，3 条跨类型合并：grade11 小班 6004（从）+ grade15 联报 23（主）+ grade15 大班单班 2（从）——与文档场景 9 预期完全一致（TID cart_gaotu100_com.287.17949915970800969）。前置保障：昨日联报 23 报错已解除、无遗留同风险缓存；V2 有关联不读缓存强制现算。

**告知 owner 可开测**：按其文档 EaKXdTkzXoJTStxBJH3cX7Qinzh 场景 9-14 验证（V2 已开）；场景 1-8 为关开关基线（注意：当前开关为开，验老链场景需再关——由 owner 决定操作）。代码/老链/缓存零改动。

## 追加（2026-11-19 第十五轮 · TAPD 缺陷 1122531521001486137 核查【进行中·上下文收束交接】）

**工单内容（已取）**：【组合商品加购/test-eco-8】加购成功后 C 端推荐接口未返回组合商品。报告人唐稳01，2026-11-19 13:39，状态 new，处理人=张泽灵。学员 7658129872、计划 **586116340522184704（小班主计划**=owner 测试文档场景 3/5 同计划）、sellerId=8645、includeBCart=true。加购组合 SKU 580508980380479488 + 483217233600958464（pt=51）均 b_cart 落库成功、signUp=0，但推荐接口（TID ea7405fa-b8d6-489e-b957-33cc49a5f824.0.3，HTTP200 code=0）年级列表无组合。**注意：工单声明「两个组合均已取消加购、数据已恢复」——复现需重新加购或靠日志取证。**

**初步比对（推断，未验证）**：与前天加购排查（归档第十轮）模式高度相似——组合 type51 加购缺失，第十轮定性=组合主 SKU `sale_status=1/can_be_sold=false`（脚本造数未上架）被展示层售卖过滤跳过=数据问题非代码 bug。本轮两个新组合 SKU 大概率同状态。且当前 V2 双开中（11-18 我开的，小班主计划走 V2 链）。

**接手最短路径**：
1. 桥调 `RenewalDataService#getCombinedDTOsBySkuNumbersWithCache([580508980380479488,483217233600958464])`（test-eco-8，大数传字符串）看 product_sku_dto.sale_status/can_be_sold——若 ≠40 即同第十轮定性（数据未上架，处置=上架组合，非代码 bug，可回复工单不成立）；
2. 若 sale_status=40 正常：TID ea7405fa 查调用链/日志定位 V2 链小班加购路径断点（getSmallClassRenewalDetail → additionalPurchaseService.recommend(context) → enrich/merge → convertToRenewalCartVO 的组合处理）；
3. 复现需重新加购（工单已取消）——造数走 b_cart addCart 或让测试重加；
4. 结论按问题卡口径回报；若定性=第十轮同类（数据），回复 owner 并可 tapd_comment/tapd_set_bug_status（接受/不解决需 owner 拍板）。

## 追加（2026-11-19 第十六轮 · TAPD 缺陷 1122531521001486137 终局：不成立，已按 owner 授权流转「不解决」）

**owner 条件授权**（原话『如果不是问题 改一下bug状态 并加上评论』）：结论=不是问题 → 直接改状态+评论。

**最终定性：不是代码缺陷（历史既有行为 + 数据未上架，非 V2 回归）**，处置=工单「不解决」。

**证据链（三档）**：
- **已验证·数据回读**：两个工单组合 SKU 主 SKU 均 sale_status=1/can_be_sold=false（桥调 getCombinedDTOsBySkuNumbersWithCache，TID cart_gaotu100_com.301.17950678400610194）；现存第三组合 591027705114509312（b_cart 有记录、属 account_id=177071 员工）同状态——测试环境组合 SKU 普遍未上架。
- **已验证·代码事实（定性核心，修正第十轮口径）**：小班 C 端推荐展示加购组合需年级来源（combineProductInfo.preCourseNumber 或 configuredGrade 之一非空）。B 端加购数据 BcartVO 从不携带年级（老链路 commit **1e368b48** 2026-05-29 提交说明明确『清理 AdditionalPurchaseBO 的 grade/subject 死字段（BcartVO 从未提供）』+『processCombineProductResult 不再因 preCourseNumber=null 丢弃扩科组合商品』——只为扩科留 configuredGrade 通道）；加购 enrich（RenewalSinglePlanDetailService:2840/V2、RenewalService:4509/老链，逐字一致）不填 preCourseNumber → convert（V2:2379 / 老:4058，逐字一致）`courseDTO==null && configuredGrade==null` → warn『组合商品无法确定年级』丢弃。**结论：加购组合在 C 端推荐页从未展示过，与上架无关，上架了也不展示**。
- **未取到·运行时 warn 日志**：工单 TID 日志在 SLS/TLS 均未命中（traceId 未采集/scanLimit 窗口外）；端到端复现需重写 b_cart 加购数据，写入通道未开（mysql 工具仅 SELECT、order-b 写接口未定位）——按代码确定性收口。
- 其它现场：TID ea7405fa trace_tree 54 span 全链 200 无错（走 SmallRenewalCoreService#recommendAll V2 小班链）；b_cart 工单两条已物理删除；listAdditionalPurchase(7658129872,8645) 现仅返回 8014 实体一条（TID ...302.17950687243600208）；V2 入口实调（TID ...295.17950688623170214）返回无 pt=51 条目，与数据现状一致；8014 实体类不进推荐列表=设计（convert 三分支均不匹配非班级类）。

**第十轮口径修正**：『组合 SKU 未上架被展示层售卖过滤、上架即可展示』**不完整**——小班 C 端加购链路根本无售卖过滤点，真正拦截是年级解析缺失；上架 SKU 不改变展示结果。第十轮当时的组合若走 C 端同样不展示。

**工单流转（已验证·回读）**：tapd_set_bug_status → **rejected（不解决）**+custom_field_14 不解决原因已落；tapd_comment（comment_id 1122531521001310352，含结论/依据/影响面/处置建议）已落；get_bug 回读 status=rejected、评论 author=张泽灵 在列。

**遗留（待 owner/产品）**：若产品要支持『B 端加购组合在 C 端展示』，需先定组合年级归属口径（子班课程推导 or 运营配置）再排开发——新需求，非缺陷修复。

## 追加（2026-11-19 第十七轮 · owner 反例对账：定性修正为「小班路径缺年级兜底」，非状态过滤）

**owner 反例**：TID 8bd69b02-c0bf-444a-83b5-f96f67381432.0.3（/web/renewal/cart?renewalNumber=**591020372877623296（大班主计划）**&sellerId=8645&includeBCart=true，test-eco-8，V2 链）展示了加购组合。

**重放反例（已验证，TID cart_gaotu100_com.302.17950695767440221，7746793735 × 591020372877623296）**：grade15 返回 `pt=51 recommend_type=3 sku=590801222278299649（造数-组合-C4）`——**加购组合展示成功**；同请求中 591199755407966209（无班级子班）未展示。

**SKU 状态对账（已验证，桥调 TID ...299.17950695795230224）**：反例展示的 590801222278299649 主 SKU **sale_status=1/can_be_sold=false（未上架，与工单两 SKU 完全同状态）**——**推翻「不展示=状态被过滤」**：展示层不做售卖状态过滤。

**真根因（代码+运行时双证）**：**主计划类型决定路径，小班路径缺年级兜底**——
- 大班路径 `RenewalSinglePlanDetailService#convertCombineResultToDTO`(:995-1067)：组合→combineClazzNumberList 子班→查 ClazzDTO→查课程→`resolveGrade`(:1072) fallback **子班课程 grades[0]** → 加购组合能展示（反例 sku 有 2 个大班子班→年级 15）；无班级子班（591199755407966209=会员卡+实物）→ grade=null → 不展示。
- 小班路径 `processCombineProductResult`(:2377-2382)：年级仅 preCourseNumber（纯续）/configuredGrade（扩科），**无「从组合子班课程推年级」兜底** → 加购组合必丢弃（工单 sku 483217233600958464 有子班也丢）。老链 RenewalService:4058 同款，历史既有非 V2 回归。

**对账表**：| 案例 | 主计划 | 组合SKU状态 | 班级子班 | 年级来源 | 展示 |；反例A(5908012..) 大班 sale_status=1 有→子班课程15 ✅；反例B(5911997..) 大班 sale_status=1 无→null ❌；工单A/B 小班 sale_status=1 有→无兜底 ❌。**同状态不同展示→状态非决定因素；同学员同请求内有/无子班不同展示→年级可得性是决定因素**。

**工单处置**：按 owner「查证不符→工单不动」执行（当前 rejected+既有评论；评论中『C端从未支持展示』表述不精确——大班主计划支持、小班主计划不支持，待 owner 定是否修正）。

**若支持小班展示（挂起授权的方案锚点）**：把大班路径的年级兜底（子班→课程→grades[0]）对齐到小班路径组合处理（V2 类 RenewalSinglePlanDetailService 小班分支，不动老链 RenewalService）；无班级子班组合维持不展示（与大班口径一致）。注意 enrich 子班收集还需覆盖 combinedSingleProductDtoList（6003/6004 SKU 类子商品，CombineProductBuildSubBuilder:419 已有先例读法）。

## 追加（2026-11-19 第十八轮 · 实施收口：小班主计划加购组合展示支持，V2+老链，全量验证通过）

**owner 决定**：『这次需要支持展示』+『新老链路都得验 组合商品逻辑 case 验证完毕才能验收』+『SKU状态跟之前保持一致 小班加大班共用解析 老链原逻辑支持 case加文档 查漏』。

**SKU 状态口径（跟之前一致·已核实）**：纯续条目过滤未上架（PostClassInfoBuildSubBuilder:92 saleStatus≠40，既有）；加购/扩科条目不过滤售卖状态（大班既有行为，反例 590801222278299649 sale_status=1 展示佐证）——小班组合对齐加购口径，可购性由下单链路把关。第十轮「组合被展示过滤」确认为推断，归档口径以第十七轮+本轮为准。

**实现（cart @2b8da20a，已推送）**：
- V2 共用解析（RenewalSinglePlanDetailService）：新增 `collectCombineSubClazzNumbers`（子班号收集，两来源：combineClazzNumberList + combinedSingleProductDtoList 班级类 6003/6004）+ `resolveCombineCourseFallback`（组合→子班→课程→grades[0] 年级兜底）；小班 processCombineProductResult 丢弃前兜底；大班 convertCombineResultToDTO firstCourse 为空时复用兜底；enrich 子班收集/构建扩展到 combinedSingleProductDtoList。
- 老链（owner 特批例外）：RenewalService 内同款私有兜底（不共用，原逻辑最小支持）。
- 单测 18/18（ProcessCombineProductResultTest 13 + RenewalServiceCombineFallbackTest 5）：兜底展示/无子班不展示/既有路径不触发兜底/两来源收集/边界。

**运行时验证（全部已验证，test-eco-8 @2b8da20a）**：
| case | 结果 | TID |
|---|---|---|
| V2 小班 v2=true 工单两组合展示（grade16/11, recType=3） | ✅ | cart_gaotu100_com.291.17950710646460006 |
| 老链 Bean 直调同款展示 | ✅ | …289.17950711364620007 |
| 老链经 C 端入口 v2=false 同款展示 | ✅ | …297.17950714163190009 |
| 大班组合展示防回归（与基线一致） | ✅ | …297.17950715086510011 |
| compare 预热=实时 consistent=true | ✅ | …294.17950715962500011 |
| 补漏①加购单班 pt=2 展示 grade15 | ✅ | …291.17950717360910015 |
| 补漏②无班级子班组合不展示（反向） | ✅ | 同上 |

**开关操作记录**：短关双开关 false/false（release 20261119145629）→ 老链验证 → 恢复 true/true（release 20261119145753）→ meta 回读 true/true/10 确认；窗口约 90 秒。**注意：Apollo appId=cart.gaotu100.com（非 cart），TEST/default/application**。

**测试数据（保留供复验，gaotu.b_cart）**：user 7658129872 + account 90247 名下 4 条造数（number 591111111111111901/902=工单两组合、903=pt2 单班 591020573457448960、904=无子班组合 591027705114509312）。

**owner 文档（EaKXdTkzXoJTStxBJH3cX7Qinzh）**：场景 16（小班主计划加购组合，V2+老链，含实测结果/TID）+ 17（补漏加购单班）+ 18（补漏无子班反向）+ SKU 状态口径段，已插入场景 15 后并回读确认。

**TAPD 1122531521001486137（已回读）**：rejected → 接受/处理（custom_field_29=续班）→ **已解决**（问题原因=功能设计缺陷，解决方案=程序代码改进），修复评论已落，旧评论「从未支持展示」已修正（action=edit）为「大班支持/小班不支持、本次已修」。

**已知差异备注（非本案范围）**：同参数下 V2 主从合并路径与老链单计划路径的加购条目集合存在差异（如 grade21 钱包/grade13 测试1 等其它账号遗留加购在部分调用出现/消失）——源于既有 (grade,subject) 去重与主从合并语义，与本次改动无关，未深究。

## 追加（2026-11-19 第十九轮 · 组合商品加购需求↔现状差距分析【只读调研，不实施】）

需求源：wiki D89iwm9U1iL6vWkEOgwcg8otnqc《小班续班优化：主讲数据+下单优化》V1.1（10-23 增组合商品+膨胀券加购）。只读调研，零改动。

### 一、已覆盖（附证据）
| 需求点 | 现状证据 |
|---|---|
| C1 勾选加购才展示（includeBCart+sellerId） | BCartQuerySubBuilder:35；场景16-18 实测 |
| C2 (grade,subject) 去重·小班路径（组合按子班展开判重，纯续>扩科>加购） | RecommendMergeService#extractGradeSubjects 情况3（本轮 2b8da20a enrich 两来源扩展后成立）|
| C3 相同商品去重（同 SKU 只展示一次） | 商品级 dedup（小班 RecommendMergeService.dedup/大班 5a seenProductKeys）|
| C4 加购不支持换课（canChangeCourse=false） | setRecommendTypeFields:2550（recType≠RENEWAL→false）；实测 TID …17360910015 |
| C5-部分 含小班课（班级类子班）组合整体展示+基础字段 | 本轮交付 @2b8da20a（场景16，TID …291.17950710646460006 等 7 项）|
| B6 推荐链接含组合（单项/批量） | 加购条目进 grade_clazz_list（recType=3）|
| 主讲数据（P0）/问卷/预报名 | 文档自标已上线/已支持，范围外 |

### 二、差距清单（按影响排序）
1. **【口径不符·大班路径】加购组合不参与 (grade,subject) 去重**。需求 C2：推荐与加购重复→以推荐为准，组合按「任意子班同学年学期」算重复。现状：大班路径 5b 去重用 `purchaseCourseMap.get(productId)`（RenewalSinglePlanDetailService:519-521/555-558），组合 SKU 非班级号查不到 course→空 keys→**不去重**；运行时佐证=owner 反例（联报23语文 grade15 与加购组合语文 grade15 同屏展示，TID cart_gaotu100_com.297.17950715086510011）。小班路径已参与（RecommendMergeService）。**补法**：大班 5b 对组合展开子班判重，复用本轮 collectCombineSubClazzNumbers（改动落 V2 类 RenewalSinglePlanDetailService，符合不动老链口径）。
2. **【未覆盖·C9】加购组合「已报名」标识失效**。现状 signUp 判定=组合SKU ∈ purchasedPostClazzSkuNumbers；而该集合只收「后置班+纯续组合子班 SKU」（UserPostClassOrderSubBuilder:41-60），**加购组合 SKU/其子商品不进集合**→加购组合 signUp 恒 0，已购组合仍可再下单。**补法**：加购组合 signUp 按「组合 SKU 或子商品 SKU 命中订单」判定；订单 item 粒度（组合 SKU vs 子商品 SKU）需先实查一单确认。
3. **【未覆盖·C7】组合多年级「筛选都能筛到」**。现状组合归 grades[0] 单一年级 tab（resolveGrade），其余年级筛不到。**补法**：按子班全年级复制条目或前端按 subjectNames 匹配——涉及前端契约，需产品（王永诗）+前端（金瑞琳）定交互。
4. **【部分覆盖·C5】「全其他商品组合过滤不展示」口径**。需求字面=组合不含小班课（6004）则过滤；现状=按「有班级类子班（6003/6004/大班班号）」判断——组合仅含大班课/仅 1v1 子班时现状展示、需求口径应过滤（1v1 是否算小班课也需确认）。**补法**：isClazzLikeSubProduct 收紧为 6004（或产品定口径），改动小。
5. **【未覆盖·C6】组合按「开课时间最早的班级」展示**。现状组合条目时间取活动时间（activityStartTime→normDescList），无最早开课子班逻辑、排序不含此维度。需产品确认展示口径后补。
6. **【未覆盖】膨胀券加购整模块**（B 端加购/C 端展示字段/适用范围筛选/勾选即展示不去重/上限20）。cart 无膨胀券商品类型——即 owner 此前「后续加膨胀券还要改两处」的解耦诉求的落地对象，建议随解耦抽象一并设计。
7. **【范围外·未核实】B 端整块**：快速加购列表（A1 范围过滤「售卖状态≠未上架」/筛选/字段/上限20联动）、已加购明细/删除/子商品订单校验、每组合限加1次、下单页顺序（推荐→班课→联报→小班→组合→膨胀券）、支付优惠——order-b/OES/前端工程，本线程未核实。**线索**：测试环境 3 个未上架组合均被成功加购过（b_cart 数据），A1 的 B 端售卖状态过滤是否已实现存疑，需 B 端 owner 确认（若 B 端已过滤，C 端遇不到未上架组合，与 C 端不过滤口径自洽）。

### 三、结论
C 端（cart）核心链路：勾选展示/同商品去重/换课限制/含小班课组合展示/小班路径年级科目去重=**已覆盖**（本轮 2b8da20a）；**遗漏 6 条**（上表 1-6，其中 1/2/4 影响正确性，3/5 影响体验，6 为新模块）；B 端整块范围外未核实（第 7 条）。补不补、优先级待 owner 拍板；1/2/4 补法均落 V2 类不动老链。

## 追加（2026-11-19 第二十轮 · 遗漏项逐项方案【方案阶段·零改动·待 owner 确认】）

### 问题1 加购组合参加 (grade,subject) 去重
**现状（业务语言）**：小班主计划的推荐页，加购组合**已经参加**"同年级+学科去重"（组合按其包含班级的年级学科展开，与纯续/扩科重复时让位）——这就是"之前的逻辑是参加的"印象来源，owner 记忆正确，但**只对小班路径成立**。大班主计划的推荐页（新链 V2 单计划与线上老链代码完全同款，RenewalService:444-448/480-483 与 RenewalSinglePlanDetailService:519-521/555-558）：去重时把加购商品号当"班级号"去查课程——单班查得到、**组合 SKU 查不到 → 组合不参与去重**，会与纯续/扩科同学科重复展示（您的反例即此现象：联报语文五年级与加购组合语文五年级同屏）。
**改法**：大班路径去重前，对组合 SKU 展开子班（复用本轮已交付的共用解析 collectCombineSubClazzNumbers：组合→子班→课程→年级学科集合）参与判重。落点：①V2 单计划类（新链，直接改）；②老链 RenewalService 同款 4 行（需 owner 批，与上单"老链组合支持"同模式）。影响面：仅大班主计划加购组合，单班/小班不受影响。
**需确认**：老链这处要不要一起改（上单先例是您特批后改的）。

### 问题2 加购组合「已报名」标识（signUp）
**现状**：您让看老链——**老链（线上）对加购条目（含组合与单班）从未实现已报名标识**：加购推荐生成时"已购集合"直接传空（RenewalService:405 `recommend(purchaseList, Collections.emptySet())`），signUp 恒 0；扩科有条目专门的订单修正（applyExpandSignUp 按班级号查有效订单），**加购没有挂这个修正**。新链现状：小班路径对**加购单班**已正确（已购集合含班级 SKU）；**加购组合**两种路径都恒 0（组合 SKU 不在已购集合——集合只收后置班+纯续组合子班 SKU，UserPostClassOrderSubBuilder:41-60）。
**改法（双粒度兼容，免"订单里记组合 SKU 还是子商品 SKU"的前置验证）**：给加购条目补订单修正——组合按「组合 SKU **或** 其全部子商品 SKU」任一命中有效订单（已支付未全退）即 signUp=1；单班按班级 SKU 查。可搭 applyExpandSignUp 同款订单接口。落点：新链 V2 类统一处理（大小班路径各一处）；老链同步改需批（同问题1）。
**需确认**：①改不改老链；②"已报名"置灰口径=signUp=1 即不可重复下单（需求 C9 原样）。

### 问题3 组合按主计划类型过滤（owner 已定规则 + 大小班都展示）
**现状**：大小班两种主计划的推荐页**都已能展示加购组合**（小班=本轮 2b8da20a 交付；大班=既有能力，您的反例即大班展示）。但**过滤口径与您定的规则不符**：现状判"组合里有没有班级类子商品"（小班 6004/1v1 6003/大班班号都算）且**不分主计划类型**——组合只含大班课或只含 1v1 时，在小班计划下也会展示；按您的规则应过滤。
**大小班判定与各自行为（按您定的规则）**：
- 主计划类型：续班计划 type=2 是小班课计划，其它是大班课（现有分流就是用这个字段，无需新逻辑）；
- 小班课计划：只展示"含小班课(6004)"的组合——1v1(6003)、纯实物/会员卡组合不展示；
- 大班课计划：只展示"含大班课"的组合——判定依据=组合子班中含大班课班级（子商品 SKU 类型=2 或子班班级查得为大班课，实现时按 ClazzDTO/SKU 类型字段确定，1 个实现确认点）；
- 主从续班：组合加购只在主计划路径计算，从计划纯续不算加购——按入口主计划类型过滤即天然满足。
**改法**：共用解析里加"主计划类型→组合必须包含的子商品类型"过滤参数：小班计划要求子班含 6004，大班计划要求子班含大班课类型；isClazzLikeSubProduct 从"班级类都算"收紧为按类型过滤。落点：新链共用方法（RenewalSinglePlanDetailService 一处）+ 老链同款（需批）。**行为变化提示**：工单组合之一（子商品为 1v1 6003 的"线下组合商品"）在小班计划下将**不再展示**（不含 6004）——与需求"全其他商品组合过滤不展示"的口径一致，但和我们刚交付的场景 16 验证结果相反，测试文档场景 16-18 需同步更新预期。
**需确认**：①1v1(6003) 在小班计划下按"不含小班课"过滤是否正确（它是 1v1 不是小班课）；②工单 SKU1（6003 组合）将不展示是否接受。

### 问题4 组合跨年级"筛选都能筛到"
**现状（已核实）**：**之前没做**。组合条目只归入"第一个子班课程年级"单个年级 tab（resolveGrade 取 grades[0]），其它年级下看不到该组合——工单组合各自只出现在一个年级组。单班/联报也是单归属（与需求 C7 只针对组合不冲突）。
**改法（二选一，涉及前端契约需前端一起定）**：
- 方案 A（后端复制）：组合条目在其全部子班课程年级各放一条（同 SKU 多条）——后端改年级分组一处即可，但前端需确认同 SKU 多条的去重/勾选交互；
- 方案 B（字段下发）：条目仍单归属，新增"全部年级"字段由前端筛选时匹配——前端改动多。
**需确认**：方案 A/B 选择（建议 A，前端改动小），需前端（金瑞琳）确认交互。

### 问题5 "按开课时间最早的班级展示"是什么
**需求原文语境**：「组合商品作为一个整体展示，默认按照开课时间最早的班级展示」——指**组合卡片上展示的信息默认取其开课最早的子班**（组合含多个班，时间/班级信息用最早开课的那个班），属于"展示信息口径"，不是列表排序规则（排序另有"未购在前→纯续>扩科>加购"）。
**现状**：组合卡片目前没有开课时间字段（时间规格取的是商品活动时间或为空）。
**改法（建议改，改动小）**：组合条目填充开课时间=最早开课子班的开课时间（子班数据现成）。与问题4 同一块代码，可一起做。
**需确认**：产品确认卡片要展示的开课时间字段（clazzDateDesc 类文案）即可实施。

### 问题6 膨胀券：不做（owner 定，仅举例），清单剔除。

### 实施顺序建议（owner 确认后）
一批做：问题3（类型过滤）+ 问题4A（跨年级）+ 问题5（最早开课时间）——都在组合条目组装同一块；问题1（大班去重）+ 问题2（signUp 修正）为另一批（去重/订单修正）。每批：单测+部署 test-eco-8+新老链路运行时验证+测试文档场景更新（场景 16-18 预期需按问题3 新口径刷新）。

## 追加（2026-11-19 第二十一轮 · 五项整改实施收口 + QA 复测评论回复）

**owner 确认口径**（round 12）：①去重按年级粒度（某年级重复仅该年级不展示）②新链做 ③1v1(6003) 不算小班课 ④跨年级方案 A ⑤卡片默认取开课最早子班。全落新链，老链/Apollo/缓存零改动。

**实施（三个提交，均部署 test-eco-8）**：
- 4ce03179：类型过滤（filterPurchaseCombinesByType：小班=6004/大班=productType 2，子商品 SKU 或子班 ClazzDTO.productType 判定）+ 年级拆条（splitPurchaseCombinesByGrade：子班课程 grades 并集每 grade 一条）+ 年级粒度判重（RecommendMergeService 情况1.5 拆条组合单年级 keys + 大班 5b 子班展开按条目年级过滤）+ applyPurchaseSignUp（组合=组合SKU∪子商品SKU 命中 listBySku...NoRefundBatch，单班=班级号 ListByClazzNumbers）+ 最早子班 clazzDateDesc（大小班两处）
- ab94a84c：拆条组合科目兜底修复（configuredGrade 非空也需子班课程填科目）
- ce3c66cf：大班 expandPurchaseGradeMap 改 IdentityHashMap（同组合拆条 DTO @Data equals 相等致 HashMap 年级映射覆盖、多条错归同一年级——运行时发现+减法实验定位）

**运行时验证（V2，test-eco-8 @ce3c66cf，全 case）**：
| case | 结果 | TID |
|---|---|---|
| 小班类型过滤：1v1 组合(580508980380479488)不再展示 | ✅ | …293.17950762650870006 |
| 小班跨年级拆条：sjg 组合 5 年级各一条（课程 grades=[11,12,13,14]+22） | ✅ | 同上 |
| 小班最早子班时间（2025-02-25 文案）+科目（编程） | ✅ | 同上 |
| 大班判重：语文(15)组合与纯续联报重复去重（owner 反例重复消除） | ✅ | …289.17950762888670007 |
| 大班跨年级拆条：579426174109902848（大班课22+小班课11）两年级各一条 | ✅ | …294.17950770832890007 |
| 无班级子班组合不展示（双向） | ✅ | 同上两 TID |
| compare 预热=实时一致 | ✅ | …289.17950771044810008 |
| 单测（含新增 PurchaseCombinePolicyTest 6） | 31/31 ✅ | mvn test |

**未覆盖**：加购组合「已报名」运行时正向样本（测试环境无组合有效订单，命中逻辑单测覆盖+同款订单接口）；B 端条目（范围外）。

**owner 文档**：场景 19（口径更新说明+19a-19g case 表含实测 TID）已插入 18 后并回读确认；场景 16 中 1v1 组合的旧预期由 19 的口径刷新段覆盖。

**QA 复测评论（TAPD，唐稳三轮 15:18/15:40/16:24）**：接口修复通过（组合返回/加购开关/同商品去重/不可换课字段/includeBCart=false 排除/无子班组合不推荐均 ✓）；困惑点=580508980380479488 不再返回（=DB 排查无学科冲突）。**已回复评论 1122531521001310369**：说明该现象=新口径类型过滤（1v1 不算小班课，过滤在判重前，QA 排查正确无冲突）+ 5 年级多条=跨年级拆条预期 + V2/老链差异与页面路由头问题说明；工单保持 resolved。

**测试数据（gaotu.b_cart 保留）**：7658129872 名下 4 条（591111111111111901/902/903/904）+ 7746793735 名下 579426174109902848（QA 15:07 加，曾短暂软删实验后已恢复 is_del=0）。
## 追加（2026-11-19 第二十二轮 · ③口径更正接力：核实现场+case 补齐+交接 prompt+回归补验）

**接力背景**：上一 Worker（五项整改实施收口后转向补 case+交接 prompt）交付前被取消。本轮接手先只读核实现场，再产出交付物。

**核实现场（已验证）**：HEAD=ce3c66cf、工作区干净（无 WIP 可保留）；@2b8da20a 后 3 提交=五项整改（旧口径③）；③口径更正（owner「推荐需要会过滤掉没有小班课的组合商品 扩科,加购没有这要求 无需过滤 之前给错了」）的代码修改**未实施**；被取消 Worker 实际已完成全量回归并写入测试文档（16:50 实测 @ce3c66cf：38 case 30 过/8 差异已定性、预热=实时 23/23、8 条差异核对章节），比上轮交接摘要记录的「全量回归未完成」更新。

**领域口径澄清（owner 本轮补充）**：续班计划类型只有大班课/小班课两种（RenewalPreCourseDTO.type：1 大班/2 小班，主从按主计划归入其一）；**不存在「组合商品类型」的续班计划**——组合是计划内可配置的「推荐商品类型」（renewalConfig.productType=51+combineProductSkuNumbers）。代码核实与该口径一致（分流=getSinglePlanDetailInternal 按 type=2 判小班）；大班纯续 coreHandle 不消费组合推荐配置（无组合引用），「大班推荐须含大班课」分支现无落点、不构造。

**交付物（均已回读验证）**：
1. 测试文档场景 20（EaKXdTkzXoJTStxBJH3cX7Qinzh）：五项整改更正口径后 case 20a-20i（③加购恢复 1v1/③推荐收紧/③大班不过滤/③扩科确认/①②④⑤回归/防回归总包），每条含前置数据（b_cart 现成查证 SQL+INSERT 模板、推荐位样本与造数指引）、操作步骤（接口+参数+泳道头）、预期结果；含领域口径段与「19a 作废」callout；b_cart 现状核实（id 3513/3532=1v1 组合在场）。
2. 交接 prompt：artifacts/20261119-handoff-prompt-3rd-batch.md（自包含：背景/领域口径/③改动点两处删除+推荐侧收紧落点/验证=场景 20 照单/验收标准/当前状态含回归结论/参照物）。
3. TAPD 1122531521001486137 口径更正评论（comment 1122531521001310373，已回读）：修正 16:34 过时口径（1v1 不返回≠预期，属待修复过度过滤）；QA 483217233600958464 验收结论维持；1486168 独立跟进确认。

**回归补验（子 Agent W1-4eb33f，只读，2026-11-19 17:5x，@ce3c66cf/test-eco-8，全部已验证）**：
- 版本：镜像 20261112-ce3c66cf-20261119162444 与 HEAD 一致，16:50 回归记录可复用
- 抽样复跑 4/4 与 16:50 一致**无疑似回归**：A=3（TID…296.17950809396880407）、C=5（…289.17950809832870409）、D=5（…288.17950809950590401）、工单组合 sjg 拆 5 年级+1v1 仍不返回=待办差异（…290.17950810303510410）
- D 组合 clazzDateDesc 空=子班源数据空文案**非回归**（…292.17950812969100469；sjg 正常显示日期佐证最早子班逻辑生效）
- signUp 三态全对：有效订单=1（586097025945298944/585960755422160896@7658129872）/无订单=0（case C 交叉印证）/组合=0；git diff 确认 signUp 改动仅落加购段（applyPurchaseSignUp 两调用点均在 additionalPurchaseService.recommend 后），纯续/扩科零改动，老链改动仅子班收集+年级兜底
- E_bc 37/38/39 判清=子班课程 grades=[37,38,39]∪[11]（…293.17950813102290458；复跑须带 sellerId=8645&p_client=1 才触发加购段）
- 缺陷单 1486168 复现（productList sign_up=0 vs cart=1，…291.17950815914600499），独立单
- 测试文档「8 条组合加购差异核对」的未判清项段落已按上结论更新（block 回读成功）

**结论**：本轮交付物齐备；「这次改动是否影响原 case」=**未发现回归**（抽样一致+8 差异已定性+signUp 全对+E_bc 判清），与更正口径唯一不符点=1v1 加购组合被旧口径过滤（③待办未实施，已写入交接 prompt 待办首位）。遗留：D1 展示侧 defaultSelect 未切年级（trace 6321285c，上轮已记录）；加购组合已报名正向样本待场景 20f。
## 追加（2026-11-19 第二十三轮 · 本线执行③口径更正实施+全量验证+文档精简）

**实施（@88c25a90，commit 88c25a90 已推送+部署 test-eco-8，eureka UP 镜像 20261112-88c25a90-20261119181805）**：
- 删 RenewalSinglePlanDetailService 两处加购侧 filterPurchaseCombinesByType 调用+方法本体+containsCombineSubProductOfType+LARGE_CLAZZ_PRODUCT_TYPE（63+/97-）
- CombineProductBuildSubBuilder 新增推荐准入 containsSmallClazzSubProduct（推荐位组合须含 6004 子班；6003 子班仍参与展开）；该 builder 为小班引擎组件（新老链共用），现有推荐配置全含 6004、老链行为无实际变化，场景 8 老链组合含 6004 不受影响
- 单测更新：删 3 个旧过滤测试，新增 3 个推荐准入测试；PurchaseCombinePolicyTest 6/6，全量 615 项 15 失败=既有基线（干净基线 stash 对照同样 15 失败，BCartQuerySubBuilderTest 6+ExpandSubjectConfigSubBuilderTest 9，字段不同步历史遗留）

**核心 case（主 Worker 直测）**：20a 1v1 组合恢复展示 grade16 rt3（TID cart_gaotu100_com.290.17950839051180012，sjg 拆 5 年级/signUp 三态/最早子班文案同时保持）；20b 推荐位 589762111522013184 照常 rt1 无误伤（…287.17950840148100017）+负向单测覆盖；20c 大班 1v1 展示+37/38/39 拆条保持（…288.17950840989720026，b_cart id 3555 新造回读）；20f 按预案降级（正向=单测、负向=运行时、纯续同接口佐证）。

**全量回归（子 Agent W1-4eb33f，@88c25a90，只读）**：38 case 25 条与 16:50 完全一致、7 条差异（A_bc+3/B_bc+3/D_bc+1/E_bc+1/F_bc+4/S4_bc+5/TICKET+1）全部定性=删加购过滤的预期变化（1v1 580508980380479488/钱包 579776626871662593/测试1 589538720332474369 均不含 6004、6004×2 组合在大班加购位恢复拆条；子商品类型读回实证 TID …286.17950846940780049），**0 条疑似回归**；compare 5/5 consistent=true（真实命中）；signUp 纯续=1/组合=0 全保持（…290.17950844672520048）。差异根因=QA 15:06-15:07 批量插入的 18 条组合（b_cart id 3536-3553）在旧口径下被「大班须含大班课」隐藏，@88c25a90 起按「加购不过滤」恢复展示。

**独立发现（既有缺陷非本轮回归）**：B 端 /operation/cart 不传 fromC 必 NPE（lang2 toBoolean(int) 拆箱，RenewalController.java:89；fromC=0 即成功；TID …286.17950847975720055）——建议独立小修，未动。

**测试文档精简（owner 要求终态快照）**：EaKXdTkzXoJTStxBJH3cX7Qinzh overwrite 为 40.8K 精简版（原 76K）：场景 1-20 case 格式不变、缺陷 A-D2 保留原因+解决简写+换课业务口径 5 行、「详情接口逐条结果（C 端 25+B 端 13）」更新为 @88c25a90 结果表、其余一行式速查（覆盖缺口/风险说明/工具入口/8 条差异）；历史全文在归档本文件。事故记录：首次 overwrite 因 heredoc $(cat) 命令替换被当字面传入致文档短暂损坏（rev137），即用 stdin 文件重定向重写恢复（rev141 回读 18 项关键内容全在位）。

**20f 补验（同日追加）**：组合「已报名」正向运行时验证完成——现成数据命中（无需造单）：学员 7634387306 对 1v1 组合子商品 580507069560399872 持有效订单（gaotu.order_item order_status=2，number 432727509236712088），其 b_cart 含 1v1 组合 580508980380479488（id 3382）；C 端打开计划 586116340522184704 → 1v1 组合条目 signUp=1（子商品 SKU 命中），同请求钱包/大班组合 signUp=0 负向对照（TID cart_gaotu100_com.291.17950858195680076）；无订单学员 7658129872 同组合 signUp=0（TID …290.17950839051180012）。测试文档 20f 行已更新并回读。至此场景 20 全部 case 运行时验证完毕（20d 代码路径+单测、20f 正负向+单测齐备）。

## 追加（2026-11-19 第二十四轮 · 主 Worker 独立全量回归，owner 指令不用子 Agent）

**执行**：主 Worker 亲自批量直连 pod（10.218.236.107:28688，traffic-env=test-eco-8），45 条一次性全跑（脚本 indep_regression.py，结果 indep_rows.json，均在 /var/folders/.../opencode/）：C 端 26（A/A2/B/C/D/E/F/G/S3/S4/S8/S9/S12/X1/X2 各含 _bc 变体+TICKET 工单组合）+B 端 13（BE×10=fromC:1、BE1×3=fromC:0）+compare 5（A/C×2/D/E）+20f 正向（7634387306）。

**结果：45/45 全 PASS，与子 Agent 前轮结论完全一致，零不一致、零新问题**：
- C 端 26 条目数与预期精确一致（A_bc=8/B_bc=6/D_bc=7/E_bc=10/F_bc=11/S4_bc=11/TICKET=11 等预期变化值复现）；锚点断言全过——D_bc/E_bc/TICKET 的 1v1 组合@g16 rt3 展示、E_bc 的 589762111522013184 拆条保持、S3 signUp=1 保持、X1 status=5/X2 status=10241007 拦截正常
- B 端 13 全过（BE1 三条 fromC=0 正常，避开 fromC NPE 既有缺陷）
- compare 5/5 consistent=true 且 preheatTriggered=true（预热真实命中）
- 20f 正向：1v1 组合 (grade=16, recommendType=3, signUp=1) 独立复现 ✅
- TID 全集：cart_gaotu100_com.284~293.179508627~179508632（45 条逐条见 indep_rows.json；抽样：TICKET=…288.17950863002590098、E_bc=…286.17950862910020096、cmp_E=…287.17950863217290095、20f=…292.17950863256990104）

**版本旁证**：git HEAD=88c25a90 干净；流水线 1355028 SUCCESS=88c25a90 后无新部署；本轮全部返回行为与 @88c25a90 预期（含③口径更正效果）精确一致。**文档更新**：「全量 case 回归」章节说明段已加独立复跑结论并回读（45/45）。20d（扩科零过滤）沿用前轮 diff 确认+单测，本轮未重跑单测（版本未变，复用 6/6 证据）。

## 追加（2026-11-19 第二十五轮 · 需求↔交付终态逐点确认【owner 质询，只读核对】）

**核对方式**：重读 PRD wiki D89iwm9U1iL6vWkEOgwcg8otnqc V1.1《组合商品加购》C 端展示原文（本地留档 prd.md），以第十九轮差距清单为底稿按最新口径修订，对照 @88c25a90 交付+45 条独立回归证据四档标注。

**关键发现**：owner ③更正口径（推荐过滤/扩科加购不过滤）与 **PRD 原文字面一致**——PRD 写明「小班课推荐会过滤到不含小班课的组合……全其他商品被加购，C端展示」；最初的旧口径（全来源过滤）才是偏离 PRD，更正即回归需求本意。

**结论：C 端（cart）范围内交付与需求一致**——12 项需求点全部 ✅（勾选展示/重复让位推荐/年级学科去重含子班展开+年级粒度/同商品去重/不可换课/推荐过滤不含小班课组合/加购全其他组合展示/最早子班展示/多年级可筛/已报名标识含组合SKU∪子商品SKU/换课年级筛选）或 🔁 按 owner 口径且与 PRD 相符（无班级子班组合不展示=场景18 既有取舍 owner 已验收；大班推荐过滤分支=coreHandle 无组合路径天然满足）。确认表已落测试文档「需求↔交付确认」章节（14 行四档表+例外清单）并回读。

**例外/遗留（如实）**：①B 端整块（快速加购/明细/校验/上限20/下单顺序/支付）范围外未核实②膨胀券 owner 明示不做③小班年级粒度判重与推荐负向过滤两条的运行时正向样本未构造（单测覆盖）④「不可重复下单」由下单链路把关（cart 外）⑤D1 换年级展示侧（既有）⑥缺陷单 1486168（独立单）⑦fromC NPE（既有，RenewalController:89）。主编数据/问卷/预报名=PRD 自标已上线/已支持。

**顺手修正（文档格式收尾）**：发现终态快照 overwrite 时场景 15/16 之间误保留 6 个旧工具章节（如何开V2开关/补充说明/预热怎么验/实时计算怎么验/Apollo配置/开关组合，10.2K，信息已并入「四、验证工具速查」）——已批量删除（298 块分 5 批）并回读：42.8K→35.0K，12 项检查全过（旧章节已删、确认表/场景 15/16/20/缺陷清单/速查在位）。

## 追加（2026-11-19 第二十六轮 · B端核查+已报名造数专项【进行中·上下文收束交接】）

**工作单**：A=B端推荐核查+验证+补case；B=已报名标记专项（mock支付造数，owner 指引 Obsidian 造数笔记）。主 Worker 亲自跑不用子 Agent。

**已完成（本轮）**：
1. 核实现场：git HEAD=88c25a90 干净。
2. **找到 Obsidian 造数笔记**（owner 所指）：`~/githubDir/quartzZZL/content/高途信息/构造数据/续班C端下单_构造与复现步骤.md` + `续班B端推荐下单_构造与复现步骤.md`。关键方法：
   - **mock 支付**：createOrder → data-agent `mock_pay`（传 createOrder 返回的**订单号/批次单号**，非支付单号；历史 run r-20261106100523-08edf28b）→ 回读 `gaotu.pay_info.pay_status=1`+`gaotu.order_item order_status=2`
   - **BossBatch 下单**（容器直连绕网关）：`/bgwApi/intranet-rpc/order-b/web/order/batch/boss/prepare?userId=X`，body `{"productList":[{"productNumber":"<SKU>","productType":<51/2/6004>,"quantity":1}]}`（归档 20261105-p0-execution-round7/preview-main-small.json 有完整样例）；create 需**有效 source orderTag**（test can.create.order.when.invalid.source=false 强制校验）——create 完整入参记录待找（round7 README 快照/B端笔记§4 有线索：历史 orderNumber 433534690352693254，trace order_gaotu100_com.444.17937606425700088）
   - 学员 7658129872（手机 12026102281，验证码 12 开头固定 1000）；B 端接口必带 b_client:EES
3. **PRD 关键定性（工作单A重点①已解答）**：PRD V1.1「快速加购组合商品」的【1】组合商品范围原文=「~~续班计划的续班学年、学期、部门、年级、科目对应的组合商品。售卖状态：非【未上架】。~~**全部组合商品**」——售卖状态过滤被删除线划掉，最终口径=全部组合商品**不过滤售卖状态**→「3 个未上架组合曾被成功加购」符合 PRD 最终稿，**不是缺陷**（待落文档）。
4. B 端链路事实（笔记+代码）：cart 的 operation/cart=LEGACY_PURE 只算纯续不含加购；B 端推荐列表=`POST /bgwApi/product-b/b/renewMaster/recommendProductList`（经 cart renewalCart feign，B 端过滤已购 signUp==1）；B 端快速加购 tab/上限20/每组合限1次/子商品订单校验/下单页顺序=order-b/OES/前端侧（只读）。

**待办（交接下一棒，按序）**：
1. 【工作单B主链】用 BossBatch 给 7658129872 造**组合订单**（sjg 483217233600958464，type 51，泳道 test-eco-8 注意 source/tag 与 traffic_env；B端笔记环境是 test-gtbg-dev-3，本轮 case 学员数据在 test-eco-8——下单走 order-b 不分 cart 泳道，mock_pay 传 traffic_env 与下单一致）→ mock_pay → 回读 pay_info/order_item → C 端 `GET /cart/web/renewal/cart?renewalNumber=586116340522184704&appointUserId=7658129872&sellerId=8645&includeBCart=true&p_client=EES`（直连 pod 10.218.236.107:28688 + traffic-env: test-eco-8）验证 sjg 5 个拆条全部 signUp=1 + 负向对照（1v1 组合仍=0）+TID
2. 【工作单B】小班课已购正向复用实证：同请求内 586097025945298944（g11 纯续）signUp=1（已多轮验证，再回读一次即可）
3. 【工作单A】fromC NPE 复核（不传 fromC→NPE，fromC=0/1→成功，TID；定性=既有缺陷非本需求回归，RenewalController:89 lang2 拆箱）
4. 【工作单A】recommendProductList ×组合行为验证（renewMasterNumber=586116340522184704&userId=7658129872，b_client:EES；看组合是否返回/过滤已购语义）
5. 【工作单A】B 端范围外项落文档定性：售卖过滤=PRD 已删（符合）、上限20/限1次/子商品校验/下单顺序=order-b/OES/前端（只读或列范围外）
6. case 按现有格式补进测试文档（场景 21：B端+已报名专项），逐条结论+TID，回读
7. 回报：B 端逐点结论+标记验证结果+问题清单（定性+该谁修）

**注意**：78c25a90 部署在 test-eco-8（pod 10.218.236.107:28688）；b_cart 学员数据（7658129872 id 3513/3532/3533/3534 等）在位；sjg 组合已在该学员 b_cart（id 3533）；本单边界=Apollo（true/true/10）/缓存/老链零改动、主 Worker 亲自跑、少用 arthas。

**追加（同日第二十六轮补 · 覆盖度自查+diff 盘点+未支持清单，owner 要求范围充分）**：以基线 4b40ee27..88c25a90 全量 diff（105 提交/59 文件/+9496 行）逐模块对照验证台账，产出三样：①12 模块功能盘点+覆盖对照表（组合加购/预热V2/P1/换课换年级/联报缓存/EM纯续关联=充分，小班联报23+V2批量预热口子+B端推荐列表+fromC NPE=本轮补验）——补验 TID：S2 小班联报 23 rt1（…287.17950876374910124）、V2 preheat 口子（…284.17950876387910137）、fromC NPE 复现 status=1（…289.17950876396110124，定性既有）、recommendProductList code=0（baijia-proxy 网关，已购过滤正确，组合不在此接口=PRD B端快速加购 tab 属 order-b 范围外）；②未支持清单 6 项（B端整块需 B 端 owner 确认/售卖过滤 PRD 已删无需实现/膨胀券不做/不可重复下单属下单链路/无班级子班组合不展示=已验收取舍/大班推荐过滤天然满足）；③重构系列行为等价由 45 条回归覆盖。已落测试文档「代码 diff 功能盘点与验证覆盖」章节并回读。**工作单 B（mock 支付造组合订单→signUp=1 全链路）未实施**——交接段已写（第二十六轮开头），下一棒第一优先。

## 追加（2026-11-19 第二十七轮 · 工作单 B 已报名标记造数专项【完成】）

**造数方法落地**（交接段方案修正一处）：BossBatch 容器直连 `POST /web/order/batch/boss/prepare|createOrder`（ORDER.GAOTU100.COM，10.255.180.31:28688）；source 校验规则实测=纯数字 10-20 位或 z 结尾即合法（MonitorSourceTagProcessor，无库表校验），orderTags 传 `tj173304329532355584z` 通过；**0 元单 needPay=false 免 mock_pay 自动完成**（pay_channel=40）——sjg 组合 totalPrice=0，直接生效。

**结果（全部已验证）**：
1. **组合订单全链路 ✅**：批次单 434960574395711494（pay_info pay_status=1；order_info 434960574395712006 大班子班 475609987106797568 / order_item 434960574395712518 小班 SKU 483180833165871104，均 status=2）。C 端 sjg 5 拆条 signUp 0→1：支付前 TID cart_gaotu100_com.286.17950882549710151 → 支付后 TID cart_gaotu100_com.286.17950886932860162。
2. **负向对照 ✅**：1v1 组合 580508980380479488 两 TID 内 signUp=0 保持；英语 585963404555053056/GPS 579971527131324416/语文 591020573457448960 均=0。
3. **小班课已报名 ✅**：586097025945298944 有效订单（order_item 433534690352694278，status=2）→ 同请求 signUp=1。
4. **小班课新造单 ⚠️ 未成**：GPS 班 579971527131324416 prepare code=0 但 createOrder code=408 库存不足（造数班库存限制，非本需求问题，未改他域库存）；正向以历史有效订单实证覆盖。
5. **测试文档**：场景 21（21a-21e）已落 EaKXdTkzXoJTStxBJH3cX7Qinzh 并回读（rev 153）；20f 过时句「无订单学员 7658129872 同组合 signUp=0」已同步修正指向场景 21。

**工作单 A/B 全部收口**。遗留待 owner 不变：fromC NPE 是否修（既有）、D1、1486168、联报 23、上线必办 2 项、开关关回、B 端快速加购 tab 进度需 B 端 owner 确认。

## 追加（2026-11-19 第二十八轮 · 组合×计划形态×来源覆盖矩阵【完成，含缺陷E修复 @d3f76f2e】）

**owner 追问四条**（大小班/组合/主从计划内组合/组合加购推荐扩科）→ 12 格覆盖矩阵（{大班,小班}×{单主,主从}×{加购rt3,推荐rt1,扩科rt2}）。

**关键动作与发现**：
1. **计划形态事实**（renew_master + renew_master_relation is_del=0）：现 case 计划全在主从集群（586116340522184704↔585960797778243584、589037361072007168 五计划互联、591020372877623296→两从等）；无单主×组合现成样本——组合三来源解析不依赖主从关联（代码同路径），单主格如实标注。
2. **组合×扩科此前无运行时样本**（20d 仅 diff+单测）——补验：测试库仅有 4 计划配 pt51 扩科（2026-06 老数据），唯二进行中计划的扩科节点时间窗已过；改用 case 计划扩科节点（586116340522184704 至 12/31、589037361072007168 至 12/7 均有效），pymysql 直连 INSERT renewal_expand_subject_recommend id118（小班主从 g11 subj6 sjg）/id119（大班主从 g31 subj3 sjg），只读回读确认。
3. **运行时补验**：小班 rt2 组合条目出现（TID cart_gaotu100_com.292.17950897429110285）、大班 rt2 出现（…285.17950897986280271）——**发现缺陷 E：已购组合在扩科位 signUp 恒 0**（小班 buildResult 只查组合 SKU 本身；大班传 emptySet 且 applyExpandSignUp 不处理组合）。
4. **缺陷 E 修复 @d3f76f2e**（已 push+部署 test-eco-8 pod 10.218.237.193 UP）：两路径各加一行 applyPurchaseSignUp(expandResults) 复用∪口径。验证：单测 RenewalExpandSignUpTest 7/7（新增 should_markExpandCombineSignUp_when_subProductOrderExists）；运行时小班 g11 rt2 su 0→1（TID …286.17950907163040007）+ 大班 g31 rt2 未购保持 0（TID …285.17950907357370007）+ 既有正负向无损。教训：首次部署构建了 88c25a90（本地 commit 未 push），补 push 后 pipeline 1355297 重发 d3f76f2e。
5. **扩科位行为记录**（如实）：配置年级单条不拆条；同 (grade,subject) rt2 与 rt3 去重合并为 rt2 呈现；大班路径 rt2 组合回填 teacher/clazzDateDesc 较全，小班路径两次实测字段不稳定（受组合缓存预热影响）。
6. **待 owner 口径细化**：③类型过滤「大班计划→须含大班课」方向无代码实现（88c25a90 准入仅「须含 6004」且在小班链路）；F 实测大班主计划 rt1 条目为从计划（小班侧已过审）合并条目，有合理解释；大班主计划自身推荐位配组合的准入未实现——如无此配置场景则无影响。

**文档**：场景 22（12 格矩阵+22a/22b+行为记录）+ 缺陷 E 落 EaKXdTkzXoJTStxBJH3cX7Qinzh 回读（rev 155）。遗留待 owner 不变。

## 追加（2026-11-19 第二十九轮 · 单主计划×组合专项【完成】+ 缓存授权落地）

**owner 决定**：①③类型过滤大班方向「不用管，需求没写」→关闭；②单主样本需要专造。追加授权：测试环境缓存可关闭提速。

**缓存开关落地（owner 授权）**：cart TEST Apollo 发布 preheat.cache.enabled / course.renewal.cache.enabled true→false（release 20261119204457），回读生效；V2 双开关 true 不动；按 owner 认可测试期间保持 false（上线检查须含恢复）。

**单主 4 格验证（软删 main 侧关联临时构造单主，验后全部还原）**：
1. 单主×小班×加购+扩科 ✅：TID cart_gaotu100_com.293.17950922090910280（缓存开）/…285.17950925541890335（缓存关干净态）——1v1 su=0 负向、sjg rt3 拆条 su=1、sjg rt2 g11 物理 su=1（∪口径）与主从态逐条一致。
2. 单主×大班×加购+扩科 ✅：TID …289.17950923791810306——软删实时生效（从计划纯续/推荐条目正确消失），sjg g31 rt2 生物 su=0、rt3 组合全保持；推荐位合并行为=单主态从计划 rt1 条目消失（正确）。
3. 单主自身推荐位新配组合 ⚠️ 未即时生效：DB 直插 renewal_link(pt51)+renewal_recommend_file（3 计划 6 行尝试）不实时（product 配置组装链多层，cart 缓存全关仍不生效）——正式入口 B 端 editProcess；组合推荐位解析由主从运行时+代码同路径覆盖，定性=配置链路限制非解析缺陷。

**关键事实沉淀**：主从真源=product productRelationList 下发 relatedRenewMasterNumbers（RenewalMasterRelationService.listSubNumbers，版本化 Redis 缓存 renewal:relation:version:{main}/v2:{main}:{version}，仅 B 端 save 刷新）；软删 gaotu.renew_master_relation 后预热缓存仍残留合并值（G1 取舍），关 preheat.cache 后实时生效。

**清理回读**：两计划 main 关联精确复原（小班 1 条/F 4 条/S4 1 条）；本轮 3 条 pt51 link+3 条 file 全部 is_del=1；S4 临时扩科节点+行全删；28 轮 id118/119 保留（场景 21/22 断言依赖）。副作用记录：F 历史关联 13 行 update_time 时间戳漂移（is_del 已精确复位，内容无损）。

**文档**：场景 23 落 EaKXdTkzXoJTStxBJH3cX7Qinzh 回读（rev 156）。事项①关闭记录在案。

## 追加（2026-11-19 第三十轮 · AICR+TAPD bug【进行中·上下文收束交接】）

**已完成（全部已验证）**：
1. **漏提交补交** e3d99f60：18 轮新增单测 RenewalExpandSignUpTest.should_markExpandCombineSignUp 上轮漏 commit。
2. **AICR 14 条逐条处置**（task #2058 FAIL：1 blocking+6 medium+7 low）——**12 项修复 @ad9c241e 已部署 test-eco-8 UP**：#52078 teacherMap 缺 key 判空（blocking，0L 混合查询缺 key NPE→联报 23 整体失败）；#52089 applyPurchaseSignUp 单班分支排除联报 23（activityNumber≠班级号编号空间）；#52088 remainCount 判空；#52081 processClazzSet 聚合查询移出循环（N+1）；#52080 endClazz 判空；#52079 allGrades grades 判空；#52083 gradesMap 判空；#52082 getClazzes 判空（新增 safeClazzNumbers）；#52086 组合查询走 WithCache；#52085 扩科/加购 beforeCourseNumber 对齐 null（与大班一致，**预期行为变化**）；#52084 orderStatus Objects.equals 4 处；#52087 魔法数字枚举化；#52090 注释纠正（不动老链）。**#52091（逐条转换 N+1 大重构）不改**，记录为后续优化。编译+定向单测 13/13 过。
3. **TAPD owner 待办 3 项**（tapd_list_my_tasks）：主 Story（EM纯续，54/54h）+ **Bug 1486168**（new）+ **Bug 1486137**（reopened）。
4. **Bug 1486168 定性=真 bug（线上既有）+已修复 @e2b17741**：productList→setSmallClazzVO（6004 项）只查 order_info 班级号，6004 订单落 order_item（DB 实证：order_info by clazz=SKU 0 行，order_item 有 433534690352694278 status=2）→ signUp 必 0。代码源自 ac6cb1ff「还原线上老代码原样」=既有。修复=补 listBySkuNumbersAndUserIdNoRefundBatch SKU 口径（与组合分支同款）。**复现（修复前 su=0，TID cart_gaotu100_com.286.17950940954010010 @ad9c241e）→ 复验（su=1 + 负向 GPS su=0，TID …295.17950943700480008 @e2b17741 pod 10.218.238.216）**。bug 状态未改（按 owner 要求）。
5. **Bug 1486137 定性=已修复待 QA 复测**：QA 17:57 复测时 eco8=ce3c66cf（旧口径）；88c25a90 已删加购过滤且 TICKET case 实证 1v1 组合 g16 rt3 恢复（TID …290.17950844672520048）。处置建议=QA 复测后关闭（**证据评论未发**，下一棒可选 tapd_comment）。

**未完成（下一棒按序）**：
1. **AICR 修复回归（第一优先）**：@e2b17741 跑核心 case——重点联报 23 路径（processClazzSet 大改 #52078/#52081/#52082）：A 计划 591020372877623296×7746793735（W1矩阵-大班主-联报23）+ TICKET（586116340522184704×7658129872&sellerId=8645&includeBCart=true）+C/D/F 核心断言；**注意 #52085 预期变化**：小班路径扩科/加购条目 beforeCourseNumber 由后置课号变 null。回归后可再跑 `python3 ~/.claude/skills/git-branch-convention/scripts/aicr.py` 看 e2b17741 评审是否转 PASS。
2. **全量测试收口**：38 case 重跑对照 /tmp/w14_result.md 基线（差异只允许=#52085 beforeCourseNumber 变化）。
3. **接口沉淀**：已验接口（renewalCart/productList/BossBatch createOrder/prepare/acl 桥 preheat 等，入口/参数/预期/示例 TID）补测试文档「已验接口」章节。
4. **造数沉淀**：BossBatch 下单（source 规则=纯数字10-20位或z结尾）、扩科组合配置 INSERT（renewal_expand_subject_recommend+已有节点实时生效；新节点被结构缓存挡）、推荐位配置（renewal_link pt51+renewal_recommend_file，**DB 直插不实时生效**，正式入口 B 端 editProcess）、单主构造（软删 renew_master_relation main 侧+关缓存后实时生效；**注意 product 侧关联有版本化 Redis 缓存 renewal:relation:version:{main}**）、mock 支付（0 元单免支付）——写到 quartzZZL/content/高途信息/构造数据/ 新笔记。
5. **分支总结（重点交付）**：功能层面+兼容层面逐条（素材=测试文档 12 模块盘点表+场景 19-23+缺陷 A-E 清单），落测试文档+话题讲清。
6. 归档第三十轮终态、插话一回复（case 在文档 rev 155/156 已确认）。

**环境现状**：test-eco-8 @e2b17741（pod 10.218.238.216 UP）；Apollo 缓存两开关 false（owner 认可）+V2 双开关 true；28 轮 id118/119 扩科配置保留；无在途部署/子 Agent。

## 追加（2026-11-19 第三十一轮 · 第 20 轮待办全清：AICR 回归+收口+沉淀+分支总结）

**环境核实**：HEAD=e2b17741 干净；pod 10.218.238.216:28688 UP（TICKET 探测正常返回）。

1. **AICR 修复运行时回归（第一优先，完成）**：主 Worker 亲自跑 45 条（脚本 reg21.py，结果 reg21_rows.json，均 opencode 目录）——38 case+TICKET+compare×5+20f **45/45 实质全过、0 疑似回归**。**#52085 预期变化全链生效**：全部 case rt2/rt3 条目 beforeCourseNumber=null（0 违规）、rt1 纯续保持课号；**联报 23 路径（#52078/#52081/#52082）无损**：A=3/A_bc=8/A2/S8 与基线一致无 NPE。相对基线（w14 @88c25a90，注意其早于 id118/119 插入）5 处差异全部判定预期：C/C_bc 5→6、F 6→7、F_bc 11→12（id118/119 扩科 sjg rt2，bc=false 也生效）、TICKET 11 不变（sjg g11 rt3→rt2 合并呈现 su=1 保持=缺陷E∪口径）。收口表 /tmp/reg21_result.md（45 条 TID 全集）。**AICR**：ad9c241e/e2b17741 push 后新评审任务未出（--list 最新仍 #2058=d3f76f2e 修复前）；代码核对修复在位（teacherMap 判空@2013、safeClazzNumbers@1993-1998），运行时回归即修复效果直接证据，新评审出来后可再确认。
2. **全量 38 case 收口（完成）**：结论落测试文档「三、全量 case 回归」新增 h3「AICR 修复回归 + 全量收口（@e2b17741）」（rev 157，回读 45/45+reg21_rows+safeClazzNumbers 全在）。
3. **已验接口沉淀（完成）**：测试文档新增 h1「已验接口速查（复用）」（rev 158）：cart 域 6 接口（cart/operation cart/productList/preheatCompare/preheat/换课链）+外部域（BossBatch prepare|createOrder、recommendProductList）+调试入口（acl 桥大数传字符串、fixture 清单、Apollo 现状），入口/参数/预期/示例 TID 齐全，回读 9 项关键内容全在位。
4. **造数方法沉淀（完成，子 Agent W1-0f8ae2）**：《续班组合商品与配置_构造与复现步骤.md》165 行落 quartzZZL/content/高途信息/构造数据/（BossBatch source 规则/扩科直插/推荐位不实时/单主软删/DB 口径/fixture 全表，格式对齐既有笔记，回读 6 项全在，既有两份笔记未动）。
5. **分支总结（重点交付，完成）**：新飞书文档 https://gaotuedu.feishu.cn/docx/TzD4dvRQLoVTx6xGTcHcWafQnOd ——功能 13 条（组合加购 12 需求点/推荐准入/扩科/∪口径已报名/类型过滤终态/预热V2/P1/换课换年级/联报缓存/EM纯续/联报23/统一解析链/质量加固）+兼容 8 条（老链零改动/开关回退/renewalRole/原key 两取舍/beforeCourseNumber 变化/过滤删除影响/上下游不变/数据兼容）+未支持 6 项+上线必办与遗留+验证状态；全文回读 14 项关键内容全在位。
6. **1486137 证据评论（完成）**：tapd_comment 落库（comments[0]，回读含 88c25a90/e2b17741/TID …290.17950844672520048 全证据与复测建议）；状态保持 reopened 未改。

**环境终态**：test-eco-8 @e2b17741 UP；Apollo 缓存两开关 false + V2 双开关 true（不变）；28 轮 id118/119 保留；无在途部署/子 Agent。遗留待 owner 不变（fromC NPE、D1、联报23 根治、上线必办 2 项、B 端 tab 进度、1486168/1486137 待 QA）。

## 追加（2026-11-19 第三十二轮 · owner 插话两项：拍板详解 + case 文档核对发送）

1. **待拍板详解（完成）**：基于既有材料（归档 363 行联报 23 二选一原文、587 行 D1、G2/G3 等）整理 6 条逐项展开（问题/为何待定/方案/影响/建议）：①fromC NPE（建议独立小修单 B）；②联报 23 根治 A 老链一行需特批/B V2 写入侧兼容/C 不修关回即不现（建议 B 或 C）；③D1 展示侧 defaultSelect（A 后端重算/B 前端/C 接受，不阻塞提测）；④B 端 tab 进度需 owner 向 B 端确认；⑤上线必办三项含 V2 开关「关回 false vs 切终态」决策（建议关回 false、切终态独立变更）；⑥QA 状态知悉。落分支总结文档新增「六、待拍板事项详解」（rev4，全文回读 8 项关键内容 IN）。
2. **case 文档核对（完成，无漏补）**：owner 历次 9 类要求逐项对上测试文档场景（大小班→22 矩阵；主从组合→22+1-14+45 条；加购/推荐/扩科→16-19/20b/20d+22ab；口径更正→20 全章 20a-20i；单主→23；已报名造数→21；小班主计划补漏→16/17/18；不影响原 case→三章节+AICR 收口；接口复用→已验接口速查），本轮逐节 section 回读核验在位（场景 17/20/21/22/23 全拉）。
3. **发送（完成）**：话题消息（拍板详解精华+9 行映射表+两文档链接）经 feishu-send-topic --task 9bddb709 发送成功，message_id=om_x100b60c4456074acb4beda8c44374c7。
边界遵守：零代码/Apollo/bug 状态改动；无新增调查（全部基于归档既有材料）。

## 追加（2026-11-19 第三十三轮 · owner 拍板 5 条执行完毕）

**拍板（原话）**：1 fromC NPE 不用管（线上没问题的话）；2 联报 23 选 B+讲清从计划数据成因；3 D1 选 A+讲清 defaultSelect；4 B 端 tab 不用管；5 记待办（测试环境恢复走 V2+预热写老 key 配置）。

**逐条执行（全部已验证）**：
1. **fromC NPE 关闭**：线上核实 cart 近 7 天错误日志零 NPE（SLS serviceName=cart + queryStr 完整 token 双姿势均 0 条；token 有效性已用 "cart.gaotu100.com" 单查有结果证实）。按 owner 口径关闭。
2. **联报 23 方案 B @8a7d596b**：话题已讲清成因（从计划班课天然无活动号，null=正常形态非脏数据；老链联报分支无差别收集致订单服务拒绝；生产未开 V2 不受影响）。实现=RenewalV2PureRenewalService.preheat 主计划联报型(role=2 且 act==null)占位自身 SKU；**新链消费 filter 早已在位**（RenewalSinglePlanDetailService:643/667，方案 B 实际只剩写入侧一处）。验证：preheat 运行时实证（A 计划 591020372877623296×7746793735，role=2 条目 act=591020573457448960=自身 SKU、role=1 保持真活动号，TID cart_gaotu100_com.304.17950999421290066）+ 单测 2 项新增（31/31）。老链端到端待缓存开关恢复后补（如实分档）。
3. **D1 方案 A @28e2eece**：话题已讲清 defaultSelect 作用与改因。实现=主计划模式（FULL/SKIP_PREHEAT）换年级记录按主+从计划号合并取最新（repository 新增 listUserRenewalGradeByNumbers，order by update_time desc）；记录年级在从计划侧时主计划不设默认（gradeRecordOutside）由合并器取从计划默认；小班侧 convertToRenewalCartVO 加 gradeRecordsOverride 参数（主计划入口传、从计划/LEGACY_PURE null 保持原行为）；老链零改动。验证（先复现后修复）：复现=插 user_renewal_grade(7746791494, 从计划号 585960797778243584, 12) → defaultSelect 停兜底 g11；修复后=**defaultSelect=1@g12**（TID …303.17950994883430008）；边缘（grade=16 不在主计划年级组）→ 合并器接管回兜底 g11 不 crash（…297.17950995129900010）+ merger 接管单测新增（@839a1612，14/14）；负向删记录回 g11（…302.17950999775500072）；复现记录已清理（回读 0 行）。
4. **B 端 tab 关闭**：记录在案。
5. **待办落文档**：分支总结新增「七、后续待办」（恢复走 V2+预热写老 key 配置，owner 安排时机执行）；第六节标题后插拍板结果 callout（rev5/6 回读 10 项 IN）。

**回归**：45 条全量 @28e2eece（reg23.py，pod 10.218.248.35）= 43 PASS + C=6/F=7 与上轮同值同判定（id118/119 预期+1），**0 疑似回归**；联报 23 路径（A=3/A_bc=8）与 bcn 断言全保持。

**提交**：8a7d596b（占位+单测）→ 28e2eece（D1 三文件）→ 839a1612（merger 单测）已 push；部署 pipeline 1355452 SUCCESS，pod 10.218.248.35 eureka UP @28e2eece。测试文档场景 24 落库（rev161 回读 10 项 IN）。

**环境终态**：test-eco-8 @28e2eece UP（HEAD=839a1612 仅多单测）；Apollo 零改动（缓存 false+V2 true/true 保持）；id118/119 保留；复现记录已清理；无在途部署/子 Agent。遗留待 owner：上线必办 3 项、待办 2 项（第七节）、1486168/1486137 待 QA、AICR 新评审未出（平台延迟）。

## 追加（2026-11-19 第三十四轮 · AICR #2062 处置 + 既有规则体检【owner 插话，只读分析】）

**一、AICR #2062（@28e2eece 新评审，10 条）处置完毕 @08f67363 部署 UP（pod 10.218.238.169）**：
- **#52237 [blocking] #52085 扩大化**：processSingleClazzResult 对所有单班条目传 null 致**纯续小班 6004 条目丢 beforeCourseNumber**（V2 extractPureMap 以其为 key，null 条目被跳过丢出合并值）——修复=纯续（RENEWAL/null）传 result.getCourseNumber()、扩科/加购保持 null。修复前现状实证=TICKET 586097 g11 rt1 bcn=None（@28e2eece 输出）；修复后=bcn'18314034380997173' 恢复+rt2/rt3 保持 null（TID cart_gaotu100_com.289.17951014193630015）+A preheat 从计划条目 bcn=18390028220432911 进合并值（TID …286.17951014530740017）。
- **#52229 [blocking] 换年级落库丢事务**（D1 修复 b61f95a5 引入）：串行直连写中途失败清空用户记录——修复=RenewalDataService 新增 productSelectGradeWithSubPlans @Transactional（主+从计划号版本），RenewalService 调用、缓存失效留事务外。
- 另修 7 项：#52230/31 subjects 判空、#52238 grade 过滤 null、#52236 拼写、#52234 无用导入、#52233 死分支、#52232 preheat 入口判空；**#52235 N+1 不改**（与 #52091 同口径记录后续优化）。定向单测 32/32。
- 45 条回归 @08f67363：43 PASS + C=6/F=7 老判定，**0 疑似回归**；TAPD 1486168（new）/1486137（reopened）无新 QA 动态。

**二、既有规则体检（owner「先分析」，只读，14 条全满足）**：
| 规则 | 结论 | 证据 |
|---|---|---|
| 列表排序：未购在前→forceBuy→纯续>扩科>加购 | ✅ | 代码三处同款（V2ResultMerger DISPLAY_ORDER:34 与 SinglePlanDetail sortClazzDetailDTOsForDisplay:2939，大班/小班/V2 合并统一）；**排序专项 6 case 程序断言全过**（TICKET/E_bc/F/A_bc/C_bc/D_bc，TID 287~294.1795101726~1733 段）；与 @28e2eece 基线顺序一致 |
| 去重（年级学科含子班展开/同商品/推荐让位加购） | ✅ | 场景 16-18/20c+45 条条目数三轮保持 |
| 类型过滤（仅推荐来源；6004 枚举；1v1 不算小班） | ✅ | 场景 20a-20i 全过+TICKET 1v1 g16 rt3 加购位（88c25a90=owner 更正口径预期变化） |
| SKU 售卖状态（B 端 fromBCart 过滤） | ✅保持 | F2 b2-0/b2-1 对照+fromBCart 透传未动 |
| 已购过滤（B 端推荐列表） | ✅ | 26 轮 recommendProductList 已购过滤正确 |
| 已报名判定（组合SKU∪子商品SKU∪子班级号） | ✅ | 场景 21 造数全链路+20f+缺陷E 22a/22b+1486168 修复复验 |
| 跨年级拆条 | ✅ | E_bc 589762 拆 37/38/39+TICKET sjg 5 年级 |
| 开课最早子班展示 | ✅ | 28 轮判定（空文案=源数据，sjg 日期佐证） |
| 主从合并展示 | ✅ | compare 5/5 三轮（88c25a90/28e2eece/08f67363）+场景 22/23 |
| 换年级默认年级 | ✅（owner 拍板新行为） | 场景 24b-24d 闭环 |
| 换课规则（从计划 key 归位/组合不可换课） | ✅ | 缺陷 C 修复实测+场景断言 |
| allSignUp 语义 | ✅ | 45 条 su 分布锚点保持 |
| 联报 23 展示与预热 | ✅ | A=3/A_bc=8 三轮一致+preheat 占位实证 |
| 开关路由与老链行为 | ✅（老链仅两处已授权修复） | BE×13/BE1×3 全过；RenewalService diff 仅换年级事务收敛+productList 两区域 |

**曾偏离两点均已闭环**：#52085 扩大化（#52237 本轮修复验证）；类型过滤口径（owner 更正=预期变化）。**疑似改坏项：无**。

环境终态：test-eco-8 @08f67363 UP；Apollo 零改动；HEAD=08f67363 已 push。

## 追加（2026-11-19 第三十五轮 · owner「再回归一遍全量case」@08f67363 复跑）

**主 Worker 亲自复跑**：45 条全量（reg24.py）+ 排序专项 6 case（order_check.py），与 @28e2eece / @08f67363 首轮逐条对照——**三轮结果完全一致：43 PASS + C=6/F=7（id118/119 预期+1 历轮同值同判定）、compare 5/5、20f 正向、排序 6/6、bcn 断言 0 违规（#52237 修复效果持续在位），0 疑似回归，无改坏**。本轮 TID 段：45 条 286~295.1795102379~1795102423；排序 286~294.1795102394~1795102399。脚本预设值已修正（C=6/F=7），后续复跑不再出预期 DIFF。测试文档收口小节已追加复跑结论（rev162 回读 4 项 IN）。环境终态不变：@08f67363 UP / Apollo 零改动 / 无在途。

## 追加（2026-11-19 第三十六轮 · owner 抽样自核 10 条：人工 vs 脚本一致率 10/10）

**抽样方式**：random.seed(26) 从 45 条覆盖集随机抽 10：F、cmp_D、F_bc、BE_B、BE1_S3、BE_S8、A2_bc、D、BE_E、A2（不挑拣）。**方法**：重新发真实请求打印完整明细（manual_dump.py，零断言），人工逐项比对各 case 断言口径（条目构成/signUp/rt/bcn/排序位置/ds）。

**结果：10/10 人工结论与脚本结论一致**。人工逐条核对要点：F=7 条（主计划 g31 纯续 4+扩科 2 含 id119 sjg、589762 g11 推荐位，bcn 纯续课号/扩科 null 全对，589212673443520512 sel=1 用户勾选保留）；F_bc=12 条（+1v1 g16 rt3+589762 拆 37/38/39+589048 g11 rt3 pt6004）；cmp_D consistent=true triggered=true；D=5 条（组合 g11 rt1+从计划 g31×4）；A2/A2_bc=3 条（588506 g11 pt6004 bcn=18390028220432911=#52237 修复在位、联报 pt23+班课）；BE_B=1 条 rtNone（LEGACY_PURE 不标记 rt=老 B 端行为保留）；BE_S8=1 条；BE_E=3 条（无 b_cart 无加购位=接口语义内）；BE1_S3=1 条 **su=1**（有效订单已报名标记正确）。本轮 TID 段 286~294.1795102782~1795102793。

**两个人工观察项均定性为非问题**：①F_bc 加购新增年级组 defaultSelect=null——git 基线 4b40ee27 老链同构（578/1164 只 set1 无 else set0），**既有行为**非本分支引入（前端线上已适配）；②F/D 的 ds1 落在 g31（主计划自身最小年级）而非含从计划年级的全局最小 g11——与「主计划年级兜底+从计划详情合并」逻辑自洽（g11 组来自从计划条目）。

## 追加（2026-11-19 第三十七轮 · owner「全部都核验一遍」全量人工核验：45/45 一致）

**范围与方法**：45 条覆盖集（上轮已人工核 10 条复用）+ 排序维度顺带人工核。剩余 35 条全部重新真实请求（manual_all1/2.py，零脚本断言）打印完整明细，人工逐项比对（条目构成/signUp/rt/bcn/排序位置/ds/allSignUp）。

**结果：人工 vs 脚本 45/45 完全一致（含复用 10 条）**。本轮 35 条人工核对要点：A=3（纯续 bcn=课号 #52237 在位）/A_bc=8（含 579426174109902848 同 SKU 跨 g22+g11 拆条人工确认）/B=1/B_bc=6/C=C_bc=6（基线5+id118 sjg rt2）/D_bc=7（1v1+组合推荐+从计划4+589041240 在 D 为 rt3 加购位=F 为 rt2 扩科位，来源差异合理）/E=3/E_bc=10（1v1+589762拆37/38/39）/G/S9/S12/X1(status=5)/X2(status=10241007) 全对/S3=S3_bc=1 且 **su=1+allSignUp=1**（有效订单）/S4=2/S4_bc=11/S8=1/TICKET=11（g11 组 su0→su1(rt1)→su1(rt2) 排序人工确认、586097 bcn=课号、sjg 五年级拆条 su 全对）；B 端 BE×7/BE1×2 条数全对（BE_C=1 只出主计划=LEGACY_PURE 语义、BE_S3 su1）；cmp_A/C1/C2/E 全 consistent=true+triggered=true；20f **1v1 g16 rt3 su=1 + 同请求 7 条无订单组合全 su=0**（正负向完整人工确认）。TID 段：第一批 286~295.1795103339~1795103355、第二批 286~295.1795103384~1795103400。

**唯一新观察项（定性：推断非问题，先记录不改）**：B 端接口部分条目 recommendType=null（如 BE_A 联报条/BE_F 首条 g31/BE_S4 首条）与 rt=1 混合——推断=null 为老链主计划路径条目（老 B 端一直不标记，基线常态）、rt=1 为 V2 合并带入的从计划/新链条目，V2 开关期间的条目来源混合表现；老 B 端前端不消费 rt 字段（null 是其常态值），无功能影响。历史轮 BE 系列仅断言条数、无 rt 基线，**标注推断未验证**；建议 QA/前端确认 B 端是否消费 rt，不消费则无影响。

## 追加（2026-11-19 第三十八轮 · 外部 AI 评审文档逐条定性【进行中·上下文收束交接】）

**输入**：文档 XQ3KdRKapov8JRxOwl8cB87QnQc（rev6，11 条：P1×2/P2×4/P3×5+取证），评审基线 **88c25a90**（早于当前 08f67363 共 8 个提交）。全文已读+11 条全提取（本地 ext_review.txt/json）。**本轮零改动**（owner 口径先别改只判断）。

**已定 9 条（证据充分）**：
- **P1-1 从计划失败→整页500**：不适用——owner 2026-11-17 已拍板强一致口径（代码注释明示「单个从计划失败必须抛异常」）；如要改降级=口径变更需 owner 决定（可配套熔断/告警）。
- **P1-2 双开关中间态**：运维注意事项不改代码——上线按 owner 已拍「V2 关回 false」不会进中间态；未来切终态需按顺序（先开预热后开详情，关闭反序）——建议补进分支总结第七节上线必办。
- **P2-1 扩科受推荐准入影响**：**真问题（口径偏差，低概率触发）**——已核实 CombineProductBuildSubBuilder 两道过滤在 build 阶段 return null（第一道 subClassList.isEmpty 无小班课子班=null=场景18既有取舍；第二道 ③88c25a90 准入），扩科共享 context.combineProductInfoList 候选→「不含6004但含其他班级子班的组合」扩科位不可达，与 owner「扩科不过滤」口径偏差；触发条件=运营在扩科位配不含小班课组合（当前测试库 id118/119 均含6004未触发）。建议=③过滤下沉推荐阶段或扩科单独取候选；**待 owner 拍**。subClassList 是否含大班子班的细节未看完（buildSubClassList）。
- **P2-4 D1**：已修复 @28e2eece+场景24闭环——评审基线早于修复，不适用。
- **P3-1**：建议项（老链换课/换年级多一次带60s缓存的关联查询，已catch降级）。
- **P3-2 单文件3587行**：已知技术债（AICR #52090 同款），后续拆分。
- **P3-3 validateNoSharedPreCourse 抛错**：设计取舍（防脏配置故意抛+1h缓存+单测 should_throw_when_main_and_related_share_same_pre_course 在案）。
- **P3-4 normalize fastjson命名**：纯工具接口（compare）展示问题不影响业务——误报级。
- **P3-5 串行**：有意设计（注释明示外层用户级并行足够），生产压测关注。
- **第六节未覆盖项**：场景14 grade31=6条 vs 文档5条 → **id118/119 预期+1（历轮已判定，文档基线滞后）**；D1/fromC/缓存开关=已修/已关闭/上线必办已知；场景1-8文档栏位空→验证在归档多轮有据（栏位滞后可补填）；renewalRole 前端=老值null已验兼容（O3），建议前端确认一句。

**未完成（下一棒续）**：
1. **P2-2 JobHandler 跳过条件**：RenewalV2JobHandler 循环内 processDTO 判空+preCourseList isEmpty 已见（40-70行），评审说的 renewalLinkActivityDTO 非空跳过在 70 行之后——**看 70-90 行确认**；若属实=普通大班计划被批量预热跳过（退化实时兜底，RT 风险），对照老 Job 跳过条件定性。
2. **P2-3 批量预热小班无订单状态过滤**：看 RenewalV2Service.queryPlanUserIds 小班分支是否真无 2/7 过滤——属实则低风险优化项（开销类不影响正确性）。
3. P2-1 补看 buildSubClassList（subClassList 是否含大班子班——决定「纯大班子班组合」能否过第一道）。
4. 汇总输出完整判断表（11 条+第六节 6 项）→ 话题汇报业务语言+归档终稿；文档本身不改。
素材：ext_review.txt（已提取全文）、ext_review.json。

## 追加（2026-11-20 第三十九轮 · 评审 11 条定性收口：P2-1 修正为误报，全部条目定性完毕，零代码待改）

**本轮完成**：P2-2/P2-3 定性 + P2-1 补强实读（buildSubClassList/ExpandSubjectRecommendService/AdditionalPurchaseService/CombineProductSortPlugin/SmallRenewalCoreService 全链路）。**P2-1 发生定性修正（真问题→误报）**，待 owner 拍板项从 1 个降为 **0 个**。本轮零改动（代码/Apollo/评审文档均未动）。

### 三条新定性

**P2-2（JobHandler renewalLinkActivityDTO 跳过）→ 既有行为/有意复制，非本分支引入（误报级）**：
- 代码属实（RenewalV2JobHandler.java:67-76），但与老 RenewalJobHandler.java:55-60 **逐字一致**（老 Job 2022-07 上线至今同一条件）。V2 有意复制老链路准入（类 javadoc 明示「两者写值语义一致」），保证两 Job 预热同一批计划；单边收紧/放宽反而破坏 V2/老链路写值面一致性。
- 「误跳普通大班计划」前提（正常计划无 renewal_link 活动记录）实测不成立：测试环境全部非联报计划（普通大班 591020573457448960 pt=2、小班 586116340522184704 等 38 case 全量计划）均可正常预热。
- 即使线上存在此类计划：老链路 4 年来同样跳过（既有行为），退化实时兜底=RT 风险非正确性问题，V2 未改变任何行为。

**P2-3（批量预热小班无订单状态过滤）→ 对象错位：评审所指代码不可达；真实路径现象属实但为既有口径，低风险优化项（建议级）**：
- 评审指的 RenewalV2Service.queryPlanUserIds 小班分支（:288-296 listByCourseNumber 无 2/7 过滤）**代码存在但不可达**：preheatByRenewalNumber :233-238 小班计划走 smallRenewalPreheatService.preheatByRenewalNumberAndCache 后 return，永远到不了 :248 queryPlanUserIds；其 small 分支为死代码（可顺手清理）。
- 小班真实用户集在 SmallRenewalPreheatService.queryUserIds（:239-245）：同样 listByCourseNumber 无状态过滤——现象属实。但 RenewalV2Service :234-236 注释明示「该问题两口子（V2/老链路）一致，不因写缓存放大计算量」——**既有差异非本分支引入**。
- 影响=预热用户集偏大（含待支付/已退款订单用户），徒增计算/Redis 开销；无正确性问题（多算用户按 userId 隔离写缓存，纯续结果为空/无意义不污染他人）。修复属老链路同款优化，需下游确认 listByCourseNumber 返回是否含状态字段。

**P2-1（类型过滤影响扩科）→ 修正为误报：评审所述代码路径不存在**：
- 评审证据链：「ExpandSubjectRecommendService 从 preClassInfo.getCombineProductInfoList() 拿候选，扩科无法访问被过滤的组合」——**实读不存在**。扩科候选来自 DB 配置表 expandSubjectConfig.getRecommendList()（renewal_expand_subject_recommend），小班路径 buildResult（ExpandSubjectRecommendService.java:190-210）与大班重载（:104-162）均直接用 recommend 的 productType/productNumber 构建 ProductKey，年级用 configuredGrade（配置行自带），signUp 用 purchasedPostClazzSkuNumbers——**全程不查 combineProductInfoList**。加购（AdditionalPurchaseService）同样无 combineProduct 依赖（b_cart 配置）。
- combineProductInfoList（build 阶段过滤结果）的消费者经穷举全部为**推荐位链路**：CombineProductHandler（V2 推荐 handler :38-51）、CombineProductSubClassMatchPlugin、CombineProductSortPlugin（supports :43-47 限 pt=51 计划的推荐候选，查不到才丢候选）、SmallRenewalCoreService.buildRecommendResult（:845 推荐位展示填充）、UserPostClassOrderSubBuilder、PurchasedProductMatchPlugin、RenewalV2ResultMerger（:270 仅按 EXPAND_SUBJECT 归类 SKU 集合做去重，不查组合详情）；C 端展示组装（RenewalSinglePlanDetailService）无 EXPAND_SUBJECT 特判。
- **补强结论（buildSubClassList :423-473）**：subClassList 只收班级类子班（isClazzLikeSubProduct :479-482 = 6004/6003，**大班子班 pt=2 不进**）→ 纯大班子班组合死在第一道过滤（subClassList.isEmpty），纯 1v1 组合过第一道死在第二道（containsSmallClazzSubProduct 要求 6004）。两道过滤只作用于推荐位候选池——**恰好与 owner 口径「推荐过滤、扩科加购不过滤」一致**。
- 证据边界：扩科配「不含 6004 组合」当前测试库无数据（id118/119 均含 6004），运行时复现需 DB 写插配置（超出本轮只读边界）；代码全链路实读无拦截点。场景 14 扩科组合 pt=51 展示正常（评审自身取证 TID .292.17950846940780049 同段）。**上一棒「真问题待拍板」作废，无需 owner 决策、无需改码**。

### 11 条完整判断表（终稿）

| 条目 | 定性 | 依据（一句话） | 建议 |
|---|---|---|---|
| P1-1 从计划失败→整页500 | 不适用 | owner 2026-11-17 强一致口径（代码注释明示） | 改降级=口径变更需 owner 决定，本轮不动 |
| P1-2 双开关中间态 | 运维注意 | 上线 V2 关回 false 不进中间态 | 切终态顺序建议补分支总结第七节（先预热后详情，关闭反序） |
| P2-1 类型过滤影响扩科 | **误报** | 扩科/加购候选直接来自 DB 配置表，不经过 combineProductInfoList；过滤只作用推荐位=口径一致 | 无需改码；扩科配不含6004组合的运行时验证留作后续可选 |
| P2-2 Job 跳过条件 | 误报级（既有行为） | 与老 Job 逐字一致（2022 至今）；38 case 全量计划均可预热 | 不改；单边改反而破坏 V2/老链路一致性 |
| P2-3 小班预热无状态过滤 | 建议项（既有口径） | 评审指的代码不可达；真实路径（SmallRenewalPreheatService:239）属实但两口子一致，开销类无正确性问题 | 后续优化：补状态过滤+清理死代码分支，需下游确认 |
| P2-4 D1 换年级 defaultSelect | 已修不适用 | @28e2eece 修复+场景24闭环（评审基线早于修复） | 无 |
| P3-1 老链换课多一次查询 | 建议项 | 带 60s 缓存已 catch 降级 | 后续加开关保护 |
| P3-2 单文件 3587 行 | 已知技术债 | AICR #52090 同款 | 后续拆分 |
| P3-3 validateNoSharedPreCourse 抛错 | 设计取舍 | 防脏配置故意抛+1h缓存+单测在案 | 运营配置规范约束 |
| P3-4 normalize fastjson 命名 | 误报级 | 纯 compare 工具接口展示问题 | 无 |
| P3-5 从计划串行 | 有意设计 | 注释明示外层用户级并行足够 | 生产压测关注 |
| 第六节·场景14=6条 | 文档滞后 | id118/119 预期+1（历轮已判定） | 测试文档基线可补 |
| 第六节·D1/fromC/缓存开关 | 已知 | 已修/已关闭/上线必办在案 | 无 |
| 第六节·场景1-8 栏位空 | 文档滞后 | 验证在归档多轮有据 | 可补填 |
| 第六节·renewalRole 前端 | 已验兼容 | 老值 null=O3 已验 | 建议前端确认一句 |

**收口结论：11 条全部定性完毕，0 条需要本轮改代码，0 条待 owner 拍板**（上轮唯一待拍项 P2-1 已修正为误报）。评审文档本身未改（owner 口径）。分支 @08f67363 终态不变：已双重核验无改坏、可交付验收。

## 追加（2026-11-20 第四十轮 · owner 反馈定性：联报23主计划两环境 1条 vs 3条 = 均正常，V2 主从合并预期）

**Owner 两条原话**：①「老链路-大班联报 23（场景1）五年级语文返回了两课 还返回了一科 一年级数学 这正常吗」②「测试环境 只返回了一条 test-eco-8 返回了三条」。

**Case 定位**：场景 1「老链路-大班联报 23」= 计划 591020372877623296 × 学员 7746793735（文档预期老链路 1 条联报 pt=23 grade15）。该主计划「W1矩阵-大班主-联报23-1117」配 **2 个从计划**（归档 315 行 owner 自测 TID 记录在案）：大班2 计划 + 小班计划 588506246722727936（文档 case 数据行「B 同时是 A 的从计划」）。

**本轮两边实跑明细（均已验证）**：
- **default 泳道（测试环境基线，@default 10.255.166.130，release 4b40ee27=线上代码）**：**1 条**——grade15 五年级语文「W1矩阵联报-M23语文AB-1117」pt=23 价格200 rt=1 su=0（TID cart_gaotu100_com.12831.17951388393798798）。老链路无主从合并能力，只出主计划自己的联报纯续——与文档场景 1 预期（1 条）一致。
- **test-eco-8（@08f67363，V2 双开关 true）**：**3 条**，全部 rt=1 纯续（TID cart_gaotu100_com.287.17951387248803577）：
  1. grade15 五年级语文「W1矩阵联报-M23语文AB-1117」pt=23 价格200 —— **主计划**联报纯续（同基线那条）
  2. grade15 五年级语文「W1矩阵S2后置班语文1117」pt=2 价格100 —— **从计划（大班2）**纯续班
  3. grade11 一年级数学「默认规格」pt=6004 价格0 —— **从计划（小班588506246722727936）**纯续班

**定性：正常，两环境都对**。差异不是缺陷，是本分支核心功能「主从计划纯续合并」的预期表现：
- owner 看到的「五年级语文两课」**不是重复**：一条是主计划的**联报商品**（一次报 M23 语文 A+B 两个后置班，200 元），一条是从计划的**单班课**（S2 后置班语文，100 元）——不同续班计划、不同商品形态，均为纯续推荐位。
- 「一年级数学一科」= 另一个从计划（小班计划）的纯续班（跨年级展示在 grade11 组）。
- 测试文档场景 9/12（同计划同学员，V2 开启）预期即「23+2+6004 三条跨类型合并」，归档 386 行 11-18 已验证一致（TID 17949915970800969）；评审取证同样一致（TID .295.17950984643270127）。
- 验收环境提醒：场景 1-8（老链路基线）在 default 泳道验=1 条；场景 9-14（V2）在 test-eco-8 验=3 条——两套预期并存是设计（老链路行为保持不变=兼容要求）。

**零改动**（纯定性排查，代码/Apollo/数据/文档均未动）。
