# 课程管理（CourseManagePro）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-goodsmanage master 代码整理；后端对照 course-center。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-goods/CourseManagePro/list` |
| 基座 | OES ark → 子应用 app-goods（chunk `p__CourseManage__index`） |
| 前端仓库 | gaotu-fe-goodsmanage `http://git.baijia.com/gaotu-ctech/gaotu-fe-goodsmanage`（master，本地 `~/IdeaProjects/WebProject/gaotu-fe-goodsmanage`） |
| 前端路由 | `config/routes.js:42` → `src/pages/CourseManage/index.js`，wrapper `@/wrappers/clazzManage`（进页加载 4 个字典） |
| 列表组件 | `src/pages/CourseManage/CourseList.js`（FeituData `fetch` 直连，`:669`）；本组件也被「添加续报前置课程」抽屉 `src/components/Clazz/CourseListModal/CourseDrawer.js` 复用 |
| 新增/再开一课/查看 | 跳 `/CourseManagePro/message/:status/:type/:courseNumber/:originCourseNumber`（`routes.js:49` → `src/pages/CourseEdit/index`），不在本页范围 |
| 后端服务 | 网关前缀 `/course-center` → 青舟 appId `course-center`（gapm-appid `course-center-b`，仓库 **course-center**，模块 `course-center-webcourse`，`AdminCourseController` 类映射 `/b/course/`） |

## tab 列表

无 tab，列表 +「续报设置」抽屉。

## 页面级接口

`CC` = `course-center-webcourse/src/main/java/com/gaotu/course/center/webcourse/controller/manager/`；前端 `service` = `src/pages/CourseManage/service/index.ts`。`app.js` 无全局请求前缀，路径即实际请求路径。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（wrapper，字典为空时） | `GET /course-center/b/common/dictionary/all` | `getDictionary` | `src/models/clazzManage.js:101`（`src/services/clazzManage.js:13`） | course-center | 共享字典 [31330] | 读 |
| 同上 | `GET /course-center/b/common/department/tree` | `getNewDepartment` | `src/models/clazzManage.js:101`（`src/services/clazzManage.js:33`） | course-center | 共享字典·部门树 [31497] | 读 |
| 同上 | `GET /course-center/b/common/category/tree` | `getNewTree` | `src/models/clazzManage.js:101`（`src/services/clazzManage.js:27`） | course-center | 共享字典·品类树 [31498] | 读 |
| 同上 | `GET /course-center/b/common/dictionary/allConfigurable` | `getDefaultCourseConfig` | `src/models/clazzManage.js:101`（`src/services/clazzManage.js:53`） | course-center | 共享字典·可配置项 [31331] | 读 |
| 进页面 | `GET /course-center/b/common/productLine/tree` | `getProductLine`（`doGetProductLineTree`） | `src/pages/CourseManage/CourseList.js:105`（`src/services/clazzManage.js:252`） | course-center | 共享字典·产品线树 [31496] | 读 |
| 进页面（umi 全局 model，非手动） | `GET /intranet-rpc/course-setting/feign/options/bff/list?fields=all` | `getCommonDictionary` | `src/models/useBffSelectItem.js:11`（`src/services/goodsManage.js:12`） | course-setting | bff 选项字典 | 读 |
| 搜索项「校区」下拉挂载 | `POST /course-center/b/campus/search` | `getCampusList`（`doGetCampusList`） | `src/components/Clazz/CampusSelect/index.js:54` → `src/models/useCampusList.js:15`（`src/pages/ClazzEdit/service.js:146`） | course-center | 校区搜索 [未找到] | 读 |
| 进页面/查询/翻页/操作后刷新 | `POST /course-center/b/course/list` | FeituData `fetch` | `src/pages/CourseManage/CourseList.js:669` | course-center | 课程管理列表 [31265] | 读 |
| 表格「自定义列」加载 | `POST /course-center/b/columns/getAllConfig`、`/getUserConfig` | `getAllConfig` / `getUserConfig` | `CourseList.js:711-712`（`src/services/userColumnConfig.js:8,16`） | course-center | 全量列配置 [31193] / 用户列配置 [31197] | 读 |
| 自定义列 新增/删除/保存/设为默认 | `POST /course-center/b/columns/addUserConfig`、`/deleteUserConfig`、`/setUserConfig`、`/changeDefaultUserConfig` | `addUserConfig` / `delUserConfig` / `updateUserConfig` / `changeDefaultConfig` | `CourseList.js:713-730`（`userColumnConfig.js:23,29,35,41`） | course-center | [31196] / [31195] / [31194] / [31198] | 写 |
| 行内「删除」（`clazzTotal===0`） | `POST /course-center/b/course/delete` | `deleteCourse` | `src/pages/CourseManage/index.js:66`（`service:4`），body `{courseNumberList}` | course-center | 删除课程 [31266] | 写 |
| 行内「发布课程」/ 顶部「批量发布」 | `POST /course-center/b/course/publish` | `setpublishStatus` | `index.js:76`（单个）、`index.js:84`（批量）（`service:35`），失败弹 `ErrorModal` | course-center | 发布课程 [31269] | 写 |
| 行内「续报设置」→ 打开抽屉 | `POST /course-center/b/course/relationList` | `getRelationList` | `src/pages/CourseManage/Continueset.jsx:52`（`service:12`），`relationType=1` | course-center | 课程关联列表 [31270] | 读 |
| 抽屉「添加续报前置课程」 | `POST /course-center/b/course/list` | FeituData `fetch` | `Continueset.jsx:202` → `CourseDrawer` → `CourseList.js:669`（bizOpenType=`Continue`） | course-center | 课程管理列表 [31265] | 读 |
| 抽屉「确定」/ 行内删除前置课 | `POST /course-center/b/course/modifyCourseRelation` | `setrelationChange` | `Continueset.jsx:98`（`service:26`） | course-center | 修改课程续报关系 [703439] | 写 |

