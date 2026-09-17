---
title: 续班预报名使用膨胀券 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

> 只保留仍能解释当前设计的决定。最终口径以 README/apis/verify/tasks 为准。

## 2026-09-17 · 花名册回溯默认带上膨胀券，券清单按班级推导

**背景**：花名册回溯（`backDwsPresaleHandler`/`backSmallDwsPresaleHandler`）原先券部分是**选做**的：
必须手填 `couponSkuNumbers` 才跑，不填就只回溯订金班。运维想给一批班补券数据得先自己枚举券商品号。

**决定**：券回溯**默认开启**，`couponSkuNumbers` 从「开关」降为**可选过滤器**。
不传时按「**班级 → 续班计划 → 计划下可展示券**」自动推导券清单。

**为什么不用「按 userId 查该学员全部订单项」**：order 侧只有「学员 ∩ 商品」的收窄查询，
虽然 SDK 有 `listByUserId`，但那要拉全量订单项再内存过滤，且属于动 order 契约。
班级 → 计划 → 券 这条链路上的数据本来就是「这个班该卖哪些券」的权威来源，更准、更省。

**券清单取计划级（不按学员收窄）**：`listDisplayableCoupons` 的 `userId` 传了会退化成
「学员在读前置课命中的券」，而花名册回溯面对整班，要的是计划能卖的全部券；所以 ACL 方法
`listCouponSkuNumbersByRenewal` 干脆不暴露 userId，避免调用方误传。

**结果语义**：落库与刷花名册是「**订金班 + 券**」的并集 —— 并集本身由
`PresaleSubjectServiceImpl#refreshByUserTermYear` 既有合流逻辑完成，本次不改合流。

**公共骨架**：两个 job 流程一致、只差「订金班那半用哪个服务」，抽到 `PresaleBackfillHelper`，
以回调传入 `dealSubclazzStudent`，避免两套实现日后走偏。

**兼容**：老数组格式 `[123]` 仍可解析，但语义从「只回溯订金班」变为「默认带上券」；
要纯订金班回溯用 `{"clazzNumbers":[123],"backCoupon":false}`。

**提交**：student-data `feature-xuban-pre` `cd56fb484`。

## 2026-09-17 · 膨胀券后置课改取「续班关系」，不再复用订金班的预报名关系

**口径**：`CourseRenewalRelationMapVO#calculateRenewalType` 中 **1 = 续班关系（计算可续）、
2 = 预报名关系（不计算可续）**。膨胀券预报名要匹配的是「学员真正能续的后置产品」，因此取 **1**；
原实现复用了订金班的 `mapPostCourseByNumber`（筛 **2**），拿到的是学员并不可续的后置课。

**订金班口径不变**：`mapPostCourseByNumber`（=2）一行未动，订金班仍按预报名关系取后置课。
两条链路口径不同，**不可互相替代或合并**。

| 仓库 | 改动 |
|---|---|
| student-data | 新增 `CourseNotNormalAclService#mapRenewalPostCourseByNumber`（筛 =1），`PresaleCouponServiceImpl` 的取数点切过去 |
| product-server | `PreOrderCouponIntersectService#listPostCourseNumbers` 原先**完全没按 `calculateRenewalType` 过滤**，续班关系与预报名关系混取，券列表里会多出学员其实续不了的券；已补上只取 =1 |

**product-server 这一处是三端同源实现**：`PreOrderCouponIntersectService` 同时服务
「花名册发链接 / B 端下单弹窗 / C 端落地页」的交集口径与预警链路，改一处三处同时生效。

**大班小班不需要分别改**：`buildRecords` 取后置课时不做班型过滤（券本身不区分大小班），
班型分流发生在其后的 `refresh` 阶段，由 `PresaleCouponClazzTypeFilter` 按前置课的
`arrangeModeType` 决定刷大班还是小班字段，一处改动对两者同时生效。

**提交**：student-data `feature-xuban-pre` `74c6e6b78`；product-server `feature-xuban-pre` `fe076a536`，
同一改动 cherry-pick 到 `feature-xuban-pre-expand-coupon` `c1937337e`。

## 2026-09-17 · 券范围放开「一券多活动 / 一活动多计划」，并订正两处环境记录

**背景**：券回溯只落到一个活动/一个计划，是上游 `listScopesByCoupons` 的分组粒度不够。
本轮按 **(券, 活动, 续班计划) 三元组**返回，两处收敛全部打开。

