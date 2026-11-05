# cart 需求核对与本地回归（完成）

基线：`feature-xuban-pure-relation-20261102` / `7bb1fb923e7ff0bda00f3ea2d7053ea5c434447a`，工作区初始干净；base 为归档明确的 origin/release。本轮仅本地验证，未部署、未写业务数据、未修改共享归档。

## 核心结论
- 确定条件性缺陷：`renewal.query.cache.enabled=true` 且 `renewal.query.local.cache.enabled=true` 时，`RenewalDataService#listRenewalMasterByRenewalNumber` 返回 Guava 缓存对象本身；`mergeRelatedPreCourseNumbers` 替换其 courseNumbers。次请求主计划自身前置课已包含从计划，B7 年级收口失效，关联开关关闭也仍能拿到污染并集。证据：`RenewalDataService.java:290-298,339`、`cache/handler/AbstractGuava#getObjectByNumber` 原对象返回。本轮已用单测复现并完成最小修复，最终94用例回归通过；归档曾记录 TEST/PROD 该缓存关闭，本轮未在线核对配置，不能声称生产已触发。
- 已修复：扩科的学年/学期来源原先遍历并集，主课信息缺失或从课排序在前时会取从计划年份；新增2例修前失败、修后通过。
- B5 采用已确认边界：从计划只贡献前置课，白名单/联报/组合规则按主计划。
- B8 采用已确认边界：不修，已有预热最多 26h 旧推荐窗口。

## 测试状态
首次测试因机器人重启中断，日志 cart-baseline-tests.log 停在 client 编译，无有效统计；重启后重跑已完成66/0/0/0，cart-baseline-tests-rerun.log。不得将旧 target 报告当成本轮验证。

## 需求 ↔ 实现 ↔ 当前证据

| 要求 | cart 实现 | 证据与边界 |
|---|---|---|
| B5 从计划只并前置课，推荐规则取主计划 | RenewalDataService 合并 courseNumbers；不替换 renewalRecommendMap/productNumberList/节点时间 | 全分支 diff 对照；未按从计划独立规则新增功能 |
| B6 大班主 + 小班从 | RenewalCrossModeOrderService item→info 保留订单项号作 orderNumber；coreHandle 按 clazz.productType 查询库存 | 基线 StockInfoQuerySubBuilderSkuTypeTest、SmallRenewalPostClassInfoSalableTest、RenewalServiceNewLogicTest 通过；旁路订单服务的完整跨模式链路尚未本轮真机验证 |
| B6 小班主 + 大班从 | UserOrderQuerySubBuilder 补 info→item；StockInfoQuerySubBuilder 查班级真实 skuType；输出真实类型 | 同上 + SmallRenewalCoreServiceIntegrationTest、UserOrderQuerySubBuilderTest 基线通过 |
| B7 扩科年级不扩大 | 大班 expansionCourseDTOMap 只保留主前置课映射；小班 collectStudentPostGrades 按 mainOwnPreCourseNumbers 过滤 | 原有小班年级 3 用例通过；新发现学年学期维度遗漏（新增两用例红灯）以及本地缓存污染 |
| 同商品同年级去重，跨年级保留 | RenewalService 三处 VO 组装调用 dedupClazzByGradeByProduct | 原有测试正常/跨年级/null 输入通过；纯续优先于扩科/加购由既有三路顺序决定 |
| 5 参入口保留纯续和账号校验 | getRenewalDetail(5参) 先合并，再走新小班/旧兼容/大班分流；无新增扩科/加购 | 源码核对；AppointUserCheckTest 4例本轮全部通过 |
| 7 参入口纯续并集、扩科加购保留 | getRenewalDetail(7参) 合并前记录主集合；纯续/扩科/加购后合并 | 源码 + 推荐组件测试；不宣称整个入口端到端已验 |
| 大小班预热仍合并纯续 | 大班 preheat 合并后 coreHandle；小班 preheatInternal 先合并再 recommendAll；大班批量枚举主前置学员、小班批量枚举合并前置学员后调用单用户预热 | SmallRenewalPreheatServiceTest 基线通过；大/小班批量枚举范围保持各自既有行为 |
| 批量取从计划及缓存 | 未命中多条走 listByNumbers；单条或批量异常回退；正缓存300s/空60s | 原有缓存5用例通过；批量异常回单查、单查异常不缓存已补测通过 |
| B8 接受最长26h | 预热 key/TTL/失效路径保持不改 | 已确认业务决定；本轮不会改变过期窗口 |

## 本地 P0 case 建议（供主 Worker 整合文档，未执行的联测步骤）

统一前置：选择独立 TEST 泳道，记录 cart/product/order 镜像 SHA、Apollo 实际开关；准备主计划 M 和从计划 S，两者都处有效期；主前置 A→后置 a，从前置 B→后置 b；学员 U 有有效 paid/部分退款订单；主规则白名单正常，候选库存>0 且售卖状态40。测试时禁用预热读取或选未预热 U，避免 B8 旧数据影响；恢复项逐条记录。

