# C 端纯续链接验证方法（2026-11-05）

## 1. 取入口
1. 用测试班级 + 续班计划调 `POST /reachPortal/reportConfig/getRecommendAppInfo`：
   ```json
   {"clazzNumber":"574882679202260992","renewalPlanId":"585960797778243584"}
   ```
2. 返回 `data[]`，每个 `value` 是 JSON 字符串，包含 `appCode`、`url`。选高途：`https://test-m.gaotu.cn/suggestShoppingCart?renewalNumber=<计划号>&seller_id=<id>&p_client=1`。
3. 直接调 `getReportUrl` 时若 `paramsMap.appInfo` 为空，返回 `code=0` 但无 URL；先取售卖主体。

## 2. 登录/账号
- C 端页面自带登录态时，network `time.gif` 的 `uid` 即当前学员（本次为 7658127801）。
- 账号以 `2` 开头时用 `100`（owner 口径）。
- 本轮未取得历史记录中的登录/签证码方法（已查需求归档与相关记录未命中），完整登录下单待补；不要在页面验证里写成通过。

## 3. 选品/价格
- 页面勾选商品后触发：
  - `POST /cart/web/renewal/productSelectConfirm?p_client=1`，请求含 `renewalNumber/productSkuNumber/beforeCourseNumber/productCourseNumber/productType`。
  - `POST /cart/web/renewal/price?p_client=1`，请求 `{"skuNumbers":"<SKU>"}`，返回 `data.totalPrice/totalDiscount`。
- 本次：小班 SKU `586097025945298944`，totalPrice=0、totalDiscount=0；trace 见 P0 6.6。

## 4. 跨商品/跨班型 + mock 支付
- 接口层已验证（round7）：大班 `588861402658267136`（100 分）+ 小班 `586097025945298944`（0 分）同单，应付 100 分；支付 `433655835275559341`，订单 `433655835275559853`/`433655835275560365`。
- 页面层：点「去结算」只触发选品/价格，未观察到订单确认/mock 支付；需要可用学员登录态后补。

## 5. 关键坑
- `getReportUrl` 需要 `paramsMap.appInfo`（售卖主体），空值会静默返回无 URL。
- C 端页面在 `test-m.gaotu.cn`，接口在 `test-api.gaotu.cn`，需带 `p_client=1` 与 `traffic-env: test-gtbg-dev-3`。
- 计划 A 的链接可能展示来自关联计划 B 的小班商品，说明关联推荐在 C 端已生效；不要按计划类型误判。
- 测试环境只 mock 支付，不真实支付；不要让页面结果替代接口 trace。
- 本次登录 uid 7658127801 的页面只可选 0 元小班；「更换课程」返回「未查询到满足条件的课程」，换大班班号取链接仍同一 URL，¥100 大班不在可选范围。要验有价商品页面下单，需换有该商品资格的学员登录态，或直接用接口层下单/支付。
- 点「去结算」只触发 `productSelectConfirm` + `/renewal/price`，未跳订单确认；0 元商品可能不进入支付流程。
- **cosplay 不支持 C 端学员**：baijia-invoke 的代课登录只支持 EES/OS 老师账号（projectCode 3/4），不能用来切 C 端学员会话；要验有价商品需 owner 提供学员 C 端登录态。
- **缓存开关实测**：cart.gaotu100.com / TEST `renewal.query.cache.enabled` 原 false → 改 true 发布（release 20261106083609）→ cart getRenewalDetail 正常返回三门商品 trace `cart_gaotu100_com.301.17939253769250778` → 恢复 false 发布（release 20261106083631）并回读 false。
- **小班好友 DB 实测**：`select account_id,user_id,friend,wechat_type from gaotu_link.tutor_wechat_info` 报 Unknown column；`show columns` 该表 17 列无学员关系列；`gaotu_link.dws_fuwu_user_teacher_wechat_info`、`student_center.dws_fuwu_user_teacher_wechat_info` 均定位不到，未找到小班好友候选。
