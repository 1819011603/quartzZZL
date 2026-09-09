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
updated: 2026-09-09
tags:
  - 需求
---

# 续班预报名使用膨胀券

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 任务板]] · [[changelog|📜 会话日志]] · [[apis|🔌 接口台账]] · [[verify|🧪 验证手册]] · [[curl|🌐 自测 cURL 集]] · `apifox-openapi.json`(导 Apifox)
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
- 🔴 **券状态枚举 = 电商 coupon-a 口径（2026-09-09 定稿）**：
  **1 使用中 / 2 已失效 / 3 已审核中 / 4 已暂停**，**没有「待开始」**。
  来源 jar `com.gaotu:coupon-a-client:1.3.15` 的 `ExpandCouponDetailDto#couponStatus`
  （接口 `POST /feign/expandCoupon/queryList`，青舟 interfaceId=5453936）。
  **只有【1 使用中】可勾选**。`COUPON_STATUS_IN_USE` 已 2→1。
- 🔴 **`couponStatusDesc` 文案本地维护是最终方案，不是临时过渡**（2026-09-09 晚间与电商
  邓俊兵在群里对齐并确认，附截图证据：`@ApiModelProperty("券状态: 1 使用中 / 2 已失效 /
  3 审核中 / 4 已暂停")`，与反编译 jar 看到的注释完全一致）——**电商原话"中文展示逻辑，
  你们按需判断展示就行"，即电商不会再下发 `couponStatusDesc` 这个字段，映射永久由我们维护**。
  之前"权威源在电商、等电商下发"的说法是错的，已作废。已实现：student-center
  `PreOrderCouponStatusEnum.descOfStatus()`；promotion `PreOrderCouponEnricher.descOfCouponStatus()`
  （B 端/C 端两条链路都补）。**不用再找电商推动这件事，这条待办已关闭。**
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

`skuId` 字段和 `productNumber` 其实是同一个值（都是 skuNumber）——历史上有人想把它单独存一列，已 revert（见下方「必须知过的坑」），`productNumber` 本身已经是券商品ID，不需要重复存。

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
| 阶段 | 开发中（**B 端 detail 回显、C 端 scopes 缺口均已修复并端到端实测通过**） |
| 进度 | T 27/27 · R 0/2 · C 0/0 |
| 排期 | 09-08~09-11 开发 · 09-14 自测 · 09-15~16 联调 · **提测 09-16** |
| 当前卡点 | 🟢 B 端 detail 回显、C 端 scopes、`couponStatusDesc` 文案、**C 端三者交集精确匹配**均**已端到端实测通过**（见 [[apis]]、[[verify]]）。<br>🔴 **上线前必查**：`promotion` 在这个环境有 `promotion-b`/`promotion-c` 两个独立部署，改动涉及 C 端链路时**两个都要发布**，本次会话因此漏发过一次 promotion-c，详见下方「必须知过的坑」 |
| 最近更新 | 2026-09-09

**六仓库代码全部提交并推送，编译全绿（BUILD SUCCESS）**。今天新增/改动的代码
（B 端 detail 回显、C 端 scopes、couponStatusDesc 本地映射）已补单测，其余历史代码仍未写单测。

| 仓库 | 最新 commit |
|---|---|
| student-center | `c777976d9`（含单测） |
| product-server | `c0a448b57`（含单测） |
| promotion | `83fec5087`（含单测；promotion-b **和** promotion-c 都需要发布这个 commit） |
| promotion-management | `961cb892` |
| order | `073dea69e2` |
| cart | `a7646b67` |
| promotion-app | 仅 spec（本期不改代码） |

## 下一步

1. detail 回显、券选品查询、B 端保存可用范围、C 端 scopes 下发**全部已实测通过，不用再验**
   （见 [[apis]]「已解决」）。
2. ~~找电商推动下发 couponStatusDesc~~ **已关闭**：邓俊兵确认电商不会下发这个字段，
   本地映射（`descOfStatus`/`descOfCouponStatus`）是永久方案，不用再跟进。
3. ⚠️ **自测/联调用的券 SKU 会过期**：coupon-a 测试环境的券数据会滚动重新生成，
   verify.md 里记的具体 sku 值随时可能失效，现查一次再用（见 [[verify]] 的警告和排障方法）。
4. ~~跟前端对齐三个新字段名~~ **已验证**：`postProductId`/`postProductName`/`activityType`
   不是本次改的（T-07/T-10 老字段），2026-09-09 深夜用真实数据直接调接口验证过，
   字段名和取值逻辑都正确，不用再跟前端对齐。
5. ~~跑一遍 C 端三者交集的精确匹配~~ **已验证通过**（见 [[verify]]）：真实券"木7"完整推荐出来，
   `grade_list`/`scope_labels`/`renewal_msg` 全部正确。
