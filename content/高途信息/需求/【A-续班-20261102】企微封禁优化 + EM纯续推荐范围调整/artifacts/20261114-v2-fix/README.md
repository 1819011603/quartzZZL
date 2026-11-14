# 2026-11-14 V2 修复（owner 授权）：为什么改、改了哪

- 分支：cart `feature-renewal-preheat-v2-20261112`，commit `47d445da`（`fix(renewal): V2预热老key只写主计划纯续，老链路消费合并值会NPE`）。
- 前置审查：[20261114-v2-branch-review](../20261114-v2-branch-review/README.md)（注意其中「格式不兼容」结论已被实证推翻，头部有更正说明）。

## 根因（运行时复现）

- 复现环境：test-eco-8 @ `c98c4158`（修复前 HEAD），TEST/default Apollo 临时 `renewal.preheat.v2.enabled=true` + `prefix=false`（模拟终态，用后恢复）。
- 步骤：单用户预热（V2 写老 key 合并值 5 条）→ C 端老链路查询（recommend.v2=false）。
- 结果：`{"status":1,"code":1,"msg":"网络异常"}`；TID `cart_gaotu100_com.293.17946524918130952`；
  堆栈 `NullPointerException at RecommendContext.lambda$listCourseDTOByClazzNumbers$2(RecommendContext.java:127)`。
- 机理：合并值含从计划条目（如 productType=51 组合，productSkuNumber 是 SKU 号非班级号），老链路 `corePreheatCache` 命中后按 productSkuNumber 查班级 → 课程中心查不到 → `afterClazzDTOMap.get(...)` 返回 null 直接解引用 NPE。
- A/B/A 佐证：同 key 老值(单计划) code=0 → V2 合并值 code=1 → 恢复老值 code=0。
- 附带更正：上轮「StringRedisTemplate 与老 GenericJackson 格式不兼容」不成立——arthas 实证老写/老读两个 RedisTemplate 字段实际都注入 StringRedisTemplate，格式一致。

## 改动清单（9 文件，+292/−77）

| # | 位置 | 改动 | 为什么 |
|---|---|---|---|
| 1 | `RenewalV2PureRenewalService#preheat/writePreheat` | prefix=false：老 key 只写**主计划纯续**（不写合并值）、不解析关联；prefix=true：v2: key 写合并值（diff 用）；空结果**删**目标 key | 终态下合并值没有任何读方（V2 实时有关联时跳预热读；无关联计划读到合并值=老链路语义破坏+NPE）。回退态/BC 入口读到主计划纯续=与老预热完全同语义，安全。空值删除防过期推荐残留 26h |
| 2 | `RenewalV2Service#preheat/preheatByRenewalNumber` | prefix=false 时跳过 resolveRelated（含冲突校验） | 只写主计划就无需关联解析/校验，计划级批量预热省每计划一次状态 RPC |
| 3 | `RenewalV2Service#getRenewalDetailForB` + `RenewalSinglePlanDetailService` 新增 `getPurePlanDetailSkipPreheat` | 主/从均按调用方 `fromBCart` 透传（仍强制跳预热读） | 原硬编码 true：BC 入口（fromC=1）本应按售卖状态过滤被跳过，可能透出不可售商品；老 B 端行为还原 |
| 4 | `RenewalV2Service#relatedDetails` 删 `applyRelatedForceBuy` | 从计划 forceBuy 不再二次查询覆盖 | RELATED_PURE 模式内部已按从计划自身配置标记 recommendType/forceBuy，原实现每从计划每次请求多一次 getRenewalMasterWithProcess RPC 且结果相同 |
| 5 | `RenewalFeignService#/preheatByRenewal` | 按 `isPreheatV2Enabled()` 路由 RenewalV2JobHandler/老 Job | 原固定老 Job：V2 开启时外部触发计划级预热会绕过 V2，语义不一致 |
| 6 | `RecommendContext`（4 个查询方法）+ `RenewalSinglePlanDetailService.processClazz/processClazzSet`（4 处） | 判空加固：解析不到的班级/课程条目跳过，不 NPE、不返回 null 元素 | 本次 NPE 复现点；该风险生产基线同样存在（被 revert 的未上线实现曾修过、随 revert 丢失），一并加固 |

