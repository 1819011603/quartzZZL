# 2026-11-15 批量预热全量用户级运行时验证（W1，补 G4 缺口）

> 回应 owner「全部验证完了吗」与一轮遗留缺口：此前样本计划 is_test_data=1 被 Job 规则过滤，
> 批量预热（Job 全量用户）路径无运行时证据。本轮以真实非测试计划触发闭环。

## 验证对象与方式

- 代码版本：`3b49fda6`（pod `cart-gaotu100-com-7b989f97d-7nw7q` / 10.218.251.72，test-eco-8，Eureka UP）
- 计划选择：`545361759016388608`（J 计划，is_test_data=0、type=1 大班、14 门前置课、
  activityNumber=589897311212015616、关联从计划 551533000353986560——满足 RenewalV2JobHandler 全部过滤条件）。
  候选筛选：ListRenewalNumber SQL（gaotu.node_config/process_config，30 个进行中计划）逐一查
  `/c/renewMaster/listRenewalWithProcessByNumber`（product，test-eco-8），is_test=0 且前置课/活动号非空者 6 个，取关联最全者。
- 触发方式：Apollo TEST `renewal.preheat.v2.enabled` true→发布（release 20261115011338）→回读
  `isPreheatV2Enabled=true` → 经 acl 桥调 `RenewalV2JobHandler#execute("[\"545361759016388608\"]")`
  （与 xjob 调度同代码路径；xjob-admin 登录态失效故走桥）。prefix=true 保持，写 `renewal:preheat:v2:` 前缀。
- 验证后恢复：`renewal.preheat.v2.enabled` false→发布（release 20261115012131）→回读 `isPreheatV2Enabled=false`。

## 规模

前置课 14 门已购用户去重 509（order_status 含非支付态的粗集；Job 实际口径 `order.paid.status={2,7}`，
其中 545361294648225792 单课 466 单全为 status=2）。

## 结果（全过）

1. **Job 执行成功**：`execute` 返回 `ReturnT code=200`，耗时 15.0s（509 用户并行，batch=1000，
   线程池 renewalPreheatAsyncTaskExecutor）。
2. **有可售商品用户 100% 写入**：course 545361410570399744 的 6 名 status=2 用户
   （19758758649346/3131496756/2647579264/2647579295/2339111865194144410/2339111865194147855）
   arthas `hasKey` 6/6 true，TTL 生效。
3. **值结构正确**：抽查 3 用户值均为 `{"545361410570399744":{"product_sku_number":545361835239485440,"renewal_role":1,...}}`
   ——`renewal_role` 字段按 owner 口径标记主计划纯续（=1）。
   （主+从混合值结构 role=1+role=2 已由单用户路径验证：TID `cart_gaotu100_com.290.17946706331600008`，
   5 条=1 主+4 从；批量与单用户走同一 `preheat(userId, config, related)`/`writePreheat`，代码同源。）
4. **空结果用户不写 key 非异常**：466 单大课与多门小课用户 key 不存在（抽样 50+18 全 miss）；
   抽 null 用户 20457738914306 单跑 `RenewalV2Service#preheat` 返回 `{}` 无异常——
   属商品不可售/无推荐配置的业务空结果（与一轮 BC 验证 saleStatus=50 过滤现象一致），非计算错误。
5. **开关恢复**：已回读 false；验证写入的 v2: key 约 6-8 个，TTL 26h 自动过期，无害保留。

## 证据

- execute 返回：`{"code":0,"data":{...RenewalV2JobHandler#execute":{"code":200}}}`（15.0s）
- Apollo 发布：20261115011338-release（开）、20261115012131-release（恢复）
- Redis 抽查：arthas vmtool（pod 内 StringRedisTemplate.opsForValue/hasKey），见上
- 开关回读：isPreheatV2Enabled true/false 两态

## 未覆盖

- is_test_data=1 计划被 Job 跳过的反向分支：本轮未重复验证（一轮已实证 skip 逻辑，代码未变）
- 从计划条目（role=2）在批量路径的直接样本：本计划从计划对 6 名用户无可售商品故无 role=2 条目；
  合并结构由单用户路径+代码同源论证，未另造跨计划用户（造数成本高、增量证据有限）
