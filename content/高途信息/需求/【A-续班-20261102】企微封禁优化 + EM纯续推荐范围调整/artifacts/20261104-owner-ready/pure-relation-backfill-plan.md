# #4 回溯：续班服务「学员标签」历史数据回溯 —— 执行方案（**圈班→更新班下学员；扫班 SQL 已从大数据侧查证；未执行**）

> 未执行回溯、未改线上。本文收敛「回溯范围/触发」口径与来源。

## 〇、owner 最新口径（2026-11-04 原话）
> 「a 你去大数据看啊；b 圈班 更新班下的学员。。c 不需要吧 看没啥作用；5 现在不执行 记上线待办」

- a) **扫班 SQL 去大数据侧查** → 本轮已从天工2 查到（见 §二）。
- b) **口径 = 圈班 → 更新班下的学员**（先按条件圈出班级，再回溯这些班下的学员）→ 见 §三。
- c) **不补 `clazzRoomType`**（owner 判断无用）→ 已从字段集建议移除。
- 「ES 更新时间也行」（上一轮）：时间判据可用 ES `updateTime` 替代班级创建时间。

## 一、大数据同步链（知识库 + 大数据侧核对）
`sync_course_center_clazz_prod`（同步最近班级）→ 扫班任务（圈班，见 §二）→ `sync_clazz_back_task_hive_to_mysql`（同步待回溯数据到 mysql → `ees_data.clazz_back_task`）→ xjob 执行回溯（更新班下学员）。

## 二、扫班 SQL（大数据侧查证，天工2 projectId=216）
> 查证入口：天工2 `dataDevelop/getHive`（Hive 任务源码，form `taskId`）。**以下 4 个任务均 `INSERT overwrite` 同一张 hive 表 `fairy_data_center.ods_service_clazz_back_task_df`**（= 圈出的待回溯班），落表后由 `03_sync_clazz_back_task_hive_to_mysql` 同步到 `ees_data.clazz_back_task`。
> （hive 表 `fairy_data_center.ods_service_clazz_back_task_df`，tableId 25830，分区 `dt`，字段 `id/clazz_number/jiaoyan_status/clazz_user_status/lesson_user_status/batch_number/create_time/update_time`。）

**① `02_sync_clazz_back_task`**（taskId 29774，"同步回溯班级"，Hive）：
```sql
INSERT overwrite table fairy_data_center.ods_service_clazz_back_task_df partition(dt='<日期>')
SELECT 0 as id, number as clazz_number, 0 as jiaoyan_status, 0 as clazz_user_status,
       0 as lesson_user_status, create_time as batch_number, create_time, update_time
FROM fairy_data_center.ods_service_sync_course_center_clazz_df
WHERE dt='<日期>' AND publish_status=40
      AND create_time >= '2019-01-01 00:00:00'
      AND clazz_room_type=1 AND operation_mode=1
ORDER BY create_time DESC;
```
→ 条件：**售卖中(`publish_status=40`) + 大班(`clazz_room_type=1`) + `operation_mode=1` + 班级创建时间≥2019-01-01**。

**② `sync_clazz_by_category`**（taskId 32542，"根据课程品类确定回溯班级"）：
```sql
INSERT overwrite table fairy_data_center.ods_service_clazz_back_task_df partition(dt='<日期>')
SELECT DISTINCT 0 as id, a.number as clazz_number, ... a.create_time, a.update_time
FROM (SELECT * FROM fairy_data_center.ods_service_sync_course_center_clazz_df WHERE dt='<日期>') a
LEFT JOIN (SELECT * FROM service_dw.ods_course_center_course_category_map_df WHERE dt='<日期>') b
       ON a.course_number = b.course_number
WHERE a.publish_status=40 AND a.create_time > '2021-01-01 00:00:00'
      AND a.clazz_room_type=1 AND a.operation_mode=1 AND b.category_id_path LIKE '811330%'
ORDER BY a.create_time DESC;
```
→ 条件同上（大班），另加**课程品类 `category_id_path LIKE '811330%'`**。

**③ `sync_clazz_back_task_by_clazzlesson`**（taskId 36654，"通过课节扫回溯班级"）：
```sql
INSERT overwrite table fairy_data_center.ods_service_clazz_back_task_df partition(dt='<日期>')
SELECT 0 as id, tmp.clazz_number as clazz_number, ..., tmp.clazz_begin as batch_number, tmp.create_time, tmp.update_time
FROM (
  SELECT clazz_number, min(begin_time) as clazz_begin, min(create_time) as create_time, max(update_time) as update_time
  FROM fairy_data_center.ods_gaotu_clazz_lesson_df WHERE dt='<日期>' group by clazz_number
) tmp
WHERE tmp.clazz_begin >= '2024-01-01 00:00:00'
ORDER BY tmp.clazz_begin DESC;
```
→ 按**课节开始时间(`begin_time`)≥2024-01-01**扫班；**无 `clazz_room_type` 过滤**（可能含小班）。

