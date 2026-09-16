---
title: 续班预报名使用膨胀券 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

> 只保留仍能解释当前设计的决定。最终口径以 README/apis/verify/tasks 为准。

## 2026-09-16 · 膨胀券预警口径订正为「计划级后置产品」+ 邮件加后置产品列

**口径（用户 2026-09-16 确认）**：
- 订金班：**维持原逻辑** —— 前置产品年级 × 活动商品年级，匹配不到标记未绑定。
- 膨胀券：**后置产品**的年级学科 × 券可用范围的年级学科；**年级学科都相同才算匹配**；
  两边各有多个时，存在相同的对即算匹配。范围是**当前续班计划的所有后置产品**。

**三处改动**（product-server）：

1. **修笛卡尔积误判**（`PreOrderCouponIntersectService`）——原实现把后置课压平成
   `postGrades` / `postSubjects` 两个独立集合再分别 `contains`，会把**跨课程**的年级与学科
   错误组合。例：后置课为「六年级·数学」+「初一·英语」，一张「六年级·英语」券会被误判命中。
   改为 `collectGradeSubjectPairs` 按**单门课程**收集「年级+学科」对。
   ⚠️ 当前测试数据三门后置课**恰好都是六年级**，掩盖了该缺陷。

2. **预警改计划级**（`InspectService#preRegistrationInspectByCoupon`）——原实现逐门前置课
   调 `intersect`（券视角：有没有券可卖）。改为先调新增的
   `listUncoveredPostPairs`（产品视角：哪些后置产品没被券覆盖）按计划整体算出未覆盖集合，
   再归位到前置课行。全部覆盖时清掉存量预警。

3. **邮件加两列**（`sendPreRegistration`）——表头与数据行增加【后置产品ID、后置产品名称】，
   **仅膨胀券形式填值，订金班留空**。提醒时间与提醒人范围不变。问卷预警邮件不受影响。

**表结构不动**：`questionnaire_inspect` 仍只存 `preCourseNumber`，后置产品按前置课实时反查，不落库。

## 2026-09-16 · 【待开始】活动放开修改开始时间

**背景**：B 端编辑预报名活动（`/promotionManagement/preOrderActivity/edit`）时，
【待开始】状态报「当前活动状态为[待开始]，只允许更新结束时间，不能修改其他字段」。
造券验证时经常需要把开始时间往前挪让活动立刻生效，卡在这条校验上。

**决定**：**只给【待开始】放开 `beginTime`**，【发布中】/【进行中】维持原样（仍只能改结束时间）。

**为什么只放开待开始**：活动还没开跑，改开始时间不影响任何已发生的业务；
而【进行中】已经产生预报名数据，回改开始时间会让统计口径失真。

**改动**（promotion，2 个文件）：
- `PreOrderActivityStatusEnum#canEditBeginTime`：新增，仅 `WAIT_START` 返回 true。
- `PreOrderActivityService`：
  - `hasNonEndTimeFieldChanges` 增加状态入参，待开始时 `beginTime` 不再算「其它字段」；
  - `buildUpdateActivityBO` 非全字段分支落 `beginTime`（**否则只是放过校验但存不进库**）；
  - `onlyEditEndTime` 放开 `endTime` 必填（待开始且只改开始时间时可不传），
    并校验开始时间早于结束时间（`endTime` 没传则取库里现值比较）；
  - 报错文案按状态动态化：待开始显示「只允许更新开始时间和结束时间」。

⚠️ **校验与落库是两处，必须一起改** —— 只改 `hasNonEndTimeFieldChanges` 会出现
「接口返回成功但开始时间没变」的静默失败。

## 2026-09-16

- **券匹配口径从「三者交集」订正为「两者匹配 + 学员维度收窄」**，依据 PRD
  （`N58DwzUDoi3sK3k1nCqcPOBMn3d`「续班服务-膨胀券推荐逻辑」）与产品流程图。两处改动：

  1. **删掉前置学科过滤**（`PreOrderCouponIntersectService`）。PRD 三处（发链接 / B 端下单弹窗 /
     C 端落地页）的匹配句都只有「用膨胀券的适用年级学科，**和后置续班产品的年级学科做匹配**」两者；
     同段那句「根据【在读班级学科、续班班级年级学科、预报名活动膨胀券年级学科】确定范围」
     是在**列举链路涉及的数据**，不是三重过滤条件——流程图里前置课程为白色不参与匹配，
     只做「定位续班计划」和「串到后置课程」的中转，参与匹配的是券范围与后置课程（绿色）。
     原实现多了一层 `preSubjects.contains(subjectCode)`，会在**扩科**场景漏券：
     学员在读数学、后置含英语、活动配了英语券时该券被滤掉，而扩科正是膨胀券的主要用途。
     一并删掉 `preSubjects.isEmpty()` 的早返回（前置既不参与匹配，它为空就不该让结果清零）；
     `preSubjects`/`preGrades` 保留计算与返回，仅作排查观测值。

  2. **券范围由「计划级」改为「学员级」**。原口径取续班计划配置的**全部**前置课程求交，
     同计划下所有学员看到的券一致；PRD 与流程图要求起点是「**当前在读班**」。
     现改为：计划配置的全部前置课程作**候选池** → 用花名册筛出该学员**真正在读**的那几门 →
     以此为起点反查后置课程。`/renewal/pre/coupon/list` 因此**新增必填入参 `userId`**。

     **收窄边界（2026-09-16 确认）**：取的是「该学员在**当前续班计划的前置班级**里的全部在读班」，
     **不是**该学员全局的在读班。两点含义：(1) 候选池必须先由计划的前置课程限定，
     下游返回的计划外课程要剔除，否则会串到该学员在其它续班计划/学年下的班级，推出不该给的券；
     (2) 取的是计划前置课程下该学员**全部**在读班，不只是「当前点进来的那一个班」——
     产品流程图里「当前在读班」与「其他在读班级」两条线最终汇入同一个后置课程集合。

