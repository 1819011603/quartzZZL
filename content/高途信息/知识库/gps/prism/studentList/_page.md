# 学员花名册 / 我的学员（studentList）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 prism master 代码整理；后端对照 student-center（origin/master `9cfc479`）、course-scene-lifecycle（master `d3f0af6`）、course-center（master `4ce8eda`）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/prism/studentList` |
| 基座 | GPS 系统 test-os（qiankun）→ 子应用 prism（chunk `p__studentList__index`） |
| 前端仓库 | prism `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/prism`（master `148a757`，本地 `~/IdeaProjects/WebProject/prism`，umi） |
| 前端路由 | `config/routes.ts:26-30` → `src/pages/studentList/index`（`index.tsx`）；按钮权限 `STUDENT_LIST_BOOK`（约课）、`STUDENT_LIST_ARRANGE`（排课）、`MY_STUDENT_BATCH_ADD_ACTIVITY`（批量添加活动） |
| 后端主服务 | 网关前缀 `/bgwApi/student-center` → 青舟 appId `student-center`（`MyStudentController` `@RequestMapping({"/my-student", "/gps/my-student"})`，`student-center-web/.../web/api/MyStudentController.java:35`） |
| 约课抽屉 | 复用 `src/pages/delivery/serviceOrder/components/bookLesson/ApplyBookLessonDrawer.tsx`，常驻挂载（`index.tsx:555`），其字典 hook 进页面即请求，所以抓包里能看到 `/course-scene/b/support/form/book/lesson/dict/*`、`/config` 和 `teachDepartment/listAll` |

⚠️ 本地 student-center 当前分支 `feature-xuban-expand-exclude` 落后，没有 `/edit`；以上行号均以 `origin/master` 为准。

## tab 列表

页面本身无 tab。行操作打开的抽屉：

| 入口 | 组件 | 说明 |
|---|---|---|
| 点学员姓名 | `components/StudentProfileDrawer/index.tsx`（内部 tab：用户信息/订单/合同/学员日历/动态，`config.ts:19`） | `@coeus/widget-render` 物料 + iframe，接口由物料自己发，未在 prism 中逐个确认 |
| 约课 | `ApplyBookLessonDrawer`（delivery 共用） | 见下表 |
| 排课 / 排课明细 | `@gaotu/arrange-ui` `ArrangeCreateDrawer` / `ArrangeDetailDrawer` | npm 组件内部接口，未确认 |
| 课时账户 | `@gaotu/hour-account` `HourAccountDrawer` | npm 组件内部接口，未确认 |
| 批量添加活动 | `@gaotu/cms-ui` `BatchAddActivityDrawer` | npm 组件内部接口，未确认 |
| 工作台 | `window.open` `studentDetail?userId=&subTeachProductId=`（`index.tsx:212`） | 不调接口 |

## 页面级接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面/查询/翻页/排序/抽屉关闭后刷新 | `POST /bgwApi/student-center/gps/my-student/list` | FeituData fetch（`API_URL`） | `src/pages/studentList/index.tsx:57`/`:430` | student-center | 我的学员列表 [4556718] | 读 |
| 进页面（年级下拉 + 年级列翻译） | `GET /bgwApi/student-center/base/gaiaEnums/grade` | `fetchGradeEnums` | `index.tsx:175`（`src/services/studentList.ts:23`） | student-center | 单个枚举通用接口（共享字典）[30710] | 读 |
| 列表行内改姓名/年级 | `POST /bgwApi/student-center/gps/my-student/edit` | `editStudentField` | `src/pages/studentList/data.tsx:122`（`src/services/studentList.ts:29`） | student-center | 我的学员编辑 [5744898] | 写 |
| 进页面（约课抽屉字典） | `POST /course-scene/b/support/form/book/lesson/dict/listSubjects` / `dict/listGrades` / `dict/listAll` | `listBookLessonSubjects` / `listBookLessonGrades` / `listBookLessonAllDicts` | `bookLesson/hooks/useBookLessonDicts.ts:31-34`（`src/services/serviceOrderForm.ts:271/278/285`） | course-scene-lifecycle | 共享字典 [4557896]/[4557880]/[4557887] | 读 |
| 进页面（约课抽屉字典） | `POST /course-center/b/teachProduct/teachDepartment/listAll` | `listTeachDepartments` | `useBookLessonDicts.ts:33`（`serviceOrderForm.ts:264`） | course-center | 共享字典 [4555206] | 读 |
| 进页面（约课配置） | `POST /course-scene/b/support/form/book/lesson/config` | `fetchBookLessonConfig` | `bookLesson/hooks/useBookLessonConfig.ts:9`（`serviceOrderForm.ts:303`） | course-scene-lifecycle | 约课配置 [4557891] | 读 |
| 约课抽屉：选学员后带子产品 | `POST /course-scene/b/support/form/assistant-teacher-change/search/subProduct` | `fetchTeacherChangeSubProducts` | `bookLesson/hooks/useSubProducts.ts:39`（`serviceOrderForm.ts:127`） | course-scene-lifecycle | 查询调老师子产品列表 [4557885] | 读 |
| 约课抽屉：选主讲 | `POST /course-scene/b/support/form/book/lesson/search/mentor` | `searchBookLessonMentors` | `bookLesson/hooks/useMentorField.ts:54`（`serviceOrderForm.ts:292`） | course-scene-lifecycle | 约课主讲搜索 [4557879] | 读 |
| 约课抽屉：大纲约课选节点 | `POST /course-center/b/teachProduct/lessonNodeByClazzType` | `fetchLessonNodesByClazzType` | `bookLesson/hooks/useOutlineNodes.ts:30`（`serviceOrderForm.ts:257`） | course-center | 班型课堂节点 [2405643] | 读 |
| 约课抽屉「提交申请」 | `POST /course-scene/b/support/form/book/lesson/create` | FeituData fetch（`endpoint`） | `ApplyBookLessonDrawer.tsx:899`/`:949` | course-scene-lifecycle | 申请约课服务单 [4557881] | 写 |

