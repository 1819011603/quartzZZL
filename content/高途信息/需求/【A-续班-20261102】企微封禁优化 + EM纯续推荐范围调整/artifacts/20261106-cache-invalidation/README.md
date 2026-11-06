# 关联修改与推荐预热缓存失效验证

## 改前证据

真实 TEST 链路先预热主计划，再清空关联：关联查询已经为空，但旧 `corePreheatCache` 仍返回从计划班级，说明仅清理关联关系缓存不能使 cart 的预热 Redis 失效。见 `before/before-cleared-cache.json`、`before/before-cleared-b.json`。

## 改后证据

环境 `test-gtbg-dev-3`：cart commit `deea4c9e`，Pod `10.218.251.197`；product C/B commit `84739aab8`，Pod `10.218.251.99` / `10.218.248.209`，三者均新 Pod Running/Eureka UP。流水线：cart `1332476`、product C `1332478`、product B `1332479`。

真实链路顺序及断言全部通过，原件见 `after/*.json` 和 `after/summary.json`：

1. 关联版本下预热并读取，命中新版本预热缓存。
2. 清空关联，product 版本推进；cart 读取新版本 key，旧预热不命中。
3. 清空后 B 端推荐只返回主计划结果。
4. 恢复关联，恢复后的新版本仍不读取旧预热；重新预热后才命中新版本。
5. 无关联老计划读取配置时 `relatedRenewMasterNumbers` 为空，仍走旧缓存 key 规则。
6. 大班关联预热入口和小班预热入口均在新 Pod 实际执行无异常；小班预热只触发下游数据缓存，不写整份推荐结果 Redis。

本次改动的 Apollo key 为 `renewal.pure.relation.cache.invalidate.enabled`，代码默认 `true`；未配置与开启等价，设置 `false` 作为回滚。关联保存、预热和推荐都没有修改订单数据。小班预热仍只预热下游数据，不把整份推荐结果写入该 Redis；其关联前置课合并受同一版本配置读取保护。
