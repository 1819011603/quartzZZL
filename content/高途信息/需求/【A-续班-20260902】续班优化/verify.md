---
title: 【A-续班-20260902】续班优化 · 验证手册
tags: [需求, 验证]
---

# 验证手册

> 只保留当前可执行条件、仍有效数据和最新预期。

## 环境

| 项 | 当前值 |
|---|---|
| **泳道分配（2026-09-24 用户定）** | **`feature-xuban-match-opt` → `test-gtbg-dev-3`**（问卷匹配 / 调课同步：product-task、student-data、teacher-tool）；**`feature-xuban-expand-exclude` → `test-gtbg-dev-1`**（扩科推荐排除 + AI 配置化：product-b / product、student-data、cart、student-center）。两分支 student-data 不再共用泳道，**别往对方泳道部署**。逻辑环境均 `dev`，请求头 `traffic-env: <泳道>` |
| 泳道 | `test-gtbg-dev-3`（本节以下数据均指问卷匹配分支） |
| 已部署服务 | `product-task`(10.218.237.230，2026-09-24 仍为本分支) / `student-data` / `teacher-tool`；⚠️ `product-b` 2026-09-24 已被其他分支覆盖（见「真实链路 E2E」） |
| 分支 | 全部 `feature-xuban-match-opt`（product-server / student-data / teacher-tool） |
| DB | `gaotu_polar_test_03`（cluster 142） |

⚠️ **问卷匹配跑在 product-task**（CDS 消费者 `product-server-task/.../mq/questionnaire/QuestionnaireRecordConsumer`）；但**反射桥只挂在 product-b**（`/bgwApi/product-b/b`），`ComputeUserService#compute` 验证走 product-b。product-task 无 acl 桥（`/test/acl/compare/service` 404）。

## 当前测试数据（2026-09-22 造/复用）

| 对象 | 值 | 说明 |
|---|---|---|
| 续班计划 | `578532432171743232` | 问卷匹配用，绑前置课 `578530883890331648` |
| 前置课程 | `578530883890331648` | 四年级语文（任务系统-续班测试） |
| 问卷 | `578690742470393856` | |
| 绑定数据 | bindNumber `578693906093350912` → 班 `578530888321613824` / accountId `133082` | |
| 前置班 A | `578530888321613824` | 唯一班级（`gaotu.clazz`） |
| 学员 | `20001`（studentName `单词速记-6001`）/ `20002`（`测试0`）/ `20003` | 手机号脱敏 `126****000X`，故用**姓名**验证 |
| 明细（新造） | `gaotu.user_questionnaire_record` 插 1 行：user 20001 / clazz 578530888321613824 / questionnaire 578690742470393856 / type=3 / unique_biz_id=999900001 | 调课调班复制用 |

## 已验证（2026-09-22，反射桥 product-b）

`com.gaotu.product.service.renewal.questionnaire.ComputeUserService#compute`，`traffic-env: test-gtbg-dev-3`：

| 例 | 入参要点 | 期望 | 实测 |
|---|---|---|---|
| A | clazz=假班 999999999 + planCourseNumbers=[前置课] + 姓名 | 计划级命中 20001 | ✅ `[{"id":1,"user_id":20001}]` |
| B | 同上但不传 planCourseNumbers | 不命中 | ✅ `[]` |
| C | clazz=真班 + 姓名 | 班内命中 20001 | ✅ `[{"id":3,"user_id":20001}]` |
| D | 不存在的姓名 | 未归属 | ✅ `[]` |
| E | 假班 + originUserId（originUser 只查班内） | 不命中 | ✅ `[]` |
| F | 两条提交（`单词速记-6001` / `测试0`） | 各自命中 20001 / 20002 | ✅ `[{"id":6,"user_id":20001},{"id":7,"user_id":20002}]` |

**结论**：7 档规则（计划级规则靠 `planCourseNumbers` 生效）、去兜底、多命中各归其主均通过。

## 已验证（2026-09-22，teacher-tool 调课调班明细同步）

反射桥直调 `com.gaotu.teacher.tool.facade.mq.TransferCourseQuestionnaireConsumer#consume`（打到新 pod `teacher-tool-5bd98df5b-mxmk2`），body = 报文的 base64：

| 例 | 动作 | 期望 | 实测 |
|---|---|---|---|
| 1 | A(`578530888321613824`)→B(`578667321965428736`) | B 新增 1 条明细（同 `questionnaireGroupId=999900001`、新 `uniqueBizId`） | ✅ 明细 21856 |
| 2 | 重复投递同一 A→B | 幂等 skip，不新增 | ✅ 仍 2 行 |
| 3 | 调回 B→A | A 已有同问卷，skip | ✅ 仍 2 行 |
| 4 | 不存在的学员 A→B | 原班无明细，no-op | ✅ 仍 2 行 |

**结论**：原班续班明细复制到新班正确、幂等（不产生重复数据）、先调后填/全程未填 no-op 均通过。

**补充（2026-09-22）**：student-data 的 `QuestionnaireAclService#batchQuestionnaires([B],[20001])` 已能查到 B 明细（`uniqueBizId 72615972506173953`）——即宽表重建时 `renewalQuestionnaireStatus` 会推导成 COMMIT。**查法坑**：① 路由要用 pathInfo `/student-data/**` → `https://test-fuwu.baijia.com/bgwApi/student-data/test/acl/compare/service`（不是 `/bgwApi/student-data/...`）；② 报 `700 请重新登录`/`code:3` 时先**刷新 baijia-proxy Cookie**（`POST http://127.0.0.1:8765/api/v1/bridge/refresh`）即可。

### 调课调班 MQ 端到端 + 幂等（2026-09-23，✅ 已验证）

真发 MQ（不再只反射调 consumer）：student-data `FuwuOnsMqProducer#sendNormalMessage` 发 `gaotu_after_sale_event_test` + tag `TRANSFER_TOUCH_EVENT`，body = `{userId:20001, originalOrderInfo:{clazzNumber:A=578530888321613824}, targetOrderInfo:{clazzNumber:B=578667321965428736}}`。

| 例 | 动作 | 期望 | 实测 |
|---|---|---|---|
| 1 | 先删 B 已有明细(id 21856) → 发 A→B 报文 | teacher-tool 消费并复制 A 明细到 B | ✅ B 新增 id `21858`（`uniqueBizId 72615972506173954`、同 `questionnaireGroupId 999900001`）|
| 2 | 重投同一报文 | 幂等 skip | ✅ user 20001 明细总数仍 2 |

**坑**：`sendNormalMessage(topic, String body)` 会把 String body 再 JSON 序列化（发成 `"{...}"`），consumer fastjson 报 `syntax error, expect {, actual string, pos 0`；**要传对象**走 `sendNormalMessage(String, List, Object)` 重载。

### 花名册 ES 顺序风险（2026-09-23，机制已定·**存在真实顺序风险**）

- **字段位置**：`renewalQuestionnaireStatus` 在小班花名册宽表 `ads_small_clazz_user`（别名→`ads_small_clazz_user_index_v4`），**不在** `small_clazz_v3`。
- **写入方**：① 问卷回收事件消费者 `DwsRenewalQuestionnaireConsumer#innerUpdateQuestionnaireStatus` **直接写**（问卷提交时）；② `RenewalQuestionnaireStatusServiceV2#buildData` 提供同口径推导（读 `batchQuestionnaires` 明细），但**未确认哪条链路会调用它重算已有文档**。
- **调课 MQ 不写花名册**（只写 teacher-tool 明细）。
- **实测（班 `529911462177622016`）**：有明细的用户 `1438684` → status `3`(已提交)；无明细的 `1449343` → status `2`(未提交)。给 `1449343` 插一条明细后跑小班花名册回溯 `BackAdsSmallClazzUserHandler#execute([clazz])`（返回 SUCCESS、文档 `updateTime` 已变）→ **status 仍为 2**，未重算。
- **结论**：**先填后调时 B 的花名册「已提交」状态不会随调课自动更新**（真实顺序风险）；确认不存在会重算该字段的 sync 链路 → **2026-09-24 已修复，见下方「先填后调缺陷修复」**。原「宽表重建时会推导成 COMMIT」的说法**未证实，已订正**。
- 旧 A/B（「任务系统」测试班）花名册 ES 无文档，已改用下一节新造的干净大班完成端到端。

### 提交→匹配→花名册/明细 真实链路 E2E（2026-09-24，✅ 已验证）

**造数（data-agent `create_renewal_regression_clazz` + 本地引擎 `batch_create_order`/`mock_pay`，泳道 `test-gtbg-dev-3`）**：前置课 `578530883890331648` 下新建两个大班，花名册在 eesServe `ads_large_subclazz_user_index`（有真实文档）。

| 对象 | 值 |
|---|---|
| A 班 | `581200735616724992`（弓雪萌辅导班 `36325046492463488`）；学员 `20017`、`20018`（姓名 `123`） |
| B 班 | `581200735551846400`（弓雪萌 `36325046495478144` / 唐稳01 `36325046539911552`）；学员 `20019`（`123`）、`20020`（`1234`） |
| A 班问卷绑定 | `sendUrl` 生成 bindNumber `581201197220882432`（accountId 177071） |

**提交方式**：真发 CDS topic `test_future_landingpage_form_submit`（实例 `MQ_INST_1941505946323830_BcTleGRs` = uqun_test），由泳道 **product-task** 真实消费。发送走 student-data 桥 `AiCommOnsMqProducer#sendOrderedMessage(String, List, Object, Object)`（**传对象、数字字段转字符串**；String 重载会被桥选错成 Object 重载，发成二次序列化的字符串，consumer 解析失败）。报文模板取 `gaotu.questionnaire_record.origin_data`，需补 `formatDataList`。

