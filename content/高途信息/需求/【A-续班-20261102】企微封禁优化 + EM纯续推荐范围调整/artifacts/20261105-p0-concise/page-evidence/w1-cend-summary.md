# C 端纯续链接验证记录（2026-11-05）

## 入口获取
- `POST /reachPortal/reportConfig/getRecommendAppInfo`
  - 入参：`{"clazzNumber":"574882679202260992","renewalPlanId":"585960797778243584"}`
  - trace：`b3084f50-7ba1-4751-970f-12d452cddee0.0.3`
  - 返回两条：高途 `https://test-m.gaotu.cn/suggestShoppingCart?renewalNumber=585960797778243584&seller_id=7682&p_client=1`；途途课堂 `https://test-m.gaotu100.com/suggestShoppingCart?...&p_client=2`。
- 实际打开高途链接。

## 页面
- URL：`https://test-m.gaotu.cn/suggestShoppingCart?renewalNumber=585960797778243584&seller_id=7682&p_client=1`
- 页面登录 uid：`7658127801`（network time.gif uid）。
- 页面展示：一年级/数学「dcg-小班扩科排除-数学-后置」，SKU `586097025945298944`，2 节课，¥0；勾选后「1 门合计 ¥0」。

## 选品/价格接口
- `POST /cart/web/renewal/productSelectConfirm?p_client=1`
  - 请求：`{"renewalNumber":"585960797778243584","productSkuNumber":"586097025945298944","beforeCourseNumber":"18314034380997173","productCourseNumber":"18314034380997207","productType":6004,"type":1,"status":1}`
  - 响应：`{"status":0,"error_info":"","code":0,"msg":""}`
  - trace：`90ba9ce9-6a65-480b-8ec1-f5b2d28823f3.0.3`
- `POST /cart/web/renewal/price?p_client=1`
  - 请求：`{"skuNumbers":"586097025945298944"}`
  - 响应：`{"status":0,"error_info":"","code":0,"msg":"","data":{"totalDiscount":0,"totalPrice":0}}`
  - trace：`07822e8e-193a-46f7-b533-a69cfd3707ad.0.3`

## 未完成
- 点「去结算」后只触发选品/价格接口，页面未观察到跳转订单确认；C 端完整结算/下单/mock 支付未完成。
- 跨商品/跨班型与 mock 支付沿用接口层 round7 证据：大班 `588861402658267136`（100 分）+ 小班 `586097025945298944`（0 分），应付 100 分；支付 `433655835275559341`，订单 `433655835275559853`/`433655835275560365`。
- 需要登录/签证码的完整 C 端下单未完成；账号 2 开头用 100 的规则尚未在本次实际使用。
