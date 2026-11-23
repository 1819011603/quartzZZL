# 续班当前实收prompt逐字符裁决

基线91012878；只读已保存LiteLLM实收。当前指本轮最后验证的配置快照，不是本轮重新联网检查。长度为Unicode字符数。完整messages按固定JSON序列化比较（ensure_ascii=False，紧凑分隔符）；不是HTTP原始字节比较。first_diff_offset为0起始。


## 画像

旧trace：2a9ff650-ba6f-4bf2-93f8-88034f864c93.0.3；新trace：2a9ff650-ba6f-4bf2-93f8-88034f864c93.0.3。

旧文件：expanded-renewal/profile-prod-received.json；新文件：expanded-renewal/profile-test-received.json。

实际角色：['user'] → ['system', 'user']。

完整messages：{"equal": false, "old_chars": 3674, "new_chars": 3582, "first_diff_offset": 10, "old_at_diff": "[{\"role\":\"user\",\"content\":\"[\\n  {\\n    \\\"role\\\": \\\"system\\\",\\n    \\\"content\\\": \\\"##角色\\n你是一名在线教育的数据分析", "new_at_diff": "[{\"role\":\"system\",\"content\":\"##角色\\n你是一名在线教育的数据分析师\\n\\n##任务\\n基于提供的“老师和用户的每通沟通记录中的关键点”（包括续班兴趣点清单、续班抗性点清"}

拆出system：{"equal": true, "old_chars": 2272, "new_chars": 2272, "first_diff_offset": null, "old_at_diff": null, "new_at_diff": null}

拆出user：{"equal": true, "old_chars": 1124, "new_chars": 1124, "first_diff_offset": null, "old_at_diff": null, "new_at_diff": null}

新请求参数（单列，不混同prompt一致）：{"response_format": {"type": "json_object"}, "stop": [], "max_tokens": 8192, "model": "doubao-seed-2-0-lite-260428", "thinking": {"type": "disabled"}}


## 摘要

旧trace：15760243-f225-4246-a103-c9565c2652ba.0.3；新trace：f059219f-2d7c-46c5-945e-fd3a9cdab509.0.3。

旧文件：trace-recheck-20261123/compare-renewal-prod-request.json；新文件：trace-recheck-20261123/dify-thinking-verified.json。

实际角色：['user'] → ['system', 'user']。

完整messages：{"equal": false, "old_chars": 2145, "new_chars": 2053, "first_diff_offset": 10, "old_at_diff": "[{\"role\":\"user\",\"content\":\"[\\n  {\\n    \\\"role\\\": \\\"system\\\",\\n    \\\"content\\\": \\\"##角色\\n你是一名在线教育的数据分析", "new_at_diff": "[{\"role\":\"system\",\"content\":\"##角色\\n你是一名在线教育的数据分析师\\n\\n##任务\\n你的主要工作是基于老师和用户的每通沟通记录中的【关键点】提炼出整体的【关键点】，接"}

拆出system：{"equal": true, "old_chars": 466, "new_chars": 466, "first_diff_offset": null, "old_at_diff": null, "new_at_diff": null}

拆出user：{"equal": true, "old_chars": 1493, "new_chars": 1493, "first_diff_offset": null, "old_at_diff": null, "new_at_diff": null}

新请求参数（单列，不混同prompt一致）：{"response_format": {"type": "json_object"}, "stop": [], "max_tokens": 8192, "model": "doubao-seed-2-0-lite-260428", "thinking": {"type": "disabled"}}


## 分层

旧trace：3c9e6b70-e6f3-4f95-883b-14408cdafc2b.0.3；新trace：7a05052d-9094-4a00-aa88-bf44dcf0eb61.0.3。

旧文件：expanded-renewal/tier-valid-prod-received.json；新文件：expanded-renewal/thinking-received.json。

实际角色：['user'] → ['system', 'user']。

完整messages：{"equal": false, "old_chars": 9065, "new_chars": 8973, "first_diff_offset": 10, "old_at_diff": "[{\"role\":\"user\",\"content\":\"[\\n  {\\n    \\\"role\\\": \\\"system\\\",\\n    \\\"content\\\": \\\"## 角色\\n- 你是一位经验丰富且专", "new_at_diff": "[{\"role\":\"system\",\"content\":\"## 角色\\n- 你是一位经验丰富且专业的数据分析师，擅长以通俗易懂且灵活多变的语言分析用户数据，并给出合理原因解释，以此让在线教育行业的辅导"}

拆出system：{"equal": true, "old_chars": 2715, "new_chars": 2715, "first_diff_offset": null, "old_at_diff": null, "new_at_diff": null}

拆出user：{"equal": true, "old_chars": 5601, "new_chars": 5601, "first_diff_offset": null, "old_at_diff": null, "new_at_diff": null}