| 例 | 场景 | 实测 |
|---|---|---|
| S1 | 在 A 班正常提交（20017，originUserId） | ✅ record `347` computed=20017 → A 花名册 status `3` → 明细 `21860`（A）（注：S1 走的是 product-b 桥 `dealCDSMsg`，匹配走同班 originUser，与新旧代码无关） |
| S3 **先调后填** | 20020 只在 B 班，用 **A 班链接**提交（姓名 `1234`、无 userId） | ✅ record `990021` **计划级姓名规则**命中 computed=20020、clazz=A → 共享课 fan-out **B 花名册 status `3`** + B 明细 `21861` |
| S2 **先填后调** | 20019 只在 B 班；补 A 班明细 `999900019` 代表调前已填 → 真发 `TRANSFER_TOUCH_EVENT` A→B | 明细 ✅ 复制到 B（`21863`、同 group `999900019`）；**花名册 ❌ B 的 20019 status 60s 后仍 `1`、updateTime 不变** → **顺序风险端到端复现** |

**结论**：先调后填正常（计划级规则 + 共享课 fan-out 覆盖）；**先填后调时 B 班花名册「已提交」不会更新**，属真实缺陷（明细已同步、花名册未同步），需决定是否让调课消费链路补写 `renewalQuestionnaireStatus`（大班 `ads_large_subclazz_user_index` / 小班 `ads_small_clazz_user`）。

### 先填后调缺陷修复 + 端到端验证（2026-09-24，✅ 已验证，v2 架构）

**v1（已废弃）**：student-data 新增独立 consumer，与 teacher-tool 复制明细的 consumer 各自订阅同一事件、互不通信，靠限次重试等对方复制完。commit `3039e7756`（含一次 code review 加固 `6a3d7ab74`：去掉靠 `questionnaireAclService.batchQuestionnaires` 判断"原班有没有问卷"来决定要不要重试的逻辑——底层 `SysInvokeUtil` 会把 RPC 异常吞掉按空结果处理，这个判断会把「下游抖动」和「学员确实没填」混为一谈，一旦命中就永久错过）。

**v2（当前，用户 code review 后要求收敛为单一入口）**：two-consumer 改成 orchestration —— student-data 消费者同步调 teacher-tool 新增的 Feign 接口复制明细，复制成功后立即重算状态、算出「已提交」就回写；teacher-tool 那个独立 consumer 已退役（连同它专用的 `TransferCourseMessageDTO` 一并删除）。不再需要"等/重试对方复制完"这套逻辑：复制这步只要没抛异常就代表数据已落地，下游任一步失败直接向上抛异常，交给 MQ 通用的 `ReconsumeLater`。

**改动（两个仓库）**：
- `teacher-tool-api`：新增 `TransferQuestionnaireSyncRequest` + `QuestionnaireClient#syncTransferQuestionnaire`，版本 `1.0.28-SNAPSHOT`（已发 Nexus snapshots）。
- `teacher-tool`（commit `b82665d9`）：复制逻辑原样从 `TransferCourseQuestionnaireConsumer` 搬到 `QuestionnaireServiceImpl#syncTransferQuestionnaire`（幂等，按 questionnaireId 去重），新增 Feign 端点 `POST /feign/questionnaire/user/transfer/sync`；退役旧 consumer；新增单测 4 条（JUnit5——仓库既有的 JUnit4 `@RunWith(MockitoJUnitRunner)` 风格实测在当前 surefire 配置下跑不到 0 个用例，无 junit-vintage-engine，与本次改动无关的既有环境问题，为了测试真的会跑改用 JUnit5）。
- `student-data`（commit `ecfcb6e4f`）：`QuestionnaireAclService` 新增 `syncTransferQuestionnaire`——**直接调 Feign、不经过 `SysInvokeUtil`**（那个工具会吞异常，这里恰恰需要异常真实传播），失败抛 `RpcException(RpcErrorCode.TEACHER_TOOL_INTERFACE_ERROR)`；`RenewalQuestionnaireTransferSyncService#syncAfterTransfer` 简化成直线：同步复制 → 查询/计算 → 命中已提交就写；`student-data-client` 的 `teacher-tool-api` 依赖同步升到 `1.0.28-SNAPSHOT`。单测 5 条（新增"复制失败直接抛异常、不应该继续算/写"）。

**部署**：均 `test-gtbg-dev-3`——teacher-tool pipeline `1284973` → 新 pod `teacher-tool-58cf8584d4-g4npc`（`10.218.238.42`）eureka UP；student-data pipeline `1284995` → 新 pod `student-data-86967d5587-w4ds6`（`10.218.238.245`）eureka UP。

**验证（新造学员 20022，走完整新链路，未复用 v1 的验证数据）**：A 班插入明细（`unique_biz_id=999900022`，`finish_time` 2026-09-24 14:19:43） → 真发 `TRANSFER_TOUCH_EVENT` A→B（14:22:04）：

| 层 | 证据 |
|---|---|
| 消费日志 | `RenewalQuestionnaireTransferConsumer#consume`（14:22:05.013）收到消息 → `RenewalQuestionnaireTransferSyncService#writeCommitStatus`（14:22:06.150，userId=20022, clazzNumber=B, submitTime=1790230800000） |
| teacher-tool 明细落库 | `user_questionnaire_record` 新增 id `21865`，`clazz_number`=B，`questionnaire_group_id=999900022`（与 A 班原明细对应）、`create_time`=**14:22:06**——比发消息晚 2 秒，证明是本次同步调用产生的，不是遗留数据 |
| ES 回读 | B 花名册（`36325046495478144-20022`）`renewalQuestionnaireStatus` **由 `1` 变为 `3`**，`updateTime` 刷新为 `1790230926215` |

**结论**：先填后调场景闭环，单一入口 + 同步复制 + 即时重算的新架构端到端验证通过。

### 第二轮 code review 修复 + 端到端验证（2026-09-24，✅ 已验证）

对 v2 改动做对抗复审，发现并修复两处：

1. **teacher-tool 重复复制**（真问题）：`syncTransferQuestionnaire` 判重用的新班明细快照只在循环开始前查一次；原班若存在两条同 `questionnaireId` 的记录（历史重复提交未清理），后一条看不到前一条刚插入新班的记录，会把两条都复制过去，产生重复行，违背方法自己声明的幂等语义。改成随循环增长的 Set 跟踪。commit `5d158d55f`，新增单测锁定该场景（5 条→本条）。
2. **student-data 日志格式**（style）：两行新日志用了 `ClassName#methodName` 而非仓库规定的 `ClassName | methodName | message` 管道格式，跟本次其它新文件写法也不一致。commit `f1c352a8e`。

**部署**：均 `test-gtbg-dev-3`——teacher-tool 新 pod `teacher-tool-844cbd8f46-sfqvh`（`10.218.248.99`）eureka UP；student-data 新 pod `student-data-5d96d7dc78-mk8nf`（`10.218.248.197`）eureka UP。

**验证（新造学员 20023，A 班插入两条相同 `questionnaireId` 的明细模拟历史重复提交）**：真发调班事件后回读：

| 层 | 证据 |
|---|---|
| teacher-tool 明细 | A 班 2 条（id `21866`/`21867`，同 `questionnaireId`）→ B 班**只复制了 1 条**（id `21868`，`create_time` 比发消息晚 1 秒，确认是本次同步产生，未产生重复行） |
| ES 回读 | B 花名册（`36325046495478144-20023`）`renewalQuestionnaireStatus=3`，`updateTime=1790232544588` |

**结论**：重复问卷记录场景下不再产生重复复制，修复生效。

### 第三轮：原班无问卷短路 + 兼容旧版 teacher-tool（2026-09-24，✅ 已验证）

**改动**：teacher-tool 同步接口改为 `RO<Boolean>`（data = 原班是否存在续班问卷明细；新班已有、无需复制时仍返回 true），`teacher-tool-api` 升 `1.0.29-SNAPSHOT`（已发 Nexus）；student-data 收到**明确 `false`** 才跳过查班级/计划/重算。**`data=null`（旧版 teacher-tool 的 `RO<Void>`）按「有问卷」处理**——否则发布顺序错开或 teacher-tool 回滚时，所有调课都会短路、先填后调缺陷复现（本轮复审发现并修正）。commit：teacher-tool `8f5b2787`、student-data `a20d71543`。单测：student-data 11 条（新增 `QuestionnaireAclServiceImplTest` 覆盖 true/false/null/失败/异常）、teacher-tool 5 条，全过。

**部署**：均 `test-gtbg-dev-3`——teacher-tool pipeline `1285156` → pod `teacher-tool-c9bfddbd5-r75nj`（`10.218.236.50`）eureka UP；student-data pipeline `1285157` → pod `student-data-76849cd8fb-x65g5`（`10.218.237.107`）eureka UP。**2026-09-24 晚复核**：发现这批 pod 的 createTime 早于代码最终定稿时间，判断是滚动发布窗口内验证的（代码内容一致，只是不放心就重新触发了一轮部署，pod 换成 teacher-tool `teacher-tool-54d97b9b84-k5pmj`（`10.218.249.32`）/ student-data `student-data-6665694bcd-j5cbq`（`10.218.248.242`），均 eureka UP），并在新 pod 上补做一轮独立验证（见下）。

