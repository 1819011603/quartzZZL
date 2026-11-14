# 需求逐点核对（W1-9856ce，2026-11-15）：HEAD 3b49fda6 vs 需求归档

- 对象：cart `feature-renewal-preheat-v2-20261112` @ `3b49fda6`（本地 HEAD 904a5f13 = 3b49fda6 + 空 chore 提交，代码一致；工作区干净）。
- 基线：`af82f18a`（origin/release 顶端）。范围：只读核对，未改任何代码/配置。
- 需求来源：归档 README「已定共识/当前规则与边界」、tasks.md T-22/T-23、owner 二轮口径（om_x100b60b3f8f3b0a4c1e8a4154a701a8 等）、artifacts/20261114-v2-fix/README.md。

## 一、核对表

| # | 需求点/规则 | 实现位置（类:行，均在 cart-app） | 结论 | 说明 |
|---|---|---|---|---|
| O1 | 原 `renewal:preheat:` key 记录主+从完整合并信息 | RenewalV2PureRenewalService#preheat:435-449（无条件 computeMergedPure→写原 key，prefix 不再影响写值内容）；writePreheat:451-469 | 一致 | 运行时证据 preheat-new.txt：5 条 renewal_role=1主+4从；TID cart_gaotu100_com.290.17946706331600008 |
| O2 | `v2:` 前缀仅测试对比用 | cacheKey:471-474（prefix 只切前缀，值内容相同） | 一致 | preheat-v2prefix.txt 同内容 5 条；TID 17946707868170009 |
| O3 | renewalRole 1=主纯续/2=从纯续，老值 null 兼容 | ClazzDetailDTO:95-102（常量+字段）；preheat:439-446 按 mainPreCourseNumbers 标记；老链路读 corePreheatCache（RenewalSinglePlanDetailService:1117-1121）同 ClazzDetailDTO 反序列化，老值缺字段=null | 一致 | 运行时值 renewal_role=1/2（fastjson 全局 snake_case，与既有 product_sku_number 同风格，无格式漂移）；单测 2 用例覆盖双前缀 role 标记 |
| O4 | 新线程池并行化（owner 建议） | BasicConfig#renewalRelatedPlanExecutor:137-152（8-16 线程/SynchronousQueue/CallerRuns，与 C 端详情池隔离）；computeMergedPure:316-342 与 relatedDetails（RenewalV2Service:144-170）按提交顺序 join，结果顺序=串行 | 一致 | 运行时 c-para.json：结果与串行等价、C 端 1.5-1.7s→1.06-1.21s；单测 MoreExecutors.newDirectExecutorService 保确定性 |
| O5 | 计划级 Job 多计划并行评估**不做**（RPC 放大） | RenewalV2JobHandler:62-86 for 循环串行逐计划 | 一致 | 用户级批量仍并行（renewalPreheatAsyncTaskExecutor，RenewalV2Service:229-244，既有行为） |
| O6 | 改动需部署测试验证 | —（流程项） | 一致 | task_brief：test-eco-8 @3b49fda6 6 组全过（TID 17946706444010009 等） |
| R1 | 推荐并集只并纯续（主+从），扩科不变 | RenewalV2ResultMerger#merge:59-104（从计划只取 isRenewal 条目）；主计划 FULL（纯续+扩科+加购）；getRelatedPlanDetail→RELATED_PURE（skipExpandPurchase=true，RenewalSinglePlanDetailService:224-231） | 一致 | isRenewal 判定：recommendType null 或 1（V2PureRenewalService#isPure:212-216） |
| R2 | 扩科年级/学年/学期仍按主计划；同年级同商品去重、跨年级保留、纯续优先 | 小班链路 preClassInfo 只来自本计划 courseNumbers（UserOrderQuerySubBuilder:84-87）；V2 架构下扩科只用主计划自身详情；V2ResultMerger#dedupeByProductPriority:255-288（纯续>扩科>加购、跨年级保留）；reconcilePure:218-227 同 SKU 纯续优先 | 一致 | 基线 B7 扩科收口过滤（ExpandSubjectRecommendService mainOwnPreCourseNumbers）已随 1f5a9118 revert 删除——安全性成立：HEAD 小班 context 不再并入从计划前置课，B7 无存在前提 |
| R3 | Apollo 总开关 `renewal.pure.relation.enabled`（cart 独立配置，默认 true，关闭回单计划） | **cart 侧 0 处引用**（基线 5 处全随 1f5a9118 revert 未上线实现移除） | 口径变化（非代码 bug，需归档同步） | 回退等价能力保留：product 侧关→不下发 relatedRenewMasterNumbers→V2 resolveRelated 空→单计划；cart 侧回退=renewal.recommend.v2/preheat.v2.enabled=false。但 cart Apollo 若存在该 key 已是死配置，README「cart 实例独立配置」口径不再成立 |
| R4 | 原预热 TTL 最长 26h 保持 | 老：RenewalService:124+188；V2：V2PureRenewalService:73+464（同 `preheat.cache.time:26`） | 一致 | |
| R5 | 关联提交版本或有效从计划集合变化会**隔离旧预热**，不能继续推荐失效从计划 | V2 无隔离机制（RenewalRelationCacheService 随 revert 删除）；存量合并值保留至 TTL | **冲突（归档规则 vs V2 实现取舍）** | 见 G1 |
| R6 | 主从各自独立预热、推荐再合并（20261110 口径） | V2=各计划独立计算（自身订单/售卖/库存）后合并输出；value 结构由「主∪从并集单引擎」改为「逐计划条目+role 标记」 | 一致（架构升位，语义保持） | 但新老 Job 并存覆写原 key，见 G2 |
| R7 | 从计划仅【待开始/进行中】有效（product 侧状态过滤） | V2PureRenewalService#resolveActiveSubs:101-133 只保留 product 返回的 active 子集 | 一致 | |
| F1 | 老链路消费合并值不回归 NPE（T-22 P0） | RecommendContext:135-149/151-166/168-177/179-192 四方法判空 + getCourseDTOByClazzNumber:115-121；processClazzSet:1547-1550、processClazz:1704-1706 courseDTO/clazzDTO null 跳过 | 一致 | 运行时回退态读合并值 code=0（TID 17946706444010009，对照 c98c4158 同场景 code=1 NPE） |
| F2 | B/BC 入口售卖过滤（fromBCart 透传，T-22 修复） | RenewalV2Service.relatedDetails:154、getRenewalDetailForB:130 透传；过滤在 coreHandle:1282-1286（!fromBCart→SALE_STATUS）与联报 2955-2960 | 一致 | 运行时 b2-0/b2-1.json：fromC=0→2 条、fromC=1→1 条（saleStatus=50 过滤）保持 |
| F3 | /preheatByRenewal 按开关路由（T-22 修复） | RenewalFeignService:82-88（isPreheatV2Enabled→V2/老 Job）；/preheat HTTP 同口径（RenewalController:145-147、FeignService:71-75） | 一致 | |
| F4 | 空结果删 key（防过期残留） | writePreheat:451-460（空→delete 目标 key） | 一致 | 单测 ×2（双前缀） |
| F5 | V2 实时有关联跳预热读、无关联可读缓存 | RenewalV2Service#getRenewalDetailForC:96-102（related 空→getMainPlanDetail 读缓存；非空→SkipPreheat） | 一致 | 无关联读路径与 R5 窗口叠加场景见 G1 |
| F6 | 单从计划异常隔离不拖垮主计划 | relatedDetails:151-159（catch→null）；joinPlanPure:344-357（预热侧异常重抛，不写半量值） | 一致 | |
| 附 | 小班 type=2 分派（主/从均按小班引擎） | RenewalSinglePlanDetailService#getSinglePlanDetailInternal:280+（type=2→small 引擎）；computeSinglePlanPureMap:2842-2843 | 一致 | 小班用户级 V2 预热写原 key 无 C 端消费方（既有已知口径，写而无害） |

