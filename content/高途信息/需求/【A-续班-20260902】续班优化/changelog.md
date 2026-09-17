---
title: 【A-续班-20260902】续班优化 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

---

## 2026-09-17

### 🤖 Claude
- 建档：付星/马胜在飞书一次性转发5个续班优化wiki链接，要求初评并记录需求。最初误判为5个独立需求分别建了5个目录，用户澄清"这五个需求是一个需求"后合并为单一目录 `续班优化(秋季批)`，旧名保留在 frontmatter `aliases` 里防止按旧目录名搜索时找不到。
- 5路 Explore agent 并行完成两仓库(student-data/student-center)代码定位，结论已整合进本文件「涉及的代码」按子需求分节呈现。
- 核对5份PRD原文后修正：子需求2补记续班确认表(P1)与快速加购组合商品(P0)、删去"等需求方补充方案"的失效待确认；扩科推荐历史数据口径改为条件句（当前不回溯）；补记调课调班同步前提与场景、各子项P级、PRD可点链接。
- 重跑两仓库代码定位核查（基准 `origin/master`，工作区在另一需求的 `feature-xuban-pre`）并抽查复核，订正 6 处关键结论：问卷状态刷新非唯一挂载点(共4条路径)、`StudentSubclazzQuestionnaire` 是零引用孤立实体、多次提交去重在 `pageQuestionnaire` 非 `pageQueryQuestionnaire`、`mainTeacherList` 由 `WideSmallClazzTeachingBinder` 绑定、`CartEventService` 是业务 Service 非 ACL 适配器、数据落表另有直连 Doris Stream Load 先例；并补实 C端推荐/选品在 cart、快速加购落 product-server+order、续班确认表改动面在 contentReport+reach-service。

### 👤 我
- 在飞书里转发5个续班优化需求wiki链接，要求初评并记录需求，同时看下应该怎么做、做下设计。
- 澄清：这五个需求是一个需求，文档只要记录在一个文件夹下。
