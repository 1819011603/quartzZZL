# 老链路功能清单与 V2 覆盖对照（W1，只读）

- 版本：HEAD 0528c192；基线 1f5a9118（线上老链路）。
- 方法：只读代码，没有调用任何接口。行号对应 HEAD 版本。
- 缩写：RS = `cart-app/.../renewal/RenewalService.java`；SPD = `RenewalSinglePlanDetailService.java`；V2 = `RenewalV2Service.java`；M = `RenewalV2ResultMerger.java`；PRS = `RenewalV2PureRenewalService.java`；Ctl = `cart-controller/.../controller/RenewalController.java`；Fgn = `cart-controller/.../feign/RenewalFeignService.java`。
- 开关：
  - 详情 V2：`isRecommendV2Enabled`，C 端和 B 端详情都看它。
  - 预热 V2：`isPreheatV2Enabled`。
  - `small.renewal.enabled` 默认 false（RS:192），决定小班走新引擎 SmallRenewalCoreService 还是旧引擎 smallRenewalService。
  - `preheat.cache.enabled` 默认 true（RS:171，SPD:159）。

## 1. 对外入口

| 入口 | 方法 + 完整路径 | 参数 / 鉴权 | V2 关 | V2 开 |
|---|---|---|---|---|
| C 端详情 | GET `/web/renewal/cart`（Ctl:71） | `renewalNumber`（选填，空则抛 KEY_INFO_IS_EMPTY）；`appointUserId`（链接指定学员，与登录人不一致时 status=1，返回 appointPhone；`debugAppointUserEnabled` 打开时直接把它当 userId）；`sellerId` + `includeBCart`（默认 false，两者都有时才查 B 端加购）。鉴权：header `sid`，部分 URL 用 `pt`（UserAuthInterceptor） | V2:96-98 → `RS.getRenewalDetail(7 参数)`（RS:240），fromBCart=false | 无关联：V2:103-104 → `SPD.getMainPlanDetail`（FULL）。有关联：V2:108 主计划 `getMainPlanDetailSkipPreheat` + V2:114 从计划 `relatedDetails` → `getRelatedPlanDetail`，然后 M.merge 和 M.reconcilePure |
| B 端详情 | GET `/web/renewal/operation/cart`（Ctl:85） | `renewalNumber`、`userId`（query 参数，不取登录态）、`fromC`（1 表示 fromBCart=false）。走同一个拦截器（sid） | V2:128-129 → `RS.getRenewalDetail(5 参数)`（RS:1024），getContext=true | 无关联：V2:133-134 → `SPD.getPurePlanDetail`（LEGACY_PURE）。有关联：主计划 `getPurePlanDetailSkipPreheat` + `relatedDetails`，然后 merge 和 reconcile |
| Feign 推荐购物车 | GET `/feign/renewal/renewalCart`（Fgn:52） | `userId`（必填）、`renewalNumber`、`sellerId`、`includeBCart` | 同 C 端，但 fromBCart=**true** | 同 C 端，但 fromBCart=true（永远不读预热缓存） |
| 预热（单用户） | GET `/web/renewal/preheat`（Ctl:142）、GET `/feign/renewal/preheat`（Fgn:64） | userId、renewalNumber | `RS.preheat` | `V2.preheat` |
| 预热（批量） | POST `/feign/renewal/preheatByRenewal`（Fgn:76）、xjob | List<renewalNumber> | RenewalJobHandler → `RS.preheatByRenewalNumber` | RenewalV2JobHandler → `V2.preheatByRenewalNumber` |
| 对比接口（新增，只在测试用） | GET `/web/renewal/preheatCompare` | — | — | — |
| 换课 / 换年级相关 | POST `/productList`、GET `/productFilterData`、POST `/productSelectData`、`/productSelectConfirm`、`/productSelectGrade`（Ctl:96-140） | 请求中带 renewalNumber | 直接调用 RS | **不受 V2 开关影响**，仍然走 RS（见 G1） |

## 2. 功能点对照（以老链路为基线）

