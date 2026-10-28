# 续班保障 · 共享 Redis 班级缓存被压高（CPU 告警）排查与优化

> **只解决**：续班压测期，`gaotu:studentdata:sync:clazz:v1:<clazzNumber>` 这类**班级缓存热 key** 把共享 Redis 实例 CPU 打高（如 2026-10-29 00:18 `gaotu-fairy-prod` 89.74%）。
> Sentinel 流控告警走 [`续班保障打限流排查.md`](续班保障打限流排查.md)。

## 结论（谁打满的）

- 热 key `gaotu:studentdata:sync:clazz:v1:<clazzNumber>` 是 **student-data 的班级信息缓存**（`student-data-client` `ClazzSyncAclService`，TTL 60s）。
- 主力读写方 = **`student-data-dws` 的消费链路**（`DwsSubclazzStudentSyncConsumer` 消费 `gaotu_subclazz_student_event_prod`，逐条按班级号读缓存）；次要 = `student-data` 服务查询。
- 机制：续班压测 → `subclazz_student` 事件洪峰 → 消费端按班级号高频读缓存 + 60s TTL 反复过期→回源(`course-center /feign/clazz/query/listByNumbers`)→重建 → 读(GET)写(SET)双高，把单线程 Redis 顶到 CPU 81%。
- 告警实例是**共享 Redis**（`r-2ze51b484ccb4964`）：student-data(dws) 用 db15，reach-service/reach-data/crm-app 用 db0 —— 所以 CPU 告警挂在了 fairy 名下。

关键指标（2026-10-29 00:16–00:19 本地）：`TotalQps` 7k→**129k/s**、`GetQps` **11.4万/s**、CPU 5%→**81%**、`Keys` **+170万**、`ExpiredKeysPerSecond` 峰值 **3456/s**。

## 怎么查（复用）

1. 实例 CPU/QPS/key 趋势（阿里云 Tair，注意 **UTC 时间**）：
   `aliyun_console_api(product=kvstore, action=DescribeHistoryMonitorValues, params={InstanceId,StartTime:"…Z",EndTime:"…Z",IntervalForHistory:"01m",MonitorKeys:"CpuUsage,TotalQps,GetQps,PutQps,Keys,Expires,ExpiredKeysPerSecond"})`。
2. 谁在读写某 key：先拿 key 前缀定位定义代码（`rg` 客户端 SDK / 各仓库），再在**候选服务 pod** 用 arthas 量缓存方法调用速率：
   ```
   pod_term.py arthas --service-code <code> --env prod \
     --command 'monitor -c 2 -n 3 com.gaotu.student.data.client.utils.RedisCacheUtilV1 listByKeysCache' --stop
   ```
   或按连接：`pod_term.py exec --cmd 'netstat -tan | grep -c <redis_ip>:6379'`（连接数≠命令量，仅参考）。
3. 实例被哪些服务用：拉一条调用链，看各服务 `type=redis` 的 `operation` 里出现的实例域名。

## 优化改进

分三档，按「止血 → 低风险改造 → 架构」推进；下面均为**建议**，改配置/发布需按授权执行。

### A. 压测期止血（配置级，最快）

1. **调大班级缓存 TTL**：`student-data` `clazz.data.query.cache.time` 60 → 300~600s，减少过期→回源→重建频率。
2. **缓存过期加随机抖动**：同一批 key 补随机秒数，避免同时过期造成尖峰。
3. **压测前预热**：脚本按本轮压测班级调一次 `ClazzSyncAclService.listByNumbersFromCache`，把 key 提前铺好。
4. **Pipeline 不用动（已开，且非本问题解药）**：`redis.v1.cache.use.pipeline` 代码默认 `true`、线上未覆盖（arthas 实读 `usePipeline=true`、`pipelineMinBatchSize=1`）。
   它只优化**写**路径（`batchSetCache → executePipelined`）；**读路径本来就是批量 `multiGet`**（`RedisCacheUtilV1.java:169`），而本次热点是**读**(`GetQps ~11.4万/s`) → 开关它不解决读热点，别把它当止血项。
5. **实例侧**：确认规格/加只读从节点分摊读；压测期必要时临时升配。
6. **消费/实例隔离兜底**：压测前把非关键 consumer 降速，减少对同一实例的争抢。

### B. 低风险代码改造（收益最大）

7. **加进程内 L1 本地缓存**：`student-data-client` `RedisCacheUtilV1` 前置 Caffeine/Guava 本地缓存（TTL 5~30s），命中直接返回、Redis 只兜底 → 可将读放大降一个数量级。
8. **逻辑过期（soft TTL）**：缓存值带逻辑过期时间，过期时**返回旧值 + 异步单飞刷新**，避免过期瞬间的 miss 风暴（缓存击穿）。
9. **消费侧批量化/去重**：`DwsSubclazzStudentSyncConsumer` 对一批消息的 `clazzNumber` 先去重合并（含相邻消息），再一次性 MGET，避免同一班级重复读。
10. **回源合并**：miss 回源前先合并去重，并按更大的 `clazz.query.size` 批量调 `course-center /feign/clazz/query/listByNumbers`（它自身也有限流规则）。

### C. 架构（中长期）

11. **缓存实例隔离**：把 student-data 班级缓存从共享 `gaotu-fairy-prod` 迁到独立 Redis，避免与 fairy / reach / crm-app 互相影响。
12. **热 key 治理**：对 `gaotu:studentdata:sync:clazz:v1:*` 加热 key 监控；若长期热点，说明**key 粒度偏细**（可按 course/clazz 维度聚合缓存或分段）。

### 验证（改后怎么算数）

- 实例：同压强下 `CpuUsage`/`GetQps`/`ExpiredKeysPerSecond` 回落对比。
- 应用：`listByKeysCache` 调用速率（arthas monitor）、本地缓存命中率、回源 RPC 量下降。
- 端到端：`course-center /feign/clazz/query/listByNumbers` 的到达 QPS 与 429 减少。

## 涉及系统

- 仓库 / 服务：`student-data`（`student-data-dws` 主力 + 服务）、`student-data-client`（SDK）
- 代码：`ClazzSyncAclService.listByNumbersFromCacheV1`、`RedisCacheUtilV1.listByKeysCache/batchSetCache`、`DwsSubclazzStudentSyncConsumer`
- 配置项：`clazz.data.query.cache.time`、`redis.v1.cache.use.pipeline`、`clazz.query.size`
- 实例：`r-2ze51b484ccb4964`（共享；student-data db15）
- 关联：[`续班保障打限流排查.md`](续班保障打限流排查.md)