# 子项2「EM 纯续推荐范围调整」契约提炼（只读）

## 0. 阅读凭证（回读用）
| 材料 | 对象 | revision | 读取时间 | 备注 |
|---|---|---|---|---|
| 子项2 PRD《纯续推荐-纯续关联推荐》 | wiki node `UewqwsMWOiunOgk9Kloce1Jrn52` → docx `WDYOddTNloOrunxiCzmcnNzJnFe` | 707 | 2026-11-12 10:52 CST | 正文 5041 字符，唯一 1 张方案表 + 4 张截图 |
| 技术方案（含表结构+接口） | docx `AQEtdIeKzo7P5IxeQEzc7EpxnBe` | 79 | 2026-11-12 10:52 CST | 40624 字符；**注意**下发的 token 多写一个 Z（`AQEtdIeZKzo…` 报 3380002，正确的是 `AQEtdIeKzo…`） |
| 需求总入口 wiki | `MCUowPVhriDC3okHO0mcW49Unyf` | 79 | 2026-11-12 10:52 CST | 解包后就是上面那份技术方案，不是目录节点，无子节点列表 |
| 本地需求归档 | `…/【A-续班-20261102】…/` 下 README.md(11-12 09:14)、回归测试方案-主从续班计划纯续.md(11-11 11:59)、tasks.md(11-11 13:03)、verify.md(11-12 09:14) | — | 2026-11-12 10:53 | 本地材料含 PRD 之外的口径（缓存键、三场景、已验/未验），冲突处已标注 |

无权限缺失。PRD 正文极简（背景/目标/一张方案表），大量实现口径来自技术方案与本地归档，下文逐条标来源。

## 1. 业务对象模型（一句话定义 + 易混点）
- **续班计划（renew_master）**：OES 里的一期招生计划，`number` 是计划号，`status` 待开始(1)/进行中(2)/其它，`type` 1=大班计划、2=小班计划。推荐/链接都以计划号为单位。
- **主计划 A / 从计划 B·C·D**：A 上配置【纯续关联】，A 的班级推荐时把「A ∪ B ∪ C ∪ D 内学员全部在读班级」的后置纯续班级一起推；**B/C/D 自己作入口时只推本计划**。关系是**计划级、单向、不传递**（A→B 不代表 B→A，也不代表 B 的从计划进入 A）。
- **纯续 vs 扩科**：纯续＝同学科往上升一级（course-center `calculateRenewalType=1`），本次扩到主∪从；扩科＝跨学科推荐，**只取主计划自己的扩科配置，不并从计划**（PRD 原文「A推A扩科，B推B扩科」）。
- **大班 / 小班**：计划 `type` 1/2；推荐商品 `productType` 2=大班班级、6004=小班课产品。本次允许**跨授课模式**同链接、同车、同单。
- **联报 / 组合**：联报（`CLAZZ_SET`，productType=23）是计划入口/条目形态，组合（`COMBINE_PRODUCT`，51）是可售组合商品；两者都不是「计划 type」。**易混点**：联报计划入口(23) ≠ 联报商品条目。
- **学员前置课 / 在读班级**：推荐输入＝学员在「主∪从」计划下的已支付前置课；大班订单在 `order_info`、小班 6004 在 `order_item`，**这是跨模式并集最易断的点**。
- **链接**：纯续/推荐链接只带一个主计划 `renewalNumber`；业务误用的「个人链接」（promotion createLink）可拼多班级，是大小班报错根因，**不在本次改造内**。
- **易混点汇总**：① 上限 10 是「从计划个数」，不是商品数；② 去重是「同年级同商品」只展示一次，**不做同学科校验**；③ 关联是计划级不是课程级；④ 未配置关联＝完全老行为（含缓存键与结果）。

