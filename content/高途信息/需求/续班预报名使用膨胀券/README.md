---
title: 续班预报名使用膨胀券
aliases:
  - 【续班】预报名使用膨胀劵
  - 【预报名】预报名支持膨胀劵
  - 004-xuban-pre
status: 开发中
owner: zhangzeling
branches:
  - promotion:feature-xuban-pre
  - promotion-app:feature-xuban-pre
  - product-server:feature-xuban-pre
  - order:feature-xuban-pre
  - cart:feature-xuban-pre
  - student-center:feature-xuban-pre
  - promotion-management:feature-xuban-pre
updated: 2026-09-11
tags:
  - 需求
---

# 续班预报名使用膨胀券

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 任务板]] · [[changelog|📜 会话日志]] · [[apis|🔌 接口台账]] · [[verify|🧪 验证手册]] · `apifox-openapi.json`(导 Apifox)
> 技术方案在飞书反讲文档里（见 [[links]]），本地不留副本。
> 续接这个需求：读完本文件即可。

## 一句话

在现有「订金班预报名」之外新增一种**膨胀券预报名**形态：活动挂膨胀券商品，学员购券即完成预报名，无需进班。

## 需求摘要

> 飞书文档只存链接不落全文，这里是唯一的离线兜底。

- **要解决的问题**：现有预报名只支持「订金班」（挂预报名班级课程商品、付订金占位、可见范围读可续关系）。
  本次新增「膨胀券」形态 —— 活动挂膨胀券商品，学员购券（如付 50 抵 200），**购券即预报名**。
- **给谁用**：老师（花名册发链接 / 下单弹窗加购）、学员（C 端落地页选券）、运营（配置活动与券范围）。
- **两种形态的可见范围口径完全不同**（最容易搞错的地方）：订金班读**可续关系**；膨胀券读**券上配置的年级+学科**，不读可续关系。
- **核心改动**（6 个模块，跨 6 个仓库）：配置（product-server/promotion）、发链接（student-center）、
  B 端下单（product-server/order）、C 端落地页（cart）、字段与指标（student-data，**归马胜**）、预报名预警。
- **判定做完的标准**：六个模块端到端跑通；学员购券后由**券订单消息**驱动落库预报名状态与科目（不需进班）。
- **明确不做**：C 端过滤不沿用老那套；优惠金额展示走统一逻辑、不做配置。

## 已定共识（硬约束，改代码前先扫一眼）

- **`productType` = 8014**。⚠️ 不是 8027 —— 8027 是「课时包商品」，student-center 与 promotion-app 均已占用；也不要用 27（老优惠券概念）。
- **券范围唯一键 = 活动级** `uk_act_grade_subject(activity_number, grade_code, subject_code)`：
  同一活动内「年级+学科」只能出现一次；**同一张券的同一组合在不同活动可各配一次 → 跨活动重复必须放行**（误拦是回归项）。
- **券不参与满赠**（2026-09-08 产品确认），且 promotion-app 本期不改。
- **order 侧只做「膨胀券商品能加购」+ 购物车总价**，下单/支付成功/退款由订单团队自行兼容。
- **除 student-data 外，6 个仓库全是我的活**（含 promotion/promotion-app/order/cart/product-server）。
  反讲文档「项目关联方」写「待定」指的是对方服务对接人待定，**不是这活不是我的**。
- 灰度按**续班计划 ID**；用**膨胀券商品ID**；C 端一券只能买一次、页面多选；加购上限来源=电商接口。
- **券范围落库链路 = promotion-b 事务内回调 product-b**（2026-09-09 定）：
  表留在 gaotu 库不动；promotion-b 落完活动后调 product-b 的
  `POST /feign/preOrderActivity/couponScope/save`（**只写表、不调下游**，避免循环调用），
  调用放在 `@Transactional` 内，Feign 失败即回滚活动。**前端不用改**。
