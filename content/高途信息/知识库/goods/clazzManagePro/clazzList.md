# 班级管理 / 班级列表（clazzList）

## 定位

| 项 | 值 |
|---|---|
| tab | `/ark/app-goods/clazzManagePro/list` 默认 tab「班级列表」（`tabKey=clazzList`） |
| 前端仓库 | gaotu-fe-goodsmanage（见 [_page.md](_page.md)） |
| tab 组件 | `src/pages/ClazzManage/components/index.js`（下称 `I`，2415 行）；搜索区 `src/pages/ClazzManage/SearchHead/index.js`；展开行辅导班表 `src/pages/ClazzManage/Subclazz/index.js`（下称 `S`） |
| 前端 service | `src/pages/ClazzManage/services/index.js`（下称 `svc`） |
| 后端主服务 | course-center（`CC` = `course-center-webcourse/src/main/java/com/gaotu/course/center/webcourse/controller/`，`AdminClazzController` = `CC/manager/clazz/AdminClazzController.java`，下称 `ACC`） |

## 接口清单

### 列表与搜索

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 path | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进 tab/查询/翻页/操作后刷新 | `POST /course-center/b/clazz/list/search` | `getClazzList` | `I:242`，调用 `I:319`（`svc:7`） | `ACC:155` | 列表搜索 [31473] | 读 |
| 进 tab | `GET /course-center/b/common/productLine/tree` | `getProductLine` | `I:187`、`SearchHead/index.js:40`（`src/services/clazzManage.js:252`） | 共享字典 | 产品线树 [31496] | 读 |
| 进 tab（仅 OLS） | `POST /ols/w/clazz/biz/get/partConfig` | `getLLSEnums` | `I:182`（`src/services/clazzManage.js:268`） | gaotu-ols，未追 | — | 读 |
| 搜索项「校区」挂载 | `POST /course-center/b/campus/search` | `getCampusList` | `src/components/Clazz/CampusSelect/index.js:54` → `src/models/useCampusList.js:15`（`src/pages/ClazzEdit/service.js:146`） | `campus/campus-controller/.../CampusManagementController.java:93` | 校区搜索 [未找到] | 读 |
| 自定义列 加载/新增/删除/保存/设默认 | `POST /course-center/b/columns/{getAllConfig,getUserConfig,addUserConfig,deleteUserConfig,setUserConfig,changeDefaultUserConfig}` | `getAllConfig` 等 | `I:2233-2250`（`src/services/userColumnConfig.js`），key=`getColumnsKey(false)`（`src/pages/ClazzManage/config.js:341`） | `CC/manager/custom/UserCustomPageColumnsController.java:27` | [31193]/[31197]/[31196]/[31195]/[31194]/[31198] | 读/写 |

### 顶部按钮与批量

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 path | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 「批量发布」（勾选） | `POST /course-center/b/clazz/batchPublish` | `batchPublish` | `I:2069` → `I:500`（`svc:58`） | `ACC:230` | 批量发布 [31446] | 写 |
| 其他批量功能 → 批量上架 / 批量下架 | `POST /course-center/b/clazz/batch/update/upStatus` | `batchShelves` | `I:1971` / `I:1994` → `I:493`（`svc:37`），`newStatus=1/0` | `ACC:212` | 批量上下架 [31445] | 写 |
| 其他批量功能 → 批量设置售卖状态 | `POST /course-center/b/clazz/batchChangeSaleStatus` | `batchSalesStatus` | `src/pages/ClazzManage/components/BatchSalesStatusBtn/index.js:19` | `ACC:248` | 批量改售卖状态 [310371] | 写 |
| 其他批量功能 → 批量修改适用地区 | `POST /course-center/b/clazz/batchUpdateArea` | `batchUpdateArea` | `SelectAreaModal` 确定 → `I:404`（`svc:187`） | `ACC:431` | 批量改地区 [31468] | 写 |
| 其他批量功能 → 批量设置班级主讲 | `POST /teacher-basic/b/teacher/searchFromDB`；`POST /course-center/b/clazz/teacherCategoryVerify`；`POST /course-center/b/clazz/batchEditMainTeacher` | `getTeacherList` / `teacherCategoryVerify` / `batchEditMainTeacher` | `components/BatchEditTeacher/index.js:175` / `:141` / `:84`（`src/pages/ClazzEdit/service.js:63`、`BatchEditTeacher/service.js:3,8`） | teacher-basic；`ACC:446`；`ACC:453` | 老师搜索 / 校验 [54169] / 批量改主讲 [54171] | 读/读/写 |
| 「导出班级至邮件」（仅 OLS） | `POST /course-center/b/clazz/list/export` | `exportClazz` | `I:2076` → `I:1931`（`svc:203`） | `ACC:459` | 班级导出 [669686] | 写（异步发邮件） |
| 「+ 新增班级」→ 选课程抽屉 | `POST /course-center/b/course/list` | FeituData `fetch` | `I:2086` → `CourseDrawer`（`src/pages/CourseManage/CourseList.js:669`），选完跳 `/clazzManagePro/edit/info/0/0/0?courseNumber=`（`I:2404`） | `CC/manager/course/AdminCourseController.java:86` | 课程列表 [31265] | 读 |
| 「一键排课」 | 多个 | — | `src/components/QuickArrangeDrawer/QuickArrangeButton` | 未追 | — | — |

