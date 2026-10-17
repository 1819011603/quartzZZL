# 续班归因 · AI 调用失败导致 MQ 堆积

> **只解决**：续班归因消费组堆积/告警，且 `student-data` 日志里是 **AI 调用失败**（网关截断或模型返回非法 JSON）。
> 其它情况（消费组根本没消费、位点异常、班级任务没投出去）走 MQ 工具（`toolbox` → `aliyun-console`）与 `gaotu-ticket-triage`，与本文件无关。

## 判定入口

- **消费组 / topic**：`GID_student-data_renewal_reason_task_prod` / `student-data_renewal_reason_task_prod`（tag `RENEWAL_REASONING_TASK`）。堆积分**就绪**与**处理中**，看曲线别用位点差（`ConsoleConsumerProgress.accumulate` 会被 tag 过滤放大）。
- **服务**：`student-data`。两类错误日志：
  - `RenewalReasoningService | reasoningEvent | ai invoke error`，异常 `BusinessException: AI应用任务执行失败: LLM网关响应被截断, finish_reason=length`
  - `AbstractRenewalReasonContextService | parseSummary | parse error`，异常 `com.alibaba.fastjson.JSONException: syntax error, unexpect token error`（或 `not close json text`）
- **链路**：班级任务 `RenewalReasonTaskService.handleClazzTask` 收窄后逐学员发 MQ → `RenewalReasonTaskConsumer` → `handleSingleUser` → `RenewalReasoningService.reasoningEvent` →（三路上下文 + md5 幂等）→ LLM 网关 → `saveReasoningResult` 落 `ees_data.ai_app_clazz_user_scene` → 回写花名册 ES。
  失败即 `HANDLE_CODE_FAIL` → `Action.ReconsumeLater`（模型调用层内还有 `ai_application.retry_times` 次重试），**确定性失败**（同样的输入必然再失败）会反复重试到 `maxReconsumeTimes`，表现为堆积。
  **处理策略的坑**：把「解析失败/截断」一律当「可重试」，确定性失败会被放大成堆积。正确顺序是**先从源头消除失败**（改提示词 / 加 `response_format` / 抬 max-tokens），重试只兜真·瞬时抖动；解析失败本可降级为放弃（课题：`handleResult` 里 parse 失败返回 null 即判 FAIL）。

## 排查

1. **定位**：`qingzhou-observe` 查 `student-data` 错误日志（token `RenewalReasoningService` / `AbstractRenewalReasonContextService`）；堆积曲线走 MQ 工具。
2. **两类根因与处置**：
   - **截断**（`finish_reason=length`，通常占少数）：模型输出超上限。归因模型是**推理模型**（响应含 `reasoning_content` / `usage...reasoning_tokens`，这些 token 也占 `max_tokens`）。处置：抬 Apollo `renewal.reason.llm.max-tokens`（`student-data`/PROD/application，需发布）。⚠️ 网关兜底值 `llm.gateway.default-max-tokens` 对**显式传了 max_tokens 的调用方无效**——归因代码显式传了，所以只改它没用。
   - **非法 JSON**（`parse error`，通常占多数）：模型在 JSON 字符串值里打了**未转义半角引号**（实测答案 ASCII `"` 中位 ~128、中文引号 ~0）。
     **首选处置——改提示词**：在 `prompt_config` 的 `core_prompt` 末尾加「输出必须是合法 JSON；字符串值内部禁止半角双引号，需要引用原文/关键词时改用中文引号（“” 或 「」）」。
     已线上验证（2026-10-17 续班归因）：12 个「重试 10 次仍失败」的学员重跑 **12/12 成功**，改后 `parse error` 基本归零。**提示词有效性 > 代码里的重试**——不要靠重试兜确定性失败。
     **备选/兜底**：给网关 caller 路由加 `response_format={"type":"json_object"}`（`force=false`）——但 **prod 路由改动走审批、非即时生效**，见 skill `llm-gateway-admin`。
3. **网关 / 提示词 / Apollo 入口**：网关路由走 skill `llm-gateway-admin`；提示词在 `ees_data.prompt_config`（改 `core_prompt`；prod 可经 acl 桥调 `PromptConfigService#updatePromptConfig`）；Apollo key 读写走 `apollo-config`。⚠️ **caller 别认错**：student-data 的 AI 调用按 Apollo `llm.gateway.api-key`（= **gps-ai** 的 key）认证，落在 **caller `gps-ai`** 上（caller `gps-ai` 就是 student-data 自己的 caller，nid `baijia.gt.jiaoyan.ees-be.student-data-gps`，改它只影响 student-data 的调用），不是 `student-data-ai`；路由 test/prod 各一套。
4. **重跑失败学员（验证 + 补数）**：从 `student-data` 日志取 `parse error` 记录的 `(clazzNumber, userId)`，用 acl 桥调 `RenewalReasonTaskService#handleSingleUser(clazzNumber, userId, false)` 重跑——失败学员无落库→必调模型，已成功的上下文未变→幂等跳过。返回 `handleCode`：`2` 成功 / `1` 未变化(跳过) / `0` 跳过 / `-1` 失败。重跑既验证修复、也补上失败学员缺失的归因结果。

## 验证

- **配置生效**：Apollo `apollo_get_key` 读回**已发布**值；提示词用 acl 桥 / `prompt_config` 读回；网关路由 `callerRoute/get` 读回新默认参数。
- **业务疗效（首选）**：`student-data` 日志里 `ai invoke error` / `parse error` 频次下降、消费组堆积回落到 0。**最快验证**：抽几个失败学员按「重跑」重跑，`handleCode=2` 且改后日志 `parse error` 归零 = 修好。
- 不算通过：`apollo_set_key` 返回成功（那是草稿）、`callerRoute/save` 返回 200 或生成审批单、告警认领。