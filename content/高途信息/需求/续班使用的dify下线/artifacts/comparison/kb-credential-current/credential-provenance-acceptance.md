# 凭据来源验收补充（2026-11-26）

本轮仅历史证据核对与文档补充，未读取密钥明文、调用业务接口、新建/删除/轮换凭据。复用已有检索结果，不作当前凭据有效性复测。

## 签发、身份与范围

成功检索证据所用为生产Dify知识库Service API的dataset类型凭据，不是应用/chat-messages key、TEST dataset key或Console Cookie。生产Console使用登录身份及current tenant签发：ApiToken.generate_api_key生成，保存tenant_id、type=dataset、created_by和description。当前部署为Python/Flask，Arthas适用于Java student-data，不适用于Dify Python进程；无需为取凭据附加Arthas。

来源证据：prod-key-list-create-source.txt（运行Pod dify-api-78886c7f97-8lhxw，datasets.py:970-1038）；normal-console-readback.json确认当时生产身份151350、workspace 550e8400-e29b-41d4-a716-446655440000、owner，目标库86233d1a-bddf-4a15-a229-c90b6a061c57启用API。创建入口仅接description，没有单dataset或只读scope参数，不能宣称该key仅限原库或仅可读。

校验由Service API执行：按Bearer验证dataset类型token，检查目标库存在且enable_api=true，确认token租户正常并存在owner；query权限进一步按token创建人的Teable空间与dataset关联空间求交。证据prod-dataset-auth-source.txt及../kb-console-current/fact-correction.md。后者记录原库关联spcAm3oupwKuWRMD8UV和spczjG62GXkZ0ZSOBYS；成功检索证明当次鉴权通过，但未记录运行时具体命中了哪个空间，不外推所有库或全部权限。

## 历史创建与授权边界

authorized-key-create.json记录创建HTTP200、id=361cfa66-495d-46c2-84f8-7ce87b54b83c，客户端记录UTC 2026-11-24T16:01:05.541325+00:00（北京时间11月25日00:01:05），服务端created_at=1795536066（北京时间00:01:06）。key-postcreate-readback.json记录本人列表总数1、目标匹配1、token_readback_matches=true。创建是历史生产写入，本轮没有重复执行。

所有者授权依据：未知。已检查当前工作单提供的owner原话、上述归档及本机managed/tasks.sqlite3的本任务inbox；没有找到明确允许创建生产key的原始消息。现有文件名、旧报告“已获授权”描述和HTTP成功不能单独证明所有者授权。当前所见边界是生产只读，不能将历史创建追认为当前授权；也不能在缺少完整历史会话时断定当时必然未经授权。

## 加载、传递与实测边界

创建记录保存位置为本机私有目录中的production-dataset-key.json，记录权限0600；历史文档记录目录0700。回读记录证明当时私有文件内容与返回凭据一致，本轮未打开该文件。检索证据标明本机验证驱动经授权代理访问生产Service API，并非student-data Pod；没有证据显示该生产key写入Apollo或业务配置。

Service API要求Authorization: Bearer，已有成功请求与鉴权源码支持当次使用dataset凭据通过校验。但原始驱动脚本/命令未在本次限定证据中找到，具体读取字段、内存加载实现、请求头构造及全过程日志脱敏实现均未独立核实，不把推荐做法写成已验证事实。

authorized-production-retrieve-fulltext.json：查询“答疑反馈慢”，full_text_search/top_k4/不rerank，HTTP200、4条非空片段，trace cbc61996-27a1-4263-b504-dea8a8ef1e14.0.1。authorized-production-retrieve.json：另一业务query以keyword_search返回0条。两者输入不同，不构成单变量比较；生产四应用完整等价及Pod自动链路没做，四正式应用继续Dify。
