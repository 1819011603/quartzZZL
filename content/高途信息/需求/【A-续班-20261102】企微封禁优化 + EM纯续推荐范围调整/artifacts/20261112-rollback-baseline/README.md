# 2026-11-12 回滚基线分支 + diff 风险 + V2 可行性

> 本阶段只交付：意图复述与方案、回滚分支、master↔基线全量 diff 分析、线上 release/master 现状、V2 设计可行性。
> **未改业务代码、未改线上配置、未发布**。契约要点见 [prd-contract-extract.md](prd-contract-extract.md)；可执行开发方案见 [V2-开发方案.md](V2-开发方案.md)。

## 1. 结论

- **分支已交付（按 owner 更正后重建）**：`feature-renewal-rollback-clazzset-dedup-20261112`，从 `origin/release@af82f18a` 新建，HEAD `1f5a9118`，已 force-push 更新远端（旧基点提交 `b6692a63` 已废弃）。
  内容与 `origin/feature-renewal-clazzset-dedup@e315a655` **逐文件一致（diff=0）**，也与线上 cart 镜像提交 `4b40ee27` **逐文件一致（diff=0）**。
- **线上 cart 生产镜像**：`release-4b40ee27-20261107115215`，Pod 创建时间 2026-11-11 15:00–15:02（昨天的回滚动作=重发旧镜像，不是改分支）。
- **release/master 未回滚**：`origin/release@af82f18a`、`origin/master@0eb97988`，两棵树完全相同，都含错误的 `feature-renewal-preheat-small-20261111` 代码。
  生产 product-c/b 已在 `release-c1bc0d6b`（含关联下发），cart 基线忽略未知字段，生产实际仍是单计划行为。
- **V2 设计可行，但必须调整 3 处**：
  1. 无法做到「RenewalService 一行不改」——至少需要开关入口 + 单计划推荐结果出口（建议 Controller/Feign/Job 放开关，RenewalService 只加包内单计划方法）。
  2. 缓存值**不能加 `@mergedRenewal@` 前缀**（与 owner「value 格式不变」冲突）。
  3. 回滚开关后老代码会读到合并值，需约定清理/重跑预热或灰度期只写 v2 key。

## 2. 分支与校验

| 项 | 值 |
|---|---|
| 仓库 | `gaotu/cart` |
| base | `origin/release` = `af82f18a`（2026-11-11 11:21，Merge feature-renewal-preheat-small-20261111） |
| 分支 | `feature-renewal-rollback-clazzset-dedup-20261112` |
| HEAD | `1f5a911895730a1b919c4900998807bbebf980fb`（父提交 = `af82f18a`） |
| 远端 | `1f5a9118...`（`--force-with-lease` 更新，旧 `b6692a63` 已废弃；MR !298 头提交已自动跟随） |
| 基线 | `origin/feature-renewal-clazzset-dedup` = `e315a655`（2026-11-07 11:46） |
| 线上镜像提交 | `4b40ee27`（2026-11-07 11:48，Merge branch 'feature-renewal-clazzset-dedup' into 'release'） |

核对命令（可复跑）：

```bash
git rev-parse HEAD^                                          # af82f18a（基点=origin/release）
git diff --name-only origin/feature-renewal-clazzset-dedup   # 0
git diff --name-only 4b40ee27                                # 0
git diff --stat origin/master                                # 41 files, +166/-3638
```

工作区：`/Users/gaotu/IdeaProjects/JavaProject/cart-rollback-clazzset-dedup`（独立 worktree，不影响原开发分支）。
原始 diff：`diff-master-vs-baseline.patch` / `.stat`。

## 3. master（错误）相对基线的全量 diff

方向：`origin/main` → `feature-renewal-clazzset-dedup`（删除=master 多出来的错误实现）。41 文件，+166/−3638。

### 3.1 生产代码（17 个）