## 2. 需求点全清单（PRD 正文逐条，标来源）
| # | 需求点 | 来源 | 预热/缓存 |
|---|---|---|---|
| R1 | 续班计划操作列新增【纯续关联】入口（OES 续班计划管理） | PRD | |
| R2 | 可操作状态：待开始/进行中；其它状态按钮置灰；绑定后、发送推荐时从计划状态变为其它 → 直接过滤该从计划推荐 | PRD | ⚠️ 缓存需能反映状态变化 |
| R3 | 仅续班计划管理员可操作，否则【仅续班计划管理员可操作】 | PRD | |
| R4 | 弹窗展示当前计划状态/名称/ID/管理员 | PRD | |
| R5 | 从计划搜索：名称单项模糊、ID 批量精确、状态默认=待开始/进行中、过滤测试数据默认=是；搜索范围仅待开始/进行中；按创建时间倒序；展示状态/名称/ID/管理员 | PRD | |
| R6 | 可多选，最多 10 个（**上限可配置**），超限提示【最多可纯续关联X个续班计划】 | PRD | |
| R7 | 相同从计划不可重复绑定（已绑定直接显示绑定态）；不可关联自身 | PRD + 技术方案 | |
| R8 | 已选列表按创建时间倒序，移除需二次确认 | PRD | |
| R9 | 关联结果**本期只在操作弹窗展示**；未绑定显示空 | PRD | |
| R10 | **推荐范围（主计划班级）**：包括主、从续班计划的全部纯续推荐商品 | PRD | ✅ 预热写/读均需主∪从 |
| R11 | **推荐范围（从计划班级）**：只展示本续班计划的纯续推荐商品 | PRD | ✅ 从计划 key 不合并 |
| R12 | 不做同学科校验；每个班级只要有后置班级都推荐 | PRD | |
| R13 | 同商品校验：推荐同商品只展示一次（本地口径：同年级同商品去重，跨年级可重复） | PRD + tasks.md | |
| R14 | 大小班纯续**推荐逻辑不变**，只改推荐范围 | PRD | |
| R15 | 展示位置 4 处：续班服务-批量/单项发链接-推荐链接(大小班)、续班服务-下单-推荐页(大小班)、续班服务-通用链接-推荐链接(大班)、C 端纯续链接(大小班) | PRD | ✅ 读缓存路径 |
| R16 | 扩科推荐无变化，每个续班计划只推自己扩科 | PRD | ✅ 不得并入预热合并结果 |
| R17 | 一次支付含多部门课程、不同主体不能一起下单，只看主体；优惠无影响 | PRD（备注列） | |
| R18 | 紧急需求，目标=减少大小班报错 | PRD | |

技术方案/实现补充（**非 PRD 正文**，但影响契约）：
- T1 新表 `renew_master_relation(main,sub,is_del,…)` + `uk_main_sub`，一主多从；DDL 先于接口上线。
- T2 接口：`GET /b/renewMaster/relation/list`、`POST /b/renewMaster/relation/save`（**全量最终集合**，空=清空）、`/b/renewMaster/list` 扩批量精确号。
- T3 下发：复用 `listRenewalMasterByRenewalNumber`（cart）/`listRenewalWithProcessByNumber`（student-center），DTO 扩 `relatedRenewMasterNumbers`，受开关门控。
- T4 cart 并集：`RenewalService#mergeRelatedPreCourseNumbers` 在 type 分流前合并前置课；大班 `coreHandle`、小班 `SmallRenewalCoreService` 均消费。
- T5 order 放行：`CartSameClazzOrCourseImpl`/`PaymentSizeImpl` 在开关开且**跨授课模式**时放行 `SAME_CLAZZ=4`/`SAME_COURSE=5`/`PAYMENT_SIZE=3`；同商品真重复仍拦；改动点在 **ADD_CART 层**（order-b）。
- T6 开关口径（2026-11-03 owner 确认）：代码默认 `@Value(":true")`＝需求默认生效，Apollo **仅用于回滚**（置 false 回旧逻辑）；单一开关 `renewal.pure.relation.enabled`（cart/order/product 共读）。
- T7 非功能：性能（Redis + 预热）、兼容（未配置=不变）、幂等（唯一键+软删复位）、可回滚（开关）、灰度（白名单/小比例）。

## 3. 明确不做 / 范围外 / 取消项
- 不做同学科校验（PRD 明确「不做」）。
- 扩科**不**并入从计划、不因并集改变扩科配置（只主计划自身）。
- 从计划自身不跨计划推荐；不传递、不回路（互为主从要各自成键，不互相覆盖）。
- 个人链接的拼接能力不改（根因对象，不改造）。
- 子项2 **无存量回溯**（未配置即空，历史链接只带单计划号）。
- PRD「关联结果本期只在操作弹窗展示」——列表页/详情页关联展示不做。
- 技术方案已拍板 Q2=A：不再评估除「计划间关联」外的其它路径（取消项）。
- 前端 cronus（子项1 两 tab）与 GAIA 显示设置是子项1/owner 手动范围，不在子项2。

