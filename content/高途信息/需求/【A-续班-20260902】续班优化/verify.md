---
title: 【A-续班-20260902】续班优化 · 验证手册
tags: [需求, 验证]
---

# 验证手册

> 只保留当前可执行条件、仍有效数据和最新预期。

## C 端推荐加购不展示（2026-10-22，只读定位）

对象：test-gtbg-dev-1，学员 `7658127801`，大班续班计划 `585960797778243584`。原请求 `includeBCart=true&sellerId=null` 返回 status=0，但仅纯续语文、扩科英语两项；trace `0cefcfc7-3cb1-4908-a9bb-f4920961b621.0.3`。仅将 sellerId 改为员工ID `8645` 后，增加小班课 `586267768769386496`（高一、recommendType=3）；trace `4b3693a8-6532-4008-a88a-14cbfa1324dd.0.3`。sellerId 语义为 employeeId，不是 accountId 90247；上游错配原因见下节。

`BCartFacadeImpl#listAdditionalPurchase(7658127801,8645)` 实查4项：小班课6004一项、组合商品51三项（SKU `584632626097291265`、`584458369312655361`、`584631715075588097`）；trace `cart_gaotu100_com.292.17926548626380069`。组合DTO三项均查到，且 combineClazzNumberList 全为空；子商品分别是会员卡8007+实物8010、三张会员卡8007、会员卡8007+实物8010；trace `cart_gaotu100_com.301.17926549279290078`。

当前两个独立缺口：① includeBCart=true仍要求有效sellerId，否则大小班分支均跳过加购查询；字符串null兼容修复只保证参数能绑定，不恢复老师身份。② 大班 `RenewalService#convertCombineResultToDTO` 仅从组合的大班子班回查课程年级；这三项无子班，且加购无configuredGrade，最终resolveGrade=null→返回null被丢弃。实际是商品已查到、缺课程年级导致转换丢失，不能误记为SKU查不到或前端单独隐藏。

