# 续班计划管理（continuation-classes）— 页面级

> 2026-10-09 用 chrome-devtools 带登录态在 test 环境点击抓包整理，前端代码对照 gaotu-fe-promotions master，后端对照 product-server。

## 路由链路

| 项 | 值 |
|---|---|
| 列表页 URL | `https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/list` |
| 详情页 URL | `https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/detail?n=<续班计划number>` |
| 菜单 | OES（ark 基座）→ 续班管理 → 续班计划管理 |
| 基座 | ark → 子应用 app-promotions（静态资源 `gtoss.gsxcdn.com/.../projects/promotions/`） |
| 前端仓库 | gaotu-fe-promotions `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/gaotu-fe-promotions`（master，本地 `~/IdeaProjects/WebProject/gaotu-fe-promotions`；青舟 serviceCode `baijia.gt.ecommerce.fe.gaotu-fe-promotions`） |
| 页面目录 | `src/pages/continuationClasses/`（list / detail：Relations、RenewableStudent、Process、PlanTarget） |
| 后端服务 | 网关前缀 `/product-b` → 青舟 appId `product-b`（代码仓库 **product-server**，模块 `product-server-b`） |
| 主库 | `gaotu` 库（test 集群见各 tab 文件） |

## tab 列表

| tab | 文件 | 说明 |
|---|---|---|
| 列表页 | 本文件 | 计划列表筛选 |
| 详情页 / 续班关系 | 本文件 | 前置课程 ↔ 后置课程 |
| 详情页 / 续班学员 | [renewableStudent.md](renewableStudent.md) | 在读班级列表 + 续班配置 + 管理可续学员（是否展示不可续见此文件） |
| 详情页 / 续班流程 | [renewalProcess.md](renewalProcess.md) | 续班问卷 / 预报名 / 续班正式报名，**问卷绑定在这里** |

## 页面级接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 列表页 进页面/查询/翻页 | `POST /product-b/b/renewMaster/list` | `ProTable fetch` | `src/pages/continuationClasses/list/index.js:361` | product-b | `/b/renewMaster/list` | 续班计划列表 | — |
| 列表页 进页面 | `GET /course-center/b/common/department/tree` | — | —（共享组件） | course-center | `/b/common/department/tree` | 部门树 | 所属部门筛选 |
| 列表页 进页面 | `GET /course-center/b/common/dictionary/all` | — | —（共享组件） | course-center | `/b/common/dictionary/all` | 字典 | 学年/学期/年级/学科 |
| 详情页 进页面 | `POST /product-b/b/renewMaster/detail` | `getContinuationClassesPlanDetail` | `src/hooks/useBasicInfo.js:24（src/services/continuationClasses.js:31）` | product-b | `/b/renewMaster/detail` | 续班计划详情 | 入参 `{"number": 计划number}`；回年级/学科/学期/部门/管理员 |
| 详情页 续班关系 | `POST /product-b/b/renewMaster/productRelationList` | `getProductRelationList` | `src/pages/continuationClasses/detail/Relations/provider.js:61（src/services/continuationClasses.js:107）` | product-b | `/b/renewMaster/productRelationList` | 续班关系列表 | 前置产品 ↔ 后置产品 |
| 详情页 续班关系 | `POST /product-b/b/renewMaster/listCoursesByPreCourseNumber` | `getCourseAllSceneTypeList` | `src/pages/continuationClasses/detail/Relations/index.js:79（src/services/continuationClasses.js:163）` | product-b | `/b/renewMaster/listCoursesByPreCourseNumber` | 按前置课程查后置课程 | 入参 `{"preCourseNumber": ...}` |

## 续班关系管理接口（增删改）

详情页「续班关系」tab：左「前置产品」（= 计划的 `renew_master_course_relation`）、右「后置产品」（= 选中前置课程在 `course_relation_map` 的续报关系）。增删改入口如下（前端均在 `src/pages/continuationClasses/detail/Relations/`）：

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|---|
| 「+ 批量修改续班关系」弹窗上传 Excel | `POST /product-b/b/renewMaster/courseRelation/batchFollowRelation` | `batchSettingRelations` | `BatchSettingRelations/index.js:85（services/continuationClasses.js:133）` | product-b | `/b/renewMaster/courseRelation/batchFollowRelation` | 批量修改续班关系 | 入参 `{operationType(1添加/2删除), excelUrl, renewalMasterNumber}`；**按「前置课程」整体增删**，见下方注意 |
| 前置产品「+添加」 | `POST /product-b/b/renewMaster/bindPreCourse` | `bindPreCourse` | `AddPreProductDrawer/index.js:49（services/continuationClasses.js:177）` | product-b | `/b/renewMaster/bindPreCourse` | 续班计划绑定前置课程 | 入参 `{renewalMasterNumber, preCourseNumberList}` |
| 前置产品「删除」 | `POST /product-b/b/renewMaster/unbindPreCourse` | `unbindPreCourse` | `Relations/index.js:112（services/continuationClasses.js:184）` | product-b | `/b/renewMaster/unbindPreCourse` | 续班计划解绑前置课程 | 同上入参 |
| 前置产品「已选平铺」下拉 | `POST /product-b/b/renewMaster/listPreCourseNumberList` | `getSelectedPreCourseNumberList` | `AddPreProductDrawer/index.js:64（services/continuationClasses.js:170）` | product-b | `/b/renewMaster/listPreCourseNumberList` | 查询所有前置课程（平铺） | — |
| 后置产品「+添加」/编辑 | `POST /product-b/b/renewMaster/courseRelation/add` | `modifyCourseRelation` | `AddPostProductDrawer/index.js:45（services/continuationClasses.js:126）` | product-b | `/b/renewMaster/courseRelation/add` | 修改前后置关系 | — |
| 后置产品「删除」单条 | `POST /course-center/b/course/deleteRelation` | `deleteCourseRelation` | `Relations/index.js:93（services/continuationClasses.js:119）` | course-center | `/b/course/deleteRelation` | 删除关联关系 | 只删选中那条前置↔后置对 |
| 后置产品「计算可续」开关 | `POST /product-b/b/renewMaster/courseRelation/modifyCalculate` | `editCanRenewalCount` | `Relations/index.js:338（services/continuationClasses.js:204）` | product-b | `/b/renewMaster/courseRelation/modifyCalculate` | 编辑是否可续 | — |

