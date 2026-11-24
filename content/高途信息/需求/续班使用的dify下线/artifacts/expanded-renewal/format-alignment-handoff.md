# 旧Dify格式应用级实现（进行中）

基线8becd39fb，worktree /private/tmp/student-data-xuban-review-20261123。

配置键 `llm.gateway.application-prompt-formats`（Apollo JSON，默认 `{}`），以应用编号字符串为键。值 `USER_FLAT`：用原DynamicPromptGenerator.generate产出单user；`SYSTEM_USER_FLAT`：外层gateway_core_prompt原文+一个换行，内层user保持原generate结果。不覆盖原core，不重复外层模板。只在普通网关路径读取，V2不改，Dify路径不改。13项中SOP继续V2无需配置；4个知识库不配置。其它模型参数未修改。

非空错误模式、B模式缺外部system、A模式存在外部system均拒绝，避免静默丢模板。换行依据Dify simple_prompt_transform.py:163-164、208。

当前修改AiApplicationExecutor、DynamicPromptGenerator，新增LegacyDifyPromptTest（6项）。正在最终编译，后续JUnitCore实际执行及提交推送尚未完成；不能据此宣称已部署实收一致。

## 本地交付

提交56b53f3c5已推送feature-xuban-dify-offline。mvn8 -pl student-data-service -am test-compile -DskipTests成功（/tmp/format-build-final.log）；JUnitCore实际执行6项全部通过（/tmp/format-junit.log）；最终Executor单独javac成功（/tmp/format-final-javac.log）。未部署、未改Apollo或数据库、未业务调用。等待主Worker按应用编号配置上述键并统一部署实收。AICR异步评审尚未取得本提交结果。