| P0 | 操作步骤 | 断言 |
|---|---|---|
| C01 双向并集 | ① M=大班、S=小班且关联；② 请求7参购物车；③ 交换主从模式再次请求；④ 分别检查推荐类型和SKU类型 | 每方向都有两模式纯续；大班type2、小班type6004；不出现库存商品类型错误 |
| C02 主扩科不扩大 | ① 主后置年级7，从后置年级9；② 主配置年级7和9的不同商品扩科；③ 开/关关联对照；④ 大小班主各跑一次 | 年级9仍可有从计划纯续，但不能凭从计划新增年级9扩科；主原年级7扩科保留 |
| C03 排除条件不串从计划 | ① 主前置2026/学期1，从前置2027/学期2；② 主扩科配置排除不同模式在读；③ 调整订单排序使从课在前；④ 分别测试主课学年学期完整与缺失 | 在读排除请求只使用主课2026/1；主信息缺失仍按原降级，不取从课2027/2 |
| C04 同商品同年级去重 | ① A与B都映射同一后置商品P且同年级；② 扩科/加购也配置P；③ 请求；④ 给P另一个配置年级再请求 | 同年级P只有1条，纯续优先；不同配置年级各保留，不跨年级误删 |
| C05 入口保留 | ① 对同U/M调用5参、7参；② 小班开关新引擎路径；③ 传错appointUserId；④ 大小班分别单用户预热后读取 | 5参仍纯续且账号不匹配状态1/掩码手机；7参保留扩科/加购；预热纯续包含主+从；旧兼容路径单独记录 |
| C06 缓存隔离/开关回退 | ① 开启计划本地缓存；② 同M连续请求两次；③ 关闭关联总开关再请求未预热U；④ 恢复配置 | 第二次主扩科范围不扩大；关闭后只主前置纯续；缓存内主前置始终只有A；此用例不要求清除B8预热 |
| C07 无关联/异常回退 | ① 无从计划；② 总开关关；③ 从计划API失败/批量失败回单查；④ Redis不可用 | 无关联/关闭不补旁路，原主结果不变；异常只按已有降级处理，不能把失败写成永久缓存 |
| C08 B8接受边界 | ① 用关联M→S预热U；② 修改/解绑S；③ 在26h内访问；④ 过期或选新U比较 | 缓存用户可能旧推荐，明确作为已接受边界，不记为本轮未修bug |

执行后恢复：关联表、主扩科配置、临时课关系、测试订单/购物车与Apollo；保留请求/响应、traceId、服务SHA。上述涉及测试数据写入/部署须由主 Worker 后续按授权执行，本轮没有执行。

## 修复前已确认失败证据
- `cart-b7-red.log`：5 tests / 2 failures / 0 errors / 0 skipped；两例分别是主学年2026被从学年2027替代、主学年缺失应null却得到2027。
- `cart-cache-red-rerun.log`：6 tests / 1 failure / 0 errors / 0 skipped；缓存原始课程应[1]实为[1,2]。
- `cart-cache-red.log` 是错误的重叠 Maven 构建产生的编译缺类，不作为回归结果；已等另一个构建结束后串行重跑得到上面的真实断言失败。首次重启日志同样不计测试。

## 本轮修复范围
1. `RenewalDataService` 仅本地缓存返回时复制 DTO 和 courseNumbers，防止请求并集污染共享主计划；Redis/直查路径保持既有行为。
2. `RenewalService` 大班在线与预热的扩科 currentCourse 只使用合并前主课；预热扩科年级也与在线一致取主课。
3. `ExpandSubjectRecommendService` 小班排除在读的学年/学期来源遵循 mainOwnPreCourseNumbers；保留未设置该字段的旧调用行为。
4. `SmallRenewalPreheatService` 单用户预热在合并前记录主课、传给扩科上下文；纯续仍使用并集，预热结果key/TTL没有改。
5. 补测试：缓存污染与回滚、批量失败回退、单查失败不缓存、总开关关闭、自关联/null/重复关系与课程去重、小班学年学期两边界、大班来源、预热主集合。

## 验证命令与环境

目录：`/Users/gaotu/IdeaProjects/JavaProject/cart`。工具：mvn8=Maven 3.9.9/JDK 1.8.0_202。比较基准 `origin/release=3e1e366ca643a2c823abbfa9186589a3d4f65972`。初始本地与远端需求分支同为7bb1fb92。

