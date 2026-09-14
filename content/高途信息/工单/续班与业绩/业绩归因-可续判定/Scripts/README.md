# 业绩归属排查 & 回溯 · 可执行手册

> 本文件原为全局 skill `attribution-judge-debug`，2026-09-14 迁入案例库。
> 同级 `../README.md` 是案例（发生过什么），本文件是方法（怎么做）。
> 触发词：查不到归属人、业绩归属为空、归属人不对、不参与判单、回溯判单、可续分母、`no template matched`。

## 0. 先破除三个常见误判（不做这步会走偏一整轮）

| 现象 | 常见误读 | 真实含义 |
|---|---|---|
| 日志 `should judge but still processing orderNumbers is [...]` | 判定任务卡在处理中 | **不代表卡住**。`PerformanceBaseServiceImpl.handleNotJudgeOrders` 里它只表示"业绩表查不到这单 + **当前**班级 `is_attribution=1`"。配置事后被改开就会稳定产生这个假象 |
| 接口返回 `type="-"` | 未知/异常 | 同一函数：`paid_time` 超 `performance.calculate.limit.hour`(默认 24h) → `"-"`；24h 内 → `"业绩正在计算中"`。只是时间分支 |
| `performance_attribution_credentials` 无该单记录 | 消息没消费到 | **调课单走继承分支不写凭证表**。凭证只在 `buildAttributionCredential`（非调课分支）落库。凭证表有无不能推断消息是否消费 |

结论：**别拿这三个信号当证据，必须去捞全链路日志。**

## 症状路由（先分清是哪一类，再往下走）

| 症状 | 是什么问题 | 去哪 |
|---|---|---|
| 业绩表查不到这单 / 归属人为空 | 判单问题 | 本文第 1~3 节 |
| 判单正常、业绩已落库，但**排行榜/业绩显示 0** | **取数问题，不是判单问题** | `references/ranking-zero.md` |
| 不算可续分母 / 可续锁在别的订单 | 可续标记问题 | `references/can-renewal.md` |
| 已确认 `is_attribution=0`，要查谁改的 / 要回溯补数据 | 配置与回溯 | `references/setting-and-backtrack.md` |
| 对完日志要跳源码 | —— | `references/code-map.md` |

## 1. 定位链路：拿 logger_id 捞全链路（决定性一步）

先按订单号捞，找出消费该单的 handler 的 `logger_id`（日志行里 `- [TID:` 前那个 32 位 hex，**不是** trace_id 字段）：

```
mcp__qingzhou-log__get_sls_log_v2
  serviceName: performance-attribution      # 用 qingzhou_get_service_info 的 appId，不是 -server
  env: prod, logType: app
  keyword: <订单号>
```

订单消息体有好几 KB，一次几十条就会超 token 被落盘。**解析落盘文件时只打印 `timestamp / class / message[:200]`**，别整篇读。

然后按 logger_id 二次精捞（`queryStr` 里字段名不能带裸冒号，值要加引号）：

```
queryStr: "<logger_id>" and ("filterOnlineAttributionCredentials" or "no orders need judge performance"
          or "transfer order" or "generate transfer attribution" or "no attribution configs found")
```

同一笔单会有多条 handler 各自消费（bigclazz / smallClazz / soloClazz / def / productcenter × Created/PaySuccess × bizLine 1 和 2）。**认准 `bizLine` 与订单 `courses[].biz_line` 一致的那条**，其余会打「构造数据为空」属正常。

## 2. 沿判单主干逐个卡点比对

`AbstractPerformanceAttributionJudgeTemplate.judgePerformanceAttribution` 的早退顺序：

1. **`filterAttributionCredentials` 滤空** → 日志 `no orders need judge performance`
   - 线上：`filterOnlineAttributionCredentials` 查 `performance_attribution_setting`，日志 `query is performance, clazzNumberList：[...]` 紧跟 `is performance:{clazzNumber:false}` ← **`false` 就是元凶**（最高频真因）
   - 线下(LOCAL)：查课程 `dataLabelDTOList` 是否含 `performance.attribution.local.is.attribution.id`(默认 114)
2. **待支付凭证不存在** → `no pay credentials does not exist` 后 `return false`（消息会重投）。注意 `isTransfer` / `isChooseGift` / BACKTRACK / COMPLAIN 场景**跳过**此校验
3. **策略链取不到配置** → `no attribution configs found, orderNumber is ...`
4. 调课单进 `generateTransferAttributionResultList`：父单业绩不存在 → `parent performance not exist`；否则按 `judgeSatisfyAllClazzRenewalConfig` 决定 `继承` / `重判`。**每个分支都会 `saveK12TransferOrderJudgeReason`**，所以判单原因表没记录 ⇒ 根本没进这个方法

对完日志要跳源码 → `references/code-map.md`（四条主干 + 两个读码坑）。

## 3. 证据源（prod，DMS cluster_id **259** = gaotu-stats-prod）

> 73 / 332 / 339 是 ETL/ADB/腾讯侧副本，服务实际读写的是 259，别混。

| 表 | 看什么 |
|---|---|
| `gaotu_stat.performance_order_attribution` | 最终业绩。`trade_status`：0待付/1支付/2部分退/3全退/4调出退款 |
| `gaotu_stat.performance_order_attribution_no_pay` | 待支付判单结果 |
| `gaotu_stat.performance_attribution_credentials` | 凭证，`stage` = 判单场景码（1待支付/2支付/3回溯/4申诉/5调课） |
| `gaotu_stat.performance_attribution_judge_reason` | 判单原因，`scene` 同上；字段是 `rule_result`（不是 strategy_judge_reason） |
| `gaotu_stat.performance_attribution_setting` | **判单开关** `is_attribution`，`idx_clazz_number` |
| `gaotu_stat.performance_attribution_setting_log` | **开关变更审计**，`operation_records` = `{"oldIsAttribution":x,"newIsAttribution":y}`。**不存操作人** |
| `course_center.course`（cluster **317**） | `course_type` = 判单规则卡的课程类型；`master_category_id` = 商品类目 |
| `course_center.course_category`（cluster 317） | 类目中文名，靠 `parent_id` 逐级拼全路径 |

**索引红线**：`performance_order_attribution` 没有 `clazz_number` 前导索引，`create_time` 也没索引（只有 `trade_time` 有）。按班级统计必超时 —— 要先从订单侧拿 `order_number` 列表，再 `order_number IN (...)` 反查。可用前导列：`order_number / pre_order_number / top_order_number / refund_order_number / trade_time / user_id / employee_email / pre_employee_id / pre_subclazz_number`。

## 验证

- 定位到真因后，**必须在日志里找到对应的那条早退日志原文**才算证据，光看数据库缺行不算。
- 说「这单不进排行榜」之前，必须做完 `ranking-zero.md` 的 8.5 SQL 对账 + 8.7 打线上接口，两边数字相等才算闭环。
- 回溯跑完验 `sign_x` 的 `update_time` + status；ES `canRenewal` 有 600s Caffeine 缓存，看板约 10 分钟后才变。
- 判单开关由 0 改 1 **不会回补历史订单** —— 改完不等于历史单有业绩，要另跑回溯。

参见 memory：`project-attribution-setting-no-backfill`、`reference-performance-attribution-table-indexes`、`project-can-renewal-debug-and-back-sop`。
