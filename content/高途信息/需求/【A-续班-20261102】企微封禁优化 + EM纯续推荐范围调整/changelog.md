# 决策摘要

- 2026-11-02 确认一个主需求两个子项；统一名 `【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整`。
- Q1=B；Q2=A。
- 推荐并集只并纯续（主+从），扩科不变。
- 单一 Apollo 开关 `renewal.pure.relation.enabled`（默认 false，cart+order 共读）。
- 历史兼容不刷数。
- 子项2 接口收敛：**只保留单个「最终确认」save 接口（全量集合差分落库）**，去掉独立 bind/unbind（2026-11-03 所有者口径）。
- 「大小班报错」线上真实报错码无直接证据（代码级枚举 SAME_CLAZZ=4/SAME_COURSE=5/PAYMENT_SIZE=3）——已知缺项。
- 2026-11-03 统一分支 `feature-xuban-pure-relation-20261102`（cart 亦然）。
- 2026-11-03 修复：`RenewalMasterRelationController` 返回类型改 `RestTraceResponse`（原 `RestResponse` 在异常路径触发 CCE，非管理员报「未知错误」）。
- 2026-11-03 部署 `test-gtbg-dev-3` 四服务 eureka UP；product-b 侧 save/list/差分/缓存/下发已验证。
- 2026-11-03 阻塞：`product`/`order.gaotu100.com` Apollo 均无发布权限（litao04）→ product-c 下发与 order 放行开关在 test 无法打开，cart 并集/order 放行端到端未验证。
- 2026-11-03 修复：`RenewalMasterRelationService#save` 落库 `create_account_id`（登录上下文兜底），push `116175f00`。
- 2026-11-03 代码级结论：cart `course.filter.type{30,40}` 是**课程类别**（30-专题课/40-系列课）非授课模式；`coreHandle` 全程无 `clazzRoomType` 过滤 → **跨模式（小班）并集课程不会被该过滤掉**（此前交接的「大班只处理大班课程类型」属对 `courseTypes` 的误读）。小班主计划走 `SmallRenewalCoreService` 为另一路径，未实测。
- 2026-11-03 边界用例（product-b HTTP）：非管理员/空白名单、状态非可编辑、超上限10 均按预期拦截。
- 2026-11-03 小班主计划结论：`SmallRenewalCoreService`/`SmallRenewalContextBuilder` 链路**无大班/小班模式或计划归属过滤**（`ProductType` 分支仅 单课6004/组合51；白名单缺项降级非丢弃），合并后的从计划（大班）课**不被丢弃** → 无需改码（实现用「统一合并 courseNumbers」替代原设计的小班 SubBuilder 改造）。
- 2026-11-03 端到端（Arthas 临时开 product-c/order 开关，测后复位）：product-c 下发含 `related_renewMasterNumbers`；cart 收到 `related_renew_master_numbers` 且合并（日志 `size=2`，开关关则无）；order 大班2+小班6004 跨模式放行、同模式真重复 `SAME_COURSE` 拦、开关关回拦。
- 2026-11-03 **cart 实际报价验证发现跨模式缺口**：学员 7658127801（主/从前置课均有已支付订单）下 `getRenewalDetail(主计划)` 只返回主(大班)纯续+扩科，**无小班从计划报价**。根因：合并后小班前置课被「订单过滤」剔除——`listByCourseNumbersAndUserIdAndStatus` 只读 `order_info`(大班)、`listBySpuNumbersAndUserIdAndStatus` 只读 `order_item`(6004)。需补齐另一模式订单查询（主流程，待决策）。
