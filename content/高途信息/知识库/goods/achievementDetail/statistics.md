# 业绩看板 / 业绩统计（statistics）

## 定位

| 项 | 值 |
|---|---|
| tab | `/ark/app-goods/achievementDetail` tab `list`「业绩统计」 |
| 前端仓库 | gaotu-fe-goodsmanage（见 [_page.md](_page.md)） |
| tab 组件 | `src/pages/Achievement/statistics/index.tsx`（面包屑 `statistics/breadUrl.tsx`） |
| 后端主服务 | performance-attribution `PerformanceStatisticsController`（类 `@RequestMapping("/performance/management")`，`performance-attribution-web/.../web/controller/PerformanceStatisticsController.java:44`） |

## 接口清单

`S` = `src/pages/Achievement/statistics/index.tsx`，service `src/pages/Achievement/service/index.ts`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 controller | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进 tab（mount） | `GET /performance/management/statistical/department` | `departmentLevelInit` | `S:67,170`（`service/index.ts:57`） | `:69` | 查询部门层级 [36990] | 读 |
| 查询 / 翻页 / 切层级 / 行「查看」下钻 | `POST /performance/management/statistical/list` | `getStatisticalList` | `S:124,140,164,181`，下钻 `S:280`（`service/index.ts:64`） | `:94` | 业绩统计列表 [36991] | 读 |
| 「导出」→ 按员工 | `POST /performance/management/statistical/employee/export` | `getEmployeeStatisticalList` | `S:312`（`service/index.ts:72`） | `:193` | 按人员导出 [36993] | 读（异步发邮件） |
| 「导出」→ 按当前组织 | `POST /performance/management/statistical/export` | `getLevelsStatisticalList` | `S:321`（`service/index.ts:80`） | `:146` | 按组织层级导出 [36992] | 读（异步发邮件） |

## 链路与表

`PerformanceStatisticsServiceImpl`（`performance-attribution-domain/.../performancekanban/impl/`）：

| 接口 | 服务方法 | 读表 | 写表 | 其它 |
|---|---|---|---|---|
| statistical/department | `#getDepartmentHierarchy:156` | 无 | 无 | staff 分支（OES 默认）：`staffFeignService.listPermissionBySceneAndPreTag` / `listAllChildOrgPathByOrgNumber`；menshen 分支：门神部门树 + medusa 部门信息 |
| statistical/list | `#getAttributionStatisticsList:333` → `getAttributionStatisticsResult` | 课程：**ADB** `gaotu_stat.performance_order_attribution_total`（`mapper/analyticdb/PerformanceOrderAttributionTotalAdbMapper.xml`）；商品：MySQL `gaotu_stat.performance_physical_attribution`（`selectPayStatisticsByTimeAndEmailPrefix` / `selectRefundStatisticsByTimeAndEmailPrefix`） | 无 | controller `:124` 先按 staff 岗位 tag 取权限；medusa/staff 取下属员工与部门 |
| statistical/export | `#attributionStatisticsExport:340` | 同 list | 无 | 线程池异步，`sendAttributionMail:630` 发模板附件邮件；`sendMailLimitSwitch=1` 时只发白名单 `sendMailLimitList` |
| statistical/employee/export | `#employeeAttributionStatisticsExport:369` | 同 list（按员工维度） | 无 | 同上 |

## 排查提示

- 统计数和明细对不上：统计读 ADB（同步延迟），明细读 MySQL `performance_order_attribution_total`，先排除 ADB 延迟
- 导出没收到邮件：看 `sendMailLimitSwitch` / `sendMailLimitList`（Apollo），以及异步线程异常日志

## 青舟接口详情页

- [GET /performance/management/statistical/department](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36990&appId=performance-attribution&branchName=release) id=36990
- [POST /performance/management/statistical/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36991&appId=performance-attribution&branchName=release) id=36991
- [POST /performance/management/statistical/export](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36992&appId=performance-attribution&branchName=release) id=36992
- [POST /performance/management/statistical/employee/export](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36993&appId=performance-attribution&branchName=release) id=36993
