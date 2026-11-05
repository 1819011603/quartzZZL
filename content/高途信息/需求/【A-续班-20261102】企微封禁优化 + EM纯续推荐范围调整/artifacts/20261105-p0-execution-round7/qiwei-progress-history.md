# round7 企微执行增量（持续更新）

当前仅TEST受控样本与业务执行；不改代码、部署、生产、外部P0/skill或对外联系。未撤销TEST授权。原错误班号行120554未动，主Worker EM计划及A/B关系未动。

## 已成立增量

- 独立TEST登录实际身份109942/zhangzeling/张泽灵/课程顾问已核，trace `c2e31b56-8d40-4455-b298-be289b0ff0c0.0.3`，`qiwei-actual-session-identity.json`。原申请名zhangzeling109942与gaotu.employee真实email_prefix zhangzeling不同；helper只提交申请、没有把新会话写入TEST浏览器，原浏览器仍177071/gongxuemeng，二者分开。没有把申请成功冒充身份生效。当前没有新cosplay申请，全局浏览器仍Gong，独立登录会话凭据仅私有临时文件保管、不入证据包。
- 实际浏览器Gong有大班续班服务权限；原网络请求按leadTeacher177071过滤，16人，真实班574882679202260992/续班归因-正经前置班-0820、辅导班35930167940088064。`qiwei-renewal-request.network-request`及脱敏response；网关trace `8a6b821d-89c3-4276-beca-9e1128f317ae.0.0`，请求流量test-gtbg-dev-3，尚未由trace映射实际Pod，不冒充目标分支。
- 已正规创建受控12开头测试号学员并独立DB回读：7704846434企微目标甲、7704846439企微目标乙、7704846440企微未选对照。`qiwei-create-target1/target2/control.json`，`qiwei-db-created-users-final.json`。既有Gong页面16人未取得受控依据，不写这些旧用户。
- 目标甲正规下单pay433654889322643489，真订单433654889322644001；mock支付回执OK，独立order_info回读status2、100分、paid_time2026-11-05 17:57:55；subclazz_student进入目标Gong辅导班35930167940088064/status1。`qiwei-db-order1-paid.json`。order_info.sub_clazz_number为35930169788203264，与服务辅导班关系值不同，保留原件，未强行改库统一。其余样本准备继续中。
- 官方源关系按account109942/177071、wechat_type2在27分表定向查询：Gong有20004真实候选，user20004在super_class.user为12开头测试号/name修改用户名。实时FriendRelationService#getRelation进一步确认WK friend=true，ableToSendNow=true，其中1688855652617956在线且原备注空，另两条离线分别原备注转辅导班-2和空。`qiwei-account-relations.json`、`qiwei-db-official-candidates.json`、`qiwei-official-friend-controlled.json`。这已超出旧“两候选27分表无行”范围，但不能直接当官方备注写后终态。正在核精确恢复入口，尚未提交备注任务。
- P0-12联系学员reach-widget实际页面：官方私聊及群聊两模式均出现二讲规范Af3VwjizwiKxDhkUFtEcvpZpn4P、顾问规范Ar7YdcPqsowMITxRBNacwjkpn3d；二讲链接已实际打开新tab48，标题“二讲侧-群发工具使用规范”，`qiwei-guideline-loaded.txt`。`qiwei-official-chat-dialog.txt`/`qiwei-official-group-dialog.txt`/截图。只打开/取消，没有选择发送账号、填内容或发送；弹窗取消后已清空临时选中。默认花名册企微群发两入口仍在补验。

## 结论口径

以末尾最新执行记录为准；前段是当时采样历史，不能按“尚未执行”覆盖后续已成功记录。P0-10已验证真实HTTP批量/单人/清空及源新旧表对照，页面/ES和小班未完整验证；P0-11单人固定模板官方任务及恢复已成功，批量/默认模板/大小班页面仍待覆盖；P0-12按实际打开的入口和链接单列。整卡与原7条QW不按接口子集一律判通过。

## 18:13 可立即整合的实测及恢复状态

