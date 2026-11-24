# TEST知识库替换契约核对

核对范围：本地已落盘的Console配置、Dify工作流、Service API与TEST E2E证据；只读，不调用业务、不读取秘密、不改配置。

## 四个正式知识库业务路由

四个目标不是Console去重后的应用数量，而是Apollo/业务映射中的四个 `ai_agent`：

| 业务路由 | agent号 | Dify绑定/形态 | 已有证据与契约 |
|---|---:|---|---|
| 问题建议-高中 | 256918735665808384 | 旧Dify agent-chat；知识库工具链 | `expanded-scope/scope-reconciliation.md`、`expanded-renewal/source-migration-sheet.json`；本期保留Dify，不把TEST废弃agent样本当正式基线 |
| 问题建议-素养 | 256918818763359232 | 旧Dify agent-chat；知识库工具链 | 同上；旧模型映射为`doubao/Doubao-Seed-1-6`，不能直接套高中prompt/模型 |
| 降退费服务建议-精品班 | 256995156763347968（application 256995990719977472） | 已发布Dify advanced-chat workflow，绑定`5c7ac7f6-af1d-4120-91a5-9a6485fd3d99`；start→code→knowledge-retrieval→llm→answer | `expanded-refund/deprecated-binding.md`、`binding-5c7ac7f6-af1d-4120-91a5-9a6485fd3d99-app.json`、`kb-console-current/workflow-retrieval.json`；dataset=86233，query变量=refundReason，top_k=4，reranking=false |
| 降退费服务建议-素养班 | 261424592068814848（application 261424650482886656） | 已发布Dify advanced-chat workflow，绑定`1043df8c-f3d3-44b3-accd-ec2051c0c4a3`；同为单LLM工作流 | `expanded-refund/deprecated-binding.md`、`binding-1043df8c-f3d3-44b3-accd-ec2051c0c4a3-app.json`；原库绑定事实有证，但素养独立query/top_k/rerank正文尚未落盘，不能套精品参数 |

补充：`related-apps.json`的5行是空间/应用列表（跨空间重复），只覆盖精品/素养降退费工作流与废弃agent，不能替代上述四条业务映射。`format-application-map.md`明确另有两个“问题建议”agent，且四个知识库agent被排除在13个普通prompt迁移应用之外。

## 已证的替换最小结构

1. 入口保留原业务query/字段抽取。
2. 调用Dify retrieve，明确传入dataset、query及原检索参数；当前已证工作流为`top_k=4`、`reranking=false`，不得使用库默认值覆盖。
3. 将命中的`segment.content`按确定顺序拼入LLM messages；`kb-deployed-context.md`明确Dify LLM节点不会因存在context自动追加消息，新链路必须显式拼装。
4. 保留原system/user消息、输出schema、模型映射和stream等已确认参数；随机生成结果不作逐字相等判据，比较messages、参数、检索片段和结构化字段。
5. 若目标是agent形态，必须实现完整工具循环：白名单参数校验、tool_call_id匹配、实际检索、assistant/tool消息回灌、循环次数及上下文长度限制。仅给模型增加tools字段不等价（依据`kb-platform-reuse-plan.md`）。
6. 记录下游LiteLLM trace，绑定完整请求body、检索响应和最终入口响应；区分“固定前置检索工作流”和“模型自主选query agent”。

## 已可复用的TEST证据

- `expanded-refund/kb-test-retrieval/real-test-retrieve.json`：隔离TEST Service API真实返回4条片段。
- `expanded-refund/kb-service-e2e.md`：Java检索→上下文拼装→TEST生成成功，trace `3eaabb15-c22b-48f9-bcb4-7b0fd7783511.0.3`；system 1390字、完整业务query与4条segment逐条包含已断言。
- `expanded-refund/kb-e2e-litellm-fixed.json`、`kb-e2e-input-assertions.json`：下游实收body及断言。
- `comparison/kb-console-current/workflow-retrieval.json`：正式工作流检索参数和query变量。
- `expanded-refund/kb-deployed-context.md`：context不会自动进入messages、Service API鉴权/空间校验链。

## 当前差异与最小补证

| 差异/缺口 | 影响 |
|---|---|
| 正式库与TEST隔离库不是同一dataset，分段/索引/权限不同 | TEST检索成功不能宣称正式四应用对等 |
| 高中工作流已有检索参数，素养工作流未落盘同等细节 | 素养不能直接套高中契约 |
| 废弃agent完整工具循环未形成当前版本证据 | 不能把固定检索替换成agent或反向宣称等价 |
| 原4个业务路由的应用级system/user、query抽取、输出schema未全部绑定到同一份TEST实收 | 替换实验必须逐应用保存旧Dify/新入口messages与LiteLLM trace |
| 正式生产dataset key已由`comparison/kb-credential-current.md`记录并完成原库4片段受控检索（trace `cbc61996-27a1-4263-b504-dea8a8ef1e14.0.1`） | 这只证明Service认证/检索可用，不证明四业务路由已迁移或TEST Java已接正式库；密钥不写报告 |

最小验证结构：每个目标应用保存`old-dify`和`new-test`的完整messages、检索请求/4条命中片段、LiteLLM请求参数、入口trace及结构化响应；比较顺序、字段和参数，允许模型自然输出差异。当前已完成的TEST隔离库E2E可作为方法模板，不能替代四应用逐场景实收。
