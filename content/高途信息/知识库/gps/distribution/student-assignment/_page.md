# 学员分班管理（student-assignment）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gps-distribution master 代码整理；后端对照 student-center（本地 `feature-xuban-expand-exclude`）、clazz-distribution-server（本地 `fix/join-count-zset-cross-clazz-pollution`）、student-data（本地 `feature-xuban-expand-exclude`）、ces-teach-product（本地 `feature-20260713-v3.6`）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/distribution/student-assignment` |
| 基座 | GPS test-os（qiankun）→ 子应用 distribution，静态资源 `gtoss.gsxcdn.com/fe/project/gps-distribution/` |
| 前端仓库 | gps-distribution `http://git.baijia.com/esai/gps-fe/gps-distribution`（master `94710e6`，本地 `~/IdeaProjects/WebProject/gps-distribution`），serviceCode `baijia.gt.jiaoyan.oes-fe.gps-distribution` |
| 前端路由 | `src/routes/index.tsx` `/distribution/student-assignment`「学员分班管理」→ `src/pages/StudentAssignment/index.tsx` |
| 请求封装 | `src/services/request.ts` axios 实例，请求头注入 `b_client=EES`；`code=70009` 跳登出 |
| 后端主服务 | 网关 `/bgwApi/student-center` → 青舟 appId `student-center`（`AllocationController`，`student-center-web/.../web/api/AllocationController.java:47`，类映射 `{"/allocation", "/gps/allocation"}`） |

## tab 列表

无 tab：一个筛选面板 + 学员表格 +「分班」抽屉（单行「分班」或勾选后「批量学员分班」都打开同一个 `ClazzSelectorDrawer`）。

## 页面级接口

`SA/` = `src/pages/StudentAssignment/`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面/筛选「校区」下拉（含搜索） | `POST /bgwApi/api/teachProduct/teachProductClazzType/sku/store` | `useCampusList` | `SA/components/FilterPanel/index.tsx:59,61` → `SA/queries/useCampusList.ts:20` | ces-teach-product-service | 获取sku门店信息 [3575341]（共享字典） | 读 |
| 进页面/「品类」级联 | `GET /bgwApi/course-center/b/common/category/tree` | `useCategoryTree` | `SA/components/FilterPanel/index.tsx:62` → `SA/queries/useCategoryTree.ts:34` | course-center | 品类树 [31498]（共享字典） | 读 |
| 进页面/查询/翻页/分班成功后刷新 | `POST /bgwApi/student-center/gps/allocation/student/page` | `useStudentAssignmentList` | `SA/components/AssignmentTable/index.tsx:30`、`SA/index.tsx:20` → `SA/queries/useStudentAssignmentList.ts:13` | student-center | 学员分班管理列表查询 [4155764] | 读 |
| 手机号「查看」 | `POST /bgwApi/student-center/userSecret/getBaseInfo` | `useRevealPhone` | `SA/components/AssignmentTable/index.tsx:87` → `SA/queries/useRevealPhone.ts:27` | student-center | 查询学员机密信息 [30733] | 读 |
| 打开分班抽屉 → 班级列表 | `POST /bgwApi/course-center/b/teachClazz/search` | `useClazzList` | `src/components/ClazzSelectorDrawer/index.tsx:70` → `src/components/ClazzSelectorDrawer/useClazzList.ts:23` | course-center | 班级搜索 [2652065]（共享） | 读 |
| 行内「分班」(`AssignmentTable/index.tsx:185`) / 「批量学员分班」(`SA/index.tsx:61`) → 抽屉确定 | `POST /bgwApi/student-center/gps/allocation/student/batch-assign` | `useAssignMutation` | `SA/components/ClazzSelectorDrawer/index.tsx:31` → `SA/queries/useAssignMutation.ts:18` | student-center | 批量学员分班 [4155763] | 写 |

页面无导出按钮。

## 后端链路

