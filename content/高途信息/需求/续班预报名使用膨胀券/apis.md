---
title: 续班预报名使用膨胀券 · 接口契约
tags: [需求, 接口]
---

# 接口契约

> 只记录当前生效的跨服务契约。字段类型和请求示例以 `apifox-openapi.json` 为准。

## 接口清单

| 服务 | 接口 | 方法/类 | 当前契约 | 调用方 | 状态 |
|---|---|---|---|---|---|
| promotion-b | `/domain/promotion/b/preOrderActivity/detail` | `PreOrderActivityService#detail` | product 项返回券 ID、券名、商品 ID、金额、双状态、状态文案、创建人及 scopes | promotion-management、product-server | 联调通过 |
| promotion-c | `POST /domain/promotion/c/preOrderActivity/listFromCache` | `PreOrderActivityService#listFromCache` | 返回活动形式及完整券字段/scopes，供 C 端组装 | cart | 联调通过 |
| product-b | `POST /feign/preOrderActivity/couponScope/save` | `PreOrderCouponScopeFeignController#save` | 只写券范围表，不调用 promotion；由 promotion-b 事务内调用 | promotion-b | 自测通过 |
| product-b | `POST /feign/preOrderActivity/couponScope/listByActivityNumbers` | `PreOrderCouponScopeFeignController#listByActivityNumbers` | 按活动号批量返回扁平 scope 行 | promotion-b/c | 联调通过 |
| product-b | `POST /feign/preOrderActivity/couponScope/listDisplayableByRenewalPlan` | `PreOrderCouponScopeFeignController#listDisplayableByRenewalPlan` | **入参只有 `renewMasterNumber`**（2026-09-16 下午移除 `userId`）。**计划级**：用计划配置的全部前置课程反查后置，再与券范围「年级+学科」整对匹配；未绑活动、订金班或无匹配返回空列表 | student-center | 实测通过 |
| student-center | `POST /renewal/pre/coupon/list` | `PreOrderCouponController#listCoupon` | **无 `userId`**（2026-09-16 下午移除，当日上午曾短暂必填）：`renewMasterNumber` 单独即可算出**计划级**范围。双状态条件始终透传 coupon-a。返回 `availableScope`、字符串 `holdLimit`、双状态文案及 `creator`；售罄用 `selectable=false` | B 端选品弹窗 | 实测通过 |
| student-center | `POST /renewal/pre/couponScope/list` | `PreOrderCouponController#listCouponScopes` | 查询券可用范围 | 老师端 | 自测通过 |
| cart | `GET /web/renewal/preRegistration` | `RegistrationService#preRegistration` | 按活动形式分订金班/膨胀券；膨胀券走三者交集和双状态过滤，返回统一 `RegistrationProductVO` | C 端落地页 | 联调通过 |
| promotion-b | `/promotionManagement/preOrderActivity/edit`、`/editAndPublish` | `PreOrderActivityService#validateProductListByType` | 膨胀券售罄时报 `PARAMS_ERROR`；订金班满班时报 `PARAMS_ERROR`，`capacity=-1` 放行 | OES 活动管理 | 已编码，待边界实测 |
| product-b | `POST /feign/preOrderCoupon/listScopeByCouponSkuNumbers` | `PreOrderCouponFeignController#listScopeByCouponSkuNumbers` | 按券商品 ID 批量反查预报名范围（`activityNumber`/`renewalNumber`/`scopes`）；入参**裸 `List<Long>`**，不是包装对象；查不到续班计划的券不返回 | student-data 券回溯链路 | 2026-09-15 联调通过 |

## T-43 落地（用户确认接口）

- 用户明确指出：目标接口就是 `student-center` 的 `POST /renewal/pre/coupon/list`（`PreOrderCouponController#listCoupon`），即 T-36 已实现的那个膨胀券选品接口，OES「添加商品」弹窗与「老师下单弹窗」复用同一套接口。之前两轮代码排查走的 promotion-management/product-server 方向（`spuSearch` 等）是误判，本需求不涉及那条链路。
- 用户口径：**去掉 Apollo 展示白名单**，`statusList`/`saleStatusList` **不传即全量**（不按该维度过滤）——默认勾选【使用中】【开售中】由前端决定，服务端不再补默认值；传了就原样透传给电商（原白名单是老师下单弹窗的安全网，会把 OES 想看的【审核中/已失效/停售中】也拦掉，2026-09-16 已去掉）。
- ⚠️ 2026-09-16 用户已确认电商侧 `saleStatuses` 服务端过滤的已知限制**已修复**（此前 coupon-c `CouponExpandConfigRepositoryImpl#normalize()` 漏拷字段，传了等于没传），筛选可正常生效。
- 已实现（2026-09-16，student-center，已提交 `49a2a9ab7`，已推送，部署中）：
  - `PreOrderCouponListRequest` 新增 `saleStatusList`（`List<Integer>`），与既有 `statusList` 对称；`obtainStatusList()`/`obtainSaleStatusList()` 改为「未传返回 `null`」（不再补默认值）。
  - `PreOrderCouponBiz` 删除 `displayCouponStatusConfig`/`displaySaleStatusConfig` 两个 Apollo 白名单字段及 `resolveCouponStatuses`/`parseStatusConfig`/`toQueryStatusesOrNull`；`statusList`/`saleStatusList` 直接用 `request.obtainStatusList()`/`obtainSaleStatusList()` 下发给电商（`null` 时电商按不限处理）。
  - 新增 `revokeSelectableWhenNotOnSaleInUse`：非【开售中】的券 `selectable` 置 `false`（`PreOrderCouponWrapper` 里 `selectable` 只按 `couponStatus` 算，这一层补 `saleStatus` 维度），配合已有的 `selectableOfStatus`（couponStatus 维度）与售罄判定，三层共同保证「只能勾选使用中且售卖中」。
  - 响应字段（`couponStatus`/`couponStatusDesc`/`saleStatus`/`saleStatusDesc`）此前已存在，**未改动**，OES 列表展示无需额外开发。
  - 同步改了 `PreOrderCouponBizScopeFilterTest`：删掉引用已删 Apollo 字段的反射 setter；把几条基于「本地过滤删行」的旧断言（2026-09-14 服务端过滤重构后已经名不副实）改写成按 `selectable` 断言，并补了状态透传/全量的用例。**18 条全过**。
