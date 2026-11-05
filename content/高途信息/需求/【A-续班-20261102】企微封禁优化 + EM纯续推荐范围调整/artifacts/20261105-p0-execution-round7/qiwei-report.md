# 企微 TEST round7 实测与恢复

本轮已完成可独立执行的标签接口/DB、官方备注任务和规范链接页面子集；未把这些子集称为P0-10/11整卡通过。真实阻塞为续班服务ES父熔断；没有已确认必须owner提供账号/官方好友的阻塞。没有发送消息、改业务代码、部署、生产写入、外部P0或skill修改。主Worker统一维护外部文档。自动上下文交接不是owner业务暂停。

结构化结果：`qiwei-results.json`；历史进展采样：`qiwei-progress-history.md`；原件均在本目录，以各原件time为准。

## 环境与身份

- 当前实际调用后端10.255.176.174:28688、Pod student-center-5d84df769-gxbql、镜像release-5dce9cdb-20261103201632；另一个默认TEST实例为feature-regular-course-query-df66fed8-20261102114739。`qiwei-current-pods.json`、页面trace/SLS。没有冒称目标feature/MR已部署。浏览器头test-gtbg-dev-3实际回落默认TEST。
- 本地student-center HEAD `396d84f076d066c652a49ce39e68b9b917c242e0`，只读源码，git status干净；源码不能冒充上述部署版本。
- 浏览器真实账号始终177071/gongxuemeng/弓雪萌，当前角色课程顾问，班级带班权限由真实请求leadTeacher177071证明。独立正规TEST准备会话实际109942/zhangzeling/张泽灵，原申请名zhangzeling109942不是employee.email_prefix，代课申请helper不写TEST浏览器会话；不能把Gong的结果算在申请身份上。独立身份trace `c2e31b56-8d40-4455-b298-be289b0ff0c0.0.3`。
- 本轮没有新cosplay申请、没有切换全局浏览器身份。结束身份读回177071，trace `ad241b1e-7136-42a4-b5db-bda35125981a.0.3`，`qiwei-final-session-state.json`；独立私有临时凭据文件已删除，凭据不入证据包。原round6两个项目已退出的事实仍仅作为历史。

## 真实对象及标识

TEST cluster153/course_center.clazz精确查询与真实ClazzAclService#getAllClazzInfo逐项比对：

|用途/学员ID|班名|DB id|实际API clazzNumber/number|API bizNumber＝DB biz_number|
|---|---|---|---|---|
|新建标签目标甲7704846434/乙7704846439、未选7704846440|续班归因-正经前置班-0820|208807|574882679202260992|32YYTS25D6LS11002|
|官方备注好友654489|madman-续班-正价-11|124836|496625388833767424|21YW25CY2A11001|
|官方备注好友654500|续班计划-大班课-02【改1111】|124525|495672366492309504|19YW22C8DF11001|

证据：`qiwei-clazz-id-mapping-dms.json`、`qiwei-class-api-current.json`（trace `student-center.899883.17938744996356322`）、`qiwei-class-identifier-mapping.json`。三个API响应id都为0，不能当DB主键。标签实际写契约ClazzStudentVO为clazzNumber/userId，备注契约为userIds/wkRemarkTemplate，班详情输出number/name/bizNumber，均无精确名bizId字段。**未证明某个API bizId等于id/number/biz_number，不编造等同关系**；父Worker正文应保留实际字段名，若另有bizId接口须按该接口续核。

- 三名新建学员真实姓名：甲“企微目标甲”、乙“企微目标乙”、对照“企微未选对照”；均正规student_create的12前缀测试号，源用户表独立读回。真实订单分别433654889322644001、433655061119763372、433655095481074192，正常下单/mock支付100分后order_info status2、paid_time有值。`qiwei-db-created-users-final.json`、`qiwei-db-three-paid.json`。
- 三人最终服务辅导班35930167940088064、status1；乙初分Tang组后正规转班至Gong组，旧组status2、新组status1。`qiwei-db-target2-transferred.json`。商业订单sub_clazz_number另为35930169788203264，原件如实保留，不强改为服务组。课程500775364606343168、班级未修改。
- 官方好友654489/654500源姓名均空（不是微信昵称），均12前缀测试号，实时WK friend=true、ableToSendNow=true，唯一目标Gong官方绑定1688855652617956，机器人10085011/BeShan/corp1970325001068435在线；真实external_userid经映射API取得，未伪造。654489当前班辅导班31039307458937472/status1；654500当前30979523514204416/status1，另历史30994965567898240/status2。`qiwei-db-official-class-relations.json`。
- 654499只读作未选好友对照，额外绑定其他归属官方身份，不写；654502与654500共享微信身份，不把两学员ID冒充两个独立官方好友。20004同样有额外非目标归属绑定，未提交任务。备注接口不按班隔离，这两名真实好友分属两个班，不能据此称“同班大/小班页面批量通过”。