| # | 功能 | 触发条件 | 老链路位置 | V2 位置 | V2 是否覆盖 | 依据 |
|---|---|---|---|---|---|---|
| F1 | renewalNumber 为空 | 不传 | RS:243-246、1025-1028，抛异常 | SPD:251-254 | 覆盖 | 同样抛 KEY_INFO_IS_EMPTY。但有关联判断之前，V2 会先执行 `loadMainConfig`：传 null 时它返回 null，resolveRelated 判 main 为 null 后返回空，于是走无关联分支并抛异常 |
| F2 | 计划不存在或没有前置课 | 计划号错误 | RS:251-254，返回空 VO | SPD:259-263 | 覆盖 | 返回空 VO（场景 15 已有运行时证据） |
| F3 | 计划失效 `!isEffective`（productType 为空或 ≤0），大班 | — | RS:342-345、1059-1062，返回空 VO | 主计划：SPD:413-416；从计划：PRS 的 `listActiveRelatedPreCourses` 只保留有效从计划 | 覆盖 | — |
| F4 | userId 缺失 | C 端没有 sid；Feign 不传 | Ctl 用 `getUserIdOrThrow` 抛异常；Fgn 显式抛 USER_IS_EMPTY | 同左（Controller 层，与 V2 无关） | 覆盖 | 入口层代码相同 |
| F5 | 指定学员 ≠ 登录人 | appointUserId ≠ userId | 结果为空时 status=1（RS:363-367、1081-1086、1172-1178）；小班 RS:318-323 | SPD 各分支相同；有关联时 M.merge 第一行以主计划 status 为准（M:50），不拼从计划 | 覆盖 | 有关联时主计划非空就不检查，与老链路相同 |
| F6 | 无前置订单 / 无后置班 / 无后置课程关系 | — | coreHandle 返回空 Map，然后 RS:362 返回空 VO | SPD:1203 起的 coreHandle 是逐行复制的（已审，等价）。有关联时：主计划为空、从计划有内容，会合并出从计划的结果 | 覆盖，**行为变化（有意为之）** | 老链路主计划为空就只返回空；V2 主计划为空时仍会展示从计划纯续（V2 的本意） |
| F7 | 大班纯续 pt2 普通班 | 计划 productType≠23 | RS `processClazz`（RS:1881） | SPD `processClazz`（SPD:1725） | 覆盖 | 方法体与 RS 完全相同（两边判空一致） |
| F8 | 大班纯续 pt23 联报 | 计划 productType=23 | RS `processClazzSet`（RS:1723），订单按 activityNumber 查 | SPD `processClazzSet`（SPD:1566）；SPD:609-614、633-637 增加了 activityNumber 非空过滤 | 覆盖 | 过滤只对合并缓存里的从计划条目起作用，老数据下等价 |
| F9 | 大班 coreHandle 内部：白名单 / 指定推荐（renewalRecommendMap）、联报 handleClazzSet、售卖状态（fromBCart=false 才过滤）、库存本地缓存、用户已换的班（dealSelect + listUserRenewalClazz） | — | RS coreHandle 及其调用的方法 | SPD:1203 起逐行复制 | 覆盖 | 上一轮已逐方法比对，等价（/tmp/w1review/RESULT.md） |
| F10 | 年级分组、默认年级、用户换年级 | — | RS:507-518，`listUserRenewalGrade(userId, renewalNumber)` | 单计划：SPD:586 相同。合并后：M.merge 只在主计划没有 defaultSelect 时补一个（M:113-116） | 单计划覆盖；**多计划行为变化** | 从计划自己的「用户换年级」以从计划 renewalNumber 为准；合并后默认年级以主计划为准，主计划为空时取从计划的 default 或第一个年级 |
| F11 | gradeDesc（年级合并文案 mergeGrade） | `gradeDescEnabled` 且计划在 renewalNumberList 里 | RS 中 mergeGrade 的写法 | SPD 相同；合并时**只沿用主计划的** gradeDesc | 单计划覆盖 | 从计划在名单里而主计划不在时，不会显示（推断，影响小） |
| F12 | 扩科（大班） | 有扩科配置、在时间窗内、`expandSubject=true` | RS:371-395 | SPD:450-465，仅主计划（`!skipExpandPurchase`）；从计划不算 | 覆盖，**有意变化** | owner 口径：从计划只算纯续 |
| F13 | 加购 B 端购物车（大班） | `includeBCart=true` 且 sellerId 不为空 | RS 加购段（`bCartFacade.listAdditionalPurchase`） | SPD:468-472，仅主计划 | 覆盖，有意变化 | 同上 |
| F14 | 三路去重 纯续 > 扩科 > 加购（商品级 + (年级, 学科) 级） | 有扩科或加购 | RS 中 5a/5b 段 | SPD:485 起，单计划内；跨计划由 M.reconcilePure 和 dedupeByProductPriority（M:255）处理 | 覆盖 | 跨计划时只处理同年级同 SKU；**(年级, 学科) 级去重不跨计划**（推断：从计划纯续与主计划扩科同年级同学科但 SKU 不同时，两条都会保留） |
| F15 | recommendType / forceBuy / renewalForceBuy / expandForceBuy / canChangeCourse | C 端 7 参数入口 | RS:405-410、`setRecommendTypeFields`（RS:4185） | 主计划：SPD:482-488。从计划（RELATED_PURE）按**从计划自己的** renewalForceBuy 标记。VO 上的 renewalForceBuy / expandForceBuy 取主计划的值 | 覆盖，有意变化 | 从计划条目的 forceBuy 跟随从计划配置 |
| F16 | B 端不打标、不排序、不设 forceBuy | 5 参数入口 | RS:1040-1180 | LEGACY_PURE（SPD:268、473、653、681） | 覆盖 | 上一轮已确认等价 |
| F17 | 同年级展示排序（未购在前 → 强制购买在前 → 纯续 > 扩科 > 加购） | C 端 | RS `sortClazzDetailDTOsForDisplay` | SPD 相同；合并后 M 中 `DISPLAY_ORDER`（M:34）按同一口径重新排 | 覆盖 | 有关联的 **B 端**合并结果也会被 DISPLAY_ORDER 排序，而老 B 端不排序（行为变化，影响小） |
| F18 | signUp / allSignUp | — | processClazz / processClazzSet | 单计划相同；合并时 allSignUp 取主计划和所有有贡献的从计划的 AND（M:96-97） | 覆盖 | 主计划为空时取从计划的值 |
| F19 | msg（getContext 调试信息） | B 端 getContext=true | RS `recommendContext.getInfos()` | 相同；合并时追加从计划的 msg（M:98-102） | 覆盖 | — |
| F20 | 小班，新引擎 C 端 | type=2 且 `small.renewal.enabled=true` | RS:271-324：recommendAll(带 sellerId/includeBCart) → 扩科 → 加购 → merge → 转 VO | SPD:297 `getSmallClassRenewalDetail`：FULL 时相同，另外可读小班缓存（SPD:317-326，命中后现场重建上下文）；RELATED 时只算纯续（SPD:330 起） | 覆盖 | 商品类型：6004 走 `processSingleClazzResult`，51 走 `processCombineProductResult`，23 走 `processClazzSetResult`（SPD:2200，**新增**了 postClassInfo 为空时用前置课降级组装，老链路会直接丢掉该条） |
| F21 | 小班，新引擎 B 端 | type=2、5 参数、开关为 true | RS:1041-1054：3 参数 recommendAll + 转 VO + appoint 检查 | SPD LEGACY_PURE 分支（SPD:322 起，3 参数 recommendAll） | 覆盖 | 等价 |
| F22 | 小班，旧引擎（`small.renewal.enabled=false`） | type=2、开关为 false | **C 端（RS:271）条件不满足，type=2 掉进大班 getLargeClassRenewalDetail**；B 端（RS:1055-1057）走 `smallRenewalService.getRenewalDetail` | SPD:284 条件是 `smallRenewalEnabled ‖ legacyPure`：C 端 FULL 和 RELATED 同样掉进大班逻辑；B 端走 SPD:307-311 旧引擎 | 覆盖（保留了老行为，包括 C 端掉进大班逻辑这一老问题） | V2 下的差异：`computeSinglePlanPureMap` 对 type=2 调用 `getPurePlanDetail` → LEGACY_PURE → 旧引擎，并传 fromBCart=true，这只影响**预热**；实时 C 端走大班逻辑。**开关为 false 时，小班的预热和实时会走不同引擎**（代码确认；需确认线上开关值） |
| F23 | 小班组合商品 51 / 6004 / 扩科 / 加购的 enrich | — | RS `enrichRecommendResults`（RS:4206） | SPD:2572，规范化后完全相同 | 覆盖 | — |
| F24 | 预热缓存读取（大班） | `preheat.cache.enabled` 且 !fromBCart | RS:352、1067 → `corePreheatCache` | SPD:429（另加 `!skipPreheatRead` 条件）；命中后 retainAll（SPD:1183） | 覆盖 | 见第 4 节 |
| F25 | 主从关系合并 | 计划配置了 relatedRenewMasterNumbers | **老链路没有这个功能**（RS 中 `RelatedRenewMaster` 出现 0 次） | V2 新增：PRS.resolveRelated（关联、有效性、共用前置课校验，失败直接抛异常）+ 从计划并行（10s 超时）+ M.merge / reconcilePure | V2 新增能力 | 有共用前置课时抛 BUSINESS_ERROR（PRS:197）；从计划失败或超时时整个请求失败（V2:165-181）——**老链路没有这种失败方式** |
| F26 | 预热写入 | /preheat | RS.preheat：只处理大班，写 K = 主计划纯续；小班直接 return | V2.preheat：大班写主+从合并值（打 renewalRole），小班写 Payload（V2:208-210） | 覆盖并扩展 | — |

