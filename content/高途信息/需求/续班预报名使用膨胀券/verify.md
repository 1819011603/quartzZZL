---
title: 续班预报名使用膨胀券 · 验证手册
tags: [需求, 验证]
---

# 验证手册

> 只保留当前可执行条件、仍有效数据和最新预期。接口字段结构见 `apifox-openapi.json`。

## 环境

| 项 | 当前值 |
|---|---|
| 本需求泳道 | `test-gtbg-dev-3` |
| coupon-a 泳道 | `test-eco-7` |
| 逻辑环境 | 两个泳道均为 dev；查 pod 使用 `--env dev` |
| 请求头 | `traffic-env: test-gtbg-dev-3` |
| 数据库 | `gaotu_polar_test_03`，cluster_id `142`；scope 表在 `gaotu` 库，活动主数据在 `promotion` 库 |
| 商品类型 | Apollo `pre.order.coupon.product.type=8014` |

验证镜像前先确认目标服务 eureka UP。promotion 涉及 C 端时同时确认 promotion-b 与 promotion-c。

## 登录

测试环境不发送短信，登录前写入一次性验证码：

```bash
cd "脚本"
python3 set_test_smscode.py --mobile 17900911102 --client 613156985,613156986 --clear-limit
```

页面使用手机号 `17900911102`、验证码 `1234`。登录成功后验证码会被删除，下次登录重新执行脚本。

## 当前测试数据

> 🔴 **2026-09-15 重造**：0910 的木系列券（木7/木11/木12）已全部 `couponStatus=2 已失效`、
> `saleStatus=1 未开售`，挂它们的活动 `578669527399682048` 随之报废。下方是当前有效的一套。

| 对象 | 值 | 用途 |
|---|---|---|
| **膨胀券活动（当前）** | **`579607430990692352`** | zzl-膨胀券-案系列-0915（已发布/进行中）。⚠️ **2026-09-17 复查：3 张券 `saleStatus` 都已回落成 1（停止售卖）**，`couponStatus` 仍是 1（使用中）——该活动若之后要编辑保存会被 T-44 新加的状态校验拦住，需先把券恢复成售卖中或换券。<br>⚠️ 它并未绑定到计划 `578668076965308416`——该计划实际绑的是 `578667303502106624`，见下方「排查记录」 |
| 续班计划 | `578668076965308416` | 六年级 数学/英语/语文 三槽位，已绑上面的活动 |
| 前置班/课程 | 班级 `578667321965428736`（`16SX26C4H511001`）/ 课程 `578667318880518144` | 六年级·数学，**16 名在读学员** |
| 后置课程 | 数学 `578667723368869888` / 英语 `578667772899405824` / 语文 `578667774495338496` | 三者交集的「后置产品年级学科」 |
| 辅导班 | `36166710321086848`（弓雪萌SX161001） | 带班老师=弓雪萌 `537590170260606976` |
| 续班计划 | `577431949669312512` | B/C 范围过滤 |
| 预警数据 | `questionnaire_inspect.id=261` | `postProductId`/`postProductName` 验证 |

### 活动 `579607430990692352` 挂的 3 张券（2026-09-15 重造）

| 范围 | 券名 | couponId | 券商品 ID(skuNumber) | 买/抵(分) |
|---|---|---|---|---|
| 六年级·数学(16,1) | 案4券v5 | `579602402418638848` | `579602402548676609` | 2000 / 6000 |
| 六年级·英语(16,4) | 案11券v5 | `579602410106798080` | `579602410226350081` | 2000 / 6000 |
| 六年级·语文(16,5) | 案9券v3 | `579597950269800448` | `579597950383060993` | 2000 / 6000 |

2026-09-15 重造时三张均 `couponStatus=1 使用中` + `saleStatus=2 售卖中`，B 端 `total=3`、C 端推荐 3 张，B/C 一致（当时结论）。**2026-09-17 复查：`saleStatus` 已全部回落成 1（停止售卖）**，若要继续用这 3 张券验证「使用中且售卖中」相关逻辑，需要先在电商侧把它们重新置为售卖中。

⚠️ **选券必须取 coupon-a 最新批次**：按到期时间或售卖期长短挑历史券，promotion 侧 enrich 取不到，
`buy_amount`/`deductible_amount` 为空，C 端直接抛 `膨胀券购买金额缺失`。

### 当前学员与购券格局（2026-09-15）

| 学员 | userId | 手机号 | 已购券 |
|---|---|---|---|
| 测试学员膨胀1 | `7542292905` | 17900001101 | 案4券v5（数学）+ 案11券v5（英语） |
| 测试学员膨胀2 | `7489620119` | 17900001102 | 案9券v3（语文） |

学员1 的「数学+英语」用于验证 K-TC0002 多科目斜线分隔与按学科 ID 升序（数学1 < 英语4）。

**2026-09-15 新补 10 名在读学员**（前置班 6 → 16 人）：手机号 `17900002201`~`17900002210`，
全部 `order_status=2`。用于 F-TC0001 批量发链接与花名册类用例。

测试前先查询上述数据仍存在且状态满足用例。共享数据不得直接假定保持不变。

### 小班课链路（2026-09-15 建，K-TC0014 用）

> 造法与大班课的差异见 [[build-data]] 第 13 节；**小班课课程/班级在 `course_center` 库，不在 `gaotu`**。

| 对象 | 编号 | 名称 |
|---|---|---|
| 续班计划 | `579596447754823680` | zzl-小班课续班膨胀券-0915（`type=2`，status=0 未发布） |
| 前置课程 | `579596056986261504` | zzl-小班课续班膨胀券-前置-六年级数学-0915（biz `16SX26CKTA3`） |
| 前置班级 | `579596144554940416` | zzl-小班课续班膨胀券-前置班-六年级数学-0915 |
| 后置课程 | `579596212490082304` | zzl-小班课续班膨胀券-后置-六年级数学-0915 |
| 后置班级 | `579596250695997440` | zzl-小班课续班膨胀券-后置班-六年级数学-0915 |
| 预报名流程 | `579596549208745984` | type=3 |
| └ 预报名配置节点 | `579596549215037440` | type=4，活动绑在这里 |
| └ 链接发放节点 | `579596549215037441` | type=5 |
| 膨胀券活动 | `579601011014926336` | zzl-小班课膨胀券活动-0915，挂券 Q1（六年级·数学） |