- **券信息全部实时取电商，不落库不做 mock**（2026-09-09）：ACL 直连
  `coupon-a` 的 `/feign/expandCoupon/queryList`。**mock 已全部删除**，
  也不做「真接口失败回落 mock」——会掩盖真实故障。
- 🔴 **券状态枚举 = 电商 coupon-a 口径**：**1 使用中 / 2 已失效 / 3 审核中**
  （2026-09-09 定稿四个值，**09-11 随 jar 升 1.3.17 删掉「4 已暂停」**）。
  **没有「待开始」**（售卖期由 `saleStartTime`/`saleEndTime` 表达）。**只有【1 使用中】可勾选**。
  权威源：jar `com.gaotu:coupon-a-client:1.3.17` 的 `ExpandCouponDetailDto#couponStatus`
  （`POST /feign/expandCoupon/queryList`，青舟 interfaceId=5453936）。
- 🔴 **`saleStatus` 是第二个状态维度**（1.3.17 新增）：券**商品**售卖状态 1 停售中 / 2 开售中，
  平台券为空。与 `couponStatus` 正交，**`selectable` 要两者都满足**；为空时不改判。
- 🔴 **`couponStatusDesc` 文案由我们本地维护，是最终方案不是过渡**（2026-09-09 电商邓俊兵确认
  「中文展示逻辑你们按需判断展示就行」，即电商不会下发此字段）。已实现，**不用再找电商推动**。
- 🔴 **B 端下单弹窗膨胀券 tab「一直展示」，不做灰度、不做显隐校验**（2026-09-10 用户定稿）。
  续班计划没配膨胀券时**点进去没数据**（列表空），不是把 tab 藏起来。
  ⚠️ 需求截图里王永诗 09-03 答的「不配膨胀券不展示」**已被推翻**，别再照它加 `showCouponTab`
  之类的显隐字段（试写过一次已 revert，见 [[changelog]] 09-10 第七轮）。
- **券列表的范围过滤入口 = `/renewal/pre/coupon/list` 的可选入参 `renewMasterNumber`**：
  传了才按三者交集过滤，不传不过滤（运营纯券搜索 / 详情页复用同一接口，存量行为不能变）。
  交集**只在 product-server 算**（`listDisplayableByRenewalPlan`），student-center 不重算。
- 三者交集 = 前置班学科 ∩ 后置班年级学科 ∩ 券配置范围，且仅【使用中】。**按「年级+学科」成对判定**，
  分别求交会放行「年级来自A组合、学科来自B组合」的伪命中。

## 核心概念（续接必读，比代码更容易搞混）

### 券ID vs 券商品ID —— 两个不同的 ID，别混用

来自电商 `ExpandCouponDetailDto`（jar `com.gaotu:coupon-a-client:1.3.15`）：

| 字段 | 中文 | 是什么 | 举例 |
|---|---|---|---|
| `couponNumber` | **券ID** | 这张券的「定义」本身的身份证，主要用于展示"这是哪张券"、查状态 | `578534533350174720` |
| `skuNumber` | **券商品ID** | 这张券对应的**可购买商品 SKU**，真正用来加购/下单/挂在活动商品行上 | `578534533488603137` |

我们系统里活动商品行的 `productNumber` 字段，存的**是券商品ID(`skuNumber`)，不是券ID**——因为这一行代表"能被购买的商品"，必须是 SKU。券ID(`couponNumber`)只是附带信息，存在同一行的 `couponId` 字段里，给页面显示用，不参与加购/下单。

`skuId` 字段和 `productNumber` 其实是同一个值（都是 skuNumber）——历史上有人想把它单独存一列，已 revert（见下方「必须知道的坑」），`productNumber` 本身已经是券商品ID，不需要重复存。

### 推荐流程：一个接口，两条完全不同的分支