- **在读数据源选花名册（clazz-distribution），不用 student-data 的
  `dws_fuwu_clazz_user_presale_subject`**。该表有两个硬伤：(1) `is_del=0` 不等于在读——
  学员不在班时 `PresaleSubjectServiceImpl#getPresaleRecords` 仍会插 `clazzNumber=0` 的
  「辅助预报名记录」，`isDel` 同为 false；(2) 该表只在学员**已进后置班**时才落行，
  而券推荐的目标人群恰恰是「在读前置班、**还没买**后置」的学员，用它筛会把目标人群整体漏掉。
  改调 `ClazzDistSubclazzStudentService#listSubclazzStudentByCourseNumbersAndUserId`——
  正是 student-data 自己筛在读时用的那个接口，实时权威、无 MQ 延迟与补数偏差。
  product-server **已依赖** `clazz-distribution-server-client`，故 student-data **一行未改**、不必发包。
  在读状态取 `ACTIVE/INACTIVE/HOLD` 三态，与 student-data `SubclazzStudentStatusEnum#getAllStatus()` 对齐。

- **学员无在读前置班时返回空列表，不退化为计划级**（2026-09-16 产品确认）。
  同理 student-center 侧传了 `renewMasterNumber` 却缺 `userId` 时直接空页，
  避免"少传一个参数就多推一批不该给该学员的券"。

- **预警链路（`InspectService`）不加学员维度**：巡检场景没有单个学员上下文，
  PRD 规定预警按「前置班级 + 后置班级」维度统计。它仍直接调 `intersect`，不经过
  `PreOrderDisplayableCouponService`，故只受「删前置过滤」影响（与 PRD 的
  「膨胀券预警逻辑：后置产品的年级学科与活动膨胀券的年级学科匹配」一致）。

- **打通预报名科目与看板取数，推翻「等离线跑批」的旧结论**。原记「6 条用例卡在 ES 索引
  `ads_large_subclazz_user_index` 无数据、无写入路径、需等离线或找马胜灌数」——三条都不成立：
  索引本就有百万级文档；写入路径就在本仓库（`backDwsPresaleHandler` 的 `refresh(...)` 同时写
  MySQL 与 ES）；跑一次回溯 job 即可。看板 job 5900 的真正卡点是**学员 `canRenewal=0`**——
  该 job 分两段查**不同索引**（① `subclazz_search` 查辅导班、② `ads_large_subclazz_user_index`
  按 `canRenewal ∈ [1,2,8]` 聚合学员），新造学员默认不可续被第②段滤空，
  于是 `handleCode=200` 但不打 `Inserting batch of...` 日志、快照表零写入。
  `_update_by_query` 把 26 条改为可续后，快照表即出数（26 可续 / 7 已预报名，与 ES
  `presaleStatus=1` 的 7 条自洽）。完整步骤与踩坑见 [[verify]]。
  排查中两处教训已记档：**代码里 `largeSubclazzUserIndex` 常量在该方法未被使用**，
  照它查索引会得出完全错误的结论；**雪花 ID 传数字会被 JSON 精度截断**导致误判「数据不存在」。

- **⚠️ 发现 cart 的 C 端是另一套近似实现，本轮未改，需单独决策**：
  `RegistrationService#listPostClazzGrades` 取的是**续班计划自身的目标年级**
  (`RenewalMasterDTO#getCourseGradeList`)，而不是「前置班映射到的后置班级」年级，
  方法上原有 TODO 已写明这是近似（「可能比严格口径宽，表现为多展示券，不会漏展示」）。
  匹配动作本身（`PreRegistrationCouponAssembler#assembleOne` 按年级+学科成对判定）是对的，
  **错的是喂给它的原料**。因此 C 端目前既没有学员维度、也没有真正的后置班级年级。
  要对齐 B 端口径，需让 cart 改调 product-server 的 `listDisplayableByRenewalPlan`；
  但 cart 调 product 走的是 `clientv4` jar（`RenewalMasterFeignService`）而非本地 feign 接口，
  新增方法要发 jar 版本，改动比 B 端大，故拆出单独评估。

