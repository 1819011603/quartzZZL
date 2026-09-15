---
title: 续班预报名使用膨胀券 · 造数手册
tags: [需求, 验证, 造数]
---

# 造数手册：从零造一条膨胀券预报名链路

> 本节是 `verify.md` 的补充，写**方法**不写死具体 ID——当前有效的测试数据以 `verify.md`「当前测试数据」段为准。
> 读者是下一个要造一条新链路（例如另一个年级/学科组合、或另一条完全独立的验证链路）的人。
> 举例用到的 ID 一律标注「示例」，不代表可复用。

## 0. 造数顺序总览

```
建前置班+学员 → 建后置课程 → 建续班计划 → 绑前置课程 → 配前置→后置续班关系
  → 加续班预报名流程(type=3 + 两节点) → 建膨胀券活动(挂券+配范围) → 发布活动 → 绑活动到 type=4 节点
```

依赖关系是单向的：前面的步骤不成功，后面步骤要么报错、要么"看似成功但数据不生效"（例如续班计划没绑前置课程时，交集接口会直接返回空，不会报错）。**每步都要按下方"怎么验证"自检，不要连续造完最后一起验**，否则出问题很难定位是哪一步。

## 1. 建前置班 + 学员

前置班代表学员当前在读、将来要续报的班级；三者交集里的「前置班学科」就来自这一步。

1. `create_course` 建前置课程：传 `grades`（年级 code）、`subjects`（学科 code，单学科）。拿到 `courseNumber`。
2. `create_clazz` 建班：传 `courseNumber`。拿到 `clazzNumber`。
3. `course_publish` 发布课程、`clazz_publish` 发布班级——不发布后续 `create_clazz`/花名册/下单链路会报"课程未发布，无法建班"或查不到班。
4. 学员进班：`batch_create_order` 下 0 元单（`productType=2`，大班课），`choiceProductList` 传 `productNumber=clazzNumber`（不是 `clazzNumber` 这个字段名）。`payPlanType=0` 免费，`price=0`。
5. 需要几个学科的前置班在读，就重复 1-4 建几个前置班——**学员在几个学科的前置班在读，B 端交集就最多出几张券**（这是三者交集里最容易漏的一环，见第 2 节）。

怎么验证这步成功：
- `course_publish` 成功判据 `data.failList` 为空。
- `batch_create_order` 返回 `isSuccess:true`；响应里的 `orderNumber` 实际是 `pay_number`（字段语义错位），需要真订单号时按 `pay_number` 反查 `gaotu.order_info.order_number`（大班课）。
- 花名册/`list_subclazz_students` 能查到该学员在该班。

## 2. 建后置课程

后置课程代表续报之后要上的课，决定三者交集里的「后置产品年级学科」这一环。

- 同样用 `create_course` + `course_publish`（+ 如需要班级用 `create_clazz`/`clazz_publish`）。
- **后置课程的年级要与前置班一致**（同一个续班计划下，前置/后置一般同年级跨学期），学科按要验证的组合建（如要出数学+英语+语文三个槽位，就建三个学科的后置课程/班级）。
- 记下每个后置课程（或班级）的 `courseNumber`/`clazzNumber`，下一步续班关系要用。

## 3. 建续班计划

`create_renew_master`（Step 1/9）：

- POST `product-b` `/b/renewMaster/create`。
- 成功判据：`code==0`，`data` 即续班计划编号（`renewalMasterNumber`）。
- 记下这个编号，后续 `bind_pre_course`、`add_renew_master_course_relation`、`process/edit`、B/C 端验证接口全部要用它。

## 4. 绑前置课程到续班计划

`bind_pre_course`（Step 4/9），POST `product-b` `/b/renewMaster/bindPreCourse`。

⚠️ **这是覆盖式 SET，不是追加**：调用前先用 `renewmaster_listcoursesbyprecoursenumber`（或等效查询）核对该续班计划**当前**绑定了哪些前置课程，把旧的 + 新的一起拼进 `preCourseNumberList` 传入，否则会把已有绑定冲掉。