## 步骤、结果与证据

|步骤与预期|实际结果|trace/原件|
|---|---|---|
|两目标批量加标签2需中关注，未选不变|HTTP code0；新源120556/120557及旧源26592/26593均tags2；对照无行|2490b2bb-d793-4568-b2fc-4900f59a7e4f.0.3；qiwei-tag-bulk-save.json、qiwei-db-tag-bulk-after.json|
|只改甲为3需弱关注，乙保留2|新旧表甲3、乙2、对照无行；甲源集合不残留2|7df78fce-b798-49da-ad2a-98813493e9b8.0.3；qiwei-tag-single-save.json、qiwei-db-tag-single-after.json|
|按标签筛人、ID/名称集合一致|未证明；续班页30172，ES父熔断；default/page吞异常返0不能作筛选通过|ab2ed085-38a9-4d94-ae7c-d8119fd1fc54.0.0；qiwei-page-error-log-sls-full.txt、qiwei-tag-filter2-bulk-after.json|
|清空两人并恢复空集合，未选保持|新旧表tags空串，对照无行；新空行保留，不称物理恢复写前无行；ES ID/名称都空及不再命中仍未证|f868a36f-547b-43fa-8bf7-25fae48adcf4.0.3；qiwei-db-tag-clear-restored.json|
|默认页面选甲标签后取消不保存|实际选择需中关注后取消，独立新旧源值与update_time均不变|qiwei-label-cancel-selected.txt、qiwei-label-cancelled.txt、qiwei-db-tag-cancel-after.json|
|单人真实官方备注任务、实际落值、恢复|任务294433185677210624及子任务294433185684550656均2成功；实时临时备注正确；恢复原值独立回读一致|9d3dbd16-ebde-401b-a48d-e824b13f42c2.0.3；qiwei-db-remark-track1.json、qiwei-official-after-test.json、qiwei-official-restored.json|
|正确双人模板W1-${{wkRemark}}逐人填充、未选不变|任务294434116095472640及两job均2；654489=W1-zhangkaiis，654500=W1-1105修改企微备注，654499各关系原值不变|1fd51b3d-09af-4dd6-9d46-8b70832c7ece.0.3；qiwei-db-remark-corrected-track1.json、qiwei-official-corrected-after.json|
|备注不改标签/续班相关源字段|双目标user_clazz_mark_info tags/color/layer逐字段一致，旧learning_student_info_ext两人前后均无行；不泛称所有续班字段/ES/页面均不变|qiwei-db-remark-batch-baseline.json、qiwei-db-remark-crossfield-after.json、qiwei-remark-crossfield-compare.json|
|无好友不进入提交|新建甲默认页真实检查resultStatus=false；未创建其备注任务；toast未截获，不编提示文案|3d67a99f-4967-4d36-b2cf-b94bf8e446f4.0.0；qiwei-nonfriend-request.network-request、qiwei-nonfriend-response.network-response|
|默认/联系学员两个入口、私聊/群聊均显示规范链接|四组合实际弹窗均有二讲wiki Af3VwjizwiKxDhkUFtEcvpZpn4P、顾问docx Ar7YdcPqsowMITxRBNacwjkpn3d；两文档均实际加载|qiwei-default-private-loaded.txt、qiwei-default-group-loaded-final.txt、qiwei-official-chat-dialog.txt、qiwei-official-group-dialog.txt、qiwei-guideline-loaded.txt、qiwei-advisor-doc-loaded.txt|
|点规范返回可继续编辑且不发送|默认群聊未选群0个；本地草稿返回仍在，继续输入成功；取消并确认丢弃。捕获page34 xhr/fetch窗口无发送提交，仅绑定/群确认、敏感词检查、埋点、轮询等|qiwei-guideline-draft-return.txt、qiwei-guideline-draft-after-edit.txt、qiwei-after-draft-discard.txt、qiwei-guideline-network-delta.json；只说明该捕获窗口，不冒称全传输审计|

## 失败保留与清理

本Agent一次把展示文案“企微备注”误作模板键，提交W1-${{企微备注}}；真实任务294433631114392576/父id1964、子10300/10301反复NPE而一直0。TLS app日志定位多泳道ExportExecuteHandler；SLS app仅完成扫描日志、SLS error0命中，`qiwei-batch-task-log-tls.txt`/对应SLS原件。枚举text=wkRemark、desc=企微备注，填充使用getText，**这是Agent参数错误，不归为需求缺陷**。

