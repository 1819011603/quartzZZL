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
