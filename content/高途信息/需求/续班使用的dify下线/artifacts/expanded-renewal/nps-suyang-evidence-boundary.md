# 素养 NPS 实收证据边界（2026-11-23）

## 结论

素养 NPS 的旧/新 LiteLLM 双侧实收仍未取得，不能判定输入一致，也不能把精品 NPS 的实收结论外推到素养。

## 已实际尝试

1. **核对生产绑定**：只读查询 `ai_application`/`ai_agent` 并用 agent 的 Dify `/v1/info` 核对归属。素养 NPS 为 `ai_application=261424803504732160`、`ai_agent=261424755557579776`，Dify 应用为“【素养】课程NPS分析”；精品 NPS 为 `ai_application=256996044560210944`、`ai_agent=256995228385317888`。
2. **核对两学部模板**：生产素养模板正文 321 字，精品模板正文 473 字，具体差异见 `current-NPS-department-template.diff`；两者不是同一提示词变体。
3. **核对 TEST 映射与已有实收**：TEST Apollo 只有通用“退费NPS分析” agent `255743847351465984`，已有实收 trace `d2003cc1-b573-4e1c-8918-d3a4d162fe62.0.3` 对应精品模板；没有独立的 TEST 素养 NPS Dify 映射或旧侧 trace。
4. **补做安全的本地对照**：按 `DynamicPromptGenerator` 规则，将当前 321 字素养模板与同一 302 字业务 user 组合，生成 `nps-suyang-generated-messages.json`，并验证业务 user 未变。这是确定性本地生成，不是 LiteLLM 实收。

## 为什么不能继续用当前入口补齐

把生产素养 `app/key` 放入 TEST compare 会调用生产 Dify 应用；当前授权仅允许生产只读查询，不允许生产推理。把素养模板复制到 TEST 精品 NPS 只能得到新侧消息，仍没有旧素养侧可比请求，不能形成双侧证据。当前缺少的最小条件是：提供一个绑定素养 NPS 的 TEST Dify 镜像/测试 app，或由所有者另行授权受控的生产推理；在条件具备前，本场景结论保持“未验证”。

证据：`prompt-current-refund.md`、`refund-current-suyang-nps.json`、`current-NPS-department-template.diff`、`nps-suyang-generation-check.json`、TEST 映射回读 `trace-recheck-20261123/dify-override-after.json`。
