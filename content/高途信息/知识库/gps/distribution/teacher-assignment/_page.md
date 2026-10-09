# 辅导老师分配（teacher-assignment）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gps-distribution master 代码整理；后端对照 student-center（本地 `feature-xuban-expand-exclude`）、clazz-distribution-server（本地 `fix/join-count-zset-cross-clazz-pollution`）、student-data（本地 `feature-xuban-expand-exclude`）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/distribution/teacher-assignment`（`?tab=omo` / `?tab=one-to-one`） |
| 基座 | GPS test-os（qiankun）→ 子应用 distribution |
| 前端仓库 | gps-distribution `http://git.baijia.com/esai/gps-fe/gps-distribution`（master `94710e6`） |
| 前端路由 | `src/routes/index.tsx` `/distribution/teacher-assignment`「辅导老师分配」→ `src/pages/TeacherAssignment/index.tsx`（tab 外壳，默认 `omo`） |
| 另一路由 | `/distribution/clazz-assignment`「辅导班分配管理」直接渲染 `src/pages/ClazzAssignment`，与本页 OMO tab 是同一组件 |
| 后端主服务 | 网关 `/bgwApi/student-center` → 青舟 appId `student-center`（`AllocationController.java:47`，类映射 `{"/allocation", "/gps/allocation"}`）；写操作 Feign 到 clazz-distribution-server |

## tab 列表

| tab（key） | 组件 | 可见条件 | 文档 |
|---|---|---|---|
| OMO老师分配（omo） | `src/pages/ClazzAssignment/index.tsx` | 始终 | [omo.md](omo.md) |
| 一对一老师分配（one-to-one） | `src/pages/OneToOneTeacherAssignment/index.tsx` | 权限 `Permissions.ONE_TO_ONE_MANAGE_MENU`（`TeacherAssignment/index.tsx:19`） | [one-to-one.md](one-to-one.md) |

## 页面级接口

tab 外壳本身不调接口，接口全部在 tab 内，汇总如下（明细见各 tab 文件）。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| OMO：品类下拉 | `POST /bgwApi/student-center/gps/allocation/subclazz/category/options` | `useCategoryOptions` | `src/pages/ClazzAssignment/queries/useCategoryOptions.ts:36` | student-center | 获取分辅导班品类下拉选项 [4155767] | 读 |
| OMO：列表 | `POST /bgwApi/student-center/gps/allocation/subclazz/page` | `useClazzAssignmentList` | `src/pages/ClazzAssignment/queries/useClazzAssignmentList.ts:62` | student-center | 辅导班分配列表查询 [4155766] | 读 |
| OMO：批量分配弹窗老师下拉 | `POST /bgwApi/student-center/gps/allocation/subclazz/teacher/list` | `useTeacherOptions` | `src/pages/ClazzAssignment/queries/useTeacherOptions.ts:43` | student-center | 获取可分配老师列表 [4155762] | 读 |
| OMO：批量分配确定 | `POST /bgwApi/student-center/gps/allocation/subclazz/batch-assign` | `useBatchAssignMutation` | `src/pages/ClazzAssignment/queries/useBatchAssignMutation.ts:16` | student-center | 批量转辅导班 [4155765] | 写 |
| 一对一：列表 | `POST /bgwApi/student-center/gps/allocation/user-container/page` | `searchAllocationList` | `src/pages/OneToOneTeacherAssignment/services/api.ts:19` | student-center | 一对一辅导老师分配列表查询 [4556722] | 读 |
| 一对一：老师下拉（筛选+弹窗） | `POST /bgwApi/student-center/gps/allocation/user-container/teacher/list` | `searchTeachers` | `src/pages/OneToOneTeacherAssignment/services/api.ts:38` | student-center | 获取一对一可分配辅导老师列表 [4556719] | 读 |
| 一对一：批量分配确定 | `POST /bgwApi/student-center/gps/allocation/user-container/batch-assign` | `batchAssign` | `src/pages/OneToOneTeacherAssignment/services/api.ts:25` | student-center | 一对一辅导老师批量分配 [4556721] | 写 |
| 一对一：手机号「查看」 | `POST /bgwApi/student-center/userSecret/getBaseInfo` | `useRevealPhone` | `src/pages/OneToOneTeacherAssignment/queries/useRevealPhone.ts:23` | student-center | 查询学员机密信息 [30733] | 读 |

页面无导出按钮。

## 关键表 / 索引

| 接口 | 读 | 写（操作） | 其它 |
|---|---|---|---|
| `subclazz/page` | ES `ads_subclazz_allocation_index`（studentServe） | 无 | |
| `subclazz/batch-assign` | `subclazz_student`、`gps_clazz_student` | `subclazz_student` 批量 INSERT（`OmoSubclazzAssignServiceImpl.java:138`），必要时新建辅导班 `subclazzService.createSubclazz`（`:248`）；ES `ads_subclazz_allocation_index` 回写（student-data） | MQ `subclazzStudentMsgProducer.sendOmoChangeMsg`（`:473`）；Redis 库存/在班人数缓存 |
| `user-container/page` | ES 别名 `ads_user_container_allocation`（实际索引 `ads_user_container_allocation_<年>`） | 无 | |
| `user-container/batch-assign` | `clazz_dist.user_assign_container` | `clazz_dist.user_assign_container` UPDATE 辅导老师（`UserContainerCommandServiceImpl` `containerRepository.updateAssistantNumber`）；ES `ads_user_container_allocation_<年>` 回写 | MQ topic `gaotu_gps_user_container_event_test`（test 默认值）tag CHANGED |

## 排查提示

- 列表与 DB 不一致：两个列表都只读 ES；先查 DB（`subclazz_student` / `clazz_dist.user_assign_container`）再看 student-data `/feign/subclazzAllocation/syncToEs`、`/feign/userContainerAllocation/syncToEs` 是否执行
- 一对一分配看不到 tab：缺权限 `ONE_TO_ONE_MANAGE_MENU`
- 案例库暂无相关条目；OMO 辅导班进班相关可参考 `content/高途信息/工单/数据与索引/小班课花名册ES/`（花名册 ES，与本页索引不同，仅作思路参考）

## 青舟接口详情页

- [POST /allocation/subclazz/category/options](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155767&appId=student-center&branchName=release) id=4155767
- [POST /allocation/subclazz/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155766&appId=student-center&branchName=release) id=4155766
- [POST /allocation/subclazz/teacher/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155762&appId=student-center&branchName=release) id=4155762
- [POST /allocation/subclazz/batch-assign](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4155765&appId=student-center&branchName=release) id=4155765
- [POST /allocation/user-container/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4556722&appId=student-center&branchName=release) id=4556722
- [POST /allocation/user-container/teacher/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4556719&appId=student-center&branchName=release) id=4556719
- [POST /allocation/user-container/batch-assign](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4556721&appId=student-center&branchName=release) id=4556721
- [POST /userSecret/getBaseInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30733&appId=student-center&branchName=release) id=30733
