---
title: 【A-续班-20261001】膨胀券优化 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

> 倒序保留仍能解释当前设计的决策理由。允许压缩和删除无用旧条目；这不是完整会话日志。

---

## 2026-10-30（测试泳道 student-center 拉起）

### 🤖 Claude

- 定：`test-gtbg-dev-3` 泳道 student-center **未启动**根因＝**集群资源不足、pod 无法调度**（`status=Pending`、无 nodeIp、无 container；泳道 imageList 有目标镜像，**非本次代码/镜像问题**，redeploy 同镜像无效）。
- 做：按所有者方法用 `qingzhou_adjust_pod` 把其他非 test 泳道启动最早的 pod 缩容为 0 腾资源——缩 `test-eco-3`（10-22 最早）、`test-eco-6`、`test-eco-9` 的 student-center（`pod_num=0`，`last_time=28800000`=8h 上限）。
- 结果：build `1322169` SUCCESS 后，新 pod `student-center-845599d774-b8vdh` **Running + eureka UP（commit 81b44325）**；acl 桥 `PreOrderCouponBiz#listCoupon` 由该实例返回；其余 5 服务 Running/UP。**无代码改动**。
- 记录：方法写入 `deploy-image/references/deploy-troubleshooting.md`「资源不足→缩容其他泳道最早 pod」；`verify_skills.sh` 通过。

## 2026-10-30（端到端验证全通）

### 🤖 Claude

- 验（缝/网关+改数据，泳道 test-gtbg-dev-3）：
  - **模块① 完整 B端 edit E2E**：先把活动 296 改「待发布+未来时间」造出可编辑样本（券【使用中且售卖中】），经网关 `promotionManagement/preOrderActivity/edit` 保存 `externalDeductibleAmount=5000` → **code 0**，回读 `pre_order_activity_product` **id=1258 external=5000**；验后还原 296 状态/时间与字段。
  - **按年级匹配（扩科对照）**：为活动 296 插范围行 (15,语文)，post=(15,数学)（`post_subjects=[1]`）→ `intersect` **命中** coupon（学科不参与命中）；验后删行。（旧成对逻辑需 (15,1) 对，不会命中。）
  - **模块② 33 拦截/32 边界**：`parentsMeeting/create` 33 人 → `code 30033 小灶课学员达到上限`；32 人 → 越过上限校验（返回 `code 26 学生已退款`）。B端登录态经网关 Cookie 打通（`route=/teacher-tool`）。
  - 二选一互斥、合法组合落库+出参、userIds 搜索：见上一条。
- 结论：两模块**后端**端到端验证通过；仅 **C 端页面渲染待前端 §15 实现后验证**。

## 2026-10-30（测试环境端到端验证）

### 🤖 Claude

- 验（acl 桥 / invoke_feign / invoke_http，泳道 test-gtbg-dev-3）：
  - 模块②：`getSignCountLimit(type=3)=32`、`allTypeLimit` type3=32；`listSubclazzStudent` 传 `userIds=[1449343,5661437961]` 命中 2、传 `[999999999999]` 空。
  - 模块① 落库：经桥 `PreOrderActivityProductRepositoryImpl#batchInsert` 写 `externalDeductibleAmount=5000` → 回读 `promotion.pre_order_activity_product` **id=1257 external_deductible_amount=5000**（已删除该造数行）。
  - 模块① 二选一互斥：`ProcessService#saveCStyleConfig`（计划 574500823697111040 / 节点 579414144554473474，节点未开始）两开关同开 → 抛「C端外显抵扣金额和抵扣金额二选一，不能同时开启」。
  - 模块① 合法组合+出参：`showDiscountAmount=false`+`showExternalDeductAmount=true` 保存成功；节点 `ext_config` 落库含 `showExternalDeductAmount:true`；`listRenewalWithProcessByNumber` 出参 `show_external_deduct_amount:true`（cart 取值链路打通）。
  - `promotion-management detail` 回显 `externalDeductibleAmount`；`PreOrderCouponIntersectService#intersect` 新逻辑正常执行无异常。
