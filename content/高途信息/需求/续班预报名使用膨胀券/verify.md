---
title: 续班预报名使用膨胀券 · 验证手册
tags: [需求, 验证]
---

# 验证手册

> 回答一个问题：**想跑一遍，去哪跑、用哪条数据跑。**
> 造好的数据属于当前状态（数据还在库里），所以在这儿而不是 changelog。
> 术语（券ID vs 券商品ID）和推荐流程的两条分支说明见 [[README]]「核心概念」，这里不重复。
> **请求示例/字段类型走同目录 `apifox-openapi.json`**（Apifox「导入数据 → OpenAPI/Swagger」选文件，
> 9 个接口 + 分组 + 字段说明一次到位；项目 https://app.apifox.com/project/8815485）。
> Apifox 自带 Cookie 管理不用配代理，但要在「环境 → 全局 Header」配一次 `traffic-env`。
> ⚠️ `apifox-mcp-server` 只有 3 个**只读**工具，没有写接口的能力 → Apifox 侧只能手动导入。

## 环境

| 项 | 值 |
|---|---|
| 泳道 | **test-gtbg-dev-3**（`test-gtbg-dev-3` 属于 **dev** 逻辑环境，别用 `--env test` 单独查，会漏 pod） |
| 数据库实例 | `gaotu_polar_test_03`（cluster_id **142**）· 库 `gaotu`（scope 表、questionnaire_inspect 表都在这）；`promotion` 库放活动主数据 |
| DB 直连 | host `gaotu-polar-test03.rwlb.rds.aliyuncs.com` · 账号 `gaotu_test_rw`（密码见 Apollo `product`/TEST/`jdbc-mysql` 的 `jdbc.gaotu.password`，本仓库是 public 不落密码）；`mysql-query` MCP 是只读账号，写操作要用这个账号直连（python `pymysql`） |
| 券商品类型 | Apollo `pre.order.coupon.product.type=8014` ✅ 已发布（⚠️ 不是 8027） |
| 膨胀券白名单 | Apollo `pre.order.activity.coupon.renewalPlanIds` —— 不配则活动形式永远兜底成订金班 |

⚠️ **mock 已全部删除**（2026-09-09 起券信息全部实时取电商 coupon-a），别再找 `pre.order.coupon.mock.enabled` 这类开关或 `PreOrderCouponMockEnricher`/`PreOrderCouponMockProvider` 这些类——它们已经不存在，如果哪份旧记录还提就是过时的。

## 券的可用范围唯一键（活动内唯一、跨活动放行）

```
跨活动重复   券X 的 (年级,学科) 插到活动B  → ✅ 放行
同活动跨券   另一张券在活动A 配相同 (年级,学科) → ✅ 被拦（Duplicate entry ... uk_act_grade_subject）
```

DB 层唯一键 `uk_act_grade_subject(activity_number, grade_code, subject_code)` 已兜住，2026-09-09 王永诗确认这正是想要的规则（见 README 已定共识）。

## 入口类（README 只写到模块，这里到类）

| 功能 | 类 |
|---|---|
| 券选品/列表接口 | `student-center-service/.../app/service/PreOrderCouponBiz.java` |
| B 端活动详情（回显） | `promotion-app/.../preorder/PreOrderActivityService.java#detail` |
| C 端活动列表（下发给 cart） | `promotion-app/.../preorder/PreOrderActivityService.java#listFromCache` |
| 券字段实时补齐（两条链路共用） | `promotion-domain/.../service/impl/PreOrderCouponEnricher.java`（`enrich`=缓存重建路径，`enrichDTO`=detail 路径） |
| C 端 scopes 补齐 | `promotion-app/.../PreOrderActivityService.java#fillCouponScopes`（私有方法） |
| 券范围落库/校验/批量查询 | `product-server-domain/.../renewal/preorder/PreOrderActivityCouponScopeService.java` |
| C 端落地页组装（三者交集） | `cart-app/.../renewal/preregistration/PreRegistrationCouponAssembler.java` |
| C 端推荐入口（两分支） | `cart-app/.../renewal/RegistrationService.java#preRegistration` |
| B 端预报名预警列表 | `product-server-domain/.../renewal/InspectService.java#questionnaireList` |

