---
title: 续班预报名使用膨胀券 · 接口变更台账
tags: [需求, 接口]
---

# 接口变更台账

> 这个需求动了哪些服务的哪些接口。反讲/上线 checklist 的接口章节从这里抄；联调对不上先查这张表。
> 字段类型走 `apifox-openapi.json`，这里记「改了什么、为什么、谁调、缺什么」。

## 接口清单

| 服务 | 接口路径 | 方法/类 | 变更类型 | 改了什么 | 下游影响 | 状态 |
|---|---|---|---|---|---|---|
| promotion-b | `/domain/promotion/b/preOrderActivity/detail` | `PreOrderActivityService#detail` | 字段新增 | 返回体 product 项加券字段：`couponId`/`couponName`/`skuId`/`buyAmount`/`couponStatus`（`couponStatusDesc`/`scopes` 不在这次修复范围） | B 端活动详情页 `/promotionManagement/preOrderActivity/detail`；product-server `PromotionAclService#getPreOrderActivityDetail` | ✅ **2026-09-09 已修复并实测通过**，见下方「已解决」 |
| promotion-c | `POST /domain/promotion/c/preOrderActivity/listFromCache` | `PreOrderActivityService#listFromCache` | 字段新增 | 返回体 product 项补齐 `scopes`（新增内部方法 `fillCouponScopes`，调 product-server 新接口） | cart `PreRegistrationCouponAssembler#resolveCouponScope`（之前必抛「膨胀券可用范围缺失」） | ✅ **2026-09-09 已修复并端到端实测通过**（cart `preRegistration` 反射调用 `code:0` 不再抛异常） |
| product-server(b) | `POST /feign/preOrderActivity/couponScope/listByActivityNumbers` | `PreOrderCouponScopeFeignController#listByActivityNumbers` | 新增 | 按活动号批量查 scopes，返回**扁平行** `List<PreOrderActivityCouponScopeRow>`（不是嵌套 Map，见下方坑①），供 promotion 的 `listFromCache` 消费 | promotion `PreOrderCouponScopeRemoteService` | ✅ **已修复并实测通过** |
| product-server(b) | `POST /feign/preOrderActivity/couponScope/listDisplayableByRenewalPlan` | `PreOrderCouponScopeFeignController#listDisplayableByRenewalPlan` | **2026-09-10 新增** | 按**续班计划号**查可展示的膨胀券（已按三者交集过滤 + 仅【使用中】）。入参只要 `renewMasterNumber`，活动号与前置课程号都由 product-server 自行反查；返回**扁平行** `List<PreOrderDisplayableCouponRow>`（券×命中的年级学科组合，同一张券多行）。未绑活动/订金班/无交集一律返回**空列表不抛异常** | student-center `PreOrderCouponScopeAclService`（B 端券列表范围过滤） | ✅ 单测 8/8 + **2026-09-10 端到端实测通过** |
| student-center | `/renewal/pre/coupon/list` | `PreOrderCouponController#listCoupon` → `PreOrderCouponBiz#listCoupon` | 新增 + **2026-09-10/09-11 字段新增** | B 端券选品列表，**已接真实电商数据**（mock 已删）。**09-10**：入参加可选 `renewMasterNumber`（续班计划号）——传了就按三者交集限定券范围（与预报名链接一致），并与用户手填的券商品ID求交；范围为空直接返空页且**不再调电商**。不传则不过滤，存量行为不变。**09-11 出参加 3 个字段**：`availableScope`（预报名可用范围文案，如「六年级数学」，同券多组合用「、」连接，**仅传 `renewMasterNumber` 时下发**）、`holdLimit`（单人持有上限，0=不限）、`selectable` 增加售罄判定（已售≥总量置 false，**与有没有续班计划无关**） | 老师端选品弹窗（B 端下单弹窗膨胀券 tab）；下游 product-server `listDisplayableByRenewalPlan` | ✅ **09-10 范围过滤端到端实测通过**（传计划号 total=1、不传 total=142、范围外 sku 返空；单测 5/5）；**09-11 `availableScope`/`holdLimit` 实测通过**（3 条券分别回「六年级数学/英语/语文」，`holdLimit:1`） |
| student-center | `/renewal/pre/couponScope/list` | `PreOrderCouponController` | 新增 | 券可用范围查询 | 老师端 | ✅ 自测通过 |
| product-server | 券范围落库/校验 | `PreOrderActivityCouponScopeService` | 新增 | 活动级唯一键 `uk_act_grade_subject` | B 端活动配置保存 | ✅ 自测通过 |
| promotion-b | `/promotionManagement/preOrderActivity/edit` · `/editAndPublish` | `PreOrderActivityService#validateCouponProductList` | **2026-09-11 校验新增** | 保存/发布膨胀券活动时**拦截已售罄的券**（已售≥发放总量报 `PARAMS_ERROR`）。B 端列表置灰只是前端提示、绕过照样能提交，故服务端必须拦 | OES 预报名活动管理页「添加膨胀券」 | 🔄 已编码已发布，待实测 |

