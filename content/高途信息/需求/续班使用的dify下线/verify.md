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
| 退费根因/NPS/旅程/课程体验/降退费（素养+精品班，10 个） | 18 ~ 30（只是「退费根因分析」这类标签） | **Dify**（迁到 `gateway_core_prompt`，仅新链路用） |

- 证据：`select a.name, p.core_prompt from ai_application a join prompt_config p on p.number=a.prompt_config_number` → 退费类 `core_prompt` 仅为标签；`RefundReasonServiceImpl` 内有注释 `// todo: few-shot write in system prompt`（说明 system prompt 本就在 Dify）。

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

## 退费提示词迁移（test）

**新链路提示词存 `ai_application.gateway_core_prompt`（2026-10-28 起改为应用级，新增列，仅 `platform_type=2` 时用作 system 提示词）；老链路(Dify)仍读 `prompt_config.core_prompt`（原标签）不动** → 切回 Dify 零变化，满足「可回退」。**不放 Apollo**（Apollo 有值长度限制）。

> **为什么从 prompt_config 改成 ai_application**：prod 退费 10 个应用只落到 3 个 `prompt_config`（根因×2 / 降退费×2 / **旅程+NPS+课程体验 共 6 个共用 1 个 pc**），提示词挂 pc 上无法按应用区分；挂 `ai_application`（每个 agent 恰好 1 个 app）才能逐应用给不同提示词。老链路/老数据零影响。

- DDL（test 直连 `gaotu_test_rw`）：`ALTER TABLE ai_application ADD COLUMN gateway_core_prompt text NULL ... AFTER prompt_config_version_number`
- 代码：`AiApplicationExecutor`（主执行路径）在 `platformType==2` 时用 `aiApplicationBO.gatewayCorePrompt` 覆盖 system 提示词，**为空则回落 `prompt_config.core_prompt`**（续班应用不配即用原提示词）。`DynamicPromptGenerator#buildSystemPrompt` 支持覆盖。
- test 6 个应用已迁移（值=旧 `prompt_config.gateway_core_prompt`，保持既有行为）：

| 应用（app） | app_num | gateway_core_prompt 来源 | 长度 |
|-|-|-|-|
| 退费根因分析 | 255743373455931392 | 精品退费根因.pre_prompt | 2254 |
| 退费旅程分析 | 255733517892204544 | 精品退费旅程.pre_prompt | 2482 |
| 退费课程体验分析 | 255742588441606144 | 精品课程体验.pre_prompt | 2381 |
| 退费NPS分析 | 255743873725249536 | 精品课程NPS.pre_prompt | 473 |
| 降退费服务建议 | 255743654696597504 | 素养降退费工作流.nodes | 1412 |
| 素养服务建议 | 261424322528162816 | 素养降退费工作流.nodes | 1412 |

- `prompt_config.gateway_core_prompt`（test 遗留列）已不再被代码读取，值可忽略。
- prod 需走 DDL 工单给 `ai_application` 加该列。

### 应用级提示词复验（test，2026-10-28，commit 91012878 / pod student-data-6cb8c4b998-9j2zn）

`compareAiApplication("退费根因分析", <退费内容>, "test", {})` 同输入串行两侧，落库 `ai_application_call_task_result`：

| 侧 | id | system 提示词 | q_len | 结果 |
|-|-|-|-|-|
| Dify（老链路） | 263717 | 标签「退费根因分析」 | 1205 | 合法 JSON，`directReason`/`rationales[]` |
| 网关（新链路） | 263718 | **完整提示词**「##任务背景 分析客户…」 | 3453 | 合法 JSON，结构一致 |

→ 应用级 `gateway_core_prompt` 被网关路径正确读取；老链路仍发标签，行为未变。

## 逐应用对比结果（test，2026-10-27）

方法：`compareAiApplication(app名, "", "test", {clazzNumber,userId})`，同输入串行跑 Dify vs 网关。