计划年级学科：`COURSE_GRADE=16` / `COURSE_SUBJECT=1`（六年级·数学），学年 2026、目标学期 X，部门 10007722。

🔴 **仍缺**：前置/后置班级**都没有学员**（`course_center.clazz_student` 0 行），也没有辅导班/带班老师。
学员就绪前，B 端花名册与三者交集里的 `pre_subjects` 都是空的，K-TC0014 跑不了。

### 计划 `578668076965308416` 当前绑定的券

> 🔴 **2026-09-16 15:16 实测订正**：该计划实际绑定的活动是 **`578667303502106624`**
> （zzl-P0-膨胀券预报名-0910），**不是**本文件上方「当前测试数据」里写的 `579607430990692352`。
> 绑定关系以库为准，反查两跳：
> `renewal_number -> process_config.number -> renewal_link_activity.activity_number`（`is_del=0`）。
>
> ⚠️ **该活动的券范围行已被 `gongxuemeng@baijia.com` 于 2026-09-16 15:16:16 全部软删**
> （`gaotu.renewal_pre_order_activity_coupon_scope` 3 行全部 `is_del=1`），
> 因此 `/renewal/pre/coupon/list` 传该计划时**对任何 userId 都返回空**——
> 这是**数据被删**，不是代码缺陷，也与 `userId` 无关。详见下方「排查记录」。
>
> 下表是被软删前的槽位配置，恢复数据后才重新有效。


| 槽位 | couponId | 券商品 ID | 券名 | 已售/总量 | 持有上限 | 买价/抵扣(分) |
|---|---|---|---|---|---|---|
| 六年级数学(16,1) | `579417711627513856` | `579417711732357121` | Q1 | 0/20 | 3 | 2000 / 6000 |
| 六年级英语(16,4) | `579426455071498240` | `579426455627266049` | 膨胀券-脚本 | 0/10 | 1 | 10000 / 20000 |
| 六年级语文(16,5) | `579394599487844352` | `579394599632533505` | Q8 | 3/10 | 3 | 2000 / 6000 |

三张全部 `使用中/售卖中`、`selectable=true`。

### 可用膨胀券（`使用中` + `售卖中`）

`/renewal/pre/coupon/list` 不传 `renewMasterNumber` 时 `total=40`，**全部** `couponStatus=1`
且 `saleStatus=2`、`selectable=true`。常用两张：

| couponId | 券商品 ID(skuNumber) | 券名 | 已售/总量 | 持有上限 | 买价/抵扣(分) | 备注 |
|---|---|---|---|---|---|---|
| `578839415256780800` | `578839415380715521` | zks | 0/100000 | 1 | 100 / 200 | 库存几乎无限，**跑量首选** |
| `579417711627513856` | `579417711732357121` | Q1 | 0/20 | 3 | 2000 / 6000 | 用户指定；`holdLimit=3` 可测多次持有 |

⚠️ 当前 40 张可用券**没有一张是售罄的**（`soldCount < totalCount`），
**T-33 的售罄用例仍未解锁**，见「待补边界验证 / 售罄券」。

重新拉取当前可用券：

```bash
curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" \
  'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
  -H 'Content-Type: application/json' -H 'traffic-env: test-gtbg-dev-3' \
  -d '{"pageNum":1,"pageSize":50}'
```

### ⚠️ 所有下单一律走 `test` 泳道

**造数下单（进班 0 元单、膨胀券单、小班课单）全部传 `traffic-env: test`**，不要传 `test-gtbg-dev-3`。
这是 2026-09-15 用户明确的口径，也与订单链路实际部署一致。

但 **`test` 跑的是 master 镜像，没有本需求代码**：`traffic-env: test` 调 `/renewal/pre/coupon/list` → `404`；
反射 `PreOrderCouponAclService` → 找不到实现类。所以是**两段分工**：

| 动作 | 泳道 |
|---|---|
| 下单（进班单 / 膨胀券单 / 小班课单） | **`test`** |
| 验证本需求代码（券列表、三者交集、C 端落地页、反射桥） | **`test-gtbg-dev-3`** |

券数据在 coupon-a 跨泳道共享，两段各自成立，不冲突。要在 `test` 上验证本需求接口，
必须先把相关服务发一版到 `test`。

### mock 支付页面

下单后需要支付才能推进订单状态时，用速搭的 mock 支付页，不用走真实支付：

https://sd.baijia.com/projectItem/myreview/79ab6125-96cb-4da3-a944-ab32f5772dc1/4e76c321-2ace-45d3-a387-0b5973ef4096

用法：环境选 `test`，订单号填**批次单号**（⚠️ 不是下单返回的订单号，是 OES 订单管理→付款记录页里
按学员 userId/手机号查到的批次单号），点「支付」，返回 `结果=成功` 并带 `pay_order_number`/`rid` 即成功。

## 学员维度券匹配（2026-09-16 验证通过）

> 口径见 [[changelog]] 2026-09-16。四服务均已发到 `test-gtbg-dev-3` 并 eureka UP。

### 验证基线

活动 `579607430990692352` / 计划 `578668076965308416` / 学员 `7542292905`（在读**六年级数学**班）。

| 场景 | 请求 | 实测 | 判据 |
|---|---|---|---|
| B 端券列表 | `renewMasterNumber` + `userId` | `total=3`：案4券v5(数学)、案11券v5(英语)、案9券v3(语文) | ✅ |
| B 端缺 `userId` | 只传 `renewMasterNumber` | `total=0` | ✅ 不退化计划级 |
| B 端不传计划号 | 只传分页 | `total=63` | ✅ **存量入口不受影响** |
| B 端无在读班学员 | `userId=9999999999` | `total=0` | ✅ |
| product-b Feign | `/feign/.../listDisplayableByRenewalPlan` | 3 行扁平结果 | ✅ |
| product-c C端接口 | `/c/renewMaster/listDisplayableCoupons` | 3 行，与 B 端**完全一致** | ✅ 同源 |
| C 端膨胀券落地页 | `preRegistration` | 返回券商品，含金额/`scope_labels`/文案 | ✅ |
| **C 端订金班落地页** | 订金班活动 `578695898081533952` | 不调新接口、无报错 | ✅ **未受影响** |

### 🔴 最关键的一条：扩科券不再被漏

