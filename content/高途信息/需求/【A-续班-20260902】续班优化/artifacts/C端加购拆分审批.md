---
title: C端膨胀券与组合加购拆分审批
updated: 2026-10-26
tags: [需求, 审批, 验证]
---

# C端膨胀券与组合加购拆分审批

状态：用户已在自审后授权提交、发布测试、两个分支分别验证及更新上线方案；本轮后端拆分验证已完成。未执行生产发布或release合并，页面与支付退款未验项仍保留。

## 审核结论与实现

可拆。当前分支先上线并保留扩科、AI与B端下单，只从cart移出本批C端券/组合增强及详情、算价、6003适配、勾选记忆、组合已报名回退。release原有51组合与预报名券不下线；order组合/券能力仍供B端使用，全部保留。

cart原C端差异为11个生产文件、4个测试与2个仓内说明。相对bdba9e90当前生产代码仅额外保留38行applyExpandSignUp，因为product-b推荐依赖有效订单status2/7过滤已购扩科课程，不能整提交revert a6978058。sellerId=null兼容与原扩科排除均保留。

Git继承：a6978058 → 当前拆除58dcd914 → 新分支独立恢复30e7ccb9。恢复分支基于拆除提交，未来合并才会带回C端能力。新分支生产代码与拆分前a6978058完全一致，仅新增双方共用signUp回归；原未跟踪ExpandSubjectRecommendContractTest保持原样，SHA256为9d09506596adb108e6fe2f16895cee5e9a684d9ca5c01492a8577a587d373bec，未代为提交。

双分支验证发现共享B端缺陷：组合多个子商品校验失败映射同SKU时Collectors.toMap抛Duplicate key。order两个分支同步6a36d7a4b5，最小合并策略保留首条失败提示，不放开禁止下单；公开cartDetail回归先红后绿，连同组合/券10测通过。两泳道真实详情均code0，已购组合canCreateOrder=0。

| 部署 | 当前dev-1提交/状态 | C端dev-3提交/状态 |
|---|---|---|
| gaotu_cart | 58dcd914 / UP | 30e7ccb9 / UP |
| gaotu_order | 6a36d7a4 / UP | 6a36d7a4 / UP |
| gaotu_order_task | 6a36d7a4 / UP | 6a36d7a4 / UP |
| baijia.gaotu.tech.trade.order-ad | 6a36d7a4 / UP | 6a36d7a4 / UP |
| baijia.gaotu.tech.trade.order-b | 6a36d7a4 / UP | 6a36d7a4 / UP |


## 编排与验证

[23819](https://qingzhou.baijia.com/#/publishArrangement/subPublishArrangement/publishPlan/detail?id=23819&action=edit)当前分支先发，14个部署及step2保留，cart/order提测镜像已刷新。

[24038](https://qingzhou.baijia.com/#/publishArrangement/subPublishArrangement/publishPlan/detail?id=24038&action=edit)后续C端：order、order_task、order-ad、order-b、cart五个后端新分支，原8个mweb排在其后，原前端分支feature-renewal-cart-coupon-20261023保留。后端提测test-gtbg-dev-3，前端test-gtbg-dev-1，准出test，step0保持。已有SQL/MQ/Apollo结构化配置内容均保留，服务/环境/配置/提测镜像已读回。

两分支后端分别完成测试部署与实际SHA/Eureka UP核验：当前cart58dcd914在dev-1，C端新cart30e7ccb9在dev-3，order四部署两泳道均6a36d7a4。当前cart16项及扩科JUnit10项、新cart28项、order组合/券/重复校验10项通过。15个C端真实读请求HTTP200/status0，大小班/includeBCart及纯续基线对照通过：dev-1撤去本批8014增强并保留release原51，dev-3完整券范围、组合明细/已报名与纯券/重复券/旧clazzNumbers算价正常。真实选课写接口验证旧分支切年级清选择、新分支跨年级保留与回填/单项取消隔离；验后DMS核原8条选择业务字段一致，年级16恢复。B端两泳道详情HTTP200/code0，均8项（6组合＋2券），已购组合禁止下单且返回首条失败提示，Duplicate key已修复；两条实际trace均命中对应泳道、无错误span。503原configFlag再次HTTP200/code0。23819/24038提测产物与方案已保存读回，原配置与前端保留。dev-3浏览器页面因实际请求固定dev-1及后续浏览器连接不可用，未记验收通过；当前年级payList、真实新增支付退款及剩余P0仍须独立验收，不把后端测试当整体验收。

详细证据见[双分支验证结果](C端拆分双分支验证/final-summary.json)和[[verify]]首节。[飞书上线方案](https://gaotuedu.feishu.cn/wiki/KSDfwlojaipDqWkUcbfckjnwnyd)已回写分批顺序、范围、测试证据与回滚。真实PROD镜像、正式包、最新质量门禁仍须在上线窗口闭环，TEST镜像不作PROD回滚基线。

## 503恢复与配置归因

此前dev-1 product-b无实例，先按用户授权发布原镜像；随后发现TEST/default/application的TestProductExemptPredicate.exempt.shopNumbers缺开头“[”导致启动失败。Apollo发布423816（2026-10-24 10:44:55，wangjinfeng03）引入，修复424667（2026-10-26 15:07:14，zhangzeling）仅补“[”，未恢复此前被移走的首店铺ID；本轮没有自行发布该Apollo修复。外部同事重新构建原commit c1b9225e后UP，原configFlag接口已HTTP200/code0。不能归因为本轮拆分代码或用户修改。


