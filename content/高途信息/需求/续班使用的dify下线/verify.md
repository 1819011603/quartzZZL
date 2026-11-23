---
title: 续班使用的dify下线 · 验证手册
tags: [需求, 验证]
---
> **2026-11-24 最新裁决**：允许合理格式差异，以核心指令、业务数据、约束及业务作用保留为准。已有单次场景样本可接受TEST替换；素养NPS实收已补齐。历史“不完全一致”仅是字面差异记录，不代表不通过；4个知识库应用仍保留Dify。详见 [最新逐场景裁决](artifacts/expanded-scope/semantic-acceptance.md)。



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

## 当前审查范围与证据口径

版本 `91012878`，测试泳道 `test-gtbg-dev-1`。11 个后端文件已审查，独立 worktree 编译通过；本轮无业务代码修正。生产只读，未发布。

用户要求已扩大到其余迁移场景；两例不是整体验收。当前细节见 [逐字段报告](artifacts/expanded-diff/report.md)，在途验证见 [交接](artifacts/expanded-scope/handoff.md)。历史 actual_query 仅为应用侧留痕，不能代替 LiteLLM 实收请求；以以下可查询的新 trace 为准。

PROD 迁移开关为 `{}`，不代表功能下线。部门模块开关 `{}` 的代码语义为全放开；实时续班启用，T+N 关闭仅表示该触发关闭。未取得逐应用流量统计，不能据此认定全部活跃或已下线。证据见 `artifacts/expanded-scope/`。

Dify 的知识库检索必须保留；其他应用的工具、工作流、参数默认值需结合实际请求核实，不能把无知识库等同无隐含处理。

## 2026-11-23 18:54 重建恢复及双路实收验证（当前结论）

- 按所有者决定停止旧 build498072，停止API返回200；新流水线1360042/build498084成功。目标Pod student-data-86c8f5db5d-cpwj9（10.218.238.186）Running/Eureka UP，镜像feature-xuban-dify-offline-91012878-20261123184341，commit91012878。原部署阻塞已解除。
- 在该版本的compareAiApplication进行两例同输入双路调用，Dify与gateway均成功，未改代码、数据库或Apollo。
- 续班沟通摘要trace：15760243-f225-4246-a103-c9565c2652ba.0.3。Dify实收18:53:04.814，迁移实收18:53:14.831。
- 退费根因trace：a32fe4b6-6269-4882-8d39-81c76f8ca23e.0.3。Dify实收18:53:04.743，迁移实收18:53:19.148。
- 查询日期2026-11-23北京时间18:53～18:55；SLS/app、完整trace加双引号。Dify侧在PROD日志库、迁移侧在TEST日志库，均有service=litellm的Chat_completion request。生产只读查询，无生产业务写调用。
- **已验证的内容保留**：两例user内容在Dify原flat prompt中逐字存在；续班新system内容也逐字存在；退费Dify额外system指令在迁移system中完整保留（仅末尾换行归一化），后接应用输出要求。因此这两个样本未见核心指令/数据丢失。
- **已验证的输入差异**：续班从单user flat变为system+user；退费从Dify system+user flat变为合并指令的system+纯user。旧侧stream=true、无显式max_tokens；新侧非流式、max_tokens=8192。续班新侧额外response_format=json_object、stop=[]；退费新侧enable_thinking=true、stop=[]。旧侧重定向模型最终分别为doubao-seed-2-0-lite-260428/deepseek-flash，续班另有thinking注入日志。不能从入口缺省推断提供商默认值。
- **结论边界**：完成两个代表样本的网关实收输入核对，确认内容保留但请求不逐字段等同；未证明提供商最终HTTP body及所有默认参数逐字段相同，不以随机文案差异判断迁移失败，也不能以成功两例推断全量业务等价。没有运行证据支持新增业务代码修正，未盲目改变既有消息角色策略或全局网关参数。
- 对后续放量适用：固定业务数据、对齐实际模型路由和thinking语义，区分入口参数与重定向/默认参数；按结构、合法枚举、事实忠实度验收，抽取多次结果评估随机性；保留知识库应用的检索路径和单应用回滚。
- 证据位于artifacts/trace-recheck-20261123/compare-{renewal,refund}-{prod,test}-request.json及compare-{renewal,refund}.json。未覆盖完整业务异步落值、全量应用、提供商最终请求；若必须证明提供商逐字段参数，需要网关侧提供出站请求审计（当前已查日志只有实收、重定向和返回）。


