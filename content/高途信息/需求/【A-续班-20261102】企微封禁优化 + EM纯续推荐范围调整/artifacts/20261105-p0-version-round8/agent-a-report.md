# Agent A：EM TEST 关键场景验证

执行时间：2026-11-05（TEST / `test-gtbg-dev-3`）。本轮只做真实只读回读，未创建班级/订单、未支付、未部署、未改代码；`status1-main-case.json` 不重放。

## 运行绑定

| 服务 | 实例 / IP:端口 | 镜像提交 |
|---|---|---|
| product-b | `product-b-7d48b8fb74-lxqvg` / `10.218.248.248:28688` | `07ba05df6cfabcf0472e1ad27e26ff95cff98467` |
| cart | `cart-gaotu100-com-79789ddcf4-vqnpj` / `10.218.237.47:28688` | `a34016fdf206d0163b1dd473c67ac10674ecb4b5` |
| order / order-b | `10.218.236.236` / `10.218.237.111` | `0cc8ef68b6c29f1d3101f5fa08ea7ec634050bf9` |

主计划 `585960797778243584`（`dcg-扩科排除-大班计划-1020`，type=1/status=2）→从计划 `586116340522184704`（`dcg-小班扩科排除-计划`，type=2/status=2）。大班前置班 `585960582537144320`（`dcg-扩科排除-前置-五年级语文`，bizNumber=`15YW26CCRI11001`，课程 `585960577856301056`）；大班后置 `585960755422160896`（`dcg-扩科排除-后置-六年级语文`，bizNumber=`16YW26X6IM11001`，课程 `585960751831836672`）。自建可售反例前置班 `588861397654462464`（`B测试-五年级语文春季前置B`，bizNumber=`15YW26C6M111001`，课程 `588861395571990528`，课节 2026-11-08 14:10–14:15）；后置班 `588861402658267136`（`B测试-五年级语文暑假后置1B`，bizNumber=`15YW26XTRO11001`，课程 `588861400563212288`，课节 2026-11-08 14:20–14:25）。小班前/后商品为班号/SKU `586084334251927552`（`dcg-小班扩科排除-数学`）/`586097025945298944`（`dcg-小班扩科排除-数学-后置`），课程 `18314034380997173`→`18314034380997207`；该样本中 DMS 的 number 与 biz_number 同值，不能推广为所有小班对象的字段规则。

## 实测结果

1. **主计划纯续并集与计算**：cart ACL `getRenewalDetail(7658127801,585960797778243584,true,false,null,null,false)`，trace `cart_gaotu100_com.305.17938796755390310`，code=0。返回大班 SKU `585960755422160896`/type=2/recommend_type=1 与小班 SKU `586097025945298944`/type=6004/recommend_type=1；日志说明前置课程集合为 `585960577856301056,18314034380997173`，小班匹配最终命中 `586097025945298944`。该历史观察用户已购大班后置，不能作为新单样本。

2. **从计划隔离**：同一接口 `getRenewalDetail(7658127801,586116340522184704,true,false,null,null,false)`，trace `cart_gaotu100_com.296.17938798985810314`，code=0，仅返回从计划自身 SKU `586090628920764416`/type=6004/recommend_type=1；没有主计划大班 SKU。该结果与 product-b `relation/list?renewMasterNumber=586116340522184704` 空数组（trace `4899b6bb-2078-4636-b8fe-99d790601036.0.3`）一致，证明当前纯续入口未因 A→B 自动反向扩大。带扩科参数的同计划调用另有 `recommend_type=2` 候选，不能拿来判纯续隔离。

3. **碰撞/去重**：已复用 round7 受控证据，不重放。对主计划专用前置 `588861395571990528` 临时加入已存在后置课程 `585960751831836672`，`collision-confirm.json` 回读 code=0，返回原后置 `588861400563212288` 与冲突后置各一行；cart trace `cart_gaotu100_com.296.17938731923980243` 的过滤日志把重复课程集合由 5 项去重为 4 项，且最终命中原大班后置。随后 `collision-restore.json` 独立回读仍只保留原后置，`restored_to_original=true`。该证据证明同年级同商品碰撞去重；跨年级保留仍未执行。

4. **真实计算/同单**：已复用 round7 `dual-order-readback.json`。受控学员 `7707220467`，大班后置 `588861402658267136` type=2/100分 + 小班后置 `586097025945298944` type=6004/0分，同 pay_number=`433655835275559341`；DB 两行 order_status=2，支付表 `original_price=100,coupon_price=0,activity_price=0,price=100,real_price=100`。代入 `100 + 0 = 100` 分，与支付回读一致。该学员现已购两件，不能再作为“可售未购”样本。

