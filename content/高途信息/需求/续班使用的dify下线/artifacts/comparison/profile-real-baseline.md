# 画像真实生产配置基准

当前基准为生产用户画像-prod v7完整配置复制到既有TEST副本，并使用原模型 doubao-seed-2-0-lite-260428。TEST模型已正常注册，配置发布后回读；未修改生产或共享网关。

|同数据验证|旧Dify TEST|新普通入口 TEST|
|---|---|---|
|下游trace|cff96ffc-9522-4b87-ba4b-3ccf50b0dc84.0.3|3fce4abd-3895-4b68-bb90-54777ac6d680.0.3|
|messages|单条user，内嵌system/user为文本|逐字相等|
|有效thinking|开启，1593推理tokens|开启，753推理tokens|
|保留差异|Dify EndUser UUID|额外json_object，不复制UUID|

旧0-token样本2a220458使用了替代别名，该别名重定向强制注入disabled；因此不是当前生产原模型的有效参数基准。历史完整证据保留，不能用模型映射到相同目标推定所有行为一致。

最终TEST共享画像/摘要agent已撤回实验disabled并发布回读，releaseKey=20261125115220-188a49b33afd4907。新旧推理token数和输出文本无需逐字相同；当前只证明本样本消息与thinking状态对齐，不证明所有业务语义普遍等价。

当前完整请求响应见[profile-direct-baseline](profile-direct-baseline/summary.json)，配置证据见profile-real-baseline/direct-test-detail.json、direct-test-publish.json。生产配置来源prod-detail.json；底层历史副本和反例不删除。