```
preCourseNumberList = [旧前置课程号..., 新前置课程号...]
```

成功判据：`code==0`。验证：重新查一遍，确认旧的没丢、新的已加上。

## 5. 配前置→后置续班关系

`add_renew_master_course_relation`（Step 6/9），POST `product-b` `/b/renewMaster/courseRelation/add`。

- `relationCourseNumber`：某一个前置课程号（第 4 步绑过的）。
- `courseNumberList`：这个前置课程对应的后置课程号列表（第 2 步建的）。
- `relationType`：固定 `1`。

**每个前置课程都要单独调一次**（有几个前置课程学科就调几次，各自关联同一批/或对应的后置课程），不会因为绑过一个前置课程就自动带上其它前置课程的关系。

成功判据：`code==0, msg="success！"`。

## 6. 加续班预报名流程（type=3 + 两节点）

`product_b_b_renewal_process_edit`，POST `product-b` `/b/renewal/process/edit`。

- 不传 `number` = 新建流程；传 `number` = 编辑已有流程。
- `nodeConfigs` 配节点：本需求要 `type=3`（续班预报名）流程，下面挂两个节点（配置节点 + 预报名承载节点，具体节点类型/字段以当前 `apifox-openapi.json` 或 `product_b_b_renewal_process_list` 读出的既有流程为准）。
- 建完之后用 `product_b_b_renewal_process_list` 查 `processNumber` 和各节点的 `nodeConfigs[].number`，第 9 步绑活动要用。

成功判据：`code==0`（响应 `data` 为 `Void`）。验证：`process/list` 能查到刚建的流程和两个节点号。

## 7. 建膨胀券活动（挂券 + 配范围）

⚠️ **`promotionmanagement_preorderactivity_edit` 这个 data-agent tool 的 schema 目前缺膨胀券字段**（`scopes`/`couponId`/`couponName`/`skuId`/`buyAmount`），只覆盖了订金班活动那套字段。造膨胀券活动要**直调接口**，不能只用这个 tool 默认 schema：

```
POST https://test-mi.gaotu100.com/promotionManagement/preOrderActivity/editAndPublish
```

关键参数（在 tool 描述已有字段基础上，膨胀券额外要加）：
- `type`：膨胀券活动的活动形式（区别于 `type=1` 订金班；具体取值以现有膨胀券活动详情回显为准，可先 `promotionmanagement_preorderactivity_detail` 读一个现成的膨胀券活动核对字段结构）。
- 每个券挂一条 `scopes` 对应一个「年级+学科」范围，示例结构（来自实测报文）：
  ```json
  {
    "couponId": "<券商品ID即skuNumber>",
    "couponName": "<券名>",
    "skuId": "<券商品ID，同couponId>",
    "buyAmount": <买价，单位分>,
    "scopes": [{"gradeCode": 16, "subjectCode": 1}]
  }
  ```
- `activityStatus` 创建时必须传 `0`（待发布），传 `1` 会报 `code=10240002`。
- `beginTime` 必须严格大于当前时间（建议 `now+5min`），且活动一旦进入"待开始"状态后只能改 `endTime`，改不了 `beginTime`/商品——想改开始时间只能作废重建。

**范围怎么配才能出券**（详见第 8 节三者交集）：`scopes` 的 `gradeCode`/`subjectCode` 要覆盖你想验证的年级学科组合；一个活动内相同的「年级+学科」组合只能配一次（唯一键 `uk_act_grade_subject(activity_number, grade_code, subject_code)`）。

怎么验证这步成功：
- 响应 `data` 返回活动编号（`number`）。
- `promotionmanagement_preorderactivity_detail` 回显能看到券字段（couponId/couponName/金额/scopes）完整。

## 8. 发布活动

`promotionmanagement_preorderactivity_editandpublish` 本身就是"创建并发布"，正常一步到位，成功后活动状态是"待开始"(`2`)，到 `beginTime` 后自动转"进行中"(`3`)。

