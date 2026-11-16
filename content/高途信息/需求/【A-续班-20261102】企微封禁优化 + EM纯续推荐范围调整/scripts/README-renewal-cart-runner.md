# 续班 C 端推荐接口压测/回归脚本（renewal_cart_runner.py）

- 入库时间：2026-11-16；来源：`/Users/gaotu/Downloads/renewal_cart_runner.py`（原件不动，本目录为入库副本，已做低风险适配改动，见下）
- 适用代码版本：cart `feature-renewal-preheat-v2-20261112` @ `38d2d741`（待上线）
- 用途：对 C 端续班推荐接口 `GET /web/renewal/cart` 做压测与功能回归巡检（成功率/RT 分位/role 分布/失败明细）

## 1. 接口与调用方式

- 接口：`GET /web/renewal/cart?appointUserId=<userId>&renewalNumber=<主计划号>`（`RenewalController @GetMapping("/cart")`）
- 免登录：appointUserId 直接生效依赖 Apollo `renewal.cart.debug.appoint-user.enabled=true`（cart.gaotu100.com / TEST / application，TEST 已开；PROD 默认关）
- TEST 调用通道（按场景选）：
  | 场景 | 通道 | 说明 |
  |---|---|---|
  | 压测（推荐） | pod 直连 `http://{podIP}:28688/web/renewal/cart`，头 `traffic-env: <泳道>` + `host: cart.gaotu100.com` | 绕网关，pod 从青舟/Eureka 按 cart.gaotu100.com 实例取 |
  | 单发预热/调试 | acl 桥 `POST http://{pod}:28688/test/acl/compare/service` | 桥是调试通道，**不适合高并发压测** |
- 三 Apollo 开关（cart.gaotu100.com / TEST / application）：
  - `renewal.recommend.v2.enabled`：C/B 详情走 V2（true）或老链路（false=回退态，老链路 C 端 `!fromBCart` 读老 key `renewal:preheat:{plan}:{user}`，TTL 26h）
  - `renewal.preheat.v2.enabled`：预热走 V2
  - `renewal.preheat.v2.prefix.enabled`：true 写 `renewal:preheat:v2:` 前缀（仅测试隔离）；**false 写老 key**（对比实验必须 false，否则回退态读不到）

## 2. 数据来源与准备（重要）

- `cart_yure.txt`（Downloads）是**线上**用户/计划数据（TAB 两列 userId/renewalNumber，14.2 万行、9 个线上计划），**TEST 调不通，勿直接使用**（owner 已确认）。
- 本目录附带 `cart_test_fixture.txt`（TAB 两列，来自 fixture registry 已登记数据）：
  | 主计划 | 从计划 | 用户 |
  |---|---|---|
  | 590563861447557120 | 590563948968001536 | 7704848531（两单已 mock 支付） |
  | 589037361072007168（1 主 4 从，存量） | 589037362856683520 等 4 个 | 7704848531 / 7704848533 / 7704850492 / 7704850493 / 7704850494 / 7714163148 |
- 数据量不够压测规模时按需补造：造数项目能力（plan_relation 关联 / batch_create_order + mock_pay 下单 / create_renewal_regression_clazz 正经班 / process_edit 流程节点）已验证可用，参考归档 `artifacts/20261115-fresh-seed-role2-verify.md`。
- 新数据文件格式：首行表头 `userId<TAB>renewalNumber`，之后每行一个样本；勿用 Excel 另存（ID 会变科学计数法，脚本会拦截）。

## 3. 运行命令

```bash
cd scripts/
# 前置：pip install requests；pod IP 从青舟（cart.gaotu100.com 实例）取
# TEST pod 直连（推荐；自动拼 http://{pod}:28688/web/renewal/cart + traffic-env/host 头）
python3 renewal_cart_runner.py --pod 10.x.x.x --traffic-env test-eco-8
# 限量/限时压测
python3 renewal_cart_runner.py --pod 10.x.x.x --traffic-env test-eco-8 --threads 10 --limit 1000
python3 renewal_cart_runner.py --pod 10.x.x.x --traffic-env test-eco-8 --threads 5 --duration 60 --rps 50
# 自定义入口/数据（--url 模式不带 host 头；traffic-env 头默认带上）
python3 renewal_cart_runner.py --url 'http://host:28688/web/renewal/cart' --file my_data.txt
# 回归卡点：有失败退出码 1
python3 renewal_cart_runner.py --pod 10.x.x.x --fail-on-error
```

产出：终端汇总（成功率/QPS/avg·p50·p90·p95·p99·max/异常分类/status 分布/renewalRole 分布/按计划成功率/最慢 TOP5）+ `failures_*.csv` + `summary_*.json`。

## 4. 判定标准（回归口径）

- 全部样本 HTTP 200、`status=0` 且 `code=0`、`data.gradeClazzList` 结构完整；`groups=0`（空购物车）计成功属业务合法。
- renewalRole 分布（脚本已统计，暂不断言）：
  - 回退态（recommend.v2=false）+ 预热过老 key 的样本：应出现 `role=1`（主纯续）与 `role=2`（从纯续）条目；`null` 为老条目/实时扩科加购，属预期。
  - V2 实时（recommend.v2=true）有关联计划：主从纯续条目均应出现（role 1/2），null 条目=扩科/加购。
- RT：上线前以同数据固定并发跑一轮基线存档 `summary_*.json`，回归时对比 p99 偏移（阈值自定，建议 >50% 关注）。

