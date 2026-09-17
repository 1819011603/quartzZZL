---
title: 续班&退费AI模块配置化
aliases: []
status: 需求评审
owner: zhangzeling
branches:
updated: 2026-09-17
tags: [需求]
---

# 续班&退费AI模块配置化

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 当前任务板]] · [[changelog|📜 决策摘要]]
> 技术方案在飞书反讲文档里（见 [[links]]），本地不留副本。
> 续接这个需求：读完本文件即可。

## 一句话

续班AI、退费AI 按部门配置各功能模块是否启用，未配置的模块二讲不可用、AI不分析，降低成本。

## 需求摘要

- **要解决的问题**：续班AI上线后部分功能模块使用率不高，对二讲帮助有限，但仍在跑AI分析产生成本。
- **给谁用**：二讲/老师（前端可见性），运营（配置方）。
- **核心改动**：
  1. 按部门配置续班AI、退费AI的各功能模块开关。
  2. 部门配置了某模块：二讲可用，AI继续分析该模块。
  3. 部门未配置：二讲不可用，AI不分析（省成本，这是核心目标）。
  4. 续班AI模块清单：续班用户画像、意向预测、沟通概况、已续/未续跟进、沟通建议&评分、服务建议&评分、用户反馈、主管点评。
  5. 退费AI模块清单：退费分析、意向预测、手填退费原因、AI预测退费原因、课程体验、退费沟通旅程。
- **判定做完的标准**：待反讲后补充。
- **明确不做**：待细评确认。

## 已定共识

- 未配置的模块要同时做到两件事：前端不可用 + AI 不分析（不是只隐藏前端，成本要真的降下来）（2026-09-05 PRD）。
- 续班AI、退费AI 各自的模块清单已在PRD中列出，共14个模块（2026-09-05 PRD）。

## 现在什么情况

| | |
|---|---|
| 阶段 | 需求评审 |
| 进度 | T 1/1 · R 0/0 · C 0/0 |
| 部署泳道 | 未部署 |
| 当前卡点 | 无 |
| 最近更新 | 2026-09-17：收到 PRD，代码定位进行中 |

## 下一步

1. 参与初评，确认设计草案（新建按部门的模块开关Map配置，仿照 `RenewalAiCommSceneConfigService` 的Apollo模式）。
2. 明确"部门"具体取哪个字段（结论：主数据部门/教学部门 code，见下方设计草案）。
3. 产出反讲文档，14个模块逐一列出开关生效点（student-data分析侧+student-center展示侧各自要判断）。

## 待确认

- [ ] 配置粒度：一个部门只能整体开/关某模块，还是能进一步细分到年级/学科 —— 等细评
- [ ] 关闭模块后，历史已生成的分析数据是否要隐藏还是保留可查 —— 等细评

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| student-data | 待定 | 续班AI：`app/service/syncdata/ai/renewal/`（`RenewalAiCommSceneConfigService`圈选配置，`RenewalReasonQueryService`/`RenewalReasonTaskService`归因）、`domain/renewal/reasoning/impl/`（`RenewalUnrenewedReasonServiceImpl`/`RenewalRenewedReasonServiceImpl`）、`AiAppSceneEnum`（场景枚举）；退费AI：`domain/refundless/`（`reasoning/RefundReasonServiceImpl`、`predict/RefundPredictionService`、`reasoning/impl/RefundExperienceServiceImpl`、`RefundUserNpsServiceImpl`）、`facade/job/refundless/RefundAnalysisHandler`（XXL-Job定时触发） |
| student-center | 待定 | 续班AI展示：`web/api/ai/RenewalClazzUserController`、`RenewalReasonController`、`UserFeedbackController`、`domain/service/ai/AiClazzUserPortraitServiceImpl`等，落表 `ai_app_clazz_user_*`；退费AI展示：`web/api/RefundController`、`AiRefundAnalysisController`、`domain/service/AiRefundAnalysisService`；**可参考的部门级配置模式**：`RenewalAiCommSceneConfigService`（两仓库各有一份）用 `@ApolloJsonValue` 的 `Map<部门code, 配置对象>` 做圈选阶段差异化配置；`UnificationSwitchService` 是总开关+模块开关两级设计参考（但非按部门维度） |

## 设计草案

- 新增 Apollo 配置 `Map<部门code, Set<模块枚举>>`（`@ApolloJsonValue`），扩展 `AiAppSceneEnum` 思路，给续班AI、退费AI各自的模块建枚举。
- "部门"取"课程所在的主数据部门"code（字符串数字，如`10012667`），查中文名走 `TeachDepartmentAclService.mapNamesByCodes`（student-center-adapter）。
- 生效点两处都要改：student-data 分析侧（未配置的模块不跑分析，省成本）+ student-center 展示侧（未配置的模块前端不可见/接口拒绝）。

## 上线影响面

| 配置项 | 涉及 | 工单/说明 |
|---|---|---|
| Apollo | 是（预计） | 部门→模块开关配置，可能沿用 `Map<部门code, Set<模块枚举>>` 模式 |
| ES | 待定 | |
| MySQL DDL | 待定 | |
| MQ | 否 | |
| 代课接口权限 | 否 | |

## 必须知道的坑

- 
