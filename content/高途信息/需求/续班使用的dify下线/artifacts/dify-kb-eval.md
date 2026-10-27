---
title: 知识库应用（生成沟通建议）替换评估
tags: [需求, 评估]
---

# 知识库应用的替换评估（生成沟通建议-高中/素养）

## 现象
`问题建议-高中` / `问题建议-素养`（app 名「生成沟通建议-高中/素养」）是 **agent-chat + strategy=function_call**，且绑定了 Dify **知识库（dataset）**。Dify 源码里把知识库**注册成一个工具**（`DatasetRetrieverTool`，`api/core/agent/base_agent_runner.py:94-106`、`api/core/agent/fc_agent_runner.py`）交给模型；模型**自己函数调用**去检索 → Dify 做向量检索+rerank（`api/core/rag/retrieval/dataset_retrieval.py`）→ 把命中片段回灌。**不是**把知识库预塞进 prompt。

## 知识库来源：Teable 多维表格（结构化）
文档 `data_source_type = teable_import`：

| 应用 | dataset id | 来源 Teable | 字数 |
|-|-|-|-|
| 生成沟通建议-高中 | 5b040e52-8041-48af-b7d3-acefc14bc130 | table `tblwCEzNP29MGln9wBy`（库「沟通建议-高中」，空间「陈泽鑫的空间」） | 104052 |
| 生成沟通建议-素养 | a195df23-ba87-4ecb-b9f3-7d1c3a5a9b22 | table `tblR8u9192uk6eIq91H` | 4786 |

话术表字段（**结构化**）：
`问题类型`（如价格异议）/`用户问题分类-二级`/`用户问题例举`/`相似提问的不同提问方式`/`标准回复`/`标准回复中需要引用的数据或内容`/`评分得分上限`/`评分标准`/`适用课程`

## 评估：可结构化复刻，不必上向量检索
因为话术库是**按「问题类型 + 适用课程」编排的结构化表**，不是无结构文档：

- student-data **已有 Teable 取数能力**：`TableApiDataHolder`（`https://os.baijia.com/api/table/{tableId}/record`，Bearer token 走 Apollo）。
- 新链路可这样做：模型先判 **问题类型 + 适用课程** → 从 Teable 取对应「标准回复/评分标准」→ 拼进 prompt（等价于 Dify 的检索结果）。

## 方案对比
| 方案 | 说明 | 取舍 |
|-|-|-|
| A 结构化复刻（推荐） | 用 `TableApiDataHolder` 按问题类型/课程取话术，拼进 prompt | 复用已有能力；不需向量库 |
| B 复刻向量检索 | chunk+embed+ES+rerank | 重、没必要（数据本就有结构） |
| C 暂留 Dify | 这两个应用先不下线 | 违背下线目标；但零改造 |

## 结论
- 15 个无知识库应用：直接切（已验结构一致）。
- **2 个有知识库应用（生成沟通建议-高中/素养）**：需在 student-data 加一步「按问题类型/课程取 Teable 话术」，再拼 prompt；**推荐方案 A**。素养库仅 4.8K 字，甚至可直接内联。