| 文件 | 变化 | 说明/风险 |
|---|---|---|
| `RenewalCrossModeOrderService.java`（新增 318 行） | 大班路径旁路 `order_item`、小班路径旁路 `order_info`，并集+Redis 缓存（默认关）、空哨兵防穿透 | 关联存在时每次多 1 次批量 RPC；资格口径依赖订单表；缓存 TTL 300s/60s |
| `RenewalRelatedResultMerger.java`（新增 150 行） | 主计划结果 + 各从计划纯续结果合并，同年级同商品去重 | 合并只并纯续；排序与主链路同一比较器 |
| `RenewalRelationCacheService.java`（新增 54 行） | 关联配置缓存版本（`:on:sale-v2`），失败返回 `uncached:UUID` 强制实时 | 每个计划加载多 1 次 product RPC |
| `RenewalService.java`（+858/−125） | 主从推荐编排、合并预热读写、逐计划推荐、年级回填、批量预热入口 | **风险最集中**：实时/缓存两条路径已出现不一致（审查 F1/F2/F4） |
| `RenewalDataService.java`（+158/−12） | `listRenewalMasterStandalone`、`activeRelatedRenewalNumbers`、`standalone()` 清关联、关联状态快照 | `standalone()` 原地修改 DTO，复用同一对象时易丢关联信息 |
| `BasicConfig.java` | 新增 `renewalRelatedRecommendExecutor`（core5/max10/SynchronousQueue/CallerRuns） | 无队列，超 10 个从计划时任务落请求线程；无销毁钩子 |
| `RenewalJobHandler.java` | 仅注释 | 无功能变化 |
| `recommend/condition/RecommendContext.java` | 班级/课程查询加 null 兜底 | 会掩盖 NPE、静默丢条目（参考分支已改回硬失败） |
| `small/builder/sub/PostClassInfoBuildSubBuilder.java` | 关联计划允许缺库存（`allowMissingStock`） | 只对关联计划放开的售卖口径 |
| `small/builder/sub/StockInfoQuerySubBuilder.java` | 库存按班级自身 productType 查 | 修复跨模式只查 6004 漏查 |
| `small/builder/sub/UserOrderQuerySubBuilder.java` | 小班订单并集大班 `order_info` | 依赖 `relatedRenewMasterNumbers` |
| `small/builder/sub/UserPostClassOrderSubBuilder.java` | 已购后置班补查大班 | 同上 |
| `small/context/SmallRenewalPostClassInfo.java` | `isSalable` 对关联计划放宽缺库存 | 普通计划仍严格；改动面扩大 |
| `small/context/SmallRenewalRecommendContext.java` | 新增 `mainOwnPreCourseNumbers` | 扩科年级收口用 |
| `small/service/ExpandSubjectRecommendService.java` | 扩科年级/排除只取主计划自身前置课（B7） | 业务正确，但与从计划并集耦合 |
| `small/service/SmallRenewalPreheatService.java` | 改为 standalone 配置，避免预热并入关联 | 与在线合并口径相反 |
| `cart-client/.../ProductFeignServiceAdapter(+Impl)` | 新增批量前置课 RPC | 每次请求多 1 次 product 调用 |
| `cart-client/.../RenewalRelationCacheFeignService.java`（新增） | `/c/renewMaster/relation/recommendationCacheState` | product 依赖 |
| `cart-client/.../model/RenewalPreCourseDTO.java` | 新增 `relatedRenewMasterNumbers`、`relationCacheVersion`、`activeRelatedPreCourses` | 需要 product-server-client 1.5.13 |
| `pom.xml` | 1.5.11 → 1.5.13 | 回滚分支保持 1.5.11，与生产一致 |

### 3.2 测试与任务记录（24 个）
删除 19 个主从/合并/缓存测试（`RenewalServiceSmallMergedCacheTest`、`RenewalRelated*`、`RenewalPreheatKeyCompatibilityTest` 等），改 3 个，`tasks/lessons.md` 删除、`tasks/todo.md` 截断 41 行。

## 4. 主要风险与不合理点

1. **值格式被改**：合并预热写 `@mergedRenewal@` + JSON（前缀），基线老代码 `JSON.parseObject` 不认识，回滚后读新值会解析失败。直接违反 owner「value 格式与原一致、只能加字段」。
2. **预热与实时不等价（已运行复现，见 2026-11-12 review）**：
   - F1 合并预热把入口计划强购配置套到所有条目，从计划 `forceBuy` 被覆盖；
   - F2 混合结果中 6004 已购状态与 `allSignUp` 自相矛盾（`standalone` 清空关联后订单补查被跳过）；
   - F4 跨计划扩科去重范围随缓存命中变化。
