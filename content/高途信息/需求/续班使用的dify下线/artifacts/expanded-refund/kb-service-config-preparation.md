# TEST配置准备状态

仅准备，尚未写Apollo或建数据库对象。当前工作树/private/tmp/student-data-xuban-review-20261123，HEAD91012878d，两个新Java文件尚未提交；文件SHA及模板SHA见kb-service-config-preparation.json。

已按DifyDatasetRetriever当前7个@Value准备kb-service-config-proposed-redacted.json。token从0600临时文件临场读取，不落配置提案。完整生产素养LLM system文本（含sys.query占位与末尾//）保存kb-isolated-system-template.txt，未替换为摘录。

当前DifyDatasetGatewayTestService.retrieveAndComplete仍通过AiApplicationExecutor，参数包含aiApplicationName；强制platformType=2。因此若维持此实现，需要隔离app/agent并核对gateway_core_prompt与DynamicPromptGenerator输出；若实现改直接Accessor则取消建库步骤。尚未自行决定。

协调两次均失败：W1-073b38不符合原生agent命名规则，w1_073b38路径不存在。不可假称已与实现方确认。需要主Worker转达最终调用方式与Apollo namespace/cluster，再完成写入发布。

TEST/default/application发布预检当前无草稿差异；尚未确认test-gtbg-dev-1是否应独立cluster或使用现有default/application，不新建cluster。现有4个知识库路由、生产、已完成TEST检索资源均未修改。未新增凭据或数据库行；原TEST密钥仍0600保留供后续接入。
