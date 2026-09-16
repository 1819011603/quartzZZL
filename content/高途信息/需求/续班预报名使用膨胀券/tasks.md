---
title: 续班预报名使用膨胀券 · 当前任务板
tags: [需求, 任务]
---

# 当前任务板

> 只保留当前仍需推进的任务和直接支撑本轮续接的交付锚点。状态变化后立即同步本文件与 README。

## T- 开发任务

| 编号 | 任务 | 状态 | 阻塞在哪 | 当前结果 / 下一动作 |
|---|---|---|---|---|
| T-13 | 补齐单测与功能自测 | 进行中 | — | B 端选品、详情回显、C 端 scopes/三者交集、预警字段已验证；order/cart 下单算价等存量模块仍需补覆盖，执行入口见 [[verify]]。 |
| T-32 | B 端券列表按续班计划三者交集过滤 | 已完成 | — | product-server `1de4533b9`、student-center `abe8a067d`；范围算法只在 product-server，端到端 6 条用例通过。 |
| T-33 | 券列表补可用范围/持有上限，并双端拦截售罄 | 进行中 | 无售罄券（2026-09-14 复核 40 张全部未售罄） | `availableScope`、`holdLimit` 已验证；可用券基线见 [[verify]]。需把小库存券（如 `579394614104993792`，1/5）买满造出售罄态，再验证列表不可选及活动保存拦截。 |
| T-34 | 持有上限文案与订金班满班拦截 | 进行中 | 缺少真实满班数据 | `holdLimit` 已改字符串文案；需验证 `capacity>0 && signUpCount>=capacity` 被拦截，并回归 `capacity=-1` 放行。 |
| T-35 | 接入 coupon-a-client 1.3.17 的售卖状态与创建人 | 已完成 | — | `saleStatus`/`saleStatusDesc` 与创建人姓名链路已接入并验证。 |
| T-36 | B/C 端统一过滤“使用中且开售中” | 已完成 | — | student-center `3e6bba891`；状态条件由 coupon-a 服务端过滤，端到端 `total=23` 且状态全部符合默认白名单。 |
| T-37 | 打通 student-data 券预报名回溯（`backDwsPresaleHandler`） | 已完成 | — | 2026-09-15：ES `presaleSubject`/`gradePresaleSubject` 验证有值，修复细节见 [[changelog]]。回溯用法与维度见 [[verify]]「怎么回溯」。 |
| T-38 | `presaleOrderTime` 口径订正为「取最新」 | 进行中 | 缺少两张不同支付时间的券 | 2026-09-15 按需求第 75 行改 6 处 `min → max`（大小班 × 增量/全量 4 个文件），4 个单测同步翻转。当前测试券两张支付时间相同（均 11:03:45）测不出差异，需造不同时间的券；另需与马胜确认原「取最早」是否另有上下文。详见 [[changelog]]。 |
| T-40 | 券匹配口径订正：删前置学科过滤 + 学员维度收窄 | 已完成 | — | 2026-09-16 四服务已发 `test-gtbg-dev-3` 并端到端验证通过（8 个场景，见 [[verify]]「学员维度券匹配」）。**扩科券不再被漏**已实测确认。commit：product-server `598c36183`、student-center `76e1e5d9c`。 |
| T-41 | cart C 端对齐学员维度口径 | 已完成 | — | 2026-09-16 已改调 product-c 新接口 `/c/renewMaster/listDisplayableCoupons`，删掉原「计划目标年级」近似口径及失效的 `resolveCouponScope`/`CouponScope`。B/C 端返回**完全一致**；订金班链路实测未受影响。commit：cart `95fe9572`；依赖 `product-server-client:1.5.4-SNAPSHOT`（已发 Nexus）。 |
| T-42 | 打通预报名科目与看板取数（K/I 四条用例） | 已完成 | — | 2026-09-16：跑券回溯 job 6648 写通 MySQL+ES；发现看板 job 5900 真正卡点是学员 `canRenewal=0` 被第二段索引条件滤掉（非「ES 无数据」），`_update_by_query` 改 26 条为可续后快照表出数（26 可续 / 7 已预报名）。完整步骤见 [[verify]]「预报名科目与看板取数」。**原「6 条卡在同一 ES 索引、需等离线跑批」的结论已作废。** |
| T-39 | 验证「券与订金班取并集」 | 待办 | 零数据覆盖（两表交集 0 行） | 需求第 73/74/75 行的并集规则从未被真实数据走过。造数方案（直接插库 / 走真实链路）与 ES 期望值见 [[verify]]「券与订金班并存」，含退券后应只回落券那部分的验证。 |