| 例 | 操作 | 证据 |
|---|---|---|
| N1 短路 | 学员 `20018`（任何班都无明细）真发 A→B | pod 日志 15:23:46.869 `old clazz has no questionnaire, skip roster recompute`，之后无查班级/写花名册日志；`user_questionnaire_record` 20018 仍 0 条 |
| N2 回归 | 给 20018 插 B 班明细（id `21869`，group `999900018`）→ 真发 B→A | teacher-tool 复制出 id `21870`（clazz=A，create 15:24:40）；student-data 15:24:41 `writeCommitStatus`；ES A 花名册 `36325046492463488-20018` `renewalQuestionnaireStatus` **1→3**、`updateTime=1790234682719` |
| N3 短路（新 pod 复核） | 新学员 `20024`（无任何明细）真发 A→B | 15:28:03.742 `old clazz has no questionnaire, skip roster recompute`；ES `36325046495478144-20024` `renewalQuestionnaireStatus` 保持 `1`，`updateTime` 未变 |
| N4 正常链路（新 pod 复核） | 新学员 `20025`（A 班插明细 `999900025`）真发 A→B | 15:28:04.777 `writeCommitStatus`；ES `36325046539911552-20025` `renewalQuestionnaireStatus` **1→3**，`renewalQuestionnaireSubmitTime=1790236800000` |

**造数坑（测试工具本身，非产品代码问题）**：手动模拟调课事件走 `test-fuwu.baijia.com/bgwApi/student-data/test/acl/compare/service` 反射调 `FuwuOnsMqProducer#sendNormalMessage`。**List/Object 参数的重载（3 参、4 参 `(String, List, Object, long)`）桥都会匹配错成 `(String, String, String, long)`**：tag 变成字面量 `[TRANSFER_TOUCH_EVENT]`（consumer tag 过滤收不到，**轨迹为空、无任何消费日志**），body 变成 `Map.toString()`。**稳定写法 = 直接传字符串**：`["gaotu_after_sale_event_test", "TRANSFER_TOUCH_EVENT", "<JSON 字符串>", <nowMs>]`。发完用 `ConsoleMessageDetail` 看 `TAGS`/`bodyStr` 可立刻判断。另：该 pod 日志在轻舟 TLS/SLS 延迟较大，直接 pod-terminal `grep app/log/app.log` 更快。其余造数坑：
- mock_pay 的大班课订单做大班→大班真实调课，售后恒报「原订单资金所在账户和调转商品目标收款账户不一致」（结构性，见 data-agent `candidate_lessons`），故以「只下单进 B + 真发调课事件」等价替代。
- 同一课程下不能重复购买（`code=440 您已购买过相同课程`），同一学员无法同时在 A/B。
- ⚠️ **泳道 product-b 已被其他分支覆盖**（2026-09-24 10:02 新 pod `10.218.237.126`，**无 `NamePlanRuleService`**，计划级用例 A 复跑返回空）；product-task 仍是 `feature-xuban-match-opt`（pod `10.218.237.230`，已确认含该类）。**此后问卷匹配只能通过 product-task 真实消费来验，别再用 product-b 桥验 `ComputeUserService`**。product-task 内 arthas 调 `compute` 会因下游 Feign（Hystrix）失败，不可用。

### T-07 重试次数标记 E2E（2026-09-24，✅ 已验证）

product-task pod `product-task-gaotu100-com-5c49c6f665-fgmjd`（10.218.237.230，本分支）arthas 直调 `QuestionnaireRecordService#dealNotExistedComputeUser()`（test xjob 无该任务；product-b 泳道已被他人覆盖）。把 `questionnaire_record` id `345` 临时改成满足重试条件（`manual_user_id=1`、`create_time=NOW()-1h`、`retry_count=0`），连跑 4 次 → `retry_count` 0→1→2→3，第 4 次不再被选中（仍 3）；无重复行产生。**已回滚**为原值（`manual_user_id=0`、`create_time=2026-09-15 17:00:20`、`retry_count=0`）。

**重试条件修正（2026-09-24 用户定修，✅ E2E 已验证）**：`listUnmatchedForRetry` `manual_user_id != 0` → `= 0`（product-server `f549f4070`；原条件使普通未归属记录从不重试）。部署 dev-3：product-task `product-task-gaotu100-com-846667b6b7-4h7ck`、product-b `product-b-6995d9d67f-sgnhw`（10.218.249.160），均 eureka UP。经 **product-b acl 桥**（servlet 线程）调 `QuestionnaireRecordService#dealNotExistedComputeUser`（product-task 内 arthas 线程调下游 Feign 必 Hystrix 失败；test xjob 无 product 执行器）：

| 例 | 造数 | 实测 |
|---|---|---|
| R-a 可匹配 | record 350（990102，原归 20019）置 computed=0、create=now-1h | ✅ 重试后 computed=**20019**（自动归属，不再累加次数） |
| R-b 不可匹配 | record 352（990104） | ✅ retry_count 1→2→3，第 4 次不再选中 |
| R-c 已手动绑定 | record 345 置 manual_user_id=1 | ✅ 不被选中，retry_count 保持 0（已还原） |
| 10 分钟窗口 | record 356 创建不足 10 分钟 | ✅ 不被选中 |

- 附带观察（既有行为）：并发子任务异常被 catch 后仍会给整批累加 retry_count（`QuestionnaireRecordService:595`），下游抖动会消耗重试次数。

## 用例覆盖审计（2026-09-24，对照 PRD 原文 wiki `Ijz3w9ZgAi8ncakFs3jcKZI9nxi`）

**7 档顺序**：PRD = userId →（1）同班手机号 →（2）同计划手机号 →（3）同班姓名 →（4）同计划姓名 →（5）同班亲属号 →（6）同计划亲属号；代码默认 `compute.rule.name.list` 与之**逐项一致**（PROD 未配 Apollo，走默认）。

| PRD 规则 / 最终效果 | 现有用例 | 能否真正证明 | 状态 |
|---|---|---|---|
| 各档单独命中（计划级姓名 / 班内姓名 / 不命中） | A–F（反射 product-b） | 只证明**单条规则**能命中，**不证明优先级顺序** | 部分 |
| **优先级**：高档命中时不落到低档（如同班姓名 vs 同计划手机号冲突） | 无 | — | ❌ 缺 |
| **多命中取学员 ID 小的**（姓名/亲属档） | 无（F 是两次提交各唯一命中） | — | ❌ 缺；A 班 20017/20018 同名 `123` 可直接造 |
| 手机号档 / 亲属号档 | 无（测试手机号脱敏，只验了姓名） | — | ❌ 缺 |
| 问卷+计划完全匹配（跨计划同名不命中） | B（不传计划）近似 | 未造"另一计划同名学员" | 部分 |
| 先填后调：A B 明细+花名册都展示 | S2 / 20022 / 20023 / N2 | ✅ | ✅ |
| 调课到 B 未填：A B 都无数据 | N1 | ✅ | ✅ |
| **先调后填：A B 都展示**（PRD 最终效果第 4 条） | S3 只验了 B | **A 侧未验** | ❌ 缺 |
| **前提：AB 不是同一问卷不共享数据** | 无 | — | ❌ 缺，且**代码不满足**（见下） |
| 小班调课写 `ads_small_clazz_user` | 无（全在大班验） | — | ❌ 缺 |

### 7 档优先级 / 多命中 / 跨计划 真实链路 E2E（2026-09-24，✅ 已验证，dev-3 product-task 真实消费）

造数：学员手机号 = `126000000xx`（20017–20020，经 `UserSyncAclService#listUserBaseByMobiles` 反查确认）；`student_name`：**20018=`123`(A)、20019=`123`(B)、20020=`1234`(B)，20017 为空**（旧文档写 20017/20018 同名 `123` 不对）。新建 B 班问卷链接 `questionnaire_bind_data` number `581201197220882499`（复制 A 行，clazz=B）。发送脚本 `/tmp/cds_send.py`（模板取 `questionnaire_record` id 348，经 student-data 桥 `AiCommOnsMqProducer#sendOrderedMessage(String,String,String,String)` 四个字符串参数发 `test_future_landingpage_form_submit`）。

| 例 | 链接 | 姓名 / 手机号 | 期望 | 实测 computed_user_id | 证明 |
|---|---|---|---|---|---|
| P1 | A | `123` / 12600000017 | 20017 | ✅ 20017（record 990101） | (1) 同班手机号 优先于 (3) 同班姓名（后者会得 20018） |
| P2 | A | `123` / 12600000019 | 20019 | ✅ 20019（990102） | (2) 同计划手机号 优先于 (3) 同班姓名 |
| P3 | B | `123` / 不存在号 | 20019 | ✅ 20019（990103） | (3) 同班姓名 优先于 (4) 同计划姓名（计划内还有更小的 20018） |
| P4 | A | 不存在姓名 / 12200902759（计划外用户 6286426263） | 0 | ✅ 0（990104） | 跨计划手机号不命中 |
| P5 | C 班 `578530888321613824`（同计划，无人叫 `123`） | `123` / 不存在号 | 20018 | ✅ 20018（990105） | (4) 同计划姓名 **多命中（20018、20019）取学员 ID 小的** |

| R1 | B | 不存在姓名 / 12699990018（亲属号，同时挂 20018、20019） | 20019 | ✅ 20019（990106） | (5) 同班亲属号 优先于 (6) 同计划亲属号（后者会取更小的 20018） |
| R2 | C 班（两人都不在） | 同上 | 20018 | ✅ 20018（990107） | (6) 同计划亲属号 **多命中取学员 ID 小的** |

- 亲属号造数：账号互通 `SS-ID-SERVICE` `POST /id-service/mapping/mappingUserIdWithPhone` `{"userId":"20018","phone":"12699990018","searchPriority":false,"sourceDesc":"product"}`（`sourceDesc` 必填，否则 400），经 `invoke_feign` 调；读回 `IdQueryAclService#queryUserInfoByRelatedId`。该号不是任何学员的注册手机号（`listUserBaseByMobiles` 为空），保证 (1)(2) 不会先命中。**7 档全部验证完毕。**
- 代码核对：各档实现与 PRD 一致——同班姓名 `NameRuleService` 按 userId 排序取首个；亲属 `RelationIdService` `.min()`；计划档经候选集再按计划过滤。

