---
title: 【A-续班-20260902】续班优化 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

---

## 2026-09-18（下午）

### 🤖 Claude
- 确认【问卷匹配优化】的 product-server + teacher-tool 改动归属给我，产出逐文件改动清单（见 README 子需求1「改动清单」）：product-server 7 项（ComputeParams 扩字段、解析前移、3 条 plan 级规则、Apollo 6 级顺序、去掉 `subclazzDTOS.get(0)`、无绑定号路径收敛计划、fan-out 留给 student-data）；teacher-tool 3 项（续班计划列按需、改派能力、明细查询无需改）。
- 关键结论「范围扩大能否匹配正确」：**能解决"人在同计划其他班"（调班/发错链接）+ 手机号精确匹配**；**不能解决同名/亲属手机号歧义**（取 userId 小仍是猜），范围越大歧义面越大。plan 级必须限定"同一问卷的课程"而非全计划课程，否则会匹配到不同问卷的班。
- 明确"改不了/改不全"的边界：①同名/一号多孩根因（输入信息不足，算法无解，需产品决策）；②存量错配按 PRD 不回溯；③明细 A/B 两行 fan-out 在 student-data，不在我手上；④调课调班同步若由 product-server 承接需新增 consumer + DAO 方法；⑤teacher-tool 加续班计划列需 DDL；⑥规则改动影响大班+小班全部续班问卷匹配，回归面大。
- 按用户要求在飞书建档：父文档「【A-续班-20260902】续班优化」+ 子页面「问卷匹配优化：匹配逻辑现状·改动方案·风险」（写入匹配逻辑现状/改动方案/待办清单/风险点）。**注意落在个人空间 `my_library`（space 7485951460694425602）**——原需求 wiki 空间 `7521677387233722372` 无建节点权限（131006）。链接与 token 见 links。
- 同步本地：tasks.md 加 T-06~T-09（问卷匹配开发待办），links.md 加飞书入口与 token，README 导航加飞书总入口。
- 性能评估（3 个风险点）：①**重试 Job 放大**——`dealNotExistedComputeUser` 每轮重跑 `computedUserId=0` 且 3 天内的记录（100/批、16 线程），改"不唯一→0"后这批记录永远匹配不上、每轮重复处理，叠加规则链 4→7 条，负载上升，必须同步改造重试策略；②每条提交最坏 RPC 从 7-8 升到 11-12 且串行（`compute` 顺序 for，MQ 仅 5 线程），群发场景会排队；③plan 级姓名规则最贵（班内版已 scroll 2000/批 + listByUserIds），建议改走 `listByStudentName`(限100)+计划过滤。手机号/亲属号 plan 级成本可控（500/批，候选集小）；`compute.rule.name.list` 在 Apollo 可单独降级。
- 深挖【问卷匹配优化】现状：定位到真正匹配实现不在 student-data/student-center，而在 **product-server**（即 Feign 名 `product-b`）——绑定层 `QuestionnaireService#match:928`、记录归属层 `ComputeUserService` 规则链(`OriginUser`/`Mobile`/`Name`/`RelationId`，全部限定班级内)、跨班兜底 `QuestionnaireRecordService#dealNotExistedComputeUserId:253`（混候选取第一个 `subclazzDTOS.get(0)`）。订正原 README「6级规则本仓未实现需新建匹配服务」的表述：规则链已存在且 Apollo 可插拔，改造是扩规则而非从零新建。
- 补 teacher-tool 侧：明细表 `user_questionnaire_record` 无续班计划字段，查询 SQL 只按 `type+project_number+clazz_number+user_id` 过滤；手工绑定只能改 user 不能改 clazz。
- 调课调班同步订正：student-data `SubclazzUserSyncConsumer` 已消费 `TAG_Subclazz_Transfer`，但只刷续班状态/科目，未刷问卷字段。
- 用户提供飞书分析文档《续班问卷跨班错配问题：现状、成因与产品解法》，与代码结论互相印证（其描述的"扩范围+混候选+取第一个"即 `dealNotExistedComputeUserId`）；已登记 links。可借鉴点：根因论据、6级规则仅"少猜错"不能归零、"待认领+改派"与存量修复是需求未覆盖项。

### 👤 我
- 要求弄清【问卷匹配优化】的现状/改动/影响/代码改动，并提供此前写的跨班错配分析文档供借鉴。

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
