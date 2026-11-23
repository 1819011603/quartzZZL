# TEST隔离平台检索实证

2026-11-24。共享Dify平台 os.baijia.com（不是独立TEST部署），登录账号zhangzeling/id151350。新建only_me隔离dataset `30a822a4-32f5-49e8-b497-eaad5f8280de`，名称TEST-dify-migration-20261124-isolated，app_count=0。未修改原dataset、应用路由、生产配置；未触发生产embedding或生成模型。

从此前只读导出的生产69段话术建立隔离副本，文件88a7375f-af99-4fb0-8480-f7353b5da8ac，文档cc41e00e-0410-4b69-a6df-674911a582b4。economy索引，完成69/69，无error（status.json）。副本是导出文本重新分段，不保证段ID或排序同生产。

实际调用：POST https://os.baijia.com/dify/api/console/api/datasets/30a822a4-32f5-49e8-b497-eaad5f8280de/hit-testing，经8888 Cookie代理，登录身份为测试操作者。request.json的query依据/tmp/kb-test-run/input.json的directReason/categoryName，沿原工作流code规则生成。keyword_search，reranking_enable=false，top_k=4；response.json返回4条records，含真实segment.content及score。可供主Worker组装TEST模型请求，不是本地假检索或纯tools声明。

差异：economy关键词索引与生产高质量/向量检索不等价，测试成功仅证明隔离数据→平台检索→返回内容通路。没有证明同query相同命中、排名或质量。未调用生产dataset检索。

Service API：平台api-base-info公开基址https://dify-open.baijia.com/dify/api/v1；当前workspace已有dataset API key列表为空。本轮未创建共享workspace服务key，实际成功入口是Console Cookie hit-testing；不能当作后端长期Service API凭证已经就绪。源码归档controllers/service_api/dataset/hit_testing.py存在/datasets/{id}/retrieve，需dataset级鉴权（不是应用app key）。

隔离资源保留供主Worker验证，不删除、不切正式路由。模型生成由主Worker完成；本子任务尚未执行后续生产只读条件核查，等待其模型验证完成通知。