- 复核 10240500：**直连容器缺登录上下文**所致（`invoke_feign` 调 edit 报 10240500）；改用网关 `invoke_http`（带 Cookie）后返回真实业务信息——「活动[进行中]只允许更新结束时间」「膨胀券状态不是[使用中且售卖中]」→ **非本次代码缺陷**。
- 未验：按年级 vs 成对（扩科对照）无样本；模块②「新建选 32 通过 / 33 拦截 / 关联校验」（B端 create 需登录态，直连报「登陆信息获取异常」，`invoke_http` 路由 no_match）。
- 定：所有者「只做测试、线上不动、只记待办」；PROD Apollo/DDL/发布编排/client 定版/前端联调 5 项写入 README「线上待办」。

## 2026-10-30（后端实现 + 前端改法沉淀）

### 🤖 Claude

- 定了（所有者最终口径）：**前端由前端同学实现，我们只改后端**；「前端如何改」写入子需求①技术方案 §15（docx `TmaqdSPepo9Mv9x4fFCcNUEbnYg` rev51 回读）并落本地 [[前端如何改]]。前端涉及：模块① C 端（消费 `discountPrice`/`showExternalDeductAmount`）+ B 端 OES（新增列+二选一开关）；模块② boss-counselor 工具箱（改传 `userIds`）。
- 定了（字段落点，所有者确认）：`external_deductible_amount` **券商品级**，存**预报名活动侧** `promotion.pre_order_activity_product`，不挂商品侧表。TEST DDL 已执行并回读（`bigint(20) DEFAULT 0`）。
- 做了（后端实现，6 仓 `feature-xuban-20261001`，编译均过、已提交推送）：
  - product-server：`PreOrderCouponIntersectService`（命中按年级、`isCouponDisplayable` 使用中且售卖中、预警同步）、`ProcessService`（`showExternalDeductAmount` 二选一互斥）、`CStyleConfigVO`、`PreOrderActivityProductDTO`(infra)。
  - promotion：`pre_order_activity_product` 新增列 + entity/mapper/BO/DTO/CacheDTO/Repository/Service 落库与透传（0–100000 校验）。
  - promotion-management：`externalDeductibleAmount` 写入/回显。
  - student-center：`PromotionCouponDTO`/`PreOrderCouponVO` 加字段。
  - cart：按 C 端样式开关选 `discountPrice`；`RenewalMasterWithProcessDTO.showExternalDeductAmount`（product-server 从预报名节点 C 端样式填充）；**product-server-client 升 `1.5.12-SNAPSHOT`**。
  - teacher-tool：上限默认 32、超限文案、选学员 `userIds` 批量精确搜索。
- 部署：test-gtbg-dev-3，8 条 pipeline（见 [[tasks]] T-19）。

### 👤 我

- 所有者：前端有人改；你改完后端，把前端如何改写进技术文档。

---

## 2026-10-30（TEST 上限改 32）

### 🤖 Claude

- 做了：**TEST 环境** teacher-tool Apollo `parentsMeeting.type.limit.map` 由 `{3:20;4:30}` 改为 `{3:32;4:30}` 并**已发布**（appId=`teacher-tool` / ns=`application` / cluster=`default`；releaseKey `20261030160241-ab716f5d9e0ec330`；回读**已发布值** = `{3:32;4:30}`）。
- 注：TEST 原值实为 `{3:20;4:30}`（非 15）；**PROD 未配置该 key**，走代码默认 `{3:15;4:30}`，**上线需在 PROD 配 `{3:32;4:30}`**。
- 记录：方案② §6.1（配置落地）/§11.2（上线方案）、需求入口 §4.1、本地 README（已定共识 + 上线影响面）。
- 遗留：**生产存量** `gaotu.parents_metting.sign_count` 订正为 32 **待产品**（走数据订正/DBA，本次不动库）。

### 👤 我

- 所有者：测试环境改成 32，记录到技术方案。

---

## 2026-10-29（核查小班课上限来源）

### 🤖 Claude

- 定了（核查结论）：小班课人数上限的**唯一配置源 = teacher-tool Apollo `parentsMeeting.type.limit.map`（type=3）**。读取方两条链：
  - **EES 工具箱**：动态读 teacher-tool `getSignCountLimit` / `allTypeLimit`；
  - **快照链**：`ParentsMeetServiceImpl#createParentsMeeting`（L283-284）创建时 `setSignCount(typeLimitMap.get(type))` → 写 `gaotu.parents_metting.sign_count` → ILIVE `feignParentMeet/getParentMeetingInfoFromCache.signCount` → 预约服务「先拦一次」（`size>=signCount` 抛 `IS_FULL`）。