**④ `sync_clazz_back_task_by_clazzlesson_time`**（taskId 42118，"通过课节扫回溯班级"，时间段版）：
```sql
... 同 ③，WHERE dt='<日期>' AND begin_time >= '2026-03-01 00:00:00' AND begin_time <= '2026-03-20 00:00:00' ...
```
→ 按**课节 begin_time 落在指定时间段**扫班（存的是手工填的时间段）；**无 room_type 过滤**。

**小结（事实）**：扫班条件 = `publish_status=40` + `operation_mode=1` + 大班主线 `clazz_room_type=1`（`02`/`by_category`）或课节线按 `begin_time`（`by_clazzlesson*`，无 room_type）；时间维度是**班级创建时间(`create_time`)** 或 **课节开始时间(`begin_time`)**。→ 与 owner「**圈班**（这些 Hive 任务 INSERT overwrite 圈出班级）」完全对应。

## 三、口径：圈班 → 更新班下的学员（owner 定）
1. **圈班**：大数据按 §二任一 SQL `INSERT overwrite ... ods_service_clazz_back_task_df`（圈出待回溯班级）。
2. **落库**：`03_sync_clazz_back_task_hive_to_mysql` 把该 hive 分区同步到 `ees_data.clazz_back_task`（表 = 班级/批次/各回溯状态）。
3. **更新班下学员**：xjob 按 `clazz_back_task` 的班级回溯其**学员数据**：
   - 续班/辅导班学员（= 续班服务读源）：`BackSubclazzUserHandler` → `AdsSubclazzUserBackService#dealClazz` → 写 `ads_large_subclazz_user_index`（`shardingKey = userId + subclazzNumber`，即**学员维度**）。
   - 小班花名册：`backAllAdsSmallClazzUserHandler` → `AdsSmallClazzUserBackService` → `ads_small_clazz_user`。

## 四、字段集与「含小班」结论
- **字段集需补 `studentTags`**：`ads.back.subclazz.user.fieldNames`（取数）+ `ads.large.subclazz.user.fieldNames`（写 ES）当前**均不含**（Apollo TEST 回读）；小班 `ads.small.clazz.user.full.fieldNames` **已含**。
- **不补 `clazzRoomType`**（owner 判断无用）。
- **含小班**：由「圈班 SQL」决定——`02`/`by_category` 显式大班(`clazz_room_type=1`)；`by_clazzlesson*` 不按 room_type（含小班）。**不是班级级开关、是学员维度**（`clazzRoomType` 落在 user×clazz 文档；且小班有独立表/索引/ handler）。

## 五、仍缺 / 不确定（具体）
1. **「本次续班服务学员标签回溯」到底用哪一个/哪几个圈班任务**：4 个任务写同一张表、条件不同（大班 vs 课节线、品类、时间段）；且天工侧 `periods` 显示 `02`/`by_clazzlesson*` 最近执行停在 2026-03（疑似手工/一次性，`params`/`runTimeParams` 为空、SQL 内为字面日期）。→ 需大数据确认**当前线上用哪个任务、按什么时间跑**（负责人：`02_sync_clazz_back_task` 创建人 lichenhao02；hive 表创建人 闫旭）。
2. **时间判据二选一未定**：班级创建时间(`create_time`) / 课节开始(`begin_time`) / ES `updateTime`（owner 说行）——最终用哪个由 owner 定。
3. **`studentTags` 回溯是否要覆盖小班**：若要含小班，需走课节线或小班链路（`sync_clazz_back_task_by_clazzlesson*` / `small_clazz_back_task`）。

## 六、确认后执行步骤（由我执行并回报；当前**不执行**）
1. Apollo(test) 给 `ads.back.subclazz.user.fieldNames`（+按需 `ads.large.subclazz.user.fieldNames`）补 `studentTags`（回读）。
2. 大数据按确认的圈班任务/条件跑数落 `ees_data.clazz_back_task`。
3. 跑 xjob `BackSubclazzUserHandler`（大班续班）/ `backAllAdsSmallClazzUserHandler`（小班）更新班下学员。
4. 回读 `ads_large_subclazz_user_index`（/`ads_small_clazz_user`）doc `studentTags` 有值（输入/预期/实际/清理）。
5. **线上**：记上线待办（PROD 字段集 Apollo + 生产圈班），需授权。

## 七、边界
- 未定口径前**不执行**；不改线上；不改前端；本文件为口径收敛。
