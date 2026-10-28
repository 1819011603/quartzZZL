---
title: 续班使用的dify下线 · 交接给其他 AI 执行的 prod 待办
tags: [需求, 交接]
---

# 交接：prod 上线执行清单（续班/退费 Dify 下线 → LLM 网关）

> 交接对象：另一个 AI/同学。**test 已完成**，本文只列 **prod 待办**，按序执行。
> 详细背景：[`README.md`](README.md) · 逐应用对比 [`artifacts/compare-detail.md`](artifacts/compare-detail.md) · 模型映射 [`artifacts/llm-gateway-model-mapping.md`](artifacts/llm-gateway-model-mapping.md) · 知识库评估 [`artifacts/dify-kb-eval.md`](artifacts/dify-kb-eval.md) · 提示词归档 [`artifacts/dify-refund-prompts/`](artifacts/dify-refund-prompts/)

## 0. 一句话
把续班/退费共 **15 个 Dify 应用**（续班 5 + 退费 10）切到公司 LLM 网关（caller `gps-ai`）；用 Apollo `ai.agent.accessor.override.map` 按应用控制，可回退。**2 个有知识库的应用（生成沟通建议-高中/素养）保留 Dify，不迁**——原因见第 5 节。

## 1. 已定结论（不要改）
- 切换粒度：`ai_agent.number`；开关走 **Apollo `ai.agent.accessor.override.map`**（`{name, platformType:2, model, params}`）。
- 模型：续班 `doubao-seed-2-0-lite-260428`；**退费 `deepseek-flash`**（= 网关控制面 `redirectToModelCode` 官方接管值）。
- 返回格式：续班 doubao **带** `response_format={"type":"json_object"}`；**退费不带**。
- 参数（`params`）按应用对齐 Dify 的 `completion_params`：退费根因/旅程/降退费 `enable_thinking:true`；各应用 `stop:[]`；素养服务建议加 `temperature:0.7`。
- **退费提示词**用新列 `ai_application.gateway_core_prompt`（应用级，仅 `platform_type=2` 时作 system 提示词）；老链路(Dify)仍读 `prompt_config.core_prompt` 保持原样（可回退、老链路零变化）。
- **不要对齐 Dify 的消息结构**（试过、无收益、已回退），保持：`system=完整指令`、`user=数据`。
- 隐藏能力已扫：除知识库外无其它（tools 全空、敏感词/注释/gt_configs 均关）。

## 2. prod 待办（按序）

### T-11a　DDL 工单：给 prod `ai_application` 加列
```sql
ALTER TABLE ai_application ADD COLUMN gateway_core_prompt text NULL
  COMMENT '新链路(网关)system提示词，仅platform_type=2时使用' AFTER prompt_config_version_number;
```
（test 已直连加过；prod 走 DDL 工单）
> **改到 `ai_application`（应用级）**：每个 agent 恰好 1 个 app，可逐应用给不同提示词；`prompt_config` 那版已废弃（prod 上 10 个退费应用只落到 3 个共享 pc，挂 pc 无法按应用区分）。
> 代码读取：`AiApplication`/`AiApplicationBO.gatewayCorePrompt`、`AiApplicationMapper.xml`、`AiApplicationExecutor`（主路径，`platformType==2` 时取，为空回落 `prompt_config.core_prompt`）。

### T-11b　迁 prod 退费提示词到 `ai_application.gateway_core_prompt`
按 **`ai_application.number`** 逐应用写入（每应用一条）。内容取自 [`artifacts/dify-refund-prompts/`](artifacts/dify-refund-prompts/)；**按学部取对应文件**（根因/旅程/课程体验 两学部**同文**；**NPS 素养≠精品**；降退费两学部近乎相同）。