C 端 `GET /web/renewal/preRegistration`（`cart` 的 `RegistrationService#preRegistration`）给学员推荐"要买的商品"，参数是 `renewalNumber`（续班计划号）+ `preClazzNumber`（前置班/学员当前所在班）。**这是同一个接口内部按 `activity.type` 分岔，不是两个接口**：

1. 用 `renewalNumber` 查续班计划，拿到关联的预报名活动号，再调 promotion 的 `listFromCache` 拿活动详情（含 `type`：1=订金班/2=膨胀券）
2. 校验学员是否命中活动（未开始查白名单、命中判断等）
3. **按 `type` 分岔**：
   - **`type=1` 订金班**（老逻辑，不变）：商品行的 `productNumber` 是**班级号**，拿 `preClazzNumber` 查课程中心，按年级/部门匹配活动下的班级，价格取班级自己的价格
   - **`type=2` 膨胀券**（新逻辑）：商品行的 `productNumber` 是**券商品ID**，没法查班级，走**三者交集**——
     ① 续班计划的目标年级学科（近似"后置班"范围，`courseGradeList`/`courseSubjectList`）
     ② 每张券配置的可用范围 `scopes`（来自 product-server 的 scope 表，这几轮一直在修的字段）
     ③ 两者按「年级+学科」**成对**判定交集（不能拆成两个集合分别判断，否则会放行「年级来自 A、学科来自 B」的伪命中）
     交上的券才展示，价格取券的购买金额，抵扣金额取券的抵扣金额，"是否已购买"按券商品号查订单
4. 两条分支最后都组装成同一套 `RegistrationProductVO` 返回给前端——**字段名相同但语义不同**（`productNumber` 订金班是班级号/膨胀券是券商品ID），这是最容易踩的坑，写错编译不报错，只会运行时静默查不到。

## 现在什么情况

| | |
|---|---|
| 阶段 | 开发中（**B 端下单弹窗膨胀券 tab 券范围过滤已端到端实测通过**）|
| 进度 | T 32/32 · R 0/2 · C 0/0 |
| 排期 | 09-08~09-11 开发 · 09-14 自测 · 09-15~16 联调 · **提测 09-16** |
| 当前卡点 | 🟢 无阻塞。T-32 已端到端实测通过（6 条用例全绿，见 [[verify]]）。<br>🟡 **T-33 售罄拦截待实测**：`availableScope`/`holdLimit` 已实测通过，**售罄拦截刚发布未验**（可用截图里 10/10 那张 `578845069455599617` 做数据）。<br>🟡 **遗留（非阻塞）**：电商 `couponName` 只支持左匹配，中间词搜不到，需跨团队推动，见 [[apis]]「已知契约缺口」。<br>🔴 **上线前必查**：`promotion` 有 `promotion-b`/`promotion-c` 两个独立部署，改动涉及 C 端链路时**两个都要发布** |
| 最近更新 | 2026-09-11（券选品列表补 `availableScope`/`holdLimit`；售罄券双端拦截）

**六仓库代码编译全绿（BUILD SUCCESS）、全部已 push**。
T-32 单测：product-server 16/16、student-center 16/16 通过；端到端 6 条用例全绿。
⚠️ `GradientAndDiscountTraceStrategyTest` 有 1 条失败，**stash 掉本次改动后同样失败，
是分支上原有问题，与本需求无关**，未处理。

| 仓库 | 最新 commit |
|---|---|
| student-center | `100c7abe9`（09-11：可用范围/持有上限文案/售罄置灰/jar 1.3.17 + saleStatus）|
| product-server | `1de4533b9`（含单测） |
| promotion | `30b1f5509`（09-11：售罄 + 满班拦截 + jar 1.3.17。⚠️ **只发了 promotion-b，promotion-c 未发**——本次改的是 B 端写链路校验，不涉及 C 端） |
| promotion-management | `961cb892` |
| order | `073dea69e2` |
| cart | `a7646b67` |
| promotion-app | 仅 spec（本期不改代码） |

## 下一步

