---
title: 续班预报名使用膨胀券 · 自测 cURL 集
tags: [需求, 验证, curl]
---

# 自测 cURL 集（可导入 Apifox）

> 🔴 **这份文件里具体的返回值示例是 2026-09-08/09 早期记录的快照，下面很多标成"❌"/"阻塞"的
> 结论后来都修好了**（mock 已全删、券字段回显已修好、C 端 scopes 已修好、三者交集已端到端验证、
> 单测已补齐）。**当前最新真相在 [[verify]]，这份文件只保留还有效的部分**：
> curl 语法本身、网关前缀表、`traffic-env` 头这个坑。看到具体返回值/结论类的描述，
> 以 [[verify]] 为准，这里的旧结论已在下面逐条标注。

> ## 🚀 推荐用 OpenAPI 一次性导入，别一条条粘 cURL
>
> **`apifox-openapi.json`（同目录）** —— Apifox「导入数据 → **OpenAPI/Swagger**」选文件即可，
> **9 个接口 + 3 个分组 + 字段说明 + 实测返回示例一次到位**，还带请求示例值。
> cURL 导入一次只能一条、且丢失字段注释，仅在临时试单条时用。
>
> 项目：https://app.apifox.com/project/8815485
>
> 导入后接口会落在三个目录下：`1-券选品(student-center)` / `2-券配置回显(product-server)` /
> `3-反射桥(绕过网关鉴权)`。若要「每个需求一个文件夹」，导入时在目标目录选/新建
> 「续班预报名使用膨胀券」，三个分组会挂在它下面。
>
> 下面的 cURL 保留作**终端手跑**用（终端需补 `-x` 走代理，Apifox 不用）。
>
> ⚠️ **为什么不是我直接写进 Apifox**：`apifox-mcp-server@0.0.17` 只提供 3 个**只读**工具
> （`read_project_oas` / `read_project_oas_ref_resources` / `refresh_project_oas`），
> **没有任何创建目录或写接口的能力**。所以 Apifox 侧只能手动导入，这份文件就是导入源。
>
> **不需要配代理**：Apifox 自带 Cookie 管理，下面的 curl **已去掉 `-x 127.0.0.1:8888`**。
> 若在终端里手跑，才需要补 `-x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}"`（走 baijia-proxy 注 Cookie）。

## 🔴 券状态枚举已按电商定稿（2026-09-09，与此前完全不同）

来源 `com.gaotu:coupon-a-client:1.3.15` → `ExpandCouponDetailDto#couponStatus`
（接口 `POST /feign/expandCoupon/queryList`，青舟 interfaceId=5453936）

|  | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| ~~旧(错)~~ | ~~待开始~~ | ~~使用中~~ | ~~已结束~~ | ~~已下线~~ |
| **新(对)** | **使用中** | **已失效** | **审核中** | **已暂停** |

- **只有【1 使用中】可勾选**，默认查询也只查这一个状态
- **没有「待开始」** —— 售卖期由 `saleStartTime`/`saleEndTime` 表达，不在状态码里
- ⚠️ 最危险的是 `2`：旧代码把 2 当【使用中】放行，而电商的 2 是**已失效** ——
  停在旧值会把失效券当可用券卖出去。`COUPON_STATUS_IN_USE` 已 2→1

## 两个致命前提（错一个就全是 404 / 空数据）

| 前提 | 值 | 错了会怎样 |
|---|---|---|
| **泳道头必须是 `traffic-env`（带连字符）** | `traffic-env: test-gtbg-dev-3` | 写成 `trafficenv` → **打到默认泳道，新接口一律 404**。<br>我自测时就被这个坑了半天，误以为镜像没发上去。<br>**Apifox 侧在「环境 → 全局 Header」配一次即可**，OpenAPI 里已不带此参数 |
| **网关前缀不能猜** | student-center 用 `/bgwApi/component/student-center`<br>product-b 用 `/bgwApi/product-b` | `/bgwApi/student-center` → 404；<br>`/noAuth/...` → 200 但 `code:3 登陆信息获取异常`（该路由跳过鉴权，拿不到用户上下文） |

环境：泳道 `test-gtbg-dev-3` · 网关 `https://test-fuwu.baijia.com`

---

