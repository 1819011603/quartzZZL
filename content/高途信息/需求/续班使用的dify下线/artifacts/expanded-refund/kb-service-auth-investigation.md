> 2026-11-24新证据纠正：当前原库86233的Console列表和详情均成功，关联空间包括spcAm3oupwKuWRMD8UV及旧spcz空间；下文403/凭据结论仅适用于当时身份和请求，不能概括当前原库不可见或所有生产token不存在。Console可见仍不等于Service API授权。详见[新事实](../comparison/kb-console-current/fact-correction.md)及[路由核查](../comparison/kb-console-route-review.md)。

# 权限现场与真正TEST Service API接通

2026-11-24。本轮读取PROD Pod dify-api-78886c7f97-8lhxw（10.243.8.88）和TEST Pod dify-api-84cf56596c-zbl8j（10.255.160.7）；代码根/apps/srv/instance。生产未写配置/权限/表、未检索或推理。

## 实际TEST已成功

从TEST部署配置确认Console=https://test-os.baijia.com/dify/api，Service=https://test-dify-open.baijia.com/dify/api；不是原os共享生产平台。现有TEST Cookie身份为gongxuemeng/id177071（并非PROD zhangzeling/id151350），未冒充或换用别人密钥。

通过正常Console API创建only_me隔离dataset `0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce`（TEST-service-retrieval-20261124），economy。通过正常API创建当前TEST身份的新dataset token，id `4f5a165b-b2b6-45d5-8cc8-0d2ffa95e147`，描述TEST-service-retrieval-20261124。无PROD凭据创建。部署版本key不支持单dataset绑定，因此该key是TEST环境dataset类型key，不宣称单库scope；本次仅用于隔离库。

Bearer调用POST `/dify/api/v1/datasets/0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce/document/create-by-text`成功，文档9e160ead-c8d2-4c7d-91fa-95cc3a9f311c。随后同Bearer调用POST `/dify/api/v1/datasets/0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce/retrieve`，使用既有request.json（业务原因/分类query，keyword_search/top_k4/reranking=false），HTTP200且records=4、包含话术正文。证据 `kb-test-retrieval/real-test-import.json`、`real-test-retrieve.json`、`real-test-create.json`。这次是正式Service API，不是Console Cookie检索。

采用源导出文本、automatic分段、economy关键词索引；不声称与生产分段/向量召回等价。未修改4个知识库正式路由。

## PROD key列表0的确定原因

运行代码controllers/console/datasets/datasets.py:983-993实际SELECT ApiToken条件为type=dataset、tenant_id=current_tenant、created_by=current_user.id。与本地归档新版本的workspace全量列表不同。生产容器SQL只读事务查询api_tokens按created_by聚合：14个创建人各1条，无151350。因此当前zhangzeling可见0是本人未创建，不代表生产没key。未读取任何token值、未使用其他人的key。

运行创建代码:1006-1037只接description，保存tenant_id/token/type/created_by，未接dataset_ids或单库绑定。不能照本地归档新代码给生产创建所谓单库key。因此没有在共享PROD工作空间创建服务凭据。

## 原dataset403的权限路径

生产只读SQL `gt_dataset_space_joins`确认86233d1a-bddf-4a15-a229-c90b6a061c57关联空间spczjG62GXkZ0ZSOBYS（刘家良空间）。部署datasets.py:129-158检查get_user_role_spaces(current_user)，与dataset关联空间求交。无交集时先抛Forbidden，但内部except Exception又包成“Unable to verify space permissions for this dataset.”；因此该错误会掩盖明确无空间权限，也可代表Teable调用异常。现有Teable源表直读403与此吻合，但本轮未取得当前账号完整Teable角色空间列表，不能断言已排除Teable接口异常。

生产部署wraps.py:288-328要求dataset.enable_api、dataset类型token、正常tenant/owner；额外query权限链见兄弟报告kb-deployed-context.md（token创建人的Teable空间查询权）。Console tenant owner身份不能代替Teable空间成员权；用他人key绕过不可接受。

## 最小剩余协助与状态

TEST服务链路已无凭据阻塞，主Worker可用真实检索结果继续模型。生产仍需正常的空间query授权与匹配服务身份凭据；若要解除当前个人403，需确认/赋予zhangzeling对spczjG62GXkZ0ZSOBYS的可见/查询权，先排除Teable角色接口异常。本轮不代改。

TEST新key仅保存/tmp/kb-test-service-key.json（0600），报告不含值；供同机主Worker读取集成，后续应进TEST安全配置并删除临时文件或撤销临时key。TEST新dataset、文档、token保留待复验清理；此前共享平台隔离副本30a822a4…也保留，勿与新TEST库混淆。未清理任何生产资源。


## 2026-11-24空间权限根因闭环补证

