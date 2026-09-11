---
title: 续班预报名使用膨胀券 · 会话日志
tags: [需求, 日志]
---

# 会话日志

> **只追加，倒序（新的在上）。任何时候不许改写或删除旧条目。**
> 结论错了 → 追加一条新的说明它错了，不是把旧的抹掉。
>
> **单轮 ≤25 行，只写三样**：定了什么+为什么 / 推翻了什么+为什么 / 用户的手工动作。
> 最终结论本身归 [[README]]、[[apis]]；流水账（部署了/已push/编译通过）和对话抄录一律不写。
>
> **前后矛盾在这里大多是对的** —— "09-08 定 A、09-09 改成 B" 正是要留的决策过程，别去修平。
> 只有无时间锚点的活文本（尤其「留给下次」）要处理：已作废的**行末补指针**，原文不改。
>
> 🔻 **2026-09-10 做过一次性压缩**（633 行 → 本文件）：只保留决策与理由，删掉流水账、
> 对话抄录、与 README/apis 重复的最终结论，以及**与需求无关的 skill/文档维护记录**。
> **压缩前的完整原文见 git 历史 `c3a8b27`**。此后严格只追加，不再压缩。

---

## 2026-09-11（第九轮 · 券选品列表补两个字段 + 售罄双端拦截）

### 👤 我
- 指出券列表没返回「预报名可用范围」（截图 OES 活动管理页有这一列）
- 「不传就是不用管可用范围」—— 明确只做传了续班计划的场景
- 指出创建人为空、库存字段要加；确认 `soldCount`/`totalCount` 本就有值，只补 `holdLimit`
- 「在 oes 选商品的时候如果已售>=总量之后不可选」，且**「活动里面添加券的时候也需要判断，不仅仅是返回」**

### 定了什么
- **「可用范围」不新开接口、不加 `activityNumber` 入参**：三者交集结果
  （`ProductDisplayableCouponDTO`）本来就带命中的年级学科，此前在 ACL 层
  被 `.map(getCouponSkuNumber).distinct()` 提前丢掉了。改为透传扁平行、
  由调用方去重 —— 防腐层不该替调用方决定"哪些信息以后用不上"。
- **售罄要双端拦**：前端置灰只是提示，绕过照样能提交，所以
  promotion 的 `edit`/`editAndPublish` 必须服务端拦。
  两端判据一致（已售 ≥ 总量），但**缺数据时的选择相反**：
  student-center 列表「不改判」（宁可漏置灰），promotion 写链路「放行」——
  共同的理由是**误伤正常券的代价大于漏掉一张售罄券**，且售罄可追加库存恢复。
- **`couponStatusDesc` 的老坑没再犯**：这次 `holdLimit` 直接透传电商字段，
  没有本地维护映射 —— 电商 DTO 里有的就透传，没有的（`creator`）就承认没有、
  不编造兜底值。

### 定了什么（续，当天稍晚）
- **`holdLimit` 由数字改成展示文案（String）**：电商用 `0` 表达「不限」，
  直接透传会被前端显示成「0 张」—— 语义正好相反。同 `couponStatusDesc` 一样，
  **这种「哨兵值→文案」的翻译放后端做**，不让每个前端各自判一遍。
- **满班校验与售罄校验是同一条规则的两种形态**：「卖不出去的东西不许进活动」。
  订金班判 `signUpCount >= capacity`，膨胀券判 `soldCount >= totalAmount`，
  两者「查不到就放行」的理由也一致。**`capacity = -1` 是不限班容必须放行** ——
  测试环境大量班级都是不限班容，漏了这条会把它们全拦掉。
- **查班容不能用现成的 `ClazzAclService#listByNumbers`**：它返回的 `ClazzVO`
  只有 `capacity` 没有已报名数，判不了满班。改走班级大全搜索 `clazzSearchList`
  （与 B 端选班列表 `/b/clazz/list/search/fullAuth` 同源），它才同时下发两者。
  ⚠️ 该接口 `Pager` 默认 pageSize 只有 **20**，不显式设会只回前 20 条，
  调用方把没回来的班当成「查不到」而放行 —— 是**漏校验**方向，必须设。

