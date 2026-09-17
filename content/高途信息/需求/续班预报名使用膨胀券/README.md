---
title: 续班预报名使用膨胀券
aliases:
  - 【续班】预报名使用膨胀劵
  - 【预报名】预报名支持膨胀劵
  - 004-xuban-pre
status: 开发中
owner: zhangzeling
branches:
  - promotion:feature-xuban-pre
  - promotion-app:feature-xuban-pre
  - product-server:feature-xuban-pre
  - cart:feature-xuban-pre
  - student-center:feature-xuban-pre
  - promotion-management:feature-xuban-pre
  - student-data:feature-xuban-pre
  - mweb:feature-coupon-20260901
  - cronus:feature-coupon-20260901
  - gaotu-fe-promotions:feature-coupon-20260901
updated: 2026-09-17
tags: [需求]
---

# 续班预报名使用膨胀券

> [[links|链接中心]] · [[tasks|当前任务板]] · [[apis|接口契约]] · [[verify|验证手册]] · [`build-data.md`](build-data.md) · [[changelog|决策摘要]] · [`脚本/`](脚本/) · `apifox-openapi.json`
> 本文件只保留当前最终口径。续接时先读这里，再按问题进入对应文件。

## 一句话

在订金班预报名之外增加膨胀券预报名：活动挂券商品，学员购券即完成预报名，无需进班。

## 需求范围

- 老师可在花名册发链接，并在 B 端下单弹窗选择膨胀券。
- 学员可在 C 端预报名落地页选择膨胀券；一券只能买一次，支持多选。
- 运营配置活动、券商品及适用年级学科。
- 订金班范围读取可续关系；膨胀券范围读取券配置的年级+学科。
- order 侧只负责膨胀券商品加购与购物车总价；**2026-09-15 确认 order 不在本期上线范围**，其分支与后续链路均由订单团队自行管理。
- student-data 券预报名字段与指标归马胜的分支代码（`feature-xuban-pre` 上已有 `预报名支持膨胀券` 等提交）；
  2026-09-15 因联调 `backDwsPresaleHandler` 回溯打通链路，zhangzeling 补了 product-server 侧的下游接口与两处底层 bug 修复，
  student-data 侧只改了一处 Feign 调用签名（配合 product-b 契约变更），未改动业务逻辑，详见 [[changelog]]。

## 最终口径

- `productType=8014`；8027 是课时包商品，27 是老优惠券概念。
- `presaleOrderTime` 取**最新**（多张券之间、券与订金班之间都取最新），依据需求第 75 行；
  2026-09-15 前实现为取最早，已订正，见 [[changelog]]。
- 活动商品行的 `productNumber`/`skuId` 都是券商品 ID（`skuNumber`）；`couponId` 是券定义 ID。
- 券范围唯一键为 `uk_act_grade_subject(activity_number, grade_code, subject_code)`：活动内年级学科组合唯一，同一张券可跨活动使用。
- 券不参与满赠；落地页统一使用 `/preSignUp`，不按活动形式拆 path。
- 券信息实时读取 coupon-a，不落业务库、不使用 mock；`couponStatusDesc` 由本地枚举维护。
- 默认只展示 `couponStatus=1`（使用中）且 `saleStatus=2`（售卖中）的券；任一状态为空不展示。
- 状态白名单由 Apollo 配置。student-center 将 `couponStatuses`/`saleStatuses` 透传 coupon-a 服务端过滤，不做分页后本地过滤。
- B 端膨胀券 tab 始终展示。`renewMasterNumber` 只控制续班计划范围过滤；不传时仍执行状态过滤。
- **券匹配是「两者」不是「三者」**（2026-09-16 按 PRD 订正）：券配置的年级学科 × 后置班年级学科，
  按“年级+学科”整对判断；**前置班不参与匹配**，只作为定位续班计划与反查后置课程的起点。
  原多的一层前置学科过滤会在扩科场景漏券，已删除。只在 product-server 计算。
