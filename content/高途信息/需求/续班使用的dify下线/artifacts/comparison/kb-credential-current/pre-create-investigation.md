# 正式知识库现有凭据调查

结论：已实际核查正常生产Console现有凭据入口，当前本人没有可取用的已存在dataset key（HTTP200/data=[]）。不是未登录、不是原库不可见、不是API关闭，也不能由此断言全生产没有key。当前账号具备正常创建所需可见权限条件，但本轮禁止新建生产密钥，未执行创建或使用他人key。未取得凭据，因此没有发起生产Service检索。

|项目|本轮实际证据|
|---|---|
|当前身份|profile HTTP200，zhangzeling/id151350|
|当前workspace|HTTP200，共享空间550e8400-e29b-41d4-a716-446655440000，role=owner|
|dataset key列表|GET /dify/api/console/api/datasets/api-keys HTTP200，响应顶层data，明确0条；另一次schema回读也为0|
|目标库|86233d1a-bddf-4a15-a229-c90b6a061c57，HTTP200，enable_api=true，high_quality|
|密钥列表权限|当前部署GET受DATASET_MANAGE保护，调用成功；查询固定type=dataset、tenant=current、created_by=current_user.id|
|正常创建条件|POST要求DATASET_MANAGE及admin/owner，每人最多10枚，当前已满足可见条件；未发POST，故不声称创建已验证成功|
|受控正式检索|未执行；当前授权范围内没有已存在可用key|

## “授权凭证”是什么

是Dify知识库Service API的dataset类型Bearer key，发请求时放Authorization头。它不同于浏览器Console Cookie、应用/chat-messages的app key及TEST租户dataset key。当前生产实现创建时绑定tenant/type/created_by，只有description输入，没有dataset_ids单库绑定参数；不能承诺单库只读scope。检索时先验证dataset类型token和目标库enable_api，再按token创建人的空间列表与目标库关联空间交集检查query权限。密钥不是绕过库权限的万能钥匙。

## 能不能拿到

通过本人正常Console，现在拿不到“已有”的，因为列表确实为空。现有权限看可通过正常创建入口产生本人的生产dataset key，不必借用别人身份或提高权限；但这会产生生产密钥记录，超出本轮明确禁止新建的边界。最小后续决定：允许正常创建本人生产dataset key，或由拥有者明确授权提供现有有效dataset key；取得后从TEST受控检索原库验证。当前不需要让用户反复登录，也不应再描述为必须申请旧空间权限。已有原库空间交集证据复用remaining-kb-access.md，实际Bearer检索权限仍须实测。

没有遍历其他人的密钥、从日志捞取秘密或绕过created_by筛选；没有生产生成/写入、没有新建/删除key，没有README/飞书修改。仓库/容器配置/Arthas排除结论复用此前调查，不重复扫描或输出秘密。

## 实际读取证据与局限

- kb-credential-current/normal-console-readback.json：时间、路径、HTTP、trace与安全字段白名单。
- key-list-schema-readback.json：确认响应字段data及0条，避免items/data误读。
- prod-key-list-create-source.txt：当前生产Pod dify-api-78886c7f97-8lhxw的列表/创建源码，未读取token值。
- prod-dataset-auth-source.txt：类型、API开启及token创建人空间query校验。

中途requests.Session遗留Cookie导致profile后续401，清理会话Cookie并按代理刷新后全部HTTP200，属于调用方式问题，已纠正；最终结论只使用成功回读。未将未成功响应的count默认值作为凭据数量证据。无在途操作。
