# V2 新增代码设计模式抽象方案（先方案不动代码）

> 2026-11-16 · 响应 owner：『新增的代码/类中哪些地方可以用合适的设计模式进行抽象、分隔、解耦，后续能更快更好地增加商品、解析商品，改造成本更小』
> 标尺：**下次再加一种商品类型（解析/组装/校验）能否一处接入**。以本次联报(23)补丁的真实代价为实证。

## 一、实证：加一种商品类型现在要改几处

23 补丁（1848584c + 1a8ec96e，5 文件 +363/-3）的完整触点：

| # | 触点 | 文件 | 改动内容 | 本质 |
|---|---|---|---|---|
| 1 | 类型枚举 | `ProductType` | +ACTIVITY(23) | 类型声明 |
| 2 | Key 工厂 | `ProductKey` | +ofActivity | 类型构造 |
| 3 | 候选构建 | `SmallRenewalCoreService#buildCandidates` | +23 分支（if-else 第三支） | 按类型选候选来源 |
| 4 | 白名单校验 | `WhiteListMatchPlugin#validateWhitelistProducts` | +23 分支（if-else 第三支） | 按类型校验有效性 |
| 5 | 展示组装 | `RenewalSinglePlanDetailService#processClazzSetResult` | postClassInfo 空时降级 | 按类型组装 VO |
| 6 | 组装分发 | `convertToRenewalCartVO:2005-2016` | 无需改（23 分支已存在） | if-else 三支分发 |

**结论**：推荐层 4 处（#1-#4）是同一件事的四个切面——"按商品类型选择行为"，全部用 if-else 串联，每加一类就要在 4 个文件里各插一支。展示层（#5/#6）参数重、刚经 F2 修复稳定。

另有两处**已经是一处接入**（无需再抽象）：SubBuilder 链（`supports()` 按 productType 启停，如 CombineProductBuildSubBuilder supports 51）、排序插件链（`supports()` 同模式，23 暂无排序需求，需要时加一个类即可）。

## 二、方案清单

### 方案一【建议做】推荐层类型策略：`ProductTypeHandler`

**现状问题**：#1-#4 四个触点分散在 4 个文件，if-else 按类型串联；23 补丁横切 4 处、51（2026-04）当年同样横切。类型行为（候选来源/白名单校验/Key 构造）内聚性被文件边界打散——改一个类型要开 4 个文件，review/回归面随之扩大。

**建议模式**：**策略模式（Spring 多实现注入）**——收编 #1-#4 为一个策略接口 + 每类型一个实现类：

```java
public interface ProductTypeHandler {
    Integer supportedType();                                                   // 6004/51/23
    ProductKey newKey(Long productId);                                         // 收编 ofXxx 工厂
    List<ProductKey> buildCandidates(SmallRenewalRecommendContext ctx,
                                     SmallRenewalPreClassInfo pre);            // 候选来源
    boolean isWhitelistValid(Long productId, SmallRenewalRecommendContext ctx); // 白名单校验
}
// ClazzProductHandler(6004) / CombineProductHandler(51) / ActivityProductHandler(23)
// 各 @Component，构造器注入依赖；SmallRenewalCoreService 注入 List<ProductTypeHandler>
// 构造 Map<Integer, ProductTypeHandler> 路由——与现有 matchPlugins/sortPlugins 注入方式一致
```

**收益**：
- 新类型=**一个类一处接入**（枚举值随 handler 的 supportedType 声明，可把 ProductType 枚举改为由 handler 驱动或保留双登记）；23 那样的补丁从 4 文件缩到 1 文件+单测
- 类型行为内聚：候选来源+校验+构造在同一类里读得完，不用跨文件追 if-else
- 复用现有模式：注入 List<接口> 建 Map 路由与 SmallRenewalCoreService 现有 matchPlugins 完全同构，团队无学习成本
- 不违反宪法：接口+3 实现（非单实现）；无新 Util/Helper

**成本**：
- 一次性迁移：buildCandidates/validateWhitelistProducts 现有 2/51 逻辑搬进各自 handler（约 -80 行 if-else、+3 类 ~200 行含迁移）；单测跟着搬（现有 WhiteListMatchPluginTest/ActivityProductRecommendTest 适配）
- ProductType 枚举与 handler 的双登记需要约定（建议保留枚举做单处权威，handler 引用它）

