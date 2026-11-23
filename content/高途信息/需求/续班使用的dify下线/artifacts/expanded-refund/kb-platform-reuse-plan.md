# 知识库替代方案：复用Dify检索，不只模拟tools

结论：可以评估让student-data接管编排和生成、Dify只提供检索。无需默认重建知识库、索引或数据同步；但只把tools schema拼给模型不会执行检索。现有4个应用保留Dify的决定不变，本轮没有实施替换。

## 平台检索API依据与条件

Dify官方提供POST {Service API base}/datasets/{dataset_id}/retrieve，使用知识库API key（不是chat应用key），请求query并可传retrieval_model，响应records含score和segment.content。接口返回检索片段而非最终建议。官方依据：https://docs.dify.ai/en/api-reference/knowledge-bases/retrieve-chunks-from-a-knowledge-base-test-retrieval ，权限说明：https://docs.dify.ai/en/api-reference/guides/knowledge-base-api 。

已有本地源码快照也注册了该Service API（/tmp/dify-src-archive/api/controllers/service_api/dataset/hit_testing.py:28），经DatasetApiResource校验并调用perform_hit_testing；快照未绑定公司当前部署版本，不能据此宣称公司接口已经实测可用。此前Console /retrieve和/search的404不是这个Service API的能力验证。

部署前仍须确认公司实例Service API base/网关路由、当前版本、知识库API key及目标dataset授权/API开关、embedding和检索资源可用性。现有Console Cookie能读取分段，不等于后端具有服务凭证；本轮未创建key或发起检索、生产推理。官方API能力已确认，公司服务账号接通及返回结果对等未验证。检索可能调用embedding/rerank并产生查询记录，后续需在获准测试接入时验证。

## 推荐落点

生产降退费：保留原代码提取规则与学部映射→按原query和检索参数调用平台检索→明确组装命中上下文和完整业务指令→一次网关LLM生成。原则上不需要tools。先核实旧生产context是否真正注入；如旧侧没注入，新增上下文是行为增强，不能冒称纯迁移。保留top_k、排序、阈值、去重及空命中/超时处理；不把69段全塞进prompt冒充检索。

问题建议agent：保留模型选query的行为时，需要tools声明、tool_calls解析、实际平台检索、assistant/tool消息回灌及有界循环完整执行器。校验函数白名单和参数、匹配tool_call_id、限制次数和上下文长度。现有单次网关迁移路径没有这个完整执行器，不能只加tools字段就交付。也可研究固定前置检索，但会改变模型自主选query/重复检索行为，不能未经验证称等价。

下列API请求是方案示意，不是已执行请求；retrieval_model具体值应从各目标已发布配置映射，不套用TEST废弃agent参数：
```json
{"query":"退费直接原因:<提取值> 退费原因分类:<提取值>","retrieval_model":{"top_k":4,"reranking_enable":false}}
```
响应消费结构示意：
```json
{"records":[{"score":0.8,"segment":{"content":"<命中话术片段>"}}]}
```

## 证据分档与范围

已验证：既有TEST废弃应用真实tool请求/结果回灌、生产已发布工作流图、dataset分段存在；官方独立检索接口存在。推断未验证：公司部署可直接用服务凭证接通同一检索、生产context最终注入方式及结果对等。没做：知识库替换实施、生产推理、路由配置修改。本轮只完成机制调查、方案和文档同步。

以下保留实际脱敏请求节选及生产配置依据，严格区分实收与配置，不用TEST多轮外推生产。

# 知识库真实拼装机制：现有证据复核

2026-11-24仅离线复核2026-11-23保存的证据；未刷新平台配置、未发推理、未改变保留Dify路由。本报告优先于旧报告中错误外推的说法。

## 结论

可以在新链路实现tools协议并复用Dify检索，但**只声明tools不够**：模型输出的是函数名和查询参数，调用方仍须实际检索并带tool_call_id回传内容，再调用模型。工具名称本身不是URL，不会自动连接Dify。

