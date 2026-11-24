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

2026-11-24继续用pod-terminal核查：当前TEST service `baijia.gaotu.Business.operation-workbench.student-data`列出的Running/UP Pod为 `student-data-867c48c996-pcd54`(10.255.166.59)、`student-data-6d4b796dc9-hgznq`(10.218.249.39)、`student-data-58ddf65fb6-ht5hl`(10.218.251.177)，此前trace目标10.218.237.104已不在当前Pod列表。当前抽查Pod `/apps/srv/instance/app.jar` 无 `DifyDatasetGatewayTestService`类，说明当前服务实例仍是旧镜像，不能用它读取87124f42的运行异常。

因此本轮无法在已消失的目标实例上执行arthas throwExp；不是代码静态推断，而是运行Pod已被替换且当前Pod未包含新类。未重复部署。待主Worker已有部署流程将87124f42部署到TEST后，再从新Pod执行一次入口；届时ACL真实异常需在新实例日志/arthas读取。

## 目标泳道核实（补充）

明确使用 `pod_term --env dev --pod-name student-data-7cd659b66-f478t`，该Pod为10.218.237.104、Running/Eureka UP，JVM参数含 `-Deureka.instance.metadataMap.trafficEnv=test-gtbg-dev-1`，即目标泳道已核实。Arthas `jad`确认运行类位置为 `app.jar!/BOOT-INF/lib/student-data-service-1.0.0.jar!/`，方法真实签名为六参数：`retrieveAndComplete(String,String,String,String,String,Object)`，与请求参数数量一致；此前“目标Pod消失/签名不匹配”均已推翻并保留本段证据。

该Pod日志确认：09:30:47 Retriever调用后创建AI同步任务记录，解析override为agent1795457739670155、platformType=2、model=deepseek-flash；随后ACL仍统一报“未找到方法”。未取得目标方法throwExp（watch命令在等待期间被中断），因此AiApplicationExecutor内部失败原因仍未知。未改代码/配置，未重复业务调用。