### 推翻了什么
- 一开始准备按「活动配置页也要展示可用范围」设计，要给接口加 `activityNumber` 入参
  走 `listByActivityNumbers`。**用户否掉**：不传续班计划就不用管。
  少做的这一半避免了给存量的运营纯券搜索场景引入一个只在特定页面有意义的入参。
- **「截图里那张券 10/10 就是售罄券，拿它测拦截」—— 错的**。反射桥直查电商发现它
  `sold_count=0`、`coupon_status=2`(已失效)，与页面显示三项全不符。
  **页面那列读的是 promotion 活动商品缓存，不是电商实时值。**
  教训与 09-10 那次「拿反射桥未过滤结果当证据」同源：**验券的真实状态只认电商直查**，
  页面/缓存/文档记录都可能是旧快照。售罄链路因此端到端验不了，改用单测锁逻辑（4 条）。

---

## 2026-09-10（第八轮 · 发泳道联调，修 3 个 bug 后端到端跑通）

### 👤 我
- 「现在发镜像」
- 指出泳道是 `test-gtbg-dev-3`（我沿用了旧文档里的 `test-eco-7`）

### 推翻了什么
- **「product-b 单边验证通过」不等于链路通**。三个 bug 全部只在端到端暴露，
  单测（16/16）和单边接口调用都是绿的。这轮最该记住的一条。
- **snake_case 的药下错了一次**：先加 Jackson `@JsonProperty` → 部署后仍 `data:[{}]`。
  真因是**这条链路的解码器是 FastJson**（`ProductInterceptorFeignConfig` 里的
  `GaotuRcpHttpMessageConverter extends FastJsonHttpMessageConverter`），不认 Jackson 注解。
  方向对（确实是命名不匹配），但注解族错。

### 定了什么
- **调 product-server 一律复用 `ProductInterceptorFeignConfig`，不自己拼 decoder、不手标注解**。
  `RenewalMasterFeignAdapter` 一直这么用，是既有先例；我一开始照 `ProductAdapter` 抄了
  服务名、却没抄 configuration，两处都踩了。
- 服务名用 `PRODUCT-B`（与 promotion 的 `ServiceConstant.PRODUCT_B_NAME` 同口径），
  不是 `PRODUCT.GAOTU100.COM`（那是 product 主部署，我们的接口只在 product-b 模块）。

### 排障中查清的事实
- **`data:[{}]`（数组长度对、元素是空对象）= 字段名映射错**，不是没查到数据、也不是没部署。
  这个症状此前没人记过，已写进 README。
- 排除"没发上去"的正确手段：进 pod `unzip -p app.jar BOOT-INF/lib/student-center-adapter-*.jar`
  再 `strings | grep -c <注解值>`。⚠️ **`pod_term.py` 不指定 `--pod-name` 会选错 pod**
  —— 该泳道还跑着 `feature-gps-learn-situation` 的 student-center，选错会得到 `0` 的假结论
  （我因此一度以为镜像没发上去）。
- **交集语义已用硬证据验证**：同 3 张券（状态都是 1、电商都查得到），不传计划号 `total=3`，
  加计划号 `total=1` —— 英语/语文两张纯粹被「年级+学科成对匹配」挡掉。
- 「失败抛异常不降级」这个设计在本轮直接兑现了价值：服务名写错时报出
  `PRE_ORDER_COUPON_SCOPE_QUERY_FAIL`，我才发现 404。若当初降级成"不过滤"，
  券列表照样有数据（全量券），这个 bug 会一路带到线上，把不该展示的券给老师。

### 留给下次
- 本需求侧无待验项。上线前事项见 [[README]]「下一步」。

---

## 2026-09-10（第七轮 · B 端下单弹窗膨胀券 tab 券列表按三者交集过滤）

