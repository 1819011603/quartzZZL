# TEST Java知识库入口E2E验证

时间：2026-11-24 09:30（北京时间），TEST泳道test-gtbg-dev-1，调用commit请求目标87124f42，实际Pod由pipeline1360348/6909717cc及student-data-7cd659b66-f478t可见。生产未调用生成、未写配置或数据。

## 请求与结果

入口：`DifyDatasetGatewayTestService#retrieveAndComplete`，请求文件`/tmp/kb-java-e2e/request.json`，dataset=`0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce`，fullBusinessQuery包含班级、学员、老师、作业变化、沟通原话和退费上下文；retrievalQuery为“退费直接原因/退费原因分类”。

入口响应HTTP200但业务返回：`未找到方法 retrieveAndComplete`，不是成功证据。入口trace：`2a2b1e51-d77b-4082-95fb-cc71abcf86ed.0.3`，响应/headers保存在`/tmp/kb-java-e2e/e2e-response.json`、`e2e-headers.txt`，完整日志`e2e-trace-sls.json`。

同一trace的调用链包含TEST Dify Service API检索span：`POST http://test-dify-open.baijia.com/dify/api/v1/datasets/0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce/retrieve`，HTTP/sc=200，目标Pod私网`10.218.237.104`。这证明请求实际进入了Retriever并成功访问TEST dataset；但最终ACL结果仍报方法未找到，未形成可采信的完整模型生成结果，不能宣称端到端跑通。日志未发现生产域名或生产dataset请求。

## 解释与边界

同一trace已显示test-dify-open检索200，说明该次请求确实访问了TEST Service API；但ACL返回“未找到方法”仍可能是反射匹配、内部异常包装或运行版本等原因，当前不下定论。需按目标namespace核对Pod、镜像commit并读取真实异常。Retriever已支持手动datasetId/query、baseUrl配置化和TEST environment开关，未新增参数API；密钥保持Apollo，不经ACL参数传递。

已有真实直接Service API检索4条证据：`expanded-refund/kb-test-retrieval/real-test-retrieve.json`。本次Java入口尚未证明完整system（预期约1390字）、业务query和4条片段进入LiteLLM，也没有可用LiteLLM生成trace。生产只读授权未用于生成；后续若需生产知识库只读检索，须由主Worker确认身份、域名和dataset后单独执行，仍不得生产生成或写入。

## 根因定位补充

读取 `student-data-facade/.../AclServiceCompareController.findMethod`：方法调用发生 `InvocationTargetException` 时，控制器吞掉目标异常并继续，最终统一写成“未找到方法”。因此该文案不能证明签名不存在；同一原trace已证明方法体至少执行到Retriever（Dify retrieve 200）。

再次用空context复验，入口trace `80f1cd25-e586-44cb-b8f7-cb892f5941c8.0.3` 仍返回“未找到方法”，说明不是context Map转换导致的单一问题。TEST应用1795457739670157/agent1795457739670155存在且platform_type=2，gateway_core_prompt已配置；TEST数据库未出现对应call_task_result记录。当前最小根因范围收敛为：方法体在Retriever之后的AiApplicationExecutor阶段抛异常，或运行实例与请求签名/代码版本不一致；ACL未回传真实目标异常。未修改共享ACL以暴露异常，避免扩大范围。

## Pod/运行类核查

此前查询使用默认 test 环境，非目标 dev 泳道；其 Pod 列表不能证明目标实例消失，该推断已撤回。

## 目标泳道核实（补充）

明确使用 `pod_term --env dev --pod-name student-data-7cd659b66-f478t`，该Pod为10.218.237.104、Running/Eureka UP，JVM参数含 `-Deureka.instance.metadataMap.trafficEnv=test-gtbg-dev-1`，即目标泳道已核实。Arthas `jad`确认运行类位置为 `app.jar!/BOOT-INF/lib/student-data-service-1.0.0.jar!/`，方法真实签名为六参数：`retrieveAndComplete(String,String,String,String,String,Object)`，与请求参数数量一致；此前“目标Pod消失/签名不匹配”均已推翻并保留本段证据。

该Pod日志确认：09:30:47 Retriever调用后创建AI同步任务记录，解析override为agent1795457739670155、platformType=2、model=deepseek-flash；随后ACL仍统一报“未找到方法”。未取得目标方法throwExp（watch命令在等待期间被中断），因此AiApplicationExecutor内部失败原因仍未知。未改代码/配置，未重复业务调用。

## 实际异常与修复

Arthas watch 单次命中取得真实 NPE：`DynamicPromptGenerator.getAfterProcessorPrompt:167`，完整栈 `/tmp/kb-java-e2e/watch.txt`。隔离应用 `1795457739670157` 原 `auto_use_current_version=0` 指向历史版本 `1795457739670160`，实际 prompt_config_history 查询为0行，导致 promptConfigBO=null。已仅将该TEST隔离应用 auto_use_current_version 改1，独立连接回读确认；现用当前模板1795457739670159。无需代码修复或部署。watch已reset并stop。修复后同入口复验进行中，证据 fixed-headers.txt/fixed-response.json。

## 最终验证结果（主Worker复核）

6909717c / TEST test-gtbg-dev-1 已完成 Java自动检索→上下文拼装→TEST模型生成。成功trace：`3eaabb15-c22b-48f9-bcb4-7b0fd7783511.0.3`；入口code=0，返回suggestion、recallSuccessRate、recallReason。

真实异常为隔离应用指定不存在的prompt_config_history版本，DynamicPromptGenerator.getAfterProcessorPrompt:167发生NPE，ACL吞掉异常。仅将TEST application 1795457739670157的auto_use_current_version从0改1并回读；无新增代码、部署或Apollo发布。

主Worker独立解析已落盘LiteLLM请求：system 1390字及SHA256与配置完全一致；完整业务query保留；与独立Service API返回的4条segment逐条比较，全部完整包含。断言见kb-e2e-input-assertions.json；响应及日志见同目录kb-e2e-fixed-response.json、kb-e2e-litellm-fixed.json。

该结果仅覆盖隔离TEST样本，不证明生产四个知识库应用等价，也不证明agent工具循环。生产真实地址与原dataset受控探测返回401，TEST凭据不适用；仍需生产有效授权服务凭据再验证目标空间权限，不能将401与此前个人Console空间403混同。未执行生产生成或生产写入。

监听已reset并停止，无在途业务调用。隔离TEST数据、dataset及配置保留供复现，未清理；原4个知识库应用继续Dify。
