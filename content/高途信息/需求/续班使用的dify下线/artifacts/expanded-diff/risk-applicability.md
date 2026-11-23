# 五项静态风险适用性核对

核对时间：2026-11-23；代码对象 `91012878d692119e79fb7d14baa1bab594c9534d`。未使用当前工作区分支代码代替部署版本，未调用业务/数据库/配置接口，未改公共文件。配置和数据库状态仅引用已有快照，不声称实时状态。

## 范围
本次TEST 10应用：用户画像-test、沟通摘要-test、服务SOP分析、预测分层原因、退费根因分析、退费旅程分析、退费课程体验分析、退费NPS分析、降退费服务建议、素养服务建议。前两项共用一个agent，Apollo快照共9项。不要与PROD“素养+精品班退费10应用”混为同一集合。

|风险|本次适用性结论|证据与边界|
|---|---|---|
|params.stream=true导致SSE按JSON解析|仅潜在配置风险，未发现本次命中|`trace-recheck-20261123/dify-override-after.json`九项params均无stream；旧Dify下游stream=true不等于新调用启用流式。`LlmGatewayAccessor#buildRequestBody`允许额外stream覆盖，`query`随后JSON.parseObject完整body，确有潜在不兼容，但不能据此要求当前紧急修复。|
|显式prompt不注入gatewayCorePrompt|SOP业务存在该代码路径；未证明本次缺指令。退费路径已排除|唯一业务调用者`AiSopAnalysisGenerator:143`调用syncRequestTaskV2；先在117行generate原core prompt。SOP既有归档称core指令在student-data，故不注入gatewayCorePrompt并不自动意味着丢指令。其应用由departmentAiApplicationConfig动态选定，本轮证据未锁定当前部门映射，不能声称实际流量已走该路径。|
|空gatewayCorePrompt静默回退|续班类是预期行为；6退费应用已有非空证据，未发现空值触发|`expanded-scope/handoff.md`记录TEST查库确认6退费非空；`verify.md:113`表列长度2254/2482/2381/473/1412/1412。用户画像/摘要、SOP、分层本身core有指令，回退合理。若未来退费数据迁移漏填仍有风险，但不能将其写成已发生。|
|DDL无条件依赖|所有10应用实际依赖；TEST已有满足证据，PROD尚未由本轮证实|Mapper Base_Column_List含gateway_core_prompt，不受迁移开关保护。TEST既有查库非空与已成功应用加载支持该列存在。`verify.md:125`仍记PROD需DDL工单，属于历史待办记录，不足以断言现在缺列或已加；生产发布前需要当前表结构证据。|
|compare两次动态取数|10应用对比入口均存在非冻结机制，但不等于10应用数据都变化|compare先后两次runWithPlatform→syncRequestTask→executeCoreLogic→generatePayload→getDataPrompt→dynamicDataParser.getDynamicData；每侧重新查询聚合与依赖。实际变化取决于依赖配置/数据写入。已核对原续班与退费两例user逐字符一致，不能声称这两例出现数据漂移；也不能用相同context证明其他例输入相同。|

## 调用图与误判纠正

代码路径均相对于部署提交的`student-data-service/src/main/java/com/gaotu/student/data/`：

- `domain/refundless/reasoning/RefundReasoningService.java:214` → `syncRequestTask(traceToken, command, Maps.newHashMap(), gson.toJson(refundReasoningContext))`。第4参数是extraInfo，查询内容已由`command.setUserQuery(refundReasoningContext.getContent())`设置。
- `domain/ai/core/AiApplicationExecutor.java:98` 的同步入口和`:196`异步入口均进普通executeCoreLogic；`:252`之后解析覆盖并将gatewayCorePrompt交给generatePayload。退费并未绕过该逻辑。
- 全提交搜索`syncRequestTaskV2/executeCoreLogicV2`，除定义与内部调用外，唯一外部调用为`domain/ai/business/fulfillSop/core/AiSopAnalysisGenerator.java:143`。
- SOP业务：generate(core+用户数据) → actualQueryPrompt → MD5判断 → syncRequestTaskV2 → ofFlat → 网关单user。
- SOP compare：runWithPlatform → 普通syncRequestTask → generatePayload → 网关system/user。

**需主Worker纳入覆盖结论：SOP compare并未覆盖真实业务的消息角色结构。** 这是已确认的代码入口差异，而不是已确认的生产损坏；无需把gatewayCorePrompt强行注入SOP。是否需要同入口补验，由主Worker结合当前扩围计划决定。

## 配置证据等级

1. 已直接读取：`trace-recheck-20261123/dify-override-after.json`九项agent配置，未发现stream。该快照包含已修正的画像/摘要thinking.disabled。
2. 已复用主Worker查库记录：`expanded-scope/handoff.md`关于10应用映射与6退费非空；本轮未重复查库，不能作为独立最新数据库审计。
3. 历史说明：`verify.md`列出的DDL与提示词长度。可定位迁移设计与既有状态，不替代生产当前DDL核验。
4. 原两例逐字符对比：本目录`renewal-user.diff/refund-user.diff`均标相等；这支持两例无可见user漂移，不证明Dify/网关所有参数相等。

## 处置建议与完成边界

五项中未发现本次已有配置直接启用stream、退费空system、TEST缺DDL的证据；不宜将潜在风险直接修成业务代码变更。真实确定的新发现是SOP业务V2与compare普通入口不同，需要在整体报告中明确覆盖缺口。PROD DDL是发布前需取当前证据的项目，本任务不涉及上线。报告完成的是五项适用性只读核对，不代表其他场景运行验证完成。