> **批量修改续班关系（`batchFollowRelation`）的删除是「按前置课程整体解绑」，不是「按前置↔后置对删除」**：
> 后端 `RenewalServiceImpl#batchFollowRelation` 只用 Excel「前置课程id」列匹配本计划的前置课程（忽略「后置课程id」列），
> 再 `unbindPreCourse` → `deletePreCourseRelations(plan, 前置课程列表)`，把这些**前置课程从计划里整体软删**；
> 同时调 course-center `/feign/course/batchFollowRelationByDto`（`SnowBallServiceImpl#deleteCourseRelationClient`）按 (前置,后置) 对删 `course_relation_map`。
> 所以 Excel 里出现过的前置课程，会连同它在计划下的**所有**后置关系一起从页面消失。目标只是删掉某个后置关系时，应走单条「后置产品-删除」（course-center `deleteRelation`），不要用批量。
> 相关工单：`续班与业绩/续班关系配置/`。

## 关键表

| 表 | 含义 |
|---|---|
| `gaotu.renew_master` | 续班计划（number = 页面上的「续班计划ID」） |
| `gaotu.renew_master_course_relation` | 计划下的前置课程；`questionnaire_number` 列 = 该前置课程匹配到的问卷 |
| `course_center.course_relation_map` | 前后置关系：`relation_number`=前置课程、`course_number`=后置课程；续班取 `relation_type=1`（`=0` 推荐课程、`calculate_renewal_type=2` 预报名） |
| `course_center.course` | 课程名称、`department_id`（末级部门） |
| `course_center.course_school_relation` | 课程的年级(2)/学科(3)/学年(5)/学期(4)/学部(1)，`isdel=0` |
| `course_center.course_center_dictionary` | 名称字典：`courseGrades` / `courseSubjects` / `schoolYears` / `schoolTerms` |

集群（`mysql_query` 定位，**两库不同集群不能跨库 JOIN**）：`gaotu` → cluster 71 `gaotu-center-prod`；`course_center` → cluster 317 `gaotu-course-prod`。部门名称走 course-center 部门树 API `GET /course-center/b/common/department/tree`（medusa）。

> 「续班计划ID」在飞书/前端复制时**常被 JS 精度截断**（17 位大整数末两位变 `00`），查不到先按前 15 位前缀找候选。

## 排查提示

- 计划看不到课程 / 续班关系不对 → `productRelationList`、`listCoursesByPreCourseNumber`；另见工单 `续班与业绩/续班关系配置/`
- 批量改续班关系后「计划下所有续班关系都没了」→ `batchFollowRelation` 按前置课程整体解绑，核对 Excel「前置课程id」列集合；恢复=把 `renew_master_course_relation`（及对应 `course_relation_map` 命中记录）`isdel` 改回 0
- 要按计划ID批量导出续班关系（前置↔后置对照）→ 工单 `续班与业绩/续班关系导出/`（含可复用脚本）
- 问卷相关 → [renewalProcess.md](renewalProcess.md)

## 青舟接口详情页（product-b / release）

- [POST /b/renewMaster/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734217&appId=product-b&branchName=release) id=2734217
- [POST /b/renewMaster/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734125&appId=product-b&branchName=release) id=2734125
- [POST /b/renewMaster/listCoursesByPreCourseNumber](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734280&appId=product-b&branchName=release) id=2734280
- [POST /b/renewMaster/productRelationList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734126&appId=product-b&branchName=release) id=2734126
- [POST /b/renewMaster/courseRelation/batchFollowRelation](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734274&appId=product-b&branchName=release) id=2734274
- [POST /b/renewMaster/bindPreCourse](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734147&appId=product-b&branchName=release) id=2734147
- [POST /b/renewMaster/unbindPreCourse](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734183&appId=product-b&branchName=release) id=2734183
- [POST /b/renewMaster/listPreCourseNumberList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734289&appId=product-b&branchName=release) id=2734289
- [POST /b/renewMaster/courseRelation/add](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734180&appId=product-b&branchName=release) id=2734180
- [POST /b/renewMaster/courseRelation/change](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734118&appId=product-b&branchName=release) id=2734118
- [POST /b/renewMaster/courseRelation/modifyCalculate](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734303&appId=product-b&branchName=release) id=2734303
- [POST /b/course/deleteRelation](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1950093&appId=course-center&branchName=release) id=1950093（course-center）