- 🔴 **B/C 两端券范围口径不同（2026-09-16 产品定稿，不是 bug）**：

  | 端 | 接口 | 口径 | `userId` |
  |---|---|---|---|
  | B 端下单弹窗 | `/renewal/pre/coupon/list` | **计划级**：用计划配置的全部前置课程 | **不接收** |
  | C 端落地页 | `/c/renewMaster/listDisplayableCoupons` | **学员级**：花名册筛出该学员真正在读的前置课程为起点 | **必传** |

  **为什么不同**：老师在花名册里看的是整个计划能卖哪些券，按某个学员收窄会让老师看不全；
  学员只应看到自己在读班对应的那部分。**同一计划下老师看到的券可能多于学员看到的，属预期**。
  C 端在读数据源是 clazz-distribution 花名册（非 student-data 预报名表，原因见 [[changelog]]），
  状态取 ACTIVE/INACTIVE/HOLD 三态；学员无在读前置班 → C 端返回空，不退化为计划级。

  实现上是同一个方法两种签名：`listDisplayableCoupons(planNumber)` 计划级 /
  `listDisplayableCoupons(planNumber, userId)` 学员级，`narrowToInClazzCourses` 仅 C 端调用。
- 预警链路（`InspectService`）**不加**学员维度，PRD 规定预警按「前置班级+后置班级」统计。
- **膨胀券后置课取 `calculateRenewalType=1`（续班关系）**，订金班取 `=2`（预报名关系），两条链路口径不同不可互换。
  student-data 走 `mapRenewalPostCourseByNumber`，product-server `listPostCourseNumbers` 同样只取 =1（2026-09-17 补，此前无过滤）。
- 券范围按 **(券, 活动, 续班计划) 三元组**返回：一张券可挂多个活动，一个活动可绑多个续班计划，
  两者都是合法形态，不做收敛。student-data 侧唯一键无活动/计划维度，撞键时年级学科取并集。
- `creator` 返回 CAS displayName；电商给工号后，经 teacher-basic 取 accountId，再查 CAS，失败时保留工号。
- promotion-b 保存活动时在事务内调用 product-b `POST /feign/preOrderActivity/couponScope/save` 写范围；失败回滚活动。
- 售罄券和满班课程由 promotion 保存接口服务端拦截；`capacity=-1` 表示不限班容，必须放行。
- student-data 券回溯（`backDwsPresaleHandler`）依赖的 `/feign/preOrderCoupon/listScopeByCouponSkuNumbers` 已在 product-b 补齐，
  入参是裸 `List<Long>`（不是包装对象），详见 [[apis]]；`renewalNumber` 反查经
  `activityNumber -> RenewalLinkActivity.processNumber -> ProcessConfig.renewalNumber` 两跳，一个活动只应绑一个有效续班计划。

## 现在什么情况

