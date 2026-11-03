---
title: 【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整
aliases: [企微封禁优化, EM纯续推荐范围调整, 纯续关联, 计划关联]
status: 开发中
owner: zhangzeling
branches:
  - product-server:feature-xuban-pure-relation-20261102
  - student-center:feature-xuban-pure-relation-20261102
  - cart:feature-xuban-pure-relation-20261102
  - order:feature-xuban-pure-relation-20261102
updated: 2026-11-03
tags: [需求]
---

# 【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整

> 飞书方案（含表结构+接口协议）：https://gaotuedu.feishu.cn/docx/AQEtdIeKzo7P5IxeQEzc7EpxnBe

## 一句话

一个主需求、两个子项：子项1 在 EES 续班服务（大班+小班）补齐默认花名册已有的「加标签/改企微备注」与「学员标签」；子项2 新增续班计划【纯续关联】，使一个纯续链接可含大小班纯续班级并下单。

## 已定共识

- Q1=B：子项1=大班+小班续班服务都做；「企微封禁」属功能缺失、官方接口正常。
- Q2=A：子项2 采用计划间关联（新建 `renew_master_relation` + 推荐并集 + 下单跨模式放行）。
- 推荐并集只并纯续（主+从），扩科不变。
- 单一 Apollo 开关 `renewal.pure.relation.enabled`（默认 false，cart+order 共读）。
- 上限 10、状态【待开始/进行中】；**接口收敛为单个「最终确认」save（全量集合差分）**。
- 历史兼容：不刷数。

## 现在什么情况

- 4 仓分支 `feature-xuban-pure-relation-20261102`（origin/release，--no-track）；cart 未切换、现场未动。
- test 建表 `gaotu.renew_master_relation`；cart Apollo 开关已发布=false。
- product-server：关系持久层/服务/控制器 + DTO 下发填充完成；接口收敛为 `relation/save`；编译通过，push `e16e3a27`。

## 阻塞

- order Apollo 无写权限（litao04）→ 默认 false 兜底可先上线。
- GAIA 两场景显示记录无创建入口 → 需 GAIA 后台/管理员。

## 涉及代码

- product-server：`RenewMasterRelation` / `RenewMasterRelationBizMapper`(+XML) / `RenewalMasterRelationService#save` / `RenewalMasterRelationController`（list/save）；`RenewalServiceImpl` 下发 `relatedRenewMasterNumbers`。
- cart/order：并集+预热 / 受控放行（待做）。student-center：两套字段配置（待做）。
