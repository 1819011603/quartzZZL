# 高中/素养问题建议：入口与当前使用状态

核查时间：2026-11-25 09:43–09:47（Asia/Shanghai）。环境PROD，仅GET/SELECT/日志读取，无生成、部署或配置修改。代码引用基线47b3dcb7，仅用于解释路径；生产真实运行另以日志和表记录证明。

|维度|高中问题建议|素养问题建议|
|---|---|---|
|业务应用|256919247659254784，生成沟通建议-高中|256919351674848256，生成沟通建议-素养|
|agent|256918735665808384，问题建议-高中|256918818763359232，问题建议-素养|
|PROD存在状态|应用/agent isdel=0，platform_type=1（Dify）|同左|
|当前部门映射|default及10013518→生成沟通建议-高中|10012667→生成沟通建议-素养|
|真实调用|2026-11-25 08:53成功，数据库及生产日志交叉证明|按id倒序最近3条为2026-01-20 08:17–08:30，状态成功且有推荐文本|
|在用裁决|明确仍在使用，不能移出迁移范围|有历史使用，配置仍保留；近期未证实，不能直接认定下线|

## 在哪里

这是“履约沟通问题→推荐沟通话术”能力，不是降退费服务建议工作流：

1. CommunicationFulfillmentProblemConsumer接收沟通分析消息 → FulfillProblemService.hearNewAiCommunicationProblem/processAiCommunicationProblem，建立/更新履约问题。
2. triggerRecommendWordsGeneration受realTimeAnalysis控制，默认true；asyncRealTimeAnalysis默认true时发renewalAiFastRetrospectTopic_prod，FastRetrospectConsumer调AiRecommendWordsGenerator.generateRecommendWords。
3. Generator按班级部门映射选高中/素养应用，调用syncRequestTask，将recommendWords、strategy、score写入fulfillment problem的recommendInfo。
4. `/feign/fulfillProblem/overview`由FulfillProblemOverviewService读取recommendInfo，communicationAdvice来自recommendWords。另有`/feign/fulfillProblem/retrospect/regenerateAdvice`及推荐回溯/刷新MQ入口。未核实前端页面URL，不能凭后端功能名编造菜单位置。

代码定位：AiRecommendWordsGenerator.java:56/73/100；FulfillProblemService.java:47/394；CommunicationFulfillmentProblemConsumer.java:78；FulfillmentProblemRecommendFastRetrospectConsumer.java:87；FulfillProblemOverviewService.java:337；FulfillProblemRetrospectController.java:50。

## 配置与调用证据

PROD application已发布部门映射如表，ai.agent.accessor.override.map={}。realTimeAnalysis、asyncRealTimeAnalysis及effect开关在此次application查询未配置，按已读代码默认true；未宣称已回读所有生产实例内存或所有namespace。RetrospectConsumer.onlyTransfer=true表示转发fast topic，不是总停用。skipEmptyAccountSwitch默认true，缺助教账号可跳过，不代表功能下线。

高中entry_key=296209761863489536：生产trace `student-data-dws.4201.17955679943226466`，08:53:14开始、08:53:16构造7047字prompt、08:53:29插件处理并执行成功，响应状态message；数据库id82460817，call_status=1/result_type=1，结果包含recommendWords。安全日志见high-school-success-log-safe.json。

**状态口径纠正**：实体AiApplicationCallTaskResult的注释已过时。实际CallStatusEnum和createSuccess写入为0未调用、1成功、2失败，ResultTypeEnum为0未调用、1成功。初读“1失败”的判断撤回；不能把call_status=0查询结果当成功记录。报告附表保留原数值，按实际枚举解释。

素养最新id37138490、entry_key268213842803178496、时间2026-01-20 08:30:08；最近三条均状态1/1且有推荐文本。查询是全表按id倒序limit3，不是全时段调用量统计。近7天聚合（create_time>=2026-11-18）超时，工具提示异步查询；这不是0命中。因此仅能报告最近记录时间及未取得近期调用证据，不推断“从未调用”或“已正式下线”。若要将素养排除迁移范围，需要进一步确认运营停用口径或有效上游过滤/停用配置。

## 对迁移剩余项的影响

高中明确在用，指定库403是迁移验证权限问题，不是功能不存在。素养可降为“当前使用状态待确认”，不能凭403判定在用或下线。非知识库场景替换结论由主Worker结合既有逐场景证据整合，本报告不重跑且不扩展验收结论。

证据目录problem-suggestion-usage-current/：PROD Apollo、应用状态、脱敏调用元数据、成功日志、超时事实。原始推荐文本含学员信息，未复制到归档。无在途操作。
