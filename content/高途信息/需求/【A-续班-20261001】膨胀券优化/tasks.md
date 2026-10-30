---
title: 【A-续班-20261001】膨胀券优化 · 任务板
tags: [需求, 任务]
---

# 当前任务板

> **边界**：只记当前范围内仍需跟踪的任务和少量必要交付锚点。
> - 用户手工做的事 → `changelog.md` 的「👤 我」分区
> - TAPD 工时任务 → 只在 `links.md` 存链接，真相源在 TAPD 服务端
>
> 三套编号各自独立且不复用。状态：`待办` `进行中` `已完成` `阻塞` `已取消`

维护规则：状态变化确认后立即更新本文件，并同步 README 进度/卡点/下一步。

## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 备注 |
|---|---|---|---|---|
| T-01 | 模块① 技术方案评审：拍板「下单页的券是否随新推荐规则一起变」 | 已完成 | — | 2026-10-29 所有者确认 **A**：三处共用同一交集实现，下单页券随新规则变（方案① §8.1） |
| T-02 | 模块② 确认工具箱选学员/搜索接口所在服务与仓库 | 已完成 | — | 2026-10-29 定案：= **teacher-tool `ManageSubclazzController#/studentList`**（工具箱 `boss-counselor` 调 `/bgwApi/teacher-tool/manage/subclazz/studentList`）；现手机号批量+姓名模糊，PRD 新增手机号后4位+学员ID批量精确。非 student-center/GPS |
| T-03 | 评审后落地技术方案并进入开发（统一分支 `feature-xuban-20261001`） | 已完成 | — | 2026-10-30：技术方案维持飞书权威（本仓不落 tech_spec 副本），「前端如何改」写入方案 §15 + [[前端如何改]]；后端 6 仓已开发完成（见 T-12~T-19） |
| T-04 | 收敛统一分支 `feature-xuban-20261001` 并同步技术方案/归档 | 已完成 | — | 2026-10-29：从最新 origin/release 建分支（旧占位分支已删）；student-data 复核无改动不建；两篇飞书方案与本地归档已改统一分支口径并回读 |
| T-05 | 逐仓复核改动归属、撤无关仓库分支、模块②按「小灶课」纠正 | 已完成 | — | 2026-10-29：确认需改 6 仓（product-server/promotion/promotion-management/student-center/cart/teacher-tool）；**撤 ces-teach-product / course-center**（教室上限已 32、PRD 不涉及）；剔除 GPS 小班课误判；两篇方案 + 需求入口已回读 |
| T-06 | 方案①「外显抵扣金额」按方向 A 定稿（新增独立字段 + 二选一开关）、消除内部矛盾、修 §6 表格 | 已完成 | — | 2026-10-29：§0/§2.1/§3.2/§4.2/§5/§6/§7/§9 重写为 PRD 版（`external_deductible_amount` + `showExternalDeductAmount` 二选一 + promotion 新增列/DDL）；更正「同一概念/所有者确认」错记；飞书回读确认 |
| T-07 | 模块② 产品答复落入方案②（上限全量/不按业务线、ID 搜索范围同现有），清 §8 待确认 | 已完成 | — | 2026-10-29（张泽灵问/王永诗答）：15→32 直接全量、不需灰度、不按业务线；「小班预约EM改」无特殊含义；ID 搜索范围与现有搜索一致。方案② §4.1/§4.2/§8 + 需求入口 §4 已回读 |
| T-08 | 落实最终确认口径到三份飞书文档 + 归档：下单页 A、页面=家长会、上限 Apollo 配置=32、忽略「C端预约」；删除「这次不用」项 | 已完成 | — | 2026-10-29：方案①§1/§2.2/§4.1/§8 → 下单页 A 已确认；方案②§2.1/§3/§4.1/§8 → 家长会 + 配置化=32 + 忽略C端预约 + 超限文案 15→32；需求入口§2/§3.1/§4.1 → 方向 A + 家长会 + 配置化；README/changelog 删除「这次不用」项 |
| T-09 | 两篇方案收敛为最终版、按「后端反讲权威模板」重写、加可视化示意图 | 已完成 | — | 2026-10-29：overwrite 为规范 14 节结构；新增 3 张 mermaid 画板（①推荐匹配链路、①外显抵扣数据流、②工具箱→teacher-tool 链路） |
| T-10 | 核查「小班课人数上限」来源与 小班预约/C端预约 是否需改，补全 module② 方案与画板 | 已完成 | — | 2026-10-29：上限唯一配置源=teacher-tool Apollo；`parents_metting.sign_count` 为创建时快照（create L283-284）→ ILIVE → 预约。**新建即 32、无需改 ILIVE/预约；存量待产品**。方案②§5画板/§6.1/§8.1/§11.2 + 入口§4.1 + README 已更新 |
| T-11 | TEST 环境上限改 32（teacher-tool Apollo）并记录到方案/归档 | 已完成 | — | 2026-10-30：appId `teacher-tool`/ns `application`/key `parentsMeeting.type.limit.map`，`{3:20;4:30}`→`{3:32;4:30}` 已发布，回读 `{3:32;4:30}`。PROD 未配（默认15）。方案②§6.1/§11.2 + 入口§4.1 + README 已更新 |
| T-12 | 模块① 后端实现：product-server 推荐按年级+使用中且售卖中、C 端样式 showExternalDeductAmount 二选一 | 已完成 | — | 2026-10-30：`PreOrderCouponIntersectService`（按年级、`isCouponDisplayable`）、`ProcessService`（互斥）、`CStyleConfigVO`、`PreOrderActivityProductDTO`(infra)。编译 ✅ |
| T-13 | 模块① 后端实现：promotion 新增列 `external_deductible_amount` 及落库/透传；promotion-management 透传；student-center 回显 | 已完成 | — | 2026-10-30：promotion entity/mapper/BO/DTO/CacheDTO/Repo/Service；promotion-management Req/VO/DTO/DomainService；student-center `PromotionCouponDTO`/`PreOrderCouponVO`。编译 ✅ |
| T-14 | 模块① cart：按 C 端样式开关展示外显/抵扣 + product-server-client 升 1.5.12-SNAPSHOT | 已完成 | — | 2026-10-30：`RenewalMasterWithProcessDTO.showExternalDeductAmount`（product-server 填充）、`PreRegistrationCouponAssembler.resolveDisplayAmount`、`RegistrationService` 透传；cart pom 升 `1.5.12-SNAPSHOT`。编译 ✅ |
| T-15 | 模块② teacher-tool：上限默认 32 + 超限文案 + 选学员 `userIds` 批量精确 | 已完成 | — | 2026-10-30：`ParentsMeetServiceImpl` L180、`ParentsMeetErrorCode`、`SubclazzStudentSearchRequest.userIds`、`ParentsMeetingBiz.listSubclazzStudent`。编译 ✅ |
| T-16 | 6 仓提交并推送统一分支 `feature-xuban-20261001` | 已完成 | — | 2026-10-30：6 仓 commit + push（promotion-management 修 remote 内嵌 token）。 |
| T-17 | 写「前端如何改」到子需求①技术方案 §15 + 归档 `前端如何改.md` | 已完成 | — | 2026-10-30：docx `TmaqdSPepo9Mv9x4fFCcNUEbnYg` rev51 回读确认；本地 [[前端如何改]]。 |
| T-18 | promotion TEST DDL 执行并回读表结构 | 已完成 | — | 2026-10-30：`ALTER TABLE promotion.pre_order_activity_product ADD COLUMN external_deductible_amount BIGINT DEFAULT 0`；回读 `information_schema.COLUMNS` 命中。 |
| T-19 | 部署测试环境（test-gtbg-dev-3）并验证两模块后端 | 已完成 | — | 2026-10-30：8 服务构建发布全部 SUCCESS——teacher-tool 1322156、promotion-management 1322157、student-center 1322158、cart 1322165(重试,首发 1322159 因 client 未发 Nexus 失败)、product-b 1322160、product 1322161、promotion-b 1322162、promotion-c 1322163（client `1.5.12-SNAPSHOT` 已发 Nexus）。 |
| T-20 | 测试环境端到端验证（acl 桥 / invoke_feign / invoke_http + 造数/改数据） | 已完成 | — | **全部验通**：①模块② `getSignCountLimit/allTypeLimit`=32；`listSubclazzStudent` 传 `userIds` 命中 2/未命中空。②模块① **完整 B端 `edit` E2E**：把活动 296 置「待发布+未来时间」后经网关(Cookie) `edit` 保存 `externalDeductibleAmount=5000` → 返回 code 0 → 回读 `promotion.pre_order_activity_product` id=1258 `external=5000`（验后已还原活动状态/时间与字段）。③**二选一互斥**：`saveCStyleConfig` 两开关同开 → 抛「C端外显抵扣金额和抵扣金额二选一，不能同时开启」；合法组合（external 开）保存成功、`ext_config` 落库、`listRenewalWithProcessByNumber` 出参 `show_external_deduct_amount:true`。④**按年级匹配（扩科）**：插范围行 (15,语文) 于活动296，post=(15,数学) → `intersect` **命中**该券（学科不参与）；验后删行。⑤**模块②33拦截/32边界**：`create` 33 人 → code 30033「小灶课学员达到上限」；32 人 → 越过上限校验（返回 code 26 学员退款，非上限）。⑥**10240500 复核**=直连缺登录上下文（非缺陷）。残余：C端页面渲染待前端 §15。 |
| T-21 | 线上待办（**仅记录，不执行**，所有者 2026-10-30「线上先不动」） | 待办 | — | ①PROD Apollo `parentsMeeting.type.limit.map` 配 `{3:32;4:30}`；②promotion PROD DDL 工单（`external_deductible_amount`）；③青舟发布编排（release plan + 服务顺序）；④`product-server-client` 定版 RELEASE（现 `1.5.12-SNAPSHOT`）并同步 cart pom；⑤前端按 §15 实现后联调。 |
| T-24 | 补 ①-8：student-center 下单券列表下发 C 端外显抵扣金额（product-b 券列表行透传） | 已完成 | — | 2026-10-30：PRD/spec 明确 ①-8 **属需求**（§6.2 下单页(student-center)、§6.3 student-center `/renewal/pre/coupon/list`、§8.1 透传链→product-server→student-center）。实现：product-server `PreOrderCouponIntersectResult.couponExternalAmount` + `PreOrderDisplayableCouponRow.externalDeductibleAmount` + `PreOrderDisplayableCouponService` 透传；student-center `ProductDisplayableCouponDTO.externalDeductibleAmount` + `PreOrderCouponBiz` 回填 VO。提交 product-server `1109a3c35`、student-center `889354d67` 并推送。部署 product-b(1322183)/student-center(1322184) SUCCESS，pod eureka UP。**验证**：`listCoupon(renewMasterNumber=578668076965308416)` → **`externalDeductibleAmount:5000`**（trace `student-center.636.17933766634250001`）。 |
| T-23 | 需求文档 vs 后端实现完整性对比 + 2 处带数据 HTTP E2E | 已完成 | — | student-center 列表字段源缺（待确认范围） | 2026-10-30：**造数（DB 改数据复用前置真实场景）**打通「计划 578668076965308416 ↔ 绑定活动 296(券使用中且售卖中) ↔ 在读学员 7489622228」：<br>`cart RegistrationService#preRegistration(7489622228, 578668076965308416, 0, null)` → **product_list 非空，`discount_price=5000`(=外显)**，traceId `cart_gaotu100_com.289.17933755997410037`；<br>`student-center PreOrderCouponBiz#listCoupon(renewMasterNumber=578668076965308416)` → **total:1 非空**（couponStatus1/saleStatus2/availableScope「六年级语文」），但**响应无 `externalDeductibleAmount`**，traceId `student-center.611.17933755984270016`。<br>**发现缺口**：student-center 券列表数据源=coupon-a（`PreOrderCouponAclServiceImpl:56 expandCouponAdapter.queryList`），coupon-a 无该业务字段 → 仅新增 VO 字段无法下发；B端下单弹窗展示外显需 student-center 额外从活动商品 enrich（设计待定，且 PRD「续班服务下单」是否指该弹窗待确认）。 |
| T-22 | 修复 test-gtbg-dev-3 泳道 student-center 未启动 | 已完成 | — | 2026-10-30：根因=**集群资源不足致 pod 无法调度**（pod `status=Pending`、无 nodeIp/无 container；镜像存在，非本次代码问题）。按所有者方法用 `qingzhou_adjust_pod` 将其他非 test 泳道最早 pod 缩容为 0 腾资源（缩：test-eco-3/test-eco-6/test-eco-9 的 student-center，`last_time=28800000`）。build 1322169 SUCCESS 后新 pod `student-center-845599d774-b8vdh` 达 **Running + eureka UP，commit 81b44325**；桥调 `PreOrderCouponBiz#listCoupon` 由该实例返回。其余 5 服务（product/-b、promotion-b/c、promotion-management、cart、teacher-tool）核为 Running/UP。**无代码改动**（故无提交）。方法已记入 `deploy-image/references/deploy-troubleshooting.md`。 |

