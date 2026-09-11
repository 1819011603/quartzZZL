---
title: 续班预报名使用膨胀券 · 任务板
tags: [需求, 任务]
---

# 任务板（只记 Claude 的活）

> **边界**：只记 Claude 要做/做过的任务。
> - 用户手工做的事 → `changelog.md` 的「👤 我」分区
> - TAPD 工时任务 → 只在 `links.md` 存链接，真相源在 TAPD 服务端
>
> 三套编号各自独立、**只增不减、永不复用**（删掉的标「已取消」，不腾号）。
> 状态：`待办` `进行中` `已完成` `阻塞` `已取消`

## T- 开发任务

> 按 6 个模块拆。2026-09-08 五个仓库代码全部提交并推送，**编译全绿**，但均未写单测、未跑功能自测。

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 券选品分页查询接口 `POST /renewal/pre/coupon/list` | 已完成 | — | student-center `da6d242a0`；13 新文件 |
| T-02 | 券适用范围表 + 活动配置支持膨胀券（edit/详情/列表/意向列表） | 已完成 | — | product-server `5a925c2eb`；顺手修掉 detailList 对券订单的 NPE |
| T-03 | 促销侧活动支持膨胀券形式与券可用范围 | 已完成 | — | promotion `938590af5`；原 `type!=1` 硬门槛会让膨胀券活动存不进去 |
| T-04 | 膨胀券商品加购 + 购物车总价 | 已完成 | — | order `073dea69e2`；**范围已收敛**，见备注区 |
| T-05 | C 端预报名落地页取数与算价改造 | 已完成 | — | cart `0b529fa4`；算价复用既有 `skuNumbers` 桶 |
| T-06 | ~~发链接按活动形式分流到 `/preSignUpCoupon`~~ | **已撤销** | — | 前端无此页面，配了会 404。定稿：path 不分叉，两形式共用 `/preSignUp`。`7425901f5` 中的 path 分流部分已回滚（Support/CouponStrategy/枚举/分发重载），**活动形式判定与 validate 分支保留** |
| T-07 | 三者交集同源实现 + 预警按券口径 + C 端样式分流 | 已完成 | — | product-server `c85438f92`；交集按「年级+学科」**成对**判定 |
| T-08 | 券列表 Apollo mock（解除电商接口阻塞） | 已完成 | — | student-center `b3efe04d3`；`pre.order.coupon.mock.enabled` |
| T-09 | 券适用范围表名加 `renewal_` 前缀 | 已完成 | — | product-server `1716371b2`；马胜建表时改的名 |
| T-10 | `process/list` 出参补 `activityType` 区分订金班/膨胀券 | 已完成 | — | product-server `566380d4e`；复用已有活动详情，零额外 RPC |
| T-11 | 测试环境建表 + 插 scope 测试数据 | 已完成 | — | `gaotu_polar_test_03`(cluster 142)；5 行数据，验过唯一键两个方向 |
| T-12 | 五个仓库编译验证 | 已完成 | — | 全部 BUILD SUCCESS |
| T-13 | 单测 + 功能自测 | 进行中 | — | **B 端 detail 回显、C 端 scopes、couponStatusDesc 三处新代码单测已补齐**（T-29）；其余模块(order/cart 下单算价等)尚未补单测，功能自测详见 [[verify]] |
| T-17 | 配置并发布 Apollo（mock 开关 + 券商品类型） | 已完成 | — | default cluster，release `20260908171459` |
| T-18 | cart 补齐 DTO 券字段 + 修正为成对求交 | 已完成 | — | 原按年级/学科分别求交，会放行伪命中；已删 `intersect()` helper |
| T-14 | cart 侧三处静默失败改抛异常 | 已完成 | — | `PreRegistrationCouponAssembler`：price/scopes/deductibleAmount 取不到不再返 0/空，改抛 `CommonsException`；编译通过 |
| T-15 | 静态自测：三者交集算法走查 | 已完成 | — | 成对判定确认正确，未发现 bug；5 行真实数据推演 3 场景符合预期 |
| T-16 | 四服务部署到 test-gtbg-dev-3 + 反射桥全部打通 | 已完成 | — | student-center/promotion/cart/product-b 四个桥均实测 code:0 |
| T-19 | 迁 AclServiceCompareController 到三仓库 | 已完成 | — | 三份逐字节相同、自带 RVO 内部类；cart 放行拦截器、B 侧加挂 /b 路径 |
| T-20 | 建 type=2 膨胀券活动并发布 | 已完成 | — | `578363764011708416`，挂 801400001/2 两张券 |
| T-21 | 券状态文案 `couponStatusDesc` 全链路补齐，文案权威源交给电商 | 已完成 | — | promotion `f7cd4dce2` / product-server `9626a3026` / cart `a7646b67` / student-center `35462c689`；四仓编译全绿 |
| T-22 | 券状态枚举按电商 coupon-a 定稿重写 + mock 改用电商真实字段名 | 已完成 | — | student-center `d8c7fb9cd` / promotion `3071f7335` / product-server `417bf0cb2`；**`COUPON_STATUS_IN_USE` 2→1 是资损向修复**；mock 补至 4 条覆盖四状态 |
| T-23 | 下线全部 mock，ACL 直连电商 coupon-a + 三服务上泳道验证 | 已完成 | — | student-center `49a8c97ad` / promotion `3b9f24af5`；三服务 eureka UP，券列表实测 total=56 真数据 |
| T-24 | promotion-management 补齐券字段透传 + 详情回显 + 修 detail NPE | 已完成 | — | `961cb892`；修掉 traceId `f346c23d`(scopes 被丢弃) 与 `c7d123cc`(detail NPE) |
| T-25 | 券范围落库：promotion-b 事务内回调 product-b 新增的只写接口 | 已完成 | — | product-server `86abd8914` / promotion `10a43258a`；事务内调用，Feign 失败即回滚活动 |
| T-26 | 修 B 端 detail 券字段全空：`PreOrderCouponEnricher` 加 `enrichDTO` 挂到 `detail()` | 已完成 | — | promotion `81180aa45`；用真实电商券重建活动实测通过，`couponId/couponName/couponStatus/buyAmount/skuId` 全部正确回显 |
| T-27 | C 端 listFromCache 补齐 scopes：product-server 新增批量查询 Feign + promotion 消费 | 已完成 | — | product-server `846a532ab` / promotion `7be4676b0`；测 cart 推荐接口时子 agent 发现的新缺口；中途踩了嵌套 Map 解码坑、RestTraceResponse 信封坑、promotion-b/promotion-c 双部署坑，见 [[apis]]；cart `preRegistration` 反射调用 `code:0` 实测通过 |
| T-28 | `couponStatusDesc` 本地映射（永久方案，电商邓俊兵确认不会下发） | 已完成 | — | student-center `daa8c8516` / promotion `1083c43cf`；已部署到 test-gtbg-dev-3 并实测(`coupon_status_desc: "使用中"`) |
| T-29 | 补单测：`PreOrderCouponEnricher`/`fillCouponScopes`/`PreOrderCouponStatusEnum`/`listScopesByActivities` | 已完成 | — | promotion `83fec5087`(17 个测试方法) / student-center `c777976d9`(12 个) / product-server `c0a448b57`(8 个)；3 个 subagent 并行编写，主会话逐一读过源码确认质量后提交。⚠️ **2026-09-10 更正**：product-server 那 8 个当时其实**编译不过、从未运行**（误用老版 assertj 没有的 `anySatisfy`/`noneMatch`，且连带整个 domain 模块 test 编译失败），已在 T-32 修好，现 8/8 通过 |
| T-30 | C 端三者交集精确匹配 —— 用真实数据端到端验证 | 已完成 | — | 直连 DB 造了一套年级学科真正匹配的数据（续班计划改指向真实券活动、目标年级学科对齐券范围），反射调 `preRegistration` 返回完整正确的推荐商品，详见 [[verify]] |
| T-31 | 验证 `postProductId`/`postProductName`/`activityType`（预报名预警列表）字段真实可用 | 已完成 | — | 用户要求核实这三个字段是不是本次改过。查 git log 确认未改动（T-07/T-10 的老字段）；测试环境该列表原本查不到数据，直连插了一行 `questionnaire_inspect` 后调真实接口，`postProductId`/`postProductName` 由「前置班→后置班」推荐逻辑真实查出，非编造值，详见 [[verify]] |
| T-32 | B 端下单弹窗膨胀券 tab：券列表按三者交集过滤 | 已完成 | — | product-server `1de4533b9` / student-center `abe8a067d`（初版 `974b669a5` + 2 个联调修复）。product-server 新增 `PreOrderDisplayableCouponService` + feign 出口 `listDisplayableByRenewalPlan`（交集全部委托 `PreOrderCouponIntersectService`，不重算）；student-center `/renewal/pre/coupon/list` 入参加可选 `renewMasterNumber`，传了才过滤。**tab 一直展示不做校验**（口径反转，见 [[changelog]] 09-10）。顺带修复分支上 `c0a448b57` 带的单测用了老版 assertj 不支持的 `anySatisfy`/`noneMatch`、一直编译不过卡死整个 domain 模块 test 编译。单测 product-server 8/8、student-center 5/5。**2026-09-10 已发 test-gtbg-dev-3 端到端实测通过**（6 条用例全绿，含「同 3 张券加计划号只剩 1 张」的交集语义验证，见 [[verify]]）。联调期修掉 3 个 bug：feign 服务名错(`c92abfca4`)、解码器注解族错→`data:[{}]`(`abe8a067d`)、以及上面 T-29 那个从未运行的单测 |

