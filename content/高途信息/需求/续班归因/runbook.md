# 续班归因 · 核心口径与排查手册

> 需求已上线。本文件只留**排查线上问题需要的口径**，原 skill 里 test-eco-7 的回归造数细节已废弃。

## 数据落在哪

### 归因结果表 `ees_data.ai_app_clazz_user_scene`（cluster_id 336）

唯一键 `(clazz_number, user_id, app_scene_type, app_scene_key)`，**重跑是 update 不是 insert**。
所以按 `create_time` 统计只能得到「新增」，要算「今天动过的」用 `update_time`。

`app_scene_type`：**5 = 未续跟进**，**6 = 已续总结**（1=用户画像 2=沟通摘要 3/4=建议评分，不属本需求）。

`app_scene_key` 只有四个：
`unrenewedReasonAi` / `unrenewedReasonTeacher` / `renewedReasonAi` / `renewedReasonTeacher`。

> **没有 `followUpSuggestion` 这个 key**。跟进建议内嵌在 `unrenewedReasonAi` 的值里，字段是
> `serviceSuggestion` + `suggestedFollowupTime` + `mentionedFollowupTime`，
> 由 `queryDetail` 拆成出参的 `followUpSuggestion.actions[]` / `.recommendTime`。

### 大模型调用留痕 `ees_data.ai_application_call_task`（同库）

全站 AI 网关共用。归因场景按 `application_number` 过滤：
未续 `288169360313290752`，已续 `288169360792524800`。
`extra_info` 是 JSON：`{clazzNumber, userId, subclazzNumber, reasoningEnum, refreshForce}`。

### 班级级任务表 `ees_data.ai_renewal_attribution_follow_clazz_task`

每天 **00:25 由离线侧全量重刷**。`handle_status` 0=待处理 1=已处理。
`is_renew_user_clazz=1` 表示续班用户班。

### 花名册 ES（索引 `ads_large_subclazz_user_index_v3`，`_id = {subclazzNumber}-{userId}`）

| 字段 | 含义 |
|-|-|
| `aiUnrenewedReasonKey` | 未续原因-AI 总结 |
| `manualUnrenewedReasonKey` | 未续原因-老师总结（**不是** `aiUnrenewedReasonTeacherKey`） |
| `aiRenewedReasonKey` | 已续原因-AI 总结 |
| `manualRenewedReasonKey` | 已续原因-老师总结 |

常量在 `RenewalReasonEsFieldConstants`。老师总结保存后**立即同步 ES**，不等 job。

> 按归因筛选时 `filter` 必须带 `renewalRoundFilter`（如 `[0,1,2,3]`），否则
> `RenewalRoundFilterService` 会无条件加 `termsQuery("roundIdx", [])` 把结果全滤掉，
> 看起来像「筛选把人筛没了」。`terms` 不做前缀匹配，用一级 code（如 `["2"]`）筛恒为 0 条。
>
> ⚠️ **线上 ES 不能用 es-aliyun MCP（本机直连必 502），走 `es-apply` skill 的 runDslAction。**

## 反射入口（baijia-invoke，project=student-data）

```
# 查详情（reasonType 传 null = 已续优先自动判定）
com.gaotu.student.data.app.service.syncdata.ai.renewal.RenewalReasonQueryService#queryDetail
  params: [clazzNumber, userId, reasonType|null]

# 查字典（1=未续 9×34，2=已续 7×18）
...RenewalReasonQueryService#listOptions                params: [reasonType]

# 存老师总结（形参顺序别搞反）
...RenewalReasonManualService#saveTeacherSummary
  params: [clazzNumber, subclazzNumber, userId, reasonType, [categoryCodes], supplement, operatorEmailPrefix]

# 单学员归因（refresh=true 强制重算，绕过内容级幂等）
...RenewalReasonTaskService#handleSingleUser            params: [clazzNumber, userId, refresh]
  返回 handleCode: -1失败 / 0跳过 / 1内容未变化 / 2成功

# 展示窗口三要素
com.gaotu.student.data.infrastructure.acl.RenewalPlanAclService#findFormalRenewalBeginTime  params:[clazzNumber]
...renewal.RenewalStateStatusQueryService#queryRenewalStateStatus  params:[clazzNumber, userId, null]
com.gaotu.student.data.client.acl.ClazzSyncAclService#listByNumbersFromCache  params:[[clazzNumber]]

# 班级挂的续班计划
com.gaotu.student.data.client.acl.adapter.RenewalMasterFeignAdapter#listRenewalMasterByClazzNumbers
  params: [{"clazzNumbers":[clazzNumber]}]
```

> 包名易错：`ClazzSyncAclService` 在 **`client.acl`**（不是 `infrastructure.acl`）；
> `RenewalPlanAclService` 才在 `infrastructure.acl`；`SubClazzHelper` 在 **`domain.ai.helper`**。
> 写错包名报「未找到服务…的实现类」。

HTTP 入口：`POST /inner/renewal/reason/trigger`，body `{"clazzNumber":…, "userId":…, "refresh":true}`
—— **是 clazzNumber，不是 subclazzNumber**。

## 已知坑

- **班名黑名单**：班名含 `赠课/测试/模拟课堂/家长会/体验/取消/伴学` 的班永远不会被班级 job 处理
  （`CommonRuleFilter` → `inScope=false`）。单学员路径（trigger / handleSingleUser）**不过** `inScope`。
  「2,621 个班只出 1 个班」优先怀疑这里。
- **班级运行态锁 1 小时**：key `student_data_renewal_reason_job_<clazzNumber>`，连着重跑会静默跳过。
  **key 不存在反而说明班级压根没走到抢锁那步（被 inScope 挡了）**。
- **内容级幂等**：源数据没变不会重复调模型，`handleCode=1`。要强制重算传 `refresh=true`。
- **强制全量失效开关**：Apollo `renewal.reason.ai-token.version`，改版本号即让所有上下文 token 失效。
- **在读课程有 60s Redis 缓存**：key `gaotu::clazz::renewal::listAllSubclazzStudentsByUserIdsCache::<userId>`，
  支付后立刻查续班状态会拿到旧值。
- **服务层 INFO 日志在 TLS 查不到**，只有 ERROR 与 `RequestLogAspect`。排链路靠异常堆栈 + DB 效果。
- **`ai_renewal_cdp_user_comm_base` 有上万行 `clazz_number=0`**，是角色识别骨架行，
  按 clazz_number 统计沟通量时要排掉。
- **判定「已续」只看 `RenewalStateStatusEnum{1已续,2未续}`，不读 `canRenewal`。**

## 归因数据源（三条路）

1. **沟通路**：`ai_renewal_cdp_user_comm_base` + `ai_renewal_cdp_user_comm_scene`（按 `comm_id` 关联）。
   判据是 scene 表 `comm_scene_value` JSON 里 `communicationType` 精确等于 `"续班沟通"`，
   `comm_scene_type` 固定 **22**。base 表 `comm_tag=4` 只是标记，代码不拿它过滤。
2. **问卷路**：续班问卷。
3. **预测路**：`ai_renewal_lift_feature_avg_detail`（班级参照，`features` 存 `{"q25","q50","q75"}`，取 q50）
   + `ai_renewal_lift_feature_detail`（学员特征）+ `dwd_service_renew_lift_result`（预测结果，
   `stage`/学部/学期/年级要能在 `predict_intent_config` 匹到一行，否则特征重要性全 `--`）
   + `dwd_service_renew_lift_snapshot`（分层快照）。
