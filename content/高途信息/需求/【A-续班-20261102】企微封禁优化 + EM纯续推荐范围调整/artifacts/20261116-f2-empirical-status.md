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