| | |
|---|---|
| 阶段 | 开发中；核心 B/C 链路已打通并于 2026-09-16 完成**学员维度口径订正**的端到端验证，剩余边界验证 |
| 进度 | T 12/17 · R 0/0 · C 0/0 |
| 部署泳道 | 本需求服务 `test-gtbg-dev-3`；coupon-a `test-eco-7`，两者均属于 dev 逻辑环境 |
| 当前卡点 | 缺少真实售罄券（40 张可用券全部未售罄）；缺少有限班容且已满班的班级；下单需 `test` 泳道但该泳道无本需求代码；**「券与订金班取并集」零数据覆盖，需造数** |
| 最近更新 | 2026-09-17（T-47 发布计划✅ + TAPD✅）：青舟发布计划 **23592**「【A-续班-20260901】膨胀券预报名」已排 **22 个服务**（后端 12 + 前端 10）。按仓库拉全量部署补齐了「一仓库多部署」的漏项：product-server→product-task、promotion→promotion-task、student-data→student-data-gps、mweb→lexue-m-fe/gongkao-m；产物镜像自动取各分支最新一条，配置行(SQL/MQ + Apollo key)原样回传。promotion 两条上线分支保持 `release`（master 无镜像，决定不改）。TAPD story 下张泽灵 7 条任务已全部置「已完成」。见 [[links]]「上线」、[[tasks]] T-47。<br>2026-09-17（预警邮件✅）：订正触发入口——HTTP `POST /b/renewal/insect/send` 实际调的是 `InspectService#deal()`（只重算、**不发邮件**，且会重建预警行使「已处理」被冲掉）；真正发信是 XXL-Job `RenewalInsectHandler → InspectService#send()`，手动可用 product-b 反射桥直接调。桥调 `send()` 后收到「预报名预警」邮件（计划 `578668076965308416`，英语/语文后置产品 2 行）。收件人是计划 ADMIN 的 CAS `mail`（`@gaotu.cn`，非 @baijia.com）；「预报名状态」列为硬编码「未绑定」。详见 [[verify]]「预警邮件怎么验」。<br>2026-09-17（T-46✅）：花名册回溯**默认带上膨胀券**。券清单不再手填，改为按「班级 → 续班计划 → 计划下可展示券」自动推导（计划级）；`BackPresaleParam` 加 `backCoupon`（缺省 true），`couponSkuNumbers` 降为可选过滤器；两个 job 公共骨架抽到 `PresaleBackfillHelper`。commit student-data `cd56fb484`，单测 27 条全过，已发 `test-gtbg-dev-3`（pipeline `1273791`）实测两个 job 均自动推导出券清单并完成券回溯。详见 [[verify]]「花名册回溯默认带上膨胀券」。<br>2026-09-17（T-45 端到端复测✅）：先重推券订单消息未落库，定位为 `test-gtbg-dev-3` 的 student-data-dws 镜像滞后（`5c63f8ba`，跑旧 =2 方法）；重发含 `74c6e6b78` 的镜像（pipeline `1273324`，新 pod eureka UP）后重推同一消息，MySQL `dws_fuwu_clazz_user_presale_coupon` 落 1 行 + 小班 ES `ads_small_clazz_user_index_v4` 写入 `smallPresaleStatus=1/smallPresaleSubject=[12]` 通过。详见 [[verify]]「复测通过」。<br>2026-09-17（T-45）：券回溯收数口径两处订正。①券范围按 (券,活动,续班计划) 三元组返回，不再只取首个活动/首个计划（student-data 唯一键无活动计划维度，撞键时年级学科取并集）。②膨胀券后置课改取 `calculateRenewalType=1`（续班关系）——原先复用订金班的 `mapPostCourseByNumber`（=2），取到的是学员并不可续的后置课；product-server `PreOrderCouponIntersectService#listPostCourseNumbers` 此前**完全没做该过滤**，券列表里会多出学员续不了的券，已补上，发链接/B 端弹窗/C 端落地页三处同源生效。订金班口径一行未动。student-data `74c6e6b78`、product-server `fe076a536`（cherry-pick `c1937337e`）。单测 27 条全过，桥验证与消费验证见 [[verify]]。<br>2026-09-17：售卖状态文案对齐 PRD，`saleStatusDesc` 由「开售中/停售中」改为「售卖中/停止售卖」（`PreOrderCouponSaleStatusEnum`），状态码含义不变。student-center `cfd1b4bda`，已发 `test-gtbg-dev-3` 实测确认返回值。<br>2026-09-17（T-44）：排查发现 promotion-b 保存活动时从未校验券状态（只查过售罄/满班），已失效/审核中/停止售卖的券只要没售罄就能绑定保存，前端置灰挡不住。新增 `validateCouponInUseAndOnSale`，要求 `couponStatus=1` 且 `saleStatus=2` 才放行。promotion `6fb3da3a0`，已发 `test-gtbg-dev-3`，反射调用实测：停止售卖真实券被拒绝、使用中+售卖中真实券创建成功（已清理）。⚠️ 现有测试活动 `579607430990692352` 绑的 3 张券售卖状态都已变停止售卖，之后编辑会被拦，需先恢复。详见 [[apis]]「保存活动时的膨胀券状态校验」、[[tasks]] T-44。<br>2026-09-16（T-43）：PRD 追加 OES 选品弹窗需求（筛选区/列表加使用状态与售卖状态），复用 `/renewal/pre/coupon/list`（未新建接口）。去掉 Apollo 展示白名单，`statusList`/`saleStatusList` 改为**不传即全量**（默认勾选交给前端决定）；非「使用中且售卖中」的券展示但 `selectable=false`（新增 `revokeSelectableWhenNotOnSaleInUse` 补售卖状态维度判定）。student-center `49a2a9ab7`，已发 `test-gtbg-dev-3` 并实测：不传筛选 `total=297` 全量且 selectable 正确；显式传状态筛选正确透传（含确认此前记录的 coupon-c `saleStatuses` 过滤失效问题已修复）。详见 [[apis]]「T-43 落地」、[[tasks]] T-43。<br>2026-09-16：按 PRD 与产品流程图订正券匹配口径并完成端到端验证。**两处改动**：①删掉前置学科过滤（匹配只有「券范围 × 后置年级学科」两者，前置仅作定位起点）——原实现会在**扩科**场景漏券，而扩科正是膨胀券主要用途；②券范围由「计划级」改为「学员级」（该学员在当前计划前置班级里的全部在读班），`/renewal/pre/coupon/list` 新增**必填** `userId`。在读数据源选 clazz-distribution 花名册而非 student-data 预报名表（后者 `is_del=0` 不等于在读、且只在已进后置班时落行，会漏掉目标人群），故 **student-data 一行未改**。cart 的 C 端同步改调 product-c 新接口，与 B 端同源，删掉原「计划目标年级」近似实现。四服务已发 `test-gtbg-dev-3`，8 个场景验证通过，订金班链路实测未受影响，详见 [[verify]]。<br>2026-09-15（三）：6 个仓库 WIP MR 已建（promotion 走 **master**，其余走 release；order 与 promotion-app 不在本期范围），链接见 [[links]]，口径见 [[tasks]]。<br>2026-09-15（二）：按需求第 75 行把 `presaleOrderTime` 口径从「取最早」订正为「取最新」（6 处 `min→max`，大小班 × 增量/全量 4 个文件，4 个单测同步翻转）；并发现「券与订金班取并集」规则**零数据覆盖**（两表按学员+学年+学期交集 0 行），造数方案与回溯用法已写入 [[verify]]，见 T-38/T-39。<br>2026-09-15（一）：`backDwsPresaleHandler` 券回溯链路端到端跑通并在 ES 验证生效（`presaleSubject`/`gradePresaleSubject` 有值）。过程中定位并修复 5 层问题：product-b 缺 `listScopeByCouponSkuNumbers` 接口、controller 未在实现类重声明 `@RequestBody`/`@PostMapping` 导致静默退化成表单绑定、测试活动误绑两个续班计划、`listRenewalMasterByNumbers` 未传前置课关系导致 `preCourseList` 恒空、course-center 测试后置课的 `calculate_renewal_type` 配置错误。前三处已随 product-server/student-data 提交到 `feature-xuban-pre`；后两处是 product-server 既有代码的通用 bug，修复已提交到本分支但**尚未评估是否要 cherry-pick 到 master**，见 [[changelog]] 与下一步。 |