| 层 | 原写法 | 问题 |
|---|---|---|
| 券 → 活动 | 按券单级分组，取 `couponRows.get(0).getActivityNumber()` | 首行落在哪个活动取决于 DB 返回顺序；且 `scopes` 装了该券**全部**行，年级学科跨活动串味 |
| 活动 → 计划 | `resolveRenewalNumbers` 返回 `Map<Long, Long>`，`result.containsKey` 只留第一条 | **一个活动绑多个续班计划是合法数据形态**，被丢的计划永远收不到该券的预报名数据 |

**「一活动多计划」不是脏数据**——线下 `renewal_link_activity` 实测有 **11 个** `is_del=0`
的活动绑了多条流程（最多 3 个）。此前 README 第 12 条把它当作「误绑、要排查清理」是判断错了，
应按合法形态支持。DAO 同时补 `order by coupon_sku_number, activity_number, id` 让返回顺序可复现。

**student-data 侧不用改逻辑**：唯一键 `uk_user_clazz_course_sku(user_id, clazz_number,
course_number, coupon_sku_number)` 里**既无活动也无计划维度**，原 `mergeByUniqueKey` 按
`clazzNumber_courseNumber` 合并已同时覆盖两条撞键路径，年级学科取并集的口径不变；
只补了注释与日志（新增 `keptRenewalNumber`/`droppedRenewalNumber`，便于排查被合并掉的是哪个计划）。

**接口契约未变**：`PreOrderCouponScopeFeignVO` 字段与类型一个没动，只是 list 里可能多出元素；
改的 `resolveRenewalNumbers` 是 `private` 方法。

### 两处环境记录订正（原记录与实际不符）

- **`renewal.send.test` 并未按记录复位**：verify.md 记「2026-09-16 已改回 false」，
  实际 Apollo 上已发布值与草稿**一直是 `true`**。2026-09-17 09:48 已真正改回 `false` 并发布
  （release `20260917094831-release`）。**教训：改完 Apollo 要重新读一次已发布值确认，别凭记忆记「已改回」。**
- **计划 `578668076965308416` 的 `is_test_data` 已是 `0`**（2026-09-16 20:09:51 改的，
  就在 20:12 生成预警之前），因此它**不受 `renewal.send.test` 影响、照常发邮件**。
  verify.md 原写的「该计划是 `is_test_data=1`，验证前要打开开关」已过期。

### 分支与部署

`feature-xuban-pre` 合入 `feature-xuban-pre-expand-coupon`（product-server）。
两分支各有一条同名的「按(券,活动)二级分组」提交（`b59343f4f` / `56113cc14`，同一改动提交了两次），
合并时在该方法体冲突，取 `feature-xuban-pre` 一侧（多计划版本是单计划版本的超集）。
**student-data 没有 `-expand-coupon` 分支**，仍用 `feature-xuban-pre`，两服务部署分支不同。

## 2026-09-16 · 预警落库改后置产品维度：4 处读路径 + 2 个独立缺陷

**口径定稿**：膨胀券预警 = **一个未被券覆盖的后置产品一条**（按后置产品号去重）。
订金班逻辑与展示口径**完全不变**，所有改动都在 `if (expandCoupon)` 分支内。

**为什么不能按前置课生成**：前置与后置是**多对多**——实测该计划 3 门前置各自都产出同样
3 门后置。按前置铺开会把「缺 1 个后置产品」放大成 N 条重复，且每条都指不明缺的是哪个。

**落库**：膨胀券形式下 `pre_course_number` 存**后置产品号**、`pre_course_name` 存后置产品名；
新增 `activity_type`（1 订金班 / 2 膨胀券）区分两种语义。**不加后置产品列**——
按前置反查后置是实时的，落库反而会在续班关系变更后过期。

### ⚠️ 改落库维度必然带出读路径连锁失效

规律：**所有「把库里的值当前置课程号用」的地方都会失效**（库里已是后置产品号，反查必落空）。
本轮 4 处全部命中，逐一修复并实测：

| # | 位置 | 症状 | 隐蔽度 |
|---|---|---|---|
| 1 | 列表 `postProductId/Name` | 两列恒空 | 低 |
| 2 | 列表 `inspectStatus` | `resolveCouponInspectStatus` 求交拿不到结果，**真实预警全显示「已处理」，运营一条都看不见** | **高**（接口正常返回、数据也在，只是状态全错） |
| 3 | 邮件后置两列 | 同 1 | 低 |
| 4 | `checkRestoreInspect` | 后置号传给期望前置号的 `intersect`，结果恒空 → **校验永远不触发**，已配好券的也能恢复预警 | **最高**（返回成功、状态也改了，只是本该拦的没拦） |

