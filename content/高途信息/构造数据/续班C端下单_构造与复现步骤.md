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

**第 2 步｜选品（付费商品 100 分/¥1.00）**：勾选大班商品(588861402658267136)，观察请求 `POST /cart/web/renewal/productSelectConfirm?p_client=1`（含 `renewalNumber/productSkuNumber/productType` 等）。小班商品(586097025945298944) 为 0 元，能否进入支付需实测，见 8.2。

**第 3 步｜去结算 → 订单确认 → mock 支付**：点「去结算」，核对订单确认页商品、数量、应付金额（预期 100 分）；提交后走 mock 支付，记录订单号、支付单号、金额、traceId。**页面层待验证（本轮执行中）**。

**第 4 步｜回读**：按订单号/支付号查订单状态（`order_status=2`、`pay_status=1`、`real_price=100`），并截图留证。**待验证（本轮执行中）**。

接口层已验证的等价结论（非页面）：同一单大班 `588861402658267136`（100 分）+ 小班 `586097025945298944`（0 分），应付 100 分；支付 `433655835275559341`；订单 `433655835275559853` / `433655835275560365`，均 `status=2`。

## 6. 常见坑

| 现象 | 原因 / 处理 |
|---|---|
| 「未查询到满足条件的课程」 | `renewalNumber` 用了错计划，换成学员所在计划 `588858850300473344` |
| 选完 0 元商品不确定能否支付 | 不能凭页面推断，接口层 createOrder → mock_pay → 回读 `gaotu.pay_info`，见 8.2 |
| 无法用代课方式切学员 | cosplay 不支持 C 端学员，走验证码登录 |
| 验证码一直错 | 先确认取码方式：`listTest` 取 id → `decryptTest` 解码；`12`/`2` 开头固定 `1000`，`maskedContent` 不能当码 |
| 其它站点登录态被清 | 只清 `test-m.gaotu.cn`，不要清整浏览器 |
| 造数返回成功但下单报无商品 | 未过可售门槛：查 `saleStatus`、课节数、老师、`order/prepare` |
| 用小班链接选不到大班 | 口径：主计划 `renewalNumber` + 关联并集，不是用从计划号 |
| 发链接报「暂无续班报名流程」 | 计划没配 type=2 续班报名流程；按 8.8 给计划补 `process/edit`，与学员/班级无关 |
| 换课列表「已报名」跑到中间（应在最下面） | cart `RenewalService#productList` 未做展示排序；已修复（加 `sortClazzDetailDTOsForDisplay`，已报名沉底），见 8.10 |

## 7. 纯续并集口径（先搞清数量）

**为什么主+从会生效**：cart `RenewalService#mergeRelatedPreCourseNumbers` 把主计划的前置课号与关联从计划的前置课号取**并集**，再按学员在读订单过滤，最后各自展开成纯续商品。关系是**单向**的（主→从），从计划单独发起不会反向合并主计划。

**数量对比（同一学员、同一口径）**：

| 场景 | 商品数 | 说明 |
|---|---|---|
| 只有主计划有资格（7707220467 仅买主前课） | 1 件 | 只输出主后班商品(588861402658267136) |
| 主+从均有效（7707220467 补 B 前置课后） | 2 件 | 主商品 + 从计划商品 |
| 三计划均在读（7658129872） | 3 件 | 商品(585960755422160896)、小班商品(586097025945298944)、商品(588861402658267136) |

**规则**：同一商品去重、跨年级保留、同科目不因学科误去重。验证仍用 `getRenewalDetail`，主计划 trace `cart_gaotu100_com.297.17938914022950422`。

## 8. 卡点与正确做法

### 8.1 计划号错配 → 推荐为空

- **现象/卡点**：C 端提示「未查询到满足条件的课程」，或 `getRenewalDetail` 不返回付费商品(100 分/¥1.00)。
- **原因**：`renewalNumber` 用了别的计划（如从计划(585960797778243584)），不是学员(7658129872) 所在主计划。
- **正确做法**：`renewalNumber` 固定用学员所在主计划(588858850300473344)；C 端 URL：`https://test-m.gaotu.cn/suggestShoppingCart?renewalNumber=588858850300473344&seller_id=7682&p_client=1`。
- **验证方式**：调 `RenewalService#getRenewalDetail("7658129872","588858850300473344",true,false,null)`，返回 grade16 商品(585960755422160896)、grade11 小班商品(586097025945298944)、grade15 商品(588861402658267136) 三组。

