# 迁移前后 LiteLLM 同数据输入/输出对比

## 配对口径

以下五组均使用同一 TEST fixture：班级 `500775385189890048`、学员李明、2026-11-18/20 两段沟通、数学作业正确率 85%→62%、课程体验 5/10、NPS 3/10、家长“考虑退费/增加答疑和针对性练习可能继续”。迁移前是 Dify 旧侧实收，迁移后是网关 TEST 实收；每组用同一完整 LiteLLM TID 配对，旧/新请求与响应分别保存在 `exact-*.json` 和 `1~5-*.json`。参数差异与系统/user 逐字 diff 见 `report-exact.md`。

| 场景 | LiteLLM 配对（迁移前 → 迁移后） | 实收输入（具体片段） | 参数差异 | 实际输出（具体片段） | 差异判断 |
|---|---|---|---|---|---|
| 退费旅程 | `bfd44413-31f5-493d-904b-e670783ff2c4.0.3`；2026-11-23 19:22:49 → 19:23:24 | 旧 system 2966 字，含“按时间正序…最多5个阶段”；新 system 3290 字，新增 `resolvedRefundReasonList` 及已解决原因字段；两侧 user 均 302 字，均含同一两段沟通原文 | 旧 `deepseek/DeepSeek-R1-250528`、未传 max_tokens；新 `deepseek-flash`、8192；旧 stream=true，新未显式传 | 旧输出 14195 字，含 `<think>` 和复杂 JSON 生成过程；新输出 1084 字，直接返回 `tutoringSummary/tutoringItems` JSON | 输入变化是已解决退费原因字段和格式规则变化；输出长度/格式差异不能归因随机性。两侧 user 业务数据相同。 |
| 课程体验 | `e02d7092-ee55-4e73-b731-b6f31ef2fb6e.0.3`；19:23:42 → 19:23:55 | 旧 system 2633 字；新 2621 字；两侧 user 均 302 字，包含相同班级、作业下降、课程节奏/互动、NPS及沟通原文。新侧去掉旧 flat 标签并调整输出要求 | 旧 deepseek R1、未传 max_tokens；新 deepseek-flash、8192；旧 stream=true，新未显式传 | 旧输出 3214 字，含 `<think>`；新输出 503 字，返回 `courseExperienceSummary` 与退费原因摘要 | 主要是角色/模板包装和模型参数差异；业务 user 未变。不能仅凭输出文字不同判迁移失败。 |
| NPS | `d2003cc1-b573-4e1c-8918-d3a4d162fe62.0.3`；19:24:27 → 19:24:35 | 旧 system 485 字；新 473 字；两侧 user 均 302 字。新侧保留本班级/其他班级区分，旧侧 system 多 12 字旧 flat 标签 | 旧 deepseek R1、未传 max_tokens；新 deepseek-flash、8192；旧 stream=true，新未显式传 | 旧输出 1461 字，含 `<think>`；新输出 196 字，直接给出“本班级分析/其他班级暂无数据” | 业务判断一致：作业反馈慢、个性化不足、考虑退费；输出差异主要来自 think/格式及参数。 |
| 降退费服务建议 | `81e849b4-d461-4fd0-910a-154368d68bc0.0.3`；19:24:45 → 19:24:56 | 旧首轮 system 1513 字、user 302 字；旧第二轮额外有 assistant/tool/tool，tool 结果 1363/1152 字，声明 dataset 检索；新只有 system 1613 字+user 302 字，无 tools/tool message | 旧 `tool_choice=auto`、deepseek R1；新无 tools、deepseek-flash、8192 | 旧首轮 1690 字，含“Let me use the tool/query the tool”；新 328 字，返回具体 24 小时答疑、3 道练习、48 小时反馈 JSON | **实质缺口**：旧侧存在两轮工具回灌，迁移后没有检索上下文；不能归因模型随机性。该场景未完成对等迁移。 |
| 素养服务建议 | `5e258635-6bba-4358-bb49-8c6017142140.0.3`；19:25:17 → 19:25:33 | 旧 system 1983 字，业务数据嵌在 system；旧无 user。新 system 1613 字+user 302 字，业务数据拆到 user；旧/新均无 tools | 旧 deepseek R1、temperature=0.7、stream=true；新 deepseek-flash、8192、temperature=0.7 | 旧输出 3087 字，含 `<think>`；新输出 303 字，直接返回专属答疑、分层练习、当天反馈 JSON | 旧 user 缺席不代表业务数据缺失，旧 system 内含同一业务正文；角色包装和模板长度不同，业务约束需按正文比较。 |

## 证据边界

- 五组是同一 fixture 的历史双侧实收，覆盖 2026-11-23 TEST `compareAiApplication` 样本；不是生产四应用全量，也不是 10 个生产变体全量。
- 降退费旧侧工具调用只由 LiteLLM messages 中的 `assistant/tool` 和两段 tool content 证明；compare 响应没有独立工具协议字段，不能继续推断工具实际返回了什么业务结果。迁移后确实没有 tools/tool message，属于已验证输入缺口。
- 输出不同同时受 system/user 形态、模型、max_tokens、stream/think 默认值影响；不能把所有差异归为模型随机性。输出相似也不能掩盖输入缺口。
- 知识库 Java 隔离样本只有迁移后单侧证据（trace `3eaabb15-c22b-48f9-bcb4-7b0fd7783511.0.3`），没有同一生产 Dify 旧侧 LiteLLM 配对，因此不纳入“前后对比表”。

## 完整原文索引

- 五组完整 LiteLLM messages：`exact-旅程-prod-1.json`、`exact-旅程-test-1.json`、`exact-课程体验-prod-1.json`、`exact-课程体验-test-1.json`、`exact-NPS-prod-1.json`、`exact-NPS-test-1.json`、`exact-降退费-prod-1.json`、`exact-降退费-prod-2.json`、`exact-降退费-test-1.json`、`exact-素养建议-prod-1.json`、`exact-素养建议-test-1.json`。
- 五组业务响应：`1-退费旅程分析.json`、`2-退费课程体验分析.json`、`3-退费NPS分析.json`、`4-降退费服务建议.json`、`5-素养服务建议.json`。
- 参数和逐字差异：`report-exact.md`、对应 `exact-*-system.diff` / `exact-*-user.diff`。