学员在读前置班是**六年级数学**，但返回里有**英语券和语文券**。
旧实现里 `preSubjects` 过滤会把这两张滤掉只剩 1 张——扩科正是膨胀券的主要用途，
这条是本次改动的核心价值，回归时**必须**覆盖。

### 滚动发布期间的假故障

cart 调 product-c 一度稳定复现 404，trace 显示泳道标记**正确**（`test-gtbg-dev-3`），
真因是新旧 pod 并存（`instanceCount` 13→14），feign 负载均衡打到了未下线的旧 pod。
旧 pod 下线后自动恢复。**发完版立刻验证时遇到 404/接口不存在，先查是不是这个**，不要改代码。

## C 端券状态过滤（2026-09-16 复核通过）

原冒烟轮记有一条功能性缺陷「C 端落地页未按券状态过滤，已暂停/已失效的券照样展示可购」（方向资损）。
**2026-09-16 复核：已修复。**

判据在 `PreRegistrationCouponAssembler#isSellable`（cart）：

```java
if (statusAllowed(couponConfig.getDisplayCouponStatuses(), couponStatus)
        && statusAllowed(couponConfig.getDisplaySaleStatuses(), saleStatus)) {
    return true;
}
// 不满足 -> assemble 循环里 continue，不下发给学员，并打 warn 留痕
```

- 两个白名单由 Apollo `preRegistration.coupon.display.couponStatus` / `.saleStatus` 控制，
  **代码默认值 `1`（仅「使用中」）**；测试环境未覆盖该配置，走默认，过滤生效。
- **两个状态都要卡**：`couponStatus` 管券本身是否生效、`saleStatus` 管券商品在不在卖，二者正交——
  券可以是【使用中】但商品【停止售卖】，展示了学员也买不成。
- **状态取不到（为空）一律不展示**：C 端是直接成单链路，查不到即视为不可售。
- 任一白名单配成空串会**关掉**该维度过滤，改配置时注意。

受影响用例 **H TC0002**、**TC-G004** 的券状态过滤分支应改判为通过。

> ⚠️ 想用真实失效券端到端复验时注意：木系列 3 张券虽已 `couponStatus=2`，但其活动
> `578669527399682048` 当前**未绑任何续班计划**（已被案系列替换），走不了 C 端链路，
> 需先绑计划或另造混合状态活动。

## 预报名科目与看板取数（2026-09-16 打通，含正确步骤）

> 原归档与飞书文档都记过「ES 无数据 / 无写入路径 / 等离线跑批或找马胜灌数」——**三条都不成立**，
> 已作废。真实链路分两段，**两段用不同的索引**，这是排查时最容易走错的一步。

### 第一段 · K 模块（预报名科目）：跑券回溯

xjob test 任务 `6648`「回溯预报名信息」，**必须指定泳道 pod**（否则落到 base 老镜像）：

```bash
cd ~/.local/mcp-servers
./mcpcli.py xjob_admin xjob_resolve_address -k namespace=test-gtbg-dev-3 -k service=student-data -k job_group=688
./mcpcli.py xjob_admin xjob_trigger_job -k job_id=6648 \
  -k 'executor_param={"clazzNumbers":[578667321965428736],"couponSkuNumbers":[579602402548676609,579602410226350081,579597950383060993]}' \
  -k execute_address=<上一步的 recommendedAddress> -k confirm=true
```

`clazzNumbers` 填**学员的在读前置班**（不是预报名班）；`couponSkuNumbers` 只是过滤器。
`backDwsPresaleHandler` → `PresaleCouponBackService#backfillByUser` → `PresaleCouponServiceImpl#dealCouponPaid`，
末尾 `refresh(...)` **同时写 MySQL 与 ES**（类注释：「落库与刷 ES 直接复用增量链路，不写第二套」）。

核对落点：MySQL `ees_data.dws_fuwu_clazz_user_presale_coupon`（cluster **149**，不是 142）、
ES `ads_large_subclazz_user_index` 的 `presaleSubject`。

**⚠️ 券订单三道门槛**：`confirmedTime` 非空 + `orderStatus ∈ [2,4]` + `refundType=0`。
「跑了但没收到数」先查这三项。学员 `7542292905` 的 3 笔订单均 `order_status=3` 且有 `cancel_time`
（**已取消**，不是待支付，mock 支付页付不了），回溯正确跳过；
归档早前记的「该学员已购数学+英语券」**与事实不符**。

### 第二段 · I 模块（预报名率与看板）：跑看板 job

xjob test 任务 `5900`「续班看板」，参数 `[578668076965308416]`，同样指定泳道 pod。
该 job **依次查两个索引**：

| 步骤 | 索引 | 集群 | 条件 |
|---|---|---|---|
| ① 查辅导班 | `subclazz_search` | **阿里云 subclazz 集群** | `renewalPlanId` + `assistantNumber` exists |
| ② 聚合学员 | `ads_large_subclazz_user_index` | studentServe | **`canRenewal ∈ [1,2,8]`** + `subclazzNumber` |

⚠️ 代码里 `largeSubclazzUserIndex` 这个常量**在该方法中并未被使用**，第一段索引取自
`StudentESTypeEnum.ADS_SUBCLAZZ_ES`。照着常量去查会得出完全错误的结论。

### 🔴 真正的卡点：`canRenewal=0`

新造的学员默认不可续，被第②步全部滤掉 → 聚合为空 → 不调 `insert()` → 快照表零写入。
此时 job 仍返回 `handleCode=200` 且**不打任何 `Inserting batch of...` 日志**，
极易误判成「跑成功了但库找错了」。**判据就是有没有这行日志。**

解法（直接改 ES，凭证取自 Apollo `student-data / TEST / **es**` namespace 的 `student.serve.es.*`；
测试环境是自建域名、非阿里云实例，不走 SRE 工单）：

```bash
curl -u 'gaotu_student_archive:gaotustudentarchivetest123' \
  -XPOST 'http://esclustercommon-test.baijia.com:9200/ads_large_subclazz_user_index/_update_by_query?refresh=true&conflicts=proceed' \
  -H 'Content-Type: application/json' -d '{
  "query": {"bool": {"must": [
    {"terms": {"subclazzNumber": ["36166710321086848","36177643862098432","36225439398363520","36178241120764288","36178263845765504","36178237989716352"]}},
    {"term": {"canRenewal": "0"}}
  ]}},
  "script": {"source": "ctx._source.canRenewal = 1", "lang": "painless"}
}'
# → updated: 26, failures: []
```

