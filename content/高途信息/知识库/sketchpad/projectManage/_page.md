# 问卷/CDS 平台 · 项目管理（projectManage）

## 定位
| 项 | 值 |
|---|---|
| 页面 URL | `https://test-cds.baijia.com/fe/sketchpad/projectManage`（CDS 平台，基座 `um-dma-qiankun-fe`） |
| 前端仓库 | `sketchpad`（gitlab `pandora/activity/sketchpad`，部署名 `gaotu-activity-cms-fe`，gitProjectId=11136） |
| 基座仓库 | `um-dma-fe`（gitlab `pandora/uqun/um-dma-fe`，部署名 `um-dma-qiankun-fe`） |
| 后端主服务（B端配置） | `future-landingpage-manage`（gitlab `pandora/activity/future-landingpage-manage`，gitProjectId=11158，Java springcloud，包名 `com.gaotu.future.landingpage`） |
| 后端同仓另一部署 | `future-landingpage-manage-in`（同一 git 仓库，内部环境变体） |
| **后端 C 端答题服务** | **`future-landingpage-service`**（gitlab `pandora/activity/future-landingpage-service`，gitProjectId=11163，同组织另一独立仓库，不是 manage 的部署变体）——**真正处理用户提交问卷答案、写 CRM/EES、发 MQ 的服务**，`future-landingpage-manage` 只是后台配置，不处理答题 |
| 下游依赖服务 | `sn-source`（投放类型查询 `/v2/putType/inner/byAppId`）；`future-landingpage-manage` → `future-landingpage-service` 有一条 Feign（`LandingpageToCFeignService`，缓存/预览用，`feign.url.future-landingpage-manage` 配置项名字反过来，待确认方向） |
| 数据源 | MySQL `uqun-test01.mysql.rds.aliyuncs.com:3306/gaotu`；Redis `uqun-test02.redis.rds.aliyuncs.com:6379/10` |

## 接口清单
| 触发 | 前端调用路径 | 后端服务 | 后端 path | 后端实现 | 说明 |
|---|---|---|---|---|---|
| 进页面 / 列表查询 | `/future-landingpage-manage/project/list` | future-landingpage-manage | `/project/list` | `FutureProjectMapper#projectList`、`FutureProjectPageRelationMapper#selectList`、`FuturePageMapper#selectList`/`getPageListByCondition` | 实测 traceId `630b4e3f-1956-40ee-9b8b-8446c26fc085.0.0`（test，泳道 `test-gtbg-dev-1`），200，另带一次对 `sn-source` 的 `queryByAppId` 查询 |
| 新增/编辑问题 → 保存 | `/future-landingpage-manage/question/add`、`/question/update` | future-landingpage-manage | `/question/add`、`/question/update` | `QuestionController` → `QuestionServiceImpl` | 前端代码 `src/pages/formList/components/QuestionDrawer/crm.tsx`（GAIA 来源问题）/`normal.tsx`（普通问题）；入参 `questionSourceType`(1=Gaia/2=Normal)、`questionSourceNumber`、`content.options[].gaiaOption` |
| 问题详情 | `/future-landingpage-manage/question/detail` | future-landingpage-manage | `/question/detail` | `QuestionController` | — |
| 字段范围/收集字段下拉 | `/future-landingpage-manage/question/gaiaTagList`、`/question/gaiaPropertyList` | future-landingpage-manage | 同左 | `QuestionServiceImpl` → `PropertyClientAdapter`（Feign 到 `gaia-center` 的 `PropertyClient`） | 字段范围=GAIA 的 `tagName`，收集字段=该 tag 下的 `GaiaProperty`（即 EES/GAIA 侧字段，如"续班扩科意向"） |

## 问卷题目编辑/保存机制（`sketchpad` 前端仓库实测，2026-10-16）

**两套完全独立的"标签"概念，排查时别混**：
1. **问题库里的"应用标签"**（`crm.tsx` 的 `tagList` 字段，接口 `/question/getTagList`）——给问题本身打的分类标签（CDP 用），与 EES 字段同步无关。
2. **表单编辑里每个选项的"标签"**（`formPage` 的 `TagCascader`，三级级联 `owningType/tagId/tagValueId`，字段 `option.optionTags`）——给**表单里的选项**打的学科/年级标签，这个也不是直接写 EES，是表单侧的筛选/统计用标签，来源接口 `/question/getOwnTagList`。