### 行内操作（`I:1370` 起）

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 path | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 「发布」（未发布行） | `POST /course-center/b/clazz/batchPublish` | `batchPublish` | `I:1492` → `I:562`（单个也走批量） | `ACC:230` | [31446] | 写 |
| 「取消申请」（审批中） | `POST /course-center/b/audit/revokeProcess` | `clazzRevokePublish` | `I:1501`/`I:1539` → `I:602`（`svc:88`） | `CC/manager/audit/AdminAuditController.java:37` | 撤销审批 [31396] | 写 |
| 「上架」/「下架」 | `POST /course-center/b/clazz/batch/update/upStatus` | `batchShelves` | `I:1609`/`I:1627` | `ACC:212` | [31445] | 写 |
| 「开始售卖」/「停止售卖」 | `POST /course-center/b/clazz/update/saleStatus` | `changeSaleStatus` | `I:1647`/`I:1662` → `I:541`（`svc:48`）；联报冲突时二次确认带 `force:true`（`I:519`） | `ACC:202` | 改售卖状态 [31444] | 写 |
| 「删除」 | `POST /course-center/b/clazz/delete` | `clazzDelete` | `I:1701` → `I:579`（`svc:78`） | `ACC:194` | 删除班级 [31471] | 写 |
| 「修改停售时间」 | `POST /course-center/b/clazz/update/endSaleTime` | `setStopSaleTime` | `I:1711` → `components/StopSaleTimeModal/index.tsx:53`（`svc:106`） | `ACC:346` | 改停售时间 [31442] | 写 |
| 「定时停售」 | `POST /course-center/b/clazz/timer/endSale` | `setTimerStopSaleTime` | `I:1722` → `components/TimerEndSaleModal/index.tsx:54`（`svc:114`） | `ACC:356` | 定时停售 [31459] | 写 |
| 「定时上下架」打开 / 保存 / 撤销审批 | `GET /course-center/b/clazz/showAppInfo`；`POST .../showAppEdit`；`POST .../cancelShowAppApproval` | `showAppInfo` / `showAppEdit` / `cancelShowAppApproval` | `I:1733` → `components/UpDownScheduled/index.tsx:94` / `:191` / `:102`（`svc:155,163,171`） | `ACC:364` / `:370` / `:378` | [31460] / [31461] / [31462] | 读/写/写 |
| 「推荐班级」打开 / 添加 / 删除 | `GET /course-center/b/clazz/recommend/list`；`POST .../add/recommend`；`POST .../delete/recommend` | `getClazzRecommend` / `addClazzRec` / `deleteClazzRec` | `I:1773` → `components/RecommendClazz/index.tsx:105` / `:133` / `:144`（`svc:122,130,138`） | `ACC:315` / `:299` / `:308` | [31456] / [31455] / [31457] | 读/写/写 |
| 「直播推课」弹窗 | `GET /course-center/b/clazz/liveRecommendList`；`POST .../editLiveRecommend`；选班 `POST .../clazz/list/search/fullAuth`；选联报 `POST /course-setting/b/activity/list` | `getLiveRecommandList` / `editLiveRecommand` / `getClazzList` / `getUnionList` | `I:1740` → `src/components/AddRecommandLessonsModal/service.js:5,12,18,25` | `CC/LiveRecommendController.java:40`；fullAuth `ACC:165`；course-setting | [31424] / [31423] / [31448] | 读/写 |
| 「设置讲义」 | `/express-management/clazzGoodsConfig/*`、`/express-management/goodsApprovalManage/*` | `saveOrUpdate` 等 | `I:1751` → `src/components/BookSetting/service.js:4-31` | express-management，未追 | — | 读/写 |
| 「下载学员名单」（大班课已发布有学员） | `GET /clazz/exportStudentList.do` | AutoDownload | `I:1761` | 老网关路径，服务未确认 | — | 读 |
| 「销售链接」/「销售二维码」 | `POST /product-b/b/product/bff/sellLink`；`POST /course-setting/source/create` | `getShortLink` / `getSource` | `I:1442`/`I:1452` → `src/pages/GoodsManage/components/SaleUrlModal`、`SaleQRModal`（`src/services/goodsManage.js:47,60`） | product-b / course-setting，未追 | — | 读/写 |
| 「分班中」 | `POST /distribution-management/subclazz/management/checkAutoSelect`；再 `.../autoSelectSubclazz` | `newCheckAutoSelect` / `newAutoSelectSubClazz` | `I:1790` → `I:663`（`svc:147`）→ `components/AutoSelectSubClazz/index.js:38` | clazz-distribution-management，未追 | — | 读/写 |
| 「批量关辅导班」 | `POST /clazz/getAssistantList.do`；`.../listCouldCloseSubclazz`；`.../batchClose` | `getCloseClazzSearch` / `getCloseClazzData` / `getBatchCloseClazz` | `I:1808` → `components/ClazzCloseModal/index.js:66` / `:140`、`search.js` | clazz-distribution-management，未追 | — | 读/写 |
| 「批量调班」 | `POST /clazz/batchTransferStudentList.do`、`/clazz/batchTransferClazzList.do`、`/clazz/batchTransferDetail.do`、`/order/batchTransfer.do` | `batchTransfer*` | `I:1823` → `components/BatchChangeModal/index.js:74,123,220,271` | 老网关路径，未追 | — | 读/写 |
| 「我的班级草稿」→ 删除草稿 | `DELETE /course-center/b/clazz/deleteClazzDetailDraft` | `deleteClazzDetailDraft` | `I:1843` → `I:722`（`svc:179`） | `ACC:400` | 删草稿 [31465] | 写 |
| 「招生方案」 | `/distribution-management/clazzdistPlan/common/{showEnrollConfig,deleteEnrollConfig,getAllChannel,showEditEnrollConfig,editEnrollConfig}` | — | `I:1860` → `RecruitModal` → `components/PlanList/index.js:17-25`、`AdultUnion.js:19,23` | clazz-distribution-management，未追 | — | 读/写 |
| 「班级设废」 | `POST /course-center/b/clazz/ineffective` | `clazzRepeal` | `I:1877` → `I:1343`（`src/pages/ArrangeClazzManage/service.js:48`） | `ACC:239` | 班级设废 [507242] | 写 |
| 「课节内容管理」 | 多个 `/course-center/b/lesson/*` | — | `I:1559` → `src/components/LessonOptions/LessonContent` | 未逐个追 | — | 读/写 |
| 「已关联」→ 导出关联关系 | `POST /course-center/b/lesson/union/manage/export` | `exportAllClazzLessonRelation` | `components/RelationDetail/index.js:48`（`svc:195`） | `CC/manager/clazzlesson/AdminLessonManageController.java:113` | [31382] | 写（导出） |
| 查看/编辑/复制班级/班级排课/学员列表/班级家长会 | — | 路由跳转 | `I:1396`、`:1574`、`:1588`、`:1677`、`:1687`、`:1784` | — | — | — |

