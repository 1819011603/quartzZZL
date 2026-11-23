# 续班扩大验证 2026-11-23

基线91012878d，test-gtbg-dev-1，只读worktree /private/tmp/student-data-xuban-review-20261123。未改代码、Apollo或业务库。

## 结论
画像、SOP、预测分层原因均完成非空样本双路调用和LiteLLM实收核对。分层强制JSON格式与提示词直接输出原因冲突，空/有效样本均复现，不能解释为输出随机性。分层已通过TEST配置修正并复验，见 tier-fix.md 与 thinking-followup.md；以下初始响应只用于说明修正依据。

|场景|traceId|覆盖|
|-|-|-|
|用户画像-test|2a9ff650-ba6f-4bf2-93f8-88034f864c93.0.3|真实问卷，三字段有值|
|服务SOP分析|e3197197-27eb-4b23-8b1e-2f8b83d16ff5.0.3|沟通及服务上下文，双路建议非空|
|分层首次|a711d06d-e6c2-4e8d-9160-afef54fc4099.0.3|空特征，不计有效覆盖|
|分层有效样本|3c9e6b70-e6f3-4f95-883b-14408cdafc2b.0.3|真实特征，双路原因非空|

业务入口全部TEST。每条trace查询PROD/SLS/app是Dify下游，TEST/SLS/app是迁移下游。*-received.json是service=litellm的Chat_completion request实收；logs保存response usage，usage.json提取8组用量。SOP首次TEST查询100条截断，后以AND "LiteLLM"补齐；service:litellm查询不支持，失败证据保留，最终按返回service字段核验。

## 提示词和参数
所有三场景新路system/user正文均逐字包含于旧路user包装内；具体差异见各*-prompt.diff及received.json。旧路为一条user消息，内部用伪JSON书写system/user；新路为真正system/user消息，角色权重改变。伪JSON内部换行和引号未转义，不能严格json.loads解析。

旧路画像/分层 model=doubao/Doubao-1-5-pro-32k；SOP model=doubao/Doubao-Seed-1-6、stream=true、有user；新路model=doubao-seed-2-0-lite-260428、max_tokens=8192、stop=[]、response_format=json_object，无显式stream/user。画像新路thinking=disabled，SOP和分层未显式thinking。旧模型别名结合redirect日志判断，不能只看名字认定不同模型。未传参数也不等于不存在路由或供应商默认值。

## 结构、语义与下游风险
画像两路均返回renewalInterest/renewalResistance/portraitSummary，识别物理学习困难、满意度7/7/8、续班仍有疑虑。单次措辞与摘要侧重不同，未证明质量统计相等。

SOP两路均有sopAnalysisItemList以及sopName/strategy/actionRecommend/score/maxScore。旧路有think前缀和代码围栏，仍需保留清洗兼容；未执行业务写回路径。

分层旧路直接输出原因，新路返回JSON对象“原因”。有效样本两路主要事实均为服务108天、完成度偏低、微信互动低、未预报名；旧路显示31.82%，新路0.318。提示词明确直接输出原因，不符合当前强制JSON格式。RenewalLiftReasonHandle调用tryToGetJsonAnswer后直接updateReasonBySubclazzAndUser，需确认对象字符串是否会直接展示；本子任务无权修改代码或公共Apollo。

## 样本与覆盖边界
首次用户7404351741仅有clazzNumber，分层上下文空。RenewalFeaturePromptDataClaimer按userId+subClazzNumber查特征。TEST表查询找到同班用户6761113627、辅导班31298462823089024，补齐后用户特征文本5601字符；证据tier-matching-sample.txt、tier-valid-*。未使用首条userId=3等占位记录作为有效样本。

高中/素养部门路由未覆盖：本次指定应用“预测分层原因”，没有按业务事件部门经aiAgentDeptMap选择“续班分层原因分析-高中/-素养”，不可外推两套部门应用均通过。该覆盖边界需主Worker合并整体报告。未重复原两例，未验证生产业务或最终供应商HTTP。