已保留原请求/状态/日志后，在授权TEST必要清理内，只软删本轮错误父任务及两子任务，状态0保持，未改成成功；`qiwei-invalid-task-cancel.json`含事务、行锁、断言和实际SQL，独立回读`qiwei-db-invalid-task-cancel-readback.json`。调度查询排除is_del，错误任务不再可执行。正确契约的新任务另行提交并验证，未覆盖失败原件。未用桥写入、未修改代码或预期凑通过。

ES父熔断在标签写前18:02:47已存在：ads_large_subclazz_user_index，实时5.8GB超过5.7GB限制，trace/SLS精确Pod与镜像；TLS同页面trace无命中。没有把ES异常说成标签缺陷，也未重复同法查询已知受阻页面。xjob管理只读查询登录失效，不是业务身份或官方好友缺失；未触发扫描他人任务的全局Handler、未改调度配置。

## 覆盖映射

|原编号→卡|本轮结论|
|---|---|
|QW-G001→P0-10|完整链路没做；筛选受ES阻塞。实际群发不属本次规范替换必验，未发送|
|QW-B01-001→P0-10|已验证大班接口/DB双目标+未选对照及恢复；大班续班页批量保存未验证|
|QW-B01-002→P0-10|小班实际页面/3人组未做，不借大班接口代替|
|QW-B02-001→P0-10|单人源集合切换已验证；筛选、ES名称/ID、标签+老师联合约束未验证|
|QW-B02-002→P0-10|小班编辑/筛选未做，共用代码仅推断|
|QW-B03-001→P0-11|单人、双人原备注占位符服务任务、实时落值、未选对照、恢复已验证；同班大班页面/默认姓名手机号身份模板一致性未验证|
|QW-B03-002→P0-11|小班页面未做；共用服务不能替代小班UI通过|
|QW-B04-001/回溯→历史回溯|未做；仍按min(begin_time)，不采用测试侧创建时间口径|
|QW-B05-001→P0-12|当前TEST默认私聊/群聊新链接显示已验证，两个规范实际加载|
|QW-B05-002→P0-12|当前TEST联系学员官方私聊/群聊链接显示已验证，未发送|

新增映射QW-B02-004仅源集合无残留子集；B02-006联合筛选未验证；B03-007仅上述源字段子集；B05-005返回编辑/无发送窗口已验证。测试平台30/120条均0执行/0通过，不复用平台结果、不修改测试侧用例。原30条非上述企微范围不评估、12卡非P0-10/11/12九卡未触碰。信息完整性与业务通过分别判断，不汇成整卡通过数。

## 最终恢复、保留与剩余

- 标签：两目标业务值已空，未选无行；新旧空标签行保留，颜色/分层未改。原历史错误班号行120554未动，旧正例120542未动。
- 官方备注：654489恢复zhangkaiis，654500恢复1105修改企微备注。恢复HTTP分别trace32a6ff01-b7ee-4776-be39-19784dbee5da.0.3、4e6f5561-7705-4057-8ff6-7ab6ec1876ad.0.3；**即时读仍旧临时值，未冒称成功**。18:32:33延迟独立读回两人原值且未选保持，trace `student-center.610.17938747537998677`，`qiwei-official-batch-restored-later.json`。无待恢复备注。
- 正常两笔任务均终结；错误笔已软删，最终状态另见`qiwei-db-task-final.json`。无在途业务请求或待重试有效任务。业务任务是同步HTTP创建后服务自身异步处理，无data-agent runID；没有未结束shell/会话操作。标签/备注清理责任为W1-e4187e。
- 新建三人、三张已付测试单、服务关系、空标签行保留fixture，7项登记unknown，`qiwei-fixture-registry.json`。不擅自退款/删用户、动共享班或主Worker EM计划/A-B/新学员7707220467。保留fixture不等于班整体sellable。
- 两规范新标签页48/49已关闭，本地草稿丢弃、选中清空；主页面留在默认花名册、搜索仍为自建甲7704846434，便于续接，没有为了恢复视图再次触发已知受阻续班查询。
- 剩余：需可用的目标TEST索引/实际版本后补大班页面筛选、ES ID/名称与清空不命中、联合老师约束；小班受控3人和UI尚未准备执行；备注同班大小班页面、默认姓名/手机号/身份模板未验证；历史min(begin_time)回溯未做。未查完的项不能称已确认权限阻塞。父Worker决定后续环境安排与正文实际标识命名，当前没有新增owner审批需求。
