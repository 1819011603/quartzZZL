# 模型及非messages参数实收审计

仅只读本地证据。当前8个TEST样本使用56b53f3c5（旅程strict），SOP复用历史。13正式应用中4个学部实例无独立实收；不声称生产等价。

## 配置化判断

已有per-agent model/params覆盖快照见format-apollo-before.json，可表达model、stop、thinking、response_format等；本任务未改配置。旧别名已重定向到新model，建议保持接管目标，不能把同目标理解为同一次底层部署。max_tokens旧未传、新8192不证明旧有效上限；需先补默认/模型限制证据。stop未传与[]只标显式差异。temperature/top_p等两侧均未传时有效默认未知。

分层text与JSON协议冲突，保持修正；stream=true与当前同步解析冲突，不能直接配置恢复。Dify user是身份元数据，不能复制旧固定ID。DeepSeek enable_thinking和thinking不能凭名称判定等价。

## 13应用覆盖

|应用|样本|覆盖|
|---|---|---|
|用户画像|画像|TEST同类样本，不能外推生产参数|
|沟通摘要|摘要|TEST同类样本，不能外推生产参数|
|服务SOP分析|SOP V2|TEST同类样本，不能外推生产参数|
|分层原因高中|分层修正后|TEST同类样本，不能外推生产参数|
|分层原因素养|无|无独立实收；参数未知|
|根因精品|退费根因|TEST同类样本，不能外推生产参数|
|根因素养|无|无独立实收；参数未知|
|旅程精品|旅程|TEST同类样本，不能外推生产参数|
|旅程素养|无|无独立实收；参数未知|
|体验精品|课程体验|TEST同类样本，不能外推生产参数|
|体验素养|无|无独立实收；参数未知|
|NPS精品|NPS|TEST同类样本，不能外推生产参数|
|NPS素养|素养NPS|TEST同类样本，不能外推生产参数|

## 画像

旧trace 2a9ff650-ba6f-4bf2-93f8-88034f864c93.0.3；新trace dd182d47-b845-4135-80f2-f13575803a7e.0.3；新证据 artifacts/comparison/format-runs/56b53f3c5/画像/trace-full.received.json

旧返回model及来源：[{"model": "doubao-seed-2.0-lite", "source": "/Users/gaotu/githubDir/quartzZZL/content/高途信息/需求/续班使用的dify下线/artifacts/expanded-renewal/profile-prod-logs.json", "trace": "2a9ff650-ba6f-4bf2-93f8-88034f864c93.0.3", "aggregate_source": "artifacts/expanded-renewal/complete-pairs.json", "raw_file_exists": true, "raw_trace_and_model_present": true}]

新返回model及来源：[{"model": "litellm_proxy/doubao-seed-2.0-lite", "source": "artifacts/comparison/format-runs/56b53f3c5/画像/trace-full.received.json"}]

|参数|旧显式值|新显式值|结论|
|---|---|---|---|
|max_tokens|未传（默认未知）|8192|显式差异；未传不代表默认值相同或不同|
|model|"doubao/Doubao-1-5-pro-32k"|"doubao-seed-2-0-lite-260428"|别名差异须结合重定向快照；不能证明每次同部署|
|response_format|未传（默认未知）|{"type": "json_object"}|显式差异；未传不代表默认值相同或不同|
|stop|未传（默认未知）|[]|显式差异；未传不代表默认值相同或不同|
|stream|true|未传（默认未知）|旧stream=true，新未传；当前同步响应链路不应仅改参数为true|
|thinking|未传（默认未知）|{"type": "disabled"}|豆包旧别名重定向force注入thinking.disabled有控制面及日志证据；显式传参差异不等于有效thinking不同。|
|user|"e4763467-0f1a-4a09-92f1-e4471db27940"|未传（默认未知）|旧Dify用户标识不应盲目复制为新侧固定用户|

## SOP V2

旧trace 315c294d-dbc3-4d8f-adc6-e036ad96d1e1.0.3；新trace 2b757fa1-ac59-4cbd-aac5-1260f6bcba8a.0.3；新证据 artifacts/comparison/pairs.json sides[1]

旧返回model及来源：[{"model": "doubao-seed-2.0-lite", "source": "/Users/gaotu/githubDir/quartzZZL/content/高途信息/需求/续班使用的dify下线/artifacts/expanded-renewal/sop-v2-1-logs.txt", "trace": "315c294d-dbc3-4d8f-adc6-e036ad96d1e1.0.3", "aggregate_source": "artifacts/expanded-renewal/complete-pairs.json", "raw_file_exists": true, "raw_trace_and_model_present": true}]

