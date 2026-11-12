# 老/新泳道元数据对比 + Redis 实读验证（2026-11-12）

## 1. 环境与版本

| 角色 | 泳道 | Pod / IP | 分支 / 提交 | 镜像 / 说明 |
|---|---|---|---|---|
| 老泳道（老代码/老 key） | `test-eco-9`（部署前空闲） | `cart-gaotu100-com-76966c7fb4-g7gn7` / `10.218.249.60` | `feature-renewal-rollback-clazzset-dedup-20261112` / `1f5a9118` | 与生产基线同树；pipeline `1341089`，eureka UP |
| 新泳道（V2/新 key） | `test-eco-8` | `cart-gaotu100-com-8484ddcc54-25z8q` / `10.218.251.55` | `feature-renewal-preheat-v2-20261112` / 修复前 `76a0e7d6`，修复后 `f70ebd93` | pipeline `1341155`（f70ebd93） |

- Redis：`r-2zeb585b59575984.redis.rds.aliyuncs.com:6379`，库 0；本机 IP 不在白名单，故在 cart Pod 内用 `/dev/tcp` + RESP 命令行读取（AUTH → GET/STRLEN/TTL）。
- Apollo（TEST）：`renewal.preheat.v2.prefix.enabled=true`；`renewal.recommend.v2.enabled=false`；`renewal.preheat.v2.enabled=false`。

## 2. Redis 原始读取证据（修复前，`76a0e7d6`）

### 2.1 大→小：计划 `585960797778243584` / 用户 `7658127801`

老 key（v1，StringRedisTemplate 写入，原始 JSON）：

```
TTL renewal:preheat:585960797778243584:7658127801  -> 93588
STRLEN                                             -> 155
GET renewal:preheat:585960797778243584:7658127801
{585960577856301056:{"clazz_number":585960755422160896,"product_sku_number":585960755422160896,"product_type":2,"select":0,"sign_up":0,"subject_names":[]}}
```

V2 key（v2，修复前用 GenericJackson2JsonRedisSerializer，值被二次编码为 JSON 字符串）：

```
TTL renewal:preheat:v2:585960797778243584:7658127801 -> 93570
STRLEN                                              -> 741
GET renewal:preheat:v2:585960797778243584:7658127801
"{585960577856301056:{...} ,18314034380997173:{...}}"
```

**发现**：修复前 v2 value 是带引号的 JSON 字符串（`"{...}"`），老代码 `JSON.parseObject(...)` 无法按 `Map` 解析；根因是 `RenewalV2Service` 注入了 `RedisTemplate`（`GenericJackson2JsonRedisSerializer`），而老链路实际注入的是 `StringRedisTemplate`（`StringRedisSerializer`，实测 arthas 见下）。

```
RenewalService.redisTemplate  -> StringRedisTemplate / StringRedisSerializer
RenewalV2Service.redisTemplate-> RedisTemplate / GenericJackson2JsonRedisSerializer
```

### 2.2 修复（提交 `f70ebd93`）

`RenewalV2Service` 改为注入 `StringRedisTemplate` 并在 `writePreheat` 写入，保证 value 为原始 JSON 文本；单测 6/6 通过。部署 test-eco-8 后复读见 §5。

## 3. 老泳道 vs 新泳道对比（同计划/同用户）

| 场景 | 计划 / 用户 | 老泳道（1f5a9118） | 新泳道（V2） | 差异 |
|---|---|---|---|---|
| 大→小 | `585960797778243584` / `7658127801` | v1 1 条（仅主计划 `585960577856301056`→`585960755422160896`，productType=2） | v2 2 条（主 + 从 `18314034380997173`→`586090628920764416`，productType=6004） | V2 增加从计划纯续条目，字段结构同老格式 |
| 小→大 | `589721954597011456` / `7704848531` | 老链路小班主计划不走 `RenewalService#preheat` 写 v1（返回空 map），v1 key 不存在（TTL=-2） | v2 5 条（主 51 + 4 个从计划 2） | V2 写 v2 key；老链路小班预热不写该 key |
| 不关联 | `588872241920421888` / `7658129872` | v1 1 条（`588861400563212288`，productType=2），STRLEN=155 | v2 1 条，同一条目，STRLEN=169（修复前含外层引号） | 条目一致；修复前仅序列化外层引号差异 |

### 3.1 「新链路不改老 key」验证

1. 老泳道写 v1 后：`TTL=93588`，`STRLEN=155`。
2. 新泳道 V2 预热同一计划/用户后：`TTL=93544`（仅自然递减 44s，未重置），`STRLEN=155`，value 原文不变。
3. 结论：**V2 只写 v2 key，不读写老 key，老 key 内容/行为未受影响。**

### 3.2 单计划多学员（xjob 口径）