| T-33 | 券选品列表补「预报名可用范围」与「单人持有上限」，并双端拦截售罄券 | 进行中 | — | student-center `c92427fd8`（前两个字段 `e5d9a817c`/`619aa6564`）、promotion `2aee304de`。① `availableScope`：三者交集结果里本就带命中的年级学科，此前在 ACL 层被去重成券商品ID时丢了，改为透传扁平行、Biz 层按券聚合成文案（同券多组合用「、」连接，`LinkedHashSet` 保序避免文案抖动）；② `holdLimit`：电商 `ExpandCouponDetailDto` 本就有，透传即可；③ **售罄双端拦截** —— student-center 列表 `selectable` 置 false（与有没有续班计划无关）、promotion `edit`/`editAndPublish` 服务端拦截（置灰只是前端提示，绕过照样能提交）。前两个字段已实测通过（`availableScope` 3 张券年级学科与页面逐条一致、`holdLimit:1`）；**售罄拦截仅单测覆盖**（`efa4b13fc`，售罄/超卖/未售罄/数量缺失 4 条，共 10/10 通过）——环境里没有真正售罄的券，**且踩到 OES 页面「已售/总量」列不是电商真值这个坑**（详见 [[verify]]），端到端待造数后补验 |

### T-13 自测进展

**当前状态**：B 端券选品、B 端 detail 回显、C 端 scopes、C 端三者交集、预警列表字段
**全部真实数据端到端实测通过**（清单与命令见 [[verify]]「已验证清单」）。
新代码（T-26/T-27/T-28）单测已补（T-29）；T-32 的范围过滤单测已补；order/cart 下单算价等历史模块仍无单测。

