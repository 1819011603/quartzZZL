# #4 回溯：续班服务「学员标签」历史数据回溯 —— 执行方案（**按知识库「大数据同步」口径修正**；未执行）

## 一、修正说明（本轮 owner 纠正）
- owner 指定：**#4 回溯的正确来源 = 从大数据同步过来的**，先查 Obsidian 知识库「回溯班级」。
- **命中出处**：`~/githubDir/quartzZZL/content/高途信息/文档/EES/洗数据 班级-学员加筛选字段.md`，章节 **「### 回溯班级-学员ES数据」**（含「大数据」「天工2」任务链 + handler/service + 字段集）。
- **修正理由**：原方案把机制只写成「速达 QuickBack type13」，并把它当唯一来源；实际**正确/官方来源是大数据(天工2)同步链 → `ees_data.clazz_back_task` → xjob handler → ES**。速达 QuickBack 仅是与大数据链**共用底层服务**的另一（ad-hoc）触发入口。据 owner 口径，**以大数据同步为准**。

## 二、大数据同步回溯机制（知识库原文摘要 + 代码核对）
**大数据侧任务链（天工2 `https://tiangong2.baijia.com/develop`）**：
1. `同步最近班级数据`（`sync_course_center_clazz_prod`）
2. `扫特定条件班级并排序`（`sync_clazz_back_task`）
3. `同步待回溯数据到mysql`（`sync_clazz_back_task_hive_to_mysql`）→ 落 `ees_data.clazz_back_task`
4. `执行回溯任务`

**落库表/实体（代码核对）**：
- `ees_data.clazz_back_task` ↔ `com.gaotu.student.data.infrastructure.dao.entity.ClazzBackTask`（`@TableName("ees_data.clazz_back_task")`）。

**执行（xjob handler）**：
- 续班/辅导班学员（=续班服务读源）：`BackSubclazzUserHandler` → `AdsSubclazzUserBackService#dealClazz` → 写 `ads_large_subclazz_user_index`
- 大班花名册学员：`backAdsClazzUserHandler` / `BackAllAdsClazzUserHandler` / `backDwsClazzUserHandler` → `AdsClazzUserBackService#dealClazz`
- 字段集（Apollo·student-data）：`ads.back.subclazz.user.fieldNames`（subclazz）/ `ads.back.clazz.user.fieldNames`（clazz，知识库示例 `["orderNumber","clazzRoomType"]`）

## 三、与「速达 QuickBack」的关系
- 速达 QuickBack（`ees_data.back_quick_task` + `quickBackJobHandler` + `quickBack*Worker`，skill `clazz-roster-es-backfill`）与大数据链**共用底层服务** `AdsSubclazzUserBackService#dealClazz`（type 13），但**触发/来源不同**：QuickBack 是 ad-hoc 单班/批班即时触发；大数据链是 hive→`clazz_back_task` **按条件扫班**。
- **正确来源=大数据链**；QuickBack 可作**单班抽检**辅助。

## 四、口径结论（据知识库）与仍缺项
- **触发/范围**：由大数据 `sync_clazz_back_task` 的**「特定条件班级」**决定 → PRD「班级创建时间20260101及以后」应是**该扫班条件**，即**口径由大数据任务参数确定**。
- **字段集**：需给 `ads.back.subclazz.user.fieldNames`（大班续班）补 `studentTags`（现状不含，代码/Apollo 已核）；小班对应字段集同理。
- **仍缺（需大数据/owner 确认，不擅自定）**：① `sync_clazz_back_task` 的**精确扫班条件**（是否=班级创建≥2026-01-01？含小班否？）；② `clazz_back_task` 表字段（班级/批次/状态）与「执行回溯任务」**具体触发哪个 handler**（subclazz ↔ clazz 的对应）。

## 五、确认后执行步骤（由我执行并回报）
1. Apollo(test) `ads.back.subclazz.user.fieldNames` += `studentTags`（回读）。
2. 由大数据按条件扫班落 `ees_data.clazz_back_task`（或我先用现成 QuickBack 抽 1-2 班辅助验证写入）。
3. 跑 xjob `BackSubclazzUserHandler` 执行回溯。
4. 回读 `ads_large_subclazz_user_index` doc `studentTags` 有值（输入/预期/实际/清理）。
5. **线上**：另行评估（字段集 Apollo PROD + 生产扫班）。

## 六、边界
- 未定口径前**不执行**；不改线上；不改前端。
