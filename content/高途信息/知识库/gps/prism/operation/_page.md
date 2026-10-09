# 运营管理 · 请假 / 调课 / 调班（operation）— 页面级概览

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 prism master 代码整理；后端对照 course-scene-lifecycle（master `d3f0af6`）、course-center（master `4ce8eda`）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/prism/operation/{leave,reschedule,transfer}` |
| 基座 | GPS 系统 test-os（qiankun）→ 子应用 prism |
| 前端仓库 | prism `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/prism`（master `148a757`，本地 `~/IdeaProjects/WebProject/prism`，umi） |
| 前端路由 | `config/routes.ts:48-73`，组件都在 `src/pages/operation/operationsManagement/<page>/index.tsx`（同目录还有 makeUp/trial/teacherChange/bookLesson/exception，本次未整理） |
| 后端服务 | 网关前缀 `/course-scene` 被剥掉 → 青舟 appId `course-scene-lifecycle`，后端真实路径 `/b/support/form/...`；列配置/字典走 `/course-center/b` → `course-center` |

## 三页对照

| 页面 | 文件 | 列表接口 | 服务单类型 | 详情接口 |
|---|---|---|---|---|
| 请假管理 | [leave.md](leave.md) | `/course-scene/b/support/form/leave/searchAll` | `LEAVE` | 通用 `/b/support/form/detail` |
| 调课节管理 | [reschedule.md](reschedule.md) | `/course-scene/b/support/form/transfer/lesson/search/all` | `TRANSFER_LESSON` | 通用 `/b/support/form/detail` |
| 调班管理 | [transfer.md](transfer.md) | `/course-scene/b/support/form/transfer/class/search/all` | `TRANSFER_CLASS` | 专用 `/b/support/form/transfer/class/detail` |

注意「调课节管理」（reschedule 路由）对应的是**调课节**（transfer/lesson），不是后端的 `reschedule`（补课）。

## 共用结构

三页是同一个模板，只读、无写按钮：

- `FeituData` + `QueryFilter`（学员信息 `userKey` / 单据ID `supportFormNumber` / 状态 `statusList`）+ `FeituTable`
- 列配置：`src/hooks/useEditColumnsProps.ts` → course-center `/b/columns/*`（`getAllConfig`/`getUserConfig` 进页面调，`add/set/delete/changeDefaultUserConfig` 在「自定义列」弹层里调），各页 key 见 `src/const/colums.ts:12-17`
- 原因枚举：`useReasonFromDictionary(type)` → `useDictionary`（`src/hooks/useDictionary.ts:59`）→ `GET /course-center/b/common/dictionary/all`（5 分钟缓存）
- 「查看详情」抽屉：`src/pages/checkDetail/index.tsx`，详情 `useRequest(fetchDetailFn ?? getServiceOrderDetail)`（`:63`）+ 操作记录 `FeituData fetch="/course-scene/b/support/form/operation/log"`（`:333`）
- 手机号组件 `src/components/phoneDesensitization/index.tsx:126` 复制时调 `POST /student-center/userSecret/getBaseInfo`（student-center [30733]）

## 共用后端链路

`*AppService#searchAll/listAll` → `BasicSupportFormAppService#buildCondition:707`（`userKey` 先按手机号调用户中心 `StandardUserServiceFeignClientProxy#querySingleInfo` 换 userId，同时作 ES 全文检索）→ `WideSupportFormRepository#findTableByCondition` 查 ES **`support_form_search`**（Apollo `wide.supportForm.es.indexName`，`WideSupportFormDao.java:73`）只拿单号 → 回 MySQL `course_scene_lifecycle.support_form` + 子表补全 → Feign 补课节/班级/老师/用户。

## 排查提示

- 列表查不到但 DB 有单：列表先查 ES `support_form_search`，宽表靠 MQ 同步（`wide.supportForm.generalSyncTriggerTopic` 等），先看 ES 是否落文档
- 按手机号搜不到：`userKey` 会先调用户中心按手机号换 userId，换不到只剩全文匹配
- 原因列显示码值：course-center `dictionary/all` 缓存或配置缺失
- 案例库暂无服务单相关条目
