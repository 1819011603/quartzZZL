---
title: 续班预报名使用膨胀券 · 自测 cURL 集
tags: [需求, 验证, curl]
---

# 自测 cURL 集（可导入 Apifox）

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

数据走 Apollo mock（`pre.order.coupon.mock.enabled=true`），内置 3 张券。

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

## 2. 膨胀券活动的券配置与适用范围（B 端活动详情抽屉回显）✅ 接口通

`POST /b/renewal/preOrderActivity/couponScope/list` · product-b

```bash
curl --location --request POST 'https://test-fuwu.baijia.com/bgwApi/product-b/b/renewal/preOrderActivity/couponScope/list' \
--header 'Content-Type: application/json' \
--header 'traffic-env: test-gtbg-dev-3' \
--data-raw '{"preOrderActivityNumber":578363764011708416}'
```

**实测返回**（2026-09-09）：
```json
{"code":0,"data":[
  {"deductible_amount":20000,"product_number":"801400001","scopes":[]},
  {"deductible_amount":40000,"product_number":"801400002","scopes":[]}]}
```

⚠️ **`scopes` 为空、券字段全无 —— 这是已知问题不是新 bug**，两个原因叠加：
1. scope 表里造的数据挂在**假活动号** 9001/9002/9003，与真实活动 `578363764011708416` 对不上
2. promotion `pre_order_activity_product` 表无券列，缓存重建后券字段为 null（详见 [[verify]]）

要看到非空 `scopes`，得先把 scope 数据的 `activity_number` 改成真实活动号。

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
--data-raw '{"serviceNameAndMethodName":"com.gaotu.promotion.app.service.preorder.PreOrderActivityService#listFromCache","params":[{"preOrderActivityNumbers":[578363764011708416]}]}'
```
✅ **实测通过**。用来复现「券字段不落库」那个阻塞项 —— 返回的 `product_list` 每项**只有 5 个字段**：
```json
{"deductible_amount":20000,"id":916,"pre_order_activity_number":578363764011708416,
 "product_number":801400001,"product_type":8014}
```
`couponId/couponName/skuId/buyAmount/couponStatus/couponStatusDesc/scopes` **全部缺失**，与 [[verify]] 记录一致。

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

## 我到底测了什么（诚实版）

| 项 | 结论 |
|---|---|
| 券列表：空条件 / 名称模糊 / ID 批量 / 状态过滤 | ✅ **HTTP 实测通过**（本次会话，1.1~1.3 逐条跑过） |
| `couponStatusDesc` 随券列表下发 | ✅ **实测有值**（使用中/待开始），本次新增字段生效 |
| `productType=8014`、`selectable` | ✅ 实测正确 |
| 券范围接口 couponScope/list | ⚠️ **接口通(code:0)，但 scopes 为空** —— 造数挂在假活动号上 |
| 券的**真实**名称/金额/状态 | ❌ **全部是 mock**，电商券商品接口至今未提供 |
| B 端活动详情回显券字段 | ❌ 验不了，promotion 表无券列（阻塞项） |
| C 端落地页 | ❌ 未跑，前提是先修好上面两条 |
| 单元测试 | ❌ **一个都没写** |

> 一句话：**券列表这条链路是真跑通了的；券范围与 C 端是「代码写完、编译过、但没端到端跑通」。**