## 合入现状（2026-09-15，MR 已建）

> MR 链接见 [[links]]「上线 → Merge Request」。源分支统一 `feature-xuban-pre`；
> **目标分支不统一**：promotion 走 `master`，其余走 `release`，依据各仓库 `origin/HEAD`。

| 仓库 | 目标 | vs 目标分支 | MR | 备注 |
|---|---|---|---|---|
| student-data | release | ahead 5 / behind 0 | !1645 | 已同步 release；T-38 改动已提交推送（`0109fc498`，合并马胜 `9fef6f55f` 后为 `dd5b6e587`） |
| student-center | release | ahead 26 / behind 4 | !1437 | origin/HEAD 本就是 release，最干净 |
| product-server | release | ahead 25 / behind 41 | !747 | 用 `feature-xuban-pre`，**不含**建品那 10 个提交 |
| cart | release | ahead 7 / behind 0 | !269 | release 祖先，可直接合 |
| promotion-management | release | ahead 7 / behind 0 | !171 | release 祖先，可直接合 |
| promotion | **master** | ahead 25 / behind 0 | !669 | 见下「为什么走 master」 |
| order | — | — | 不提 | **不在本期范围**（2026-09-15 确认），改动归订单团队 |
| promotion-app | — | — | 不提 | 用户明确排除，仅 spec 文档 |

### 为什么 promotion 走 master

该仓库 `release` 与 `master` **无共同祖先**（`git merge-base` 退出码 1，两条独立历史线，
`release..master` ahead 1 / behind 5924）。本分支从 `master` 拉出且 `behind master = 0`，
合 master 是快进式的正常合并；若强行合 release 会变成无关历史合并，风险极高。
仓库 `origin/HEAD` 也指向 master，与此一致。

> ⚠️ README「必须知道的判据」记有 promotion 存在 `promotion-b` / `promotion-c` 两个部署，
> 改 C 端链路时两个都要发布，上线时注意。

### order 不在本期范围

2026-09-15 确认 order **不随本需求上线**，本期不提 MR。该仓库 `feature-xuban-pre` 上已有 3 个提交
（膨胀券加购与购物车总价），归订单团队自行管理与发布。

> 附记：当时尝试建 MR 时 `gaotu/order` 稳定返回 `LOGIN_EXPIRED`，而同一时刻其它仓库正常、
> 刷新 Cookie 后依旧，判断为无该仓库访问权限。既然已移出本期，无需再申请权限。

### 其它

- 所有 MR 标题均带 **WIP** 前缀，避免被误合。
- `student-data` 合并时发现马胜 14:31 推了 `9fef6f55f`（改同一文件 +183 行），已自动合并无冲突，
  `presaleOrderTime` 取最新的 6 处改动经复核全部保留。
- 各仓库未跟踪的 `.run/`（IDE 配置）未提交。

## 当前阻塞

- T-33：需要可售状态下的售罄券数据；当前 40 张可用券全部未售罄，需造数。
- T-34：需要有限班容且已满班的班级数据。
- T-13（下单部分）：下单须在 `test` 泳道，但 `test` 跑 master 镜像、无本需求代码
  （`/renewal/pre/coupon/list` 返回 404）。需先发版到 `test` 才能验证下单算价。
- T-38：需要两张支付时间不同的券才能验证「取最新」，现有两张时间相同。
- T-39：需要同一学员在同一「学年+学期」下同时有订金班记录和券记录，当前交集为 0，必须造数。

## 完成判据

- T-33 两个入口均使用同一张真实售罄券验证，记录请求、预期和实测。
- T-34 同时覆盖有限满班拦截与不限班容放行。
- T-38 用两张不同支付时间的券验证取到较晚的那个；跨形态（券+订金班）并存时同样取较晚的。
- T-39 并集生效（`presaleSubject` = 订金班 ∪ 券）且退券后只回落券那部分、订金班部分不受影响。
- 补充验证后立即更新 [[verify]]，并同步 README 进度与下一步。
