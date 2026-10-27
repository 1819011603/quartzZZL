---
title: 续班使用的dify下线 · 验证手册
tags: [需求, 验证]
---

# 验证手册

## 环境

| 项 | 值 |
|---|---|
| 泳道 | `test-gtbg-dev-1`（部署流水线 1316179，分支 `feature-xuban-dify-offline`） |
| 依赖服务 | `student-data`（facade / service / dws） |
| 数据库 | `ees_data`（`ai_agent` / `ai_application`）；`mysql_query` 传 `ees_data.ai_agent` 自动定位 |
| 网关 caller | `gps-ai`（test key 与 prod key **按环境分开**：Apollo TEST `llm.gateway.api-key`=gps-ai test key + `llm.gateway.domain=test-llm.baijia.com`；PROD = gps-ai prod key + 默认 `llm.baijia.com`） |

## 切换对象（test 环境，起于 2026-10-27 现查）

`ees_data.ai_agent`（`platform_type=1`，续班相关）：

| 应用（智能体） | number | 场景 | 关联 ai_application |
|-|-|-|-|
| 用户画像/沟通摘要-test | 255107338300556288 | 用户画像 + 沟通摘要 | 用户画像-test(255107395528688640) / 沟通摘要-test(255551371814636544) |
| 服务SOP分析 | 256325360053917696 | 服务建议 | 服务SOP分析(256327049255322624) |
| 素养服务建议 | 261423990261694464 | 服务建议 | 素养服务建议(261424322528162816) |
| 预测分层原因 | 262172718139452416 | 分层原因 | 预测分层原因(262173928596712448) |
| 问题建议-高中-豆包 | 255465773531663360 | 沟通建议 | 生成沟通建议-高中 等 |
| 问题建议-素养-豆包 | 255465673062353920 | 沟通建议 | — |
| 退费旅程分析 | 255733061835044864 | 退费旅程 | 退费旅程分析(255733517892204544) |
| 退费课程体验分析 | 255742622136547328 | 退费课程体验 | 退费课程体验分析(255742588441606144) |
| 退费根因分析 | 255743333766281216 | 退费根因 | 退费根因分析(255743373455931392) |
| 退费NPS分析 | 255743847351465984 | 退费NPS | 退费NPS分析(255743873725249536) |
| 降退费服务建议 | 255743632420648960 | 降退费服务建议 | 降退费服务建议(255743654696597504) |

新链路对照：`LLM网关-claude-sonnet-5`（prod 288169334962948096 / test 286798016992532480，`platform_type=2`）。

## 提示词归属（重要）

切网关后提示词由 `DynamicPromptGenerator` 从 student-data 的 `prompt_config.core_prompt` 拼装下发。**提示词不在 student-data 的应用，只改 Apollo 会丢提示词、行为不对。**

| 应用 | core_prompt 长度 | 提示词在哪 |
|-|-|-|
| 用户画像 / 沟通摘要 / 服务SOP分析 / 问题建议-高中 / 问题建议-素养 | 535 ~ 4239 | **student-data**（可直接切） |
| 续班分层原因分析-高中 / -素养 | 7489 | **student-data**（可直接切） |
| 退费根因/NPS/旅程/课程体验/降退费（素养+精品班，10 个） | 18 ~ 30（只是「退费根因分析」这类标签） | **Dify**（切前须把提示词搬进 student-data） |

- 证据：`select a.name, p.core_prompt from ai_application a join prompt_config p on p.number=a.prompt_config_number` → 退费类 `core_prompt` 仅为标签；`RefundReasonServiceImpl` 内有注释 `// todo: few-shot write in system prompt`（说明 system prompt 本就在 Dify）。

## 判定是否走了新链路（不看库，看留痕）

- `ees_data.ai_application_call_task` / `ai_application_call_task_result`：按 `ai_application_number` 看本次调用的平台与响应。
- 走 Dify：响应 `event=message` + UUID message_id；走网关：`event=litellm_proxy/...`、message_id 形如 `chatcmpl-...`。
- 服务端日志按 traceId 定位（`qingzhou-observe`）。

