# 决策摘要

- 2026-11-02 确认一个主需求两个子项；统一名 `【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整`。
- Q1=B；Q2=A。
- 推荐并集只并纯续（主+从），扩科不变。
- 单一 Apollo 开关 `renewal.pure.relation.enabled`（默认 false，cart+order 共读）。
- 历史兼容不刷数。
- 子项2 接口收敛：**只保留单个「最终确认」save 接口（全量集合差分落库）**，去掉独立 bind/unbind（2026-11-03 所有者口径）。
- 「大小班报错」线上真实报错码无直接证据（代码级枚举 SAME_CLAZZ=4/SAME_COURSE=5/PAYMENT_SIZE=3）——已知缺项。
