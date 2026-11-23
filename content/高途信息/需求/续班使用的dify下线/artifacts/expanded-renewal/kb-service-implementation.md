# TEST知识库Service API接入实现

2026-11-24，代码基线91012878隔离worktree；仅TEST验证，未部署、未提交、未修改生产。

## 实现

新增 `DifyDatasetRetriever`：

- 默认关闭，且强制 `ai.dify.dataset.retrieve.environment=test`；默认 base URL 为已验证 TEST Service API `https://test-dify-open.baijia.com/dify/api/v1`，避免漏配时误发生产，防止生产误用。
- datasetId必须为UUID，避免拼接路径注入。
- Bearer凭证只从配置读取，不记录、不返回；异常日志只记datasetId和异常类型，不输出异常正文。
- POST请求显式`Content-Type: application/json`。
- 请求契约使用Dify `retrieval_model`：`search_method`、`top_k`、`reranking_enable`均配置化；默认`keyword_search`、4、false，符合本次TEST economy keyword证据，不硬编码生产检索策略。
- 响应只提取`records[].segment.content`，空结果抛业务异常，不静默继续。

新增 `DifyDatasetGatewayTestService`，仅提供独立TEST入口：`retrieveAndComplete(datasetId, aiApplicationName, fullBusinessQuery, retrievalQuery, userTag, context)`。它先用`retrievalQuery`检索，再把完整`fullBusinessQuery`原文和全部命中片段拼入userQuery，调用`AiApplicationExecutor`并强制`platformType=2`，因此走正常system prompt、context数据和LlmGatewayAccessor。正式四个应用没有引用该服务。

## 验证

- 2026-11-24新增实际执行结果：JDK8 `org.junit.runner.JUnitCore` 执行 `DifyDatasetRetrieverTests`，**OK (6 tests)**，覆盖请求契约、关闭fail closed、缺凭证fail closed、完整业务输入与4条上下文保留、platformType=2。Surefire在该工程配置下仍显示 Tests run: 0，实际执行以JUnitCore结果为准。
- 已提交并推送本人分支 `feature-xuban-dify-offline`：commit/远端SHA均为 `87124f42e2a3d5f71f561868356ae6d25796fa0d`，提交 `feat(ai): TEST知识库前置检索接入`，仅包含上述3个新增Java/测试文件，未建MR。

真实TEST Service API已由同轮现场验证：dataset `0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce`，Bearer检索返回4条，证据为`expanded-refund/kb-test-retrieval/real-test-retrieve.json`；凭证仅在`/tmp/kb-test-service-key.json`（0600），未读取、未写入代码或报告。

`DifyDatasetRetrieverTests`覆盖：只取非空segment内容、缺records返回空、`retrieval_model`契约、keyword_search可配置；项目无JUnit依赖导致Surefire不发现测试类（`Tests run: 0`），但编译成功。完整`mvn8 -pl student-data -am -DskipTests compile`在91012878基线及新增代码下BUILD SUCCESS（约1:40）。定向测试命令完成编译后以0退出但执行0条，不能宣称测试方法已运行。

## 当前边界

尚未用真实TEST凭证从部署应用经该新Java入口跑一次端到端；原因是新增入口尚未部署，且本轮禁止部署/提交。Service API检索本身已用独立curl证据跑通；Java请求body、完整业务输入保留和网关入口由单元代码/编译检查覆盖。后续统一审查时需在TEST配置启用、部署后用非生产业务样本验证LiteLLM trace，并回读`fullBusinessQuery`字段未丢失。
