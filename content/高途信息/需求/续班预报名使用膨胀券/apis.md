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
| student-center | `/renewal/pre/coupon/list` | `PreOrderCouponController` → `PreOrderCouponBiz#pageQueryCoupon` | 新增 | B 端券选品列表，**已接真实电商数据**（mock 已删） | 老师端选品弹窗 | ✅ 自测通过（total=79，模糊查/精确查均正常） |
| student-center | `/renewal/pre/couponScope/list` | `PreOrderCouponController` | 新增 | 券可用范围查询 | 老师端 | ✅ 自测通过 |
| product-server | 券范围落库/校验 | `PreOrderActivityCouponScopeService` | 新增 | 活动级唯一键 `uk_act_grade_subject` | B 端活动配置保存 | ✅ 自测通过 |

**状态枚举**：`设计中` / `已编码` / `自测通过` / `联调通过` / `已上线`

## 内部方法契约（跨模块）

| 服务 | 类#方法 | 变更类型 | 改了什么 | 谁在调 |
|---|---|---|---|---|
| product-server | `PreOrderCouponIntersectService#intersect` | 新增 | 三者交集，按「年级+学科」成对判定 | C 端落地页取数 |
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

#### 🔥 中间踩了三个坑，全部记进了 README「必须知过的坑」

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

**口径反转两次**：白天定"不做本地兜底、等电商下发"；晚上先改成"电商下发前本地按 jar
注释映射"；再后来电商邓俊兵在群里直接确认"中文展示逻辑你们按需判断展示就行"（附截图，
与反编译 jar 的 `@ApiModelProperty("券状态: 1 使用中 / 2 已失效 / 3 审核中 / 4 已暂停")`
注释完全一致）——**电商不会下发这个字段，本地映射是永久方案**。

**已实现**：
- student-center `PreOrderCouponStatusEnum.descOfStatus()`（`daa8c8516`）+
  `PreOrderCouponWrapper#convertCouponVO` 优先透传电商值、为空再本地补
- promotion `PreOrderCouponEnricher.descOfCouponStatus()`（`1083c43cf`），
  `enrich()`/`enrichDTO()` 两条链路（B 端 detail + C 端缓存重建）都补

两处都遵循"只补为空字段，电商真给了就不覆盖"的规则，万一电商哪天真的开始下发，
不用改代码也能自动切换成透传。

## 已知契约缺口（仍未解决）

目前没有已知的未解决契约缺口。