改完重跑 job 5900，快照表即有数据。

### 验证结果（cluster 200 `student_data_renewal_test.sub_clazz_renewal_process_snapshot`）

| 辅导班 | 名称 | 带班老师 | 可续 | 已预报名 | 预报名率 |
|---|---|---|---|---|---|
| 36166710321086848 | 弓雪萌SX161001 | 弓雪萌 | 18 | 3 | 16.7% |
| 36177643862098432 | 弓雪萌SX1002 | 弓雪萌 | 8 | 4 | 50% |

合计 26 可续、7 已预报名，与 ES 中 `presaleStatus=1` 的 7 条自洽。`snapshot_time=2026-09-16`。

⚠️ 该表里每天 `00:00:00` 的固定 19 条是**另一条离线管道**的产出，与本 job 无关，别拿它当判据。

### K 模块可用样本

| 用例 | 学员 | presaleSubject | 说明 |
|---|---|---|---|
| K TC0001 单科目 | `7489622238` | `[4]` 英语 | ES 文档 `36166710321086848-7489622238` |
| K TC0002 多科目 | `7489622226` | `[1,5]` 数学+语文 | 期望展示「数学/语文」，数学1 < 语文5 |
| （备选多科目） | `7489622230` | `[1,4]` 数学+英语 | |

### ⚠️ 雪花 ID 一律传字符串

查 ES / 反射桥时传数字会被 JSON 精度截断（`36166710321086848` → `...850`、
`578668076965308416` → `...400`），命中 0 条，极易误判成「数据不存在」。本轮因此误判两次。

## 核心验证

### B 端券列表

```bash
curl -X POST 'https://test-fuwu.baijia.com/bgwApi/component/student-center/renewal/pre/coupon/list' \
  -H 'Content-Type: application/json' \
  -H 'traffic-env: test-gtbg-dev-3' \
  -d '{"renewMasterNumber":"577431949669312512","pageNum":1,"pageSize":20}'
```

预期：只返回三者交集范围内的券，每条同时满足默认 `couponStatus=1`、`saleStatus=2`，`total` 与列表一致；
`availableScope` 为年级学科文案、`holdLimit` 为字符串、`creator` 为姓名或兜底工号；不传 `renewMasterNumber`
时不做续班计划范围过滤但状态过滤仍生效。传 `577431949669312512` 返回 `total=0` 属正常（命中券
`saleStatus=1` 被白名单滤掉，非缺陷），见下方排查口径。

### B 端活动详情

使用反射调用：

```text
project=promotion
traffic_env=test-gtbg-dev-3
service_method=com.gaotu.promotion.app.service.preorder.PreOrderActivityService#detail
params=[{"number":"578563007821410304"}]
```

预期：券 ID、券名、商品 ID、金额、双状态、状态文案、创建人和 scopes 均完整。

### C 端推荐

```text
project=cart
traffic_env=test-gtbg-dev-3
service_method=com.gaotu.renewal.RegistrationService#preRegistration
params=[1,"577431949669312512","514762045841821696",null]
```

预期：活动形式为膨胀券；商品命中三者交集与双状态白名单；价格和抵扣金额非空。

### 范围唯一键

- 同活动的相同年级学科组合：保存失败。
- 不同活动使用相同券和年级学科组合：保存成功。
- 唯一键：`uk_act_grade_subject(activity_number, grade_code, subject_code)`。

### 券列表返回空的排查口径

`/renewal/pre/coupon/list` 传 `renewMasterNumber` 返回 `total=0` 时，**不要先怀疑三者交集或解码器**，按序定位：

1. 直调 product-b `/feign/preOrderActivity/couponScope/listDisplayableByRenewalPlan`（服务名 `PRODUCT-B`，
   ⚠️ 入参字段是 `renewMasterNumber` 不是 `renewalPlanNumber`；19 位 ID 传字符串）。返回非空即交集正常。
2. 拿交集返回的 `coupon_sku_number`，用 `couponSkuNumberList`（不是 `couponSkuNumbers`，写错字段名会被
   静默忽略并返回全量，极易误判成"过滤没生效"）查列表。
3. 仍为空则直查 coupon-a：反射 `PreOrderCouponAclService#pageQueryCoupon`，看券的真实状态值。

⚠️ 反射桥的 19 位 ID 必须传字符串，传数字会被截断（`578667318880518144` → `578667318880518100`），
交集因此误判为 `empty=true`。

### 🔴 券展示的两个数据源必须同时满足

一张券要出现在 `/renewal/pre/coupon/list`，两处都要有它：`gaotu.renewal_pre_order_activity_coupon_scope`
（范围行）与 promotion 活动的商品列表 `promotion.pre_order_activity_product`（活动商品行）。
`PreOrderCouponIntersectService` 先取活动详情拿商品列表，再拿范围行求交，**只改 scope 表不改活动商品，
券会在交集阶段被丢掉**。所以换券必须走 promotion 的 `/preOrderActivity/edit`，由它在事务内回调 product-b 写范围。

### 槽位数量上限

券能展示几张，由**交集出来的「年级+学科」对数**决定：唯一键
`uk_act_grade_subject(activity_number, grade_code, subject_code)` ⇒ 一个「活动+年级+学科」只能放一张券。
计划 `578668076965308416` 的 `post_grades=[16]`、`post_subjects=[1,4,5]` ⇒ 六年级×数学/英语/语文，只有
3 个槽位。要展示更多券，只能换一个后置学科更多的续班计划，或新建活动绑到别的计划。

### 进行中的活动怎么改券

活动 `activity_status=3`（进行中）时 `/preOrderActivity/edit` 只允许改结束时间
（`validateActivityStatusForEdit`，只有 `0 待发布` 能全字段编辑）。测试环境换券：先把
`activity_status` 临时改成 `0`，调 `/preOrderActivity/edit`（`beginTime` 必须晚于当前时间），
再改回 `3` 并还原原时间窗（`578842182125903872` 的原窗口：
`2026-09-11 10:35:13` ~ `2026-09-29 10:30:13`）。

## 待补边界验证

### 售罄券

当前 40 张可用券全部未售罄（见「可用膨胀券」表），需造数：优先挑小库存券
（如 `579394614104993792`，1/5）买满，`578839415256780800` 总量 100000 不适合拿来刷售罄。

