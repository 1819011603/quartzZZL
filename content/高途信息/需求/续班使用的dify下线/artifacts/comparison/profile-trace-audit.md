# 指定画像trace原始请求复核

结论：完整HTTP不相等；messages正文相等。此前“system_chars=3494”字段命名错误，这3494字实际是外层user.content，不是真正system消息。不能用messages相等替代全部请求等价，也不能用此次TEST通用agent重放宣称原生产应用配置完整等价。

|字段|旧344ab83c|新bc6a6825|
|---|---|---|
|来源|litellm，2026-11-25 10:49:52.064|litellm，10:49:58.933|
|外层messages|仅1条user|仅1条user|
|content|3494字符 / 8712 UTF-8字节|3494字符 / 8712 UTF-8字节|
|content SHA256|7015cd89381788f6e8784642b98e8f463ce308992321428c5fedd3ce0f613afa|同左|
|完整body字节数|9001|8998|
|model|doubao/Doubao-1-5-pro-32k|doubao-seed-2-0-lite-260428|
|response_format|省略|json_object|
|user|Dify EndUser UUID|省略|
|stream|true|true|
|max_tokens/thinking/temperature|均省略|均省略|

正文中的system/user是模板拼接的JSON样式文本，包含未转义换行和引号，严格JSON解析失败；模型实际收到的是一条user文本，不是system+user两条角色。两边共同保留了该旧格式，本轮不改变提示词。

原始记录重新从指定trace精确查询，每侧唯一Chat_completion received记录，外层完整JSON可解析，且与此前归档对象完全一致。比较仅解析HTTP JSON转义，不strip正文、不重排角色、不修复内部文本；原始body及日志完整保存于profile-replay-current/trace-audit/。完整body hash、Pod、时间、镜像见profile-trace-audit.json，不能用不同body hash否定其content相同。

旧入口91eeae60响应对应message d9bc6161-e05d-4b70-88cc-d2ebc92dcaf1；Console详情EndUser=11ef22be-8a22-46bd-9567-820f390799fe，与旧下游HTTP user一致。旧日志还明确记录模型redirect到doubao-seed-2-0-lite-260428，completion model=doubao-seed-2.0-lite；请求别名层和实际模型层不能混比。路由日志见trace-audit/old-model-routing.json。

重要证据限制：旧侧复用了已发布TEST通用agent（空pre_prompt、无工具、旧豆包配置），并直接传入归档画像flat prompt；它不是原生产画像app本次运行，也没有完成原生产app全部配置的逐字段复制核验。历史映射中生产画像agent为256917438512284672，与TEST画像/摘要共享agent不同。当前能证明此次旧TEST链路与新链路messages相等，不能证明所有原生产app行为都已覆盖；未遗漏这一限制继续作等价结论。

输出抗性归类仍有实质差异；json_object是可验证的请求差异，当前没有证据证明它就是归类差异原因，也不能直接归因随机。此次仅只读取证，无新增生成、配置写入、代码修改或部署，无在途操作。