**状态枚举**：`设计中` / `已编码` / `自测通过` / `联调通过` / `已上线`

## 内部方法契约（跨模块）

| 服务 | 类#方法 | 变更类型 | 改了什么 | 谁在调 |
|---|---|---|---|---|
| product-server | `PreOrderCouponIntersectService#intersect` | 新增 | 三者交集，按「年级+学科」成对判定 | C 端落地页取数 |
| product-server | `PreOrderDisplayableCouponService#listDisplayableCoupons` | **2026-09-10 新增** | 按续班计划反查（活动号 + 前置课程号）后**委托** `PreOrderCouponIntersectService#intersect`，再把结果拍平成扁平行。**本类不自行求交** | `PreOrderCouponScopeFeignController#listDisplayableByRenewalPlan` |
| student-center | `PreOrderCouponScopeAclService#listDisplayableCoupons` | **2026-09-10 新增 · 09-11 改签名** | 取 product-server 的交集结果；**下游失败抛异常不降级**（降级成空=运营误判「没配券」，降级成不过滤=全量券越权展示）。⚠️ 09-11 由 `listDisplayableCouponSkuNumbers(): List<Long>` 改为 `listDisplayableCoupons(): List<ProductDisplayableCouponDTO>` —— 原先在防腐层就去重成券商品ID，把命中的年级学科丢了，而「预报名可用范围」文案正是要用它。**去重改到调用方做** | `PreOrderCouponBiz#listCoupon` |
| promotion | `PreOrderCouponEnricher#queryCouponsBySkuNumbers` | **2026-09-11 新增** | 把私有的 `queryCoupons` 开放给**写链路校验**复用，为的是复用它规避 FastJson SnakeCase 的写法（必须用 `CamelExpandCouponQueryRequest`，否则 `skuNumbers` 发成 `sku_numbers` 被电商静默忽略→筛选失效返全量） | `PreOrderActivityService#validateCouponNotSoldOut` |
| promotion | `PreOrderActivityService#validateCouponNotSoldOut` | **2026-09-11 新增** | 保存/发布活动时拦截已售罄（已售≥发放总量）的券。挂在 `validateCouponProductList` 末尾，`edit`/`editAndPublish` 两条路径都经过。**一次批量查完**不逐张调（100 张券=100 次 RPC）；**券查不到直接放行**（电商抖动误杀正常配置的代价 > 漏拦一次，且售罄可追加库存恢复） | `PreOrderActivityService#validateProductListByType` |
| promotion | `PreOrderCouponEnricher#enrich` | 新增 | 券字段实时补齐（**已从 mock 切换为真实电商 coupon-a**），挂在缓存重建路径 | `PreOrderActivityDomainServiceImpl:238` |
| promotion | `PreOrderCouponEnricher#enrichDTO` | **2026-09-09 新增** | `enrich()` 的重载版本，针对 `detail()` 用的 `PreOrderActivityProductDTO`（字段集与 `enrich()` 完全一致） | `PreOrderActivityService#detail` |
| promotion | `PreOrderActivityService#fillCouponScopes` | **2026-09-09 新增** | `listFromCache` 补齐 scopes，调 product-server 新增的批量查询接口 | `PreOrderActivityService#listFromCache` |

## 已解决（2026-09-09 本次会话）

### ✅ B 端 detail 券字段全空 —— 已修复并实测通过

**根因**（挂载点缺口，不是新 bug）：`detail()` 直接读 DB（表只有 8 列无券字段），
不像列表页那样经过缓存重建路径，`PreOrderCouponEnricher` 之前完全没有挂在这条链路上。

**修法**：给 `PreOrderCouponEnricher` 加 `enrichDTO()` 重载，在 `detail()` 里
`fillProductNames` 之前调用（promotion `81180aa45`）。