- 三人正规下单/mock支付已全独立读回status2（每单100分）：甲真订单433654889322644001、乙433655061119763372、对照433655095481074192；`qiwei-db-three-paid.json`。甲/对照已自动进入Gong组；乙初分Tang组，正规转辅导班接口code0后，独立关系回读旧组status2/新组35930167940088064 status1，`qiwei-transfer-target2.json`、`qiwei-db-target2-transferred.json`。未修改班级、课程、主Worker A/B或新计划。
- P0-10批量业务标签：真实HTTP `/batchOperate/tag/save`，scene continuationService/type1，字符串长班号574882679202260992、甲7704846434+乙7704846439，studentTags=[2]。code0，trace `2490b2bb-d793-4568-b2fc-4900f59a7e4f.0.3`；新表ees_data.user_clazz_mark_info生成120556/120557，account177071、tags2；旧表gaotu.learning_student_info_ext生成26592/26593，tags2。同班未选对照7704846440仍无行。`qiwei-tag-bulk-save.json`、`qiwei-db-tag-bulk-after.json`。标签选项接口当前确认2=需中关注、3=需弱关注，trace `3fda301c-3992-4894-b35a-ad3fabdef0f3.0.3`。
- 单人改甲为[3]：code0，trace `7df78fce-b798-49da-ad2a-98813493e9b8.0.3`；源表甲tags3、乙仍2、对照仍无行，旧表对应一致，`qiwei-tag-single-save.json`、`qiwei-db-tag-single-after.json`。
- 清空兼恢复：两目标studentTags=[]，code0，trace `f868a36f-547b-43fa-8bf7-25fae48adcf4.0.3`；独立源表/旧表均tags空串，对照无行。`qiwei-tag-clear-restore.json`、`qiwei-db-tag-clear-restored.json`。新测试fixture保留，源/旧标签空行仍保留（写前无行，不能宣称已物理恢复absence），业务标签已清空，无待恢复非空标签；颜色/分层未改。ID集合与名称集合的ES/页面清空尚未证实。
- 页面真实阻塞不是未尝试：大班续班服务 `/roster/renewal/page` 在18:02:47（标签写前）返回30172“ES查询异常”。trace `ab2ed085-38a9-4d94-ae7c-d8119fd1fc54.0.0`，trace_tree及SLS精确定位10.255.176.174、镜像5dce9cdb；ES父熔断器Data too large，5.8GB > 5.7GB。`qiwei-renewal-error-response.network-response`、`qiwei-page-error-trace.json`、`qiwei-page-error-log-sls-full.txt`；TLS同trace0命中。源索引ads_large_subclazz_user_index；没有把ES异常当标签功能缺陷，不改代码/配置/部署。18:06:32 Pod复核仍原两个默认TEST镜像，`qiwei-current-pods.json`。
- 另一真实等效default/page筛选接口返回code0/0人，trace `73dc655a-18c9-41ab-8248-3b0c744884a3.0.3`，不能据此判过滤通过：此旧接口代码会吞查询异常返回空页。固定ACL读取也出现“未找到方法”包装错误，源码桥会把被调方法异常降成该错误，不据此断言未部署；未重试相同失败链路。尚无直接ES文档ID/名称集合或页面写后通过。
- P0-12默认花名册“企微群发→私聊群发”已实际进入iris弹窗，同样显示两个规范链接；`qiwei-default-private-loaded.txt`。默认群聊入口当时处于loading，尚未进入，不把该部分列通过。reach-widget官方私聊/群聊及规范实际打开已成立，既无发送内容也无实际消息。
- P0-11新增真实可执行候选：654500在TEST super_class.user为12开头测试号，姓名原值空；DWS在Gong177071下仅一条WK关系，原备注“1105修改企微备注”；实时linkup关系WK friend=true、ableToSendNow=true、唯一绑定1688855652617956在线，Robot逻辑10085011/BelongWorker gongxuemeng/官方acctId BeShan/真实corp1970325001068435。实际映射API返回真实external_userid，未伪造任何好友。`qiwei-db-more-official-candidates.json`、`qiwei-friend-only-relations.json`、`qiwei-official-candidate2-current.json`、`qiwei-official-external-mapping.json`、`qiwei-official-robot-info.json`。20004因同用户额外绑定其他belongWorker的官方身份，不提交其全量备注任务。654500任务及恢复尚未执行，当前无官方备注变更。
- 当前全局浏览器仍177071/Gong，未新申请cosplay；独立109942会话只用于正规TEST准备，没有将两身份混用。所有新增本轮用户、订单、转辅导班和空标签行将登记保留fixture。禁止把以上接口子集提升为7条QW或P0-10/11整卡通过。

## 备注任务已提交（待终态，不计通过）