**风险**：低——行为等价搬迁，路由 Map 未命中时回退现有默认分支兜底（可加 log.warn）；老代码大班链零涉及。

**是否建议做：✅ 是**（下次再加类型前做最划算；现在做也可与 23 补丁回溯合并验证）。

### 方案二【暂缓】展示组装接口化（processXxxResult 系列）

**现状问题**：`convertToRenewalCartVO` 按 isSingleClazz/23/51 三分发到 processSingleClazzResult/processClazzSetResult/processCombineProductResult；三个方法签名重（7-8 个 map 参数）、且 processClazzSetResult 刚经 F2 修复（1848584c）+回退态大班版本（processClazzSet）另有 11-14 判空取舍——展示层确实也有类型分发，但**改动它触的是刚稳定的代码**。

**若做**：同一 ProductTypeHandler 加 `assembleVO(result, AssembleContext)`，把 7 参数收拢为一个 AssembleContext。**收益**是分发统一；**成本**是引入新上下文对象+双版本（纯续/FULL）的组装语义搬移；**风险**是 F2 修复、11-14 取舍、回退态行为都在这层，回归面大。

**是否建议做：❌ 暂缓**——YAGNI：展示层三类型行为差异大（单课/联报活动/组合 DTO 结构不同），强行统一签名会造"参数黑洞"对象。**触发条件**：下次新增类型时其展示组装与现有三者都不同构，再抽不迟。

### 方案三【条件做】联报信息 SubBuilder（复用 supports 模式）

**现状**：23 的可售性兜底在展示层（ClazzSetVO 查不到跳过），推荐层不预载活动信息；大班链有联报库存缓存（RenewalService:218）。若未来 23 需要**推荐期可售/库存校验**（白名单校验升级）或年级解析增强，按现有 SubBuilder 模式加 `ClazzSetBuildSubBuilder`（supports productType=23，查 ClazzSetVO 进 context）即可，WhiteList 校验从 handler 里读 context——**不动主链**。

**是否建议做：⏸ 条件做**——当前 23 场景（白名单 interrupt+展示兜底）已验证够用；出现"不可售活动被推荐"的实际问题再做。

### 不建议动的清单（明确说明为什么）

| 处 | 为什么不动 |
|---|---|
| 老代码大班链（RenewalService 的 23/51 处理） | owner 六轮口径：老类不动；且它是线上原样参照系 |
| RenewalV2ResultMerger | 类型无关（按 grade+sku 去重），无类型分发可抽 |
| RenewalV2PureRenewalService（合并/提取/缓存） | 类型无关（beforeCourseNumber 通用键）；职责单一 |
| 排序插件链/SubBuilder 链 | 已是 supports() 一处接入模式，是本方案要**对齐**的范本而非改造对象 |
| RenewalSinglePlanDetailService 巨类拆分 | 已按模式收敛过（59be925b 单计划入口收敛）；再拆牵动新老共用路径，收益低 |

## 三、实施建议（经 owner 认可后）

1. **顺序**：先方案一（推荐层，风险低行为等价）→ 观察一个迭代 → 按触发条件决定方案三；方案二挂起。
2. **验证口径**：方案一落地时用 23 的同套验证链（单测+实时/预热端到端+compare 31 样本回归零破坏）——正好复用本轮已固化的回归资产。
3. **规模预估**：方案一约 1 人日（迁移+单测+回归）；无 DDL/Apollo/上下游依赖。

## 四、一句话总结

**真正值得抽的只有推荐层四处类型 if-else（方案一，策略模式，一处接入）；展示层暂缓（刚稳定+签名重）；其余要么类型无关、要么已是一处接入。**

---

## 五、实施记录（2026-11-16 深夜·方案一 owner 已批）

**状态：✅ 已实施、已部署、等价性验证完毕（commit `636e67d0`，test-eco-8 部署，2026-11-16 23:00 前后闭环）。**

