# SSE/严格参数实现交接（暂停，未提交）

基线56b53f3c5，worktree /private/tmp/student-data-xuban-review-20261123。owner上下文80%指令后停止新增实施、commit/push/部署/配置/业务调用。不得把本轮实现当作已完成。

## 已做

- AiAgentAccessorOverride/AiModelCallOption新增Boolean omitMaxTokens，Executor透传；为true时跳过command/default max token，buildRequestBody删除max_tokens键（不是null）。未配置沿用原行为。
- params.stream=true选择SSE聚合。Hutool execute(true)取得响应流；try-with-resources关闭HttpResponse。非流式仍读取完整JSON。
- 新增GatewaySseReader，以BufferedReader支持UTF-8跨网络分片、多行data和空行事件分隔；聚合index0 content，保存id/model/usage；须stop及[DONE]，错误/length/断流拒绝。
- LlmGatewayResponse/AiModelResponse/DifyResponse新增usage透传，没提供时为空。
- 新增GatewaySseReaderTest，写了多行/单字节网络分片/usage/缺DONE/缺finish/length/error/IO异常，以及反射测试max_tokens真省略、stream透传、thinking不凭空加入和8192旧行为。

## 配置契约

`ai.agent.accessor.override.map[agent].omitMaxTokens=true`；`params.stream=true`。thinking是否出现仍由params显式字段控制，Java不注入。模型由原override.model选择，待主Worker映射调查决定旧别名。messages实现不改。费用身份需求尚未接到主Worker最终事实/改动要求，没有硬编码身份。

## 验证与在途

第一次mvn8 -pl student-data-service -am test-compile -DskipTests成功：/tmp/sse-build.log。期间之后增加usage透传/测试及格式整理，因此不作为最终版本完整验证。
最终同命令在途exec session **22732**，日志 **/tmp/sse-build-final.log**。可write_stdin(session_id=22732,chars="")读取；无部署或业务请求。首轮session73718已退出。
**JUnitCore尚未执行**；不能用test-compile称单测通过。既有format的6项通过不覆盖SSE。

## 续接待办（恢复授权后）

1. 先读最终编译结果/当前git diff，勿重建已改文件。
2. 完成自审及测试补足：真正多delta拼接、HTTP Content-Type/非SSE返回、event:error无空格形式、格式错误、非法choice等边界；现实现event错误检测只认精确`event: error`。确认严格要求空行后[DONE]是否与目标流兼容。
3. 检查异常是否含敏感正文、响应关闭及读取超时；现JSON解析异常未经专门脱敏，不宣称已完成安全复核。
4. 用已有/tmp/student-data-test.cp实际JUnitCore执行GatewaySseReaderTest，必要时加入不配置/非流式回归；usage DTO兼容需确认。
5. 等主Worker费用身份事实，完成必要身份改动；不要自行猜账号。
6. 编译测试通过后按恢复授权commit push（当前没有提交），主Worker统一配置部署实收。

## 当前文件

```
 M student-data-service/src/main/java/com/gaotu/student/data/domain/ai/core/AiApplicationExecutor.java
 M student-data-service/src/main/java/com/gaotu/student/data/domain/ai/core/agentaccess/AiAgentAccessorOverride.java
 M student-data-service/src/main/java/com/gaotu/student/data/domain/ai/core/agentaccess/LlmGatewayAccessor.java
 M student-data-service/src/main/java/com/gaotu/student/data/domain/ai/core/agentaccess/entity/AiModelCallOption.java
 M student-data-service/src/main/java/com/gaotu/student/data/domain/ai/core/agentaccess/entity/AiModelResponse.java
 M student-data-service/src/main/java/com/gaotu/student/data/domain/ai/core/agentaccess/entity/DifyResponse.java
 M student-data-service/src/main/java/com/gaotu/student/data/domain/ai/core/agentaccess/entity/LlmGatewayResponse.java
?? student-data-service/src/main/java/com/gaotu/student/data/domain/ai/core/agentaccess/GatewaySseReader.java
?? student-data-service/src/test/java/com/gaotu/student/data/domain/ai/core/agentaccess/
```

