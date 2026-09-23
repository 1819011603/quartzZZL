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
| T-06 | 【问卷匹配】product-server 改动（ComputeParams 扩字段/解析前移、3 条 plan 级规则、Apollo 7 档顺序、去兜底） | 已完成 | — | 已部署 `test-gtbg-dev-3`，7 档逻辑反射实测 6 例全过（见 [[verify]]）；无绑定号收敛本批不做 |
| T-07 | 【问卷匹配】重试 Job `dealNotExistedComputeUser` 加「重试次数」标记 | 已完成 | — | `questionnaire_record.retry_count`（TEST DDL 已加）+ `no.compute.user.max.retry.count:3`；未归属记录累加、达阈值不再重试 |
| T-08 | 【问卷匹配】teacher-tool 明细改动 | 已完成 | — | 不加续班计划列；改派不做。改为**新增调课调班消费者**（见 T-09） |
| T-09 | 【问卷匹配】调课调班同步（teacher-tool 承接） | 已完成 | — | 新增 `TransferCourseQuestionnaireConsumer`：原班续班明细复制到新班（同 group、幂等 skip）。**2026-09-23 真发 MQ 端到端已验证**（`gaotu_after_sale_event_test`+`TRANSFER_TOUCH_EVENT` → B 新增明细、重投幂等，见 [[verify]]）。花名册 ES 落值受限未验 |
| T-10 | 【扩科推荐】新增【推荐排除】：product-server 配置 + student-data 计算侧过滤 + cart 推荐适配 | 已完成 | — | 分支 `feature-xuban-expand-exclude`。B/C 端真实入口 E2E 已验证；修掉 cart fastjson SnakeCase 致 Feign 恒空的真 bug（`96e334b8`）。详见 [[verify]]「第二批」 |

| T-11 | 【AI 配置化】部门→模块开关（Apollo，不接 GAIA）：student-data 配置+匹配服务+分析侧（续班5/6、退费5、续班1/2/3圈选实时+历史）+ feign 透出；student-center 展示侧 | 进行中 | **部门口径修正已部署并验证通过**（`12e41da47`/`84ec1b732`，2026-09-23 复核 eureka UP + 门控/续班&**退费分析侧 E2E**/展示侧入口全过，见 [[verify]]「部门口径修正」）；圈选侧门控函数级已验、MQ 圈选消息不可观测；剩 ①退费预测(prediction)未单独验 ②**上线前须配全部门** | 分支 `feature-xuban-expand-exclude`（student-data + student-center，均已 push：`c91d5cd66`/`7b9215766`，口径修正 `12e41da47`/`84ec1b732`）。**口径**：部门 = 老师（二讲）虚拟组织架构主岗路径，按 `_` 分段精确命中；模块 code 续班 `1-8`、退费 `tutoring/learning/satisfaction/refund_root_cause/service_suggestion/prediction`；**未配置=关闭**。配置 key `renewal.ai.dept.module.switch` / `refund.ai.dept.module.switch`；feign `POST /feign/ai/module/switch/query` |

## R- 反讲整改项

| 编号 | 整改项 | 状态 | 谁提的 | 备注 |
|---|---|---|---|---|
| R-01 | 反讲按 `origin/master` 全量核验代码位置（4 组并行 ~90 处），订正 8 处并升 v0.4 | 已完成 | 我 | 见反讲「变更历史 v0.4」 |
| R-02 | 反讲：目标/Non-goals 归位、子需求2 口径统一（无需开发）、问卷匹配 DDL 否→是、移除不存在的 `predictLevelReason`、补《发问卷整体技术方案》7 项现状/风险 | 已完成 | 我 | 同上 |
| R-03 | 新建《待产品确认清单》21 条（按 5 子需求分组，可直接转发产品） | 已完成 | 用户 | https://gaotuedu.feishu.cn/docx/L2yrdOPEAoIOMux1JLXcGtR4nde |
| R-04 | 线上核实 Apollo：`compute.rule.name.list` 是否未配置、共享开关 `all.share.questionnaire.renewal` 实际值 | 已完成 | 我 | appId=`course-setting`（product-server-b/c/task 共用）。PROD/TEST 均**未配置** `compute.rule.name.list`（走代码默认 4 规则顺序，7 档在规则内部实现）、**未配置** `all.share.questionnaire.renewal`（默认 `true`）；`share.questionnaire.renewal.numbers` PROD=`[16091330849213120,15927198832724032]`、TEST=`[]`（仅 all.share=false 时生效） |

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
- T-09 调课调班后 A、B 两班的**问卷明细**已验（真发 MQ → B 复制成功 + 幂等，见 [[verify]]）；**花名册问卷字段（ES 落值）受限未验**（缺真绑定同问卷且有花名册文档的 A/B，机制已定为宽表重建时推导）。
- T-10 选【排除不同授课模式在读】时，大班在读学科不再被小班推荐、反之亦然；【无排除】保持现状；B 端 / C 端 / 选品过滤一致。→ **B 端 / C 端已验（✅ 开/关排除对照通过，见 [[verify]]）；选品 `productSelect` 过滤未单独验，待补。**
