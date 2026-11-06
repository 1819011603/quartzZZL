# 续班 B 端推荐/下单：构造与复现步骤

> 适用：验「纯续关联」在 **B 端**（EES 续班服务 / EM 续班计划）的**推荐商品列表**（`recommendProductList`）与**批量下单**（BossBatch 代下单）。
> 环境：TEST / 泳道 `test-gtbg-dev-3`。网关 `test-fuwu.baijia.com`；B 端接口**必须带 `b_client: EES`**（否则报 `code:42 调用staff失败`），并带 `traffic-env: test-gtbg-dev-3`。
> C 端对应文档见 [续班C端下单_构造与复现步骤.md](续班C端下单_构造与复现步骤.md)。

## 1. 前置与环境

| 项 | 值 |
|---|---|
| 网关 | `test-fuwu.baijia.com`（B 端路径多带 `/bgwApi/`） |
| 泳道 | `test-gtbg-dev-3`（请求头 `traffic-env` + `ingress-traffic-env` 都填） |
| 必带头 | `b_client: EES`、`content-type: application/json` |
| 学员 | `7658129872`（三计划在读）；`7707220467`（仅主→补 B 前课后 2 件）；`7658127801`（已购，勿当新单正例） |
| 计划 | 主计划 `588858850300473344`（关联小班 `585960797778243584`、`586116340522184704`）；待开始正例 `588872241920421888` |
| 商品 | 大班 `588861402658267136`（100 分/¥1.00）、`585960755422160896`；小班 `586097025945298944`（0 元） |

## 2. 造数（data-agent，复用现成 fixture，不要每次重建）

**能做什么**：大/小班课、GPS/OMO/CES 教学产品、续班计划与前后置班、辅导班排课、下单与 mock 支付、可续关系。
**不能做什么**：造出来的对象**不会自动「可售/可续」**；造数返回 `ok`、`published=true` 都不等于能下单。必须回读 `saleStatus>0`、真实课节数>0、老师非空、`order/prepare` 可售。

```bash
curl -s https://sd.baijia.com/api-qa/data-agent/scenarios          # 看场景
curl -s https://sd.baijia.com/api-qa/data-agent/scenarios/<name>   # 看参数契约
curl -s -X POST https://sd.baijia.com/api-qa/data-agent/scenarios/<name>/run \
  -H 'Content-Type: application/json' \
  -d '{"params":{...},"options":{"traffic_env":"test-gtbg-dev-3","timeout_s":600}}'
```

铁律：`traffic_env` 必填（漏了会 code=0 但不落库）；body 包一层 `params`；价格单位=分（100 分=¥1.00）；手机号须是已注册测试号。

**本需求实际用到**：
- 主续班计划 `588858850300473344`（已关联小班 `585960797778243584`/`586116340522184704`）
- 目标学员 `7658129872`；B 端批量下单用的未购用户（如 `n`=续班扩科隔离测试）
- 已付接口证据：支付 `433655835275559341`，订单 `433655835275559853`/`433655835275560365`（C 端）；B 端批量单见 §4

## 3. B 端推荐列表（`recommendProductList`）

**接口**：`POST /bgwApi/product-b/b/renewMaster/recommendProductList`

```bash
curl -s 'https://test-fuwu.baijia.com/bgwApi/product-b/b/renewMaster/recommendProductList' \
  -H 'content-type: application/json' -H 'b_client: EES' \
  -H 'traffic-env: test-gtbg-dev-3' -H 'ingress-traffic-env: test-gtbg-dev-3' \
  --data-raw '{"pager":{"pageSize":50,"current":1,"total":0},"renewMasterNumber":"588858850300473344","userId":7658129872,"filterTest":false}'
```

**链路**：product-b `RenewalProductServiceImpl#recommendProductList` → cart `/feign/renewal/renewalCart` → `RenewalService#getRenewalDetail`（大班/小班路径）。
- 大班：`processClazz`（纯续）+ 扩科 + 加购；小班：`SmallRenewalCoreService` + 扩科 + 加购。
- **B 端会过滤已购**（`signUp==1` 不返回，`RenewalProductServiceImpl` L448）→ 「一个商品都没有」常见于**唯一候选已被该 user 买过**，不是没算出来。核对：直接调 cart `RenewalService#getRenewalDetail` 看 `sign_up`。
- 返回字段：`productNumber / productType（2 大班 / 6004 小班）/ price / teacherList / bizNumber`。

