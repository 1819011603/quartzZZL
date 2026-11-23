# 五场景原始日志精确复核
只读2026-11-23既有日志；部署91012878。按service=litellm且Chat_completion request筛选，以完整TID配对，不用messageId代替trace。轮次数仅针对已保存日志，不外推不可见调用。

## 旅程
|环境/轮次|完整TID|时间|service|角色|tools|
|---|---|---|---|---|---|
|prod/1|bfd44413-31f5-493d-904b-e670783ff2c4.0.3|2026-11-23 19:22:49,960|litellm|system,user|0|
|test/1|bfd44413-31f5-493d-904b-e670783ff2c4.0.3|2026-11-23 19:23:24,406|litellm|system,user|0|

|参数（首轮）|PROD|TEST|
|---|---|---|
|enable_thinking|"<未传>"|true|
|max_tokens|"<未传>"|8192|
|model|"deepseek/DeepSeek-R1-250528"|"deepseek-flash"|
|stop|"<未传>"|[]|
|stream|true|"<未传>"|
|user|"ad7b115e-08f6-44b7-80fd-222057e85cf9"|"<未传>"|

system: 相等=False，旧/新字符数=2966/3290；见exact-旅程-system.diff。

user: 相等=True，旧/新字符数=302/302；见exact-旅程-user.diff。
提示词完整body按轮保存为exact-场景-环境-轮次.json；原始messages不做角色合并，diff仅额外提供旧flat展开后的对照。

## 课程体验
|环境/轮次|完整TID|时间|service|角色|tools|
|---|---|---|---|---|---|
|prod/1|e02d7092-ee55-4e73-b731-b6f31ef2fb6e.0.3|2026-11-23 19:23:42,540|litellm|system,user|0|
|test/1|e02d7092-ee55-4e73-b731-b6f31ef2fb6e.0.3|2026-11-23 19:23:55,604|litellm|system,user|0|

|参数（首轮）|PROD|TEST|
|---|---|---|
|max_tokens|"<未传>"|8192|
|model|"deepseek/DeepSeek-R1-250528"|"deepseek-flash"|
|stop|"<未传>"|[]|
|stream|true|"<未传>"|
|user|"b76f6171-90d1-4eb6-bb30-93f2afd581cb"|"<未传>"|

system: 相等=False，旧/新字符数=2633/2621；见exact-课程体验-system.diff。

user: 相等=True，旧/新字符数=302/302；见exact-课程体验-user.diff。
提示词完整body按轮保存为exact-场景-环境-轮次.json；原始messages不做角色合并，diff仅额外提供旧flat展开后的对照。

## NPS
|环境/轮次|完整TID|时间|service|角色|tools|
|---|---|---|---|---|---|
|prod/1|d2003cc1-b573-4e1c-8918-d3a4d162fe62.0.3|2026-11-23 19:24:27,614|litellm|system,user|0|
|test/1|d2003cc1-b573-4e1c-8918-d3a4d162fe62.0.3|2026-11-23 19:24:35,007|litellm|system,user|0|

|参数（首轮）|PROD|TEST|
|---|---|---|
|max_tokens|"<未传>"|8192|
|model|"deepseek/DeepSeek-R1-250528"|"deepseek-flash"|
|stop|"<未传>"|[]|
|stream|true|"<未传>"|
|user|"66dfce4b-7349-43fc-a8a6-332ae76fdecb"|"<未传>"|

system: 相等=False，旧/新字符数=485/473；见exact-NPS-system.diff。

user: 相等=True，旧/新字符数=302/302；见exact-NPS-user.diff。
提示词完整body按轮保存为exact-场景-环境-轮次.json；原始messages不做角色合并，diff仅额外提供旧flat展开后的对照。

## 降退费
|环境/轮次|完整TID|时间|service|角色|tools|
|---|---|---|---|---|---|
|prod/1|81e849b4-d461-4fd0-910a-154368d68bc0.0.3|2026-11-23 19:24:45,191|litellm|system,user|1|
|prod/2|81e849b4-d461-4fd0-910a-154368d68bc0.0.3|2026-11-23 19:24:50,133|litellm|system,user,assistant,tool,tool|1|
|test/1|81e849b4-d461-4fd0-910a-154368d68bc0.0.3|2026-11-23 19:24:56,985|litellm|system,user|0|

|参数（首轮）|PROD|TEST|
|---|---|---|
|enable_thinking|"<未传>"|true|
|max_tokens|"<未传>"|8192|
|model|"deepseek/DeepSeek-R1-250528"|"deepseek-flash"|
|stop|"<未传>"|[]|
|stream|true|"<未传>"|
|tool_choice|"auto"|"<未传>"|
|user|"f7cd8aa1-e363-4824-8836-2991f23aa9d2"|"<未传>"|