## 电商 coupon-a 联调信息

| 项 | 值 |
|---|---|
| 接口 | `POST /feign/expandCoupon/queryList`（青舟 interfaceId=5453936） |
| 依赖 | `com.gaotu:coupon-a-client:1.3.15`，分支 `feature-expand-coupon` |
| **服务所在泳道** | **`test-eco-7`**（不在 `test-gtbg-dev-3`！） |
| 跨泳道可达 | ✅ 已实测：`test-gtbg-dev-3` 的 promotion-b 能调到 `test-eco-7` 的 coupon-a |

❌ ~~**coupon-a 测试环境的券 SKU 会滚动重新生成**~~ —— **2026-09-10 证伪，这条是错的**。

当时的观察（下午记的 `578513860277893121`，晚上查变成 `578534533488603137`）是真的，但**结论错了**：
不是券被重新生成，而是**同名的两张不同券**（相隔约 3 小时各建了一张「木7」）。
2026-09-10 实测按 `couponName=木7` 查，`total=2`，**两张 sku 至今都还在、`couponStatus` 都是 1**。

真因是 `PreOrderCouponEnricher` 发给电商的请求体被序列化成 snake_case（`sku_numbers`），
电商只认 camelCase，筛选被静默忽略 → 只返回全量第一页 → 目标券不在第一页就 miss。
新建的券恰好排在第一页，于是「换张新券重测就正常」，造出了「旧 sku 失效」的错觉。
已修（见 [[README]] 坑位「调电商请求体 snake_case」）。**文档里记的 sku 值可以放心复用。**

查券命令（`couponName` 是**左匹配**，只能按开头搜）：

```
mcp baijia-invoke invoke_service project=promotion traffic_env=test-gtbg-dev-3
service_method=com.gaotu.coupon.a.client.feign.ExpandCouponFeignService#queryList
params=[{"skuNumbers":["随便填"],"pageNum":1,"pageSize":20}]
```

⚠️ **`invoke_service` 反射桥调 `queryList` 时 `skuNumbers` 不生效**（传什么都返回同一页默认数据）。
**2026-09-10 更正**：原先写「真实 Feign 调用不受影响」是**错的** —— 真实 Feign 同样中招，
病根是 promotion 的全局 SnakeCase 把请求体发成了 `sku_numbers`（已修）。
要精确按 sku 查，**直接 curl 打 coupon-a 实例**（camelCase 入参），别用反射桥：

```bash
# 实例 IP 每次重新部署会变，用 invoke_feign 现拿：
#   mcp baijia-invoke invoke_feign service_name=COUPON-A.GAOTU100.COM \
#     path=/feign/expandCoupon/queryList traffic_env=test-gtbg-dev-3 body='{"couponName":"木7","pageNum":1,"pageSize":10}'
curl -sk 'http://<coupon-a实例IP>:28688/feign/expandCoupon/queryList' \
  -H 'content-type: application/json' \
  -d '{"skuNumbers":[578534533488603137],"pageNum":1,"pageSize":5}'
```

⚠️ **ID 是 19 位雪花数**，前端 JS 会精度截断——出参需 `@JSONField(serializeUsing = ToStringSerializer.class)`；手工在浏览器/JSON 工具里粘贴大数字 ID 同样会截断，别拿手工调用的截断结果当 bug。

## 当前造好的测试数据（2026-09-09 深夜，最新状态）

⚠️ **这几条数据互相关联，改的时候留意别弄断了链路**。

