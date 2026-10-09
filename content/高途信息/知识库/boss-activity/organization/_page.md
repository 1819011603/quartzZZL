# 组织架构（organization）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 boss-activity master 代码整理；后端对照 staff 仓库 master（逐接口追到 mapper XML）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-activity/organization` |
| 基座 | OES ark → 子应用 app-activity（静态资源 `gtoss.gsxcdn.com/.../projects/boss-activity/`，chunk `organization`） |
| 前端仓库 | boss-activity `http://git.baijia.com/gaotu-fe/boss-activity`（master，本地 `~/IdeaProjects/WebProject/boss-activity`；青舟 serviceCode `gaotu_fe_mi`） |
| 前端路由 | `src/configs/router.config.js:598-601`（懒加载）、`:850` `<Route path="/organization">` → `src/page/organization/index.js` |
| URL 常量 | `src/common/ajaxConfig.js:973-1006`（`ORGANIZATION.*`，`handleEnvIsolation('organization')` 前缀为空） |
| 后端服务 | 网关前缀 `/staff` → 青舟 appId `staff.gaotu100.com`（gapm-appid `staff-gaotu100-com`）；仓库 **staff** `http://git.baijia.com/gaotu/staff`（master，本地 `~/IdeaProjects/JavaProject/staff`；青舟 serviceCode `gaotu_i_org`） |

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

库：**`i_org`**（mapper XML 全部写死 `i_org.` 前缀；数据源 bean `gaotuDataSource`，`staff-web/.../config/DatasourceConfig.java`，连接串 `jdbc.baijiabao.url` 在 Apollo）。删除**全是逻辑删**（`isdel=1`）。
Controller 在 `staff-web/src/main/java/com/gaotu/staff/controller/`：`OrganizationController`（`/organization`）、`AdminController`（`/admin`）、`StaffBcpTaskController`（`/bcpTask/`）、`LabelController`（`/label`）、`StaffController`（无类级前缀）。

### 接口 → 表

