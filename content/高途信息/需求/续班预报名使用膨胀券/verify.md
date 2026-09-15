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
| 续班计划 | `577431949669312512` | B/C 范围过滤 |
| 前置班/课程 | `514762045841821696` | C 端推荐入参 |
| 预警数据 | `questionnaire_inspect.id=261` | `postProductId`/`postProductName` 验证 |

测试前先查询上述数据仍存在且状态满足用例。共享数据不得直接假定保持不变。

### 小班课链路（2026-09-15 建，K-TC0014 用）

> 造法与大班课的差异见 [[build-data]] 第 13 节；**小班课课程/班级在 `course_center` 库，不在 `gaotu`**。

| 对象 | 编号 | 名称 |
|---|---|---|
| 续班计划 | `579596447754823680` | zzl-小班课续班膨胀券-0915（`type=2`，status=0 未发布） |
| 前置课程 | `579596056986261504` | zzl-小班课续班膨胀券-前置-六年级数学-0915（biz `16SX26CKTA3`） |
| 前置班级 | `579596144554940416` | zzl-小班课续班膨胀券-前置班-六年级数学-0915 |
| 后置课程 | `579596212490082304` | zzl-小班课续班膨胀券-后置-六年级数学-0915 |
| 后置班级 | `579596250695997440` | zzl-小班课续班膨胀券-后置班-六年级数学-0915 |
| 预报名流程 | `579596549208745984` | type=3 |
| └ 预报名配置节点 | `579596549215037440` | type=4，活动绑在这里 |
| └ 链接发放节点 | `579596549215037441` | type=5 |
| 膨胀券活动 | `579601011014926336` | zzl-小班课膨胀券活动-0915，挂券 Q1（六年级·数学） |

计划年级学科：`COURSE_GRADE=16` / `COURSE_SUBJECT=1`（六年级·数学），学年 2026、目标学期 X，部门 10007722。

🔴 **仍缺**：前置/后置班级**都没有学员**（`course_center.clazz_student` 0 行），也没有辅导班/带班老师。
学员就绪前，B 端花名册与三者交集里的 `pre_subjects` 都是空的，K-TC0014 跑不了。

### 计划 `578668076965308416` 当前绑定的券

| 槽位 | couponId | 券商品 ID | 券名 | 已售/总量 | 持有上限 | 买价/抵扣(分) |
|---|---|---|---|---|---|---|
| 六年级数学(16,1) | `579417711627513856` | `579417711732357121` | Q1 | 0/20 | 3 | 2000 / 6000 |
| 六年级英语(16,4) | `579426455071498240` | `579426455627266049` | 膨胀券-脚本 | 0/10 | 1 | 10000 / 20000 |
| 六年级语文(16,5) | `579394599487844352` | `579394599632533505` | Q8 | 3/10 | 3 | 2000 / 6000 |

三张全部 `使用中/开售中`、`selectable=true`。

### 可用膨胀券（`使用中` + `开售中`）

`/renewal/pre/coupon/list` 不传 `renewMasterNumber` 时 `total=40`，**全部** `couponStatus=1`
且 `saleStatus=2`、`selectable=true`。常用两张：

| couponId | 券商品 ID(skuNumber) | 券名 | 已售/总量 | 持有上限 | 买价/抵扣(分) | 备注 |
|---|---|---|---|---|---|---|
| `578839415256780800` | `578839415380715521` | zks | 0/100000 | 1 | 100 / 200 | 库存几乎无限，**跑量首选** |
| `579417711627513856` | `579417711732357121` | Q1 | 0/20 | 3 | 2000 / 6000 | 用户指定；`holdLimit=3` 可测多次持有 |

⚠️ 当前 40 张可用券**没有一张是售罄的**（`soldCount < totalCount`），
**T-33 的售罄用例仍未解锁**，见「待补边界验证 / 售罄券」。

重新拉取当前可用券：

```bash
curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" \
  'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
  -H 'Content-Type: application/json' -H 'traffic-env: test-gtbg-dev-3' \
  -d '{"pageNum":1,"pageSize":50}'
```

### ⚠️ 下单必须在 `test` 泳道

下单链路要求走 `test` 泳道，但 **`test` 跑的是 master 镜像，没有本需求代码**：
`traffic-env: test` 调 `/renewal/pre/coupon/list` → `404`；反射 `PreOrderCouponAclService` → 找不到实现类。
券数据在 coupon-a 跨泳道共享，缺的是**本需求的代码**——要在 `test` 下单，必须先把相关服务发一版到 `test`，
否则只能在 `test-gtbg-dev-3` 验证到加购之前的链路。