新请求参数（单列，不混同prompt一致）：{"response_format": {"type": "text"}, "stop": [], "max_tokens": 8192, "model": "doubao-seed-2-0-lite-260428", "thinking": {"type": "disabled"}}


## SOP V2

旧trace：315c294d-dbc3-4d8f-adc6-e036ad96d1e1.0.3；新trace：2b757fa1-ac59-4cbd-aac5-1260f6bcba8a.0.3。

旧文件：expanded-renewal/sop-v2-1-received.json；新文件：expanded-renewal/sop-v2-2-received.json。

实际角色：['user'] → ['user']。

完整messages：{"equal": true, "old_chars": 15002, "new_chars": 15002, "first_diff_offset": null, "old_at_diff": null, "new_at_diff": null}

拆出user：{"equal": true, "old_chars": 13647, "new_chars": 13647, "first_diff_offset": null, "old_at_diff": null, "new_at_diff": null}

新请求参数（单列，不混同prompt一致）：{"response_format": {"type": "json_object"}, "stop": [], "max_tokens": 8192, "model": "doubao-seed-2-0-lite-260428"}
## 裁决表

|场景|完整messages|拆出指令文本|拆出业务数据|不一致原因|
|---|---|---|---|---|
|画像|不一致，3674→3582字符|2272字符相等|1124字符相等|旧是单user承载伪JSON角色文本；新是真system+user，去掉包装|
|摘要|不一致，2145→2053字符|466字符相等|1493字符相等|同上；新用thinking.disabled最终复验请求|
|分层|不一致，9065→8973字符|2715字符相等|5601字符相等|同上；新用text+thinking.disabled最终复验请求|
|SOP V2|一致，15002字符|未拆分成真system；整段flat保持|单user content13647字符相等|无差异|

前三项首个差异均为固定JSON序列化offset=10：role的user变system。长度不是提示词token数。旧flat不是严格JSON，含原生换行/未转义引号；脚本按实际固定分隔符拆分，未做strip、空白归一或语义近似。完整比较是实际messages对象结构+字符串值比较，不能将拆出的文本相等写成“实际prompt完全一致”。

代码原因：普通executeCoreLogic调用DynamicPromptGenerator.generatePayload，Dify访问器消费flat，新网关消费messages；SOP真实V2先generate得到flat，再ofFlat供两路使用，故两侧保持单user。角色优先级变化是真实请求差异，本轮仅解释原因，不擅自改回旧结构。是否以正文逐字符相等作为本轮满足条件由主Worker依owner口径整合，不新增输出质量门槛。

## 时间与配置边界

画像两侧为同一trace；摘要、分层使用旧有效样本trace对比最终参数修正后新trace，因此是跨次执行，但实收正文逐字符相等有直接证据，不靠“输入参数一样”推断。SOP两条trace为同fixture V2双路。摘要最终复验文件是列表，第0项body为请求，第1项body是响应，比较只取请求。

最终有效配置：画像/摘要thinking.disabled；分层response_format.text且thinking.disabled；SOP保留既有thinking行为，旧Seed-1-6与新都曾产生推理，不能套1.5禁用规则。参数与prompt分别报告；stream/max_tokens/model/user等差异不被messages相等隐去，也不在本任务追加参数验收。

## PROD五agent模板映射与白名单边界

|PROD原agent|对应TEST证据|能证明什么/不能证明什么|
|---|---|---|
|256917438512284672 用户画像|TEST用户画像-test，agent255107338300556288|证明本TEST模板的正文相等；不证明PROD当前模板逐字相同|
|257085994022484992 沟通摘要|TEST沟通摘要-test，同上共享agent|证明本TEST模板的正文相等；PROD两个独立agent不能当作共享TEST agent直接套配置|
|256919048417231872 服务SOP分析|TEST应用256327049255322624，agent256325360053917696，V2 fixture|证明传入执行器的完整messages相等；fixture已含“已知SOP服务要求”，不据相等自动纳入无前置知识库白名单，是否排除由主Worker结合前置读取归属决定|
|263057785613229056 分层原因-高中|TEST预测分层原因agent262172718139452416|只证明TEST一个模板，未按高中部门路由重放，不冒充高中模板完成逐字核验|
|263080101791455232 分层原因-素养|同一个TEST分层模板|未按素养部门路由重放；不能一份TEST证据当两份生产模板证据|

原需求归档README中的PROD清单是映射依据；本轮没有新读生产配置，不确认模板版本现值。owner已排除全部前置知识库，本报告不恢复任何知识库替换任务，也不把“SOP输入相等”自动转换为“无知识库所以可替换”。此轮只交付续班prompt事实及原因，未调用业务、未改代码/配置/公共文档。
