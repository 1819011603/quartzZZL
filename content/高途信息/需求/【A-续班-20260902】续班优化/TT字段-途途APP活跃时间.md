---
title: 【A-续班-20260902】续班优化 · TT字段（途途APP活跃时间）
tags: [需求, TT字段, 途途]
---

# TT字段：大班线上花名册新增途途APP登录 / 活跃字段

和问卷匹配同批上线（第一批，10/16 前）。**纯配置，代码不改**：student-data / student-center 的 `feature-tutu-active-time` 分支相对 release 没有提交。

- 技术方案：https://gaotuedu.feishu.cn/wiki/Qv9fwuVYzixVz2k7lFhcUtDpnkb
- 上线 CheckList（权威清单，逐项勾）：https://gaotuedu.feishu.cn/wiki/ZEMMwceJMiHpvvkDkoicwysGnWY
- PRD：https://docs.baijia.com/sheet/DQUpCd2pqbFdITEJnUm5GaFVl?tab=3t6gv1

## 字段

| GAIA 字段 | 展示名 | 说明 |
|---|---|---|
| `tutuApp7DaysState` | 7日登录途途app | 枚举 1=PC 2=APP 3=日内未登录 4=未登录，dict `7DaysLogin` |
| `tutuApp15DaysState` | 15日登录途途app | 同上，dict `15DaysLogin` |
| `tutuAppLastActiveDate` | 途途app活跃时间 | long 毫秒，日期区间筛选 |

ES 底层字段：`tutuAppLastActiveDate`（APP）、`tutuPcLastActiveDate`（PC）。

## 已定共识

- **本次做的是途途APP（`tutuApp*`）**；线上已有的 `tutuLexue*` 是高途乐学，不是本次范围。
- **business_id（= pClient）= `2`**：线上交叉验证过。取线上 `businessLine=2` 的登录事件学员去调 CDP，都只有 `tutuAppLastActiveDateTime`；`businessLine=1` 的只有 `gaotuAppLastActiveDateTime`。
- **CDP 源字段**（刘欢给的映射表）：APP 用 `tutuAppLastActiveDateTime`，PC 用 `tutuGwPcLastActiveDateTime`。线上用 student-data 身份调 `getUserDetail` 两个都能拿到（PC 用学员 6788548699 验过）。CDP 里还有一个 `tutuPcLastActiveDateTime`，和 `tutuGwPcLastActiveDateTime` 只差 2 秒，按映射表用 `*GwPc*`。
- **GAIA 展示名**：按 PRD，同上表。
- **学员详情页不在本次范围，也不用改**：线上早已展示途途活跃时间。
  - Apollo `student.detail.userActiveTimes` 已包含 `tutuApp/PcLastActiveDate`。
  - GAIA「线上班级花名册-学员详情页面」已挂 `tutuAppLastActiveDate`。
  - 这个页面走 `UserActiveTimeDataFill` 实时查活跃时间接口，不走 ES。
- **性能**：上线前不改代码，先上配置再观察；详见 CheckList 第六节。
  - 途途登录事件峰值约 1.3 条/秒，约为现有三条线的 2.4 倍。
  - 每人平均约 5.7 条大班花名册文档，按 1 小时折叠后，峰值约 6 次文档更新/秒。
  - 真有压力时再按顺序优化：① 只写大班索引 ② 开 CDP 缓存 ③ 加大折叠窗口。

## 上线配置（TEST 都已配 / PROD 都没配）

| # | 位置 | 配置 | PROD 要做 |
|---|---|---|---|
| 1 | ES `ads_large_clazz_user_*` | 两个 long 字段 | SRE mapping 工单。GAIA 发布时只会自动补 GAIA 里有的字段，`tutuPcLastActiveDate` 补不到，必须手动提 |
| 2 | DB `ees_data.es_query_config` | type=7 nameMapping 6 行（照 TEST id 866–871） | INSERT，SQL 在 CheckList 第三节 |
| 3 | student-data Apollo `cdp.to.es.field.map` | `tutuAppLastActiveDateTime→tutuAppLastActiveDate`、`tutuGwPcLastActiveDateTime→tutuPcLastActiveDate` | 加 |
| 4 | student-data Apollo `user.business.to.es.field.map` | `"2":"tutuAppLastActiveDate"` | 加 |
| 5 | student-center Apollo `active.date.time.config` | `tutuApp7DaysState` / `tutuApp15DaysState` | 加 |
| 6 | student-center Apollo `large.clazz.list.field.names` | 两个状态字段 | 加 |
| 7 | student-center Apollo `large.clazz.array.range.fieldNames` | `tutuAppLastActiveDate` | 加 |
| 8 | GAIA 公共模型/线上花名册页面 | 3 个字段 + 字段集 + 显示设置 | 建。PROD 的 `tutuAppLastActiveDate` 只挂在线索页 / 学员详情，不在花名册页面；照 PROD 的 `tutuLexue7DaysState`（272769378357891072）建 |

漏配后果：
- 漏 #4：登录事件全部被过滤掉。
- 漏 #3：字段不会写进 ES。
- 漏 #2：状态列所有人显示「未登录」，而且不报错。

## 测试环境验证（2026-09-29，177071 / gongxuemeng）

班级 `545361298330824704` + `501340731061899264`，在读 480 人，花名册列表接口 + 页面：

