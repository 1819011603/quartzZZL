# 正式知识库凭据创建及受控检索已完成

2026-11-25。owner明确授权生产创建本人dataset key后，已正常创建并验证正式Service API检索可用。此前“没有凭据无法检索”的结论已被本次结果覆盖；不代表四个正式知识库应用已迁移或生产上线。

|验证项|实际结果|
|---|---|
|创建前查重|本人列表0枚，本任务key不存在|
|创建|正常Console POST，HTTP200；key id 361cfa66-495d-46c2-84f8-7ce87b54b83c；描述续班迁移TEST受控检索-20261125|
|创建后回读|HTTP200，本人共1枚、本任务匹配1枚、值与安全存储一致|
|首次检索|keyword_search，业务长查询，HTTP200、0片段；只证明认证/权限通过，不证明召回|
|实际召回验证|query=答疑反馈慢；full_text_search、top_k=4、reranking_enable=false、score_threshold_enabled=false；HTTP200，1文档/4非空片段|
|正式检索trace|cbc61996-27a1-4263-b504-dea8a8ef1e14.0.1|
|响应环境|X-Env=production、GAPM-AppID=dify-api|
|来源|本机TEST验证脚本经既有授权代理；不是student-data TEST Pod自动链路|

## 调用对象与结果

POST `https://dify-open.baijia.com/dify/api/v1/datasets/86233d1a-bddf-4a15-a229-c90b6a061c57/retrieve`。

命中文档 `ed0e3608-ca60-4007-bd00-b6e1d361d423`（降退费服务建议话术库）。四个片段长度944、240、635、694字；脱敏证据保存segment/document id、score、长度和SHA256，不复制片段全文。原库high_quality，full_text_search与其已读配置方法一致；本次明确指定不rerank/top_k4，不声称与正式工作流全部召回行为或排序等价。

## 密钥安全与范围

密钥仅保存在 `/Users/gaotu/.codex/private/dify-dataset-migration/production-dataset-key.json`（0600），目录0700；不在仓库、报告、消息或普通日志输出原文。描述和id可用于后续正常管理，未重复创建。当前未把密钥写入Apollo、数据库业务配置或应用环境，因此不声称Java接入已完成。

它是本人zhangzeling/id151350、生产共享租户的dataset类型Bearer key。当前部署不提供单库只读创建参数；检索仍校验token创建人的空间权限。正常创建和本次原库查询均已成功，其他库/修改权限未测试。不是浏览器Cookie或app聊天key。

## 验证边界

只做已授权生产密钥创建与原库检索。没有知识库文档内容写入、生产业务生成、路由切换、应用上线、提权、对外消息或正式四应用配置变更；四应用继续Dify。检索成功不等于完整迁移通过，后续若要验证TEST Java真实自动检索到生成，须作为独立目标限定范围。无在途操作。

## 证据文件

- kb-credential-current/authorized-key-create.json：创建/查重元数据，无token。
- key-postcreate-readback.json：匹配数量、0600、值一致布尔断言。
- authorized-production-retrieve.json：首次0条的完整参数与HTTP/trace。
- authorized-production-retrieve-fulltext.json：成功召回参数、HTTP、trace和片段安全元数据。
- normal-console-readback.json及prod-*-source.txt：身份、权限与鉴权机制原证据。
- pre-create-investigation.md：此前未获创建授权时的历史调查，现已覆盖。
