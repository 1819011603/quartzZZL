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
| 券 ID | `578534533350174720` | 券定义标识 |
| 券商品 ID | `578534533488603137` | 活动商品 `productNumber`/`skuId` |
| 券范围 | grade `19`、subject `6` | 三者交集 |
| 续班计划 | `577431949669312512` | B/C 范围过滤 |
| 前置班/课程 | `514762045841821696` | C 端推荐入参 |
| 预警数据 | `questionnaire_inspect.id=261` | `postProductId`/`postProductName` 验证 |

测试前先查询上述数据仍存在且状态满足用例。共享数据不得直接假定保持不变。

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
- `total` 与返回列表一致；2026-09-14 最近一次有效实测为 `total=23`。
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

## 待补边界验证

### 售罄券

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