## R- 反讲整改项

> 来源：飞书反讲文档 `8.1.3 Todo List`（**那份才是真相源**）。
> **上线前必须全部闭环。**

| 编号 | 整改项 | 谁提的 | 状态 | 备注 |
|---|---|---|---|---|
| — | （未评审，暂无） | — | — | — |

## C- case 联调问题

> 来源：case 评审后按 case 联调发现的问题。**提测前必须清完。**

| 编号 | 问题 | 对应 case | 状态 | 备注 |
|---|---|---|---|---|
| — | （未开发，暂无） | — | — | — |

## 阻塞详情

> 每个「阻塞」任务都要写清楚卡在谁/什么事上，否则下个会话判断不了能不能推进。

（当前无阻塞任务；模块②选学员接口已定案。）

## 完成判据

> 判据口径见 `~/.claude/skills/requirement-docs/references/writing-rules.md`（一个任务 = 一个能独立验证的结论；
> 每条写死落点 / 怎么验 / 不达标先查）。
> 完成一项删一行；全部闭环后本节为空。

- T-03 落点：两模块各改动仓 `specs/<迭代>/tech_spec.md` 落地，覆盖推荐规则/C 端展示抵扣金额与上限/ID 搜索。怎么验：spec 头部三项齐全、接口变更类型已标注，与飞书技术方案一致。不达标先查：对照开发操作 SOP（links.md）核对格式。