| 对象 | 值 | 说明 |
|---|---|---|
| 膨胀券活动 | `578563007821410304`（名称"zzl验证detail0909b"） | 挂真实券"木7"，`activity_status=2` 已发布，`begin_time` 已改到过去 |
| 该活动挂的券 | couponId `578534533350174720`、skuNumber(=productNumber) `578534533488603137` | ⚠️ 这个 sku 也会过期，见上方电商联调信息段的警告 |
| 券可用范围 | `gaotu.renewal_pre_order_activity_coupon_scope` id=11，grade=19(大班)/subject=6(物理) | 挂在上面这个活动/券上 |
| 续班计划 | `577431949669312512` | `renew_master_ext` 的 `COURSE_GRADE`/`COURSE_SUBJECT` 已改成 `19`/`6`，对齐上面的券范围 |
| 续班计划↔活动关联 | `renewal_link_activity` id=307，`activity_number` 已改指向 `578563007821410304` | |
| 前置班/课程关系 | `renew_master_course_relation`，`pre_course_number=514762045841821696`（isdel=0 的那条） | 这是 `preClazzNumber`，验证 `preRegistration` 时用它 |
| 预警列表数据 | `gaotu.questionnaire_inspect` id=261，`renewal_number=577431949669312512, type=3(预报名)` | 验证 `postProductId`/`postProductName` 时插的，`pre_course_number` 同上 |

🔴 **改的是共享测试数据，不是新增独立行**：续班计划 `577431949669312512` 原来的 `COURSE_GRADE`/`COURSE_SUBJECT` 是 `15`/`1`，`renewal_link_activity` id=307 原来指向活动 `578559765060276224`（那个活动挂的是已过期的旧 sku `578513860277893121`）。**如果后面有测试依赖这条续班计划的老状态，会发现对不上——不是环境坏了，是这次验证改过了**。

## 已验证清单（当前最新，全部真实数据端到端跑通）

| 验证项 | 结果 | 验证方式 |
|---|---|---|
| B 端 detail 回显券字段 | ✅ `couponId/couponName/couponStatus/buyAmount/skuId/couponStatusDesc` 全部正确 | 反射调 `PreOrderActivityService#detail`，见下方命令 |
| C 端 listFromCache 下发 scopes | ✅ `scopes:[{grade_code:19,subject_code:6}]` | 反射调 `PreOrderActivityService#listFromCache` |
| C 端三者交集完整推荐 | ✅ 真实券"木7"完整推荐出来，`grade_list`/`scope_labels`/`renewal_msg` 全部正确 | 反射调 `RegistrationService#preRegistration` |
| `couponStatusDesc` 本地映射 | ✅ 状态 1→"使用中" 正确回显 | 同 detail 验证 |
| 券选品查询（B 端） | ✅ 真实电商数据 `total=79`，模糊查/精确查均正常 | 反射调 `PreOrderCouponBiz#listCoupon` |
| B 端保存可用范围 | ✅ 页面报文 `code:0`，范围自动落 scope 表，编辑改范围幂等（旧行置删+新行 upsert） | chrome fetch 调 `/promotionManagement/preOrderActivity/edit` |
| `postProductId`/`postProductName`（预警列表） | ✅ 由「前置班→后置班」推荐逻辑真实查出，非编造值 | 反射调 `InspectService#questionnaireList` |
| 券范围唯一键 | ✅ 活动内唯一、跨活动放行，两个方向都验证过 | 直连 DB 插入验证 |
| **券列表按三者交集过滤（T-32）** | ✅ **2026-09-10 端到端实测通过**（6 条用例全绿，含「同 3 张券加了计划号只剩 1 张」的语义验证） | 见下方「膨胀券 tab 券列表范围过滤」 |

**验证命令**：
```
# B 端 detail 回显
mcp baijia-invoke invoke_service project=promotion traffic_env=test-gtbg-dev-3
service_method=com.gaotu.promotion.app.service.preorder.PreOrderActivityService#detail
params=[{"number": "578563007821410304"}]

# C 端 listFromCache
service_method=com.gaotu.promotion.app.service.preorder.PreOrderActivityService#listFromCache
params=[{"preOrderActivityNumbers": ["578563007821410304"]}]

# C 端完整推荐（三者交集）
project=cart
service_method=com.gaotu.renewal.RegistrationService#preRegistration
params=[1, "577431949669312512", "514762045841821696", null]

# B 端预警列表 postProductId/postProductName
project=product-server
service_method=com.gaotu.product.service.renewal.InspectService#questionnaireList
params=[{"renewalNumber": "577431949669312512", "pager": {"current": 1, "pageSize": 5}}, 3]
```