| 应用（ai_agent name） | ai_agent.number | ai_application.number | 提示词文件 |
|-|-|-|-|
| 退费根因分析(素养学部) | 261424983727715328 | 261425035474903040 | 素养退费根因.pre_prompt.txt |
| 退费根因分析(精品班学部) | 256995079971961856 | 256995936629163008 | 精品退费根因.pre_prompt.txt |
| 退费NPS分析(素养学部) | 261424755557579776 | 261424803504732160 | 素养课程NPS.pre_prompt.txt |
| 退费NPS分析(精品班学部) | 256995228385317888 | 256996044560210944 | 精品课程NPS.pre_prompt.txt |
| 退费旅程分析(素养学部) | 261425291830803456 | 261425336093323264 | 素养退费旅程.pre_prompt.txt |
| 退费旅程分析(精品班学部) | 256994902246699008 | 256995767298823168 | 精品退费旅程.pre_prompt.txt |
| 退费课程体验分析(素养学部) | 261425172233344000 | 261425205028651008 | 素养课程体验.pre_prompt.txt |
| 退费课程体验分析(精品班学部) | 256994989452607488 | 256995860148134912 | 精品课程体验.pre_prompt.txt |
| 降退费服务建议（素养学部） | 261424592068814848 | 261424650482886656 | 素养降退费工作流.nodes.txt |
| 降退费服务建议（精品班学部） | 256995156763347968 | 256995990719977472 | 精品降退费工作流.nodes.txt |

> 取 `ai_application.number`：`select ap.number from ees_data.ai_application ap where ap.ai_agent_number=<agent_num>`（prod 每 agent 恰 1 个 app）。
> **写入要求（关键）**：只写 `ai_application.gateway_core_prompt`，**`prompt_config.core_prompt` 不动**；**不走 `updatePromptConfig` 接口**（提示词不在 pc 上，无 afterProcessor 回传问题）。prod 只读连接 `user_dynamic_rw`（Apollo PROD `jdbc-mysql` namespace）。

### T-12　gps-ai prod 路由（工单）
在 AI 平台给 caller `gps-ai`（env=prod）加两条路由：
- `doubao-seed-2-0-lite-260428`（"Doubao-Seed-2.0-lite 260428"）
- **`deepseek-flash`**（"DeepSeek-V4.1-Flash"）
> ⚠️ 之前提的工单 **5547 是 `deepseek-v4.1-flash-1017`，要作废/改成 `deepseek-flash`**。
> test 已加（doubao id 37268、deepseek-flash id 37277）。CLI：`llm-gateway-admin` skill 的 `gateway_admin.py save`。

### T-13　代码发布
分支 `feature-xuban-dify-offline`（MR `!1796`，合 `release`）→ 发镜像。
> 顺序：**T-11a → T-11b → T-12 → T-13 → T-09**；否则发版后退费会缺提示词/路由。

### T-09　发正式 Apollo 配置（**代码上线后**才发）
当前 prod `ai.agent.accessor.override.map` = `{}`（全走老链路，零影响）。上线后改为下面 15 条并发布：
```json
{"256917438512284672":{"name":"用户画像","platformType":2,"model":"doubao-seed-2-0-lite-260428","params":{"response_format":{"type":"json_object"},"stop":[]}},"257085994022484992":{"name":"沟通摘要","platformType":2,"model":"doubao-seed-2-0-lite-260428","params":{"response_format":{"type":"json_object"},"stop":[]}},"256919048417231872":{"name":"服务SOP分析","platformType":2,"model":"doubao-seed-2-0-lite-260428","params":{"response_format":{"type":"json_object"},"stop":[]}},"263057785613229056":{"name":"续班分层原因分析-高中","platformType":2,"model":"doubao-seed-2-0-lite-260428","params":{"response_format":{"type":"json_object"},"stop":[]}},"263080101791455232":{"name":"续班分层原因分析-素养","platformType":2,"model":"doubao-seed-2-0-lite-260428","params":{"response_format":{"type":"json_object"},"stop":[]}},"261424983727715328":{"name":"退费根因分析(素养学部)","platformType":2,"model":"deepseek-flash","params":{"enable_thinking":true,"stop":[]}},"256995079971961856":{"name":"退费根因分析(精品班学部)","platformType":2,"model":"deepseek-flash","params":{"enable_thinking":true,"stop":[]}},"261424755557579776":{"name":"退费NPS分析(素养学部)","platformType":2,"model":"deepseek-flash","params":{"stop":[]}},"256995228385317888":{"name":"退费NPS分析(精品班学部)","platformType":2,"model":"deepseek-flash","params":{"stop":[]}},"261425291830803456":{"name":"退费旅程分析(素养学部)","platformType":2,"model":"deepseek-flash","params":{"enable_thinking":true,"stop":[]}},"256994902246699008":{"name":"退费旅程分析(精品班学部)","platformType":2,"model":"deepseek-flash","params":{"enable_thinking":true,"stop":[]}},"261425172233344000":{"name":"退费课程体验分析(素养学部)","platformType":2,"model":"deepseek-flash","params":{"stop":[]}},"256994989452607488":{"name":"退费课程体验分析(精品班学部)","platformType":2,"model":"deepseek-flash","params":{"stop":[]}},"261424592068814848":{"name":"降退费服务建议（素养学部）","platformType":2,"model":"deepseek-flash","params":{"enable_thinking":true,"stop":[]}},"256995156763347968":{"name":"降退费服务建议（精品班学部）","platformType":2,"model":"deepseek-flash","params":{"enable_thinking":true,"stop":[]}}}
```

