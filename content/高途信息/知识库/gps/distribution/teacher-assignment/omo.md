# 辅导老师分配 · OMO老师分配（tab=omo）

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gps-distribution master 代码整理；后端对照 student-center、clazz-distribution-server、student-data。返回 [_page.md](_page.md)。

组件 `src/pages/ClazzAssignment/index.tsx`（下文 `CA/`），同时挂在独立路由 `/distribution/clazz-assignment`。

## 接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 筛选「品类」下拉（输入搜索） | `POST /bgwApi/student-center/gps/allocation/subclazz/category/options` | `useCategoryOptions` | `CA/components/FilterPanel/index.tsx:51` → `CA/queries/useCategoryOptions.ts:36` | student-center | 获取分辅导班品类下拉选项 [4155767] | 读 |
| 进页面/查询/翻页/分配后刷新 | `POST /bgwApi/student-center/gps/allocation/subclazz/page` | `useClazzAssignmentList` | `CA/index.tsx:27` → `CA/queries/useClazzAssignmentList.ts:62` | student-center | 辅导班分配列表查询 [4155766] | 读 |
| 勾选后「批量分配」(`CA/index.tsx:52`) → 弹窗老师下拉 | `POST /bgwApi/student-center/gps/allocation/subclazz/teacher/list` | `useTeacherOptions` | `CA/components/BatchAssignModal/index.tsx:28` → `CA/queries/useTeacherOptions.ts:43` | student-center | 获取可分配老师列表 [4155762] | 读 |
| 弹窗确定 | `POST /bgwApi/student-center/gps/allocation/subclazz/batch-assign` | `useBatchAssignMutation` | `CA/components/BatchAssignModal/index.tsx:73`（body `{assignItems, accountId}`）→ `CA/queries/useBatchAssignMutation.ts:16` | student-center | 批量转辅导班 [4155765] | 写 |

## 后端链路（student-center `AllocationController`，类映射 `{"/allocation","/gps/allocation"}`）

| 接口 | controller | 链路 |
|---|---|---|
| `subclazz/category/options` | `AllocationController.java:120` | `SubclazzAllocationCategoryService#getCategoryOptions` → `CourseCenterDictionaryAclService.getCategoryTree`（course-center 品类树 Feign，`:55`）+ `PermissionTagFeignClient.getDataAuth` 数据权限过滤（`:118`）；不落表 |
| `subclazz/page` | `AllocationController.java:98` | `SubclazzAllocationService#page`（`:60`）→ `SubclazzAllocationEsQueryBuilder`（品类权限复用 CategoryService；手机号转 userId 走 `UserAclService`）→ ES `ads_subclazz_allocation_index`（`@Value subclazz.allocation.es.index` 默认值，`SubclazzAllocationService.java:42`） |
| `subclazz/teacher/list` | `AllocationController.java:105` | `SubclazzAllocationTeacherService#pageTeachers` → `AllocateService#pageSubStaffByFuzzyName`（`allocate/AllocateService.java:186`）→ `organizationAclService.searchSubStaffByName`（组织架构 Feign，relationType 取 Apollo `staff.teacher.relationType` 默认 `[0,2]`） |
| `subclazz/batch-assign` | `AllocationController.java:112` | `SubclazzAllocationBatchAssignService#batchAssign`（上限 Apollo `subclazz.batch.assign.max.size` 默认 50）→ Feign `ClazzDistOmoSubclazzAdapter`（`CLAZZ-DISTRIBUTION-SERVER.GAOTU100.COM` `/omoSubclazz/batchAssign`，`:82`）→ clazz-distribution-server `ClazzDistOmoSubclazzController.java:90` → `OmoSubclazzAssignServiceImpl#batchAssign`（`clazz-distribution-server-domain/.../gps/service/impl/OmoSubclazzAssignServiceImpl.java:91`）；成功后 `SubclazzAllocationSyncAclService.syncToEs`（`:102`）→ student-data `/feign/subclazzAllocation/syncToEs` → `SubclazzAllocationSyncService` |

## 关键表 / 索引

| 接口 | 读 | 写（操作） | 其它 |
|---|---|---|---|
| `subclazz/page` | ES `ads_subclazz_allocation_index` | 无 | |
| `subclazz/batch-assign` | `gps_clazz_student`（`hourPackageDao.listExistingClazzStudentKeys`，`:224`）、`subclazz`、`subclazz_student` | `subclazz_student` 批量 INSERT（`subclazzStudentService.batchInsertSubclazzStudent`，`:138`；mapper `mappers/mult/SubclazzStudentMapper.xml:142`，多数据源路由，具体库未确认）；按需新建辅导班 `subclazzService.createSubclazz`（`:248`）；进班明细 `studentTransactionDetailUserService.recordAndSendEnterSubclazzEvent`（`:431`）；ES `ads_subclazz_allocation_index` 回写（student-data `SubclazzAllocationSyncService.java:27`） | MQ `sendOmoChangeMsg`（`:473`）；Redis 库存/在班人数 `subclazzControllCacheService.incr/decr*` |

## 青舟接口详情页

- [POST /allocation/subclazz/category/options](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155767&appId=student-center&branchName=release) id=4155767
- [POST /allocation/subclazz/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155766&appId=student-center&branchName=release) id=4155766
- [POST /allocation/subclazz/teacher/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155762&appId=student-center&branchName=release) id=4155762
- [POST /allocation/subclazz/batch-assign](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155765&appId=student-center&branchName=release) id=4155765