用 `couponStatus=1` 且 `sold_count >= total_amount` 的真实券验证：`/renewal/pre/coupon/list` 返回该券
时 `selectable=false`；`/promotionManagement/preOrderActivity/editAndPublish` 添加该券时报"膨胀券已售罄，
不可添加"；库存判据以 coupon-a 返回为准，不使用 OES 活动缓存中的已售/总量。

### 满班课程

用 `capacity>0` 且 `signUpCount>=capacity` 的班级验证：订金班活动保存时报"班级班容已满，不可添加"，
`capacity=-1` 的班级必须允许保存（回归）。

### 持有上限

- `holdLimit>0` 返回数字字符串。
- `holdLimit=0` 返回“不限”。

### 🔴 券与订金班并存（取并集）—— 零数据覆盖

需求第 73/74/75 行都写了「两种方式都配置，**取并集**」，代码实现了，但**线上线下都没有一条这样的数据**，
这条规则从未被真实数据走过。2026-09-15 实测（test，cluster 149 `ees_data`）：

| 表 | 总行数 | 学员数 | 有效行(is_del=0) |
|---|---|---|---|
| `dws_fuwu_clazz_user_presale_coupon`（券） | 9 | **2** | 9 |
| `dws_fuwu_clazz_user_presale_subject`（订金班） | 415 | 259 | 339 |
| `dws_fuwu_small_clazz_user_presale_subject`（小班） | 79 | 66 | 76 |

按「学员 + 学年 + 学期」join 两张表，`is_del=0` 的交集为 **0 行**——券的 2 个学员与订金班的 259 个学员完全不重叠。

并集发生在 `PresaleSubjectServiceImpl#refreshByUserTermYear`：两张表捞进同一个 list，
`presaleStatus` 用 `anyMatch`、`presaleSubject` 用 `flatMap + distinct`，天然并集。
**粒度是「学员 + 学年 + 学期」，不是班级。**

> 这也是「取最早 / 取最新」口径分歧长期没暴露的原因：跨形态合并分支从来没跑过真实数据。

#### 为什么必须造数（不能只靠单测）

单测已覆盖合并逻辑本身（`PresaleSubjectServiceImplTest#should_合流券科目并取最新下单时间_when_券与订金班并存` 等），
但 mock 不掉的是**两条独立写入链路在同一个学员身上并发收敛**：订金班由花名册进退班消息驱动，
券由订单事件驱动，两者落不同表、各自触发 refresh。要验的是它们合流后 ES 的最终值，这只有真实数据能验。

#### 造数方案 A：直接插库（推荐，最快）

并集只读这两张表，不关心记录从哪来。给一个**已有订金班预报名记录**的学员补一条券记录即可：

```sql
-- 1. 挑一个有有效订金班记录的学员，记下 user_id / school_year_id / school_term_id / clazz_number / course_number
SELECT user_id, clazz_number, course_number, school_year_id, school_term_id,
       presale_subject_id, grades, course_type, course_tags
FROM ees_data.dws_fuwu_clazz_user_presale_subject
WHERE is_del = 0
ORDER BY id DESC LIMIT 10;

-- 2. 按同一「学年+学期」补一条券记录，presale_subject_id 故意取一个订金班没有的学科，便于验证并集
--    course_type 必须是付费课（40），course_tags 不能含排除标签（默认 13,4,26,11,27）否则会被判成赠课而不计入
INSERT INTO ees_data.dws_fuwu_clazz_user_presale_coupon
  (user_id, clazz_number, course_number, grades, course_type, course_tags,
   school_term_id, school_year_id, coupon_sku_number, renewal_number,
   pre_order_activity_number, coupon_order_item_number, presale_subject_id,
   presale_order_time, is_del)
VALUES
  (<user_id>, <clazz_number>, <course_number>, '[16]', 40, '[35]',
   '<school_term_id>', <school_year_id>, 579394599632533505, 578668076965308416,
   578842182125903872, 999999999999999999, '[<订金班没有的学科ID>]',
   '2026-09-20 10:00:00', 0);
```

`presale_order_time` 建议**设成比订金班订单支付时间更早**，这样能顺带验证「取最新」口径
（期望取订金班的时间，不是券的）——这正是 2026-09-15 修正的那处，见 [[changelog]]。

写完跑回溯触发重算（见下节「怎么回溯」），然后查 ES 期望：

| 字段 | 期望 |
|---|---|
| `presaleStatus` | `1` |
| `presaleSubject` | 订金班学科 ∪ 券学科（去重、按学科 ID 升序） |
| `gradePresaleSubject` | 同上，按年级归组 |
| `presaleOrderTime` | 两者中**较晚**的一个 |

⚠️ `course_type=40`、`course_tags` 不含排除标签是硬前提：`listPresaleSubjectId()` 会因非付费课或赠课返回空列表，
造出来的数据不计入并集，看起来像"并集没生效"。

#### 造数方案 B：走真实链路（更贴近线上，成本高）

挑一个已进预报名班（订金班）的学员，再给他买一张膨胀券，要求券的「年级+学科」能匹配上他前置课的**可续后置课**
（`calculate_renewal_type=2`），且学年学期与订金班记录一致。匹配不上不会落券记录，只有一条 INFO 日志。
成本主要在凑「同一学员 + 同一学年学期 + 年级学科可匹配」这三个条件。

#### 退款侧也要验

并集建立后再退券：期望回落成**只剩订金班那部分**（`presaleSubject` 去掉券学科、`presaleStatus` 仍为 `1`、
`presaleOrderTime` 回到订金班的时间），而不是整个清空。这条是券退款不会误伤订金班的关键保证。

## 后置课续班关系口径订正的验证（2026-09-17）

对应 [[changelog]]「膨胀券后置课改取续班关系」。

**单测**：`PresaleCouponServiceImplTest` 27 个用例全过，其中 4 个为多活动场景新增
（多活动都收数、坏活动跳过而不丢整张券、撞唯一键取并集、全部活动不可用不落库）。

**反射桥实测（product-b）**：券 `579434436486002689`
修复前返回空数组 `[]`；修复后返回 1 条——activity `579811561793671168` /
renewal `556560317436436480` / scopes `grade 12` + `subject 12`。
该券另挂的两个未绑续班流程的活动被正确跳过，年级学科没有串进 scopes。

**`preCourseList` 恒为空的既有缺陷已确认修复**（commit `e7bbfaacc`，product 主服务部署后）：
`queryRenewalMasterInfoElseException(556560317436436480)` 返回 `preCourseList: [17218465768538824]`。

