# reach-service 调用入口与数据源

多个触达类 runbook 共用的调用入口、网关路由、库表信息。由 [`../没收到企微进班提醒.md`](../没收到企微进班提醒.md) 等引用。

## acl 桥（反射调 Bean/Feign）

- 后端映射：`AclServiceCompareController`（reach-service-web），`@RequestMapping("/reachPortal/test/acl/compare")` + `@PostMapping("/service")`，开关 `AclServiceCompareController.enabled` 默认 true。
- 调用域名（POST，body `{"serviceNameAndMethodName":"全类名#方法","params":[...]}`）：
  - 测试：`https://test-fuwu.baijia.com/bgwApi/reachPortal/test/acl/compare/service`
  - 线上：`https://fuwu.baijia.com/bgwApi/reachPortal/test/acl/compare/service`
- 走 `baijia-invoke` 的 `invoke_service(project=reach-service)` 会自动落到这个桥；返回默认带 traceId 可直接喂日志。
- 桥能正常返回（如 `com.gaotu.reach.domain.service.ReachSceneService#listByIds` 参数 `[13]` 可查出场景 13「进班提醒」）；但个别 ES/泛型返回方法（如 `ChannelSubTaskDataBiz#listByParam`、`ChannelSubTaskApi#list`）实测返回空 `{}`，取数改走库/ES 或触达明细接口。

## 网关路由（青舟 APISIX，appId=reach-service）

| pathInfo | rewrite | 说明 |
|---|---|---|
| `/reachPortal/**` | 无 | B端主路由。后端 Portal*Controller 自带 `/reachPortal` 前缀（如 `PortalDictionaryController` `@RequestMapping("/reachPortal")`+`@GetMapping("/dictionary")` → `https://test-fuwu.baijia.com/bgwApi/reachPortal/dictionary`），即「网关前缀=后端 controller 前缀」 |
| `/reachServiceYace/**` | StripPrefix=1 | 压测 |
| `/api/bgwApi/reachPortal/**` | StripPrefix=2 | 兼容路由 |
| `/bgwApi/reachPortal/**` | StripPrefix=1 | 兼容路由 |

⚠️ reach-service-server 的 Feign API（如 `ChannelSubTaskApi` → `/channelSubTask/list`）**不带** `/reachPortal` 前缀，经 `/reachPortal/**` 路由调会 404；带前缀的 B 端接口都在 reach-service-web 的 `Portal*Controller`。Feign 接口要直调就走上面 acl 桥。

## 数据源

- MySQL 库名 **`reach_service`**（mapper XML 里的库名别名 `n.` 即它，构建期替换）。集群候选：`gaotu-i-prod`(cluster 227) / `prod-gaotu-reach`(cluster 395)，查询需按库授权。
  - `channel_subtask`：通道子任务=每条触达。字段 `receiver_id`/`receiver_account`（WK 账号 type=4 时直接存企微账号名/邮箱前缀）、`status`、`fail_reason`、`reach_type`、`reach_scene`、`template_id`、`msg`。
  - `notice_task` / `notice_subtask` / `notice_part_task`：通知任务与拆分。
- ES 宽表（触达明细页数据源）：`reach_data_channel_subtask_v2`、`reach_data_notice_task`、`reach_data_channel_task`。
- 查询接口：`/channelSubTask/list`（`PageChannelSubTaskRequest`：reachSceneList/receiverIdList/receiverName/startTime「yyyy-MM-dd HH:mm:ss」/pager），被拦截的任务取不到通道子任务，状态以 ES 返回为准。

## 关键枚举

- `ReachScene` 13 = 「二讲通知-进班提醒」，reachSceneCode=`studentEnterClazz`，reachTypes [11(企微), 10, 15]；模板示例 templateId 3421「1v1和1vN 进班提醒」（channelType 11）、4972「H升学规划-填报服务进班提醒」（channelAccount=NoticeSale）。
- `AccountType` 4 = WK_ACCOUNT（企微账户，接收账号名直接是企微账号/邮箱前缀）；`NotificationSecondType` 16 = 学员进班。
- 企微发送落瓦力云通道（`WaLiYunWkNoticeTaskReacher`，applicationName=「进班提醒」），发送前 `WkAuthQueryProcessor.getCorpUserInfo` 校验老师是否在该企微主体（corpId），不在则 `stopError("老师不在该主体下")`。