**中间踩过的两个坑**（结论已进 [[README]]「必须知道的坑」，过程见 [[changelog]] 09-08）：
把「Apollo 查泳道 cluster 404」误判成环境不可用（实际读不到会回落 default）；
查 pod 的时刻早于用户发布镜像的时刻。

### T-04 order 侧范围收敛（重要）

初版做多了（券订单事件消息、批量下单校验、满赠剔券共 327 行），已 revert。
**order 侧我们只负责「膨胀券商品能加购」+ 购物车总价**，下单、支付成功、退款由订单团队自行兼容，
student-data 收数也由订单侧现有消息覆盖。

## R- 反讲整改项

> 来源：飞书待办表「技术反讲」阶段的 TODO 项（**那张表才是真相源**）。
> **上线前必须全部闭环。**

| 编号 | 整改项 | 谁提的 | 状态 | 备注 |
|---|---|---|---|---|
| R-01 | 一个膨胀券只能在一个活动中用么？ | 王永诗 | 已完成 | 王永诗确认：一张券可以跨多个活动用；同一活动内配置的「年级+学科」组合不能有交集（即活动内唯一，不是分别检查年级集合/学科集合）。与现有实现（`uk_act_grade_subject` 活动内唯一、跨活动放行）完全一致，**不用改代码** |
| R-02 | 测试冲突问题 | — | 已取消 | 含义始终不清楚，用户决定不用管，不再跟进 |

## C- case 联调问题

> 来源：case 评审后按 case 联调发现的问题。**提测前必须清完。**

| 编号 | 问题 | 对应 case | 状态 | 备注 |
|---|---|---|---|---|
| — | 尚未进入 case 阶段 | — | — | |

## 阻塞详情

R-01、R-02 均已闭环，当前无阻塞项。

## 开发期新增待确认项（需反讲/前端/电商定稿）

这些是写代码时冒出来的，**不在原待办表里**。

**已解决（5 条）**：电商券接口已接通并删 mock ✅ · 券状态码定稿 1/2/3/4 ✅ ·
`scopes` 落 product-server、promotion 跨服务查 ✅ · `postProductId`/`postProductName`/`activityType`
验证为老字段无需改动 ✅ · `couponStatusDesc` 本地映射为永久方案 ✅（详见 [[README]]「已定共识」）

**未定（4 条）**：

| # | 待确认 | 影响 | 现状处理 |
|---|---|---|---|
| 5 | `showDiscountAmount` 膨胀券口径 | 展示逻辑 | 暂定「任一张券抵扣金额>0 即展示」 |
| 6 | 膨胀券专属背景图 | C 端样式 | Apollo `renewal.cStyle.preRegistrationCoupon.bgUrl`，暂用订金班同一张 |
| 7 | 膨胀券 reportCode 取值 | Apollo 内容配置，**不配则老师端无入口** | 暂写 `pre_registration_coupon_link` |
| 8 | promotion 侧「按 renewalNumber 查活动」入口不存在 | 活动形式判定 | Adapter 占位签名；可用 Apollo 白名单强制判定自测 |

## 非本次范围（记着别忘）

- **历史预报名活动统一刷成订金班预报名** —— 马胜，**待上线后统一处理**，不在本次开发内