| 接口（后端 path） | Controller:行 | 读表 | 写表（操作） | 其它副作用 |
|---|---|---|---|---|
| organization/showTree.do | Organization:97 | orginazation、staff_organization_relation、admin、admin_config_org | — | 已 @Deprecated 仍在用 |
| organization/type.do | Organization:397 | 无（枚举） | — | — |
| admin/getAdminType.do | Admin:32 | admin、admin_config_org | — | — |
| bcpTask/exist、bcpTask/search | StaffBcpTask:111 / :55 | admin、admin_config_org、orginazation、staff_bcp_task ⨝ staff_bcp_task_permission | — | — |
| bcpTask/enums | StaffBcpTask:98 | 无（枚举） | — | — |
| bcpTask/sync | StaffBcpTask:119 | — | staff_bcp_task（UPDATE status、op_account_id） | — |
| list/organization/member.do | Staff:565 | staff ⨝ staff_organization_relation ⨝ orginazation、approval_task、org_staff_label_relation、label、label_group | — | — |
| organization/searchDetailByOrgNumber.do | Organization:183 | orginazation、org_level_dict、city_dict、staff、staff_organization_relation、admin、admin_config_org、org_staff_label_relation、label | — | — |
| search/member.do | Staff:201 | orginazation、staff_organization_relation、staff | — | — |
| delete/member.do | Staff:286 | admin、admin_config_org、orginazation、staff、staff_organization_relation、approval_task | staff_organization_relation（逻辑删）；approval_task（INSERT/UPDATE，走审批时） | Redis 权限缓存、MQ、OperateLogClient |
| account/batch/delete/member.do | Staff:329 | 同上 + batch_operate_task_detail | 开 batchTaskEnable：batch_operate_task / _detail（INSERT→UPDATE）、scene_rist_level_record（INSERT）；否则同单删 | 同上 |
| organization/modifyOrgStatus.do | Organization:116 | orginazation | orginazation（UPDATE 状态/隐藏） | — |
| organization/export.do | Organization:407 | orginazation、staff、staff_organization_relation、org_staff_label_relation、label、label_group | — | 异步，BaiLing 发邮件 |
| organization/showOrgNodeTree.do | Organization:125 | orginazation、staff_organization_relation、admin、admin_config_org | — | — |
| change/member.do | Staff:388 | admin、admin_config_org、orginazation、staff、staff_organization_relation、approval_task | staff_organization_relation（INSERT/upsert + 逻辑删）；approval_task | Redis、MQ、OperateLogClient |
| searchByEmailAndName.do | Staff:653 | orginazation、staff、staff_organization_relation | — | HTTP 查 Medusa/CAS |
| add/member.do | Staff:213 | admin、admin_config_org、orginazation、staff、staff_organization_relation、approval_task、org_staff_label_relation | staff（INSERT）；staff_organization_relation（INSERT/upsert）；approval_task | Redis、MQ、OperateLogClient |
| batchAddStaff.do | Staff:930 | staff_organization_relation | —（只解析选人） | HTTP 查 Medusa/CAS |
| batchImportStaff.do | Staff:941 | admin、admin_config_org、orginazation、staff、staff_organization_relation、org_staff_label_relation | staff_organization_relation（INSERT + 逻辑删）；operate_log（INSERT … ON DUPLICATE KEY UPDATE） | Redis、MQ、BaiLing、OperateLogClient |
| download*Template.do（两个） | Staff:918 / :924 | 无 | — | 返回写死的 OSS 地址 |
| label/listLabel.do | Label:44 | label_group、label、label_config_org、admin、admin_config_org、orginazation | — | — |
| label/listLabelByOrgNumber.do | Label:50 | org_staff_label_relation、label、label_group | — | — |
| label/batchUpsertStaffLabel.do | Label:68 | org_staff_label_relation、staff_organization_relation、label、label_group、label_config_org、orginazation | org_staff_label_relation（INSERT + 逻辑删） | MQ、OperateLogClient |
| label/batchUpsertOrgLabel.do | Label:57 | 同上（不含 staff_organization_relation） | org_staff_label_relation（INSERT + 逻辑删） | MQ、OperateLogClient |
| list/dashLine.do | Staff:554 | staff ⨝ orginazation ⨝ staff_organization_relation | — | — |
| search/dottedLine/leader.do、list/leader.do | Staff:192 / :542 | staff_organization_relation、staff | — | — |
| add/leader.do | Staff:443 | admin、admin_config_org、orginazation、staff、staff_organization_relation、approval_task | staff（INSERT）；staff_organization_relation（INSERT + 逻辑删）；approval_task | Redis、MQ、OperateLogClient |
| delete/leader.do | Staff:495 | 同上 | staff_organization_relation（逻辑删 + INSERT）；approval_task | Redis、MQ、OperateLogClient |
| organization/levelList.do | Organization:193 | orginazation、org_level_dict、city_dict | — | — |
| organization/addNode.do | Organization:153 | orginazation、city_dict、label | orginazation（INSERT）；org_staff_label_relation（INSERT） | MQ 清缓存 |
| organization/changeLevel.do | Organization:304 | orginazation、city_dict、staff、staff_organization_relation、org_staff_label_relation、label | orginazation（UPDATE）；org_staff_label_relation（INSERT + 逻辑删） | MQ、OperateLogClient |
| organization/delNode.do | Organization:289 | orginazation、staff_organization_relation、approval_task、org_staff_label_relation | orginazation（UPDATE）；staff_organization_relation、org_staff_label_relation（逻辑删）；approval_task | MQ |
| organization/exchangeNode.do | Organization:237 | orginazation、staff_organization_relation、admin、admin_config_org、org_staff_label_relation、label | orginazation（UPDATE path/parent）；staff_organization_relation（逻辑删）；org_staff_label_relation（INSERT + 逻辑删） | Redis、MQ、HTTP |

### 表（均在 `i_org` 库）

| 表 | 含义 |
|---|---|
| `orginazation`（原文拼写） | 组织节点：number、parent_number、org_level_code、city、org_path |
| `staff` | 员工：account_id、name、pinyin_name（邮箱前缀）、status、join_date |
| `staff_organization_relation` | 员工 ↔ 组织关系，type 区分成员 / 负责人 / 虚线汇报 |
| `admin` / `admin_config_org` | 管理员（超管/普通）及普通管理员可管的节点 |
| `label` / `label_group` / `label_config_org` | 标签值 / 标签组 / 标签组可用节点 |
| `org_staff_label_relation` | 节点或员工打标关系（config_type 区分） |
| `org_level_dict` / `city_dict` | 组织层级字典 / 城市字典 |
| `approval_task` | 变更审批任务 |
| `staff_bcp_task` / `staff_bcp_task_permission` | 异动待办 / 待办可见范围（post_tag=组织路径前缀） |
| `batch_operate_task` / `batch_operate_task_detail` / `scene_rist_level_record` | 批量操作任务、明细、场景风险等级 |
| `operate_log` | 本地变更日志（before/after） |

