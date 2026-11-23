# 实际入口、参数差异与生产只读条件

2026-11-24；主Worker通知TEST模型code0、三字段JSON成功后执行本轮只读检查。不复跑检索，不调用生产检索或生成，不修改生产。

## 本次成功入口

POST `https://os.baijia.com/dify/api/console/api/datasets/30a822a4-32f5-49e8-b497-eaad5f8280de/hit-testing`。凭据是zhangzeling（151350）的Console登录Cookie，经8888代理注入；**本次未使用Service API，也没有Bearer key成功调用证据**。原请求request.json与响应response.json已经保存，四条正文全部供主Worker模型验证。

## 隔离与差异

平台是共享Dify、非独立TEST部署。TEST隔离库only_me、名称TEST-dify-migration-20261124-isolated，创建时app_count=0，未关联正式应用。复制历史导出的69个话术分段为文件再导入，索引69/69完成。副本economy，embedding_model/provider=null，避免生产embedding推理。请求覆盖keyword_search/top_k4/reranking=false/score_threshold_enabled=false；返回4条记录score均null，正文长度914/944/53/312。

创建响应retrieval_model_dict仍显示semantic_search/top_k2的默认字段，不能把默认值当本次实际运行参数；本次以请求keyword_search/top_k4及economy索引为准。

生产已发布工作流已知：同一原dataset86233d1a-bddf-4a15-a229-c90b6a061c57、multiple检索、top_k4、reranking=false；query由directReason/categoryName构造。原dataset具体indexing_technique、embedding模型、search_method和score阈值尚未取到，不能凭工作流multiple字段认定是某个向量模式。此前README“生产高质量/向量”仅应作为潜在差异，不是已核实参数。重新分段的副本也不保证内容边界、ID、排名相同。当前仅证明平台真实检索→内容→TEST生成通路成功，未证明检索等价。

## 生产只读结果

1. Console `GET /datasets/api-base-info` 返回Service API基址 `https://dify-open.baijia.com/dify/api/v1`（api-base.json）。
2. 对 `/datasets/86233d1a-bddf-4a15-a229-c90b6a061c57/retrieve` 发OPTIONS返回HTTP2 200、空正文。没有发POST。OPTIONS可被网关统一响应，只证明可达性，不证明真实检索鉴权/处理成功。
3. Service API `GET /datasets?page=1&limit=1` 无Bearer返回401，要求Authorization以Bearer开头（service-read-auth.json）。这验证服务鉴权存在，不证明任何现成key有效。
4. 当前Console `/datasets/api-keys` 返回data=[]；key-inventory.json只保存可见数量0，无凭据。不能外推其他账号/租户无key，不能拿app的chat API key代替dataset key。
5. 原dataset详情GET仍返回403：Unable to verify space permissions for this dataset（prod-dataset-access.json）。之前documents/segments可读不等于此接口或Service API权限齐全；原dataset enable_api也尚无法确认。
6. 本地源码归档 `/tmp/dify-src-archive/api/controllers/service_api/wraps.py:357` 显示dataset类型token或resource_access_token鉴权、tenant匹配、dataset绑定scope及enable_api检查；`controllers/service_api/dataset/hit_testing.py` 声明POST /datasets/{id}/retrieve。源码不是本轮部署版本校验，作为接入条件参考，不能替代实测授权。

可复用平台检索的原理已由Console隔离试验证明；正式后端Service API仍需具备覆盖指定dataset的服务凭据、enable_api和租户权限，再做受控验证。当前未创建/修改任何共享服务key，也没有将个人Cookie纳入正式后端方案。

## 保留与清理状态

保留隔离dataset30a822a4-32f5-49e8-b497-eaad5f8280de、文档cc41e00e-0410-4b69-a6df-674911a582b4、上传文件88a7375f-af99-4fb0-8480-f7353b5da8ac用于复验；未删除。无新建Service API凭据需要撤销。测试资料位于本目录；认证Cookie由原代理管理，未导出。若后续要求清理，只删上述隔离资源，不能删除原dataset86233…或源Teable表。现有四个知识库应用继续走Dify，未做正式替换。