3. **关联变更不失效合并预热（代码确认，未运行复现）**：预热 key 固定 `renewal:preheat:{plan}:{user}`，`hasMergedRenewalCache` 只判前缀不比对版本；关系变更后 26h 内仍可能返回旧从计划商品（与审查 F3 同类）。
4. **批量预热放大**：每个 A 计划用户都要额外算全部从计划的纯续；xjob 逐计划跑时主/从会重复计算，job 时长和 RPC 量需实测。
5. **早退丢预热**：`preheat()` 在 product 版本不可用时直接 return，不再写任何预热；基线是始终写单计划值。
6. **小班单用户预热丢扩科内存预热**：基线 `preheat` 小班走 `preheatInternal`（含 `expandSubjectRecommendService.recommend`），master 改为 `smallPlanPureMap`，少了这一步（批量 job 仍保留）。
7. **空池/线程**：`SynchronousQueue`+CallerRuns 在从计划多时把任务压回请求线程；建议有界队列或固定并发。
8. **测试被删**：主从合并相关回归被整体删除，只留新增测试，回滚后没有对应覆盖。

## 5. 线上 release/master 现状与回滚方案

### 5.1 现状（已验证，2026-11-12）

| 对象 | 当前 | 证据 |
|---|---|---|
| cart 生产镜像 | `release-4b40ee27-20261107115215`，4 Pod Running/UP，创建 2026-11-11 15:00–15:02 | 青舟 getServicePods（prod），runtime-state.json |
| 生产源码 | 与基线 `e315a655` 逐文件一致 | `git diff 4b40ee27 e315a655` = 0 |
| `origin/release` | `af82f18a`（Merge feature-renewal-preheat-small-20261111） | ls-remote |
| `origin/master` | `0eb97988`（merge cd-delivery-af82f18a） | ls-remote |
| release vs master | 树完全相同 `2011e666` | `git diff --stat` 空 |
| product-c/b 生产 | `release-c1bc0d6b`（11-10，含关联下发） | getServicePods |

结论：昨天的回滚只回滚了**生产部署**（重发 11-07 旧镜像），**release/master 两个分支未回滚**，下次从它们构建会把错误代码带回生产。

### 5.2 回滚方式（已做本地合并模拟，未推送）

祖先关系（已验证，按新基点）：

- 回滚分支 `1f5a9118` 的**父提交就是 `origin/release@af82f18a`** → release 可**快进**；
- `origin/master@0eb97988` 不是分支祖先，但其 tree 与 `af82f18a` 相同（都为 `2011e666`），
  因此 master 合并时以 `af82f18a` 为 merge base，master 侧无内容变化 → 合并结果就是回滚树，无冲突。

本地模拟（Git 2.45）：

```bash
# 无冲突验证（Git 2.45）
git merge-tree --write-tree origin/release feature-renewal-rollback-clazzset-dedup-20261112
# 输出 58cd2a93c91133df592dddb089e1d007abc31263，exit=0（release 侧为快进）
git merge-tree --write-tree origin/master  feature-renewal-rollback-clazzset-dedup-20261112
# 输出 58cd2a93c91133df592dddb089e1d007abc31263，exit=0（无冲突）
```

树比对（已验证）：

| 引用 | tree |
|---|---|
| 回滚分支 HEAD `1f5a9118`（父=`af82f18a`） | `58cd2a93` |
| merge-tree(release, 回滚分支) | `58cd2a93` |
| merge-tree(master, 回滚分支) | `58cd2a93` |
| 基线 `e315a655` | `58cd2a93` |
| 生产镜像提交 `4b40ee27` | `58cd2a93` |
| 当前 release/master | `2011e666` |

### 5.3 建议执行步骤（待 owner 明确授权后执行，本阶段未做）

1. **release**：把 `feature-renewal-rollback-clazzset-dedup-20261112` 合入 `release`。该分支父提交就是 release，可**快进**到 `1f5a9118`（或 `--no-ff` 生成同树 merge commit）。
2. **master**：再把同一分支合入 `master`。master 含 release 之外的 cd-delivery 合并提交，不能快进，但以 `af82f18a` 为 base 无内容冲突，合并结果为回滚树 `58cd2a93`。
   > 注意：GitLab 上已存在 **MR !298**（source=本分支，target=`master`），是旧基点推送后生成的。建议先把 !298 的目标改为 `release` 并合并，再另建/复用 MR 合 master；不要先合 master。
3. **合并后回读**：

```bash
git ls-remote origin refs/heads/release refs/heads/master   # 应为 1f5a9118 或同树 merge commit
git diff --name-only origin/release origin/feature-renewal-clazzset-dedup   # 0
git diff --name-only origin/master  origin/feature-renewal-clazzset-dedup   # 0
```

4. **生产**：无需发布，现有 Pod 已是同一棵树。仅当 owner 要求「镜像 tag 与 release 提交对齐」时，再单独批准一次 release 构建+发布（属于生产写操作）。

### 5.4 影响面