| 接口 | controller | 链路 |
|---|---|---|
| `allocation/student/page` | `AllocationController.java:81` | `StudentAllocationService#page`（`student-center-service/.../domain/service/allocation/StudentAllocationService.java:60`）→ `StudentAllocationEsQueryBuilder` 拼查询（手机号先经 `UserAclService.listStudentDetailByMobiles` Feign 转 userId，`:44`）→ `studentServeClient` 查 ES |
| `allocation/student/batch-assign` | `AllocationController.java:88` | `StudentAllocationBatchAssignService#batchAssign` → `ClazzDistHourPackageAclService.batchAssignClazz`（`student-center-adapter/.../acl/ClazzDistHourPackageAclService.java:38`）→ Feign `ClazzDistHourPackageAdapter`（`CLAZZ-DISTRIBUTION-SERVER.GAOTU100.COM` `/hourPackage/batchAssignClazz`）→ clazz-distribution-server `ClazzDistHourPackageController.java:118` → `HourPackageService#batchAssignByAccountKeys`（`clazz-distribution-server-domain/.../gps/service/HourPackageService.java:630`）；成功项再经 `HourPackageAssignSyncAclService.syncToEs`（`:30`）Feign student-data `/feign/hourPackageAssign/syncToEs` → `HourPackageAssignSyncService` 更新 ES |
| `userSecret/getBaseInfo` | `UserSecretController.java:36`（类映射 `userSecret`） | `userSecretBiz.getUserSecurityInfo`，按 Referer 鉴权返回明文手机号（下游未逐层确认） |

## 关键表 / 索引

| 接口 | 读 | 写（操作） | 其它 |
|---|---|---|---|
| `allocation/student/page` | ES `ads_clazz_hour_package_assign_index`（studentServe 集群；Apollo `student.allocation.es.index` 未配，走代码默认值 `StudentAllocationService.java:42`） | 无 | 手机号查询走 user 服务 Feign |
| `allocation/student/batch-assign` | `clazz_dist.hour_package_account_record`、`clazz_dist.gps_clazz_student`；course-center 班级信息（Feign） | `clazz_dist.gps_clazz_student` 批量 INSERT（新进班）/ 批量 UPDATE 复进（status=1）；`clazz_dist.hour_package_clazz_assign_record` 批量 INSERT（`HourPackageDao` `batchSaveClazzStudents`/`batchUpdateReenter`/`batchSaveAssignRecords`）；ES `ads_clazz_hour_package_assign_index` 回写（student-data `HourPackageAssignSyncService.java:40`） | 成功后发进班消息 `sendAssignEnterMsg` / `sendClazzUserEnterEvent`（topic 未逐条确认） |

库名依据：clazz-distribution-server mapper 在 `infrastructure/repository/db/mappers/clazzdist/`，由 `ClazzDistDataSourceConfig` 扫描（jdbc 库 `clazz_dist`）。

## 排查提示

- 列表数据不对/分班后状态没变：列表读的是 ES 宽表，不是 DB。先看 `clazz_dist.hour_package_clazz_assign_record` 是否已落库，再看 student-data `syncToEs` 是否成功（student-center 侧 sync 失败只打日志，不影响分班结果）
- 分班报「单次最多 N 条」：clazz-distribution-server `ClazzDistHourPackageController.java:132` 受 `batchAssignMaxSize` 限制
- 案例库 `content/高途信息/工单/` 暂无 GPS 分配/分班相关条目

## 青舟接口详情页

- [POST /allocation/student/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155764&appId=student-center&branchName=release) id=4155764
- [POST /allocation/student/batch-assign](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155763&appId=student-center&branchName=release) id=4155763
- [POST /userSecret/getBaseInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30733&appId=student-center&branchName=release) id=30733
- [POST /api/teachProduct/teachProductClazzType/sku/store](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3575341&appId=ces-teach-product-service&branchName=release) id=3575341
- [GET /b/common/category/tree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31498&appId=course-center&branchName=release) id=31498
- [POST /b/teachClazz/search](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2652065&appId=course-center&branchName=release) id=2652065