**调课同步按 PRD「非同一问卷不共享」修正（2026-09-24 用户定，已提交·部署 dev-3 中）**：原实现 teacher-tool 把 A 班全部续班明细无条件复制到 B（花名册侧安全，但 B 明细页会出现不属于 B 问卷的记录）。现改为：
- student-data `RenewalQuestionnaireTransferSyncService`：先查 B 班所在已发布续班计划（`preCourseList` 含 B 课程，口径同 `RenewalQuestionnaireStatusServiceV2`）→ 问卷匹配拿 `bizId` → B 未绑定则直接返回（不复制不重算）；这两步用新增的**抛异常**方法 `RenewalMasterAclService#queryRenewalMasterInfoElseException(List)`、`QuestionnaireAclService#queryQuestionnaireMatchResultElseException`（原方法经 `SysInvokeUtil` 吞异常成 null，会把下游抖动误判为未绑定）。
- teacher-tool：`TransferQuestionnaireSyncRequest` 新增可选 `projectNumber`，非空时只复制 `projectNumber` 相同的明细；为空保持旧行为（兼容任意发布顺序）。api 仍 `1.0.29-SNAPSHOT`（已重发）。
- commit：student-data `660ad3247`、teacher-tool `1260d455`；单测 student-data 14 条 / teacher-tool 7 条全过。
- 代价：原「原班无问卷就跳过全部查询」的短路变为「先查 B 绑定再复制」，每个调课事件多 2 次 product-b 调用（调课事件低频，可接受）。
- **对抗复审后再修（`0ec17d469` / `c169f274`）**：① 复制成功后重算走 V2（内部 `SysInvokeUtil` 吞异常），算不出「已提交」只可能是下游失败 → 改为抛异常重试，不再 ack 丢消息；② 同课程多个已发布计划时与 V2 一致取**最后一个**（原 findFirst 会与 V2 选到不同问卷）；③ 空白 bizId 视为未绑定；④ teacher-tool `projectNumber` 改 `@NotBlank` 必填，去掉「为空就全量复制」后门（该接口未上过线，无旧调用方需兼容）。单测 student-data 18 条 / teacher-tool 7 条。
- **E2E（2026-09-24，dev-3 新 pod `student-data-59f5db8c58-7rszh` / `teacher-tool-558c47bc44-mnqqh`，✅ 已验证）**：
  | 例 | 造数 | 实测 |
  |---|---|---|
  | T2 非同一问卷不共享 | 20018 在 B 的明细 21869 `project_number` 改成 `99999999999999999`，发 B→A | ✅ 日志 `old clazz has no same questionnaire, skip`；A 未新增 999 明细 |
  | T1 同一问卷 → 重算 | 删 20019 B 班明细 21863、B 花名册置 1，发 A→B | ✅ `writeCommitStatus`；ES B 花名册 `renewalQuestionnaireStatus` 1→3、`submitTime=1790238068000`（B 已有 16:21 共享课 fan-out 的同问卷明细，故按 questionnaireId 跳过复制；真实复制路径见上「第三轮」N2） |
  | 未绑定返回形态 | arthas 直调 `queryQuestionnaireMatchResultElseException` | ✅ 未绑定班 → `null`（不抛异常），已绑定班 → bizId `17323095168254394`；复审担心的「未绑定也抛异常→进死信」不成立 |
- **造数坑（新）**：acl 桥调 `FuwuOnsMqProducer#sendNormalMessage` 四个字符串参数**也不稳定**（16:30 一次被选成 Object 重载，body 二次序列化，consumer 报 `expect {, actual string`，重试 5 次后进死信，属造数失败非产品问题）。**稳定做法：pod 内 arthas `instances[0].sendNormalMessage("topic","TAG","<json>")`**，脚本 `/tmp/send_t.sh <userId> <old> <new>`；ES 花名册重置脚本 `/tmp/es_set_status.py <docId> <status>`。
- **本轮测试数据改动（TEST，保留）**：新增 B 班问卷链接 `questionnaire_bind_data` number `581201197220882499`；明细 21869 `project_number`→`999…`（T2 用）；删除明细 21863、21870；`questionnaire_record` 新增 id 349–353（P1–P5）；ES 花名册 `36325046492463488-20018`=1、`36325046495478144-20019`=3。
- **已知限制（记录，不处理）**：先调课、B 的续班计划/问卷绑定后才配置 → 调课当时判未绑定直接跳过，之后无补偿；同一消息并发重投的"先查后插"去重非原子（依赖消费端串行，未见唯一索引）；复制出的明细与原班明细后续修改不双向同步。

### AI 配置化圈选侧 E2E（2026-09-24，✅ 已验证）

泳道临时切 `feature-xuban-expand-exclude`（pod `student-data-677fb55b75-wdqkv` 10.218.238.5，只剩此 pod 后走网关桥），直调 `RenewalAiCommRealTimeSelectHandleService#buildBizSelectCondition(userId, start, end, {}, orgPaths)`（含场景→模块过滤的那个重载），直接断言返回的圈选条件：

| orgPaths | 返回 |
|---|---|
| `12345_97349606689168923`（配置部门本身） | 21/22/23 三个场景 |
| `12345_97349606689168923_888_999`（下属） | 三个场景 |
| `12345_9734960668916892`（id 前缀）/ `..._973496066891689231`（超串） | `[]`（不误命中） |
| 老师真实路径 `12345_4959407036876800_6816343048455168_66707677944472576`（未配置） | `[]` |

- **外层门控另有既有闸**：测试班 `500775385189890048` 被 `CommonRuleFilter` 以 `not_need_handle_clazz_name_in_blacklist` 拒掉（班名黑名单），故整链路 `needHandle=false`、MQ 圈选消息本就不会发——这是此前"MQ 不可观测"的真因，与本需求门控无关。
- ⚠️ **Apollo 现值已被改动**：student-data TEST `renewal.ai.dept.module.switch` 现为 `{"97349606689168923":[1..8]}`（不再是 `6816343048455168`），`refund.ai.dept.module.switch` 仍为 `6816343048455168`。用 177071 测续班展示侧会得到"全关"，属配置而非代码问题。
- 补单测 `AiModuleSwitchServiceTest` 11 条（部分模块开关 / 下属继承 / id 前缀与超串不误命中 / 多部门并集 / 退费字符串 code），commit `3777608bc`（expand-exclude）。

### expand-exclude 迁 `test-gtbg-dev-1` + 扩科补验（2026-09-24，✅ 已验证）

**dev-1 部署（eureka UP、本分支镜像）**：cart `cart-gaotu100-com-86dcd745b7-rl9f2`(10.218.238.129) / student-data `student-data-549fd8d47c-mzpzs`(10.218.248.159) / product-b `product-b-d5b79766-cprsr`(10.218.237.202) / product `product-gaotu100-com-75946fc5b5-*`(10.218.249.72、10.218.238.117) / student-center `student-center-56dd6d4bbd-d4hsm`(10.218.249.73)。**此后扩科 / AI 配置化一律 `traffic-env: test-gtbg-dev-1`。**

| 例 | 调用 | 实测 |
|---|---|---|
| B 端开排除复跑 | product-b `RenewalProductServiceImpl#recommendProductList(579985778241837056, 20002)` | ✅ 只剩 subject=7 + 纯续 |
| C 端开排除复跑 | cart `RenewalService#getRenewalDetail("20002","579985778241837056",...)` | ✅ subject=1 不出现 |
| 在读透出 | `RenewalInReadSubjectService#listOtherModeInReadSubjects(20002, 1)` | ✅ `[1,2,4]` |
| **小班路径 开排除** | cart `ExpandSubjectRecommendService#recommend` 小班重载，学员 `5001708464`（大班在读 subject=5）excludeMode=1 | ✅ 只剩 subject=4 |
| 小班路径 关排除 | 同上 excludeMode=0 | ✅ subject=5、4 都在 |
| **全局开关回退** | cart TEST Apollo `renewal.expand.exclude.switch=false` 后复跑小班 excludeMode=1 | ✅ 退化为无排除，两条都在；已改回 `true`（原本未配、代码默认 true，等价） |
| **AI 部分模块开关（门控）** | student-data Apollo 临时 `{"6816343048455168":[1,2]}` → `queryModuleSwitch(1, 177071, ["1","2","5"])` | ✅ `{1:true, 2:true, 5:false}`；已恢复 `{"97349606689168923":[1..8]}` 并读回 |
| **AI 部分模块开关（展示侧真实入口）** | 同上配置，proxy 登录态即 177071（gongxuemeng）；`POST /bgwApi/component/student-center/ai/clazzUser/userPortrait`（模块 1）与 `/bgwApi/component/student-center/problem/fulfillProblem/overview`（模块 3），入参 `{userId:7404351741, clazzNumber:500775385189890048}` | ✅ 模块 1 放行（返回对象，拦截形态是 `data:null`）；模块 3 被拦 `data:{}`；**对照**：临时改 `[1,2,3]` 后模块 3 返回 `score:100…` 完整数据 → 拦截生效。已恢复原值并读回 |

**坑**：arthas 线程里直调 cart 推荐会因 Ribbon 子上下文懒加载失败抛 `HystrixRuntimeException`，排除逻辑按设计 fail-open 成「无排除」——是 arthas 调用环境问题，改走 acl 桥（真实 servlet 线程）即正常。

### AI 开关灰度语义修正（2026-09-24，dev-1）

用户订正：未配置应=全量放开（灰度未开始），否则发版即停全部 AI。student-data `24be1d776`（空配置→true；已配置时无部门/未命中→false）、student-center `a3a4d7cb5`（开关查询异常/缺值/无登录→fail-open）。单测 student-data 12 条、student-center 3 条通过。

