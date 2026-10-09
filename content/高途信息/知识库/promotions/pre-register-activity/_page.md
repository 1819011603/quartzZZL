# 预报名活动（pre-register-activity）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-promotions master 代码整理。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/pre-register-activity` |
| 菜单 | OES（ark 基座）→ 续班管理 → 预报名活动 |
| 前端仓库 | gaotu-fe-promotions `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/gaotu-fe-promotions`（master，本地 `~/IdeaProjects/WebProject/gaotu-fe-promotions`） |
| 前端路由 | `routes.js:16-20` → `src/pages/PreRegisterAvtivity/index.jsx`（目录名拼写就是 Avtivity），wrapper `src/wrappers/commonDict.js` |
| 新建/编辑/查看 | 同页抽屉 `src/pages/PreRegisterAvtivity/CreateOrEditActivity/index.jsx`（`type`=create/edit/view），无子路由 |
| 后端主服务 | 网关前缀 `/promotionManagement` → 青舟 appId `promotionmanagement.gaotu100.com`（gapm-appid `promotionmanagement-gaotu100-com`，仓库 **promotion-management**，`PreOrderActivityController`） |
| 关联页面 | 续班计划详情 → 续班流程 → 预报名配置「+活动管理」绑定的就是这里的活动（`node_config` 预报名节点存 `preOrderActivityNumber`） |

## tab 列表

无 tab，列表 + 抽屉。

## 页面级接口

`.../CreateOrEditActivity/` = `src/pages/PreRegisterAvtivity/CreateOrEditActivity/`；`UserScope/` = `.../CreateOrEditActivity/components/UserScope/`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（字典为空时） | `GET /course-center/b/common/department/tree` | `getDepartmentTree` | `src/models/useCommonDict.js:58`（`src/services/continuationClasses.js:83`） | course-center | 部门树 | 读 |
| 进页面（同上） | `GET /course-center/b/common/dictionary/all` | `getCommonDictionary` | `src/models/useCommonDict.js:59`（`src/services/continuationClasses.js:77`） | course-center | 字典 | 读 |
| 进页面/查询/翻页/操作后刷新 | `POST /promotionManagement/preOrderActivity/list` | `queryPreRegisterActivityList` | `src/pages/PreRegisterAvtivity/index.jsx:48`（`service.js:4`） | promotionmanagement | 预报名活动列表 [2650267] | 读 |
| 列表「发布」 | `POST /promotionManagement/preOrderActivity/publish` | `publishPreRegisterActivity` | `index.jsx:67`（`service.js:20`） | promotionmanagement | 发布 [2650265] | 写 |
| 列表「删除」 | `POST /promotionManagement/preOrderActivity/delete` | `deletePreRegisterActivity` | `index.jsx:81`（`service.js:34`） | promotionmanagement | 删除 [2650264] | 写 |
| 列表「作废」 | `POST /promotionManagement/preOrderActivity/abolish` | `abolishPreRegisterActivity` | `index.jsx:95`（`service.js:27`） | promotionmanagement | 作废 [2650266] | 写 |
| 列表「暂停」/「重启」 | `POST /promotionManagement/preOrderActivity/modifyStatus` | `modifyPreRegisterActivityStatus` | `index.jsx:120`（`service.js:57`），`operateType=PAUSE/RESTART` | promotionmanagement | 修改状态 [3363885] | 写 |
| 点「查看」/「编辑」 | `POST /promotionManagement/preOrderActivity/detail` | `getPreRegistrationActivityDetail` | `.../CreateOrEditActivity/index.jsx:177`（`src/services/continuationClasses.js:225`） | promotionmanagement | 活动详情 [2650261] | 读 |
| 打开抽屉 | `POST /promotionManagement/activity/queryUserConditionDictionary.do` | `getUserScopeConditions` | `UserScope/index.jsx:27`（`UserScope/service.js:3`） | promotionmanagement | 用户范围条件字典 [62014] | 读 |
| 用户范围输入班级ID | `POST /promotionManagement/activity/checkClazzId.do` | `checkClazzId` | `UserScope/hooks/userValidator.js:27` | promotionmanagement | 校验班级ID [62067] | 读 |
| 用户范围输入课程ID | `POST /promotionManagement/activity/checkCourseId.do` | `checkCourseId` | `UserScope/hooks/userValidator.js:33` | promotionmanagement | 校验课程ID [62066] | 读 |
| 用户范围输入营销活动ID | `POST /promotionManagement/activity/checkPromotionActivityId` | `checkActivityId` | `UserScope/hooks/userValidator.js:39` | promotionmanagement | 校验活动ID [62065] | 读 |
| 保存前（含班级条件时） | `POST /clazz/getClazzInfosByValue.do` | `getClazzInfosByValue` | `.../CreateOrEditActivity/utils/index.js:12`（`UserScope/service.js:28`） | promotionmanagement | 按值查班级 [62023] | 读 |
| 抽屉「保存」 | `POST /promotionManagement/preOrderActivity/edit` | `createPreRegisterActivity` | `.../CreateOrEditActivity/index.jsx:110`（`service.js:42`） | promotionmanagement | 新建/编辑 [2650262] | 写 |
| 抽屉「保存并发布」 | `POST /promotionManagement/preOrderActivity/editAndPublish` | `saveAndPublishPreRegisterActivity` | `.../CreateOrEditActivity/index.jsx:148`（`service.js:49`） | promotionmanagement | 保存并发布 [2650263] | 写 |
| 「+添加膨胀券」选券抽屉 查询/翻页 | `POST /component/student-center/renewal/pre/coupon/list` | `queryPreOrderCouponList` | `.../components/ExpansionCoupon/SelectDrawer.jsx:40`（`service.js:65`） | student-center | 预报名可选膨胀券 [5644416] | 读 |