### 8.2 0 元商品能否支付

- **现象/卡点**：页面选 0 元小班商品(586097025945298944) 时，无法从页面表现判断它是否进入支付。
- **原因**：页面「去结算」只触发选品/价格，不直接暴露支付链路；不能凭页面现象推断「0 元不进支付」。
- **正确做法**：接口层 `createOrder` → `mock_pay` → 回读 `gaotu.pay_info` 与报名状态。
- **验证方式**：`pay_info.pay_status=1` 且页面显示「已报名」= 支付成功；本轮结论**待验证（本轮执行中）**。

### 8.3 验证码 1001 登录失败

- **现象/卡点**：手机号(12026102281) 填 `1001` 登录报 code=34「验证码不正确」。
- **原因**：知识库「12 开头 1001」是错的；且短信平台返回 `maskedContent` 是脱敏串，不能直接当验证码。
- **正确做法**：短信平台 `listTest` 取 id → `decryptTest` 解码；`12` 开头实际固定 `1000`（`2` 开头同为 `1000`）。
- **验证方式**：登录成功后核对 uid=`7658129872` 与站点 cookie。

### 8.4 mock 支付入参用错（不是订单号，是批次单号）

- **现象/卡点**：直接传支付单号，或去前端找 mock 接口，走不通。
- **原因**：data-agent `mock_pay` 内部经 `gaotu.pay_info` 换单，认的是 createOrder 返回的**订单号(批次单号)**，不是支付单号。
- **正确做法**：`mock_pay` 传 createOrder 返回的订单号(批次单号)，如 `433715450493796358`。
- **验证方式**：看 data-agent run id（如 `r-20261106100523-08edf28b`）+ 回读 `gaotu.pay_info.pay_status=1`。

### 8.5 订单中心查不到支付单

- **现象/卡点**：`payCard/detail` 返回 code=1「订单号不存在」；`/orders` 待支付为空、无「立即支付」入口。
- **原因**：订单中心与支付中心数据不一致；疑似首请求 `ERR_ABORTED` 产生半成品单。
- **正确做法**：以 `gaotu.pay_info`（`pay_status=1`）+ 页面「已报名」判定支付成功；订单中心差异记为**待查项**，不写成通过也不写成缺陷。
- **验证方式**：附 traceId 与批次单号，单独登记待查。

### 8.6 cosplay 切不到 C 端学员

- **现象/卡点**：代课登录无法切到学员(7658129872) 的 C 端会话。
- **原因**：cosplay 只支持 EES/OS 老师账号，不支持 C 端学员。
- **正确做法**：走手机号(12026102281) + 验证码 `1000` 登录。
- **验证方式**：登录后 uid 与站点 cookie 一致。

### 8.7 浏览器调试丢登录态

- **现象/卡点**：重连或新开浏览器实例后登录态丢失，无法继续验证。
- **原因**：owner 约束——必须复用同一条已登录 Chrome，不加 debug 端口、不 stop/重连。
- **正确做法**：只连现有已登录实例，直接操作既有页面；不新开、不重连。
- **验证方式**：`list_pages` 能看到既有页面且仍是登录态。

### 8.8 计划无「续班报名流程」→ 发链接报「暂无续班报名流程」