| 例 | 配置 | 调用 | 实测 |
|---|---|---|---|
| 灰度未开始 | `renewal.ai.dept.module.switch={}` | `queryModuleSwitch(1, 1/177071, [1,3,8])` | ✅ 全 true（含无部门老师 1） |
| 灰度中 | 恢复 `{"97349606689168923":[1..8]}` | 同上 | ✅ 未命中部门全 false |

- student-data 新 pod `student-data-764ff58fbd-z77q5`(10.218.238.232) eureka UP；Apollo 已恢复并读回。
- ⚠️ student-center 新 pod `student-center-789db6448c-frnlj` **一直 Pending 无 IP（集群调度/资源问题）**，泳道仍是旧 pod，fail-open 仅单测验证、未在环境验证。**2026-09-29 已补验，见下节，结论已更新**。

### student-center 展示侧 fail-open 环境补验（2026-09-29，dev-1，✅ 已验证）

前次 pod 调度问题已解决：`student-center-865c9c4547-wld47`（commit `a3a4d7cb`）、`student-data-867b58c649-l7znj`（commit `24be1d77`）均 eureka UP，就是当时验证卡住的那两个 commit，直接在其上补验，不用重发。

| 分支 | 验证方式 | 实测 |
|---|---|---|
| 无登录态 → fail-open | arthas 直调 `AiModuleSwitchQueryService#isRenewalModuleEnabled(1)`（无 web 请求上下文，`LoginInfoUtils` 天然取不到登录态） | ✅ `true` |
| 部门显式不匹配 → 仍拦截 | 真实 HTTP `POST /bgwApi/component/student-center/problem/fulfillProblem/overview`（proxy 登录态 177071），Apollo `renewal.ai.dept.module.switch` 临时改成两个不同的不匹配部门号（`999999999999999999`、`97349606689168923` 本身也不匹配 177071） | ✅ 两次都 `data:{}`（拦截形态），确认 fail-open 没有把显式 false 也放行 |
| 部门匹配（正对照） | 同接口，Apollo 临时改成 177071 真实部门 `6816343048455168` | ✅ 返回完整数据（`score:100` 等），与拦截态对比清晰 |

验证过程：Apollo 每次改值都读回确认 pod 内存值同步（arthas 查 `AiDeptModuleSwitchConfig#renewalDeptModuleSwitch`）后再发请求；验完已改回原值 `{"97349606689168923":[1,2,3,4,5,6,7,8]}` 并读回确认。**T-11 至此三条分支（无登录/不匹配拦截/匹配放行）全部环境验证通过，状态置为已完成。**

### 扩科「在读」上课形式过滤已补（2026-09-30，✅ dev-1 已验证）

**改动**：`RenewalInReadSubjectService`（student-data，`feature-xuban-expand-exclude` `dce3b3a45`）读在读科目表后，按班级上课形式补充过滤——`ClazzSyncAclService#listByNumbersFromCache`（60s 缓存）批量查 `ClazzDO.operationMode`，不在 Apollo 允许列表内的班级整行剔除；**Apollo `renewal.inread.operation.modes`（student-data application）为 list，空/未配 = 不过滤（历史现状）**；查不到上课形式（班级缺失/下游异常）的记录**保守保留**（宁可少排除，不误放大学员在读范围）。单测 `RenewalInReadSubjectServiceTest` 8 条（空配置/大班取小班/小班取大班/查失败保留/非法参数/无在读）全过。

**Apollo**：TEST 已配 `[1]`（仅线上算在读）并**发布生效**（releaseKey `20260930190324-188a49b33afd2313`，读回确认）。回退 = 清空该 key。**PROD 上线后同 key 配 `[1]`**（旧代码不读该 key，先配也无影响）。降级链完整：key 清空 → 不过滤；cart 侧另有 `renewal.expand.exclude.switch` 全局回退。

**dev-1 E2E（2026-09-30，✅）**：新 pod `student-data-69665b9c5-fzd5h`（10.218.237.240，commit `dce3b3a4`）eureka UP；网关桥调 `listOtherModeInReadSubjects(20002, 1)` → `[1,2,4]`（与改前一致，该学员在读班全为线上）；pod 日志 `filterByOperationMode | allowedModes: [1], total: 8, kept: 8`——配置已加载、过滤路径真实执行、线上课零误伤。「剔除线下行」分支 TEST 无线下在读数据可造，由单测覆盖（`should_dropRowsWhoseOperationModeNotInConfig`，大小班两路径）。

### 扩科「在读」口径缺口（2026-09-29 复核，结论更新）

README 原写「上课形式为线上 / 订单未全部退款**现有链路没有，需补**」，产品反馈这两条是既有功能、之前做过。重新查代码 + 查库，结论分开：

- **「订单未全部退款」✅ 确认已实现**：不是 student-data 自己过滤的，是 `clazz-distribution-server` 的 `OrderEventRefundSuccessConsumer#consumeOrder`（`clazz-distribution-server-jobs/.../consumers/rocketmq/order/OrderEventRefundSuccessConsumer.java:59-62`）——`RefundOrderStatus.NORMAL_REFUND`（正常退款/退课）会调 `enterClazzService.quitClazzAndDelRight`，退课后触发 `SUBCLAZZ_QUIT` 事件，student-data 收到后把这条记录从「在读」表里删掉。「退款不退课」类型不退课，仍保留在读，这个也符合预期。所以"在读"本身已经排除了会退课的那种退款，是靠上游机制间接满足的。
- **「上课形式为线上」❌ 代码确实没有过滤**，但**实测数据上不构成风险**：`dws_fuwu_clazz_user_subject`/`dws_small_clazz_user_subject` 两张表字段里没有 `operation_mode` 列（查不到就没法按它过滤）；写入前置校验（`DwsRenewalSubjectConsumer#checkFilter`、`OdsSmallRenewalSubjectSyncService` 的进班处理）只查成人课/课程类型/赠课标签/预售/学季枚举；上游消息路由 `SubclazzStudentMsgProducer#isOmoClazz`（clazz-distribution-server）只区分 OMO 和非 OMO，`OperationModeEnum.OFFLINE(2)` 在整个仓库里除枚举定义外未被引用过。**查了 PROD 全部 3739 个续班计划绑定过的前置课程（`course_center.course.operation_mode`），100% 是线上(1)，零线下、零 OMO**——现状没有风险，是因为业务上从没人往续班计划里绑过线下课程，不是代码挡住了。course-center 确实支持创建线下课程（`arrange1v1offline` 体系是真实在用的），如果哪天有人把线下课程绑进续班计划，这条学员会被误判为"在读"，扩科排除会悄悄失效、不报错。**2026-09-30 用户定要补上：已按 Apollo list 实现（见上一节），Javadoc 一并订正。**

另：小班当前课 → 取大班在读的推荐链路、全局开关 `renewal.expand.exclude.switch=false` 回退均无 E2E。

### 主讲适配线上配置（2026-09-24，✅ 已核实）

PROD `es_query_config` type=5：`smallClazzRoster` / `microContinuationService` 的 account 字段含 `assistantAccountId` + **`mainTeacherAccountIds`**，postTag 含 `mainTeacherMainPostTag` → 主讲 OR 权限线上已配。

### 先调后填 A 侧（机制已验）/ 小班调课（✅ 端到端）

- **先调后填 A 侧**（PRD 最终效果第 4 条）：**查询侧按班级取**——student-center `RenewalService#pageQueryQuestionnaire` → teacher-tool `queryRecordsMultiByClazz`，SQL 为 `project_number = 问卷 AND clazz_number IN (所查班级) AND user_id IN (该班花名册)`，不跨班；A 能看到靠**写入侧 fan-out 给 A 落一条 clazz=A 的明细**。不经调课同步，走提交时 fan-out——`DwsRenewalQuestionnaireConsumer` 用 `listStudentByUidByCourseNos(userId, shareCourses, getAllStatus())` 取学员**所有状态**班级，明细 `sendTeacherToolQuestionMsg` 与花名册 `updateQuestionnaireStatus` 都对该列表逐班写、无状态过滤。**实测**：20019 在课程 `467797268366426112` 下的已退出班 `467798149581307904`（status=2）会被该接口返回 → 已离开的 A 班同样会写入。整链未造：无法造「离开 A、在读 B」真实状态（大班调课受收款账户限制、同课程不可重复购买、造数引擎无退款工具）。B 侧已由 S3 端到端验证。
- **小班调课（2026-09-24 17:12，✅ 端到端已验证）**：小班 `529222801226287104`（计划 `529067710552891392` 进行中、绑定问卷 bizId `17085061328535727`）。学员 1449414 的该班明细 20560 临时挪到假原班 `999000222`、小班花名册置 1，arthas 发调课 `999000222 → 529222801226287104`：日志 `writeCommitStatus | isSmallClazz: true`；明细复制出 21884（clazz=新班，同 group）；ES `ads_small_clazz_user` `529222801226287104-1449414` 状态 **1→3**、`submitTime=1774419606000`。已还原（删 21884、20560 挪回、花名册本就为 3）。另：小班 `529911462177622016` 计划已不存在 → 正确走「新班未绑定问卷，skip」。小班花名册脚本 `/tmp/es_set_small.py <docId> <status>`。

### QA 用例 49607 全量回归（2026-09-28，dev-3，✅ 22/23 通过、1 阻塞）

用例 https://qa.baijia.com/banshan/#/caseManager/171/49607/70678/3（tangwen01，23 条）。环境：分支未合 master → 只能测试环境；四服务重发 dev-3 并按 `imageName` 核对：student-data `70c32f0f` / teacher-tool `c169f274` / product-task、product-b `f549f407`，均 eureka UP。本轮 CDS recordId 990201–990217，发送 `/tmp/cds_send2.py`（`ORIGIN_USER_ID=<uid>` 带 userId）；调课 `/tmp/send_t.sh`（pod 已改 `student-data-7f5f6ccd77-g6fhr`）。

