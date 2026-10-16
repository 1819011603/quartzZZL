# 排课结果（arrangeResult）— 页面级

> 2026-10-16 test 环境 chrome-devtools 抓包 + 前端 gps-operation master 代码整理；后端未对照（仅凭前端代码推断 path）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/app-operation/arrangeResult` |
| 导航 | 顶部「运营」→ 左侧「排课管理」→「排课结果」 |
| 基座 | GPS（test-os.baijia.com）qiankun 基座 → 子应用 app-operation（与 `clazzManageNew` 同仓库） |
| 前端仓库 | gps-operation `http://git.baijia.com/esfe/gps-operation`（master `ab924d5`，本地 `~/IdeaProjects/WebProject/gps-operation`） |
| 前端路由 | `src/routes/index.tsx:42` `/arrangeResult` → `src/pages/ArrangeResult/index.tsx` |
| 后端服务 | `baseApi`（`src/services/arrangeResult.ts`，值未在当前读取范围内确认，推断为 `/bgwApi/course-center`） → course-center |

## tab 列表

页面无 tab，顶部按异常类型分组统计（未排班级 / 缺少老师或时间 / 老师上课时间冲突 / 产品单元课节已被删除），下方是课节级列表 + 筛选表单（产品单元/班级名称/主讲名称，展开更多）。

## 页面级接口

`AR/` = `src/pages/ArrangeResult/`，`SVC` = `src/services/arrangeResult.ts`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 请求体 | 读/写 |
|---|---|---|---|---|---|---|
| 进页面 / 查询 / 翻页 | `POST /bgwApi/course-center/b/lessonArrangeResult/list` | `getArrangeResultList` | `AR/index.tsx:405`（`SVC:172`） | course-center | `ArrangeResultSearchParams` | 读 |
| 进页面（顶部 4 个异常统计） | `GET .../b/lessonArrangeResult/getExceptionNum` | `getAbnormalData` | `SVC:175`，调用方 `AR/hooks/useArrangeResultData.tsx:5`（`manual:true`，需手动 `run`） | course-center | — | 读 |
| 进页面（「未排班级」计数） | `POST .../b/teachProduct/node/search` | `getUnarrangedNodeList` | `SVC:213`，调用方 `useArrangeResultData.tsx:6` | course-center | `UnarrangedNodeSearchParams` | 读 |
| 教室筛选项联想（`ClassroomMultiSearch` 组件） | `POST .../b/offline/clazzroom/searchGroupByCampus` | `searchClazzroomGroupByCampus` | `SVC:262`，调用方 `src/components/SearchComponents/ClassroomMultiSearch/index.tsx:31` | course-center | `{"keyword":"..."}` | 读 |
| 学部筛选（经 `useAllDepartments` hook，与 `clazzManageNew` 共用） | `POST .../b/teachProduct/teachDepartment/listAll` | `fetchTeachDepartments` | `src/services/clazzManageNew.ts:81` | course-center | `{"statusList":[1]}` | 读 |
| 「添加排课」/「班级排课」 | `POST .../b/teachClazz/search` | `getUnArrangedClazzList` | `SVC:204` | course-center | `{"arrangeModeTypeList":[...],"arrangeStatus":...,"pager":{...}}` | 读 |
| 「添加排课」确定 | `POST .../b/lessonArrangeResult/create` | `createArrangeResult` | `SVC:210` | course-center | `CreateArrangeResultParams` | 写 |
| 行「编辑」 | `POST .../b/lessonArrangeResult/edit` | `editArrangeResult` | `SVC:178` | course-center | `EditArrangeResultParams` | 写 |
| 批量/单条「删除」 | `POST .../b/lessonArrangeResult/delete` | `deleteArrangeResult` | `SVC:195` | course-center | `ArrangeSelectionPayload`（显式勾选 `numberList` 或条件全选 `selectAllByCondition+queryRequest+excludeNumberList`） | 写 |
| 批量/单条「发布」 | `POST .../b/lessonArrangeResult/publish` | `publishArrangeResult` | `SVC:198` | course-center | `ArrangeSelectionPayload` | 写 |
| 批量/单条「取消发布」 | `POST .../b/lessonArrangeResult/noPublish` | `noPublishArrangeResult` | `SVC:201` | course-center | `ArrangeSelectionPayload` | 写 |
| 「导出」 | `POST .../b/lessonArrangeResult/exportEmail` | `exportArrangeResult` | `SVC:235` | course-center | `ExportArrangeResultParams` | 写 |
| 关联班级编辑 | `POST .../b/lessonArrangeResult/clazzRelationEdit` | `editClazzRelation` | `SVC:238` | course-center | `ClazzRelationEditParams` | 写 |
| 老师时间冲突详情 | `GET .../b/lessonArrangeResult/conflictDetail` | `getTeacherTimeConflictDetail` | `SVC:216` | course-center | `{"arrangeResultNumber":...}` | 读 |

共用的 GPS 基座接口：同 `prism/clazzList`，不重复记。`FeituData` 字典/树接口（`dictionary/all`、`category/tree`、`department/tree`）与 `clazzManageNew` 页面共用同一套，详见该页记录。

## 排查提示

- 顶部「未排班级」计数走 `getUnarrangedNodeList`（`node/search`），**不是**从 `getExceptionNum` 来；`getExceptionNum` 只覆盖缺老师/时间冲突/课节删除三类。两者都是 `useRequest(..., {manual:true})`，需确认页面是否真的触发了 `run`。
- 批量操作（删除/发布/取消发布/导出）统一走 `ArrangeSelectionPayload` 契约：显式勾选传 `numberList`；「全选筛选结果」传 `selectAllByCondition:true` + 当前 `queryRequest`（筛选条件）+ `excludeNumberList`（反选排除），后端 `ArrangeResultSelectionResolver` 统一解析——批量操作结果和预期不符先看前端传的是哪种选择模式。
- 「添加排课」「一对一排课」「班级排课」用的是同一个 `getUnArrangedClazzList`（`/b/teachClazz/search`），按 `arrangeModeTypeList`/`arrangeStatus` 区分场景。

## 青舟接口详情页

未查（需要按 path 搜 course-center 下的 `/b/lessonArrangeResult/*`、`/b/teachClazz/search` 等）。
