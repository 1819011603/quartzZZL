---
title: 续班预报名使用膨胀券 · 验证手册
tags: [需求, 验证]
---

# 验证手册

> 回答一个问题：**想跑一遍，去哪跑、用哪条数据跑。**
> 造好的数据属于当前状态（数据还在库里），所以在这儿而不是 changelog。

## 环境

| 项 | 值 |
|---|---|
| 泳道 | **test-gtbg-dev-3** |
| 数据库实例 | `gaotu_polar_test_03`（cluster_id **142**）· 库 `gaotu` |
| DB 直连 | `gaotu-polar-test03.rwlb.rds.aliyuncs.com` / `gaotu_test_rw` / `gaotu@test2020` |
| 券列表 mock 开关 | Apollo `pre.order.coupon.mock.enabled=true` —— **不开则调真接口必失败**（电商未提供） |
| 券商品类型 | Apollo `pre.order.coupon.product.type=8014`（⚠️ 不是 8027） |

## 造好的测试数据

表 `gaotu.renewal_pre_order_activity_coupon_scope`，5 行（2026-09-08 直连插入）：

| 券商品号 | 活动 | 券ID | 年级 | 学科 | 这条是干嘛的 |
|---|---|---|---|---|---|
| 801400001 | 9001 | 10086 | 21 | 1 | 一张券配两个组合 |
| 801400001 | 9001 | 10086 | 21 | 2 | 同上 |
| 801400002 | 9001 | 10087 | 21 | 4 | 同活动第二张券 |
| 801400001 | **9002** | 10086 | 21 | 1 | **跨活动重复**，验证必须放行 |
| 801400003 | 9003 | 10088 | 11 | 37 | 券已结束，验状态过滤 |

**券商品号与 mock 对齐**：801400001/2/3 正是 `PreOrderCouponMockProvider` 内置的三张券
（暑期50抵200 / 秋季100抵400 / 春季已结束），所以 mock 与库数据能串起来。
**年级学科用的是真值**（21/11、1/2/4/37），取自 `gaotu.renewal_expand_subject_recommend`，与续班域同源。

## 唯一键已验证（两个方向都跑过）

```
跨活动重复   券801400001 的 (21,1) 插到活动 9002  → ✅ 放行
同活动跨券   另一张券在活动 9001 配 (21,1)        → ✅ 被拦
             Duplicate entry '9001-21-1' for key 'uk_act_grade_subject'
```

与定稿口径一致：**活动内唯一、跨活动放行**。DB 层已兜住，应用层校验只为给可读文案。

## 怎么调

```bash
# 查 scope 数据
mcp mysql-query mysql_query cluster_id=142 db_name=gaotu env=test \
  sql="SELECT * FROM gaotu.renewal_pre_order_activity_coupon_scope WHERE is_del=0"

# 反射调 Bean（券列表 / 三者交集），mcp baijia-invoke invoke_service
project=student-center  traffic_env=test-gtbg-dev-3
service_method=com.gaotu.yunying.student.center.app.service.PreOrderCouponBiz#pageQueryCoupon

project=product-server  traffic_env=test-gtbg-dev-3
service_method=com.gaotu.product.service.renewal.preorder.PreOrderCouponIntersectService#intersect
```

**入口类**（README 只写到模块，这里到类）：

| 功能 | 类 |
|---|---|
| 券列表接口 | `student-center-web/.../web/api/PreOrderCouponController.java` |
| 券列表编排 | `student-center-service/.../app/service/PreOrderCouponBiz.java` |
| 券列表 mock | `student-center-adapter/.../acl/impl/PreOrderCouponMockProvider.java` |
| 三者交集（同源实现） | `product-server-domain/.../renewal/preorder/PreOrderCouponIntersectService.java` |
| 券范围校验落库 | `product-server-domain/.../renewal/preorder/PreOrderActivityCouponScopeService.java` |
| 发链接膨胀券 Strategy | `student-center-service/.../roster/content/RenewalPreRegistrationCouponStrategy.java` |
| C 端落地页组装 | `cart-app/.../renewal/preregistration/PreRegistrationCouponAssembler.java` |

## 能验到哪一层

- ✅ **可验**：券列表筛选与分页（走 mock）、券范围落库与唯一键校验、三者交集算法、
  发链接 path 切到 `/preSignUpCoupon`、订金班不回归
- ❌ **验不了**：券真实名称/金额/状态（**电商券商品接口未提供**）、
  C 端 `price`（上游只有抵扣额、无购买金额，当前恒返 0 并打 error）、
  B 端活动详情回显券字段（promotion 表无券列）
- ⚠️ 别把"上游没给"误判成"自己写错了" —— 上面三条现在就是空/0，是预期行为

## 新建的东西（上线 checklist 原料）

| 类型 | 名称 | 位置 / 值 | 测试 | 线上 |
|---|---|---|---|---|
| 表 | `renewal_pre_order_activity_coupon_scope` | `gaotu_polar_test_03` · 库 gaotu | ✅ 已建（直连，未走工单） | 待建（马胜或提工单） |
| Apollo | `pre.order.coupon.mock.enabled` | false | 待配 | **不要配**（mock 仅测试用） |
| Apollo | `pre.order.coupon.product.type` | 8014 | 待配 | 待配 |
| Apollo | `renewal.content.config.map` | 加膨胀券 reportCode | 待配 | 待配（**不配则老师端无入口**） |
| Apollo | `renewal.cStyle.preRegistrationCoupon.bgUrl` | 暂用订金班图 | 待配 | 待运营给图 |
| Apollo | `pre.order.activity.coupon.renewalPlanIds` | 空 | 可选 | 白名单，用于强制判膨胀券自测 |
| 代课权限 | `/renewal/pre/coupon/list`、`/couponScope/list` | sd.baijia.com | 待登记 | 待登记 |
