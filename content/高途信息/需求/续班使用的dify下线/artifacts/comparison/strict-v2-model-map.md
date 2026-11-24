# Strict v2模型映射与验证期望

实时只读PROD/TEST控制面，未生成、未写配置。安全字段及版本见同名JSON。

## 旧名与重定向

|旧请求model|PROD目标|TEST目标|重定向默认|
|---|---|---|---|
|doubao/Doubao-1-5-pro-32k|doubao-seed-2-0-lite-260428|doubao-seed-2-0-lite-260428|{"prod": {"thinking": {"type": "object", "value": {"type": "disabled"}, "force": true}}, "test": {"thinking": {"type": "object", "value": {"type": "disabled"}, "force": true}}}|
|doubao/Doubao-Seed-1-6|doubao-seed-2-0-lite-260428|doubao-seed-2-0-lite-260428|{"prod": null, "test": null}|
|deepseek/DeepSeek-R1-250528|deepseek-flash|deepseek-flash|{"prod": null, "test": null}|
|deepseek-v4-flash-0731|deepseek-flash|deepseek-flash|{"prod": null, "test": null}|

## Caller与部署边界

TEST gps-ai只有deepseek-v4-flash-0731具明确旧名route；三种其他旧名不在其routeList，但目标均在。部署源码已补证：旧别名鉴权先于重定向，目标授权不能代替原始model授权；需新增三条TEST旧别名路由。PROD gps-ai路由与TEST不同，不能外推。旧Dify caller_0167的实际redirect日志证明历史旧调用发生映射，不证明新caller权限。

目标有多个供应商部署；返回model名称一致不保证部署一致。部署defaultParams为空不代表供应商默认已知。旧豆包1.5重定向force disabled有证据，客户端应按旧省略thinking，由重定向产生有效disabled；Seed1.6具体默认见表，不套用1.5。

## 九场景精确期望

|场景|model|stream|max_tokens|thinking|消息基准|
|---|---|---|---|---|
|画像|doubao/Doubao-1-5-pro-32k|true|不传|"不传"|artifacts/comparison/format-samples/画像-old-messages.json|
|SOP V2|doubao/Doubao-Seed-1-6|true|不传|"不传"|artifacts/comparison/format-samples/SOP V2-old-messages.json|
|分层修正后|doubao/Doubao-1-5-pro-32k|true|不传|"不传"|artifacts/comparison/format-samples/分层修正后-old-messages.json|
|素养NPS|deepseek-v4-flash-0731|true|不传|{"type": "enabled"}|artifacts/comparison/format-samples/素养NPS-old-messages.json|
|摘要|doubao/Doubao-1-5-pro-32k|true|不传|"不传"|artifacts/comparison/format-samples/摘要-old-messages.json|
|退费根因|deepseek/DeepSeek-R1-250528|true|不传|"不传"|artifacts/comparison/format-samples/退费根因-old-messages.json|
|旅程|deepseek/DeepSeek-R1-250528|true|不传|"不传"|artifacts/comparison/format-samples/旅程-old-messages.json|
|课程体验|deepseek/DeepSeek-R1-250528|true|不传|"不传"|artifacts/comparison/format-samples/课程体验-old-messages.json|
|NPS|deepseek/DeepSeek-R1-250528|true|不传|"不传"|artifacts/comparison/format-samples/NPS-old-messages.json|

请求层必须严格对齐：9例max_tokens均省略、stream=true；仅素养NPS显式thinking.enabled。旧user作为身份来源线索而非可复制常量，x-tech-ai-user-id由主Worker核实真实来源。stream=true需要消费完整SSE并保存最终usage与正常结束，不能只看HTTP200。

消息沿既有严格旧基准，旅程不得回到strict前模板。样本不扩为13生产应用逐一验证；4KB排除。以上是测试期望，不是本轮新实收。

## TEST授权顺序已补证

只读pod `litellm-69797d7f6-69rtm`（10.255.161.138）部署源码：proxy_server.py先调用control_plane_api_key_auth_builder(validate_route=True)，鉴权按原始model逐项匹配caller.route_list，非admin未命中返回403；之后才在3430行apply_model_redirect_routing。实时控制面gps-ai admin=false、status=normal，三种旧别名均未配置。故需要TEST gps-ai增加doubao/Doubao-1-5-pro-32k、doubao/Doubao-Seed-1-6、deepseek/DeepSeek-R1-250528路由；已有目标路由不足以代替。deepseek-v4-flash-0731已有明确路由。

证据见strict-v2-auth-evidence/及JSON authorization_order_verified。本次不配置、不生成，结论为源码+配置推导，未主动产生403；新增后仍须实收校验。仅核查一个TEST副本，不声称全部副本/生产源码同版本。

## 最终旧模型→新模型裁决（2026-11-24，只读控制面+运行证据）

|旧请求model|重定向新model|目标实际部署（PROD/TEST一致）|运行证据/备注|
|---|---|---|---|
|doubao/Doubao-1-5-pro-32k|doubao-seed-2-0-lite-260428|litellm_proxy/ep-20260508155629-tkjvf、ep-20260721112117-79txh、ep-20260721112145-4sdqz、doubao-seed-2.0-lite|重定向force注入thinking.disabled；请求层仍应省略thinking|
|doubao/Doubao-Seed-1-6|doubao-seed-2-0-lite-260428|同上|无重定向强制参数|
|deepseek/DeepSeek-R1-250528|deepseek-flash|litellm_proxy/deepseek-v4.1-flash、deepseek/deepseek-flash、ep_wuxzxwds4_ds-v4-1-flash|多部署按网关选择；TEST素养NPS实跑返回deepseek-v4.1-flash（trace 24d4ad82）与ep_wuxzxwds4（trace 76d487c5）||
|deepseek-v4-flash-0731|deepseek-flash|同上|素养NPS旧别名TEST已授权并实跑成功|

来源：LLM网关控制面，不是itemllm/litellm运行时或Dify：PROD为 `GET https://tech.baijia.com/llm-gateway/admin/config/all?env=prod`，TEST为 `GET https://tech.baijia.com/llm-gateway/admin/config/all?env=test`（控制台Cookie认证，凭据不落盘输出）。四条映射均来自响应 `models[].redirectToModelCode/deployments`；trace 24d4ad82、76d487c5仅作为素养NPS运行结果佐证，不是映射来源。不需要保存或修改callerRoute。

## AICR结果（2026-11-24）

- f23459b3：task 2329已完成，FAIL，1 blocking/1 high/4 medium/9 low。blocking #59150指旧身份校验在createNotCalled后抛错会导致记录停留未调用；263ba48a已删除该抛错与兜底映射（缺失仅warn不阻断），按实现已消除，待新评审确认。
- 263ba48a：确认未生成AICR任务（2026-11-24复查）。此前失败原因是`aicr.py`默认请求未带历史成功调用必需的`ingress-traffic-env: grayTest`、`traffic-env: grayTest`与`X-Requested-With: XMLHttpRequest`。按task2329成功方式经127.0.0.1:8888代理只读查询task/list，HTTP/code均200，total=8；最新task 2329 headSha仍为f23459b399c2148e1ec84e888d9a2d0bc5d19869，无263ba48a任务。本地与远端分支HEAD均为263ba48ad2e476e7092093d36414280dddef2ed6d。复查结束，不再重复调用。
