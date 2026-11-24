# 降退费知识检索/tools迁移方案（第五项只读交付）

2026-11-24，复核已发布工作流、既有实收、部署代码摘录及最新Console证据；本轮不查询系统、不推理、不改权限/凭据/配置。4个正式知识库应用继续Dify。本方案不是已实施替换。

## 结论：正式降退费应复用检索接口，不照抄废弃agent的tools

|对象|已证机制|迁移含义|
|---|---|---|
|正式精品/素养降退费|advanced-chat：start→code提取原因→knowledge-retrieval→一个LLM→answer|在student-data实现固定前置检索编排并复用Dify检索，不必改成模型自主tools循环|
|历史TEST【废弃】降退费|agent-chat，trace81e849b4…首轮声明dataset工具，模型给两次tool_calls，第二轮带两条tool结果；总2次LLM|可作为tools协议参考，不是正式生产降退费工作流基准|
|问题建议高中/素养|历史配置为agent-chat/function_call＋dataset|若未来迁移须真正执行工具及有界循环，不能仅配置tools；本轮不迁|

tools schema可配置，**工具执行不可靠schema完成**。函数名不是URL；必须接收tool_calls、校验工具白名单及query、执行检索、把原assistant.tool_calls及对应tool_call_id结果追加回messages，再请求模型，直到最终content。并行多工具结果不能丢失id对应；工具错误、空命中和循环上限须有显式处理。当前完整单次响应解析不能因params能塞tools就认作具备该执行器。

## 正式工作流应保留的契约

正式精品应用256995990719977472/agent256995156763347968；素养应用261424650482886656/agent261424592068814848。已保存published图及最新workflow-retrieval.json共同支持：

1. code从arg1用正则取第一个`"directReason":\s*"([^\"]+)"`（DOTALL），取全部categoryName，以`, `连接；缺失均“暂无”。产出`退费直接原因:{directReason} 退费原因分类:{categoryNames}`。迁移先复刻这个规则，不能擅自换成“完整业务query”或因JSON解析更漂亮改变旧提取结果；正则遇转义引号的边界作为原行为保留/另议。
2. 检索dataset=86233d1a-bddf-4a15-a229-c90b6a061c57；query来自[1760511521805,refundReason]；retrieval_mode=multiple，top_k=4，reranking_enable=false。gte-rerank-v2名称残留不代表运行了rerank。
3. **库级默认另算**：最新详情top_k=3、rerank=true、full_text_search，不能直接覆盖工作流top_k4/rerankfalse。Service API的search_method/阈值等需以对应工作流运行解析结果确认，当前证据不足的键不能猜成库默认或上游默认。
4. 知识片段应保留返回顺序、content、score与文档/segment溯源；不把69段全量拼入冒充top_k结果。迁移需要明确空结果/失败策略及超时预算；建议失败显式报错或受控回退，不能静默伪装无知识生成成功。
5. system完整Dify业务模板、业务query和结果结构应保留；**context存在一个已确认的兼容问题**：当前保存图context绑定result但basic prompt无context占位符。TEST与生产抽样Pod的LLM节点SHA256相同，部署代码只替换显式`{#context#}`，不自动追加。因此直接把检索片段新塞进messages是行为增强，不能称严格复刻当前旧messages。需在隔离TEST对旧图副本A（原样）、B（显式引用）以及新实现各自实收作对照，明确选“复刻旧行为”还是“修正旧未消费知识”。本任务不替owner决定正式行为变更，也不因此要求生产推理。

## 推荐配置契约（拟议，不表示已落地）

|配置|作用与验证要求|
|---|---|
|application/department→retrieval profile|按正式应用/学部绑定，禁止复用废弃agent或按名字包含TEST判断环境|
|serviceBaseUrl + credentialRef|独立Service API基址与密钥引用；不把Cookie、Bearer值放普通配置示例/日志/文档|
|datasetId|上述原86233库；复制库需单独版本、分段、索引、检索结果对等证据|
|queryExtractor=legacy_refund_reason|固定上述已发布code语义及缺失规则|
|retrieval overrides|top_k4/rerankfalse显式；其他键证实有效目标后设置。不能机械套库详情默认|
|context renderer/policy|明确旧兼容不引用或获准增强显式引用；不能由“enabled”隐式猜测|
|timeout/result budget/failure mode|与旧实际行为对照；限制大小需记录截断，不能无声丢片段|
|tool registry/iteration limit（仅agent方案）|函数名→检索profile，校验query、tool_call_id和次数；正式固定工作流无需此项|

调用形式：POST `{serviceBaseUrl}/datasets/{datasetId}/retrieve`，Authorization由credentialRef取dataset类型Bearer；body包含query和retrieval_model。公司TEST部署代码已确认retrieve/hit-testing同处理器，返回records内segment.content；Java隔离TEST已有自动检索→拼装→生成成功trace3eaabb15-c22b-48f9-bcb4-7b0fd7783511.0.3，4条segment完整进入实收。该成果支持实现路径，不证明原库正式身份、索引或context旧行为等价。

## identity与环境依赖：按最新证据，不复述过时阻塞

Console最新列表/详情均可读原86233，关联spcAm3oupwKuWRMD8UV与spczjG62GXkZ0ZSOBYS；旧403不再等同当前原库不可见。响应production标识，两个test头/Cookie优先级未证；名称TEST的30a822隔离库不是Java test-dify-open的0105aec9库。相关应用5行是跨空间重复，UUID去重3个。

Service API仍须独立身份：dataset类型token、dataset enable_api、tenant及token创建人的Teable空间与dataset空间交集。公司wraps代码有专门query权限检查；不是只拿某个chat app key就可用，也不要求query者必为dataset创建人。Console Cookie成功不能证明后端token有效；旧401只证明当次TEST token/生产目标组合无效，不能断言所有生产token不存在。需要由获授权服务身份完成对应原库受控检索验证；不绕权、不借登录Cookie作为常驻Java服务身份、不创建未授权凭据。

## 实施分界

配置能解决：已支持检索客户端的基址/dataset/profile/服务凭据引用及已核实参数。代码需负责：固定query提取、接口执行、结果映射、context策略、错误处理/可观测性；如果采用agent tools，还需多轮工具执行器。平台已有检索不意味着新链路只配tools即可。建议先完成正式降退费固定前置检索TEST闭环，再单独处理agent场景；当前四应用保留Dify，方案不触发切换。

来源：expanded-refund/binding-{1043df8c-f3d3-44b3-accd-ec2051c0c4a3,5c7ac7f6-af1d-4120-91a5-9a6485fd3d99}-published.json；exact-降退费-prod-{1,2}.json；kb-deployed-context.md；kb-service-e2e.md；comparison/kb-console-current/{workflow-retrieval,dataset-detail,related-apps,request-evidence}.json；kb-console-route-review.md。所有结论复用现有证据，无新增查询或生成。
