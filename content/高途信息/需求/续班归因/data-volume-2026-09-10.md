# 线上数据量盘点 · 2026-09-10

> 统计时点：2026-09-10 14:00（当天尚未结束）。库 `ees_data`，cluster_id **336**（`gaotu-student-dynamic-prod`）。

## 结论

**今天（09-10）实际调用大模型做归因的量非常小：**

| 指标 | 数量 |
|-|-|
| 调用大模型的**班级**数 | **1** 个（`556596222882912256`） |
| 调用大模型的**班级-学员**数 | **4** 个 |
| 大模型调用次数 | **4** 次（全部 `UNRENEWED_REASON_AI` 未续归因） |
| 已续归因（`RENEWED_REASON_AI`）调用 | **0** 次 |
| 产出归因结果行 | 4 行（`app_scene_type=5` / `unrenewedReasonAi`） |
| 发生时间 | 12:03:50 ~ 12:04:18（**集中在 1 分钟内**） |

**但班级级 Job 今天是跑了的，而且是第一次真正跑起来：**

| 指标 | 数量 |
|-|-|
| Job 今天派发的班级任务 | **2,621** 个班（`create_time` 00:25 生成） |
| 今天被置为已处理 `handle_status=1` | **2,621** 个（01:00:00~01:01:55 全部处理完） |
| 其中 `is_renew_user_clazz=1`（续班用户班） | 2,546 个 |
| 其中 `is_renew_user_clazz=0` | 75 个 |

> ⚠️ **2,621 个班被"处理"，但只有 1 个班真正调了大模型。**
> 2 分钟内跑完 2,621 个班，说明绝大多数班在进入大模型之前就被前置条件挡掉了
> （班名黑名单 `CommonRuleFilter`、不在展示窗口、无未续/已续学员、无沟通/问卷/预测源数据、
> 内容级幂等未变化等）。这是**预期内的过滤**还是**漏跑**，需要按 runbook 里的口径逐层核对。

## 日趋势（未续归因 app `288169360313290752`）

| 日期 | 大模型调用次数 | 班级数 | 班级-学员数 |
|-|-|-|-|
| 2026-09-10 | 4 | 1 | 4 |
| 2026-09-07 | 187 | 8 | 187 |
| 2026-09-06 | 183 | 14 | 183 |
| 2026-09-05 | 188 | 8 | 188 |
| **2026-09-04** | **8,632** | **22** | **7,225** |
| 2026-09-03 | 316 | 13 | 289 |
| 2026-09-02 | 80 | 4 | 66 |
| 2026-08-28 | 6 | 1 | 2 |

## 日趋势（已续归因 app `288169360792524800`）

| 日期 | 大模型调用次数 | 班级数 | 班级-学员数 |
|-|-|-|-|
| 2026-09-10 | 0 | 0 | 0 |
| 2026-09-07 | 58 | 1 | 58 |
| **2026-09-04** | **7,777** | **7** | **6,334** |
| 2026-09-03 | 123 | 1 | 71 |
| 2026-09-02 | 40 | 2 | 38 |
| 2026-08-28 | 1 | 1 | 1 |

> **09-04 是一次大批量刷数**（未续 8.6k + 已续 7.8k ≈ 1.6 万次调用），此后回落到每天几十~两百次。
> 09-10 只有 4 次，是有数据以来除首日外的最低。

## 累计（截至 09-10 14:00）

| 场景 | 结果行数 | 覆盖班级数 | 首次 | 最近 |
|-|-|-|-|-|
| `unrenewedReasonAi`（未续 AI） | 8,083 | 48 | 2026-08-28 16:42 | 2026-09-10 12:04 |
| `renewedReasonAi`（已续 AI） | 6,449 | 12 | 2026-08-28 16:59 | 2026-09-07 19:27 |
| `unrenewedReasonTeacher`（老师总结） | 1 | 1 | 2026-08-28 17:20 | 2026-08-28 17:20 |
| `renewedReasonTeacher` | 0 | — | — | — |

班级级任务表 `ai_renewal_attribution_follow_clazz_task` 累计 17,702 行 / 2,646 个班，
其中 **15,081 行仍是 `handle_status=0`**（08-28~09-02 那几批全部未处理，只有 09-10 这批 2,621 行处理了）。

## 今天那 1 个班的明细

班级 `556596222882912256`，辅导班 `35819050886889856`，4 个学员：
`3547026154` / `238431457560689` / `7442617271` / `7439905795`，
均走**续班沟通记录**这条数据源，`refreshForce=false`。

## 查询口径（复跑用）

两张主表都**没有时间索引**，直接 `WHERE create_time >= CURDATE()` 会超时，
必须先二分出当天起始 `id` 再带上 `id >=` 条件走主键范围扫描。

```sql
-- 1. 先定位当天起始 id（示例为 09-10）
SELECT MIN(id) FROM ees_data.ai_app_clazz_user_scene
WHERE id BETWEEN 6500000 AND 6550000 AND create_time >= '2026-09-10 00:00:00';
-- → 6525055

-- 2. 归因结果（app_scene_type 5=未续 6=已续）
SELECT app_scene_type, app_scene_key, COUNT(*) rows_cnt,
       COUNT(DISTINCT clazz_number) clazz_cnt,
       COUNT(DISTINCT CONCAT(clazz_number,'-',user_id)) clazz_user_cnt
FROM ees_data.ai_app_clazz_user_scene
WHERE id >= 6525055 AND create_time >= '2026-09-10 00:00:00' AND app_scene_type IN (5,6)
GROUP BY app_scene_type, app_scene_key;

-- 3. 大模型调用次数（extra_info 里有 clazzNumber/userId/reasoningEnum）
SELECT JSON_UNQUOTE(JSON_EXTRACT(extra_info,'$.reasoningEnum')) re, COUNT(*) calls,
       COUNT(DISTINCT JSON_EXTRACT(extra_info,'$.clazzNumber')) clazz_cnt,
       COUNT(DISTINCT CONCAT(JSON_EXTRACT(extra_info,'$.clazzNumber'),'-',
                             JSON_EXTRACT(extra_info,'$.userId'))) clazz_user_cnt
FROM ees_data.ai_application_call_task
WHERE id >= 68009277 AND create_time >= '2026-09-10 00:00:00'
  AND application_number IN (288169360313290752, 288169360792524800)
GROUP BY re;

-- 4. 班级级 Job 派发与处理情况
SELECT handle_status, is_renew_user_clazz, COUNT(*) cnt,
       COUNT(DISTINCT clazz_number) clazz_cnt, MIN(update_time), MAX(update_time)
FROM ees_data.ai_renewal_attribution_follow_clazz_task
WHERE update_time >= '2026-09-10 00:00:00'
GROUP BY handle_status, is_renew_user_clazz;
```

**AI 应用编号（`application_number`）对照：**

| application_number | 场景 |
|-|-|
| `288169360313290752` | `UNRENEWED_REASON_AI` 未续归因 |
| `288169360792524800` | `RENEWED_REASON_AI` 已续归因 |

> `ai_application_call_task` 是**全站 AI 网关**共用表，一天七八万次调用里绝大多数是画像/沟通摘要等
> 其它场景，统计归因量**必须按上面两个 `application_number` 过滤**，不能只按日期数行数。

## 待确认

- [ ] 2,621 个班只出 1 个班的归因，逐层核对过滤原因（班名黑名单 / 展示窗口 / 源数据缺失 / 幂等）
- [ ] 08-28~09-02 那 15,081 行 `handle_status=0` 是否需要补跑
- [ ] 已续归因自 09-07 后再无调用，确认是否符合预期
