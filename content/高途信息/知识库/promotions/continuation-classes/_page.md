# 续班计划管理（continuation-classes）— 页面级

> 2026-10-09 用 chrome-devtools 带登录态在 test 环境点击抓包整理；后端代码对照 product-server。前端仓库在 GitLab 未定位到（Chrome 与代理均未登录 GitLab），「前端代码位置」暂缺；接口均为浏览器实际抓包。

## 路由链路

| 项 | 值 |
|---|---|
| 列表页 URL | `https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/list` |
| 详情页 URL | `https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/detail?n=<续班计划number>` |
| 菜单 | OES（ark 基座）→ 续班管理 → 续班计划管理 |
| 基座 | ark → 子应用 app-promotions（静态资源 `gtoss.gsxcdn.com/.../projects/promotions/`） |
| 后端服务 | 网关前缀 `/product-b` → 青舟 appId `product-b`（代码仓库 **product-server**，模块 `product-server-b`） |
| 主库 | `gaotu` 库（test 集群见各 tab 文件） |

## tab 列表

| tab | 文件 | 说明 |
|---|---|---|
| 列表页 | 本文件 | 计划列表筛选 |
| 详情页 / 续班关系 | 本文件 | 前置课程 ↔ 后置课程 |
| 详情页 / 续班学员 | 未收录 | — |
| 详情页 / 续班流程 | [renewalProcess.md](renewalProcess.md) | 续班问卷 / 预报名 / 续班正式报名，**问卷绑定在这里** |

## 页面级接口

| 触发 | 前端调用路径 | 后端服务 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|
| 列表页 进页面/查询/翻页 | `POST /product-b/b/renewMaster/list` | product-b | `/b/renewMaster/list` | 续班计划列表 | — |
| 列表页 进页面 | `GET /course-center/b/common/department/tree` | course-center | `/b/common/department/tree` | 部门树 | 所属部门筛选 |
| 列表页 进页面 | `GET /course-center/b/common/dictionary/all` | course-center | `/b/common/dictionary/all` | 字典 | 学年/学期/年级/学科 |
| 详情页 进页面 | `POST /product-b/b/renewMaster/detail` | product-b | `/b/renewMaster/detail` | 续班计划详情 | 入参 `{"number": 计划number}`；回年级/学科/学期/部门/管理员 |
| 详情页 续班关系 | `POST /product-b/b/renewMaster/productRelationList` | product-b | `/b/renewMaster/productRelationList` | 续班关系列表 | 前置产品 ↔ 后置产品 |
| 详情页 续班关系 | `POST /product-b/b/renewMaster/listCoursesByPreCourseNumber` | product-b | `/b/renewMaster/listCoursesByPreCourseNumber` | 按前置课程查后置课程 | 入参 `{"preCourseNumber": ...}` |

## 关键表

| 表 | 含义 |
|---|---|
| `gaotu.renew_master` | 续班计划（number = 页面上的「续班计划ID」） |
| `gaotu.renew_master_course_relation` | 计划下的前置课程；`questionnaire_number` 列 = 该前置课程匹配到的问卷 |

## 排查提示

- 计划看不到课程 / 续班关系不对 → `productRelationList`、`listCoursesByPreCourseNumber`；另见工单 `续班与业绩/续班关系配置/`
- 问卷相关 → [renewalProcess.md](renewalProcess.md)

## 青舟接口详情页（product-b / release）

- [POST /b/renewMaster/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734217&appId=product-b&branchName=release) id=2734217
- [POST /b/renewMaster/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734125&appId=product-b&branchName=release) id=2734125
- [POST /b/renewMaster/listCoursesByPreCourseNumber](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734280&appId=product-b&branchName=release) id=2734280
- [POST /b/renewMaster/productRelationList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734126&appId=product-b&branchName=release) id=2734126
