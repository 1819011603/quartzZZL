# context绑定但无模板引用：源码边界与TEST验证预期

2026-11-24只读本地源码与已存工作流/日志。未调用生产、未查询生产条件、未发推理、未改公共文档。

## 可交付结论

**不能仅凭context.enabled=true认定检索结果进入LLM。** 本地可见模板处理代码仅替换显式context占位符；工作流生成器甚至专门为绑定context的LLM补占位符。但当前本地工作流LLM实际执行委托给未包含的graphon，且与公司镜像版本无法对应，所以“公司已部署版本无占位符一定不注入”尚无足够源码证据。最有价值的下一步是TEST哨兵内容A/B实收对比，不需要生产调用。

## 已有工作流确切状态

已重新解析本地两份binding-*-published.json：
- 精品：binding-5c7ac7f6-af1d-4120-91a5-9a6485fd3d99-published.json。
- 素养：binding-1043df8c-f3d3-44b3-accd-ec2051c0c4a3-published.json。

两者LLM context均为enabled=true、variable_selector=[1760513220734,result]；prompt_template没有{{#context#}}，也没有直接引用1760513220734.result。绑定检索节点与模板引用是两个独立事实。当前配置本身只能证明读取意图，不能证明发送到LLM。

## 本地源码位置与含义

根目录 `/tmp/dify-src-archive` 无.git，不能取得commit；api/pyproject.toml:3为1.20.0。

1. `api/core/workflow/llm_node.py:6`导入graphon.nodes.llm.node.LLMNode，DifyLLMNode只扩展polling finalizer，不包含prompt/context渲染。不能把这个薄封装误当完整渲染实现。
2. pyproject.toml:60声明graphon==0.8.0；:83指向git rev `4fa22141774dff80e90e4dfa98ea3e6fbf0421bb`。本地未找到graphon/nodes/llm实现，因此核心工作流运行时的自动追加与否不能在此快照闭环。
3. `api/core/prompt/advanced_prompt_transform.py:166-183`，chat basic路径对raw_prompt执行replace("{{#context#}}", context or "")，另一分支只把parser.variable_keys需要的变量交给format；:264-273的_set_context_variable也以“#context#在variable_keys中”为条件。该可见转换器没有凭context非空自动追加段落；但它不是已确认的当前graphon工作流调用链，不能强套版本。
4. `api/core/workflow/generator/runner.py:2177-2193`的_ensure_llm_context_placeholder注释为“Ensure an enabled LLM context is actually present in its prompt”：已有引用则返回，无引用时向末条user追加，或者新建user {{#context#}}。:2157附近在合并多检索节点的生成修复阶段调用它。**这是工作流生成/修复逻辑，不是每次执行所有已发布图都会自动调用的运行时保障。** 不可用它断言当前存量图运行时会自动补。
5. `api/core/workflow/node_factory.py:793-820`按context selector取得检索结果用于segment附件权限检查；这只证明附件访问校验读取了context，不能证明文本已拼进prompt。

## 与实际部署的关系

既有prod原始日志image_name显示公司镜像`acr.baijia.com/uqun/dify-api:release-81f07d7b-20261119090929`；plugin-daemon为release-594155de-20260817102236。只读提取镜像标签，未访问生产。

没有证据把公司81f07d7b提交映射到上述无git的1.20.0快照或graphon rev；plugin-daemon也不是工作流prompt渲染的充分版本证据。因此以上是上游/本地版本的实现线索，非公司生产实现的定论。不混用旧agent工具检索机制作为工作流context注入证明。

## 最小TEST样例（交主Worker执行，本任务未运行）

使用独立TEST工作流副本，保留同版LLM节点；code节点输出确定性Array[Object] `result`，如：

```json
[{"content":"KB_SENTINEL_20261124_CONTEXT_ONLY_7QX","metadata":{"_source":"knowledge","position":1,"dataset_id":"test-context-fixture","document_id":"test-document","document_name":"context-fixture"},"title":"context-fixture"}]
```

LLM context.enabled=true，variable_selector=[codeNodeId,result]。用代码结果先测试渲染，不引入向量检索随机性；实际知识库检索可由主Worker其他TEST验证承接。

- A：system="仅回答OK。"，无context或result引用。
- B：其余完全相同，system="仅回答OK。\n<context>{{#context#}}</context>"。
- 可选C：context关闭，prompt直接引用{{#codeNodeId.result#}}，只用于区分通用变量替换；与A/B不是同一渲染机制。

查看TEST LiteLLM实际Chat_completion request messages中完整哨兵是否存在、角色及包装；不要用回答是否提到哨兵来判断输入（模型可忽略输入）。预期假设：A不含、B含；**这是待测预期而非已验证结果**。若A也含，记录自动追加的真实角色和文本，这将推翻“不自动注入”假设；若B也不含，先检查selector值类型、模板语法及节点实际执行结果，不据此说context无用。

需要的最小缺口：同公司TEST Dify版本的A/B实收，或公司部署81f07d7b对应LLM节点源码。当前独立任务按只读范围交付到此，不扩展生产调用、不重复业务运行。