生产精品/素养降退费是另一种机制：代码先确定检索query，再检索，再一个LLM节点生成；不用为了迁移强行改为工具多轮。问题建议高中/素养是agent机制，可由模型发起检索。平台继续存在意味着可以考虑保留Dify的知识存储/索引/检索，不意味着当前应用凭据就具备dataset检索权限。

## A. TEST废弃降退费：真实LiteLLM请求与回灌

这是TEST业务调用，Dify下游落在PROD LiteLLM，**不是生产业务应用实测**。trace `81e849b4-d461-4fd0-910a-154368d68bc0.0.3`，TEST agent `255743632420648960`绑定【废弃】降退费服务建议 `c76ff517-b2a6-4476-8171-92af9364e344`。

第一轮实际字段摘录（省略正文与user身份；tools来自实收，未自行构造）：
```json
{
  "model": "deepseek/DeepSeek-R1-250528",
  "stream": true,
  "tool_choice": "auto",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "dataset_86233d1a_bddf_4a15_a229_c90b6a061c57",
        "description": "降退费服务建议话术库，根据根因分类匹配对应的服务建议话术",
        "parameters": {
          "properties": {
            "query": {
              "description": "Query for the dataset to be used to retrieve the dataset.",
              "type": "string"
            }
          },
          "required": [
            "query"
          ],
          "type": "object"
        }
      }
    }
  ],
  "messages": [
    {
      "role": "system",
      "content": "[省略既有system正文；非新增占位字段]"
    },
    {
      "role": "user",
      "content": "[省略既有user正文；非新增占位字段]"
    }
  ]
}
```
原user.content是包含role/system和role/user字样的序列化文本；它仍是外层user消息，不会自动变成额外system角色。

首轮响应finish_reason=tool_calls，一次返回两个查询；第二轮在原system/user之后实际追加如下消息（工具内容仅节选，不是完整请求）：
```json
[
  {
    "role": "assistant",
    "content": "",
    "tool_calls": [
      {
        "id": "call_00_ql1i01jf80olhguk1a2gk29r",
        "type": "function",
        "function": {
          "name": "dataset_86233d1a_bddf_4a15_a229_c90b6a061c57",
          "arguments": "{\"query\": \"孩子觉得课程节奏快、互动少，作业正确率下降，考虑退费，NPS低，作业反馈慢、个性化不足，如何干预挽单\"}"
        }
      },
      {
        "id": "call_01_dmh3s0u128o85e78xqjkg64h",
        "type": "function",
        "function": {
          "name": "dataset_86233d1a_bddf_4a15_a229_c90b6a061c57",
          "arguments": "{\"query\": \"数学课程体验差，直播听懂课后不会做，需要增加答疑和针对性练习，退费犹豫干预建议\"}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "content": "话术一\nxx妈妈您好，我是孩子的二讲老师，刚才看到您提交了退费申请，心里还挺着急的，赶紧跟您打个电话聊聊。其实特别能理解您的顾虑——这两个月二讲老师确实调整了两次，孩子刚适应张老师的节奏，又要重新熟悉[本报告截断，原文见证据文件]",
    "tool_call_id": "call_00_ql1i01jf80olhguk1a2gk29r"
  },
  {
    "role": "tool",
    "content": "序号: 26;一级分类: 课程适配类;二极分类: 分层教学缺失;建议话术: XX妈妈/爸爸，我完全理解您的顾虑。您希望孩子能在适合他水平的课程里学习，这对学习效果确实至关重要。您能具体说说孩子最近在我[本报告截断，原文见证据文件]",
    "tool_call_id": "call_01_dmh3s0u128o85e78xqjkg64h"
  }
]
```
第二轮完整roles为system,user,assistant,tool,tool，工具正文长度1363/1152字符；不是把tools schema换成检索正文，也不是复制一句“使用知识库”。两个查询各自有工具结果，调用id一一匹配。首轮prompt/completion tokens=1424/299，第二轮3068/606，第二轮finish_reason=stop。该样本共两次LLM请求，但首轮包含两次工具调用，不能混为“两次检索即两次LLM”。