**小班回溯链路已打通**：

```
券 579434436486002689
 → 活动 579811561793671168
 → 续班计划 556560317436436480「续班计划-新的-小班课」
 → 前置课 17218465768538824「前置-三年级-历史-王金峰-2026-2027春」（arrangeModeType=4 小班）
 → 学员 7542297028 在班：clazzNumber 551005295197935616、
   subclazzNumber 34438197699674624、status=1
```

**数据侧已就绪**：前置课 `17218465768538824`（「前置-三年级-历史-王金峰-2026-2027春」）
在 course-center 配了两门后置课 `17218465768538707`「后置-二年级-历史-尹超」、
`17218465768538626`「后置-二年级-历史-梅涛林」，均 `grades=[12]` `subjects=[12]`
`arrangeModeType=4`（小班），与券范围 `grade 12` + `subject 12` 成对匹配。

### 🔴 2026-09-17 复测：端到端未落库，根因是**消费端镜像滞后**（非代码/数据问题）

重推消息 `0ADAFACF0001379CE046514F6031125A`（消费组
`GID_student-data_dws_presale_coupon_order_test_test-gtbg-dev-3`）返回 `CR_SUCCESS` / 698ms，
但 `ees_data.dws_fuwu_clazz_user_presale_coupon` 仍无 `user_id=7542297028` 的记录。

日志（pod `student-data-dws-858f45c68d-gzjnd`）显示消费端调的是**旧方法** `mapPostCourseByNumberBatch`：

```
CourseNotNormalAclServiceImpl:195 mapPostCourseByNumberBatch ｜ response is {17218465768538824=[
    CourseRenewalRelationMapVO(courseNumber=17218465768538626, calculateRenewalType=1),
    CourseRenewalRelationMapVO(courseNumber=17218465768538707, calculateRenewalType=1)]}
PresaleCouponServiceImpl:369 buildRecords | 前置课没有可续的后置课程，跳过, courseNumber:17218465768538824
PresaleCouponServiceImpl:124 dealCouponPaid | 券适用范围与可续后置课的年级学科无匹配,
    activityNumber:579811561793671168, scopes:[{gradeCode:12,subjectCode:12}]
```

旧方法筛 `calculateRenewalType=2`，而数据全是 `=1` → 全被滤掉 → 不落库。**这恰好反证改动的必要性。**

**真因**：部署镜像 `student-data-dws:feature-xuban-pre-5c63f8ba-20260917102049`（构建 10:20）
基于提交 `5c63f8ba2`（10:01），而 `74c6e6b78`（11:03）**不是它的祖先**（`git merge-base --is-ancestor` 退出 1），
即该镜像不含 =1 改动。**把它发到 `test-gtbg-dev-3` 后重推同一消息即可落库**（`scopeSize:1` 说明券范围链路已通，
只剩后置课过滤这一处）。

> ⚠️ 此前记的「消费验证日志确认新代码生效」有误——当时只确认了 `CR_SUCCESS`，未核对日志里调用的方法名，
> 实际跑的是旧代码。**判定消费端是否含改动，认日志里的方法名/镜像 commit，别只看消费结果码。**
> 消息重推（控制台「消费验证」）会生成**新的 msgId**（本次 `0BC1F0C0...`，trace 与旧消息相同），
> 按旧 msgId 搜日志会漏，用 `messages: <userId>` 或原 traceId 查。

### ✅ 复测通过（2026-09-17 11:56，重发 dws 后）

把 `feature-xuban-pre`（含 `74c6e6b78`）发到 `test-gtbg-dev-3` 的 student-data-dws
（pipeline `1273324`，新 pod `student-data-dws-7f7b465bd6-94l5s`，eureka UP），重推同一消息
`0ADAFACF0001379CE046514F6031125A`（新 msgId `0BC1F0C0...`），`CR_SUCCESS` / 713ms。

日志：`buildRecords | matched ... postCourseNos:[17218465768538707, 17218465768538626], grades:[12], subjects:[12]`
→ `dealCouponPaid | saved, records size:1`。

落库（cluster 149）：

| 列 | 值 |
|---|---|
| `id` | 94 |
| `user_id` | 7542297028 |
| `clazz_number` | 551005295197935616 |
| `course_number` | 17218465768538824（前置课） |
| `coupon_sku_number` | 579434436486002689 |
| `renewal_number` | 556560317436436480 |
| `pre_order_activity_number` | 579811561793671168 |
| `grades` / `presale_subject_id` | `[12]` / `[12]` |
| `presale_order_time` | 2026-09-16 18:55:56 |
| `is_del` | 0 |

小班刷新链路同时走通（前置课 `arrangeModeType=4`）：`SmallPresaleSubjectServiceImpl#refreshByCouponRecords`
→ `updatePresaleStatusAndOrderTime`（`presaleStatus=1`）→ `updatePresaleSubject`（`smallSubjectIds:[12]`），
ES `ads_small_clazz_user_index_v4` doc `551005295197935616-7542297028` 实测：
`smallPresaleStatus=1`、`smallPresaleSubject=[12]`、`smallPresaleOrderTime=1789556156465`（=2026-09-16 18:55:56）。

**结论**：T-45 ②号改动（后置课取续班关系）端到端落库 + ES 写入全部通过。

## 怎么回溯

两个 XXL-Job，大小班各一个：

| Handler | 管什么 |
|---|---|
| `backDwsPresaleHandler` | 大班课预报名 |
| `backSmallDwsPresaleHandler` | 小班课预报名 |

入参两种格式：

```
[3001234,3001235]
    只回溯订金班，行为与加券前完全一致（控制台历史参数就是这个格式）

{"clazzNumbers":[3001234,3001235],"couponSkuNumbers":[579394599632533505]}
    额外回溯膨胀券；couponSkuNumbers 不传或传 [] 等价于老格式
```

`couponSkuNumbers` 本身就是开关，没有另设 Apollo 开关。

### 维度：班级驱动，但券的落点与传入班级无关

两个字段角色不对称：`clazzNumbers` 是**驱动源**（决定遍历哪些学员，必填），
`couponSkuNumbers` 只是**过滤器**（订单侧反查都要 userId，光给券号找不到购买者）。
实际路径是「班级 → 捞该班学员 → 按 userId 回溯」；券记录落在哪由
「券 → 续班计划 → 前置课 → 学员在前置课的在班班级」决定。