受控候选654500当前好友检查code0/resultStatus=true，trace7c3037b3-04e4-44a2-8199-f54aeec57239.0.3。已提交唯一一次真实备注任务，固定临时模板W1-243aa61a-企微备注验证，接口code0/resultStatus=true，trace9d3dbd16-ebde-401b-a48d-e824b13f42c2.0.3，原备注1105修改企微备注。此为任务接收，不是终态或官方落值。恢复路径已由TEST路由解析核定/bgwApi/linkup/wk/relation/editWkRemark（原件qiwei-remark-restore-route.json）；待任务读回后立即精确恢复。

## 18:17 备注真实成功并已恢复（可立即整合）

- 真实受控官方好友654500，仅Gong177071一个WK关系/在线官方身份；任务294433185677210624（batch id1963）、子任务294433185684550656（id10299）在18:15:21/18:15:30分别task_status2/process_status2，源码枚举均“成功”，非仅HTTP接收。`qiwei-db-remark-track1.json`保留原始params、SQL与时点。
- 18:16:30真实FriendRelationService#getRelation独立回读同teacherWechat1688855652617956，remark变成W1-243aa61a-企微备注验证，trace `student-center.590576.17938737904642519`，`qiwei-official-after-test.json`。真实官方映射/官方服务路径已核；未伪造friend、external_userid或DB写行。未向用户发送消息。
- 随即通过真实TEST linkup恢复接口写回原值1105修改企微备注；code0/data=true，trace `834a93d3-24b3-4146-aad8-1bdc93becc86.0.3`，`qiwei-remark-restore.json`。18:16:43独立实时关系回读原值一致，trace `student-center.601.17938738038158526`，`qiwei-official-restored.json`。恢复结果来自另一次读取，不把接口ACK当恢复成立。
- 这是固定静态模板、单人、受控官方身份的任务/关系终态子集。学员654500姓名原值空（DB真实值），不能借这次执行冒充默认姓名/手机号/身份占位符模板、批量多好友、页面提交、大小班全入口或P0-11整卡。未操纵原姓名或手机号凑预期。没有待恢复官方备注或待运行任务。

## 页面与取消新增

- 默认花名册用本人新建甲7704846434（当前页面精确ID搜索1行、选择1人）打开添加标签，选择业务标签需中关注后点击取消，未点确认。`qiwei-label-cancel-open.txt`、`qiwei-label-cancel-selected.txt`、`qiwei-label-cancelled.txt`。独立源表和旧表复查甲乙tags仍空、update_time仍18:10:09/10、对照仍无行，`qiwei-db-tag-cancel-after.json`，符合取消不保存预期。仅该默认页取消子集，不称大小班续班服务全取消覆盖。
- 默认花名册群聊群发真实弹窗已打开，两规范URL与私聊一致，`qiwei-default-group-loaded-final.txt`。已点击取消，无发送。期间菜单会保留loading文字；按该真实可点按钮进入了后续弹窗，未修改页面代码或绕过禁用校验。四个组合（默认私聊/群聊、联系学员官方私聊/群聊）的链接显示均有页面原件。

## 18:22 批量备注在途
已新增第二个真实受控12开头测试好友654489，唯一Gong在线官方关系、原备注zhangkaiis；654499因额外外部身份绑定仅只读对照、不写。双目标654489/654500新任务模板W1-${{企微备注}}，验证批量及原备注占位符；原值已新鲜读回，恢复入口和逐人真实externalID已备。qiwei-remark-batch-create.json为接收证据，待DB终态与实时关系，不计通过。

## 规范链接返回编辑

默认群聊弹窗未选择任何群（0个），仅本地草稿W1-243aa61a-仅本地未发送草稿。点击顾问规范实际新tab49加载“顾问侧-系统工具使用规范”（`qiwei-advisor-doc-loaded.txt`），返回34草稿原值仍在（`qiwei-guideline-draft-return.txt`），继续输入成功（`qiwei-guideline-draft-after-edit.txt`，此组件fill实际追加，原件记录完整值）。之后取消并确认丢弃未保存草稿，`qiwei-after-draft-discard.txt`已回主列表。页面34 xhr/fetch窗口内仅绑定/群确认、敏感词检查、埋点及后台轮询，无提交发送接口；`qiwei-guideline-network-delta.json`明列范围，不能当所有传输的全局审计。这是QW-B05-005已有范围内的“返回可继续编辑、未点击发送”增量；未发任何消息。

