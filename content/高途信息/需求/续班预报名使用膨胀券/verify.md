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
| 泳道 | **test-gtbg-dev-3** ✅ 已验证可用（student-center pod Running/UP，2026-09-08 16:37 发布 feature-xuban-pre 镜像） |
| 数据库实例 | `gaotu_polar_test_03`（cluster_id **142**）· 库 `gaotu` |
| DB 直连 | host `gaotu-polar-test03.rwlb.rds.aliyuncs.com` · 账号 `gaotu_test_rw`（**密码见 Apollo `product` / TEST / `jdbc-mysql` 的 `jdbc.gaotu.password`**，本仓库是 public 不落密码） |
| 券列表 mock 开关 | Apollo `pre.order.coupon.mock.enabled=true` ✅ **已发布**（default cluster，20260908171459-release）。Apollo 无泳道 cluster 时自动读 default，不必单独建 |
| 券商品类型 | Apollo `pre.order.coupon.product.type=8014` ✅ **已发布**（⚠️ 不是 8027） |
| 膨胀券白名单 | Apollo `pre.order.activity.coupon.renewalPlanIds` —— **不配则活动形式永远兜底成订金班，膨胀券链路进不去**，自测前必配 |

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
  发链接 path **不分叉**（膨胀券与订金班同为 `/preSignUp`，出现 `/preSignUpCoupon` 即缺陷）、订金班不回归
- ✅ **已实测通过（2026-09-08，泳道 test-gtbg-dev-3 反射调用）**：
  - `PreOrderCouponBiz#listCoupon` 空条件 → **3 条 mock 券返回 2 条**，已结束券被默认状态过滤掉 ✅
  - `productType` 全部为 **8014** ✅ · `couponStatusDesc`(使用中/待开始) 与 `selectable` 正确 ✅
  - 券名称模糊查询「秋季」→ 精确命中 1 条 ✅ · `couponIdList` 批量精确查询 ✅
  - 复现命令见每次调用返回的 curl，或用 `mcp baijia-invoke invoke_service`

- ❌ **仍验不了**：券的**真实**名称/金额/状态（电商券商品接口未提供，当前全部走 mock）、
  B 端活动详情回显券字段（promotion `pre_order_activity_product` 表无券列）
- ⚠️ **C 端落地页自测的真正前提是「有 type=2 的膨胀券活动」**：
  库里 `promotion.pre_order_activity` 现存活动**全部是 type=1 订金班**，
  且 scope 表里的 activity_number(9001/9002/9003) 是造的假号，与真实活动对不上。
  C 端要跑通，得先在 B 端建一个膨胀券活动、挂上券并配好范围。

## 🔴 阻塞级发现：promotion 券字段不落库，C 端拿不到

**已实测复现**（2026-09-08，活动 `578363764011708416`，已发布 `activity_status=2`）：

调 `PreOrderActivityService#listFromCache` 返回的 `product_list`，每项**只有 5 个字段**：

```json
{"id":916, "pre_order_activity_number":578363764011708416,
 "product_number":801400001, "product_type":8014, "deductible_amount":20000}
```

**`couponId` / `couponName` / `skuId` / `buyAmount` / `couponStatus` / `couponStatusDesc` / `scopes` 全部丢失。**

### 为什么

- `promotion.pre_order_activity_product` 表**只有 8 列，没有任何券字段**（已 SHOW COLUMNS 确认）
- 创建时这些字段只写进 **Redis 缓存 DTO**（`PreOrderActivityProductCacheDTO` 里确实定义了这 6 个字段）
- 但缓存 miss 会 **从 DB 重建**（`listVisibleActivityByNumbersFromCache` → `listVisibleActivityByNumbersFromDB`），
  重建后券字段必然为 null —— 本次实测就是重建路径
- 代码注释自己也写了：「膨胀券字段与券范围：**BO 侧不落库**，此处随缓存结构一并透传」

### 影响面（比原以为的严重）

原先 README 记的是「B 端活动详情回显会丢券字段」，**低估了**。实际是：

| 场景 | 后果 |
|---|---|
| 缓存有效期内 | 正常 |
| **缓存过期/重启/miss** | 券信息**整体丢失**，C 端落地页无券可展示 |
| product-server 三者交集 | 拿不到 `scopes` 与 `couponStatus`，交集必然为空 |
| cart C 端组装 | 拿不到 `buyAmount`/`scopes` → 按新逻辑**直接抛异常**（落地页 500） |

**C 端自测在此修复前跑不通**，且这是**上线阻塞项**，不是自测环境问题。

### 修复进展（2026-09-09 修正：原方案已撤销）