> 只列还没做的。做完的已删（历史见 [[changelog]]）。

1. **验「卖不出去的不许进活动」两条校验**（T-33/T-34，均已发布、仅单测覆盖）：
   - **膨胀券售罄** —— 卡在没有售罄券：需造 `sold_count >= total_amount` 且 `coupon_status=1` 的券。
     ⚠️ 别拿 OES 页面「已售/总量」列当依据，它读 promotion 缓存不是电商实时值
     （实测页面显示 10/10 的券，电商真值 `sold_count=0` 且状态已失效）→ 见 [[verify]]。
   - **订金班满班** —— 需造 `signUpCount >= capacity` 且 `capacity > 0` 的班级。
     ⚠️ 测试环境大量班级是「不限制」（`capacity=-1`），这些**必须能正常保存**，也要一并回归。
2. **复验 `holdLimit`** 现在返回的是文案（不限→「不限」）而非数字。
3. 🔴 **改动涉及 C 端链路时 `promotion-b` 和 `promotion-c` 两个部署都要发布** ——
   只发 b、用反射桥验证通过≠cart 端到端通了（见下方坑位）。
4. 上线前：三处 `AclServiceCompareController.enabled` 显式配 `false`、
   线上建表、5 个 Apollo key、2 个代课接口权限登记（明细见 [[verify]]「新建的东西」）。
5. R-01/R-02 已闭环。

## 待确认

> 真相源是飞书待办表，这里是镜像。开发期新增的 9 条见 [[tasks]] 末尾。

- [x] ~~一个膨胀券只能在一个活动中用么？~~ **王永诗已确认**：一张券可跨多活动用；同一活动内配置的「年级+学科」组合不能有交集（活动内唯一，不是分别检查年级集合/学科集合）——与现有实现完全一致，不用改代码
- [x] ~~测试冲突问题~~ **已取消**：含义始终不清楚，决定不再跟进
- [ ] 一个前置班级只能在一个续班计划上，但班级可脱离续班计划配置，如何控制 —— 无处理人
- [ ] 新续班计划配置的预报名活动 vs 老的非续班计划配置并存，是否并集 —— 等马胜
- [ ] 历史预报名活动统一刷成订金班预报名 —— 等马胜（**待上线后处理**，不在本次开发内）

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/student-center | feature-xuban-pre | 券选品接口 `PreOrderCouponController#listCoupon`/`PreOrderCouponBiz#listCoupon`（含按 `renewMasterNumber` 的范围过滤）、`PreOrderCouponScopeAclService`、发链接分流 `PreOrderActivityFormResolver` |
| /Users/gaotu/IdeaProjects/JavaProject/product-server | feature-xuban-pre | 活动配置、券范围表、三者交集 `PreOrderCouponIntersectService`、按计划查可展示券 `PreOrderDisplayableCouponService` + `PreOrderCouponScopeFeignController`、预警 `InspectService`、C端样式 |
| /Users/gaotu/IdeaProjects/JavaProject/promotion | feature-xuban-pre | 活动形式、券可用范围、baseUrl 分叉 |
| /Users/gaotu/IdeaProjects/JavaProject/promotion-management | feature-xuban-pre | **B 端页面的真正入口**（OES→它→promotion-b）。`PreOrderActivityProductEditReq` 透传券字段、`PreOrderActivityDomainServiceImpl#detail` 判空 |
| /Users/gaotu/IdeaProjects/JavaProject/order | feature-xuban-pre | 仅加购 + 购物车总价 |
| /Users/gaotu/IdeaProjects/JavaProject/cart | feature-xuban-pre | C 端落地页取数与算价 |
| /Users/gaotu/IdeaProjects/JavaProject/promotion-app | feature-xuban-pre | 仅 spec；满赠校验在此服务，本期不改 |
| student-data | — | **不要动**，B 端收数归马胜 |

## 上线影响面