6. ~~R-01 找王永诗；R-02 问清「测试冲突」指什么~~ **均已闭环**，见下方「待确认」。

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
| /Users/gaotu/IdeaProjects/JavaProject/student-center | feature-xuban-pre | 券选品接口、发链接分流、券列表 mock |
| /Users/gaotu/IdeaProjects/JavaProject/product-server | feature-xuban-pre | 活动配置、券范围表、三者交集、预警、C端样式 |
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

> ⚠️ **mock 已全部删除**（2026-09-09 起券信息全部实时取电商），`pre.order.coupon.mock.enabled`
> 这类 mock 开关**已不存在于代码里**，上线不用管它——如果哪份旧文档还提这个开关，那份是过时的。

## 必须知过的坑

- **8027 ≠ 膨胀券**，是课时包商品，两个仓库都已占用。膨胀券是 **8014**。
- **Apollo 没有泳道 cluster 是正常的** —— 读不到会自动回落 `default`，不必为泳道单独建 cluster。
  别把「查泳道 cluster 404」当成环境不可用（我犯过这个错）。
- **泳道名不能反推逻辑环境**：`test-gtbg-dev-3` 属于 **dev** 不是 test，只查 environment=test
  会误判「该泳道没 pod」。已修进 `pod_term.py pods`（默认聚合 test+dev，带 `--ns` 过滤）。
- **promotion 券字段不落库是设计如此**，只在 Redis 缓存里；插 DB 造不出可用的膨胀券活动。
  ⚠️ 别再想着「给表加券列」——`product_number` 已是券商品 ID、`product_type=8014` 已能区分，
  券名/金额/状态是电商权威数据，落库即脏快照。2026-09-09 试过一次已 revert（`a620a7e2f`→`8ed5fbab1`）。
- **cart 侧三处已改为抛异常**（price / scopes / deductibleAmount）：上游字段缺失时落地页直接失败，
  **这是预期行为**（不能静默失败）。别把它当回归 bug 去「修回」返 0。
- **成对求交**：cart 原本把年级、学科**分别求交**，会放行「年级来自 A 组合、学科来自 B 组合」的
  伪命中，已改为按 `PreOrderActivityCouponScopeDTO` 整对比对，并删掉诱发该写法的 `intersect()` helper。
- 🔴 **`couponStatusDesc` 本地翻译这条口径 2026-09-09 晚间已反转两次，以最新为准**：
  白天定的是"不做本地兜底、等电商下发"；晚上先改成"电商真的下发前本地按 jar 注释映射"；
  再后来邓俊兵在群里直接确认"中文展示逻辑你们按需判断展示就行"——**电商压根不打算下发这个
  字段，本地映射是永久方案**，不是过渡。**这条教训**：早期"权威源在 XX，等 XX 提供"这类决定
  要小心，对方一句"你们自己判断"就能让"等对方"变成死等；下次遇到类似的"文案/枚举权威源在
  下游"的设计，最好一开始就直接问清楚"你们会不会下发"，不要假设会。现状：
  student-center `PreOrderCouponStatusEnum.descOfStatus()`、promotion
  `PreOrderCouponEnricher.descOfCouponStatus()` 都已按永久方案实现，不用等电商。
- 🔴 **别把券状态 2 当「使用中」**。这个值错过两次：最初写 1（当时枚举「1 待开始」）、
  09-08 改成 2（当时枚举「2 使用中」），而**电商真实枚举 2 = 已失效**。
  停在 2 会把失效券当可用券放行，是资损方向。判据只有一个：
  以 `coupon-a-client` jar 里的 `ExpandCouponDetailDto` 为准，别信任何本地文档的旧表述。
- 🔥 **接外部 Feign jar 前先看它的注解是哪个包**。`coupon-a-client` 用的是旧包
  `spring.cloud.netflix.feign.FeignClient`，student-center 用 `openfeign` 3.0.3 ——
  **不同注解类，`@EnableFeignClients` 只认自己那个**，怎么配 basePackages 都注册不上。
  症状是**编译全绿但启动即挂**（`bean of type XxxFeignService not found`），
  pod 一直 Running 而 eureka 永远 None。解法：只复用 jar 的 DTO，接口本地重新声明。
  ⚠️ promotion 用旧包注解所以能直接用 —— **两仓不对称是版本差异，别以为是笔误去"统一"**。
- **青舟构建失败要先分辨真假**：`Aborted by uqun`(人为/并发中止) 与
  `JNLP4-connect failed`(agent 掉线) 都是假失败，`errors` 数组为空；
  日志里刷屏的「不支持的解析类型, XxxController」是 apidoc 噪音，不是原因。