system: 相等=False，旧/新字符数=1513/1613；见exact-降退费-system.diff。

user: 相等=True，旧/新字符数=302/302；见exact-降退费-user.diff。
提示词完整body按轮保存为exact-场景-环境-轮次.json；原始messages不做角色合并，diff仅额外提供旧flat展开后的对照。

## 素养建议
|环境/轮次|完整TID|时间|service|角色|tools|
|---|---|---|---|---|---|
|prod/1|5e258635-6bba-4358-bb49-8c6017142140.0.3|2026-11-23 19:25:17,155|litellm|system|0|
|test/1|5e258635-6bba-4358-bb49-8c6017142140.0.3|2026-11-23 19:25:33,975|litellm|system,user|0|

|参数（首轮）|PROD|TEST|
|---|---|---|
|enable_thinking|"<未传>"|true|
|max_tokens|"<未传>"|8192|
|model|"deepseek/DeepSeek-R1-250528"|"deepseek-flash"|
|stream|true|"<未传>"|
|temperature|0.7|0.7|
|user|"74978896-889c-42ca-a9f7-2c556efef798"|"<未传>"|

system: 相等=False，旧/新字符数=1983/1613；见exact-素养建议-system.diff。

user: 相等=False，旧/新字符数=0/302；见exact-素养建议-user.diff。
提示词完整body按轮保存为exact-场景-环境-轮次.json；原始messages不做角色合并，diff仅额外提供旧flat展开后的对照。
## 裁决与具体内容差异

1. **旅程无检索工具证据**：bfd44413-31f5-493d-904b-e670783ff2c4.0.3只找到一条PROD实收、无tools。不能混用81e降退费的两轮证据。新system确实新增“已解决退费原因”处理要求与resolvedRefundReasonList/resolvedRefundReasonCategory/resolvedRefundReasonSummary/resolvedRefundReasonOriginal字段；另将JSON示例键加引号，去掉旧flat标签“退费旅程分析”。这不是随机输出差异，是输入契约变化。user302字符完全相等。
2. **课程体验**：旧真实system保留，旧flat标签“退费课程体验分析”被去掉，输出要求提升到新真实system；user302字符相等。精确删除位置见diff，不笼统称输入完全一致。
3. **NPS**：同样去旧flat标签、保留实质指令并提升角色；user302字符相等。旧/新system差12字符可从diff逐行核查。
4. **降退费存在检索丢失**：81e849b4-d461-4fd0-910a-154368d68bc0.0.3旧两轮均声明工具dataset_86233d1a_bddf_4a15_a229_c90b6a061c57、tool_choice=auto；第二轮含assistant两次tool_calls与两条tool结果，结果content分别1363/1152字符。新只有一轮、无tools及tool角色，未携带这两段知识。这是独立可复核的迁移缺口，不能靠提示词同义或文案随机性消解。新system另增加本班/其他班隔离要求，含“### node 大模型”“[system]”和未展开的{{#sys.query#}}、//标记。业务user302字符虽相等，也不代表检索上下文等价。
5. **素养建议不是上述检索链**：5e258635-6bba-4358-bb49-8c6017142140.0.3旧一轮、无tools，全部内容（含业务数据flat）嵌在单条真实system。新改成system+user，正文中仍留{{#sys.query#}}但把业务数据放user。旧user缺席不代表旧输入没业务数据；302字符业务正文在旧system中可以找到。temperature两侧均0.7；未发现可将降退费检索缺口归于此场景的证据。

## 参数边界

五例旧入口均deepseek/DeepSeek-R1-250528、stream=true；新均deepseek-flash、max_tokens=8192，无显式stream/user。旅程/降退费/素养显式enable_thinking=true，体验/NPS未传；素养两侧temperature=0.7且新无stop，另外四例新stop=[]。未传不等于提供商默认值确定，模型名称差异需另结合路由证据；本轮不新增网络请求。

## 证据索引与验证

summary-exact.json记录每场景每轮的完整TID、时间、service、来源文件、完整body及拆分比较结果；exact-*.json为每轮实收body，exact-*-system/user.diff为可逐行复核内容差异，parse-exact.py可重跑。原始日志仅作只读来源，未改REPORT.md。所有新旧配对脚本断言完整TID一致；五组为1/1、1/1、1/1、2/1、1/1轮（PROD/TEST）。业务response的messageId不是trace，本轮仅以日志完整TID识别。