**排障方法留档**（下次"回显还是空"按这个顺序查，别猜）：

1. `trace_tree` 看 traceId 有无报错 span（没报错≠数据对，只说明没崩）
2. **查日志 `get_tls_log_v2 queryStr='messages: PreOrderCouponEnricher'`，看有没有
   `部分券在电商查不到`** —— 这条直接告诉你是不是券本身查不到，比换接口反复试快得多
3. 只有确认"电商真的没这张券"才怀疑测试数据过期，别先怀疑修复代码
4. 改完 DB 查缓存路径接口（`listFromCache`/`detail`）**先清 promotion Redis 缓存**：
   `PreOrderActivityDomainService#clearAllVisibleActivityCache params=[["活动号"]]`
5. 浏览器 `fetch` 调外部服务**必须手动带 `traffic-env` 头**（反射桥已自动带）

## 膨胀券 tab 券列表范围过滤（T-32，✅ 已实测通过）

口径：**tab 一直展示**，不做显隐校验；续班计划没配膨胀券就是列表空。
范围 = 三者交集（在读班级学科 ∩ 续班班级年级学科 ∩ 活动券配置年级学科）且仅【使用中】。

**当前实际数据**（2026-09-10 实测，与本文上面那段「2026-09-09 造好的数据」已不同 ——
续班计划 `577431949669312512` 现绑活动 `578667346476945408`，该活动配了 **3 张券**，
范围都是 grade=16 六年级、subject 分别 1 数学 / 4 英语 / 5 语文，券状态都是 1）：

| 对象 | 值 |
|---|---|
| 续班计划 | `577431949669312512` |
| 绑定活动 | `578667346476945408`（`renewal_link_activity` id=307） |
| 交集命中的券 | `578323391191220225`「退款口径膨胀券caseSDD_1788846422662」六年级+数学 |
| 被交集挡掉的券 | `578323229840539649`（英语）、`578323085464207361`（语文） |

复现命令：

```
# 1) product-server 侧先单独验交集出口（应返回券 578534533488603137 一行，grade 19 / subject 6）
mcp baijia-invoke invoke_feign service_name=PRODUCT.GAOTU100.COM traffic_env=test-gtbg-dev-3 \
  path=/feign/preOrderActivity/couponScope/listDisplayableByRenewalPlan \
  body='{"renewMasterNumber":"577431949669312512"}'

# 2) student-center 侧验券列表（应只返回交集内、状态为1的券）
curl -X POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
  -H 'Content-Type: application/json' -H 'traffic-env: test-gtbg-dev-3' \
  -d '{"renewMasterNumber":"577431949669312512","pageNum":1,"pageSize":20}'

# 3) 反例：换一个订金班（或没绑活动的）续班计划 -> 期望 total=0 / list 空，且日志有
#    「续班计划无可展示的膨胀券」
```

**实测结果（2026-09-10，pod `student-center-7b6d9977df-6f4p5` + `product-b-68fd8df7c5-r662v`，均 eureka UP）**：

| 用例 | 期望 | 实测 |
|---|---|---|
| A 传膨胀券计划 | 只返交集内且状态1的券 | ✅ `total=1`，`productType=8014`、`couponStatus=1`、`couponStatusDesc=使用中`、`selectable=true` |
| B 不传 `renewMasterNumber` | 不过滤，存量不回归 | ✅ `total=142` |
| C 传计划号 + 范围内 sku | 求交后仍在 | ✅ `total=1` |
| D 传计划号 + 范围外 sku | 空页，且不调电商 | ✅ `total=0`、`list=[]` |
| E 传不存在/未绑活动的计划号 | 空页**不报错** | ✅ `code=0, total=0`（tab 仍在，点进去没数据） |
| **F 交集语义（最关键）** | 同 3 张券，加计划号后只剩交集命中的 | ✅ 不传计划号查这 3 张 → `total=3`（都在电商、状态都是1）；**加计划号 → `total=1`**，英语/语文两张被交集挡掉 |

