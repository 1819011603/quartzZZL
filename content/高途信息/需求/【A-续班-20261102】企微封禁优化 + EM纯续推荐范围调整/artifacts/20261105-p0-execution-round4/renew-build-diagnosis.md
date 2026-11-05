# renew_build 502 与停止来源只读诊断

本轮类型：requirement 的只读诊断阶段。只读核对历史请求、日志、部署代码、run记录及TEST目标数据；未重放renew_build、未造数、未执行业务写入，未改P0、业务代码、skill或MR。

## 结论

502不是建课建到一半后超时，而是造数API的参数声明与同镜像执行脚本不一致：API把publish=true转为--publish，脚本只接受--no-publish，在argparse阶段73ms内退出。已找回失败runID r-20261105171613-61c22fcd。脚本在parse_args成功后才执行cmd_build，因此本次build没有进入建课、建班、绑定或发布逻辑。该结论来自实际失败记录与实际部署文件，不是重跑结果。

此前clone请求已经独立成功，创建了TEST计划588858850300473344；应保留复用，不要再次clone，不需要为此次参数失败清理业务对象。

## 请求、环境与时间

- 原始请求：build-main-request.json（原件位于相邻原交接证据）。2026-11-05 17:16:13（北京时间）POST https://sd.baijia.com/api-qa/data-agent/scenarios/renew_build/run。
- 输入：source=585960797778243584，target=588858850300473344，subjects=语文，posts_per_subject=1，price=100，no_protect=true，publish=true；options traffic_env=test-gtbg-dev-3、timeout_s=600、confirm=true。
- 入口qa-data-agent-service运行在prod控制面（不是对生产业务造数），处理pod qa-data-agent-service-fddf958d9-4bf9w，IP10.243.9.173，镜像release-ca77991e-20261029164819；运行记录traffic=test-gtbg-dev-3，脚本业务env默认test。未向生产业务服务写入。
- 原HTTP原件只有openresty HTML502，未记录响应头/trace。SLS应用日志确认同pod 17:16:13.647实际返回502、272字节；日志trace_id为空，不能补造trace。
- run记录：status=runtime、http_status=502、duration_ms=73、outputs={}、error.message=renew_from_source.py: error: unrecognized arguments: --publish。

## 已创建、未创建与关联状态

已创建（属于17:15:33独立clone请求，不属于失败build）：

- run r-20261105171533-0f5b22cf，916ms，ok。
- gaotu.renew_master：id966，number588858850300473344，名称W1-P0-243aa61a-EM独立主计划，creator_id131951，status0/is_test_data1/isdel0，create_time与update_time均2026-11-05 17:15:33。
- 17:19原回读与本轮17:28:06独立只读事务一致：renew_master_course_relation对目标0行；renew_master_relation正反向对目标0行。该计划只是草稿骨架，不是已准备好、可售或已验证的样本。

本次失败build未创建：前后置课程、大纲、班级、课节、辅导班、保护期、课程绑定、前后置续班关系或发布。依据是实际error发生在parse_args（部署entry第146行），第147行args.func尚未执行，cmd_build中的业务模块import/建课调用都在此后。没有这些新对象的ID；不能为“清理”去删除同一时段他人对象。

技术侧新增run记录与访问日志已确认存在；未核算其他旁路用量埋点，这不影响业务对象零写入结论。未单独全表扫查同时间所有课程/班级；它们不能仅按创建时间归到本请求。此前“未知是否有半截业务对象”的担忧已由执行前失败证据解除。

## 根因定位依据

1. SLS prod app日志（log-prod-app.txt）：17:15:33 clone返回200；17:16:13 renew_build由Django basehttp记录502。TEST日志为空是因为查的是业务TEST，不是sd工具入口的prod控制面，不能据此推断没有请求。
2. 在处理该请求的pod只读打开SQLite run_records.db（mode=ro），按17:14~17:18和场景/目标过滤，找回两笔记录；规范化原件run-records.json、终端原始回执pod-run-records.txt。
3. 同pod实际文件deployed-code.json：data_api/scenarios/renew_build.json第38~40、54行声明publish并映射--publish；skills/data-agent/workflows/scripts/renew_from_source.py第111行只注册--no-publish，第146~147行先parse_args再调用业务函数，第55~57行默认发布。
4. 外层openresty为何把结构化失败显示为HTML尚未定位到具体网关配置；应用已返回502而非外层超时/连不上已确认。HTML替换属于表现层推断，不影响参数契约漂移的直接根因。