| # | QA 用例 | 入参 | 实测 | 结论 |
|---|---|---|---|---|
| 1/17 | 全局 TC0001 / 调课 TC0001 | 提交 990201（A 链接，userId=20017）+ 20024 A 班插明细 21910 后发 A→B | 20017 computed=20017、A 花名册 3；B 复制 21911（新 uniqueBizId、同 group）、B 花名册 1→3、submitTime=A 明细 finish | 通过（提交人与调课人分开，大班真实调课受收款账户限制） |
| 2 | 全局 TC0002 | 20018 B→A（B 明细 21869 属 project `999…`） | teacher-tool `no old record to share, projectNumber is 1732…`，A 无新增 | 通过 |
| 3 | 规则1 userId | 990201 A 链接 userId=20017、姓名 `1234`(20020)、手机号 12600000019(20019) | computed=20017 | 通过 |
| 4–11 | 规则2–7 / 优先级 / 计划隔离 | 990202–990209（同 P1–P5/R1/R2） | 20017/20019/20019/20018/20019/20018/20017/0 | 通过 |
| 12 | 同名上限 | arthas 临时 `NamePlanRuleService.studentNameQueryLimit=0`（需 `options strict false`）→ 990214；还原 20 → 990215 | 0 → 20018 | 通过（等价代跑：测试库所有同名学员 ID 最小的都在本计划内，造不出第 21 位；已还原并读回 20、strict=true） |
| 13 | 未归属重试 | product-b acl 桥 `QuestionnaireRecordService#dealNotExistedComputeUser` ×4 | 365/366 retry 1→2→3→3；370(990214) 首轮自动归属 20018 | 通过（「达阈值后人工绑定」未验） |
| 14 | 辅导老师不匹配 | 990210 A 链接(177071) userId=20025（B 班唐稳01）；对照 990211 userId=20019（B 班弓雪萌） | 990210 computed=0 + `no account subclazz matched, mark as unattributed`；990211 归属 20019、clazz=B | 通过 |
| 15 | 不同手机号都展示 | 990216 B 链接姓名 `123`、新号 12999990216 | 新增 21913；20019 B 班 6 个手机号各 1 行 | 通过 |
| 16 | 同手机号只展示最新 | 990217 B 链接 12600000019 | 21876 原地更新 finish 16:37:42、不新增；B 花名册 submitTime→16:37:41 | 通过 |
| 18 | 先调后填 | B 侧：990203（20019 只在 B，用 A 链接）→ B 明细/花名册更新。**A 侧（2026-09-28 补验，✅ 已通过）**：新学员 20040，直接写 `gaotu.subclazz_student` 两行模拟「A 已退出（status=2）+ B 在读（status=1）」（`ClazzDistSubclazzStudentService#listSubclazzStudentByCourseNumbersAndUserId` 读回确认两行都返回）；`ORIGIN_USER_ID=20040` 用 B 链接提交（990218/990219）→ `questionnaire_record` computed=20040 clazz=B；`user_questionnaire_record` A/B 两班各有明细（21916–21920）；ES 花名册 A(`36325046492463488-20040`)/B(`36325046495478144-20040`) 均 `renewalQuestionnaireStatus=3` | 通过 |
| 19 | 调了没填 | 20024（无任何明细）A→B | `old clazz has no same questionnaire, skip roster recompute`、无明细、花名册 1 | 通过 |
| 20 | 幂等 | 重投 20024 A→B | teacher-tool `new clazz already has questionnaire, skip`，仍 2 行 | 通过 |
| 21 | 开关 | student-data TEST 发布 `renewal.questionnaire.transfer.switch=false`（pod 读回 false）→ 发 A→B；删 key 发布（pod 读回 true）→ 再发 | 关：无消费日志、无明细、花名册 1；开后旧消息不重投，新事件复制 21912、花名册 1→3 | 通过（key 已删，已发布 848 项与原一致） |
| 22 | 同班 | feign 直连 old=new | `code=0,data=false,msg=无需同步` | 通过 |
| 23 | 必填校验 | 四种缺参 | 均 `code=400 参数异常` | 通过（**预期文案与实现不符**：`@Valid` 先拒，Controller 的「参数错误：…必填项」走不到） |

**QA 用例需修正**：规则 TC0003 日志在 product-task 不在 product-b；未归属 TC0001 触发是 product-task xjob `QuestionnaireRecordComputeHandler`（test 无该任务，用 product-b 桥），且需创建满 10 分钟、`manual_user_id=0`；未归属 TC0002 前置应为「问卷带 userId、学员在计划其它班（不在链接班）、辅导老师≠链接 accountId」；规则 TC0010 可改为调小 limit；调课 TC0002 A 侧靠提交时 fan-out 而非计划级规则；调课 TC0006/0007 路径 `/feign/questionnaire/user/transfer/sync`、TC0007 预期文案应为 `参数异常`。

**本轮测试数据改动（TEST，保留）**：`questionnaire_record` 新增 990201–990219；`user_questionnaire_record` 新增 21910（20024 A 班，group 999900024）、21912、21913，21876 被 990217 更新；ES `36325046495478144-20024`=1。`gaotu.subclazz_student` 新增 20040 两行（course `578530883890331648`，clazz A `581200735616724992` status=2 / clazz B `581200735551846400` status=1，直写模拟真实退出/在读，非真实订单产生）；20040 的 `user_questionnaire_record` 21916–21920、ES 花名册 A/B 均保留（status=3，见 #18）。

**2026-09-28 用户已清理 #21 现场**：`user_questionnaire_record` id=21911（原软删的 B 班同步副本）已硬删除；ES `36325046495478144-20024` 的 `renewalQuestionnaireStatus` 已重置为 `1`。**上面 #21 开关用例表格里「花名册 1→3」这条证据的现场已不存在**，重新验证需另起学员或重新走一遍开关流程；20024 现在只剩 A 班明细 21910 + 第二次同步产生的 B 班明细 21912（is_del=0，未受影响）。

**观察（既有行为，非本分支改动）**：20018、20040 两次都出现过 A 班重复明细（teacher-tool 先查后插非原子），不影响判定结果，未处理。

## 第二批：扩科【推荐排除】（2026-09-22，`feature-xuban-expand-exclude`）

**PROD Apollo（2026-09-30，草稿已建·未生效）**：cart.gaotu100.com / PROD / application 新增 `renewal.expand.exclude.switch=true`（dry_run diff 仅此一条）。发布 403——zhangzeling 有修改权（草稿写入成功）但**无发布权**，负责人 lijianxiang；待其后台发布或授权。不发布不影响功能：代码默认 true，key 仅作降级开关。读回确认走 `apollo_get_key(cart.gaotu100.com, PROD, renewal.expand.exclude.switch)`。

**部署**：`product-b` / `product` / `student-data` / `cart` 均 `test-gtbg-dev-3`、eureka UP。
**坑**：cart 是 Boot1.5 + Netflix feign，**不能依赖 `student-data-client`**（带 Boot2.x/openfeign 类 → 启动崩）→ 改 cart 自持 DTO + Netflix `@FeignClient`。

### 已验证

| 项 | 例 | 实测 |
|---|---|---|
| student-data 透出接口 `RenewalInReadSubjectService#listOtherModeInReadSubjects` | 学员 `7542297028` 当前**大班** → 取小班在读 | ✅ `[12]`（历史） |
| 同上 | 当前**小班** → 取大班在读（该学员无大班在读） | ✅ `[]` |
| 同上 | 学员 `7542292905`（无小班在读） | ✅ `[]` |
| 同上 | 不存在学员 / 非法 mode | ✅ `[]` |
| cart 过滤 | `ExpandSubjectRecommendServiceTest` | ✅ 7 passed（本地） |
| product-server 配置读回 | DB 给扩科节点(id 772 / 计划 `546943017307740160`) 的 ext_config 写 `excludeMode:1` → `ProcessService#listProcess` 返回 `extConfig.excludeMode=1` | ✅ |
| product-server 字段级合并 | `ProcessService#convertNodeConfig` 传**不带** `excludeMode` 的 extConfig → 返回仍带 `excludeMode:1`（未被清空） | ✅ |

### cart→student-data Feign 请求体命名风格（2026-09-23，已修复）

**真因**：请求体命名风格不一致（非测试泳道基础设施问题），**线上同样会复现**。

| 证据（arthas 实测） | 值 |
|---|---|
| cart 传进 Feign 代理的对象 | 有值（`getUserId()=7542297028`） |
| cart 实际发出的 body | `{"current_room_type":1,"user_id":7542297028}` ← **snake_case** |
| student-data 侧 watch 到的入参 | `userId=null, currentRoomType=null` → 返回 `[]` |
| cart Ribbon 实际选中的实例 | 13/13 次全打到正确的 base test 实例 `10.255.164.233`（**不存在打错泳道**） |

**根因**：cart 的 `cart-controller/.../MvcConfig.java:100` 把 fastjson 全局 `SerializeConfig` 设为 `SnakeCase`，
而 student-data 契约是 camelCase，服务端绑不上 → 两字段全 null → 接口恒返回空集合。

**修复**（commit `96e334b8`）：`RenewalInReadSubjectFeignService` 的 `configuration` 由 `FeignConfig`
改为仓库已有的 `CesCamelCaseFeignConfig`（fastjson 编/解码强制驼峰）。

**修复后实测**：

