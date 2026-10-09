# 我的组 / 个性化分组管理（groupList）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 prism master 代码整理；后端对照 student-center（origin/master `9cfc479`）、clazz-distribution-server（origin/master `9526f4e`）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/prism/groupList` |
| 基座 | GPS 系统 test-os（qiankun）→ 子应用 prism |
| 前端仓库 | prism `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/prism`（master `148a757`，本地 `~/IdeaProjects/WebProject/prism`，umi） |
| 前端路由 | `config/routes.ts:7-11`「个性化分组管理」→ `src/pages/groupList/index.tsx` |
| 后端主服务 | 网关前缀 `/bgwApi/student-center` → 青舟 appId `student-center`（`GpsGroupController` `@RequestMapping("/gps/group")`，`student-center-web/.../web/api/GpsGroupController.java:66`）；组的真实存储在 **clazz-distribution-server**（Feign `CLAZZ-DISTRIBUTION-SERVER.GAOTU100.COM` path `gpsGroup`，`ClazzDistGpsGroupAdapter`） |

列表读 ES `ads_gps_group_index`（student-data 写入端维护），新建/编辑/详情经 Feign 落 clazz-distribution-server 的 `clazz_dist` 库。

## tab 列表

无 tab，单页表格 +「新建组 / 编辑」抽屉（`components/GroupFormDrawer/index.tsx`）。抽屉内嵌两个选择器：选子产品（cms-ui `CourseDesignProductSelect`，走 `/jiaoyan-ces`）和选学员（`src/components/studentTransferPicker`）。「查看」列只 `window.open` 到 `deliveryDetail?groupId=`（`src/pages/groupList/utils.ts:41`），不在本页调接口。

## 页面级接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面/查询/翻页 | `POST /bgwApi/student-center/gps/group/list` | FeituData fetch（`GROUP_LIST_API`，body 由 `buildGroupListBody` 平铺） | `src/pages/groupList/index.tsx:246`（定义 `src/services/group.ts:27`/`:56`） | student-center | 组列表分页查询 [5269060] | 读 |
| 「管理员」下拉展开/搜索/滚动 | `POST /bgwApi/student-center/gps/group/subordinates/pageSearch` | `searchGroupSubordinates` | `src/pages/groupList/index.tsx:114`（`src/services/group.ts:223`） | student-center | 登录人下属扁平分页查询 [5269055] | 读 |
| 新建/编辑抽屉打开 | `POST /course-center/b/teachProduct/teachDepartment/listAll` | `listTeachDepartments` | `GroupFormDrawer/index.tsx:162`（`src/services/serviceOrderForm.ts:264`） | course-center | 学部全量（共享字典）[4555206] | 读 |
| 新建/编辑抽屉打开 | `POST /bgwApi/student-center/gps/group/config/studentLimitMax` | `getGroupStudentLimitMax` | `GroupFormDrawer/utils.ts:44`（`src/services/group.ts:242`） | student-center | 组学员上限查询 [5269054] | 读 |
| 「编辑」回填 | `POST /bgwApi/student-center/gps/group/detail` | `getGroupDetail` | `GroupFormDrawer/index.tsx:191`（`src/services/group.ts:145`） | student-center | 组详情 [5269057] | 读 |
| 抽屉「选择子产品」 | `/jiaoyan-ces/...`（cms-ui 组件内部） | `CourseDesignProductSelect` | `GroupFormDrawer/index.tsx:665` | CES 教研产品库 | 未确认（node_modules 未装，具体路径未取到） | 读 |
| 抽屉「添加/编辑学员」候选 | `POST /bgwApi/student-center/gps/group/student/pick` | `pickGroupStudents` | `src/components/studentTransferPicker/candidateSource.ts:38`（`src/services/group.ts:188`） | student-center | 组创建/编辑选学员 [5269056] | 读 |
| 选学员「已选栏」回显 | `POST /bgwApi/student-center/student/base/list` | `listStudentBase` | `src/components/studentTransferPicker/selectedSource.ts:33`（`src/services/group.ts:209`） | student-center | 按 userIds 批量查学员基础信息 [5269061] | 读 |
| 新建 → 确定 | `POST /bgwApi/student-center/gps/group/create` | `createGroup` | `GroupFormDrawer/index.tsx:391`（`src/services/group.ts:157`） | student-center | 创建组 [5269059] | 写 |
| 编辑 → 确定（含关组/改学员） | `POST /bgwApi/student-center/gps/group/update` | `updateGroup` | `GroupFormDrawer/index.tsx:408`（`src/services/group.ts:171`），`userIds` 全量覆盖 | student-center | 编辑组 [5269058] | 写 |

## 关键表 / 索引

### 后端链路