**真正决定"问卷答案能不能同步到 EES 对应字段"的是 GAIA 绑定（`crm.tsx`）**：
- 一个"续班扩科意向"这类题目，`questionSourceType=1`（Gaia 来源），题目整体绑定一个 `questionSourceNumber`（= GAIA 的 `PropertyNumber`，即 EES 侧字段编号）。
- 题目下**每一个选项**（如"数学""英语"……"暂无"）单独绑定一个 `gaiaOption`（`{value, label}`，来自该 GAIA 字段的枚举值列表 `GaiaProperty.options`）。
- 保存校验（`crm.tsx` `confirmHandle`，约 L246-282）：`currentQuestionFields` 里**每一个选项**都必须有 `optionName` 且 `gaiaOption?.value` 非空，否则弹"请选择对应字段枚举值"，**阻止保存**。即选项与 GAIA 枚举值的绑定是逐选项校验的，不存在"整体不校验"的情况。
- **因此，"某个选项（如暂无）没绑定 GAIA 字段枚举值"在设计上只会在编辑/保存该问题时直接拦截，不应该出现"已保存但某选项未绑定"的存量状态**——荆雅兰反馈的"没有绑定系统的扩科字段"更可能是：①该题目/选项是旧数据（当前这版强校验上线前创建的，历史遗留未绑定）；②或该题目走的不是 GAIA 来源（`questionSourceType=2` 普通题，`normal.tsx` 没有 `gaiaOption` 校验，普通题本身就不会同步到 EES/GAIA 字段）。排查时先确认该问卷题目的 `questionSourceType`。
- 单个选项未绑定只影响**该选项自身**的枚举值回填——前端数据结构是 `options[]` 数组，每项独立持有自己的 `gaiaOption`，相互没有级联关系，所以"暂无"选项的绑定状态不会影响同一题目下其他学科选项的同步。

**答案提交 → 实际写回 EES/CRM 的完整链路（已 clone `future-landingpage-service` + `product-server` 源码核实确认，2026-10-16）**：

`future-landingpage-manage`（B端配置后台）本身**不处理答题提交**，`PropertyClientAdapter`/`PropertyClient` 只有只读方法（`queryByTagNo`/`queryByNos`），没有写方法。真正的 C 端答题提交服务是**同组织下的另一个独立仓库 `future-landingpage-service`**（见上方定位表）。

**CDS → EES/CRM 链路（已验证）**：
1. 用户在 C 端表单页提交答案 → `future-landingpage-service` 的 `FormManageServiceImpl`（`saveForm` 相关逻辑，约 L306-317）在异步线程里依次做三件事：
   - `syncDataToCrmData`：同步数据到 CRM；
   - `syncDataToStudyDynamic`：同步到学员动态；
   - 当 `futureForm.getBusinessType()` 命中 `${form.syncCrmQuestionTypes:[5,7]}`（学情调研/预报名）时，调 `CrmQuestionReportService#syncFormFieldToCrmData`——**这是真正写字段的地方**：按 `FutureFormField.fieldSourceType=1`（来源问题库）取出每题的 `gaiaOption.value`，组装 `FieldSaveDTO`，调 **`StudentFieldClient#edit`（student-center 的 Feign 接口）**，把问卷答案写进 **student-center 的学员字段**（`EditStudentFieldRequest`，`updateSource=201` 标记来源是问卷场景）。**这条路径不经过 student-data、不经过 teacher-tool**，是 `future-landingpage-service` 直连 student-center。
