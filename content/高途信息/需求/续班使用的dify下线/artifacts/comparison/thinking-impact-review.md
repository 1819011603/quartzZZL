# Thinking影响：当前适用结论

## 画像基准已核清

|证据|实际值|能证明什么|
|---|---|---|
|`profile-real-baseline/prod-detail.json:model_config.model`|用户画像-prod；model=`doubao-seed-2-0-lite-260428`；completion_params只有stop=[]|当前归档生产配置直接用目标模型，不走豆包1.5旧别名|
|`profile-real-baseline/test-detail.json:model_config.model`|TEST画像真实生产基准20261125；model=`doubao/Doubao-1-5-pro-32k`|复制时更换了模型名，不能称有效参数原样复制|
|`profile-real-baseline/copied-config-diff.json:model`|明确记录上述差异|模板/messages可复用，模型有效行为基准须分开|
|`strict-v2-model-map.json`|PROD35941/TEST35943历史快照：豆包1.5重定向force thinking.disabled|旧别名注入语义有据；不表示目标直呼也被注入|
|owner给出的两个响应|TEST旧2a220458…为0；新f2e3ea9d…为1202 reasoning_tokens|该TEST对照实际行为不同，不证明生产旧画像为0|

**当前不能据此要求生产画像对应新链路一律disabled。** 复用生产提示词的TEST副本更换了模型名，该差异本身可能引入thinking关闭。若在新侧加disabled与这个副本对齐，只能证明旧别名兼容实验，不能称已经对齐当前生产画像。也不能从生产配置未显式thinking推定其真实响应一定推理开启；有效部署默认仍须实收。

## 哪些有disabled依据

|场景|判断|下一步边界|
|---|---|---|
|画像历史旧别名TEST实验|有旧别名force disabled和0-token实际证据|可以作为历史别名行为复现；不能替代当前生产模型基准|
|画像当前生产配置迁移|暂无直接disabled依据|应以直接目标模型的真实生产配置复制基准核对有效参数，保留已证相同messages|
|摘要、高中分层、素养分层|旧别名样本→新目标的同因候选；新tokens为736/338/410|只有确认当前目标基准仍保留该旧别名语义后，才有定向disabled修正依据；未确认当前生产映射，不写全部确诊|
|服务SOP、精品根因/体验/NPS|快照未见同类强制disabled|不套用画像修正；旧响应缺usage不算0|
|精品旅程、三素养根因/旅程/体验、素养NPS及两降退费|当前已存对照旧新model相同，可排除此特定“跳过旧别名force disabled”路径|不因此重跑；也不扩大为全部供应商默认已证一致|

画像/摘要共享TEST agent，不能把一次共享配置改动当成两个当前生产独立应用都已适配。直接目标模型和旧别名即使最终模型名称相同，也不等于有效参数相同。

## 交接状态

本轮只读本地模型白名单字段并修订本报告及JSON；不改Apollo/代码/飞书、不生成，无在途操作。已读取实现者新落盘画像/摘要invoke：HTTP200、rvoCode=0、reasoning_tokens均0（画像a5d885f0-835c-4466-b91d-8be3f65a3961.0.3；摘要8ef8ed4f-165e-4e0d-8b8f-0124cbff4de4.0.3；来源thinking-effective-alignment/各场景-invoke.json）。仅确认这些新调用响应；尚未取得同次完整请求和最终对齐断言，不能合并为当前生产基准“已通过”。原控制面为历史快照，新增实收需绑定实际基准模型、完整messages、有效thinking与新旧trace后再更新当前结论；不能以入口字段均省略或旧0新1202直接外推生产旧侧行为。