由此三条实操判据：

1. **必须传学员的在读班（前置班）**。传预报名班时券部分会空跑——纯券学员不在预报名班花名册里。
2. **传 A 班可能改的是 B 班的 ES 字段**，A 班字段不动是正常现象。
3. **本 job 只能填大班班级号**。订金班那半的 `getPostPresaleRecords` 没有班型过滤，
   填小班号会往大班预报名表插脏行；小班走 `backSmallDwsPresaleHandler`。

### 🔴 消费者在 student-data-dws，不在 student-data

膨胀券实时收数的消费者 `DwsCouponPresaleOrderConsumer` 属于 **student-data-dws** 模块，
独立部署（serviceCode `baijia.gaotu.Business.counseling-workbench.student-data-dws`）。
发 `student-data` 服务**不承载这个消费者**——验证实时收数必须发 dws，否则跑的还是旧镜像。

### 消费组名带泳道后缀

测试环境实际消费组名是「配置里的 group 名 + `_泳道名`」，例如
`GID_student-data_dws_presale_coupon_order_test_test-gtbg-dev-3`。
按裸 group 名做消费验证会报「该 group 当前无在线消费端」，不是消费端挂了。

### 券没收上来先查这三个

券订单项还要过三道门槛：`confirmedTime` 非空、`orderStatus` 命中
`back.presale.coupon.paid.order.status`（默认 `[2,4]`）、`refundType=0`。
再看日志里 `券回溯完成` 那行的 `failedUserIds` 是否为空。

### 不适合挂 cron

`clazzNumbers` 是必填驱动源，定时跑等于把班级清单写死后反复重刷同一批班。
若为"新券上线补数"临时挂了定时，跑完要把 `couponSkuNumbers` 清掉。
券部分纯串行、每个学员多一串 RPC，几千人的大班先拿单个班验证再放量
（限速 `back.dws.presale.coupon.batch.sleep.millis`，默认 200ms，大小班两个 job 共用此 key）。

## 反射桥地址

| 服务 | 地址 |
|---|---|
| student-center | `https://test-fuwu.baijia.com/bgwApi/component/student-center/test/acl/compare/service` |
| promotion-b | `https://test-fuwu.baijia.com/bgwApi/promotion/b/test/acl/compare/service` |
| product-b | `https://test-fuwu.baijia.com/bgwApi/product-b/b/test/acl/compare/service` |
| cart | `https://test-api.gaotu100.com/cart/test/acl/compare/service` |

网关前缀以 `baijia_invoke.py` 的 `ROUTE_MAP` 为准。19 位 ID 一律使用字符串。

## 上线配置

详细清单见 README「上线影响面」；具体 Apollo key 名：`pre.order.coupon.product.type`（`8014`）、
`renewal.content.config.map`（膨胀券 reportCode）、`renewal.cStyle.preRegistrationCoupon.bgUrl`（背景图）、
student-center/cart 各自的 `couponStatus`/`saleStatus` 白名单 key（默认 `1`/`2`）。

## 页面复现

1. 打开 `https://test-mi.gaotu100.com/ark/app-promotions/continuation-classes/pre-register-activity`。
2. 确认前端分支包含 `feature-expand-coupon`，请求头泳道为 `test-gtbg-dev-3`。
3. 新建活动，活动形式选“膨胀券预报名”，活动开始时间必须晚于当前时间。
4. 添加当前状态符合白名单的券，配置年级和学科范围后保存。
5. 编辑详情应完整回显券字段和范围；scope 表应按活动/年级/学科保持唯一。


## 排查记录：`/renewal/pre/coupon/list` 返回空（2026-09-16）

**现象**：`{"userId":7489622228,"renewMasterNumber":"578668076965308416"}` 返回空列表，
traceId `2e3143df-a0ec-49dc-9022-25eb44487107.0.0`（15:16:57）。

**结论：数据问题，非代码缺陷。** 链路 230 span **0 error**、全程 HTTP 200、泳道正确
（`test-gtbg-dev-3`），是正常业务分支返回空，不是异常。

逐段验证（全部实测，均正常）：

| 段 | 结论 |
|---|---|
| 学员在读（花名册） | ✅ `7489622228` 在读前置课 `578667318880518144`，`status=1`、`isdel=0` |
| 计划前置课 | ✅ 3 门：`578667318880518144` / `578851790032846848` / `578851839439650816` |
| 后置课反查 | ✅ 返回数学/英语/语文 3 门（`578667723368869888` / `...772899405824` / `...774495338496`） |
| 券状态 | ✅ coupon-a 返回 3 张 `couponStatus=1` + `saleStatus=2` |
| **券范围 scope 行** | ❌ **3 行全部 `is_del=1`**，被 15:16:16 软删 |

`PreOrderCouponIntersectService#intersect` 在 `scopeRows` 为空时直接
`return PreOrderCouponIntersectResult.empty(...)`，故券列表为空。

**复现/验证命令**（表名是 `renewal_pre_order_activity_coupon_scope`，不是 `pre_order_activity_coupon_scope`）：

```sql
-- 1. 计划 -> 活动（两跳）
SELECT pc.renewal_number, rla.activity_number, rla.is_del
FROM gaotu.process_config pc
LEFT JOIN gaotu.renewal_link_activity rla ON rla.process_number = pc.number
WHERE pc.renewal_number = 578668076965308416;

-- 2. 活动 -> 券范围（is_del 必须有 0 行才会出券）
SELECT activity_number, coupon_sku_number, grade_code, subject_code, is_del, operator, update_time
FROM gaotu.renewal_pre_order_activity_coupon_scope
WHERE activity_number = 578667303502106624;
```

**恢复办法**：在 B 端重新保存该活动的券适用范围（会重新插 `is_del=0` 行），
或直接改库把这 3 行置回 `is_del=0`。恢复后无需重发服务即可生效。

**可用的对照数据**：`renewal_pre_order_activity_coupon_scope` 仍有 40 行 `is_del=0`、覆盖 23 个活动，
表本身正常。这三门前置课的在读学员（`gaotu.subclazz_student`，均 `status=1`）：

| 前置课 | 在读人数 | 说明 |
|---|---|---|
| `578667318880518144` | 30 | 含 `7489622228` |
| `578851790032846848` | 2 | `7489620185` / `7542292979` |
| `578851839439650816` | 2 | `7489620185` / `7542292979` |