## 已查范围与真实剩余

官方关系已定向检查109942/177071的27个DWS分表，并对现成12开头测试候选20004/654499/654500/654489做实时关系读取；654502与654500共享同一userWechat，不能当两名独立官方好友。已自主取得两名可控、仅Gong单一在线官方绑定的独立好友，无“必须owner提供身份/好友”的已确认阻塞。20004/654499涉及额外非目标归属官方身份，未提交其任务，不扩大官方账号写范围。

新建三名同班标签样本、独立正规TEST会话、两名官方好友均已自主取得，不能继续沿用旧报告“全部对象/身份缺失”。真实阻塞是续班服务ES父熔断及目标版本映射未证，不是授权缺失。未准备新的小班写场景，不将尚未执行称权限失败；当前共享索引异常下不重复同法页面调用。历史回溯仍min(begin_time)，未新增回溯任务/造数或采纳创建时间口径。测试侧30/120条仅作覆盖映射，平台0执行/0通过不被本报告改写。

受控三人、三单、关系及空标签行已登记全局fixture（7项，均unknown，未冒称班级整体sellable），`qiwei-fixture-registry.json`。既有共享课程/班未登记独占，不擅自退款/删用户/改旧班。恢复边界为业务标签空集合与原备注；新造fixture保留，不说所有DB行物理复原。

默认页用新建甲7704846434点“修改企微备注”，真实好友检查返回code0/resultStatus=false，trace `3d67a99f-4967-4d36-b2cf-b94bf8e446f4.0.0`，`qiwei-nonfriend-request.network-request`/`qiwei-nonfriend-response.network-response`。未创建其备注任务、未造官方好友；toast未被及时截获，不编提示文字。此为未加好友门槛，不证明账号封禁场景。

## 批量输入纠错（不是业务缺陷）

错误模板W1-${{企微备注}}任务294433631114392576在多泳道ExportExecuteHandler实际NPE、两子任务一直0，TLS原件qiwei-batch-task-log-tls.txt；SLS app仅CompleteHandler日志，error0命中。源枚举EditWkRemarkFillEnum定义text=wkRemark、desc=企微备注，填充map使用getText；错误是本Agent把展示名当变量键。不得把失败归因为需求或删除失败记录冒称成功。已按已授权TEST必要清理范围，只软删本轮错误父任务1964及两子任务10300/10301，状态0保持、完整原值和SQL另存qiwei-invalid-task-cancel.json及独立读回；不改业务代码、不把task_status改成功、不改其他任务。正确输入应W1-${{wkRemark}}，将独立记录新任务，不覆盖失败原件。

## 班级标识精确映射（owner新增要求）

|对象|班名|DB主键id|业务number/实际clazzNumber入参|API bizNumber＝DB biz_number|学员ID|
|---|---|---|---|---|---|
|新建3人均status1/isdel0，Gong组35930167940088064|续班归因-正经前置班-0820|208807|574882679202260992|32YYTS25D6LS11002|7704846434,7704846439,7704846440|
|既有班学员status1/isdel0，subclazz31039307458937472|madman-续班-正价-11|124836|496625388833767424|21YW25CY2A11001|654489|
|当前subclazz30979523514204416 status1/isdel0；另历史subclazz30994965567898240 status2|续班计划-大班课-02【改1111】|124525|495672366492309504|19YW22C8DF11001|654500|

原件`qiwei-clazz-id-mapping-dms.json`（TEST cluster153/course_center）、`qiwei-class-api-current.json`（trace student-center.899883.17938744996356322）、`qiwei-db-official-class-relations.json`。三个查询API响应id均0，不能当数据库主键。已验证clazzNumber/number与DB number、API bizNumber与DB biz_number三组逐值对应。当前所用标签写接口ClazzStudentVO只有clazzNumber/userId；备注任务只有userIds/wkRemarkTemplate；班详情输出number/name/bizNumber，均无精确名为bizId的字段，因此不编造“API bizId已确认”。若正文用bizId作为统一列名，应并列注明实际API字段名和映射，或由父Worker指定确有bizId字段的接口后再证，不把208807、574882679202260992、32YYTS25D6LS11002互换。官方两好友当前在上述各自真实班；备注接口不按班隔离，不能因提供班名就宣称同班批量。姓名DB均原值空，按空报告，不给微信昵称冒名。消息目标说明不授权发送消息。
