# ID存储与配置格式（2026-11-26）

依据迁移分支47b3dcb7e的实体、Mapper、访问器和已归档生产绑定核验；本轮没有在线查询数据库/Apollo，因此表内具体值是历史快照，不是当前线上回读。

## ID和存储位置

|对象|存储/传递位置|含义|
|---|---|---|
|业务application编号|ees_data.ai_application.number|业务应用主键，非Dify UUID|
|业务agent编号|ees_data.ai_agent.number；ai_application.ai_agent_number关联它|访问平台及应用凭据的配置对象|
|提示词配置编号|ai_application.prompt_config_number；prompt_config_version_number/auto_use_current_version选择版本|gateway_core_prompt承载迁移system提示词|
|Dify应用UUID|已发布Dify Console应用/工作流配置；应用key绑定对应Dify应用|未在上述ai_agent/ai_application Mapper发现单独Dify UUID列；旧调用通过access_key识别应用，不把业务number当UUID|
|dataset UUID|旧Dify工作流knowledge-retrieval节点data.dataset_ids数组|原降退费库86233d1a-bddf-4a15-a229-c90b6a061c57；不是业务application编号|
|TEST新入口datasetId|retrieveAndComplete方法参数或WorkflowRequest.datasetId|调用方显式传入，Retriever未从业务表读取dataset；无dataset-id Apollo字段|
|应用聊天凭据|ai_agent.access_key|访问/chat-messages时作为Bearer；不是dataset token|
|dataset凭据|Dify ApiToken/type=dataset；Java配置ai.dify.dataset.retrieve.api-key|与Console Cookie分离；生产key仅有本机历史验证证据，未证实进入Apollo/Pod|

Dify内部dataset/工作流JSON实际数据库表字段，本轮没有对应部署模型/DDL证据，不猜测具体物理表。问题建议agent的dataset绑定位于Dify应用配置；本轮未重查其内部持久化字段。

## 正式绑定与路由格式

历史生产快照：精品/高中降退费application=256995990719977472，agent=256995156763347968，Dify UUID=5c7ac7f6-af1d-4120-91a5-9a6485fd3d99；素养application=261424650482886656，agent=261424592068814848，Dify UUID=1043df8c-f3d3-44b3-accd-ec2051c0c4a3。

Apollo student-data / application 的refund.reasoning.suggesstion.dept-agent为JSON：
```json
{"10013429":256995990719977472,"default":256995990719977472,"10012667":261424650482886656,"10019736":261424650482886656}
```
虽然键名含agent，value实际为ai_application.number。另一配置ai.agent.accessor.override.map的key才是ai_agent.number字符串；格式示意为{"<agent number>":{"platformType":2,"model":"<模型>","params":{}}}，不是本次要发布的配置。四正式知识库仍保留Dify。

## 域名、检索配置与请求格式

旧应用域名键AiAgentAccessHelper.domain，代码默认https://dify-open.baijia.com/dify/api/v1，拼/chat-messages。默认值不能代替当前Apollo实际值。

TEST检索配置位于student-data TEST/default/application（已有发布证据）；键前缀ai.dify.dataset.retrieve.：enabled=true、environment=test、base-url=https://test-dify-open.baijia.com/dify/api/v1、api-key=<安全注入dataset凭据>、top-k=4、reranking-enabled=false、search-method=keyword_search、score-threshold-enabled=false。最后一项有代码默认false，不据此断言已单独发布该键。代码默认enabled=false、environment为空；environment=test是客户端启用条件，不会自动转换域名或凭据环境。

生产Service API基址https://dify-open.baijia.com/dify/api/v1；请求POST /datasets/{datasetId}/retrieve，Authorization: Bearer <对应环境dataset token>，JSON：
```json
{"query":"答疑反馈慢","retrieval_model":{"search_method":"full_text_search","top_k":4,"reranking_enable":false,"score_threshold_enabled":false}}
```
这是既有生产成功样本格式，不是当前TEST默认方法；旧工作流另有multiple_retrieval_config.top_k=4、reranking_enable=false及query_variable_selector。不能把显式API参数、TEST默认参数和旧工作流配置混作同一层。

TEST隔离application1795457739670157、agent1795457739670155、prompt_config1795457739670159、dataset0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce均为实验资源，不是正式生产配置。

证据：迁移分支AiAgentMapper.xml、AiApplicationMapper.xml、AiAgentAccessHelper.java、AiAgentAccessorOverrideResolver.java、DifyDatasetRetriever.java、DifyDatasetGatewayTestService.java；artifacts/expanded-refund/deprecated-binding.md、kb-service-config-published.json；artifacts/comparison/kb-credential-current/credential-provenance-acceptance.md。生产具体配置现值、生产key在运行Pod的加载状态以及Dify内部物理表字段仍未在线核实。本轮仅文档增量，无代码/配置/数据变更或业务调用。
