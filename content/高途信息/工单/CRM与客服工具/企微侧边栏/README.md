# 企微侧边栏工单记录

通用日志查询、ACL 重放和字段排查方法维护在 `crm-service/.claude/skills/wk-student-info-replay/SKILL.md`；这里仅保存案例当前快照。

## 2026-09-11 改姓名后亲密称呼跟着变化

### 检索信息

- 状态：非缺陷
- 最后核验：2026-09-11
- 关键词：企微侧边栏，改姓名，亲密称呼自动变化，亲密称呼回显，10001，60008，前端兜底
- 关键 ID：accountId `86764`，userId `7309871552`，traceId `7d5fd3da-a860-4ce3-9023-aa42afe7a947.0.1`、`e8591f0f-9c5a-414e-acd0-13d9f2462578.0.1`、`a1328a0f-4dfb-4be0-90e5-a539fe616a9b.0.1`

### 反馈信息

- 反馈渠道：飞书转发及录屏
- 涉及对象：老师 `liuying24`，学员 userId `7309871552`

### 当前结论

不是后端字段联动问题。亲密称呼没有值时，企微侧边栏前端使用姓名兜底回显；crm-service 的姓名字段 `10001` 与亲密称呼字段 `60008` 独立存储、独立写入。

### 关键证据

- 两次修改姓名的请求只写字段 `10001`，没有写入 `60008`。
- 重放 `StudentMdmService#getDynamicWkStudentInfo` 时，独立填写亲密称呼前字段 `60008` 没有 `value`，填写后才出现。
- 前端存在“亲密称呼为空时使用姓名”的回显兜底。

### 当前状态与处置

业务已确认保持现有逻辑，不修改代码。需要固定亲密称呼时先填写一次；之后修改姓名不会再触发姓名兜底覆盖。

### 涉及系统

- 仓库 / 服务：`crm-service`、企微侧边栏前端
- 代码 / 数据：`StudentMdmController#getDynamicWkStudentInfo`、`#updateDynamicWkStudentInfo`，`StudentMdmService#getUpdateDimensionInfos`，字段 `10001`、`60008`
- 排查 runbook：`crm-service/.claude/skills/wk-student-info-replay/SKILL.md`
