# 续班剩余场景 LiteLLM 前后对照（历史实收）

本表只复用归档中的历史 LiteLLM 日志和请求/响应文件，不重跑业务。配对依据是同一业务 fixture、同一 TID（旧侧 `caller_0167`，新侧 `gps-ai`）及相邻调用时间；模型、参数和输出均按实收记录读取。新旧输出不应仅以文字不同判定失败，需先区分模板、角色、模型和参数差异。

| 场景 | 配对证据 | LiteLLM 输入 | 参数/模型 | 原始输出 | 结论 |
|---|---|---|---|---|---|
| 用户画像 | `profile-prod-logs-litellm.json` TID `2a9ff650-ba6f-4bf2-93f8-88034f864c93.0.3`；`profile-test-logs-litellm.json` 同 TID | 旧 body 9001B、system/user 包装；新 8951B，system 直接承载相同业务字段；两侧完整 messages 见 `profile-*-received.json` | 旧 `Doubao-1-5-pro-32k`、stream=true；新 `doubao-seed-2.0-lite`、max_tokens=8192、JSON response_format、thinking | 旧/新业务入口原文分别见 `profile-prod-received.json`、`profile-test-received.json`；TEST `profile-response.json` messageId `b663ab7f-74b6-4ca7-8ed4-fd896579677f` | 业务字段保留；system 包装、模型和 JSON/think 参数变化，无法做逐字等价。 |
| 服务 SOP V2 | `sop-v2-1-received.json` → `sop-v2-2-received.json`；请求/响应文件成对 | 两侧 messages 长度接近（15118/15135B），同一 SOP fixture；新侧显式 system+user 与 JSON 参数 | 旧 `Doubao-Seed-1-6`、stream=true；新侧 `doubao-seed-2.0-lite`、max_tokens=8192、response_format JSON；旧 response 含 `<think>` | 旧 messageId `f636be0b-5315-4c0c-872d-03277f71a17a`；新 `chatcmpl-c3cdbf20a71d4f3ca20cdf3a098ed8dd`；两份完整响应分别在 `sop-v2-1-response.json`、`sop-v2-2-response.json` | 核心 SOP 条目与评分均保留；输出格式从 think+JSON fenced 变为纯 JSON，差异主要由参数/模板造成。 |
| 预测分层原因（有效修正版） | `tier-valid-prod-received.json`、`tier-valid-test-received.json`；同一业务样本 | 两侧业务数据一致，system/user 逐字差异见 `tier-valid-prompt.diff` | 旧 `Doubao-1-5-pro-32k`、stream=true；新 `doubao-seed-2.0-lite`、max_tokens=8192、JSON response_format | `tier-valid-response.json`：旧入口判断“完成度31.82%、互动低、无预报名”；gateway 返回同因果结论，messageId `chatcmpl-6fd16ca300494d3cb077954e7b299f96` | 语义一致；输出压缩为单字段 JSON，属于格式/模型差异。另有 `tier-test-*` 早期证据已修正，不与本配对混用。 |
| 素养 NPS | `suyang-old-received.json`、`suyang-new-received.json`、`suyang-received-comparison.json` | `full_messages_equal=false`；system 除尾换行相等；业务正文 `business_exact_equal=true`；旧/新 roles 均 system,user | 参数明细以对应日志和 `suyang-actual-input-verification.md` 为准；新侧为复制的素养模板 TEST fixture | 原始 messages 与生成检查见 `suyang-nps-generation-check.md`、`suyang-nps-copy-validation.md` | 业务输入完全一致，差异仅外层消息包装/参数；该项属于 TEST 复制验证，不能当生产旧侧实收。 |

## 逐场景证据边界

- 用户画像、SOP、分层均保存了完整请求对象和 LiteLLM 日志；业务入口响应与 LiteLLM 原始响应分别保存，不能把入口 JSON 当作 LiteLLM 原文。
- SOP 的普通 `sop-prod-logs-litellm.json` 与 `sop-test-logs-litellm.json` 不构成有效配对（TEST 列表为空）；本表使用 `sop-v2-1/2` 成对文件。
- 素养 NPS 的 `business_exact_equal=true` 只证明输入业务正文相等；新侧为 TEST 复制模板，缺少生产同模板 LiteLLM 实收，故不宣称生产等价。
- 知识库隔离 Java trace `3eaabb15-c22b-48f9-bcb4-7b0fd7783511.0.3` 只有迁移后单侧证据，排除在前后表之外。

## 原始文件索引

`profile-{prod,test}-received.json`、`profile-{prod,test}-logs-litellm.json`、`profile-response.json`；`sop-v2-{1,2}-{received,request,response}.json`；`tier-valid-{prod,test}-received.json`、`tier-valid-response.json`、`tier-valid-prompt.diff`；`suyang-{old,new}-received.json`、`suyang-received-comparison.json`。完整原始输出保留在这些 JSON，正文仅列可核验摘要。
