# 2026-11-12 Cart 续班代码审查与既有用例重跑

结论：主、从计划各自推荐再合并纯续的方向可保留；当前合并预热的读路径还不能认定与实时路径等价。复现 2 项正常业务问题，另确认 1 项换课缓存失效遗漏。未修改 Cart 代码。遵守“关联稳定，变更后重新预热”的业务前提，不提出版本机制要求。

## 范围和证据

- 目标分支 `feature-renewal-preheat-small-refactor-20261111`，提交 `da7b9d06836b2cdd607a760555dbbc9ce1e5f735`。
- 代码基线 `origin/feature-renewal-clazzset-dedup` / `e315a655da44cebac1638b759984cc91f552c662`；基线运行镜像 fd1fdc28 与该引用仅 tasks/todo.md 不同，业务代码一致。未使用 master。
- 目标实例 `test-eco-1`，`10.218.249.187:28688`，镜像 `feature-renewal-preheat-small-refactor-20261111-da7b9d06-20261112001751`；直连固定实例，HTTP 带 traffic-env。
- 复用 [飞书 P0 用例](https://gaotuedu.feishu.cn/docx/ZQUXdlDxWoknJhxu914c2uVYnBr) revision449，重点 EM-02、EM-03、EM-07 及历史组合商品样本。另查到 [5计划14关系配置](https://gaotuedu.feishu.cn/docx/HqaEdvM9rotA6bxYv2jcGKjPnrf) revision7，该文档没有可直接执行的学员样本，未作为运行通过证据。
- 目标版本：6 组计划/学员 × C、B实时、B(fromC=1) × 预热前后，共 36 次查询均 code=0；6 次单用户预热均返回非空纯续 map。另做同实例 3 组缓存/跳过预热对照。接口成功不等于业务全部通过。
- 本地现有聚焦回归：231 项，失败0、错误0、跳过0，日志 `local-tests.log`。未新增或改写测试。
- 基线实例 `test-gtbg-dev-1` 另执行18次查询。测试 Redis 共享且已有新格式缓存，部分基线 C 查询报错；不把这批结果当作完全隔离的新旧A/B验收。主要缺陷由同目标实例两条代码路径和原始HTTP响应互证。

## 样本矩阵

|代号|入口计划|学员|当前关系/覆盖|
|---|---|---|---|
|M|588858850300473344|7658129872|大班主，关联A、B；2/6004混合|
|A|585960797778243584|7658129872|大班主，关联B；自身扩科|
|B|586116340522184704|7658129872|小班，无出向关联；纯续和扩科|
|J|545361759016388608|654745|当前入口商品类型2，关联JS；从计划组合51|
|JS|551533000353986560|654745|小班组合51，关联J|
|M2|588858850300473344|7707220467|大班主入口，当前C可展示已购小班商品|

C=`/web/renewal/cart?renewalNumber=...&appointUserId=...&includeBCart=false`；B=`/web/renewal/operation/cart?renewalNumber=...&userId=...&fromC=0`；BC=同接口fromC=1。预热=`/web/renewal/preheat?renewalNumber=...&userId=...`。原始请求、响应、trace 在各泳道子目录。

## F1：预热命中后从计划强购标记被主计划覆盖（运行复现，P1）

J / user654745 的组合 SKU551700015760906241：预热输出 force_buy=true；同实例跳过预热读的 C 推荐 forceBuy=true，命中合并预热后 forceBuy=false。HTTP J-C-after 同样 false，而 JS 自身 C 推荐 true。这会改变从计划商品的强购标记，已违背两条路径应等价的目标。

根因：RenewalService.java:567-572 对整个合并 map 统一写主计划 renewalForceBuy；实时链路中从计划在独立计算时使用自身配置。缓存的商品范围正确，但商品规则被入口计划重写。

建议：只给入口计划自己的纯续条目设置入口强购配置，保留从计划已算好的规则；若产品最终规定所有条目跟主计划，也必须让实时和预热两条路径统一。本分支当前“各计划独立推荐再合并”的实现应保持从计划结果。

证据：test-eco-1/J-preheat.json、J-C-after.json、JS-C-after.json、same-instance-cache-vs-realtime.txt。HTTP trace `cart_gaotu100_com.299.17944255627670164`。

## F2：已报名的小班商品，合并预热后总报名状态错误（运行复现，P2）

M2 / user7707220467：C 返回唯一商品586097025945298944，signUp=1；同实例跳过预热时 allSignUp=1，命中预热时 allSignUp=0。A 也可复现；A 的两件纯续均已报名，但合并缓存路径 allSignUp=0。

根因链：RenewalDataService.standalone（445）先清空 relatedRenewMasterNumbers；RenewalService.queryClazzOrderInfos（838）把混合班级条目交给订单查询，但 withPostClazzOrders（RenewalCrossModeOrderService:157）以关联列表为空为由跳过小班 order_item 补查。processClazz（2050）没有拿到小班有效订单，把总体状态置0，却保留缓存条目的 signUp=1，因此出现同一响应自相矛盾。

建议：按结果商品实际类型查询报名状态，混合结果中的6004补查 order_item，不再依赖已被standalone清空的关系列表；再按同一口径计算商品和总体状态。不要仅把总体状态改为缓存signUp的汇总，以免掩盖后续支付后的刷新问题。

证据：test-eco-1/M2-C-before.json、M2-C-after.json、A-C-after.json、same-instance-cache-vs-realtime.txt。M2 HTTP trace `cart_gaotu100_com.298.17944255699460167`。

## F3：在主计划页面更换从计划课程，只清从计划缓存（代码确认，未执行换课，P1）

正常流程：主计划M已预热并包含从计划B的推荐；用户在M入口更换B的课程。productSelectConfirm 现在把选择存入所属计划B，并只 invalidateUserPreheat(B,user)（RenewalService:3358、3377）；Helper:99仅删除传入计划的一个 key。M的合并预热key没有清理；下次M页面仍命中旧map，跳过重新计算从计划，可能继续展示换课前的商品/选择。

这与配置变更无关，是用户日常换课流程。dedup基线原实现删除 request.renewalNumber 的入口key；本次改为owner后漏掉入口。

建议：至少同时清 request.renewalNumber 与 ownerRenewalNumber 的当前用户缓存，去重即可。若业务要求其他关联入口立即同步，再按明确范围补齐，不需要版本机制。本轮未写学员选择记录，因此不把此项标成运行复现。

## 其余现象和通过范围

- 2/6004/51 混合推荐能正常返回；B无出向关联时，纯续未反向带出主计划商品；从计划扩科没有混入M的展示结果。这些支持独立推荐再合并的业务方向。
- M主商品588861402658267136当前 saleStatus=50，已只读回查；C不推荐、B实时仍显示的差异符合两入口已有售卖过滤差异，不计回归缺陷。见 test-eco-1/main-clazz-current.json。
- A非默认年级16的纯续商品：命中缓存时name/price为空，跳过缓存时完整。processClazz只补默认年级详情，且现有productList支持按商品补详情。记录为返回契约差异，尚未验证前端是否正常补齐，不直接判定页面/购买故障。
- 首轮HTTP前后，A/B扩科商品集合有变化；同实例后续对照A只剩名称/价格、总体状态差异。未排除现有数据/依赖缓存变化，不归因为确定回归。
- 历史“联报入口”J当前productType=2，实际商品为51；本轮不能宣称真实23联报商品已验。
- 未执行订单创建/支付、修改关系/Apollo、切换学员年级/课程、批量发送消息。仅更新6个测试用户级预热缓存和测试记录。

## 建议的最小收敛

保留主从各自推荐、只并纯续的设计；重点把缓存消费和实时消费的商品规则、报名状态、选择后的失效范围对齐。优先补“同一真实样本→实时→预热→缓存命中”的字段对照，以及“主入口更换从计划课程→再次读取”的业务回归。现有231项通过只证明局部测试通过，尚未覆盖以上组合路径。

本轮结果已追加到[原飞书P0文档本轮记录](https://gaotuedu.feishu.cn/docx/ZQUXdlDxWoknJhxu914c2uVYnBr#doxcnVdJcS5gYCRX58AkMagGHCg)，revision450，并回读整节核对，回执见feishu-record-readback.json。


## 2026-11-12 09:13 最新提交复核（2c6ff967）

- 本地与远端目标分支均为 `2c6ff967ac8a39c9f3e3ad971e1c28d96a5ff7b3`；dedup 仍为 `e315a655da44cebac1638b759984cc91f552c662`。相比前轮 `da7b9d06` 只新增3个测试类、54个用例，业务源码 diff 为空，因此 F1/F2/F3 对当前源码的判断不变。本轮未重新核验部署或重放远端业务请求。
- 实际执行7个现有测试类，共94项，失败0、错误0、跳过0。日志 `recheck-2c6ff967-tests.log`。未修改Cart源码或测试。
- 新增测试补充了商品类型解析、缓存读写契约、主从编排；但未覆盖主从不同强购配置的实时/缓存等价性、6004已购与总体报名状态一致性、主入口换从计划课程后的入口缓存失效。`RenewalRealTimeRelatedPlanTest` 中扩科及加购服务固定返回空，三路合并器mock成只返回纯续；不能据此认定跨计划扩科去重通过。

### F4：大班入口扩科的跨计划去重范围随缓存命中变化（代码确认，尚未用真实样本复现）

正常场景示例：主计划纯续为七年级数学，同时配置七年级英语扩科E1；从计划纯续为七年级英语E2，E1/E2是不同商品，`allowDuplicate=false`。

实时路径先算主计划，主计划自己的纯续中没有英语，所以保留E1；随后 `RenewalRelatedResultMerger.addPure`（112）只按同年级SKU去重，追加E2，最终E1/E2均在。

大班入口命中合并缓存时，`getLargeClassRenewalDetail` 的 `renewalCourseDTOMap` 来自完整 `classEntries`，含从计划E2；608-628行按完整纯续集合的年级/科目过滤主计划扩科，E1被移除。这里选择6004/2班级条目即可触发，不依赖组合商品或配置中途变化。

这证明两条代码路径的判重范围不一致；本轮未构造或修改计划配置来做远端实测，不记为运行复现。建议将跨计划的商品去重、年级科目去重及纯续/扩科优先级放在同一合并阶段，实时和缓存共用；主计划扩科候选仍按其自身配置及前置课计算。此结论不要求引入复杂策略框架或缓存版本机制。
