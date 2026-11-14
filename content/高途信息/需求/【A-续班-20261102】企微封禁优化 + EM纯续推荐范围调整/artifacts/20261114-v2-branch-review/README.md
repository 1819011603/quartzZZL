# 2026-11-14 V2 分支完整检查与测试验证（W1）

> **⚠️ 2026-11-14 晚更正**：本文「二、问题清单」中的 P0「序列化格式不兼容」结论**已被运行时实证推翻**——
> `userRenewalRedis`/老 `redisTemplate` 经 Spring 泛型匹配实际都注入 **StringRedisTemplate**（arthas vmtool 实证，
> 两个类字段均为 `StringRedisTemplate$$EnhancerBySpringCGLIB`），新旧写读同为裸 JSON，格式一致。
> **真实 P0（同日端到端复现）**：prefix=false 时 V2 把主+从合并纯续写进老 `renewal:preheat:` key，老链路读者
> （recommend.v2 回退 / BC 入口）读到从计划组合 SKU 等非班级条目时 `RecommendContext:127` 解析班级 **NPE**
> （TID `cart_gaotu100_com.293.17946524918130952`，code=1 网络异常；A/B/A 验证：老值 code=0 → V2 合并值崩溃 → 老值恢复 code=0）。
> 下文「序列化探针」实验本身有效（GenericJackson 确实读不了裸 JSON），但该序列化器不在这条链路上——结论不适用。
> 修复见 `artifacts/20261114-v2-fix/`（老 key 只写主计划纯续 + 判空加固）。

对象：cart `feature-renewal-preheat-v2-20261112` @ `c98c4158`（本地=远端，工作区干净）。
基线：`af82f18a`（= origin/release 顶端 = origin/master 合并点；线上生产镜像 release-4b40ee27 内容 = clazzset-dedup@e315a655，由 revert 提交 `1f5a9118` 对齐）。
范围：只读检查 + 本地构建测试，未修改任何业务代码。

## 一、diff 概览（20 提交，56 文件 +6323/−7573）

1. **revert 对齐生产**（`1f5a9118`）：把 release 顶端合入的旧版主从合并实现（RenewalCrossModeOrderService/RenewalRelatedResultMerger/RenewalRelationCacheService 等，含 12 个测试类）整体回滚到线上运行的 clazzset-dedup 基线。回滚提交内附回读校验（tree 与生产镜像 4b40ee27 一致）。
2. **V2 重做**（19 提交）：
   - 新增 `RenewalV2Service`（C/B 详情编排 + 单用户/计划级预热）、`RenewalV2PureRenewalService`（关联解析→单计划纯续→合并去重→写缓存共享主链路）、`RenewalV2ResultMerger`（合并 + 实时纯续校正/商品级三层去重）、`RenewalV2JobHandler`（新 xjob，已注册 test）。
   - `RenewalService` 983 行实现抽取为 `RenewalSinglePlanDetailService`（3178 行），入口按 DetailMode（FULL/SKIP_PREHEAT/RELATED_PURE/LEGACY_PURE）收敛。
   - 三个开关：`renewal.recommend.v2.enabled`（实时走 V2）、`renewal.preheat.v2.enabled`（预热走 V2）、`renewal.preheat.v2.prefix.enabled`（写 `renewal:preheat:v2:` 前缀仅写不读，人工对比用；关闭=写老 key）。
   - product-server-client 1.5.11→1.5.13（`relatedRenewMasterNumbers` 下发）。
   - 设计动机：规避旧实现审查发现的 F1~F4（从计划强购被主计划覆盖/allSignUp 错误/换课失效漏入口/扩科去重范围随缓存命中变化）——V2 实时有关联时不再消费合并缓存。

## 二、问题清单（证据分档）

### P0【已验证】V2 预热写值格式与老读链路不兼容——prefix=false 终态必炸

- 事实链：
  1. `RedisConfig#redisTemplate`（@Primary）value 序列化器 = GenericJackson2JsonRedisSerializer（RedisConfig.java:71-77）；老写 `RenewalService.preheat:187` 与老读 `RenewalSinglePlanDetailService.corePreheatCache:1110`（`userRenewalRedis`，同类型注入解析到同一 @Primary bean）自洽：Redis 值 = **带引号的 Jackson JSON 字符串**。
  2. V2 写 `RenewalV2PureRenewalService.writePreheat:409` 用 **StringRedisTemplate 裸 JSON**（f70ebd93 引入，提交说明「保持与老链路 value 格式一致」与 RedisConfig 实际配置不符）。
  3. **JVM 实测**（项目自身依赖 spring-data-redis 1.8.11 + jackson 2.8.4，探针类见本目录 `RedisSerializerProbe.java`，输出 `probe-output.txt`）：裸 JSON 经 GenericJackson 反序列化直接抛 `SerializationException: missing property '@class'`。
  4. 读路径活跃：`getLargeClassRenewalDetail:390` 在 `preheat.cache.enabled && !fromBCart && !skipPreheatRead` 时读老 key；**PROD 与 TEST Apollo 均为 true**。
- 触发条件：`renewal.preheat.v2.enabled=true` 且 `prefix=false`（设计终态，见 RenewalV2JobHandler javadoc）→ V2 写老 key → 后续任一老读（**无关联计划的 C 端实时**（related-empty 走 getMainPlanDetail 读缓存）或 recommend.v2=false 回退态）抛异常 → C 端「网络异常」（与 2026-11-12 线上脏缓存事故同症状，事故卡见 `../20261112-renewal-cache-clean/问题卡.md`）。
- 覆盖缺口佐证：V2 单测 mock Redis；11-12 泳道开关矩阵（`../20261112-cart-rerun/apollo-switch-matrix-20261112.json`）测过 prefix=off 覆写老 key（LEN 104→1045）但**只验 LEN/TTL 后即恢复原值，未做老链路读**。
- 当前实际影响：无（PROD 三个 V2 开关均未配置默认 false；TEST v2=false/prefix=true）。**prefix 切 false 前必须修复**。
- 修复方向（未获授权，仅建议）：V2 写改回同一 `redisTemplate` bean（f70bd93 之前正是如此），或读侧换 StringRedisTemplate 并清理存量值。