## 下一步

1. 上线时 **product-c 先于 cart**（cart 启动即依赖其新接口）。前端 `userId` 改造已完成。
2. 造售罄券（建议把小库存券如 `579394614104993792` 买满），验证 B 端不可选和 promotion 保存拦截。
3. 造 `capacity>0 && signUpCount>=capacity` 的班级，验证满班拦截，并回归 `capacity=-1` 放行。
4. 复验 `holdLimit=0` 返回“不限”文案。
5. 造「同一学员 + 同一学年学期 + 订金班与券并存」的数据，验证取并集与退券只回落券那部分（T-39，方案见 [[verify]]）。
6. 造两张支付时间不同的券，验证 `presaleOrderTime` 取最新（T-38）；并找马胜确认原「取最早」是否另有上下文。
7. 补 order/cart 下单算价等未覆盖的自动化测试。
8. 下单验证前，先把本需求服务发布到 `test` 泳道（当前 `test` 无本需求代码，接口 404）。
9. 上线前完成 DDL、Apollo、代课权限，并把三处反射桥开关显式设为 `false`。
10. 找马胜确认 student-data 侧的一处调用签名改动（`PreOrderActivityCouponAclServiceImpl` 改传裸 `List<Long>`）无异议。
11. 评估 `RenewalServiceImpl#listRenewalMasterByNumbers` 补前置课关系、`PreOrderCouponFeignController` 补 `@RequestBody`
   这两处修复要不要从 `feature-xuban-pre` 单独 cherry-pick 到 master（是通用 bug，不止本需求受影响）。
12. ~~排查是否还有其它测试活动误绑了多个续班计划~~ —— 2026-09-17 订正：**一个活动绑多个续班计划是合法数据形态**，
   不是误绑（线下实测 11 个活动如此，最多绑 3 个）。代码已改为每个计划各出一条，不再只认首个，见 [[changelog]]。

## 待确认

- ~~PRD 的“每个膨胀券只能用于一个预报名活动”与当前“允许跨活动使用”冲突~~ —— 2026-09-16 已确认：
  PRD 只是那么写，**设计上有意支持跨活动复用**，唯一键保持不变，不实现该限制。
- 一个前置班级可脱离续班计划配置时，如何保证只属于一个续班计划。
  （注：活动侧「一活动多计划」已确认合法并支持，与此条是两件事。）
