# 2026-11-15 全新造数补验：批量预热 role=2 端到端（W1）

> 回应 owner 纠正「主从关联和下单，你也可以造啊…去造数项目去看」——上轮「造数项目缺
> 主从关联 save 与购课下单 scenario」的判断**错误**：关联与下单能力在造数项目里完整存在
> （`continueclass/plan_relation.py` 关联保存+回读核对、`batch_create_order`+`mock_pay` 下单支付、
> `knowledge/renewal-plan-relation.md`/`knowledge/execution.md` 文档），上轮只看了 sd.baijia.com
> 的 17 个 HTTP scenario 列表没读仓库文档。本轮全新造数端到端验证。

## 造数链路（全部走造数项目，test 泳道 test-eco-7，数据落 TEST 库共享）

| 步骤 | 工具 | 产物 |
|---|---|---|
| 1 主/从计划骨架 | `renew_clone_plan`（dept=10007722；默认部门报「部门非法」，环境 11-06 后变化） | 主 M=590563861447557120、从 S=590563948968001536 |
| 2 克隆课程+班+发布 | `renew_from_source build`（语文，publish） | 前置课主 590563875993239552 / 从 590563954137317376，各带后置课班（未开售） |
| 3 主从关联 | `continueclass/plan_relation --mode append --apply`（自动回读核对 verified=true） | M→S 单向关联 |
| 4 正经班 ×4 | `create_renewal_regression_clazz`（自动选主讲+排课节+发布+2 辅导班） | 主前 590564403009634304 / 主后 590564313490604032 / 从前 590564421519097856 / 从后 590564441871958016，回读 saleStatus=40/课节1/老师1（按班号精确匹配逐班核过） |
| 5 流程+节点 | `product_b_b_renewal_process_edit`（configType=1、node type=3 productType=2、时间窗当前~+1y） | M/S 各 1 流程——**关键修复**：骨架无 process 时 effective=false（isEffective=productType>0），预热直接跳过 |
| 6 用户下单 ×2 | `batch_create_order`（productType=2 按 clazzNumber，100 分单）+ `mock_pay` | 7704848531 购主前+从前置班，真订单 434525581180666386 / 434525740094456338，DB 复核 order_status=2 已支付 |

踩坑记录：① sd.baijia.com `renew_build` endpoint 502（其余场景正常），改本地
`workflows/scripts/renew_from_source.py` 执行成功；② `renew_build` 建的班 saleStatus=0/无课节/无老师
不达可售门槛，须 `create_renewal_regression_clazz` 补正经班；③ BFF orderNumber 是 pay_number，
post_actions db_reconcile 自动回填真订单号；④ get_order_info 的 order_number 须传 integer。

## 验证（test-eco-8 @3b49fda6，pod cart-gaotu100-com-7b989f97d-7nw7q）

前置：cart 桥查主/从前置课订单各 1 条（7704848531, status=2）——数据可见。

1. Apollo v2=true + prefix=false（写老 key，release `20261115031453`）。
2. `preheatByRenewalNumber("590563861447557120")`（批量预热本体）正常返回。
3. **Redis 老 key（arthas）**：`renewal:preheat:590563861447557120:7704848531` =
   `{590563875993239552:{sku:590564278055026688, renewal_role:1}, 590563954137317376:{sku:590564441871958016, renewal_role:2}}`
   ——**全新造数上主+从合并（role=1 主前置课条目 + role=2 从前置课条目）直接实证**。
4. **回退态老链路读取**（C 端 `/web/renewal/cart`，TID `cart_gaotu100_com.294.17946839875570153`）：
   code=0 无异常；`renewalRole=1`×1（W1主计划后置正经班-1115）+ `renewalRole=2`×1（W1从后置正经班-1115）
   正确展示。
5. 恢复 v2=false / prefix=true（release `20261115032006`），桥回读 `isPreheatV2Enabled=false`。

## 结论

owner 指出「关联和下单可以造」**正确**：造数项目具备完整能力（关联 plan_relation / 下单 batch_create_order+mock_pay /
正经班 create_renewal_regression_clazz / 流程 process_edit），配合 renew_clone_plan+build 可从零造出
「从计划对用户有可售商品」的完整场景。全新造数端到端验证与上轮存量复用验证（TID 17946794980070108）
**结论一致**：批量预热主+从合并值正确写入，回退态老链路读取无异常、role=1/2 条目正确展示。

fixture 已登记（plan:590563861447557120，含全部班号/订单号与保留边界）。