新返回model及来源：[{"model": "litellm_proxy/doubao-seed-2.0-lite", "source": "/Users/gaotu/githubDir/quartzZZL/content/高途信息/需求/续班使用的dify下线/artifacts/expanded-renewal/sop-v2-2-logs.txt", "trace": "2b757fa1-ac59-4cbd-aac5-1260f6bcba8a.0.3"}]

|参数|旧显式值|新显式值|结论|
|---|---|---|---|
|max_tokens|未传（默认未知）|8192|显式差异；未传不代表默认值相同或不同|
|model|"doubao/Doubao-Seed-1-6"|"doubao-seed-2-0-lite-260428"|别名差异须结合重定向快照；不能证明每次同部署|
|response_format|未传（默认未知）|{"type": "json_object"}|显式差异；未传不代表默认值相同或不同|
|stop|未传（默认未知）|[]|显式差异；未传不代表默认值相同或不同|
|stream|true|未传（默认未知）|旧stream=true，新未传；当前同步响应链路不应仅改参数为true|
|user|"aad12f3c-2c87-4a43-b0cd-53112cf6d22a"|未传（默认未知）|旧Dify用户标识不应盲目复制为新侧固定用户|

## 分层修正后

旧trace 3c9e6b70-e6f3-4f95-883b-14408cdafc2b.0.3；新trace e604b357-f357-4997-b28b-f3192b531eb8.0.3；新证据 artifacts/comparison/format-runs/56b53f3c5/分层修正后/trace-full.received.json

旧返回model及来源：[{"model": "doubao-seed-2.0-lite", "source": "/Users/gaotu/githubDir/quartzZZL/content/高途信息/需求/续班使用的dify下线/artifacts/expanded-renewal/tier-valid-prod-logs.json", "trace": "3c9e6b70-e6f3-4f95-883b-14408cdafc2b.0.3", "aggregate_source": "artifacts/expanded-renewal/complete-pairs.json", "raw_file_exists": true, "raw_trace_and_model_present": true}]

新返回model及来源：[{"model": "litellm_proxy/doubao-seed-2.0-lite", "source": "artifacts/comparison/format-runs/56b53f3c5/分层修正后/trace-full.received.json"}]

|参数|旧显式值|新显式值|结论|
|---|---|---|---|
|max_tokens|未传（默认未知）|8192|显式差异；未传不代表默认值相同或不同|
|model|"doubao/Doubao-1-5-pro-32k"|"doubao-seed-2-0-lite-260428"|别名差异须结合重定向快照；不能证明每次同部署|
|response_format|未传（默认未知）|{"type": "text"}|保持text：非JSON输出协议冲突，不盲目恢复JSON|
|stop|未传（默认未知）|[]|显式差异；未传不代表默认值相同或不同|
|stream|true|未传（默认未知）|旧stream=true，新未传；当前同步响应链路不应仅改参数为true|
|thinking|未传（默认未知）|{"type": "disabled"}|豆包旧别名重定向force注入thinking.disabled有控制面及日志证据；显式传参差异不等于有效thinking不同。|
|user|"b1d3615e-1921-4281-88f0-b3ec598bb0d5"|未传（默认未知）|旧Dify用户标识不应盲目复制为新侧固定用户|

## 素养NPS

旧trace 8c802dc4-ed69-4533-b63a-3851e20bb83d.0.3；新trace 5a814ae8-b8ae-4450-ada4-895a41d53463.0.3；新证据 artifacts/comparison/format-runs/56b53f3c5/素养NPS/trace-full.received.json

旧返回model及来源：[{"model": "ep_wuxzxwds4_ds-v4-1-flash", "source": "/private/tmp/w1-suyang-chain-prod.txt", "trace": "8c802dc4-ed69-4533-b63a-3851e20bb83d.0.3", "aggregate_source": "artifacts/expanded-renewal/complete-pairs.json", "raw_file_exists": true, "raw_trace_and_model_present": true}]

新返回model及来源：[{"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/comparison/format-runs/56b53f3c5/素养NPS/trace-full.received.json"}]

|参数|旧显式值|新显式值|结论|
|---|---|---|---|
|max_tokens|未传（默认未知）|8192|显式差异；未传不代表默认值相同或不同|
|model|"deepseek-v4-flash-0731"|"deepseek-flash"|别名差异须结合重定向快照；不能证明每次同部署|
|stop|未传（默认未知）|[]|显式差异；未传不代表默认值相同或不同|
|stream|true|未传（默认未知）|旧stream=true，新未传；当前同步响应链路不应仅改参数为true|
|thinking|{"type": "enabled"}|未传（默认未知）|DeepSeek素养NPS旧显式thinking.enabled，本次56b53f3c5新侧未传thinking；有效默认未知。主Worker仅安排此项配置enabled，本审计不冒称配置后实收已验证。|
|user|"c3fec88f-c18e-4c89-8ddb-3e2217928de3"|未传（默认未知）|旧Dify用户标识不应盲目复制为新侧固定用户|