若活动已经是"进行中"（`3`）要改券配置：`/preOrderActivity/edit` 在 `activity_status=3` 时只允许改结束时间。测试环境要改券，需要先把 `activity_status` 临时改成 `0`，调 `/preOrderActivity/edit`（`beginTime` 必须晚于当前时间），改完再改回 `3` 并还原原时间窗（详见 `verify.md`「进行中的活动怎么改券」）。

验证：`promotionmanagement_preorderactivity_detail` 或 B 端活动列表能看到状态转为"待开始"/"进行中"。

## 9. 绑活动到 type=4 节点

`product_b_b_renewal_preorderactivity_bind`，POST `product-b` `/b/renewal/preOrderActivity/bind`。

- `processNumber`：第 6 步的流程号。
- `nodeNumber`：第 6 步里 `type=4`（预报名承载节点）那个节点的 `number`（用 `process/list` 查出来）。
- `preOrderActivityNumber`：第 7/8 步建好的膨胀券活动号。

成功判据：`code==0`（响应 `data` 为 `String`）。验证：`process/list` 重新查一遍，该节点的 `preOrderActivityNumber` 应等于刚绑的活动号。

到这一步，一条完整链路（前置班 → 续班计划 → 续班关系 → 预报名流程 → 膨胀券活动）就搭完了，可以进入第 11 节复跑验证。

---

## 10. 三者交集口径（最容易造错的地方）

**口径**：前置班学科 ∩ 后置产品年级学科 ∩ 券配置范围，按「年级+学科」成对判定，只在 `product-server` 的 `PreOrderCouponIntersectService#intersect` 计算（唯一同源实现）。

### 10.1 三个集合分别从哪来

| 集合 | 来源 | 由谁决定 |
|---|---|---|
| 前置班学科 `pre_subjects` | 学员当前在读的前置班（第 1 节建的班），按学员实际进了哪些学科的前置班 | 造数时"学员进了几个学科的前置班" |
| 后置产品年级学科 `post_subjects` | 续班计划配置的后置年级/学科（`post_grades`/`post_subjects`，来自第 5 节续班关系） | 续班计划配置 |
| 券配置范围 | 活动 `scopes` 里配的 `(gradeCode, subjectCode)` 对 | 第 7 节建活动时配的 scopes |

三者对同一个「年级+学科」都命中，这张券才会出现在结果里；任一环缺失，这个学科的券就被砍掉。

### 10.2 最容易踩的坑：漏了"前置班学科"这一环

只关注"后置课程学科"和"券范围学科"两者对齐是不够的——**学员实际在读的前置班学科**才是第三个、也是最容易被忽略的过滤条件。

实测证据（三选一保留即可，供理解口径）：同一活动、同一续班计划，只改传入的"前置课程号列表"这一个入参：

| 传入的前置课程 | `pre_subjects` | 出券数 |
|---|---|---|
| 仅数学前置班 | `[1]` | 1 |
| 数学+英语+语文三个前置班课程号 | `[1,4,5]` | 3 |

结论：**学员在几个学科的前置班在读，B 端交集就最多出几张券**。要让某学科的券出现，必须让学员**真实进了该学科的前置班**（第 1 节第 5 步），而不是只在后置课程/券范围上配了这个学科。

### 10.3 造多学科交集的操作要点（复用第 1-5 节即可）

1. 按需要验证的学科数，重复第 1 节，给学员建对应学科的前置班并进班。
2. 第 4 节 `bind_pre_course` 时把新旧前置课程号**合并**传入（覆盖式 SET，见第 4 节警告）。
3. 第 5 节 `add_renew_master_course_relation` 对每个新增的前置课程都单独调一次，关联到对应的后置课程。
4. 第 7 节活动的 `scopes` 补齐对应的「年级+学科」组合。
5. 用 `PreOrderCouponIntersectService#intersect` 反射直调核对：`pre_subjects`/`post_subjects`/`coupon_sku_numbers` 应该都覆盖到目标学科集合，`empty=false`。

### 10.4 年级学科 code 对照

| 年级 | code |
|---|---|
| 三年级 | 13 |
| 五年级 | 15 |
| 六年级 | 16 |

