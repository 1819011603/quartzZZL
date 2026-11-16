# 2026-11-16 六轮：重构（RenewalService 还原老代码）+ AICR#1668 处置 + 等价性验证（W1）

> 回应 owner 重构要求『把 RenewalService 还原到基线那里 在基线了轻微改动 RenewalV2Service
> 除了开关分支要依赖 RenewalService 其他都是依赖新的类…领导说尽量不动原来的老代码』
> 与『记得看 aicr 已经出现了』。

## 一、重构（commit ac6cb1ff）

- **还原目标口径**：RenewalService 取 **1f5a9118 版（=线上 e315a655 原样，4468 行单计划逻辑）**，
  而非 af82f18a（5201 行含 feature 分支已 revert 的旧版主从合并实现、引用已删除的
  RenewalCrossModeOrderService 等三类）——还原 af82f18a 会把未上线的旧实现带回，违背「其他不变」。
- 分支上 RenewalService 曾被抽成 1377 行薄壳（委托 RenewalSinglePlanDetailService）；还原后老链路
  （回退态/B 端/老 Job）全部回到老代码自身实现。
- **轻微改动（保留 1 处）**：processClazz 六处判空加固（47d445da 引入的 P0 根因修复）重新应用到
  还原后的老代码对应位置——不保留则回退态老链路读 V2 合并值时组合 SKU 条目解析班级 NPE（P0 回归）。
- **V2 依赖结构**（本轮未动，已符合要求）：RenewalV2Service 开关 false 分支调 renewalService
  （老类，:90/:122），true 分支及 RenewalV2PureRenewalService 依赖 RenewalSinglePlanDetailService（新类）；
  RenewalSinglePlanDetailService 保留（V2 消费 getMainPlanDetail*/getPurePlanDetail*/getRelatedPlanDetail/
  computeSinglePlanPureMap），无反向依赖老类。
- 本地：全模块 install 通过；cart-app 554 项 539 过，15 失败=基线既有
  （ExpandSubjectConfigSubBuilderTest 9 + BCartQuerySubBuilderTest 6），与重构前完全一致。

## 二、AICR #1668 处置（评审 head 904a5f13，12 项，commit 38d2d741）

| # | 级别 | 处置 | 说明 |
|---|---|---|---|
| 42569 | high/blocking | **修复**+平台判定 | minGrade 早退恢复无条件（59be925b 加 `!legacyPure` 前缀引入回归，minGrade 空走 minGrade.get() 必抛 NoSuchElementException） |
| 42570 | high/blocking | **误报**（平台判定） | 「写读 Redis 模板序列化不配套」已被 arthas 实证推翻（老写/老读均注入 StringRedisTemplate）+ 两轮运行时验证 code=0（TID 17946839875570153/17946706444010009） |
| 42571 | medium | **修复** | V2 计划级预热小班 delegate 后恢复 return，不再落穿合并纯续（小班 C 端不读该 key 写而无消费 + 小班 queryPlanUserIds 无支付过滤放大无效计算） |
| 42568 | medium | **修复** | V2 单用户 preheat 补 type=2 分支委托 smallRenewalPreheatService.preheatInternal（老链路同语义） |
| 42567 | medium | **修复** | computeMergedPure（仅预热链路）改当前线程串行，renewalRelatedPlanExecutor 专留实时从计划详情，避免批量预热占满池导致实时 C 端 CallerRuns 退化；删 joinPlanPure/未用注入 |
| 42564 | medium | **修复** | renewalRelatedPlanExecutor 补 TtlExecutors 包装（与 renewalContextBuildExecutor 一致，防 trace 断链） |
| 42573 | low | **修复** | isRenewal 入口判空（列表 null 元素防 NPE） |
| 42565 | low | **修复** | pom 注释补 1.5.13 变更说明（related_renew_master_numbers） |
| 42572 | medium | 定性不修 | join 超时降级会静默丢从计划商品（比慢更糟）；下游有 Hystrix 兜底；并行化后 RT 已降 25-35% |
| 42575 | low | 定性不修 | 预热/实时年级口径差异触发条件窄（跨年级学员+主从前置不同年级+同 SKU）；修复需统一去重键语义并全量重验，V2 终态切换前处理 |
| 42566 | low | 定性不修 | 魔法值 1/2（状态常量），风格类 |
| 42574 | low | 定性不修 | Job 配置双拉/CollectionUtils 混用，低价值 |

修复后本地 554/539/15 与基线一致（曾因删注入致 V2PureRenewalServiceTest.setUp 16 失败，同步移除
已删字段反射注入后恢复）。#1668 现状 **PASS / block=0**。对 38d2d741 的更新评审 push 后异步未出，
MR 创建时平台强制再评。

## 三、等价性验证（test-eco-8 @38d2d741，pod cart-gaotu100-com-55d64658bd-jwv7q/10.218.238.179）

样本=上轮全新造数（主 590563861447557120+从 590563948968001536，用户 7704848531 已购主/从前置课）。
**全程 acl 桥+HTTP，未用 arthas**（arthas 曾致新 pod JedisConnection 类初始化污染全 Redis 链路挂——
owner 约束后弃用；kill 1 重建 pod 恢复）。

| # | 项 | 结果 | 证据 |
|---|---|---|---|
| 1 | V2 单用户 preheat（返回值=写入内容） | **role=1（主前置课 sku 590564278055026688）+ role=2（从前置课 sku 590564441871958016）**，与重构前一致 | 桥返回 |
| 2 | 小班计划 V2 preheat（#42571 修复） | 返回 `{}` 走 small delegate，不落穿 | 桥返回 |
| 3 | 批量预热 preheatByRenewalNumber | 正常（void 返回） | 桥 |
| 4 | **回退态老链路 C 端读合并值（老代码还原+判空保留）** | **code=0，role=1×1（主班）+ role=2×1（从班）正确展示** | TID `cart_gaotu100_com.291.17947966233040009` |
| 5 | V2 实时 C 端（recommend.v2=true） | code=0，主+从条目展示（recommendType=1），1.68s（含冷启动） | TID `cart_gaotu100_com.294.17947967571350010` |
| 6 | B 端入口（/feign/renewal/renewalCart） | 主班+从班 2 条 grade=15 齐全 | cart_b.json |

开关翻转（v2=true+prefix=false+recommend.v2=true）→ 验证 → **全部恢复并回读**
（isPreheatV2Enabled=false；release `20261116110155`）。

## 四、结论

重构目标达成：老代码还原为线上原样（仅保留 P0 判空加固一处轻微改动并说明），V2 仅开关分支依赖老类、
其余全依赖新类；老链路与 V2 链路行为与重构前等价（六项对照全过）；AICR #1668 十二项全部闭环
（修 7 / 误报 1 / 定性 4，block=0 PASS）。

## 未覆盖（如实）

- 老 Job（RenewalJobHandler）入口在重构后版本未单独触发运行时验证（其实现=老代码原样还原，
  preheat/preheatByRenewalNumber 方法签名未变，风险极低；此前 T-24 已验证 Job 链路）。
- 对 38d2d741 的 AICR 新评审未出（异步；MR 时强制再评）。