- **现象/卡点**：EES 续班服务行内点「发链接 → 推荐链接」不弹窗，Toast「暂无续班报名流程」；接口 `POST /bgwApi/component/student-center/roster/renewal/renewalOrder/validate`，body `{"clazzNumbersStr":"588861402658267136","renewalPlanId":"588872241920421888","type":1}` → `{"code":1,"msg":"暂无续班报名流程"}`（trace `b0c414aa-f7f5-4eea-a05f-9d4164047607.0.0`）。
- **原因**：student-center `RenewalService#renewalOrderValidate`（源码 line 2066-2099）先按 `renewalPlanId` 查续班流程（`processFeignAdapter.listByRenewalNumber`），**查不到 `type=2`（续班报名流程）就直接返回该错，与学员/班级无关**。计划 `588872241920421888` 在 `gaotu.process_config`（cluster 142 `gaotu_polar_test_03`）里 **0 行**（是 clone 出来的草稿骨架，没配流程）；主计划 `588858850300473344` 有 `type=2`（number `588864200919560192`）+ `type=3`（`588993307433054208`），所以主计划同接口返回「跳过校验」。
- **正确做法（造数：给计划补 `type=2` 续班报名流程 + `type=3` CART 节点）**：
  - 调 product-b `POST /b/renewal/process/edit`（源码 `ProcessService#editProcess`）。test 环境可用 acl 桥直调：`com.gaotu.product.service.renewal.process.ProcessService#editProcess`（`project=product-server`、`service_name=PRODUCT.GAOTU100.COM`、`traffic_env=test-gtbg-dev-3`）。
  - 请求体（`ProcessEditReq` + `NodeEditReq`）：
    ```json
    {"renewalNumber":"588872241920421888","type":2,"configType":1,
     "administrators":[90247,177071],
     "beginTime":1793962860000,"endTime":1801738860000,
     "nodeConfigs":[{"type":3,"administrators":[90247,177071],
        "beginTime":1793962860000,"endTime":1801738860000,"recommendProductType":2}]}
    ```
    说明：`type=2`=续班报名流程；节点 `type=3`=续班购物车(CART)；`recommendProductType=2`=大班课；毫秒用计划自己的 begin/end（示例即 `588872241920421888` 的 2026-11-06 19:01 ~ 2027-02-04 19:01）。
  - 回读：`gaotu.process_config`（type=2）、`gaotu.node_config`（type=3）、`gaotu.renewal_link`（product_type=2）各 1 行。本次新增 number：process `589010207351453696`、node `589010207357745152`、renewal_link `589010207364036608`；edit 调用 trace `product_gaotu100_com.274.17939423059270585`。
- **验证方式**：重调 `renewalOrder/validate`（同 body，`type=1`）→ `{"code":0,"msg":"跳过校验"}`（trace `b8765cbe-a85d-4b39-b9ac-0fdf36dfcea5.0.3`）；桥 `RenewalService#renewalOrderValidate` 返回 `{true:"跳过校验"}`（trace `student-center.21791960.17939423331180465`）。
- **注意**：`type=1`（预览）会跳过时间窗校验，所以补流程后即便不在报名时间窗也返回「跳过校验」；`type=3`（发送）才校验流程时间窗。补流程只解决「流程不存在」这一类拦截，不代表链接生成/发送全链路都过。补流程后的完整生成链路见 8.9。

### 8.9 EES 单人「发链接 → 推荐链接」完整链路（生成侧）

- **入口**：EES 续班服务 → 选中学员行 → 行内「发链接」→「推荐链接」→ 弹窗「发推荐链接」→ 选 H5「推荐下单链接」+ 售卖主体「高途」→ 左侧 H5 预览 → 「复制通用链接」（或「发送」）。
- **接口链**（host `test-fuwu.baijia.com`，实测均 200；缺前置见 8.8）：
  1. `POST /bgwApi/component/student-center/roster/renewal/renewalOrder/validate`，body `{clazzNumbersStr, renewalPlanId, type}`（生成预览 type=1 / 复制·发送 type=2）→ 需该计划有 type=2 续班报名流程。
  2. `POST /bgwApi/component/student-center/roster/renewal/config`，body `{reportCode:"suggest_order_link", planClazzList:[{clazzNumber,renewalPlanId}]}` → 返回 reportType/h5 模板。
  3. `POST /bgwApi/component/student-center/roster/renewal/recommend/appInfo` → 返回售卖主体列表（高途 / 途途课堂）。
  4. `POST /bgwApi/component/student-center/roster/renewal/recommend/url`，body `{type, appInfo, userIdList:[<uid>], ...}` → 返回 `{ "<计划号>_<班级号>_<uid>": {url:"https://dwz.cn/xxx", name:"发推荐下单链接"} }`。
  - 预览 H5 另会打 `GET test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=<计划号>&appointUserId=<uid>&...`。
- **落地页**：`https://dwz.cn/xxx` 302 → `https://test-m.gaotu.cn/suggestShoppingCart?renewalNumber=<计划号>&seller_id=7682&p_client=1&pt=<带uid的JWT>&includeBCart=false&appointUserId=<uid>`。
- **本次实测（2026-11-06，学员 `7658129872` / 计划 `588872241920421888`）**：
  - 生成短链 `https://dwz.cn/ojzBCOlq`（type=1，trace `826a1da8-b6db-4ac2-9ee5-3a2e7e016b1f.0.0`）；「复制通用链接」`https://dwz.cn/Oh1DQuHg`（type=2，trace `52781009-640d-49c8-a448-de81d03fc758.0.0`）。
  - validate(type=1) trace `92a5e823-8b10-48b9-87a1-07ca5489dc55.0.0`；validate(type=2) trace `60531775-d482-4792-987a-c9a578bcb246.0.0`；config trace `b0d10bc5-9657-45f8-a7e9-789c77750468.0.0`；appInfo trace `9f72dadd-523f-433b-963a-aeaeb86100aa.0.0`。
  - H5 预览实时渲染成功；短链 302 落地页 200。**未点「发送」**（会真发企微/短信），发送后下游未验。