### mock 支付页面

下单后需要支付才能推进订单状态时，用速搭的 mock 支付页，不用走真实支付：

https://sd.baijia.com/projectItem/myreview/79ab6125-96cb-4da3-a944-ab32f5772dc1/4e76c321-2ace-45d3-a387-0b5973ef4096

用法：环境选 `test`，订单号填**批次单号**（⚠️ 不是下单返回的订单号，是 OES 订单管理→付款记录页里
按学员 userId/手机号查到的批次单号），点「支付」，返回 `结果=成功` 并带 `pay_order_number`/`rid` 即成功。

## 核心验证

### B 端券列表

```bash
curl -X POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
  -H 'Content-Type: application/json' \
  -H 'traffic-env: test-gtbg-dev-3' \
  -d '{"renewMasterNumber":"577431949669312512","pageNum":1,"pageSize":20}'
```

预期：只返回三者交集范围内的券，每条同时满足默认 `couponStatus=1`、`saleStatus=2`，`total` 与列表一致；
`availableScope` 为年级学科文案、`holdLimit` 为字符串、`creator` 为姓名或兜底工号；不传 `renewMasterNumber`
时不做续班计划范围过滤但状态过滤仍生效。传 `577431949669312512` 返回 `total=0` 属正常（命中券
`saleStatus=1` 被白名单滤掉，非缺陷），见下方排查口径。

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

### 券列表返回空的排查口径

`/renewal/pre/coupon/list` 传 `renewMasterNumber` 返回 `total=0` 时，**不要先怀疑三者交集或解码器**，按序定位：

1. 直调 product-b `/feign/preOrderActivity/couponScope/listDisplayableByRenewalPlan`（服务名 `PRODUCT-B`，
   ⚠️ 入参字段是 `renewMasterNumber` 不是 `renewalPlanNumber`；19 位 ID 传字符串）。返回非空即交集正常。
2. 拿交集返回的 `coupon_sku_number`，用 `couponSkuNumberList`（不是 `couponSkuNumbers`，写错字段名会被
   静默忽略并返回全量，极易误判成"过滤没生效"）查列表。
3. 仍为空则直查 coupon-a：反射 `PreOrderCouponAclService#pageQueryCoupon`，看券的真实状态值。

⚠️ 反射桥的 19 位 ID 必须传字符串，传数字会被截断（`578667318880518144` → `578667318880518100`），
交集因此误判为 `empty=true`。

### 🔴 券展示的两个数据源必须同时满足

一张券要出现在 `/renewal/pre/coupon/list`，两处都要有它：`gaotu.renewal_pre_order_activity_coupon_scope`
（范围行）与 promotion 活动的商品列表 `promotion.pre_order_activity_product`（活动商品行）。
`PreOrderCouponIntersectService` 先取活动详情拿商品列表，再拿范围行求交，**只改 scope 表不改活动商品，
券会在交集阶段被丢掉**。所以换券必须走 promotion 的 `/preOrderActivity/edit`，由它在事务内回调 product-b 写范围。

### 槽位数量上限

券能展示几张，由**交集出来的「年级+学科」对数**决定：唯一键
`uk_act_grade_subject(activity_number, grade_code, subject_code)` ⇒ 一个「活动+年级+学科」只能放一张券。
计划 `578668076965308416` 的 `post_grades=[16]`、`post_subjects=[1,4,5]` ⇒ 六年级×数学/英语/语文，只有
3 个槽位。要展示更多券，只能换一个后置学科更多的续班计划，或新建活动绑到别的计划。

### 进行中的活动怎么改券

活动 `activity_status=3`（进行中）时 `/preOrderActivity/edit` 只允许改结束时间
（`validateActivityStatusForEdit`，只有 `0 待发布` 能全字段编辑）。测试环境换券：先把
`activity_status` 临时改成 `0`，调 `/preOrderActivity/edit`（`beginTime` 必须晚于当前时间），
再改回 `3` 并还原原时间窗（`578842182125903872` 的原窗口：
`2026-09-11 10:35:13` ~ `2026-09-29 10:30:13`）。

## 待补边界验证

### 售罄券

当前 40 张可用券全部未售罄（见「可用膨胀券」表），需造数：优先挑小库存券
（如 `579394614104993792`，1/5）买满，`578839415256780800` 总量 100000 不适合拿来刷售罄。

用 `couponStatus=1` 且 `sold_count >= total_amount` 的真实券验证：`/renewal/pre/coupon/list` 返回该券
时 `selectable=false`；`/promotionManagement/preOrderActivity/editAndPublish` 添加该券时报"膨胀券已售罄，
不可添加"；库存判据以 coupon-a 返回为准，不使用 OES 活动缓存中的已售/总量。