## 1. 券选品分页查询（B 端券列表抽屉）✅ 实测通过

`POST /renewal/pre/coupon/list` · student-center · **本需求的核心新接口**

🔴 **下面示例数据是 mock 时代的记录，mock 已于 2026-09-09 全部删除**——现在这个接口走的是真实电商
coupon-a 数据（空条件查询 `total=79`，见 [[verify]]），返回结构不变，`couponName`/`couponStatus`
等字段是真实值，不再是"暑期50抵200"这几张固定 mock 券。下面的 curl 语法仍然有效，照抄用。

### 1.1 空条件（默认过滤：只返回可勾选的「待开始+使用中」）

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"pageNum":1,"pageSize":20}'
```

**实测返回**：`total=2`，第三张「春季膨胀券30抵100(已结束)」被状态过滤掉 ✅
每条含 `productType=8014` / `couponStatus` / **`couponStatusDesc`（本次新增）** / `selectable`。

### 1.2 券名称模糊查询

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"couponName":"秋季","pageNum":1,"pageSize":20}'
```
实测：精确命中 1 条（秋季膨胀券100抵400）✅

### 1.3 券 ID 批量精确查询（数组传法）

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"couponIdList":[10086,10087],"pageNum":1,"pageSize":20}'
```

### 1.4 券商品 ID 空格分隔字符串传法（运营粘贴场景）

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"couponSkuNumbersStr":"801400001 801400002","pageNum":1,"pageSize":20}'
```
> 分隔符兼容半角/全角空格、逗号、换行、Tab。与 `couponSkuNumberList` 同时传时**数组优先**。

### 1.5 显式查「已结束」券（验证状态过滤确实生效）

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"statusList":[3],"pageNum":1,"pageSize":20}'
```
预期：返回「春季膨胀券30抵100(已结束)」，且 `selectable=false`、`couponStatusDesc="已结束"`。

---

## 2. 膨胀券活动的券配置与适用范围（B 端活动详情抽屉回显）✅ 已修复，端到端实测通过

`POST /b/renewal/preOrderActivity/couponScope/list` · product-b

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/product-b/b/renewal/preOrderActivity/couponScope/list' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"preOrderActivityNumber":578563007821410304}'
```

🔴 **下面这段是 09-08 记的旧结论，`scopes` 为空的问题已经修好了，别再信**：

~~实测返回 `scopes:[]`，两个原因叠加：① scope 表数据挂假活动号 ② promotion 表无券列缓存重建后为 null~~

**现在的真实结果**（用当前有效的真实活动号 `578563007821410304` 查，见 [[verify]] 造好的数据）：
`scopes` 正确返回 `[{"grade_code":19,"grade_name":"大班","subject_code":6,"subject_name":"物理"}]`，
`couponId`/`couponName`/`couponStatus`/`buyAmount` 等券字段全部正确回显——两个原因都已解决：
promotion 的 `PreOrderCouponEnricher` 补齐了券字段（`enrichDTO`），跨服务查询补齐了 `scopes`。

---

## 3. 反射调 Bean（不走 HTTP，绕过网关与鉴权）

前端没开发时，**这是验证业务逻辑最快的路**——不依赖 Controller 是否暴露、不依赖登录态。

**各服务的反射桥前缀不一样，别猜也别试** —— 权威表在
`~/.local/mcp-servers/baijia_invoke.py` 的 `ROUTE_MAP`（invoke_service 就是按它拼 URL 的），
改动以那份为准，本文件只是抄录：

| 服务 | host | 反射桥完整 URL |
|---|---|---|
| student-center | test-fuwu.baijia.com | `/bgwApi/component/student-center/test/acl/compare/service` |
| promotion | test-fuwu.baijia.com | `/bgwApi/promotion/b/test/acl/compare/service` |
| product-server | test-fuwu.baijia.com | `/bgwApi/product-b/b/test/acl/compare/service` |
| **cart** | **test-api.gaotu100.com** | `/cart/test/acl/compare/service`（**不带 `/bgwApi`**）|
| student-data | test-fuwu.baijia.com | `/bgwApi/student-data/test/acl/compare/service` |

⚠️ 两个反直觉点，都实测踩过：
- **`/bgwApi/component/{服务}` 只有 student-center 有**，别当成通用规律套到别的服务上。
- **cart 是 C 端服务，路由没绑 B 端网关 `test-fuwu`**，必须换 host 到 `test-api.gaotu100.com`。

