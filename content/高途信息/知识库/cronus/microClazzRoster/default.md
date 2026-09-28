# 小班课花名册 / 花名册（microClazzRoster · tabKey=default）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/microClazzRoster?tabKey=default` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/microClazzRoster/index.jsx` |
| tab 组件 | `src/pages/microClazzRoster/DefaultRoster/` |
| 主 service 文件 | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级说明见 [_page.md](./_page.md)；续班服务 tab 见 [continuationService.md](./continuationService.md)。

## 接口清单

### 1. 列表 / 编辑

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/筛选/翻页/排序 | `getMicroClazzRosterList` | `/component/student-center/smallClazz/clazzStudentList` | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js:5` | student-center | `/smallClazz/clazzStudentList` | 小班花名册列表查询 [2044941] | **主列表数据** |
| 行内编辑保存 | `updateStudentInfo` | `/component/student-center/studentClazz/edit` | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js:13` | student-center | `/studentClazz/edit` | [POST]/edit [30662] | 保存单元格修改（场景 `smallClazzRoster`） |
| 批量改颜色/分层 | `batchEditStudentInfo` | `/component/student-center/studentClazz/batchEdit` | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js:54` | student-center | `/studentClazz/batchEdit` | [POST]/batchEdit [2863102] | `BatchColorEdit` 批量修改学员颜色/分层 |

### 2. 筛选 / 悬浮

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 主讲/班主任下拉搜索 | `getTeacherList` | `/bgwApi/student-center/smallClazz/filter/clazz/teacher/list` | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js:21` | student-center | `/smallClazz/filter/clazz/teacher/list` | [POST]/clazz/teacher/list [2044923] | `EnhancedGlobalSearch` 老师选项 |
| 班级筛选下拉 | `ClazzAndPeriod`（内联 `api.clazz`） | `/component/student-center/smallClazz/filter/clazz/list` | `src/pages/microClazzRoster/DefaultRoster/components/EnhancedGlobalSearch/index.jsx:254` | student-center | `/smallClazz/filter/clazz/list` | [POST]/clazz/list [2044937] | `@coeus/business` 班级选择器数据源 |
| hover 最近听课 | `getRecentListenSituation` | `/component/student-center/smallClazz/lessonSituation` | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js:37` | student-center | `/smallClazz/lessonSituation` | 获取学员看课进度条 [2366331] | `RecentListenTime` 悬浮进度 |

### 3. 表格 schema

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | `getSchema`（`@coeus/render`） | coeus 低代码 schema | `src/pages/microClazzRoster/DefaultRoster/hooks/useTableSchema.js:14` | coeus/render | — | — | 拉表格列 / 筛选 schema（`identification=smallClazzRoster`） |

> 共享组件（`ReportWidget` / `ReachReport` / `SendCoins` / `SettingTags` / `ModifyWechatNote` / `StudentCertificateReport` / `DownLoadCorrections` / `WrongBook` / `Attendance` 等）另有接口，被多页面复用，待单独归档。

## 青舟接口详情页

- [POST /smallClazz/clazzStudentList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044941&appId=student-center&branchName=release)
- [POST /studentClazz/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30662&appId=student-center&branchName=release)
- [POST /studentClazz/batchEdit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2863102&appId=student-center&branchName=release)
- [POST /smallClazz/filter/clazz/teacher/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044923&appId=student-center&branchName=release)
- [POST /smallClazz/filter/clazz/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2044937&appId=student-center&branchName=release)
- [POST /smallClazz/lessonSituation](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2366331&appId=student-center&branchName=release)