### 满班课程

用 `capacity>0` 且 `signUpCount>=capacity` 的班级验证：订金班活动保存时报"班级班容已满，不可添加"，
`capacity=-1` 的班级必须允许保存（回归）。

### 持有上限

- `holdLimit>0` 返回数字字符串。
- `holdLimit=0` 返回“不限”。

### 🔴 券与订金班并存（取并集）—— 零数据覆盖

需求第 73/74/75 行都写了「两种方式都配置，**取并集**」，代码实现了，但**线上线下都没有一条这样的数据**，
这条规则从未被真实数据走过。2026-09-15 实测（test，cluster 149 `ees_data`）：

| 表 | 总行数 | 学员数 | 有效行(is_del=0) |
|---|---|---|---|
| `dws_fuwu_clazz_user_presale_coupon`（券） | 9 | **2** | 9 |
| `dws_fuwu_clazz_user_presale_subject`（订金班） | 415 | 259 | 339 |
| `dws_fuwu_small_clazz_user_presale_subject`（小班） | 79 | 66 | 76 |

按「学员 + 学年 + 学期」join 两张表，`is_del=0` 的交集为 **0 行**——券的 2 个学员与订金班的 259 个学员完全不重叠。

并集发生在 `PresaleSubjectServiceImpl#refreshByUserTermYear`：两张表捞进同一个 list，
`presaleStatus` 用 `anyMatch`、`presaleSubject` 用 `flatMap + distinct`，天然并集。
**粒度是「学员 + 学年 + 学期」，不是班级。**

> 这也是「取最早 / 取最新」口径分歧长期没暴露的原因：跨形态合并分支从来没跑过真实数据。

#### 为什么必须造数（不能只靠单测）

单测已覆盖合并逻辑本身（`PresaleSubjectServiceImplTest#should_合流券科目并取最新下单时间_when_券与订金班并存` 等），
但 mock 不掉的是**两条独立写入链路在同一个学员身上并发收敛**：订金班由花名册进退班消息驱动，
券由订单事件驱动，两者落不同表、各自触发 refresh。要验的是它们合流后 ES 的最终值，这只有真实数据能验。

#### 造数方案 A：直接插库（推荐，最快）

并集只读这两张表，不关心记录从哪来。给一个**已有订金班预报名记录**的学员补一条券记录即可：

```sql
-- 1. 挑一个有有效订金班记录的学员，记下 user_id / school_year_id / school_term_id / clazz_number / course_number
SELECT user_id, clazz_number, course_number, school_year_id, school_term_id,
       presale_subject_id, grades, course_type, course_tags
FROM ees_data.dws_fuwu_clazz_user_presale_subject
WHERE is_del = 0
ORDER BY id DESC LIMIT 10;

-- 2. 按同一「学年+学期」补一条券记录，presale_subject_id 故意取一个订金班没有的学科，便于验证并集
--    course_type 必须是付费课（40），course_tags 不能含排除标签（默认 13,4,26,11,27）否则会被判成赠课而不计入
INSERT INTO ees_data.dws_fuwu_clazz_user_presale_coupon
  (user_id, clazz_number, course_number, grades, course_type, course_tags,
   school_term_id, school_year_id, coupon_sku_number, renewal_number,
   pre_order_activity_number, coupon_order_item_number, presale_subject_id,
   presale_order_time, is_del)
VALUES
  (<user_id>, <clazz_number>, <course_number>, '[16]', 40, '[35]',
   '<school_term_id>', <school_year_id>, 579394599632533505, 578668076965308416,
   578842182125903872, 999999999999999999, '[<订金班没有的学科ID>]',
   '2026-09-20 10:00:00', 0);
```

`presale_order_time` 建议**设成比订金班订单支付时间更早**，这样能顺带验证「取最新」口径
（期望取订金班的时间，不是券的）——这正是 2026-09-15 修正的那处，见 [[changelog]]。

写完跑回溯触发重算（见下节「怎么回溯」），然后查 ES 期望：

| 字段 | 期望 |
|---|---|
| `presaleStatus` | `1` |
| `presaleSubject` | 订金班学科 ∪ 券学科（去重、按学科 ID 升序） |
| `gradePresaleSubject` | 同上，按年级归组 |
| `presaleOrderTime` | 两者中**较晚**的一个 |

⚠️ `course_type=40`、`course_tags` 不含排除标签是硬前提：`listPresaleSubjectId()` 会因非付费课或赠课返回空列表，
造出来的数据不计入并集，看起来像"并集没生效"。

