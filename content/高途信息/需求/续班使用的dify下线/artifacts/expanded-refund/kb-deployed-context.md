# 实际部署context与Service API代码核对

2026-11-24，仅只读TEST容器：baijia.base-tech.ai.teable.dify-api，Pod dify-api-84cf56596c-zbl8j，10.255.160.7，namespace=test。代码根/apps/srv/instance；pyproject.toml版本1.10.0，git HEAD未提供。不同于此前本地无git的1.20.0快照，以下直接来自部署文件。文件SHA256见deployed-version.txt。本轮未访问生产、未执行推理、未查权限表或凭据。

## context判定

实际部署`core/workflow/nodes/llm/node.py:885-956`：fetch_prompt_messages将context传给handle_list_messages，后者1170-1230逐消息处理basic模板，只执行`message.text.replace("{#context#}", context)`，随后variable_pool.convert_template，再将文本构造为原role的PromptMessage。没有在context非空时自动追加检索消息的逻辑。memory和sys_query是独立追加路径，不自动携带context。

因此对**此TEST部署、basic chat模板、无context/结果引用**：即便context.enabled=true并取到检索结果，也不会凭绑定自动把context文本塞进messages。存在引用才替换。公司代码实际替换串为单层`{#context#}`；若模板写双层`{{#context#}}`，该replace会留下外围一对大括号，不能照上游快照认定包装完全相同。jinja2走另一显式变量渲染分支，不能用basic规则代替其变量配置。

已保存生产两工作流只有system basic模板且没有任何context或结果变量引用：若生产同文件同逻辑，则该绑定不产生文本注入；本轮没读生产部署，不将TEST结论冒称为生产版本已核实。已有原始工作流配置不是运行时实收。

文件证据：deployed-context-lines.txt、deployed-render.txt、deployed-call.txt。此为部署源码结论，未伪称本轮做过TEST LLM A/B调用；主Worker可复用此前哨兵方案验证真实实收。

## retrieve接口确实存在及鉴权链

`controllers/service_api/dataset/hit_testing.py:11`注册同一POST处理器的`/datasets/<uuid:dataset_id>/hit-testing`与`/datasets/<uuid:dataset_id>/retrieve`。HitTestingApi继承DatasetApiResource，调用get_and_validate_dataset→parse_args→hit_testing_args_check→perform_hit_testing。存在路由不等于请求已成功。

`controllers/service_api/wraps.py:452`规定method_decorators=[validate_dataset_token]；:251-328读取dataset、要求enable_api、校验scope=dataset的token、要求正常tenant及owner account。:349-374代码要求Authorization Bearer，并按ApiToken.type==scope查找；普通应用app token不能当dataset token。

retrieve方法另加`dataset_permission_check(operation_type='query')`（:404-449）：get_creator_from_api_token取得token创建人，get_teable_client().get_user_role_spaces(user=creator_account)取其空间，DatasetService.check_dataset_in_spaces检查知识库所属空间；不满足抛403“您没有权限查询此知识库”。因此仅有tenant owner上下文、Console Cookie、dataset存在都不代表token创建人具备query空间权限。修改分支要求创建人一致，但本任务retrieve走query分支，不能误要求查询者必须是dataset创建人。

以上为代码检查条件，不含具体账号权限事实。权限表/凭证由另一子任务核对，本任务未触碰。原库403须根据实际错误路径判断enable_api、token类型、创建人空间等，不能直接断言缺某一项。

## 接入含义

新链路前置retrieve后必须显式把检索正文拼入LLM messages，不能只声明“context绑定”；若要复刻旧工作流而旧版确实未注入，需要明确这是补齐知识使用而不是假称旧输入完全相等。接口不需另造endpoint，但需要匹配的dataset Bearer和公司空间权限；现有代码支持不代表当前凭据已获权。无配置、代码、路由或权限修改。


## 2026-11-24增量：生产部署只读比对完成

本节替代上文“生产部署版本未核对”的旧边界；未重读TEST、未进行生产推理或任何生产变更。

发现生产有prod与prod-1两组Pod，各抽取一个：
- prod：dify-api-75848d98bf-2ssjs，10.243.45.88。
- prod-1：dify-api-78886c7f97-8lhxw，10.243.8.88。

两者`/apps/srv/instance/pyproject.toml`均version=1.10.0。以下三个文件在两生产Pod与此前TEST中SHA256全部相同：

|相对路径|SHA256|
|---|---|
|core/workflow/nodes/llm/node.py|74c2cc9483c3dea3bbde7bfbb8c029c35e8248eeace5a29a6d57149d7c304f03|
|controllers/service_api/wraps.py|1cc05b8020fc071453af7ef558e0f4aa01e1cc8f4d2482e2b938880104f386a9|
|controllers/service_api/dataset/hit_testing.py|1c3d6f4b12b8ee0407ad4fb81473dce46b4ee4c3c3bb5fbf67ff22736df77979|

因此无需重新重复读取相同源码片段：前文准确路径/行号的context替换、retrieve路由、dataset Bearer与token创建人空间query检查，在这两个生产抽样Pod对应文件中完全相同。

**对已保存生产工作流的具体裁决**：其basic system模板没有context或检索结果引用；结合现生产LLM节点同代码，可以确认该模板路径不会仅因context.enabled=true自动把检索正文追加进LLM messages。绑定可取到数据并用于元信息，不等于正文被消费。这里是已部署代码+已保存工作流配置得出的行为结论，不伪称已观察生产最终实收，也未重新刷新工作流配置。

权限结论同样只限代码：接口支持与检查条件相同，不代表具体dataset enable_api、token创建人/租户/空间权限已具备；这些事实由权限子任务单独核对。本轮没有读取任何凭证/权限表。

证据：deployed-prod-hashes.txt、deployed-prod1-hashes.txt、deployed-prod-version.txt、deployed-prod1-version.txt、deployed-prod-comparison.json。脚本断言两组各3个hash均等于TEST通过。不是20个Pod逐个校验，不声称全部依赖/内存补丁/运行配置一致。