> 新建的表 / Apollo key / 代课权限逐项清单 → **见 [[verify]] 末尾「新建的东西」**（那份是上线 checklist 的原料）。

| 配置项 | 涉及 |
|---|---|
| MySQL DDL | ✅ 一张新表，测试已建、线上待建。⚠️ `pre_order_activity_product` **不加列**（工单 8025 已撤） |
| Apollo | ✅ 5 个 key，其中 `renewal.content.config.map` **不配则老师端无入口** |
| 代课接口权限 | ✅ 2 个新接口待登记 |
| **反射桥开关** | 🚨 **promotion / cart / product-server 三处 `AclServiceCompareController.enabled` 线上必须显式配 `false`**（代码默认 true，不配=开启）→ 见 [[verify]] |
| MQ | ❌ 券订单消息由订单团队发 |
| ES | ❌ 写 ES 归马胜 |

> ⚠️ **两个 Apollo key 不要新增**：`gaotu.website.preRegistrationCouponUrl`(promotion) 与
> `renewal.content.config.preRegistration.coupon.path`(student-center) —— 落地页 path 分叉已撤销、
> 代码里已经没有它们了；触达后台 `report_content` 的 url 模板必须写 `/preSignUp`。

> ⚠️ **mock 已全部删除**（2026-09-09 起券信息全部实时取电商），`pre.order.coupon.mock.enabled`
> 这类 mock 开关**已不存在于代码里**，上线不用管它——如果哪份旧文档还提这个开关，那份是过时的。

## 必须知道的坑

> 只留「不知道就会走错路」的，每条一句结论 + 一句判据。调查过程见 [[changelog]]。

**ID / 枚举**
- **膨胀券 `productType` = 8014**。8027 是课时包商品（两个仓库都已占用），27 是老优惠券概念。
- **券状态 = 电商口径，`1 使用中 / 2 已失效 / 3 审核中`，没有「待开始」**。
  ⚠️ **1.3.17 起「4 已暂停」也被电商删了**（本地枚举已同步删 `PAUSED`）。
  这个值错过三次（1→2→1，再删 4）。**2 是已失效**，停在 2 会把失效券当可用券放行，是资损方向。
  判据只认 `coupon-a-client` jar 的 `ExpandCouponDetailDto`，别信任何本地文档旧表述。
- **`couponStatusDesc` 由我们本地维护，是永久方案**（电商邓俊兵确认不会下发此字段）。
  已实现 `PreOrderCouponStatusEnum.descOfStatus()` / `PreOrderCouponEnricher.descOfCouponStatus()`。
  ⚠️ 教训：「权威源在下游、等下游提供」这类设计，一开始就要问清「你们会不会下发」，否则会死等。
- ❌ ~~**coupon-a 测试环境券 SKU 会滚动重新生成**~~ —— **2026-09-10 证伪，别再信这条**。
  实测旧 sku `578513860277893121`（曾被判定"已过期"）与 `578534533488603137` **两张都还在**，
  只是恰好都叫「木7」（相隔 3 小时建的两张不同券）。当初"查不到"的真因是下面这条 snake_case bug：
  筛选条件被电商静默忽略 → 只返回全量第一页 → 目标券不在第一页就 miss。
  **新建的券恰好排在第一页，所以"换张新券重测就好了"，这才造出"旧 sku 失效"的错觉。**
