# 共享后端只读核查

本轮仅调查。没有修改源码、新增测试、commit/push、部署、业务写入；下述建议均未实施。所有者最新口径覆盖早期修复授权。

## 版本与证据边界

- cart：`7ea045de6401499607836446c22e22b936e40072`，本地/远端需求分支一致，工作区干净。
- order：`e464fa98bd4fdc6c1ad9ee1e5e4f1f90a07bd507`，本地/远端需求分支一致。
- 统一后端分支：`feature-xuban-pure-relation-20261102`。基线依据已有归档登记 origin/release，未更换基线或分支。
- product-server 首读 `592e96a09` + 3 个预存未提交文件；调查中共享现场变为 `7da8a1432a22b26694d05ef2bb12a8e661ae21f6`，工作区变干净。主 W1 没有执行这些源码修改或 Git 写入；不能把新提交归为本轮交付，也不能继续按旧版本缺字段下最终结论。
- PRD：企微 docx `W4ftd48kFoq1LyxMrVYc1AhynFe` revision 253；纯续 `WDYOddTNloOrunxiCzmcnNzJnFe` revision 659；技术方案 `AQEtdIeKzo7P5IxeQEzc7EpxnBe` revision 72。PRD 正文优先于旧方案；最新所有者决定优先于旧归档。
- 下列“已证实”指完整源码路径已证实，不等于线上已发生。本轮未确认需求分支与生产发布版本对应关系。

## 已证实的实现偏差

### B-CART-01 从计划配置丢失，合并前置课不等于合并推荐结果

- 预期：A 关联 B 后，A 展示 A、B 各自原有纯续推荐结果；大小班原推荐逻辑不变。B 自身入口不因被关联而扩大。
- 实际：`RenewalDataService#mergeRelatedPreCourseNumbers` 只读 B 的 `courseNumbers` 并覆盖 A 的字段；`type/productType/renewalRecommendMap/productNumberList/combineProductSkuNumbers/recommendMapType` 均继续用 A 的配置。
- 触发：B 设置了与 A 不同的指定班级白名单，或 B 为联报/组合商品而 A 为单课，或反向组合。
- 影响：B 原来指定的后置班被降级成自动推荐；联报/组合商品范围、类型可能被主计划覆盖。即使返回了两种前置课，也不能证明原推荐规则保留。
- 证据：cart `RenewalDataService.java:290`、`:304`、`:312`；`RenewalService.java:260`、`:1521`、`:1575`；`small/builder/sub/WhitelistBuildSubBuilder.java:51`、`PreClassInfoBuildSubBuilder.java:48`；`small/plugin/WhiteListMatchPlugin.java:59`、`:66`、`:113`。
- 建议：按来源计划保留完整纯续配置和原引擎语义，再按同年级同商品合并；不能仅把缺失白名单当“降级正常”。先确定多计划共享同一前置课而配置不同的优先级。
- 不改：有差异配置的关联计划无法保证“只扩大范围，不改变推荐逻辑”。当前有效历史样本没有覆盖白名单/联报/组合差异；本轮未造数。

### B-CART-02 小班主计划关联大班从计划，库存与商品类型链路不兼容

- 预期：小班主计划链接也能正确展示、报价大班从计划商品，商品类型保持大班 `2`。
- 实际：小班构建器给所有前置课赋主计划 productType；库存构建器只接受 `6004`，显式跳过大班 `2`；后置班库存默认 null，库存插件要求非空且 >0。单课 ProductKey 固定 `6004`。
- 触发：小班主（单课 6004）关联大班从，走小班引擎且默认库存插件开启。正常自动匹配路径会剔除缺库存的大班后置班；若由更早的已购/白名单插件中断放行，商品类型仍可能成为 6004。
- 影响：反向跨模式推荐少商品，或下游拿到错误商品类型。没有证明当前生产已出现此情况。
- 证据：cart `small/builder/sub/PreClassInfoBuildSubBuilder.java:48`、`:67`；`StockInfoQuerySubBuilder.java:65`；`PostClassInfoBuildSubBuilder.java:188`、`:234`；`small/context/SmallRenewalPostClassInfo.java:66`、`:70`；`ProductKey.java:74`；`ProductType.java:18`；`small/plugin/StockMatchPlugin.java:66`、`:84`；`SmallRenewalCoreService.java:621`。
- 建议：按来源计划和实际商品类型保留各自引擎、库存和报价契约，补“小班主→大班从”的最终商品/类型验收。
- 不改：旧验证只证明反向预热 `preClassCount=2`，不足以支持反向推荐已完成。

