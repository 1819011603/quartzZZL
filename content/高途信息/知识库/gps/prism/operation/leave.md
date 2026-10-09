# 请假管理（operation/leave）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 prism master 代码整理；后端对照 course-scene-lifecycle（master `d3f0af6`）、course-center（master `4ce8eda`）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/prism/operation/leave` |
| 基座 | GPS 系统 test-os（qiankun）→ 子应用 prism（chunk `p__operation__operationsManagement__leave__index`） |
| 前端仓库 | prism `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/prism`（master `148a757`） |
| 前端路由 | `config/routes.ts:49-53`「请假管理」→ `src/pages/operation/operationsManagement/leave/index.tsx`（列定义 `leave/data.tsx`） |
| 后端服务 | `/course-scene` 前缀剥掉 → 青舟 appId `course-scene-lifecycle`（`LeaveSupportFormController` `@RequestMapping("/b/support/form/leave")`，`adapter/web/controller/supportForm/LeaveSupportFormController.java:29`） |

三页共用模板说明见 [_page.md](_page.md)。

## tab 列表

无 tab，单表格 +「查看详情」抽屉（`CheckDetail`）。页面只读，无新建/取消/审批/导出按钮。

## 页面级接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面/查询/翻页 | `POST /course-scene/b/support/form/leave/searchAll` | FeituData fetch | `leave/index.tsx:117` | course-scene-lifecycle | 请假单列表 [3349465] | 读 |
| 进页面（原因枚举） | `GET /course-center/b/common/dictionary/all` | `useReasonFromDictionary('leave')` → `getAllConfigurableDictionary` | `leave/index.tsx:51`（`src/services/dictionary.ts:9`） | course-center | 共享字典 [31330] | 读 |
| 进页面（列配置） | `POST /course-center/b/columns/getAllConfig`、`/getUserConfig` | `useEditColumnsProps(SERVICE_ORDER_MANAGEMENT_LEAVE)` | `leave/index.tsx:109`（`src/services/userColumnConfig.ts:86/95`） | course-center | 共享字典 [31193]/[31197] | 读 |
| 自定义列 新增/保存/删除/设默认 | `POST /course-center/b/columns/addUserConfig` / `setUserConfig` / `deleteUserConfig` / `changeDefaultUserConfig` | 同上 hook | `src/hooks/useEditColumnsProps.ts:32-47`（`userColumnConfig.ts:104-134`） | course-center | 共享列配置 [31196]/[31194]/[31195]/[31198] | 写 |
| 「查看详情」 | `POST /course-scene/b/support/form/detail` | `getServiceOrderDetail` | `src/pages/checkDetail/index.tsx:63`（`src/services/serviceOrder.ts:21`） | course-scene-lifecycle | 服务单详情 [3349471] | 读 |
| 「查看详情」操作记录 | `POST /course-scene/b/support/form/operation/log` | FeituData fetch | `src/pages/checkDetail/index.tsx:333` | course-scene-lifecycle | 服务单操作日志 [3349480] | 读 |
| 手机号复制 | `POST /student-center/userSecret/getBaseInfo` | `getBaseInfo` | `src/components/phoneDesensitization/index.tsx:126`（`src/services/serviceOrder.ts:14`） | student-center | 查询学员机密信息 [30733] | 读 |

## 关键表 / 索引

### 后端链路

- `leave/searchAll`：`LeaveSupportFormController.java:74` → `LeaveSupportFormAppService#listAll:328` → `getSearchResponseForAll:338`（type=`LEAVE`）→ `BasicSupportFormAppService#buildCondition:707`（`userKey` 按手机号调用户中心 `querySingleInfo` 换 userId）→ `WideSupportFormRepository#findTableByCondition` → ES `support_form_search`；`convertToAllResponseList` 回表 `supportFormReadRepository.listByNumberList` + `leaveSupportFormReadRepository.listBySupportFormNumberList`，再 Feign 补课节（`ClazzLessonQueryApiFeignClientProxy#listByNumbers`）、班级（`ClazzQueryApiFeignClient#listBasicInfoByNumbers`）、老师（`teacherExternalApiRemoteProxy#listTeacherBaseInfo`）。
- `detail`：`BasicSupportFormController.java:87`（`@RequestMapping("/b/support/form")`）→ `BasicSupportFormAppService#detail:463` → 按 type 分派 `LeaveSupportFormAppService#addExtralDetail`。
- `operation/log`：`BasicSupportFormController.java:78` → `BasicSupportFormAppService#operationLog:426` → `supportFormLogReadRepository.listBySupportFormNumber` + staff 服务换操作人姓名。

### 接口 → 表

| 接口 | 读 | 写 | 其它 |
|---|---|---|---|
| `leave/searchAll` | ES `support_form_search`；`course_scene_lifecycle.support_form`、`leave_support_form` | 无 | 用户中心/课节/班级/老师 Feign |
| `support/form/detail` | `support_form`、`leave_support_form` | 无 | |
| `support/form/operation/log` | `support_form_log` | 无 | staff 服务 |
| `columns/*` / `dictionary/all` | course-center 列配置/字典 | 列配置写（共享，不展开） | 共享字典 |

## 排查提示

- 列表缺单：先查 ES `support_form_search` 有无该 `supportFormNumber`，再查 `course_scene_lifecycle.support_form`（type=LEAVE）
- 详情报「未找到服务单」：`support_form` 无该单号
- 案例库暂无相关条目

## 青舟接口详情页

- [POST /b/support/form/leave/searchAll](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3349465&appId=course-scene-lifecycle&branchName=release) id=3349465
- [POST /b/support/form/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3349471&appId=course-scene-lifecycle&branchName=release) id=3349471
- [POST /b/support/form/operation/log](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3349480&appId=course-scene-lifecycle&branchName=release) id=3349480
- [GET /b/common/dictionary/all](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31330&appId=course-center&branchName=release) id=31330
- [POST /b/columns/getAllConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31193&appId=course-center&branchName=release) id=31193
- [POST /b/columns/getUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31197&appId=course-center&branchName=release) id=31197
- [POST /userSecret/getBaseInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30733&appId=student-center&branchName=release) id=30733