### 👤 我
- 给了 `recommendProductList` 的 URL 说「这个服务得加个接口，这个 tab 得续班计划配了膨胀卷才展示」
- 贴需求截图（金瑞琳问「这个 tab 需要灰度控制吗」→ 王永诗 09-03 答「不用，续班计划不配膨胀券不展示」）
- 追问「膨胀卷的列表接口是哪个」，纠正接口归属：**是 student-center 的膨胀券选择分页查询，不是 product-server 新接口**
- **中途改口径**：「tab 一直展示，不用加灰度或者其他校验，不配膨胀券就点进去没数据」
- 要求字段名用 `renewMasterNumber`（给了样例值 `500775609543200768`）
- 指出我沿用了旧文档里的 `test-eco-7`，实际泳道是 `test-gtbg-dev-3`

### 推翻了什么
- **「不配膨胀券就不展示 tab」→「tab 常显，没数据即空」**。原按截图口径已在
  `PreOrderCouponPageVO` 加了 `showCouponTab` 字段并在 Biz 里按活动形式短路，
  用户改口径后**整体 revert**（该文件现零 diff）。
  理由：既然 tab 不隐藏，"有没有数据"本就是交集过滤的自然结果，
  再多一个显隐字段等于让前端和后端各存一份判断，多余且会分叉。
- **一开始理解成「在 product-server 加接口」→ 实际是给 student-center 已有的
  `/renewal/pre/coupon/list` 加过滤能力**。那个接口早就存在、8 列字段齐全，
  缺的只是"范围"这一维。

### 定了什么
- **交集出口开在 product-server，student-center 只取结果不重算**。
  `PreOrderCouponIntersectService` 的类注释早就点名三个调用方（发链接 / B 端下单弹窗券列表 /
  C 端落地页）口径必须一致、"不得自行再算一遍"，本次就是第二个调用方。
  在 student-center 重写一份交集 = 老师看到的券 ≠ 学员能买的券。
- **新 feign 入参只要 `renewMasterNumber`**：活动号（→ 预报名节点 → 绑定活动）和
  前置课程号（→ 续班关系表）在 product-server 都能自足反查。让调用方拼这两个值
  等于把交集的输入口径散出去。
- **ACL 失败抛异常不降级**：降级成空列表运营会误判「没配券」，
  降级成"不过滤"会把电商全量券暴露给老师（更严重，属越权展示）。
- **范围与用户手填的券商品ID求交**，不是二选一：范围覆盖检索条件会让搜索框失效，
  只用检索条件则绕过范围限制。
- 不做分批：product-server 侧单活动券上限 100，与 student-center 批量上限同值，
  恰好不会超；对端若放宽该上限，这里要改成分批（已写进代码注释）。

### 顺带修掉
- **`c0a448b57` 那条提交带的单测其实一直没编译过**（用了本仓库 assertj 版本没有的
  `anySatisfy`/`noneMatch`），把整个 `product-server-domain` 的 test 编译卡死 ——
  也就是说那轮"已补单测"实际从未运行。已改成等价显式写法，8/8 通过。
  教训：单测提交前必须真跑一次，"写完编译过"不等于"测试跑过"（test 编译是独立阶段）。
- student-center 两个只影响 test 域的环境坑：mockito `core 2.23.4` 与
  `junit-jupiter 3.9.0` 版本冲突（`NoSuchMethodError: Plugins.getMockitoLogger`）→ 一起钉 3.3.3；
  `log4j-slf4j-impl` 与 `log4j-to-slf4j` 双桥接使 `@Slf4j` 类静态初始化即失败 → 排掉后者。

### 留给下次
- **接口实测还没做**（需发 `test-gtbg-dev-3`）：验 `renewMasterNumber` 传膨胀券计划
  只返回交集内且【使用中】的券、传订金班计划返空 list。发完先确认 eureka UP。
- product-b 的网关路由能否通到 `/feign/preOrderActivity/couponScope/listDisplayableByRenewalPlan`
  需联调实测一次（adapter 用的服务名 `PRODUCT.GAOTU100.COM` 与仓库既有写法一致）。

---