## Apollo 开关

| key | 默认 | 说明 |
|---|---|---|
| `ai.agent.accessor.override.map` | `{}` | json map：`ai_agent.number`(字符串) → 覆盖对象。命中即按对象改该应用的访问方式，未命中用库值 |

覆盖对象字段（value 是 JSON，`name` 必填便于识别这个 ID 是什么应用）：

| 字段 | 必填 | 说明 |
|---|---|---|
| `name` | 是 | 应用名称，仅可读性用，不参与逻辑 |
| `platformType` | 否 | 目标 `platform_type`，如 `2`=LLM 网关；空用库值 |
| `model` | 否 | 目标模型 modelCode；空用调用方传入 |
| `params` | 否 | 追加到网关请求体的自定义参数（OpenAI 兼容），如 `{"response_format":{"type":"json_object"}}`；`model`/`max_tokens`/`messages` 三键不受其影响 |

- 试点 TEST `application`：
  `{"255107338300556288":{"name":"用户画像/沟通摘要-test","platformType":2,"model":"doubao-seed-2-0-lite-260428","params":{"response_format":{"type":"json_object"}}}}`
- 读回：`apollo_get_key app_id=student-data env=TEST key=ai.agent.accessor.override.map`（读**已发布**值）。
- 旧 key `ai.agent.platform.type.override.map` 已被取代，TEST 置 `{}`（代码不再读）。

## 测试环境首个试点验证步骤（T-04）

1. 试点应用：`用户画像/沟通摘要-test`（`ai_agent.number=255107338300556288`）
2. Apollo TEST 配开关命中试点并发布；部署 `student-data` 到 `test-gtbg-dev-1`
3. 触发一次该应用的续班调用（走对应触发链路）
4. 校验：`ees_data.ai_application_call_task_result` 响应形态为网关（`chatcmpl-` / `event=litellm_proxy/...`）、业务产出与 Dify 一致、无报错
5. 反向验证：把开关改回（去掉该 key 或设 1）→ 回到 Dify（`event=message` + UUID）

## 验证结果（2026-10-27 · test-gtbg-dev-1 · 分支 feature-xuban-dify-offline）

| 项 | 结论 |
|---|---|
| 部署 | pod `student-data-74fcf5779-k7wkk`（10.218.251.189）`eurekaStatus=UP`，commit `f0c58aaf` |
| 开关开（`platformType=2`） | 通。`沟通摘要-test` 走出网关：`event=litellm_proxy/...`、`messageId=chatcmpl-...` |
| 开关关（`{}`） | 通。回退 Dify：`event=message`、`messageId=UUID` |
| **模型覆盖**（`model=doubao-seed-2-0-lite-260428`） | 通。`event=litellm_proxy/doubao-seed-2.0-lite`（不再是网关默认 `claude-sonnet-5`） |
| **自定义参数**（`params.response_format=json_object`） | 通。`answer` 为纯 JSON、无 \`\`\`json 包裹 |
| 触发方式 | ACL 桥直调 `AiApplicationTestServiceImpl#quickTestAiApplication`（`POST /bgwApi/student-data/test/acl/compare/service`，头 `traffic-env: test-gtbg-dev-1`） |

## 新旧链路对比方法（桥调用）

- 方法：`com.gaotu.student.data.domain.ai.manager.service.impl.AiApplicationTestServiceImpl#compareAiApplication`
- 入参：`[aiApplicationName, userQuery, userTag, context]`；`context` 至少含 `clazzNumber`、`userId`（沟通摘要/画像类），大 ID 传**字符串**避免精度截断
- 行为：同一输入**串行**跑 Dify(`platformType=1`) 与 LLM 网关(`platformType=2`)，返回 `{dify, gateway}` 两侧原始响应（`event`/`messageId`/`answer`）供人工比对；任一侧失败返回 `event=ERROR`（不吞另一侧）。网关侧模型/参数取应用级覆盖
- 命令（ACL 桥）：
  ```bash
  curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" \
    'https://test-fuwu.baijia.com/bgwApi/student-data/test/acl/compare/service' \
    -H 'content-type: application/json' -H 'traffic-env: test-gtbg-dev-1' -H 'identification: microLessonStudent' \
    --data-raw '{"serviceNameAndMethodName":"com.gaotu.student.data.domain.ai.manager.service.impl.AiApplicationTestServiceImpl#compareAiApplication","params":["沟通摘要-test","","test",{"clazzNumber":"500775385189890048","userId":"7404351741","commTag":0}]}'
  ```
