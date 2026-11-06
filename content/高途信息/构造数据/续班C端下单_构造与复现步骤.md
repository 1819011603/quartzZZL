# 续班 C 端下单：构造与复现步骤

> 适用：验「纯续关联」在 C 端续班链接里能选到关联计划的大/小班商品并同单下单。
> 环境：TEST / 泳道 `test-gtbg-dev-3`。C 端 `test-m.gaotu.cn`，网关 `test-fuwu.baijia.com`。

## 1. 前置与环境

| 项 | 值 |
|---|---|
| C 端站点 | `https://test-m.gaotu.cn` |
| 网关 | `test-fuwu.baijia.com`（接口域名 `test-api.gaotu.cn` 时带 `p_client=1`） |
| 泳道 | `test-gtbg-dev-3`（请求头 `traffic-env: test-gtbg-dev-3`） |
| 学员(7658129872) | 手机号(12026102281) |
| 计划(588858850300473344) | 主计划，含大小班纯续 |
| 商品 | 大班商品(588861402658267136，100 分/页面 ¥1.00)；小班商品(586097025945298944，0 元) |
| 验证码 | `12` 开头固定 `1000`，`2` 开头也固定 `1000`（2026-11-06 短信平台实测 `12026102281` 解码为 1000；见 `知识库/sms/message/_page.md`） |

取学员手机号（不猜）：调 student-center `UserAclService#querySingleInfo(userId, "ALL")` 拿加密手机号，再 `decryptSingleMobileForServer(密文, "gaotu")` 解密。本学员完整号 `12026102281`。

## 2. 如何构造数据

**造数项目（data-agent）能做什么**：大/小班课、GPS/OMO/CES 教学产品、续班计划与前后置班、辅导班排课、下单与 mock 支付、可续关系。

**不能做什么**：造出来的对象不会自动“可售/可续”；造数返回 `ok`、`published=true` 都不等于能下单。必须回读 `saleStatus>0`、真实课节数>0、老师非空、`order/prepare` 可售。

**本需求实际使用（复用现成 fixture，不要每次重建）**：

- 主续班计划 `588858850300473344`（已关联小班计划 `585960797778243584`、`586116340522184704`）
- 目标学员 `7658129872`，目标商品见上表
- 已付测试单（接口层证据）：支付 `433655835275559341`，订单 `433655835275559853` / `433655835275560365`

需要新造时：

```bash
curl -s https://sd.baijia.com/api-qa/data-agent/scenarios              # 看有哪些场景
curl -s https://sd.baijia.com/api-qa/data-agent/scenarios/<name>       # 看参数契约
curl -s -X POST https://sd.baijia.com/api-qa/data-agent/scenarios/<name>/run \
  -H 'Content-Type: application/json' \
  -d '{"params":{...},"options":{"traffic_env":"test-gtbg-dev-3","timeout_s":600}}'
```

铁律：`traffic_env` 必填（漏了会 code=0 但不落库）；body 必须包一层 `params`；价格单位是分（100 分 = ¥1.00；本需求商品即 100 分）；学员手机号必须是已注册测试号。

## 3. 如何选数据（关键校验，先做）

**① 用 `getRecommendAppInfo` 取 C 端入口链接**

```
POST /reachPortal/reportConfig/getRecommendAppInfo
{"clazzNumber":"<班级号>","renewalPlanId":"588858850300473344"}
```

返回 `data[]`，每个 `value` 是 JSON 字符串，含 `appCode`、`url`。选高途链接；URL 形如：

```
https://test-m.gaotu.cn/suggestShoppingCart?renewalNumber=588858850300473344&seller_id=7682&p_client=1
```

注意：`getReportUrl` 若 `paramsMap.appInfo` 为空，会 `code=0` 但返回无 URL，先取售卖主体。

**② 用 cart `getRenewalDetail` 校验该学员在该计划下确实有目标商品**

```
RenewalService#getRenewalDetail("7658129872", "588858850300473344", true, false, null)
```

预期：返回 grade16 大班 `588861402658267136`（100 分）、grade11 小班 `586097025945298944`（0 分）、grade15 `585960755422160896` 等纯续商品。

> **`renewalNumber` 必须等于学员所在计划。** 用错计划（如 `585960797778243584`）时只返回 `585960755422160896` + 0 元小班，没有付费商品(100 分/¥1.00)，C 端表现为「未查询到满足条件的课程」。