## 2026-09-10（第六轮 · 补 B 端 detail scopes + 揪出 snake_case 序列化根因）

### 👤 我
- 「昨天代码有问题导致现在的活动都没配可用范围」，要求用编辑接口补；后追加「不能通过接口就直接改表」
- 页面新建活动后追问「为什么这个活动 detail 还是看不到可用范围」
- 直接 curl 打 coupon-a 三个 sku，`total=1` 全部命中，**当场推翻我"券已过期"的判断**
- 指出「你查机器啊别查 apollo 了我没配」，把排查方向从配置拉回 Eureka/实例
- 要求修复后「影响面小吧 不用影响其他地方 要不然太恐怖了」

### 定了什么
- **scopes 补齐抽成共用方法**（`loadCouponScopeRows`/`applyCouponScopes`），C 端 B 端都走它。
  理由：这两条链路各自独立补齐，已经先后漏了两次（09-09 C 端、09-10 B 端），
  再分开写第三次还会漏。
- **`PreOrderActivityCouponScopeDTO` 补 `gradeName`/`subjectName`**：只用于回显，
  不进 `couponScopeKey`，唯一键与校验口径不变（已用重复组合/空范围两条用例坐实）。
- **snake_case 修法选「子类覆写 getter + `@JSONField`」**，不动全局配置、不换编解码器。
  理由见 [[apis]]；另两条路一条波及全部对外接口，一条在 Edgware.SR5 上根本编译不过。

### 推翻了什么
- ❌ **「coupon-a 测试环境券 SKU 会滚动重新生成」是错的**（09-09 写进 README/verify）。
  实测 `couponName=木7` 返回 `total=2`，旧 sku `578513860277893121` 和
  `578534533488603137` **两张都还在**，是同名的两张不同券，不是同一张被换号。
  真因是筛选失效只返回第一页；新券恰好在第一页，才造出"旧 sku 失效"的错觉。
- ❌ **「反射桥参数不生效是工具缺陷、真实 Feign 不受影响」后半句是错的**。
  真实 Feign 同样中招，同一个 snake_case 病根。
  **教训：反射桥像是没过滤时，先验真实调用，别急着归因于工具。**
- ❌ 我自己中途两个误判也记下：先说 mitmdump 没起（其实一直在跑，grep 漏了进程名）、
  先说「tianti 必须走 CAS 换票所以通道不通」（其实是 cookie 没刷新到位，刷新后直接通）。

### 👤 用户手工动作
- 09:28 从页面删掉了 4 个旧测试活动（`578532548546686976` 等），
  我之前直接改表补的那批范围数据因此作废 —— 真正要修的是代码，不是数据。
- 新建了活动 `578653392472137728`（膨胀卷-zzl-test-1）、`578660732372013056`、
  `578667346476945408`（造数）用于验证。

## 2026-09-09（第五轮 · 修 detail 回显 + 发现并修 C 端 scopes 缺口）

### 👤 我
- 转发马胜消息确认架构：promotionManager=应用层(透传)，promotion-b/product-b=两个 domain
- 指出反射桥登录失败可能是路由配错，让去查 `ROUTE_MAP`
- 转发电商邓俊兵群里确认 + 截图：`@ApiModelProperty("券状态: 1 使用中 / 2 已失效 /
  3 审核中 / 4 已暂停")`，原话"中文展示逻辑，你们按需判断展示就行"

### 🤖 Claude
- **推翻「等电商下发 couponStatusDesc」的口径**（T-28）：拿到用户转发的确认后定案为
  **本地映射是永久方案**。**教训**：「权威源在下游、等下游提供」这类设计，
  一开始就该问清"你们会不会下发"，否则"等对方"会变成死等。
- **定了 detail 与 listFromCache 是两个独立缺口，必须各修各的**：
  `detail()` 走 DB、`listFromCache` 走缓存，两条链路此前都没挂券信息补齐。
- **定了跨服务查 scopes 返回扁平行而非嵌套 Map**：FastJson 的 Feign 解码器
  解不出嵌套泛型容器（`parseLong error`）。
