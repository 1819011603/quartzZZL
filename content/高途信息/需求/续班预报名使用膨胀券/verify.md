---
title: 续班预报名使用膨胀券 · 验证手册
tags: [需求, 验证]
---

# 验证手册

> 回答一个问题：**想跑一遍，去哪跑、用哪条数据跑。**
> 造好的数据属于当前状态（数据还在库里），所以在这儿而不是 changelog。
> 术语（券ID vs 券商品ID）和推荐流程的两条分支说明见 [[README]]「核心概念」，这里不重复。

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

🔴 **coupon-a 测试环境的券 SKU 会滚动重新生成，不要相信任何文档里记的具体 sku 值**——当天下午记的"木7 skuNumber=578513860277893121"，晚上用同一个 couponName 查已经变成了 `578534533488603137`（couponNumber 也变了）。每次要用真实券自测前，现查一次：

```
mcp baijia-invoke invoke_service project=promotion traffic_env=test-gtbg-dev-3
service_method=com.gaotu.coupon.a.client.feign.ExpandCouponFeignService#queryList
params=[{"skuNumbers":["随便填"],"pageNum":1,"pageSize":20}]
```

⚠️ **`invoke_service` 反射桥调 `queryList` 时，`skuNumbers`/`pageSize` 这些 `List<Long>`/复杂类型参数不会正确生效**（传什么都返回同一页默认数据）——这是反射桥自身 JSON→Java 参数适配的缺陷，不代表接口真的不支持过滤，真实 Feign 调用不受影响。现查时直接看返回的 `list` 里挑一条 `coupon_status=1` 的券，用它当下最新的 `sku_number`/`coupon_number`。

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

**排障方法留档**（下次遇到"回显还是空"先按这个顺序查，别猜）：

1. 先用 `mcp qingzhou-trace trace_tree` 看 traceId 有没有报错 span——没有报错不代表数据对，只能说明没崩
2. 查日志 `mcp qingzhou-log get_tls_log_v2 queryStr='messages: PreOrderCouponEnricher'`，看有没有 `部分券在电商查不到` 的 WARN——**这条日志直接告诉你是不是券本身查不到**，比反复用不同接口测快得多
3. 只有查到"电商真的没这张券"才需要怀疑测试数据是不是过期了，不要先怀疑修复代码本身
4. 改完 DB 直接查缓存路径的接口（`listFromCache`/`detail`）**别忘了清 promotion 的 Redis 缓存**：
   `service_method=com.gaotu.promotion.domain.service.PreOrderActivityDomainService#clearAllVisibleActivityCache params=[["活动号"]]`
5. 用浏览器 `fetch` 调外部服务（如 `test-fuwu.baijia.com`）**必须带 `traffic-env: test-gtbg-dev-3` 请求头**，否则打到默认泳道，看不到测试泳道插的数据——反射桥（`invoke_service`）已经自动带了这个头，浏览器 fetch 要手动加

## 反射桥调用地址（四个服务，均实测）

| 服务 | 调用地址 | 状态 |
|---|---|---|
| student-center | `https://test-fuwu.baijia.com/bgwApi/component/student-center/test/acl/compare/service` | ✅ |
| promotion(-b) | `https://test-fuwu.baijia.com/bgwApi/promotion/b/test/acl/compare/service` | ✅ |
| **cart** | `https://test-api.gaotu100.com/cart/test/acl/compare/service` | ✅ |
| product-server(B) | `https://test-fuwu.baijia.com/bgwApi/product-b/b/test/acl/compare/service` | ✅ |

`mcp baijia-invoke invoke_service` 的 `ROUTE_MAP` 已按上表登记，直接用 `project=xxx` 即可。

🔴 **`promotion-management` 没有登记在 ROUTE_MAP 里，也没挂反射桥 Controller**——测它只能走真实业务接口（登录了 OES 页面的浏览器 fetch），见下方「B 端页面复现手册」。

🔴 **`promotion` 项目在这个环境有 `promotion-b`（serviceCode `gaotu_promotion`）和 `promotion-c`（serviceCode `gaotu_promotion_c`）两个独立部署**，同一份代码两份运行实例：**反射桥走的是 promotion-b，cart 走的是 promotion-c**。只发 promotion-b、用反射桥验证通过，不代表 cart 端到端真的通了。判据：`trace_tree` 里对应 span 的 `gapmApp`/`service` 字段会显示到底是哪个部署接的请求。**改动涉及 C 端链路（`listFromCache`/`calculate`/`calculateWhite`）的代码，两个部署都要发布。**

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

# B 端页面复现手册

> 目的：下次要复现「新建/编辑膨胀券活动」不用再摸索。**每一步都实测过**。

## 0. 两个前置，缺一个就白忙

| 前置 | 怎么确认 |
|---|---|
| **前端必须是 `feature-expand-coupon` 分支** | 控制台跑 `document.cookie.match(/_app_br_=([^;]+)/)`，应含 `ark#feature-expand-coupon#xxx`。<br>❌ 若是 release 版：新建表单**没有「活动形式」单选**，选品框商品类型只有「课程」(6003)、**没有膨胀券(8014)** —— 根本建不出膨胀券活动 |
| **后端泳道 `test-gtbg-dev-3`** | 页面加载的 JS 路径里应含 `promotions.release.test-gtbg-dev-3.umi.*.js` |

页面：https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/pre-register-activity

## 1. 用 Chrome + CDP 驱动（Claude 自动化时）

```bash
bash ~/.claude/chrome-mcp/chrome-mcp.sh "<页面URL>"      # 起 Chrome(9222) 并灌 Cookie
# 若跳 CAS 登录页，重灌一次 Cookie 再导航：
cd ~/.claude/chrome-mcp && N=/Users/gaotu/.nvm/versions/node/v22.21.1/bin && \
  PATH="$N:/usr/bin:/bin" "$N/node" inject.mjs
```

⚠️ 页面是 **antd v5**，class 前缀是 `antv5-` 不是 `ant-`。选择器要用 `[class*=picker-dropdown]` / `[class*=select-item-option]` 这种**模糊匹配**，写死 `.ant-picker-dropdown` 一律选不中。

## 2. 新建膨胀券活动（逐步，通过页面点击）

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

## 3. 直接调接口造数（绕过 UI，更快，控制台里跑）

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
