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

> 2026-10-09 逐接口追到 mapper XML SQL 核对。

链路：promotion-management `PreOrderActivityController` → `PreOrderActivityDomainServiceImpl` → Feign `PreOrderActivityRemoteService`（`PROMOTION-B.GAOTU100.COM`，`/domain/promotion/b/preOrderActivity`）→ **promotion** 仓库 `promotion-controller/.../feign/preorder/PreOrderActivityFeignService.java` → `promotion-app/.../service/preorder/PreOrderActivityService.java`（下称 `S`）。
**promotion-management 自己不碰库**，只额外读 cas（创建人名）、product、course-center。

### 接口 → 表

| 接口 | promotion 方法 | 读表 | 写表（操作） | 事务 / MQ / 缓存 / 其它 |
|---|---|---|---|---|
| list | `S#page:152` | `pre_order_activity`（`is_del=0`，按 name/number/status/type 筛） | 无 | — |
| detail | `S#detail:489` | `pre_order_activity`、`pre_order_activity_product`；条件型另读 `promotion_range_relation`、`promotion_user_condition_enums`、`promotion_user_condition_ext`；文件型读 `promotion_user_condition_file`；`renewal_white_user`；Feign product-b 读 `gaotu.renewal_pre_order_activity_coupon_scope` | 无 | 另调 coupon Feign 补券信息 |
| edit · 新建（number 空） | `S#create:610` → `createActivityWithProducts:1056` | 校验读 `pre_order_activity_product`、`pre_order_activity`（券是否被占用 :1476） | **事务内**：`pre_order_activity` INSERT；`pre_order_activity_product` INSERT（每个商品一行）；条件型 `promotion_range_relation` 批量 INSERT；文件型 `promotion_user_condition_file` INSERT + `promotion_user_relation` INSERT；Feign product-b upsert `gaotu.renewal_pre_order_activity_coupon_scope`。**事务外**：`renewal_white_user` 物理 DELETE 再 INSERT | 另调 `clazzAclService` 校验班满；无 MQ |
| edit · 编辑（number 非空） | `S#edit:562` | 同上 | 仅可改结束时间的状态（`onlyEditEndTime:1903`）：`pre_order_activity` UPDATE 起止时间。其余状态（`updateActivityWithProducts:1089`，事务）：`pre_order_activity` UPDATE；传了商品则 `pre_order_activity_product` 置 `is_del=1` 再 INSERT；传了用户条件则 `promotion_range_relation` / `promotion_user_condition_file` / `promotion_user_relation` 置 `isdel=1` 再重插；传了券则 upsert coupon_scope。两分支事务外都 DELETE+INSERT `renewal_white_user` | 改结束时间分支：发 MQ `modify_status`（时间落在当天才发），**不清缓存**；其余分支清 Redis `promotion:preOrderActivity:visible:{number}` |
| editAndPublish · 新建 | `S#createAndPublish:679` → `executeCreateAndPublish:891` | 同新建 | 新建的全部写入 + `pre_order_activity` UPDATE `activity_status`（`executePublishStatusUpdate:855`）。事务外：`renewal_white_user` DELETE+INSERT；条件型 `promotion_user_rule` INSERT（ruleId 来自 Feign `RULE.GAOTU100.COM` `postRule`） | 非条件/文件型发 MQ；**不清缓存** |
| editAndPublish · 编辑 | `S#editAndPublish:716` → `executeEditAndPublish:909` | 同编辑 | 编辑的全部写入（无"仅改结束时间"分支）+ UPDATE `activity_status`；事务外同上 | 非条件/文件型发 MQ；清 Redis（:758） |
| publish | `S#publish:647` | `pre_order_activity` | **事务内** `pre_order_activity` UPDATE `activity_status`（条件/文件型 → PUBLISHING，否则按时间算）。事务外：条件型 `promotion_user_rule` INSERT（postRule） | 非条件/文件型发 MQ；文件型交给 xjob；**不清缓存** |
| abolish | `S#abolish:766` | `pre_order_activity`、`promotion_user_rule`（`isdel=0`） | `pre_order_activity` UPDATE `activity_status=ABOLISHED` | 无事务；有规则时 Feign `disableRule`（不改 `promotion_user_rule`）；清 Redis |
| delete | `S#delete:786` | `pre_order_activity` | `pre_order_activity` UPDATE `is_del=1`（仅待发布状态可删） | 无事务；**不级联**商品/范围/白名单；清 Redis |
| modifyStatus | `S#modifyStatus:806` | `pre_order_activity` | `pre_order_activity` UPDATE `activity_status`（operateType=1 暂停 → STOPED；重启按时间重算，未变则跳过） | 无事务；清 Redis；无 MQ |

### 表

| 表 | 库 | 含义 |
|---|---|---|
| `pre_order_activity` | promotion | 活动主表：number、name、type（1 定金班 / 2 膨胀券）、begin/end_time、activity_status、user_condition_type、creator_id、is_del |
| `pre_order_activity_product` | promotion | 活动商品：pre_order_activity_number、product_number、product_type、is_del（不存券） |
| `promotion_range_relation` | promotion | 用户条件范围（操作符行 + 值行）：promotion_activity_number、promotion_user_condition_number、operator_type/value、isdel |
| `promotion_user_condition_enums` | promotion | 用户条件字典，只读 |
| `promotion_user_condition_ext` | promotion | 条件操作符/枚举扩展，只读 |
| `promotion_user_rule` | promotion | 活动 → 规则引擎 userRuleId |
| `promotion_user_condition_file` | promotion | 文件型用户条件 |
| `promotion_user_relation` | promotion | 活动 ↔ 用户关联标记（文件型 relation_type=0） |
| `renewal_white_user` | promotion | 白名单手机号，`biz_number`=活动 number |
| `renewal_pre_order_activity_coupon_scope` | **gaotu**（product-server `PreOrderActivityCouponScopeBizMapper.xml`） | 膨胀券可用范围：活动 number、coupon_sku_number、年级/学科、is_del；upsert / 逻辑删 |

注意：
- 库名取自 mapper XML 里的 `promotion.` / `gaotu.` 前缀，没核对数据源 yml。
- 白名单和 `promotion_user_rule` 的写入在事务外，和活动主表不是原子的；coupon_scope 走 Feign，也不是分布式事务。
- MQ topic 是 `@Value` 默认值 `promotion_preorder_activity_delay_test`、tag `modify_status`，延迟到起止时间投递；线上 topic 名没确认。
- 可能的坑：publish、createAndPublish、编辑"仅改结束时间"三处不清 Redis 可见缓存；delete 不级联子表；`getByNumber` 不过滤 `is_del`。

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