证据：`exact-降退费-prod-1.json`、`exact-降退费-prod-2.json`；原始响应及usage在`prod-trace-service-main.log`（仅service=litellm记录有效，排除日志查询网关的嵌套回显）。

## B. 生产精品/素养降退费：已发布工作流配置，不是实收消息

精品application/agent：256995990719977472 / 256995156763347968；素养：261424650482886656 / 261424592068814848。绑定与已发布Apollo学部映射见`deprecated-binding.md`。两个已发布图都是start→code→knowledge-retrieval→llm→answer，仅一个LLM节点。

code从sys.query正则读取directReason与全部categoryName，缺失置“暂无”，形成 `退费直接原因:{directReason} 退费原因分类:{categoryNames}`。检索节点query_variable_selector=[1760511521805,refundReason]；dataset_ids=[86233d1a-bddf-4a15-a229-c90b6a061c57]；retrieval_mode=multiple；top_k=4；reranking_enable=false。gte-rerank-v2仅配置残留，不代表实际rerank。

LLM context.enabled=true，variable_selector=[1760513220734,result]；prompt_template仅一个system模板，末尾包含sys.query。精品模型R1-250528/temp0.7；素养v4-flash-0731/temp0.7/enable_thinking=true。

**证据边界**：这里证实“检索节点及其result绑定到LLM context”，没有生产工作流该次LiteLLM实收。两个保存的prompt_template都不含显式#context#或检索节点变量占位符。不能仅凭context.enabled=true就断言最终插入了多少话术或以哪个角色/包装插入；Dify运行时是否自动加入context、是否必须模板引用，仍须以对应版本实现或真实工作流实收确认。因此本报告不伪造生产messages。此前把context配置直接当作已观测最终注入的说法应限定为配置意图。

证据：`binding-5c7ac7f6-af1d-4120-91a5-9a6485fd3d99-published.json`（version 2025-12-03 14:09:25.978047）与`binding-1043df8c-f3d3-44b3-accd-ec2051c0c4a3-published.json`（2026-09-21 06:33:31.703225）。

## C. 高中/素养问题建议：历史机制证据

复用`../dify-kb-eval.md`历史归档：agent-chat、strategy=function_call；高中dataset=5b040e52-8041-48af-b7d3-acefc14bc130，素养=a195df23-ba87-4ecb-b9f3-7d1c3a5a9b22。归档引用DatasetRetrieverTool/base_agent_runner/fc_agent_runner：Dify注册dataset工具，模型选择query，Dify执行检索，再回灌结果。其原理与A同类，但本次没有这两个应用独立的实收请求，不把A的dataset工具名称、两次LLM次数或检索参数套给它们。是否使用rerank及top_k须各自当前配置证明；历史“结构化过滤等价向量检索”的建议不是等价验证。

## 复用Dify平台的可行性与仍待确认项

实现agent方式需要：传tools→解析assistant.tool_calls→执行Dify检索→保持原消息并追加assistant/tool→再调用LLM直至文本终结；设置有界迭代、工具失败处理与结果大小预算。工作流方式可在调用LLM前用相同code规则取query、调用检索、明确注入命中片段，保留单LLM生成。两者都继续依赖Dify平台检索能力，不需要从零重建向量库，但这不是本轮获准实施。

已经取得dataset全部69段，来源为Teable导入，数据存在；`dataset-document-detail.raw`记录分段双换行/max_tokens1024/overlap50。69段全量内联并不等于top_k检索；配置分段token数也不能代替运行时实际token统计。已有Console文档/分段读取成功、dataset详情403、Teable直读403；此前猜测Console /retrieve与/search为404仅说明那两个路径不通，**不能证明Dify平台无检索API**。服务端检索API、授权scope、当前dataset搜索方式/阈值与结果格式尚未验证，不应要求owner重建已有库或声称已经可以直接接通。

四个知识库场景仍保持Dify；本报告只提供机制与方案边界。
