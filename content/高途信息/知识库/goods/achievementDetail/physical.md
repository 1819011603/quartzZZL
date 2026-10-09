# 业绩看板 / 订单明细（商品）（physical）

## 定位

| 项 | 值 |
|---|---|
| tab | `/ark/app-goods/achievementDetail` tab `Physical`「订单明细（商品）」（OLS 叫「商品业绩」） |
| 前端仓库 | gaotu-fe-goodsmanage（见 [_page.md](_page.md)） |
| tab 组件 | `src/pages/Achievement/Physical/index.tsx` |
| 后端主服务 | performance-attribution `PerformanceKanbanPhysicalController`（类 `@RequestMapping("/performance/management/")`，`performance-attribution-web/.../web/controller/PerformanceKanbanPhysicalController.java:53`） |

## 接口清单

`P` = `src/pages/Achievement/Physical/index.tsx`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 controller | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 查询 / 翻页 / 表头状态筛选 | `POST /performance/management/attribution/physical/list` | `getPhysicalList` | `P:116,155`（`src/pages/Achievement/service/index.ts:26`） | `:82` | 实物业绩明细 [36982] | 读 |
| 「导出」 | `POST /performance/management/attribution/physical/export` | `exportPhysicalList` | `P:296`，按钮 `P:384`（`service/index.ts:18`） | `:134` | 导出实物业绩明细 [36983] | 读（异步发邮件） |
| 归属人输入搜索 | `POST /performance/management/verify/employee` | `getBelongerList` | `P:361`（`service/index.ts:10`） | `PerformanceKanbanCourseController.java:396` | 校验归属人查询权限 [36999] | 读 |
| 手机号「复制」明文 | `POST /component/student-center/userSecret/getBaseInfo` | `getBaseInfo` | `P:251` → `src/components/InfoDesen/index.js:44` | student-center | 用户敏感信息 | 读 |

进 tab 是否自动查一次未确认（代码里只看到查询/翻页触发）。

## 链路与表

`PerformanceKanbanPhysicalServiceImpl`（`performance-attribution-domain/.../performancekanban/impl/`）：

| 接口 | 服务方法 | 读表 | 写表 | 其它 |
|---|---|---|---|---|
| physical/list | `#getOrderAttributionList:145` → `formatQueryCondition` → `selectPerformanceOrderAttribution` | `gaotu_stat.performance_physical_attribution`（`PerformancePhysicalAttributionMapper.xml` `selectSpuNumbersByCondition` / `getCount` / `selectList`） | 无 | controller 先取门神部门树 + 品类权限（`:104-109`）；Feign student（手机号/姓名→userId）、teacher（员工）、product（`listBaseInfoBySpuNumbers` 补商品信息） |
| physical/export | `#getOrderAttributionExport:152` | 同上 | 无 | 线程池异步，`MailUtils` 发邮件 |

## 青舟接口详情页

- [POST /performance/management/attribution/physical/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36982&appId=performance-attribution&branchName=release) id=36982
- [POST /performance/management/attribution/physical/export](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36983&appId=performance-attribution&branchName=release) id=36983
- [POST /performance/management/verify/employee](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36999&appId=performance-attribution&branchName=release) id=36999