- 🔥 **调电商 coupon-a 的请求体会被序列化成 snake_case，筛选条件静默失效**（2026-09-10 修复）。
  `SuperSpringConfig` 把 FastJson **全局**命名策略设为 `SnakeCase`（promotion 对外 API 口径，不能动），
  该全局实例同样作用于 Feign 请求体；jar 的 `ExpandCouponQueryRequest` 又没有任何 `@JSONField`
  → 实发 `{"sku_numbers":[..],"page_num":1}`，而电商只认 `skuNumbers/pageNum/pageSize`。
  **症状极隐蔽**：未知字段被静默忽略 = 不带筛选 → HTTP 200、`list` 非空（全量第一页）→
  既不抛异常也不打「全部取不到」告警（**日志里什么都搜不到**）→ 但按 skuNumber 匹配全 miss
  → 券名/券ID/购买金额/状态恒为 null。
  修法：`CamelExpandCouponQueryRequest` 继承 jar 入参类、覆写 getter 加 `@JSONField(name=camelCase)`
  （其优先级高于全局策略）。**别改全局 SnakeCase**（波及所有对外接口）；
  **也别想换 Feign 编解码器**——jar 把 `configuration` 写死在注解上，且本仓库
  spring-cloud 是 **Edgware.SR5，`@FeignClient` 还没有 `contextId`**，同服务名重复声明会 bean 名冲突。
- 🔥 **OES 页面的「已售/总量」列不是电商真值**（2026-09-11 实测）：页面读 promotion 活动商品缓存，
  实测显示 10/10 的券，电商真值是 `sold_count=0`、`coupon_status=2`(已失效)。
  判断一张券的真实售卖/状态，**只认反射桥直查电商**（命令见 [[verify]]）。
- ❌ ~~`creator` 恒为 null 且无解~~ —— **2026-09-11 已作废**。电商 1.3.17 新增了
  `creatorEmployeeId`，已接上。⚠️ 下发的是**工号不是姓名**，页面会显示成数字；
  要显示姓名需再查员工服务（本期未做）。
- 🔴 **券有两个状态字段，别混用**（1.3.17 起）：`couponStatus` 是**券本身**是否生效
  （1 使用中 / 2 已失效 / 3 审核中），`saleStatus` 是**券商品**在不在卖（1 停售中 / 2 开售中，
  平台券为空）。一张券可以是【使用中】但商品【停售中】—— 选了也卖不出去，
  故 `selectable` 要两者都满足（再叠加售罄判定）。
- **膨胀券名称搜索只支持「左匹配」**（`like '关键字%'`，jar 注释写明）：搜「退款口径」能命中
  「退款口径膨胀券caseSDD_x」，搜「口径」「caseSDD」一律 0 条。这是电商口径，我们只透传关键字。

**部署 / 链路拓扑**
- 🔴 **`promotion` 有 `promotion-b`(`gaotu_promotion`) 和 `promotion-c`(`gaotu_promotion_c`) 两个独立部署**。
  反射桥走 b、cart 走 c → 涉及 C 端链路（`listFromCache`/`calculate`/`calculateWhite`）**两个都要发**。
  判据：`trace_tree` 里 span 的 `gapmApp`/`service` 显示是哪个部署接的请求。本次会话因此漏发过一次。
- 🔥 **B 端链路上还有 `promotion-management`**（`OES → promotion-management → promotion-b`），
  不在最初那 6 个仓库里。它是纯透传层，但 **DTO 落后于下游契约时会静默丢字段**（Jackson 忽略未知属性），
  表现是页面配了范围却报「膨胀券必须配置可用范围」，**且报错在下游、它自己日志里看不出原因**。
  下游加字段时这层必须同步加。
- 🔥 **promotion-b 只连 promotion 库，scope 表在 gaotu 库** —— `GaotuDataSourceConfig` 类名有误导性，
  它读 `jdbc.promotion.*`。所以「promotion 直接写 scope 表」做不到，必须跨服务。
- ⚠️ **别让 promotion-b 回调 product-b 的 `/b/renewal/preOrderActivity/edit`** —— 那个接口内部调
  promotion-b，会成环。必须用只写表的专用接口 `/feign/preOrderActivity/couponScope/save`。
- 🔥 **product-b 与 promotion-management 之间两个方向都无调用关系**。
  `ServiceConstant.PRODUCT_SERVICE_NAME` 有定义但无人使用，且指向商品中心≠product-b，排查时别被它误导。