配套测试：`RenewalV2PureRenewalServiceTest`（重写预热组装 5 用例：主计划纯续写入/合并写 v2:/空删 key×2）、`RenewalV2ServiceTest`（B 路径 fromBCart 透传+不再二次查 forceBuy、预热 prefix 分流×2）、新增 `RecommendContextNullGuardTest`（5 用例）。

## 不改的项（设计取舍，已核对需求规则）

- **V2 实时有关联时串行全量重算主+N从**：换新鲜度/正确性（复用 11-12 已验证的「三链路一致」口径）；从计划上限 10，量级可控；本轮不并行化。
- **小班用户级 V2 预热写入无消费方**（small.renewal.enabled=true 时小班 C 端不读预热 key）：写而无害，留作回退数据；不改。
- **老/新 Job 并存**：修复后两者写老 key 语义相同（主计划纯续、同格式），并存无正确性冲突，仅重复计算；切终态时停老 Job 是可选优化而非必须。
- **冲突校验缓存 1h 不随关联变化失效**：冲突/异常不缓存，静默窗口 ≤1h，可接受。

## 验证（2026-11-14，test-eco-8 @ `47d445da`，pod cart-gaotu100-com-78849dd749-s7vqp）

**改前复现**（@c98c4158，临时 preheat.v2=true+prefix=false）：单用户预热写老 key 合并值 5 条 → C 老链路
`code=1 网络异常`，NPE `RecommendContext:127`（TID `cart_gaotu100_com.293.17946524918130952`）；同 key 恢复老值后 code=0（A/B/A）。

| # | 验证项 | 结果 | 证据 |
|---|---|---|---|
| 1 | prefix=false 预热写老 key | `renewal-v2 preheat done, key=renewal:preheat:589037361072007168:7704848531, entries=1`（主计划纯续，改前 5 条合并） | pod app.log，TID `cart_gaotu100_com.294.17946536998440006` |
| 2 | C 老链路读 V2 写的 key | `code=0` + 日志 `renewal-data-from-preheat` 命中（改前同场景 code=1+NPE） | TID `cart_gaotu100_com.296.17946537111390006` |
| 3 | prefix=true diff 模式 | `key=renewal:preheat:v2:..., entries=5`（合并值写 v2 前缀） | TID `cart_gaotu100_com.298.17946537902400007` |
| 4 | V2 实时（recommend.v2=true）C 端 | 6 条 = 纯续 5（主1+从4，含从计划 51 组合 589762111522013184）+ 扩科 1，与 11-12 矩阵一致 | 响应存档 `c-v2.json` |
| 5 | B/BC 售卖过滤（J 545361759016388608/user 654745） | fromC=0：2 条（含 saleStatus=50 的 564918064353779712）；fromC=1：1 条（已过滤；改前两态均 2 条） | `b-0.json` / `b-1.json` |
| 6 | /preheatByRenewal 路由 | POST [589037...] 进入 `RenewalV2JobHandler`（该计划 is_test_data=1 按 Job 规则 skip 预热，路由已证） | TID `cart_gaotu100_com.297.17946538329740007` |
| 7 | 开关恢复 | 三开关恢复验证前值（v2 全关/prefix 开），恢复态 C 查询 code=0 | Apollo release `20261114185739` + final query |

本地：全模块 `mvn8 clean install` 通过；cart-app 554 项 539 过（15 失败=基线既有 ExpandSubjectConfigSubBuilderTest/BCartQuerySubBuilderTest，与本批无关）；V2 更新+新增测试 43 项全过（RenewalV2PureRenewalServiceTest 15、RenewalV2ServiceTest 10、RenewalV2ResultMergerTest 13、RecommendContextNullGuardTest 5）。

**未覆盖**：计划级批量预热未跑通全量用户（样本计划 is_test_data=1 被 Job 过滤；单用户级同写入链路已运行时验证，Job 编排逻辑 11-12 已验且本轮未改）；prod 未动（三开关 PROD 未配置默认 false）；冲突校验/换课失效路径本轮未改未重验。

## 二轮调整（同日 23 时，owner 纠正后）：原 key 恢复主+从合并值 + renewalRole 标记 + 从计划并行化