## 关键表 / 索引

### 后端链路

- `my-student/list`：`MyStudentController.java:48` → `MyStudentService#page:105` → `MyStudentEsQueryBuilder#buildListQuery`（按登录老师 accountId 过滤）→ ES `ads_user_container_allocation`（Apollo `my.student.es.index`，`studentServeClient`，`MyStudentService.java:68`）；再按 Apollo `my.student.list.enrich.fields`（默认 `["userGrade"]`）经 `DataHelperV2` 回源刷新年级。
- `my-student/edit`：`MyStudentController.java:71` → `MyStudentEditService#edit`：
  - `GRADE` → `StudentListEditServiceImpl#editGrade` → `UserAclService#updateByUserId`（用户中心 `userRemoteAdapter.updateByUserId`）
  - `NAME` → `#editStudentName`（scene `ONE_BY_ONE_ROSTER`）→ `IStudentDetailAclService#update`（用户中心 `updateStudentDetail`）→ 读 `user_clazz_sync_flow` 触发 ES 重算 → `userContainerAllocationService.updateStudentNameByUserId` 改 ES `ads_user_container_allocation`
- `base/gaiaEnums/{bizName}`：`BaseController.java:91`（`@RequestMapping("/base")`）→ `dynamicFormService.listFieldPropsByName`（GAIA 字段配置）。
- `book/lesson/create`：`BookLessonSupportFormController.java:87`（`@RequestMapping("/b/support/form/book/lesson")`）→ `BookLessonSupportFormAppService#apply:509` → `applyInternal:546` → `BookLessonSupportFormDomainService#create` + `insertTimeIndex`；异常时 `saveApplyFailed` 落 APPLY_FAILED 单。

### 接口 → 表

| 接口 | 读 | 写（操作） | 其它 |
|---|---|---|---|
| `gps/my-student/list` | ES `ads_user_container_allocation` | 无 | 年级字段回源（ods 数据源，未逐个确认） |
| `gps/my-student/edit` | `user_clazz_sync_flow`（student-center 库，改姓名时） | 用户中心（年级/姓名）；ES `ads_user_container_allocation` UPDATE `studentName` | 下游用户中心表不在本仓库 |
| `base/gaiaEnums/grade` | GAIA 字段配置 | 无 | 共享字典 |
| `book/lesson/create` | 课节/班型 Feign | `course_scene_lifecycle.support_form`、`book_lesson_support_form`、`book_lesson_support_form_time_index` INSERT | 事件发布后写宽表 ES `support_form_search`（推断） |
| `book/lesson/dict/*`、`config`、`teachDepartment/listAll` | — | 无 | 共享字典 |

## 排查提示

- 花名册列表空/少人：数据全在 ES `ads_user_container_allocation`，按登录老师的分配关系过滤；先确认学员容器分配是否落 ES
- 改了年级列表没变：列表年级默认会回源（`my.student.list.enrich.fields`），配成空数组就退回 ES 快照
- 改姓名后其它花名册没同步：姓名按 `user_clazz_sync_flow` 触发重算；姓名写的是用户中心，副作用可参考 [改姓名后亲密称呼跟着变化](../../../../工单/CRM与客服工具/企微侧边栏/案例/2026-09-11-改姓名后亲密称呼跟着变化.md)（企微侧边栏场景，仅作线索）
- 约课、排课、课时账户问题走对应 npm 组件和 course-scene 约课单，不在本页列表链路里

## 青舟接口详情页

- [POST /my-student/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4556718&appId=student-center&branchName=release) id=4556718（青舟按 `/my-student` 前缀收录，`/gps/my-student` 是同一方法）
- [POST /my-student/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5744898&appId=student-center&branchName=release) id=5744898
- [GET /base/gaiaEnums/{bizName}](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30710&appId=student-center&branchName=release) id=30710
- [POST /b/support/form/book/lesson/create](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4557881&appId=course-scene-lifecycle&branchName=release) id=4557881
- [POST /b/support/form/book/lesson/config](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4557891&appId=course-scene-lifecycle&branchName=release) id=4557891
- [POST /b/support/form/book/lesson/search/mentor](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4557879&appId=course-scene-lifecycle&branchName=release) id=4557879
- [POST /b/support/form/assistant-teacher-change/search/subProduct](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4557885&appId=course-scene-lifecycle&branchName=release) id=4557885
- [POST /b/support/form/book/lesson/dict/listSubjects](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4557896&appId=course-scene-lifecycle&branchName=release) id=4557896
- [POST /b/support/form/book/lesson/dict/listGrades](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4557880&appId=course-scene-lifecycle&branchName=release) id=4557880
- [POST /b/support/form/book/lesson/dict/listAll](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4557887&appId=course-scene-lifecycle&branchName=release) id=4557887
- [POST /b/teachProduct/teachDepartment/listAll](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=4555206&appId=course-center&branchName=release) id=4555206
- [POST /b/teachProduct/lessonNodeByClazzType](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2405643&appId=course-center&branchName=release) id=2405643
