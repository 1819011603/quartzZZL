---
title: 续班预报名使用膨胀券 · 验证手册
tags: [需求, 验证]
---

# 验证手册

> 只保留当前可执行条件、仍有效数据和最新预期。接口字段结构见 `apifox-openapi.json`。

## 环境

| 项 | 当前值 |
|---|---|
| 本需求泳道 | `test-gtbg-dev-3` |
| coupon-a 泳道 | `test-eco-7` |
| 逻辑环境 | 两个泳道均为 dev；查 pod 使用 `--env dev` |
| 请求头 | `traffic-env: test-gtbg-dev-3` |
| 数据库 | `gaotu_polar_test_03`，cluster_id `142`；scope 表在 `gaotu` 库，活动主数据在 `promotion` 库 |
| 商品类型 | Apollo `pre.order.coupon.product.type=8014` |

验证镜像前先确认目标服务 eureka UP。promotion 涉及 C 端时同时确认 promotion-b 与 promotion-c。

## 登录

测试环境不发送短信，登录前写入一次性验证码：

```bash
cd "脚本"
python3 set_test_smscode.py --mobile 17900911102 --client 613156985,613156986 --clear-limit
```

页面使用手机号 `17900911102`、验证码 `1234`。登录成功后验证码会被删除，下次登录重新执行脚本。

## 当前测试数据

| 对象 | 值 | 用途 |
|---|---|---|
| 膨胀券活动 | `578563007821410304` | B 端详情、C 端推荐 |
| 膨胀券活动(已换新券) | `578842182125903872` | 绑定计划 `578668076965308416`，3 张券已于 2026-09-14 全量换成新券 |
| 续班计划(新券) | `578668076965308416` | 六年级 数学/英语/语文 三槽位 |
| 券 ID | `578534533350174720` | 券定义标识 |
| 券商品 ID | `578534533488603137` | 活动商品 `productNumber`/`skuId` |
| 券范围 | grade `19`、subject `6` | 三者交集 |
| 续班计划 | `577431949669312512` | B/C 范围过滤 |
| 前置班/课程 | `514762045841821696` | C 端推荐入参 |
| 预警数据 | `questionnaire_inspect.id=261` | `postProductId`/`postProductName` 验证 |

测试前先查询上述数据仍存在且状态满足用例。共享数据不得直接假定保持不变。

### 计划 `578668076965308416` 当前绑定的券（2026-09-14 换新后）

| 槽位 | couponId | 券商品 ID | 券名 | 已售/总量 | 持有上限 | 买价/抵扣(分) |
|---|---|---|---|---|---|---|
| 六年级数学(16,1) | `579417711627513856` | `579417711732357121` | Q1 | 0/20 | 3 | 2000 / 6000 |
| 六年级英语(16,4) | `579426455071498240` | `579426455627266049` | 膨胀券-脚本 | 0/10 | 1 | 10000 / 20000 |
| 六年级语文(16,5) | `579394599487844352` | `579394599632533505` | Q8 | 3/10 | 3 | 2000 / 6000 |

三张全部 `使用中/开售中`、`selectable=true`。原先的 caseSDD 三张券已全部替换下线。

### 可用膨胀券（2026-09-14 实测，`使用中` + `开售中`）

`/renewal/pre/coupon/list` 不传 `renewMasterNumber` 时 `total=40`，**全部** `couponStatus=1`
且 `saleStatus=2`、`selectable=true`。下面是挑出来常用的几张，按“还能买多少”排序：

| couponId | 券商品 ID(skuNumber) | 券名 | 已售/总量 | 持有上限 | 买价/抵扣(分) | 备注 |
|---|---|---|---|---|---|---|
| `578839415256780800` | `578839415380715521` | zks | 0/100000 | 1 | 100 / 200 | 库存几乎无限，**跑量首选** |
| `579417711627513856` | `579417711732357121` | Q1 | 0/20 | 3 | 2000 / 6000 | 用户指定；`holdLimit=3` 可测多次持有 |
| `579426455071498240` | `579426455627266049` | 膨胀券-脚本 | 0/10 | 1 | 10000 / 20000 | 金额较大，测算价明显 |
| `579394599487844352` | `579394599632533505` | Q8 | 3/10 | 3 | 2000 / 6000 | 已有销量，测部分售出 |
| `579394549091184640` | `579394549208610817` | Q1 | 8/20 | 3 | 2000 / 6000 | 同名不同券，测重名场景 |

⚠️ 这批券**没有一张是售罄的**（`soldCount < totalCount`），
因此 **T-33 的售罄用例仍未解锁**，见「待补边界验证 / 售罄券」。

重新拉取当前可用券：

```bash
curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" \
  'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
  -H 'Content-Type: application/json' -H 'traffic-env: test-gtbg-dev-3' \
  -d '{"pageNum":1,"pageSize":50}'
```

### ⚠️ 下单必须在 `test` 泳道

下单链路要求走 `test` 泳道，但 **`test` 跑的是 master 镜像，没有本需求代码**，2026-09-14 实测：