| 学科 | code |
|---|---|
| 数学 | 1 |
| 英语 | 4 |
| 语文 | 5 |
| 物理 | 6 |
| 历史 | 12 |

> 只列举了材料中出现过的年级/学科；其余年级学科 code 造数前先查现有数据或字典接口确认，不要凭经验套用。

### 10.5 B 端与 C 端口径不完全一致（已知差异，非本次造数目标但要知道）

- **B 端**下单页 `PreOrderCouponBiz#listCoupon`（走 `PreOrderCouponIntersectService`）：按"前置班学科 ∩ 后置年级学科 ∩ 券范围"三者过滤，口径与 README 定义一致。
- **C 端**落地页 `RegistrationService#preRegistration`（`PreRegistrationCouponAssembler`）：只按"续班计划的年级学科 ∩ 券范围"两者过滤，**没有前置班学科这一环**，会比 B 端多出券。
- 这是已知口径分歧（产品待确认哪个是目标口径），造数验证时**不要假设两端出券数一定相等**；如果验证 B/C 一致性用例，这条差异本身就是当前的预期失败点，不代表造数造错了。

---

## 11. 已知的坑

| 坑 | 判据 |
|---|---|
| `python3` 用系统自带的，不要用别的版本 | 某些环境装的 `python3`（如 3.14）缺 `jsonschema` 包会导致相关脚本报错；改用 `/usr/bin/python3` 执行 |
| `bind_pre_course` 是覆盖式 SET | 调用前必须先查当前已绑定的前置课程列表，把旧值和新值**合并**后一起传，否则会冲掉已有绑定（见第 4 节） |
| `promotionmanagement_preorderactivity_edit` 这个 data-agent tool 的 schema 缺券字段 | 造膨胀券活动不能只用这个 tool 的默认参数，`scopes`/`couponId`/`couponName`/`skuId`/`buyAmount` 要直调接口手动补上（见第 7 节） |
| `batch_create_order` 这个 tool 的枚举缺 `8014`（膨胀券商品类型） | 膨胀券下单不能直接用 tool 的商品类型枚举选择，需要直调 `order/boss/facade/batch/createOrder.do` 接口，`choiceProductList` 里 `productType` 手动传 `8014` |
| 19 位雪花 ID 一律传字符串 | 传数字会在 JS/反射链路里发生精度截断（例如 `578667318880518144` 被截成 `578667318880518100`），导致查询/交集误判为空，而不是报错——查出"空结果"先怀疑这个，再怀疑业务逻辑 |
| 建班自动生成的辅导班 `assistant_number=0`（没带班老师） | 花名册筛不出该班学员；这类班级如果要在花名册里操作（发链接等），必须先确认 `assistant_number` 非 0，否则误判成"学员没进班" |
| 小学年级建课必须用小学部门参数 | 六年级等小学年级建课要 `schoolDepartment=10` + `departmentIdPaths=["10007722"]`；沿用高中那套（`schoolDepartment=30` + `10000000/10001684/10001689`）会报「部门非法」，且 `create_course` 只返回 `courseNumber:null` 不报错，后续步骤全部空跑 |
| 小班课的课程/班级不在 `gaotu` 库 | 小班课链路的课程与班级落在 **`course_center`** 库（`course_center.course` / `.clazz` / `.course_extension` / `.course_relation_map`），在 `gaotu.course` 里查恒为空——别据此判断「没造出来」 |

### 改带班老师（有坑，实测过）

接口 `POST /distribution-management/subclazz/management/edit`（`b_client: OES`）。

🔥 **只传 `assistantNumber` 会「返回 code:0 但纹丝不动」**。根因在
`SubclazzServiceImpl#constructEditSubclazz`：K12 业务线（`biz_type=1`）走的分支是

```java
if (bizType == BizTypeEnum.PRIMARY_MIDDLE.getCode()) {
    if (Objects.equals(editSubclazzDto.getCourseCategoryId(), CourseCategoryEnums.PUBLIC_COURSE.getCode())) {
        subclazz.setAssistantNumber(editSubclazzDto.getSalesNumber());   // ← 赋的是 salesNumber
    }
}   // 非公开课时 setAssistantNumber 根本不会被调用，字段保持 null → 不落库
```