- 定了：**改 Apollo type=3=32 后，EES 与「新建」小灶课自动为 32，无需改 ILIVE / 预约服务代码**；**存量小灶课 `sign_count` 仍 15**，预约/ILIVE 侧对存量仍卡 15，**是否订正（`UPDATE gaotu.parents_metting SET sign_count=32 WHERE type=3`）待产品**。
- 改：方案② §5.1 画板（加入 sign_count→ILIVE→预约链）、§6.1（上限来源与读取方）、§8.1（存量影响）、§11.2（存量订正）；需求入口 §4.1；README 已定共识/上线影响面。

### 👤 我

- 所有者转发讨论，要求核实上限来源与「小班预约 / C端预约」是否需改。

---

## 2026-10-29（技术文档收敛为最终版 + 可视化）

### 🤖 Claude

- 定了：两篇技术方案按**「后端反讲权威模板」**（`XVAidhBptogZIqxhdypciXY5nhd`，同需求前作「续班预报名使用膨胀券」的后端反讲即用此结构）重写为**最终版**，去掉过程/已推翻/待确认噪音；结构 = 变更历史 / 背景（背景资料·名词解释·项目关联方）/ 目标 / 系统环境 / 整体设计（功能架构·核心流程·数据库设计）/ 详细设计（含后端接口·数据迁移·服务切换）/ 接口说明 / 影响管理 / 风险管理 / 数据与监控 / 发布计划（三板斧·上线）/ 非功能性需求 / 整体排期 / 参考资料。
- 定了：新增 3 张 mermaid 画板（与最终口径一致）——方案①「推荐匹配链路」「外显抵扣金额数据流与开关」；方案②「工具箱→teacher-tool 选学员/上限链路」。
- 需求入口维持最终口径（下单页 A / 家长会 / Apollo 配 32 / 忽略 C端预约），无过程噪音。

### 👤 我

- 所有者：只留最终方案、按技术文档规范修订、加可视化。

---

## 2026-10-29（最终确认）

### 🤖 Claude

- 定了（所有者逐条确认，最终口径）：①模块① **下单页券口径 = A（三处共用同一交集实现，下单页券随新规则一起变）**；②模块② **页面 = 家长会**（PRD 详情「答疑课节」不采用）；③模块② **上限 15→32 走 Apollo 配置 `parentsMeeting.type.limit.map` type=3（配置化=32）**；④ PRD 备注「C端预约」**不属本需求、忽略**。
- 定了：**「膨胀券的，这次不用」项作废**——所有者要求「不用管、不用记」，已从两篇技术方案 / 需求入口 / 本地归档移除，不再作为待确认（当前待确认为空）。
- 定了：模块② 超限报错文案 `ParentsMeetErrorCode.STUDENT_EXCEED_RELATION_LIMIT` 由「小班课上限15，自习室上限30」→ **同步「小班课上限32，自习室上限30」**。
- 改：方案① §1/§2.2/§4.1/§8（下单页 A 已确认）；方案② §2.1/§3/§4.1/§8（家长会 + 配置化=32 + 忽略C端预约 + 超限文案）；需求入口 §2/§3.1/§4.1（方向 A + 家长会 + 配置化）；本地 README/tasks/changelog 同步。

### 👤 我

- 所有者确认上述四项口径；要求「这次不用」不用记。

---

## 2026-10-29（方向 A 定稿 + 模块②答复）

### 🤖 Claude

- 定了（**方向 A，所有者确认**）：模块①「外显抵扣金额」按 PRD——**新增独立【C 端外显抵扣金额】字段**，与既有【抵扣金额】**并列、不共用**（配置页新增列、promotion 新增独立列 `external_deductible_amount`、需 DDL）；C 端样式配置**新增配套开关 `showExternalDeductAmount`，与【抵扣金额】开关二选一**（同时开报错），为 0 即使开启也不展示。据此重写方案① §0/§2.1/§3.2/§4.2/§5/§6/§7/§9，消除「同一概念/不新增列/不设二选一」矛盾，**更正错记的「所有者确认=同一概念」**。
- 定了（模块②产品/所有者答复，张泽灵问 / 王永诗答）：**上限 15→32 直接全量、不需要灰度、不按业务线区分**；「小班预约EM改」无特殊含义；**学员 ID 搜索范围与现有搜索一致**（不额外限辅导班、不扩大范围）。据此收敛方案② §4.1/§4.2、清空 §8 待确认；同步需求入口 §4。
- 修：方案① §6 影响面表格错位（DDL 行「项」列被覆盖）已修正并回读整表。
- 仍待（当时）：模块① 下单页券口径（A/B）——已于「2026-10-29（最终确认）」定为 A。