- **注意**：链接里 `pt` 是带 userId 的 JWT，`appointUserId`=学员 uid，`renewalNumber`=行内计划号。本学员 `7658129872` 的续班服务行是班级 `588861402658267136` / 计划 `588872241920421888`（**不是** `574882679202260992`，该学员不在那个班）。

### 8.10 换课列表「已报名」跑到中间（应在最下面）

- **现象**：C 端换课/选品列表里带「已报名」徽标的商品出现在中间，后面还跟着未报名商品；期望**已报名沉底**。
- **原因**：cart `RenewalService#productList`（接口 `POST /cart/web/renewal/productList`，trace `f785a1d4-085b-435b-b311-b6a2d1fb46df.0.3`）把各 `productType` 分组查询的结果**按前端传入的原始顺序**合并返回，**没做展示排序**；而续班序列列表（`gradeClazzList`）走的是 `sortClazzDetailDTOsForDisplay`（未购买在前→强制购买在前→纯续>扩科>加购），换课列表漏了这一步。
- **正确做法 / 修复**：在 `productList` 组装 `result` 后调用 `sortClazzDetailDTOsForDisplay(result)`——稳定排序，未购买在前、已报名沉底，其余保持原序（该路径 DTO 未设 `forceBuy`/`recommendType`，实际等价于按 `signUp` 升序）。commit `d5729426`，已 push 到 `feature-xuban-pure-relation-20261102`，并入 cart MR **!284**。
- **验证方式**：部署 cart 到 `test-gtbg-dev-3` 后调 `POST /cart/web/renewal/productList`，已报名项应排在末尾。

## 9. 证据与未验证项

**已验证**

- C 端域名/网关、学员 `7658129872`、主计划 `588858850300473344`、商品(588861402658267136，100 分)/商品(586097025945298944，0 元)。
- 错计划 `585960797778243584` 下 `getRenewalDetail` 无付费商品。
- 手机号取法（student-center 解密）与验证码规则（`12`/`2` 开头→`1000`，需 list→decrypt 解码）。
- 接口层跨模式同单 + mock 支付（支付 `433655835275559341`，两订单 `status=2`）。
- 接口层 data-agent `mock_pay`（按批次单号）：run `r-20261106100523-08edf28b`，批次单号 `433715450493796358`，`pay_info.pay_status=1`、`pay_channel=6`、`paid_time 2026-11-06 10:05:23`，页面「已报名」。
- C 端入口/选品/价格页面（小班 0 元样本）：入口 trace `b3084f50`、选品 `90ba9ce9`、价格 `07822e8e`。
- 计划(588872241920421888) 补 `type=2` 续班报名流程后，`renewalOrder/validate` 由「暂无续班报名流程」→「跳过校验」（见 8.8）。
- EES 单人「发链接 → 推荐链接」完整生成链路已跑通：H5 预览渲染成功、生成短链 `https://dwz.cn/ojzBCOlq`（type1）/ 复制通用链接 `https://dwz.cn/Oh1DQuHg`（type2）、短链 302 落地页 200（见 8.9）；未点「发送」。截图在 `.../opencode/03_dialog.png`、`04_dialog_preview.png`、`05_after_copy.png`。

**待查项**

- 订单中心与支付中心数据不一致：`payCard/detail` 报 code=1「订单号不存在」、`/orders` 待支付为空（批次单号 `433715450493796358`），记为待查项，不作为支付结论依据。

**推断未验证**

- 关联并集在 C 端页面完整可见（接口已返回，页面本轮未用付费商品(100 分)样本走完）。

**没做 / 待验证**

- 页面层付费商品(100 分)完整链路：选品 → 去结算 → 订单确认 → mock 支付 → 回读（本轮执行中）。
- 优惠活动、异收款主体反例。
- 跨学年/跨学季样本的 C 端页面下单。