## 二、冲突/缺口清单

**G1【冲突·规则未同步】R5 关联变化隔离旧预热 vs V2 无隔离机制**
- 归档 README「当前规则与边界」：「关联提交版本或有效从计划集合变化会隔离旧预热，不能继续推荐失效从计划」——该机制（RenewalRelationCacheService 版本键隔离）属被 revert 的未上线实现，V2 未重建。
- V2 现状：关联清空/失效后，存量合并值留至 TTL（≤26h）；V2 实时（resolveRelated 实时解析）不受影响；受影响读方=回退态老链路 + V2 无关联分支读缓存（ForC:97 getMainPlanDetail）——可继续展示失效从计划条目 ≤TTL。
- fix record 已如实记录为已知取舍（「靠变更后重跑预热兜底」）。判定：按归档规则=冲突，按 V2 设计=已声明的取舍。**需 owner 确认口径并同步更新归档规则**（或补运维动作：关联变更后触发该计划重跑预热）。

**G2【缺口·运维顺序+文档自相矛盾】新老 Job 并存覆写原 key**
- RenewalJobHandler:39-71 无任何 v2 开关判断；V2 开启期间老 Job 调度仍会以**单计划值**覆写原 key 的主+从合并值，破坏 O1「原key=完整信息」口径。
- 正确性无损（所有读方消费单计划值均安全，老值本就是单计划语义）；但 O1 口径只在 V2 Job 是唯一写方时成立。**切终态时需停老 RenewalJobHandler 调度**（分支审查 P1 已指出，二轮未处理，属运维顺序问题）。
- RenewalV2JobHandler:25 javadoc「两者写值语义一致（老 Job 写单计划纯续、V2 写主+从合并）」自相矛盾，建议改写避免误导。

**G3【口径变化·需归档同步】cart 侧 `renewal.pure.relation.enabled` 引用清零**
- 基线 5 处（CrossMode/RelationCache/DataService/Service/PostClassInfoBuild）全随 1f5a9118 revert 移除；回退能力转由「product 不下发 + cart v2 双开关」承接（等价可用）。
- README 共识「product/cart/order 各实例独立配置」对 cart 不再成立；TEST/prod cart Apollo 若配过该 key 即死配置。需在归档+飞书文档同步说明，避免误以为 cart 侧可独立回退。

**G4【未覆盖·非冲突】两项验证缺口（task_brief 已列，本轮复核确认仍缺）**
- 计划级批量预热全量用户：样本计划 is_test_data=1 被 Job 过滤（RenewalV2JobHandler:77-80），未跑通全量用户写入回读；单用户级同链路已运行时验证。
- 跨模式已购并集（原 RenewalCrossModeOrderService 场景）：V2「各计划独立查自身订单再合并」设计上天然覆盖（从计划条目 signUp 由从计划自身计算），**推断等价、无跨模式已购用户专项运行时验证**；11-12 矩阵与 11-14 六组均未含该样本。

**其余：无冲突。** O1-O6、R1/R2/R4/R6/R7、F1-F6 全部一致。

## 三、结论

二轮改动（合并值写原 key+renewalRole、并行线程池、v2: 仅测试）与 owner 口径及既有规则（老链路消费兼容、BC 售卖过滤、开关路由、TTL26h、纯续优先/去重、扩科按主计划）**全部一致**；4 项发现中 G1/G3 为「归档规则未随架构演进同步」需 owner 知悉并更新文档，G2 为切终态运维顺序缺口，G4 为既有验证缺口。