## 4. 预热与缓存规则（现状 + 本需求要求）
### 4.1 老预热（基线，owner 要求保持不变）
- key：`renewal:preheat:{renewalNumber}:{userId}`（无版本后缀）；TTL=`preheat.cache.time`，默认 **26h**（不改）。
- 写：xjob `RenewalJobHandler`（计划号列表，空=全部在办计划）→ `preheatByRenewalNumber` → **大班按前置课分页取该计划已支付订单用户**，逐用户 `preheat(userId, renewalNumber)`；小班走 `SmallRenewalPreheatService`。跳过无前置课/无活动/测试数据；单用户失败被捕获不阻断。
- **学员范围＝A 计划下（前置课有已付订单）的学员**（owner 最新要求：新预热仍只处理 A 续班计划下的学员，与老一致）。
- 读：C 端 `GET /web/renewal/cart`，`preheat.cache.enabled=true` 且非 B 端加购（`fromBCart=false`）；命中日志 `renewal-data-from-preheat`；B 端 `operation/cart?fromBCart=true` **不读缓存**；未命中现算（结果应一致，仅性能差异）。MISS 不写缓存。
- 值：推荐结果 map（实现细节：本地回归方案记载当前开发分支在主计划老 key 里写合并 map，值前缀 `@mergedRenewal@`；小班按 `beforeCourseNumber` 并入）。

### 4.2 主从合并口径（本需求）
- 预热把「主 + 全部**有效从**（含大小班）」的**纯续**并成一份 map，写回**主计划老 key**；扩科/加购仍为主计划自身；同年级同商品去重。
- 无效从（状态非待开始/进行中、已删、停售/`saleStatus` 冲突）在合并时过滤（对应 R2）。
- 从计划自身入口用自己的 key，预热本计划学员，不继承主计划并集。
- tech 文档 §六(六) 原假设「并集在引擎里所以预热自动带出主+从」**已被 2026-11-04 修正推翻**（`preheat()` 直接调 `coreHandle` 未合并），现实现补 `mergeRelatedPreCourseNumbers`（大班+小班）。

### 4.3 关联关系缓存（product-server）
- key `renewal:relation:{mainRenewMasterNumber}`；值=从计划号列表 JSON，空存 `[]`。
- TTL 非空 1800s（`renewal.pure.relation.cache.expireSeconds`）/ 空 60s（`...emptyExpireSeconds` 防穿透）。
- 失效：`relation/save` 差分落库后**主动删 key**；开关关闭时**不启用缓存直接查库**；Redis 异常告警后回退查库。
- 版本隔离（本地 tasks/verify）：`renewal.pure.relation.cache.invalidate.enabled` + 版本号（含 `:on:sale-v2`），关联变更/售罄口径变化时隔离旧预热。

### 4.4 跨模式订单旁路缓存（cart 新增，性能保护）
- 触发：开关开 && 存在关联从计划；大班路径旁路 `order_item(6004)`、小班路径旁路 `order_info`，不改主查询。
- key `renewal:relation:order:{userId}:{i2i|i2o}:{md5(sorted 前置课号)}`；非空 **300s**、空值哨兵 `[]` **60s**（负缓存）；单次批量 RPC；Redis 异常降级直查。

### 4.5 失效 / 上线时序（必须写进契约）
- 关联变更 → 删 `renewal:relation:{main}` + 预热版本隔离（旧预热 key 不再命中）。
- 换班/换年级 → `invalidateUserPreheat` 清用户预热键。
- 上线：开关先随代码上线（默认开或关需按 owner 口径），**先清 `renewal:preheat:{renewalNumber}:*` 或重跑 `RenewalJobHandler`**，否则 26h 内仍是旧单计划结果。
- 关闭总开关 → 推荐回单计划、order 不放行、不读关联表/缓存；**已写入的关联数据不删**。
- ⚠️ **冲突提示**：owner 最新要求「redis value 格式与原来一致、字段只能新增」与本地记载的现分支做法「值前缀 `@mergedRenewal@`」存在冲突（前缀属于格式变更，老代码解析会当未知标记→MISS）。若坚持老 key 老格式，需把合并结果放进「新增字段」或独立 key，不能靠值前缀。