### 闭环验证（部署 `636e67d0` 新 pod t5nc4 = 10.218.249.53）
- **端到端（部署前后 + 与原基线三方一致）**：
  - 实时 `getPurePlanDetail(7704848531,"590843035351398400",false,true,null)` → 23 条目/activity=565844673592092672/before=after=590853244278898688/五年级——与原 TID 17948380350700006、部署前复采（旧 pod TID 17948400391750050）、部署后新 pod 逐字段一致。
  - 预热 `preheat(userId, mainConfig, related)` → 合并值 `{590853244278898688: 23条目, renewal_role=2}`——与原 TID 17948381795630008 逐字段一致。
- **compare 31 样本回归零破坏**：规则一 no_related **21/21 一致**；规则二 related **7/10**（3 个不一致=同批纯从学员预期差异 uid 7704850493/7704850494/7714163148，plan 589037361072007168，预热只处理主计划学员）；**与上一轮（1a8ec96e 部署后 compare_diff_20261116_221417）rule1/rule2 逐条签名比对完全相同**。本轮产物：`scripts/compare_baseline_20261116_224941.json` / `compare_v2_20261116_225012.json` / `compare_diff_20261116_225022.json`。
- **Apollo**：验证期间临时开 recommend.v2=true（release 20261116225001），验毕恢复 false（release 20261116225053）；三开关回读全 false。
- 单测：定向 5 类 79/79 全绿；全量 563、15 失败=既有基线（无新增失败）。

### 已改（commit `636e67d0`，基于 HEAD 1a8ec96e）
- 新增 `small/handler/` 包：`ProductTypeHandler`（接口）+ `ProductTypeHandlerRegistry`（@Component，List 注入建 Map，get/getOrDefaultClazz）+ 三实现 `ClazzProductHandler`(6004)/`CombineProductHandler`(51)/`ActivityProductHandler`(23)——各实现逻辑从原 if-else 分支**逐字等价迁移**（含 23 的 1a8ec96e 口径与 51/6004 原口径）。
- `SmallRenewalCoreService`：构造器 +registry 参数（5 参）；`buildCandidates` 改策略路由（未知类型/null registry→空候选，等价原未命中）；2 参测试构造器内建真实 registry。
- `WhiteListMatchPlugin`：构造器注入 registry；`validateWhitelistProducts` 改 `getOrDefaultClazz(productType)` 路由（类型缺失/未知默认按班级校验=原 else 兜底语义）。
- 测试适配 4 个：`ActivityProductRecommendTest`（真 registry 路由）、`WhiteListMatchPluginTest`（去 @InjectMocks 改手动构造真 registry）、`SmallRenewalCoreServiceIntegrationTest`（registry 传入）、`SmallRenewalCoreServiceTest`（registry 传入，曾传 null 导致 17 失败已修）。
- 未动：老代码大班链/ResultMerger/PureRenewalService/排序与 SubBuilder 链/展示层（方案二三不做）。

### 验证进度
- ✅ 定向 5 类 79/79 全绿（含 23 候选/白名单/51 回归/路由真实行为）。
- ✅ 全量 563、15 失败=既有基线（无新增失败）——**等价性代码层达成**。
- ✅ 端到端 + compare 31 样本 + 部署 test-eco-8 + Apollo 恢复回读（见上方"闭环验证"）——**全部完成**。

### 接手指令（已全部执行完毕，留作流程存档）
1. 端到端复采：pod 直连（当前最新 pod 需重新 qingzhou 查或沿用部署后新 IP）桥调 getPurePlanDetail(7704848531,"590843035351398400",false,true,null) 期待与 17948380350700006 相同（23 条目+before=590853244278898688）；preheat 同参数（camelCase！内层 configs 也 camelCase）期待与 17948381795630008 相同（role=2）。
2. compare 31 样本（scripts/renewal_cart_compare.py --phase baseline/--phase v2/--diff，prefix 须 false）。
3. commit（refactor(renewal): 方案一——推荐层商品类型策略收编…）→ push → qingzhou 部署 test-eco-8（service_code=gaotu_cart）→ 部署后 pod 复跑①②确认线上等价 → Apollo 恢复回读。
4. 本文档标注"已实施验证完毕"+empirical-status 追加+owner 简报（改了哪些/为什么/等价性证据）。
- 坑复用：桥 DTO 全 camelCase（内外层都是）；compare 后恢复 recommend.v2=false；造数数据全部就绪勿重建。
