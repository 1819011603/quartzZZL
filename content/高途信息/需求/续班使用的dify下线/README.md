---
title: 续班使用的dify下线
aliases: [续班dify下线, 退费dify下线, 续班退费dify下线, 续班AI去dify, dify下线, 续班AI切换大模型网关]
status: 开发中
owner: zhangzeling
branches:
  - student-data:feature-xuban-dify-offline
repos:
  - student-data
updated: 2026-11-24
tags: [需求]
---
# 续班Dify迁移：输入输出对照入口

## 比较的是什么

同一份业务数据分别走旧链路“student-data → Dify → LiteLLM”和新链路“student-data → LLM网关 → LiteLLM”。比较的是LiteLLM实际收到的messages及参数、实际返回的最终content；业务answer是后续加工层，不混称原始响应。旧日志在PROD、新日志在TEST是日志归属，不表示两个不同业务样本。

## 从这里阅读

[飞书：逐场景对照与完整原文](https://gaotuedu.feishu.cn/docx/EWI6dsdvPokck0xy89ccJDuEnhg)

文档已重整为比较定义、阅读结论、11组场景对照、表内完整原文。每组展示样本、历史或修正阶段、时间trace、输入输出片段和参数；无需打开本地文件。主要证据来自2026-11-23的91012878验证阶段，不冒充6909717c重新回归。

覆盖画像、SOP V2、修正后分层、素养NPS、摘要、退费根因、旅程、课程体验、精品NPS，以及历史降退费和素养建议样本。SOP V2同fixture输入逐字段相等；其他场景保留包装、模板和参数差异。历史废弃降退费agent的工具回灌差异不外推正式生产工作流。输出不同的成因未经受控实验，不笼统归因随机性。

## 证据与历史

- [整理后的配对数据](artifacts/comparison/pairs.json)
- [飞书回读证据](artifacts/comparison/readback.json)
- [整理前README备份](artifacts/comparison/README-before-reorganize.md)
- [整理前飞书revision47备份](artifacts/comparison/feishu-revision47-backup.json)

历史记录保留用于追溯，不作为当前阅读入口。去think及首尾空白后相同与原文逐字相同分别标注。

## 独立事项

知识库Java隔离TEST接入6909717c已跑通，但只有新侧样本，不参与旧新配对。4个正式知识库应用保留Dify。生产知识库有效服务凭据和空间授权限制独立保留，详情见[服务接入证据](artifacts/expanded-refund/kb-service-e2e.md)及[凭据调查](artifacts/expanded-refund/kb-service-auth-investigation.md)。本次只重整文档，未重跑业务或改代码配置。

## user原文核对（revision56）
11组仅SOP V2真实user逐字相等，其余10组不同。画像/摘要/分层内嵌指令迁入system；NPS/素养NPS/体验删除通用指令；根因/旅程/降退费删除场景标签；素养建议业务正文由system移入user。业务正文相等不能称user相等。全部输入输出及字符级差异直接放飞书表格内。回读11表143代码块全部逐字一致（还原展示换行）。证据：artifacts/comparison/user-diff-audit.json、user-table-verification.json。

## 当前进行中：输入格式对齐旧Dify
所有者已将验收口径改为旧Dify实际messages格式对齐，语义近似不再满足新增目标。应用级实现进行中，尚未部署或完成新一轮实收。全局单user尝试已撤销，远端8becd39fb与6909717cc代码相同。当前基准见[13应用格式映射](artifacts/comparison/format-application-map.md)：续班5项使用原flat（SOP保留V2），退费8项保留独立Dify system及原flat user；正文按各应用自身配置，不能照搬历史TEST旅程模板。TEST应用与Apollo当前回读分别见[应用快照](artifacts/comparison/format-test-applications.json)、[覆盖配置快照](artifacts/comparison/format-apollo-before.json)。