### 展开行：辅导班表（`I:1898` → `S`，service `src/pages/ClazzManage/Subclazz/service.js` 下称 `SS`）

`/distribution-management/*` 走青舟 appId `clazz-distribution-management.gaotu100.com`，后端仓库不在本地，表未追。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 path | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 展开行 / 刷新 | `POST /distribution-management/subclazz/management/listSubclazzByClazzNumber` | `getSubClazzList` | `S:65`（`svc:27`） | distribution | 按班级查辅导班 [31660] | 读 |
| 「学员列表」（销售/辅导角色先校验） | `POST /course-center/b/clazzHour/userListCheck` | `userListCheck` | `S:135`（`svc:98`） | `course-center-weblesson/.../manager/hour/AdminClazzHourController.java:53` | [31561] | 读 |
| 「辅导班关联课节」打开 / 取消关联 / 添加关联 / 搜主班 / 确定 | `POST /course-center/b/subclazz/{subclazzLessonUnionInfo,cancelRelate,getRelateSlaveSubclazz,getRelateMasterSubclazz,relateSubclazz}` | `getSubClazzUnionList` / `doCancelRef` / `doGetSlaveSubClazz` / `getMasterSubclazz` / `relateSubCLazz` | `S:168` / `:213` / `:263` / `components/RelevanceLessonList/index.js:50` / `S:229`（`SS:13-28`） | `CC/manager/subclazz/AdminSubclazzController.java:82` / `:55` / `:63` / `:72` / `:44` | [31260]/[31261]/[31258]/[31259]/[31262] | 读/写 |
| 「辅导班自动关联」搜索 / 保存 | `POST /course-center/b/subclazzUnion/auto/clazzSearch`、`/auto/edit` | `autoClazzSearch` / `autoEdit` | `Subclazz/SubclazzAutoMergeConfig.jsx:37` / `:74` | `CC/manager/clazzlesson/SubclazzLessonUnionController.java:59` / `:69` | [40734]/[40736] | 读/写 |
| 「新辅导班关联」打开 / 开关 / 课节查询 / 提交 | `POST /course-center/b/userFullFunctionCustomConfig/{query,add,edit}`；`/b/subclazzUnion/manual/{lessonSearch,singleSearch,edit}` | `queryFun`/`addFun`/`editFun`；FeituData / `getSingleSearch` / `manualEdit` | `Subclazz/SubClazzHandleMerge.jsx:47,63,106,186,141`；`ClazzLessonMerge.jsx:238` | `CC/manager/custom/UserFullFunctionCustomConfigController.java:23`；`SubclazzLessonUnionController.java:76` / `:88` / `:96` | query [31339]；[40738]/[40737]/[40735] | 读/写 |
| 「关班」/ 改班容 / 分配开关 | `POST /distribution-management/subclazz/management/{close,editSubclazzCount,changeAssignSwitch}` | `closeSubclazz` / `editStudentCount` / `changeAssignSwitch` | `S:303` / `:339` / `:91`（`SS:33,38,89`） | distribution | — | 写 |
| 「合班」校验 / 提交 | `POST /distribution-management/subclazz/management/combined/check`、`/combine` | `doCheck` / `doSubmit` | `components/CombinationDialog/index.js:81` / `:97` | distribution | — | 读/写 |
| 「单独添加辅导班」/「辅导班编辑」 | `POST /distribution-management/subclazz/management/create`、`/edit`；`/subclazz/checkSameTeacherSubclazz/byClazzNumberAndTeacher`；`/subclazz/relateSameTeacherSubclazz/byClazzNumber`；老师下拉 `/teacher/list.do` | `createSubclazz` / `editSubclazz` / `checkByTeacherNumber` / `relateByTeacherNumber` | `components/AddSubclazz/index.js:217-219`、`:171`、`:147` | distribution / 老网关 | — | 写 |
| 「批量添加辅导班容量」/「批量添加辅导班」上传 | `POST /distribution-management/subclazz/management/batchChangeCapacityByExcel`、`/createByExcel` | Upload `action` | `S:641` / `S:671` | distribution | — | 写 |