- `traffic-env: test` 调 `/renewal/pre/coupon/list` → `404 Not Found`。
- `traffic-env: test` 反射 `PreOrderCouponAclService` → 「未找到服务…的实现类」。

券数据在 coupon-a，是跨泳道共享的，所以上表这些券在 `test` 同样存在；
缺的是**本需求的代码**。要在 `test` 下单，必须先把相关服务发一版到 `test`，
否则只能在 `test-gtbg-dev-3` 验证到加购之前的链路。

### mock 支付页面（2026-09-14 实测可用）

下单后需要支付才能推进订单状态时，用速搭的 mock 支付页，不用走真实支付：

https://sd.baijia.com/projectItem/myreview/79ab6125-96cb-4da3-a944-ab32f5772dc1/4e76c321-2ace-45d3-a387-0b5973ef4096

用法：环境选 `test`，订单号填**批次单号**，点「支付」。返回 `结果=成功` 并带
`pay_order_number` 和 `rid` 即支付成功。

⚠️ 这里的「订单号」不是下单返回的订单号，是 **OES 付款记录页的批次单号**。
取法：OES → 订单管理 → 付款记录，用学员 userId 或手机号查批次单列表，取对应批次单号。

2026-09-14 实测记录：批次单号 `428826139177255000` → 成功，
`pay_order_number=102609142523008272`、`rid=ec28a8c4b5db832f77cdee44bbff2ef5`。

## 核心验证

### B 端券列表

```bash
curl -X POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
  -H 'Content-Type: application/json' \
  -H 'traffic-env: test-gtbg-dev-3' \
  -d '{"renewMasterNumber":"577431949669312512","pageNum":1,"pageSize":20}'
```

预期：

- 只返回三者交集范围内的券。
- 每条同时满足默认 `couponStatus=1`、`saleStatus=2`。
- `total` 与返回列表一致。不传 `renewMasterNumber` 时 2026-09-14 实测 `total=35`；
  传 `577431949669312512` 当前实测为 `0`（命中券 `saleStatus=1` 被白名单滤掉，非缺陷，见下方排查口径）。
- `availableScope` 为年级学科文案，`holdLimit` 为字符串，`creator` 为姓名或兜底工号。
- 不传 `renewMasterNumber` 时不做续班计划范围过滤，但状态过滤仍生效。

### B 端活动详情

使用反射调用：

```text
project=promotion
traffic_env=test-gtbg-dev-3
service_method=com.gaotu.promotion.app.service.preorder.PreOrderActivityService#detail
params=[{"number":"578563007821410304"}]
```

预期：券 ID、券名、商品 ID、金额、双状态、状态文案、创建人和 scopes 均完整。

### C 端推荐

```text
project=cart
traffic_env=test-gtbg-dev-3
service_method=com.gaotu.renewal.RegistrationService#preRegistration
params=[1,"577431949669312512","514762045841821696",null]
```

预期：活动形式为膨胀券；商品命中三者交集与双状态白名单；价格和抵扣金额非空。

### 范围唯一键

- 同活动的相同年级学科组合：保存失败。
- 不同活动使用相同券和年级学科组合：保存成功。
- 唯一键：`uk_act_grade_subject(activity_number, grade_code, subject_code)`。

### 券列表返回空的排查口径（2026-09-14 实测）

`/renewal/pre/coupon/list` 传 `renewMasterNumber` 返回 `total=0` 时，按下面顺序定位，
**不要先怀疑三者交集或解码器**：

1. 直调 product-b `/feign/preOrderActivity/couponScope/listDisplayableByRenewalPlan`
   （服务名 `PRODUCT-B`，⚠️ 入参字段是 `renewMasterNumber`，**不是** `renewalPlanNumber`；
   19 位 ID 传字符串）。返回非空即交集正常。
2. 拿交集返回的 `coupon_sku_number`，用 `couponSkuNumberList`（**不是** `couponSkuNumbers`，
   写错字段名会被静默忽略并返回全量，极易误判成"过滤没生效"）查列表。
3. 仍为空则直查 coupon-a：反射 `PreOrderCouponAclService#pageQueryCoupon`，
   看这些券的 `couponStatus` / `saleStatus` 真实值。

⚠️ **反射桥的 19 位 ID 必须传字符串**：传数字会被截断（实测
`578667318880518144` → `578667318880518100`），交集因此返回 `empty=true`，
看起来像"没配范围"，其实是入参已经不是那个 ID 了。

### 🔴 券展示的两个数据源必须同时满足（2026-09-14 踩坑）

一张券要出现在 `/renewal/pre/coupon/list`，**两处都要有它**：

1. `gaotu.renewal_pre_order_activity_coupon_scope` —— 范围行（年级+学科）
2. **promotion 活动的商品列表** `promotion.pre_order_activity_product` —— 活动商品行