> ⚠️ 2026-09-08 的「加 5 列落库」方案**已作废并 revert**，工单 8025 **已撤**。
> 下面是最终口径，看到旧结论以本节为准。

**为什么撤**（用户 review 指出，已确认）：

| 原方案加的列 | 为什么不需要 |
|---|---|
| `coupon_id` / `sku_id` | **冗余** —— `product_number` 存的就是券商品 ID（见 `PreOrderActivityProductEditDTO` 注释），券商品详情里能查到 sku。同一身份存两列，必然出现「以谁为准」 |
| `coupon_name` / `buy_amount` / `coupon_status` | **权威源在电商，落库即快照**。券改名、状态流转后快照不会跟着变；`coupon_status` 尤其是会流转的状态，落库必脏 |

**正确口径**：`product_type=8014` 已足以区分券商品与课程商品（`PreOrderActivityCouponConstant`，
Apollo `gaotu.preOrderActivity.coupon.productType` 可配），**表结构一列都不用加**。

**已执行**（promotion `8ed5fbab1`，revert 掉 `a620a7e2f`）：

| 位置 | 状态 |
|---|---|
| DDL 工单 8025 | ✅ 已撤，测试环境表**始终是 8 列**，未加过列 |
| `Base_Column_List` / resultMap / insertSelective | ✅ 已还原为 8 列 |
| Entity 5 字段 + RepositoryImpl 双向补齐 | ✅ 已还原 |

🚨 **顺带消除一个必挂故障**：revert 前 `Base_Column_List` 已含那 5 列，而表里没有。
select 是**硬拼列名、与值是否 null 无关**，一旦发布，`selectByExample` / `selectByPrimaryKey`
必报 `Unknown column`，**连订金班活动查询一起挂**（不限膨胀券）。revert 同时解决。

### 原 bug 仍在：缓存 miss 丢券字段

**撤的是错误修法，不是修好了。** 缓存 miss 从 DB 重建后，
`couponName` / `buyAmount` / `couponStatus` / `couponStatusDesc` / `skuId` 仍为 null：

- cart `PreRegistrationCouponAssembler:215` 取不到 `buyAmount` → 走兜底/抛异常
- product-server `PreOrderCouponIntersectService:250` 取不到 `couponStatus` → 「未知即放行」，**过滤静默失效**

**正解**：重建时用 `product_number` 调**券商品详情**实时补齐（券改名、状态流转能同步，无快照问题）。
**阻塞**：电商券商品接口尚未提供（找邓俊兵，见 [[links]] 的 TODO-券信息接口），
当前先接 student-center 已有的 Apollo mock 顶替。

### 已接 Apollo mock 顶替（2026-09-09，promotion `eb72e083f`）

电商接口没来之前，缓存重建路径先由 mock 补齐，让 C 端在**缓存过期后**也能跑通。

| | |
|---|---|
| 类 | `promotion-domain` → `PreOrderCouponMockEnricher` |
| 挂载点 | `PreOrderActivityDomainServiceImpl#convertPreOrderActivityProductCacheDTOS` 出口（DB 重建唯一必经处） |
| 开关 | `pre.order.coupon.mock.enabled`，**默认 false**，线上不配即不生效 |
| 数据 | `pre.order.coupon.mock.data`（不配用内置 3 条），与 student-center `PreOrderCouponMockProvider` **同源同字段** |
| 对齐键 | `productNumber` = 券商品 ID（`couponSkuNumber`） |

**内置 mock 的券商品 ID**：`801400001`(使用中) / `801400002`(待开始) / `801400003`(已结束)。

**2026-09-09 起 mock 同时给出 `couponStatusDesc`**（使用中/待开始/已结束）——
文案权威源在电商、本地不翻译，mock 不成对给就会一路 null 到前端。
自定义 `pre.order.coupon.mock.data` 时**记得带上这个字段**，否则券列表状态列为空。
⚠️ 活动里挂的券商品 ID 必须是这三个之一才补得上，否则 `hit=0`。

**行为边界**（刻意如此，别当 bug 改）：
- 只补 `product_type=8014` 的行，课程商品不碰
- **只补为空的字段**，不覆盖缓存命中路径的真实值
- 不补 `scopes`（权威源在 product-server）
- **不做「真接口失败回落 mock」**——会让联调期真实故障被假数据掩盖
- 每次生效打 `warn` 日志：`券信息由 MOCK 补齐(电商接口未提供)`，**日志里看到它就说明走的是假数据**

🚨 **上线前必须处理**（两处 mock 都要）：

