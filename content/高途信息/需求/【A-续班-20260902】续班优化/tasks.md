---
title: 【A-续班-20260902】续班优化 · 任务板
tags: [需求, 任务]
---

# 当前任务板

## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 代码定位：问卷匹配优化 | 已完成 | — | 结论见 README 子需求1 |
| T-02 | 代码定位：主讲数据+下单优化 | 已完成 | — | 结论见 README 子需求2 |
| T-03 | 代码定位：扩科推荐优化 | 已完成 | — | 结论见 README 子需求3 |
| T-04 | 代码定位：数据落表 | 已完成 | — | 结论见 README 子需求4；需数仓侧确认落表方式才能继续 |
| T-05 | 代码定位：AI模块配置化 | 已完成 | — | 结论见 README 子需求5 |
| T-06 | 【问卷匹配】product-server 改动（ComputeParams 扩字段/解析前移、3 条 plan 级规则、Apollo 6 级顺序、去兜底取第一个、无绑定号收敛计划） | 待办 | 归属已确认给我 | 详见 README 子需求1「改动清单」；飞书子页面 https://gaotuedu.feishu.cn/wiki/KR7qwGZdEiGXW4k360NckPnxnnf |
| T-07 | 【问卷匹配】product-server 重试 Job `dealNotExistedComputeUser` 加「终态未匹配/重试次数」标记 | 待办 | 与 T-06 同批，否则被未匹配记录拖垮 | 性能风险见 README 子需求1「性能评估」 |
| T-08 | 【问卷匹配】teacher-tool 改动（是否加 renewal_number 列、补「改派」能力） | 待办 | 续班计划列待评审 | 建议不加列；改派是需求缺口 |
| T-09 | 【问卷匹配】新增调课调班事件消费并确认承接方（product-server 新建 consumer+DAO vs 扩 student-data `DwsAfterSaleSyncConsumer` tag 分支） | 待办 | 待评审 | 调课调班= topic `gaotu_after_sale_event_test`+`TRANSFER_TOUCH_EVENT`（非 `TAG_Subclazz_Transfer`）；明细 A/B fan-out 在 student-data |

## R- 反讲整改项

| 编号 | 整改项 | 谁提的 | 状态 | 备注 |
|---|---|---|---|---|

## C- case 联调问题

| 编号 | 问题 | 对应 case | 状态 | 备注 |
|---|---|---|---|---|

## 阻塞详情

### T-04（数据落表子需求，非阻塞当前任务板项，仅提示后续开发前置条件）
- **卡在**：落表方式未定（MQ推送 or 数仓侧binlog直拉）
- **需要谁**：数仓侧
- **可以先做**：其他4个子需求的评审和设计可并行推进，不受此阻塞
