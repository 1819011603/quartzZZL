---
title: 【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整
aliases: [企微封禁优化, EM纯续推荐范围调整, 纯续关联, 计划关联]
status: 联调中
owner: zhangzeling
branches:
  - product-server:feature-xuban-pure-relation-20261102
  - student-center:feature-xuban-pure-relation-20261102
  - cart:feature-xuban-pure-relation-20261102
  - order:feature-xuban-pure-relation-20261102
  - order:feature-revert-order-mr2391-20261109
  - cart:feature-renewal-preheat-merge-plan-20261110
  - cart:feature-renewal-preheat-small-refactor-20261111
updated: 2026-11-12
tags: [需求]
---

# 【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整

> **Order 对照验证（2026-11-09）**：旧release `317482f9` 已部署test-eco-10并UP，与dev3 `0cc8ef68` 对照完成；两版均支持批量大小班同支付单拆两笔订单并mock支付成功，两版购物车均被资金账户校验拦截。相同编号的运行校验显示旧版跨模式拦截、新版放行；该项为构造输入，不冒充真实商品页面验证。[验证结论](verify.md) / [证据](artifacts/20261109-order-comparison.json)。

> **状态边界修复（2026-11-07）**：重新阅读PRD707，确认推荐时须过滤失效从计划。Cart `04022be8` 已部署TEST/dev3；213项本地测试、16项状态/预热运行检查、10项售卖回归及3项开关回退对照通过，测试状态与开关已恢复。[证据](artifacts/20261107-related-status-fix.json)。当前待QA复测，新版本覆盖率尚未重算。