在途编译保留供续接，未取消。没有启动新的子Agent或独立部署。

## 恢复实施记录

上轮最终编译日志无成功终态且进程已结束，不计通过。本轮补多delta、紧凑event:error、格式错误脱敏、非流式响应及usage回归，重新编译日志/tmp/sse-resume-build.log，session94887。尚未提交/部署；待实际JUnit运行结果。当前SSE只支持文本index0，tool_calls等非stop结束拒绝，不声称支持知识库agent工具循环。流中未返回usage时保持空，不伪造用量，不额外插入旧请求没有的stream_options。

## 本轮局部验证结果（最新）

/tmp/sse-resume-build.log：BUILD SUCCESS，2026-11-24 14:26:05，耗时1:22。/tmp/sse-resume-junit.log：JUnitCore实际执行17项，OK (17 tests)，3.096秒；其中GatewaySseReaderTest 11项（多行/UTF-8分片、多个delta顺序、usage、缺DONE、缺finish、length、错误JSON、紧凑event:error、IO中断、解析脱敏、max_tokens请求省略与旧8192行为、非流式解析的组合断言），LegacyDifyPromptTest 6项。没有HTTP真实流或部署实收验证。当前无在途句柄：94887、89290均exit0。

已完成本轮独立局部测试，未commit/push。后续费用身份结论合并后还需总diff复核和相应测试，再按恢复授权提交；主Worker部署实收。上述旧“等待编译/未执行JUnit”条目已由本节结果覆盖。

## Java员工查询能力只读补充

已读strict-v2-cost-identity.md：旧链路由Dify Account.name规范化，非EndUser UUID。报告提及另一checkout HEAD5a7fbcf不作为本worktree版本；本现场仍56b53f3c。

现有可复用入口：`infrastructure/acl/impl/OrganizationService.getEmployeeInfo(String domain)`，调用Medusa `EmployApiImpl.employInfoSearch(EmployParam.domains)`，返回EmployDTO.domain/name/commonName；本地Employee明确domain为“域账号/邮箱前缀”。能验证**已知域账号**对应员工，不能直接证明email→Dify Account.name等价。searchEmployee按姓名返回列表，可能重名，不能用findAny作为费用身份映射。getEmployeeInfo自身未找到时返回空Employee，接入必须校验命中。

RunUser当前有id/name/email；Dify的Account.id不能未经映射直接当Medusa员工id。此次未调用员工接口/数据库，也未修改费用来源。等待身份负责人gongxuemeng数据映射及旧API创建人事实，再决定采用受控映射或权威查询；不能把Employee注释当与Dify账号一致的证明。

## 合流交付（最新）

提交f23459b39已推送。/tmp/sse-cost-build.log BUILD SUCCESS；最新新增头断言单独javac后JUnitCore全25项通过，/tmp/sse-cost-junit.log。未部署、未配置、未业务调用，不能称已真实HTTP验证。当前无在途句柄。

费用契约：Apollo `llm.gateway.application-cost-fallbacks`，键application编号，存在即启用严格身份，值为已核验兜底Account.name，空字符串禁止兜底；`llm.gateway.verified-cost-identities`键为`id:202332`、`email:gongxuemeng@gaotu.cn`、`name:gongxuemeng`或`cost:已核验账号`，值均来自账号调查的Account.name。代码不硬编码样本。显式costUserId优先，其次runUser.id > email > name；有输入无映射则失败，不退创建人。无动态身份才用应用兜底；未知/空账号失败。仅网关且应用显式配置时启用，Dify与未配置应用沿原行为。费用头仍由buildHeaders写入。

费用来源依据strict-v2-cost-account-readback.json及strict-v2-cost-identity.md。API同应用多创建人时不可任取，应由主Worker确认实际旧token对应主体再填fallback，或先留空让缺身份失败。此次未把旧EndUser UUID当费用账号。

参数契约不变：override[agent].omitMaxTokens=true真正省略；params.stream=true开启SSE；thinking仅显式params输入。旧别名TEST不可用为独立平台阻塞，未替换模型伪称一致。新增usage字段保存可获取用量，未返回时为空。AICR异步尚未获得本提交评审结果。