| 应用（app 名） | Dify | 网关 | 结论 |
|-|-|-|-|
| 用户画像-test | `event=message`、```json 包裹 | `litellm_proxy/doubao-seed-2.0-lite`、纯 JSON | 一致 |
| 沟通摘要-test | `event=message`、```json 包裹 | `doubao-seed-2.0-lite`、纯 JSON | 一致 |
| 服务SOP分析 | `message`（含 think） | `doubao-seed-2.0-lite`、纯 JSON | 一致 |
| 生成沟通建议-高中 | `message`（含 think） | `doubao-seed-2.0-lite`、纯 JSON（调课咨询话术） | 一致 |
| 预测分层原因 | `message`「暂无分析原因」 | `doubao-seed-2.0-lite`「暂无分析原因」 | 一致 |
| 问题建议-素养（app：生成沟通建议-素养） | `message`（含 think） | `doubao-seed-2.0-lite`、纯 JSON（调课咨询话术） | 一致；test 原无此 app，**已新建后再验** |
| 退费根因分析 | `message`（含 think） | `deepseek-flash`、纯 JSON（`directReason`/`rationales`） | 一致 |
| 退费旅程分析 | `message`（含 think） | `deepseek-flash`、纯 JSON（`tutoringSummary`） | 一致 |
| 退费课程体验分析 | `message`（含 think） | `deepseek-flash`、纯 JSON（`courseExperienceSummary`） | 一致 |
| 退费NPS分析 | `message`（文本） | `deepseek-flash`、文本（`本班级/其他班级分析`） | 一致；**该应用不带 `params`**（纯文本，`json_object` 会 400） |
| 素养服务建议 | `message`（含 think） | `deepseek-flash`、纯 JSON（`suggestion`） | 一致 |
| 降退费服务建议 | `message`（含 think） | `deepseek-flash`、纯 JSON（`suggestion`） | 一致 |

> 触发口径：桥调 `AiApplicationTestServiceImpl#compareAiApplication`；`aiApplicationName` 要传 **ai_application 名**（如「生成沟通建议-高中」）。续班样本 clazz `500775385189890048` / user `7404351741`；退费类把 **mock 退费内容当 `userQuery`** 传（数据走 userQuery）。

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
| 退费全部 10 个（根因/NPS/旅程/课程体验/降退费，素养+精品班） | deepseek-v4-flash-0731 或 deepseek/DeepSeek-R1-250528 | **`deepseek-flash`**（统一，= 网关官方接管值） |

> 退费整条线统一迁到 **`deepseek-flash`**（DeepSeek-V4.1-Flash，网关 `redirectToModelCode` 的官方接管目标）；取代早期选的 `deepseek-v4.1-flash-1017`（同为 v4.1，但部署不同）。见 [`artifacts/llm-gateway-model-mapping.md`](artifacts/llm-gateway-model-mapping.md)。

- gps-ai **原有**：`deepseek-v4-flash-0731`（id 24983）。
- gps-ai **test 已新增**：`doubao-seed-2-0-lite-260428`（id 37268）、`deepseek-v4.1-flash-1017`（id 37270），均 `callerRoute/save`、`env=test`。
- 网关目录里下线模型 `status=2`、`save` 报 `模型不存在或已下线`，加不了同 code，只能迁到替换模型。

> 新增路由的 CLI：`gateway_admin.py save --env test --file <json> --confirm`；json 见 [`llm-gateway-admin/references/admin-api.md`](../../../.claude/skills-cold/llm-gateway-admin/references/admin-api.md) 的 `save 请求体`（新建时**不带 `id`**）。

### gps-ai prod DeepSeek 路由的 `response_format`（id 33566）

- 现状：`callerRoute` id **33566**（`gps-ai` / `deepseek-v4-flash-0731` / **prod**）`defaultParams.response_format = {"type":"json_object"}, force=false`；其余 gps-ai 路由 `defaultParams` 均空。
- `force=false` 语义 = 只补调用方**没传**的参数；而 `LlmGatewayRequest`（`student-data`）**不发送 `response_format`** → 该 route 下**所有**调用方（当前=续班归因）实际都被注入 `json_object`。
- 判断：**当前有必要保留**（续班归因必须稳定 JSON，去掉会回归「非法 JSON 解析失败」）。风险点：把退费类（同用 `deepseek-v4-flash-0731`）迁到 gps-ai 后**共用同一 route**，若其中有**要纯文本**的场景会被强约束成 JSON。
- 处置建议（二选一）：① 确认同 route 下所有应用都要 JSON → 保留；② 需要按应用区分 → **不删 route 默认值，改在请求里按应用下发 `response_format`**（给 `AiModelCallOption`/`LlmGatewayRequest` 加可选字段），route 默认值再退为兜底。

## 迁移审查复核（2026-11-23）

### 当前实际生效配置

- 读取 Apollo 已发布值：`student-data / TEST / application / ai.agent.accessor.override.map` 当前命中 9 个应用；续班/退费的两个知识库应用未命中，仍保留 Dify。
- `student-data / PROD / application / ai.agent.accessor.override.map` 当前为 `{}`，生产没有误切新链路；生产提示词列、路由和代码发布仍按 T-09～T-13 的顺序推进。
- 证据来自 Apollo 已发布配置读取，入口分别为 `http://test-apollo-meta.baijia.com/configs/student-data/TEST/application` 与 `http://10.255.162.197:8000/configs/student-data/PROD/application`。

