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
  - order:feature-xuban-pre
  - cart:feature-xuban-pre
  - student-center:feature-xuban-pre
updated: 2026-09-08
tags:
  - 需求
---

# 续班预报名使用膨胀券

> **本目录导航**：[[links|🔗 链接中心]] · [[tasks|✅ 任务板]] · [[changelog|📜 会话日志]] · [[verify|🧪 验证手册]]
> 技术方案在飞书反讲文档里（见 [[links]]），本地不留副本。
> 续接这个需求：读完本文件即可。

## 一句话

在现有「订金班预报名」之外新增一种**膨胀券预报名**形态：活动挂膨胀券商品，学员购券即完成预报名，无需进班。

## 需求摘要

> 飞书文档只存链接不落全文，这里是唯一的离线兜底。

- **要解决的问题**：现有预报名只支持「订金班」（挂预报名班级课程商品、付订金占位、可见范围读可续关系）。
  本次新增「膨胀券」形态 —— 活动挂膨胀券商品，学员购券（如付 50 抵 200），**购券即预报名**。
- **给谁用**：老师（花名册发链接 / 下单弹窗加购）、学员（C 端落地页选券）、运营（配置活动与券范围）。
- **两种形态的可见范围口径完全不同**（最容易搞错的地方）：订金班读**可续关系**；膨胀券读**券上配置的年级+学科**，不读可续关系。
- **核心改动**（6 个模块，跨 6 个仓库）：配置（product-server/promotion）、发链接（student-center）、
  B 端下单（product-server/order）、C 端落地页（cart）、字段与指标（student-data，**归马胜**）、预报名预警。
- **判定做完的标准**：六个模块端到端跑通；学员购券后由**券订单消息**驱动落库预报名状态与科目（不需进班）。
- **明确不做**：C 端过滤不沿用老那套；优惠金额展示走统一逻辑、不做配置。

## 已定共识（硬约束，改代码前先扫一眼）

- **`productType` = 8014**。⚠️ 不是 8027 —— 8027 是「课时包商品」，student-center 与 promotion-app 均已占用；也不要用 27（老优惠券概念）。
- **券范围唯一键 = 活动级** `uk_act_grade_subject(activity_number, grade_code, subject_code)`：
  同一活动内「年级+学科」只能出现一次；**同一张券的同一组合在不同活动可各配一次 → 跨活动重复必须放行**（误拦是回归项）。
- **券不参与满赠**（2026-09-08 产品确认），且 promotion-app 本期不改。
- **order 侧只做「膨胀券商品能加购」+ 购物车总价**，下单/支付成功/退款由订单团队自行兼容。
- **除 student-data 外，6 个仓库全是我的活**（含 promotion/promotion-app/order/cart/product-server）。
  反讲文档「项目关联方」写「待定」指的是对方服务对接人待定，**不是这活不是我的**。
- 灰度按**续班计划 ID**；用**膨胀券商品ID**；C 端一券只能买一次、页面多选；加购上限来源=电商接口。
- 三者交集 = 前置班学科 ∩ 后置班年级学科 ∩ 券配置范围，且仅【使用中】。**按「年级+学科」成对判定**，
  分别求交会放行「年级来自A组合、学科来自B组合」的伪命中。

## 现在什么情况

| | |
|---|---|
| 阶段 | 开发中（**B 端券列表自测已通过**） |
| 进度 | T 16/18 · R 0/2 · C 0/0 |
| 排期 | 09-08~09-11 开发 · 09-14 自测 · 09-15~16 联调 · **提测 09-16** |
| 当前卡点 | 建膨胀券活动受阻：promotion 反射桥拒登录 → 改走 arthas，但**青舟登录也过期了，需先重登** |
| 最近更新 | 2026-09-08

**六仓库代码全部提交并推送，编译全绿（BUILD SUCCESS）**，但均未写单测、未跑功能自测。

| 仓库 | 最新 commit |
|---|---|
| student-center | `7425901f5` |
| product-server | `566380d4e` + **未提交**（券状态码 1→2 修正，编译通过） |
| promotion | `938590af5` |
| order | `073dea69e2` |
| cart | `0b529fa4` + **未提交**（DTO 补券字段 + 三处改抛异常 + 成对求交，编译通过） |
| promotion-app | 仅 spec（本期不改代码） |

## 下一步

1. **让用户重登 qingzhou.baijia.com** —— arthas 依赖它换 container_token，当前已过期。
2. **建膨胀券活动**（C 端自测的唯一前提）。⚠️ **不能直接插 DB**：promotion 的券字段
   （couponId/buyAmount/couponStatus/scopes）**不落库**，只存在于 Redis 缓存 DTO，
   且缓存 miss 会从 DB 重建、券字段必为 null。必须走 `PreOrderActivityService#create()`。
   - promotion 反射桥 `acl/compare/service` 拒绝登录（CAS 重定向 / 403），换 host 无效 —— 应用侧鉴权更严
   - 改走 **arthas 进程内调用**：已验证能拿到 bean 实例，OGNL 见 `/tmp/mkact2.ognl`
   - ⚠️ OGNL **字符串必须用单引号**，双引号会被 pty 吃掉导致 ParseException
   - 若报 ClassNotFound，先 `sc -d <类名>` 拿 classloader hash，再 `-c <hash>`
