# #4 回溯：续班服务「学员标签」历史数据回溯 —— **最终方案**（按「开始时间」圈班 → 更新班下学员；**未执行**）

> 未执行回溯、未改线上。最终口径：时间判据=**「开始时间」**；范围=**班级开始时间 = min(课节 `begin_time`) ≥ 2026-01-01**（PRD 原日期）。

## 〇、最终口径（owner + PRD）
- **时间字段**：owner 把「创建时间」改为**「开始时间」** → 落在**课节开始时间** `begin_time`。
- **范围判据**：**班级开始时间 = `min(课节 begin_time)` ≥ 2026-01-01**（**日期取 PRD 原值 2026-01-01**，owner 未改日期；标注「按 PRD 取值、起点如需 owner 可再确认」）。
- **机制**：**圈班 → 更新班下的学员**（owner）。
- **模式**：课节线**不额外按模式过滤**（owner：含小班=学员维度；圈班→更新班下学员）。如只想要续班服务范围，加模式过滤为**可选**。
- **字段集**：`studentTags` 仍需补；**不补 `clazzRoomType`**（owner：无用）。
- 不执行回溯、不改线上。

## 一、「开始时间」对应字段/表（已定位，事实）
- **✅ 唯一来源 = 课节开始时间 `begin_time`**：表 `fairy_data_center.ods_gaotu_clazz_lesson_df`（tableId **23010**，注释「班级课节数据」，`begin_time` comment=「课节开始时间」）。
- ❌ 班级表 `fairy_data_center.ods_service_sync_course_center_clazz_df`（tableId **25427**，新班级表）**无结构化「开始时间」列**——只有 `create_time`/`update_time`/`publish_time`/`end_sale_time`/`off_time`/`down_time`；「上课时间」仅文本 `time_desc`/`clazz_date_desc`/`clazz_time_desc`。
- 故「班级开始时间」用**该班最早课节 `begin_time`（= `clazz_begin`）**表示。
- （`02_sync_clazz_back_task`(29774)/`sync_clazz_by_category`(32542) 用的是班级 `create_time`=**创建时间**，不是「开始时间」，不属本口径。）

## 二、圈班任务：推荐 + 差异（大数据侧执行项）
两者都写 `fairy_data_center.ods_service_clazz_back_task_df`（分区 `dt`，tableId 25830）→ `03_sync_clazz_back_task_hive_to_mysql`(29789) → `ees_data.clazz_back_task`。

**A. `sync_clazz_back_task_by_clazzlesson`**（taskId **36654**，"通过课节扫回溯班级"）——现配：
```sql
INSERT overwrite table fairy_data_center.ods_service_clazz_back_task_df partition(dt='<日期>')
SELECT 0 as id, tmp.clazz_number, ..., tmp.clazz_begin as batch_number, tmp.create_time, tmp.update_time
FROM (SELECT clazz_number, min(begin_time) as clazz_begin, min(create_time) as create_time, max(update_time) as update_time
      FROM fairy_data_center.ods_gaotu_clazz_lesson_df WHERE dt='<日期>' group by clazz_number) tmp
WHERE tmp.clazz_begin >= '2024-01-01 00:00:00'   -- ← 需改起点为 2026-01-01
ORDER BY tmp.clazz_begin DESC;
```

**B. `sync_clazz_back_task_by_clazzlesson_time`**（taskId **42118**，"通过课节扫回溯班级"时间段版）——现配：
```sql
... FROM (SELECT ... FROM ods_gaotu_clazz_lesson_df
          WHERE dt='<日期>' AND begin_time >= '2026-03-01' AND begin_time <= '2026-03-20'
          group by clazz_number) tmp ...
```

