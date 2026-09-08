---
title: 续班预报名使用膨胀券 · 会话日志
tags: [需求, 日志]
---

# 会话日志

> **只追加，倒序（新的在上）。任何时候不许改写或删除旧条目。**
> 结论错了 → 追加一条新的说明它错了，不是把旧的抹掉。
>
> 两个执行者在**同一条时间轴**上：`🤖 Claude` 和 `👤 我`。

---

## 2026-09-08（第四次会话 · B 端自测通过）

### 🤖 Claude
- **订正上一条会话的两个错误结论**（原条目保留不改，按规矩追加说明）：
  1. 「泳道 test-gtbg-dev-3 是空壳、不可用」**是错的**。Apollo 查不到泳道 cluster 会**自动回落 default**，
     404 不代表环境不可用；且用户 16:37 已发布镜像，我查 pod 的时刻在那之前。
     实际 student-center 在该泳道 Running / eureka UP。
  2. 「promotion 尚未下发 scopes 与券购买金额」**也是错的**。promotion 侧
     `PreOrderActivityProductDTO` 早已有 `buyAmount` / `couponId` / `couponStatus` / `scopes` 字段，
     缺的是 **cart 自己的 client DTO 没同步**这些字段 —— 是我方要补，不是等上游。
- **Apollo 已配置并发布**（default cluster，release `20260908171459`）：
  `pre.order.coupon.mock.enabled=true`、`pre.order.coupon.product.type=8014`。
- **B 端券列表自测通过**（泳道反射调 `PreOrderCouponBiz#listCoupon`）：
  空条件 3 条 mock 返 2 条（已结束被过滤）、productType 全 8014、状态文案与 selectable 正确、
  券名模糊查询与 couponIdList 批量精确查询均正确。
- **cart 侧改动**（未提交，编译通过）：
  - `cart-client` 补齐 `PreOrderActivityProductDTO` 的 5 个券字段 + 新增 `PreOrderActivityCouponScopeDTO`
  - price / scopes / deductibleAmount 三处由「打日志返 0/空」改为**抛 `CommonsException`**（用户要求不能静默失败）
  - **修掉一个真 bug**：原来把券范围的年级、学科**分别求交**，会放行「年级来自 A 组合、
    学科来自 B 组合」的伪命中；改为按整对比对，并删掉诱发该写法的 `intersect()` helper。
    （product-server 的同源实现本来就是对的，是 cart 这边漂了）

### 留给下次
- C 端自测卡在**没有 type=2 膨胀券活动**，与环境无关：库里活动全是 type=1，
  scope 表的 9001/9002/9003 是假活动号。需先在 B 端建活动、挂券、配范围。
- cart 改动待提交并发布到 test-gtbg-dev-3。
- 注意 `getByRenewalPlanId` 有 Redis 缓存，改配置不生效时先想到缓存。

---

## 2026-09-08（第三次会话 · 自测准备）

### 🤖 Claude
- **自测未能真正开跑 —— 环境是空壳**。三方证据一致：Apollo 无 `student-center/TEST/test-gtbg-dev-3`
  这个 cluster（404）；青舟环境注册表里该子环境**存在**（`envInfoId=314`），但 student-center 与
  product-server **从未在该 namespace 部署过任何 pod**。当前唯一有 UP pod 的是默认 `test`。
  → 之前 verify.md 记的「泳道 test-gtbg-dev-3」只是计划值，从未被验证过可用。已订正。
- **发现第二个前置阻塞**：4 个新 Apollo key 在 `default` cluster 里一个都没配（核对了全量 564 项）。
  其中 `pre.order.activity.coupon.renewalPlanIds` 不配，`PreOrderActivityFormResolver#resolve`
  就永远兜底成订金班，**膨胀券链路根本进不去**——不先配这个，自测跑的还是订金班老路径。
- **静态自测（可离线做的部分）已完成，结论是好的**：
  - 三者交集 `PreOrderCouponIntersectService` **确认是按「年级+学科」成对判定**（判定始终锚定单行
    `PreOrderActivityCouponScope`，不存在把 grade/subject 拆成两个集合分别求交的写法），
    不会产生「年级来自 A 组合、学科来自 B 组合」的伪命中。用库里 5 行真实数据推演 3 个场景全部符合预期。
  - 唯一键 `uk_act_grade_subject` 与定稿口径一致：DB 查证同活动内无重复、801400001 在 9001/9002
    跨活动共存。upsert SQL 确认会把 `is_del` 置回 0，软删行可被正确复活。
- **按用户要求「不能静默失败，抛异常」改造 cart 侧三处**（`PreRegistrationCouponAssembler`）：
  `resolveBuyAmount`(price)、`resolveCouponScope`(券可用范围)、`deductibleAmount` 校验，
  原本都是「打条 error 日志然后返回 0 / 空范围」，现改为抛 `CommonsException(ErrorType.SYSTEM)`。
  cart-app 编译通过。
  ⚠️ **副作用（预期内）**：promotion 尚未下发 `scopes` 与券购买金额，所以 **C 端落地页现在必然 500**，
  不再是「空态」。这正是改造的目的——空态与「本来就没配券」无法区分，属于静默失败。

### 留给下次
- **先做环境决策**（T-13）：用默认 `test` 泳道，还是把 test-gtbg-dev-3 补全（发两次镜像 + 建 Apollo cluster）。
  这个决定卡住后面所有自测。
- 环境定了之后：配 4 个 Apollo key（尤其白名单）→ 部署 → 才能跑 B 端券选品与发链接自测。
- C 端自测**不要等**，它卡在 promotion 补 `scopes` + 券购买金额字段，与环境无关。

---

## 2026-09-08（第二次会话 · 开发）