### 👤 我

- 所有者定方向 A（按 PRD 改）；产品答复模块② 3 项待确认。

---

## 2026-10-29（早·定稿）

### 🤖 Claude

- 定了（定稿）：**模块②「选学员搜索」= teacher-tool**，非 student-center。证据：工具箱前端 `boss-counselor/src/pages/Toolbox/SmallClazz` 的 `services/manage.ts`（root=`/bgwApi/teacher-tool`）选学员搜索调 `/manage/subclazz/studentList`、人数上限调 `/manage/subclazz/getSignCountLimit`；现支持手机号（逗号/空格批量）+ 姓名模糊，PRD 新增手机号后4位批量 + 学员ID批量精确。GPS（GpsGroupController/MyStudent）与 student-center 选学员链路排除。
- 定了（定稿）：模块①**下单页的券是否随新推荐规则一起变**仍待产品——已重写为业务语言：A（统一改一处，下单页券跟着变）/ B（按调用方分叉，下单页不变），并推荐 A；含 `PreOrderCouponIntersectService#intersect` 被下单页/C 端/发链接三处共用的证据（方案① §8.1）。
- 定了：模块① 改动仓库已定（product-server/promotion/promotion-management/student-center/cart），仓库归属项从待确认移除。
- 更新：两篇技术方案 + 需求入口 + 本地归档按上述定稿并回读；模块② 全文按「小灶课/辅导班小班课」、无 GPS 残留。

> 注：本段下方原「删除『这次不用』边界项」「外显=抵扣金额同一概念」两条已被 2026-10-29 方向 A 定稿取代（方向 A：新增独立字段 + 二选一开关）；其中「这次不用」项已由所有者确认作废、不再记录。

### 👤 我

- 所有者授权：「可以 修改技术方案」（回应「可否按待确认结论补一版方案」）。

---

## 2026-10-29（早）

### 🤖 Claude

- 定了：本迭代「【A-续班-20261001】膨胀券优化」由两条 PRD 合并为**1 个需求、2 个子需求**交付（模块①膨胀券预报名优化-推荐和外显抵扣金额、模块②小班课学员人数上限修改），对应飞书单一权威需求节点 + 两个模块技术方案子文档。
- 定了：模块①本期在范围内，覆盖两条 P0（推荐规则改全学科券 / 新增外显抵扣金额）。
- 定了：两子需求**共用统一分支 `feature-xuban-20261001`**，不按子需求拆分支。旧占位分支 `feature-xuban-presale-expand-opt`、`feature-small-clazz-limit-and-search` 确认 ahead=0 后已删。
- 定了（2026-10-29 复核后收敛）：真正需改业务代码的只有 **6 仓** —— product-server / promotion / promotion-management / student-center / cart（模块①）+ teacher-tool（模块②，小灶课/辅导班小班课人数上限）。**ces-teach-product / course-center 不需改动、已撤统一分支**（教室形态上限默认已 32、排课随教室上限自动放宽，PRD 不涉及）。
- 定了：模块②的「小班课」= **小灶课 / 辅导班小班课（工具箱-小班课）**，主链路在 teacher-tool；**不是 GPS 小班课**（`GpsGroupController` 等排除）。（2026-10-29 所有者明确）
- 定了：**student-data 无代码改动**（无外显抵扣/推荐交集；家长会/小班课仅 DWS ETL，与选人上限/ID 搜索无关），不建本需求分支，已删其两个旧占位分支。
- 定了：旧占位分支中 product-server / student-center 基于过期 release 头，统一分支一律改为最新 `origin/release`。

### 👤 我

- 所有者明确：本次两篇 PRD 属同一需求的两个小需求，要用统一分支，不要两个分支；要求按「1 需求 + 2 子需求」重整归属与命名，并逐仓复核「是否都要改」；纠正「小班课」= 小灶课的小班课，不是 GPS 小班课。