**验证**（用当下真实存在的电商券"木7" skuNumber=578534533488603137 重新建活动 `578563007821410304`）：
`detail()` 返回 `coupon_id`/`coupon_name`/`coupon_status`/`buy_amount`/`sku_id` 全部正确回显；
经 `promotion-management` 透传层（`961cb892`）后同样正确。**排查过程踩了一个坑**：
第一次用 verify.md 里记的旧 skuNumber(578513860277893121，标注"木7") 测，一直显示 null，
以为是修复没生效——查日志发现 `PreOrderCouponEnricher#enrichDTO | 部分券在电商查不到`，
换真实当下存在的 sku 重测才通过。**结论：coupon-a 测试环境的券 SKU 会滚动重新生成，
verify.md 里记的具体 sku 值会过期，不能当长期有效的测试数据用**，见 [[verify]]。

`scopes` 与 `couponStatusDesc` 当时仍是 null（不在 detail 那次修复范围）：
- `couponStatusDesc`：后续已单独修复，见下方「✅ couponStatusDesc 本地映射」
- `scopes`：权威源在 product-server，见下一条

### ✅ C 端 listFromCache 不下发 scopes —— 已修复并端到端实测通过

**发现过程**：测 cart 的 `preRegistration` 推荐接口时，子 agent 造数据打通了续班计划关联，
链路推进到膨胀券分支后卡在 `PreRegistrationCouponAssembler#resolveCouponScope` 抛异常
「膨胀券可用范围缺失」。追查发现 `listFromCache` 返回的 `PreOrderActivityProductDTO.scopes`
**恒为 null**——promotion 自己不落 scopes（权威源在 product-server 的
`renewal_pre_order_activity_coupon_scope` 表），但**之前完全没有跨服务读接口去补**，
cart 类头的 TODO 也明确写了这是"promotion 缺口"。

**这是和 detail 缺口完全不同的另一个接口**：`detail()` 是 B 端详情页用的，`listFromCache`
才是 C 端取数用的，两边各自独立没有互相补齐，**这次一次性修了两个**。

**最终方案**：product-server 新增 `POST /feign/preOrderActivity/couponScope/listByActivityNumbers`
（product-server `846a532ab`，返回**扁平行**），按活动号批量查 scope 表；promotion 新增
`PreOrderCouponScopeRemoteService#listByActivityNumbers` 消费（promotion `7be4676b0`），
在 `listFromCache` 里按 `productNumber`(=couponSkuNumber) 回填到对应券商品行。
只映射 `gradeCode`/`subjectCode`，年级学科中文名不需要（cart 只校验这两个字段非空）。

**验证**：直接反射调 `RegistrationService#preRegistration(1, "577431949669312512",
"514762045841821696", null)`，返回 `code:0`，`status:0`（正常），**不再抛异常**。
`product_list` 为空数组是因为这条造出来的测试数据年级学科没有落在三者交集内，
不是回归——修复目标是"scopes 传得到、不抛异常"，交集精确性不是这次要验的东西。

#### 🔥 中间踩了三个坑，全部记进了 README「必须知道的坑」

1. **嵌套 `Map<Long, Map<Long, List<...>>>` 返回类型，FastJson Feign 解码器解不出来**
   （报 `parseLong error`）——改成扁平行 `List<Row>` 规避
2. **Feign 方法返回类型必须对齐对端的 `RestTraceResponse<T>` 信封**，不能声明成裸
   `List<...>`——`save()` 是 void 返回，Feign 压根不走解码，之前一直没暴露这个问题
3. **🔴 最隐蔽的一个**：`promotion` 项目在 test-gtbg-dev-3 有 `promotion-b` 和
   `promotion-c` **两个独立部署**，cart 走的是 `promotion-c`。前两轮反复部署都**只发了
   promotion-b**，promotion-c 一直跑老代码，导致改完代码、部署"成功"、直接反射调
   `listFromCache`(走 promotion-b) 都验证通过了，但 cart 端到端就是不生效——
   **靠 trace_tree 看到 span 里 `gapmApp` 是 `promotion-c.gaotu100.com` 才发现**。
   以后改 promotion 涉及 C 端链路的代码，**两个部署都要发**。

### ✅ couponStatusDesc 本地映射 —— 已修复，永久方案（不是过渡）

**定稿口径**：电商**不会下发**这个字段（2026-09-09 邓俊兵确认"中文展示逻辑你们按需判断展示就行"，
附截图，与 jar 的 `@ApiModelProperty("券状态: 1 使用中 / 2 已失效 / 3 审核中 / 4 已暂停")` 一致），
**本地映射是永久方案**。中间反复过两版（"等电商下发"→"临时本地兜底"→定稿），过程见 [[changelog]] 09-09。

