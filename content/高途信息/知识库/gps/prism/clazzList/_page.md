# 班级列表（clazzList）— 页面级

> 2026-10-16 test 环境 chrome-devtools 抓包 + 前端 prism master 代码整理；后端未对照（仅凭抓包）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/prism/clazzList` |
| 导航 | 顶部「教学」→ 左侧「我的班级」 |
| 基座 | GPS 系统 test-os（qiankun）→ 子应用 prism（chunk `p__clazzList__index`） |
| 前端仓库 | prism `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/prism`（master `a228ffa`，本地 `~/IdeaProjects/WebProject/prism`，umi） |
| 前端路由 | `config/routes.ts:4-5` `/clazzList` → `src/pages/clazzList/index.tsx` |
| 后端服务 | 前端前缀 `/bgwApi/student-center/gps/clazz`（`src/services/clazzData.ts`） → gapm-appid `student-center` |

## tab 列表

页面无 tab，单一列表（`FeituData` + `FeituTable`）+ 筛选表单（`QueryFilter`：班级/学员/老师/上课时间/教材版本/科目/年级，展开后还有学年/学季）。

## 页面级接口

`CL/` = `src/pages/clazzList/`，`SVC` = `src/services/clazzData.ts`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 请求体示例 | 读/写 |
|---|---|---|---|---|---|---|
| 进页面 / 查询 / 翻页（`FeituData` 自动管理分页，`useCache=true`） | `POST /bgwApi/student-center/gps/clazz/list` | `getClazzList` | `CL/index.tsx:243`（`SVC:53`） | student-center | `{"pager":{"current":1,"pageSize":50,"pageNum":1},"classTimeRanges":["<startMs>","<endMs>"]}` | 读 |
| 老师下拉展开 | `POST /bgwApi/student-center/gps/clazz/filter/clazz/teacher/list` | `getCurrentTeacherList` | `CL/index.tsx`（`SVC:71`） | student-center | `{}` | 读 |
| 教材版本 / 科目 / 年级 下拉展开（共用一个接口，按请求体数组区分 type） | `POST /bgwApi/student-center/gps/clazz/dicts` | `getSmallClassEnum` | `CL/index.tsx`（`SVC:63`） | student-center | `["clazzTypeBookVersion"]` / `["clazzTypeSubject"]` / `["clazzTypeGrade"]` | 读 |

`SVC` 里还定义了 `getClazzDetail`（`/gps/clazz/detail`）和 `getFilterClazzList`（`/gps/clazz/filter/my/clazz/list`），本页**不调用**。

共用的 GPS 基座接口（各页面都会调，不重复记）：`GET /api/gpsBase/config?key=systemList`、`GET /api/gpsBase/config?key=userMenuList`、`POST /gateway-api/ac/getFlatAuth`。

## 关键请求头

- `b_client`：来自 qiankun 基座注入的 `qiankunProps.b_client`（`CL/index.tsx:81` `getQiankunProps()`），每个请求都带，**不是硬编码值**；直调复现时要用对应页面当时拿到的真实值，不同基座子应用取值可能不同。

## 排查提示

- 列表默认按「上课时间」本周范围筛选（`classTimeRanges`），班级总数对不上时先看筛选条件是否被重置。
- `FeituData` 带 `useCache=true`，刷新页面不一定重新请求，排查数据滞后先看是不是缓存命中。
- 「批量添加活动」按钮调的是 `@gaotu/cms-ui` 里的 `BatchAddActivityDrawer` 组件，接口未在本页面代码里直接出现（组件内部自己发），本次未展开抓。

## 青舟接口详情页

未查（需要按 path 搜 `student-center` 下的 `/gps/clazz/list`、`/gps/clazz/dicts`、`/gps/clazz/filter/clazz/teacher/list`）。