| 例 | 泳道 | 实测 |
|---|---|---|
| cart 出站 body | test | ✅ `{"currentRoomType":1,"userId":7542297028}` |
| cart→student-data，学员 `7542297028` 当前大班(mode=1) | test | ✅ `[12]`（修复前 `[]`） |
| 同上 | test-gtbg-dev-3 | ✅ `[12]` |
| 同上，当前小班(mode=2)（该学员无大班在读） | test | ✅ `[]`（证明入参真的生效，非恒空） |
| cart 解码 product-server 的扩科配置（计划 `546943017307740160`） | test | ✅ `excludeMode=1`、`expandSubject=true` |

**注意**：用 arthas `vmtool` 直接调该 Feign 会抛 `HystrixRuntimeException`（子上下文在 arthas 线程里初始化失败，
报 `ConfigurationPropertiesBindingPostProcessorRegistrar.class not found`）——这是**调用手段的副作用**，
走正常 Spring 路径（acl 桥 / 业务链路）正常。验这个 Feign 用 acl 桥，别用 arthas。

**`FeignTrafficEnvForwardConfig` 与 Apollo 开关 `feign.traffic.env.forward.enabled` 均已移除**（commit `6deaa256`）：Ribbon 本就选对实例，无需该转发。

### 排除逻辑端到端（2026-09-23，已验证）

B/C 端真实入口跑不通（当时缺合格测试数据，见下「B/C 端真实入口端到端」），先改在 cart JVM 内直调大班重载
`ExpandSubjectRecommendService#recommend(userId, config, courseDTOMap, purchasedProducts)`，
**真实走 Feign 到 student-data**，只跳过商品详情组装。学员 `7542297028`（小班在读 subject=12），
推荐列表配两条：`grade=13/subject=12`(商品 111111) 与 `grade=13/subject=4`(商品 222222)。

| 例 | 入参 | 期望 | 实测 |
|---|---|---|---|
| 开排除 | `excludeMode=1` | 只剩 subject=4 | ✅ 仅返回 `productId=222222, configuredSubject=4` |
| 对照 | `excludeMode=0` | 两条都在 | ✅ 返回 `111111`(subject 12) + `222222`(subject 4) |

**复现**（`-c <classloader hash>` 每次部署会变，先 `sc -d com.gaotu.feignclient.studentdata.OtherModeInReadSubjectReq` 取）：

```bash
~/.local/mcp-servers/venv/bin/python "$HOME/.claude/skills/pod-terminal/pod_term.py" arthas \
  --service-code gaotu_cart --env test --command "$(cat /tmp/e1.txt)"
# e1.txt 内容见本节说明：vmtool -x 3 -c <hash> --action getInstances \
#   --className com.gaotu.renewal.small.service.ExpandSubjectRecommendService \
#   --express '(#cfg=new ...ExpandSubjectConfigBO(), #cfg.setExcludeMode(1), ... instances[0].recommend(7542297028L,#cfg,#m,new java.util.HashSet()))'
```

**排查要点**：cart 调 student-data 的 Feign 名必须用 eureka 名 `STUDENT-DATA`（不是 `student-data`）。

### B/C 端真实入口端到端（2026-09-23，✅ 已验证）

**测试数据（合格组合，`test-gtbg-dev-3`）**

| 项 | 值 |
|---|---|
| 续班计划 | `579985778241837056`「任务系统-续班测试-无正式报名-0917」（`renew_master.type=1` **大班**，有效期 2026-09-09~2027-09-30）|
| 前置课 | `579985105158701056` → 后置课 `579985185825652736` / 后置班 `579985190466650112`（四年级语文，**grade=14**，`product_type=2`）|
| 学员 | `20002`（另 20003~20011、7416248574 同样可跑）|
| 扩科节点 | `node_config` id 760 / number `580101357072160769`；2026-09-23 直连 test 改 `begin_time/end_time` = `2026-09-22 00:00 ~ 09-30 23:59`、`ext_config={"allowDuplicate":false,"expandSubject":true,"forceBuy":false,"excludeMode":1}` |
| 推荐行 | id 70 `grade=14/subject=1/type=2/560886393904048128`（应被排除）、id 71 `grade=14/subject=7/type=2/566006711792488448`（应保留）|
| 学员小班在读 | `listOtherModeInReadSubjects(20002, currentRoomType=1)` = `[1,2,4]` → 大班路径排除 subject∈{1,2,4} |

**B 端** `POST /b/renewMaster/recommendProductList`（`RenewalProductServiceImpl#recommendProductList`，经 product-b acl 桥）

| excludeMode | 返回商品 | 结论 |
|---|---|---|
| 1（开排除）| `566006711792488448`(subject=7) + `579985190466650112`(纯续后置班) | subject=1 被排除 ✅ |
| 0（对照）| `560886393904048128`(subject=1) + `566006711792488448` + `579985190466650112` | 三条都在 ✅ |

**C 端** `GET /web/renewal/cart`（同 7 参 `RenewalService#getRenewalDetail`，fromBCart=false）

| excludeMode | 返回 `(productSkuNumber, recommendType)` | 结论 |
|---|---|---|
| 1 | `(579985190466650112,1)`(纯续) + `(566006711792488448,2)`(扩科 subject=7) | subject=1 被排除 ✅ |
| 0 | `(579985190466650112,1)` + `(560886393904048128,2)`(subject=1) + `(566006711792488448,2)` | 三条都在 ✅ |

**跑通 B/C 端的完整数据条件（复用要点）**：① 计划 `type=1` 大班 + 有效；② `renew_master_course_relation` 有前置课；③ 学员在该前置课**有有效订单**（`order_info.order_status in (1,2,3)`）——这是最容易漏的一条，`coreHandle:1264` 无订单直接返回空；④ 前置课在课程中心配了后置课（`course_extension` / cart `getAfterCourseMap`）；⑤ 扩科节点 `ext_config.expandSubject=true` 且时间窗覆盖当前；⑥ 推荐行 `grade` = 后置课年级。
**选组合的 SQL**：`renew_master(type<>2,有效) join renew_master_course_relation join order_info(order_status in (1,2,3))`，再对候选逐个调 cart `getRenewalDetail` 看 `grade_clazz_list` 非空（本次 60 个候选里只有计划 `579985778241837056` 命中）。

**已废弃的错组合（留档）**：计划 `546943017307740160` 是 `type=2` **小班课计划**，学员 `7542297028` 是**大班**学员且**无任何订单** → 天然跑不通（改时间窗/插推荐都救不了）。

#### 复现命令（可直接粘终端；经代理需先起 8765+8888，见 baijia-proxy skill）

```bash
# B 端（product-b acl 桥，走网关）
curl -sk -x http://127.0.0.1:8888 \
  'https://test-fuwu.baijia.com/bgwApi/product-b/b/test/acl/compare/service' \
  -H 'content-type: application/json' -H 'traffic-env: test-gtbg-dev-3' \
  --data-raw '{"serviceNameAndMethodName":"com.gaotu.product.service.renewal.impl.RenewalProductServiceImpl#recommendProductList","params":[{"renewMasterNumber":"579985778241837056","userId":"20002"}]}'

# C 端逻辑（cart 7 参 getRenewalDetail，fromBCart=false；等价 web/renewal/cart，绕开登录）
curl -sk 'http://<cart-pod-ip>:28688/test/acl/compare/service' \
  -H 'content-type: application/json' -H 'traffic-env: test-gtbg-dev-3' -H 'host: CART.GAOTU100.COM' \
  --data-raw '{"serviceNameAndMethodName":"com.gaotu.renewal.RenewalService#getRenewalDetail","params":["20002","579985778241837056",false,false,null,null,false]}'

# 对方模式在读（student-data 桥，走 pathInfo 前缀 /student-data/**）
curl -sk -x http://127.0.0.1:8888 \
  'https://test-fuwu.baijia.com/bgwApi/student-data/test/acl/compare/service' \
  -H 'content-type: application/json' -H 'traffic-env: test-gtbg-dev-3' \
  --data-raw '{"serviceNameAndMethodName":"com.gaotu.student.data.domain.service.RenewalInReadSubjectService#listOtherModeInReadSubjects","params":[20002,1]}'
# 期望：B/C 端 excludeMode=1 只剩 subject=7；改 node 760 ext_config.excludeMode=0 后 subject=1 也出现
```

#### 已改动测试数据清单（2026-09-23，可回滚）

| 表.行 | 字段 | 原值 | 现值 | 目的 |
|---|---|---|---|---|
| `gaotu.node_config` id 760 | begin/end | `2026-09-18 09:17:15`（起=止，已过期）| `2026-09-22 00:00 ~ 2026-09-30 23:59` | 让扩科节点生效 |
| `gaotu.node_config` id 760 | ext_config | `{"allowDuplicate":false,"expandSubject":false,"forceBuy":false}` | `{"allowDuplicate":false,"expandSubject":true,"forceBuy":false,"excludeMode":1}` | 开扩科+排除 |
| `gaotu.renewal_expand_subject_recommend` | 新增 id 70/71 | — | `grade=14/subject=1/type=2/560886393904048128`、`grade=14/subject=7/type=2/566006711792488448` | 推荐行 |
| （留档·错组合）`gaotu.node_config` id 772 | begin/end | `2026-09-25 04:00 ~ 09-26` | `2026-09-22 ~ 09-30` | 计划 `546943017307740160`（小班，跑不通）|
| （留档·错组合）`gaotu.renewal_expand_subject_recommend` | 新增 id 68/69 | — | plan `546943017307740160` | 同上 |
| （留档·错组合）`gaotu.renew_master_course_relation` | 新增 id 69817 | — | plan `546943017307740160` ← pre_course `578667318880518144` | 同上 |

> **TEST 查库直连即可**：DMS(`mysql_query`) test 侧常登录失效；用 `gaotu_test_rw` 直连（`mysql_query.resolve_rw_dsn(库名)` 取 host/密码 + pymysql），已写进 mysql-query skill。

