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
| promotion-b | `/domain/promotion/b/preOrderActivity/detail` | `PreOrderActivityService#detail` | 字段新增 | 返回体 product 项加 7 个券字段：`couponId`/`couponName`/`skuId`/`buyAmount`/`couponStatus`/`couponStatusDesc`/`scopes` | B 端活动详情页 `/promotionManagement/preOrderActivity/detail`；product-server `PromotionAclService#getPreOrderActivityDetail` | 🔴 **已编码但未生效**，见下方缺口 |
| promotion-c | `/domain/promotion/c/preOrderActivity` | `PreOrderActivityDomainServiceImpl#listVisibleActivityByNumbersFromCache` | 字段新增 | 缓存 DTO 带券字段；缓存 miss 从 DB 重建时由 `PreOrderCouponMockEnricher` 补齐 | cart `PreRegistrationCouponAssembler`；product-server `PreOrderCouponIntersectService` | 已编码（**测试环境开关未配，等于没生效**） |
| student-center | `/renewal/pre/coupon/list` | `PreOrderCouponController` → `PreOrderCouponBiz#pageQueryCoupon` | 新增 | B 端券选品列表，走 mock | 老师端选品弹窗 | ✅ 自测通过 |
| student-center | `/renewal/pre/couponScope/list` | `PreOrderCouponController` | 新增 | 券可用范围查询 | 老师端 | ✅ 自测通过 |
| product-server | 券范围落库/校验 | `PreOrderActivityCouponScopeService` | 新增 | 活动级唯一键 `uk_act_grade_subject` | B 端活动配置保存 | ✅ 自测通过 |

**状态枚举**：`设计中` / `已编码` / `自测通过` / `联调通过` / `已上线`

## 内部方法契约（跨模块）

| 服务 | 类#方法 | 变更类型 | 改了什么 | 谁在调 |
|---|---|---|---|---|
| product-server | `PreOrderCouponIntersectService#intersect` | 新增 | 三者交集，按「年级+学科」成对判定 | C 端落地页取数 |
| promotion | `PreOrderCouponMockEnricher#enrich` | 新增 | 券字段 mock 补齐，**仅挂在缓存重建路径** | `PreOrderActivityDomainServiceImpl:238` |

## 🔴 已知契约缺口

| 缺什么 | 哪个接口 | 现在怎么顶 | 谁负责补 | 上线前必须 |
|---|---|---|---|---|
| 券名/金额/状态**权威数据** | 电商券商品接口 | `PreOrderCouponMockEnricher` + student-center `PreOrderCouponMockProvider` | 邓俊兵（电商） | 换真实 ACL 调用，删两处 mock，开关置 false |
| **B 端 detail 拿不到券字段** | `promotion-b .../preOrderActivity/detail` | ❌ **无兜底，直接返回 null** | 我方（本需求内） | 必须修，见下 |

### 缺口详情：B 端 detail 券字段全空（2026-09-09 实测复现）

**现象**：HTTP 200，页面能开，但券行的名称/金额/状态全是空 —— 「微坏」。
traceId `2d0e9489-5562-4963-9aa2-4d111707dbf9.0.3`（无 error span，全链路 200）。

**实测**（活动 `578363764011708416`，泳道 test-gtbg-dev-3 反射调用 `PreOrderActivityService#detail`）：

```json
{"id":916,"pre_order_activity_number":578363764011708416,
 "product_number":801400001,"product_type":8014,"deductible_amount":20000}
```

只有 5 个 DB 列，7 个券字段**一个都没有**。

**根因是挂载点缺口，不是新 bug**：

| 路径 | 数据源 | 有没有过 enricher |
|---|---|---|
| C 端 `listVisibleActivityByNumbersFromCache` | 缓存 miss → DB 重建 | ✅ 有（`PreOrderActivityDomainServiceImpl:238`） |
| **B 端 `detail()`** | **直接读 DB** `preOrderActivityProductRepository.getByPreOrderActivityNumber` | ❌ **没有** |

表只有 8 列、无券列（这是「不加列」的既定口径，没错），所以 BO→DTO 拷过来的券字段必然是 null。
`convertPreOrderActivityProductDTO` 该 set 的都 set 了，只是源头就是空的。

**两个附带发现**：

1. **promotion 的 mock 开关压根没配** —— `pre.order.coupon.mock.enabled` 在
   `promotion.gaotu100.com`/TEST **不存在**（默认 false）。verify.md 记的「✅ 已发布」
   是 **student-center 那个**，promotion 这个从没配过 → **C 端缓存重建路径现在也没在补齐**。
2. **scope 表没有真活动的数据** —— 5 行全是假活动号 9001/9002/9003，
   真活动 `578363764011708416` 一行没有 → 就算 enricher 修好，`scopes` 仍然为空。

**修法（待定，见 README 下一步）**：把 `enrich()` 也挂到 `detail()` 的 DB 读出口，
与缓存重建路径同源。注意 `detail()` 在 promotion-app、enricher 在 promotion-domain，
挂载点选在 repository 出口还是 app 层需确认分层。