**小班课(6004) 售价坑**（2026-11-06 已修，cart commit `34bf1fd7`）：小班课取价走 course-center，其 `price` 是 **-1 哨兵或 null**（不含商品定价），真实售价在**商品系统 SKU** 上。此前的纯续补全 `RenewalService#processClazz` 未回填 SKU 售价 → B 端展示 `-1` / `¥ null`。修复后 6004 售价回填 SKU `salePrice`（样例 SKU `586097025945298944`=0）。同口径参考 `convertNormalClazzResultToDTO` / `setSmallClazzVO`。

```bash
# 接口层等价复现（acl 桥直调 cart，绕网关）
com.gaotu.renewal.RenewalService#getRenewalDetail("7658129872","588858850300473344", true,false,null,null,false)
# 预期 grade16 大班 588861402658267136(100)+grade11 小班 586097025945298944(0+SKU回填)+grade15 585960755422160896
```

## 4. B 端批量下单（BossBatch 代下单）

**真实入口**：`order.gaotu100.com` 路由 `/web/order/**` → `BossBatchOrderController`（`/web/order/batch/boss/prepare` + `/createOrder`）。
- **网关 `/web/order/**` 有登录拦截（返 700/CAS）** → 改**容器直连**（`invoke_feign`，Eureka IP 直连容器）绕过。
- 入参：`productList`（`[大班 type2 585960755422160896 + 小班 type6004 586097025945298944]`）+ **有效 `source` orderTag**（test `can.create.order.when.invalid.source=false` 会强制校验）+ 一个**未买过该课**的用户。
- 回读：DB `pay_number` 下须同时有**大班 `order_info`** + **小班 `order_item`（product_type=6004）**，`order_status=2`。

**本需求已跑通（2026-11-04，等价接口层）**：preview `code:0`（大班+小班双展示，trace `order_gaotu100_com.446.17937602669630086`）；create `code:0`，orderNumber `433534690352693254`（trace `order_gaotu100_com.444.17937606425700088`）；同模式真重复拦 `ONCE_BY_LIMIT`；跨模式同请求加 `code:0`。
**遗留**：跨请求/增量混加大班+小班会触发既有 `PAYMENT_SIZE`（本需求未改、非本场景）。

## 5. 纯续并集口径（先搞清数量）

关系**单向**（主→从）；主计划 `renewalNumber` + 关联从计划前置课**并集**，按学员在读订单过滤后各自展开。

| 场景 | 商品数 |
|---|---|
| 仅主有资格（7707220467 仅买主前课） | 1 件 |
| 主+从均有效（7707220467 补 B 前置课后） | 2 件 |
| 三计划均在读（7658129872） | 3 件 |

规则：同商品去重、跨年级保留、同科目不因学科误去重。

## 6. 常见坑

| 现象 | 原因 / 处理 |
|---|---|
| 推荐「一个商品都没有」 | 计划错配 / **唯一候选已购(signUp==1) 被 B 端过滤** / 从计划关联已软删(`renew_master_relation.is_del=1`) |
| 小班课售价为负/`¥ null` | cart 纯续路径未回填 6004 SKU 售价（已修 `34bf1fd7`；course-center 6004 price=-1 哨兵） |
| 推荐条数忽多忽少（如「一次 2 一次 4」） | 「推荐排除」`/feign/renewal/otherModeInReadSubjects` 间歇 404（cart 打到旧 student-data 实例）→ 降级「不排除」→ 扩科多；该泳道 student-data 需只剩含该接口的版本 |
| B 端接口报 `code:42 调用staff失败` | 漏带 `b_client: EES` |
| 下单接口返 700/CAS | `/web/order/**` 网关登录拦截，改容器直连 |
| 造数成功但下单无商品 | 未过可售门槛：查 `saleStatus`、课节数、老师、`order/prepare` |

## 7. 证据与未验证项

**已验证**
- 学员 `7658129872` 在计划 `588858850300473344` 下 `recommendProductList` 返回纯续商品；B 端价格链路与 C 端 `/web/renewal/productList` 对齐（2026-11-06）。
- B 端批量下单接口层跑通（orderNumber `433534690352693254`，大班 order_info + 小班 order_item 6004，status=2）。
- student-data 部署到泳道 `test-gtbg-dev-3`（`feature-xuban-pure-relation-20261102`=release `f7845f9e`，含推荐排除接口）。

**未验证 / 待办**
- B 端**页面层**（EES 续班服务行内「发链接/推荐」、EM 续班计划「选择商品」弹窗）完整下单链路。
- 小班课售价修复后**页面**展示 0 的回归。
- 优惠活动、异收款主体反例；跨学年/跨学季 B 端页面下单。
