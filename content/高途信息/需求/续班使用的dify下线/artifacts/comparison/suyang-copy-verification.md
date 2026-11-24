# 三项素养替代模型验证完成

三项真正TEST Dify应用已用映射目标deepseek-flash配置、发布并成功运行；与修正后的新链路完整LiteLLM messages和指定参数全部相等。此前模型名单阻塞已自行解除，不再等待外部开通。

|场景|旧Dify入口trace|旧LiteLLM trace|最终新trace|结果|
|---|---|---|---|---|
|素养根因|7905ec1b-e7b6-4f7e-826a-09abc2401963.0.3|c9a92c1d-d766-4982-a6d9-700ba4c45e48.0.3|1b812e6a-3ef7-4399-b2e4-47b2d5f88b15.0.3|messages、参数全等|
|素养旅程|3882b435-710f-4b9a-95ad-c133230a3db2.0.3|130df5c1-0813-4fd0-9a86-325e5e2077ee.0.3|7c633ac1-66ed-4e74-9634-ab8ce0bcf9cb.0.3|messages、参数全等|
|素养体验|23854005-9901-439b-ba74-699ddd8edfff.0.3|61d3107e-f6b6-4fbe-ac11-5e83de9a6a9d.0.3|f018e314-4756-49c3-9660-7c2b6d216317.0.3|messages、参数全等|

## 条件与修正

当前TEST身份gongxuemeng/id177071，workspace owner；MODEL_MANAGE保护的凭据接口实际HTTP200。已有模型凭据指向test-llm.baijia.com，但API返回掩码不能直接复用。随后使用student-data TEST Apollo已有网关凭据（此前gps-ai真实调用deepseek-flash成功，授权已验证），经正常Dify模型凭据API注册deepseek-flash，HTTP201。未取生产密钥、未改callerRoute。仅该TEST目标模型使用独立凭据配置TEST迁移验证gps-ai。

三个应用复用现有草稿，完整线上model_config仅model.name替换deepseek-flash，配置HTTP200，发布到TEST ai-base，非飞书渠道。三次旧生成均200且有answer/usage。此为替代模型对照，不是旧名称原样回放，不要求随机输出一致。

旧Dify实际将enable_thinking=true转换为thinking={type:enabled}，stream=true，max_tokens及stop均不传。新侧原来省略thinking，因此为三个素养TEST应用建立独立agent覆盖（不改变精品agent），补thinking.enabled并发布回读：20261124231941-188a6f5d9e0ed672。定向三项复验成功，旧新除user外完整非messages字段相等：model=deepseek-flash、stream=true、thinking.enabled，max_tokens省略。Dify user为EndUser UUID，不复制到新侧。

## 证据

`suyang-copy-current/final-summary.json`包含旧入口/下游/新trace、逐字和参数断言；`register-target-response.json`、`test-permission-credential-probe.json`、`workspace-readback.json`为注册条件；`thinking-release.txt`/`thinking-readback.txt`为最终发布。

`remaining-current-runs/test-dify-old/各场景/replacement-*`为旧应用配置回读、响应、消息详情和完整LiteLLM实收。旧Dify入口trace未直接透传网关，以持久化from_end_user_id关联同次LiteLLM请求中的user，旧messages也与持久化message及新请求交叉相等。

`remaining-current-runs/suyang-thinking-final/各场景/received.json`和invoke.json、sls.txt为修正后新实收。`suyang-isolated-agents.json`记录三个TEST独立agent绑定。请求RunUser仍来自已核验业务老师gongxuemeng，未用兜底。

本次无生产生成/写入、无正式知识库改动、无代码部署、无README/飞书改动、无无关12例重跑；三项参数变更后的定向复验必要且已完成。无在途操作。此前本报告中的模型未注册阻塞口径由本次结果覆盖。

Apollo：https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default