- **踩坑：只发 promotion-b 不算发布完**。反射桥走 b、cart 走 c，两个独立部署；
  靠 `trace_tree` 看 `gapmApp` 才发现。结论已进 README 坑位。
- 单测派了 3 个 subagent 并行写，逐一读过源码才提交（不只信 agent 自述）。

---

## 2026-09-09（第四轮 · 券范围落库改由 promotion-b 回调 product-b）

### 👤 我
- **定方案**：库不变，由 promotion 通过 Feign 调 product-b 保存可用范围，**要求加事务保证原子性**
- 提供 traceId `f346c23d`（scopes 丢失）与 `c7d123cc`（详情 NPE）

### 🤖 Claude
- **定了新增专用只写接口，不复用 `/b/renewal/preOrderActivity/edit`**：
  后者内部会调 promotion-b，被回调就形成 **promotion-b → product-b → promotion-b 循环**。
- **查清了为什么必须跨服务**（而不是让 promotion 直接连表）：promotion-b 只连 promotion 库，
  scope 表在 gaotu 库，两张表不同库、跨库 join 不可行。
- **留档一个已知取舍**：非分布式事务，「product-b 已提交但 promotion 回滚」仍可能发生。
  判定风险可接受（残留行挂在不存在的活动号上不会被命中，且对端幂等），
  若要根治需引入本地消息表或定时对账。

---

## 2026-09-09（第三轮 · 下线 mock 接真实接口）

### 👤 我
- 电商接口有数据了，要求**把 mock 都删了直接用接口**

### 🤖 Claude
- **定了不保留「真接口失败回落 mock」**：会掩盖真实故障。mock 全部删除，不留开关。
- **踩坑：Feign 注解包不同导致启动失败，编译期发现不了**。`coupon-a-client` 用旧包注解，
  student-center 用 openfeign 3.0.3，`@EnableFeignClients` 只认自己那个。
  定案：**只复用 jar 的 DTO，接口本地重新声明**。promotion 侧不用改（正好用旧包注解）——
  **两仓不对称是版本差异，不是笔误**。
- 另踩 grpc 硬版本区间冲突（排掉全部传递依赖解决）、青舟"假失败"误判。结论均进 README。

---

## 2026-09-09（第二轮 · 券状态枚举按电商定稿）

### 👤 我
- 给出电商接口 interfaceId=5453936 与依赖 `com.gaotu:coupon-a-client:1.3.15`

### 🤖 Claude
- 🔴 **推翻本地枚举，发现资损向缺陷**：`COUPON_STATUS_IN_USE`=2，而**电商的 2 是「已失效」**，
  会把失效券当可用券放行。已 2→1。
  **根因：一直拿本地暂定枚举自洽，没有权威源** —— 这个值因此错过两次（最初 1、09-08 改 2）。
  定案：只认 jar 的 `ExpandCouponDetailDto`。
- **定了 mock 的 JSON 改用电商真字段名**，这样接真实 Feign 时只需拆掉 mock 分支、映射逻辑不用改。

---

## 2026-09-09（券状态文案第一版口径，当天晚间即被推翻）

### 🤖 Claude
- **定了：券状态文案权威源在电商，本地不做兜底翻译**（用户决策），
  `descOfStatus()` 随之删除。
  → ⚠️ **本条口径当晚被推翻**，见「第五轮」：电商确认不会下发，本地映射才是永久方案。

---

## 2026-09-09（券字段落库方案撤销 + 改接 mock）

### 👤 我
- review 指出：`product_number` 就是券商品 ID、`product_type=8014` 已能区分券与课程，
  `coupon_id`/`sku_id` 属冗余；券名/金额/状态权威源在电商，落库即脏快照。**一列都不用加**

### 🤖 Claude
- **推翻 09-08 的「加 5 列」方案并 revert**，DDL 工单 8025 已撤。
- 🚨 **顺带消除一个必挂故障**：revert 前 `Base_Column_List` 已含 5 列而表里没有 →
  一发布 `selectByExample` 必报 `Unknown column`，**连订金班活动查询一起挂**。
