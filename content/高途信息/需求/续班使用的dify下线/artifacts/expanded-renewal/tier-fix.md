# TEST分层格式修正及复验

代码91012878；TEST/test-gtbg-dev-1；未改代码或生产。

## 契约与改动
RenewalLiftReasonHandle:65调用普通syncRequestTask，随后tryToGetJsonAnswer只清理think/代码围栏，不提取JSON对象字段，清理后的完整字符串直接updateReasonBySubclazzAndUser。因此原强制JSON对象不是预期原因文本。

仅TEST/default/application的ai.agent.accessor.override.map中agent262172718139452416的params.response_format由{"type":"json_object"}改为{"type":"text"}。未删除该字段，避免默认格式兜底。读取最新已发布值后合并；修改前dry-run无未发布变更，修改后dry-run仅目标key变化；回读整个map与目标完全一致，其他agent包括画像thinking.disabled未变。

releaseKey：20261123192847-188a49b33afd47bc；releaseTitle：20261123192847-release。

## 真实同入口验证
完全复用tier-valid-request.json，响应头trace：dabc87b7-0a58-4682-ae04-e6cfa2b3224f.0.3（2026-11-23 19:28:58—19:29:13）。业务桥TEST；LiteLLM实收查TEST/SLS/app，过滤service=litellm。

实收response_format.type=text，服务接受且产生文本原因。新answer带普通代码围栏，按现有tryToGetJsonAnswer清理后为纯原因文本，不含JSON对象。旧路也为原因文本。两侧均描述108天服务、完成度偏低、微信互动低、无预报名；小数精度/措辞差异不作为等价失败。

证据：tier-fix-before.json、tier-fix-target.json、tier-fix-dry-before.txt、tier-fix-dry-after.txt、tier-fix-release.txt、tier-fix-readback.txt；tier-fix-headers.txt、tier-fix-response.json、tier-fix-received.json、tier-fix-llm-response.json、tier-fix-test-litellm.json。

## 剩余边界
本次验证compare入口与实际消费方法契约，未触发MQ事件或业务update落库；部门路由高中/素养应用不外推。本次没有修改thinking或其他参数。text限制允许文本但不是严格业务语义校验，单次成功不保证每次措辞一致。保留当前TEST修正供验证。

配置页：https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default

本次finish_reason=stop；usage={"completion_tokens": 458, "prompt_tokens": 4248, "total_tokens": 4706, "completion_tokens_details": {"accepted_prediction_tokens": null, "audio_tokens": null, "reasoning_tokens": 380, "rejected_prediction_tokens": null}, "prompt_tokens_details": {"audio_tokens": null, "cached_tokens": null}}。
修正前后messages逐字段相等：True。
