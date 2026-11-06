# 三个 MR 的代码审查基线（2026-11-06）

后续状态：F1/F2/F4及库存兜底范围已在用户授权下修复并验证；F3全集保存并发按用户要求不改。当前代码、部署、结果以[修复报告](20261106-relation-fix/README.md)为准。

## 范围与证据

对照需求 README、已有验证边界，读取 GitLab MR 当前 metadata/changes，并核对本地 HEAD 与 MR head 完全一致；逐项追踪相关调用方、订单适配器、库存服务与新增测试。初轮为静态审查；后续已按用户要求复用 TEST 造数完成定向运行验证，见下节。没有修改业务代码、调用业务写接口、部署或执行 Maven。F1/F2 已有当前版本运行证据；F3/F4 仍为代码条件推导，未做并发运行复现。

| 服务 | MR | 审查提交 |
|---|---|---|
| product-server | [862](https://git.baijia.com/gaotu/product-server/-/merge_requests/862) | 07ba05df6cfabcf0472e1ad27e26ff95cff98467 |
| cart | [284](https://git.baijia.com/gaotu/cart/-/merge_requests/284) | d572942668fc5566c7421005efa8f9a7ae22a21c |
| order | [2391](https://git.baijia.com/gaotu/order/-/merge_requests/2391) | 0cc8ef68b6c29f1d3101f5fa08ea7ec634050bf9 |

三个 MR 实际覆盖 EM 纯续关联，不包含 student-center/前端的企微标签、备注实现，因此不能据此宣称企微子项审查通过。已认可的预热最长 26 小时旧结果窗口不列为新缺陷。

## 造数与运行复核结论

- 时间：2026-11-06；环境 TEST/test-gtbg-dev-3。当前 cart 镜像 `feature-xuban-pure-relation-20261102-d5729426-20261106174905`、实例10.218.238.95，与MR head一致；没有拿昨日a34016fd实测冒充新版本。product-b07ba05df、order-b0cc8ef68；product-c本次未取得镜像，不推断其版本。
- 复用专用主计划588858850300473344、从计划586116340522184704；学员7707220467及7658129872，目标小班后SKU586097025945298944、前课18314034380997173、后课18314034380997207。主从关系直接DB回查有效。
- 样本有效性：小班saleStatus40、2课节、教师非空、容量20；实际库存18/锁定0/已用2。两个学员目标SKU的order_item均status2/refund0；大班后置亦有有效order_info对照。没有新订单、支付、关联或业务配置写入。
- 关键证据是**同学员、同SKU、同请求，仅换renewalNumber**的对照；因此可以排除“该商品本来不可用/没造好/没有支付”的替代解释。

| 检查 | 关联大班主计划 | 小班自身计划 | 判断 |
|---|---|---|---|
| operation/cart所用5参服务分支，已购小班SKU | sign_up=0 | sign_up=1 | F2已复现；两学员主计划均重现 |
| web/renewal/cart所用7参服务分支，同SKU | sign_up=0 | sign_up=1 | F2也影响C端使用的计算分支；不是浏览器端到端实测 |
| productSelect同前后课/SKU | errors=部分商品不存在 | 正常1件、sign_up=1 | F1已复现 |
| 同SKU库存按类型查询 | skuType2报部分商品不存在 | skuType6004返回stock_left18 | 错误根因进一步实证 |
| 推荐后回读主配置 | course_numbers仍仅主课588861395571990528 | — | 本样本未见主课集合被并集污染；不外推所有缓存开关组合 |
| 当前小班价格 | 推荐price=0 | 自身计划price=0 | 样本为0元，修正了课程中心-1哨兵；不覆盖收费小班金额链路 |

主要trace：换班失败 `.297.17939593176870012`、成功 `.292.17939593176870014`；C分支主 `.301.17939593801720014`、从 `.293.17939593801680018`；库存正确 `.292.17939593801680017`、错误 `.295.17939593803870015`，均以前缀 `cart_gaotu100_com` 拼接。完整请求、结果、耗时和实例见 [原件目录清单](20261106-runtime-review/manifest.json)、[DB独立回读](20261106-runtime-review/db-current.json)。ACL外层rvoCode0不等于业务成功，失败按errors字段判定。

### 下一步优化顺序

1. **先修两个实测业务问题**。按候选实际商品类型查询库存；补齐前置资格、后置已购优先、展示signUp的两类订单来源。回归两种主从方向，覆盖推荐→更换→已购展示；不把只修某一个入口当闭环。
2. **抽出小范围共用能力，减少入口规则分叉**。当前5参/7参推荐、productList、productSelect、小班引擎各自处理库存/订单，已证实同商品随入口而改变结果。建议共用按模式查询库存、查询有效已购、组装商品类型/价格的适配层；主计划配置仍决定推荐规则。无需为此重写整个推荐引擎。
3. **明确库存缺失与售罄的区别**。目前缺失被当可售、异常分组继续，会隐藏未来的数据不齐/类型错误。保留可观测的失败原因，决定只降级故障商品还是整体报错，不能统一认为可售。库存0、缺记录、服务失败应有不同用例；本轮未造故障或改库存。
4. **关系保存与缓存作为一致性专项**。按主计划锁/版本控制全集保存，事务提交后失效并防旧值晚回填。已认可的26小时预热窗口不是本轮重新要求推翻的规则；如后续要求关联撤销或退款更快反映，可考虑关系版本/订单事件定向失效，不能只叠TTL缓存。
5. **扩展现有fixture的区分能力**。现有成功同单是大班100分+小班0分、优惠0、同账号12；这只能证明该组合。后续补收费小班、售罄边界、退款后资格与已购状态、异收款主体/优惠最小反例。现存学员7658129872的大班后SKU588861402658267136现在已有新有效订单，不能继续沿用旧记录“未购”前提；每次复用先快照当前订单/库存/关系，避免假通过。

优先级边界：F1/F2为当前版本已复现，建议合并前处理；F3/F4为尚未动态复现的一致性风险；order全局去重和client类型兼容为范围/契约评估，不把条件性风险统称为线上故障。当前少量查询耗时不足以证明性能瓶颈，不据此提出线程池或缓存扩容。

## 建议修复的缺陷

### F1 · P1：大班主计划的小班从计划商品，更换班级仍用大班库存类型

- 新增合并前置课后，大班主入口可以返回 type=6004 的从计划推荐；`productSelect` 却仍按主计划分支执行，在主计划 productType=2 时给所有候选调用 `getClazzCount(clazzNumbersStock, 2)`。
- [漏改位置：RenewalService:2839](https://git.baijia.com/gaotu/cart/-/blob/d572942668fc5566c7421005efa8f9a7ae22a21c/cart-app/src/main/java/com/gaotu/renewal/RenewalService.java#L2839)；[本次已适配的推荐库存分组：1514](https://git.baijia.com/gaotu/cart/-/blob/d572942668fc5566c7421005efa8f9a7ae22a21c/cart-app/src/main/java/com/gaotu/renewal/RenewalService.java#L1514)。
- 触发：大班主计划关联小班计划，从计划候选为有限库存小班，库存仅存在于 (skuNumber,6004)。展示推荐成功后，对该商品调用更换班级。
- 结果：库存按 (skuNumber,2) 查询，`StockStrategyDistributeService#distributeBySkuInfo` 找不到对应库存并抛“部分商品不存在”；该入口没有推荐路径的分组处理。
- 修复：更换班级库存查询同样按候选实际商品类型分组；回归两种主从方向，以及换班候选价格/商品类型。

### F2 · P1：跨模式只补前置资格，漏补后置已购识别

- [本次旁路补查只接在前置订单：1391](https://git.baijia.com/gaotu/cart/-/blob/d572942668fc5566c7421005efa8f9a7ae22a21c/cart-app/src/main/java/com/gaotu/renewal/RenewalService.java#L1391)。后置课优先选择已购班级仍在 [1447](https://git.baijia.com/gaotu/cart/-/blob/d572942668fc5566c7421005efa8f9a7ae22a21c/cart-app/src/main/java/com/gaotu/renewal/RenewalService.java#L1447) 查 `order_info`，主列表的 `signUp` 在 [551](https://git.baijia.com/gaotu/cart/-/blob/d572942668fc5566c7421005efa8f9a7ae22a21c/cart-app/src/main/java/com/gaotu/renewal/RenewalService.java#L551) 仍只用 `ListByClazzNumbersAndUserIds`。
- 触发：大班主计划下，从小班计划推荐的 6004 后置班已支付，只有有效 `order_item`，没有对应 `order_info`。
- 结果：无法识别已购班级、`signUp` 仍为未报名，可能继续推荐同课其他班；已报名沉底/全部报完的展示逻辑也得不到正确信息。这里不推断最终支付必然能重复购买。
- 反向也存在同类遗漏：小班主路径的 `UserPostClassOrderSubBuilder:76` 只查 `order_item`，不能覆盖仅落 `order_info` 的大班后置班。
- 修复：前置资格、后置已购优先、展示已报名三个环节都按模式补齐订单来源，并保留各自有效状态/退款判断。验证同一学员同一后置班购买前后、两种主从方向。
- 归档曾记录同类已购显示差异但未确认本次引入；本轮确认本 MR 扩展了跨模式纯续输入，而现有后置识别链路未同步扩展。本次追加运行态复现已确认，见上方对照结果。

### F3 · P2：全量保存并发后可能变成集合并集，突破 10 条上限

- [RenewalMasterRelationService:250](https://git.baijia.com/gaotu/product-server/-/blob/07ba05df6cfabcf0472e1ad27e26ff95cff98467/product-server-domain/src/main/java/com/gaotu/product/service/renewal/RenewalMasterRelationService.java#L250)：事务内先普通查询 `currentSubs`，按请求集合做差分；没有按主计划串行化或版本冲突检测。
- 触发：同一主计划初始关联为空，两个管理员并发各保存 10 个互不重叠的从计划，两者都在对方写入前读到空集。
- 结果：两次请求各自通过上限校验并插入，最终可以留下 20 条。唯一键只能保护同一个主从 pair；`@Transactional` 也不保证整集合替换的互斥。
- 修复：事务内先锁定主计划稳定行，再读取并计算差分，或引入版本条件更新。回归同主计划并发两份不同全集，最终必须等于某一个合法请求全集且不超过上限。

### F4 · P2：清关联缓存发生在提交前，旧关联可回填为有效缓存

- [RenewalMasterRelationService:278](https://git.baijia.com/gaotu/product-server/-/blob/07ba05df6cfabcf0472e1ad27e26ff95cff98467/product-server-domain/src/main/java/com/gaotu/product/service/renewal/RenewalMasterRelationService.java#L278) 在 `@Transactional` 方法结束前删除 Redis；[124](https://git.baijia.com/gaotu/product-server/-/blob/07ba05df6cfabcf0472e1ad27e26ff95cff98467/product-server-domain/src/main/java/com/gaotu/product/service/renewal/RenewalMasterRelationService.java#L124) 的 cache miss 随后普通读库并回填。read-master 窗口只覆盖 B 端关联列表，不覆盖 C 端 `listSubNumbers`。
- 触发时序：保存事务写 DB → 删除缓存 → 并发 C 端请求 miss、读到未提交前的旧关系并回填 → 保存事务提交。
- 结果：即使 Redis 删除成功，C 端仍可持有旧非空关系至默认 1800 秒，旧空关系至默认 60 秒；主从复制延迟也可能造成类似回填。此项是关系缓存一致性窗口，与已接受的 cart 预热缓存 26 小时是两层问题。
- 修复：失效动作移到 afterCommit，并结合 C 端写后读主库/关系版本号防止旧读晚回填；单独 afterCommit 不能彻底覆盖在途旧读竞争。验证提交边界插入读取，及主从延迟下的结果。

## 有损变化及兼容性风险

### R1：库存失败/缺失从阻止推荐变为放行，影响未关联的旧计划

- [小班 isSalable:70](https://git.baijia.com/gaotu/cart/-/blob/d572942668fc5566c7421005efa8f9a7ae22a21c/cart-app/src/main/java/com/gaotu/renewal/small/context/SmallRenewalPostClassInfo.java#L70) 将 `stockQuantity != null && stockQuantity > 0` 改成 `stockQuantity == null || stockQuantity > 0`，没有关联或总开关限制；库存过滤和白名单过滤都调用它。
- [大班库存分组:1514](https://git.baijia.com/gaotu/cart/-/blob/d572942668fc5566c7421005efa8f9a7ae22a21c/cart-app/src/main/java/com/gaotu/renewal/RenewalService.java#L1514) 新增 catch 后继续，查失败的分组不填库存 map，而后续“map 没有此班”即放行。
- 确定的行为差异：旧单计划、总开关 false 时也有此变化；缺库存/库存查询故障时可能推荐实际售罄或无有效库存的班级。这里不声称可绕过订单扣库存或必然超卖。
- 建议按实际商品类型补齐库存，明确缺失时的策略；如果只为跨模式兜底，应限定范围，不能把“无数据”整体等同“可售”。

### R2：order 的放行是全部加购/购物车详情范围，不只关联续班

- [CartSameClazzOrCourseImpl:122](https://git.baijia.com/gaotu/order/-/blob/0cc8ef68b6c29f1d3101f5fa08ea7ec634050bf9/order-app/src/main/java/com/gaotu/app/cart/validate/impl/CartSameClazzOrCourseImpl.java#L122) 只检查总开关与 2↔6004/6003 类型；类注册于通用 ADD_CART、CART_DETAIL，没有计划/关联来源条件。
- 因而默认 true 会让非关联计划、普通手工加购的跨模式同课程/同班号组合也不再命中 SAME_COURSE/SAME_CLAZZ；同模式重复仍拦截，新测试已覆盖“第三件同模式商品”的情况，不重复报已修问题。
- 这是确定的范围变化。是否算缺陷取决于业务是否接受全局去重语义按模式区分；不要把它描述成“只改纯续关联入口”。本轮未替业务作扩大范围决策。

### R3：product-server-client 的 number 字段是 Java API 不兼容变更

- `RenewalMasterListRequest.number` 从 `Long` 改为 `String`，发布到 1.5.13；HTTP 单 ID 被解析兼容不等于 Java setter/getter 兼容。
- 重新编译旧 Java 调用方的 `setNumber(Long)` 会失败；旧编译产物混用新 jar 时可能 `NoSuchMethodError`。本轮 cart/order 源码未发现该请求类的直接使用，未证明已有线上调用方受损。
- 建议保留原字段类型，批量搜索使用已新增 `numberList` 或独立请求字段；如坚持改类型，需要明确检查其他 client 消费方。

## 未误报的部分与验证限制

- 本次的主从单向合并、自关联拒绝、管理员校验、单请求去重/上限、同年级商品去重、主计划扩科年级/学年来源约束均有对应实现；新增本地缓存对象拷贝也已避免直接改写缓存 courseNumbers。
- 没有把旧的 numberList 缺 getter、adminList 命名问题、第三件重复商品漏拦重新报为当前问题。
- 没有把旧 TEST 子集通过当成本次 MR head 的全量回归。已完成上述查询服务级定向复现与独立DB核验；未执行 Maven、数据库并发或浏览器端到端测试。后续补 F1/F2 修复后的完整入口回归与 F3/F4 并发边界用例。
