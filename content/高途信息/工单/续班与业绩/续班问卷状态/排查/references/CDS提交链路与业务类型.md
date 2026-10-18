# CDS 提交链路与表单业务类型（businessType）

CDS = 落地页/表单平台服务 **`future-landingpage-service`**（appId `future-landingpage-service`，serviceCode `baijia.gt.incre.ad-common.future-landingpage-service`，仓库 `git.baijia.com/pandora/activity/future-landingpage-service`，集群 uqunProd）。续班问卷、学情调研、预报名等"表单类"都从它进来。

## 提交入口与落库表（库 `future_landingpage`）

- C 端提交：`POST {m.theark.top}/future-landingpage-service/form/saveData` → `FormManageServiceImpl.saveData`（`.../app/service/impl/FormManageServiceImpl.java`）。
- 提交记录落表 **`future_form_user_data`**；表单定义 **`future_form`**（含 `business_type`）；字段 **`future_form_field`**。
- ⚠️ 本机 `mysql_query` 对 `future_landingpage` 库**无查询权限**（表名为 `L4#future_form_user_data`）；要读表得先提权限工单。

## 一份提交走哪条链（按 businessType 分流）

同一份提交在 `saveData` 里同时做两件事：

1. **发 MQ**（`ons.mq.formSubmitTopic`，tag=`form_submit`）→ **product-task `QuestionnaireRecordConsumer`**（`@Profile("task")`；**写死 `if (businessType != 8) return Success;` 只处理 8**）→ `QuestionnaireRecordService.dealCDSMsg` → 写 `gaotu.questionnaire_record` + 发 `product-renewal-questionnaire-record-event-prod` → **student-data-dws `DwsRenewalQuestionnaireConsumer`** → 发明细(teacher-tool `gaotu.user_questionnaire_record`) + 刷花名册 ES + 写动态(`source_db_type=33`)。
2. **直接写学员动态**：`syncDataToStudyDynamic`，仅当 `businessType ∈ Apollo form.syncStudyDynamicTypes`（**PROD 运行态 = `{3,5,7}`**，arthas 读回；namespace application 无该 key → 代码默认）→ 调 student-center `addStudentDynamic` → 动态 `sub_dynamic_type=7 / source_db_type=27`（`sourceId` = `future_form_user_data.id`）。**不写明细、不刷花名册。**

⇒ **只有 `businessType==8（续班）`才进"续班明细/花名册"这条链**；`{3,5,7}` 只写动态；其余(1/2/4/6)两条都不进。

## 表单业务类型枚举（`future-landingpage-service` `FormTypeEnum`）

| code | 含义 |
|---|---|
| 1 | 问答表单 |
| 2 | 基础表单 |
| 3 | 线索表单 |
| 4 | 普通调研 |
| 5 | 学情调研 |
| 6 | 满意度调研 |
| 7 | 预报名 |
| **8** | **续班**（代码枚举只到 7；8 是新增/配置类型，两份 `FormSubmitMqDTO` 注释均写"8:续班"） |

⚠️ 两处 `FormSubmitMqDTO`（product-server 与 future-landingpage-service 各一份）注释有笔误：`3:线索表单 4:普通调研 4:学情调研 6:预报名 7:满意度调研 8:续班`——把 **5 误写成重复的 4**，以 `FormTypeEnum` 为准。

## 查某次提交「到底有没有进系统 / 是哪种类型」

1. **日志（免权限，首选）**：全量日志按手机号/姓名搜（`get_log_v2` `queryStr`；或 `serviceName=future-landingpage-service` + 客户端 `grep`）。
   - future-landingpage-service 的 **`发送表单提交变更mq, 消息结构体： {FormSubmitMqDTO…}`**（`FormManageServiceImpl:392`）——报文含 **`businessType`**、`formNumber`、`formData`（姓名/手机号）。
   - product-task 的 **`QuestionnaireRecordConsumer#consume | msgId is …, formSubmitMqDTO is …`**——**只对 `businessType==8` 打**（非 8 无此日志）。
2. **表（需 `future_landingpage` 读权限）**：`future_form.business_type`（按 `form_number`）；或 `future_form_user_data` 那条提交对应的表单。

## 判据

- **CDS 表 + 上面两处日志都查不到该手机号/姓名 ⇒ 这条提交没进系统**（要么没提交/填的是外部链接如问卷星 `v.wjx.cn`，要么被 `saveData` 前置校验拦下——如重复填写 `FORM_DUPLICATE_ERROR`，其**在落库前抛异常、不写表**）。
- 反过来：日志里能搜到那条 `发送表单提交变更mq` ⇒ 提交进了 CDS，其 `businessType` 即该问卷类型；再结合"是否 8"判断它该不该进续班明细/花名册。

## 与其它链路的边界

- reach「**发问卷**」触达 = **scene 61**（`planName=续班-发问卷手动通知`），与 businessType 不是一个维度；查触达用 `ReachTaskDataService#listClazzUserTasks`（见主 runbook §批量核对）。
- product-task 消费的这个 topic，生产名 = Apollo `gmq.questionnaire.event.topic`（消费组 `GID_product_questionnaire_record_*`，nameServer `uqun.ons.nameServer`）。
