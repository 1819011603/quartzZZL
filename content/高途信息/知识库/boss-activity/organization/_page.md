# 组织架构（organization）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 boss-activity master 代码整理。后端 staff 服务本地无仓库，表未收录。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-activity/organization` |
| 基座 | OES ark → 子应用 app-activity（静态资源 `gtoss.gsxcdn.com/.../projects/boss-activity/`，chunk `organization`） |
| 前端仓库 | boss-activity `http://git.baijia.com/gaotu-fe/boss-activity`（master，本地 `~/IdeaProjects/WebProject/boss-activity`；青舟 serviceCode `gaotu_fe_mi`） |
| 前端路由 | `src/configs/router.config.js:598-601`（懒加载）、`:850` `<Route path="/organization">` → `src/page/organization/index.js` |
| URL 常量 | `src/common/ajaxConfig.js:973-1006`（`ORGANIZATION.*`，`handleEnvIsolation('organization')` 前缀为空） |
| 后端服务 | 网关前缀 `/staff` → 青舟 appId `staff.gaotu100.com`（gapm-appid `staff-gaotu100-com`）；本地无仓库 |

## tab 列表

无 tab：左侧组织树 + 右侧团队信息/成员列表 + 顶部按钮弹窗。

## 页面级接口

下表「代码位置」括号里是 `ajaxConfig.js` 行号；不带 `src/` 的路径相对 `src/page/organization/`。

### 进页面

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|
| 进页面（Layout） | `POST /course-setting/b/base/commonDictionary` | `getCommonDictionary` | `src/Layouts/index.js:89`（54） | 公共字典（course-setting） | 读 |
| 进页面 | `POST /staff/organization/type.do` | `getRoles` | `index.js:131`（994） | 组织类型字典 [37386] | 读 |
| 进页面 | `GET /staff/admin/getAdminType.do` | `getRoles` | `index.js:139`（996） | 当前用户管理员类型 [37361] | 读 |
| 进页面（无权限判断 + 左侧树根，共 2 次） | `POST /staff/organization/showTree.do` | `useEffect` / `handleTreeData` | `index.js:575`、`OrganizationTree/index.js:110`（984） | 组织树 [37411] | 读 |
| 展开树节点 / 增删改节点后刷新 | 同上 | `onLoadData` 等 | `OrganizationTree/index.js:145` 等 | 组织树 [37411] | 读 |
| 进页面（异动待办角标） | `GET /staff/bcpTask/exist` | `getExist` | `TopFunc/components/AbnormalTodo/index.js:14` | 是否有异动待办 [942573] | 读 |
| 进页面 | `GET /staff/bcpTask/enums` | `getEnums` | `AbnormalTodo/index.js:19` | 异动待办枚举 [942568] | 读 |

### 树节点 / 成员

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 读/写 |
|---|---|---|---|---|
| 点树节点 / 切 tab / 翻页 | `POST /staff/list/organization/member.do` | `handleDataList` | `index.js:160`（981） | 读 |
| 点树节点 | `POST /staff/organization/searchDetailByOrgNumber.do` | `handleDataInfo` | `TeamInformation/index.js:80`（986） | 读 |
| 成员搜索框 | `POST /staff/search/member.do` | `handleInputSearch` | `TeamTableSearch/index.js:34`（982） | 读 |
| 删除成员 / 批量删除 | `POST /staff/delete/member.do`、`/staff/account/batch/delete/member.do` | `handleDeleteSingleConfirmOK` / `handleDeleteBatchConfirmOK` | `TeamInformation/index.js:173`、`:196`（978 / 977） | 写 |
| 节点显示/隐藏/恢复 | `POST /staff/organization/modifyOrgStatus.do` | `handleModifyOrgStatus` | `TeamInformation/index.js:219`（1006） | 写 |
| 节点「导出」（发邮件） | `GET /staff/organization/export.do` | `handleExport` | `TeamDetail/index.js:196`（995） | 读 |
| 移动人员：选目标节点 / 确定 | `POST /staff/organization/showOrgNodeTree.do` → `/staff/change/member.do` | `handleTreeData` / `handleConfirmOK` | `SelectTargetNode/index.js:36`、`MoveEmployees/index.js:45`（1003 / 975） | 读 → 写 |
| 添加兼岗：搜人 / 确定 | `POST /staff/searchByEmailAndName.do` → `/staff/add/member.do` | `handleInputSearch` / `handleOk` | `AddPerson/index.js:72`、`AddMembers/index.js:32`（991 / 974） | 读 → 写 |
| 添加兼岗：批量模板 / 上传 | `GET /staff/downloadBatchAddStaffTemplate.do`、`POST /staff/batchAddStaff.do` | 下载 / antd Upload | `UploadCustomModal/index.js:45`、`:160`（1000 / 999） | 读 / 写 |
| 改员工标签：列表 / 保存 | `GET /staff/label/listLabel.do` → `POST /staff/label/batchUpsertStaffLabel.do` | `handleLabelData` / `handleOk` | `ChangePersonalLabel/index.js:106`、`:88`（1004 / 1002） | 读 → 写 |

