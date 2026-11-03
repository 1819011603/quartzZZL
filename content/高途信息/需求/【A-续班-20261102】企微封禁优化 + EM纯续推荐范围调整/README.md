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

- 4 仓 HEAD 均为 `feature-xuban-pure-relation-20261102`；cart 已切统一分支，原 `feature-xuban-expand-exclude` 未提交现场（yapidoc.json、ExpandSubjectRecommendContractTest）已 `git stash` 保留。
- test 建表 `gaotu.renew_master_relation`；Apollo 开关默认 false（product-b/cart 已回读 false，白名单置空）。
- 编译：cart / product-server-b / order-app 均通过。
- 部署 `test-gtbg-dev-3` 全部 **eureka UP**：cart `9781f993`、product-b `d99e9162`、product-c `473b26b7`、order `0aaa0f44`。
- **修复 bug**：`RenewalMasterRelationController` 原直返 `RestResponse` 导致非管理员路径 `ClassCastException`→「未知错误」；改为 `RestTraceResponse`+`RestTraceResponseUtils.handleRequest`（push `d99e9162`）。
- product-b 已验证：save（白名单/管理员校验）+ list + 全量差分（增/软删/软删复位）+ 缓存 + 下发字段随开关。

## 阻塞

- **product Apollo（app `product`，负责人 litao04）无发布权限** → product-c 的 `renewal.pure.relation.enabled` 无法在 test 打开 → cart 并集端到端无法验证（product-c 下发实测仍无 `related_renewMasterNumbers`）。
- **order Apollo 无权限（litao04）** → 跨模式放行开关无法在 test 打开 → order 放行未验证（默认 false 兜底）。
- GAIA 两场景显示记录无创建入口 → 需 GAIA 后台/管理员；student-center 两套字段配置需管理员。
- 代码级风险（未实测）：cart 大班 `coreHandle` 按 `course.filter.type:30,40` 过滤后置课程，跨模式（小班）并集可能被排除。

## 涉及代码

- product-server：`RenewMasterRelation` / `RenewMasterRelationBizMapper`(+XML) / `RenewalMasterRelationService#save` / `RenewalMasterRelationController`（list/save）；`RenewalServiceImpl` 下发 `relatedRenewMasterNumbers`。
- cart/order：并集+预热 / 受控放行（待做）。student-center：两套字段配置（待做）。
