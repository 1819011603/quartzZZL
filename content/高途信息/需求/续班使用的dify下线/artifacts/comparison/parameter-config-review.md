# 模型与参数配置入口复核

2026-11-24，只读代码56b53f3c及归档；不改配置、不业务调用。messages一致不代表全部模型参数相等。

## 生效层和可实施项

配置入口为Apollo `ai.agent.accessor.override.map`（键是**agent编号**，与格式配置的application编号不同）。model字段覆盖command.modelName；params追加请求参数，但model/max_tokens/messages三个键被Java剔除。以下建议尚未由本子任务实施。

| 参数 | 当前证据/生效层 | 配置建议及限制 |
|---|---|---|
| model | Java优先override.model，其次command.modelName，最后llm.gateway.default-model（代码兜底claude-sonnet-5）。旧入口名可由caller特定重定向改变：历史日志Doubao1.5→doubao-seed-2-0-lite-260428，DeepSeek-R1→deepseek-flash。 | 使用已核实的逻辑目标model，而非为字符串相同直接填旧别名。TEST当前目标有多个modelParam，不能说每次供应商endpoint相同；SOP旧Seed1.6、新Seed2.0是否同路由须独立证据，不能套用1.5映射。 |
| max_tokens | Java command.maxTokens非null优先，否则llm.gateway.default-max-tokens（代码4096，实收8192）；params同名键不生效。旧实收省略。 | 当前不能按agent配置省略；要对齐省略或按agent设置上限需最小代码支持（显式省略策略/独立字段），不能用0或params:null冒充。全局调默认会影响其他应用，不建议。旧省略不等于无限或8192。 |
| temperature / top_p | Java没有额外默认，可在params传数值；目标控制面defaultParams={}。旧大多数样本省略，历史素养建议0.7但该知识库不在迁移范围。 | 对旧实际显式值按应用设置；旧省略时不猜供应商默认0/1/0.7。多部署及供应商默认还未逐一核实。 |
| stop | 旧样本省略，新实收[]；LlmGatewayRequest本身无stop，来源是extraParams或后续网关层，需结合已回读Apollo逐项定位。Dify插件调用把stop单独传入。 | 若当前params含stop:[]可移除来对齐请求字段，是否下游再注入看实收；空列表通常无停止序列，但不能称字节一致。 |
| response_format | params可设；新画像/摘要/SOP部分json_object，分层修正为text，旧多省略。 | 可以删除对应params键以请求省略；分层不能盲恢复json_object，其与自然语言输出已证冲突。保持text或确认删键后的下游行为，不能以“旧没传”解释为旧强制JSON。 |
| thinking | Doubao旧入口在TEST控制面重定向强制注入{type:disabled}；目标部署defaultParams为空。素养NPS旧请求显式enabled，新请求省略。 | 直达Doubao目标应显式params.thinking={type:disabled}以复刻旧有效行为，不回退既有关闭思考修正。素养NPS可按其agent设置params.thinking={type:enabled}，再验证实际路由支持及实收；省略不能当enabled等价。 |
| enable_thinking | 根因/旅程新样本出现true，旧对应样本未显式传；Java作为任意params透传。 | 这是供应商相关字段，非通用OpenAI字段；不能假设与thinking.type等价。不机械将所有true转换enabled；先据旧有效行为和选定路由确认。若目标严格复刻旧省略可移除此键，并检查是否有下游注入/转换。 |
| stream | 旧实收true，新未显式传；Java同步获取response.body后JSON.parseObject完整LlmGatewayResponse。 | **不能仅配置true**：虽params透传允许，但SSE会使完整JSON解析不兼容。要协议对齐须增加流式读取、聚合delta、usage/finish_reason/中断处理及测试；本轮只读未改。保留非流式应明确协议差异，非messages差异。 |
| user | 旧Dify请求含user，新Java请求DTO不设user；成本归属走x-tech-ai-user-id头，来自command.costUserId/runUser邮箱或llm.gateway.fallback-user。 | params技术上可加user，但静态复制旧用户标识不正确；user与计费头不是同一语义。若需动态对齐需明确身份映射并改代码，不能硬编码旧trace用户。 |

## max_tokens省略究竟发生在哪层

本次可确认：旧Chat_completion request到达LiteLLM时未含max_tokens，新侧Java必定选command或默认值并写入。TEST安全控制面目标部署defaultParams={}，没有该处注入8192的证据；但这不能排除LiteLLM适配器、代理下游或供应商自己的默认。

本地Dify源码api/core/plugin/impl/model.py:172起将model_parameters/stop/stream交给plugin daemon；此文件不删除max_tokens。api/core/llm_generator/llm_generator.py:47的_normalize_completion_params会删除非正token上限，但它是另一辅助调用路径，**未证明本次旧应用走它，不能用此函数宣称旧参数被删除**。本地归档未找到对应运行provider插件处理证据，因此“Dify应用未配置/插件先删/下游补默认”尚不能唯一定位。不得将省略当作已知有效上限，也不应为追字面一致盲设max_tokens=0。

## 已验证与未验证

- 已验证（归档/代码）：上述Java优先级和保护键；旧重定向历史日志；TEST安全控制面Doubao1.5强制disabled与目标defaultParams={}；stream解析协议冲突。
- 可配置待实施：逐agent model、temperature/top_p/stop/response_format/thinking及移除不适用enable_thinking；须按场景确认，不全局覆盖。
- 需代码才完整支持：按应用省略/覆盖max_tokens；stream=true SSE响应；动态user映射。
- 未验证：当前每个请求最终供应商endpoint、供应商缺省参数、旧provider插件是否删除max_tokens。模型返回名及入口别名不足以证明全链路逐字段相等。

来源：AiApplicationExecutor.buildCallOption；LlmGatewayAccessor.query/buildRequestBody/buildHeaders/convertAndValidate；LlmGatewayRequest；comparison/pairs.json、format-runs/56b53f3c5；parameter-defaults-test-safe.json；trace-recheck-20261123/model-redirect-evidence.json与dify-thinking-redirect.json。未读取或输出/tmp/dify-param-control-test.json敏感原文。