**查法**：student-data 桥走 pathInfo 前缀 `/student-data/**` → `https://test-fuwu.baijia.com/bgwApi/student-data/test/acl/compare/service`；报 700 先 `POST http://127.0.0.1:8765/api/v1/bridge/refresh` 刷 Cookie。

## 第三批：AI 模块配置化（2026-09-23）— 有效结论

> 部门口径 / Apollo 配置值 / 部署与验证细节见下一节「部门口径修正」（本节原基于「课程部门」的结论已作废）。

- **模块 code**：续班 `1 用户画像 / 2 沟通概况 / 3 沟通建议&评分 / 4 服务建议&评分 / 5 未续跟进 / 6 已续总结 / 7 用户反馈 / 8 主管点评`；退费 `tutoring / learning / satisfaction / refund_root_cause / service_suggestion / prediction`
- **灰度语义**：整个配置为空 = 灰度未开始、全量放开（与上线前一致）；配置了任意部门后，只放开命中部门的已配置模块，其余关闭（2026-09-24 订正，原「未配置 = 关闭」作废：那样发版即全量停 AI）
- **配置放 student-data 的 Apollo**（不接 GAIA）；student-center 展示侧走 feign 查 student-data，两侧同源同口径
- **Apollo key**（默认 `{}`）：`renewal.ai.dept.module.switch` / `refund.ai.dept.module.switch`
- **代码落点**：student-data `AiDeptModuleSwitchConfig` / `AiModuleSwitchService` / `RenewalAiModuleEnum` / `RefundAiModuleEnum`；分析侧接线 `RenewalReasoningService`(5/6)、`RefundReasoningService`(退费5)、圈选 `RenewalAiComm{RealTime,History}SelectHandleService`(1/2/3/4)、`RefundPredictionService`(prediction)；透出 `AiModuleSwitchController` → `POST /feign/ai/module/switch/query`。student-center `AiModuleSwitchFeignClient`（本地契约）+ `AiModuleSwitchQueryService`（fail-closed）
- **展示侧已接接口**：`ai/clazzUser/userPortrait`(1)、`commSummary`(2)、`/problem/fulfillProblem/overview`(3)、`/fulfillSop/overview`(4)、`/user/feedback/query`(7)、`ai/clazzUser/evaluateQuery`(8)、`roster/refund/reasonType`+`roster/refund/analysis`(refund_root_cause)、`/course`(learning)、`/stage`(tutoring)、`/intent/record`(prediction)
- **提交**：`c91d5cd66` / `7b9215766`（首轮）、`cf47510d5` / `cab6106ac`（第二轮补退费展示侧）

## AI 模块配置化：部门口径修正（2026-09-23 已改·已部署·**已验证**）

**口径（PRD https://gaotuedu.feishu.cn/wiki/AH5ewehsEiXohfkDgQEcKQjHnad）**：按**虚拟架构部门**配置，本部门及下属某模块配置了，二讲才可用 / AI 才分析；未配置即关闭。部门来源 = **老师（二讲）**主岗部门，**不是课程部门**（课程部门会让同课程下所有老师都可见，不隔离）。

| 维度 | 实现 |
|---|---|
| 部门来源 | 老师虚拟组织架构主岗路径 `StaffDto.mainPostOrgPathFromRoot` |
| 展示侧(student-center) | 登录老师 `LoginInfoUtils.getLoginUser().getAccountId()` → org path |
| 分析侧(student-data) | 该班辅导老师：`clazzNumber → 辅导班 assistantNumber → accountId → org path` |
| 匹配 | 路径按 `_` 分段**精确**命中配置部门 id（本部门及下属生效；数字 id 前缀不误命中） |
| 配置值 | key = 虚拟架构部门 org number；整体为空 = 全量放开，配置后未命中部门 = 关闭 |

**已改（2026-09-23，已 push）**：student-data `12e41da47`、student-center `84ec1b732`（分支 `feature-xuban-expand-exclude`）
- student-data：`AiModuleSwitchService` 新增 `resolveAssistantOrgPaths(userId, clazzNumber, subclazzNumber)` / `resolveAccountOrgPaths(accountId)`；5 处分析侧调用点全改；`matchDept` 分隔符 `/`→`_`；feign 入参 `departmentIdPaths` → **`accountId`**
- student-center：`AiModuleSwitchQueryService.isRenewal/RefundModuleEnabled(moduleCode)` 内部取登录老师 accountId；11 处调用点去掉 `clazzNumber`

**部署（2026-09-23 复核）**：test-gtbg-dev-3 —— student-data pipeline `1284022` → 新 pod `10.218.250.176`、student-center pipeline `1284028` → 新 pod `10.218.236.63`，**均 eureka UP**。

**Apollo（student-data/TEST，已发布）**：2026-09-23 两个 key 均换成 org number `6816343048455168`（全模块开）；**2026-09-24 复查 `renewal.ai.dept.module.switch` 已被改为 `97349606689168923`**（refund 仍是 `6816343048455168`），见下文「AI 配置化圈选侧 E2E」。

**已验证（2026-09-23，student-data acl 桥走网关 + student-center 真实入口）**

| 项 | 调用 | 实测 |
|---|---|---|
| 老师 org path | `resolveAccountOrgPaths(177071)` | ✅ `["12345_4959407036876800_6816343048455168_66707677944472576"]` |
| 续班门控（命中） | `queryModuleSwitch(1, 177071, [1,2,5,6,7,8])` | ✅ 全 true |
| 退费门控（命中） | `queryModuleSwitch(2, 177071, [tutoring,prediction])` | ✅ 全 true |
| 未命中老师 | `queryModuleSwitch(1, 1, [1,2])` | ✅ 全 false（已配置、未命中部门=关闭） |
| 分析侧（班级维度） | `resolveAssistantOrgPaths(7404351741, 500775385189890048, null)` | ✅ 解析到同一 org 路径 |
| 分析侧（辅导班维度，退费预测用） | `resolveAssistantOrgPaths(null, null, 31298462823089024)` | ✅ 同一 org 路径 |
| **分析侧 E2E** | `RenewalReasonTaskService#handleSingleUser(500775385189890048, 7404351741, true)` | ✅ `handleCode=2`（SUCCESS），AI 产出完整未续归因并落库 |
| student-center→student-data feign | `AiModuleSwitchFeignClient#queryModuleSwitch({bizType:1,accountId:177071,moduleCodes:[7]})` | ✅ `{7:true}` |
| 展示侧真实入口 | `POST /ai/clazzUser/userPortrait`、`/ai/clazzUser/commSummary`（proxy 登录态；class `500775385189890048` / user `7404351741`） | ✅ 返回非空（门控放行，非 `data:null`） |
| **退费归因 E2E** | 造 `ees_data.refund_intent_info` 1 行（user `7463487951`，`refund_reason` 有值）改上下文 → `RefundReasonTaskService#refreshReasoning(500775385189890048, 31298462823089024, [7463487951])` | ✅ 新 pod `student-data-f578c6459-gpz7h` 走完时间窗/内容变更守卫，**无「退费归因AI模块未开启」**，调用 AI（`RefundReasoningService:234`）并落库 `subclazz_scene_ai_summary.refundReason`（ai_token `0c640c3f...`） |
| **退费预测 E2E** | `RefundPredictionService#publishSubClazzEvent(31298462823089024, {clazzNumber:500775385189890048, userIdList:[7463487951]})`（桥可调 private） | ✅ 新 pod 无「退费预测模块未开启」，走到 `RefundPredictionService:373` 打印「辅导班老师通知完成:31298462823089024」 |

**测试数据**：班级 `500775385189890048`（辅导老师 = gongxuemeng accountId `177071`，主岗部门路径命中配置）+ 学员 `7404351741`（续班沟通 8 条 + 问卷 1 条，见上一节）；退费 E2E 用同班学员 `7463487951` + 新造 `ees_data.refund_intent_info` 1 行（改上下文用，可回滚）。

**取数链路（参考）**
- 老师 org path：`OrganizationSyncAclService.listMainPostStaffByAccountIds("EES", accountIds)` → `StaffDto.getMainPostOrgPathFromRoot()`（先例 `AccountStaffDataQueryServiceV2.java:44-61`）
- 班级辅导老师：`SubclazzSyncAclService` / `TeacherSyncAclService`（clazz → assistantNumber → accountId）
- student-center 登录人：`LoginInfoUtils`（同文件 `RenewalClazzUserController:104` 已在用）

**待办**：灰度时配要放开的部门（key 用线上真实虚拟架构部门 id）；不配 = 全量放开。（圈选侧已于 2026-09-24 在 pod 内直接断言圈选条件验证通过，见下文。）

**圈选侧（场景 21/22/23 → 模块 1/2/3，`RenewalAiComm{RealTime,History}SelectHandleService#buildBizSelectCondition` 的 `filter(isSceneModuleEnabled)`）**
- 门控函数级已验：`queryModuleSwitch(1, 177071, [1,2,3])` → 全 true（配置部门命中 → 3 个场景全通过）
- `RenewalAiJudgeNeedHandleService#needHandle(clazz 500775385189890048, course 500775364606343168)` → `true`；`RenewalAiCommSceneHandleHelper#handleAiCommRealTimeSelectConditions(base)` 调用成功（无异常）
- **未做端到端断言**：桥调用 traceId 在日志后端查不到 student-data 自身日志（`AiCommOnsMqProducer#sendOrderedMessage` 亦查不到），故实际发出的圈选条件条数/内容未能观测

## 反射桥地址

| 服务 | 地址 |
|---|---|
| product-b | `https://test-fuwu.baijia.com/bgwApi/product-b/b/test/acl/compare/service` |
| teacher-tool | `https://test-fuwu.baijia.com/bgwApi/teacher-tool` |

19 位 ID 一律传字符串（防精度截断）。