## 可行续接与防重（本轮未执行）

- 复用计划588858850300473344，不再调用renew_clone_plan。
- 续接前只读确认计划仍是自己的TEST草稿且课程关联为空；若已有后续操作者补写，按实际新对象/关联续接，不重跑整build。
- 本次原build确认零业务步骤执行，因此可从build第一步开始，不需要清理后重建。使用同source/target/科目/数量/价格/no_protect，移除publish字段，不能再传publish=true；部署脚本默认发布，省略该字段可避开不兼容--publish。
- 这只是已核对部署脚本的静态可行参数，未在本轮重新提交或证明后续课程创建必然成功。正式续接时仍须核可售/课节/辅导班等业务前置、保留新对象输出并按原P0结构执行。
- 无需为解决此参数问题修改业务代码、部署或重建计划。造数工具API schema与脚本的一致性修复属于另项工具维护，本单没有动它。
- 当前只读scope来自本轮Boss安排；不能因诊断已清楚就自行翻回造数执行。

## “所有者要求停止”的来源纠正

已确认真实owner最新业务授权：消息om_x100b61f0ce5154acc1baf9298cf7105，正文“允许在 TEST 准备最小等效样本，并执行对应步骤补齐 P0 证据”；managed human_input事件18363接收时间2026-11-05 17:10:35.930692。该时间是本机接收记录，不冒充飞书发送时间。

与之不同，上下文消息原话是“上下文已达 80%。请完成当前安全步骤后收束本轮，提供已做事项、实际证据、剩余待办和未结束操作，供新 worker 交接；无需询问所有者。”本机运行时managed_context.py第231~245行、具体第243行，在context_due时自动handle.steer该原句；这是运行时安全交接，不是新的业务暂停决定。

运行时注入的精确时刻没有独立事件回执，不编造；能定位的转述时间为17:18:50.726224，事件18393，父Worker向W1-e4187e发送“所有者要求80%上下文安全收束。立即停止新增业务调用、造数和验证”。“所有者”归因是父Worker扩大解释，子任务又沿用了该归因。上下文交接本身应执行，但不能据此撤销TEST授权或要求owner重新授权。

当前任务记录只有两条human_input（MR比较、TEST授权），未发现更新的owner业务暂停。17:22:44.320018事件18403是Boss明确下发本轮只读诊断限制，当前遵守此限制。证据pause-source-audit.json、pause-source-events.json。原handoff中把安全交接当持续业务暂停的表述以本节纠正。

## 企微侧最小帮助边界

详见qiwei-minimum-help.md。两候选关系/标签查询与历史失败只能说明这些候选尚不满足成功前置，不能证明系统无可用对象。

- 业务标签：TEST候选身份cosplay、角色/页面核实、第三名同班未选对照与原标签快照尚未完成，不是已经证实必须owner提供的条件；有既定TEST授权后应先由执行者自主准备/查证。任务终态查询入口也应由执行者查源码/API，不应交给owner调查。
- 企微备注/官方临时标签：必须有受控企微测试老师的官方身份与同一账号下真实官方好友，不能靠DB friend=1或伪造external_userid代替。如可用测试账号/好友不能从现成登录态和数据取得，真正所需帮助仅是指定一组受控官方TEST老师—测试好友关系（或由其持有人建立真实好友），允许读取并恢复原备注；不需要生产账号或联系真实业务用户。
- 尚未证明cosplay或全系统样本搜寻已穷尽，所以本轮没有把“需人工登录/账号权限”判为最终不可自行解决的阻塞。外部帮助是受控官方关系无法自主取得时的条件性最小输入。

本轮结束：父Worker无在途调用；子任务只读报告已完成，result-7终态completed且无错误，回执见qiwei-diagnostic-receipt.json。P0版本仍沿用revision159；无新业务验证通过数。
