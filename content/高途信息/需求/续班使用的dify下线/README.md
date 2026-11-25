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

## 当前结论：15场景有限TEST验收完成

当前生产生成配置的TEST对照已闭合：画像旧/新推理token1593/753，摘要806/751，均开启thinking；高中分层、素养分层均0/0，关闭thinking。四组完整messages逐字相等，推理token数量不要求相同。画像/摘要保持原目标模型默认行为；两分层新侧显式disabled保留生产旧别名force注入行为，不再混用模型基准。

完整输入、HTTP、响应和trace见[15场景对照](artifacts/comparison/final-15-comparisons.json)、[画像有效基准](artifacts/comparison/thinking-effective-alignment.md)、[关联三场景实收](artifacts/comparison/thinking-related-verification.md)。当前TEST47b3dcb7，普通链路未受影响证据复用263ba48a，未全量重跑。仅有限TEST验收完成，不代表生产全量等价、生产上线或普遍输出语义等价。

|场景|当前结果|证据版本|
|---|---|---|
|用户画像|生产原目标模型TEST旧新messages相等、thinking均开启；1593/753|47b3dcb7|
|沟通摘要|当前生产模型TEST旧新messages及有效thinking相等；806/751开启|47b3dcb7|
|服务SOP|完整对照齐全，messages相等|263ba48a|
|高中分层|当前生产旧别名TEST对照，messages相等、有效thinking均关闭0/0|47b3dcb7（旧证据按项复用）|
|精品根因|完整对照齐全，messages相等|263ba48a|
|精品旅程|完整对照齐全，messages相等|47b3dcb7|
|精品课程体验|完整对照齐全，messages相等|263ba48a|
|精品NPS|完整对照齐全，messages相等|263ba48a|
|素养分层|当前生产旧别名TEST对照，messages相等、有效thinking均关闭0/0|47b3dcb7（旧证据按项复用）|
|素养根因|完整对照齐全，messages相等|263ba48a|
|素养旅程|完整对照齐全，messages相等|263ba48a|
|素养课程体验|完整对照齐全，messages相等|263ba48a|
|素养NPS|完整对照齐全，messages相等|47b3dcb7|
|高中降退费|完整对照齐全，messages相等|47b3dcb7|
|素养降退费|完整对照齐全，messages相等|47b3dcb7|

画像/摘要基准证据分层及结论变化见[基准说明](artifacts/comparison/baseline-thinking-clarification.md)：按生产配置的TEST复现，不是生产运行直接观测。

## 差异与边界

保留差异：旧模型别名按已核实网关映射使用替代模型；旧Dify user为EndUser UUID，不复制；response_format按场景保留JSON约束或text（旧侧部分省略），逐项以完整请求表为准。因此不是全部HTTP字段字面一致。

两降退费工作流为同输入、同隔离TEST库的检索→渲染→生成对照；旧新模板均未把检索片段注入LLM消息。不代表知识增强或生产索引召回效果等价。

退款真实refundReasoningEvent未传RunUser，自动取得老师并发送gongxuemeng费用头，trace 611aeb2f；SOP自动身份同次trace d7043e0b。watch MDC为空的退款按完整body与同trace下游HTTP精确关联。工作流代表样本ec09563e验证显式身份传递，素养复用相同费用头路径，不冒称自动老师来源。

本轮排除：高中问题建议、素养问题建议，指定库分别5b040e52/a195df23查询403，真实语料工具循环未完成。高中履约沟通推荐话术11月25日08:53仍在成功调用；素养最新查得1月20日记录、配置保留，近期使用未确认。四生产知识库应用继续Dify。

## 交付与证据

代码47b3dcb7已提交推送及TEST部署（流水线1362995），4项JUnit及编译通过；普通链路原有效证据复用。AICR2403取消，不称评审通过。本轮补齐未新增代码部署。

- [迁移注意事项与适用实践](artifacts/comparison/migration-practices-current.md)
- [15场景最终验证](artifacts/comparison/final-15-verification.md)
- [完整输入输出及请求对照](artifacts/comparison/final-15-comparisons.json)
- [机器验收结果](artifacts/comparison/final-15-verification.json)
- [问题建议实际使用](artifacts/comparison/problem-suggestion-usage-current.md)
- [飞书完整对照](https://gaotuedu.feishu.cn/docx/EWI6dsdvPokck0xy89ccJDuEnhg)

## 现在什么情况

T-验收：15/15有限TEST场景完成，两个403场景排除；生产未切换，随机输出与生产全量等价未作保证。

## 当前资源

TEST NPS fixture30339441、独立旅程与SOP样本保留供复验；密钥仅私有存储。Arthas已reset/stop，无在途操作。底层历史证据保留作溯源，不作为当前状态。



画像当前基准及完整对照见[真实生产配置验证](artifacts/comparison/profile-real-baseline.md)。旧通用agent证据不再作为当前基准；历史原始文件保留。