## 摘要

旧trace 15760243-f225-4246-a103-c9565c2652ba.0.3；新trace 62b40ff1-972a-4906-bd24-28e9486d4aa5.0.3；新证据 artifacts/comparison/format-runs/56b53f3c5/摘要/trace-full.received.json

旧返回model及来源：[{"model": "doubao-seed-2.0-lite", "source": "/private/tmp/compare-renewal-prod-llm.json", "trace": "15760243-f225-4246-a103-c9565c2652ba.0.3", "aggregate_source": "artifacts/expanded-renewal/complete-pairs.json", "raw_file_exists": true, "raw_trace_and_model_present": true}]

新返回model及来源：[{"model": "litellm_proxy/doubao-seed-2.0-lite", "source": "artifacts/comparison/format-runs/56b53f3c5/摘要/trace-full.received.json"}]

|参数|旧显式值|新显式值|结论|
|---|---|---|---|
|max_tokens|未传（默认未知）|8192|显式差异；未传不代表默认值相同或不同|
|model|"doubao/Doubao-1-5-pro-32k"|"doubao-seed-2-0-lite-260428"|别名差异须结合重定向快照；不能证明每次同部署|
|response_format|未传（默认未知）|{"type": "json_object"}|显式差异；未传不代表默认值相同或不同|
|stop|未传（默认未知）|[]|显式差异；未传不代表默认值相同或不同|
|stream|true|未传（默认未知）|旧stream=true，新未传；当前同步响应链路不应仅改参数为true|
|thinking|未传（默认未知）|{"type": "disabled"}|豆包旧别名重定向force注入thinking.disabled有控制面及日志证据；显式传参差异不等于有效thinking不同。|
|user|"e4763467-0f1a-4a09-92f1-e4471db27940"|未传（默认未知）|旧Dify用户标识不应盲目复制为新侧固定用户|

## 退费根因

旧trace a32fe4b6-6269-4882-8d39-81c76f8ca23e.0.3；新trace f33b2e1d-019e-42d1-b97f-13e98c78c612.0.3；新证据 artifacts/comparison/format-runs/56b53f3c5/退费根因/sls.received.json

旧返回model及来源：[{"model": "deepseek-v4.1-flash", "source": "/private/tmp/compare-refund-prod-llm.json", "trace": "a32fe4b6-6269-4882-8d39-81c76f8ca23e.0.3", "aggregate_source": "artifacts/expanded-renewal/complete-pairs.json", "raw_file_exists": true, "raw_trace_and_model_present": true}]

新返回model及来源：[{"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/comparison/format-runs/56b53f3c5/退费根因/sls.received.json"}]

|参数|旧显式值|新显式值|结论|
|---|---|---|---|
|enable_thinking|未传（默认未知）|true|DeepSeek场景：不适用豆包force disabled结论；thinking与enable_thinking为不同字段，是否转换/优先级及有效默认须独立证据，不能认定等价。|
|max_tokens|未传（默认未知）|8192|显式差异；未传不代表默认值相同或不同|
|model|"deepseek/DeepSeek-R1-250528"|"deepseek-flash"|别名差异须结合重定向快照；不能证明每次同部署|
|stop|未传（默认未知）|[]|显式差异；未传不代表默认值相同或不同|
|stream|true|未传（默认未知）|旧stream=true，新未传；当前同步响应链路不应仅改参数为true|
|user|"138a7353-4436-4c96-b627-4b94bd88eadf"|未传（默认未知）|旧Dify用户标识不应盲目复制为新侧固定用户|

## 旅程

旧trace bfd44413-31f5-493d-904b-e670783ff2c4.0.3；新trace b83e29de-f629-4a5e-b864-588da89e26b4.0.3；新证据 artifacts/comparison/format-runs/56b53f3c5-journey-strict/旅程/sls.received.json

旧返回model及来源：[{"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/expanded-refund/llm-c9335c5b-42d6-4418-839e-760e051ce0d0.log"}, {"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/expanded-refund/llm-full-c9335c5b.log"}]

新返回model及来源：[{"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/comparison/format-runs/56b53f3c5-journey-strict/旅程/sls.received.json"}]