1/2/3 改为**直接取库值**，`resolveCouponInspectStatus` 删除；
4 改为按「该后置产品是否仍在 `listUncoveredPostPairs` 未覆盖集合里」判断，与生成口径同源。

### 另外两个独立缺陷

- **`status` 语义判错导致「标记为已处理」被误拦**：`QuestionInspectCourseReq.status` 是
  **目标 `inspect_status`**（0 预警中 / 1 已处理），由 DAO 直接写库；
  而 DTO 注释写的是「操作类型：0关闭 1开启」——**注释是错的**，照它理解就会把
  `RESTORE_INSPECT_STATUS` 取成 1，正好与「标记为已处理」传的 `status=1` 撞上，
  运营点击必然弹「已配置预报名活动，无需预警」且改不动状态。已改为 0。
- **邮件表头按形式动态生成**：膨胀券只出后置两列（前置两列会与后置取到同一个值、
  四列两两重复且列名与内容不符），订金班保持前置两列；`updateTime` 为 null 时回落空串并格式化。

### 实测（product-b `srzzv`，计划 `578668076965308416` / 活动 `579790752417087488`）

活动只配了 `(16,1)` 数学，后置有数学/英语/语文 → 精确生成 **2 条**（英语、语文），
非造数、是真实漏配。列表两列有值、`inspectStatus=0`；
数学恢复预警**被拦**、语文放行、英语标记已处理成功；邮件 2 行、时间正常。

## 2026-09-16 · OES 选品弹窗复用下单接口，去掉服务端展示白名单

- **PRD 追加需求**：OES 创建/编辑活动的「添加商品」选品弹窗需要筛选/展示「使用状态」「审核中/使用中/已失效」
  「售卖状态」「售卖中/停止售卖」，且只有【使用中且售卖中】可勾选，其余状态可查看不可选。
- **用户明确指出接口就是 T-36 的 `/renewal/pre/coupon/list`**：OES 弹窗与老师下单弹窗复用同一个
  `PreOrderCouponController#listCoupon`，不新建接口。这否定了之前两轮代码排查往 promotion-management/
  product-server（`spuSearch` 等）方向找"独立选品接口"的猜测——那条路线根本不对，本需求不涉及那些仓库。
- **白名单去掉，且不传即全量**（而不是保留默认值只放开显式覆盖）：原 Apollo 白名单
  （`displayCouponStatusConfig`/`displaySaleStatusConfig`，默认【使用中】【售卖中】）是 2026-09-14 加的
  安全网，专为老师下单弹窗设计；OES 弹窗要能查看【审核中/已失效/停止售卖】，若保留"调用方传的状态 ∩ 白名单"
  会把这类搜索直接拦掉。用户进一步拍板：**不传状态筛选就是全量**（不再由服务端补默认值），默认勾选
  【使用中】【售卖中】的 UX 交给前端实现，服务端不兜底——这样两个调用方（OES/老师弹窗）用同一套接口语义
  一致，不用按 `identification` 区分身份加特殊分支。
- **可选性判定分三层**，都不靠"从结果里删行"（那是 2026-09-14 之前的做法，已废弃）：
  ① `PreOrderCouponWrapper` 按 `couponStatus` 算（既有）；② 新增 `revokeSelectableWhenNotOnSaleInUse`
  按 `saleStatus` 算；③ 既有的售罄判定。三层任一不满足则 `selectable=false`，行仍然展示。
- **一并确认修复**：`PreOrderCouponAclServiceImpl#buildQuery` 里记录的"`saleStatuses` 电商服务端过滤
  未生效"已知限制（coupon-c `CouponExpandConfigRepositoryImpl#normalize()` 漏拷字段），已由电商修复，
  `test-gtbg-dev-3` 实测确认筛选真实生效。
- 实现：student-center `49a2a9ab7`。改动与实测数据见 [[apis]]「T-43 落地」。

## 2026-09-16 · B 端券范围改回计划级，C 端保持学员级

- **产品当日下午调整**：EES B 端下单弹窗的膨胀券范围**只和续班计划有关、与学员在读无关**。
  理由是老师在花名册里看的是**整个计划**能卖哪些券，按某个学员收窄会让老师看不全；
  而 C 端学员只应看到自己在读班对应的那部分。**两端口径从此不同，这是产品定的，不是 bug。**

  | 端 | 接口 | 口径 | `userId` |
  |---|---|---|---|
  | B 端 | `/renewal/pre/coupon/list` | 计划级 | 已移除 |
  | C 端 | `/c/renewMaster/listDisplayableCoupons` | 学员级 | 必传 |

