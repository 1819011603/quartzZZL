# 正式知识库接入剩余条件核实

2026-11-24；仅正常 Console/Teable GET，经现有 Cookie 代理；无环境头、无身份冒用。生产响应 x-env=production、gapm-appid=dify-api。未修改代码、TEST配置、生产资源或四正式应用路由。

| 核实项 | 当前实测 | 结论 |
|---|---|---|
| 原库86233详情 | HTTP200，enable_api=true，high_quality | 当前可见且允许API，不沿用旧403 |
| 原库关联空间 | spcAm3oupwKuWRMD8UV、spczjG62GXkZ0ZSOBYS | 包含续班AI |
| 本人正常空间列表 | HTTP200，张泽灵个人空间owner、续班AI owner、企业空间commenter | 与原库有关联空间交集；旧空间缺权不是当前已证阻塞 |
| 当前Console dataset key元数据 | GET /dify/api/console/api/datasets/api-keys HTTP200，data数量0 | 本人正常Console目前无可取用现存dataset key |
| 生产Service检索 | 本轮未发起 | 无已授权可用生产凭据；未创建key或使用他人key |

## 实际剩余与边界

当前不能完成正式Service检索。最小外部缺口是提供/配置一个**已授权给当前调用主体、生产租户有效的dataset Service凭据**；当前职责明确禁止新建生产凭据、使用他人凭据，因此本轮到此收束。不是要求重新登录，也不要求先授予旧spcz空间权限。正常登录、原库可见和enable_api已被当前成功响应证明；真正Service token创建主体的空间query校验仍须持有授权凭据后实测，不能由Console owner角色直接宣称通过。

按既有运行源码，key列表按current_user.created_by过滤。因此此次0条仅证明当前本人正常Console无现存可用key，不证明全生产没有key。不遍历他人凭据、不从日志搜取密钥，不把应用app key或TEST dataset key当生产dataset key。历史TEST→PROD 401不重复调用。既有TEST Java端到端成功证据继续复用kb-service-e2e.md，不扩张为正式库通过。

## 当前证据

脱敏原始白名单响应：[remaining-kb-access-evidence.json](remaining-kb-access-evidence.json)，含请求路径、时间、HTTP和环境标识；未保存密钥值或Cookie。

- key列表trace：6a412a65-e870-492e-91b4-e4e6479c8a21.0.1
- 空间列表trace：5b7fbd3a-ea34-4bcc-b489-5647d67fea1c.0.1
- 原库详情trace：c1c61983-2dea-496c-9149-3811c13bd750.0.1

只读调查已完成；正式Service检索因上述外部凭据缺口未完成。无在途操作，无需取消/恢复任务。未改飞书及其它归档。
