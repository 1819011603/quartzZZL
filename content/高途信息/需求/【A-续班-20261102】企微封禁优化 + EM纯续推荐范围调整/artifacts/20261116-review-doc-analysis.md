# 评审文档《购物车 MR 300｜纯续关联需求一致性审查与验收建议》逐条定性（2026-11-16）

- 来源：https://gaotuedu.feishu.cn/docx/AzBwdbegioDO3ax2noJc32honlh （owner 转发，提醒「不一定是问题」）
- 审查对象：MR 300 / HEAD 38d2d741（与实际部署一致：test-eco-8 pod 38d2d741）
- 定性口径：真问题 / 不是问题（误报·生产行为·已闭环·设计取舍）/ 待定；本轮只分析不修码，处置待 owner 定夺。

## F1｜从计划全部失效后，旧缓存仍可能带出推荐 —— **真问题（代码事实确凿，评审定位准确；owner 求证结论「无变化感知只能重新预热」已确认准确）**

- 机制链（已核代码）：`resolveActiveSubs:99-131` 每次实时查 product 有效从计划 → B 失效后 related 为空 → `RenewalV2Service:96-98` 走 `getMainPlanDetail`（非 skip 版）→ `RenewalSinglePlanDetailService:390` 命中合并缓存 → `corePreheatCache:1120-1141` 反序列化后无任何状态过滤 → 失效 B 条目（role=2）展示。
- 写侧无失效机制：`writePreheat:439` 写值 TTL 默认 26h（`preheat.cache.time:26`），全仓无监听/回调/主动失效；唯一清理=重跑预热（重算时 B 被过滤→主-only 值覆盖；整体为空则删 key，`writePreheat:428-435`）。
- 影响面：仅①回退态（recommend.v2=false 老读链路，TID 17946706444010009 已实证读合并值）②V2 无有效关联读（含本场景）。不受影响：V2 有关联实时（主计划 SkipPreheat 全重算）、B 端 fromBCart=true、主计划自身失效（`:380 isEffective()` 门在缓存读之前）。
- 与既有事实关系：**与 G1 同族**（G1=关联配置变化、F1=从计划状态变化，同为 26h TTL 窗口合并值陈旧）；G1 提议的「有效关联集合指纹入缓存值、读时比对不一致当 miss」可同时覆盖 F1。评审窄修法（related 为空跳过合并缓存/只留主条目）只堵 F1。「冲突校验 1h 缓存」同族但仅延迟冲突报错，不产生脏推荐（有效关联集合本身不走该缓存）。
- 条目级班满/下架读缓存不重查=与老系统同语义，非 V2 新引入；V2 增量=从计划条目进主 key 带来的跨计划陈旧。
- 严重度：中。窗口=状态变化→下次重热；**生产 V2 预热 Job 尚未配置调度，上线时必须配**，否则窗口=人工触发间隔（上限 26h）。
- 处置建议（owner 决策）：A. 版本指纹法（覆盖 G1+F1，读侧兜底，改动集中在读路径）；B. 窄修 F1（related 空时不读合并缓存）；C. 接受窗口+保障重热频率（Job 密集调度）。A/B 均需开发+回归。

## F2｜小班联报实时可展示，但预热遗漏 —— **真问题（代码事实确凿；场景可达性属产品配置，TEST 可造验）**

- 机制链：联报 DTO 构建 `RenewalSinglePlanDetailService:2192-2269`（processClazzSetResult，productType=23）**从不设置 beforeCourseNumber**；推荐类型默认 RENEWAL=1（`setRecommendTypeFields:2485-2488`）；而纯续提取要求 before 非空——预热侧 `extractPureMap:2819-2823` 与实时侧 `extractFromDetail:242` 都跳过 null → 联报条目进不了预热合并值；但实时**展示**合并（merge VO）保留联报 → 「页面有、预热无」。
- 影响差异面：V2 实时页面有联报、回退态（读预热值）没有——回退态从计划联报推荐缺失。与 F1 不同族，这是**预热值内容缺失**（非陈旧）。
- 与本轮实测的 51 组合条目区分：51 组合（combine_product_sku_numbers）before 有值、预热值**有**该条目（单用户重预热返回已证实，TID 17948129236470191），回退态不展示是 processClazz 判空取舍；**联报(23)是预热值本身没有**——两个不同机制，评审 F2 只指后者，成立。
- 修复方向（评审建议成立）：联报 DTO 补真实前置课号（postClassInfo.getCourseNumber()，即 key=该前置课，跨计划不共用前置课有校验保证）；修后需验预热+实时均含该条目。等 owner 定夺。

## F3｜跨计划同 SKU 预热缺年级信息可能不去重 —— **待定（设计内边界场景，本轮实测未出现）**

- 机制链：`V2PureRenewalService#merge:385-386` 去重条件 `grade != null && seen.add(grade+":"+sku)`——预热路径年级来自 `resolveGrades`（课程查询，解析不到不误删→不去重），实时路径来自展示年级分组（`extractFromDetail:249-250`）→ 两侧年级解析不一致时，同(grade,sku)预热留两条、实时一条。
- 本轮 31 样本规则二 sku 多重集全对上（唯一差异=51 组合条目，另有解释），**未出现该场景实例**。
- 处置：纳入对比脚本观察（脚本按 sku 多重集比对，重复条目会表现为 count diff，天然覆盖）；暂不修。

## 评审前提与其他条目核对

- 「关联配置变更后必须重新预热」前提：与 G1/F1 陈旧窗口族一致，已并入 F1 结论。
- 「预热 A 只处理 A 的学员，关联单向」：代码一致（`preheatByRenewalNumber:228` 只遍历 A 学员）；本轮实测纯从学员 baseline 空/实时有 role=2 条目=该设计的表现（预期差异）。
- 「V2 前缀 diff 通过后回原 key 重热并验证」：本轮已按此执行（prefix=false 写老 key→双规则对比→开关恢复回读），见 scripts/README 第 8 节验证记录。

## 本轮新增观察（评审文档之外，推断未验证）

- 批量预热从计划解析/单用户计算瞬时失败会**静默写部分合并值**（`loadRelatedConfigs:157-166` 跳过查询失败从计划、`resolveActiveSubs` 异常返回 null→按无关联处理、`preheatByRenewalNumber:242-249` 单用户异常仅 log.error），无重试/告警，留 ≤26h。与 G1/F1 同吃「读侧版本指纹」兜底，可并入 A 方案。