#### 造数方案 B：走真实链路（更贴近线上，成本高）

挑一个已进预报名班（订金班）的学员，再给他买一张膨胀券，要求券的「年级+学科」能匹配上他前置课的**可续后置课**
（`calculate_renewal_type=2`），且学年学期与订金班记录一致。匹配不上不会落券记录，只有一条 INFO 日志。
成本主要在凑「同一学员 + 同一学年学期 + 年级学科可匹配」这三个条件。

#### 退款侧也要验

并集建立后再退券：期望回落成**只剩订金班那部分**（`presaleSubject` 去掉券学科、`presaleStatus` 仍为 `1`、
`presaleOrderTime` 回到订金班的时间），而不是整个清空。这条是券退款不会误伤订金班的关键保证。

## 怎么回溯

两个 XXL-Job，大小班各一个：

| Handler | 管什么 |
|---|---|
| `backDwsPresaleHandler` | 大班课预报名 |
| `backSmallDwsPresaleHandler` | 小班课预报名 |

入参两种格式：

```
[3001234,3001235]
    只回溯订金班，行为与加券前完全一致（控制台历史参数就是这个格式）

{"clazzNumbers":[3001234,3001235],"couponSkuNumbers":[579394599632533505]}
    额外回溯膨胀券；couponSkuNumbers 不传或传 [] 等价于老格式
```

`couponSkuNumbers` 本身就是开关，没有另设 Apollo 开关。

### 维度：班级驱动，但券的落点与传入班级无关

两个字段角色不对称：`clazzNumbers` 是**驱动源**（决定遍历哪些学员，必填），
`couponSkuNumbers` 只是**过滤器**（订单侧反查都要 userId，光给券号找不到购买者）。
实际路径是「班级 → 捞该班学员 → 按 userId 回溯」；券记录落在哪由
「券 → 续班计划 → 前置课 → 学员在前置课的在班班级」决定。

由此三条实操判据：

1. **必须传学员的在读班（前置班）**。传预报名班时券部分会空跑——纯券学员不在预报名班花名册里。
2. **传 A 班可能改的是 B 班的 ES 字段**，A 班字段不动是正常现象。
3. **本 job 只能填大班班级号**。订金班那半的 `getPostPresaleRecords` 没有班型过滤，
   填小班号会往大班预报名表插脏行；小班走 `backSmallDwsPresaleHandler`。

### 券没收上来先查这三个

券订单项还要过三道门槛：`confirmedTime` 非空、`orderStatus` 命中
`back.presale.coupon.paid.order.status`（默认 `[2,4]`）、`refundType=0`。
再看日志里 `券回溯完成` 那行的 `failedUserIds` 是否为空。

### 不适合挂 cron

`clazzNumbers` 是必填驱动源，定时跑等于把班级清单写死后反复重刷同一批班。
若为"新券上线补数"临时挂了定时，跑完要把 `couponSkuNumbers` 清掉。
券部分纯串行、每个学员多一串 RPC，几千人的大班先拿单个班验证再放量
（限速 `back.dws.presale.coupon.batch.sleep.millis`，默认 200ms，大小班两个 job 共用此 key）。

## 反射桥地址

| 服务 | 地址 |
|---|---|
| student-center | `https://test-fuwu.baijia.com/bgwApi/component/student-center/test/acl/compare/service` |
| promotion-b | `https://test-fuwu.baijia.com/bgwApi/promotion/b/test/acl/compare/service` |
| product-b | `https://test-fuwu.baijia.com/bgwApi/product-b/b/test/acl/compare/service` |
| cart | `https://test-api.gaotu100.com/cart/test/acl/compare/service` |

网关前缀以 `baijia_invoke.py` 的 `ROUTE_MAP` 为准。19 位 ID 一律使用字符串。

## 上线配置

详细清单见 README「上线影响面」；具体 Apollo key 名：`pre.order.coupon.product.type`（`8014`）、
`renewal.content.config.map`（膨胀券 reportCode）、`renewal.cStyle.preRegistrationCoupon.bgUrl`（背景图）、
student-center/cart 各自的 `couponStatus`/`saleStatus` 白名单 key（默认 `1`/`2`）。

## 页面复现

1. 打开 `https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/pre-register-activity`。
2. 确认前端分支包含 `feature-expand-coupon`，请求头泳道为 `test-gtbg-dev-3`。
3. 新建活动，活动形式选“膨胀券预报名”，活动开始时间必须晚于当前时间。
4. 添加当前状态符合白名单的券，配置年级和学科范围后保存。
5. 编辑详情应完整回显券字段和范围；scope 表应按活动/年级/学科保持唯一。
