# 交接 Prompt：cart 续班 V2 组合商品加购——③口径更正实施与验证（2026-11-19）

> 使用方式：把本文件全文作为一个 prompt 交给接手 AI。内容自包含，无需其他上下文。

---

## 一、背景

- 需求：cart 服务「组合商品加购」——B 端二讲勾选的加购组合商品在 C 端续班推荐页展示。PRD wiki：https://gaotuedu.feishu.cn/wiki/D89iwm9U1iL6vWkEOgwcg8otnqc ；方案见需求归档第二十轮（路径见文末参照物）。
- 仓库：`/Users/gaotu/IdeaProjects/JavaProject/cart`，分支 `feature-renewal-preheat-v2-20261112`，当前 HEAD=**ce3c66cf**（已推送，工作区干净）。
- 已交付（勿重做）：
  - `@2b8da20a` 小班主计划加购组合展示（V2+老链最小支持），测试文档场景 16-18 全部验证通过；TAPD 1122531521001486137（加购成功后 C 端未返回组合）已据此流转已解决。
  - `@ce3c66cf`（3 提交：4ce03179/ab94a84c/ce3c66cf）组合加购五项整改（旧口径③），已部署 test-eco-8，V2 逐 case 运行时验证通过（归档第二十一轮表），单测 31/31。
  - 全量 case 回归已跑（2026-11-19 16:50 实测 @ce3c66cf，写入 owner 测试文档「全量 case 回归」章节）：38 条详情 case 30 过 + 8 条差异（全部定性为五项整改有意效果，见「8 条组合加购差异核对」小节）；预热 vs 实时 23/23 一致；已修复缺陷回归 4 条通过、D1 落库通过但展示侧 defaultSelect 未切年级（trace 6321285c-a4b0-4724-b464-e343a150af50，遗留待查）。
- 接力原因：owner 在 ce3c66cf 之后**更正了③的口径**（此前给错），更正后的代码修改未实施；case 已按更正口径补进测试文档场景 20（2026-11-19 第三批），由你执行。

## 二、领域口径（owner 澄清，勿再确认）

- **续班计划类型只有大班课、小班课两种**（`RenewalPreCourseDTO.type`：1 大班 / 2 小班；主从续班计划按主计划归入其一）。**不存在「组合商品类型」的续班计划**——组合商品是计划内可配置的「推荐商品类型」（`renewalConfig.productType=51` + `combineProductSkuNumbers`），大小班主从计划均可配置。③的设计只有大小班两分支，禁止构造「组合类型计划」的场景或枚举分支。
- 商品类型枚举（代码已有定义为准）：51 组合商品、6004 小班课、6003 1v1（不算小班课）、2 大班课、8014/8007/8010 会员卡/实物类（无班级子班）。

## 三、待办：③口径更正实施（唯一代码改动）

**最终口径（owner 已确认）**：③类型过滤**只作用于「推荐」来源**的组合——小班计划（含主从、主计划小班）推荐来源组合须含小班课(6004)；大班计划（含主从、主计划大班）推荐来源组合须含大班课；**扩科、加购来源不过滤**（扩科/加购无此要求）。因此 1v1(6003) 组合在加购来源继续展示。①②④⑤口径不变：①去重=组合按子班展开参与 (grade,subject) 判重+年级粒度；②已报名=组合按「组合SKU∪子商品SKU」命中有效订单、单班按班级号；④跨年级=方案 A（子班课程年级各出一条）；⑤卡片信息默认取开课最早子班；⑥膨胀券不做。

**改动点（全落新链 V2 类，已核实）**：
1. 删 `cart-app/src/main/java/com/gaotu/renewal/RenewalSinglePlanDetailService.java` 两处加购侧调用（③旧口径误加的）：
   - 小班加购段：`additionalPurchaseService.recommend(...)` 之后的 `purchaseResults = filterPurchaseCombinesByType(purchaseResults, ProductType.CLAZZ.getCode());`
   - 大班加购段：`bCartFacade.listAdditionalPurchase(...)` → `additionalPurchaseService.recommend(...)` 之后的 `purchaseResults = filterPurchaseCombinesByType(purchaseResults, LARGE_CLAZZ_PRODUCT_TYPE);`
   - `filterPurchaseCombinesByType` / `containsCombineSubProductOfType` 若再无调用方则一并删（YAGNI）。
