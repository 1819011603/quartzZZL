# 2026-11-06 续班后续复核

## 复核范围

- 代码仓：product-server、cart、order，分支 `feature-xuban-pure-relation-20261102`。
- 明确保持不改：关联全集保存并发覆盖语义。
- 现有逻辑基线：未报名在前、已报名沉底；本轮未调整排序。

## 造数基线回读

TEST / `test-gtbg-dev-3` 复用既有数据，未新增计划、关联、订单或支付。

- 主计划 `588858850300473344`、从计划 `585960797778243584`/`586116340522184704` 均在 `gaotu.renew_master`，`status=2,isdel=0,is_test_data=1`。
- 主计划到两个从计划的有效关联已在 `gaotu.renew_master_relation` 回读；反向软删记录保留。
- 候选班级 `585960755422160896`、`586097025945298944`、`588861402658267136` 均 `sale_status=40`；有效课节分别为 1、2、1，且每节 `teacher_number>0`。
- 订单/订单项按用户、课程、班级回读。用户 `7658129872` 已存在大班后置有效订单，不能再作为未报名样本；后续未用该用户证明未报名路径。

## 本轮修复

### cart `4de323d2`

- 纯续开关关闭时，即使残留关联列表非空，也不执行跨模式订单旁路查询，保持老计划旧逻辑。
- 跨模式前置订单旁路缓存默认关闭，支付/退款状态实时查；只有显式开启 `renewal.pure.relation.order.cache.enabled` 才使用缓存。
- 关联缓存版本在纯续总开关关闭时返回空版本，避免配置漂移使用新缓存键。

### product-server `455e8ba8d`

- `renewal.pure.relation.enabled=false` 或缓存失效开关关闭时，不读取/生成推荐缓存版本，回到旧缓存协议。

## 验证

- cart 定向测试：26 项通过。
- product `RenewalMasterRelationServiceSaveTest`：16 项通过。
- order `CartSameClazzOrCourseImplTest`：17 项通过。
- product C/B 与 cart 已部署 TEST，目标 commit 均 Eureka UP：product C `10.218.251.125`、product B `10.218.238.105`、cart `10.218.239.166`。
- product C 关联计划缓存状态返回非空版本；无关联计划 `588872241920421888` 返回空版本；product B 当前关闭纯续开关时返回空版本，证明旧协议隔离生效。
- cart `getRenewalDetail(7658129872,588858850300473344,...)` 返回主+关联计划商品，含小班 SKU `586097025945298944`，调用 trace `cart_gaotu100_com.298.17939748068670008`。

## 未改与后续边界

- 并发全集保存仍保持原实现，未触碰。
- order 跨模式放行位于购物车 `ADD_CART/CART_DETAIL` 校验链路，按续班下单需求验证通过；没有改订单创建、支付、退款等通用流程。校验器未携带续班计划号属于实现取舍，不影响本次需求实际生效。
- product client `number` 保持 String：前端计划 ID 使用文本框并按字符串提交，String 同时承载 18 位 ID 和批量精确查询；仓内未发现依赖 Long getter 的调用方。