### B-CART-03 扩科年级上下文扩大，关联后可能新增主计划扩科项

- 预期：只扩大纯续范围；A 只推 A 的扩科，扩科行为不因关联 B 变化。
- 实际：扩科配置确实只取 A，但大班将合并后的纯续结果转成后置课程年级，小班则遍历合并后的前置课与续班关系收集年级。
- 触发：A 的扩科配置含某年级，该年级只从 B 的在读/后置课产生，并通过其他过滤。
- 影响：关联 B 后出现原先不出现的 A 扩科项；“没改扩科类”不能证明行为不变。
- 证据：cart `RenewalService.java:257`、`:274`、`:368`、`:386`；`small/service/ExpandSubjectRecommendService.java:65`、`:120`、`:168`。归档 README“扩科不变性对照”曾记录 grade11 的此类实测，trace `cart_gaotu100_com.291.17937237475350010`；这是历史记录，本轮没有重放。
- 建议：将纯续合并上下文与主计划扩科计算上下文分开。需所有者判断“扩科不变”是否要求结果严格不增；PRD“无变化”支持严格保留，旧归档用“正常配置不会触发”淡化影响没有业务依据。
- 不改：特定跨年级配置下扩科范围跟随纯续关联变化。

### B-CART-04 关联变更或开关回退后，预热缓存仍可返回旧推荐

- 预期：解绑/重绑后按新主从集合推荐；回滚开关置 false 回到单计划。
- 实际：预热缓存 key 只有主计划与用户；读取时不比较当前关联集合、版本或开关。保存关联只清 product-server 的关系 key，未清 cart 的预热结果；默认预热 TTL 为 26 小时。
- 触发：有旧预热缓存，`preheat.cache.enabled=true`、`fromBCart=false`，此时改变关联或关闭纯续关联开关。
- 影响：解绑后仍显示原从计划、绑定后暂缺新从计划、关开关仍可能返回并集。
- 证据：cart `RenewalService.java:347`、`:1069`、`:1227`、`:1319`、`:1341`、`:179`；product-server `RenewalMasterRelationService#save` 只删除 `renewal:relation:{main}`。
- 当前配置：只读 Apollo TEST/application `preheat.cache.enabled=false`，PROD/application 为 true；该测试公共配置关闭预热；旧记录未给出开启预热命中缓存的对照，不能证明该路径正确。未确认生产部署本需求版本，不能称生产故障。未配 TTL 项按代码默认 26h，未读取运行实例字段或逐泳道覆盖值。
- 建议：关联/开关版本参与预热命中校验，或在变化时失效并重建；若暂不改码，发布与回滚必须有可执行的缓存处置，但无法替代日常运营解绑的一致性。
- 不改：开启预热的环境有旧结果窗口。未做写缓存/解绑的运行态复现。

## 待运行态核实的关联影响

### V-CART-01 从小班商品换班仍按大班主计划查 type=2 库存

`RenewalService#productSelect:2713` 仍按主计划类型分流，大班分支 `:2803-2806` 对候选统一调用 `getClazzCount(...,2)`；推荐入口 coreHandle 已按实际商品类型分组，换班入口没有对齐。大班主链接选从小班课换班时可能查错库存类型。需前端真实操作请求和库存响应闭环；本轮未点击页面，未调用会保存选择的接口。建议按商品真实类型路由库存/选择；不改有“推荐能看，换班失败”的风险。

