# 13个正式非知识库应用：旧Dify消息基准

只读现有归档及pairs.json，2026-11-24。13=续班5+退费8；原17减去问题建议高中/素养、降退费建议精品/素养4个知识库agent。11历史对照不是13正式应用逐一实收：含2个已排除建议样本，也未覆盖所有学部。禁止将11组统一处理为单user。

## 格式类别（供实现）

- A 动态flat：真实messages仅一条user，content=应用原始DynamicPromptGenerator.generate得到的flat。flat内含原core_prompt+后处理约束、userQuery+动态数据；保留原换行、伪JSON、通用句及标签，不能先用gateway_core_prompt替换原core再生成flat。
- B Dify外部system + 动态flat user：真实messages=[system(Dify pre_prompt原文), user(应用原始flat)]。Dify系统模板和应用core是两层，不能合并到system，也不能把外部system塞入user。样本旧system常比归档pre_prompt多末尾换行，严格比对时以实收/对应Dify渲染为准。
- A-V2：与A同样单user，但content来自调用方已经生成的actualQueryPrompt；不能重生成、拆分或再次加system。SOP服务规则已包含在里面。

## 正式13项映射

应用号指ai_application.number；agent号另列，不能互换。PROD映射为既有快照，不新查库。

|正式场景|PROD应用号 / agent号|格式|旧system、user来源及实收基准|
|---|---|---|---|
|用户画像|256923739884667904 / 256917438512284672|A|无外部system；应用core+后处理+动态数据→flat。pairs“画像”，2a9ff650-ba6f-4bf2-93f8-88034f864c93.0.3。TEST样本，不冒称此PROD应用实收|
|沟通摘要|256923816171717632 / 257085994022484992|A|无外部system；原应用flat。pairs“摘要”，15760243-f225-4246-a103-c9565c2652ba.0.3。TEST画像/摘要共享agent，生产独立|
|服务SOP分析|PROD应用号本次已读映射未提供 / 256919048417231872|A-V2|无额外system，直接保留actualQueryPrompt。TEST应用256327049255322624/agent256325360053917696；pairs“SOP V2”，旧315c294d-dbc3-4d8f-adc6-e036ad96d1e1.0.3；完整user13647字，不重跑不重拼|
|分层原因高中|263057935240821760 / 263057785613229056|A|原分层core+后处理+动态特征flat；pairs“分层修正后”，旧3c9e6b70-e6f3-4f95-883b-14408cdafc2b.0.3；只直接验证TEST default，正式高中映射来自department-PROD-mapping.json|
|分层原因素养|263080132187550720 / 263080101791455232|A（同入口依据）|同生成机制，用此应用自己的core/动态配置；没有独立素养分层旧实收，不能复制高中正文。映射快照与调用路径支持类别，不支持两者正文同文|
|根因精品|256995936629163008 / 256995079971961856|B|外system=精品根因pre_prompt；内flat core=“退费根因分析”+RefundRationaleSummary输出约束及过滤；userQuery为RefundReasoningContext.content。pairs“退费根因”，a32fe4b6-6269-4882-8d39-81c76f8ca23e.0.3（TEST同类）|
|根因素养|261425035474903040 / 261424983727715328|B|素养根因pre_prompt与精品快照同文2254字；应用core/后处理也同配置。复用类别证据，未独立实收此PROD应用|
|旅程精品|256995767298823168 / 256994902246699008|B|外system=当前精品旅程2482字（含resolvedRefundReasonList）；正式内flat core=“请按要求分析用户数据”，after_processor为空。历史TEST旅程bfd44413-31f5-493d-904b-e670783ff2c4.0.3的内core却是“退费旅程分析”且有JSON/过滤后处理；不能照抄该TEST内层当正式基准|
|旅程素养|261425336093323264 / 261425291830803456|B|当前素养旅程与精品pre_prompt同文；正式内flat同通用句、无后处理。历史TEST外system还缺已解决原因字段，不能为追旧TEST相等删除生产当前合法字段|
|体验精品|256995860148134912 / 256994989452607488|B|外system=精品体验2381字；内flat core=“请按要求分析用户数据”，无后处理。pairs“课程体验”，e02d7092-ee55-4e73-b731-b6f31ef2fb6e.0.3|
|体验素养|261425205028651008 / 261425172233344000|B|素养体验与精品pre_prompt同文2381字；正式内flat同上。TEST同类实收支持格式，不声称此应用独立实收|
|NPS精品|256996044560210944 / 256995228385317888|B|外system=精品473字pre_prompt；内flat通用句“请按要求分析用户数据”，无后处理。pairs“NPS”，d2003cc1-b573-4e1c-8918-d3a4d162fe62.0.3|
|NPS素养|261424803504732160 / 261424755557579776|B|外system=素养321字pre_prompt，不能用精品473字；内flat通用句、无后处理。pairs“素养NPS”旧8c802dc4-ed69-4533-b63a-3851e20bb83d.0.3，是后续TEST复制补证，已优于早期“无实收”报告|

## 实现边界与关键反例

1. 普通syncRequestTask第四参数extraInfo，不是显式prompt。退费RefundReasoningService使用普通动态生成；真实V2显式prompt调用为SOP。不能把所有调用统一V2单user。
2. A恢复原flat，但B必须保留Dify外部system和原应用flat两消息。gateway_core_prompt若承载Dify系统模板，只能放B外层system，不能替掉内层原core/标签。
3. 旅程基准冲突是确定事实：正式PROD内core通用句、无后处理，历史TEST内core场景标签+后处理；外部模板也有版本差异。适配器应读取各应用真实原配置，不能硬编码“退费旅程分析”或以历史TEST旧模板覆盖正式新指令。
4. 本任务仅messages格式；既已修正的thinking.disabled、分层response_format.text等不回退。SOP A-V2已相等，不必因普通路径改造重复改变它。
5. 排除4个知识库agent：256918735665808384、256918818763359232、261424592068814848、256995156763347968。pairs里“降退费/素养建议”的工具/单system工作流形式不纳入本13项适配规则。

## 可直接复查来源

- comparison/pairs.json：11项sides[0].request.messages原始旧请求及trace；无需从摘要猜角色。
- expanded-renewal/department-prod-templates.json、department-PROD-mapping.json：4项续班应用映射；SOP生产应用号缺口如上，不编造。
- expanded-renewal/refund-current-prod-templates.json：8正式应用number/agent/core/后处理；refund-current-精品/素养*.json和refund-current-suyang-nps.json：Dify模板。
- expanded-renewal/prompt-current-refund.md是早期阶段说明；素养NPS后续实收以pairs为准。
- expanded-renewal/sop-real-entry.md、expanded-diff/prompt-current-renewal.json：SOP真实入口与续班字符证据。

结论：5项续班采用原flat单user（SOP保留现有V2），8项退费采用外部Dify system+原动态flat user。类别可共用实现，但正文必须按应用配置；正式13与历史11不能一一硬映射。

## Dify末尾换行机制补证

本机归档Dify源码 `/private/tmp/dify-src-archive/api/core/prompt/simple_prompt_transform.py:163` 在pre_prompt非空时执行 `prompt += pre_prompt + "\n"`，随后208行创建SystemPromptMessage。旧NPS321→322、473→474及根因2254→2255的实收长度吻合。B模式应保留pre_prompt原文并追加一个换行，不trim，也不以末尾已有换行判定跳过追加。该源码机制与已保存实收交叉支持；本轮未重新查询部署代码。
