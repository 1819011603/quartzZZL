---
title: 【A-续班-20261001】膨胀券优化 · 链接中心
tags: [需求, 链接]
---

# 链接中心

> 这个需求仍有效的外部入口。新增时去重，链接失效或被替代后删除/更新。

## 需求与方案

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 需求wiki节点（权威） | 【A-续班-20261001】膨胀券优化（教学服务下） | https://gaotuedu.feishu.cn/wiki/MwezwKLebiU0afkphtCcNTgbndf | 2026-10-29 |
| 技术反讲（模块①） | 技术方案 · 膨胀券预报名优化（推荐规则 + 外显抵扣金额） | https://gaotuedu.feishu.cn/wiki/VMNYwMWA2iTvqskLi0ocNRyQnWg | 2026-10-29 |
| 技术反讲（模块②） | 技术方案 · 小班课学员人数上限修改 | https://gaotuedu.feishu.cn/wiki/CwkcwY5Q9iAD7fkx6CBcPKRDnpg | 2026-10-29 |
| PRD（模块①） | 【PRD】膨胀券预报名优化-推荐和外显抵扣金额 | https://gaotuedu.feishu.cn/wiki/TIGtweLV4iWdYtksyqNcWhIhnYb | 2026-10-29 |
| PRD（模块②） | 小班课学员人数上限修改 | https://gaotuedu.feishu.cn/wiki/PVy5woTCoiMvoMkQzKrcXckHnLw | 2026-10-29 |
| 调研（模块①背景） | 膨胀券业务问题汇总 | https://gaotuedu.feishu.cn/wiki/M4Prwi5uMizbR9kTuUsc4NTVnEe | 2026-10-29 |
| 待办表 | 教学服务迭代待办 | https://gaotuedu.feishu.cn/wiki/VgbOwav5TigsvDkr0cYcVnF6nsh | 2026-10-29 |
| 开发操作 SOP | 团队开发操作规范 | https://gaotuedu.feishu.cn/wiki/IJ5VwuzBciJ8uNkY3fOcYNpYnuh | 2026-10-29 |

## 开发与测试

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| TAPD | （待登记） | | |
| case | （待登记） | | |
| MR | （待建） | | |
| 接口文档 | （待登记） | | |

## 上线

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 上线checklist | （未到阶段） | | |
| 发布计划 | （未到阶段） | | |
| 工单 | 模块① MySQL DDL（promotion 活动商品新增列）待提；模块② Apollo（`parentsMeeting.type.limit.map`）待提 | | |

## 跨会话检索锚点

> 需求会改名，这些 ID 不会。下个会话搜目录时靠它们兜底（`rg -l "<id>" 需求根目录`）。

- 需求 wiki node_token：`MwezwKLebiU0afkphtCcNTgbndf`（docx `LLCwdnf8Lo1crexW4Mjc3i0GnCf`）
- 模块① 技术方案 node_token：`VMNYwMWA2iTvqskLi0ocNRyQnWg`（obj_token `TmaqdSPepo9Mv9x4fFCcNUEbnYg`）
- 模块② 技术方案 node_token：`CwkcwY5Q9iAD7fkx6CBcPKRDnpg`（obj_token `L763djIJhoYuamx8z77c4gOjnNd`）
- PRD（模块①）token：`TIGtweLV4iWdYtksyqNcWhIhnYb`（obj_token `KsdfdFRUeofBeLxzFhtckHcInda`）
- PRD（模块②）token：`PVy5woTCoiMvoMkQzKrcXckHnLw`（obj_token `QGG8dQwwQoxWuCxqiYRctOTUnNf`）
- 统一分支（2 子需求共用）：`feature-xuban-20261001`，建于 **6 个真实涉及仓库**（product-server / promotion / promotion-management / student-center / cart / teacher-tool），均基于最新 `origin/release`、本地未推远端；student-data 无改动、不建分支；ces-teach-product / course-center 不需改动、已撤分支。
- 旧占位分支（已清理，勿再用）：`feature-xuban-presale-expand-opt`、`feature-small-clazz-limit-and-search`

## 只存链接，不镜像明细

- **TAPD 工时任务** → 真相源 TAPD 服务端
- **反讲 TODO** → 真相源飞书技术方案文档
- **待办表** → 真相源飞书多维表格