|参数|旧显式值|新显式值|结论|
|---|---|---|---|
|enable_thinking|未传（默认未知）|true|DeepSeek场景：不适用豆包force disabled结论；thinking与enable_thinking为不同字段，是否转换/优先级及有效默认须独立证据，不能认定等价。|
|max_tokens|未传（默认未知）|8192|显式差异；未传不代表默认值相同或不同|
|model|"deepseek/DeepSeek-R1-250528"|"deepseek-flash"|别名差异须结合重定向快照；不能证明每次同部署|
|stop|未传（默认未知）|[]|显式差异；未传不代表默认值相同或不同|
|stream|true|未传（默认未知）|旧stream=true，新未传；当前同步响应链路不应仅改参数为true|
|user|"ad7b115e-08f6-44b7-80fd-222057e85cf9"|未传（默认未知）|旧Dify用户标识不应盲目复制为新侧固定用户|

## 课程体验

旧trace e02d7092-ee55-4e73-b731-b6f31ef2fb6e.0.3；新trace 6c006207-ade9-4800-b40a-a0db181b4c9c.0.3；新证据 artifacts/comparison/format-runs/56b53f3c5/课程体验/sls.received.json

旧返回model及来源：[{"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/expanded-refund/llm-full-c2512c21.log"}, {"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/expanded-refund/llm-c2512c21-8fea-48e7-b3e0-aaf9629cc7f4.log"}, {"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/comparison/format-offline-check/historical-test.log"}]

新返回model及来源：[{"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/comparison/format-runs/56b53f3c5/课程体验/sls.received.json"}]

|参数|旧显式值|新显式值|结论|
|---|---|---|---|
|max_tokens|未传（默认未知）|8192|显式差异；未传不代表默认值相同或不同|
|model|"deepseek/DeepSeek-R1-250528"|"deepseek-flash"|别名差异须结合重定向快照；不能证明每次同部署|
|stop|未传（默认未知）|[]|显式差异；未传不代表默认值相同或不同|
|stream|true|未传（默认未知）|旧stream=true，新未传；当前同步响应链路不应仅改参数为true|
|user|"b76f6171-90d1-4eb6-bb30-93f2afd581cb"|未传（默认未知）|旧Dify用户标识不应盲目复制为新侧固定用户|

## NPS

旧trace d2003cc1-b573-4e1c-8918-d3a4d162fe62.0.3；新trace b7f98851-b9b7-4395-89f9-39a63bbaeeef.0.3；新证据 artifacts/comparison/format-runs/56b53f3c5/NPS/sls.received.json

旧返回model及来源：[{"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/expanded-refund/llm-full-fa98c35e.log"}, {"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/expanded-refund/llm-fa98c35e-5d23-4b47-9e53-4f9773a64b1d.log"}]

新返回model及来源：[{"model": "litellm_proxy/deepseek-v4.1-flash", "source": "artifacts/comparison/format-runs/56b53f3c5/NPS/sls.received.json"}]

|参数|旧显式值|新显式值|结论|
|---|---|---|---|
|max_tokens|未传（默认未知）|8192|显式差异；未传不代表默认值相同或不同|
|model|"deepseek/DeepSeek-R1-250528"|"deepseek-flash"|别名差异须结合重定向快照；不能证明每次同部署|
|stop|未传（默认未知）|[]|显式差异；未传不代表默认值相同或不同|
|stream|true|未传（默认未知）|旧stream=true，新未传；当前同步响应链路不应仅改参数为true|
|user|"66dfce4b-7349-43fc-a8a6-332ae76fdecb"|未传（默认未知）|旧Dify用户标识不应盲目复制为新侧固定用户|

## 路由证据边界

旧模型重定向快照与实际redirect日志见JSON route_evidence。豆包旧名→doubao-seed-2-0-lite-260428；deepseek-v4-flash-0731及DeepSeek-R1-250528→deepseek-flash。旧豆包重定向force注入thinking.disabled已有证据。返回model仅提供可见名称，不证明权重、部署、默认参数完全一致。本次9个样本旧返回model均已找到；旧6组从complete-pairs.json补齐，并核对原始来源中的完整trace及model。返回模型字符串仍不能证明供应商部署相同。

## 最新TEST控制面补证

已读取主Worker实时只读安全提取的parameter-control-test-safe.json和parameter-defaults-test-safe.json。Doubao1.5重定向强制thinking.disabled，与既有redirect实收相互印证。目标部署defaultParams={}只证明控制面部署层没有显式默认项，不能推定SDK/供应商的temperature、top_p、max_tokens等有效默认。目标存在多个部署，返回model相同不能推出同一供应商部署；模型别名接管目标一致与部署级等价必须分开。完整安全默认快照纳入JSON current_test_control_evidence。


## 本轮定向修正

仅素养NPS的thinking.enabled由主Worker处理；其余参数保留，列可配置方案、业务约束或有效默认未知。这里的新侧值仍是指定56b53f3c5既有实收，不冒称后续配置效果。豆包force disabled仅用于豆包场景，DeepSeek thinking/enable_thinking转换和有效默认无证据时保留未知。旧6组model并非事实缺失，已补证并纠正。