### 顶部按钮 / 节点操作

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 读/写 |
|---|---|---|---|---|
| 「异动待办」抽屉 列表 | `POST /staff/bcpTask/search` | `getTableData` | `TopFunc/components/SearchTable/index.js:18` | 读 |
| 「异动待办」同步 | `POST /staff/bcpTask/sync` | `bcpTaskSync` | `AbnormalStaffList.js:29`、`AbnormalNodeList.js:29` | 写 |
| 「批量调整人员」模板 / 上传 | `GET /staff/downloadBathUploadStaffTemplate.do`、`POST /staff/batchImportStaff.do` | 下载 / antd Upload | `UploadCustomModal/index.js:45`、`:160`（`TopFunc/index.js:116-117`） | 读 / 写 |
| 「批量编辑节点标签」选节点 / 确定 | `POST /staff/organization/showOrgNodeTree.do` → `/staff/label/batchUpsertOrgLabel.do` | `handleTreeData` / `handleOk` | `SelectTargetNode/index.js:36`、`ChangeNodeLabel/index.js:79`（1003 / 1001） | 读 → 写 |
| 「虚线汇报总表」列表 / 搜负责人 / 删除 | `POST /staff/list/dashLine.do`、`/staff/search/dottedLine/leader.do`、`/staff/delete/leader.do` | `handleDataList` / `handleInputSearch` / `handleDelete` | `DottedReportAll/index.js:38`、`:155`、`:62`（979 / 983 / 976） | 读 / 读 / 写 |
| 「添加」子/平级节点、编辑节点：层级 / 标签 | `POST /staff/organization/levelList.do`、`GET /staff/label/listLabel.do`、`GET /staff/label/listLabelByOrgNumber.do` | `handleLevelData` / `handleLabelData` / `handleselectedLabelData` | `index.js:326`、`:340`、`:354`（992 / 1004 / 1005） | 读 |
| 「添加」确定 / 编辑节点确定 | `POST /staff/organization/addNode.do`、`/staff/organization/changeLevel.do` | `handleAddNode` / `handleEditNode` | `ChangeTreeNode/index.js:60`、`:99`（988 / 990） | 写 |
| 「删除」节点 | `POST /staff/organization/delNode.do` | `handleConfirmOK` | `index.js:258`（989） | 写 |
| 「变更上级」 | `POST /staff/organization/exchangeNode.do` | `handleOk` | `ChangeLeader/index.js:82`（987） | 写 |
| 「虚线汇报」/ 实线负责人弹窗 | `POST /staff/list/leader.do`、`/staff/searchByEmailAndName.do`、`/staff/add/leader.do`、`/staff/delete/leader.do` | `handleDataList` / `handleInputSearch` / `handleAdd` / `handleDeleteRequest` | `ReportInfo/index.js:41`、`:133`、`:166`、`:59`（980 / 991 / 973 / 976） | 读 / 读 / 写 / 写 |

> `ExportInfo`（`/staff/organization/exportCheck.do`）未被引用，是死代码。两处 antd Upload 的 method 按 antd 默认记为 POST，未实测。

## 关键表

后端 staff 服务（`staff.gaotu100.com`）本地没有仓库，表未收录。本地只有调用方：`reach-service/.../StaffFeignClient.java`、`fairy/.../OrganizationRemoteService.java`。

## 青舟接口详情页（staff.gaotu100.com / release）

- [POST /organization/showTree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37411&appId=staff.gaotu100.com&branchName=release) id=37411
- [POST /organization/type](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37386&appId=staff.gaotu100.com&branchName=release) id=37386
- [GET /admin/getAdminType](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37361&appId=staff.gaotu100.com&branchName=release) id=37361
- [GET /bcpTask/exist](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=942573&appId=staff.gaotu100.com&branchName=release) id=942573
- [GET /bcpTask/enums](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=942568&appId=staff.gaotu100.com&branchName=release) id=942568
