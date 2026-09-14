# 业绩归因

判不出归属人、排行榜显示 0、可续分母、判单开关与回溯。

## 症状路由

| 症状（用户会怎么说） | 去哪 |
|---|---|
| 业绩表查不到这单 / 归属人为空 | [`查不到归属人.md`](排查/查不到归属人.md) |
| 判单正常但排行榜显示 0 | [`ranking-zero.md`](排查/references/ranking-zero.md) |
| 不算可续分母 / 可续锁在别的订单 | [`can-renewal.md`](排查/references/can-renewal.md) |
| 已确认 is_attribution=0，查谁改的 / 要回溯 | [`setting-and-backtrack.md`](排查/references/setting-and-backtrack.md) |
| 对完日志要跳源码 | [`code-map.md`](排查/references/code-map.md) |

每份排查文件末尾附该问题的历史案例。新问题在 `排查/` 新建一份并在上表加一行。