```sh
# 基线（已完成66/0/0/0，8类）
mvn8 -pl cart-app -am -Dtest=RenewalServiceNewLogicTest,StockInfoQuerySubBuilderSkuTypeTest,SmallRenewalPostClassInfoSalableTest,ExpandSubjectRecommendServiceMainOwnPreCourseTest,RenewalDataServicePureRelationMergeCacheTest,UserOrderQuerySubBuilderTest,SmallRenewalCoreServiceIntegrationTest,SmallRenewalPreheatServiceTest -Dsurefire.failIfNoSpecifiedTests=false test
# 缓存缺陷复现（修前6/1/0/0）
mvn8 -pl cart-app -am -Dtest=RenewalDataServicePureRelationMergeCacheTest -Dsurefire.failIfNoSpecifiedTests=false test
# B7缺陷复现（修前5/2/0/0）
mvn8 -pl cart-app -am -Dtest=ExpandSubjectRecommendServiceMainOwnPreCourseTest -Dsurefire.failIfNoSpecifiedTests=false test
# 最终回归（94/0/0/0，日志cart-final-tests.log）
mvn8 -pl cart-app -am -Dtest=RenewalServiceNewLogicTest,StockInfoQuerySubBuilderSkuTypeTest,SmallRenewalPostClassInfoSalableTest,ExpandSubjectRecommendServiceMainOwnPreCourseTest,RenewalDataServicePureRelationMergeCacheTest,UserOrderQuerySubBuilderTest,SmallRenewalCoreServiceIntegrationTest,SmallRenewalPreheatServiceTest,RenewalServiceAppointUserCheckTest,ExpandSubjectRecommendServiceTest,RecommendMergeServiceTest -Dsurefire.failIfNoSpecifiedTests=false test
```

测试统计顺序=run/failures/errors/skipped；使用本轮日志/Surefire XML，不混入历史 target 文件。复用本仓JUnit4/TestNG既有测试，未新增依赖、未改其他仓。

## 未覆盖 / 明确不宣称
- 本轮未做新鲜TEST接口调用、端到端购物车/下单、浏览器页面、生产验证或并发压测；不能将本地Mock依赖测试等同业务验收。
- B6既有真机证据仅历史参考：归档记录反向修后 `cart_gaotu100_com.289.17937844100170008`、正向独立复跑 `cart_gaotu100_com.293.17937847867120012`；这些不是当前新代码的在线证据。
- 未跑全量历史测试。归档记录cart-app历史15失败属于BCartQuerySubBuilderTest 6 + ExpandSubjectConfigSubBuilderTest 9，本轮不据此判本分支回归，也不声称已经修掉。
- B5主规则与B8已接受延迟均保持。批量预热大班/小班枚举范围有既有差异，未扩展需求。
- 当前测试没有覆盖7参完整门面与大班预热完整RPC链，仅覆盖相关纯逻辑、缓存、上下文及原有小班集成测试；P0 C01/C02/C05仍建议后续TEST联测。
- AICR push前只读查询提示「项目未接入或分支暂无评审」，见cart-aicr-before.txt；push后再次读，未判定/关闭任何finding。

## 最终交付与复核

- 2026-11-05 本地回归完成：**11类 / 94 tests / 0 failures / 0 errors / 0 skipped，BUILD SUCCESS**。其中本轮新增10例，原有84例；基线8类66例，新增范围同时纳入另外3类18例。修前红灯为缓存1例、学年学期2例。
- 提交并已推送：`a34016fdf206d0163b1dd473c67ac10674ecb4b5`，分支 `feature-xuban-pure-relation-20261102`；本地 HEAD == `git ls-remote origin refs/heads/feature-xuban-pure-relation-20261102`，upstream 同名 origin 分支，工作区干净。
- 没有部署、没有新增MR、没有改业务数据或Apollo，没有改共享需求归档或其他仓库。
- 修改：4个生产文件、4个原有测试文件，200 additions / 10 deletions；`git diff --check` 通过。请求副本仅浅复制DTO加复制课程列表，保护本需求赋值操作，不引入新框架/新依赖。
- 本轮测试日志 `cart-final-tests.log`；不可变XML副本 `cart-final-TestSuite.xml`；各类统计 `cart-test-counts.json`。没有用历史全量失败掩盖当前失败。

| 本轮执行的测试类 | 用例数 |
|---|---:|
| SmallRenewalPostClassInfoSalableTest | 6 |
| ExpandSubjectRecommendServiceTest | 7 |
| SmallRenewalPreheatServiceTest | 10 |
| SmallRenewalCoreServiceIntegrationTest | 25 |
| ExpandSubjectRecommendServiceMainOwnPreCourseTest | 5 |
| RecommendMergeServiceTest | 7 |
| UserOrderQuerySubBuilderTest | 9 |
| StockInfoQuerySubBuilderSkuTypeTest | 3 |
| RenewalServiceAppointUserCheckTest | 4 |
| RenewalDataServicePureRelationMergeCacheTest | 10 |
| RenewalServiceNewLogicTest | 8 |

AICR：push前 `cart-aicr-before.txt` 提示跳过（未接入/暂无评审）；push后结果见 `cart-aicr-after.txt`。没有任务不等于AICR通过，若之后异步出现任务须按当前SHA继续看。没有等待中的构建/部署/业务操作。

主 Worker 后续可直接以本提交整合报告和P0用例；本地范围已完成，无需范围决策。需明确告知 owner：当前新版尚未部署/接口验收；B8预热旧值仍按约定接受，缓存隔离修复不代表预热立即失效。