- **「每个膨胀券只能用在一个预报名活动中」不实现**：PRD 有这句且给了错误文案，
  但设计上有意支持跨活动复用，唯一键 `uk_act_grade_subject(activity_number, grade_code, subject_code)`
  保持不变（2026-09-16 用户确认：「prd 只是这么说，设计上考虑多个」）。

## 2026-09-15

- **`presaleOrderTime` 口径由「取最早」订正为「取最新」**，依据需求《大班课字段及数据指标》
  「续班服务-花名册」第 75 行：「如果预报名多个班级，取最新下单」「如果下单多个膨胀券，取最新下单」
  「两种方式都配置，取最新时间」。原实现是**有意**取最早（注释写「语义上取学员首次预报名下单的时间」），
  与需求相反。共改 6 处 `min → max`，分布在 4 个文件——增量链路与全量(回溯)链路、大班与小班都必须同步改，
  只改一边会让 ES 值在两条链路之间来回跳：
  `PresaleSubjectServiceImpl#calcPresaleOrderTime`、`PresaleSubjectDataQueryServiceV2#getPresaleOrderTime`、
  `SmallPresaleSubjectServiceImpl#getPresaleOrderTime`、`SmallPresaleStatusDataQueryServiceV2#getPresaleOrderTime`。
  `RenewalOrderTimeQueryService#getLatestOrderTime` 未动（内部本就是 `max`）。4 个钉住旧口径的单测同步改名并翻转期望值。
  **存量数据不会自动纠正**，需跑回溯才会刷成新口径；当前券表仅 2 个学员且无跨形态并存数据，实际无存量待刷。
  待与马胜确认原「取最早」是否另有未写进注释的上下文。
- **发现「取并集」规则零数据覆盖**：券表与订金班表按「学员+学年+学期」交集为 0 行，
  这条需求规则从未被真实数据走过——也是上面口径分歧长期未暴露的原因。造数方案记入 [[verify]]。
- `listScopeByCouponSkuNumbers` 入参最终定为裸 `List<Long>`，不用包装 DTO：根因是 controller 用
  `implements XxxFeignClient` 复用接口方法时必须在实现类自己的方法上重声明 `@RequestBody`/`@PostMapping`，
  Spring 不从接口继承参数注解，漏了会静默退化成表单绑定；此前怀疑的 FastJson/JaCoCo 冲突是误诊，见 [[apis]]。
- 一个预报名活动只应绑定一个续班计划：`578842182125903872` 曾被误绑两个，已删除无效的那个（详见 [[verify]]）。
- `RenewalServiceImpl#listRenewalMasterByNumbers` 遗漏前置课关系、course-center 的 `calculate_renewal_type`
  测试值配错，两处都是既有代码/数据问题而非本需求引入，顺手修复，是否合并到 master 待评估（见 README 下一步）。

## 2026-09-14

- 复核可用券基线：`total=40`，全部 `couponStatus=1` + `saleStatus=2` + `selectable=true`，
  常用 5 张记入 [[verify]]。当前**无售罄券**，T-33 只能靠造数或买满小库存券解锁。
- 确认下单所需的 `test` 泳道运行 master 镜像，不含本需求代码（接口 404 / 反射找不到实现类）。
  券数据在 coupon-a 跨泳道共享，缺的是代码，下单验证前必须先发版到 `test`。

- B/C 端默认只展示 `couponStatus=1` 且 `saleStatus=2` 的券；两个白名单均支持 Apollo 配置，状态为空不展示。
- coupon-a 已支持 `couponStatuses`/`saleStatuses` 服务端过滤，student-center 直接透传条件并删除本地二次过滤，保证分页 `total` 与列表一致。
- 采用服务端过滤，因为分页后本地过滤会导致总数和页内容不一致。

## 2026-09-11

- 券有两个正交状态：`couponStatus` 表示券本身状态，`saleStatus` 表示商品售卖状态；展示必须同时满足两个白名单。
- 建券人通过 `creatorEmployeeId -> accountId -> CAS displayName` 两跳批量转换，查不到时保留工号。
- 活动保存增加售罄券和满班课程服务端校验，避免只依赖前端不可选状态。

## 2026-09-10

- B 端膨胀券 tab 始终展示；`renewMasterNumber` 只控制三者交集范围过滤，没有可展示券时返回空列表。
- 三者交集统一由 product-server 的 `PreOrderCouponIntersectService` 计算，其他服务只消费结果。
- promotion 的 B/C 两条读取链路都必须补齐券字段与 scopes，跨服务返回使用扁平行和 `RestTraceResponse<T>` 信封。

## 2026-09-09

- 券信息实时读取 coupon-a，不落业务库、不使用 mock；`couponStatusDesc` 由本地枚举维护。
- 券范围表由 promotion-b 在事务内调用 product-b 的专用接口写入，Feign 失败回滚活动，避免循环调用。
- 范围唯一键按活动级 `(activity_number, grade_code, subject_code)`，允许同一张券跨活动使用。

## 2026-09-08

- 膨胀券商品类型定为 `8014`；券不参与满赠。
- 落地页继续使用 `/preSignUp`，不按活动形式拆分 path。
- order 侧范围限定为加购与购物车总价；订单后续链路和 student-data 收数由对应团队负责。