## 5. 评审结论（入库副本已做的低风险改动）

| # | 改动 | 原因 |
|---|---|---|
| 1 | 删除默认线上网关 URL（`https://api.gaotu.cn/...`），必须 `--pod` 或 `--url` 二选一 | 原默认指向**线上**；数据文件是线上 ID，TEST 打线上=误打生产 |
| 2 | 新增 `--pod <IP>` + `--traffic-env <泳道>`：自动拼 `http://{pod}:28688/web/renewal/cart` 并带 `traffic-env`/`host: cart.gaotu100.com` 头 | TEST pod 直连必需（方法 GET 与实现 `@GetMapping("/cart")` 一致，网关前缀 `/cart` 在直连时要去掉） |
| 3 | `--file` 默认改为 `cart_test_fixture.txt`（TEST fixture） | `cart_press.txt` 不存在且线上数据调不通 |
| 4 | 新增 renewalRole 分布统计（1/2/null 计数进汇总与 summary JSON，不断言） | 回归核心口径：主/从纯续条目是否产出 |
| 5 | docstring/报错信息更新（用法、头、数据约束、Excel 科学计数法拦截保留） | 口径对齐当前实现 |

建议项（未改，结构性）：
- 可选 `--assert-role`：按 fixture 预期断言 `role=1≥1 且 role=2≥1`（当前只统计）。
- 每秒 TPS 时间序列与错误率曲线（当前只有总 QPS/分位）。
- 多 pod 轮询（`--pod ip1,ip2`）：避免单 pod 热点；单 pod 并发上限与多 pod 收益**未实测**，压测时建议从低并发（5-10 线程）逐步加压观察错误率。
- `--timeout` 默认 30s 偏宽松，压测可显式 `--timeout 10`。

## 6. 实时 vs 预热对比逻辑：脚本当前没有，步骤级补法

脚本现只做单接口断言，无「V2 实时结果 vs 预热缓存读取结果」对比。人工/半自动流程（同一 `(user, plan)`，如 7704848531 + 590563861447557120）：

1. **预热写老 key**：Apollo 设 `preheat.v2.enabled=true`、`prefix.enabled=false`、发布；acl 桥 `POST http://{pod}:28688/test/acl/compare/service`，body：
   ```json
   {"serviceNameAndMethodName":"com.gaotu.renewal.RenewalV2Service#preheatByRenewalNumber","params":["590563861447557120"]}
   ```
   （大数一律传**字符串**防精度截断；单用户用 `#preheat("7704848531","590563861447557120")`）
2. **回退态读缓存**：Apollo 设 `recommend.v2.enabled=false` → 等发布生效 → `GET /web/renewal/cart?appointUserId=7704848531&renewalNumber=590563861447557120` → 存 `R_cache`（此响应来自老 key `renewal:preheat:{plan}:{user}`）
3. **V2 实时**：Apollo 设 `recommend.v2.enabled=true` → 同参数再调 → 存 `R_realtime`（V2 强制跳过预热读、全量实时计算）
4. **diff**：从两个响应的 `gradeClazzList[].clazzDetailDTOList[]` 抽条目（键 `productSkuNumber`）：
   - 纯续子集等价性：`R_realtime` 中 `renewalRole∈{1,2}` 条目集合 vs `R_cache` 中 `renewalRole∈{1,2}` 条目集合 → 输出「只在实时有 / 只在缓存有」差异清单
   - role 分布对比：两边 1/2 计数应一致
   - 口径注意：V2 实时=主计划完整体验（纯续+扩科+加购）+从计划合并，缓存=纯续合并，**整体集合不等价是预期**，只对比纯续子集；null 条目只统计数量
5. **恢复开关并回读确认**（对比期间 `prefix=false` 占老 key 是必要代价，跑完恢复原值）

判定：纯续子集无差异 + role 分布一致 → 预热与实时等价；有差异 → 按 `productSkuNumber` 差异清单排查（优先查主从去重/51 组合条目判空跳过逻辑）。

## 7. 已验证 / 未验证

- 已验证（本地）：语法编译通过；无参正确拦截；`--pod` 模式 URL/参数/头拼接正确（`http://127.0.0.1:28688/web/renewal/cart?appointUserId=...&renewalNumber=...`）；fixture 7 行加载；失败分类/CSV/summary JSON 产出；role_dist 字段就位（空跑对 127.0.0.1，未到真实服务端）。
- 未验证：对真实 TEST pod 的端到端跑批（待下次回归在 TEST 执行一次并回填基线 summary）；role 分布真实数值需预热/开关就位后才非零。

## 7. 端到端验证记录（2026-11-16）

- 环境：TEST test-eco-8，pod 直连 10.218.238.179:28688（cart @38d2d741），开关全默认（回退态老链路）
- 命令：`python3 renewal_cart_runner.py --pod 10.218.238.179 --traffic-env test-eco-8 --threads 3 --limit 7`
- 结果：**7/7 成功**（其中业务空 3 = 纯从计划学员无推荐结果，已归类 success_empty 不计失败）；
  role 分布 role=1×1 / role=2×1 / null×9（含老缓存条目）；QPS 3.4（3 线程冷启动，仅功能性验证非压测结论）
- 首轮发现的归类问题已修：code=0 且 data 无 gradeClazzList 从 data_missing 改为 success_empty（业务空）
- 未做：高并发压测（单 pod 承载上限未实测，建议 5-10 线程起步观察）；实时 vs 预热对比按第 4 节步骤执行
