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
| T-13 | 单测 + 功能自测 | 进行中 | C 端等膨胀券活动 | **B 端券列表已实测通过**，详见 [[verify]] |
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
| T-21 | 推动 promotion 券字段落库 | 待办 | **卡 promotion 团队** | 🔴 上线阻塞，表无券列、缓存 miss 即丢，详见 [[verify]] |

### T-13 自测进展（2026-09-08 订正）

> ⚠️ 本节此前记「泳道是空壳、不可用」，**该结论是错的**，已订正。
> 错因：① Apollo 查泳道 cluster 报 404 被误判成环境不可用 —— 实际 Apollo 读不到泳道会**自动回落 default**；
> ② 查 pod 的时刻早于用户发布镜像的时刻（16:37）。

**环境实际可用**：`test-gtbg-dev-3` 下 student-center pod Running / eureka UP，镜像 `feature-xuban-pre`。

**已实测通过（反射调 `PreOrderCouponBiz#listCoupon`）**：

| 场景 | 结果 |
|---|---|
| 空条件查询 | 3 条 mock 券返回 **2 条**，已结束券被默认状态过滤 ✅ |
| productType | 全部 **8014** ✅ |
| 状态文案 / 可勾选 | `使用中`/`待开始` + `selectable=true` ✅ |
| 券名模糊「秋季」 | 精确命中 1 条 ✅ |
| `couponIdList` 批量精确 | ✅ |

**C 端仍跑不通，但原因不是环境**：`promotion.pre_order_activity` 里现存活动**全部 type=1 订金班**，
没有 type=2 膨胀券活动；且 scope 表的 activity_number(9001/9002/9003) 是造的假号，与真实活动对不上。
→ 需先在 B 端建一个膨胀券活动并配券范围，见 README 下一步 #1。

### T-04 order 侧范围收敛（重要）

初版做多了（券订单事件消息、批量下单校验、满赠剔券共 327 行），已 revert。
**order 侧我们只负责「膨胀券商品能加购」+ 购物车总价**，下单、支付成功、退款由订单团队自行兼容，
student-data 收数也由订单侧现有消息覆盖。

## R- 反讲整改项

> 来源：飞书待办表「技术反讲」阶段的 TODO 项（**那张表才是真相源**）。
> **上线前必须全部闭环。**

| 编号 | 整改项 | 谁提的 | 状态 | 备注 |
|---|---|---|---|---|
| R-01 | 一个膨胀券只能在一个活动中用么？ | 王永诗 | 阻塞 | 等王永诗答复 |
| R-02 | 测试冲突问题 | — | 阻塞 | 未指派，含义待明确 |

## C- case 联调问题

> 来源：case 评审后按 case 联调发现的问题。**提测前必须清完。**

| 编号 | 问题 | 对应 case | 状态 | 备注 |
|---|---|---|---|---|
| — | 尚未进入 case 阶段 | — | — | |

## 阻塞详情

### R-01 一个膨胀券只能在一个活动中用么？
- **卡在**：王永诗（待办表里的处理人）
- **需要谁**：王永诗给结论
- **为什么重要**：直接决定券↔活动是一对多还是一对一，影响配置模块的数据模型与校验
- **可以先做**：按「一券一活动」保守假设梳理配置模块，结论回来再调整

### R-02 测试冲突问题
- **卡在**：无处理人，**含义本身不清楚**
- **需要谁**：先找提出人问清楚指的是什么（多人共用测试环境？测试数据冲突？）
- **可以先做**：无 —— 得先问清楚才能判断

## 开发期新增待确认项（需反讲/前端/电商定稿）

这些是写代码时冒出来的，**不在原待办表里**，定稿前代码里都是暂定值或 TODO：

| # | 待确认 | 影响 | 现状处理 |
|---|---|---|---|
| 1 | ~~电商券商品接口未提供~~ **已接通** | — | ✅ **2026-09-09 已接真实 Feign 并删除全部 mock**，泳道实测返回 56 条真数据 |
| 2 | ~~券状态码取值~~ **已定稿**：1 使用中 / 2 已失效 / 3 审核中 / 4 已暂停 | — | ✅ 三仓已对齐，`COUPON_STATUS_IN_USE`=1；文案 mock 阶段本地按码补，真接口以电商为准 |
| 3 | `scopes` 落库方是 product-server 还是 promotion | promotion 侧回显会丢券字段 | 按 product-server 落库实现；scope 表已有回查方法 |
| 4 | 两列字段名 `postProductId`/`postProductName`、`activityType` | 前端按名取值 | 后端已起名，需前端对齐 |
| 5 | `showDiscountAmount` 膨胀券口径 | 展示逻辑 | 暂定「任一张券抵扣金额>0 即展示」 |
| 6 | 膨胀券专属背景图 | C 端样式 | Apollo `renewal.cStyle.preRegistrationCoupon.bgUrl`，暂用订金班同一张 |
| 7 | 膨胀券 reportCode 取值 | Apollo 内容配置，不配则老师端无入口 | 暂写 `pre_registration_coupon_link` |
| 8 | promotion 侧「按 renewalNumber 查活动」入口不存在 | 活动形式判定 | Adapter 占位签名；可用 Apollo 白名单强制判定自测 |
| 9 | 🔴 **电商不下发 `couponStatusDesc`** | 前端拿不到券状态文案（现恒为 null） | 按定的口径「不做本地兜底」，需产品决策：推电商补字段 or 改口径允许本地翻译 |

## 非本次范围（记着别忘）

- **历史预报名活动统一刷成订金班预报名** —— 马胜，**待上线后统一处理**，不在本次开发内