`SS:53` `manualExport`（`/b/subclazzUnion/manual/export`）前端无调用方，后端也未找到该路由。

## 关键表（`course_center` 库，test 集群 gaotu-course-test，cluster_id=153）

数据源 `course-center-infrastructure/.../configuration/CourseCenterDataSourceConfig.java:36`（`jdbc.coursecenter`，扫 `repository.coursecenter` + `campus.infrastructure.repository`）。`DS` = `course-center-domain/src/main/java/com/gaotu/course/center/domain/service/clazz/impl/`。

### 接口 → 表

| 接口 | 后端 service | 读 | 写（操作） | ES / MQ / 其它 |
|---|---|---|---|---|
| clazz/list/search | `ACC:155`（`@DataRight` 学段/学科/品类）→ `DS/ClazzQueryServiceImpl#listQuery:363`（`authFilter=true`） | **ES 索引 `clazz_search`**（`course-center-infrastructure/.../dao/es/base/ClazzEsDao.java:69`）；Apollo `clazz.query.es.switch`（默认 true）为 true 时拿 ES 命中的 clazzNumber 回查 `course_center.clazz`；ES 异常或 `clazz.list.query.degradation=true` 时全走 DB（`ClazzMapper.xml`） | 无 | `clazz.list.es.fail.to.end=true` 时 ES 失败直接报错 |
| clazz/batchPublish | `ACC:230` → `DS/ClazzStatusChangeServiceImpl#batchPublish:1400`（逐个调 `publish`） | `clazz`、期次校验 | `clazz` UPDATE publish_status/sale_status 等（在 `publish:1215`，按排课班 tab 的追踪结论） | 发 `ClazzPublishEvent`、推商品 SKU |
| clazz/batch/update/upStatus | `ACC:212` → `#updateStatusChange:237` | `clazz` | `clazz` UPDATE `up_status` | 发领域事件 |
| clazz/update/saleStatus | `ACC:202` → `#updateSaleStatus:324` | `clazz` | `clazz` UPDATE `sale_status` | 联报冲突返回 `interactionActivityNumberList` |
| clazz/batchChangeSaleStatus | `ACC:248` → `#batchUpdateSaleStatus` | `clazz` | `clazz` UPDATE `sale_status`（未逐行确认） | — |
| clazz/update/endSaleTime | `ACC:346` → `#updateStopSaleTime:361` | `clazz` | `clazz` UPDATE 停售时间/售卖状态 | 发领域事件 |
| clazz/timer/endSale | `ACC:356` → `#timerStopSale:496` | `clazz` | `clazz` 开/关直播推荐开关 | 发领域事件；定时任务落点未确认 |
| clazz/showAppEdit / cancelShowAppApproval | `ACC:370` → `#timerEditShowApp:565`；`ACC:378` → `#cancelEditClazzAppShelfApproval:771` | `clazz`、`product_audit_apply` | 不直接写 clazz，走 `auditProcess.auditSubmit` / `revokeProcess` 提审批 | 审批通过后定时上下架 |
| clazz/delete | `ACC:194` → `DS/ClazzDeleteServiceImpl#delete:104` | `clazz` | `clazz` 删除（未发布才可删）；连带删 `clazz_area_map`、`clazz_extension`、`clazz_file`、`clazz_chapter`、`clazz_arrange_outline_config`、`clazz_arrange_outline_vertical_config`、`arrange_outline_package_relation` | `clazzEsWriteService.writeOrRefresh` 刷 ES |
| clazz/ineffective | `ACC:239` → `DS/ClazzEffectiveStatusServiceImpl#ineffective:89` | `clazz` | `clazz` 批量 UPDATE（失效 + 停售） | 发领域事件，取消课节下游未追 |
| clazz/deleteClazzDetailDraft | `ACC:400` → `DS/ClazzQueryServiceImpl#deleteClazzDraftByClazzNumber:2787` | — | `course_center_temp_storage` DELETE | — |
| clazz/batchUpdateArea | `ACC:431` → `DS/ClazzEditServiceImpl#batchEditClazzArea:576`（Redis 锁 + 复用 `edit`） | `clazz` 详情 | `clazz_area_map` 等（走整班编辑，未逐行确认） | Redis 锁 |
| clazz/batchEditMainTeacher | `ACC:453` → `#batchEditTeacher:903`（并发 `editTeacher`） | `clazz` | 主讲关系表（推断 `clazz_teacher`，未确认） | — |
| clazz/recommend/* | `ACC:315` / `:299` / `:308` | `clazz_recommend` | `clazz_recommend` INSERT / DELETE（未逐行确认操作类型） | — |
| clazz/list/export | `ACC:459` → `#exportClazzList:2838` | 同列表 | 无 | 线程池异步，结果发邮件 |
| columns/* | 同课程管理页 | `page_columns_config`、`user_custom_page_columns_config` | `user_custom_page_columns_config` | — |
| campus/search | `CampusManagementController.java:93` | `campus_info` | 无 | — |

## 排查提示

- 列表展示和 DB 不一致：`clazz.query.es.switch=true` 时行数据来自 DB、过滤来自 ES，筛选不准就是 ES `clazz_search` 没刷
- 「删除」只对未发布班级；已发布班级只能「班级设废」
- 辅导班相关（分班/关班/合班/招生方案）都在 clazz-distribution-management，不在 course-center

## 青舟接口详情页

- [POST /b/clazz/list/search](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31473&appId=course-center&branchName=release) id=31473
- [POST /b/clazz/batchPublish](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31446&appId=course-center&branchName=release) id=31446
- [POST /b/clazz/batch/update/upStatus](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31445&appId=course-center&branchName=release) id=31445
- [POST /b/clazz/update/saleStatus](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31444&appId=course-center&branchName=release) id=31444
- [POST /b/clazz/batchChangeSaleStatus](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=310371&appId=course-center&branchName=release) id=310371
- [POST /b/clazz/delete](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31471&appId=course-center&branchName=release) id=31471
- [POST /b/clazz/ineffective](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=507242&appId=course-center&branchName=release) id=507242
- [POST /b/audit/revokeProcess](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31396&appId=course-center&branchName=release) id=31396
- [POST /b/clazz/update/endSaleTime](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31442&appId=course-center&branchName=release) id=31442
- [POST /b/clazz/timer/endSale](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31459&appId=course-center&branchName=release) id=31459
- [GET /b/clazz/showAppInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31460&appId=course-center&branchName=release) id=31460
- [POST /b/clazz/showAppEdit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31461&appId=course-center&branchName=release) id=31461
- [POST /b/clazz/cancelShowAppApproval](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31462&appId=course-center&branchName=release) id=31462
- [DELETE /b/clazz/deleteClazzDetailDraft](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31465&appId=course-center&branchName=release) id=31465
- [POST /b/clazz/batchUpdateArea](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31468&appId=course-center&branchName=release) id=31468
- [POST /b/clazz/batchEditMainTeacher](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=54171&appId=course-center&branchName=release) id=54171
- [POST /b/clazz/teacherCategoryVerify](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=54169&appId=course-center&branchName=release) id=54169
- [GET /b/clazz/recommend/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31456&appId=course-center&branchName=release) id=31456
- [POST /b/clazz/add/recommend](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31455&appId=course-center&branchName=release) id=31455
- [POST /b/clazz/delete/recommend](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31457&appId=course-center&branchName=release) id=31457
- [POST /b/clazz/list/export](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=669686&appId=course-center&branchName=release) id=669686
- [POST /b/lesson/union/manage/export](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31382&appId=course-center&branchName=release) id=31382
- [POST /b/clazzHour/userListCheck](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31561&appId=course-center&branchName=release) id=31561
- [POST /subclazz/management/listSubclazzByClazzNumber](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31660&appId=clazz-distribution-management.gaotu100.com&branchName=release) id=31660
- 辅导班关联：[31260](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31260&appId=course-center&branchName=release) subclazzLessonUnionInfo、[31262](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31262&appId=course-center&branchName=release) relateSubclazz、[31261](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31261&appId=course-center&branchName=release) cancelRelate、[40735](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=40735&appId=course-center&branchName=release) manual/edit、[40736](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=40736&appId=course-center&branchName=release) auto/edit
