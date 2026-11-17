# 独立复核报告 — 续班预热 V2 测试交付（2026-11-17 晚）

> 应所有者要求，由 3 个只读子 agent + 1 条主 Worker 自查线独立复核。**全程只读**：未改数据、未下单、未动 Apollo、未重跑测试、未改代码。
> 证据文件：`/tmp/w1audit/data-check.md`（数据线）、`/tmp/w1audit/trace-check.md`（trace 线）、`/tmp/w1audit/report-check.md`（文档线）、`/tmp/w1audit/apollo-check.md`（Apollo 线，主 Worker 自查）。

## 一句话结论

**此前回报可信**：核心声称（计划/关联/学员/订单真实落库、trace 真实存在且内容支撑结论、Maven 161 项、Apollo 10 次发布全部闭环）经独立回读**全部核实**；缺口是 3 处文档级瑕疵（「V2 28 项」计数口径未留痕、报告重复章节号、release 标识混用）和 1 处结构性局限（第二层嵌套无法证伪），均不影响已验证结论的有效性。

## 三档汇总表

### 复核通过（附证据）

| # | 声称 | 复核方式 | 证据 |
|---|---|---|---|
| 1 | 5 个计划类型正确（大班主/从 type=1，3 个小班 type=2，全 status=2 isdel=0） | DB 直查 | data-check.md ①，5/5 |
| 2 | 主从关联：大班主挂 [S2, 小班6004]；混合主挂 [小班51, S2]；大班从跨挂两主构成嵌套 | DB 直查 renew_master_relation | data-check.md ②，4/4 精确吻合 |
| 3 | 小班 6004 前置 4 笔订单全 order_status=2 | DB 直查 order_item | data-check.md ③（588506026511294464×2、586084334251927552×2） |
| 4 | 大班前置 6 笔（100 分 mock 支付） | pay_info 直查 | data-check.md ③：15:42 两批次 ×3 人全 pay_status=1；5 人 11-17 合计恰 10 笔支付。注：该 6 笔不在 gaotu.order_item（B 端订单库不同），以 pay 侧佐证，**符合预案非出入** |
| 5 | 小→小补单 pay 434770016363085842、混合补单 pay 434770876430286866 | pay_info 直查 | data-check.md ④，2/2 均 user 7704848531 pay_status=1 |
| 6 | 组合 51 未被任务修改 | DB 直查 product_sku | data-check.md ⑤：sale_status=1、update_time=2026-11-10 16:54:01 未变 |
| 7 | 14 个本地响应/日志文件内容与 TraceID 全部一致 | 逐一 cat/解析 | trace-check.md：13/14 通过，含 loop 6 条 SKU 全唯一、mvn15.log 实测 `Tests run: 161, Failures: 0` |
| 8 | 5 个关键 trace 在日志系统真实存在且为 cart 调用链 | get_log_v2（test sls+tls 双查） | trace-check.md：`.289.17949067348720087`（17:12，查 51 前置 SPU 与响应逐字段吻合）、`.283.17949122103700167`、`.291.17949124627200177` 均实锤 |
| 9 | **P1 修复正反证据链完整** | tls 日志原文 | trace-check.md：命中 trace 实锤 `SmallRenewalPreheatCacheService:93 'small preheat cache hit key=renewal:preheat:586116340522184704:7746791494'`（镜像 e6199773），未命中 trace 无 hit 日志、时序吻合 |
| 10 | Apollo 10 次发布闭环、终态 false | release_history.py（openapi 只读） | apollo-check.md：releaseId 437360→437623 与报告 §2.2/§6 逐一对应，末次 diff true→false |
| 11 | fixture 44 行（43 数据行 ≥ 39+），五类别 + 5 学员全在 | 文件直读 | report-check.md ① |
| 12 | 订单笔数、场景编号 1..43 连续无重复 | 程序化验证 | report-check.md ② |
| 13 | 51 结论四处（checkpoint/round13/台账/报告）同口径，旧表述仅存台账划线段 | 全文比对 | report-check.md ④ |
| 14 | 60 个 trace 引用跨文件交叉零冲突 | 脚本抽取 | report-check.md ⑤ |
| 15 | 两仓库 HEAD/干净状态与声称一致 | git log/status 实读 | report-check.md（cart `5f0df948`、quartzZZL `9b917c19`） |

### 有出入（说明差异与影响）

| # | 差异 | 影响 | 定性 |
|---|---|---|---|
| 1 | **「V2 28 项」计数口径未留痕**：17:35-17:40 窗口本地实有 16 个 v2 响应文件（内容全部真实）；「28」= 本轮 16 项 + 早前窗口 5 个 v2_*.json + 预热/异常等子项的合计，但台账/报告未写明这个加法 | 数字本身可解释且内容真实，**非虚报**；但统计口径未留痕，复核时无法直接对账 | 口径瑕疵 |
| 2 | **报告重复章节号**：存在两个 §4.3（L133/L214）、两个 §4.4（L158/L209）——追加小节时旧段未重编号 | 交叉引用歧义，不影响内容正确性 | 文档瑕疵 |
| 3 | **release 标识 1 秒差混用**：§4.3-4.5 及台账引 releaseKey（…182828/184317/184848），§2.2/§6 用 release 名（…182827/184316/184847），同一发布两种 id 差 1 秒 | 对照时易误认为两次发布；实际为同一次（releaseTitle 与 releaseKey 的生成秒差），Apollo 线已按 diff 内容对齐确认 | 文档瑕疵 |

### 无证据（如实列出）

| # | 项 | 说明 |
|---|---|---|
| 1 | 第二层嵌套关联是否被 V2 递归展开 | 第二层从计划学员均无前置单，即使展开也无纯续可出，**现有数据无法证伪**（已在报告 §4.5 如实标注验证边界） |
| 2 | Apollo TEST 其余 7 个实例的运行时开关 | 全程只直连核 1 个实例（test-eco-8），与报告声明一致，未扩大 |

## 附注（非虚报，如实记录）

- 当天 15:0x-15:4x（本 worker 接手前）同账号 zhangzeling 还有 6 次相关发布（单 recommend 开关 + timeout 0→10），不在本任务「10 次发布」声称范围，报告也未声称「当天仅 10 次」。
- 大班前置 6 笔订单在 gaotu.order_item 无记录属 B 端订单库结构所致，pay_info 全额佐证；此前台账已注明「B 端订单不在 gaotu.order_item」，口径一致。

## 复核方式与边界

- 数据线：mysql_query 只读 SELECT（TEST cluster 142 / gaotu）。
- trace 线：本地文件解析 + get_log_v2（test，sls 与 tls 双 backend，cart 自身日志在 tls）。
- 文档线：归档文件全文比对 + 脚本化 trace 交叉与编号连续性验证 + git 只读。
- Apollo 线：release_history.py（openapi historiesPage，只读）。
- 未做任何写操作；发现的出入均未修复，待所有者决定。