| 服务 | Apollo key | 线上 |
|---|---|---|
| `promotion-b.gaotu100.com` | `pre.order.coupon.mock.enabled` | **必须 false 或不配**（默认 false，但建议显式配） |
| `student-center` | `pre.order.coupon.mock.enabled` | **必须 false 或不配** |

**下线步骤**：电商接口就绪 → 置开关 false 止血（不需发版）→ 把 `enrich()` 换成真实 ACL 调用
→ 删 `PreOrderCouponMockEnricher` 与 student-center 的 `PreOrderCouponMockProvider` 及其 mock 分支。

`scopes` 不落 promotion 库不变 —— 一对多，权威源在 product-server 的
`renewal_pre_order_activity_coupon_scope` 表。

**上线时线上库不需要加列**（原「另提 prod 工单」作废）。

## 反射桥调用地址（四个服务，均实测）

| 服务 | 调用地址 | 状态 |
|---|---|---|
| student-center | `https://test-fuwu.baijia.com/bgwApi/component/student-center/test/acl/compare/service` | ✅ |
| promotion | `https://test-fuwu.baijia.com/bgwApi/promotion/b/test/acl/compare/service` | ✅ |
| **cart** | `https://test-api.gaotu100.com/cart/test/acl/compare/service` | ✅ |
| product-server(B) | `https://test-fuwu.baijia.com/bgwApi/product-b/b/test/acl/compare/service` | 待验(已加挂 /b 路径) |

`mcp baijia-invoke invoke_service` 的 `ROUTE_MAP` 已按上表登记，直接用 `project=xxx` 即可。

### 三个必踩的坑

1. **「请重新登录」≠ Cookie 失效**，绝大多数是**路由/host 不匹配**打到了 CAS 兜底。
   判据：看日志里有没有这条请求 —— 没有就是压根没到应用，别去查 Cookie。
2. **cart 是 C 端服务**，网关路由**没绑 `test-fuwu.baijia.com`**（那是 B 端网关），
   必须走 `test-api.gaotu100.com` 且**不带 `/bgwApi` 前缀**。
3. **`curl --data-raw @file` 不会读文件**，会把 `@/tmp/x.json` 当字面量发出去，
   服务端报 `JSONException: syntax error, expect {` 但外层只回「参数异常」。
   读文件要用 `--data @file`。（2026-09-08 为此误判成校验失败查了很久）

## 🚨 上线必做：关闭三个反射调用桥

`AclServiceCompareController` 迁进了 **promotion / cart / product-server** 三个仓库，
它能**反射调用任意 Spring Bean 的任意方法**，线上必须关掉。

| Apollo appId | key | 测试环境 | **线上** |
|---|---|---|---|
| `promotion.gaotu100.com` | `AclServiceCompareController.enabled` | true(默认) | **必须 false** |
| `cart.gaotu100.com` | `AclServiceCompareController.enabled` | true(默认) | **必须 false** |
| `product` | `AclServiceCompareController.enabled` | true(默认) | **必须 false** |

⚠️ **代码里的默认值是 `true`**（`@Value("${AclServiceCompareController.enabled:true}")`），
所以**不配 = 开启**。线上必须显式配 `false`，不能靠"没配就是关的"。

cart 还额外把 `/test/acl/compare/**` 加进了 `MvcConfig` 的
`excludePathPatterns`（绕过 `UserAuthInterceptor`），这条**也只有开关能兜底**——
即 enabled=false 时 Controller 直接返回失败，放行路径本身不构成风险。

这三条已进上线 checklist，见 [[README]] 的「上线影响面」。

## 新建的东西（上线 checklist 原料）

| 类型 | 名称 | 位置 / 值 | 测试 | 线上 |
|---|---|---|---|---|
| 表 | `renewal_pre_order_activity_coupon_scope` | `gaotu_polar_test_03` · 库 gaotu | ✅ 已建（直连，未走工单） | 待建（马胜或提工单） |
| Apollo | `pre.order.coupon.mock.enabled` | true(测试) | **待配**（已核对 default 无此 key） | **不要配**（mock 仅测试用） |
| Apollo | `pre.order.coupon.product.type` | 8014 | 待配 | 待配 |
| Apollo | `renewal.content.config.map` | 加膨胀券 reportCode | 待配 | 待配（**不配则老师端无入口**） |
| Apollo | `renewal.cStyle.preRegistrationCoupon.bgUrl` | 暂用订金班图 | 待配 | 待运营给图 |
| Apollo | `pre.order.activity.coupon.renewalPlanIds` | 空 | 可选 | 白名单，用于强制判膨胀券自测 |
| 代课权限 | `/renewal/pre/coupon/list`、`/couponScope/list` | sd.baijia.com | 待登记 | 待登记 |