- 回滚提交删除的是：主从关联合并（`RenewalCrossModeOrderService`/`RenewalRelatedResultMerger`/`RenewalRelationCacheService`）、合并预热（`@mergedRenewal@` 值）、小班跨模式适配，以及对应测试；`pom` 回到 1.5.11。
- product-server / order / student-center **不改**。生产 product 已下发 `relatedRenewMasterNumbers`，基线 cart 按 FastJSON 默认忽略未知字段（代码推断，未对生产实例发请求）。
- 现有 `feature-renewal-preheat-*` 系列分支仍含错误代码；回滚后**不要再把这些分支合入 release**，V2 应从新的 release/master 重新拉分支。已合入的 MR（!284/!293/!289 等）保留在历史中，由回滚提交覆盖。
- 未回滚的风险：下一次 release/master 构建即把错误实现带回生产；任何基于当前 release 的 hotfix 也会继承。
- 回滚提交会删除 19 个测试文件；若其他在途分支改过这些文件，后续合并会有冲突，需以回滚后的 release 为基重新对齐。

### 5.5 为什么不能单点 revert `af82f18a`

`af82f18a` 只撤销 11-11 的 `feature-renewal-preheat-small-20261111` 合并；11-09 的主从关联（MR !284）和 11-10 的合并预热（MR !293）是更早的独立提交，单点 revert 后仍留在 release，结果不等于生产镜像。**按内容整体对齐是唯一与线上一致的做法**。

## 6. V2 设计可行性（对 owner 约束逐条）

| 约束 | 结论 | 冲突/说明 |
|---|---|---|
| 以回滚后代码为基线 | 能 | 分支已就绪 |
| value 格式不变，只加字段 | 能，需改实现 | 现分支 `@mergedRenewal@` 前缀必须去掉；值保持 `JSON(Map<Long, ClazzDetailDTO>)`；需要来源标记就给 DTO 加字段 |
| 预热 A 只处理 A 学员 | 能，现状如此 | 大班按 A `courseNumbers` 查 `order_info` 已付用户；小班 `queryUserIds` 同样只用 A `courseNumbers`；V2 不得遍历从计划学员 |
| 大班关联小班/小班关联大班/不关联三场景 | 能 | 前两者分别走 `coreHandle` 与 `SmallRenewalCoreService`；不关联必须与改前逐字段一致 |
| Apollo 控制 v2 key 前缀仅用于 diff | 能 | 新增 key（建议 `renewal.preheat.v2.prefix.enabled`），key=`renewal:preheat:v2:{plan}:{user}`，value 同格式；生产仍写 `renewal:preheat:` |
| 逻辑集中到一个新核心类 | 部分能 | 大班 `coreHandle`/预热读取是 `RenewalService` private 且强耦合；V2 复用必须开一个包内单计划出口，或把 500+ 行私有逻辑搬出（参考分支做法，改动大） |
| RenewalService 尽量不变，外层开关 | 能，但需最小改动 | 建议开关放 `RenewalController`/`RenewalFeignService`/`RenewalJobHandler`；RenewalService 仅加一个包内单计划方法给 V2 调用，避免递归 |
| 新增 RenewalV2Service 兼容老代码+主从 | 能 | V2 负责：关联解析、逐计划推荐、纯续合并、预热值组装；老代码原样保留 |
| `renewal:preheat:` 结构不变 | 能，需去掉前缀 | 老代码解析新字段安全；合并值写老 key 的回滚风险需单独约定 |

### 6.1 owner 决策后的最终形态（2026-11-12）

owner 已对 7 个决策点拍板，完整方案见 [V2-开发方案.md](V2-开发方案.md)。要点：

1. **公共类 + 最小改动**：新增 `RenewalV2Service`（编排）和 `RenewalCommonService`（公共复用层）；`RenewalService` 只新增 2 个包内方法（单计划纯续结果、合并 map 装配），**原方法体不动**，不做全量抽取。
2. **value 完全不变**：老 key 写纯 `JSON(Map<Long,ClazzDetailDTO>)`，去掉 `@mergedRenewal@` 前缀；不新增字段、不加包装。
3. **v2 前缀只写不读**：`renewal:preheat:v2:{plan}:{user}` 仅用于 owner 直接看 Redis 做人工 diff；线上最终写回 `renewal:preheat:`。
4. **不引入版本键、不清缓存、不做守卫**：关联变化后 TTL 内可能返回旧从计划商品，作为已知风险由 owner 确认接受。
5. **选品/换课/换年级不做**：保持老行为，不接 V2、不新增失效逻辑。
6. **依赖**：`product-server-client` 1.5.11 → 1.5.13。
7. **小→大测试数据**：用造数项目新建。

