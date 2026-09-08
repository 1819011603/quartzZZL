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
- 改了两个 skill：`tapd-task` 加「建任务前必问 4 件事 + 不要反复重建 + 倒推排期脚本」；
  `requirement-docs` 的 README 行数上限 120 → 500。

### 我做错的地方（留档）
- **把排期写进了 spec markdown 并 push**，用户要的是 TAPD 任务 → 已 force push 回滚两个仓库。
- **TAPD 任务反复增删改 4 轮**（建 8 条 → 删 8 条重建 → 两次改日期 → 删 5 条合并）。
  根因是创建前没问清自测/联调天数、提测日能否干活、排序偏好 → 已把「必问 4 件事」写进 `tapd-task` skill 防复发。
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