2. 推荐侧收紧（补上 owner 口径的过滤）：`cart-app/src/main/java/com/gaotu/renewal/small/builder/sub/CombineProductBuildSubBuilder.java`——小班推荐引擎的组合商品构建器（计划配置推荐商品类型 productType=51 时启用，supports() 判 renewalConfig.getProductType()）。当前 6003/6004 都算班级类子班参与展开（isClazzLikeSubProduct，此用途保留：1v1 子班仍参与年级拆条/判重/最早子班），缺「组合须含 6004」的**推荐准入**——不含 6004 子班的组合不进推荐结果。落点可在构建准入处（buildCombineProductInfo 或组合候选过滤），自行看类内结构定最小改动。
3. 大班侧：coreHandle（大班纯续）不消费组合推荐配置（已核实无组合引用），「大班计划推荐须含大班课」分支现无落点（天然满足），**不构造**；扩科来源零过滤（现状即口径）。
4. 单测更新：`cart-app/src/test/java/com/gaotu/renewal/PurchaseCombinePolicyTest.java`——`should_remove_combine_with_only_1v1` 类断言按新口径反转（加购保留）；新增推荐侧准入测试（含 6004 保留 / 仅 1v1 不进推荐）。

**硬边界**：老链（RenewalService 及老链类）零改动；Apollo 零改动（`renewal.recommend.v2.enabled`/`renewal.preheat.v2.enabled` 当前 true/true、`v2.thread.pool...`10 为 **owner 自验状态，勿动**，Apollo appId=cart.gaotu100.com，TEST/default/application）；缓存零改动；少用/不用 arthas。

## 四、怎么验证（测试文档场景 20 = 逐条照单执行）

owner 测试文档：https://gaotuedu.feishu.cn/docx/EaKXdTkzXoJTStxBJH3cX7Qinzh **场景 20（20a-20i）**已按更正口径写好每条的：前置数据（去哪找/怎么造，含 b_cart INSERT 模板）、操作步骤、预期结果。执行要点：
- 环境：TEST 泳道 test-eco-8；部署用 qingzhou-deploy（branch=feature-renewal-preheat-v2-20261112，sub_env=test-eco-8），部署后核实 pod 版本=目标 commit。
- 入口：C 端 `GET /cart/web/renewal/cart?renewalNumber=…&appointUserId=…&sellerId=8645&includeBCart=true&p_client=EES`（头 traffic-env=test-eco-8；appointUserId 免登录依赖 Apollo `renewal.cart.debug.appoint-user.enabled=true` 已开）；对比接口 `GET /cart/web/renewal/preheatCompare?...`（返回 consistent+diffs）。
- 核心正向：20a 1v1 加购组合 580508980380479488 恢复展示（QA 复测看到「不返回」即待修现象）；20b 推荐位不含 6004 的组合不展示（样本需造：product 侧给小班计划推荐配置增配 1v1 组合；造不出则单测覆盖+运行时验含 6004 防回归）；20c 大班加购不过滤。
- 防回归：20e-20i——①②④⑤行为与 16:50 回归记录一致；compare consistent=true；单测全绿；38 条旧 case 重跑，预期变化仅③相关（1v1 加购组合由不出→出），其余逐条一致；区分「预期变化 vs 回归」。
- 造数：b_cart 可直接写 test 库（模板在场景 20 文末）；组合有效订单用 gaotu-data-seeding 下单 mock 支付；先搜现成数据再造。
- 每条 case 记录 GAPM-TraceID，执行后在场景 20 表格追加「实际结果+TID」。

## 五、验收标准