`PreOrderCouponIntersectService` 先取活动详情拿商品列表，再拿范围行求交，
**只改 scope 表不改活动商品，券会在交集阶段被丢掉**（实测：只改 scope 表后列表从 3 张掉到 1 张）。
所以换券必须走 promotion 的 `/preOrderActivity/edit`，由它在事务内回调 product-b 写范围。

### 槽位数量上限

券能展示几张，由**交集出来的「年级+学科」对数**决定，不是想加几张就加几张：

- 唯一键 `uk_act_grade_subject(activity_number, grade_code, subject_code)`
  ⇒ **一个「活动 + 年级 + 学科」只能放一张券**。
- 计划 `578668076965308416` 实测 `post_grades=[16]`、`post_subjects=[1,4,5]`
  ⇒ 六年级 × 数学/英语/语文，**只有 3 个槽位**，最多展示 3 张券。

要展示更多券，只能换一个后置学科更多的续班计划，或新建活动绑到别的计划。

### 进行中的活动怎么改券

活动 `activity_status=3`（进行中）时 `/preOrderActivity/edit` 只允许改结束时间
（`validateActivityStatusForEdit`，只有 `0 待发布` 能全字段编辑）。
测试环境换券的做法（2026-09-14 实测可行）：

```sql
-- 1. 临时改成待发布
UPDATE promotion.pre_order_activity SET activity_status=0 WHERE number=578842182125903872;
-- 2. 调 /preOrderActivity/edit（beginTime 必须晚于当前时间，否则报"活动开始时间必须大于当前时间"）
-- 3. 改回进行中并还原时间窗
UPDATE promotion.pre_order_activity SET activity_status=3,
  begin_time='2026-09-11 10:35:13', end_time='2026-09-29 10:30:13'
WHERE number=578842182125903872;
```

## 待补边界验证

### 售罄券

⚠️ 2026-09-14 复查：当前 40 张可用券**全部未售罄**（见「可用膨胀券」表），
最接近的是 `579394549091184640`（8/20）。仍需造数或把某张券买到售罄。
`578839415256780800` 总量 100000，不适合用来刷售罄；
优先挑 `totalCount=5` 的小库存券（如 `579394614104993792` 券 Q13，1/5）买满。

准备 `couponStatus=1` 且 `sold_count >= total_amount` 的真实券：

1. `/renewal/pre/coupon/list` 返回该券时 `selectable=false`。
2. `/promotionManagement/preOrderActivity/editAndPublish` 添加该券时返回“膨胀券已售罄，不可添加”。
3. 库存判据以 coupon-a 返回为准，不使用 OES 活动缓存中的已售/总量。

### 满班课程

准备 `capacity>0` 且 `signUpCount>=capacity` 的班级：

1. 订金班活动保存时报“班级班容已满，不可添加”。
2. 使用 `capacity=-1` 的班级回归，必须允许保存。

### 持有上限

- `holdLimit>0` 返回数字字符串。
- `holdLimit=0` 返回“不限”。

## 反射桥地址

| 服务 | 地址 |
|---|---|
| student-center | `https://test-fuwu.baijia.com/bgwApi/component/student-center/test/acl/compare/service` |
| promotion-b | `https://test-fuwu.baijia.com/bgwApi/promotion/b/test/acl/compare/service` |
| product-b | `https://test-fuwu.baijia.com/bgwApi/product-b/b/test/acl/compare/service` |
| cart | `https://test-api.gaotu100.com/cart/test/acl/compare/service` |

网关前缀以 `baijia_invoke.py` 的 `ROUTE_MAP` 为准。19 位 ID 一律使用字符串。

## 上线配置

| 类型 | 名称 | 上线要求 |
|---|---|---|
| MySQL | `renewal_pre_order_activity_coupon_scope` | 线上建表；`pre_order_activity_product` 不加列 |
| Apollo | `pre.order.coupon.product.type` | `8014` |
| Apollo | `renewal.content.config.map` | 增加膨胀券 reportCode，否则老师端无入口 |
| Apollo | `renewal.cStyle.preRegistrationCoupon.bgUrl` | 配置最终背景图 |
| Apollo | student-center `pre.order.coupon.display.couponStatus` / `.saleStatus` | 默认 `1` / `2` |
| Apollo | cart `preRegistration.coupon.display.couponStatus` / `.saleStatus` | 默认 `1` / `2` |
| Apollo | 三个 `AclServiceCompareController.enabled` | promotion、cart、product-server 均显式设为 `false` |
| 代课权限 | `/renewal/pre/coupon/list`、`/renewal/pre/couponScope/list` | 上线前登记 |

## 页面复现

1. 打开 `https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/pre-register-activity`。
2. 确认前端分支包含 `feature-expand-coupon`，请求头泳道为 `test-gtbg-dev-3`。
3. 新建活动，活动形式选“膨胀券预报名”，活动开始时间必须晚于当前时间。
4. 添加当前状态符合白名单的券，配置年级和学科范围后保存。
5. 编辑详情应完整回显券字段和范围；scope 表应按活动/年级/学科保持唯一。
