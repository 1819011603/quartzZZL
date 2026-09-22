---
title: 【A-续班-20260902】续班优化 · 任务板
tags: [需求, 任务]
---

# 当前任务板

## 排期（2026-09-22 更新 · 王永诗按业务节点分两批）

| 批次 | 内容 | 节点 |
|---|---|---|
| 第一批 | 问卷匹配优化（product-server + teacher-tool）、小班主讲数据（**无需开发**）、TT字段（独立需求） | 10/16 前 |
| 第二批 | 扩科【推荐排除】、下单优化（**先不做，后续做**） | 10 月底 |
| 无业务节点 | AI 模块配置化 | — |

原「一起上线」排期作废，以上表为准。TT字段（途途APP）属独立需求，不在本目录跟踪。

## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 代码定位：问卷匹配优化 | 已完成 | — | 结论见 README 子需求1 |
| T-02 | 代码定位：主讲数据+下单优化 | 已完成 | — | 结论见 README 子需求2 |
| T-03 | 代码定位：扩科推荐优化 | 已完成 | — | 结论见 README 子需求3 |
| T-04 | 代码定位：数据落表 | 已完成 | — | 结论见 README 子需求4；需数仓侧确认落表方式才能继续 |
| T-05 | 代码定位：AI模块配置化 | 已完成 | — | 结论见 README 子需求5 |
| T-06 | 【问卷匹配】product-server 改动（ComputeParams 扩字段/解析前移、3 条 plan 级规则、Apollo 7 档顺序、去兜底取第一个） | 已完成 | — | 已编译 + 部署 `test-gtbg-dev-3`；**7 档逻辑反射实测 6 例全过**（见 [[verify]]）；无绑定号收敛计划**本批不做**（口径未定，用户 2026-09-22 定） |
| T-07 | 【问卷匹配】重试 Job `dealNotExistedComputeUser` 加「重试次数」标记 | 已完成 | — | `questionnaire_record.retry_count`（TEST DDL 已加）+ `no.compute.user.max.retry.count:3`；未归属记录累加、达阈值不再重试 |
| T-08 | 【问卷匹配】teacher-tool 明细改动 | 已完成 | — | 不加续班计划列；改派不做。改为**新增调课调班消费者**（见 T-09） |
| T-09 | 【问卷匹配】调课调班同步（**已定 teacher-tool 承接**，非 student-data） | 已完成 | — | 新增 `TransferCourseQuestionnaireConsumer`：原班续班明细复制到新班（同 group、幂等 skip）。反射实测 4 例全过（见 [[verify]]）。ES 靠宽表重建，顺序风险待验 |
| T-10 | 【扩科推荐】新增【推荐排除】：product-server 配置（`ExpandSubjectConfigDTO`/`NodeExtConfigVO` + B 端 `process/edit`·`process/list`）+ student-data 计算侧过滤（大班/小班 subtract）+ cart 推荐/选品适配 + 「授课模式/上课形式线上/订单未全部退款」3 个新建条件 | 进行中 | 端到端未验 | 分支 `feature-xuban-expand-exclude`（product-server/student-data/cart，已提交已部署 `test-gtbg-dev-3`）；配置 + 透出接口 + cart 过滤已实现并编译。**坑**：cart 是 Boot1.5/Netflix feign，不能依赖 student-data-client（带 Boot2.x/openfeign 类）→ 改用本地 DTO+Netflix feign；「订单未全部退款/线上」按用户确认为老逻辑、不再补；client 已发 Nexus 1.5.9-SNAPSHOT / 0.0.52.5-SNAPSHOT |

## R- 反讲整改项

| 编号 | 整改项 | 状态 | 谁提的 | 备注 |
|---|---|---|---|---|
| R-01 | 反讲按 `origin/master` 全量核验代码位置（4 组并行 ~90 处），订正 8 处并升 v0.4 | 已完成 | 我 | 见反讲「变更历史 v0.4」 |
| R-02 | 反讲：目标/Non-goals 归位、子需求2 口径统一（无需开发）、问卷匹配 DDL 否→是、移除不存在的 `predictLevelReason`、补《发问卷整体技术方案》7 项现状/风险 | 已完成 | 我 | 同上 |
| R-03 | 新建《待产品确认清单》21 条（按 5 子需求分组，可直接转发产品） | 已完成 | 用户 | https://gaotuedu.feishu.cn/docx/L2yrdOPEAoIOMux1JLXcGtR4nde |
| R-04 | 线上核实 Apollo：`compute.rule.name.list` 是否未配置、共享开关 `all.share.questionnaire.renewal` 实际值（本机 PROD Apollo 不可达） | 待办 | 我 | 反讲待确认 20 |

## C- case 联调问题

| 编号 | 问题 | 对应 case | 状态 | 备注 |
|---|---|---|---|---|

## 阻塞详情

### T-04（数据落表子需求，非阻塞当前任务板项，仅提示后续开发前置条件）
- **卡在**：落表方式未定（MQ推送 or 数仓侧binlog直拉）
- **需要谁**：数仓侧
- **可以先做**：其他4个子需求的评审和设计可并行推进，不受此阻塞

## 完成判据

> 每个未闭环任务「怎样才算完成」的可检查判据；完成一项删一行，全部闭环后本节为空。

- T-06 7 档规则生效：手机号 / 姓名 / 亲属号 × 同班 / 同计划 组合用例匹配正确；多命中取学员 ID 小的；无绑定号路径收敛到本计划；不再有"取第一个"兜底。
- T-07 `computedUserId=0` 记录不再每轮重复重跑（有终态未匹配 / 重试次数标记），重试 Job 负载不高于改造前。
- T-08 按评审结论：不加列则无 DDL；若加「改派」，跨班改后同 `questionnaire_group_id` 的其余行同步更新。
- T-09 调课调班后 A、B 两班（绑定同一问卷）的花名册问卷字段与问卷明细都正确。
- T-10 选【排除不同授课模式在读】时，大班在读学科不再被小班推荐、反之亦然；【无排除】保持现状；B 端 / C 端 / 选品过滤一致。
