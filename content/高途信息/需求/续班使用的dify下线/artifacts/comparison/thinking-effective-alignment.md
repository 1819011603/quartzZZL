# Thinking有效行为对齐

已修正并验证TEST旧别名对照中的画像/摘要实际thinking差异；不能外推当前生产画像应关闭thinking。

旧trace2a220458运行日志明确先redirect、再注入thinking；控制面历史记录force disabled。新直呼目标跳过该路径，实际reasoning_tokens=1202。仅在student-data TEST共享agent255107338300556288增加params.thinking.disabled，模型、路由、提示词未改。发布20261125114552-188aa6ecfba6978c，完整发布值与目标回读相等。

|场景|新trace|messages|有效响应|
|---|---|---|---|
|画像|a5d885f0-835c-4466-b91d-8be3f65a3961.0.3|与旧2a220458逐字相等|reasoning_content=null，reasoning_tokens=0|
|摘要|8ef8ed4f-165e-4e0d-8b8f-0124cbff4de4.0.3|与既有摘要样本逐字相等|reasoning_content=null，reasoning_tokens=0|

完整HTTP/invoke/LLM响应、注入日志、发布/回读见thinking-effective-alignment目录。不是仅凭入口省略判断通过。

关键限制：生产画像v7直接用doubao-seed-2-0-lite-260428；TEST副本因名单限制改为doubao1.5旧别名，虽映射同目标却额外关闭thinking。因此本次是旧别名兼容实验修正，尚未完成当前生产直呼模型有效基准核验；不能把额外disabled推广到生产。画像/摘要共享TEST配置不代表两生产独立应用都已适配。分层只为同因候选，尚未修改或生成。

无代码改动部署、无共享网关或生产写入、无在途操作。后续应完成直呼目标的TEST基准配置条件，再决定最终TEST画像策略；当前局部disabled已发布，不能当成“未写”。

Apollo：https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default