> `service.js` 指 `src/pages/PreRegisterAvtivity/service.js`。`app.js` 无全局前缀，路径即实际请求路径；本页不走 `productPrefix`(`/product-b`)。

## 关键表

promotion-management 本身不落库，`PreOrderActivityController` 经 Feign `PreOrderActivityRemoteService`（`PROMOTION-B.GAOTU100.COM`，`/domain/promotion/b/preOrderActivity`）调 **promotion** 服务（`PreOrderActivityFeignService` → `PreOrderActivityService`）。

| 表 | 含义 |
|---|---|
| `promotion.pre_order_activity` | 预报名活动主表 |
| `promotion.pre_order_activity_product` | 活动关联商品 |
| `promotion.promotion_range_relation` | 活动范围关系 |
| `promotion.promotion_user_relation` / `promotion_user_rule` / `promotion_user_condition_file` | 用户范围（人群、规则、上传的条件文件） |
| `promotion.renewal_white_user` | 白名单 |

各接口具体写哪张表未逐个核对，只确认 service 注入了这些 repository。

## 排查提示

- 列表/详情不对 → `preOrderActivity/list`、`detail`（promotion-management）
- 选不到膨胀券 → `renewal/pre/coupon/list`（student-center）
- 续班计划里预报名节点关联错活动 → 续班计划 `renewal/process/list` 返回的 `preOrderActivityNumber`，见 [续班流程](../continuation-classes/renewalProcess.md)

## 青舟接口详情页

- [POST /promotionManagement/preOrderActivity/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2650267&appId=promotionmanagement.gaotu100.com&branchName=release) id=2650267
- [POST /promotionManagement/preOrderActivity/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2650261&appId=promotionmanagement.gaotu100.com&branchName=release) id=2650261
- [POST /promotionManagement/preOrderActivity/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2650262&appId=promotionmanagement.gaotu100.com&branchName=release) id=2650262
- [POST /promotionManagement/preOrderActivity/editAndPublish](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2650263&appId=promotionmanagement.gaotu100.com&branchName=release) id=2650263
- [POST /promotionManagement/preOrderActivity/publish](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2650265&appId=promotionmanagement.gaotu100.com&branchName=release) id=2650265
- [POST /promotionManagement/preOrderActivity/abolish](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2650266&appId=promotionmanagement.gaotu100.com&branchName=release) id=2650266
- [POST /promotionManagement/preOrderActivity/delete](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2650264&appId=promotionmanagement.gaotu100.com&branchName=release) id=2650264
- [POST /promotionManagement/preOrderActivity/modifyStatus](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3363885&appId=promotionmanagement.gaotu100.com&branchName=release) id=3363885
- [POST /renewal/pre/coupon/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5644416&appId=student-center&branchName=release) id=5644416
