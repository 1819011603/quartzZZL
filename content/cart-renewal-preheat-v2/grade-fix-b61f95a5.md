# 换年级缺陷修复实测闭环（commit b61f95a5）

## 老链路归因分析（2026-11-19）

baseline `1f5a9118` 的 `productSelectGrade` 与当前 HEAD 字节一致，三段行为：

| 段 | 老链路行为 |
|---|---|
| 写入 | `renewalNumber=request.getRenewalNumber()`，始终写在入参计划号下 |
| 删除 | 只按入参计划号删 `user_renewal_clazz`，无从计划号 |
| 读取 | `listUserRenewalGrade(userId, renewalNumber)` 按当前计划自身号查 |

老链路无主从合并，各计划写读同号，完全自洽。

## 两个缺陷归因

| 缺陷 | 归因 |
|---|---|
| 合并页切从计划年级不生效 | V2 引入的回归——V2 合并展示后前端仍传主计划号，写读 key 不一致 |
| 换年级未清从计划换课/勾选 | f6c12222 连带引入——clazz 记录落从计划号，但删除仍只按主计划号 |

## 修复内容（commit b61f95a5，2026-11-19 09:14）

### RenewalV2PureRenewalService：新增 `resolveAllSubPlanNumbers`

返回主计划所有有效从计划号（`resolveActiveSubs` 的 keySet）；关联查询失败降级返回空列表，换年级不因此失败。

### RenewalService.productSelectGrade：重写

- **写入侧**：`resolveCourseOwnerPlan` 按前置课反查所属从计划号，年级记录落正确计划号
- **删除侧**：遍历 `resolveAllSubPlanNumbers` 结果，同步清除各从计划号下 clazz 和 grade 记录
- **缓存失效**：失效主计划及所有从计划预热 key
- **读取侧**：不改

### 单测：ProductSelectGradeSubPlanKeyTest（4 项）

1. `should_storeGradeUnderSubPlan_when_gradeChangeOnSubEntry` — 从计划年级落从计划号
2. `should_deleteSubPlanClazzRecords_when_gradeSwitch` — 换年级清从计划 clazz 记录
3. `should_storeUnderMainPlan_when_noRelatedPlan` — 无关联单计划回归
4. `should_fallbackToMainPlan_when_relatedQueryFails` — 关联查询失败降级

## 编译与单测

- 编译：`mvn clean install -pl cart-app -am -Dmaven.test.skip=true` 通过（无输出）
- 单测：`ProductSelectGradeSubPlanKeyTest` 4/4 通过；`ProductSelectConfirmSubPlanKeyTest` 5/5 通过；合并跑 9/9 全绿

## 部署（TEST test-eco-8）

- pipeline 1352959，构建 SUCCESS
- pod `cart-gaotu100-com-9b78b7c6-5dnjf`，IP 10.218.250.14，commit b61f95a5，eureka UP 09:28

## 实测闭环

### 场景1：缺陷①修复验证（从计划年级落从计划号）

请求：`productSelectGrade(renewalNumber=591020372877623296, beforeCourseNumber=591020433489467392, grade=11)`，userId=7746793735

回读 `user_renewal_grade`：
- row 729：`renewal_number=591020374322561024`（从计划号），`grade=11` ✅

### 场景2：缺陷②修复验证（换年级清从计划 clazz 记录）

前置：写入 clazz 记录 row 1482（`renewal_number=591020374322561024`，从计划号）

请求：`productSelectGrade(renewalNumber=591020372877623296, beforeCourseNumber=591020433489467392, grade=15)`

回读：
- `user_renewal_clazz` 0 条（row 1482 已删）✅
- `user_renewal_grade` row 730：`renewal_number=591020374322561024`，`grade=15` ✅

### 场景3：老链路回归（无关联单计划）

请求：`productSelectGrade(renewalNumber=591020374322561024, grade=10)`（从计划无 relatedRenewMasterNumbers）

回读 `user_renewal_grade` row 731：`renewal_number=591020374322561024`，`grade=10` ✅（落入参号，老链路行为不变）

## 清理恢复

验证后通过 acl 桥调 `UserRenewalClazzRepositoryImpl#deleteGrade` 清除测试记录：
- `renewal_number=591020374322561024`，userId=7746793735：deleted=1
- `renewal_number=591020372877623296`，userId=7746793735：deleted=0（无记录）

回读两表均 0 条 ✅

## 飞书文档更新

`EaKXdTkzXoJTStxBJH3cX7Qinzh`「接口与交互扫尾清单」：
- 编号 7（换年级主计划页→从计划年级）：🔴 问题证实 → 🟢 已修复并实测生效（commit b61f95a5）
- 编号 7b（换年级不清空从计划操作记录）：🔴 问题证实 → 🟢 已修复并实测生效（commit b61f95a5）

revision_id 110 回读确认 ✅

## Apollo 状态

TEST 三开关全 true（release 438174，2026-11-18 16:45）：
- `renewal.recommend.v2.enabled` = true
- `renewal.preheat.v2.enabled` = true
- `preheat.cache.enabled` = true
