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

# 续班Dify迁移：当前验证结果


## 当前实收结果（56b53f3c5，2026-11-24）

TEST/test-gtbg-dev-1流水线1361114已部署UP，八场景新侧调用及LiteLLM实收核验完成：七例完整messages逐字相等；旅程user逐字相等，system恰等当前2482字模板加换行，保留resolvedRefundReasonList增强，与历史旧模板不同，不称完全相等。SOP V2复用既有完整输入一致证据。八业务answer均逐字等于下游最终content且stop；原9项model/platform/params覆盖完全未变。

13正式非知识库应用映射不等于八TEST样本覆盖全部生产应用；四知识库仍走Dify。本轮无生产修改；TEST新配置保留供后续验证，无临时监听或后台业务操作。

|场景|新trace|完整messages|
|---|---|---|
|画像|`dd182d47-b845-4135-80f2-f13575803a7e.0.3`|逐字相等|
|分层修正后|`e604b357-f357-4997-b28b-f3192b531eb8.0.3`|逐字相等|
|素养NPS|`5a814ae8-b8ae-4450-ada4-895a41d53463.0.3`|逐字相等|
|摘要|`62b40ff1-972a-4906-bd24-28e9486d4aa5.0.3`|逐字相等|
|退费根因|`f33b2e1d-019e-42d1-b97f-13e98c78c612.0.3`|逐字相等|
|旅程|`32999155-127f-418b-b073-600b6b159b6a.0.3`|user相等；system保留当前增强模板，与历史版本不同|
|课程体验|`6c006207-ade9-4800-b40a-a0db181b4c9c.0.3`|逐字相等|
|NPS|`b7f98851-b9b7-4395-89f9-39a63bbaeeef.0.3`|逐字相等|

完整旧新请求、user/system、最终输出及差异直接更新于原飞书各场景表，新版列已替换，SOP及两历史知识库表保留；revision67回读11表151代码块逐字一致（还原展示换行）。

证据：[统一结果](artifacts/comparison/format-runs/56b53f3c5/final-summary.json)、[业务响应回读](artifacts/comparison/format-runs/56b53f3c5/response-readback.json)、[覆盖配置未变](artifacts/comparison/format-overrides-preserved.json)、[部署UP](artifacts/comparison/format-deployment-ready.log)、[表格回读核验](artifacts/comparison/format-table-verification.json)。


## 比较对象与原表入口

同一业务数据分别经旧Dify及新网关，比较LiteLLM实际messages及最终content。旧路PROD日志与新路TEST日志是下游归属，不代表用了不同业务数据。参数差异独立展示，输出不同不强求对齐。

[飞书完整对照（revision67）](https://gaotuedu.feishu.cn/docx/EWI6dsdvPokck0xy89ccJDuEnhg)：八组新列已换为56b53f3c5本轮实收，完整输入输出和差异直接在原各表内；SOP V2复用既有完整输入相等结果，两个历史知识库样本仅供追溯。主要当前证据是本轮八场景实收，不再以91012878阶段差异作为当前状态。

## 实现与配置

56b53f3c5按应用恢复旧Dify消息形式：续班原flat单user，退费独立Dify system＋原应用flat user；SOP V2不变。TEST八应用格式配置已发布回读，releaseKey为20261124120843-188aa6ecfba696ce；流水线1361114部署UP且本轮实收已完成。此前全局单user尝试已撤销，不属于当前实现。

旅程保留当前模板增强，旧TEST模板与当前正式模板的差异不通过删除合法字段消除。正式应用映射见[13应用基准](artifacts/comparison/format-application-map.md)。生产DDL、发布与全量应用验证不属于此次TEST交付。

## 历史阶段与独立事项

revision56及91012878阶段曾记录“仅SOP user相等、其他场景包装不同”，对应旧实现；本轮八场景格式修复已覆盖该历史差异，当前结论以上方实收表为准。[旧配对](artifacts/comparison/pairs.json)、[旧差异审计](artifacts/comparison/user-diff-audit.json)保留追溯，不充当最新结果。

知识库Java隔离TEST接入6909717c已有独立成果，四个正式知识库应用仍保留Dify，不加入本轮格式迁移。生产凭据及空间授权调查见[接入证据](artifacts/expanded-refund/kb-service-e2e.md)和[权限调查](artifacts/expanded-refund/kb-service-auth-investigation.md)，不阻塞本轮非知识库格式结果。
