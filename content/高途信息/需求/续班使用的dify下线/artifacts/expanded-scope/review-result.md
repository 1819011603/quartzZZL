# 迁移审查当前交付

## 结论
本轮不是“整体对等迁移”验收，而是按最新范围完成输入一致性审查：17 个生产应用中，问题建议高中/素养与降退费精品/素养 4 个有前置知识库/检索的应用保留 Dify；其余 13 个目标按 8 类场景核对 LiteLLM 实收。SOP V2 在测试 fixture 上完整 messages 一致；其余场景的具体差异、原因与可替换判断见下表和证据文件。素养 NPS 缺旧/新双侧 LiteLLM 实收，保留未验证；已核对生产绑定、TEST映射、模板差异并完成本地确定性生成，具体阻塞见 `../expanded-renewal/nps-suyang-evidence-boundary.md`。

范围：student-data feature-xuban-dify-offline，91012878，11文件diff；TEST test-gtbg-dev-1已部署。生产仅只读，没有代码修改/新commit/生产发布。原仓库其他需求现场保留。

## 已处理并验证

|对象|修正|运行证据|
|---|---|---|
|画像/摘要共享agent|TEST thinking.disabled，对齐旧1.5别名重定向|f059219f-2d7c-46c5-945e-fd3a9cdab509.0.3|
|预测分层原因|TEST response_format=text及thinking.disabled|最终7a05052d-9094-4a00-aa88-bf44dcf0eb61.0.3，releaseKey20261123193207-188aa6ecfba69670|
|降退费服务建议|TEST应用提示词变量改为引用user信息|25046ce3-eb13-43e3-88ae-78859fd34e33.0.3|
|素养服务建议|同上，业务正文与原实收相等|cd3eed1b-00db-4c9d-bdd4-a4cf7ad22c33.0.3|

以上配置和两行测试数据保留；独立回读均完成。未触发业务MQ/最终业务落值验证。模板修正不代表检索修复。

## 场景覆盖

- 画像、摘要：双路有效输入及实收已核对；旧flat转真实system/user。生产直接模型名与TEST旧别名不同，不能直接复制TEST默认参数结论。
- SOP：普通compare及真实V2历史fixture重放已验；V2单user 13647字相等，10项SOP。旧Seed-1.6两侧有推理，未错误关闭。未覆盖外围部门选择、知识表实时读取、去重和档案写回。
- 分层：真实非空特征样本已验，文本格式和思考模式已修正。高中/素养模板与TEST相同，TEST只有default路由，不冒称两学部端到端通过。
- 根因：双路实收已核对，长system保留；弱样本缺分类表/沟通ID，不能算枚举或落值验收通过。
- 旅程：一轮/一轮、当前样本无tools。保留2025年已存在的resolvedRefundReasonList契约及归档模板，但当前旧Dify未要求，明确为输入差异；不修改历史DTO消费逻辑。
- 课程体验、NPS：各一轮，业务user302字相等，去旧标签并提升输出指令角色。未覆盖跨班级NPS及所有学部映射。
- 降退费：旧2轮带dataset与2条tool结果，新1轮无tools，确定不对等。
- 素养服务建议：旧单system嵌业务正文，新system+user，正文保留、温度均0.7；本样本无工具，不混用降退费证据。

完整逐行diff及参数表：../expanded-refund/report-exact.md、../expanded-diff/report.md。实收参数存在model别名、stream、max_tokens8192、stop、user、response_format/thinking差异；未传不能当作默认相同。未完成长文本截断、耗时或多次质量统计，不声称性能/质量等价。

## Dify隐含能力与范围决定

降退费trace81e849b4-d461-4fd0-910a-154368d68bc0.0.3，旧首轮dataset工具，第二轮回灌1363/1152字话术。源码上下文只有根因/旅程，未读取话术，提示词注释不能替代实现。

dataset已通过Console导出全部69分段，源Teable表存在但直接record接口403；已尝试Console检索路径404。现有TableApi是组件复用机会，不是已完成退费检索实现。全量文本拼接不等于旧检索。

范围决定已落实：生产降退费精品/素养与问题建议高中/素养共4个应用保留Dify，本轮不建设替代检索、不改路由。生产发布仍未授权；后续发布前置仍包括生产DDL、路由与Apollo配置。

## 发布前置与证据边界

PROD gateway_core_prompt列实查不存在；Mapper无条件依赖此列，关闭迁移开关也不能规避，发布须先DDL。生产无授权修改。
Apollo模块{}语义为放开，T+N关闭不代表应用下线；未取得全量流量统计，不能确认每应用均活跃。生产未开迁移开关。TEST10应用不等于生产15目标应用；独立生产app映射及全量异步落值没有验证。

验证判断采用输入内容/角色/实际路由和默认参数、消费格式、事实与枚举；随机文案不要求一致。共有多用户措辞问题不归因迁移。提供商最终HTTP未观测，不影响本次已完成的LiteLLM层取证。

最新应用归属与计数见call-count-evidence.md及../expanded-refund/deprecated-binding.md；TEST废弃两轮不外推生产。

## 两项增量缺口的最终说明

素养 NPS 已完成实际取证尝试：生产绑定为 `261424803504732160 / 261424755557579776`，TEST 只有精品 NPS 映射和旧侧 trace `d2003cc1-b573-4e1c-8918-d3a4d162fe62.0.3`；已做 321 字素养模板的本地确定性消息生成，但没有旧素养侧 LiteLLM 实收。使用生产 app/key 会触发生产推理，当前授权不允许；复制模板到 TEST 也只能补新侧。缺少 TEST 素养 Dify 镜像或受控生产推理授权，因此该场景保持未验证。详见 `../expanded-renewal/nps-suyang-evidence-boundary.md`。

范围计数已核清：17 是原始生产 agent 应用数；15 是只排除问题建议高中/素养两项后的历史中间目标；13 是在此基础上再排除降退费精品/素养两项后的当前目标。原两项明确不迁包含在当前四项保留 Dify 应用内，详见 `scope-reconciliation.md`。
