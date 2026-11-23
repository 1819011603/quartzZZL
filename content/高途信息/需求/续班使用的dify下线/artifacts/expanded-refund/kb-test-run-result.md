# 知识库复用测试结果（2026-11-24）

已跑通隔离知识库检索→新链路显式拼装→TEST网关模型生成。不是正式业务替换，也不是生产语义检索对等证明。4个原知识库应用仍保留Dify。

共享Dify平台新建only_me隔离dataset 30a822a4-32f5-49e8-b497-eaad5f8280de，app_count=0，从已有只读导出69段话术建立economy副本，69/69索引完成。实际Console hit-testing用原工作流代码规则形成查询，keyword_search/top_k=4/reranking=false，命中4条、正文共2223字，其中含“服务不满意-沟通答疑及时性”话术。不是模拟检索。源生产dataset未被检索或修改；共享平台中的隔离测试资源保留，未建共享服务key。

新链路使用完整生产素养降退费系统模板，将sys.query替换为合成业务对象（未发起退费、答疑慢、课后不会做、愿在服务改善后继续），另加user消息<context>承载全部4条真实检索片段。通过TEST/test-gtbg-dev-1现有LlmGatewayAccessor#query调用，无代码、路由或配置改动；沿用此前91012878部署，本轮未重新部署，未独立刷新镜像版本。模型返回suggestion、recallSuccessRate、recallReason三字段合法JSON，包含及时答疑、当天收题、针对性练习等干预建议，成功率中高。这里只验证生成和结构，不据一条输出宣称质量全面通过。

真实入口及下游共用trace：74955599-a191-4f56-92d6-f63eaaa9aca9.0.3。TEST SLS可查到一条LiteLLM请求；实收messages与提交messages逐字段相同，证明检索内容实际进入模型。TEST TLS未命中。原始请求、响应、响应头、实收及检查在kb-test-model目录；检索请求响应与资源记录在kb-test-retrieval目录。

完成TEST模型调用后才核查生产条件：平台公开Service API base为https://dify-open.baijia.com/dify/api/v1；只读接口无Bearer返回401，说明存在鉴权要求，不能证明已有可用凭证。当前工作区dataset API key列表为空，原生产dataset详情返回403（Unable to verify space permissions for this dataset）。因此当前只证明Console登录态可以操作隔离库，长期服务账号访问生产知识库尚未就绪。未创建共享workspace key，未修改生产权限、配置、路由，也未触发生产检索或业务推理。

限制明确：economy关键词检索不等于生产向量/高质量检索，同query命中与排名未验证；此为本地编排+TEST现有访问器试验，不是已部署的自动检索adapter。问题建议agent的完整tools循环本轮没做，不能用前置检索成功替代该机制验证。旧生产工作流context.enabled虽为true，但无显式引用；可见源码版本未对应公司镜像，实际旧侧自动注入仍未确认（kb-context-source-check.md）。新链路显式注入已验证，不冒充旧生产context验证。

剩余外部条件：需要目标生产知识库获授权的Service API凭证/访问权限，之后才可验证服务身份接入与生产同参数检索。若需旧生产工作流注入对照，须在TEST建立对应工作流及同配置知识库副本再比实收；当前未完成。上述缺口不靠复制tools声明解决，也不需要先自建知识库。现有4项保留Dify决定不变。