## 3. 重点：老链路有、V2 缺失或语义改变的功能

| # | 问题 | 位置 | 影响 | 证据 |
|---|---|---|---|---|
| **G1** | **从计划条目的换课和换年级与合并展示不闭环** | 从计划条目是 `getRelatedPlanDetail(userId, relatedNumber, …)` 按**从计划 renewalNumber** 算出来的。用户换的班读的是 `listUserRenewalClazz(userId, 从计划号, …)`（SPD:1891），换年级读的是 `listUserRenewalGrade(userId, 计划号)`（SPD:586）。但合并结果 `RenewalCartVO.renewalNumber` 只有**主计划号**（SPD:257），`ClazzDetailDTO` **没有来源计划字段**（ClazzDetailDTO.java 中 renewalNumber 出现 0 次）。前端调 `/productSelectData`、`/productSelectConfirm`、`/productSelectGrade`、`/productFilterData` 时带的是主计划号（RS:2686、3177、3196、2099） | 用户在**从计划条目**上「换课」：(a) 候选列表按主计划的 type 判断大小班（`isSmall(主计划号)`，RS:3630）。主计划是小班、从计划条目是大班时，会进入小班换课逻辑（反之亦然）。(b) 确认后写入的是 `UserRenewalClazz(主计划号, 前置课)`，而从计划详情读的是 `(从计划号, 前置课)`，**换课不生效**，刷新后又变回原推荐。(c) 换年级只写主计划，从计划的年级默认值不受影响 | 代码确认（数据流推断）；运行时**未验证**。需要前端或 owner 确认从计划条目是否允许换课（canChangeCourse：RELATED_PURE 下大班为 true、小班纯续为 true） |
| G2 | V2 开、`small.renewal.enabled=false` 时，小班预热与实时走不同引擎 | PRS → `SPD.computeSinglePlanPureMap`（SPD:2883 起）对 type=2 用 LEGACY_PURE → `smallRenewalService` 旧引擎，fromBCart=true；实时 C 端 SPD:284 条件不满足，进入大班逻辑 | 预热写入的值与 C 端实时不一致；从计划是小班时，合并纯续的口径也不同 | 代码确认；线上开关值需要另查。若线上为 true，则不会触发 |
| G3 | 新增失败方式：从计划超时 / 失败、关联查询失败、共用前置课校验失败 → 整个请求失败 | V2:165-181、PRS:123-127、PRS:197 | 老链路只算主计划，不会因为别的计划失败。V2 下任一从计划出问题，用户就看不到主计划的推荐 | 代码确认；这是 owner 2026-11-17 定的口径（有意为之），但需要在覆盖矩阵里单独列出来测 |
| G4 | 主计划为空时仍展示从计划结果；默认年级、allSignUp、gradeDesc、renewalForceBuy 都以主计划为准 | M:48-118 | 与老链路「主计划为空即空页」不同 | 代码确认，有意为之 |
| G5 | 跨计划只按同 SKU 去重，不做 (年级, 学科) 去重 | M.reconcilePure / dedupeByProductPriority | 主计划扩科 X 学科和从计划纯续 X 学科在同一年级时，两条都展示（老链路单计划内只会留纯续） | 推断，未验证 |
| G6 | 有关联的 B 端结果会被 DISPLAY_ORDER 重新排序，且条目里没有 recommendType 时统一当作纯续 | M:34、M:333 | 老 B 端不排序 | 代码确认，影响小 |
| G7 | 预热缓存只在**无关联**计划上生效（V2:103-108） | — | 有关联计划在 V2 下每次实时计算（性能，不是功能） | 代码确认（见 /tmp/w1audit/cov/paths.md 第 0 节） |
| G8 | 小班联报 23 在 postClassInfo 为空时用前置课降级组装 | SPD:2209-2242 | 老链路会丢掉这一条；V2 会展示，且年级取前置课年级 | 代码确认，有意为之（commit 1848584c） |

## 4. `preheat.cache.enabled=false` 时是否完全不读预热缓存

- 老链路大班：RS:352（C 端）、RS:1067（B 端），条件都是 `preheatEnabled && !fromBCart`，false 时**不读**。老链路小班本来就不读。
- V2 大班：SPD:429 `preheatEnabled && !fromBCart && !skipPreheatRead`，false 时**不读**。
- V2 小班：SPD:317 `Boolean.TRUE.equals(preheatEnabled) && …`，false 时**不读**。
- 全仓读预热 key 的地方只有 RS.corePreheatCache、SPD.corePreheatCache、SmallRenewalPreheatCacheService.read 三处，都被上面这几个条件控制。
- 其他：对比接口经由 SPD 读取，同样受控；`RenewalV2PureRenewalService` 的 `hasKey` 读的是关联校验缓存 `renewal:relation:validate:*`，不是结果缓存。
- 结论：key 名为 `preheat.cache.enabled`，设为 false 时，老链路和 V2 的 C 端、B 端**都完全不读**预热结果缓存（代码确认）。
- 注意：它**不影响写入**。V2.preheat 和 RS.preheat 不看这个开关，照样写；写入只受 `isPreheatV2Enabled` 路由控制。