用户本轮明确目标：B端加购的大班课、小班课、联报、组合商品及膨胀券应在C端推荐的加购区域展示。膨胀券8014在order已有SKU查询、限购及算价处理，cart续班推荐仍缺专用券转换和展示字段；已有预报名券页是独立链路，不代表推荐加购已支持。已在需求总入口下创建[产品确认稿](https://gaotuedu.feishu.cn/docx/RuYOdNkIfoP7fAxPlhecESgYnrc)并回读核验；独立加购区域、同科去重、券范围与数量规则待产品确认。无业务代码、配置或购物车数据变更。

## C 端购物车 sellerId 参数兼容（2026-10-22）

本轮仅修改后端 cart，分支 `feature-xuban-expand-exclude` → `test-gtbg-dev-1`。trace `1d5b5869-e5ad-49e7-ae46-b9a2a3cf2caf.0.3` 对应 `/cart/web/renewal/cart?renewalNumber=585960797778243584&includeBCart=false&sellerId=null&p_client=1`；登录用户 `7658127801`，调用链未进入 RenewalService。直连同泳道同路径已复现 HTTP200、`status=5/error_info=参数异常`；使用原请求的登录上下文重放仍为 status=5，而省略 sellerId 返回 status=0。Spring MVC 实际参数解析测试修复前唯一失败点为 `NumberFormatException: "null"`，其余9项通过。

| 改动 | 影响依据 | 验证项与预期 | 结果 |
|---|---|---|---|
| sellerId 字符串 null 兼容为未传 | 可选 Long 参数在 MVC 转换阶段失败 | MVC 真解析覆盖缺省、空串、null、合法数字；其他非法值与其他参数仍拒绝；部署后原请求成功 | cart `bdba9e90`，JDK8编译及10项MVC参数解析测试通过；流水线1309368部署dev-1，新pod Eureka UP，7项真接口验证通过 |

**当前有效结果**：新 pod `cart-gaotu100-com-57dc9dcb6c-6kgxd`，commit `bdba9e90`，Eureka UP。复用原 trace 的测试学员登录上下文，调用同一 GET `/web/renewal/cart`：sellerId 字符串 `null` / 省略 / 空串 / 数字 `90247`（仅验证数字绑定）均 `status=0` 且响应 data 完全一致，也与修复前省略 sellerId 的 data 基线一致（保留纯续与扩科两类推荐）；`sellerId=abc`、Long 越界、`renewalNumber=null` 均仍为 `status=5/参数异常`。7项均命中新pod。原请求修复后 trace：`cart_gaotu100_com.292.17926514768370006`。本轮为后端接口验证，未修改或验证前端页面。AICR分支暂无评审任务，不记为评审通过。

### C-04 student-center教师状态筛选（进行中）

按用户最新指定，仅在 `getCasUidByLoginInfo` 的账号查询候选流增加 `status=1` 筛选；`TeacherInfoDO` 补教师状态字段，`TeacherServiceImpl` 从 `baseInfo.status` 映射。该状态为教师启用状态（0初始化、1启用、2停用），不是员工在离职状态。已撤回直接返回LoginInfo.casUid的改动，保留教师号优先、账号查询兜底及异常逻辑。前端不修改。

验证范围：真实Feign/ACL/TeacherService链路覆盖停用记录排前、启用记录被选中，状态null/0/2/-1均不被选中、启用但CAS缺失时继续筛选、无教师记录保留业务异常。当前测试待执行；尚未提交、部署。

此改动不等于tangwen01根因修复：旧教师仍status1，单加教师状态筛选无法排除其对应离职员工。原推荐和预报名appInfo基线4个链接均seller_id=null，不能写成筛选后应自动变8645；需另行处理员工身份一致性。

### tangwen01 上游身份核验（2026-10-22，测试环境，仅定位）

原链接生成 trace `a835b653-db83-4fc0-979e-887ad1794848.0.0`（14:25:10）已核实：

| 环节 | 当前证据 |
|---|---|
| 登录身份 | `user_info` 为 accountId=90247、casUid=132658、employeeId=8645；同请求 `gaotu-cas-authorization.teacherNumber=7405394941575616` |
| 旧教师号来源 | 认证服务 `/feign/employee/getTeacherNumber` 入参 accountId=90247/teacherType=2，实际返回旧教师号7405394941575616；其部署源码release-3e1d691a只按教师status=1/type=2过滤后findFirst，没有限定当前employeeId/casUid |
| student-center | `RenewalContentCommonSupport#getCasUidByLoginInfo` 优先按登录teacherNumber取教师casUid，没有使用登录casUid；实时查询旧教师号得到casUid=120805、employeeId=2994 |
| teacher-basic | 原trace实际收到 `casUids=[120805]`；员工查询只含 `status=1`。实时全状态员工查询2994为status2（离职），8645为status1（在职）；但旧教师7405394941575616仍status1/type2，认证候选第一条。当前员工8645的教师号为572009172424521728，也为status1/type2，排在后面 |
| 映射对照 | base test真实 `/service/employee/queryId/byCasuid` 传 `[120805,132658]`，code0只返回 `132658→8645`；当前登录CAS映射正常 |
| promotion | `PersonalLinkDomainService#groupUrl2` 查询空列表后取空对象employeeId=null，直接拼出seller_id=null；Cronus传回、mweb转名 |

**结论**：这是“员工已离职但旧教师记录仍status1 + 认证层按账号/类型取首条、未限定当前员工 → student-center取到旧CAS → teacher-basic排除离职员工 → promotion未校验空值”的组合问题，不能记为当前登录CAS缺失员工映射。cart `bdba9e90` 仅完成消费端兼容；C-04按最新指示仅补教师启用状态筛选，不改变CAS身份取值优先级；这不能消除本例旧教师status1的问题。promotion及认证服务本轮不修改。认证选值源码定位：`GHArch/arch-general-apisix-auth` deployed commit `3e1d691a`，`EmployeeAppService#loadTeacherInfo`（437行附近）；本地只读检出 `/tmp/tangwen-auth-source`。查询教师列表trace `teacher-basic_gaotu100_com.583.17926545680258941`，查询员工状态trace `teacher-basic_gaotu100_com.284.17926543443153319`。定位阶段未改业务代码、配置或身份数据。数字90247仅是前轮参数绑定验证输入，不是该老师employeeId；其当前employeeId为8645。

## CASE-108 第1步最新实测（2026-10-22）

仅复验“本部门续班、退费全关”，结果通过；第2、3步本轮未执行。唐稳01 `tangwen01`（accountId `90247`）在普通大班花名册退费管控，选班“dcg-扩科排除-前置-五年级语文” `585960582537144320`，打开学员 `7658127801` 的 AI 分析抽屉，刷新后退费、续班均只显示“暂无数据”。浏览器真实 `POST /bgwApi/component/student-center/ai/moduleSwitch` 携带 `traffic-env: test-gtbg-dev-1`、`b_client: EES`，返回续班8项、退费7项全部 `false`。

操作为 student-data / TEST / default / application 的 `renewal.ai.dept.module.switch`、`refund.ai.dept.module.switch` 各临时新增 `"5253663827314688":[]`，保留其他部门；验证后仅移除本轮新增条目并发布，两个 key 已回读与操作前 JSON 一致，无遗留草稿，恢复后15项开关仍全关。页面保留在该学员 AI 分析的续班空态。现场结果已回填[在线 CASE-108](https://gaotuedu.feishu.cn/wiki/WpNuwpXLqi5JsskcmXFcwT2dnkg#doxcnEgNsxTuM01fHdbG5Q5FEEc)。

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

### AI 模块开关表接口（需求5，2026-10-12，dev-1，✅ 已验证）

**改动**：student-center 新增 **`POST ai/moduleSwitch`**（无入参，按登录老师判定）——`AiModuleSwitchQueryService#queryModuleSwitchTable` 下发 **13 key**：续班 `1,2,3,4,5,7,8,9`（「已续/未续跟进」合并单 key `5` = 后端模块 5‖6；`9=意向预测`）、退费 `service_suggestion/prediction/manual_reason/learning/tutoring`；`refund_root_cause`/`satisfaction` **不下发**；fail-open（部门未配 / 登录缺失 / 查询异常 / 缺 key → `true`）。数据接口兜底：`evaluateQuery` 用户反馈按 7 / 主管点评按 8、`managerEvaluate` 写按 8、`/roster/refund/analysis` 改 `service_suggestion`（关返 `{}`）、通用编辑入口 `StageFeedBackService.edit` 写 `manual_reason` 管辖列时拦、`ai/renewal/reason/detail` 按 reasonType 看 5/6、`ai/clazzUser/predictLevelReason` 续班 9 / 退费 prediction、`/user/feedback` 读写均按 7。student-data 枚举补 `RenewalAiModuleEnum.INTENTION_PREDICTION(9)` / `RefundAiModuleEnum.MANUAL_REASON("manual_reason")`。单测 `AiModuleSwitchQueryServiceTest` 5 条全过。

**提交/部署（`test-gtbg-dev-1`）**：student-center `7d74dbf8f` pipeline `1294629` → pod `student-center-96f6c6d5-bm7j5`(10.218.250.42) eureka UP；student-data `6ae6bc798` pipeline `1294630` → pod `student-data-7f4c876b6f-5bvgd`(10.218.239.23) eureka UP。分支 `feature-xuban-expand-exclude`。

| 例 | 调用 | 实测 |
|---|---|---|
| 开关表（真实入口，登录 177071，**首版 14 key**） | `POST /bgwApi/component/student-center/ai/moduleSwitch` | ✅ 返回 14 key：renewal `1..9` 全 `false`；refund `service_suggestion:true / prediction:true / manual_reason:false / learning:true / tutoring:true`；**无** refund_root_cause/satisfaction |
| student-data 原始判定对照 | `AiModuleSwitchService#queryModuleSwitch(1,177071,null)` / `(2,177071,null)` | ✅ renewal `{1..9:false}`（含新 `9`）、refund 含新 `manual_reason:false`，逐 key 一致 |
| fail-open（无登录态，桥直调 controller） | `AiCommonController#moduleSwitch`（直连 pod，无 web 上下文） | ✅ 全 `true` |

> ⚠️ **2026-10-12 变更**：续班「已续/未续跟进」5/6 合并为对外单 key `5` → 开关表由 **14 key 缩为 13 key**（续班 `1,2,3,4,5,7,8,9`）。**已复验**（student-center `40e5f24a7` → pod `10.218.248.27` eureka UP）：`POST /bgwApi/component/student-center/ai/moduleSwitch` 返回 renewal `{1,2,3,4,5,7,8,9}`（**无 6**）+ refund 5 项；`POST /roster/refund/edit`（bizName=`refundReason`）→ `code 8「手填退费原因模块未开放」`（写拦下沉到 `StageFeedBackService#edit` 后生效，覆盖 4 个通用 edit 入口）。

- 说明：TEST 现有部门配置未覆盖 177071（renewal）且 refund 未配 `manual_reason`，故显示 `false`，属配置预期。网关新路径未收录于自动路由表，需按 pathInfo `/component/student-center` 传 `route` 调（`invoke_http` 的 `route` 参数）。
- **`ai/clazzUser/predictLevelReason` 门控已完成**：release 已合入 `feature-predict-level-reason`，续班按 9 / 退费按 prediction，关闭返空对象。**意向预测写侧（含回溯）是「算法真表 → Sync job 落库 + 刷 ES」的数据管道，不挂模块门控（写全量）、不需要专门回溯**；旧链路（`SyncRenewalLiftSnapshotHandler` 等旧 xjob）已停用。

### 扩科老计划 `excludeMode` 回显兼容（2026-10-12，dev-1，✅ 已验证）

**改动**：product-server `ProcessService#convertNodeConfigVO`——B 端回显 `ext_config` 时，`excludeMode` 为空兜底为 `0`（无排除）；历史计划（`ext_config` 无该 key）打开即显示【无排除】、老师无需补选。推荐侧 `excludeMode != 1`（含 null）即不排除，行为同上线前。**不刷数**（该字段在 `node_config.ext_config` 的 JSON 里，非列）。

**提交/部署**：product-server `2d8ae7ccb`（`feature-xuban-expand-exclude`）；`test-gtbg-dev-1` product / product-task / product-b 三部署已发、新 pod eureka UP。

| 例 | 调用 | 实测 |
|---|---|---|
| 老计划回显兜底 | 桥调 `ProcessService#convertNodeConfigVO({number:1, type:6, extConfig:"{\"expandSubject\":true,\"forceBuy\":false}"})`（**不含 excludeMode**） | ✅ `extConfig.excludeMode = 0`（= 无排除）|

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

### 恢复跨班兜底 `get(0)` 后复测（2026-10-08，dev-3，✅ 已验证）

**改动**：product-server `92f1a5234` 把 `dealNotExistedComputeUserId` 老师对不上时的处理恢复为 master 原样（`subclazzDTOS.get(0)`），撤销 `2a3486754` 的「判未归属」。理由：计划级 3 规则前置后，走到兜底的基本只剩「userId 在同计划其它班」，候选即本人，`get(0)` 落本人班。

**部署**：product-task `product-task-gaotu100-com-5bffc79698-v2wzx`(10.218.248.136) / product-b `product-b-5d584cd7f4-jb2v8`(10.218.248.157)，均 eureka UP、commit `92f1a523`。

**入口**：product-b acl 桥 `QuestionnaireRecordService#dealCDSMsg(FormSubmitMqDTO)`（servlet 线程，Feign 可用；与 product-task 同一份 domain 代码），报文取 `questionnaire_record` id 366（990210）的 `origin_data` + `format_data`→`formatDataList`，改 id/userId/姓名/手机号。payload 生成脚本已删（临时文件）。

| 例 | 入参 | 改前（09-28 #14） | 实测 | 证据 |
|---|---|---|---|---|
| N1 | A 班链接（177071），`userId=20025`（只在 B 班，老师唐稳01），姓名/手机号无主 | record 366 computed=0（判未归属） | ✅ record 382 computed=**20025**、clazz=**B** `581200735551846400` | 明细 21930（user 20025 / B 班）；ES `36325046539911552-20025` status=3（该文档此前可能已为 3，不作为本例增量证据） |
| N3 | 同链接，无 userId，姓名/手机号无主 | — | ✅ record 383 computed=0、clazz=A | 广播 3 行 user_id=0（21931 A / 21932 C `578530888321613824` / 21933 B），同 group |

日志：TLS/SLS 按 traceId（`product-b.265.17914441157010002`）+ 关键字两次均未命中 `no account subclazz use default`，按 DB 效果判定。

**QA 用例需同步改**：49647 F-TC0003、49607「未归属 TC0002」预期改为「老师对不上时落候选（userId 本人）所在班，日志 `no account subclazz use default`」。

**本轮测试数据（TEST，保留）**：`questionnaire_record` 382/383（record_id 990301/990303）；`user_questionnaire_record` 21930–21933。

### 同计划姓名不 trim、精确匹配（2026-10-08，dev-3，✅ 已验证）

**用户定**：姓名不 trim，按原值精确匹配（与同班姓名规则一致）。

**根因**：只去掉 `NamePlanRuleService` 的 `trim()`（`56957130a`）不够——用户中心 `UserAclService#listByStudentName("123 ")` 本身忽略首尾空格，返回 100 个 `student_name='123'` 的学员（最小 20018、20019…）。故 `1e277cba4` 对返回结果再按原值 `studentName.equals(baseInfo.studentName)` 精确过滤。

**部署**：product-b `product-b-6647d8887-5lzlq`(10.218.249.69) / product-task `product-task-gaotu100-com-6cc999b6f5-t5d2t`(10.218.248.186)，均 eureka UP、commit `1e277cba`。入口同上（product-b 桥 `dealCDSMsg`，C 班链接 bindNumber `578693906093350912`，C 班无人叫 `123`，20018 在 A、20019 在 B）。

| 例 | 姓名 | 只去 trim（`56957130`） | 精确比对（`1e277cba`） |
|---|---|---|---|
| T1 尾空格 | `'123 '` | ❌ record 385 computed=20018（同计划姓名档命中，用户中心忽略空格） | ✅ record 387 computed=**0**（计划级不命中） |
| T2 对照 | `'123'` | record 386 computed=20018 | ✅ record 388 computed=20018（同计划姓名多命中取最小） |

**既有行为（未改）**：T1 不命中后走跨班兜底，兜底收集候选时**仍 trim**（master 原样），选到 20019 的 B 班 → 在 B 班重跑规则（原值 `'123 '`）仍不命中 → 记录 computed=0、clazz=B。

**本轮测试数据（TEST，保留）**：`questionnaire_record` 385–388（record_id 990311/990312/990321/990322）及其下游明细。

### 造数项目 + 真实 MQ 链路复测（2026-10-08，dev-3 product-task `1e277cba`，✅ 已验证）

**造数**：qa-data-agent-service 拉到 `origin/release`（`e45d5db`），用其已造环境：计划 `582291836641611776`、问卷 projectNumber `17085061328535721`；A `582291608895033344` / B `582291645278523392` / E `582291663569883136`（同绑 Q1，老师 90247）；S3 `7489636594`（测试学员三，只在 B）、S4 `7489636595`（只在 B）。执行：`python -m core.executor run-workflow submit_renewal_questionnaire`（依赖装在临时 venv）。

**泳道坑（重要）**：造数工具 `cds_form_save_data` 走 CDS（grayTest），产出的 MQ **不带泳道标，被 base 泳道（release 老代码）消费**；把 HTTP 头改成 `traffic-env: test-gtbg-dev-3` 也不传递到 MQ。dev-3 pod 内 `grep -c QuestionnaireRecordConsumer#consume` = 0 证实。→ 要测分支代码，取 CDS 产出的真实报文（`questionnaire_record.origin_data` + `format_data`→`formatDataList`），经 student-data dev-3 桥 `AiCommOnsMqProducer#sendOrderedMessage(String,String,String,String)` **四个字符串参数**重发到 `test_future_landingpage_form_submit`（gapm 透传泳道标，dev-3 隔离日志「当前env与消息env相同，消费消息」）。Object 重载那次 dev-3 收到但每秒重投、无业务日志、不落库（报文形态不对），别用。

| 例 | 入参（A 班链接） | 消费方 | 实测 | 结论 |
|---|---|---|---|---|
| D1 | S3 手机号，无 userId（真实 CDS 提交 24036） | base 老代码 | computed=S3、clazz=**B** | 老逻辑：班内不命中→跨班兜底落 S3 真实班 |
| D2 | S4 手机号，无 userId（真实 CDS 提交 24037） | base 老代码 | computed=S4、clazz=B | 同上 |
| M1 | 24037 报文重发（990332） | **dev-3** | computed=S4、clazz=**A**；明细只在 B（21944，同手机号原地更新）；ES `36396389295456896-7489636595` status=3 | 新逻辑：同计划手机号命中，记录挂链接班，扇出到真实班，A 无脏数据 |
| M2 | userId=S3、姓名手机号无主（990341） | dev-3 | computed=S3、clazz=B；明细 1 行 S3@B | 跨班兜底 `get(0)` 落本人班 |
| M3a | 姓名 `'测试学员三 '`（尾空格）（990342） | dev-3 | computed=0；广播 4 行 user_id=0 | 精确匹配，不 trim |
| M3b | 姓名 `'测试学员三'`（990343） | dev-3 | computed=S3、clazz=A；明细 S3@B | 同计划姓名命中 |
| M4 | 姓名手机号无主（990344） | dev-3 | computed=0；广播 4 行（A/B/E + 第 4 班 `582291712689377280`） | 未归属按问卷广播（既有逻辑） |

dev-3 pod `QuestionnaireRecordConsumer#consume` 计数 = 5（M1–M4 共 5 条）。

**注意**：TEST 库出现 record_id 990401（computed 20025）/990402（20018），16:26 创建，**不是本会话造的**，来源未知，未处理。

### 全量 diff 复核 + 桥方法单测 + 端到端抽测（2026-10-08，dev-3，✅）

**范围**：`feature-xuban-match-opt` 三仓 vs `origin/master`（product-server 11 文件 / student-data 12 / teacher-tool 10）。dev-3 现存 product-b `product-b-6647d8887-5lzlq`（commit `1e277cba`）、service/domain 同源。

**桥方法单测**（`com.gaotu.product.service.renewal.questionnaire.ComputeUserService#compute`，product-b 桥，`traffic-env: test-gtbg-dev-3`；plan = `[578530883890331648]`）：

| 例 | 入参要点 | 期望 | 实测 |
|---|---|---|---|
| P1 | 假班 + plan + 姓名`123` | 计划级姓名 → 20018 | ✅ |
| P2 | 假班 + 姓名`123`（无 plan） | 不命中 | ✅ `[]` |
| P3 | 链接班 + plan + 姓名`123` | 20018 | ✅ |
| P4 | 假班 + plan + 手机号`12600000018` | 计划级手机号 → 20018 | ✅ |
| P5 | B班 + plan + 姓名`123` | 班内姓名 → 20019 | ✅ |
| P6 | B班 + 手机号`12600000018` + 姓名`123` | **计划手机号(20018) 先于班内姓名(20019)** | ✅ 20018 |
| P7 | B班 + originUserId `20019` | originUser 最高优先 | ✅ 20019 |
| P8 | 假班 + plan + 姓名`无此人己` | 不命中 | ✅ `[]` |
| P10 | 假班 + plan + 姓名`123` | 多命中取 ID 最小 | ✅ 20018 |

**端到端抽测**（product-b 桥 `QuestionnaireRecordService#dealCDSMsg(FormSubmitMqDTO)`，A 链接 bindNumber `578693906093350912`）：

| 例 | 入参 | 实测（DB `questionnaire_record`） |
|---|---|---|
| E1 跨班兜底 get(0) | userId=20025（只在 B）、姓名/手机号无主 | record 990401 computed=**20025**、clazz=**B**(581200735551846400) ✅ |
| E2 计划级姓名跨班 | userId 空、姓名`123` | record 990402 computed=**20018**、clazz=**链接班**(578530888321613824) ✅ |

**其它桥方法**：teacher-tool `QuestionnaireFeignController#syncTransferQuestionnaire` 同班 old=new → `data:false 无需同步` ✅、缺 projectNumber → `参数异常` ✅；student-data `QuestionnaireAclService#queryQuestionnaireMatchResultElseException(B, 578532432171743232)` → `{number:578690742470393856, bizId:17323095168254394}` ✅。

**本轮新增测试数据（TEST，保留）**：`questionnaire_record` record_id 990401/990402（number `583779222907160576` / `583779224836540416`）及其下游明细/花名册。

**coverage 说明**：本次未在 banshan 平台重跑 QA 用例 49607（MCP 未挂载）；23 条上次 2026-09-28 结论仍有效，本次仅对 2026-10-08 改动项（兜底 get(0)、姓名精确匹配、7 档顺序/多命中）做桥复测。

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

## 调课同步「提交时间/预报名科目」修复验证（2026-10-10，test 泳道，✅）

改动：student-data `af1ca55d1`（feature-xuban-match-opt）——
① consumer `tag` 改 Apollo 可配 `renewal.questionnaire.transfer.event.tags`，默认 `TRANSFER_TOUCH_EVENT||TRANSFER_SUCCESS_EVENT`；
② 调课时 `RenewalIntentInfoService#copyIntentToClazz` 把原班 `renewal_intent_info` 复制到新班（幂等）；
③ `RenewalQuestionnaireTransferSyncService#writeCommitStatus` 一并回写意向派生字段。
部署：test（envInfoId 2）pod `student-data-5b94766b4f-q6hjc`(10.255.165.86) eureka UP。

真实售后调课 A→B：售后单 `36487077547475328`（10-08 已提交、卡待审批）经 `bpm_agree`（审批人 fuxing，BPM `7fd7d22f-c301-11f1-80fb-00163e7fd82d`）通过 → A 单 `431058595531457534` order_status=6、B 新单 `431213780216578558` status=2、学员进 B 辅导班 `36396389295456896`。

ES 花名册 `ads_large_subclazz_user_index_v3` 文档 `36396389295456896-7489640475`：

| 字段 | 修复前 | 修复后 |
|---|---|---|
| renewalQuestionnaireStatus | 3 | 3 ✅ |
| renewalQuestionnaireSubmitTime | 缺失 | 1791454640000 ✅ |
| preRegistrationIntentKey | 0 | 1 ✅ |
| preRegistrationIntentSubjectKey | 缺失 | [1] ✅（花名册页「问卷预报名科目」用的就是它） |
| subjectExpansionIntentKey | 缺失 | [1] ✅ |
| referralIntentKey | 缺失 | -1 ✅ |
| preRegistrationSubject | [] | [1] ✅（复用 `ClazzDataQueryServiceV2` 补学年/学期/年级入参后算出） |

消费日志：`RenewalQuestionnaireTransferSyncService | writeCommitStatus | ... submitTime: 1791454640000, fields: [subjectExpansionIntentKey, renewalQuestionnaireStatus, preRegistrationIntentKey, preRegistrationIntentSubjectKey, renewalQuestionnaireSubmitTime, referralIntentKey, preRegistrationSubject]`。

`preRegistrationSubject` 曾算空：`StudyingSubjectDataQueryServiceV2`（weight=fourth）依赖 dataMap 里的 `schoolYearId`/`schoolTermId`/`courseGrades`。已复用 `ClazzDataQueryServiceV2`（weight=third，`getFields` 含这三个）——把这 3 个字段名加进 `QUERY_FIELD_NAMES`，由它从「班级→课程」补出，再算出 `[1]`（与同班正常学员 `7489636595` 一致）。

**并发/幂等**：consumer 默认只订 `TRANSFER_SUCCESS_EVENT`（每笔调课成功只发一次），避免 TOUCH/SUCCESS 双事件并发；`copyIntentToClazz` 对并发重复插入捕获 `DuplicateKeyException`（表有唯一键 `uq_number(clazz_number,user_id)`）按已存在跳过。

**造数坑（发售后事件）**：acl 桥对这个方法的重载解析不稳——
① `[topic, [tag], {obj}]` 有时被匹配成 `(String,String,String)` → tag 变 `[TAG]`(方括号)、body 变 `Map.toString()`，tag 过滤收不到；
② `[topic, "TAG", "<json>"]` 有时被匹配成 `(String,List,Object)` → body 又被 `JSON.toJSONString` 一次，消费端 `expect {, actual string` 反序列化失败；
**③ 稳定写法 = 4 个字符串参数 `[topic, "TRANSFER_SUCCESS_EVENT", "<json>", <nowMs>]`**（命中 `(String,String,String,long)`，body 原样发）。
④ 最稳：直接调 `com.gaotu.arch.ons.OnsMqTemplate#send(topic, tag, "<json>")`（3 参 String 唯一签名，body 原样发；桥会 fan-out 到同名 bean，发的是同一 topic，可当并发冒烟用）。

**MQ 幂等（2026-10-10）**：consumer 以 `(userId,原班,新班)` 抢 Redis SETNX（`renewal.questionnaire.transfer.idempotent.seconds`，代码默认 **5s**，`296cf844` 从 10s 下调到 5s 以 < 首次重试 ~10s）去重；抢到才处理，**失败释放标记**交 MQ 重试（避免重试被当重复漏同步），Redis 异常 fail-open。实测：并发发同一事件 → 1 条 `writeCommitStatus` + 1 条 `duplicate event, skip`。

## 提测 P0 用例核查 + base `test` 泳道复验（2026-10-10，✅ 部分已验证）

**背景**：用户提测前核查飞书《提测 P0 用例》doc（node `VvGjwKFO3iIJNtkUE8kcEkPdnCd`），该 doc 声明来源 = banshan **49607 / record 70678（23 条）**，被测泳道 `test-gtbg-dev-3`。要求下订单/调课调班改在 base `test` 泳道复验。

### 用例基线（重点）

- banshan **49607** 已被标注停用并入 **49647「[V1.0]续班问卷匹配优化」**。49607/70678 = totalCount 24 / success 23（doc 头「23/23」不准，第 24 项是停用说明节点）。
- **49647 才是现行维护集**：用例节点 70，功能用例 record **70798 = 77 项 / 已执行 32 / 2 不执行（B-TC0007/0008 撞号）**。已通过 32：G001/G006/G008；B-TC0001–0006、0009–0014；E-TC0002、E-TC0008；F-TC0001–0007。**未执行约 36**：模块 A（9）、C（7）、D（8）全未跑，E 缺 TC0001/0003–0007/0009–0011，G 缺 G002/G003/G005/G007/G009/G010。
- 提测编排 23716 挂在 **49607**（70678.planId=23716）；49647 三个 record（70797/70798/70799）**无 planId**。→ 需向 QA(tangwen01) 确认提测到底用哪套；建议迁 49647。

### base `test` 泳道现状（已验证）

| 项 | 值 |
|---|---|
| 部署 | student-data `296cf844`（pod student-data-597bf68f9f-nrgd4, 10.255.177.218）· teacher-tool `9c98a14a` · product-task `35f2a80e`，均 eureka UP、分支 `feature-xuban-match-opt` |
| Apollo student-data TEST | `renewal.questionnaire.transfer.switch=true`；`renewal.questionnaire.transfer.event.tags` **未配**（默认只订 `TRANSFER_SUCCESS_EVENT`）；`renewal.questionnaire.transfer.idempotent.seconds` 未配（默认 5s） |
| 环境数据 | 计划 `582291836641611776`（4 前置课：A/B/E→Q1 `583732612560865280`、D→Q2 `583916770547484672`）；Q1 projectNumber `17085061328535721` |

**直接调同步逻辑 ✅**：桥直调 `RenewalQuestionnaireTransferSyncService#syncAfterTransfer(7489640566, A=582291608895033344, B=582291645278523392)` → B 新增明细 `id=22087`（同 group `583943296376877056`、`create_time=2026-10-10 14:34:42`）→ **同步逻辑 + 明细复制 OK**。

**合成 MQ 调课事件 ❌ 未被消费**：桥 `FuwuOnsMqProducer#sendNormalMessage("gaotu_after_sale_event_test","TRANSFER_SUCCESS_EVENT","<json>")`（3 字符串重载）发 2 次（user 7489640566、7569545505，A→B）→ 均 `result:true`，但 25s+ 后 B **无新增明细**、student-data app/error 日志均无 `RenewalQuestionnaireTransferConsumer` 记录。对照组：同为 A→B 的真实售后/直调（user 7489640475 → B 明细 22082、user 7489640566 直调 → 22087）均成功。→ **与 data-agent playbook「调课自动同步在测试环境 MQ 断点」一致：E/G 模块在 base test 应走真实售后（提交+BPM 审批），合成事件注入不可靠**（旧 doc §四「sendNormalMessage 不带泳道也行」在 base test 不成立）。

### 文档自身需订正项（对照 PRD + 现实现）

1. **调课事件 tag 已变**：doc §四/§7 教发 `TRANSFER_TOUCH_EVENT`，现默认只订 `TRANSFER_SUCCESS_EVENT`（`af1ca55d1`/`48ff645e2`）→ 按 doc 发 TOUCH 不会被消费；且 doc 的 acl 桥发法（`[topic,[tags],{obj}]`）与 `verify.md` 的稳定写法（3 字符串 + body JSON 字符串）冲突。
2. **F-TC0003 预期过时**：`92f1a5234` 已恢复跨班兜底 `get(0)`，「找不到辅导老师→判未归属」不再成立（应为「老师对不上→落候选本人班；无任何候选→未归属」）。49647 F-TC0003 用例文字未改（平台仍标通过）。
3. **数据污染**：Q1（`17085061328535721`）是公共模板，别人也在用（data-agent 记录：A 班明细 S2 有 4 条、广播 13 条），**断言条数的用例（G001/C 模块）不可靠**，应换 `new-questionnaire` 复制的专属问卷。Q1 实际表单 formNumber=`16637758182064207`（姓名 `...208`/手机号 `...209`），用旧 formNumber 造数会让明细页手机号显示「-」。
4. **新增代码未进用例**：2026-10-10 的意向派生字段回写（`preRegistrationIntent*`/提交时间/预报名科目）、`copyIntentToClazz`、tag Apollo 可配、Redis 幂等，doc 23 条均未覆盖（verify.md 上一节已单独验证）。

### 双用例集实跑（2026-10-10，base test，✅ 部分 / ⛔ 被环境变更打断）

**入口**：product-b 桥 `POST /bgwApi/product-b/b/test/acl/compare/service`，方法 `QuestionnaireRecordService#dealCDSMsg(FormSubmitMqDTO)`，头 `traffic-env: test`；Q1 表单 formNumber `16637758182064207`（姓名 `...208`/手机号 `...209`）、A 链接 bindNumber `583732690300192768`、B `583732690870618112`。

**已通过（record.computed + 明细 `user_questionnaire_record` + ES `eesServe/ads_large_subclazz_user_index_v3` 三处一致）**：

| 用例 | record_id | 实测 computed |
|---|---|---|
| 49607 规则TC0001 L0 userId | 995001 | S1 `7569541631` |
| 49607 规则TC0002 L1 同班手机号 | 995002 | S2 `7489636593` |
| 49607 规则TC0003 L2 同计划手机号 | 995003 | S3 `7489636594`（clazz=A 链接班） |
| 49607 规则TC0004 L3 同班姓名 | 995004 | S2 |
| 49607 规则TC0005 L4 同计划姓名 | 995005 | S3 |
| 49607 规则TC0006 L5 同班亲属号 | 995008 | S2 |
| 49607 规则TC0007 L6 同计划亲属号 | 995009 | S3 |
| 49607 规则TC0008 手机号>姓名优先级 | 995006 | S2 |
| 49607 规则TC0009 计划隔离 | 995007 | 0 |
| 49647 B-TC0002 uid vs mobile | 995010 | S1 |
| 49647 B-TC0003 uid vs name | 995011 | S1 |
| 49647 B-TC0004 uid 无效降级 | 995012 | S2 |
| 49647 B-TC0006 手机号负向（少/多/+86/空格） | 995013–995016 | 均 0 |
| 49647 B-TC0012 姓名负向（尾空格/错字/全角） | 995019–995021 | 均 0 |
| 49647 B-TC0014 报名号先于亲属号 | 995022 | S5 `7569543424` |
| 49647 A-TC0006 跨班链接仅落本人班 | 995025 | S1（clazz=B 链接班、明细 fan-out A） |
| 49647 C-TC0001 不同手机号都展示 | 995026/995027 | S5（2 条明细） |
| 49647 C-TC0003 同手机号取最新 | 995028 | S5（原地更新） |
| 49647 未归属造数 | 995030 | 0（广播 3 行 user_id=0） |
| 49607 TC0010 同名>20 截断 | 995023 | 0（`同名边界测试`） |

ES 实证（例）：`36396360685978240-7569543424`、`36396360685978240-7489636593` 等 `renewalQuestionnaireStatus=3`、`renewalQuestionnaireSubmitTime=1791462000000`（=本次桥提交时间）。

**订正（env 漂移）**：① 49607 TC0010 的 21 同名目标 ID 已变（现命中 `7569545689`，非文档写的 `7489640540`）——机制（多命中取最小 ID/limit 截断）成立，具体 ID 以实测为准；② 49647 A-TC0007 原用 S6 `7569543442` 做「不在读广播」，但 S6 现已在大班在读（有 A/B 明细）→ 前提不成立，需换真正不在读学员。

**⛔ 环境变更打断**：实跑中途 base test **student-data 被重新部署成 `release`（`b6a3c0aa`）**——`origin/release` **不含** `RenewalQuestionnaireTransferSyncService/Consumer`（feature 未合 release），故 `syncAfterTransfer` 桥调报「未找到实现类」，**调课同步（49607 调课模块 + 49647 E/G + F 依赖）在 base test 全部跑不了**。同期 teacher-tool/product-task/product-b 仍是 feature（`9c98a14a`/`35f2a80e`），匹配类用例不受影响。→ 要在 base test 继续跑调课同步，需把 student-data 重新部署 feature-xuban-match-opt（或改走仍带 feature 的甬道）。

**已标记（banshan 落库）**：
- 49607「未归属与重试」TC0002（node `cd2ywnrv7hys`）→ **阻塞**（预期「判未归属」与 `92f1a5234` 恢复的「落候选本人班」实现不符）。
- 49647 `F-TC0003`（node `ff25f9e364984e07`）→ **阻塞**（同上）。
- record 读数：70798 = 32 通过 / 1 阻塞 / 2 不执行；70678 = 23→22 通过 / 1 阻塞。

### 反合 release + 重发后复验（2026-10-10，base test）

**动作**：student-data 反合 `origin/release`（`ea0efd8df`，23 commit、无冲突）并 push；把 **student-data（`ea0efd8d`）与 student-data-dws（`ea0efd8d`）** 都重发到 base test（envInfoId 2），均 eureka UP（此前两服务被误发成 `release` `b6a3c0aa`，`origin/release` 不含 transfer sync 代码）。

**复验通过**：① 匹配 record 计算正确（product-b/task feature 未动）；② 桥调 `syncAfterTransfer(7569545505,A,B)` 成功，B 新增明细 `22130`（同 group、新 uniqueBizId），幂等（重调不新增，`7634383219` B 仍 1 条）；③ teacher-tool `POST /feign/questionnaire/user/transfer/sync`：old==new→`data:false 无需同步`、缺 projectNumber→`code:400 参数异常`。

**✅ 更正（2026-10-10）：链路正常，之前判错**——① 明细「没出现」其实是**原地更新**（同手机号取最新）：真实 CDS 提交后 S5 明细 `22028.update_time=17:29:55` = 提交时间；② groupId 已按泳道隔离（ONS `ConsoleTopicSubDetail`：base test `GID_teacher_tool_questionnaire_finish_test_group_test`、dev-3 `..._test-gtbg-dev-3`），**各泳道独立组、不互抢**；base test group 确在消费（`ConsoleConsumerProgress`：clientId `10.255.179.34`、accumulate=0）。③ 之前「被 test-eco-2 pod 抢」是误判。**排查方法**：轻舟 log `queryStr=<topic>` 看 `MqIsolationUtil` 日志 + ONS 控制台查 group/位点——别猜、别进容器。**总开关 `mqIsolation` 保持默认**（代码 `MqIsolationUtil.msgIsolationByConfig`：topic 在例外列表用其 `envIsolation`，不在才回落总开关）。

---

## 代码规范审查·必改验证（2026-10-12/13，`test-gtbg-dev-1` 泳道，✅）

**验证方法**：临时把 `student-data / TEST / application / refund.ai.dept.module.switch` 配成**不命中登录部门**（`{"__qa_verify_nomatch__":["learning"]}`）→ 退费模块对该部门全关；**必须带 `traffic-env: test-gtbg-dev-1` 头**，否则 student-center→student-data 的 Feign 落 base test、拿不到 AI 代码会 fail-open，门控不触发。**验完已发布还原并读回确认**。

**入口**：`POST https://test-fuwu.baijia.com/bgwApi/component/student-center/roster/refund/{edit,course}`（route `/component/student-center`）。

| 项 | 调用 | 实际返回 | 判定 |
|---|---|---|---|
| Q-06 | `edit {bizName:"refundReason"}` | `code:8 "手填退费原因模块未开放"` | ✅ 退费原因写仍被门控拦 |
| Q-06 | `edit {bizName:"__qa_probe_not_refund__"}` | `code:0, data:[]` | ✅ **非退费 bizName 不再被误拦**（本次修复点） |
| Q-07 | `course` | `code:0, data:{}` | ✅ **空对象，非 null**（防旧版前端白屏） |

> 同轮部署：student-center `5ba12b10`、cart `3594af88`、product-server `9a9b4350`，均 dev-1/dev-3 eureka UP。
> Q-08/Q-09（cart pom）、Q-10（cache key）为构建/正确性级，以「编译通过 + 部署 eureka UP」为验证。

---

## 第二批收口（2026-10-14 · 扩科在读补学年学期 + AI 门控漏网，✅ 单测/编译验证，环境待验）

**对照 PRD 逐条核 diff 后修 3 项**（PRD 原文：「在读小班课范围：与当前课程**相同学年+学期**、且授课模式为小班课、且上课形式为线上、且不含赠课、且订单未全部退款、且专题/系列课、且非纯预售、且非成人」）。

### 1. 扩科「推荐排除」在读补「与当前课程相同学年+学期」（真缺陷）

- **原问题**：`RenewalInReadSubjectService` 只按授课模式取对方模式在读，**没按学年学期过滤**（DAO `listByUserId`/`listClazzInfo` 只 `is_del=0`）→ 会把学员**其它学期**的对方模式在读学科也当「在读」，**过度排除推荐**。PROD `dws_small_clazz_user_subject` 实测确有跨 `school_term_id` 的 `is_del=0` 行。
- **修复**：cart 透出当前（前置）课程 `schoolYearId/schoolTermId`（`CourseDTO` 原未映射 course-center `CourseVO` 的这两个字段，已补）；student-data 按学年+学期过滤。
- **学期格式坑**：课程学期是 **OES(C/X/Q/D)**；**大班在读表即 OES、小班在读表是 CES(1/2/3/4)**（写入侧 `OdsSmallRenewalSubjectSyncService`/`SmallClazzUserManualService` 做了 `getCesValueByOes` 转换）。故**大班路径查小班表时需把课程学期 OES→CES**。
- **降级**：学年/学期缺失、或 OES 无法映射 CES（复合学期如 `CU`）时**保守返回空（不排除）**——宁少排除、不误排。
- **验证**：`mvn8` 编译通过；单测 student-data `RenewalInReadSubjectServiceTest` **13/13**（含跨学年/学期剔除、OES→CES 转换、缺失降级、复合学期不排除）、cart `ExpandSubjectRecommendServiceTest` **7/7** 全过。**环境 E2E 待 dev-1 补**（需造「当前课程 2026 秋 + 学员在对方模式有 2025 学期历史在读」样本，验跨学期行被剔除）。
- 提交：student-data `f1817c92d` / cart `7794a329`。

### 2. AI 门控漏网：`/roster/refund/reason` 按 `manual_reason` 门控

- `/roster/refund/reason` 返回手填退费原因（`refund_intent_info.refund_reason`）= `manual_reason` 模块的展示数据，**原未门控** → 关闭模块后前端隐藏但接口仍返。已补门控，关闭返**空对象**（非 null，防旧前端白屏），与写拦（`StageFeedBackService.edit`）口径一致。提交 student-center `479817691`。

### 3. AI 分析侧性能：灰度未开始时短路部门解析

- 原实现每条 AI 分析事件都 `resolveAssistantOrgPaths`（含 `listMainPostStaffByAccountIds` ACL）；新增 `isRenewalGrayStarted/isRefundGrayStarted`，5 处分析侧调用点（圈选实时/历史、续班归因、退费归因、退费预测）在**部门配置为空时短路**（结果仍全放开）。提交 student-data `f1817c92d`。

### 仍待确认（未擅自动）

| # | 事项 | 影响 |
|---|---|---|
| a | `refund_root_cause` 门控 `/reasonType` 但它**不在开关表下发名单** → 灰度开始后该接口恒返 `[]` | 是否随前端基线分支下线？（Q-03） |
| b | `ai/clazzUser/levelReasonAndHistory`（分层原因/变化）**未门控** | 属另一需求 `feature-predict-level-reason`？ |
| c | `RefundPredictionService` 对「退费风险升高通知」按 `prediction` 门控 | 「写侧不挂门控」是否含通知？ |
| d | 复合学期（`CU/QD/QU/CD/X-Q`）课程的对方模式在读**匹配不到 → 不排除** | 是否需展开复合学期？ |
| e | 分析侧「已配置但解析不到老师部门 → false」与展示侧 fail-open 不一致（2026-09-24 已定，非 bug） | 双隐藏是否可接受 |

### 清理

- cart / product-server 误提交的 `.run/bridge-remote-*.run.xml`（含 pod IP）移出仓库并 gitignore（cart `7794a329` / product-server `c1b9225ef`）；订正 `filterByOperationMode` 注释、`AiModuleSwitchClient` javadoc。

### 追加修复 + 环境执行（2026-10-14 晚，`test-gtbg-dev-1`，✅）

**再修 3 项**（均编译+部署+E2E）：
- **`/roster/refund/reason` 挂 `manual_reason` 门控**（student-center `479817691`）：关闭返空对象。
- **`ai/clazzUser/levelReasonAndHistory` 挂续班模块 9 门控**（student-center `dfe9e0495`，pod `dfe9e049`）：关闭返空对象。
- **AI 分析侧灰度未开始时短路部门解析**（student-data `f1817c92d`）。

**执行记录**（真实 HTTP / 桥，dev-1）：

| # | 用例 | 入参 | 实测 | 判定 |
|---|---|---|---|---|
| EX-1 | 扩科排除·服务级·跨学期剔除 | `listOtherModeInReadSubjects(20002,1,2026,"X")` | `[4]`（仅 2026 夏季） | ✅ |
| EX-2 | 同上·另一学期 | `(20002,1,2025,"C")` | `[1,2]`（仅 2025 春季） | ✅ |
| EX-3 | 同上·无该学期 | `(20002,1,2026,"Q")` | `[]` | ✅ |
| EX-4 | 同上·学年学期缺失降级 | `(20002,1,null,null)` | `[]`（不排除） | ✅ |
| EX-5 | **扩科排除·cart 端到端·学期 X** | `recommend(20002,{excludeMode:1,...},{course.schoolYearId:2026,schoolTermId:"X"},[])` | 只返 subject 9（**4 被排**） | ✅ |
| EX-6 | **扩科排除·cart 端到端·学期 Q** | 同上但 `schoolTermId:"Q"` | 4、9 都返（**不排**） | ✅ |
| EX-7 | 扩科 B 端 | `recommendProductList(579985778241837056,20002)` | 只剩语文（同既有记录） | ✅ |
| AI-1 | 开关表 | `POST ai/moduleSwitch` | renewal `1,2,3,4,5,7,8,9`（无6）+ refund 5 项（无 refund_root_cause/satisfaction） | ✅ |
| AI-2 | `/roster/refund/reason` 负向（有数据行 `subclazz 31298462823089024/user 7463487951`，manual_reason 关） | 真实 HTTP | `{}`（有数据仍被拦） | ✅ |
| AI-3 | 同上·正对照（临时给 177071 部门加 `manual_reason`） | 真实 HTTP | 返回 `refundReason:"家长反馈…", source:2` | ✅ |
| AI-4 | `levelReasonAndHistory` 负向（模块 9 关） | 真实 HTTP | `{levelReason:"", changeHistoryList 缺省}`（gate） | ✅ |
| AI-5 | 同上·正对照（临时给 177071 部门加模块 9） | 真实 HTTP | `{levelReason:"", changeHistoryList:[]}`（服务跑） | ✅ |

- **Apollo 临时改动已全部还原并读回确认**：`renewal.ai.dept.module.switch` 回 `{"97349606689168923":[1..8]}`、`refund.ai.dept.module.switch` 回原值；`moduleSwitch` 复核 renewal `9:false`、refund `manual_reason:false`。
- **部署**：student-data `f1817c92`(10.218.250.204) / cart `7794a329`(10.218.249.39) / student-center `dfe9e049`(10.218.250.181)，均 eureka UP。

**已知未覆盖**：扩科 cart 端到端用的是桥调构造 context（真实页面 C 端链路未点）；复合学期（P-01）降级分支无线下/复合样本，仅单测覆盖。

## 2026-10-20 · 扩科+AI P0 用例造数（CASE-001 主流程，`test-gtbg-dev-1`，✅）

用 qa-data-agent-service（release `44806a5`）跑通扩科主流程造数，产物（可直接使用）：
- 学员 mobile `13900801001` / userId `7658127801`
- 小班在读数学：clazz `585960405711579136`、order `432168261541953856`（二讲 弓雪萌）
- 大班前置课（五年级语文 2026C）：course `585960577856301056`、clazz `585960582537144320`、subclazz `36622538973250048`、order `432168408644583744`
- 大班后置课（六年级语文 2026X）：course `585960751831836672`
- 大班续班计划 `585960797778243584`（type=1，C/2026→X/2026，已绑前置+后置+已发布）
- **待手工**：B 端给该计划配扩科节点（扩科推荐=是、推荐排除=排除不同授课模式在读、导入六年级数学/英语）
- P0 用例文档（10 条，data-agent 可执行）：[[links]]《扩科推荐+AI 模块配置化 提测 P0 用例》 https://gaotuedu.feishu.cn/wiki/WpNuwpXLqi5JsskcmXFcwT2dnkg
- 坑：data-agent 工作流内层 tool 的 cookie 不会被 run_cases 自动注入（`run_cases` 只对单 tool 注入），跑工作流需显式传 `cookie`；`create_small_clazz_product_with_dist` 需传 `teachDepartmentCode=100001`（默认 100003 报「所选学部已禁用」）；`batch_create_order.userId`、`bind_pre_course`/`add_renew_master_course_relation`/`release_renew_master` 的参数须传 **integer**（传字符串触发 guardrail）。
- **补齐（10 条用例全量就绪）**：计划 `585960797778243584` 已配扩科节点 `585963455412989952`（`extConfig.excludeMode=1`）+ 推荐节点 `585963455448641536`（flow `585963455406698496`）；扩科商品 `renewal_expand_subject_recommend`：grade16/subject1数学→`585963384338507776`、subject4英语→`585963400792762368`（对应大班课 `585963384338507776`/`585963400792762368`）。CASE-003 跨学年行：`dws_small_clazz_user_subject` 插 `(7658127801, 585963400792762368, subj 4 英语, 2025)` → 现该学员小班在读 = 2026{数学1,语文5} + 2025{英语4}，验证「按当前课程学年过滤」。AI 组（006~010）按 Apollo 开关：`renewal/refund.ai.dept.module.switch` 空=全放开、配部门=未命中全关；`refund.reason.root-cause.enable` 默认 true（跑）、配 false 跳过。全量明细见飞书 [[links]]《扩科推荐+AI 模块配置化 提测 P0 用例》「全量补齐结果」段。
- **实跑验证（2026-10-20）**：CASE-001 `cart RenewalService#getRenewalDetail(7658127801,585960797778243584)`（excludeMode=1）→ 扩科只出**英语**、**数学被排除** ✅；CASE-002 改 excludeMode=0 → 数学恢复 ✅；CASE-003 `listOtherModeInReadSubjects(7658127801,1,2026,"C")=[1,5]` ✅；CASE-006/007 `ai/moduleSwitch`（弓雪萌命中部门→全 true；tangwen01 未命中→全 false）✅。**关键发现：cart 的「当前课程」取后置课学年+学期（本例 X/夏），在读行学期须与之一致才被算在读并排除**（已把数学在读行 term 设为 2 对齐）。CASE-008/009 实跑（2026-10-20）：Apollo 把 `refund.ai.dept.module.switch` 配成未命中登录部门 → `/roster/refund/{reason,analysis,course}`→`{}`、`{stage,intent/record}`→`[]`（关闭返空、非 null）；配 dept `5253663827314688` 去掉 `satisfaction` → 门控 `satisfaction=false`/`learning=true`，触发 `refreshReasoning(585960582537144320,36622538973250048,[7658127801])` → `ees_data.ai_refund_analysis_process_log`（process_id `refresh292983528073741312`）5 模块均有记录 → 关单模块未终止流程、END 照跑 ✅。Apollo 已还原读回。CASE-010 需本需求根因开关代码部署后才能跑。

## 2026-10-20 · 扩科排除「当前课程」口径问题（C-01，疑似 bug，阻塞 CASE-001）

**PRD**（扩科推荐优化 wiki）：当前课程（**续班花名册选择的班级**）是大班课 → 排除在读小班课学科，在读范围「**与当前课程相同学年+学期**」。即口径 = 花名册选的那个班 = **前置课**。

**实测**：本例 前置课=五年级语文 **2026 C(春)**、后置课=六年级语文 **2026 X(夏)**。cart `RenewalService#getRenewalDetail(7658127801,585960797778243584)` 实际按 **X(夏)** 过滤：
- 小班在读数学 = 春(`1`) → cart **不排除**数学（与 PRD 期望相反）
- 小班在读数学 = 夏(`2`) → cart 才排除数学
- 直调 `listOtherModeInReadSubjects`：`(...,"C")→[5]`、`(...,"X")→[1]`

→ cart 取的是**后置课**学年学期，与 PRD「花名册选的班（前置课）」不符，**疑似 bug**（`getLargeClassRenewalDetail` 里 `renewalClazzNumbers→courseDTOMap` 疑取到后置课）。**待开发核**。数据已按 PRD 改回春(`1`)。

**✅ 已修复 + 部署验证（2026-10-20，C-01 完成）**：cart `RenewalService` 新增 `resolveCurrentPreCourse(renewalPreCourseDTO, recommendContext)`——取续班计划前置课课程号 `renewalPreCourseDTO.getCourseNumbers()` → `recommendContext.getCourseDTO(前置课号)` 的 `schoolYearId/schoolTermId`，传入 `ExpandSubjectRecommendService.recommend(..., CourseDTO currentCourse, ...)`（大班重载新增入参，删掉原从后置 map 取学年的 `resolveCurrentCourse(Map)`）；**后置课仍用于「后置课程年级」匹配**（未动）；小班路径本就取前置课、未改。提交 cart **`4724b384`**，`mvn8` 编译通过，部署 `test-gtbg-dev-1` eureka UP（pod `cart-gaotu100-com-6cf4cf8b4d-tfspw`）。**验证**：数学在读=春 → cart 扩科**数学被排除** ✅；excludeMode=0 → 数学恢复 ✅。

## Showcase 清单（test · test-gtbg-dev-1）

**学员 `13900801001` / userId `7658127801`；计划 `585960797778243584`**（前置 2026C → 目标 2026X；扩科节点 `585963455412989952`）。

| 场景（用例） | 班级 clazzNumber | 班级 bizId | 学员/账号 | 预期 |
|---|---|---|---|---|
| 扩科排除·主（CASE-001/011） | 大班前置五年级语文 `585960582537144320` | `15YW26CCRI11001` | `7658127801` | 扩科只出英语、数学被排除 |
| 纯续/扩科商品 | 后置语文 `585960755422160896`；数学 `585963387758962688`；英语 `585963404555053056` | `16YW26X6IM11001` / `16SX26XN1011001` / `16YY26X7IK11001` | `7658127801` | — |
| 扩科无排除·对照（CASE-002） | 同上 | 同上 | `7658127801` | 数学+英语都在 |
| 小班在读（被排除对象） | 小班 `585960405711579136`（数学, 2026春） | —（花名册可见） | `7658127801` | 支撑排除数学 |
| AI 开关表·命中（CASE-006/007） | — | — | 登录 `gongxuemeng`（弓雪萌 177071） | renewal 8key/refund 5key 全 true |
| AI 开关表·未命中 | — | — | 登录 `tangwen01` | 全 false |
| AI 展示侧关模块（CASE-008） | clazz `585960582537144320` / subclazz `36622538973250048` / userId `7658127801` | — | 当前登录老师 | 关模块→接口返空 `{}`/`[]` |
| AI 分析侧关单模块（CASE-009） | 同上（辅导老师 唐稳01，部门 `5253663827314688`） | — | 桥调 `refreshReasoning` | 关 satisfaction→END 照跑 |

**补充验证（2026-10-20 收口）**：CASE-005 历史计划 `excludeMode` 空 → cart 视为【无排除】（删掉节点 ext_config.excludeMode → 数学+英语都在）✅；CASE-012 B端下单推荐 `POST /b/renewMaster/recommendProductList` → 纯续语文+英语(扩科) ✅；在读范围·小班表写入侧 `OdsSmallRenewalSubjectSyncService` 只过滤「正价课(专题/系列)+赠课订单(payChannel=免费)」，**未过滤 成人/纯预售/赠课标签** → 与 PRD 在读范围有出入（既有数据管道口径，非本次代码）。CASE-010 作废（代码已删）；CASE-013 属前端。

## 2026-10-21 · CASE-014 补齐（小班计划 → 排除大班在读，`test-gtbg-dev-1`，✅）

**复用/补齐**半成品小班计划 `dcg-小班扩科排除-计划`（`586116340522184704`，type=2，已发布）：
- 前置小班课 `18314034380997173`（线上小班课-小学数学-0917-OP1，一年级/2026春，班 `586084334251927552`）；后置小班课 `18314034380997207`（一年级/2027暑，班 `586097025945298944`）——**续班后置关系本就存在**（course-center 续班关系，`calculateRenewalType=1`，产品侧 `listCoursesByPreCourseNumber` 可见，cart `getCourseExtensionByExtensionInfo` 同源）。
- 扩科节点 `586116659463352321`(type=6)：`ext_config.excludeMode=1`。**2026-10-20 历史现象**：当时 B 端 `renewal/process/edit` 未落 excludeMode，曾直接写 `node_config.ext_config`（CASE-001 同）；该结论不再代表当前版本，2026-10-21 已验证真实 HTTP 保存 0/1，见下文「2026-10-22 扩科节点配置与单字段修改入口核对」。
- 扩科商品 `renewal_expand_subject_recommend`(node 586116659463352321)：**grade 16→11**（原配 grade16 与后置年级 11 不符 → `studentPostGrades` 不含 16 → 扩科恒空），subject4 英语→`585963404555053056`、subject5 语文→`585960755422160896`。
- 学员 `7658127801` 向前置小班课下单+支付：`orderItem 432249582456931136` / payNumber `432249582456930624`（productType 6004，0 元已支付）。
- 学员「大班在读」= 语文(5)@2026春（`dws_fuwu_clazz_user_subject`，clazz `585960582537144320`）。

**实跑（acl 桥，`traffic-env: test-gtbg-dev-1`）**：

| 例 | 调用 | 实测 |
|---|---|---|
| 读侧·小班取大班在读 | student-data `RenewalInReadSubjectService#listOtherModeInReadSubjects(7658127801,2,2026,"C")` | `[5]` ✅（`"X"`→`[]`） |
| C端 E2E·开排除 | cart `RenewalService#getRenewalDetail("7658127801","586116340522184704",true,false,null,null,null)`，excludeMode=1 | 扩科**只出英语**(`585963404555053056`)、**语文被排除** ✅ |
| 对照·关排除 | 同上，excludeMode=0 | 英语 + **语文**都在 ✅ |
| 结果年级 | — | `grade_clazz_list[0].grade=11 一年级`（纯续+扩科） |

**结论**：CASE-014 端到端通过（语文排除/英语保留，关排除恢复），与 CASE-001（大班计划 → 排除小班在读）对称。

**调用坑（重要）**：cart 端到端必须调 **7 参重载** `getRenewalDetail(userId,renewalNumber,getContext,fromBCart,appointUserId,sellerId,includeBCart)`（`RenewalService:217`）——只有它经 product-server `listRenewalWithProcessByNumber` 加载扩科配置；**5 参重载（`RenewalService:960`）不加载扩科配置**（`renewalDataService` 只回计划壳，`expandSubjectConfig=null` → 扩科恒空）。另 product-server `listFeignMasterProcess` 只回 type=3(推荐)节点，扩科配置单独由 `buildCartAndExpandSubjectConfig` 读 CART 流程内 type=6 节点 `ext_config` + `renewal_expand_subject_recommend` 拼装。

**遗留**：`计划2` `586117007542349824`、`1020扩科小班` `585953412800081920` 仍为空壳（无流程/课程），未动。

### 2026-10-21 补充 · CASE-014 纯续补齐（✅）

**现象**：补齐扩科排除后，cart/B 端推荐只有扩科英语、无纯续数学（B 端「下单-推荐范围」应=纯续+扩科）。

**根因（两处，均 dcg 半成品计划遗留）**：
1. **后置小班课无商品 SKU**：后置课 `18314034380997207` 只建了课+班（clazz `586097025945298944`），没建商品。cart `PostClassInfoBuildSubBuilder` 要求后置班有商品 SKU 且 `saleStatus=40`，否则跳过 → 纯续候选为空。**补齐**：`create_uniform_product` 给后置班建 GPS 统一商品（productType 6004，SPU=`18314034380997207`、SKU=`586097025945298944`，`saleStatus=40`；镜像前置课商品；后置课有 CES 子产品 `clazzTypeNumber=18314034380997207`，上游 `upstreamProductType=10001`）。
2. **推荐节点商品类型错配**：计划「推荐节点」`586116659480129536` 的 `renewal_link.product_type=2`（班级）→ product-server `listFeignMasterProcess` 回 `productType=2` → cart `renewalConfig.productType=2 ≠ ProductType.CLAZZ(6004)` → `PostClassInfoBuildSubBuilder.supports()=false`、`buildCandidates` 落空 → **纯续恒空**。**改为 6004**（小班课）。

**复跑**：cart 7 参 `getRenewalDetail` → 纯续 `586097025945298944`(6004,recommend_type=1) + 扩科 英语 `585963404555053056`(recommend_type=2)；B 端 `recommendProductList` → 纯续「dcg-小班扩科排除-数学-后置」+ 扩科「英语」✅。

**沉淀（小班续班排查要点）**：cart 小班纯续要三件齐——① 后置班已建商品 SKU 且 `saleStatus=40`；② 计划推荐节点 `renewal_link.product_type==6004`（小班课，决定 `renewalConfig.productType`）；③ course-center 前置→后置续班关系存在（`calculateRenewalType=1`）。缺任一一律纯续为空。

**注意（缓存）**：cart 对「计划配置 / SKU / 班级」有本地(guava)+Redis 缓存（`single.product.query.cache.time=1800` 等），改完配置需下轮才生效（本次靠随后 `buildContext` 调热缓存）。

## 2026-10-21 第二批复核结论（审计完成，验收未准出）

- 以最新 PRD 为准，Banshan 仅参考。新版飞书 P0 为 CASE-101～120，共20条（扩科7、AI7、下单6）；qa-data-agent-service 同步 cases.yaml/cases.md/analysis.md/gaps.md/audit-evidence.json。结构校验0 ERROR，不代表实际执行通过；旧 cases.result.json 是此前缺cookie中止记录，不计入新版结果。
- 单测：student-data 33、cart 7、student-center 5，合计45通过。student-center 指定UTF-8后构建成功；未取得核心行覆盖率≥80%的证明。
- dev-1 实测：学员7658127801，大班计划585960797778243584与小班计划586116340522184704，cart七参数入口和product-b推荐集合一致，分别排除数学/语文且保留纯续和英语。此为服务查询证据，不代替前端端到端及八条件全覆盖。历史跨年英语样本order_number=0，仅机制数据，不能当有效订单。
- AI：student-data续班9内部alias、退费7 key；student-center真实HTTP返回续班8描述key/退费7 key。组合一/二真实分析、前端隐藏及禁止写入未完成全量验收。
- 下单：order购物车明细返回组合584632626097291265，会员卡8007＋实物8010，数量各1，原价0/9900分；只部分验证CASE-117，未支付。组合搜索调用未成功，不计为通过。
- 静态偏差/待确认：小班写表未见成人/纯预售/赠课标签过滤；多前置课取第一门有学年学期；B端excludeMode保存须重验；小班重复购买提示未带子商品名；20上限按种类/件数需统一。逐项复现步骤及造数条件见新版P0。
- 发布计划23819已补关联下单story1122531521001394689，保留原服务清单，共12后端＋2前端。Apollo/config/rollback文本为空；旧上线方案8服务/数字key口径不能直接执行。
- PROD已发布查询未命中renewal.inread.operation.modes、renewal.ai.dept.module.switch、refund.ai.dept.module.switch、refund.ai.module.deps。仅线上过滤须配[1]，AI组合灰度前补依赖图；空模块配置全放开为代码行为，不代表需求已验收。
- fetch后student-data缺release 45提交、student-center缺66提交，上线前合并复测。本轮未修改业务源码、未部署/支付/写生产数据；仍需补八条件真实样本、组合AI和混合商品支付数据及完整验收。

以上结论替代本文件此前“10条全量就绪/自动可执行”、旧根因下线开关及旧数字key说明。稳定证据在 qa-data-agent-service/skills/data-case-gen/storage/xuban-expand-exclude/audit-evidence.json 和指定飞书P0。

## 2026-10-21 增量验证与修复（进行中）

本轮以最新PRD和diff为准。下单重复校验、数量限制、支付为既有能力，仅保留直接影响的兼容验证；不作为本次新增未完成的依据。

- P0飞书文档已落20条/53个细分场景，含具体入口/数据/动作/预期/实际结果；仍有在测项，不能整批标通过。上线方案已原位改为12后端、2前端项目，并补两个实际GAIA组件发布步骤及配置/回滚。
- 扩科：真实B HTTP保存0/1→list0/1→推荐3/2项；大小班B/cart集合相等、纯续保留；新学员7658129769真实订单432268881905058380入班DWS29183。赠课标签13和纯预售关系分别返回[]，恢复后[1]。资格32测通过；student-data f5540c121部署1308190已EurekaUP并7项实测通过。退款对照发现样本arrangeMode曾由4改2，已精确恢复4；不能用受影响样本直接判需求bug，干净样本继续验证。
- AI：student-center 8cffd81c5/pipeline1308150已EurekaUP，预测B不再从画像泄漏、reasonType0关闭时editable=false均真实HTTP通过。widget534767b/0.0.55-alpha.3真实页面通过，默认仍alpha.2。
- student-data 442bfa869/pipeline1308164已EurekaUP：null模块/授权空项修复17测通过，运行时9矩阵及混合空key请求通过，临时Apollo恢复精确原值。
- 真实AI分析：新续班沟通1434，未续开启handle2落库summary1950，已续关闭handle0；退费tutoring开启handle2、belong255=1，关闭新belong256时保持0；后续组合一授权依赖tutoring后256处理为1。组合一root、组合二root/suggestion均handle2且落库32220/32221；组合一suggestion有明确关闭日志。重跑关闭对照须新comm_id，不能复用256当未分析。
- 下单增量：ContinuClazzOrder742d719/0.0.19-alpha.3真页面显示软件会员8007/出版图书8010、购买数量，检索不带saleStatus/计划限制。默认组件未切换。历史修复675e7e5278/pipeline1308144 ORDER已UP，真实重复提示和21拒绝通过；页面实际order-b仍旧版，不冒充页面已发布。99元支付432268438450733376及两个子单真实完成仅作兼容证据。
- AICR：student-data91a49c01旧head PASS0blocking不代表后续head；center新head任务476取消，不能引用旧PASS。fresh独立review发现courseTypes=null降级边界，已修并32测通过。
- 详细临时证据：/tmp/xuban-audit-20261021/{expand-verified.md,ai-verified.md,order-verified.md,adversarial-review.md}；稳定可重放资产同步至qa-data-agent-service后从本节更新入口。


最新补验：扩科promotions fad1dffd配置页面全部通过；干净全退、成人、体验、线下和全局开关false→3/true→2实测通过，配置恢复。AI门控77项定向测试全部通过，核心AiModuleSwitchService行覆盖108/127=85.04%、分支112/136=82.35%；RenewalInReadSubjectService行覆盖96/103=93.20%。真实learning/NPS落库32224/32223。组合商品删除后购买数量残留1已复现并以83fa4e0修复；alpha.4删除/加回/19→20/20禁用及混合班课明细真实通过。

2026-10-21最终补验：部分退售后36635172243112576已status1/process99，order432271791745401715 refund_type1，仍在读[1]。AI同一隔离学员完整依赖产生summary32224～32228；一次模型建议JSON格式失败且无脏写，原输入重试成功，非连续成功。最终临时Apollo精确恢复、真实15模块均false。稳定P0细项与执行证据位于qa-data-agent-service/skills/data-case-gen/storage/xuban-expand-exclude/，其中replay-expand-readonly.py已在最终环境再次执行7项全部通过；旧cases.result.json未改成虚假全绿。

最终组合组件：ContinuClazzOrder83fa4e0已推送，测试0.0.19-alpha.4定向实际加载。CASE116真实19→20、20禁止再次写，删除1→0/加回1；CASE117大小班混合明细名称/类型/数量/原价正确，未提交额外订单。GAIA默认alpha.2不变，生产切版走审批。当前P0文档已覆盖53子场景，明确共用出口代码覆盖与实际页面覆盖边界；不是生产准出声明。


## 2026-10-21 最终补录（人工执行卡与发布编排实测）

详见 [[本次工作记录-20261021]]。20条case已补账号、班/辅导班、学员及关系、配置、操作和可见预期；53个执行场景保留。技能已固定人工优先规范，审计73条路由通过。发布编排实际执行一次，后端汇总57%，准出未执行、总门禁未过；历史79条告警仍未处理。DWS/GPS配置类型错误已补部署并验证UP/真实Bean/新pod无解析错误。AI及cart核心缺口已补验、临时数据配置恢复；未重算平台，不声明上线放行。


### 第二轮平台覆盖率已验证

21:25:57重算后：product92.11%（39333）、data81.44%（39334）、center83.43%（39335）、cart82.45%（39336）、order83.80%（39337）；后端汇总81%已通过，未改阈值或业务排除。前端空计划保护真实补验后单独重算中。准出未执行，不能据此声称生产放行。无关历史告警已停止处理，未经明确要求不建缺陷；三条误登记TAPD已置不解决，但天玑status2恢复操作未生效，7条分类残留已如实写在线文档。技能审计errors0/warnings0、75条路由0失败。


### 最终平台覆盖率

最终平台结果：后端汇总81%、前端汇总97%，两项覆盖率门禁均通过。后端product92.11%、student-data81.44%、center83.43%、cart82.45%、order83.80%；前端promotions97.91%（39331）、cronus100%（7/7，39338）。全部为新报告实际值，未改阈值或业务排除。准出仍未执行，USER_CASE/ALARM等其他门禁不等于通过。按用户要求，无关历史告警不处理、不新增缺陷。

Cronus补测走真实小班页面：唐稳01/tangwen01登录→清空续班计划→非续班期且不限本人→班级“测试触达”494625569468663808→学员5661436125“接口自动化测试”→下单，显示“缺少续班计划号，无法下单，请先选择续班计划”，不打开下单容器；两次均通过。完成后已恢复专用数学班、续班计划及7658127801，无订单/支付/购物车写入。


### 2026-10-22 扩科节点配置与单字段修改入口核对

- 对象：续班计划 `585960797778243584`，流程 `585963455406698496`；环境 `test-gtbg-dev-1`。通过 product-b ACL 桥只读调用 `com.gaotu.product.dao.old.NodeConfigDao#getByNumber`，两次响应 code=0。
- 扩科节点 `585963455412989952`（type=6，id=797）实际 ext_config 为 `{"allowDuplicate":false,"excludeMode":1,"expandSubject":true,"forceBuy":false}`；购物车节点 `585963455448641536`（type=3，id=798）为 `{"excludeMode":0,"forceBuy":false}`。两份 extConfig 分属不同节点，值不一致不是配置冲突。
- `RenewalServiceImpl#buildCartAndExpandSubjectConfig` 只从 type=6 节点取扩科 excludeMode；type=3 只取纯续 forceBuy。excludeMode=0 为无排除，1 为排除不同授课模式在读。`ProcessService#convertNodeConfigVO` 对缺失 excludeMode 的非空配置补 0，因此回显 0 也可能是默认值，但本次购物车节点实际存有 0。
- 当前本地 feature-xuban-expand-exclude 中 NodeExtConfigVO 已声明 excludeMode，`ProcessService#mergeExistingExtConfig` 在请求未传 excludeMode 时保留旧值；2026-10-21 已有真实 HTTP 保存 0/1 的验证。2026-10-20 的“不落 excludeMode”仅为历史现象。
- 在该分支 ProcessController 与青舟该分支接口清单中未发现仅修改 excludeMode 的专用业务 HTTP 接口。测试 ACL 桥可调用 `com.gaotu.product.dao.old.NodeConfigDao#updateByNumber(NodeConfig, Long)`，第一个参数只传 extConfig 字符串、第二个参数传目标扩科节点号；Mapper 为 updateByExampleSelective，未传的数据库列不更新。
- 上述 DAO 更新会替换整个 ext_config 字符串，不会逐 key 合并；必须先读原 JSON，仅修改 excludeMode 并保留其余 key。不可只传 `{"excludeMode":1}`，也不能将其当作正式业务 API。流程 edit 还会处理 renewal_link 等关联，不适合当作字段级更新。此次仅核对读入口及源码，未调用写方法；扩科节点当前已为 1。


### 2026-10-22 切换扩科排除后推荐列表不变：修改节点与查询计划不一致

- 用户先修改大班扩科节点 `585963455412989952`，随后用 `POST /b/renewMaster/recommendProductList` 查询小班计划 `586116340522184704`、学员 `7658127801`（dev-1）。两者不属于同一计划，修改前者不会影响后者。
- 本次只读实查：大班节点 update_time 为 `2026-10-22T10:27:04`、excludeMode=1；小班计划 `/b/renewal/process/list` 返回流程 `586116659463352320`、扩科节点 `586116659463352321`，excludeMode=1，节点 update_time 仍为 `2026-10-21T14:30:07`。
- 原推荐请求 code=0，返回英语 `585963404555053056` 与纯续数学 `586097025945298944`，未返回扩科语文。当前结果与小班节点一直为 excludeMode=1 一致。
- 修改小班计划时，应以 `586116659463352321` 为 DAO updateByNumber 第二个参数；若修改 `585963455412989952`，应查询其所属大班计划 `585960797778243584`。保留 ext_config 其他 key。此次未写业务数据，未重跑 0/1 对照。


### 2026-10-22 CASE-102 原文与当前推荐复核

- 已读取飞书 P0 文档 revision 159 的 CASE-102 章节（标题块 doxcnXX5BdGmbZDIqlhmkBGnuKg）：大班计划 `585960797778243584`、扩科节点 `585963455412989952`、学员 `7658127801`，入口为大班花名册 `clazzRosterOL`。用户此前贴的 `microClazzRoster` / 小班计划 `586116340522184704` 不属于该 case。
- 最新只读核对：大班扩科节点 excludeMode 已为 0，update_time `2026-10-22T10:29:46`。按 CASE-102 正确大班计划调用 `recommendProductList`，code=0，精确返回纯续语文 `585960755422160896`、扩科数学 `585963387758962688`、扩科英语 `585963404555053056` 共 3 项，说明关闭排除已体现在该接口结果中。
- CASE-102 开启排除（excludeMode=1）的文档预期为纯续语文+扩科英语共 2 项；当前现场为关闭状态，本轮没有代改节点或重跑开启状态，不将历史通过记作本轮 0/1 全量对照。做本 case 应切换大班节点并查询大班计划，无需改小班节点。


## 2026-10-22 CASE-108：退费预测等级开关修复

student-center `2cc0194a9` 在 `/roster/refund/analysis` 返回前，按 `prediction` 清空两预测字段；保留既有整卡门控。7项真实领域服务/H2/HTTP集成测试通过，含开启/关闭、缺省、null、503、整卡关闭及无预测数据。流水线1309131发布test-gtbg-dev-1，新pod student-center-c85d97cbd-btdgt、commit2cc0194a、Eureka UP。随后页面同源接口返回code0，人工意向2/中及服务建议保留；样本本身无预测等级，仅证明开启路径兼容，不冒充关闭场景验收。模块接口回读续班8项与退费7项均true，现场配置与两tab保持。前端未修改，改法及后续组合验收见 [CASE-108 修复说明](CASE-108-退费预测开关修复.md)。AICR489取消，未获得本head评审通过结论；整项页面验收未闭环。


### 2026-10-22 花名册「小班在读科目 / 续班小班科目」不展示（学员 7658127801）

- 现象：**续班服务 tab**（`/crm/cronus/clazzRosterOL?tabKey=continuationService` → `POST /component/student-center/roster/renewal/page`）班级 `585960582537144320`（`dcg-扩科排除-前置-五年级语文`）学员 `7658127801` 的「小班在读科目」「续班小班科目」两列不展示（为空）。接口实查该行 `smallStudyingSubject=[]`、`smallStudyingSubjectCnt=0`、`smallRenewalSubject=[]`、`smallRenewalExpansionSubject=[]`（对照 `studyingSubject=[1,4,5]` 有值）。
- 数据来源：**EES 索引 `ads_large_subclazz_user_index`（物理 `_v3`）文档 `36622538973250048-7658127801`** 的这 4 个字段（页面按 subclazzNumber-userId 取该 doc）。花名册索引 `ads_large_clazz_user_2026` 同 id 文档**不含**这 4 个字段（只 `studyingSubject=[1,4,5]`）。
- 字段产生：DQ 字段 `largeRelationSmallRenewalSubject`（`LargeRelationSmallRenewalSubjectQueryService#buildData` → `SmallRenewalSubjectService#calRenewalInfo`，大班分支）。该服务只读小班在读表 `dws_small_clazz_user_subject`（学员有 4 行）并按 `largeRenewalSubjectInfoList` 中 `clazzNumber` 匹配，产出上述 4 字段（`smallStudyingSubject`=小班在读科目 / `smallRenewalSubject`=续班小班科目）。
- 直接原因：该字段按「**同学年+学期+同年级**」把学员的小班在读记录归到对应大班班级（`collectSmallStudyingSubjects` 做年级交集）。实测 ACL 桥 `SmallRenewalSubjectService#calRenewalInfo("7658127801", true)`：大班班级 `585960582537144320` 的 `smallStudyingSubjectList=[]`、`smallRenewalSubjectSet=[]`、`largeStudyingSubjectList=[{5}]`（仅大班本班语文）。
- 年级对照：大班课程 `585960577856301056` `grades=[15]`（五年级，`courseCategory` 五年级）；学员小班班级年级 `grade_id` 为 `3`/`3`/`11`（课程 `18308368321085798`/`18308368321085803`/`18314034380997173`，`grades=[3]`/`[3]`/`[11]`，category 均为一年级）→ **与大班五年级无年级交集** → 小班在读科目算空；同年级小班组为空 → 无可比后置课程 → 续班小班科目也空。
- ⚠️ 口径不一致：扩科排除实际用的 `RenewalInReadSubjectService#listOtherModeInReadSubjects` **只按同学年+学期过滤，不卡年级**，故数学仍被排除 —— 于是出现「花名册列不展示、但扩科确实排除了数学」。两处口径（展示卡年级 / 排除不卡年级）需确认哪个是期望；若期望花名册可见，测试小班应建成与大班同年级（或确认展示口径是否应放宽到只按学年+学期）。
- 定性：**测试数据年级不一致**（大班五年级 vs 小班一年级）导致的展示为空；非 ES/回溯问题（该字段走 DQ 实时计算，不走 ES）。未改任何代码/数据。


### 2026-10-23 TAPD#1122531521001483882 扩科推荐「B端管理页与C端/下单读口径不一致（node 隔离）」

- 工单：`续班扩科推荐-扩科商品配置未按节点(nodeNumber)隔离，管理页面显示0条但推荐接口仍返回`（reporter 唐稳，owner 张泽灵，`线下问题/服务端`，环境 `test-gtbg-dev-1`，分支 `feature-xuban-expand-exclude`）。
- 代码核对（product-server，本分支仅加 excludeMode；该不一致在 `origin/release` 已存在，**非本分支引入**）：
  - 读侧（cart / `/b/renewMaster/recommendProductList` 经 C feign `listRenewalWithProcessByNumber`）`RenewalServiceImpl#buildCartAndExpandSubjectConfig` 第 2924 行用 `selectByRenewalNumber(renewalNumber)` —— **只按计划号，忽略 node_number**。
  - 管理页 `ExpandSubjectServiceImpl#list:73`、节点回显 `ProcessService#convertNodeConfigVO:1179` 用 `selectByNodeNumber(nodeNumber)` —— **按节点**。
  - 写侧 `expandSubject/add`（`ExpandSubjectServiceImpl#add`）只校验节点存在，**不校验 `type=6`，也不校验节点属于本计划**。
- 数据核对：test 计划 `586333423417849856` 的 2 条记录挂在 **type=3 购物车节点** `586333640670214145`，而 type=6 扩科节点 `586446512379162624` 下 0 条 → 管理页 0 条、但 cart/recommend 仍出 2 条（初二物理 `586333286253586432`/初二化学 `586333327565383680`）。生产/测试存量：**prod 15 条全部挂 type=6（5 计划）**；test 45 条 type=6 + 仅该计划 2 条 type=3。
- 正常路径不可复现：FE（`gaotu-fe-promotions` `ExpandSubject/*`，`services/expandSubject.js`）nodeNumber 明确取自 `process/list` 返回的 `nodeConfigs[type=6].nodeNumber`，AddDrawer/ManageDrawer 均用该值；工单复现是测试用接口把记录写到了 type=3 节点。
- 定性：**代码层面确为「读/管两条口径不一致」的真实缺陷**（建议修）；但按 UI 正常操作不可触发，属健壮性/一致性缺口，**非现网事故**（prod 均挂 type=6）。修法：读侧 `selectByRenewalNumber` → `selectByNodeNumber(node.getNumber())`（与 `list` 对齐）；可选加固 `add/delete` 校验节点 `type=6`。归属 product-server。<br>以上为只读诊断，未改任何代码/数据。


## 2026-10-23 膨胀券「加购」C端展示 + 组合商品含小班课子项（已实现·已实测）

- 目标：B 端加购的**膨胀券 / 组合商品**在 C 端续班推荐展示；口径 —— 组合商品**跟联报一致**、膨胀券**不按年级学科过滤/不去重（同一商品去重保留一个）**。
- cart 改动（`feature-xuban-expand-exclude` → `test-gtbg-dev-1`）：
  - `75507a43` 大班路径 `RenewalService#convertResultToClazzDetailDTO` 增 `productType=8014` 分支；
  - `334fa126` 小班路径 `#convertToRenewalCartVO` 增 8014 分支；
  - `6b988e9e` 组合商品转换（大班/小班）子项 = 大班课子班(`combineClazzNumberList`) + 小班课子商品(`combinedSingleProductDtoList` 中 `productType=6003/6004`，skuNumber 即班级号)；**纯「其他商品」组合过滤不展示**；展示年级/学科取**首个子项**（对齐联报）；新增 `PurchasedAdditionalPurchaseSkuSubBuilder`(order=97) 单独查加购商品(券/组合)有效订单填 `purchasedAdditionalPurchaseSkuNumbers` 供加购项 signUp，**不动**既有 `purchasedPostClazzSkuNumbers`。
  - 券：年级/学科取 `listDisplayableCoupons(renewalNumber,userId)` 命中行、名称/售价取单品；同一商品(productId)去重、不参与(年级,学科)去重。
- 测试数据（test，已回读）：`renewal_pre_order_activity_coupon_scope` 券范围行 `is_del` 置 0；计划补预报名流程并绑活动 `578667303502106624`（`process_config type=3`+`node_config type=4`+`renewal_link_activity`）；小班补「一年级·数学」券范围行；**`gaotu.coupon_expand_config` 3 张券 `sale_status` 1→2 + `sale_end_time` 延后**（B 端出券关键）。
- 接口实测：B 端 `POST /bgwApi/component/student-center/renewal/pre/coupon/list`（大班/小班各 `total=1`、使用中+售卖中）；加购 `POST /bgwApi/orderComponent/b/cart/addCart`(8014)；C 端 `GET /cart/web/renewal/cart`（大班 grade16 券「六年级语文」、小班 grade11 券「一年级数学」，`recommendType=3`、未被去重）。纯其他组合（会员卡/实物）已按规则过滤不展示。
- 边界与验证状态：组合「含课程子项」正向已实测 —— 组合 `579426174109902848`（大班课子班）在**大班**展示；组合 `402910767185154048`（**只含小班课子项 6003**）也在 C 端展示 → 证明小班课子商品(6003/6004)读取生效（`9bfb6fea` 放开 6003+6004）。纯其他组合已验证被过滤。**未实测**：加购项「已报名」signUp（大小班代码均已补齐按加购 SKU 查询，未造支付订单验已购）、券「同一商品去重」（商品级去重共用，无重复券数据可触发）。B/C 页面 UI 未逐页点击。

### 本轮新增接口验证（2026-10-23）

cart `12cba6a949b0021df8a346e9e789cc903fbcbff1`，流水线1311214，dev-1新pod UP；JDK8全仓编译成功、6项TestNG测试通过。order `5ab5476dfb`补齐canCreate券上下文、prepare券限购量；JDK8全仓编译及4项JUnit测试通过，流水线1311467构建成功；新Pod `order-gaotu100-com-77d749995d-mvlxk` / `10.218.239.138:28688` 确认镜像5ab5476d且Eureka UP。测试集群滚动发布资源不足已通过该泳道短暂0→1副本释放旧资源解决，副本恢复1。

真实 HTTP 使用学员7658127801有效sid，lane请求头 dev-1；大班计划585960797778243584/券578323391191220225，小班计划586116340522184704/券578323085464207361，sellerId8645。认证材料不入归档。

| 场景 | 实测结论 | trace |
|---|---|---|
| 大班/小班GET加购 | 券名、范围、10000分、canChangeCourse=false | cart_gaotu100_com.298.17927404377750025 / cart_gaotu100_com.301.17927404417930026 |
| productList带计划 | 正确范围与券详情 | cart_gaotu100_com.302.17927404412010024 / cart_gaotu100_com.303.17927404434110026 |
| productList旧请求无计划 | 名称售价正常；无范围、select0 | cart_gaotu100_com.304.17927404439610028 |
| 同券跨两个年级 | 大小班每个命中年级各1行；真实范围一年级数学、六年级语文 | cart_gaotu100_com.299.17927392875480013 / cart_gaotu100_com.301.17927392895120014 |
| 新skuNumbers/旧clazzNumbers/跨桶重复 | totalPrice均10000，不重复计价 | cart_gaotu100_com.305.17927404441640025 / cart_gaotu100_com.307.17927404467640027 / cart_gaotu100_com.299.17927404476900028 |
| 课程+券算价 | 课程0分、券10000分，总价10000；discount0 | cart_gaotu100_com.298.17927404486510027 |
| 券选择、重复提交、取消另一券隔离 | 选中券仍select1；取消后0；原4条课程选择不变 | cart_gaotu100_com.303.17927404505550028 / cart_gaotu100_com.305.17927404513200027 / cart_gaotu100_com.301.17927404539760030 |
| fullGive/validateNew | 8014商品保留，status0；无满赠数据 | promotion-app_gaotu100_com.96023.17927393454000426 |
| prepare | 返回券名/8014/10000分 | order_gaotu100_com.417.17927404429440004 |
| createOrder | 主单432439620802707776，子项432439620802708288，8014、10000分；DB与订单事件核实。客户端响应中断未保存 | order_gaotu100_com.434.17927407804790005 |
| 测试订单清理 | 未支付，取消接口status0，DB状态3 | order_gaotu100_com.453.17927413243960006 |
| 独立6003需求核对 | 有效单品SKU401085548055267328传productType6003，productList返回空；组合内6003支持不代表独立路径支持 | cart_gaotu100_com.304.17927428631760060 |
| 新版纯券canCreate（force=true） | status0，券不进入课程冲突/分层考试 | order_gaotu100_com.419.17927440955560001 |
| 新版超量购买 | 券A数量2拒绝，先命中既有商品总限购 | order_gaotu100_com.424.17927440978430001 |
| 已有订单后超限再购 | 内部HTTP共用预校验；用户1437332、SKU577635362308947969已买1，再请求2，总上限2，拒绝 | order_gaotu100_com.431.17927441701380001 |
| 新版prepare券限购字段 | onceBuyLimit=1，与商品SKU一致，价格10000 | order_gaotu100_com.429.17927441642990001 |
| 普通课程兼容对照 | SKU585960755422160896/productType2，补丁前后均status0，响应一致 | order_gaotu100_com.459.17927431045320011 / order_gaotu100_com.434.17927441715600001 |
| 商品停售预校验/生单 | 通过商品stopSale置SPU/SKU不可售，两个C入口均返回60048 | order_gaotu100_com.443.17927442011550001 / order_gaotu100_com.447.17927442038370001 |

多范围临时关系、scope行以及券选择均已恢复。停售测试商品已通过sale接口恢复，并独立读回SPU/SKU saleStatus40、canBeSold=true（product_gaotu100_com.273.17927442102001374）。promotion-app在测试共享default实例处理，非专属dev-1 pod。本次未命中优惠，不能声称已覆盖所有折扣。超量/已有订单负向先命中既有商品总限购，SKU单次/个人上限独立边界、全退和不限购另由4项契约测试覆盖。支付、退款、页面逐项点击不在本轮实测结果中。

### 加购相关接口清单（test-gtbg-dev-1）

**C 端**（学员登录态；header 带 `traffic-env: test-gtbg-dev-1`）
- `GET /cart/web/renewal/cart`（网关 `https://test-api.gaotu.cn`；header 另带 `ingress-traffic-env: test-gtbg-dev-1`、`pt=<学员登录令牌>`）
  - 入参：`renewalNumber`、`appointUserId`、`sellerId`（**二讲 employeeId**，非 accountId）、`includeBCart`、`p_client`。
  - 返回 `data.gradeClazzList[].clazzDetailDTOList[]`，关键字段：`productSkuNumber`、`productType`（**51 组合 / 8014 膨胀券 / 2 大班课 / 6004 小班课 / 23 联报**）、`recommendType`（**1 纯续 / 2 扩科 / 3 加购**）、`subjectNames`、`price`、`signUp`（1 已报名）、`grade`（分组年级）。
- 无登录态时验服务层（反射桥）：`com.gaotu.renewal.RenewalService#getRenewalDetail`，params `[userId, renewalNumber, false, false, null, sellerId, includeBCart]`。

**B 端**
- `POST /bgwApi/component/student-center/renewal/pre/coupon/list`（student-center；header `b_client: EES`）—— 续班计划下的膨胀券选品
  - body：`{"renewMasterNumber":"<计划号>","statusList":[1],"saleStatusList":[2],"pageNum":1,"pageSize":50}`（`statusList` 1 使用中 / `saleStatusList` 2 售卖中；都不传时按计划场景默认这两个）。
  - 返回 `data.list[]`：`couponName`、`couponId`、`couponSkuNumber`、`productType`(8014)、`buyAmount`、`deductibleAmount`、`couponStatus`(1 使用中)、`saleStatus`(2 售卖中)、`selectable`、`availableScope`（如「六年级语文」）。
- `POST /bgwApi/orderComponent/b/cart/addCart`（order-b；header `b_client: OES`）—— 老师为学员加购
  - body：`{"userId":<学员>,"accountId":<二讲 accountId>,"productList":[{"productNumber":"<券SKU/组合SKU>","productType":<8014/51/...>,"quantity":1}]}`；⚠️ **大数字 productNumber 必须传字符串**（否则精度截断）。
- 加购商品查询（反射桥）：`com.gaotu.facade.bcart.BCartFacadeImpl#listAdditionalPurchase(userId, sellerId)`。


### 2026-10-23 TAPD#1122531521001483911 扩科排除 excludeMode=1「未排除物理」——核查为**造数问题**

- 工单现象（`test-gtbg-dev-1`，分支 `feature-xuban-expand-exclude`）：计划 `586478827253954560`（节点 `586479612247175168` ext_config.excludeMode=1）候选 初二化学/初二物理，学员 `7658131792` 小班"在读"初二物理，cart 未排除物理。traceId `c3da9429-3298-47d6-adfe-84254e72f9f7.0.3`。
- 配置核对 OK：`gaotu.node_config` 586479612247175168 = `{"excludeMode":1,"expandSubject":true,...}`；`gaotu.renewal_expand_subject_recommend` 2 条 → subject **2**/product 化学 `586333327565383680`、subject **6**/product 物理 `586333286253586432`（物理=6 正确）。
- 排除读侧实调（ACL 桥 student-data，dev-1）：`RenewalInReadSubjectService#listOtherModeInReadSubjects(7658131792, 1, 2026, "C")` = **`[4]`**。
- 小班在读行（`ees_data.dws_small_clazz_user_subject`，该学员仅 1 行）：clazz `586478070328846336`（`dcg-G001-小班-初二物理-S2clean`）、year 2026/term **1**（CES，=OES C）、**subject_id=4**。计划前置 3 课（`586478949184432128/…949184432128…`）均为 2026 C → 学年学期匹配无误。
- 该小班课在 course-center `subjects=[4]`、品类=语文(1010)；**真实小班物理课**（`458397534824491008`「初二物理」、`579394671130843136`「高中物理」）`subjects=[6]`；全表 `subject_id=6`(物理) 有 206 行 → 小班在读表用 **OES 科码、物理=6**。
- **结论**：排除逻辑/配置/链路均正确——读到的「其它模式在读」是 subject 4，与候选 {2 化学, 6 物理} 无交集 → 不排除，cart 输出物理+化学与代码一致。**根因是造数：该小班课 course-center `subjects=4`（非物理 6）**，需修正/重建该小班课 subject=物理(6) 后复测；product-server / student-data 无需改代码。未改任何数据。