> **缺陷修复（2026-11-07）**：[TAPD1485167](https://www.tapd.cn/tapd_fe/22531521/bug/detail/1122531521001485167) 已修复并置已解决，待QA复测。Cart `7f749e65` 已部署TEST/dev3；210项本地测试、10项运行断言及B/C开关关闭/恢复对照通过。改前后证据和回退配置见 [verify.md](verify.md)。

> **发布编排复核（2026-11-07）**：后端准入覆盖率已达 **64%≥60%**，任务已终态；Product 72.57%、Cart 64.42%、Order 65.38%，详见[验证及报告](verify.md)。通过补跑真实业务入口达标，未改阈值/排除项。计划24210仍为“规划中”，唯一剩余强卡是 `USER_CASE=0%`：班山功能记录72430显示88/88通过，但冒烟72429仍0/17；原因待核实，不再断言为同步故障。已按页面“刷新”同接口回读，未正式提测。

> 飞书方案（含表结构+接口协议）：https://gaotuedu.feishu.cn/docx/AQEtdIeKzo7P5IxeQEzc7EpxnBe
>
> 上线方案（含 Apollo、DDL、GAIA、ES、历史回溯、灰度与回滚）：https://gaotuedu.feishu.cn/wiki/Uqqyw0MROiPysgk30x8cwhRlnOe；青舟发布计划 24210：https://qingzhou.baijia.com/#/publishArrangement/subPublishArrangement/publishPlan/detail?storyId=&pageNum=1&id=24210&action=audit

## Order 回滚决定（2026-11-09）

用户确认大小班不会共用课程编号，要求完整回滚 Order !2391。旧版真实同单支付已验证，因此本需求移除Order跨模式重复放行逻辑，恢复原有防重复校验；Product/Cart关联推荐不在此次回滚范围。回滚分支 `feature-revert-order-mr2391-20261109` 从最新release建立，提交 `fad87492bd`，[回滚MR !2392](https://git.baijia.com/gaotu/order/-/merge_requests/2392) 已创建并回读为opened，目标release；编译及9项独立行为检查通过。尚未合并或部署，AICR尚无评审结果。

## 当前追加：全局权限与预热键兼容

2026-11-12 已复用飞书 P0 的6组样本重跑 Cart da7b9d06（test-eco-1）：36次查询、6次预热及同实例对照；本地231项通过。运行复现强购标记与总体报名状态不一致，代码确认换课只清所属计划缓存、漏入口缓存；当前有未通过项，详见 [本轮报告](artifacts/20261112-cart-rerun/review.md) 和 [verify.md](verify.md)。

2026-11-11 继续执行 T-21 主从续班「纯续」回归：test-eco-7 直连已验证联报入口23带组合条目51；大班主从预热后 C 端同时返回纯续 productType=2/6004，B端 fromC=0 实时查询正常。真实商品条目23及全类型混排、计划级逐用户缓存回读、开关/历史缓存格仍缺；`RenewalServiceSmallMergedCacheTest` 本轮10/10通过（此前47项相关测试通过），cart-app 全量另有15项既有测试 setup 失败。T-21 仍进行中，未经用户明确允许不发生产灰度或全量。当前证据见 [verify.md](verify.md)，覆盖矩阵见 [回归测试方案](回归测试方案-主从续班计划纯续.md)。

2026-11-10 最新口径：保留原计划管理员和状态置灰逻辑，只叠加全局邮箱前缀白名单 `renewal.pure.relation.admin.email-prefixes`。无参 permission 仅返回全局白名单 grant，前端列表请求一次；每行入口始终显示，可操作=(本计划管理员或白名单)且待开始/进行中，非管理员非名单置灰。save 后端管理员或白名单放行。修正已提交：product-server 5ea561da0/MR866（31项测试通过）、前端1a3a4abb/MR134（12项测试通过）。test-eco-4前端1336713（模板10）目标1a3a4abb已Running并实测10行始终展示、3行管理员可点/7行置灰、一次无参permission；后端1336710（模板1）目标5ea561da已Running/Eureka UP；旧9c09172ac/654307b6不作为本批验收版本。TEST/default新key已由用户发布为tangwen01，config-server回读确认；同浏览器permission=true，8行可操作状态均可点、2行未发布仍灰，非管理员计划可打开抽屉且仍仅1次权限请求。旧accounts key已删除。PROD/default已暂存tangwen01,zhangzeling,wangyongshi；重新读取确认仅此一项新增，发布被Apollo HTTP403拒绝，当前账号zhangzeling无发布权限。config-server仍未命中新key，尚未生效，需有权限人员发布。发布编排24298，MR866/134，TAPD1122531521001397879，未生产发布。

cart追加修复已提交3e012ec2，[MR291](https://git.baijia.com/gaotu/cart/-/merge_requests/291)，32项缓存聚焦回归通过；保持原完整预热键 `renewal:preheat:{plan}:{user}` 及原JSON值结构，读写和换班/换年级清理统一。关联配置缓存保留提交版本隔离；主从各自独立预热、推荐再合并的现有规则保持。test-eco-4 pipeline1336633已完成，目标3e012ec2 Pod 10.218.248.204 Running/Eureka UP；只读调用同计划v1/v2关联版本均返回相同原完整预热键，运行验证通过。

## 当前缓存补强（已完成）

test-eco-4 cart `preheat.cache.enabled=true` 已发布并在 Pod 内回读为 true；样本推荐接口返回后置班，trace `cart_gaotu100_com.291.17943083914781043`。

按owner要求补B端推荐、Redis失效与预热联动：已复现清空关联后旧大班预热仍含从计划。默认开启失效、从未关联的老计划保持原推荐/缓存语义；证据及状态见[当前验证](verify.md)。四项上一批修复结论保持有效，本批已完成TEST验证；关联缓存与预热联动证据见[缓存失效报告](artifacts/20261106-cache-invalidation/README.md)。

## 当前修复（2026-11-06，已完成）

T-18完成：cart **1ebd315d**、product-b/product-c **2593dae78**已推送并部署TEST/test-gtbg-dev-3，目标实例均UP。跨模式换班、后置已购、库存兜底范围、关联缓存四项修复；76项聚焦测试及9组改前后同输入运行对照通过，缓存版本切换/miss→hit有日志证据，DB关系/订单与改前一致。详见[修复与对照](artifacts/20261106-relation-fix/README.md)。

排序兼容性补验：125项回归通过，已保存的6组接口样本商品顺序一致。owner确认“未报名在前、已报名沉底”是原有业务规则，普通计划也应保留；`productList` 的排序调用符合该规则，不列为兼容性缺陷，不收窄范围。原推荐评分/白名单/开课时间规则未改。详见同一[修复与对照](artifacts/20261106-relation-fix/README.md)末节。

**全集保存并发按用户要求不改**。Order 只改购物车 ADD_CART/CART_DETAIL 的跨模式重复校验，未改订单创建、支付、退款等通用订单流程；该链路按续班下单需求验收通过。Product 计划编号前端按字符串传输，后端保留 String 以支持 18 位 ID 与批量精确查询。后续生产配置、QA 用例和外部回溯按上线清单推进，不能替代1485167的QA复测。

## 当前核对与 P0 验证（2026-11-05）

- **最新P0 revision395为按代码改动精简版 v2**：正文按「改了什么 → 关键上下文 → 主链路 → 原链路回归 → 影响范围 → 接口改动与关联回归」组织，步骤在前；正文 131653→33400 字符。补入 code=35 结论（缺 sceneVersionNumber，补参后 code=0）、页面级验证（EM 计划列表 + 关联弹窗 + 页面保存、EES 续班服务页 + 标签弹窗、status1 页面均通过）、C 端入口/选品/价格（入口 trace b3084f50、选品 90ba9ce9、价格 07822e8e）与 7 项剩余范围定性；C 端完整下单/mock 支付仍以接口层 round7 证据为准，完整方法见 [C端验证方法.md](C端验证方法.md)。旧版 revision319 全文与 7 份历史附件引用存档 `artifacts/20261105-p0-concise/feishu-revision-before.xml`，本轮证据 `verification.json` 与页面截图/network 已存 `artifacts/20261105-p0-concise/`。
- **Banshan skill 已固化新写法**：新增「按代码改动写 P0」四规则（先查代码改动、必查前端调用链、直接改动与关联接口回归分开、步骤在前控篇幅），模板同步；`verify_skills.sh` 84 条触发评测 0 失败。
- **本轮后端改动已实际生效**：TEST 目标版本已部署并 Eureka UP；三计划推荐、已购过滤、跨模式加购/下单、缓存失效与预热联动、排序兼容性、企微标签/备注接口均已回读，这些既有样本通过；新样本1485167已修复并完成接口层回归，仍待QA复测。版本、对象、原件、消耗顺序见[当前验证](verify.md)和[后续复核报告](artifacts/20261106-followup-review.md)。
- **上线前置仍保留**：生产配置、QA 用例、历史回溯和部分页面矩阵由对应负责人按上线清单推进；同时保留缺陷1485167的QA复测。
- **分别统计**：[双统计](artifacts/20261105-p0-execution-round11/statistics.json)12卡完整1/准备2/缺失9，原30条完整5/准备19/缺失6；不当业务通过数，实际结果逐项见外部P0。整卡按最弱子场景。
- **Banshan只读对照完成**：[120条逐项比较](artifacts/20261105-p0-execution-round7/banshan-comparison.csv)，线上/冒烟各30条与原30一致，无新业务规则，采纳7处步骤细化。3任务执行0，不复用平台通过。创建时间圈班不覆盖owner最早开课口径，未改测试原集。
- **专用skill已同步**：源/安装banshan-case入口与模板一致，真实输入/公式/代入/结果、筛选纳排、编号语义及集中证据规范已回读；UTF8审计及84路由0失败，见[最终自检](artifacts/20261105-p0-execution-round7/skill-concise-final-check.json)。不重复业务/MR测试。
- MR1528既有[静态比较](artifacts/20261105-p0-detail-round3/mr-comparison.md)继续有效：空标签名称清理、预演/并发/失败反馈可参考；createTime与min(begin_time)冲突，不直接合并，未作运行验证。
- 受控计划/班/课节/辅导班/学员及已付测试订单登记保留；临时碰撞映射删除、备注恢复、标签业务值清空（空行保留）、身份保持Gong177071。父子均终态，无在途业务/部署，无消息发送。没有业务代码或生产改动；自动交接不是所有者暂停。

### round10 定向补验（2026-11-05）

已补真实跨学年/跨年级接口子集及同班小班非好友前置；P0 revision295及证据附件已回读。完整验收仍未完成，详见 `verify.md`。

### round11 当前结果

小班单人页面与默认/续班真好友三变量实际保存对照已补；P0 revision319和附件已回读。原30业务3个所述入口已验证/20子集/7没做，整卡通过0；标签/备注/身份已恢复，无在途操作。[详细交接](artifacts/20261105-p0-execution-round11/handoff.md)。

## 一句话

一个主需求、两个子项：子项1 在 EES 续班服务（大班+小班）补齐默认花名册已有的「加标签/改企微备注」与「学员标签」；子项2 新增续班计划【纯续关联】，使一个纯续链接可含大小班纯续班级并下单。

## 已定共识

- Q1=B：子项1=大班+小班续班服务都做；「企微封禁」属功能缺失、官方接口正常。
- Q2=A：子项2 采用计划间关联（新建 `renew_master_relation` + 推荐并集 + 下单跨模式放行）。
- 推荐并集只并纯续（主+从），扩科不变。
- 单一 Apollo 总开关 `renewal.pure.relation.enabled`（代码默认 true，显式 false 回退；product/cart/order各实例独立配置）。
- 上限 10、状态【待开始/进行中】；**接口收敛为单个「最终确认」save（全量集合差分）**。
- EM关联历史兼容：不刷数；企微历史标签另按回溯方案处理。

## 现在什么情况

- 当前工作单 T 9/11 · R 0/0 · C 2/2：C-2从计划状态变化过滤已修复部署并实测；C-1（1485167）已修复部署且接口层实测通过；T-20/T-21（预热审查修复、纯续全量回归）进行中；当前阶段为“联调中（待QA复测）”，生产配置、QA用例和外部回溯保留为上线前置。
- 本轮TEST采样与保留对象/恢复结论见verify；前端不改、不新部署，不把默认TEST企微结果归给目标feature。
- 下一步按P0剩余缺口推进；已补受控大班筛选，剩余EM/小班/页面场景按已授权TEST范围执行，不重放build或已付单。

## 当前规则与边界

- 关联单向；只合并主从有效前置课，推荐规则、扩科年级/学年/学期仍按主计划；同年级同商品去重，跨年级保留，纯续优先。
- 计划管理员或全局邮箱前缀白名单人员、待开始/进行中可改；上限10且配置可调，保存最终全集差分，取消不落库。
- `renewal.pure.relation.enabled`默认true，product/cart/order实例独立配置；关闭只回单计划，不恢复已写关系/标签/备注。原预热TTL最长26小时保持；关联提交版本或有效从计划集合变化会隔离旧预热，不能继续推荐失效从计划。
- 企微历史圈班按`min(begin_time)≥2026-01-01`，不是创建时间；生产回溯、DDL/GAIA/ES字段及上线配置仍需独立交付证据，不从TEST推断生产就绪。
- **「微信备注」`wechatRemark` 不得登记进 `ees_data.student_field_config`（2026-11-06 更正）**：它是 ES 原生字段（`ads_small_clazz_user.wechatRemark`），登记进 field_config 会被 `GaiaEsMappingService#getNeedFromEsFields` 当作 ODS 字段从 ES fetch 中剔除又无人补值 → 续班服务页「微信备注」恒空。已删除 `continuationService`/`microContinuationService` 的该行，与默认花名册 `smallClazzRoster` 口径一致；test 已回读 `/roster/small/renewal/page` 返回备注值。详见 [tasks T-16](tasks.md) 与 [知识库口径](~/githubDir/quartzZZL/content/高途信息/知识库/cronus/microClazzRoster/continuationService.md)。
- 测试样本已付/已消费有时间顺序；复跑先核当前资格，不重放同单支付、整批build或未选对象。

## 涉及代码与入口

- product-server：`RenewalMasterRelationService#save`、list/save Controller及关联下发；cart：`RenewalService#mergeRelatedPreCourseNumbers`；order：`CartSameClazzOrCourseImpl`。本批product关联缓存及cart已购/换班/库存范围已修，order保持原提交。
- student-center：标签/备注与GAIA/ES下游；实际版本/对象/恢复以[verify.md](verify.md)为准，不能把本地分支当已部署。
- 需求入口及PRD、方案、发布编排、协作责任见[links.md](links.md)；当前任务见[tasks.md](tasks.md)，新造样本方法沿用gaotu-data-seeding入口，端到端入口参考[e2e.md](e2e.md)，实际版本与对象以verify为准。
- **主从续班计划「纯续」全量回归测试方案**见 [回归测试方案-主从续班计划纯续.md](回归测试方案-主从续班计划纯续.md)（商品类型 2/6004/51/23 全覆盖 × 实时计算/预热 × xjob 计划级/UserId 级）。
- 页面/接口契约问题归金瑞琳，业务预期归王永诗；本轮未联系。当前无已确认账号/好友或部署阻塞；按必需边界补未执行项，历史回溯另按既定执行边界安排。

## 2026-11-05 round8 集成记录

历史round8结论见[round8集成报告](artifacts/20261105-p0-version-round8/integration-report.md)、[双统计](artifacts/20261105-p0-version-round8/integration-statistics.json)与[终态](artifacts/20261105-p0-version-round8/integration-final-state.json)为准；原历史执行记录保留。P0/skill表达交付已完成，整体业务验收未全完成，未执行项不记通过。没有新增代码、部署、生产或外部联系。

## 当前边界收敛（round9）

[最新边界报告](artifacts/20261105-p0-boundary-round9/boundary-report.md)与[终态](artifacts/20261105-p0-boundary-round9/final-state.json)包含本轮定向补验及外部P0最新revision。新增小班页面双人标签/恢复筛选、有值从扩科候选不污染；原30业务证据2入口/21子集/7没做，12卡整卡通过仍0。信息12卡1/2/9、原30为4/19/7。必需未完成继续留在T-15，可选全矩阵不升门槛；跨模式已购差异为修复建议、历史回溯为既定外部后续，不阻塞P0文档交付。没有新账号/好友/部署决策缺口；无在途业务或待恢复写入，TEST样本按登记保留。