3. 活动建好后配 `pre.order.activity.coupon.renewalPlanIds` → 跑发链接 path 切换 + C 端落地页自测。
   ⚠️ `getByRenewalPlanId` 有 Redis 缓存，改配置不生效先想到缓存。
4. 提交并发布 cart / product-server 改动到 test-gtbg-dev-3。
5. 找电商（邓俊兵）要券商品接口，确认券状态码枚举（当前按 1待开始/2使用中/3已结束/4已下线）
6. 跟前端对齐三个新字段名：`postProductId` / `postProductName` / `activityType`
7. 定 `scopes` 落库方 —— **本轮发现 promotion 侧根本不落库**，这条已不只是"回显丢字段"，
   而是「缓存过期后券信息整体丢失」，优先级应提高
8. R-01 找王永诗；R-02 问清「测试冲突」指什么

## 待确认

> 真相源是飞书待办表，这里是镜像。开发期新增的 8 条见 [[tasks]] 末尾。

- [ ] 一个膨胀券只能在一个活动中用么？ —— 等王永诗（**注意**：券范围唯一键已按「活动级、跨活动放行」定稿，此条若答"只能一个活动"则需改口径）
- [ ] 测试冲突问题 —— 无处理人
- [ ] 一个前置班级只能在一个续班计划上，但班级可脱离续班计划配置，如何控制 —— 无处理人
- [ ] 新续班计划配置的预报名活动 vs 老的非续班计划配置并存，是否并集 —— 等马胜
- [ ] 历史预报名活动统一刷成订金班预报名 —— 等马胜（**待上线后处理**，不在本次开发内）

## 涉及的代码

| 仓库 | 分支 | 关键位置 |
|---|---|---|
| /Users/gaotu/IdeaProjects/JavaProject/student-center | feature-xuban-pre | 券选品接口、发链接分流、券列表 mock |
| /Users/gaotu/IdeaProjects/JavaProject/product-server | feature-xuban-pre | 活动配置、券范围表、三者交集、预警、C端样式 |
| /Users/gaotu/IdeaProjects/JavaProject/promotion | feature-xuban-pre | 活动形式、券可用范围、baseUrl 分叉 |
| /Users/gaotu/IdeaProjects/JavaProject/order | feature-xuban-pre | 仅加购 + 购物车总价 |
| /Users/gaotu/IdeaProjects/JavaProject/cart | feature-xuban-pre | C 端落地页取数与算价 |
| /Users/gaotu/IdeaProjects/JavaProject/promotion-app | feature-xuban-pre | 仅 spec；满赠校验在此服务，本期不改 |
| student-data | — | **不要动**，B 端收数归马胜 |

## 上线影响面

> 新建的表 / Apollo key / 代课权限逐项清单 → **见 [[verify]] 末尾「新建的东西」**（那份是上线 checklist 的原料）。

| 配置项 | 涉及 |
|---|---|
| MySQL DDL | ✅ 一张新表，测试已建、线上待建 |
| Apollo | ✅ 5 个 key，其中 `renewal.content.config.map` **不配则老师端无入口** |
| 代课接口权限 | ✅ 2 个新接口待登记 |
| MQ | ❌ 券订单消息由订单团队发 |
| ES | ❌ 写 ES 归马胜 |

## 必须知过的坑

- **8027 ≠ 膨胀券**，是课时包商品，两个仓库都已占用。膨胀券是 **8014**。
- **Apollo 没有泳道 cluster 是正常的** —— 读不到会自动回落 `default`，不必为泳道单独建 cluster。
  别把「查泳道 cluster 404」当成环境不可用（我犯过这个错）。
- **泳道名不能反推逻辑环境**：`test-gtbg-dev-3` 属于 **dev** 不是 test，只查 environment=test
  会误判「该泳道没 pod」。已修进 `pod_term.py pods`（默认聚合 test+dev，带 `--ns` 过滤）。
- **promotion 券字段不落库**，只在 Redis 缓存里；插 DB 造不出可用的膨胀券活动。
- **cart 侧三处已改为抛异常**（price / scopes / deductibleAmount）：上游字段缺失时落地页直接失败，
  **这是预期行为**（不能静默失败）。别把它当回归 bug 去「修回」返 0。
- **成对求交**：cart 原本把年级、学科**分别求交**，会放行「年级来自 A 组合、学科来自 B 组合」的
  伪命中，已改为按 `PreOrderActivityCouponScopeDTO` 整对比对，并删掉诱发该写法的 `intersect()` helper。