**设计如此，别当 bug 去"修回"**
- **promotion 券字段不落库**，只在 Redis 缓存里 → 插 DB 造不出可用的膨胀券活动。
  别给表加券列（`product_number` 已是券商品ID、`product_type=8014` 已能区分，券名/金额/状态是
  电商权威数据，落库即脏快照）。2026-09-09 试过一次已 revert（`a620a7e2f`→`8ed5fbab1`）。
- **cart 三处抛异常**（price / scopes / deductibleAmount）：上游字段缺失时落地页直接失败是**预期行为**，
  不能静默返 0。
- **成对求交**：年级、学科必须按 `PreOrderActivityCouponScopeDTO` **整对**比对；分别求交会放行
  「年级来自 A 组合、学科来自 B 组合」的伪命中（诱发该写法的 `intersect()` helper 已删）。
- **三者交集只有 `PreOrderCouponIntersectService` 一份实现，任何新调用方都只能"取结果"**。
  它的类注释点名了三个调用方（发链接 / B 端下单弹窗券列表 / C 端落地页）。
  在别的服务里重算一遍 = 老师看到的券 ≠ 学员能买的券。
  跨服务取用走 product-b 的 `couponScope/listDisplayableByRenewalPlan`（只要续班计划号）。
- **范围过滤失败绝不能降级**：降级成"空列表"运营会误判「没配券」；
  降级成"不过滤"会把电商全量券暴露给老师（越权展示，更严重）。故 ACL 层直接抛业务异常。

- 🔥 **student-center 调 product-server 必须用 `ProductInterceptorFeignConfig`，且服务名是 `PRODUCT-B`**。
  两个都错过一次，症状都极隐蔽：
  ① 服务名写 `PRODUCT.GAOTU100.COM` → 指向 product **主部署**（我们的接口在 product-b 模块，只有
  product-b 有）→ **404**。实测主部署 404 / product-b 200。口径同 promotion 的 `PRODUCT_B_NAME`。
  ② `configuration` 用默认的 `FeignConfiguration` → 那个类**只是 RequestInterceptor 不含 decoder**，
  解码落到普通 Jackson(camelCase)，而 product-server 出参是 **snake_case** →
  **`data:[{}]`：数组长度对但每个元素是空对象**、字段全 null → 列表恒空，**不报错无异常日志**。
  `ProductInterceptorFeignConfig` 内部是 `GaotuRcpHttpMessageConverter`（继承
  `FastJsonHttpMessageConverter`），天生认 snake_case；`RenewalMasterFeignAdapter` 一直这么用。
- ⚠️ **这条链路的解码器是 FastJson，别用 Jackson 的 `@JsonProperty`** —— 标了等于没标
  （实测标完仍是 `data:[{}]`）。要显式标只能用 `@JSONField`；但正确做法是复用上面那份 config。
  **判据：看 `@FeignClient(configuration=...)` 那个类里有没有 `Decoder` bean，没有就是默认 Jackson。**
- 🔥 **`data:[{}]` 这个症状要会认**：数组长度正确 + 元素空对象 = **字段名映射错**（命名策略/注解族），
  不是"没查到数据"、也不是"没部署上"。排它的顺序：先进 pod `unzip` 验注解在不在镜像里
  （在 → 不是发布问题），再反编译那个 converter 看它是 Jackson 还是 FastJson。

**测试 / 构建**
- 🔥 **本仓库 `product-server-domain` 的 assertj 版本没有 `anySatisfy`/`noneMatch`**，
  误用会让**整个模块的 test 编译失败**（不是单个测试失败）→ 连带其他测试一个都跑不了。
  `c0a448b57` 就这么埋了一个"从未运行过"的单测，直到 09-10 才发现。
  **教训：单测提交前必须真跑一次**——`mvn compile` 过不代表 test 编译过，是两个独立阶段。
- **跑单测必须带 `-am`**：只写 `-pl <模块>` 时兄弟模块未安装进本地仓库，
  会报一堆"找不到符号/程序包不存在"，那是**假错误**，不是代码问题。
