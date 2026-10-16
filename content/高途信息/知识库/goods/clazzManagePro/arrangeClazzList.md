# 班级管理 / 排课班列表（arrangeClazzList）

## 定位

| 项 | 值 |
|---|---|
| tab | `/ark/app-goods/clazzManagePro/list?tabKey=arrangeClazzList`「排课班列表」 |
| 前端仓库 | gaotu-fe-goodsmanage（见 [_page.md](_page.md)） |
| tab 组件 | `src/pages/ArrangeClazzManage/index.jsx`（`src/pages/ClazzManage/Container.jsx:24` 懒加载）；行操作 `Operations.jsx`；service `src/pages/ArrangeClazzManage/service.js`（下称 `svc`） |
| 后端主服务 | course-center：`ArrangeClazzController`（`course-center-webcourse/.../controller/manager/clazz/ArrangeClazzController.java`，类 `{"/b/arrangeClazz/","/ols/arrangeClazz"}`，下称 `AR`）+ `AdminClazzController`（下称 `ACC`） |
| 新增/编辑/查看/复制 | 跳 `/clazzManagePro/arrangeClazz/detail?type=create|edit|view`（→ `src/pages/ArrangeClazzEdit`），不在本 tab 范围 |

## 接口清单

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 path | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进 tab / 查询 / 翻页 / tab 切回 | `POST /course-center/b/arrangeClazz/list/search` | FeituData `fetch` | `index.jsx:326` | `AR:104` | 排课班列表 [33199] | 读 |
| 进 tab | `GET /course-center/b/common/productLine/tree` | `doGetProductLineTree` | `index.jsx:58` → `src/models/clazzManage.js:134` | 共享字典 | 产品线树 [31496] | 读 |
| 进 tab / 校区下拉（countCampus 为空） | `POST /ols/w/clazzroom/byAccount`、`/ols/w/campus/byAccount` | `getClazzRoomByCount` / `getCampusByCount` | `index.jsx:68` → `src/models/useCampusList.js:34`（`src/pages/ClazzEdit/service.js:159,168`） | gaotu-ols，未追 | — | 读 |
| 「批量发布」 | `POST /course-center/b/arrangeClazz/batchPublish` | `batchPublish` | `index.jsx:239`（`svc:16`） | `AR:98` | 批量发布 [33195] | 写 |
| 行内「发布」 | `POST /course-center/b/clazz/publish` | `clazzPublish` | `Operations.jsx:13`（`svc:27`） | `ACC:222` | 发布 [31469] | 写 |
| 行内「删除」（未发布） | `POST /course-center/b/arrangeClazz/delete` | `clazzDelete` | `Operations.jsx:23`（`svc:38`） | `AR:83` | 删除排课班 [33197] | 写 |
| 行内「班级设废」 | `POST /course-center/b/clazz/ineffective` | `clazzRepeal` | `Operations.jsx:37`（`svc:48`） | `ACC:239` | 班级设废 [507242] | 写 |
| 「批量操作」下拉挂载 | `GET /course-center/b/batch/queryAllFunction?source=pkblb` | `queryAllFunction` | `src/components/BatchOperations/index.jsx:27`（`service.js:13`） | `job/BatchController.java:50` | [31556] | 读 |
| 批量操作弹窗打开 | `GET /course-center/b/batch/queryOperateConfig` | `queryOperateConfig` | `src/components/BatchOperations/OperateModal.jsx:34`（`service.js:21`） | `BatchController.java:56` | [31550] | 读 |
| 批量操作弹窗上传文件 | `POST https://internal-storage.genshuixue.com/privateUpload/upload` | Upload `action` | `OperateModal.jsx:22,128` | 外部存储 | — | 写 |
| 批量操作弹窗提交 | `POST /course-center/b/batch/submit` | `submitOperation` | `OperateModal.jsx:76`（`service.js:29`） | `BatchController.java:67` | [31555] | 写 |
| 自定义列 加载/新增/删除/保存/设默认 | `POST /course-center/b/columns/*` | `getAllConfig` 等 | `index.jsx:363-379`（`src/services/userColumnConfig.js`） | `UserCustomPageColumnsController.java:27` | [31193]/[31197]/[31196]/[31195]/[31194]/[31198] | 读/写 |
| 学员列表 / 排课 | — | 路由跳转 | `Operations.jsx:92`（`/clazzManagePro/studentList/:clazzNumber/4`）、`:103`（`/clazz/offine/arrange/:clazzNumber`） | — | — | — |