`7489620185` 与 `7542292979` **三门前置课全在读**，适合验证多在读班合并后置范围的场景。

⚠️ **花名册表在 `gaotu` 库不在 `clazz_dist` 库**：`clazz_dist.subclazz_student` 查这几门课恒 0 行，
正确的是 `gaotu.subclazz_student`。查错库极易误判成「学员不在读」。

⚠️ **Feign 入参字段名是 `courseNumberList` 不是 `courseNumbers`**
（`SubclazzStudentByCourseNumberAndUserIdRequest`），传错名字段为空，接口返回 `[]` 且不报错。


## 排查记录二：换活动后仍空 —— 券售卖期过期（2026-09-16 15:26）

**换绑后**：计划 `578668076965308416` 已改绑活动 **`579785105883561984`**（15:24:10），
券范围 3 行均 `is_del=0`（六年级 × 数学/英语/语文），**product-b 已正常返回 3 条**：

```bash
# 实测返回 3 条，说明 scope/在读/后置 全链路已通
curl -sk 'http://<product-b>/feign/preOrderActivity/couponScope/listDisplayableByRenewalPlan' \
  -H 'content-type: application/json' -H 'traffic-env: test-gtbg-dev-3' \
  --data-raw '{"renewMasterNumber":"578668076965308416","userId":"7489622228"}'
```

**但 student-center `/renewal/pre/coupon/list` 仍空**，原因在最后一道券状态闸：

| skuNumber | 券名 | couponStatus | saleStatus | 售卖结束 |
|---|---|---|---|---|
| `579603771085060097` | 案10券2（数学） | 1 ✅ | **1 ❌** | 2026-09-16 15:23:46 |
| `579603756914604033` | 案4券v6（英语） | 1 ✅ | **1 ❌** | 2026-09-16 15:23:39 |
| `579603763728250881` | 案10券1（语文） | 1 ✅ | **1 ❌** | 2026-09-16 15:23:43 |

三张券**售卖期只有 24 小时**（09-15 15:23 ~ 09-16 15:23），在 15:23 全部到期，
`saleStatus` 由 2 回落为 1。展示口径要求 `couponStatus=1` **且** `saleStatus=2`，
故 student-center 短路成空页。

⚠️ **与「排查记录一」是两个不同原因**：一是 scope 行被软删（product-b 就空），
二是券售卖期过期（product-b 有数、student-center 空）。
**按「product-b 有没有数」即可区分这两类**。

### 选券硬要求（造数时必须满足）

1. `couponStatus=1`（使用中）
2. `saleStatus=2`（售卖中）且 **`sale_end_time` 未过期**
3. **售卖期要留足** —— 脚本默认只给 24h，隔天复测必失效。这是本轮踩的坑。

```sql
-- 选当前真正可售的券（本 SQL 已含未过期判断）
SELECT ec.sku_number, c.name, ec.sale_status, FROM_UNIXTIME(ec.sale_end_time/1000) AS sale_end
FROM gaotu.coupon_expand_config ec LEFT JOIN gaotu.coupon c ON c.number = ec.coupon_number
WHERE ec.sale_status = 2 AND ec.sale_end_time > UNIX_TIMESTAMP()*1000 AND c.status = 1
ORDER BY ec.sale_end_time DESC;
```

**推荐长效券**（售卖期到 9/24 之后，适合反复复测）：

| skuNumber | 券名 | 售卖结束 |
|---|---|---|
| `579417711732357121` | Q1 | 2026-09-27 |
| `579394599632533505` | Q8 | 2026-09-26 |
| `579394606764947457` | Q11 | 2026-09-26 |
| `579394614417455105` | Q13 | 2026-09-26 |
| `579563199997704193` | 自动化-自动激活 | 2026-10-15 |

### 年级学科怎么配

**范围本身不用改** —— 计划 `578668076965308416` 的后置课是六年级数学/英语/语文，
现配的 `(16,1) / (16,4) / (16,5)` **完全正确**，product-b 三条全命中。
要做的只是**把过期券换成上表中未过期的券**（活动挂券 + scope 的 `coupon_sku_number` 同步换）。


## 预警邮件怎么验（2026-09-16）

**`sendPreRegistration` 会真的发邮件**，没有「只拼正文不发送」的办法——
`MailServiceIHandler` 是真实 SMTP，无测试环境开关。别指望反射调它来「只看正文」。

**测试数据计划默认不发**：`send()` 里 `is_test_data=1` 且 `renewal.send.test=false` 时直接跳过
（[`InspectService.java:174`](../../../../IdeaProjects/JavaProject/product-server/product-server-domain/src/main/java/com/gaotu/product/service/renewal/InspectService.java)，
判定是 `isTestData == 1 && !sendTest`）。

**2026-09-17 复查订正**：本需求的计划 `578668076965308416` 的 `is_test_data` **已是 `0`**
（2026-09-16 20:09:51 改的，就在 20:12 生成预警之前），因此**它不受这个开关影响，照常发邮件**，
不需要为验证它而打开 `renewal.send.test`。此前本节写的「该计划是 `is_test_data=1`」已过期。

⚠️ **同日发现开关并未按记录复位**：`renewal.send.test` 在 Apollo 上一直是 `true`
（已发布值与草稿都是），2026-09-16 记的「已改回 false」并未真正生效。
2026-09-17 09:48 已改回 `false` 并**发布**（release `20260917094831-release`）。
教训：改 Apollo 后要用 `apollo_diff` / 重新读一次已发布值确认，别只凭记忆记「已改回」。

```
Apollo product-b / TEST: renewal.send.test
  = false   # 常态。计划 is_test_data=0 时不影响本需求验证
  = true    # 仅当要验 is_test_data=1 的计划时临时打开，验完立刻改回并发布
```
打开它的副作用是**所有**测试计划的负责人都会收到预警邮件，注意打扰面。

**收件人**来自续班计划的 `renew_master_ext` 中 `relation_type='ADMIN'` 的行：

```sql
-- 把自己加进负责人以便收测试邮件（accountId 从 CAS 查）
INSERT INTO gaotu.renew_master_ext (renew_master_number, relation_type, relation_value, isdel)
VALUES (578668076965308416, 'ADMIN', '109942', 0);
```

**触发**：`POST /b/renewal/insect/send`（无参，遍历全部「进行中/待开始」计划，
会给其它计划的负责人也发信，注意打扰面）。