> F 这条是「交集真的在过滤」的硬证据：三张券状态相同、电商都查得到，唯一差别就是年级学科是否与前置/后置课程成对匹配。

| 边界 | 行为 |
|---|---|
| product-b 路由不通 | 报 `PRE_ORDER_COUPON_SCOPE_QUERY_FAIL`「查询膨胀券适用范围失败」，**不静默返空**（刻意设计；本次正是靠它暴露了服务名写错）|
| product-b 直调（绕过 student-center） | `POST http://<product-b podIP>:28688/feign/...`，入参空报 `code:5`，不存在的计划返 `data:[]` |

⚠️ `renewMasterNumber` 是大数字，**一律传字符串**，否则精度截断表现为"查无数据"。

## 券选品列表的三个新字段（T-33，2026-09-11）

同一个接口 `/renewal/pre/coupon/list`，curl 与上面 T-32 完全一样（`renewMasterNumber=578668076965308416`）。

| 字段 | 口径 | 实测 |
|---|---|---|
| `availableScope` | 预报名可用范围文案，同券多组合用「、」连接。**仅传 `renewMasterNumber` 时下发**，不传为 null | ✅ 3 张券分别回「六年级数学」「六年级英语」「六年级语文」，与 OES 活动管理页该列逐条一致 |
| `holdLimit` | 单人持有上限，**String 展示文案**：电商原值 0 → 「不限」，否则数字字符串 | ✅ 实测返回 `"1"`（字符串）。原值为 0 的「不限」分支暂无数据可验 |
| `selectable` | 原本只看状态，**09-11 加售罄判定**：已售≥总量置 `false`，与有没有续班计划无关 | ⚠️ 单测 4 条覆盖（售罄/超卖/未售罄/数量缺失），**端到端未验 —— 环境里没有真正售罄的券** |

### ⚠️ 别拿 OES 页面的「已售/总量」当电商真值

排查售罄用例时踩到：OES 活动管理页显示 `578845069455599617` 是 **10/10**（看着已售罄），
但反射桥直查电商 `PreOrderCouponEnricher#queryCouponsBySkuNumbers` 拿到的是
**`sold_count: 0`、`total_amount: 10`、`coupon_status: 2`（已失效）** —— 三项全对不上。

判据：**页面那列读的是 promotion 活动商品缓存，不是电商实时值**；
券状态=2 时 student-center 列表默认只查状态=1，所以这张券在选品接口里根本查不到（`total:0`），
不是接口 bug。要确认一张券的真实售卖情况，**只认反射桥直查电商的结果**。

**售罄链路端到端待验**（需先造一张 `sold_count >= total_amount` 且 `coupon_status=1` 的券）：
① 列表里该券 `selectable` 应为 `false`；
② 加进膨胀券活动保存（`/promotionManagement/preOrderActivity/editAndPublish`）
应报「膨胀券已售罄，不可添加到活动，券商品编号：xxx（已售 N/M）」。

### 订金班满班拦截（2026-09-11，同批次）

同一个 `editAndPublish`，`type=1` 订金班分支：**在班 ≥ 班容的班级不可选进活动商品**。

数据来源与 B 端选班列表 `/course-center/b/clazz/list/search/fullAuth` 同源
（`IClazzFeignService#clazzSearchList`），页面「在班/班容」列即 `signUpCount`/`capacity`。

⚠️ **`capacity = -1` 是「不限班容」**（页面显示「2 / 不限制」），**必须放行**。
测试环境大量班级都是不限班容 —— 漏了这条会把它们全拦掉，属于最容易犯且影响面最大的错。

待验：造一个 `signUpCount >= capacity` 且 `capacity > 0` 的班级，加进订金班活动保存，
应报「班级班容已满，不可添加到活动，班级：xxx（在班 N/M）」。