- **过程教训**：本轮开工没先读归档 README，凭代码推理把已定稿的 `productType=8014`
  当成"还没定"，来回纠正四轮。**教训：开工先读归档 README，别凭代码推理已定稿的口径。**

---

## 2026-09-09（下午·续接）

### 🤖 Claude
- **定位根因**：`detail` 直接读 DB，而 mock enricher 只挂缓存重建路径 → B 端券字段全 null。
  这是**挂载点缺口，不是新 bug**。
- **附带查清两条**：promotion 的 mock 开关**从没配过**（verify 记的"已发布"是 student-center，
  两个 appId 混了）；scope 表 5 行全是假活动号。
- 新建 [[apis]] 接口变更台账。

---

## 2026-09-08（第六次会话 · 撤销落地页 path 分叉）

### 👤 我
- 前端确认 **`/preSignUpCoupon` 页面不存在**，要求撤：path 不分叉，两形式共用 `/preSignUp`

### 🤖 Claude
- **一个错误的前端假设污染了 5 份 spec + 2 个仓库的已提交代码**。用户点名 3 份，
  实际排查另有 2 份也写了同一假设，且 2 个仓库已按它写完代码合进分支。
- **定了回滚边界（问过用户）**：只回滚 path 分流，**保留活动形式判定** ——
  `FormResolver`/`FormEnum` 还被下单前校验 validate 用着，直接 `git revert` 会误伤校验链路。
- **定了删掉 Strategy 与 `getPreOrderActivityType`**：前者与订金班唯一差异就是切 path，
  去掉后是纯透传；后者已无调用方。留着都是挂一条无人验证的分支。
- 📌 **查清 promotion 有三个青舟部署共用同一产物**（promotion-b/c/task），
  `qingzhou_deploy` 传 `project_name` 会因命中多个而失败，**必须传 service_code**。
- ⚠️ **上线注意**：Apollo **不要**新增那两个 path 相关 key —— 代码里已经没有了。

---

## 2026-09-08（第六次会话 · 桥全打通 + 发现上线阻塞项）

### 🤖 Claude
- **定了反射桥三份逐字节相同、自带极简 RVO**，不复用各仓响应包装类
  （product-server 一个仓库就有 5 种，复用必漂移）。
- 🔴 **发现上线阻塞项：promotion 券字段不落库**，缓存 miss 会从 DB 重建、重建后必为 null。
  **影响比原以为的严重**：不只是"B 端详情回显丢字段"，而是**缓存一过期券信息整体丢失**
  → C 端无券可展示、三者交集必空、cart 直接抛异常。
  → 后续定案是**不落库、实时取电商**（见 09-09），中途试过加列已 revert。
- **三个坑已进 verify**：「请重新登录」多半是路由/host 不匹配非 Cookie 失效；
  cart 是 C 端服务必须换 host；`curl --data-raw @file` 不读文件。

---

## 2026-09-08（第五次会话 · 建活动受阻 + 修工具）

### 🤖 Claude
- **推翻上一轮「三个服务在泳道没有 pod」的结论**：错因是查 pod 只用了 `environment=test`，
  而 **test-gtbg-dev-3 属于 dev 逻辑环境** —— 泳道名不能反推逻辑环境。
- **修掉一个跨仓库真 bug**：product-server 的 `COUPON_STATUS_IN_USE`=1 与 student-center
  枚举（1=待开始/2=使用中）不一致 —— 两边各自"自洽"、不报错，只表现为券列表多券/少券。
  → ⚠️ 这次改成 2 **后来又被推翻**（电商真实枚举 2=已失效），见 09-09 第二轮。
- ⚠️ **发现券字段不落库**（`pre_order_activity_product` 只有 8 列，券信息只在 Redis）：
  → **直接往 DB 插活动造不出可用的膨胀券活动**，必须走 `create()` 让它写缓存。

---

## 2026-09-08（第四次会话 · B 端自测通过）