- 测试文档场景 20 全部 case 验证完毕，每条有结论+证据（TID/回读）才交付；结论三档分档：已验证（附证据）/ 推断未验证 / 没做。
- 交付时回报：改了哪些（文件:行号）、为什么、部署版本、逐 case 结果表、预期变化与回归的区分、遗留项。

## 六、当前状态 / 已知差异（2026-11-19 核实）

- ③更正未实施：test-eco-8 @ce3c66cf 现状=1v1 加购组合仍被过滤（预期内待办差异，非回归）。
- **回归补验结论（2026-11-19 17:5x 实测，只读，@ce3c66cf/test-eco-8）**：①版本核实=镜像 `20261112-ce3c66cf-20261119162444`，环境与 16:50 回归时一致，38 case 记录可复用；②抽样复跑 4/4 一致无疑似回归（A=3 TID…296.17950809396880407、C=5 TID…289.17950809832870409、D=5 TID…288.17950809950590401、工单组合 sjg 拆 5 年级+1v1 仍不返回=待办差异 TID…290.17950810303510410）；③D 组合 clazzDateDesc 空=子班源数据空文案、非回归（TID…292.17950812969100469；sjg 组合正常显示日期佐证最早子班逻辑生效）；④signUp 三态全对：有效订单=1（586097025945298944/585960755422160896@7658129872）、无订单=0、组合=0；git diff 确认 signUp 改动仅落加购段（applyPurchaseSignUp 两调用点均在 additionalPurchaseService.recommend 后），纯续/扩科 signUp 零改动；⑤E_bc 37/38/39 已判清=全部来自子班课程 grades=[37,38,39]∪[11]（TID…293.17950813102290458；复跑须带 sellerId=8645&p_client=1，漏传则加购段不触发、无拆条，非回归）；⑥缺陷单 1486168 现象复现（productList 6004 sign_up=0 vs cart signUp=1，TID…291.17950815914600499），独立单跟进不在本单范围。- 场景 19 的 19a 判定已作废（文档已加 callout 标注）；QA comment 1122531521001310369 的口径说明已过时，本轮已发更正评论（TAPD 1122531521001486137，保持 resolved，修复部署后 QA 复测 1v1 组合应恢复展示）。
- 遗留（不属本次③范围，勿顺手改）：D1 换年级展示侧 defaultSelect 未切（trace 6321285c…）；QA 独立缺陷单 1486168「切换年级后 signUp 丢失」；B 端条目为范围外。
- 测试数据（test 库 gaotu.b_cart 保留）：user 7658129872×account 90247（b_cart id 3513/3532=1v1 组合 580508980380479488、3533=sjg 组合 483217233600958464、3534=加购单班 591020573457448960）；7746793735 有 579426174109902848；关键 SKU：483217233600958464（sjg，6004，子班课程 grades=[11,12,13,14]+22）、590801222278299649（大班组合，判重样本）、589762111522013184（小班计划推荐位组合，6004×2，拆 37/38/39）。

## 七、参照物

- 仓库：`/Users/gaotu/IdeaProjects/JavaProject/cart`（分支 feature-renewal-preheat-v2-20261112，HEAD=ce3c66cf）
- 需求归档：`~/githubDir/quartzZZL/content/高途信息/需求/【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整/artifacts/20261116-f2-empirical-status.md`（第十六~二十一轮全记录：第二十轮=五项方案、二十一轮=实施收口、第二十二轮=本轮口径更正与接力）
- owner 测试文档：https://gaotuedu.feishu.cn/docx/EaKXdTkzXoJTStxBJH3cX7Qinzh （场景 1-20；「全量 case 回归」章节=38 条清单与 16:50 结果）
- compare 资产：`…【A-续班-20261102】…/scripts/renewal_cart_compare.py` + 31 样本基线 `compare_diff_20261117_154559.json` + fixture `cart_test_fixture.txt`（用法见同目录 README-renewal-cart-runner.md）
- TAPD 工单：1122531521001486137（已解决，QA 复测跟进中）；独立缺陷单 1486168（signUp 切年级丢失，不在本单范围）