反射桥直查电商券真值（排障第一手段）：
```
invoke_service promotion \
  com.gaotu.promotion.domain.service.impl.PreOrderCouponEnricher#queryCouponsBySkuNumbers \
  [["<skuNumber>"]] --traffic-env test-gtbg-dev-3
```

✅ **`creator`（创建人）已可用**（2026-09-11 晚，jar 升 1.3.17）——
电商新增 `creatorEmployeeId`，已接上。此前「1.3.15 里没这个字段、只能永远为空」的结论**已作废**。
⚠️ 下发的是**工号不是姓名**，页面显示为数字；要姓名需再查员工服务（本期未做）。

### 两个状态字段（1.3.17 起）

| 字段 | 含义 | 取值 |
|---|---|---|
| `couponStatus` | **券本身**是否生效 | 1 使用中 / 2 已失效 / 3 审核中（**「4 已暂停」1.3.17 已删**）|
| `saleStatus` | **券商品**在不在卖 | 1 停售中 / 2 开售中；**平台券为空** |

两者正交：券可以是【使用中】但商品【停售中】。`selectable` = 券使用中 ∧ 商品未停售 ∧ 未售罄。
`saleStatus` 为空（平台券）时不改判 —— 缺数据置灰会误杀正常券。

✅ **2026-09-11 实测到了这个正交场景**（`renewMasterNumber=578668076965308416` 那 3 张券）：
`couponStatus:1 使用中` 但 `saleStatus:1 停售中` → `selectable:false`。
原因是这几张券 `saleEndTime` 已过。**只看 `couponStatus` 会误判成可选**，
这正是接第二个状态字段的价值。完整返回：

```json
{"couponName":"退款口径膨胀券caseSDD_1788846422662","holdLimit":"1","creator":"8277",
 "couponStatus":1,"couponStatusDesc":"使用中","saleStatus":1,"saleStatusDesc":"停售中",
 "selectable":false,"availableScope":"六年级数学","soldCount":0,"totalCount":10}
```

## 反射桥调用地址（四个服务，均实测）

| 服务 | 调用地址 | 状态 |
|---|---|---|
| student-center | `https://test-fuwu.baijia.com/bgwApi/component/student-center/test/acl/compare/service` | ✅ |
| promotion(-b) | `https://test-fuwu.baijia.com/bgwApi/promotion/b/test/acl/compare/service` | ✅ |
| **cart** | `https://test-api.gaotu100.com/cart/test/acl/compare/service` | ✅ |
| product-server(B) | `https://test-fuwu.baijia.com/bgwApi/product-b/b/test/acl/compare/service` | ✅ |

`mcp baijia-invoke invoke_service` 的 `ROUTE_MAP` 已按上表登记，直接用 `project=xxx` 即可。

🔴 **`promotion-management` 没有登记在 ROUTE_MAP 里，也没挂反射桥 Controller**——测它只能走真实业务接口（登录了 OES 页面的浏览器 fetch），见下方「B 端页面复现手册」。

🔴 **反射桥走 `promotion-b`，而 cart 走 `promotion-c`（两个独立部署）** —— 反射桥验证通过≠cart 端到端通了。详见 [[README]]「必须知道的坑 · 部署/链路拓扑」。

### 走 HTTP 直调时的两个致命前提（错一个全是 404 / 空数据）

| 前提 | 值 | 错了会怎样 |
|---|---|---|
| **泳道头是 `traffic-env`（带连字符）** | `traffic-env: test-gtbg-dev-3` | 写成 `trafficenv` → 打到默认泳道，新接口一律 404，极易误判成「镜像没发上去」 |
| **网关前缀不能猜** | student-center `/bgwApi/component/student-center`<br>product-b `/bgwApi/product-b/b`<br>promotion-b `/bgwApi/promotion/b`<br>cart `test-api.gaotu100.com/cart`（**不带 `/bgwApi`**） | 前缀错 → **不是 404 而是 `code:700 请重新登录`**（CAS 兜底），长得像 Cookie 失效。<br>`/bgwApi/component/{服务}` **只有 student-center 有**，别当通用规律。<br>`/noAuth/...` → 200 但 `code:3 登陆信息获取异常`（跳过鉴权拿不到用户上下文） |