2. 同一次提交还会发 MQ：`sendFormSubmitMq` 发 `message.setTopic(formSubmitTopic)`（Apollo key `ons.mq.formSubmitTopic`，无默认值），消息体 `FormSubmitMqDTO`。
3. **`product-server` 消费这条 MQ**：`QuestionnaireRecordConsumer`（`product-server-task/.../mq/questionnaire/`）监听 `topic = "${gmq.questionnaire.event.topic:test_future_landingpage_form_submit}"`，收到后判断 `businessType==8` 才处理，调用 `QuestionnaireRecordService#dealCDSMsg`（方法名直接点名"CDS"）——按 `clickUrl` 解析绑定号、匹配续班计划/前置课程、7档规则匹配学员，写入 `QuestionnaireRecord` 等表。
4. `product-server` 处理完后再发 `${questionnaire.record.mq.topic:product-renewal-questionnaire-record-event-test}`，**`student-data` 的 `DwsRenewalQuestionnaireConsumer`（`student-data-dws/.../mq/dws/renewal/`）消费这条才真正写 EES/ES**：`renewal_intent_info` 表、学员动态、`ads_subclazz`/`ads_small_clazz` 等 ES 索引（`renewalQuestionnaireStatus` 等字段）。

**结论**：CDS 问卷到 EES 实际上是**两条并行路径同时发生**，不是一条：
- **路径 A（CRM字段，直连）**：`future-landingpage-service` → `StudentFieldClient.edit` → student-center 学员字段。这条路径只在题目 `fieldSourceType=1`（来源问题库）且表单 `businessType` 命中 `syncCrmQuestionTypes`（学情调研=5/预报名=7）时触发，逐题用 `gaiaOption.value` 取值。
- **路径 B（续班问卷状态，经 MQ）**：`future-landingpage-service` →(`formSubmitTopic`)→ `product-server`(`QuestionnaireRecordConsumer#dealCDSMsg`，仅处理 `businessType=8`) →(`questionnaire.record.mq.topic`)→ `student-data`(`DwsRenewalQuestionnaireConsumer`) → 写 EES/ES 的 `renewalQuestionnaireStatus` 等字段。

**之前的猜测已证实是错的**：`teacher_tool_questionnaire_finish_test` 这条链的生产者是 **homework 服务**（通用考试首次提交），跟 CDS 问卷平台完全无关，该链在 student-data 侧只触发 AI 画像分析（`RenewalQuestionnaireSaveTriggerAiConsumer`），不写 EES。这是另一套独立系统，只是题材都叫"问卷"，排查时别混进来。

**排查荆雅兰反馈的"扩科意向没绑定系统字段"**：
- 如果关心的是**CRM字段是否同步**（路径A）：查该表单的 `businessType` 是否在 `syncCrmQuestionTypes`里、该题 `fieldSourceType` 是否为 1、选项是否绑了 `gaiaOption`；三者缺一都不会走到 `studentFieldReport`。
- 如果关心的是**花名册/EES 续班问卷状态字段**（路径B）：按 `product-server` 的 `dealCDSMsg` 逻辑，只有 `businessType=8` 的消息才会被处理成续班问卷记录，还要求能解析出绑定号（`QuestionnaireBindData`）才能继续匹配——没匹配上的会走 `dealNotExistedQuestionBindNumber`/`dealNotExistedComputeUserId` 兜底逻辑。需要先确认该问卷在 CDS 平台上配的 `businessType` 是不是 8，以及是否已通过 OES 续班计划"绑定问卷"流程绑定（即知识库 [`续班计划管理`](../../promotions/continuation-classes/renewalProcess.md) 记录的绑定关系），否则压根进不到这条链。

## 排查提示
- 排查"问卷填了但 EES 字段没同步"：先确认该题 `questionSourceType`（Gaia=1 才会同步，Normal=2 不同步）；再确认具体没同步的选项当时是否真的绑定了 `gaiaOption`（可能是旧数据遗留，不是当前编辑态的问题）。
- 直连后端验证时，用 `baijia-invoke`（`invoke_feign`，`service_name=FUTURE-LANDINGPAGE-MANAGE`）会拿到 500（缺少网关层账号/角色上下文，`project/list` 实际依赖 apisix 网关转发前的 `/feign/cache/getAccount` 等鉴权调用），复现应走网关地址而非直连容器。
- 本机 clone 该仓库 `http://git.baijia.com/...` 走 https 失败（`failed to store: -61`），改用 ssh `git@git.baijia.com:pandora/activity/<repo>.git` 可成功。

## 青舟接口详情页
- 未查（`future-landingpage-manage` 未在当前环境确认已登记青舟 apidoc，待补）
