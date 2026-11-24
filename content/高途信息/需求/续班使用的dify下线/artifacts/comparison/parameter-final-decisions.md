# response_format / enable_thinking 最终裁决

2026-11-24，只读56b53f3c代码与既有归档。本子任务不发布配置、不业务调用；仅下列定向删除交主Worker执行。未重开max_tokens、stream、user或stop。

| 场景与TEST对象 | 旧有效证据 | 新值与业务依据 | 本轮裁决 |
|---|---|---|---|
| 画像 application255107395528688640；摘要255551371814636544；共享agent255107338300556288 | pairs两场景旧request均省略response_format；未取得供应商有效默认为某个值的证据 | 新json_object。两场景原system明确要求结构化字段/JSON输出，结果对象分别RenewalAiUserPortraitResult、RenewalAiCommSummaryResult。没有“删除该参数已失败”的回归证据；JSON输出契约不等于该参数必需 | **保留具体JSON约束差异**。不声称参数一致，也不声称业务必须依赖json_object本身。现有目标只证明旧请求省略，尚未证明删后有效约束等价；不以输入一致为由移除输出约束。若后续专门要求连此约束都撤销，可单独验证，当前不新增该门槛 |
| SOP V2 application256327049255322624；agent256325360053917696 | 旧省略response_format | 新json_object；AiSopAnalysisGenerator.java:272-276清理后JSON.parseObject为AiSopAnalysisResultValueObject。原SOP prompt亦规定JSON | **保留具体JSON约束差异**，非旧默认等价结论。无删键失败实证，但当前解析有结构化要求；不动已有一致SOP输入 |
| 分层 application262173928596712448；agent262172718139452416 | 旧省略response_format，旧结果原因文本 | 新text；此前json_object使完整JSON作为原因落值，RenewalLiftReasonHandle只清理围栏/think，不抽JSON字段。tier-fix.md中dabc87b7同入口修复验证文本 | **保留text**，明确修复过真实格式冲突。不得回退json_object，也不为字面省略再撤销已验证约束 |
| 根因 application255743373455931392；agent255743333766281216 | pairs“退费根因”旧请求省略enable_thinking及thinking | 新params.enable_thinking=true。Java仅任意透传；旧业务不要求该非标准键，未找到新增键修复回归或消费依赖。目标安全快照defaultParams={} | **有依据可删除params.enable_thinking**，以匹配旧请求省略；删除而非false，也不要替换thinking.enabled。主Worker只改此agent此键，验证messages不变及下游字段确实消失。有效思考模式仍未知，不能承诺删除即禁用或token不变 |
| 旅程 application255733517892204544；agent255733061835044864 | pairs“旅程”旧请求省略enable_thinking及thinking | 新params.enable_thinking=true；同上，没有要求该键的契约。旅程system严格对齐成果保持 | **有依据可删除params.enable_thinking**；精确同上，不动system/user、模型或其它参数 |
| 素养NPS agent7530633600362872933 | 旧thinking.type=enabled，是明确目标，不是enable_thinking | 新已发布thinking.enabled并实收42399367-6e72-4a2f-839c-e42f486b0da2.0.3，messages不变 | **保留已完成对齐**，不混同两种字段，不重验 |
| 画像/摘要、分层 thinking.disabled | 旧Doubao1.5重定向force disabled；分层曾出现新reasoning_tokens>0并已修正 | 显式disabled复制旧生效规则 | **保留**，不能因旧入口省略thinking而删除直达目标所需显式值 |

## 可执行变更清单（仅两项）

Apollo TEST/application `ai.agent.accessor.override.map`：从agent255743333766281216和255733061835044864的params删除enable_thinking。实施时先读最新发布值并合并，避免覆盖另一子任务正在处理的stop及已发布素养NPS thinking。此报告不是已执行回执。

## 证据强度

省略是确定的**请求层目标**，不是确定的**供应商有效默认**。对enable_thinking删除可确切消除新侧额外字段，暂无契约冲突证据；其是否被下游忽略/映射以及默认推理强度仍未证实，删除后不能宣称思考参数语义全部等价。response_format有明确输出约束，分层另有真实回归修复，故分类保留并在场景表直写差异，不笼统写“其它参数均对齐”。

来源：comparison/pairs.json、format-apollo-before.json、parameter-defaults-test-safe.json；expanded-renewal/tier-fix.md、thinking-followup.md；AiSopAnalysisGenerator.java:272-276；两类结果DTO及原system。未声称未找到依赖等于全仓不存在依赖，以上按本次链路范围裁决。