**已实现**（两处都遵循「只补为空字段，电商真给了就不覆盖」，将来电商若开始下发不用改代码）：
- student-center `PreOrderCouponStatusEnum.descOfStatus()`（`daa8c8516`）+
  `PreOrderCouponWrapper#convertCouponVO`
- promotion `PreOrderCouponEnricher.descOfCouponStatus()`（`1083c43cf`），
  `enrich()`/`enrichDTO()` 两条链路都补

## 已解决（2026-09-10 本次会话）

### ✅ B 端 detail 不下发 scopes —— 已修复并端到端实测通过

**根因**（又一处「只在一条链路挂补齐」）：scopes 权威源在 product-server 的
`renewal_pre_order_activity_coupon_scope` 表，promotion 自己不落库。09-09 加的跨服务读取
**只挂在 C 端 `listFromCache`**，B 端 `detail` 这条路径没挂 → 范围明明已落库，
详情页「预报名可用范围」恒显示「未配置」。

**修法**（promotion）：`detail()` 里新增 `fillCouponScopesForDetail()`，走与 C 端同一个远端接口；
把「拉取+分组」「映射」抽成 `loadCouponScopeRows` / `applyCouponScopes` 两个共用方法，
C 端也改为复用 —— 就是因为两条链路各自独立补齐，才先后漏了两次。
另给 `PreOrderActivityCouponScopeDTO` 补 `gradeName`/`subjectName`
（原先只有 code，promotion-management 侧那两个名字字段恒为 null，页面只能显示数字）。

**验证**：活动 `578653392472137728` 经页面接口 `/promotionManagement/preOrderActivity/detail`
返回 `一年级/英语`、`四年级/生物`、`六年级/生物`，与 scope 表 id=12/13/14 逐条对得上。
写入路径同步验过：新建活动落库 → 读回中文名正确；重复组合、空范围两条校验仍正常拦截。

### ✅ 调电商券接口请求体 snake_case，筛选静默失效 —— 已修复并实测通过

**根因**：`SuperSpringConfig` 把 FastJson **全局**命名策略设成 `SnakeCase`（promotion 对外
API 口径，不能动），该全局实例同样作用于 Feign 请求体序列化；jar 的
`ExpandCouponQueryRequest` 没有任何 `@JSONField` → 实际发出
`{"sku_numbers":[..],"page_num":1,"page_size":3}`，而电商只认
`skuNumbers/pageNum/pageSize`。

**为什么极难定位**：未知字段被电商静默忽略 = 等价于「不带筛选」→ HTTP **200**、
`list` **非空**（全量第一页 20 条）→ `queryCoupons` 既不抛异常、也不打
「电商券信息全部取不到」告警（**日志里搜不到任何线索**）→ 但按 skuNumber 匹配全部 miss
→ 券名/券ID/购买金额/状态恒为 null。**只有目标券恰好落在第一页时才「看起来是好的」。**

**定位方式**：在 pod 里用 arthas 调 `JSON.toJSONString(request)` 打出真实请求体
（`vmtool ... --express`），一眼看到 `sku_numbers`。此前靠日志、trace、Apollo 都查不出来。

**修法**（promotion）：新增 `CamelExpandCouponQueryRequest` 继承 jar 入参类，覆写六个 getter
加 `@JSONField(name=camelCase)`（优先级高于全局策略），enricher 里 `new` 换成它。
**改动面 1 个新文件 + 1 处 4 行改动，不碰全局配置，不影响其它 Feign 调用。**

**两个走不通的方案**（别再试）：① 改全局 SnakeCase → 波及 promotion 所有对外接口；
② 换 Feign 编解码器 → jar 把 `configuration` 写死在注解上，且本仓库 spring-cloud 是
**Edgware.SR5，`@FeignClient` 尚无 `contextId`**，同服务名重复声明 bean 名冲突（实测编译即报错）。

**验证**：活动 `578667346476945408`（「造数」，挂 3 张券）修复前券字段全 null，
修复后 B 端 `detail` 与 C 端 `listFromCache` 均完整返回券名/券ID/购买金额/`couponStatus=1 使用中`。
C 端这条尤其关键：**修复前三者交集里的券状态判定拿到的是错的，属资损方向**。

## 已知契约缺口（仍未解决）

| 缺口 | 影响 | 处理 |
|---|---|---|
| 电商 `couponName` 只支持**左匹配**（`like '关键字%'`） | 券选品搜索「口径」「caseSDD」等中间词一律 0 条，运营必须从券名开头输入 | 需推动电商改成 `%关键字%`，**跨团队，尚未提出** |
