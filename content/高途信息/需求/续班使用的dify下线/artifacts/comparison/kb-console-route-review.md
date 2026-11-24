# Console泳道与空间机制复核

2026-11-24；仅只读仓库、已部署代码摘录及主Worker本轮查询产物。本子任务不发送接口请求，不读取/输出Cookie，不改路由、权限或凭据。

## 实际目标结论

本轮`os.baijia.com/dify/api/console/api/datasets?page=1`响应声明`x-env=production`、`gapm-appid=dify-api`，trace `392de8bc-4b9b-4960-8778-5b1bf81d7f1c.0.1`。因此本次证据支持请求落到生产标识的Dify API，而不是凭两个test头就认作TEST服务；尚无后端Pod/IP与镜像回读，不把响应环境标签进一步外推为已验证某个具体生产实例。

请求同时含ingress-traffic-env=test-gtbg-dev-2、traffic-env=test-eco-8。已有本地Dify API代码搜索未命中这两个头或Cookie泳道选择逻辑；未找到os入口实际Ingress/APISIX/Nginx配置，不能证明头优先级、Cookie优先级、头是否忽略/重写或无匹配时如何回退。现有/tmp/dify-route-detail.json实际是模型caller重定向配置，不是os反向代理路由，不能用于裁定HTTP泳道。

referer路径中的spcAm3oupwKuWRMD8UV是当前页面空间线索，1043df8c-f3d3-44b3-accd-ec2051c0c4a3是素养workflow应用；路径不是请求dataset ID。本次datasets URL仅page=1，没有显式space参数。未找到运行代理按referer选空间的证据，不能断言referer切换了tenant或授权。应用绑定需看related-apps及workflow配置，不靠referer单独证明。

## 可见性新证据与旧403边界

| 项目 | 本轮可证明事实 |
|---|---|
| 列表 | total=2，has_more=false；仅说明此次身份、路由和筛选上下文下完整两项，不是平台所有知识库 |
| 原库 | 86233d1a-bddf-4a15-a229-c90b6a061c57，名称“降退费服务建议话术库”；列表可见且详情成功 |
| 原库空间 | 当前space_ids同时含spcAm3oupwKuWRMD8UV与spczjG62GXkZ0ZSOBYS；不能再只按旧单空间归属判断当前可见性 |
| TEST命名项 | 30a822a4-32f5-49e8-b497-eaad5f8280de，名称TEST-dify-migration-20261124-isolated；名称带TEST不代表请求落测试环境；亦不等于此前真正TEST Service API成功的0105aec9库 |
| 关联应用 | 主Worker本轮related-apps返回5条、去重3个app UUID；存在同应用跨空间重复，不能把5行当5个独立应用，更不能凭此替换4个正式知识库路由 |

旧报告的403确实属于当时zhangzeling对spczjG62GXkZ0ZSOBYS的空间详情及原库访问，仍是历史证据。但“当前原库Console不可见/必须先给旧空间授权”已不能作为全局结论：本轮同原库详情成功，且已增加/具备另一个空间关联。不能反推原spcz空间详情现已授权，也不能断言谁在何时变更关联，未做相关审计。

## Console与Service API必须分开

已部署代码摘录expanded-refund/deployed-permission-code.txt证明Service API先由dataset token确定creator_account，再取其Teable角色空间与dataset关联空间求交；并有tenant、token类型等校验。新增空间关联可能改变可授权路径，但Console Cookie当前可见不等于已有匹配该生产dataset的Bearer token，也不证明token创建人具备查询权。此前TEST token请求生产返回401仍是该次身份/目标组合的历史事实，不能用它否定本轮Console成功，也不能由Console成功推出该token已有效。

因此需纠正文档为：**当前原库Console列表及详情已可访问，旧空间403不再构成原库全局不可见结论；后端生产Service API凭据仍需按实际token创建身份、tenant和当前空间交集核实，本轮未新建/试用凭据或检索生成。** 不需要因名称或头冲突直接换库、改权限或修改共享泳道。

证据：kb-console-current/{request-evidence,datasets,dataset-detail,related-apps}.json；expanded-refund/kb-service-auth-investigation.md、deployed-permission-code.txt。本地dify-src-archive为源码归档，不等同运行代理配置或当前生产版本。
