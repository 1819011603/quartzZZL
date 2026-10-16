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

### 入参

- `POST /performance/management/attribution/physical/list`（`PerformanceKanbanPhysicalController#getOrderAttributionList`，DTO `OrderAttributionRequest`，`PerformanceKanbanPhysicalController.java:82`）：
  - `beginTime` (Long, 可选) — 开始时间(ms)
  - `endTime` (Long, 可选) — 结束时间(ms)
  - `userParam` (String, 可选) — 用户手机号/姓名/userId（空格分隔批量；单值 ≤20 字符，批量 ≤100）
  - `orderNumber` (String, 可选) — 订单号（须为数字）
  - `clazzBizNumber` (String, 可选) — 班级 bizNumber
  - `courseBizNumber` (String, 可选) — 课程 bizNumber
  - `typeList` (List<Integer>, 可选) — 业绩类型枚举值
  - `emailPrefixList` (List<String>, 可选) — 业绩归属人邮箱前缀
  - `sortField` (String, 可选) — 排序字段
  - `sortType` (Integer, 可选) — 1 升序 / 2 降序
  - `statusCode` (Integer, 可选) — 状态筛选
  - `pager` (Pager, 可选) — 分页，字段 `pageSize`/`pageNum`/`count`
  - `sorter` (List<QuerySorter>, 可选) — 元素 `{field, order}`
  - `timer` (List<Long>, 可选) — 查询时间区间（本 tab 主用；校验 `@NotEmpty`，为空报「开始时间和结束时间不能为空」）
  - `spuNumber` (String, 可选) — spu number（须为数字）
  - `roleSign` (Integer, 可选) — 0 运营 / 1 非运营
  - `categoryPaths` (List<String>, 可选) — 品类路径
  - 前端传 `{timer:[min,max], userParam, orderNumber, emailPrefixList, spuNumber, roleSign, sorter?, statusCode?, pager}`（`Physical/index.tsx:92-155`）
- `POST /performance/management/attribution/physical/export`（`PerformanceKanbanPhysicalController#getOrderAttributionExport`，DTO `OrderAttributionRequest` 同上，`PerformanceKanbanPhysicalController.java:134`）：
  - 字段同 `physical/list`（前端复用 `getParams()`，`Physical/index.tsx:295-296`）
- `POST /performance/management/verify/employee`（`PerformanceKanbanCourseController#verifyEmployee`，DTO `VerifyEmployeeRequest`，`PerformanceKanbanCourseController.java:396`）：
  - `employeeName` (String, 可选) — 归属人姓名/邮箱前缀关键字
  - 前端传 `{employeeName: words}`（`Physical/index.tsx:361`）
- `POST /component/student-center/userSecret/getBaseInfo`（student-center `UserSecretController#getUserSecretBaseInfo`，DTO `SecretUserIdRequest`，`student-center-web/.../web/api/UserSecretController.java:38`）：
  - `userId` (Long, 必填) — 学员 userId（controller 判空）
  - `typeList` (List<Integer>, 必填) — 取用类型，1 mobile（controller 判空）
  - `entranceUrl` (String, 可选) — 当前页面全路径 url
  - `reason` (String, 可选) — 解密原因
  - 前端经 `InfoDesen` 传 `{userId, typeList:[1], entranceUrl: window.location.href, reason}`（`src/components/InfoDesen/index.js:44-48`）

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
