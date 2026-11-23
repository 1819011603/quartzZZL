# 续班学部变体覆盖核对

2026-11-23当前只读查询；本轮无业务调用、无配置/代码修改。原调用基线91012878d。SOP普通compare旧模型已纠正为Seed-1.6，本轮不据旧错误口径讨论SOP。

## 分层：两学部模板相同，TEST只有default映射

已发布Apollo renewal.lift.reasoning.ai.agent.dept.map：
- PROD default/精品班学部 → 应用263057935240821760，agent263057785613229056（续班分层原因分析-高中）。
- PROD 综合素养学部 → 应用263080132187550720，agent263080101791455232（续班分层原因分析-素养）。
- TEST 仅default → 应用262173928596712448，agent262172718139452416（预测分层原因）。

名称虽叫ai.agent.dept.map，代码实际将value作为aiApplicationNumber使用，以上数字为应用编号。

两生产应用及TEST核心提示词均2641字符、SHA256前12位2a5153324fa5，逐字相同。完整prompt_config的core_prompt、after_processor_prompt_config、dependency_metadata_config均一致；差异仅名称/编号/版本元数据/时间。当前数据库证据department-{prod,test}-templates.json与full-templates.json。

Dify控制台当前“预测分层原因分析-高中/素养”配置相同：model=doubao/Doubao-1-5-pro-32k，provider=langgenius/openai_api_compatible/openai_api_compatible，completion_params={stop:[]}，pre_prompt为空、prompt_type=simple、chat_prompt_config及completion_prompt_config为空对象。详情文件department-dify-预测分层原因分析-{高中,素养}.json。此为配置读取，非生产实收；未进行生产调用。

TEST已验证样本可代表相同模板及旧别名的单次执行兼容性，但不能宣称两学部端到端均通过：TEST没有精品班/综合素养独立路由条目，只有default；两学部独立应用263057935240821760/263080132187550720未在TEST对应存在。实际特征数据、部门字段和重要性由业务上下文决定，单样本不代表两个学部数据分布。

## 画像/摘要：模板一致，Dify当前模型名不一致

|项目|PROD应用/agent|TEST应用/agent|核心模板|
|-|-|-|-|
|画像|256923739884667904 / 256917438512284672|255107395528688640 / 255107338300556288|2043字符，SHA256前12位1724b42dfa3e，相同|
|摘要|256923816171717632 / 257085994022484992|255551371814636544 / 255107338300556288|305字符，SHA256前12位9239b9facd83，相同|

两对完整prompt_config的core_prompt、after_processor_prompt_config、dependency_metadata_config逐字一致，仅名称/编号/版本元数据/时间不同。该结论是当前prompt_config表内容比较，不扩张为所有历史版本均一致。

Dify控制台“用户画像-prod”“沟通摘要-prod”当前直接使用doubao-seed-2-0-lite-260428；TEST共享应用“续班AI-用户画像&沟通摘要-test”仍为doubao/Doubao-1-5-pro-32k。两边completion_params均stop=[]、pre_prompt均空、prompt_type均simple；PROD chat_prompt_config含空system文本，completion_prompt_config为空文本/角色前缀；TEST这两个对象均空。配置无额外非空系统长指令。

因此TEST结果可支持模板内容无缺失，但不能直接代表生产直接模型名的redirect默认参数行为。旧别名可能注入thinking等默认参数，生产直接目标名可能不走同一规则；此项已有W1-d5f701负责，不重复修改或复验。

## 证据边界
当前Dify配置从团队列表按应用名称定位详情，与归档命名一致；本轮未通过生产API key调用/info再次核绑定，也未发生产推理请求。控制台配置不是LiteLLM实收。已完成TEST实收证据继续以此前报告为准，不将现在的配置读取倒推为之前调用时的全部状态。

证据目录内department-TEST-mapping.json及department-PROD-mapping.json保存已发布映射；department-dify-*.json保存控制台详情；department-*-templates.json保存当前模板及应用关联。无须重跑已有SOP/分层。