权威源是 `~/.local/mcp-servers/baijia_invoke.py` 的 `ROUTE_MAP`（`invoke_service` 按它拼 URL），以那份为准。

### 三个必踩的坑

1. **「请重新登录」≠ Cookie 失效**，绝大多数是**路由/host 不匹配**打到了 CAS 兜底。判据：看日志里有没有这条请求——没有就是压根没到应用，别去查 Cookie。
2. **cart 是 C 端服务**，网关路由**没绑 `test-fuwu.baijia.com`**（那是 B 端网关），必须走 `test-api.gaotu100.com` 且**不带 `/bgwApi` 前缀**。
3. **`curl --data-raw @file` 不会读文件**，会把 `@/tmp/x.json` 当字面量发出去，服务端报 `JSONException: syntax error, expect {` 但外层只回「参数异常」。读文件要用 `--data @file`。

## 🚨 上线必做：关闭三个反射调用桥

`AclServiceCompareController` 迁进了 **promotion / cart / product-server** 三个仓库，它能**反射调用任意 Spring Bean 的任意方法**，线上必须关掉。

| Apollo appId | key | 测试环境 | **线上** |
|---|---|---|---|
| `promotion.gaotu100.com` | `AclServiceCompareController.enabled` | true(默认) | **必须 false** |
| `cart.gaotu100.com` | `AclServiceCompareController.enabled` | true(默认) | **必须 false** |
| `product` | `AclServiceCompareController.enabled` | true(默认) | **必须 false** |

⚠️ **代码里的默认值是 `true`**（`@Value("${AclServiceCompareController.enabled:true}")`），所以**不配 = 开启**。线上必须显式配 `false`，不能靠"没配就是关的"。

cart 还额外把 `/test/acl/compare/**` 加进了 `MvcConfig` 的 `excludePathPatterns`（绕过 `UserAuthInterceptor`），这条**也只有开关能兜底**——即 enabled=false 时 Controller 直接返回失败，放行路径本身不构成风险。

这三条已进上线 checklist，见 [[README]] 的「上线影响面」。

## 新建的东西（上线 checklist 原料）

| 类型 | 名称 | 位置 / 值 | 测试 | 线上 |
|---|---|---|---|---|
| 表 | `renewal_pre_order_activity_coupon_scope` | `gaotu_polar_test_03` · 库 gaotu | ✅ 已建（直连，未走工单） | 待建（马胜或提工单） |
| Apollo | `pre.order.coupon.product.type` | 8014 | ✅ 已发布 | 待配 |
| Apollo | `renewal.content.config.map` | 加膨胀券 reportCode | 待配 | 待配（**不配则老师端无入口**） |
| Apollo | `renewal.cStyle.preRegistrationCoupon.bgUrl` | 暂用订金班图 | 待配 | 待运营给图 |
| Apollo | `pre.order.activity.coupon.renewalPlanIds` | 空 | 可选 | 白名单，用于强制判膨胀券自测 |
| Apollo | `AclServiceCompareController.enabled`（3 处） | true(默认) | 保持默认 | 🚨 **必须显式 false** |
| 代课权限 | `/renewal/pre/coupon/list`、`/couponScope/list` | sd.baijia.com | 待登记 | 待登记 |

**上线时线上库不需要加列**——`pre_order_activity_product` 表不加券字段列（`product_type=8014` 已足以区分商品类型，券的名称/金额/状态权威源在电商，落库即脏快照）。

---

## B 端页面复现手册

> 目的：下次要复现「新建/编辑膨胀券活动」不用再摸索。**每一步都实测过**。

### 0. 两个前置，缺一个就白忙

| 前置 | 怎么确认 |
|---|---|
| **前端必须是 `feature-expand-coupon` 分支** | 控制台跑 `document.cookie.match(/_app_br_=([^;]+)/)`，应含 `ark#feature-expand-coupon#xxx`。<br>❌ 若是 release 版：新建表单**没有「活动形式」单选**，选品框商品类型只有「课程」(6003)、**没有膨胀券(8014)** —— 根本建不出膨胀券活动 |
| **后端泳道 `test-gtbg-dev-3`** | 页面加载的 JS 路径里应含 `promotions.release.test-gtbg-dev-3.umi.*.js` |

