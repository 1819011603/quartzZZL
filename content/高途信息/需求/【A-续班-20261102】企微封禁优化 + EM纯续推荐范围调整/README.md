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

- **最新P0 revision247按测试侧简洁风格保存**：12张卡正文保留必要前置/短操作/关键预期及实际，计算保留真实输入与简短代入；详细记录集中附录，25项契约和原30条映射保留。业务标识按实际number/bizNumber明确映射，数据库主键另列，无同名bizId不推测。
- **本轮TEST子集已闭环，整体仍未验收**：正常补齐两班真实课节/教师并可售；10/11边界、三计划推荐、仅主资格、同商品碰撞/恢复、双模式同单支付及DB落值；企微大班标签2+1、官方单/双人任务与备注恢复、四组合链接/草稿返回。版本、对象、原件、消耗顺序见[当前验证](verify.md)和[本轮证据](artifacts/20261105-p0-execution-round7/README.md)。
- **仍需推进**：真实异年/异学期、有值从扩科、跨年级/第三件重复、本地缓存组合、优惠/异主体、其余页面、小班企微与历史回溯。续班ES父熔断阻塞筛选；企微实际release-5dce9cdb，目标feature版本未确认。身份/受控好友已取得，不再是必须人工提供条件。
- **分别统计**：[信息完整性](artifacts/20261105-p0-execution-round7/reproducibility-current.json)12卡完整1/准备1/缺失10，原30条完整4/准备17/缺失9；不当业务通过数，实际结果逐项见外部P0。整卡按最弱子场景。
- **Banshan只读对照完成**：[120条逐项比较](artifacts/20261105-p0-execution-round7/banshan-comparison.csv)，线上/冒烟各30条与原30一致，无新业务规则，采纳7处步骤细化。3任务执行0，不复用平台通过。创建时间圈班不覆盖owner最早开课口径，未改测试原集。
- **专用skill已同步**：源/安装banshan-case入口与模板一致，真实输入/公式/代入/结果、筛选纳排、编号语义及集中证据规范已回读；UTF8审计及84路由0失败，见[最终自检](artifacts/20261105-p0-execution-round7/skill-concise-final-check.json)。不重复业务/MR测试。
- MR1528既有[静态比较](artifacts/20261105-p0-detail-round3/mr-comparison.md)继续有效：空标签名称清理、预演/并发/失败反馈可参考；createTime与min(begin_time)冲突，不直接合并，未作运行验证。
- 受控计划/班/课节/辅导班/学员及已付测试订单登记保留；临时碰撞映射删除、备注恢复、标签业务值清空（空行保留）、身份保持Gong177071。父子均终态，无在途业务/部署，无消息发送。没有业务代码或生产改动；自动交接不是所有者暂停。

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

- 当前工作单 T 6/7 · R 0/0 · C 0/0：T-9至T-14交付；T-15包含已验子集及剩余环境阻塞，未标整需求完成。
- 本轮TEST采样与保留对象/恢复结论见verify；前端不改、不新部署，不把默认TEST企微结果归给目标feature。
- 下一步按P0剩余缺口推进；ES恢复后补筛选，其他独立EM/小班/页面场景按已授权TEST范围执行，不重放build或已付单。

## 当前规则与边界

- 关联单向；只合并主从有效前置课，推荐规则、扩科年级/学年/学期仍按主计划；同年级同商品去重，跨年级保留，纯续优先。
- 计划管理员、待开始/进行中可改；上限10且配置可调，保存最终全集差分，取消不落库。
- `renewal.pure.relation.enabled`默认true，product/cart/order实例独立配置；关闭只回单计划，不恢复已写关系/标签/备注。B8预热结果保留最长26小时，不用新链接强行当新缓存。
- 企微历史圈班按`min(begin_time)≥2026-01-01`，不是创建时间；生产回溯、DDL/GAIA/ES字段及上线配置仍需独立交付证据，不从TEST推断生产就绪。
- 测试样本已付/已消费有时间顺序；复跑先核当前资格，不重放同单支付、整批build或未选对象。

## 涉及代码与入口

- product-server：`RenewalMasterRelationService#save`、list/save Controller及关联下发；cart：`RenewalService#mergeRelatedPreCourseNumbers`；order：`CartSameClazzOrCourseImpl`。本轮这些业务代码均未修改。
- student-center：标签/备注与GAIA/ES下游；实际版本/对象/恢复以[verify.md](verify.md)为准，不能把本地分支当已部署。
- 需求入口及PRD、方案、发布编排、协作责任见[links.md](links.md)；当前任务见[tasks.md](tasks.md)，新造样本方法见[build-data.md](build-data.md)，端到端入口参考[e2e.md](e2e.md)，实际版本与对象以verify为准。
- 页面/接口契约问题归金瑞琳，业务预期归王永诗；本轮未联系。ES环境恢复和目标版本核实是续接条件，其他独立场景继续按TEST授权执行。