### P1【推断未验证】`/preheatByRenewal` 未按开关路由 V2

`RenewalFeignService:73-83` 计划级预热 HTTP 端点固定调老 `RenewalJobHandler`。V2 终态下被外部调用会用老格式单计划值覆写 V2 合并值（双写不一致）。仓库内无调用方，实际影响取决于外部调用者（如 product 侧联动）。同理：**新老两个 Job 并存调度也会交替覆写同一 key**，切终态前需停老 `RenewalJobHandler` 调度（运维顺序问题）。AICR #40865 同指此点。

### P2【推断未验证】V2 实时有关联时每次全量重算 + 串行

`relatedDetails` 串行逐从计划完整 coreHandle（RPC 放大 ~N 倍，N≤10），且主计划强制跳过预热读（换正确性的设计取舍）；从计划 forceBuy 双取（详情内 + applyRelatedForceBuy 再查一次，每从计划多一次 RPC）。11-12 矩阵未测时延。AICR #40867 同指（被删的并行线程池属被 revert 的未上线实现）。

### P2【推断未验证】V2 B/BC 入口硬编码 fromBCart=true 跳过售卖过滤

`getRenewalDetailForB:128/133` 对主/从均硬编码 true。B（fromC=0）行为不变；**BC（fromC=1，老链路 fromBCart=false 会按售卖状态过滤）有关联时跳过过滤，可能透出不可售商品**。AICR #40868 同指。11-12 矩阵验证的是三链路纯续集合一致，未覆盖售卖过滤差异。

### P3【推断未验证】其余低风险

- `writePreheat` 空结果不写不删旧 key：资格变化后旧值留至 TTL 26h；V2 主路径不读缓存无影响，回退态可能读到（AICR #40866）。
- 前置课冲突校验缓存 1h 不随关联配置变化失效：新冲突最长 1h 检不出（冲突/状态查询异常不缓存的设计正确）。
- 小班用户级 V2 预热写入无消费方（`small.renewal.enabled=true` 时小班 C 端不读预热 key）：写而无害；若该开关未来翻 false 则并入 P0 场景。

### AICR（task#1612, head ee567467, FAIL 15 项）甄别结论

- #40857 实参顺序（blocking）→ **已由分支提交 ca6f2648 修复，当前代码已核正确**。
- #40869 年级重排 → **已由 c98c4158 修复**（reconcilePure gradeAdded 后排序，现有代码已含）。
- #40860/61/62/63/64/70（NPE 防护/缓存对象污染/@mergedRenewal@ 存量/用户去重）→ 经与生产基线 `1f5a9118` 逐项比对：**均为生产行为本身**（AICR 对比基线是 release 顶端，含未上线的修复），非本分支引入；其中 NPE 防护属「被 revert 掉的未上线修复」，可作为可选加固由 owner 决定是否重新带入。

## 三、测试验证（本地，HEAD c98c4158）

| 项 | 结果 | 证据 |
|---|---|---|
| 全模块构建 `mvn8 clean install -Dmaven.test.skip=true` | 通过 | 本轮执行，EXIT=0 |
| cart-app `mvn8 test` | 546 项：531 过 / 15 失败 / 0 错误 | `local-test-summary`（见下） |
| 15 失败定性 | **基线既有**：ExpandSubjectConfigSubBuilderTest(9)+BCartQuerySubBuilderTest(6)，均「Could not find field 'enabled'」反射失败；两处类与测试在本分支 0 提交改动；与 README 2026-11-11 记录一致 | `git log 1f5a9118..HEAD -- '*ExpandSubjectConfigSubBuilder*'` 空 |
| V2 新测试 | RenewalV2PureRenewalServiceTest 13/13、RenewalV2ResultMergerTest 13/13、RenewalV2ServiceTest 9/9 全过 | surefire TEST-TestSuite.xml |
| 序列化器探针 | 裸 JSON 经 GenericJackson 反序列化抛 SerializationException | `probe-output.txt` |
| 老路径抽取保真 | 基线 59 方法：48 逐字一致；6 改动均为 delegation/新 flag 门控（已逐个人审 getLargeClassRenewalDetail/coreHandle/preheat/productSelect/getRenewalDetail/getAfterCourseMap）；2「缺失」为基线死代码 | `method_diff.py` 输出 |

**沿用既有运行时验证**（11-12，test-eco-8，镜像 68e825e1，非 HEAD）：7 组主从样本预热 vs 实时纯续等价、三开关 ON/OFF 矩阵、计划级预热 v2 key（TTL 26h）。其后 3 个实质提交（59be925b 模式收敛纯重构/ca6f2648 实参修正/c98c4158 年级重排）经静态核对为低风险等价改动，未重做运行时验证（HEAD 与 68e825e1 的运行时差异未覆盖）。

## 四、需 owner 决策

1. P0 格式不兼容的修复方案（改回 redisTemplate / 读侧换 StringRedis+清存量），修复前不得将 prefix 切 false。
2. `/preheatByRenewal` 是否按开关路由 V2（取决于外部调用方是否存在）。
3. 切终态运维顺序：停老 Job 调度 → 修 P0 → prefix 切 false。
4. 是否重新带入被 revert 的 NPE 防护等未上线修复（AICR #40860-62/63/64）。