- ⚠️ **`pod_term.py` 不指定 `--pod-name` 会选错 pod**：`test-gtbg-dev-3` 里同时跑着别的分支的
  student-center（如 `feature-gps-learn-situation`）。用它验"类进没进镜像"时选错 pod 会得到
  `0` 的假结论（本次真踩到，一度以为镜像没发上去）。先 `pods --ns <泳道>` 拿到本次的 pod 名再 `--pod-name`。
- student-center 跑单测踩的两个 test 域坑（已在 `student-center-service/pom.xml` 修掉并注释）：
  mockito `core 2.23.4` 与 `junit-jupiter 3.9.0` 版本冲突（`NoSuchMethodError:
  Plugins.getMockitoLogger`）→ 一起钉 3.3.3；`log4j-slf4j-impl` 与 `log4j-to-slf4j`
  双桥接使 `@Slf4j` 类静态初始化就抛 `LoggingException` → 在 infrastructure 依赖上排掉后者。

**工具 / 环境**
- 🔥 **接外部 Feign jar 前先看它的注解是哪个包**。`coupon-a-client` 用旧包
  `spring.cloud.netflix.feign.FeignClient`，student-center 用 `spring.cloud.openfeign.FeignClient`(3.0.3) —— 不同注解类，
  `@EnableFeignClients` 只认自己那个，怎么配 basePackages 都注册不上。症状是**编译全绿但启动即挂**
  （`bean of type XxxFeignService not found`），pod 一直 Running 而 eureka 永远 None。
  解法：只复用 jar 的 DTO，接口本地重新声明。promotion 用旧包注解所以能直接用 —— **两仓不对称是版本差异，别去"统一"**。
- 🔥 **跨服务 Feign 契约两个坑，都只在有返回值的读接口上暴露**（`void` 的 `save()` 不走解码器，
  别以为「照 save() 抄」就安全）：① 嵌套 `Map<Long,Map<Long,List<..>>>` FastJson 解不出（报
  `parseLong error`）→ 改扁平 `List<Row>`；② 对端用 `RestTraceResponse<T>` 包了一层时，Feign 方法
  不能声明裸 `T`，要声明信封类型再 `.getData()`。
- 🔥 **`invoke_service` 反射桥调带 `List<Long>` 等复杂参数的方法时参数不生效**（传什么都返回同一页
  默认数据）。⚠️ **2026-09-10 更正**：原先写「是反射桥自身缺陷、真实 Feign 不受影响」，
  **后半句是错的** —— 至少对 coupon-a 这条链路，真实 Feign 同样中招，病根就是上面那条
  snake_case 序列化。当时拿反射桥的未过滤结果当证据，据此误判「券已过期」，绕了很大弯路。
  **教训：反射桥返回「像是没过滤」时，先验证真实调用，别直接归因于工具缺陷。**
- 🔥 **`baijia_invoke.py` 的 `ROUTE_MAP` 没登记 `promotion-management`**，且该仓库压根没挂反射桥
  Controller（只在 student-center/promotion/cart/product-server 四仓）→ 测它只能走真实业务接口。
  走兜底前缀被 CAS 兜底成「请重新登录」，**跟 Cookie 无关，是路由没配**。
- **Apollo 没有泳道 cluster 是正常的**，读不到会回落 `default`，别把「查泳道 cluster 404」当环境不可用。
- **泳道名不能反推逻辑环境**：`test-gtbg-dev-3` 属 **dev** 不是 test，只查 environment=test 会误判
  「该泳道没 pod」。已修进 `pod_term.py pods`。
- **青舟构建失败先分辨真假**：`Aborted by uqun`（人为/并发中止）、`JNLP4-connect failed`（agent 掉线）
  都是假失败，`errors` 数组为空；日志刷屏的「不支持的解析类型, XxxController」是 apidoc 噪音。
