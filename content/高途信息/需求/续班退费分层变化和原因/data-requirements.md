---
title: 续班退费分层变化和原因 · 冒烟阻塞与造数需求
tags: [需求, 测试, 造数]
---

# 造数/补验需求

本轮 23 条冒烟用例中 2 条阻塞，均**不是数据缺失**，而是**验证入口缺失**（前端/CRM 页面无法在指定泳道打开）。列此备查。

## 阻塞清单

| 用例 | 一句话缺什么 |
|---|---|
| TC-G007 / TC0001(I) | 需在能渲染的 CRM「学情跟进-续报」页面上确认旧「预测原因」模块不再展示、且旧接口不再被调用 |

## 非阻塞但建议补的活数据 fixture（提高置信度）

| 用例 | 现状 | 建议 |
|---|---|---|
| TC0004(A) 无变化不展示 | 靠单测 `should_skip_when_levelUnchanged` | 造一名「未超期 + 连续两天同分层」学员，跑 `SyncPredictLevelReasonHandler` 验证第二天空变化点不落库 |
| TC0002(G) 六种下降组合 | 靠扫描谓词 `predict_level > pre_predict_level` | 造 6 名学员覆盖 A→B/C/D、B→C/D、C→D，跑 `RenewalLevelDownNotifyHandler` 核对 6 条内容与收件人 |

---

### TC-G007 / TC0001(I) 旧「预测原因」模块下线

#### 为什么跑不了
- 该条的被测点是 **CRM「学情跟进-续报」页签不再渲染旧「预测原因」模块**，属前端/CRM 页面行为，后端没有"页面不展示"的可调方法。
- 已穷举的候选验证入口：① 真实浏览器打开 EES/CRM 页面——GAIA 组件**无泳道概念**（CDN 只有一份共享构建），真实用户流量落到 release/base 池，拿不到只发布在 `test-eco-2` 的后端分支，会 404；② 直调后端接口——只能证明接口存在/返回数据，不能证明前端已移除旧模块；③ 前端仓库 `aianalysisinformations` 源码——本机未克隆，GitLab API 亦不可达。
- 后端侧能给的替代证据：student-center `FieldsConvertDataQueryServiceImpl` / `RefundFiledConvertDataQueryServiceImpl` 已改为**优先读 `renewalIntentionPredictLevelResult`（新分层列）**，缺失才回退老分数换算，说明 EES 展示口径已切到新链路。

#### 要造的数据
- 无需 DB 造数。需要的是**可验证入口**：
  - [ ] 把 `feature-predict-level-reason` 后端合入 release 池，或在测试环境拿到可在真实浏览器注入 `traffic-env: test-eco-2` 的通道
  - [ ] 前端仓库 `gaotu-fe/gaotu-btech-fe/gaia-widget-submodule/aianalysisinformations`（分支 `feature-refund-reason-20260825`）的源码只读访问，或其对 CRM 学情跟进-续报页签的改动 diff

#### 验收步骤
1. 打开 CRM 学员详情 → 学情跟进-续报，确认旧「预测原因」模块节点不存在、无空白卡片/布局错位。
2. Network 面板确认不再发出旧「预测原因」接口请求。
3. 切到 学员详情-AI分析-续班，确认新的分层原因卡与旧模块两处不重复展示。

#### 注意事项
- 前端组件无泳道；要联调必须让后端分支进 release 池，否则真实浏览器必然 404（参考 README「已知问题 2026-09-29」）。
