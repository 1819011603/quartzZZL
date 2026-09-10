# 链接中心 · 续班归因

## 需求 / 方案
- 【PRD】未续归因和跟进+已续归因（飞书）
- 【续班优化】未续归因和跟进+已续归因 —— 技术方案（飞书）
- TAPD 迭代：https://www.tapd.cn/tapd_fe/22531521/iteration/card/1122531521001014662?q=095ef2ff52bc60f5e881c83e43e109de

## 测试
- banshan 用例集 171：https://qa.baijia.com/banshan/#/case/caseList/171
- 用例编号 48758（续班归因/未续归因）

## 数据
- 归因结果表：`ees_data.ai_app_clazz_user_scene`（cluster_id 336）
- 网关调用留痕：`ees_data.ai_application_call_task`（cluster_id 336）
- 班级级任务表：`ees_data.ai_renewal_attribution_follow_clazz_task`
- 花名册 ES 索引：`ads_large_subclazz_user_index_v3`

## 代码
- 仓库 `student-data`，分支 `feature-xuban-ai`（已上线合入）
- 核心包 `com.gaotu.student.data.domain.renewal.reasoning`

## AI 应用编号
- `288169360313290752` —— 未续归因 `UNRENEWED_REASON_AI`
- `288169360792524800` —— 已续归因 `RENEWED_REASON_AI`