### T-13b　发布后逐个复验 + 回填
用对比接口逐个 `compare`（见第 4 节），核对结构/关键字段；回填迁移表 tab（https://gaotuedu.feishu.cn/sheets/T9lhsNwL4hzovStIDVDcyy8znRf?sheet=Fn06qE ）与 [`tasks.md`](tasks.md)。

## 3. 坑（必看）
- **`沟通摘要-test`/`用户画像-test` 的 compare 必须传 `commTag`**（context 里，如 `0`），否则 claimer 不出数据 → 误判“不一致”。
- **退费 apps 的 compare**：数据走 `params[1]`（userQuery 传退费内容）。
- `aiApplicationName` 传 **ai_application 名**（如「生成沟通建议-高中」），不是 agent 名。
- 大 ID（clazzNumber/userId）传**字符串**，避免 JSON 精度截断。
- 网关响应框架 = 新链路是否生效：`event=litellm_proxy/...`（新）vs `message`（老 Dify）。
- 快速定位网关真实请求参数：litellm 日志在 **SLS**（`service=litellm`, `logType=app`, 按 traceId/`grep="Chat_completion request"`）。

## 4. 验证命令（对比接口，一次出两侧）
```bash
curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" \
  'https://test-fuwu.baijia.com/bgwApi/student-data/test/acl/compare/service' \
  -H 'content-type: application/json' -H 'traffic-env: test-gtbg-dev-1' -H 'identification: microLessonStudent' \
  --data-raw '{"serviceNameAndMethodName":"com.gaotu.student.data.domain.ai.manager.service.impl.AiApplicationTestServiceImpl#compareAiApplication","params":["沟通摘要-test","","test",{"clazzNumber":"585960582537144320","userId":"7658127801","commTag":0}]}'
```
（prod 复验把 host 换 prod、去掉 `traffic-env`）

## 5. 不在本次范围
- **`生成沟通建议-高中`（问题建议-高中 `256918735665808384`）/ `生成沟通建议-素养`（问题建议-素养 `256918818763359232`）——保留 Dify，不迁**。原因（给领导口径）：
  1. 这两个应用在 Dify 上是 **agent-chat + function_call 且绑定了 Dify 知识库（dataset）**；Dify 把知识库**注册成一个工具**交给模型，**由模型运行时自己发起检索**，Dify 做**向量检索 + rerank**，再把命中的话术片段**回灌**给模型。**知识不在提示词里，而在「运行时检索」这一步**。
  2. 我们迁移的目标链路（公司 LLM 网关）是**标准单次 chat completion**：只发 `system`（指令）+ `user`（数据），**没有工具/检索能力** → 直接切会**丢掉知识库检索**、答案不再基于话术库，**属有损替换**，不能做。
  3. 对比其余 15 个应用：无知识库（`tools` 全空、无 dataset），提示词可完整搬到 student-data，**切换无损、已逐个验证结构一致**。差别就在**知识库**。
  4. **不是完全没法做**：这两个知识库其实是 **Teable 结构化话术表**（高中 ~10.4 万字 / 素养 ~4.8K 字，字段：问题类型/适用课程/标准回复/评分标准…），student-data 已有 `TableApiDataHolder` 取数能力，可「先判问题类型+课程 → 从 Teable 取话术 → 拼进 prompt」等价复刻（不需向量库）——但**属额外开发、须单独立项，本期未做**。
  - **结论：本期 15 个切网关、这 2 个留 Dify，故 Dify 在这 2 个应用上暂不能完全下线**。评估明细见 [`artifacts/dify-kb-eval.md`](artifacts/dify-kb-eval.md)。
- `我家子涵最近学的怎么样`（Dify「二讲回复」；归属待定）
- ~~退费「素养/精品班」共用同一 `prompt_config` 的应用~~ —— **已由「改挂 `ai_application`（应用级）」解决**（2026-10-28）。