### 🤖 Claude
- **归属口径纠正两次**：先漏了 product-server，后漏了 cart/order。最终确认**除 student-data 外 6 个仓库全是我的活**。
  已写进项目 memory（`project_xuban_pre_coupon_ownership.md`）—— 反讲文档「项目关联方」写「待定」指对方对接人待定，不是这活不是我的。
- **完成 T-01~T-12**，六仓库代码全部提交推送，**五个仓库编译 BUILD SUCCESS**（agent 自报的编译风险点实际都没问题）。
- **发现并修掉 4 个真实缺陷**（都核到行号）：
  1. `PreOrderActivityService:948` 原 `if(type!=1) throw` —— **膨胀券活动根本存不进去**，硬阻塞
  2. `PreOrderActivityService:192-193` 对券订单 `clazzVOMap.get()` 返回 null 后直接解引用 —— **整页数据丢失**。
     这才是「膨胀券订单进不了意向列表」的根因，不是过滤条件漏了
  3. `RenewalInsectController` 原 `/deal` 无条件 `return success(null)`，没包 `handleRequest` ——
     **只在 service 加校验完全无效**，运营点了静默无反应（正是 spec 警告的失败态）
  4. `CartService.getTotalPrice` 券落兜底 `return 0L` —— 购物车券显示 ¥0 且不报错
- **推翻两处文档判断**：① cart 的 `ProductGroupRequest:44` **本来就有 `skuNumbers`**，反讲写「只有两个桶」是漏了，
  「三选一新增桶」前提不成立 → 复用现成字段，后端算价零改动；② 满赠 `fullGive/validateNew` **在 promotion-app**
  （第六个服务，反讲写 promotion 并标「路径待核实」是找错了服务），已 clone 并出 spec。
- **`productType` 定为 8014**（原文档举例 8027）。查到 **8027 在两个仓库都已被「课时包商品」占用**
  （student-center `OlsStudentArchivesBiz:184`、promotion-app `ProductTypeEnum:59`），8027 用不了。
- **order 侧范围收敛**：初版做多了 327 行（券订单事件消息/批量下单校验/满赠剔券），已 revert。
- **测试环境建表 + 造数**：`gaotu.renewal_pre_order_activity_coupon_scope`（马胜加了 `renewal_` 前缀，代码同步改名）。
  实例是 **`gaotu_polar_test_03`/cluster 142**（依据 Apollo `product` 的 `jdbc.gaotu.url`，不是线上那个 `gaotu-center-prod`）。
  插 5 行 scope 数据，**顺手验了唯一键两个方向**：同活动跨券重复被拦（`Duplicate entry '9001-21-1'`）、跨活动重复放行 —— 与定稿口径一致。
- **券列表 Apollo mock**（T-08）解除电商接口阻塞；刻意**不做「真接口失败自动回落 mock」**，否则联调期真实故障会被假数据掩盖。
- `process/list` 出参补 `activityType` 区分订金班/膨胀券（复用已有活动详情，零额外 RPC）。
- TAPD 排期重整：从 13 条压到 6 条、每天 8h，按「周五开发完 → 周一自测 → 后两天联调」。

### 我做错的地方（留档）
- **把排期写进了 spec markdown 并 push**，用户要的是 TAPD 任务 → 已 force push 回滚两个仓库。
- **TAPD 任务反复增删改 4 轮**（建 8 条 → 删 8 条重建 → 两次改日期 → 删 5 条合并）。
  根因是创建前没问清自测/联调天数、提测日能否干活、排序偏好。
- **漏派 4 条任务**（发链接分流/三者交集/预警/C端样式），因为派 agent 时任务描述给窄了 → 补派已完成。
- 一度说「三个仓库都完成了」，实际有 4 条没做 → 之后改为逐条核代码再回答。

### 👤 我
- 手工建了线上表并加 `renewal_` 前缀（截图确认库 `gaotu`、实例 `gaotu-center-prod`）
- 定了：`productType` 用 8014；券不参与满赠；order 侧只管加购；promotion-app 本期不改
- 定了排期口径：周五开发完、周一自测、后两天联调，每天 8 工时

### 留给下次
- **T-13 自测**：开 `pre.order.coupon.mock.enabled=true` 跑券列表 → 活动配置 → 三者交集
- 找电商（邓俊兵）要券商品接口；对齐券状态码枚举
- 跟前端对齐 `postProductId`/`postProductName`/`activityType` 三个新字段名
- 定 `scopes` 落库方 —— 影响 B 端回显是否丢券范围
- ⚠️ student-center 与 product-server 做过 **force push**，**不要直接 `git pull`**

---

## 2026-09-08

### 🤖 Claude
- 建本需求归档目录，从飞书拉齐现状：
  - 需求 wiki 节点 + 5 份子文档（后端反讲 / 整体技术方案 / 技术依赖梳理 / 2 份前端反讲）
  - 后端反讲 v0.2（masheng 2026-09-06）：读出 6 大模块划分与 7 条目标
  - 待办表 21 条：15 条 DONE（已定共识写进 README）、**5 条 TODO**
  - 6 个仓库的 tech_spec 链接，路径统一 `specs/004-xuban-pre/tech_spec.md`
- 把待办表「技术反讲」阶段的 2 条 TODO 立为 `R-01`/`R-02`，均标**阻塞**
- 判定当前阶段为 **反讲评审**（反讲文档已到 v0.2，但技术反讲阶段仍有未闭环项）

### 留给下次
- R-01 找王永诗；R-02 先问清楚「测试冲突」指什么
- 两条清完再按 6 个模块拆 `T-` 开发任务
- README「上线影响面」五项目前全是"待定"，读完反讲的「数据库设计」和发布计划后填实