- 代码判断：`RenewalV2JobHandler` 已支持入参 `["planNumber"]`；未传参时取全量计划。`RenewalV2Service#preheatByRenewalNumber` 内部按 A 计划 `courseNumbers` 取全部已付用户，逐用户算「A+有效从」纯续并写 key——与老 `RenewalJobHandler → RenewalService#preheatByRenewalNumber` 的「单计划多学员」结构一致。
- 结论：**无需改代码，也不需要用 xjob Java glue**；新 job 本身即承接该场景。测试数据计划（`is_test_data=1`）遇 job 跳过逻辑与老 job 完全一致。
- 实测（绕过 job 的测试数据跳过，直接调同一 service 方法，等价 job 内循环）：
  - V2：`RenewalV2Service#preheatByRenewalNumber(585960797778243584)`，trace `cart_gaotu100_com.296.17944662672260099`；日志同时写出
    `renewal:preheat:v2:585960797778243584:7658127801, entries=2` 与
    `renewal:preheat:v2:585960797778243584:7658129872, entries=2`；`renewal-v2 preheat plan done`。
  - 老：`RenewalService#preheatByRenewalNumber(585960797778243584)`，trace `cart_gaotu100_com.325.17944662883450007`；两个用户 v1 key 均 STRLEN=155（各 1 条）。

## 4. 老/新泳道隔离注意（测试环境已发现并恢复）

- 默认 test 泳道 Pod（`10.255.181.48`）镜像为 `release-af82f18a-20261111114554`，实测 `RenewalService#preheat` 返回 2 条并在老 key 写入 `@mergedRenewal@{...}`（错误 master 逻辑）。
- 本轮误触发一次后，已用 `test-eco-9` 基线老泳道重新写入老 key，恢复为 1 条原始 JSON（TTL≈26h，无前缀）。
- 结论：老/新对比必须使用 **test-eco-9 基线** 作为老泳道；默认 test 泳道（af82f18a）不能作为老基线。

## 5. 修复后复读（f70ebd93 已部署 test-eco-8）

- 新 Pod `cart-gaotu100-com-6b9c8bbbfc-9rbfx` / `10.218.249.248`，commit `f70ebd93`，eureka UP；pipeline `1341155`。
- 复读结果（Pod 内 RESP）：

```
STRLEN renewal:preheat:v2:585960797778243584:7658127801 -> 679
GET    renewal:preheat:v2:585960797778243584:7658127801
{585960577856301056:{"clazz_number":585960755422160896,...,"product_type":2,...},18314034380997173:{...,"product_type":6004,...}}
（原始 JSON，首字符 {，无外层引号，2 条）

STRLEN renewal:preheat:v2:586116340522184704:7658127801 -> 679（2 条，小→大）
STRLEN renewal:preheat:v2:589721954597011456:7704848531 -> 1045（5 条，小→大）
STRLEN renewal:preheat:v2:588872241920421888:7658129872 -> 155（1 条）
```

- 不关联场景 v2 为 155 字节，与同场景 v1 155 字节逐字节同构。
- 老 key 回读：修复后 V2 再预热同计划/用户，老 key `TTL=92579`（较上次 93544 仅自然递减）、`STRLEN=155`，原文未变，未被 V2 改写。
- 单测 `RenewalV2ServiceTest` 6/6 通过。
- 结论：v2 value 已与老格式一致；V2 只写 v2 key，老功能不受影响。

## 6. 测试数据保留现状（按 owner「数据不清理」）

- `renew_master_relation`：
  - id=1 `585960797778243584 → 586116340522184704` `is_del=0`（大→小）
  - id=14 `586116340522184704 → 585960797778243584` `is_del=0`（小→大，构造数据已保留并已推进 product 关系缓存版本 `w1-v-20261112-keep`）
- fixture 计划：`590093251235790848`（W1对等数据-小班主）、`590093266702286848`（W1对等数据-大班从）均恢复 `isdel=0`，`renew_master_ext` 19 行、`renew_master_course_relation` 1 行均 `isdel=0`。
- Redis 构造数据保留：
  - `renewal:preheat:v2:585960797778243584:7658127801`（2 条）
  - `renewal:preheat:v2:585960797778243584:7658129872`（2 条）
  - `renewal:preheat:v2:586116340522184704:7658127801`（2 条，小→大）
  - `renewal:preheat:v2:588872241920421888:7658129872`（1 条，不关联）
  - 老 key 对应 1 条版本保留（`renewal:preheat:...`）
- 老泳道 `test-eco-9` 保留运行（1 Pod，1f5a9118），便于后续复查；新泳道 `test-eco-8` 保留。

## 7. 飞书交付物（正确链接）

- **飞书电子表格（推荐）**：https://gaotuedu.feishu.cn/sheets/F761sKKgnhMmxptFFH7cE03HnTo
  - 6 个子表：三场景对照、F1/F2/F4、value格式对照、Redis实读、单计划多学员、数据保留现状。
  - 链接权限：`tenant_readable`（组织内获得链接的人可阅读），已回读确认。
- 飞书文档（补充说明）：https://gaotuedu.feishu.cn/docx/GFGVd3nd5oOxubx4GjDcEY3rnGb
  - 原先是 docx（文档）不是电子表格；已同步把链接权限从 `closed` 改为 `tenant_readable`。
