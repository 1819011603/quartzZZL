# 班级管理（clazzManageNew/list）— 页面级

> 2026-10-16 test 环境 chrome-devtools 抓包 + 前端 gps-operation master 代码整理；后端未对照（仅凭前端代码推断 path）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/app-operation/clazzManageNew/list` |
| 导航 | 顶部「运营」→ 左侧「运营单元管理」→「班级管理」（同级还有「组管理」） |
| 基座 | GPS（test-os.baijia.com）qiankun 基座 → 子应用 app-operation |
| 前端仓库 | gps-operation `http://git.baijia.com/esfe/gps-operation`（master `ab924d5`，本地 `~/IdeaProjects/WebProject/gps-operation`） |
| 前端路由 | `src/routes/index.tsx:15` `/clazzManageNew/list` → `src/pages/ClazzManageNew/list/index.tsx`（同级还有 `/view`、`/edit`、`/add`、`/addBatch`，本次只抓了 list） |
| 后端服务 | 前端前缀 `/course-center`、`/bgwApi/course-center`（无统一 `baseApi` 常量，`services/teachClazz.ts`、`services/clazzManageNew.ts` 等各自定义） → gapm-appid course-center（未在响应头确认，按路径推断） |

## tab 列表

页面无 tab，单一列表（`FeituData` + `FeituTable`）+ 筛选表单（`QueryFilter`，班级搜索/产品单元/主讲搜索，展开后还有上课时间/子产品/班级类型/交付形式/所属校区/科目/年级/学年/学习状态等，由 `@/components/SearchComponents` 下多个独立组件拼成）。

## 页面级接口

`CMN/` = `src/pages/ClazzManageNew/list/`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 请求体 | 读/写 |
|---|---|---|---|---|---|---|
| 进页面 / 查询 / 翻页（`FeituData.onBefore` 固定注入 `arrangeModeTypeList:[4]`） | `POST /course-center/b/teachClazz/search` | — | `CMN/index.tsx:341`（`onBefore` 注入见 `:323`） | course-center | `{"pager":{...},"arrangeModeTypeList":[4],...筛选字段}` | 读 |
| 进页面（校区筛选项） | `POST /course-center/b/campus/search` | `searchCampus`（命名推断） | `src/services/clazzOmo.ts:14` | course-center | — | 读 |
| 进页面（设置列-全部可选列 / 用户配置） | `POST /course-center/b/columns/getAllConfig`、`getUserConfig` | — | `src/services/userColumnConfig.ts:89,93` | course-center | — | 读 |
| 进页面（字典/品类树/部门树/可配置字典） | `GET /bgwApi/course-center/b/common/dictionary/all`、`/b/common/category/tree`、`/b/common/department/tree`、`/b/common/dictionary/allConfigurable` | `getDictionary`、`getCategoryTree`、`getDepartmentTree`、`getDefaultCourseConfig` | `src/services/clazzManageNew.ts:14-31` | course-center | — | 读 |
| 进页面（学部筛选，经 `useAllDepartments` hook） | `POST /bgwApi/course-center/b/teachProduct/teachDepartment/listAll` | `fetchTeachDepartments` | `src/services/clazzManageNew.ts:81`，调用方 `src/hooks/useAllDepartments.ts:17` | course-center | `{"statusList":[1]}` | 读 |
| 「批量导出」菜单（邮件） | `POST /bgwApi/course-center/b/teachClazz/export/email`、`/b/teachClazz/export/lesson/email` | `batchExportClazzList`、`batchExportClazzAndLessonList` | `src/services/clazzManageNew.ts:60,68`，调用方 `CMN/useBatchExport.ts` | course-center | `BatchExportClazzParams` | 写 |

`src/services/arrangeResult.ts:208` 里也定义了同一个 `/b/teachClazz/search`（跨页面复用，`arrangeResult.ts:333,358` 注释说明「取数链路与 `/b/teachClazz/search` 同源」），说明班级搜索逻辑在后端是共用的。

共用的 GPS 基座接口：同 `prism/clazzList`，不重复记。

## 排查提示

- `arrangeModeTypeList:[4]` 是前端固定写死注入的（不在筛选表单里），列表范围跟筛选表单看到的字段对不上先查这个隐藏参数。
- `FeituData` 的 `onBefore` 还会做：筛选条件变化时重置跨页选择（`resetSelection`），翻页不重置——跨页批量操作选中状态异常先看这段逻辑。
- 列表字典/树接口（`dictionary/all`、`category/tree`、`department/tree`）进页面一次性拉全，筛选项为空先查这几个接口返回而不是前端代码。
- 本次未点开「新建班级」「批量操作」弹窗内的保存/编辑动作，相关写接口（除导出）未抓到，需要另外点开 `/clazzManageNew/add`、`/edit` 对照。

## 青舟接口详情页

未查（需要按 path 搜 course-center 下的 `/b/teachClazz/search`、`/b/campus/search` 等）。