owner 设计口径更正：原 `renewal:preheat:` key 就是要记录主+从完整合并信息（"没有什么老 key，v2 只是用来测试"），上一提交 47d445da 的「老 key 只写主计划纯续」拆 key 方案撤回。commit `3b49fda6`（7 文件，+170/−84）：

| # | 改动 | 说明 |
|---|---|---|
| 1 | ClazzDetailDTO 新增 `renewalRole`（1=主计划纯续，2=从计划纯续；snake: renewal_role） | owner 指定的区分方式；老值无字段反序列化为 null 兼容 |
| 2 | preheat 恢复无条件写主+从合并值（老 key 与 v2: key 内容相同，仅前缀区分）；role 按 MergedPure.mainPreCourseNumbers 标记 | 原 key=完整记录；v2:=测试对比；空结果删 key 保留 |
| 3 | resolveRelated/冲突校验恢复无条件执行（prefix 不再影响） | 合并值需要关联信息 |
| 4 | 新线程池 `renewalRelatedPlanExecutor`（8-16 线程，SynchronousQueue+CallerRuns，与 C 端详情池隔离） | owner 建议「加一个线程池并行化」；①实时 relatedDetails 各从计划并行（按提交顺序 join，结果与串行一致）；②预热 computeMergedPure 主/从逐计划并行 |
| 5 | 单测更新+新增（合并写入 role 标记/双前缀/空删 key/并行合并顺序保持），43 项全过；全量 554 项 539 过（15 失败=基线既有） | |

### 运行时验证（test-eco-8 @3b49fda6，pod cart-gaotu100-com-7b989f97d-7nw7q）

| # | 验证项 | 结果 | 证据 |
|---|---|---|---|
| 1 | prefix=false 预热老 key | 5 条合并，renewal_role=1主+4从（含 51 组合 role=2） | /preheat 响应 + 日志 TID `cart_gaotu100_com.290.17946706331600008` |
| 2 | **回退态老链路读合并值（P0 不回归）** | code=0，从计划 51 条目判空跳过、普通班条目展示（对照 c98c4158 同场景 code=1 NPE） | TID `cart_gaotu100_com.288.17946706444010009` |
| 3 | V2 实时并行化 | 结果 6 条与串行完全等价；耗时 1.06-1.21s vs 串行基线 1.5-1.7s（**降 ~25-35%**；基线首测冷缓存 4.4s）；B 端 1.03-1.29s vs 1.29-1.36s | 响应存档 c-para.json（基线测量见上一节后补充） |
| 4 | BC 售卖过滤回归 | J 计划 fromC=0 → 2 条；fromC=1 → 1 条（saleStatus=50 过滤）保持 | b2-0/b2-1.json |
| 5 | prefix=true | v2: key 5 条 role 标记 | 日志 TID `cart_gaotu100_com.293.17946707868170009` |
| 6 | 开关恢复 | 三开关恢复验证前值（release 20261114234007），恢复态 C code=0 | final 查询 |

已知口径（如实）：回退态展示中同 SKU 纯续+扩科可并存（老链路按 productId+configuredGrade 去重的既有口径，应急态，非本轮引入）；关联配置变更后存量合并值有 ≤TTL 过期窗口（V2 设计既有，靠「变更后重跑预热」兜底）；并行子线程日志无请求 TID（与项目既有并行写法一致）。

**并行化基线（串行 @47d445da，同日测得）**：C 端关联 4 从 1.5-1.7s（冷 4.4s）、B 端 1.29-1.36s。

### 拆 key 方案的当初动机（回答 owner「为什么要这么改」）

当时判断依据：终态（recommend.v2=true）下没有任何代码路径会消费合并值（V2 实时有关联时跳预热读），且已复现回退态老链路消费合并值 NPE——为了让老 key 在所有开关组合下语义绝对安全，选择了「老 key 只写主计划纯续」的最小改动。错在没有先与 owner 对齐「原 key 记录主+从」这个设计意图就改了存储语义，属于该问没问。本轮按设计意图恢复合并写入，NPE 风险由判空加固（已落地）承接，并行化顺带消掉合并计算的串行开销。