## 5. 外部依赖（含责任人状态）
| 类型 | 内容 | 责任人 / 状态 |
|---|---|---|
| DDL | `renew_master_relation`（product-server），唯一键/双索引 | 文档未写责任人；需 DDL 工单，先于接口上线 |
| Apollo | `renewal.pure.relation.enabled`（cart/order/product 共读，代码默认 true，仅回滚用）；`renewal.pure.relation.max`（默认 10）；`renewal.pure.relation.admin.accounts`（白名单，appId `course-setting`）；`renewal.pure.relation.cache.expireSeconds/emptyExpireSeconds`；`renewal.pure.relation.cache.invalidate.enabled`；`preheat.cache.enabled`；`preheat.cache.time` | **阻塞**：`product`/`order.gaotu100.com` Apollo 无发布权限（账号 ltao04），test 曾用 Arthas 临时开 |
| Job | xjob `RenewalJobHandler`（计划级预热，job 9981/7508 见 verify.md） | 上线后需重跑/清缓存 |
| GAIA | 子项2 **无** GAIA 改动（子项1 才要 studentTagNames/wechatRemark 显示设置） | 子项1 需 owner 后台手动 |
| ES | 子项2 **无** ES/索引改动（子项1 studentTags 写入与回溯另论） | — |
| 权限 | OES 操作人=计划管理员，或命中 Apollo 白名单；关联接口在 product-b | 文档未逐项署名 |
| 服务链路 | product-server(关系表/下发/关系缓存) → cart(并集/预热/旁路) ；order/order-b(ADD_CART 校验)；course-center(续班关系)；promotion/student-center(链接生成，可能零改) | 跨 4+ 仓，需同批发布（cart 并集与 order 放行必须同批） |

## 6. 验收口径
### 6.1 正向
1) 主计划链接带出主+从全部纯续商品（大班 2 + 小班 6004 混排）；2) 从计划链接只带本计划；3) 同年级同商品仅出现一次；4) 无关联老计划结果/缓存键/字段与上线前逐项一致；5) 跨授课模式同车加购/下单通过；6) 预热命中 vs 未命中（清 key 或 `preheat.cache.enabled=false`）结果无损（商品集合/年级/signUp/allSignUp/默认年级/排序）；7) B 端 `fromBCart=true` 不读合并缓存；8) 开关 false 回单计划、order 恢复拦截。
### 6.2 反向
1) 非管理员 →【仅续班计划管理员可操作】；2) 状态非待开始/进行中 → 接口拒绝+按钮置灰；3) 超上限 →【最多可纯续关联X个续班计划】；4) 重复绑定/自关联 → 拦截；5) 同模式真重复 → `SAME_CLAZZ`/`SAME_COURSE`/`ONCE_BY_LIMIT`；6) 绑定后从计划状态变化 → 该从计划推荐被过滤；7) 关联变更后旧预热不再命中，重跑后命中新集合；8) 扩科不因并集多出从计划科目（`excludeMode` 边界）。
### 6.3 三场景（owner 指定，必须各测正/反 + 预热前/后 + B/C 端 + 开关开/关）
| 场景 | 关键路径 | 判据 |
|---|---|---|
| 大班主 → 小班从 | `coreHandle` + 旁路 `order_item(6004)` + 主 key 合并预热 | C 端返回 2+6004；从计划不丢；B 端现算一致 |
| 小班主 → 大班从 | `SmallRenewalCoreService`/`UserOrderQuerySubBuilder` + 旁路 `order_info` + 小班消费合并缓存 | 返回 6004+2；`smallMergedCacheConsumed` 无损 |
| 已不关联（A1 基线） | 老 key、老值、老单计划逻辑 | 与改前逐字段一致；缓存不得出现合并标记；开关关闭同此 |
每场景证据：`traceId` + Redis key/值前缀/TTL + 接口响应原件 + 关键日志（`preheat-merged-renewal-done`、`renewal-data-from-preheat`）。

## 7. 文档未定义 / 待确认（不要脑补）
1. **同一从计划被多个主计划关联**是否允许（唯一键是 main+sub，技术上允许；PRD 未限）。
2. 推荐**排序规则**与跨模式条目展示顺序（技术文档标「待运行时确认」）。
3. 状态枚举里「未发布」能否关联（PRD 只写待开始/进行中搜索范围）。
4. 上限 10 的具体 Apollo key 名与责任人；需求编号/分支名（技术方案待确认项）。
5. 状态变化「发送推荐时过滤」以请求时刻为准还是预热写入时刻为准 → 决定是否需要状态级失效。
6. 本地已验边界：order 只到 ADD_CART 层，完整 `createOrder` 未走通；`course.filter.type` 是课程类别(30专题/40系列)非授课模式；跨模式排序/扩科共享 DTO 未运行确认。
7. 前端【纯续关联】弹窗：PRD 要求做，技术方案早期写「前端未改/owner 禁改前端」——需 owner 明确当前是否仍禁（与 owner 最新「先只回滚 master」口径相关）。
