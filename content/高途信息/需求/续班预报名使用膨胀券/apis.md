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
| promotion-c | `POST /domain/promotion/c/preOrderActivity/listFromCache` | `PreOrderActivityService#listFromCache` | 字段新增 | 返回体 product 项补齐 `scopes`（新增内部方法 `fillCouponScopes`，调 product-server 新接口） | cart `PreRegistrationCouponAssembler#resolveCouponScope`（之前必抛「膨胀券可用范围缺失」） | 🟡 **2026-09-09 已编码并 push，部署验证中** |
| product-server(b) | `POST /feign/preOrderActivity/couponScope/listByActivityNumbers` | `PreOrderCouponScopeFeignController#listByActivityNumbers` | 新增 | 按活动号批量查 scopes，返回 `activityNumber -> (couponSkuNumber -> scopes)`，供 promotion 的 `listFromCache` 消费 | promotion `PreOrderCouponScopeRemoteService` | 🟡 **2026-09-09 已编码并 push，部署验证中** |
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

`scopes` 与 `couponStatusDesc` 仍是 null（**符合设计**，不在这次修复范围）：
- `couponStatusDesc`：电商目前不下发，本地不做兜底翻译
- `scopes`：权威源在 product-server，见下一条

### 🟡 C 端 listFromCache 不下发 scopes —— 已编码，部署验证中

**发现过程**：测 cart 的 `preRegistration` 推荐接口时，子 agent 造数据打通了续班计划关联，
链路推进到膨胀券分支后卡在 `PreRegistrationCouponAssembler#resolveCouponScope` 抛异常
「膨胀券可用范围缺失」。追查发现 `listFromCache` 返回的 `PreOrderActivityProductDTO.scopes`
**恒为 null**——promotion 自己不落 scopes（权威源在 product-server 的
`renewal_pre_order_activity_coupon_scope` 表），但**之前完全没有跨服务读接口去补**，
cart 类头的 TODO 也明确写了这是"promotion 缺口"。

**这是和 detail 缺口完全不同的另一个接口**：`detail()` 是 B 端详情页用的，`listFromCache`
才是 C 端取数用的，两边各自独立没有互相补齐，**这次一次性修了两个**。

**修法**：product-server 新增 `POST /feign/preOrderActivity/couponScope/listByActivityNumbers`
（product-server `9b53b5a32`），按活动号批量查 scope 表；promotion 新增
`PreOrderCouponScopeRemoteService#listByActivityNumbers` 消费，在 `listFromCache` 里
按 `productNumber`(=couponSkuNumber) 回填到对应券商品行（promotion `e9053ab65`）。
只映射 `gradeCode`/`subjectCode`，年级学科中文名不需要（cart 只校验这两个字段非空）。

**状态**：两边已 push，部署到 test-gtbg-dev-3 中，**还没有重新跑一遍 cart 的 `preRegistration`
验证是否真的解决**——下一个会话/等部署完成后优先做这件事。

## 已知契约缺口（仍未解决）

| 缺什么 | 哪个接口 | 现在怎么顶 | 谁负责补 | 上线前必须 |
|---|---|---|---|---|
| `couponStatusDesc` 文案 | 电商券商品接口 | 不兜底，恒为 null | 邓俊兵（电商） | 产品决策：推电商补字段，或改口径允许本地翻译 |