字典（学部/学年/学期/年级/学科/品类）读 `useModel('clazzManage')`，由页面 wrapper 加载，见 [_page.md](_page.md)。

### 入参

> 以 course-center / gaotu-ols 源码为准（2026-10-16 定位）。`Pager`（`entity/common/Pager.java:29-37`）= `pageSize`/`current`/`total`（Integer, 可选）。

- `POST /b/arrangeClazz/list/search`（`ArrangeClazzController#list:107`，DTO `ArrangeClazzListQueryRequest extends BaseRequest`，`entity/clazz/request/ArrangeClazzListQueryRequest.java`）：
  - 继承 `BaseRequest`：`pager`(Pager)、`scrollId`(String)、`scrollSize`(Integer)，可选
  - `fullFuzzyText` (String, 可选) — 综合搜索；`categoryIdPath` (String, 可选) — 课程品类路径
  - `campusClazzRoomPathList` (List\<String>, 可选) — 班级校区路径；`schoolTermIdList` (List\<String>, 可选) — 学期
  - `schoolDepartmentList` / `gradeIdList` / `subjectIdList` / `schoolYearIdList` / `publishStatusList` / `testClazzList` (List\<Integer>, 可选) — 学部/年级/学科/学年/发布状态/是否测试
  - `teacherNumberList` (List\<Long>, 可选) — 老师编号
