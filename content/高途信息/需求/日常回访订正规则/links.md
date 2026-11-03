---
title: 日常回访订正规则（GPS 1v1） · 链接中心
tags: [需求, 链接]
---

# 链接中心

> 仍有效的外部入口。失效或被替代后更新/删除。

## 需求与方案

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 需求wiki节点 | 日常回访订正规则（GPS 1v1） | https://gaotuedu.feishu.cn/wiki/LzsZwCDYIiksCokUAsQcAR3Jn8g | 2026-11-02 |
| 规则PRD | 日常回访订正规则（wiki rev876） | https://gaotuedu.feishu.cn/wiki/Q0BkwzqaRiPK42kn1b9cZzDBnzd | 2026-11-02 |
| 进展表 | 需求进展/回写表 sheet=In7cnX（第 4 行 L4） | https://gaotuedu.feishu.cn/sheets/T9lhsNwL4hzovStIDVDcyy8znRf?sheet=In7cnX | 2026-11-02 |
| 上线方案 | 日常回访订正规则（GPS 1v1）上线方案 | https://gaotuedu.feishu.cn/wiki/PEtvwdzpwiAQAQkyLP5cDbBinDb | 2026-11-02 |

## 开发与测试

| 类型   | 标题                                                                                                                                                                   | 链接                                                                                                          | 记录日期       |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------- |
| TAPD | 日常回访订正规则（GPS 1v1 新链路）· story `1122531521001397150`                                                                                                                   | https://www.tapd.cn/tapd_fe/22531521/story/detail/1122531521001397150?from_iteration_id=1122531521001013848 | 2026-11-02 |
| TAPD | 任务（拆 4 条，合计 32h，均已完成）：`1122531521001397158` 1v1日常回访调度与资格规则开发 20h / `1122531521001397159` 新老链路联调 4h / `1122531521001397160` 测试环境验证 4h / `1122531521001397161` 上线支持 4h | https://www.tapd.cn/tapd_fe/22531521/story/detail/1122531521001397150                                       | 2026-11-02 |
| 仓库   | student-data `feature-1v1-daily-visit-job`                                                                                                                           | http://git.baijia.com/gaotu/yunying_workbench/student-data                                                  | 2026-11-02 |
| 仓库   | fairy `feature-1v1-daily-visit-task`                                                                                                                                 | http://git.baijia.com/gaotu/fairy                                                                           | 2026-11-02 |

## 上线

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 发布计划 | 【A-日常回访-20261102】日常回访订正规则(GPS 1v1) · id `24158` | https://qingzhou.baijia.com/#/publishArrangement/subPublishArrangement/publishPlan/detail?storyId=&pageNum=1&id=24158&action=edit | 2026-11-02 |
| 上线checklist | 日常回访订正规则（GPS 1v1）上线方案 | https://gaotuedu.feishu.cn/wiki/PEtvwdzpwiAQAQkyLP5cDbBinDb | 2026-11-02 |
| 工单 | MySQL DDL（fairy `20261023_1v1_daily_visit_task.sql` / `20261028_daily_visit_teacher_user_unique.sql`） | 待提（上线前） | 2026-11-02 |
| 工单 | MQ 消费者组（`GID_student-data_dailyVisit_subclazzQuit_prod`） | 待提/确认（上线前） | 2026-11-02 |

## 跨会话检索锚点

- PRD/wiki token：`Q0BkwzqaRiPK42kn1b9cZzDBnzd`
- TAPD story_id：`1122531521001397150`（workspace `22531521`，iteration `1122531521001013848`）
- 发布计划 id：`24158`
- 分支锚点：`feature-1v1-daily-visit-job` / `feature-1v1-daily-visit-task`