## 2026-11-23 19:00 差异处置结论（两个代表样本）

结论：核心业务指令与输入数据已核对保留，两例响应可解析，但续班两侧存在多用户措辞，退费样本缺分类清单，不能算业务质量或枚举验收通过；更不能据此证明全量等价。本轮确认并修正了一项运行差异：续班测试试点丢失旧模型重定向的 thinking disabled。

| 差异 | 决定与理由 | 影响/边界 |
|---|---|---|
| 消息角色 | 保留新system+user结构。指令/数据完整保留，明确区分可信指令和业务数据；无运行证据证明必须恢复旧flat包装 | 角色优先级会影响模型行为，不能声称语义数学等价；两例成功不排除边界样本差异 |
| stream | 保留网关非流式。现有业务同步消费完整结果，旧Dify内部流式最终也聚合为完整结果 | 内部传输、耗时/超时表现可能不同；未做流式延迟等价测试，无需为输入对齐改成流式 |
| max_tokens | 保留8192及既有length截断报错保护，旧侧入口未显式传，不擅自删上限 | 本轮四个响应finish_reason均stop，无截断；长输入的Dify动态预算不能认定已复刻，列边界，不盲目抬限 |
| response_format | 保留续班json_object，保障已有JSON解析契约；退费不强加 | 旧侧允许代码围栏、新侧纯JSON，格式约束更强，可能影响措辞，不等于指令丢失 |
| stop=[] | 保留空列表，无自定义停止串；未发现提前截断 | 不把空列表与未传视为所有提供商实现绝对相同 |
| thinking | 续班试点已对齐disabled；退费保留enable_thinking=true | 旧退费实际reasoning_tokens=1685、新侧2992，均有reasoning，数量随输入结构/采样变化，不以数量差修参数 |

续班修正依据：原compare响应旧侧reasoning_tokens=0且无reasoning，新侧522且有reasoning。只读网关配置确认旧doubao/1.5重定向规则是thinking={type:disabled}、force=true；直用新模型绕过该规则。TEST Apollo仅修改agent255107338300556288（画像/摘要共享agent）的params.thinking，其余agent内容回读不变；releaseKey=20261123185859-188a6f5d9e0ed575。配置保留供测试使用，无生产变更、无代码commit。

同入口复验trace f059219f-2d7c-46c5-945e-fd3a9cdab509.0.3（19:00前后，TEST/SLS/app，版本91012878）：实收thinking.disabled；网关返回finish_reason=stop、无reasoning内容，reasoning_tokens字段为null（不能写成计数0）。原应用双路均成功。已保存thinking规则、变更前后配置、请求/响应日志和compare结果。

外部条件：若要求提供商最终HTTP body/隐式默认值逐字段证实，仍需网关出站观测；此不是本轮两例输入内容核对的新增验收前置。当前正扩大测试场景覆盖；完整异步落值仍未覆盖，生产发布不在授权内。其他应用是否需要thinking覆盖须按各自真实旧模型重定向规则判断，不能批量套用。

## 当前新增缺口与处置（扩大验证）

- PROD DMS 实查 `ai_application.gateway_core_prompt` 返回 0 行，当前缺列；发布前必须先完成 DDL，不能靠迁移开关关闭规避。证据：[生产表结构查询](artifacts/expanded-scope/prod-ddl-check.txt)。本次生产只读。
- 画像、SOP compare、分层有效样本已取 LiteLLM 双路请求，见 [续班报告](artifacts/expanded-renewal/report.md)。分层被强制 JSON 与直接原因文本契约冲突，空/有效样本均复现，TEST 格式配置已修正并同入口复验，见 [分层修正](artifacts/expanded-renewal/tier-fix.md)：trace `dabc87b7-0a58-4682-ae04-e6cfa2b3224f.0.3`，releaseKey `20261123192847-188a49b33afd47bc`。实收 text，返回原因文本，messages 与修正前相同；未触发 MQ/业务落库。
- SOP V2 已用真实历史 fixture 双路重放：13,647 字单 user 逐字一致，两侧10项SOP；见 [V2报告](artifacts/expanded-renewal/sop-real-entry.md)。旧 Seed-1.6 与新侧均有 reasoning，不套普通 compare 的1.5别名结论。未覆盖外围部门选择、知识表实时读取、去重和档案写回。
- 退费五场景双侧LiteLLM请求已取得。降退费trace 81e849b4-d461-4fd0-910a-154368d68bc0.0.3真实两轮dataset检索回灌，新侧遗漏；旅程原始日志无tools，不采纳子报告误用的降退费证据。精确差异与最小处理方案仍在合流。
- 静态风险适用性见 [核对报告](artifacts/expanded-diff/risk-applicability.md)：当前未发现 stream=true、TEST 缺列或六退费提示词为空，不据潜在风险盲改代码。