页面：https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/pre-register-activity

### 1. 用 Chrome + CDP 驱动（Claude 自动化时）

```bash
bash ~/.claude/chrome-mcp/chrome-mcp.sh "<页面URL>"      # 起 Chrome(9222) 并灌 Cookie
# 若跳 CAS 登录页，重灌一次 Cookie 再导航：
cd ~/.claude/chrome-mcp && N=/Users/gaotu/.nvm/versions/node/v22.21.1/bin && \
  PATH="$N:/usr/bin:/bin" "$N/node" inject.mjs
```

⚠️ 页面是 **antd v5**，class 前缀是 `antv5-` 不是 `ant-`。选择器要用 `[class*=picker-dropdown]` / `[class*=select-item-option]` 这种**模糊匹配**，写死 `.ant-picker-dropdown` 一律选不中。

### 2. 新建膨胀券活动（逐步，通过页面点击）

1. 点「新建活动」→ 填名称（**≤30 字符**，超了报「活动名称长度不能超过30个字符」）
2. **「活动形式」选「膨胀券预报名」** ← 选完表单会重渲染，商品区变成「+添加膨胀券」，列名变为 膨胀券名称/膨胀券ID/膨胀券商品ID/购买金额/抵扣金额/状态/**预报名可用范围**
3. **活动时间**：⚠️ **不能直接往 input 填字符串** —— 两个值都会挤进「开始时间」一个框。必须点开日历面板点单元格再点「确 定」：
   ```js
   [...document.querySelectorAll('[class*=picker-cell-in-view]')].find(c=>c.title==='2026-09-09')
     .querySelector('div').click();
   [...document.querySelectorAll('[class*=picker-ok] button')][0].click();
   ```
   ⚠️ **开始时间必须晚于当前时间**，否则保存报「活动开始时间必须大于当前时间」，且**弹窗会静默关闭、列表里没有新活动** —— 极易误判成「保存成功了但没落库」。
4. 「+添加膨胀券」→ 选品框（实测拉到真实电商券）→ 勾选一张 →「确 定」
5. 该行点「配置可用范围」→ 选「目标年级」+「目标学科」→「确 定」→ 行内「预报名可用范围」应显示如 `五年级数学`
6. 点「保 存」

### 3. 直接调接口造数（绕过 UI，更快，控制台里跑）

```js
// 在页面控制台跑，自动带 Cookie 与泳道；couponId/productNumber 现查电商拿最新值，别抄旧的
const now=Date.now();
await (await fetch('/promotionManagement/preOrderActivity/edit',{
  method:'POST', headers:{'Content-Type':'application/json'},
  body: JSON.stringify({
    name:"验证-xxx", type:2,
    preOrderActivityProductEditDTOS:[{
      couponId:"<现查>", couponName:"<现查>", couponStatus:1,
      buyAmount:3000, deductibleAmount:9000,
      productNumber:"<现查的 skuNumber>", productType:8014,
      scopes:[{gradeCode:19, subjectCode:6}]
    }],
    userCondition:{userConditionType:0},
    beginTime: now+3600*1000, endTime: now+30*24*3600*1000, activityStatus:0
  })})).json();
// 成功返回 {"code":0,"data":"<新活动号>"}
```

**端到端已验证的完整链路**：`OES → promotion-management → promotion-b（落活动，promotion 库）→ 回调 product-b（落范围，gaotu 库）`，范围自动落表（19 位雪花 ID 无精度截断），编辑改范围幂等（旧行 `is_del=1`、新行 `is_del=0`）。

⚠️ 直接手工调 `/feign/preOrderActivity/couponScope/save` 时，**JSON 里的 19 位 ID 会被 JS/JSON 精度截断**（末尾变 00）。真实 Feign 走 Java 对象序列化不受影响——别拿手工调用的截断结果当 bug。