**差异**：
| | 36654（累积型） | 42118（时间窗口型） |
|---|---|---|
| 条件位置 | **聚合后** `min(begin_time)=clazz_begin >= 阈值` | **聚合前** `begin_time BETWEEN 起 止` |
| 语义 | 「班级最早课节 ≥ X」的**班**（班级级开始时间阈值） | 「**存在**课节 begin_time 落在窗口」的班（课节级窗口） |
| 适用 | 一次性圈出「班级开始时间 ≥ 目标日」的全部班 | 按课节开始时间**窗口**增量/补数 |

**推荐**：目标口径是「**班级开始时间 = min(begin_time) ≥ 2026-01-01**」→ **用 A（36654），把起点 `2024-01-01` 改为 `2026-01-01`**（其语义与口径完全对齐）；B（42118）适合按时间窗增量补数，非首选。
> **调整任务 SQL 属大数据侧执行项**：责任人 **`lichenhao02`**（课节任务创建人）/ **`闫旭`**（`ods_gaotu_clazz_lesson_df` 与 `ods_service_clazz_back_task_df` 创建人）。我方**只出方案，不改大数据任务、不跑任务**。

## 三、执行链（口径）
1. **圈班**（大数据）：按 §二 A（起点改 2026-01-01）`INSERT overwrite ... ods_service_clazz_back_task_df`。
2. **落库**：`03_sync_clazz_back_task_hive_to_mysql` → `ees_data.clazz_back_task`。
3. **更新班下学员**（xjob，EES/student-data）：`BackSubclazzUserHandler` → `AdsSubclazzUserBackService#dealClazz` → 写 `ads_large_subclazz_user_index`（`shardingKey = userId + subclazzNumber`，**学员维度**）；小班 `backAllAdsSmallClazzUserHandler` → `ads_small_clazz_user`。
4. **字段集**（EES Apollo）：补 `studentTags`。

## 四、外部依赖清单（谁做什么）
| # | 事项 | 负责 | 需要时机 |
|---|---|---|---|
| D1 | 圈班任务 SQL 起点改 **2024-01-01 → 2026-01-01**（36654），或改用 42118 设 `[2026-01-01, ∞)`；跑任务落 hive 表 | **大数据侧 `lichenhao02` / `闫旭`** | 回溯执行时 |
| D2 | `hive_to_mysql` 同步到 `ees_data.clazz_back_task` | 大数据侧（同上） | 圈班后 |
| D3 | Apollo(test/prod) 补 `studentTags` 到 `ads.back.subclazz.user.fieldNames` + `ads.large.subclazz.user.fieldNames` | **EES/student-data（本 worker 域，需授权）** | 回溯前 |
| D4 | 跑 xjob `BackSubclazzUserHandler`（大班续班）+ `backAllAdsSmallClazzUserHandler`（小班） | EES/student-data | 字段集+落库后 |
| D5 | 回读 `ads_large_subclazz_user_index` / `ads_small_clazz_user` doc `studentTags` 有值 | 本 worker | 执行后 |
| D6 | **线上**：PROD 字段集 Apollo + 生产圈班 | 待授权（上线待办） | 上线时 |

## 五、字段集（仍需补）
- **补 `studentTags`**：`ads.back.subclazz.user.fieldNames`（取数）+ `ads.large.subclazz.user.fieldNames`（写 ES）当前**均不含**（Apollo TEST 回读）；小班 `ads.small.clazz.user.full.fieldNames` 已含。
- **不补 `clazzRoomType`**（owner 判断无用）。

## 六、仍不确定点
1. **起点日期**：本方案取 **2026-01-01（PRD 原值）**；owner 若想改（如按最新批次），需 1 句话确认。
2. **用 36654（推荐）还是 42118**：取决于大数据跑批习惯（累积全量 vs 时间窗增量）——建议 36654，最终由大数据定。
3. **是否只留续班范围**：课节线无 `clazz_room_type` 过滤 → 圈班含全模式（大班/小班/1v1）；按 owner 不额外过滤，如只要续班范围再按模式过滤（可选）。

## 七、边界
- 未获授权前**不执行**；不改大数据任务；不改线上；不改前端。