### 代码级对等性审查结论

- `origin/feature-xuban-dify-offline` 相对 `origin/release` 仅改动 11 个后端文件；没有前端改动。`mvn8 -pl student-data-service -am -DskipTests compile` 在独立 worktree（commit `91012878d`）通过。
- 已确认 Dify 额外承担的功能只有知识库 dataset 的向量检索/rerank 回灌；扫描到的目标应用 `tools` 为空，敏感词、注释和其它 `gt_configs` 均关闭，不能把普通模型输出文本差异当成迁移缺陷。
- 新链路已按应用复制 Dify 的 `completion_params`（`enable_thinking`、`stop`、`temperature` 等），网关请求合并时禁止 `params` 覆盖 `model`、`max_tokens`、`messages`；旧链路仍使用原 flat prompt 和 Dify accessor。
- 目前没有发现可由代码直接修正的确定性缺陷，因此本轮未改业务代码。模型输出的自由文本和分类项仍可能因模型、随机性和上下文结构产生差异；验收应优先检查 JSON 结构、枚举合法性、关键业务语义和非空约束，不能要求逐字相同。

### 未覆盖 / 仍需按发布顺序验证

- 本轮未调用生产业务入口、未写生产 Apollo/数据库、未进行生产发布；生产 15 个应用的逐应用成功 trace 仍待 T-09～T-14 完成。
- 测试现有对比证据覆盖桥调 `compareAiApplication` 和测试泳道，不等价于全量线上异步任务验证；上线后仍需按应用回读 `ai_application_call_task_result` 及最下游 LLM trace。

## 对增量问题的澄清（2026-11-23）

### 最下游 LLM 输入与 trace 覆盖边界

- **已覆盖一条真实测试对比链路**：`artifacts/compare-detail.md` 的 trace `9e84dced-3614-499e-80b7-b1fb0bb0ca4d.0.3` 对应退费根因应用；同一应用、同一输入在 `ai_application_call_task_result.actual_query` 留下 Dify 与网关两条请求，已逐项核对 system/user 来源、请求路径和模型参数。Dify 的完整指令由 Dify 内部补齐，网关侧来自 `gateway_core_prompt`；参数差异集中在 `enable_thinking`、`stop` 等，补齐后相似度由 0.228 提升到 0.531。
- **已覆盖测试桥返回层**：`verify.md` 中 `沟通摘要-test` 的 trace `005cf022-…` 证明同一输入串行命中 Dify 与网关，响应事件分别为 `message` 和 `litellm_proxy/...`；`actual_query`/`result` 和网关模型、参数的对比证据见 `artifacts/compare-detail.md`。
- **边界**：这些证据能证明测试链路的下游请求构造和差异原因，覆盖的是代表性退费应用及续班试点，不代表 15 个应用的每个真实异步任务都已取得独立 LLM SLS trace；本轮不再把“结构一致”扩写成“全量输入完全一致”。

### “部分功能线上可能已下线”的核实

- **已核对的 Apollo 运行状态**：`student-data` TEST/PROD 已发布 namespace 中，`renewal.ai.dept.module.switch`、`refund.ai.dept.module.switch`、`refund.ai.module.deps` 均为 `{}`；PROD `refund.predict.async.switch=true`，续班/退费相关 topic、group 和 AI agent 映射仍存在。结合 `ees_data.ai_agent` 中目标应用的 `platform_type=1` 清单，未发现某个本期目标应用被 Apollo 明确关闭的证据。
- PROD `ai.agent.accessor.override.map={}` 只说明迁移开关尚未打开，不能据此判断业务功能下线；因此本期迁移范围仍按已确认的 15 个目标应用 + 2 个知识库应用保留 Dify 处理。
- **未覆盖**：没有业务访问量/调用次数或逐应用线上任务统计，因此不能据此证明每个应用当前都有流量；若后续要缩小范围，应另查应用调用记录或产品确认，不能把“无开关关闭证据”当成“全量仍在使用”。


## 2026-11-23 18:22 trace 实查纠正（优先于此前结论）