- 「查看子产品」(`index.js:212`) 只做 `window.open`，不调接口；「新增课程」「再开一课」「查看」是路由跳转。
- `useBffSelectItem` 是 `src/models/` 下的 umi model，`useRequest` 未设 `manual`；抓包每页都出现，推断是 plugin-model 全局初始化触发（未逐行确认 umi 版本行为）。

## 关键表（`course_center` 库，test 集群 gaotu-course-test，cluster_id=153）

> 2026-10-09 test 库 `information_schema` 已确认 `course_center.course` / `course_center.clazz` / `course_center.course_relation_map` 存在；数据源 `CourseCenterDataSourceConfig`（`jdbc.coursecenter`）。

### 接口 → 表

| 接口 | 后端 controller → service | 读 | 写（操作） | ES / MQ / 其它 |
|---|---|---|---|---|
| course/list | `CC/course/AdminCourseController.java:86` → `CourseQueryServiceImpl#listQuery:254`（`authFilter=true`，带数据权限） | **ES 索引 `course_search`**（`CourseEsSearchDao.java:61`）；ES 异常或开关 `course.list.query.degradation=true` 时降级查 `course_center.course`（`CourseMapper.xml`）；`course.list.es.fail.to.end=true` 时 ES 失败直接报错不降级 | 无 | Apollo `course.list.arrange.course.filter`（默认 true，只查 SPU 场景课程） |
| course/delete | `AdminCourseController.java:117` → `CourseDelServiceImpl#delByNumberList:76` | `clazz`（按课程查班级） | `course`（`delByNumbers`）；连带删 `course_extension`、`course_category_map`、`course_attr_relation`、`course_clazz_tag`、`course_school_relation`、`outline`、`chapter` | `courseEsSearchDao.delete` 删 ES 文档；发 Spring 事件 `CourseDelEvent` |
| course/publish | `AdminCourseController.java:125` → `CourseStatusChangeServiceImpl#publishCourse:95` | `course`、发布校验 | `course` UPDATE `publish_status`（`:182`）、UPDATE app（`:186`） | 发 `CoursePublishEvent`（`:194`），下游刷 ES 未追 |
| course/relationList | `AdminCourseController.java:141` → `CourseRelationServiceImpl#listRelationCourseList:71` | `course_relation_map`、`course` | 无 | — |
| course/modifyCourseRelation | `AdminCourseController.java:194` → `CourseRelationServiceImpl#courseRelationChange:99` | `course_relation_map`、`course` | `course_relation_map`（增删关系，具体 write 调用在下层方法，未逐行确认） | — |
| columns/* | `CC/custom/UserCustomPageColumnsController.java:27`（`:35` getAllConfig，`:40` set，`:47` delete，`:54` add，`:61` getUserConfig，`:67` changeDefault） | `page_columns_config`（`PageColumnsConfigMapper.xml`）、`user_custom_page_columns_config` | `user_custom_page_columns_config` | 课程页 key = `columnsKey`（`src/pages/CourseManage/config.js:118`，按 `b_client` 区分） |
| campus/search | `campus/campus-controller/.../CampusManagementController.java:93`（类 `/b/campus`）→ `campusInfoApplication.campusInfoList` | `campus_info`（`CampusInfoMapper.xml`，同 coursecenter 数据源） | 无 | — |

## 排查提示

- 列表查不到 / 数据和库不一致 → 先怀疑 ES `course_search` 未刷新；把 `course.list.query.degradation` 打开就是走 DB（但 DB 降级只支持名称/编号条件，品类/年级/学科鉴权失效）
- 删除按钮不显示：`clazzTotal>0`、GPS 课程、线下 1v1 产品体系课程都隐藏（`index.js:162-165`）
- 发布失败原因看返回 `failList[].failReason`，单个失败 toast，批量失败弹 `ErrorModal`

## 青舟接口详情页

- [POST /b/course/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31265&appId=course-center&branchName=release) id=31265
- [POST /b/course/delete](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31266&appId=course-center&branchName=release) id=31266
- [POST /b/course/publish](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31269&appId=course-center&branchName=release) id=31269
- [POST /b/course/relationList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31270&appId=course-center&branchName=release) id=31270
- [POST /b/course/modifyCourseRelation](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=703439&appId=course-center&branchName=release) id=703439
- [POST /b/columns/getAllConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31193&appId=course-center&branchName=release) id=31193
- [POST /b/columns/getUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31197&appId=course-center&branchName=release) id=31197
- [POST /b/columns/addUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31196&appId=course-center&branchName=release) id=31196
- [POST /b/columns/deleteUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31195&appId=course-center&branchName=release) id=31195
- [POST /b/columns/setUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31194&appId=course-center&branchName=release) id=31194
- [POST /b/columns/changeDefaultUserConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31198&appId=course-center&branchName=release) id=31198
- [GET /b/common/productLine/tree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31496&appId=course-center&branchName=release) id=31496
- `/b/campus/search`：青舟 course-center 全分支搜索 0 条，未录入
