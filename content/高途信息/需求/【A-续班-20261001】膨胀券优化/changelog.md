---
title: 【A-续班-20261001】膨胀券优化 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

> 倒序保留仍能解释当前设计的决策理由。允许压缩和删除无用旧条目；这不是完整会话日志。

---

## 2026-10-29

### 🤖 Claude

- 定了（定稿）：**模块②「选学员搜索」= teacher-tool**，非 student-center。证据：工具箱前端 `boss-counselor/src/pages/Toolbox/SmallClazz` 的 `services/manage.ts`（root=`/bgwApi/teacher-tool`）选学员搜索调 `/manage/subclazz/studentList`、人数上限调 `/manage/subclazz/getSignCountLimit`；现支持手机号（逗号/空格批量）+ 姓名模糊，PRD 新增手机号后4位批量 + 学员ID批量精确。GPS（GpsGroupController/MyStudent）与 student-center 选学员链路排除。
- 定了（定稿）：模块①**下单页的券是否随新推荐规则一起变**仍待产品——已重写为业务语言：A（统一改一处，下单页券跟着变）/ B（按调用方分叉，下单页不变），并推荐 A；含 `PreOrderCouponIntersectService#intersect` 被下单页/C 端/发链接三处共用的证据（方案① §8.1）。
- 定了：模块① 改动仓库已定（product-server/promotion/promotion-management/student-center/cart），仓库归属项从待确认移除。
- 定了（2026-10-29 所有者反馈）：**删除「膨胀券的，这次不用」边界项**——所有者明确「不用管」，模块①按在范围内推进（方案① §8 与需求入口 §6 已移除）。
- 定了（2026-10-29 所有者反馈）：**模块①「C 端外显抵扣金额」与「抵扣金额」是同一概念**——不新增并列字段/开关；业务手填值落券的 `deductible_amount`、C 端按 `showDiscountAmount` 展示（方案① §3.2/§4.2 已按同一概念改写）。
- 更新：两篇技术方案 + 需求入口 + 本地归档按上述定稿并回读；模块② 全文按「小灶课/辅导班小班课」、无 GPS 残留。

### 👤 我

- 所有者授权：「可以 修改技术方案」（回应「可否按待确认结论补一版方案」）。

---

## 2026-10-29（早）

### 🤖 Claude

- 定了：本迭代「【A-续班-20261001】膨胀券优化」由两条 PRD 合并为**1 个需求、2 个子需求**交付（模块①膨胀券预报名优化-推荐和外显抵扣金额、模块②小班课学员人数上限修改），对应飞书单一权威需求节点 + 两个模块技术方案子文档。
- 定了：模块①本期在范围内，覆盖两条 P0（推荐规则改全学科券 / 新增外显抵扣金额）。
- 定了：两子需求**共用统一分支 `feature-xuban-20261001`**，不按子需求拆分支。旧占位分支 `feature-xuban-presale-expand-opt`、`feature-small-clazz-limit-and-search` 确认 ahead=0 后已删。
- 定了（2026-10-29 复核后收敛）：真正需改业务代码的只有 **6 仓** —— product-server / promotion / promotion-management / student-center / cart（模块①）+ teacher-tool（模块②，小灶课/辅导班小班课人数上限）。**ces-teach-product / course-center 不需改动、已撤统一分支**（教室形态上限默认已 32、排课随教室上限自动放宽，PRD 不涉及）。
- 定了：模块②的「小班课」= **小灶课 / 辅导班小班课（工具箱-小班课）**，主链路在 teacher-tool；**不是 GPS 小班课**（`GpsGroupController` 等排除）。（2026-10-29 所有者明确）
- 定了：**student-data 无代码改动**（无外显抵扣/推荐交集；家长会/小班课仅 DWS ETL，与选人上限/ID 搜索无关），不建本需求分支，已删其两个旧占位分支。
- 定了：旧占位分支中 product-server / student-center 基于过期 release 头，统一分支一律改为最新 `origin/release`。

### 👤 我

- 所有者明确：本次两篇 PRD 属同一需求的两个小需求，要用统一分支，不要两个分支；要求按「1 需求 + 2 子需求」重整归属与命名，并逐仓复核「是否都要改」；纠正「小班课」= 小灶课的小班课，不是 GPS 小班课。