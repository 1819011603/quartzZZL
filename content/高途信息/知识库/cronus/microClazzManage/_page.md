# 小班课管理（microClazzManage）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/cronus/microClazzManage` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 cronus（`/crm/micro-cronus`） |
| epic 路由 | `epic/src/routes.ts`：`/cronus/microClazzManage`（`microApp: cronus`，`name: 小班课管理`） |
| cronus 路由 | `cronus/config/routes.js`：`/microClazzManage` → `src/pages/microClazzManage/index.tsx` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |

## 接口清单

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/筛选/翻页 | `FeituData`（`fetch` 属性） | `/bgwApi/student-center/teachProductSmallClazz/list` | `src/pages/microClazzManage/index.tsx:106` | student-center | `/teachProductSmallClazz/list` | [POST]/list [2044921] | **主列表数据**（`dataPath=list`） |
| 主讲下拉搜索 | `queryMainTeacher` | `/bgwApi/student-center/teachProductSmallClazz/mainTeacherOptions` | `src/pages/microClazzManage/services/index.ts:4` | student-center | `/teachProductSmallClazz/mainTeacherOptions` | [POST]/mainTeacherOptions [2044927] | 主讲老师模糊搜索选项 |
| 班主任下拉搜索 | `queryAssistantTeacher` | `/bgwApi/student-center/teachProductSmallClazz/assistantTeacherOptions` | `src/pages/microClazzManage/services/index.ts:10` | student-center | `/teachProductSmallClazz/assistantTeacherOptions` | [POST]/assistantTeacherOptions [2044938] | 班主任模糊搜索选项 |

> 共享组件（`EllipsisCellRender` / `feitud` 表格列配置等）另有接口，被多页面复用，待单独归档。

## 关键点 / 注意点（直调复现）

**关键点**

- 主列表 `POST /teachProductSmallClazz/list`（后端 `SmallClazzSearchService.searchPolymerizeList(request, scene=107, 登录 accountId)`），**不走** GAIA 花名册筛选，无 `identification`。
- 常用 `filter`：`assistantAccountIdList`（**二讲 accountId**，找某二讲带的班）、`mainTeacherNumberList`（主讲工号）、`clazzTeachingStatusList`（班级教学状态）。
- 页面请求头 `b_client: EES`。

**注意点**

- 该接口**按登录人权限过滤**（`scene=107`）→ 复现前先 `cosplay_login` 成该二讲（如 shizejia=200986），否则 0 条。
- 该接口**不触发** `SmallClazzUserPermissionFilterService` 的 staff 调用 → **不带 `b_client` 也不报 `code:42`**（实测 prod 空 body 返回 `code:0`）；与花名册/续班服务页不同，别混。
- 环境：线上 `fuwu.baijia.com` + `traffic-env: prod`。

## 青舟接口详情页

- [POST /teachProductSmallClazz/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044921&appId=student-center&branchName=release)
- [POST /teachProductSmallClazz/mainTeacherOptions](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044927&appId=student-center&branchName=release)
- [POST /teachProductSmallClazz/assistantTeacherOptions](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044938&appId=student-center&branchName=release)