### V-CART-02 Guava 对象被原地合并污染（当前公共配置关闭查询缓存）

`RenewalDataService:272` 从 Guava 取 DTO 后 `:312` 原地覆盖 courseNumbers；`cache/handler/AbstractGuava.java:36` 返回 `getBasicObject()` 原引用，`:160` 原样存入；`cache/model/CsGuavaObject.java:29` 直接返回引用。

若开启查询/本地缓存，先访问 B→C 再访问 A→B，可把 B 缓存中已合入的 C 带给 A；关开关后同一缓存对象也可能残留旧并集。只读 Apollo TEST、PROD application 都是 `renewal.query.cache.enabled=false`，因此不列为这两个公共配置下当前已触发故障。建议请求内复制 DTO 并保留原始课程集；不改会限制将来安全开启已有缓存能力。本轮未开关配置、未做运行态重现。

### V-ORDER-01 重复课程校验只记第一次商品类型

order `CartSameClazzOrCourseImpl.java:65`、`:90`、`:104` 每个课程/班级只记首个类型；跨模式放行直接 return，不登记第二模式。代码推演：同课程 C 按 `[2,6004,6004]` 输入，后两个均与首个 2 比较而放行，不能拦第三项与第二项的同模式重复。

该校验器的条件性算法缺口可从源码确认；还没有真实“同一课程号横跨两模式”的商品样本，不将其包装为真实可下单复现。其他限购按商品也可能拦截，不能据此宣称整条下单绕过。建议按 `(课程/班级,模式)` 记录已见集合；不改在该输入成立时不满足“同模式重复仍拦”。开关关闭保留原重复拦截。

## 保留行为与不应误报项

- PRD 备注明确不同收款主体不可一次下单。order `PaymentSizeImpl.java:99` 按 collectionAccountNumber 调合并支付规则；未改该类本身不是本需求缺陷。历史“跨模式就放行 PAYMENT_SIZE”的技术文案与 PRD 冲突，应由所有者按最新正文判断，不能无条件放行资金校验。
- cart 纯续内部不按相同学科去重；`RecommendMergeService:62` 保留纯续列表，`:73` 的年级+学科过滤作用于扩科。因此没有仅凭存在学科去重代码就认定违反纯续要求。
- 无关联/开关关的旁路订单补查会返回原结果；这一结构保留。但开启预热时回退仍受 B-CART-04 影响。
- 历史已通过的大班主→小班从推荐、同单下单、同年级同商品去重可作为特定版本/样本历史证据，不外推到反向、组合/联报、缓存变更和页面。

## 本轮实际验证

在 cart 上执行现有测试（未新增测试文件）：

```sh
mvn8 -pl cart-app -am test -Dtest=PreClassInfoBuildSubBuilderTest,WhitelistBuildSubBuilderTest,WhiteListMatchPluginTest,ExpandSubjectRecommendServiceTest -DfailIfNoTests=false -Dsurefire.failIfNoSpecifiedTests=false -DskipTests=false -Dmaven.test.skip=false
```

2026-11-04 15:55:13 构建结束，测试报告 XML：33 tests、0 failures、0 errors、0 skipped；四类分别 7/6/13/7。日志中出现过 TestNG “No test suite found”，随后执行 JUnit 兼容测试；已按 XML testcase class 逐项核实，不以 BUILD SUCCESS 单独判断。测试只覆盖原有构建器/白名单/扩科基础规则，不覆盖本轮发现的跨计划场景。

证据：`/tmp/w1-e0be7208/cart-existing-tests.log`、cart `cart-app/target/surefire-reports/TEST-TestSuite.xml`；Apollo 已发布配置只读结果 `/tmp/w1-e0be7208/cart-apollo-test.json`、`cart-apollo-prod.json`（文件内容为 CLI 文本输出）。

没有执行推荐接口、写关联接口、订单、支付、消息/job、ES回溯或页面编辑。推荐接口中 `RenewalService:1622` 存在删除失效勾选记录的隐式写入，因此本轮未把“GET/取数”当天然只读。