库里还有 `organizational_snapshot`、`staff_organization_operate_details`，本页接口不直接用。

注意：
- 表是按代码静态追的；增删成员、负责人、节点这类写路径里，部分表只在走审批或开批量任务开关时才写。
- 很多 `OrginazationDao.select*WithCache` 会顺带读 `label`、`org_staff_label_relation`。
- 写操作普遍伴随 Redis 权限缓存失效、MQ 广播、OperateLogClient 记日志，查"改了不生效"时别只看表。

## 青舟接口详情页（staff.gaotu100.com / release）

后端 path = 前端路径去掉 `/staff` 前缀与 `.do` 后缀。

- [/organization/showTree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37411&appId=staff.gaotu100.com&branchName=release) id=37411
- [/organization/type](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37386&appId=staff.gaotu100.com&branchName=release) id=37386
- [/admin/getAdminType](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37361&appId=staff.gaotu100.com&branchName=release) id=37361
- [/bcpTask/exist](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=942573&appId=staff.gaotu100.com&branchName=release) id=942573
- [/bcpTask/enums](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=942568&appId=staff.gaotu100.com&branchName=release) id=942568
- [/bcpTask/search](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=942566&appId=staff.gaotu100.com&branchName=release) id=942566
- [/bcpTask/sync](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=942570&appId=staff.gaotu100.com&branchName=release) id=942570
- [/list/organization/member](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37538&appId=staff.gaotu100.com&branchName=release) id=37538
- [/organization/searchDetailByOrgNumber](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37408&appId=staff.gaotu100.com&branchName=release) id=37408
- [/search/member](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37493&appId=staff.gaotu100.com&branchName=release) id=37493
- [/delete/member](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37498&appId=staff.gaotu100.com&branchName=release) id=37498
- [/account/batch/delete/member](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37497&appId=staff.gaotu100.com&branchName=release) id=37497
- [/organization/modifyOrgStatus](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37401&appId=staff.gaotu100.com&branchName=release) id=37401
- [/organization/export](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37375&appId=staff.gaotu100.com&branchName=release) id=37375
- [/organization/showOrgNodeTree](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37402&appId=staff.gaotu100.com&branchName=release) id=37402
- [/change/member](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37501&appId=staff.gaotu100.com&branchName=release) id=37501
- [/searchByEmailAndName](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37509&appId=staff.gaotu100.com&branchName=release) id=37509
- [/add/member](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37494&appId=staff.gaotu100.com&branchName=release) id=37494
- [/batchAddStaff](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37530&appId=staff.gaotu100.com&branchName=release) id=37530
- [/label/listLabel](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37365&appId=staff.gaotu100.com&branchName=release) id=37365
- [/label/batchUpsertStaffLabel](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37368&appId=staff.gaotu100.com&branchName=release) id=37368
- [/batchImportStaff](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37488&appId=staff.gaotu100.com&branchName=release) id=37488
- [/label/batchUpsertOrgLabel](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37367&appId=staff.gaotu100.com&branchName=release) id=37367
- [/list/dashLine](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37537&appId=staff.gaotu100.com&branchName=release) id=37537
- [/search/dottedLine/leader](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37531&appId=staff.gaotu100.com&branchName=release) id=37531
- [/delete/leader](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37505&appId=staff.gaotu100.com&branchName=release) id=37505
- [/organization/levelList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37409&appId=staff.gaotu100.com&branchName=release) id=37409
- [/label/listLabelByOrgNumber](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37366&appId=staff.gaotu100.com&branchName=release) id=37366
- [/organization/addNode](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37405&appId=staff.gaotu100.com&branchName=release) id=37405
- [/organization/changeLevel](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37379&appId=staff.gaotu100.com&branchName=release) id=37379
- [/organization/delNode](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37378&appId=staff.gaotu100.com&branchName=release) id=37378
- [/organization/exchangeNode](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37410&appId=staff.gaotu100.com&branchName=release) id=37410
- [/list/leader](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37507&appId=staff.gaotu100.com&branchName=release) id=37507
- [/add/leader](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=37503&appId=staff.gaotu100.com&branchName=release) id=37503
