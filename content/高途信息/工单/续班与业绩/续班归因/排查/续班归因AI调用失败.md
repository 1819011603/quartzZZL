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

## 排查

1. **定位**：`qingzhou-observe` 查 `student-data` 错误日志（token `RenewalReasoningService` / `AbstractRenewalReasonContextService`）；堆积曲线走 MQ 工具。
2. **两类根因与处置**：
   - **截断**（`finish_reason=length`，通常占少数）：模型输出超上限。归因模型是**推理模型**（响应含 `reasoning_content` / `usage...reasoning_tokens`，这些 token 也占 `max_tokens`）。处置：抬 Apollo `renewal.reason.llm.max-tokens`（`student-data`/PROD/application，需发布）。⚠️ 网关兜底值 `llm.gateway.default-max-tokens` 对**显式传了 max_tokens 的调用方无效**——归因代码显式传了，所以只改它没用。
   - **非法 JSON**（`parse error`，通常占多数）：模型在 JSON 字符串值里打了**未转义半角引号**（实测样例 ASCII `"` 数百个、中文引号 0 个；也有输出过长被截成半截）。处置：给 **LLM 网关该 caller 的路由**加默认参数 `response_format={"type":"json_object"}`（`force=false` 即可）；或改提示词约束引号、减少原文回抄。
3. **网关 / 提示词 / Apollo 入口**：网关路由与提示词配置走 skill `llm-gateway-admin`；Apollo key 读写走 skill `apollo-config`。⚠️ **caller 别认错**：student-data 的 AI 调用按 Apollo `llm.gateway.api-key`（= **gps-ai** 的 key）认证，落在 **caller `gps-ai`** 的路由上，不是 `student-data-ai`；且路由 test/prod 各一套，配 test ≠ 配 prod。

## 验证

- **配置生效**：Apollo `apollo_get_key` 读回**已发布**值；网关路由 `callerRoute/get` 读回新默认参数。
- **业务疗效**：`student-data` 日志里 `ai invoke error` / `parse error` 频次下降、消费组堆积回落到 0，才算修好；只看到「已发布 / 已配置 / 处理中减少」不算。
- 不算通过：`apollo_set_key` 返回成功（那是草稿）、`callerRoute/save` 返回 200、告警认领。