- ⚠️ **行为变化提醒**：老师下单弹窗（B 端）如果前端不显式传 `statusList=[1]`/`saleStatusList=[2]`，现在会看到全部状态的券（只是不可选状态置灰）——依赖前端按原 UX 默认勾选传参，不再靠服务端兜底。

## 跨模块方法

| 服务 | 类#方法 | 当前职责 | 调用方 |
|---|---|---|---|
| product-server | `PreOrderCouponIntersectService#intersect` | 唯一的匹配实现：**券范围 × 后置年级学科两者**按整对判断（2026-09-16 删除前置学科过滤） | B/C 范围链路 |
| product-server | `PreOrderCouponIntersectService#narrowToInClazzCourses` | 学员维度收窄：候选前置课程 → 该学员真正在读的那几门；走花名册 `ClazzDistSubclazzStudentDao#listInClazzStudentByUidAndCourseNos` | `PreOrderDisplayableCouponService` |
| product-server | `PreOrderDisplayableCouponService#listDisplayableCoupons` | **两个签名**：`(renewMasterNumber)` = 计划级不收窄（B 端）；`(renewMasterNumber, userId)` = `userId` 有效才按在读收窄（C 端），`userId` 为 null/≤0 等价于计划级 | B 端 scope Feign controller / C 端 RenewalMasterController |
| student-center | `PreOrderCouponScopeAclService#listDisplayableCoupons` | 入参只有 `renewMasterNumber`；读取 product-b 计划级匹配结果；失败直接抛业务异常 | `PreOrderCouponBiz#listCoupon` |
| promotion | `PreOrderCouponEnricher#enrich` / `#enrichDTO` | 使用 camelCase 请求查询 coupon-a，补齐缓存与详情两条链路的券字段 | promotion-b/c |
| promotion | `PreOrderActivityService#validateCouponNotSoldOut` | 批量查询券库存，保存活动时拦截售罄券 | edit/editAndPublish |
| promotion | `PreOrderActivityService#validateClazzNotFull` | 使用 `signUpCount`/`capacity` 拦截有限班容满班课程 | edit/editAndPublish |

## 已知陷阱

- product-b 的 controller 若通过 `implements XxxFeignClient` 复用接口方法签名，**必须在实现类自己的方法上重新声明
  `@PostMapping`/`@RequestBody`**——Spring 不从接口继承参数级注解，漏了会静默退化成 `@ModelAttribute` 表单绑定：
  包装对象入参时字段全部绑成 `null`（无异常，返回 200 空结果），裸 `List` 入参时直接抛
  `BeanInstantiationException`。`listScopeByCouponSkuNumbers` 上踩过，同目录 `QuestionnaireFeignService` 是正确写法可参考。
- 入参优先用裸集合类型（如 `List<Long>`），避免用包一层的请求 DTO——本仓库这类包装对象在这条 FastJson +
  JaCoCo 离线插桩的消息转换链路下曾出现字段绑定失败的怀疑（后来定位为上一条注解问题，但裸类型本身也是
  `listByActivityNumbers` 已验证可行的写法，风险更低）。

## 当前兼容规则

- 所有 19 位 ID 以字符串序列化。
- product-b 返回 `RestTraceResponse<T>` 信封，跨服务复杂集合使用扁平行。
- promotion 调 coupon-a 使用 `CamelExpandCouponQueryRequest`，避免全局 SnakeCase 改写请求字段。
- student-center 调 product-b 使用 `PRODUCT-B` 与 `ProductInterceptorFeignConfig`。
- `couponStatusDesc` 由本地映射；`creator` 查询失败保留工号。
- 状态白名单配置为空串时关闭对应维度过滤。

## 当前契约缺口

| 缺口 | 影响 | 当前处理 |
|---|---|---|
| coupon-a 的 `couponName` 只支持左匹配 | 输入券名中间词无法命中 | B 端提示从券名开头输入；需推动电商支持包含匹配 |
