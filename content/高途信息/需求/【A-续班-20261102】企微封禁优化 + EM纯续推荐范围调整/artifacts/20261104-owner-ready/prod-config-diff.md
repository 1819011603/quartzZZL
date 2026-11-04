# 子项1 大班续班服务「学员标签」—— PROD 配置 diff（对应 test；**未执行**）

## 一、PROD 现状（只读核对）
- `ees_data.es_query_config`：`continuationService`(大班续班) **0 行**；`microContinuationService`(小班续班) / `smallClazzRoster` 各有 3 行同款。
- `ees_data.student_field_config`：`continuationService` 仅 `entranceArea`(1 行)；`microContinuationService` **0 行**。

→ 与 test 一致前，PROD 大班续班服务「学员标签」列会空（同 test 修复前）。

## 二、需补配置（PROD，待授权后走配置流程）
### A. `es_query_config`（对应 test ids 872/873/874）
```sql
INSERT INTO ees_data.es_query_config (field_name, type, identification, command, is_del) VALUES
 ('studentTags',     6, 'continuationService', 'necessary', 0),  -- test id 872
 ('studentTagNames', 6, 'continuationService', 'extra',     0),  -- test id 873
 ('studentTags',     2, 'continuationService', 'basic',     0);  -- test id 874
```
### B. `student_field_config`（两 identification；test 此前已补）
```sql
INSERT INTO ees_data.student_field_config
 (field_name, field_type, identification, editable, filter, is_del) VALUES
 ('studentTagNames', 8, 'continuationService',      1, 1, 0),
 ('wechatRemark',    1, 'continuationService',      1, 1, 0),
 ('studentTagNames', 8, 'microContinuationService', 1, 1, 0),
 ('wechatRemark',    1, 'microContinuationService', 1, 1, 0);
```
> field_type/editable/filter 取自 test 现值（studentTagNames type8、wechatRemark type1；均 editable=1/filter=1）。

## 三、说明 / 边界
- 生产改表属高危，**需 owner 授权并走配置流程**；本文件仅 ready，未执行。
- `es_query_config` 改动经 Caffeine 缓存（≤5min）生效；`student_field_config` 同理。
- GAIA 两场景**显示记录线上禁用**（如需上线另评估）。
- 发布编排 `24210` 已含 student-center；该配置为数据项，需在发布流程中同步执行。