## 分层最终TEST参数

agent262172718139452416保留response_format=text，并补thinking.disabled；发布releaseKey `20261123193207-188aa6ecfba69670`。同有效样本复验trace `7a05052d-9094-4a00-aa88-bf44dcf0eb61.0.3`：实收disabled，stop，无reasoning_content，reasoning_tokens=null。其余agent完整map回读未变。证据：[思考参数复验](artifacts/expanded-renewal/thinking-followup.md)。未触发业务MQ或原因落库。

SOP普通compare及V2旧路均为Seed-1.6且有推理，本次未改SOP配置；原“旧路均1.5”已纠正。

## 退费精确输入差异

[五场景逐字段对照](artifacts/expanded-refund/report-exact.md)已按相同完整TID配对，旧/新轮次分别1/1、1/1、1/1、2/1、1/1。前四例业务user302字相等；素养业务正文在旧system中，迁移到新user，不能误判旧路缺数据。

- 旅程新指令要求已解决退费原因字段；该字段在2025年提交ec295156c已存在，refundless本次diff为空。保留既有字段，不修改历史保存逻辑；明确当前旧Dify与新模板并非完全相同。见 [契约归属](artifacts/expanded-renewal/journey-contract.md)。
- 课程体验/NPS实质指令保留，去掉旧标签并提升到真实system，角色语义有变。
- 降退费确认漏dataset检索；新侧另有Dify模板残留。
- 素养旧单system、新system+user，温度均0.7；未见检索工具，亦有模板残留。
- 降退费与素养的{{#sys.query#}}未展开已在LiteLLM实收确认，TEST提示词已最小修正并同输入复验；见 [模板修正](artifacts/expanded-refund/template-fix.md)，不代表检索遗漏解决。

当前汇总以 [审查交付](artifacts/expanded-scope/review-result.md) 为准；两行测试提示词已独立回读，最终trace为25046ce3-eb13-43e3-88ae-78859fd34e33.0.3及cd3eed1b-00db-4c9d-bdd4-a4cf7ad22c33.0.3。

## 原需求与调用次数复核（2026-11-23）

原始17个生产应用，问题建议高中/素养与降退费精品/素养共4个明确保留Dify，本轮目标13个不变；15是第一次排除问题建议两项后的中间口径，13是再排除降退费两学部后的当前口径，四项并集包含原明确不迁的两项。详见 [计数口径](artifacts/expanded-scope/scope-reconciliation.md)。本轮TEST10样本不是生产10/15/17项通过。9个旧/新各单次；仅TEST通用降退费旧2次、新1次，已核实它绑定【废弃】agent-chat。

生产精品/素养降退费目标为已发布advanced-chat：代码提取→知识检索→单LLM生成。不是两轮LLM；仍需迁移前置检索与context注入。撤回此前把TEST废弃两轮外推生产的口径；生产检索缺口依据已发布图而非TEST两轮。重试/compare双路/不同阶段不算内部多轮。

可支持TEST单次替换试验：画像、摘要、SOP V2、修正后的分层、课程体验、NPS本模板、修正后的素养服务建议本模板。根因弱样本与旅程指令差异不能列业务验收通过。生产学部与流程准入未全验，尤其素养TEST一次不代表生产可去掉检索。

详见[调用次数与证据](artifacts/expanded-scope/call-count-evidence.md)、[原材料对照](artifacts/expanded-renewal/source-scope.md)、[生产与废弃绑定](artifacts/expanded-refund/deprecated-binding.md)。本次未改路由/代码/生产；知识库保留决定已落实，未建设替代检索。

## TEST可替换场景实际交付

最终7个网关覆盖条目覆盖8类场景，配置发布及trace见 [TEST交付](artifacts/expanded-scope/test-replacement-delivery.md)。这代表测试环境生效，不代表生产13个应用全部通过。

## 最新收窄范围与prompt裁决

所有者已决定知识库4个生产应用保留Dify，TEST恢复旧路且复验完成。当前逐项结果和证据见 [当前prompt交接](artifacts/expanded-scope/current-prompt-handoff.md)；飞书第9节已全文回读。SOP完整一致，其他正文保留但messages不完全一致；素养NPS无双侧实收，不冒称通过。