- 新续班计划活动与老非续班计划活动并存时是否取并集，等待马胜确认。
- `showDiscountAmount` 的膨胀券展示口径。
- 膨胀券专属背景图和 reportCode 最终值。
- promotion 按 `renewalNumber` 查询活动的正式入口。
- 历史预报名活动统一刷成订金班预报名，待上线后由马胜处理。

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| `/Users/gaotu/IdeaProjects/JavaProject/student-center` | `feature-xuban-pre` | `PreOrderCouponController#listCoupon`、`PreOrderCouponBiz#listCoupon`、`PreOrderCouponScopeAclService` |
| `/Users/gaotu/IdeaProjects/JavaProject/product-server` | `feature-xuban-pre` | `PreOrderCouponIntersectService`、`PreOrderDisplayableCouponService`、`PreOrderActivityCouponScopeService` |
| `/Users/gaotu/IdeaProjects/JavaProject/promotion` | `feature-xuban-pre` | `PreOrderActivityService`、`PreOrderCouponEnricher`、`PreOrderCouponScopeRemoteService` |
| `/Users/gaotu/IdeaProjects/JavaProject/promotion-management` | `feature-xuban-pre` | B 端 OES 到 promotion-b 的 DTO 透传层 |
| `/Users/gaotu/IdeaProjects/JavaProject/cart` | `feature-xuban-pre` | `RegistrationService#preRegistration`、`PreRegistrationCouponAssembler` |
| ~~`/Users/gaotu/IdeaProjects/JavaProject/order`~~ | `feature-xuban-pre` | 膨胀券加购与购物车总价；**不在本期范围**，归订单团队 |
| `/Users/gaotu/IdeaProjects/JavaProject/promotion-app` | `feature-xuban-pre` | 仅 spec，本期不改代码 |

## 上线影响面

| 配置项 | 当前要求 |
|---|---|
| MySQL DDL | ①新建 `renewal_pre_order_activity_coupon_scope`；`pre_order_activity_product` 不加列。<br>②**`questionnaire_inspect` 新增 `activity_type`**（`int NULL DEFAULT 1`，**必须可空**——`insertSelective` 对 null 字段跳过写入，声明 NOT NULL 会在漏设值时报错，注释「预报名活动类型:1订金班 2膨胀券」）——膨胀券形式下 `pre_course_number` 存的是**后置产品号**，与订金班同表不同语义，靠该列区分。test 工单 **8048** 已提交待发布，**上线前 PROD 需另提**；<br>⚠️ **该列未建时预警任务写入会失败**，代码与 DDL 必须同步上线 |
| Apollo | 配置商品类型、入口内容、C 端样式和 B/C 状态白名单；明细见 [[verify]] |
| 代课权限 | 登记 `/renewal/pre/coupon/list`、`/renewal/pre/couponScope/list` |
| 反射桥 | promotion/cart/product-server 的 `AclServiceCompareController.enabled=false` |
| ~~前端改造~~ | ⚠️ **2026-09-16 下午需求回退**：B 端 `/renewal/pre/coupon/list` **已移除 `userId`**，前端上午按「必填」做的改造现在不需要了。服务端忽略该字段，前端传了也不报错，但建议清理。C 端落地页不受影响（仍是学员级，userId 由 cart 内部传给 product-c） |
| **jar 依赖** | cart 依赖 `product-server-client:1.5.4-SNAPSHOT`（已发 Nexus，含 `/c/renewMaster/listDisplayableCoupons`）。提测前定版发 RELEASE 并同步改 cart pom |
| **发布顺序** | product-c 必须**先于** cart 上线：cart 启动即依赖该接口，否则 C 端膨胀券落地页拿不到范围。product-b 服务 B 端，两者是不同部署单元 |
| MQ | 券订单消息由订单团队负责 |
| ES | student-data 写入由马胜负责 |

## 必须知道的判据

- promotion 有 `promotion-b` 和 `promotion-c` 两个部署；改 C 端链路时两个都要发布，cart 调用的是 promotion-c。
- promotion 对外 FastJson 使用 SnakeCase；调 coupon-a 必须通过 `CamelExpandCouponQueryRequest` 保证请求字段为 camelCase。
- student-center 调 product-server 使用服务名 `PRODUCT-B` 和 `ProductInterceptorFeignConfig`；返回 `data:[{}]` 通常表示字段名/解码器不匹配。
- promotion 不落券名称、金额和状态；这些字段由 `PreOrderCouponEnricher` 实时补齐。范围权威数据在 product-server。
- 范围查询失败不降级为空或全量，直接抛业务异常，避免误判和越权展示。
- OES 的已售/总量来自活动缓存；判断真实售罄与状态以 coupon-a 返回为准。
- 雪花 ID 按字符串传递，避免 JavaScript 精度截断。
- `traffic-env` 必须带连字符；验证镜像前先确认目标服务 eureka UP。
