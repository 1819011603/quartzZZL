# 旧Dify费用身份调查：源码续接结论

## 2026-11-24 续接裁决（覆盖下方历史交接）

生产同一 Pod dify-api-78886c7f97-8lhxw（10.243.8.88）只读源码已核完身份规则；原始证据 strict-v2-cost-source-followup.txt。本地 student-data HEAD 为 5a7fbcf173d43d53c94ca84a9dfe834685f6ebb7，检查的是当前工作树，未声称此版本已部署。

- SERVICE_API 的 run_user 经 build_employee_from_mapping(force_check=True) 强制查询 Dify Account。employee_service.py 按 id > email > name 收集查询键，命中后以库中 id/name/email/display_name/avatar 覆盖输入；不存在则 ValueError，并非邮箱前缀兜底。单条输入给了 id 时不会再采集其 email/name 用作失败回退。Employee.name 无邮箱拆分 validator。
- billing_helper.py 使用规范化 Account.name.strip() 写 x-tech-ai-user-id。billing_type=run_user 只选人，nid 只选服务，空/其他两者均选；若两种身份最终都没有，则以 api_token_created_by（参数优先，否则 flask.g）查询 Account.name 兜底。无创建人、查无账号或空 name 则日志后不注入。只要 nid 已存在，就不因缺人而触发此兜底。因此旧链路不能笼统描述为始终含员工头。
- model_manager.py:347 起复制 provider extra_headers；本次 billing_headers 含任一身份键时，先大小写不敏感移除共享凭证的两种旧身份，再合并本次 billing_headers，本次优先；没有 billing_headers 时保留原 credentials。未读取共享凭证值，不能断言特定旧样本究竟使用哪条兜底。
- user UUID 是另一链：Service API wraps.py:94-123 读取请求 user，交 EndUserService；按 tenant/app/type/session_id 查询或创建 EndUser，外部 user 同存 session_id/external_user_id；models/model.py:1633 的 EndUser.id 由 uuid_generate_v4() 生成。chat/app_generator.py:161 取 user.id，chat/app_runner.py:226 传模型 user。故旧下游 UUID 是应用内 EndUser 标识，不是 Account.name 或费用员工号，不能复制为费用头。这里只读了源码，未执行 get_or_create。

### 对 Java 的明确建议

AiApplicationExecutor.java:477 当前优先 command.costUserId，否则直接取 runUser.email 的 @ 前缀；DifyRequest 则把 run_user 原对象交旧服务。两者不是源码保证等价：必须通过权威员工映射得到与 Dify Account.name 同义的登录标识，再作为 costUserId 注入；至少对真实业务样本核验 email→Account.name 相等，不能仅凭邮箱形状认证。id/email/name 多字段冲突应遵循旧优先级或显式拒绝。调用方没有 runUser 时，若要求沿用费用归属，需由主 Worker 确认旧 API Key 创建人对应费用主体后配置受控兜底（不取密钥）；不能任意硬编码历史 user UUID。quickTest 应传已核验真实费用身份，缺失应明确失败而非静默漏头。

当前完成的是源码规则与实现差异取证，不是实际员工映射或新头实收验收。尚缺具体业务 email 对应 Account.name 及该旧应用无 run_user 时实际创建人身份的只读数据证据；未查员工记录/凭据、未生成、未改 Java/配置/权限，无在途操作。由主 Worker 决定采用权威员工查询还是已核验映射，并安排 TEST 实收。

## 历史暂停记录（不再代表当前完成状态）
### 真实样本及应用费用主体补证

生产同 Pod 的 PostgreSQL 只读事务（SET TRANSACTION READ ONLY，结束 rollback）查询必要列，未选择 api_tokens.token。结果见 strict-v2-cost-account-readback.json。gongxuemeng@gaotu.cn 唯一命中 Account.id=202332、name=gongxuemeng；结合既有 strict-v2-cost-owner-readback.json 的业务样本来源，这一个样本邮箱前缀与旧费用身份相等。禁止硬编码为全局账号。

9个旧对照场景对应8个Dify应用（画像/摘要共用）：画像/摘要-test 的所有2枚 token 创建人同为 masheng(52761)；SOP 所有2枚为 chenzexin(125062)；分层-test 1枚为 wangwei53(131789)；高中根因、旅程、体验、NPS 各2枚均为 liujialiang(59927)；素养NPS迁移对照副本1枚为 zhangzeling(151350)。因此在无 run_user 且无 nid、也无预注入身份的条件下，上述应用按当前数据库与部署源码分别回退这些创建人。此处不是历史 trace 的请求头实收证明；有 run_user 时优先真实运行人。正式素养NPS原应用另有两组 token 创建人 liujialiang/huangshishuai，不能把 TEST副本身份推广为生产，也不能仅凭 app_id 在多创建人应用任选账号。

