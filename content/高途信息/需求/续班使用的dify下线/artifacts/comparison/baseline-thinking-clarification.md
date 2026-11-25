# 画像与摘要thinking基准说明

结论：最终旧新均开启，是恢复生产原配置后的TEST实测；不是直接证明生产每次请求都开启。此前称替代别名副本为完整生产基准不准确，已纠正。

|证据层|已确认事实|证据|
|---|---|---|
|生产只读配置|用户画像-prod v7、沟通摘要-prod v3均使用doubao-seed-2-0-lite-260428；provider为openai_api_compatible，completion_params仅stop=[]，没有显式thinking|profile-real-baseline/prod-detail.json；thinking-related/摘要-prod.json|
|配置比对|两生产应用model_config与最终既有TEST副本一致，仅人员时间及file_upload扩展名排列不同（多重集合相等）|profile-real-baseline/direct-test-detail.json|
|路由快照|PROD35941/TEST35943中旧doubao/Doubao-1-5-pro-32k重定向目标并force注入thinking.disabled；目标本身无重定向、部署defaultParams为空|strict-v2-model-map.json；历史控制面快照，不冒称当前生产运行实收|
|旧反例运行|2a220458先发生旧别名redirect，再记录thinking注入，响应推理0|thinking-effective-alignment/old-runtime-injection.json及原响应|
|最终TEST实收|直呼原模型，画像1593/753、摘要806/751，两组旧新messages逐字相等，均有reasoning_content|profile-direct-baseline/；thinking-related/|

初始画像TEST副本v1因名单限制把生产原模型替成旧豆包1.5别名，其他生成配置保持；这个替换并非行为无损。最终在TEST合法注册原模型后，将同一个副本改回原model并发布为v2，未为追求输出一致更改提示词、thinking或业务输入。摘要复用这一副本，是因为逐字段比较确认其完整生成配置也与摘要生产配置相同；输入使用摘要原数据，不把画像输出作为摘要基准。

直呼目标不会经过“旧豆包1.5→目标”的强制关闭规则。TEST实际响应证明该路径本次开启，所以撤回新侧实验disabled，保留原模型省略thinking的行为。生产配置本身省略thinking不能单独证明开启，部署默认参数为空也不能推定供应商默认；生产运行时实际是否每次开启仍未直接观测，未生产生成。严谨表述是“按生产配置在TEST复现，旧新thinking一致”，不是“已实测生产旧侧开启”。

|场景|旧Dify TEST下游trace|新链路TEST下游trace|
|---|---|---|
|画像|cff96ffc-9522-4b87-ba4b-3ccf50b0dc84.0.3|3fce4abd-3895-4b68-bb90-54777ac6d680.0.3|
|摘要|ffe40068-955e-4044-9eeb-ac8641740dfd.0.3|66c8b9fa-a1d0-4fa2-a305-6e24548ef9ce.0.3|

本次说明仅复核已有证据，无新增业务调用、配置修改或生产生成。