原先「用独立 version key + 老代码守卫 + 回滚清缓存」的建议**已按 owner 决策废弃**，不再作为实施方案。

## 7. 三场景测试数据现状（test）

已查 `gaotu.renew_master_relation` / `gaotu.renew_master`（只读，2026-11-12）：

| 场景 | 可用样本 | 状态 |
|---|---|---|
| 大班关联小班 | 588858850300473344(type1) → 586116340522184704(type2)；545361759016388608(type1) → 551533000353986560(type2，组合51) | 可直接用 |
| 小班关联大班 | 586116340522184704 → 585960797778243584 当前 `is_del=1`（已解绑） | **需新建/恢复关系**后才能测 |
| 已不关联 | 588872241920421888；或任一未配置计划 | 可直接用 |

学员沿用 7658129872 / 7707220467 / 654745；预热入口 E1 xjob、E2 单用户 HTTP，读入口 C/B（详见回归方案）。

## 8. 未做 / 未验证

- 未改 release/master，未发 MR，未做生产发布（按 owner 要求等确认）。
- 未开发 V2 业务代码。
- 小班关联大班样本未创建；未跑三场景运行验证。
- 关联变更后旧合并预热是否仍命中：代码确认存在，未运行复现。
- product-c 生产返回 `related_renewMasterNumbers` 时基线 cart 的行为：按代码是忽略未知字段（FastJSON 默认），未对生产实例发请求验证。

## 9. 改动方案（建议落地顺序，未执行）

> 目标：在回滚基线上用「1 个新核心类 + 外层开关」重新实现主从纯续，老链路可一键回退，缓存 value 保持原格式。

### Step 1 依赖与开关骨架
- cart `product-server-client` 1.5.11 → 1.5.13（取 `relatedRenewMasterNumbers`；生产 product 已有该字段）。
- 新 Apollo：`renewal.recommend.v2.enabled`（默认 false）、`renewal.preheat.v2.prefix.enabled`（默认 false，仅 diff 用）。
- 开关放 `RenewalController` / `RenewalFeignService` / `RenewalJobHandler`，三分支调用 `RenewalV2Service` 或原 `RenewalService`。
- `RenewalService` 只加一个包内方法暴露「单计划推荐结果」（返回 `Map<Long, ClazzDetailDTO>` / VO），供 V2 复用大班 `coreHandle`、小班 `SmallRenewalCoreService`；不改原方法体。

### Step 2 新核心类 `RenewalV2Service`
- `getRenewalDetail(...)`：主计划配置 → 有效从计划（状态/删除过滤）→ 无关联直接走老逻辑；有关联则主 + 各从**各自按本计划推荐**（有界线程池）→ `mergePure`（只并纯续、同年级同商品去重、扩科/加购只取主）。
- `preheat(userId, A)`：只处理 A 的学员；对每个用户算「A + 全部有效从」纯续，合成 `Map<Long, ClazzDetailDTO>`；扩科不并入。
- `preheatByRenewalNumber(A)`：学员集合仍只从 A 的 `courseNumbers` 取（大班 `order_info`、小班 `orderInfoFacade.listByCourseNumber`），**不遍历从计划学员**。

### Step 3 缓存契约
- 生产 key：`renewal:preheat:{A}:{user}`，value = `JSON(Map<Long, ClazzDetailDTO>)`，TTL 26h；**不加 `@mergedRenewal@` 前缀**。
- 需要标记来源时：`ClazzDetailDTO` 新增 `sourceRenewalNumber` / `productType` 等字段（老代码反序列化忽略未知字段）。
- diff 模式：`renewal:preheat:v2:{A}:{user}` 写同一份 value（是否同时写老 key 由 owner 定）；比对脚本按用户逐条 diff。
- 回滚约定：开关关闭后老代码会读到合并值；上线方案必须写明「清 `renewal:preheat:*` 或重跑 `RenewalJobHandler`」再回滚。

### Step 4 验证（做完再交付）
- 三场景：大班→小班、小班→大班（需恢复/新建关系）、不关联；每场景 C/B 端 + 预热前/后 + 开关开/关。
- 缓存命中 vs 未命中逐字段一致（商品集合/年级/signUp/allSignUp/默认年级/排序）。
- 关联变更 → 旧预热不再命中（这是现实现缺失项，V2 必须在读取时校验版本或写值时带版本，不能只靠 TTL）。
- 批量预热 job 时长/RPC 量对比基线，给出实测。
