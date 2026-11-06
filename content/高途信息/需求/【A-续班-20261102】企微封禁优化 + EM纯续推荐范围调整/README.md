---
title: 【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整
aliases: [企微封禁优化, EM纯续推荐范围调整, 纯续关联, 计划关联]
status: 开发中
owner: zhangzeling
branches:
  - product-server:feature-xuban-pure-relation-20261102
  - student-center:feature-xuban-pure-relation-20261102
  - cart:feature-xuban-pure-relation-20261102
  - order:feature-xuban-pure-relation-20261102
updated: 2026-11-05
tags: [需求]
---

# 【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整

> 飞书方案（含表结构+接口协议）：https://gaotuedu.feishu.cn/docx/AQEtdIeKzo7P5IxeQEzc7EpxnBe

## 当前核对与 P0 验证（2026-11-05）

- **最新P0 revision375为按代码改动精简版 v2**：正文按「改了什么 → 关键上下文 → 主链路 → 原链路回归 → 影响范围 → 接口改动与关联回归」组织，步骤在前；正文 131653→33050 字符。补入 code=35 结论（缺 sceneVersionNumber，补参后 code=0）、页面级验证（EM 计划列表 + 关联弹窗 + 页面保存、EES 续班服务页 + 标签弹窗、status1 页面均通过）、C 端入口/选品/价格（入口 trace b3084f50、选品 90ba9ce9、价格 07822e8e）与 7 项剩余范围定性；C 端完整下单/mock 支付仍以接口层 round7 证据为准，完整方法见 [C端验证方法.md](C端验证方法.md)。旧版 revision319 全文与 7 份历史附件引用存档 `artifacts/20261105-p0-concise/feishu-revision-before.xml`，本轮证据 `verification.json` 与页面截图/network 已存 `artifacts/20261105-p0-concise/`。
- **Banshan skill 已固化新写法**：新增「按代码改动写 P0」四规则（先查代码改动、必查前端调用链、直接改动与关联接口回归分开、步骤在前控篇幅），模板同步；`verify_skills.sh` 84 条触发评测 0 失败。
- **本轮TEST子集已闭环，整体仍未验收**：正常补齐两班真实课节/教师并可售；10/11边界、三计划推荐、仅主资格、同商品碰撞/恢复、双模式同单支付及DB落值；企微大班标签2+1、官方单/双人任务与备注恢复、四组合链接/草稿返回。版本、对象、原件、消耗顺序见[当前验证](verify.md)和[本轮证据](artifacts/20261105-p0-execution-round7/README.md)。
- **仍需推进**：小班批量第三未选/好友成功、模板其余边界、纯续必要入口/C端、缓存必要命中回退、优惠/异主体及历史回溯；跨学年/跨年级接口、小班单人页面和默认三变量对照已补子集。企微目标前端17ee81cc已确认；两后端实例本轮受控ES筛选成功，历史父熔断不再列当前统一阻塞。身份/受控好友已取得，不再是必须人工提供条件。
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

- 当前工作单 T 6/7 · R 0/0 · C 0/0：T-9至T-14交付；T-15包含已验子集及必需未执行/外部回溯后续，未标整需求完成。
- 本轮TEST采样与保留对象/恢复结论见verify；前端不改、不新部署，不把默认TEST企微结果归给目标feature。
- 下一步按P0剩余缺口推进；已补受控大班筛选，剩余EM/小班/页面场景按已授权TEST范围执行，不重放build或已付单。

## 当前规则与边界

- 关联单向；只合并主从有效前置课，推荐规则、扩科年级/学年/学期仍按主计划；同年级同商品去重，跨年级保留，纯续优先。
- 计划管理员、待开始/进行中可改；上限10且配置可调，保存最终全集差分，取消不落库。
- `renewal.pure.relation.enabled`默认true，product/cart/order实例独立配置；关闭只回单计划，不恢复已写关系/标签/备注。B8预热结果保留最长26小时，不用新链接强行当新缓存。
- 企微历史圈班按`min(begin_time)≥2026-01-01`，不是创建时间；生产回溯、DDL/GAIA/ES字段及上线配置仍需独立交付证据，不从TEST推断生产就绪。
- 测试样本已付/已消费有时间顺序；复跑先核当前资格，不重放同单支付、整批build或未选对象。

## 涉及代码与入口

- product-server：`RenewalMasterRelationService#save`、list/save Controller及关联下发；cart：`RenewalService#mergeRelatedPreCourseNumbers`；order：`CartSameClazzOrCourseImpl`。本轮这些业务代码均未修改。
- student-center：标签/备注与GAIA/ES下游；实际版本/对象/恢复以[verify.md](verify.md)为准，不能把本地分支当已部署。
- 需求入口及PRD、方案、发布编排、协作责任见[links.md](links.md)；当前任务见[tasks.md](tasks.md)，新造样本方法沿用gaotu-data-seeding入口，端到端入口参考[e2e.md](e2e.md)，实际版本与对象以verify为准。
- 页面/接口契约问题归金瑞琳，业务预期归王永诗；本轮未联系。当前无已确认账号/好友或部署阻塞；按必需边界补未执行项，历史回溯另按既定执行边界安排。

## 2026-11-05 round8 集成记录

历史round8结论见[round8集成报告](artifacts/20261105-p0-version-round8/integration-report.md)、[双统计](artifacts/20261105-p0-version-round8/integration-statistics.json)与[终态](artifacts/20261105-p0-version-round8/integration-final-state.json)为准；原历史执行记录保留。P0/skill表达交付已完成，整体业务验收未全完成，未执行项不记通过。没有新增代码、部署、生产或外部联系。

## 当前边界收敛（round9）

[最新边界报告](artifacts/20261105-p0-boundary-round9/boundary-report.md)与[终态](artifacts/20261105-p0-boundary-round9/final-state.json)包含本轮定向补验及外部P0最新revision。新增小班页面双人标签/恢复筛选、有值从扩科候选不污染；原30业务证据2入口/21子集/7没做，12卡整卡通过仍0。信息12卡1/2/9、原30为4/19/7。必需未完成继续留在T-15，可选全矩阵不升门槛；跨模式已购差异为修复建议、历史回溯为既定外部后续，不阻塞P0文档交付。没有新账号/好友/部署决策缺口；无在途业务或待恢复写入，TEST样本按登记保留。