- 2026-10-27 实测（`沟通摘要-test`，clazz `500775385189890048` / user `7404351741`，traceId `005cf022-…`）：
  - Dify：`event=message`，answer 为 ```json 包裹
  - 网关：`event=litellm_proxy/doubao-seed-2.0-lite`，answer 为**纯 JSON**（`response_format` 生效）
  - 两侧语义一致

## 逐应用对比结果（test，2026-10-27）

方法：`compareAiApplication(app名, "", "test", {clazzNumber,userId})`，同输入串行跑 Dify vs 网关。

| 应用（app 名） | Dify | 网关 | 结论 |
|-|-|-|-|
| 用户画像-test | `event=message`、```json 包裹 | `litellm_proxy/doubao-seed-2.0-lite`、纯 JSON | 一致 |
| 沟通摘要-test | `event=message`、```json 包裹 | `doubao-seed-2.0-lite`、纯 JSON | 一致 |
| 服务SOP分析 | `message`（含 think） | `doubao-seed-2.0-lite`、纯 JSON | 一致 |
| 生成沟通建议-高中 | `message`（含 think） | `doubao-seed-2.0-lite`、纯 JSON（调课咨询话术） | 一致 |
| 预测分层原因 | `message`「暂无分析原因」 | `doubao-seed-2.0-lite`「暂无分析原因」 | 一致 |
| 问题建议-素养-豆包 | — | — | test 无对应 ai_application（待查 app 名） |
| 退费类 6 个 | — | — | 待提示词迁移后再验 |

> 触发口径：桥调 `AiApplicationTestServiceImpl#compareAiApplication`；`aiApplicationName` 要传 **ai_application 名**（如「生成沟通建议-高中」），不是 agent 名。样本 clazz `500775385189890048` / user `7404351741`。

## Dify 控制台/服务 API（查应用与模型）

> 用途：从 Dify 反查每个应用用的模型（迁移时一一对应）。全部经 **baijia-proxy**（`http://127.0.0.1:8888`）注入 Cookie，`curl -s -k -x`。

| 用途 | 方法 | 路径 |
|---|---|---|
| 团队应用列表 | GET | `https://os.baijia.com/dify/api/console/api/gt-apps?scope=team` |
| 应用详情（**含模型**：`model_config.model.name` / `provider`） | GET | `https://os.baijia.com/dify/api/console/api/apps/{app_id}` |
| 工作流应用模型 | GET | `https://os.baijia.com/dify/api/console/api/apps/{app_id}/workflows/draft`（`graph.nodes[type=llm].data.model.name`） |
| ai_agent ↔ Dify 应用核对（服务 API） | GET | `https://dify-open.baijia.com/dify/api/v1/info`，头 `Authorization: Bearer <ai_agent.access_key>` → 返回应用名 |

- `app_id` 形态：`spcAm3oupwKuWRMD8UV_<uuid>`；`ai_agent.access_key` 形如 `app-...`（Dify 服务 API key）。
- 控制台 `apps/{id}/api-keys` 返回空（`{"data":[]}`），核对归属改用服务 API `/info` 返应用名。

### 应用 ↔ 模型对应表（2026-10-27 实测）

