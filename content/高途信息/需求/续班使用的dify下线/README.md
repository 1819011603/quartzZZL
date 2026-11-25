---
title: 续班使用的dify下线
aliases: [续班dify下线, 退费dify下线]
status: 开发中
owner: zhangzeling
branches:
  - student-data:feature-xuban-dify-offline
repos:
  - student-data
updated: 2026-11-25
tags: [需求]
---

# Dify迁移当前结论

已完成15个有限TEST场景对照，非生产全量上线验收。当前代码47b3dcb7；普通链路复用263ba48a有效证据，未全量重跑。允许确认的替代模型；随机输出不要求逐字一致。

|场景|当前结果|证据版本|
|---|---|---|
|用户画像|请求对齐、字段格式兼容；输出抗性归类有差异，语义等价未证明|263ba48a|
|沟通摘要|完整对照齐全，messages相等|263ba48a|
|服务SOP|完整对照齐全，messages相等|263ba48a|
|高中分层|完整对照齐全，messages相等|263ba48a|
|精品根因|完整对照齐全，messages相等|263ba48a|
|精品旅程|完整对照齐全，messages相等|47b3dcb7|
|精品课程体验|完整对照齐全，messages相等|263ba48a|
|精品NPS|完整对照齐全，messages相等|263ba48a|
|素养分层|完整对照齐全，messages相等|263ba48a|
|素养根因|完整对照齐全，messages相等|263ba48a|
|素养旅程|完整对照齐全，messages相等|263ba48a|
|素养课程体验|完整对照齐全，messages相等|263ba48a|
|素养NPS|完整对照齐全，messages相等|47b3dcb7|
|高中降退费|完整对照齐全，messages相等|47b3dcb7|
|素养降退费|完整对照齐全，messages相等|47b3dcb7|

## 差异与边界

保留差异：旧模型别名按已核实网关映射使用替代模型；旧Dify user为EndUser UUID，不复制；response_format按场景保留JSON约束或text（旧侧部分省略），逐项以完整请求表为准。因此不是全部HTTP字段字面一致。

两降退费工作流为同输入、同隔离TEST库的检索→渲染→生成对照；旧新模板均未把检索片段注入LLM消息。不代表知识增强或生产索引召回效果等价。

退款真实refundReasoningEvent未传RunUser，自动取得老师并发送gongxuemeng费用头，trace 611aeb2f；SOP自动身份同次trace d7043e0b。watch MDC为空的退款按完整body与同trace下游HTTP精确关联。工作流代表样本ec09563e验证显式身份传递，素养复用相同费用头路径，不冒称自动老师来源。

本轮排除：高中问题建议、素养问题建议，指定库分别5b040e52/a195df23查询403，真实语料工具循环未完成。高中履约沟通推荐话术11月25日08:53仍在成功调用；素养最新查得1月20日记录、配置保留，近期使用未确认。四生产知识库应用继续Dify。

## 交付与证据

代码47b3dcb7已提交推送及TEST部署（流水线1362995），4项JUnit及编译通过；普通链路原有效证据复用。AICR2403取消，不称评审通过。本轮补齐未新增代码部署。

- [15场景最终验证](artifacts/comparison/final-15-verification.md)
- [完整输入输出及请求对照](artifacts/comparison/final-15-comparisons.json)
- [机器验收结果](artifacts/comparison/final-15-verification.json)
- [问题建议实际使用](artifacts/comparison/problem-suggestion-usage-current.md)
- [飞书完整对照](https://gaotuedu.feishu.cn/docx/EWI6dsdvPokck0xy89ccJDuEnhg)

## 现在什么情况

T-验收：已完成15/15（两个403场景本轮排除）；TEST当前47b3dcb7，生产未切换。

## 当前资源

TEST NPS fixture30339441、独立旅程与SOP样本保留供复验；密钥仅私有存储。Arthas已reset/stop，无在途操作。底层历史证据保留作溯源，不作为当前状态。

画像输出具体边界见[同层输出比较](artifacts/comparison/profile-output-comparison.md)，不以messages相等推导输出语义等价或业务落库已验。
