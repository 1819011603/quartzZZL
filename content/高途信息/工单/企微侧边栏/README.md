# 企微侧边栏工单记录

同一模块的案例按日期倒序写在本文件。通用日志查询、ACL 重放和字段排查方法不在这里复制，统一维护在 `crm-service/.claude/skills/wk-student-info-replay/SKILL.md`。

## 2026-09-11 改姓名后亲密称呼跟着变化

### 检索信息

- 状态：非缺陷
- 关键词：企微侧边栏，改姓名，亲密称呼自动变化，亲密称呼回显，10001，60008，前端兜底
- 关键 ID：accountId `86764`，userId `7309871552`，traceId `7d5fd3da-a860-4ce3-9023-aa42afe7a947.0.1`、`e8591f0f-9c5a-414e-acd0-13d9f2462578.0.1`、`a1328a0f-4dfb-4be0-90e5-a539fe616a9b.0.1`

### 反馈信息

- 反馈人 / 反馈渠道：飞书转发，王永诗 -> 马胜 -> 张泽灵；刘颖录屏演示
- 涉及对象：老师 `liuying24`，复现学员 userId `7309871552`

### 结论

不是 bug。企微侧边栏前端在亲密称呼没有值时使用姓名回显；crm-service 后端的姓名字段 `10001` 和亲密称呼字段 `60008` 独立存储、独立写入，没有联动。

### 关键证据

- 两次修改姓名的写请求只包含字段 `10001`，没有同时或紧接着写入 `60008`。
- 重放 `StudentMdmService#getDynamicWkStudentInfo` 后，写入亲密称呼前的 `60008` 没有 `value`，独立写入后才出现。
- 前端代码明确包含“亲密称呼没有值时使用姓名”的回显兜底。

### 决策与进展

金瑞琳确认这是既有前端逻辑，王永诗决定不修改。处理方式是先手工填写一次亲密称呼，之后再改姓名时不会被姓名兜底覆盖。

### 涉及系统

- 仓库 / 服务：`crm-service`、企微侧边栏前端
- 代码 / 数据：`StudentMdmController#getDynamicWkStudentInfo`、`#updateDynamicWkStudentInfo`，`StudentMdmService#getUpdateDimensionInfos`；前端 `nameIndex` 回显逻辑的具体仓库待补
- 排查 runbook：`crm-service/.claude/skills/wk-student-info-replay/SKILL.md`