### 🤖 Claude
- **订正上一轮两个错误结论**（原条目保留，按规矩追加）：
  1. 「泳道是空壳不可用」**是错的** —— Apollo 查不到泳道 cluster 会自动回落 default，
     404 不代表环境不可用；且查 pod 的时刻早于用户发布镜像的时刻。
  2. 「promotion 尚未下发 scopes 与购买金额」**也是错的** —— promotion 侧早已有这些字段，
     缺的是 **cart 自己的 client DTO 没同步**，是我方要补，不是等上游。
- **按用户要求把 cart 三处静默失败改为抛异常**：空态与"本来就没配券"无法区分，属于静默失败。
- **修掉一个真 bug**：cart 把年级、学科**分别求交**，会放行「年级来自 A、学科来自 B」的伪命中；
  改为整对比对（product-server 的同源实现本来就是对的，是 cart 漂了）。

---

## 2026-09-08（第三次会话 · 自测准备）

### 🤖 Claude
- **发现前置阻塞**：`pre.order.activity.coupon.renewalPlanIds` 不配，
  `FormResolver#resolve` 永远兜底成订金班，**膨胀券链路根本进不去** —— 不先配它，自测跑的还是老路径。
- **静态走查确认三者交集实现是对的**：判定始终锚定单行 scope，不存在拆成两个集合分别求交的写法。
- ⚠️ 本轮记的「泳道是空壳」结论**次日被推翻**，见第四次会话。

---

## 2026-09-08（第二次会话 · 开发）

### 👤 我
- 手工建了线上表并加 `renewal_` 前缀（截图确认库 `gaotu`、实例 `gaotu-center-prod`）
- 定了：`productType` 用 8014；券不参与满赠；order 侧只管加购；promotion-app 本期不改
- 定了排期口径：周五开发完、周一自测、后两天联调，每天 8 工时

### 🤖 Claude
- **归属口径纠正两次**（先漏 product-server，后漏 cart/order），最终确认
  **除 student-data 外 6 个仓库全是我的活**。已写进项目 memory ——
  反讲「项目关联方」写"待定"指对方对接人待定，**不是这活不是我的**。
- **`productType` 定为 8014**（原文档举例 8027）：8027 在两个仓库都已被「课时包商品」占用。
- **推翻反讲两处判断**：① cart `ProductGroupRequest` **本来就有 `skuNumbers`**，
  "三选一新增桶"前提不成立 → 复用现成字段零改动；② 满赠校验**在 promotion-app**（反讲找错了服务）。
- **发现并修掉 4 个真实缺陷**（都核到行号，结论已进 [[apis]]/[[README]]）：
  膨胀券活动存不进去、券订单 NPE 致整页数据丢失、Controller 校验完全无效、购物车券显示 ¥0。
- **order 侧范围收敛**：初版多做了 327 行已 revert —— 反讲列的是需求全部改动点，
  不等于我们负责的部分。
- **刻意不做「真接口失败自动回落 mock」**：联调期真实故障会被假数据掩盖。

### 我做错的地方（留档）
- TAPD 任务反复增删改 4 轮，**根因是建任务前没问清自测/联调天数、提测日能否干活、排序偏好**。
- 漏派 4 条任务（派 agent 时描述给窄了）；一度说"三个仓库都完成了"实际漏 4 条
  → 改为**逐条核代码再回答**。
- 把排期写进 spec 并 push（用户要的是 TAPD 任务）→ force push 回滚。
  ⚠️ student-center 与 product-server 因此做过 force push，**不要直接 `git pull`**

---

## 2026-09-08（建档）

### 🤖 Claude
- 建本需求归档目录，从飞书拉齐现状：需求 wiki 节点 + 5 份子文档、后端反讲 v0.2、
  待办表 21 条（15 DONE 写进 README 已定共识、5 条 TODO）、6 个仓库的 tech_spec 链接。
- 登记 TAPD story `1122531521001392077`。**未在 TAPD 下建任务**（写操作，等用户点头）。
- 判定当前阶段为**反讲评审**（反讲已到 v0.2，但技术反讲阶段仍有未闭环项）。
