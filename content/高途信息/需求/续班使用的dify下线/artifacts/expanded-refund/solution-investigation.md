
> 2026-11-24 机制与方案更新：Dify平台继续存在，可优先评估复用其独立检索API；旧文“必须自建/结构化过滤等价/平台无可用检索”的推断不再作为结论。生产前置检索与TEST废弃工具多轮不得混用。详见 kb-platform-reuse-plan.md（原归档artifacts/expanded-refund）。

# 降退费话术库遗漏：只读方案调查

## 已确认事实

1. 生产旧链路 trace `81e849b4-d461-4fd0-910a-154368d68bc0.0.3` 的首轮 LiteLLM request 携带 Dify function tool：
   `dataset_86233d1a_bddf_4a15_a229_c90b6a061c57`，描述为“降退费服务建议话术库，根据根因分类匹配对应的服务建议话术”。第二轮把 assistant tool call 与两条 tool 结果回灌后再生成建议。该 dataset 是旧链路的真实知识来源，不是提示词注释。
2. TEST 应用映射（已有 verify/handoff 证据）：
   - 通用降退费服务建议 agent `255743632420648960`，application `255743654696597504`；
   - 素养服务建议 agent `261423990261694464`，application `261424322528162816`；
   - 生产分别有精品/素养两个降退费应用（`256995156763347968`、`261424592068814848`），不能用一个 TEST 通用样例宣称十个生产变体均覆盖。
3. `student-data` 的 `RefundSuggestionServiceImpl#getReasoningContext` 实际只读取退费根因、退费旅程、上次服务建议；`buildFormatContent` 只拼接根因与旅程。源码中的“话术库”只是注释/提示词文字，没有话术表查询、Dify dataset ID、或工具回灌实现（源码：`student-data/student-data-service/src/main/java/com/gaotu/student/data/domain/refundless/reasoning/impl/RefundSuggestionServiceImpl.java:61-130`；Table API组件：`student-data/student-data-service/src/main/java/com/gaotu/student/data/domain/ai/business/fulfillProblem/service/TableApiDataHolder.java:30-120`）。
4. 仓库内确有 `TableApiDataHolder`，但它服务于履约问题推荐话术和 SOP 两条链路：`AiRecommendWordsGenerator` / `AiSopAnalysisGenerator` 读取 Apollo 的 `*.knowledgeBase` 配置，再请求 `https://os.baijia.com/api/table/{tableId}/record?viewId={viewId}`，带 Apollo token 并缓存。未检索到 `RefundSuggestionServiceImpl` 或 `refund.reasoning.*` 对该 holder 的引用，也未找到退费话术专用 table/view 配置。因此不能把现有 TableApi 当作已经可用的退费替代源。

## 最小可实施方案（需主 Worker/业务方决策后实施）

**方案 A：该场景暂保留 Dify（风险最小）**。继续使用旧降退费应用，保留 dataset 检索和多轮 tool 回灌；网关迁移验收中将降退费标为“未完成对等迁移”。依赖是旧 Dify app、dataset 及其访问凭证持续有效，无法满足彻底下线 Dify 的目标。

**方案 B：迁移话术库到 student-data/网关上下文（建议的最小替代方向）**。先从 Dify dataset 导出完整记录，按精品/素养分别落地为受控数据源；新增退费专用 table/view 或数据库表及 Apollo 的只读 table/view 映射；复用 `TableApiDataHolder` 的 HTTP、缓存、超时和错误处理，但新增 RefundSuggestion 专用 adapter，在生成网关 userQuery 前按根因/退费旅程检索并注入“匹配话术”内容。需要保留学部映射，至少覆盖 `256995156763347968` 与 `261424592068814848` 两个生产 app；先在 TEST 两个 agent 逐 app 比对同输入的命中记录与输出，再考虑删除 Dify 路由。

方案 B 的真实前置依赖：Dify dataset 全量导出与字段语义确认、精品/素养分类规则、table/view 或 DB 数据源审批、Apollo 映射发布、检索排序/命中阈值、空命中和超时降级策略、提示词长度预算，以及旧 Dify 两轮 tool 结果的回归样本。当前仓库没有这些数据或配置，不能直接实施，也不能把迁移后的单轮 JSON 结果标成等价。

## 结论

当前 student-data 没有可直接复用且已配置的退费话术检索能力；现有 TableApi 仅证明技术组件可复用，不能证明数据源或学部覆盖可复用。若不实现方案 B，降退费应继续保留 Dify，迁移状态明确标注“话术库能力缺口”。

## Dify dataset 只读复核（2026-11-23）

通过本机 Cookie 代理调用 Dify Console API：

- `GET /dify/api/console/api/datasets/86233d1a-bddf-4a15-a229-c90b6a061c57/documents?page=1&limit=100` 成功，返回唯一文档 `ed0e3608-ca60-4007-bd00-b6e1d361d423`，`has_more=false`；文档名 `刘家良的空间_降退费服务建议话术库_话术库_20250915043012`，`data_source_type=teable_import`，`tokens=52358`，`segment_count=69`，`indexing_status=completed`，`enabled=true`。
- 文档来源元数据：Teable space `spczjG62GXkZ0ZSOBYS`、base `bseaeMwt2N0dqxUI7c8`、table `tblf6HnwVYpJzy8wVlu`，空间“刘家良的空间”、base“降退费服务建议话术库”、table“话术库”。
- `GET /documents/{documentId}` 显示 Dify 分段规则：`remove_extra_spaces=true`、`remove_urls_emails=false`、分隔符双换行、`max_tokens=1024`、`chunk_overlap=50`，`doc_form=text_model`、中文；`GET /documents/{documentId}/segments?page=1&limit=100` 返回 `total=69,total_pages=1`，全部分段可读。完整脱敏导出保存为 `dataset-export-sanitized.json`，原始元数据/分段响应保存为 `dataset-document-detail.raw`、`dataset-documents-page1.json`、`dataset-metadata.json`。
- 分段内容是结构化话术记录（序号、一级分类、二级分类、建议话术逻辑/具体话术），统计到 9 个一级分类、至少 20 个二级分类；样例含“服务不满意-沟通答疑及时性”“服务不满意-未解决客户问题”等，能覆盖本次合成输入的反馈慢/个性化不足方向。数据按 Dify 1024 token 分段，不能直接把 69 段全文拼入 userQuery 视为等价检索。
- 直接请求 Teable `https://os.baijia.com/api/table/tblf6HnwVYpJzy8wVlu/record`（不带外泄 token）返回 `403 restricted_resource / no permission to access this base`；Dify Console 分段可读但当前登录态无法直接读取源表记录。Console dataset `/retrieve`、`/search` 路径返回 404，未发现可直接复用的检索接口。故“数据现成存在”已确认，“student-data 可直接按分类读取源表”尚未确认。

这修正了前文“没有退费话术数据源”的表述：准确结论是 **Dify 已有现成、已完成索引的退费话术 dataset；student-data 尚未接入，且当前 Teable 源表权限/检索 API 不可直接复用**。长期方案仍需取得 Teable 只读授权或从 Dify segments 导出后落受控源，并复刻 Dify 的分类/语义检索与分段命中策略。