## 4. 如何登录

1. 清 **仅** `test-m.gaotu.cn` 站点的登录态（不要清整浏览器，不要动其它站点）。
2. 打开 `https://test-m.gaotu.cn`，走手机号验证码登录。
3. 输入手机号(12026102281)，获取验证码后到短信平台 `listTest` 取 id → `decryptTest` 解码；`12` 开头固定 `1000`。
4. 登录后确认 uid = `7658129872`（可在 network 的 `time.gif` 参数或页面账号信息核对）。

> cosplay 只支持 EES/OS 老师账号，不能切 C 端学员会话；C 端只能走验证码登录。

## 5. 如何复现主链路（先接口，后页面）

**第 0 步｜接口层先确认**：按第 3 节跑 `getRenewalDetail`，确认目标商品存在且价格正确；价格接口 `POST /cart/web/renewal/price`，body `{"skuNumbers":"<SKU>"}`，看 `totalPrice/totalDiscount`。

**第 1 步｜打开正确链接**：登录后访问
`https://test-m.gaotu.cn/suggestShoppingCart?renewalNumber=588858850300473344&seller_id=7682&p_client=1`

**第 2 步｜选品（付费商品 100 分/¥1.00）**：勾选大班商品(588861402658267136)，观察请求 `POST /cart/web/renewal/productSelectConfirm?p_client=1`（含 `renewalNumber/productSkuNumber/productType` 等）。小班商品(586097025945298944) 为 0 元，可同车但**不会进入支付**。

**第 3 步｜去结算 → 订单确认 → mock 支付**：点「去结算」，核对订单确认页商品、数量、应付金额（预期 100 分）；提交后走 mock 支付，记录订单号、支付单号、金额、traceId。**页面层待验证（本轮执行中）**。

**第 4 步｜回读**：按订单号/支付号查订单状态（`order_status=2`、`pay_status=1`、`real_price=100`），并截图留证。**待验证（本轮执行中）**。

接口层已验证的等价结论（非页面）：同一单大班 `588861402658267136`（100 分）+ 小班 `586097025945298944`（0 分），应付 100 分；支付 `433655835275559341`；订单 `433655835275559853` / `433655835275560365`，均 `status=2`。

## 6. 常见坑

| 现象 | 原因 / 处理 |
|---|---|
| 「未查询到满足条件的课程」 | `renewalNumber` 用了错计划，换成学员所在计划 `588858850300473344` |
| 选完 0 元商品却不能支付 | 0 元商品不进支付流程，必须选付费商品(100 分/¥1.00) |
| 无法用代课方式切学员 | cosplay 不支持 C 端学员，走验证码登录 |
| 验证码一直错 | 先确认取码方式：`listTest` 取 id → `decryptTest` 解码；`12`/`2` 开头固定 `1000`，`maskedContent` 不能当码 |
| 其它站点登录态被清 | 只清 `test-m.gaotu.cn`，不要清整浏览器 |
| 造数返回成功但下单报无商品 | 未过可售门槛：查 `saleStatus`、课节数、老师、`order/prepare` |
| 用小班链接选不到大班 | 口径：主计划 `renewalNumber` + 关联并集，不是用从计划号 |

## 7. 证据与未验证项

**已验证**

- C 端域名/网关、学员 `7658129872`、主计划 `588858850300473344`、商品(588861402658267136，100 分)/商品(586097025945298944，0 元)。
- 错计划 `585960797778243584` 下 `getRenewalDetail` 无付费商品。
- 手机号取法（student-center 解密）与验证码规则（`12`/`2` 开头→`1000`，需 list→decrypt 解码）。
- 接口层跨模式同单 + mock 支付（支付 `433655835275559341`，两订单 `status=2`）。
- C 端入口/选品/价格页面（小班 0 元样本）：入口 trace `b3084f50`、选品 `90ba9ce9`、价格 `07822e8e`。

**推断未验证**

- 关联并集在 C 端页面完整可见（接口已返回，页面本轮未用付费商品(100 分)样本走完）。

**没做 / 待验证**

- 页面层付费商品(100 分)完整链路：选品 → 去结算 → 订单确认 → mock 支付 → 回读（本轮执行中）。
- 优惠活动、异收款主体反例。
- 跨学年/跨学季样本的 C 端页面下单。