- **实现没有拆两套**：`PreOrderDisplayableCouponService` 的 `userId` 改为**可选语义**——
  传了有效值走学员级（花名册收窄），不传 / null / ≤0 走计划级（直接用计划配置的全部前置课程，
  不查花名册）；另加单参重载 `listDisplayableCoupons(planNumber)`，B 端不必传裸 `null`。
  `narrowToInClazzCourses` **保留**给 C 端，未删。B 端链路的 `userId` 彻底移除（product-b 请求 DTO、
  controller、student-center 的 Request/ACL 接口与实现、`PreOrderCouponBiz` 的缺参守卫）。
  C 端（`product-server-c`、`product-server-client`、cart）**一个文件未动**。
  **匹配口径本身未变**：券范围 × 后置年级学科整对判定，前置班不参与（上午修扩科漏券那处保留）。

- **实测**（`test-gtbg-dev-3`，product-b `9f632436f` / student-center `0d85dc9b6`）：
  B 端不传 `userId` → `total=2`；传不存在的 `userId=9999999999` → **结果完全相同**，证明已忽略该字段；
  product-b 单参直调返回券、双参+不存在学员返回 `[]`（学员级收窄仍在）；
  C 端 `preRegistration` 正常返回 2 张券，**未被连累**。

- **踩坑**：验证时先拿到 B 端 `total=0` 差点判失败，实为 student-center 新 pod 尚在
  `status=Waiting / eurekaStatus=None`，请求打到**旧镜像**（旧代码 `userId` 必填，不传即空页）。
  **发版后立刻验证前必须确认 eureka UP**，`pipeline SUCCESS` 不是判据。

- **测试数据变更**：计划 `578668076965308416` 当前绑的活动已换成 `579790991194619904`
  （券：Q8 六年级数学+英语、全链路测试 六年级语文），不再是案系列 `579607430990692352`。
  非本次改动所致，归档中旧的券清单基线已过期。


## 2026-09-16 · 预警按后置产品去重落库，读路径三处连带修复

**口径**：膨胀券预警 = 一个未被券覆盖的**后置产品**一条。订金班完全不变。

**落库**：`questionnaire_inspect` 在膨胀券形式下，`pre_course_number` 存的是**后置产品号**、
`pre_course_name` 存后置产品名；新增 `activity_type`（1 订金班 / 2 膨胀券，可空默认 1）区分两种语义。

⚠️ **`activity_type` 必须可空**：`insertSelective` 对 null 字段跳过写入，
声明 NOT NULL 会在漏设值时直接报错。

**改落库必然带出三处读路径修复**——它们都在拿「库里的值」反查其后置，
而库里存的已经是后置产品号，反查恒空：

| 位置 | 症状 |
|---|---|
| 列表 `postProductId/Name` | 两列恒空 |
| 列表 `inspectStatus` | `resolveCouponInspectStatus` 按前置求交拿不到结果，**真实预警全displayed成「已处理」，运营一条都看不见** |
| 邮件后置产品两列 | 同列表，恒空 |

三处统一改为**直接取库值**，`resolveCouponInspectStatus` 已删除。
邮件的形式判断改用行上的 `activity_type`，**不再实时反查活动类型**——
实测同一计划一天内换绑三次活动，实时反查会把历史行判错形式。这是新增该列的主要目的。

**实测**（活动 `579790991194619904`，删掉语文券范围造漏配）：
预警只生成 1 条（语文后置产品），此前按前置铺开会生成 3 条重复；
恢复券范围后重跑，预警清零。

---

## 2026-09-16 · 【待开始】活动放开修改开始时间

**背景**：造券验证时常需把开始时间前移让活动立刻生效，被「只允许更新结束时间」挡住。

**决定**：**只给【待开始】放开 `beginTime`**。活动尚未开始，改开始时间不影响已发生的业务；
【发布中】/【进行中】已产生预报名数据，回改会让统计口径失真，维持原样。

⚠️ **校验与落库是两处，必须一起改**：只改 `hasNonEndTimeFieldChanges` 会出现
「接口返回成功但开始时间没变」的静默失败——`buildUpdateActivityBO` 的 else 分支原本只处理 `endTime`。

**实测**：待开始改开始时间 22:15→22:00 真正落库；待开始改名字被拦且文案为
「只允许更新开始时间和结束时间」；进行中改开始时间仍被拦、文案保持「只允许更新结束时间」。

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