- `GET /course-center/b/common/productLine/tree`：GET，无请求体。
- `POST /ols/w/clazzroom/byAccount`（gaotu-ols `ClazzroomController#myAccount:73`）：**方法无参、无请求体**（按登录账号取教室）。
- `POST /ols/w/campus/byAccount`（gaotu-ols `CampusInfoController#byAccount:120`，DTO `MyCampusQry`）：`campusName` (String, 可选) — 校区名（方法内 `request.getCampusName()`）。
- `POST /b/arrangeClazz/batchPublish`（`ArrangeClazzController#batchPublish:99`，DTO `ClazzNumberListRequest`）：`clazzNumberList` (List\<Long>, 可选)。
- `POST /b/clazz/publish`（`AdminClazzController#publish:224`，DTO `ClazzNumberRequest`）：`clazzNumber` (Long, 可选) — 单个发布。
- `POST /b/arrangeClazz/delete`（`ArrangeClazzController#delete:85`，DTO `ArrangeClazzEditRequest extends ArrangeClazzCreateRequest`）：本接口只用 `clazzNumber` (Long, 可选；`:87` 取 `request.getClazzNumber()`)，其余继承字段未使用。
- `POST /b/clazz/ineffective`（`ACC#ineffective:241`，DTO `ClazzNumberListRequest`）：`clazzNumberList` (List\<Long>, 可选)。
- `GET /b/batch/queryAllFunction`（`BatchController#getAllOperateCode:51`）：query `source` (String, 可选；本页传 `pkblb`)。
- `GET /b/batch/queryOperateConfig`（`BatchController#getWindowInfo:57`）：query `operateCode` (Integer, 必填，无 `@NotNull` 但缺参 400)。
- `POST https://internal-storage.genshuixue.com/privateUpload/upload`（外部存储）：multipart 文件上传，非本项目后端。
- `POST /b/batch/submit`（`BatchController#uploadJob:68`，DTO `BatchOperateUploadRequest`）：`operateCode`(Integer)、`fid`(String)、`fileName`(String)、`fileUrl`(String, fid 取 url 失败时兜底)、`desc`(String)、`optionalCode`(Integer) — 均可选。
- `POST /b/columns/*`：DTO 与 [课程管理页入参](../CourseManagePro/_page.md#入参) 一致（`PageConfigGetRequest` / `UserConfigListRequest` / `UserConfigAddRequest` / `UserConfigDeleteRequest` / `UserConfigModifyRequest` / `UserConfigSelectRequest`）。

## 关键表（`course_center` 库）

| 接口 | 后端 service | 读 | 写（操作） | ES / MQ / 其它 |
|---|---|---|---|---|
| arrangeClazz/list/search | `ArrangeClazzReadServiceImpl#listQuery:153` → `esSearch:482` | **ES 索引 `clazz_search`**；ES 异常回落 `course_center.clazz`；结果由 `ArrangeClazzDataResultAssemble` 的 10 个 binder 组装（各 binder 读表未追） | 无 | — |
| arrangeClazz/batchPublish | `ArrangeClazzWriteServiceImpl#batchPublish` → 逐个 `clazzStatusChangeService.publish` | 同 publish | 同 publish | 同 publish |
| clazz/publish | `ClazzStatusChangeServiceImpl#publish:1215` | `clazz`、`clazz_period_map`、`course`、`clazz_file` | 事务内 `clazz` UPDATE publish_status/publish_time/audit_status/sale_status 和 app | 发 `ClazzPublishEvent`、`pushSkuProduct` 推商品 |
| arrangeClazz/delete | `ArrangeClazzWriteServiceImpl#delete` | arrangeClazzAgg、`course` | `clazz` UPDATE `isdel=1`（限 `publish_status=0`，`ClazzDao.java:52`）；删 `clazz_extension`、`clazz_teacher`；`courseDelService.delByNumberList` 删课程 | `courseCenterSender.send` 发 MQ；`clazzEsWriteService.writeOrRefresh` 刷 ES |
| clazz/ineffective | `ClazzEffectiveStatusServiceImpl#ineffective:89` | `clazz` | `clazz` 批量 UPDATE | 发领域事件 |
| batch/queryAllFunction · queryOperateConfig | `BatchServiceImpl#queryOperateMap:551` / `queryWindowInfo:650` | 不查表，读 Apollo `operate.package` / `window.info.package` | 无 | — |
| batch/submit | `BatchServiceImpl#uploadBatchOperate:695` | — | 本地不落表 | Feign `IJobCommitFeignClient.submitJob/V2`（外部 jar，下游未追） |
| columns/* | `UserCustomPageColumnsConfigApplication` | `page_columns_config`、`user_custom_page_columns_config` | `user_custom_page_columns_config` | — |

## 排查提示

- 排课班「删除」是逻辑删 `clazz.isdel=1`，只对未发布有效；`clazz_extension`/`clazz_teacher` 是物理删还是逻辑删 未确认
- 批量操作的任务实际执行在下游 job 服务（`IJobCommitFeignClient`），本服务只提交

## 青舟接口详情页

- [POST /b/arrangeClazz/list/search](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=33199&appId=course-center&branchName=release) id=33199
- [POST /b/arrangeClazz/batchPublish](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=33195&appId=course-center&branchName=release) id=33195
- [POST /b/arrangeClazz/delete](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=33197&appId=course-center&branchName=release) id=33197
- [POST /b/clazz/publish](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31469&appId=course-center&branchName=release) id=31469
- [POST /b/clazz/ineffective](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=507242&appId=course-center&branchName=release) id=507242
- [GET /b/batch/queryAllFunction](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31556&appId=course-center&branchName=release) id=31556
- [GET /b/batch/queryOperateConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31550&appId=course-center&branchName=release) id=31550
- [POST /b/batch/submit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31555&appId=course-center&branchName=release) id=31555
