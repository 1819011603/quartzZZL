# 画像真实生产配置基准

真实生产app已定位并重新只读取得：spcAm3oupwKuWRMD8UV_2feb2cf6-ad1c-4e7a-b1cb-a13cc7957680，用户画像-prod，Console版本7；生产agent256917438512284672的Service /info名称与作者相符，历史应用绑定目录也指向该ID。生产未生成或切换。

独立TEST副本：spcynF7tYh4ROXnG8Xg_be734674-1475-43bb-9e05-da4e77e2291b。复制完整model_config并回读、发布ai-base成功。生成配置包括pre_prompt、prompt_type、chat/completion_prompt_config、agent_mode/tools等均保留。逐字段差异仅model名称、创建修改元数据、file_upload扩展名排列顺序（多重集合完全相等）。TEST不接受生产model名称，使用已通过路由日志核实映射到同目标的doubao/Doubao-1-5-pro-32k；不是擅换其他模型。

|本次证据|旧真实配置TEST副本|新普通入口|
|---|---|---|
|入口trace|1b942b63-c651-423d-a5d6-cfb84facd58e.0.3|f2e3ea9d-eb41-41a8-b041-63d20fba2554.0.3|
|下游trace|2a220458-cfd5-4547-82a0-295b5f386335.0.3|f2e3ea9d-eb41-41a8-b041-63d20fba2554.0.3|
|messages|外层单user，3494字|逐字相等且与原样本相同|
|参数边界|旧user UUID、映射模型|省略Dify user，额外json_object|

因此外层单user内嵌system/user文本不是仅通用agent回放造成：复制真实画像配置的TEST副本也实际产生相同结构。并未修改提示词迎合输出。两侧answer均解析为三个业务字段；完整当前/前次内容及差异见result.json，不将一次内容相同或不同断言为随机性或迁移Bug。

证据目录profile-real-baseline/：prod-detail、test-detail、test-publish、copied-config-diff、old/new-http、old/new-response、result.json。生产Service公开参数与Console配置来源均保留。无新代码、部署、README或飞书修改。私有TEST key保存在.codex/private/dify-dataset-migration/profile-real-key.json，0600，未归档；无在途操作。