- `list`：`GpsGroupController.java:93` → `GpsGroupBiz#pageList:183`（keyword 分派、学员反查走 `MyStudentService` ES）→ `GpsGroupQueryService#pageList:119` 查 ES `ads_gps_group_index`（Apollo `gps.group.es.index`，`GpsGroupQueryService.java:78`）。
- `detail`：`:101` → `GpsGroupBiz#detail:217` → `GroupFeignClient#queryDetail` + `listAllStudentsByGroup`（门面，实现包装 `ClazzDistGpsGroupAdapter` → clazz-distribution-server `gpsGroup/detail`、`gpsGroup/operationUnit/student/list`）。
- `create` / `update`：`:192`/`:200` → `GpsGroupWriteBiz#create:68` / `#update:106`（update 先 `groupFeignClient.queryDetail:117`）→ `GroupWriteClientImpl` → `ClazzDistGpsGroupAdapter.createGroup/updateGroup` → clazz-distribution-server `POST gpsGroup/create`、`gpsGroup/update`（`ClazzDistGpsGroupService.java:64/75`）。
- `student/pick`：`:208` → `GpsGroupStudentPickBiz#pickStudents:34` → `MyStudentService#pickPage:149` 查 ES `ads_user_container_allocation`（`studentServeClient`）。
- `student/base/list`：`StudentBaseController.java:38`（`@RequestMapping("/student/base")`）→ `StudentBaseBiz` → `userSyncAclService.listStudentBaseByUserIdsFromCache`（缓存/下游用户服务，具体来源未确认）。
- `subordinates/pageSearch`：`:183` → `GpsGroupBiz#pageSearchSubordinates:1065` → `AllocateService#pageSubStaffByFuzzyName`（staff 服务）。
- `config/studentLimitMax`：`:172` → Apollo `gps.group.student.limit.max`（默认 500，`GpsGroupBiz.java:128`）。

### 接口 → 表

| 接口 | 读 | 写（操作） | 其它 |
|---|---|---|---|
| `gps/group/list` | ES `ads_gps_group_index`；学员反查 ES `ads_user_container_allocation` | 无 | 组索引由 student-data `GroupIndexSyncService` 等写入 |
| `gps/group/detail` | `clazz_dist.gps_group_info`、`gps_group_student` 等（经 clazz-distribution-server） | 无 | 有权限校验，无权限按「组不存在」报错 |
| `gps/group/create` | — | `clazz_dist.gps_group_info` / `gps_group_admin` / `gps_group_department` / `gps_group_sub_product` / `gps_group_student` / `gps_group_teacher` / `gps_group_tag_rel` INSERT（按 `GpsGroupMapper.xml` 涉及表推断，逐条 SQL 未核对） | 操作日志 `gps_group_operation_log` 由 MQ 消费者 `GpsGroupOperationLogConsumer` 异步写（推断） |
| `gps/group/update` | 同上 | 同上表 UPDATE/INSERT（学员 diff 由上游做） | 同上 |
| `gps/group/student/pick` | ES `ads_user_container_allocation` | 无 | |
| `student/base/list` | 用户基础信息缓存（未确认） | 无 | |
| `subordinates/pageSearch` / `config/studentLimitMax` | staff 服务 / Apollo | 无 | |

## 排查提示

- 列表搜不到刚建的组：列表走 ES `ads_gps_group_index`，建组写的是 `clazz_dist` 库，中间靠 student-data 同步；先查 `clazz_dist.gps_group_info` 有没有，再查 ES 文档
- 编辑抽屉学员数与列表不一致：列表 `studentCount` 来自 ES 快照，`detail` 实时走 clazz-distribution-server
- 管理员下拉空：下属来自 staff 服务，按登录人 + `staff.teacher.relationType` 过滤
- 案例库暂无 GPS 分组相关条目

## 青舟接口详情页

- [POST /gps/group/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5269060&appId=student-center&branchName=release) id=5269060
- [POST /gps/group/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5269057&appId=student-center&branchName=release) id=5269057
- [POST /gps/group/create](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5269059&appId=student-center&branchName=release) id=5269059
- [POST /gps/group/update](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5269058&appId=student-center&branchName=release) id=5269058
- [POST /gps/group/student/pick](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5269056&appId=student-center&branchName=release) id=5269056
- [POST /gps/group/subordinates/pageSearch](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5269055&appId=student-center&branchName=release) id=5269055
- [POST /gps/group/config/studentLimitMax](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5269054&appId=student-center&branchName=release) id=5269054
- [POST /student/base/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5269061&appId=student-center&branchName=release) id=5269061
- [POST /b/teachProduct/teachDepartment/listAll](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4555206&appId=course-center&branchName=release) id=4555206（共享字典）