本次调用部署代码使用的同一路径GET `https://os.baijia.com/api/dify/user/spacelist`（当前zhangzeling登录Cookie），成功返回JSON数组，无接口异常。实际可见空间：
- spcjE2Q2agjjjJ2GYZc，张泽灵的空间，PERSONAL/owner；
- spcIHRmiYeOUfzoVvpu，企业空间，ENTERPRISE/commenter；
- spcAm3oupwKuWRMD8UV，续班AI，TEAM/owner。

不包含原dataset关联的spczjG62GXkZ0ZSOBYS。进一步GET `/api/space/spczjG62GXkZ0ZSOBYS`明确返回403 restricted_resource：“you have no permission to access this space”。这证明当前确实缺目标空间访问授权，不是仅凭Dify包装错误猜测；不追认历史时点绝无瞬时异常。

部署`services/gt_external/gt_teable_api.py:339`调用api/dify/user/spacelist；:302按Account.name向Teable传递内部身份，权限判断以用户身份对应空间列表为基础。本轮只使用本人已登录Cookie只读，没有生成内部身份token、使用他人key或改权限。

最小授权对象：原降退费dataset86233d1a-bddf-4a15-a229-c90b6a061c57关联的Teable空间spczjG62GXkZ0ZSOBYS（刘家良的空间）；当前需访问主体zhangzeling（Dify id151350）。应由该空间owner/admin通过正常授权授予可见/查询权限，并保证未来dataset服务key创建主体拥有同样query权限；不是修改ai_agent/app token，也不是再授予共享tenant owner。

现有Dify文档来源记录creator_id=59927、creator_name=liujialiang、space_name=刘家良的空间，可作为定位资源维护人的线索；当前账号无权读取该空间详情，因此未验证其当前owner/admin成员名单，不把历史导入创建人冒充已确认现任管理员。没有联系任何人或申请权限。

证据：kb-test-retrieval/prod-current-space-roles.json及prod-target-space-denied.json。

### TEST接入参数（已成功，不重复调用）

Service base：`https://test-dify-open.baijia.com/dify/api/v1`；POST `/datasets/0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce/retrieve`。
Headers：`Authorization: Bearer <TEST dataset token>`、`Content-Type: application/json`；本机仍经8888代理。此前实际HTTP请求未附traffic-env，落真正TEST Dify默认环境；后端student-data调用LLM的test-gtbg-dev-1是另一层泳道，不应混写成Dify泳道。
Body沿用kb-test-retrieval/request.json；结果real-test-retrieve.json。密钥只保留/tmp/kb-test-service-key.json（0600）；字段token供同机获授权进程读取，不进报告。当前scope内权限调查已完成；生产授权缺口如上，未改生产。TEST服务凭据/隔离资源保留供主Worker集成，未重复检索。

## 凭据来源链路最终核对（2026-11-24恢复后）

本轮复用此前容器和源码证据，未重新读取或输出任何明文凭据：

- **应用调用 key**：student-data 的 `ai_agent.access_key`，由 `AiApplicationExecutor` 放入 `AiModelCallOption.accessKey`；Dify 应用链路 `AiAgentAccessHelper` 将其作为 `/chat-messages` 的 Bearer。它属于应用级凭据，不能用于知识库 Service API。
- **知识库 Service API 凭据**：Dify `ApiToken` 中 `type=dataset` 的 token，生产 `/datasets/{dataset_id}/retrieve` 先按 Bearer 查 token，再校验 tenant、dataset token scope/绑定、`enable_api` 及创建主体对应的 Teable 空间查询权限。Dify 源码归档 `controllers/service_api/wraps.py` 及生产/TEST 容器抽取代码均支持该链路。
- **Console 登录态**：`os.baijia.com` 的 Cookie 仅用于 Console API/空间权限查询和 hit-testing；它不是 Service API Bearer，也不能代替 dataset token。此前隔离 Console 检索成功不等于后端 Service API 凭据可用。

生产实际目标 `https://dify-open.baijia.com/dify/api/v1/datasets/86233d1a-bddf-4a15-a229-c90b6a061c57/retrieve` 使用 TEST dataset token 返回 401 `Access token is invalid`。因此此前“去掉 test 域名/更换 dataset 即可”的假设已被实测排除；当前缺口是生产环境、生产租户且具备该 dataset/Teable 空间 scope 的 dataset Service API token。个人 Console 身份对目标空间 `spczjG62GXkZ0ZSOBYS` 返回 403，已由 `/api/dify/user/spacelist` 和空间详情接口只读核实；这与 401 属于不同身份层，不能互相替代。

本轮未修改生产凭据、权限、数据、配置或路由，未触发生产模型生成。没有找到可安全用于该生产 dataset 的现存授权 token，因此未进行第二次生产 POST；TEST Java 端到端成功证据继续复用 `3eaabb15-c22b-48f9-bcb4-7b0fd7783511.0.3`。
