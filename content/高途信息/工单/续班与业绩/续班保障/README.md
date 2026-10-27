# 续班保障

续班大促期（续班人次 > 3W）的压测与现场保障：续班学科链路、压测前/中/后流程，以及 student-data / EES 相关的 Apollo 配置。

> **RD 重点关注：① Apollo 配置 ② MQ 堆积情况。**

- 相邻模块：[续班关系配置](../续班关系配置/README.md)、[业绩归因](../业绩归因/README.md)

## 关联资源

飞书：

- 续班保障 SOP：https://gaotuedu.feishu.cn/wiki/Z05zw0Wl3i9z4kkug9ociTF2nxe
- 续班保障记录（知识库根）：https://gaotuedu.feishu.cn/wiki/NgbHwPnC1iXnnckJDQSccXdPnRf
  - 续班保障 SOP / 续班副本数快照 / 产研侧续班保障信息收集 / 续班保障相关前置 check / 2026 续班集中保障-值班 / 续班问题记录-2026 / 2026 续班变更 review
- 续班压测记录（每次压测的留档）：https://gaotuedu.feishu.cn/wiki/PZPAwR1DFi4uBlkBN6IcEOZan2d

代码：

- 续班扩容计划：https://git.baijia.com/gaotu/yunying_workbench/student-renewal-info

## 症状路由

| 症状（用户会怎么说） | 去哪 |
|---|---|
| 某班级/学员没进续班学科（`dws_fuwu_clazz_user_subject` 查不到） | [`排查/班级没进续班学科.md`](排查/班级没进续班学科.md) |
| 花名册/续班服务页「在读科目数」比实际多（多算 1 科，源表 `is_del=0` 却更少） | [`排查/在读科目比实际多.md`](排查/在读科目比实际多.md) |
| 续班大促压测/现场保障怎么做（压测前/中/后要配哪些 key） | [`排查/续班大促压测保障流程.md`](排查/续班大促压测保障流程.md) |

## 案例

| 日期 | 现象 | 状态 |
|---|---|---|
| 2026-09-22 | [秋季续班压测：白名单与相关 Apollo 配置核对](案例/2026-09-22-秋季续班压测配置核对.md) | 已解决 |
| 2026-10-16 | [花名册在读科目数比实际多（高一「文综生物」学员）](案例/2026-10-16-花名册在读科目数比实际多.md) | 排查中 |