即 K12 **非公开课**时该字段压根不会被 set。可行的调法是**同时**传
`courseCategoryId=10`（公开课）与 `salesNumber=<老师编号>`：

```bash
curl -s -X POST 'https://test-mi.gaotu100.com/distribution-management/subclazz/management/edit' \
  -H 'Content-Type: application/json;charset=UTF-8' -H 'b_client: OES' -H 'UID: 3217' \
  -H "Cookie: <boss>" -H 'traffic-env: <泳道>' \
  -d '{"number":<辅导班号>,"assistantNumber":<老师编号>,"assistantName":"<姓名>",
       "salesNumber":<老师编号>,"salesName":"<姓名>","courseCategoryId":10,
       "studentCount":50000,"subclazzType":0,"subclazzUsage":0,"autoExtend":false}'
```

⚠️ 副作用：这样会把 `sales_number` 一并设成同一个人，绕不开。
⚠️ `subclazzType` 与 `subclazzUsage` 不匹配会报「辅导班类型和用途不匹配」，正常辅导班用 `0`/`0`。
**改完必须查库自证**（`gaotu.subclazz.assistant_number`），不要只看 `code:0`。

## 12. 复跑验证命令

链路造完后，从三个入口自证：

### 12.1 交集（product-server，权威同源）

```
project=product-server（或按实际反射桥配置调 promotion-b 的对应转发路径）
service_method=PreOrderCouponIntersectService#intersect
params=[<活动号>, [<前置课程号1>, <前置课程号2>, ...]]
```
预期：`pre_subjects`/`post_subjects` 覆盖目标学科集合，`coupon_sku_numbers` 数量等于目标学科数，`empty=false`。

### 12.2 B 端 listCoupon

```bash
curl -X POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
  -H 'Content-Type: application/json' \
  -H 'traffic-env: <本需求泳道>' \
  -d '{"renewMasterNumber":"<续班计划号>","pageNum":1,"pageSize":20}'
```
预期：只返回三者交集范围内的券，数量与第 12.1 步一致，`couponStatus=1`、`saleStatus=2`、`selectable=true`。

### 12.3 C 端 preRegistration

```
project=cart
service_method=com.gaotu.renewal.RegistrationService#preRegistration
params=[1,"<续班计划号>","<某一前置课程号>",null]
```
预期：活动形式为膨胀券；返回的商品命中"续班计划年级学科 ∩ 券范围"（注意 C 端口径比 B 端宽，见 10.5），价格和抵扣金额非空。

三个入口都过，说明链路从前置班到活动绑定全部生效；任一入口为空或数量不对，按 `verify.md`「券列表返回空的排查口径」一节的三步定位法（先查 product-b 交集接口 → 再查 `couponSkuNumberList` 字段名 → 最后查 coupon-a 真实券状态）排查，不要一上来就怀疑三者交集算法本身。

---

## 13. 小班课链路的差异

小班课（续班计划 `renewalPlanType=2` / `type=2`）与大班课造法**主体相同**，差异集中在三处：

| 差异点 | 大班课 | 小班课 |
|---|---|---|
| 课程/班级落库 | `gaotu.course` / `gaotu.clazz` | **`course_center.course` / `course_center.clazz`**（cluster 153/212） |
| 学员在读关系 | `gaotu.order_info` 按 `clazz_number` 查 | `course_center.clazz_student` |
| 年级学科存法 | `gaotu.course` 直接有字段 | `course_center.course_extension`，`extension_type=16` 存年级、`=17` 存学科路径 |

其余（续班计划、`bind_pre_course`、续班关系、`type=3` 流程 + 两节点、膨胀券活动、绑活动）与大班课**完全一致**，
按第 3～9 节走即可；三者交集口径（第 10 节）也一致。

⚠️ 小班课建班不要套 `create_large_class`，先 `list-tools` 找小班课/GPS 对应的建班 workflow。