Java 可复用的权威来源是 Dify accounts 的 email→name/id 映射（旧 EmployeeQueryService.batch_query_employees 正是查询此表），不是 EndUser 表。已检查部署 controllers 中无 batch_query_employees 的公开控制器入口；目前未证实存在可直接给 Java 调用的现成员工映射 HTTP API。推荐经已有员工服务返回同义登录标识并与 Account 映射校验，或由受控服务封装该只读映射；不要让业务代码直连生产数据库或拷贝凭据。此为实现建议，未新增接口。无运行人的测试若要沿旧应用分摊，应按应用配置已核验创建人，不宜单个全局 fallback 覆盖上述不同费用主体。实际调用头验收仍由主 Worker 的 TEST 链路完成。


2026-11-24按owner收束指令暂停，未新增生成/配置/代码/权限写入。当前只读命令已结束，无在途句柄；本轮仅落本报告与代码定位证据。

## 已确认

只读生产服务baijia.base-tech.ai.teable.dify-api，Pod dify-api-78886c7f97-8lhxw /10.243.8.88，根/apps/srv/instance。grep限core/services/controllers/service_api源码，未读取凭据数据。完整定位结果strict-v2-cost-source-lines.txt。

- core/app/apps/base_app_generator.py:210 `_prepare_run_user`；:238-243 API请求读取args.run_user，id/email/name至少有一项时调用employee_manager.build_employee_from_mapping(run_user_data, force_check=True)。这是源码搜索命中，尚未读取完整方法及缺省分支。
- core/helper/billing_helper.py:55-72：依据billing_type决定是否传run_user；Employee取run_user.name，dict取name，将非空name.strip写入credentials.extra_headers["x-tech-ai-user-id"]。这与“复制下游UUID user”不是同一条链。billing_type=run_user只传run_user，nid只传nid，其余两者传递（需完整方法确认默认及来源）。
- agent_chat/chat/advanced_chat/workflow等runner调用计费helper；agent_chat app_runner.py:173-180有明确注入注释。model_manager.py:353含identity_keys={x-tech-ai-user-id,x-tech-ai-nid}，需确认是否清除旧身份/按调用注入。

## 尚不能结论

未确认Employee.name的规范化规则、email/id优先级、同名/无效映射处理；不能仅此grep就断言Java取email前缀一定等于旧计费name。未确认旧请求下游UUID的EndUser创建/传递链；不能把UUID当员工费用身份。未核对旧API无run_user时默认身份与billing_type实际配置，未发任何TEST生成来观测header。

主Worker已提供待核事实（本轮尚未独立展开源码）：Java DifyRequest.build传userTag/run_user；退费queryRunUser由subclazz assistantNumber→teacher.baseInfo.email，SOP SubClazzHelper同源；新resolveCostUserId取email前缀；quickTest无runUser、Apollo fallback-user未配。因此quickTest与真实业务费用来源不应混为一谈。

## 续接最小步骤

1. 仍只读指定生产容器，读取base_app_generator.py:210-260、billing_helper.py完整计费方法，定位employee_manager.build_employee_from_mapping实现及Employee.name定义；不读取或打印凭据值。
2. 沿app runner/model_manager确认billing_type、身份头合并优先级及按调用隔离；沿Service API EndUser构建到模型调用user字段确认UUID来源。
3. 本地读取指定实现版本Java DifyRequest、resolveCostUserId、SubClazzHelper/queryRunUser，给实现者费用身份精确映射建议：必须动态取真实费用人，不能硬编码历史UUID/示例员工；缺身份应明确失败或获准配置兜底，不能静默漏header。
4. 如需只读TEST来源查询再由续接worker判断；本子任务无生成或配置写授权。完成后向主Worker回报供W1-073b38实现者使用。

## 已有产物与其他范围

第五项tools方案strict-v2-tools-plan.md已交付；README/tasks已登记最新五项契约。当前费用身份第二项未完成，不能因tools已完成收束整项。无commit/push/部署/配置变更或后台监听。生产只读与禁止凭据输出约束保留。
