# 续班计划详情 / 续班学员（renewableStudent）

> 2026-11-09 整理，前端代码对照 gaotu-fe-promotions master（`src/pages/continuationClasses/detail/RenewableStudent/`），后端对照 product-server。

## 定位

| 项 | 值 |
|---|---|
| tab URL | 详情页 `continuation-classes/detail?n=<计划number>` → 「续班学员」tab |
| 前端组件 | `src/pages/continuationClasses/detail/RenewableStudent/`：班级列表 `index.js`；「管理可续学员」抽屉 `RenewalManage/`；「续班配置」抽屉 `TemplateSetting/`；批量配置按钮 `BatchSettingRenewal/` |
| 后端主服务 | product-b（仓库 product-server，模块 product-server-b，`RenewalManageController` `@RequestMapping("/b/renewal/manage")`） |
| 业务代码 | `product-server-domain/.../service/renewal/questionnaire/RenewalStudentService.java` |
| 关键表 | 页面读 `gaotu_stat.performance_regular_can_renewal_sign_x`（可续标记）；`gaotu_stat.can_renewal_config`（灰名单配置）；`gaotu_stat.performance_regular_can_renewal_config`（可续配置） |

tab 结构：上方是「在读班级列表」（每行操作：续班配置 / 管理可续学员）；「管理可续学员」抽屉里才是学员级列表（可切换可续状态）。

## 接口清单

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|---|---|
| 进 tab / 班级列表 | `POST /product-b/b/renewal/manage/clazz/list` | ProTable `fetch` | `RenewableStudent/index.js:240` | `/b/renewal/manage/clazz/list` | 班级列表 | 入参 `{renewalNumber,...}`；回 `clazzRenewalVOList` |
| 打开「管理可续学员」抽屉 | `POST /product-b/b/renewal/manage/clazzDetail` | `getRenewalManageClazzDetail` | `RenewalManage/index.js:28（src/services/continuationClasses.js:151）` | `/b/renewal/manage/clazzDetail` | 班级详情 | 入参 `{clazzNumber}` |
| 管理可续学员 学员列表 | `POST /product-b/b/renewal/manage/student/list` | ProTable `fetch` | `RenewalManage/index.js:274` | `/b/renewal/manage/student/list` | 可续学员列表 | 入参 `{clazzNumber, studentName, studentNumber, bizSubClazzNumber, subClazzTeacherNumber, canRenewalStatus}`；回 `studentRenewalList` |
| 切换可续/不可续 | `POST /product-b/b/renewal/manage/edit` | `renewalManageEdit` | `RenewalManage/index.js:38（services/continuationClasses.js:95）` | `/b/renewal/manage/edit` | 设置可续状态 | 入参 `{studentNumber, subClazzNumber, canRenewalStatus(1可续/0不可续), msgCode, msg}`，写操作 |
| 不可续原因下拉 | `POST /product-b/b/renewal/manage/renewalMsgList` | `getRenewalReasons` | `RenewalManage/index.js:106（services/continuationClasses.js:157）` | `/b/renewal/manage/renewalMsgList` | 不可续原因字典 | 设置不可续时选原因 |
| 批量配置 下载模板 | `GET /product-b/b/renewal/manage/renewalConfigType/downloadTemplate` | `downloadTemplate` | `TemplateSetting/index.js:32（services/continuationClasses.js:14）` | `/b/renewal/manage/renewalConfigType/downloadTemplate` | 下载模板 | — |
| 批量配置 上传 | `POST /product-b/b/renewal/manage/batchUploadRenewalConfigType` | `batchUploadRenewalConfigType` | `TemplateSetting/index.js:115（services/continuationClasses.js:19）` | `/b/renewal/manage/batchUploadRenewalConfigType` | 批量上传处理 | 写操作 |

## 「管理可续学员」是否展示不可续状态学员

**会展示，但只包含「续班配置灰名单(17)」这一类不可续**（即在续班配置/本页人工把学员设为不可续的）。

`studentList`（`RenewalStudentService#studentList`）按可续标记表 `performance_regular_can_renewal_sign_x.can_renewal_status` 过滤：

- 不带 `canRenewalStatus`（默认）：`CAN_RENEWAL_STATUS_CONFIG = [1(可续-未续), 2(可续-已续), 8(可续-后置退款), 17(不可续-续班配置灰名单)]`。
- 筛「可续」(`canRenewalStatus=1`)：`[1, 2]`。
- 筛「不可续」(`canRenewalStatus=0`)：`[17]`。

行状态：`canRenewalStatus = (sign 状态 == 17) ? 0(不可续) : 1(可续)`；前端 `renewalConfigType`（`RenewalManage/config.js`）：`-1 可续 / 0 不可续 / 3 动态不可续`，其中 `3` 取自 `can_renewal_config.type=3`。

**不在该列表展示**：其它系统判定型不可续码（3 非续班/4 无续班关系/5 已退款/6 过可续时间/7 调课可续修正/9~16 老学员等）—— 该页只按 `1/2/8/17` 过滤。

> 「已设不可续但页面仍显示可续」排查见工单案例 [`续班与业绩/业绩归因/排查/已设不可续但页面显示可续.md`](../../../../工单/续班与业绩/业绩归因/排查/已设不可续但页面显示可续.md)：灰名单配置存在(status=1,type=0) 但 sign_x 未回套 17 → 页面按 sign_x 显示可续。

## 青舟接口详情页（product-b / release）

- [POST /b/renewal/manage/clazz/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734319&appId=product-b&branchName=release) id=2734319
- [POST /b/renewal/manage/clazzDetail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734339&appId=product-b&branchName=release) id=2734339
- [POST /b/renewal/manage/student/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734191&appId=product-b&branchName=release) id=2734191
- [POST /b/renewal/manage/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734100&appId=product-b&branchName=release) id=2734100
- [POST /b/renewal/manage/renewalMsgList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734355&appId=product-b&branchName=release) id=2734355
- [GET /b/renewal/manage/renewalConfigType/downloadTemplate](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2766290&appId=product-b&branchName=release) id=2766290
- [POST /b/renewal/manage/batchUploadRenewalConfigType](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2766291&appId=product-b&branchName=release) id=2766291