| ai_agent（name / number） | Dify 应用（app_id） | 模型 |
|-|-|-|
| 用户画像 / 256917438512284672 | 用户画像-prod（`…_2feb2cf6-ad1c-4e7a-b1cb-a13cc7957680`） | doubao-seed-2-0-lite-260428 |
| 沟通摘要 / 257085994022484992 | 沟通摘要-prod（`…_014b80e6-a6d6-405e-bdf8-123183a6b462`） | doubao-seed-2-0-lite-260428 |
| 问题建议-高中 / 256918735665808384 | 问题建议-高中（`…_91073e8d-cf48-422e-89fc-4d83208b66e5`） | doubao-seed-2-0-lite-260428 |
| 问题建议-素养 / 256918818763359232 | 问题建议-素养（`…_6a34e48f-721b-4f0d-addc-5d71c913e3d7`） | doubao/Doubao-Seed-1-6 |
| 服务SOP分析 / 256919048417231872 | 服务SOP分析（`…_3efa158f-2ee6-4b39-b9ca-a064c34310b2`） | doubao-seed-2-0-lite-260428 |
| 续班分层原因分析-高中 / 263057785613229056 | 预测分层原因分析-高中（`…_f72b9759-3732-4230-b4d7-d728bf40ba1e`） | doubao/Doubao-1-5-pro-32k |
| 续班分层原因分析-素养 / 263080101791455232 | 预测分层原因分析-素养（`…_0952c859-ebb6-4c67-b84a-77fa72485693`） | doubao/Doubao-1-5-pro-32k |
| 退费根因分析(素养学部) / 261424983727715328 | 【素养】退费根因分析（`…_7bc17525-0cb2-4cb0-a129-f98d05a3ace0`） | deepseek-v4-flash-0731 |
| 退费根因分析(精品班学部) / 256995079971961856 | 【高中】退费根因分析（`…_277d1192-f8bd-4b3e-b4a8-235b5773bedd`） | deepseek-v4-flash-0731 |
| 退费NPS分析(素养学部) / 261424755557579776 | 【素养】课程NPS分析（`…_3d398bdf-622e-42f8-a5f3-d5543495421b`） | deepseek-v4-flash-0731 |
| 退费NPS分析(精品班学部) / 256995228385317888 | 【高中】课程NPS分析（`…_446dd984-ea29-4da4-b48f-e25993590a50`） | deepseek/DeepSeek-R1-250528 |
| 退费旅程分析(素养学部) / 261425291830803456 | 【素养】退费旅程分析（`…_38394780-f10a-4ca2-a7cd-1bc384bcc660`） | deepseek-v4-flash-0731 |
| 退费旅程分析(精品班学部) / 256994902246699008 | 退费旅程分析（`…_b3b6b157-30b9-4155-8eed-3992886b3302`） | deepseek-v4-flash-0731 |
| 退费课程体验分析(素养学部) / 261425172233344000 | 【素养】课程体验退费分析（`…_8de12316-6b62-479f-a203-7a61151dd7c7`） | deepseek-v4-flash-0731 |
| 退费课程体验分析(精品班学部) / 256994989452607488 | 【高中】课程体验退费分析（`…_626f88c9-6d79-4a80-b941-4f65a1497a23`） | deepseek/DeepSeek-R1-250528 |
| 降退费服务建议（素养学部） / 261424592068814848 | [素养]降退费服务建议分析工作流（`…_1043df8c-f3d3-44b3-accd-ec2051c0c4a3`） | deepseek-v4-flash-0731（节点 temp 0.7） |
| 降退费服务建议（精品班学部） / 256995156763347968 | 【高中】降退费服务建议分析工作流（`…_5c7ac7f6-af1d-4120-91a5-9a6485fd3d99`） | deepseek/DeepSeek-R1-250528（节点 temp 0.7） |
| （不在本期）我家子涵最近学的怎么样 / 277848708525108224 | 二讲回复 | — |
| test 试点：用户画像/沟通摘要-test / 255107338300556288 | 续班AI-用户画像&沟通摘要-test（`…_1114ea4e-e5c2-448d-9770-6d9bf63a3780`） | doubao/Doubao-1-5-pro-32k |

