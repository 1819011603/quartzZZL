# 数据与索引

ES 宽表索引、数仓同步、MQ 消费链路导致的数据缺失或不一致问题。

## 模块

- [小班课花名册ES](小班课花名册ES/README.md) - 1 条案例，含排查方法：`small_clazz_v3` 索引架构、MQ consumer 链路、主讲/班主任权限口径与排查 SOP。
- [课后督学课节学员状态](课后督学课节学员状态/README.md) - 1 条案例，含排查方法：EES 课后督学「待发课堂小结」等卡片值来源（课节学员 ES `clazzSummaryStatus`）、由「课后课堂小结」触达记录驱动、口径区分与逐人核对 SOP。
- [GPS1v1首call任务](GPS1v1首call任务/README.md) - 2 条案例，含排查方法：首call与容器日常回访（待发布审查发现误完成/改派清理/失败重试风险）、首call生成链路与过滤（大班课/规则配置/service-dock `validateFirstCall`）、为什么任务没生成、以及业务表怎么同步到大数据（天工 DS vs 数据湖多表同步）。
