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

## 青舟接口详情页

- [POST /teachProductSmallClazz/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044921&appId=student-center&branchName=release)
- [POST /teachProductSmallClazz/mainTeacherOptions](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044927&appId=student-center&branchName=release)
- [POST /teachProductSmallClazz/assistantTeacherOptions](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044938&appId=student-center&branchName=release)