- 展示 ✅：6611409826437 页面显示 APP / APP / 2026-09-28 15:11。
- 状态计算 ✅：
  - 6611409826437（09-28）：7 日 APP，15 日 APP
  - 6611409826449（09-22）：7 日「日内未登录」，15 日 APP
  - 1437282（09-10）：7 日、15 日都是「日内未登录」
  - 其余 477 人：未登录
- 筛选 ✅：
  - 7 日、15 日各状态单选、多选都对。
  - 各状态人数相加 = 480，不漏不重。
  - 活跃时间日期区间筛选对。
- **未验**：
  - PC 状态：测试环境没有任何途途 PC 数据，要验需模拟 CDP 事件补数据。
  - 活跃时间排序。

## 历史数据回溯（已定：按班回溯，测试已验证）

**为什么要回溯**
- 实时链路只在学员登录或 CDP 属性变更时才刷新数据。
- 上线前就不活跃的学员如果不回溯，会一直显示「未登录」、活跃时间为空，「未登录」筛选会把他们也筛进来。

**不受 MQ 只保留 3 天的限制**
- 回溯时直接重新查最新值：用户中心登录记录（近 30 天）+ CDP 最后活跃时间，两者取较新的，和实时链路一致。
- 测试时补出过 2024-07 的数据。

**方案**
- 新建 xjob GLUE 任务（`BackTutuActiveTimeByClazzHandler`），源码在 [[脚本/BackTutuActiveTimeByClazzHandler.java]]。
- 参数是班级号，逗号分隔可以一次跑多个班。
- 只写 `tutuAppLastActiveDate`、`tutuPcLastActiveDate` 两个字段；两个状态字段是读的时候实时算的，不用写。
- 不走速达全量字段（速达会重算 278 个字段，太重）。
- 按「班级号-学员ID」直接写该班文档（`bulkUpsertLargeClazzUser`）。
  - 最初写回走按用户维度发 MQ 的链路（`handleForLargeByDimensionMap`），但有序队列积压时一直写不进 ES，所以改成直接写。

**测试验证**（2026-09-29，jobId 9716，班级 `545361298330824704`，全班 466 人）
- 执行结果 200。有途途活跃时间的学员从 2 人变成 5 人：新补 4999988465（09-22）、4631559173（09-22）、3950102211（2024-07-18）。
- 全班文档数仍是 466，没有多建空文档。
- 花名册接口「15日=APP」「7日=日内未登录」的筛选结果都包含新补的学员，状态计算正确。

**路由用轮询**（测试已验证）
- 连续触发 3 次，分别落到 3 台不同的 pod，每次执行结果都是 200。两个班的数据都对：`545361298330824704` 仍是 466 条文档、5 人有值；`501340731061899264` 仍是 17 条文档、1 人有值。
- 为什么可以用轮询：
  - 一次只跑一小批班，一个班约 20 秒，很快就跑完，不怕跑到一半 pod 被回收。
  - 脚本直接写 ES，不经过 MQ，落到哪个泳道的 pod 都能写进去。
- **分批规则**：每次触发传 20–30 个班，等上一批执行结果 200 后再触发下一批。原因是「单机串行」只对同一台机器生效，轮询下如果不等上一批跑完，多批会在不同 pod 上同时跑，CDP 和 ES 的压力会叠加。
- 线上建任务前，先看执行器在线机器里有没有灰度实例。灰度 pod 上的代码版本不同，跑出来的结果可能不一致。

**踩过的坑**
- 最初写回走 MQ 时，默认路由「第一个」会落到功能泳道的 pod，发出的消息带泳道标记，基线消费者收不到。现在改成直接写 ES，这个问题已经不存在。
- 测试 ES 高负载时，count 查询可能因为统计不全返回偏小的数（实际碰到过 17 条显示成 11 条）。判断数据时以所有分片都成功（`_shards.failed=0`）的结果为准。
- 重放登录事件会让测试 ES 大量超时，有序消费者跟着卡住。

**线上执行前提**
- ES mapping、Apollo（特别是 `cdp.to.es.field.map`、`user.business.to.es.field.map`）都上完。
- 线上 xjob 照这个脚本建 GLUE 任务，按在读大班分批跑。
- 每批多少班、跑多快，等配置上线、确认新数据正常写入后再定。
- 脚本里每 100 人一批，批与批之间停 200ms。

## 当前卡点 / 下一步

- [x] 历史数据要不要回填 → 要，按班回溯，测试已验证（见上节）
- [ ] PROD：ES mapping 工单、GAIA 建字段（写线上，需确认后执行）→ DB → Apollo 5 项（写入后要在后台发布并读回）
- [ ] PROD：建回溯 GLUE 任务，按在读大班分批回溯
- [ ] 上线后盯 1–2 天：延迟消息堆积、`user_login_time` 消费耗时、ES bulk、CDP QPS

## 排障备忘

- 测试环境登录事件：topic `user_app_login_event_test`，挂在 **cn-beijing 的 gaotu 实例**（`MQ_INST_1941505946323830_Bay8En7I`，Apollo 没配 nameAddr，走代码默认值）。
  - 消费组 Apollo 里是 `GID_student_data_sync_user_login_test`，控制台上实际是 `…_test_test`（test 泳道）或 `…_test_test-eco-N`。
  - 测试环境 dws 的业务日志在 **SLS**，TLS 可能查不到。
- 测试环境学员 6611409826437 的登录事件是 `businessLine=18`，不是 2。测试环境靠登录事件可能刷不出途途时间，这不影响线上配 `"2"`。
- 测试环境折叠窗口没配，走默认 600 秒，重放后约 10 分钟才会写 ES。