- 历史退费 trace `9e84dced-3614-499e-80b7-b1fb0bb0ca4d.0.3`：TEST trace_tree=0 span；按北京时间 2026-10-27 00:00 至 10-29 00:00 查 app 日志，SLS/TLS 均 0 条。不能确认是 ID 错误还是日志保留期等原因。此前凭归档称最下游已核验的结论证据不足，应撤回；actual_query 是应用侧留痕，不是 Dify 内部最终 LLM 请求。
- 新续班 trace：`7fdbe39b-bd88-4579-8fc3-fc594f4658d0.0.3`，沟通摘要-test，2026-11-23 18:20:46～18:20:52 +08:00。
- 新退费 trace：`10effaa6-5d46-4f72-887b-932b033a45d9.0.3`，退费根因分析，2026-11-23 18:20:46～18:20:58 +08:00。输入为时间冲突的明确测试文本。
- 两条请求均带 test-gtbg-dev-1，入口 quickTestAiApplication，响应 event=message；TEST 调用链分别 51/46 span，含 student-data 对 /dify/api/v1/chat-messages 的调用；SLS app 日志用完整 trace 加双引号查询已实际命中，TLS 未命中。建议查询时间 2026-11-23 18:20～18:23，北京时间，不要使用默认 error 日志。
- 原 compareAiApplication 在当前泳道返回“未找到方法”，本次新证据不是双路 compare，不代表当前部署仍为 91012878d。两条新 trace 未取得 Dify 内部最下游 LLM 请求日志，不能据此宣称最终输入对等。
- 证据：[trace 实查目录](artifacts/trace-recheck-20261123/)。本次无生产修改、无代码修改。


## 2026-11-23 18:24 下游日志库纠正

已沿两条新 trace 只读查询 PROD/SLS/app，找到 dify-api、dify-plugin-daemon、litellm 同 trace 日志。测试业务请求调用共享 dify-open，不能只在 TEST 日志库搜索下游。未新增生产业务调用。

- 续班 `7fdbe39b-bd88-4579-8fc3-fc594f4658d0.0.3`：18:20:48.343 LiteLLM 收到 caller_0167 请求，model=doubao/Doubao-1-5-pro-32k，stream=true，messages 仅 user（完整 flat prompt）。
- 退费 `10effaa6-5d46-4f72-887b-932b033a45d9.0.3`：18:20:48.300 LiteLLM 收到 caller_0167 请求，model=deepseek/DeepSeek-R1-250528，stream=true，messages 为 system（Dify 补入完整指令）+ user（原应用 flat prompt）。
- 两条实收 body 均仅包含 model/stream/messages/user，未显式包含 enable_thinking、stop、temperature、max_tokens；此前从应用配置推导这些参数已完全对齐不成立。网关内部后续默认参数与模型重定向还需单独追踪。
- 精简实收请求证据：`artifacts/trace-recheck-20261123/renewal-dify-llm-request.json`、`refund-dify-llm-request.json`。这是网关实收层证据，不自动等于提供商收到的最终 HTTP body。
- **未完成**：迁移分支运行版本当前尚未恢复，原泳道缺 compareAiApplication；尚无同样输入的迁移侧网关实收请求，也未完成提供商侧最终参数核对。现有证据只能确认 Dify 侧消息结构与隐含提示词处理，不能确认迁移对等。需要先定位可用迁移版本实例或安排隔离测试部署再续验，不能把当前旧链路成功视作迁移验证完成。


## 2026-11-23 迁移侧部署阻塞与参数证据

- 已验证原 test-gtbg-dev-1 namespace 无 Pod，因此此前带该泳道头的 quickTest 请求不能标作迁移版本执行。
- 恢复测试部署流水线 1359971（record 1763148，Jenkins build 498072），分支 feature-xuban-dify-offline、commit 91012878d692119e79fb7d14baa1bab594c9534d。镜像 `acr.baijia.com/uqun/student-data:feature-xuban-dify-offline-91012878-20261123182636` 已推送，Jenkins 18:29:20 Finished: SUCCESS。
- 青舟 imageBuildRecord 仍 status=1，stepNum=1，updateTime 停留创建时间；20轮/10分钟轮询超时，目标泳道仍无 Pod。指定同镜像 redeploy 被 code=400“当前环境正在发布”拒绝，未执行成功。需要青舟平台核对该构建完成回调/记录状态并解除卡住的发布锁。未停止其他流水线，未手改平台数据库。
- 轮询进程已以退出码2结束；远端流水线仍显示 RUNNING，尚未终态，不能当作部署完成。恢复后须沿原 pipeline/镜像续验，不重复构建。
- 参数已证实：Dify caller_0167 的续班模型由 doubao/Doubao-1-5-pro-32k 重定向到 doubao-seed-2-0-lite-260428，日志明确注入 thinking；退费 R1 重定向 deepseek-flash。gps-ai TEST Doubao 路由37268的 defaultParams={}。证据见同目录 model-redirect-evidence.json、gps-doubao-route-test.json。不能从入口未传 thinking 推断实际没启用思考，也不能据这些证据断言两侧最终参数相同。
- 未完成：迁移代码实际运行后的网关请求对比、提供商最终参数核对及必要修正。没有新代码修正和生产写入。