5. **可售状态与可售未购定向补验**：改用登记学员 `7658129872` 和自建两班（不新增对象）。其前置大班订单 `433655258676199942`/pay=`433655258676199430`，DB `order_status=2`、price=0；目标后置大班 `588861402658267136` 在 DB 未找到该用户订单。cart 固定 Pod 读取 `cart-operation-fixed-ip-fromC0.json`，trace `cart_gaotu100_com.296.17938766689070280`，目标大班及小班 SKU 均 `signUp=0`，后置大班课节日期为 2026-11-08 14:20–14:25，尚未开始。正常 order-b prepare（`/intranet-rpc/order-b/web/order/batch/boss/prepare?userId=7658129872`）trace `e279fb8c-6fab-4b7d-9384-6d1bd386e09b.0.3`，code=0，`productList` 同时包含大班 `588861402658267136/type2` 与小班 `586097025945298944/type6004`，大班课程价格100、1课节、唐稳01主讲，小班 `salePrice=0`，`totalPrice=100`，有效期 2026-11-08–2029-11-08。独立 DB 回读发现小班后 SKU 已有 order_item `433534690352694278`/pay=`433534690352693254`/status=2，不能单凭 status2 断言推荐失败；订单有效性及 signUp 数据来源已按下方定向确认解释。本轮只确认大班后可售/未购和两商品 prepare 计算，不把 signUp0 或 prepare code0 冒充双商品未购下单通过。

## 小班订单有效性与 signUp0 来源（20:11 定向确认）

- 精确 SQL 同时约束订单项 `433534690352694278`、pay `433534690352693254`、user `7658129872`、SKU `586097025945298944`，命中1行；SPU=`18314034380997207`、sku_type/order_type=6004、quantity=1、status=2、refund_type=0、sku/spu_version=`1792565249996`。cancel/finished/failed_time 均为零时间；order_refund.refund_item 按该订单项精确查为0行。不是另一用户、另一 SKU 或已确认的全退单。
- 目标 cart@a34016fd 真实读取该 SKU/用户：`listBySkuNumbersAndUserIdNoRefund` 返回上述唯一订单项、status2/refund0，trace `cart_gaotu100_com.303.17938806746400323`；`ListByClazzNumbersAndUserIds` 对同 SKU/用户返回空，trace `cart_gaotu100_com.301.17938806745880326`，DB order_info 同键也为空。
- 与部署提交对应的代码：小班权益规则为 order_item status∈{2,4} 且排除 refund_type=2；本订单满足。大班主计划的纯续 VO 组装却调用 `ListByClazzNumbersAndUserIds`（order_info 体系）并按 status2/7设置 signUp，因此本例的 signUp0 可由该读取路径解释，不能据此证明小班未购，也不能归因为退款、规格变更或履约失效。该差异是已核实的订单来源分歧；是否需修正跨模式已购展示由主 Worker 决定，本轮不改代码。
- 原始 SQL/失败回执保留 `agent-a-order-validity.json`（误带不存在 isdel 列的首次查询）、成功回执 `agent-a-order-validity2.json`、运行时对照 `agent-a-order-route-confirm.json`、精确提交代码摘录 `agent-a-order-rule-source.json`。成功查询已纠正 schema，未重放任何写操作。

## 证据与边界

- 本轮机器结果：[agent-a-readback.json](/tmp/w1-p0-243aa61a/round8/agent-a-readback.json)。
- 既有碰撞/恢复：[collision-confirm.json](/tmp/w1-p0-243aa61a/round7/collision-confirm.json)、[collision-observe.json](/tmp/w1-p0-243aa61a/round7/collision-observe.json)、[collision-restore.json](/tmp/w1-p0-243aa61a/round7/collision-restore.json)。
- 既有同单与计算：[dual-order-readback.json](/tmp/w1-p0-243aa61a/round7/dual-order-readback.json)、[dual-paid-readback.json](/tmp/w1-p0-243aa61a/round7/dual-paid-readback.json)。
- 管理员 status1 保存/清空已由 [status1-main-case.json](/tmp/w1-p0-243aa61a/round8/status1-main-case.json) 完成，本轮未重放。

结论：纯续并集、从计划纯续隔离、同商品碰撞去重、`100+0=100` 真实计算，以及自建大班后置的可售/未购回读均有绑定版本/trace/DB 证据；小班后置在有效订单规则下有权益，signUp0由大班入口的订单来源分歧解释，“双后置均未购”不成立，跨年级保留仍未执行。未用 HTTP200、预览或旧订单替代业务结果。
