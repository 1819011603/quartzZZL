# 辅导班管理（tutoringClassManage）— 页面级

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-fuwu.baijia.com/crm/microFairy/tutoringClassManage` |
| 基座 | epic（base `/crm`）→ qiankun 子应用 fairy（`/crm/microFairy`） |
| epic 路由 | `/crm/microFairy/tutoringClassManage`（`microApp: fairy`，`name: 辅导班管理`） |
| fairy 路由 | `boss-counselor/config/routes.ts`：`/tutoringClassManage` → `./TutoringClassManage`（`src/pages/TutoringClassManage/index.jsx`） |
| 前端仓库 | boss-counselor `http://git.baijia.com/gaotu-fe/boss-counselor`（分支 master） |

## tab 列表

无 tab，单页表格。

## 页面级接口

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/查询/翻页/排序 | `getClazzList`（`@/services/tutoringClassManage`） | `/bgwApi/distribution-management/subclazz/management/listSubclazzAggInfo` | `src/pages/TutoringClassManage/index.jsx:77` | clazz-distribution-management.gaotu100.com | `/subclazz/management/listSubclazzAggInfo` | 辅导班管理-辅导班列表 [31665] | 辅导班列表主接口，返回 `subclazzAggInfos` + pager |
| 进页面 | `getNoteBookGray`（`@/services/tutoringClassManage`） | `/component/student-center/toolBox/config/gray` | `src/pages/TutoringClassManage/index.jsx:537` | student-center | `/toolBox/config/gray` | [GET]/config/gray [64558] | 通讯录灰度配置，决定是否走新版通讯录（`addressBook`） |
| 进页面 | `getSubordinatesGray`（`@/services/tutoringClassManage`） | `/bgwApi/component/student-center/studentClazz/subordinates/gray` | `src/pages/TutoringClassManage/index.jsx:548` | student-center | `/studentClazz/subordinates/gray` | 灰度接口 [3683444] | 决定辅导老师下拉是否走新树形下拉（`ifGray`） |
| 辅导老师下拉搜索（`useTreeSelect=false` 分支） | `getTeacher`（`@/services/tutoringClassManage`） | `/bgwApi/component/student-center/studentClazz/pageAssistantTeacher` | `src/pages/TutoringClassManage/components/SearchForm/index.jsx:115` | student-center | `/studentClazz/pageAssistantTeacher` | [POST]/pageAssistantTeacher [30677] | 辅导老师下拉候选项 |
| 打开抽屉工具详情 | `getMySubclazzDetail`（`@/services/subclazz`） | `/fairy/subclazz/detail` | `src/pages/TutoringClassManage/components/DrawerToolDetail/index.jsx:29` | fairy.gaotu100.com | `/subclazz/detail` | 辅导班详情 [35398] | 取辅导班详情用于在班人数（`currentStudentCount`） |

> 共享组件接口另见公共组件文档：`AccountNameFilter`（`@/components/AccountNameFilter`，走树形下拉时调 `subordinates/listTreeChild`、`subordinates/searchTreeChild`）、`SearchSelect`、`NoticeList`、`SwitchClazzDetail`、`TheAddressBook`、`OutDetail`、`ClazzGroupInfo`、`AliIcon` 等；`DrawerToolDetail` 内 `TutoringClassManageContent` 引用的 `src/pages/Toolbox/*` 属 Toolbox 页面自有代码，见对应页面文档。