> `app_id` 前缀统一为 `spcAm3oupwKuWRMD8UV_`，表内为省位只留 uuid 段，查询时补前缀。

### 模型 → 网关路由（2026-10-27 核对/操作）

官方【模型下线通知】（火山引擎，计划下线 2026-09-21）给出**替换映射**：

| 下线模型 | 建议替换 |
|---|---|
| `doubao/Doubao-1-5-pro-32k` | `doubao-seed-2-0-lite-260428` |
| `doubao/Doubao-Seed-1-6` | `doubao-seed-2-0-lite-260428` |
| `doubao/Doubao-Seed-1-6-flash` | `doubao-seed-2-0-mini-260428` |
| `doubao/Doubao-Seed-1-6-thinking` | `doubao-seed-2-0-lite-260428` |
| `doubao-seed-2-0-lite-260215` | `doubao-seed-2-0-lite-260428` |
| `doubao-seed-2-0-mini-260215` | `doubao-seed-2-0-mini-260428` |

落到本需求的迁移后模型：

| 应用 | 原 Dify 模型 | 迁移后模型 |
|-|-|-|
| 用户画像 / 沟通摘要 / 问题建议-高中 / 服务SOP分析 | doubao-seed-2-0-lite-260428 | doubao-seed-2-0-lite-260428（不变） |
| 问题建议-素养 | doubao/Doubao-Seed-1-6 | doubao-seed-2-0-lite-260428（映射） |
| 续班分层原因分析-素养 / -高中 | doubao/Doubao-1-5-pro-32k | doubao-seed-2-0-lite-260428（映射） |
| 退费全部 10 个（根因/NPS/旅程/课程体验/降退费，素养+精品班） | deepseek-v4-flash-0731 或 deepseek/DeepSeek-R1-250528 | **`deepseek-v4.1-flash-1017`**（统一） |

> 退费整条线统一迁到 `deepseek-v4.1-flash-1017`（含原用 `deepseek-v4-flash-0731` 的素养学部与用 R1 的精品班学部）。R1/V3 下线通知建议 DeepSeek-V4-Flash，具体采用 `deepseek-v4.1-flash-1017`。

- gps-ai **原有**：`deepseek-v4-flash-0731`（id 24983）。
- gps-ai **test 已新增**：`doubao-seed-2-0-lite-260428`（id 37268）、`deepseek-v4.1-flash-1017`（id 37270），均 `callerRoute/save`、`env=test`。
- 网关目录里下线模型 `status=2`、`save` 报 `模型不存在或已下线`，加不了同 code，只能迁到替换模型。

> 新增路由的 CLI：`gateway_admin.py save --env test --file <json> --confirm`；json 见 [`llm-gateway-admin/references/admin-api.md`](../../../.claude/skills-cold/llm-gateway-admin/references/admin-api.md) 的 `save 请求体`（新建时**不带 `id`**）。

### gps-ai prod DeepSeek 路由的 `response_format`（id 33566）

- 现状：`callerRoute` id **33566**（`gps-ai` / `deepseek-v4-flash-0731` / **prod**）`defaultParams.response_format = {"type":"json_object"}, force=false`；其余 gps-ai 路由 `defaultParams` 均空。
- `force=false` 语义 = 只补调用方**没传**的参数；而 `LlmGatewayRequest`（`student-data`）**不发送 `response_format`** → 该 route 下**所有**调用方（当前=续班归因）实际都被注入 `json_object`。
- 判断：**当前有必要保留**（续班归因必须稳定 JSON，去掉会回归「非法 JSON 解析失败」）。风险点：把退费类（同用 `deepseek-v4-flash-0731`）迁到 gps-ai 后**共用同一 route**，若其中有**要纯文本**的场景会被强约束成 JSON。
- 处置建议（二选一）：① 确认同 route 下所有应用都要 JSON → 保留；② 需要按应用区分 → **不删 route 默认值，改在请求里按应用下发 `response_format`**（给 `AiModelCallOption`/`LlmGatewayRequest` 加可选字段），route 默认值再退为兜底。
