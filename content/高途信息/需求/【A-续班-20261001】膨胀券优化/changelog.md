---
title: 【A-续班-20261001】膨胀券优化 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

> 倒序保留仍能解释当前设计的决策理由。允许压缩和删除无用旧条目；这不是完整会话日志。

---

## 2026-10-29

### 🤖 Claude

- 定了：本迭代「【A-续班-20261001】膨胀券优化」由两条 PRD 合并为**1 个需求、2 个子需求**交付（模块①膨胀券预报名优化-推荐和外显抵扣金额、模块②小班课学员人数上限修改），对应飞书单一权威需求节点 + 两个模块技术方案子文档。
- 定了：模块①本期在范围内，覆盖两条 P0（推荐规则改全学科券 / 新增外显抵扣金额）。
- 定了：两子需求**共用统一分支 `feature-xuban-20261001`**，不按子需求拆分支。已在 8 个真实涉及仓库从**最新 `origin/release`** 建分支：product-server / promotion / promotion-management / student-center / cart / teacher-tool / ces-teach-product / course-center；旧占位分支 `feature-xuban-presale-expand-opt`、`feature-small-clazz-limit-and-search` 确认 ahead=0 后已删。
- 定了：**student-data 无代码改动**（无外显抵扣/推荐交集；家长会/小班课仅 DWS ETL，与选人上限/ID 搜索无关），不建本需求分支，已删其两个旧占位分支。
- 定了：旧占位分支中 product-server / ces-teach-product / course-center / student-center 基于过期 release 头，统一分支一律改为最新 `origin/release`。

### 👤 我

- 所有者明确：本次两篇 PRD 属同一需求的两个小需求，要用统一分支，不要两个分支；要求按「1 需求 + 2 子需求」重整归属与命名，并复核真实涉及仓库。