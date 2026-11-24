# TEST知识库替换实验（进行中）

基线263ba48ad2e476e7092093d36414280dddef2ed6d，worktree干净。生产仅配置只读及已授权原库检索；生成在TEST。已复用现有私有dataset凭据，不重复创建。

|对象|旧机制|当前新实现差距|本轮验收|
|---|---|---|---|
|精品降退费|advanced-chat固定code→检索→LLM→answer|已有隔离入口仅追加片段到user，不是旧工作流完整消息模板|同输入实际旧新messages/参数及检索证据|
|素养降退费|同图结构，使用自身模板|同上，不先假设模板相同|独立实收或明确等价依据|
|高中问题建议|agent-chat/function_call＋dataset|当前无有界工具执行循环|实际tools调用及tool结果循环对照|
|素养问题建议|同类agent但学部配置独立|同上|不能用固定工作流证据替代|

历史发现待本轮原样TEST复验：降退费LLM context绑定检索结果，但模板没有context占位符；严格复刻可能不消费知识。保留线上system/角色/参数，不擅自将增强拼接称为等价。既有12例不重跑。

现有DifyDatasetGatewayTestService仅检索后追加“##知识库检索结果”并执行普通动态prompt，未设置RunUser。当前只完成现状取证与TEST应用/库盘点，无代码、部署或新业务生成，本报告不表示替换已通过。

## 已完成旧侧真实前置实验

两项正式线上发布workflow已分别只读取得，复制为TEST advanced-chat应用并发布。唯二环境替换：旧模型改已确认deepseek-flash、dataset绑定既有TEST隔离库0105aec9；不宣称该库索引与生产对等。统一输入见kb-test-replacement/shared-business-input.txt。

两项调用均HTTP200/event=message，code、knowledge-retrieval、LLM、answer全部succeeded，检索各4片段。node-executions.process_data.prompts提供完整实际LLM消息；两者都是单system，检索片段未进入prompt，确认旧模板context未消费问题，不能用新追加片段入口冒称严格复刻。高中temperature=0.7，素养另有enable_thinking=true，必须分开参数。

证据old-workflow-summary.json及各场景prod-published.json、test-draft-request.json、old-request/response、old-node-executions.json、old-actual-messages.json。

## 续接（上下文交接，不是业务阻塞）

- 本轮无代码修改/commit/部署，worktree仍263ba48a干净。TEST两个workflow应用已创建发布，不能重复创建；id在old-workflow-summary.json。TEST app key安全存.codex/private/dify-dataset-migration下对应场景-test-app-key.json，0600，不入归档。
- 新侧DifyDatasetGatewayTestService需最小支持固定workflow消息契约（原因提取、检索、按旧system模板渲染，不无条件附加知识；显式context增强另列实验），RunUser取现有SubClazzHelper真实来源。修改前已有真实前置证据。
- 接下来取得两旧侧LiteLLM实收非messages参数：入口response headers/EndUser或workflowRun关联；持久化prompts已可用，不要重跑旧业务。
- 对同一TEST库同输入配置Java新入口并实跑，比较完整messages及指定参数；修正/测试后一次commit+push+TEST部署，再定向复验。
- 高中/素养问题建议agent场景尚未读取完整线上独立发布配置、未复制运行；需要保留tool schema/tool调用/tool结果与有界循环，不复用废弃降退费agent当基准。
- source skills已读requirement-docs/student-data-dev/dev-anti-rework、git-branch-convention；原仓库AGENTS.md已定位并读前65行，编码前读完整。worktree无AGENTS，适用原仓库规范。不创建子agent。
- 可复用脚本/tmp/kb_workflow_copy.py、kb_workflow_publish.py、kb_workflow_run.py、kb_collect_old.py。publish脚本不具备key创建幂等性，不可重跑；run脚本有response存在跳过。所有当前操作已结束，无在途句柄。

## workflow新入口实现批次

47b3dcb7e5c6bdb4c908821cfe6ddf20d01e476e 已commit+push。新增DifyDatasetGatewayTestService.retrieveWorkflowAndComplete(WorkflowRequest)，检索原因复刻旧正则，按发布模板渲染messages，未引用context时不追加片段；自动SubClazzHelper获取RunUser。原入口与正式业务不变。Maven reactor compile成功，4个JUnit Jupiter测试通过，日志见本目录。

两旧侧LiteLLM实收已补：高中83af554c-558e-4491-9baf-c2add01b2e27.0.3：stream=true、temperature=0.7、model=deepseek-flash；素养38f00685-52f1-4c61-9637-0ea17be772da.0.3再加thinking.enabled；均无max_tokens。各场景old-llm-received.json保留完整请求。

已触发TEST部署，结果/跟踪入口/tmp/kb-workflow-deploy.json，尚未确认新Pod生效；不得将47b3dcb7标成已实测。仍需新入口同输入实际复验、当前head AICR及两问题建议agent实现验证。