- 🔥 **B 端链路上还有 `promotion-management`，它不在最初那 6 个仓库里**。
  路径是 `OES 页面 → promotion-management → promotion-b`，它是**纯透传层**，
  但 DTO 落后于下游契约时会**静默丢字段**（Jackson 忽略未知属性），
  表现极具迷惑性：页面配了可用范围却报「膨胀券必须配置可用范围」，
  而且**报错发生在下游 promotion-b，promotion-management 自己的日志里看不出原因**。
  ⚠️ **下游 promotion/product-server 加字段时，这一层必须同步加**，否则白改。
- 🔥 **promotion-b 只连 promotion 库，scope 表在 gaotu 库**。
  `GaotuDataSourceConfig` 这个类名极具误导性 —— 它读的是 `jdbc.promotion.*`，连的是
  promotion 库。所以「让 promotion 直接连表写 scope」做不到，必须跨服务。
- 🔥 **product-b 与 promotion-management 之间没有任何调用关系（两个方向都没有）**。
  product-b 的 Feign 指向 **promotion-b**；promotion-management 的下游里没有 product。
  `ServiceConstant.PRODUCT_SERVICE_NAME` 有定义但**无人使用**，且指向商品中心≠product-b。
  排查链路归属时别被这个常量误导。
- ⚠️ **别让 promotion-b 回调 product-b 的 `/b/renewal/preOrderActivity/edit`** ——
  那个接口内部会调 promotion-b，会形成 **promotion-b → product-b → promotion-b 循环**。
  必须用只写 scope 表的专用接口 `/feign/preOrderActivity/couponScope/save`。
- 🔥 **`baijia_invoke.py` 的 `ROUTE_MAP` 没登记 `promotion-management`**，用
  `mcp baijia-invoke invoke_service project=promotion-management` 会走兜底前缀
  `/bgwApi/component/promotion-management`（不存在的路由），被 CAS 兜底成「请重新登录」——
  跟 Cookie 没关系，是路由没配。且就算配对路由，**promotion-management 仓库压根没挂
  `AclServiceCompareController`**（反射桥只在 student-center/promotion/cart/product-server
  四个仓库里），测它只能走真实业务接口（登录了 OES 页面的浏览器 fetch）。
- 🔥 **`invoke_service` 反射桥调 `queryList` 这类带 `List<Long>` 参数的方法时，参数不会真正生效**——
  传什么 `skuNumbers`/改多小的 `pageSize` 都返回同一页默认数据，这是反射桥自身 JSON→Java
  参数适配的缺陷，**不代表接口真的不支持过滤**。真实 Feign 调用（业务代码内部走 Java
  对象序列化）不受影响。用这个反射桥测复杂参数方法前，先确认返回是不是「不管传什么都一样」。
- 🔥 **coupon-a 测试环境的券 SKU 会滚动重新生成**，今天下午记的 skuNumber 晚上可能已经对应
  别的券或查不到。别直接复用文档里记的具体 sku 值，每次要用真实券自测先现查一次，
  详见 [[verify]]「电商 coupon-a 联调信息」段。排查"回显是空"先查日志里有没有
  `PreOrderCouponEnricher | 部分券在电商查不到`，别先怀疑代码逻辑。
- 🔴 **`promotion` 在 test-gtbg-dev-3 有 `promotion-b`(serviceCode `gaotu_promotion`)和
  `promotion-c`(serviceCode `gaotu_promotion_c`)两个独立部署**，同一份代码两份运行实例。
  **B 端反射桥走的是 promotion-b，cart 走的是 promotion-c**——只发 promotion-b、
  用反射桥调 `listFromCache` 验证通过，不代表 cart 端到端真的通了，因为 cart 打的是
  另一个从没发过新代码的 pod。**判据**：`qingzhou-trace trace_tree` 里对应 span 的
  `gapmApp`/`service` 字段会显示到底是哪个部署接的请求，别假设"发过一次就都发了"。
  改动涉及 C 端链路(`listFromCache`/`calculate`/`calculateWhite`)的代码，
  **promotion-b 和 promotion-c 都要重新发布**。
- 🔥 **跨服务 Feign 契约里，嵌套泛型容器和响应信封是两个独立的坑，都会在真正联调时才暴露**：
  ① `Map<Long, Map<Long, List<...>>>` 这类嵌套 Map，FastJson 的 Feign 解码器解不出来，
  报 `parseLong error`——改成扁平 `List<Row>`；
  ② Feign 方法声明的返回类型必须**精确对齐对端实际的 HTTP 响应体结构**，如果对端用
  `RestTraceResponse<T>`（`{code,msg,data}`）包了一层，Feign 方法就不能直接声明成
  裸 `T`，要声明成信封类型再手动 `.getData()`。**这两个坑都在 `void` 返回的写接口
  （如 `save()`）上测不出来**——Feign 对 void 返回值压根不走解码器，得等第一个
  真正有返回值的读接口才会暴露，别以为"跟 save() 抄的写法"就一定安全。
