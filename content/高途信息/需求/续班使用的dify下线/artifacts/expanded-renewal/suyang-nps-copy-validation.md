# 素养 NPS TEST 副本与双侧实收（2026-11-23）

## 副本

从线上只读应用 `spcAm3oupwKuWRMD8UV_3d398bdf-622e-42f8-a5f3-d5543495421b`（“【素养】课程NPS分析”）读取 `agent-chat` 的完整 `model_config.pre_prompt`，长度 321 字，模型为 `deepseek-v4-flash-0731`，复制为 TEST Dify 应用：

- Dify TEST app：`spcjE2Q2agjjjJ2GYZc_fb2db0ac-d837-43d6-a1ab-8e7b46e06bfa`
- Dify app：`【TEST】素养NPS迁移对照`
- TEST Dify 已通过工作台发布，版本 1；service `/v1/info` 已回读应用名。
- TEST `ai_agent=7530633600362872933`，access key 仅存测试库；`ai_application=7530633600362872934`，`gateway_core_prompt` 321 字。
- Apollo TEST 已增加该 agent 的网关覆盖，发布 `20261123221121-188aa6ecfba69681`，模型 `deepseek-flash`、`stop=[]`。

## 同输入双侧调用

调用入口：`AiApplicationTestServiceImpl#compareAiApplication`，泳道 `test-gtbg-dev-1`，应用名 `退费NPS分析-素养TEST迁移副本`，输入复用 NPS 有效样本（clazz `500775385189890048`，user `7404351741`，业务正文 302 字）。

- Dify 旧侧：`event=message`，messageId `92f54eec-345e-4e58-829a-dc8504f4bb4c`，非空成功。
- 网关新侧：`event=litellm_proxy/deepseek-v4.1-flash`，messageId `22df5821-d4ed-4856-ac9d-229e04cb1bc4.0.3`，answer 2159 字，非空成功。

两侧均成功返回，说明副本绑定、Dify 发布、Apollo 覆盖和网关入口已串通。Dify console 配置和 `ai_application.gateway_core_prompt` 的 321 字文本 SHA256 均为 `792367953211702387ba02b1e2c3a136134fcd753238b134039754c87a920ab4`，复制内容完整一致。当前日志检索未命中这两个 message/trace 标识，因此本次以 Dify 配置回读、TEST 数据库回读、Apollo 回读和 compare 双侧结果作为证据；没有把 answer 文本差异解释成输入差异。

## 限制

本次副本只验证素养 NPS 321 字模板的双侧入口和配置一致性；精品 NPS 473 字模板仍是另一归属，不能混用。未改生产、未调用生产推理、未做提供商最终 HTTP 或输出质量验收。

## 后续实际输入核对
已补齐两侧LiteLLM实收，完整messages不相同，正文相同；详见 [实际输入补证](suyang-actual-input-verification.md)。真实trace为 `8c802dc4-ed69-4533-b63a-3851e20bb83d.0.3`，上述响应messageId不是trace。
