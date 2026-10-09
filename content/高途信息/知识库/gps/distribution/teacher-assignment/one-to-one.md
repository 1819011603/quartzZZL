# 辅导老师分配 · 一对一老师分配（tab=one-to-one）

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gps-distribution master 代码整理；后端对照 student-center、clazz-distribution-server、student-data。返回 [_page.md](_page.md)。

组件 `src/pages/OneToOneTeacherAssignment/index.tsx`（下文 `O2O/`），可见需权限 `ONE_TO_ONE_MANAGE_MENU`。接口前缀 `API_PREFIX = '/bgwApi/student-center/gps/allocation/user-container'`（`O2O/constants.ts:1`），服务定义 `O2O/services/api.ts`。

## 接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面/查询/翻页/分配后刷新 | `POST /bgwApi/student-center/gps/allocation/user-container/page` | `searchAllocationList` | `O2O/index.tsx:23` → `O2O/queries/useAllocationList.ts:37` → `O2O/services/api.ts:19` | student-center | 一对一辅导老师分配列表查询 [4556722] | 读 |
| 筛选「辅导老师」下拉 / 批量分配弹窗老师下拉 | `POST /bgwApi/student-center/gps/allocation/user-container/teacher/list` | `searchTeachers` | `O2O/components/FilterPanel/index.tsx:46`、`O2O/components/BatchAssignModal/index.tsx:25` → `O2O/queries/useTeacherOptions.ts:21` → `O2O/services/api.ts:38` | student-center | 获取一对一可分配辅导老师列表 [4556719] | 读 |
| 手机号「查看」 | `POST /bgwApi/student-center/userSecret/getBaseInfo` | `useRevealPhone` | `O2O/components/AllocationTable/index.tsx:39` → `O2O/queries/useRevealPhone.ts:23` | student-center | 查询学员机密信息 [30733] | 读 |
| 勾选后「批量分配」(`O2O/index.tsx:48`) → 弹窗确定 | `POST /bgwApi/student-center/gps/allocation/user-container/batch-assign` | `batchAssign` | `O2O/components/BatchAssignModal/index.tsx:50` → `O2O/queries/useBatchAssign.ts:8` → `O2O/services/api.ts:25` | student-center | 一对一辅导老师批量分配 [4556721] | 写 |

## 后端链路（student-center `AllocationController`）

| 接口 | controller | 链路 |
|---|---|---|
| `user-container/page` | `AllocationController.java:129` | `UserContainerAllocationService#page`（`:60`）→ `UserContainerAllocationEsQueryBuilder`（学员混合查询上限 Apollo `user.container.allocation.student.search.max.size` 默认 200）→ ES `ads_user_container_allocation`（`@Value user.container.allocation.es.index` 默认值，`:42`） |
| `user-container/teacher/list` | `AllocationController.java:136` | `UserContainerAllocationTeacherService#pageTeachers` → `AllocateService#pageSubStaffByFuzzyName` → 组织架构 Feign |
| `user-container/batch-assign` | `AllocationController.java:148` | `UserContainerAllocationBatchAssignService#batchAssign`（上限 Apollo `user.container.batch.assign.max.size` 默认 50）→ `ClazzDistUserAssignAclService.batchTransferTeacher`（`:62`）→ Feign `ClazzDistUserAssignAdapter`（`CLAZZ-DISTRIBUTION-SERVER.GAOTU100.COM` `/userAssign/batchTransferTeacher`）→ clazz-distribution-server `ClazzDistUserAssignController.java:166` → `UserContainerAssignAppService#batchTransfer`（`clazz-distribution-server-domain/.../userContainerAssign/service/UserContainerAssignAppService.java:387`）→ `commandService.change`（`:443`）→ `UserContainerCommandServiceImpl`；成功项 `UserContainerAllocationAclService.syncToEs`（`:65`）→ student-data `/feign/userContainerAllocation/syncToEs` |

## 关键表 / 索引

| 接口 | 读 | 写（操作） | 其它 |
|---|---|---|---|
| `user-container/page` | ES 别名 `ads_user_container_allocation` | 无 | 写索引按子产品创建年份分片 `ads_user_container_allocation_<年>`（student-data `UserContainerAllocationIndexResolver.java:42-45`） |
| `user-container/batch-assign` | `clazz_dist.user_assign_container`（`selectBySubProductAndUser`） | `clazz_dist.user_assign_container` UPDATE 辅导老师（`containerRepository.updateAssistantNumber`，mapper `infrastructure/userContainerAssign/repository/mapper/UserAssignContainerMapper.xml`，由 `ClazzDistDataSourceConfig` 扫描）；ES `ads_user_container_allocation_<年>` 回写 | 顺序 MQ topic `user-container.event.topic`（test 默认 `gaotu_gps_user_container_event_test`）tag CHANGED（`UserContainerEventPublisherImpl.java:43,61`） |

## 青舟接口详情页

- [POST /allocation/user-container/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4556722&appId=student-center&branchName=release) id=4556722
- [POST /allocation/user-container/teacher/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4556719&appId=student-center&branchName=release) id=4556719
- [POST /allocation/user-container/batch-assign](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4556721&appId=student-center&branchName=release) id=4556721
- [POST /userSecret/getBaseInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30733&appId=student-center&branchName=release) id=30733