用错的表现**不是 404 而是 `code:700 请重新登录`**（CAS 兜底），长得像 Cookie 失效，
实际是**路由未命中** —— 2026-09-08 为此误判了很久。

### 3.1 券列表编排层

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/test/acl/compare/service' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"serviceNameAndMethodName":"com.gaotu.yunying.student.center.app.service.PreOrderCouponBiz#listCoupon","params":[{"pageNum":1,"pageSize":20}]}'
```

### 3.2 直接调 Controller（验证 Controller 已在镜像里）

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/test/acl/compare/service' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"serviceNameAndMethodName":"com.gaotu.yunying.student.center.web.api.PreOrderCouponController#listCoupon","params":[{"pageNum":1,"pageSize":20}]}'
```

### 3.3 promotion 活动详情（看券字段有没有丢）

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/promotion/b/test/acl/compare/service' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"serviceNameAndMethodName":"com.gaotu.promotion.app.service.preorder.PreOrderActivityService#listFromCache","params":[{"preOrderActivityNumbers":[578563007821410304]}]}'
```

🔴 **09-08 记的是「券字段不落库」阻塞项的复现结果（返回只有 5 个字段，券字段全部缺失），这个问题已经在
09-09 修好了**——现在同一个接口对当前有效活动号会正确返回 `couponId`/`couponName`/`skuId`/`buyAmount`/
`couponStatus`/`couponStatusDesc`/`scopes` 全部字段，详见 [[verify]]「已验证清单」。

⚠️ 入参是**查询 DTO**（`{"preOrderActivityNumbers":[...]}`），不是裸数组；传裸数组会报「未找到方法」。

### 3.4 三者交集（前置班学科 ∩ 后置班年级学科 ∩ 券配置范围）

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/product-b/b/test/acl/compare/service' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"serviceNameAndMethodName":"com.gaotu.product.service.renewal.preorder.PreOrderCouponIntersectService#intersect","params":[578363764011708416,[]]}'
```
✅ **实测通过**，返回 `activity_type=2`(膨胀券已正确识别)、`empty=true`(交集为空，因 scopes 造数挂在假活动号上)。

⚠️ 两个坑：前缀是 **`/bgwApi/product-b/b`**（少了 `/b` → CAS 要求重新登录，不是 404）；
`intersect` 是**两个参数** `(activityNumber, preCourseNumbers)`，只传一个会报「未找到方法」。

---

## 我到底测了什么（诚实版，2026-09-09 深夜更新）

> 🔴 这张表下面这版是最新的。上面还留着的具体 curl 返回值示例是历史快照，别看那些数字，
> 结论以这张表和 [[verify]]「已验证清单」为准。

| 项 | 结论 |
|---|---|
| 券列表：空条件 / 名称模糊 / ID 批量 / 状态过滤 | ✅ **真实电商数据实测通过**（`total=79`） |
| `couponStatusDesc` | ✅ 本地映射已实现并实测（电商不下发这个字段，本地按 jar 官方注释维护是永久方案，电商邓俊兵已确认） |
| `productType=8014`、`selectable` | ✅ 实测正确 |
| 券范围接口 / B 端活动详情回显券字段 | ✅ **已修复并端到端实测通过**（`couponId`/`couponName`/`buyAmount`/`couponStatus`/`skuId`/`scopes` 全部正确） |
| 券的真实名称/金额/状态 | ✅ **已接通真实电商 coupon-a**，mock 全部删除 |
| C 端落地页（三者交集完整推荐） | ✅ **真实数据端到端验证通过**，真实券"木7"完整推荐出来 |
| `postProductId`/`postProductName`/`activityType`（预警列表） | ✅ 验证是老字段（非本次改动），真实数据回显正确 |
| 单元测试 | ✅ 已补 38 个测试方法（promotion 17 / student-center 12 / product-server 8） |

> 一句话：**这个需求目前涉及的接口链路都已经端到端跑通并有真实数据验证**。仍未做的是：单测覆盖不全
> （order/cart 的下单算价等历史模块没补）、上线 Apollo 配置几项待配、前端字段对齐没有新的待办。
