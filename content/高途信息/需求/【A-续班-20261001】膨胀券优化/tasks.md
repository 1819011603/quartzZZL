---
title: 【A-续班-20261001】膨胀券优化 · 任务板
tags: [需求, 任务]
---

# 当前任务板

> **边界**：只记当前范围内仍需跟踪的任务和少量必要交付锚点。
> - 用户手工做的事 → `changelog.md` 的「👤 我」分区
> - TAPD 工时任务 → 只在 `links.md` 存链接，真相源在 TAPD 服务端
>
> 三套编号各自独立且不复用。状态：`待办` `进行中` `已完成` `阻塞` `已取消`

维护规则：状态变化确认后立即更新本文件，并同步 README 进度/卡点/下一步。

## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 模块① 技术方案评审：拍板「下单页券列表口径」 | 待办 | — | 仓库归属已按代码证据定（见 README「涉及的代码」） |
| T-02 | 模块② 确认工具箱「家长会/小班课/自习室」选学员/搜索接口所在服务与仓库 | 阻塞 | 待页面负责人确认 | 初步证据：student-center `StudentGlobalSearchController#searchByUserIds`(L58-63)/`GpsGroupController#studentPick`(L209)，teacher-tool `ManageSubclazzController#listSubclazzStudent`；需确认三页面实际调用 |
| T-03 | 评审后落地各仓 `specs/<迭代>/tech_spec.md` 并进入开发（统一分支 `feature-xuban-20261001`） | 待办 | 依赖 T-01、T-02 | 8 仓统一分支已就绪 |
| T-04 | 收敛统一分支 `feature-xuban-20261001` 并同步技术方案/归档 | 已完成 | — | 2026-10-29：8 仓从最新 origin/release 建分支（旧占位分支已删）；student-data 复核无改动不建；两篇飞书方案与本地归档已改统一分支口径并回读 |

## R- 反讲整改项

> 来源：飞书反讲文档 `8.1.3 Todo List`（**那份才是真相源**）。
> **上线前必须全部闭环。**

| 编号 | 整改项 | 谁提的 | 状态 | 备注 |
|---|---|---|---|---|
| — | （未评审，暂无） | — | — | — |

## C- case 联调问题

> 来源：case 评审后按 case 联调发现的问题。**提测前必须清完。**

| 编号 | 问题 | 对应 case | 状态 | 备注 |
|---|---|---|---|---|
| — | （未开发，暂无） | — | — | — |

## 阻塞详情

> 每个「阻塞」任务都要写清楚卡在谁/什么事上，否则下个会话判断不了能不能推进。

### T-02
- **卡在**：工具箱三页面（家长会/小班课/自习室）的选学员接口到底走哪条链路未最终确认。已有两类候选实现：①student-center `StudentGlobalSearchController#searchByUserIds`(L58-63) + `GpsGroupController#studentPick`(L209) + `MyStudentController#list`；②teacher-tool `ManageSubclazzController#listSubclazzStudent`(L185)/`ParentsMeetingBiz#listSubclazzStudent`(L383)。
- **需要谁**：工具箱页面负责人 / 本次反讲对口后端。
- **可以先做**：模块② 上限 15→32（Apollo `parentsMeeting.type.limit.map`）这条与搜索无关，可先行。

## 完成判据

> 判据口径见 `~/.claude/skills/requirement-docs/references/writing-rules.md`（一个任务 = 一个能独立验证的结论；
> 每条写死落点 / 怎么验 / 不达标先查）。
> 完成一项删一行；全部闭环后本节为空。

- T-01 落点：模块①技术方案评审通过，README「已定共识」记录下单页口径与改动仓库归属。怎么验：评审结论写入 已定共识并清空对应「待确认」。不达标先查：先约产品当面确认口径。
- T-02 落点：给出工具箱三页面搜索接口的服务名+路径+类#方法（含证据，如青舟路由或代码 file:line）。怎么验：用该接口按姓名/手机号各调一次，命中现有行为。不达标先查：先查三页面前端调用的网关路由，再顺路由反查服务。
- T-03 落点：两模块各改动仓 `specs/<迭代>/tech_spec.md` 落地，覆盖推荐规则/外显抵扣金额与上限/ID 搜索。怎么验：spec 头部三项齐全、接口变更类型已标注，与飞书技术方案一致。不达标先查：对照开发操作 SOP（links.md）核对格式。