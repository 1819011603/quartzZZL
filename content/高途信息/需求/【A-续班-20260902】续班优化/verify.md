---
title: 【A-续班-20260902】续班优化 · 验证手册
tags: [需求, 验证]
---

# 验证手册

> 只保留当前可执行条件、仍有效数据和最新预期。

## 环境

| 项 | 当前值 |
|---|---|
| 泳道 | `test-gtbg-dev-3`（逻辑环境 `dev`，`traffic-env: test-gtbg-dev-3`） |
| 已部署服务 | `product-task`(10.218.237.230) / `product-b`(10.218.251.254) / `student-data`(10.218.248.8) / `teacher-tool`(10.218.251.152)，均 eureka UP |
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
- **结论**：**先填后调时 B 的花名册「已提交」状态不会随调课自动更新**（真实顺序风险）；是否最终一致取决于是否存在会重算该字段的 sync 链路（未确认）。原「宽表重建时会推导成 COMMIT」的说法**未证实，已订正**。
- **受限**：A/B 是「任务系统」测试班，**花名册 ES 无文档**（`ads_small_clazz_user` 查无）、B 也未绑定问卷（`queryQuestionnaireMatchResult(B, 计划 578532432171743232)=null`，A 有匹配），故无法用 A/B 直接验「先填后调」的落值。

## 待验

| 项 | 卡点 |
|---|---|
| 先填后调：B 班花名册 `renewalQuestionnaireStatus` 落值 | **存在真实顺序风险**（调课 MQ 不写花名册、回溯 Job 不重算该字段，见上）；A/B 测试班无花名册文档，无法端到端验 |
| 先调后填端到端 | 靠计划级规则 + 主链路扇出（7 档逻辑已验证，未跑完整 submit→ES/明细 链路） |

## 第二批：扩科【推荐排除】（2026-09-22，`feature-xuban-expand-exclude`）

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
- **未配置 = 关闭**（上线前须配全，否则全量 AI 停）
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
| 配置值 | key = 虚拟架构部门 org number；未配置 = 关闭 |

**已改（2026-09-23，已 push）**：student-data `12e41da47`、student-center `84ec1b732`（分支 `feature-xuban-expand-exclude`）
- student-data：`AiModuleSwitchService` 新增 `resolveAssistantOrgPaths(userId, clazzNumber, subclazzNumber)` / `resolveAccountOrgPaths(accountId)`；5 处分析侧调用点全改；`matchDept` 分隔符 `/`→`_`；feign 入参 `departmentIdPaths` → **`accountId`**
- student-center：`AiModuleSwitchQueryService.isRenewal/RefundModuleEnabled(moduleCode)` 内部取登录老师 accountId；11 处调用点去掉 `clazzNumber`

**部署（2026-09-23 复核）**：test-gtbg-dev-3 —— student-data pipeline `1284022` → 新 pod `10.218.250.176`、student-center pipeline `1284028` → 新 pod `10.218.236.63`，**均 eureka UP**。

**Apollo（student-data/TEST，已发布）**：`renewal.ai.dept.module.switch` / `refund.ai.dept.module.switch` 均已换成 org number `6816343048455168`（全模块开）；旧 7 个课程部门 key 已失效。

**已验证（2026-09-23，student-data acl 桥走网关 + student-center 真实入口）**

| 项 | 调用 | 实测 |
|---|---|---|
| 老师 org path | `resolveAccountOrgPaths(177071)` | ✅ `["12345_4959407036876800_6816343048455168_66707677944472576"]` |
| 续班门控（命中） | `queryModuleSwitch(1, 177071, [1,2,5,6,7,8])` | ✅ 全 true |
| 退费门控（命中） | `queryModuleSwitch(2, 177071, [tutoring,prediction])` | ✅ 全 true |
| 未命中老师 | `queryModuleSwitch(1, 1, [1,2])` | ✅ 全 false（未配置=关闭） |
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

**待办**：① **上线前须把要开放的部门配全**（未配置=全关），key 用线上真实虚拟架构部门 id；② 圈选侧 MQ 圈选消息未能在日志后端观测（门控函数级已验）。

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
