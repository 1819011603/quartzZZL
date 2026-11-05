# 当前验证与证据（2026-11-05）

## 本次验证范围

- 统一分支 feature-xuban-pure-relation-20261102；后端需求内修复，前端只读。测试均为聚焦子集，不能叫全仓通过。
- product-server `07ba05df6`：批量搜索、保存差分、B端读主窗口、序列化；JDK8/mvn8实际20/0失败/0错误/0跳过。
- cart `a34016fd`：本地缓存DTO隔离、大小班扩科年级/学年学期主计划来源、预热上下文、订单旁路与库存类型、去重、账号校验；11类94/0/0/0。修前缓存1例、学年学期2例失败，修后转绿。已推送，未部署。
- order `0cc8ef68b6`（已推送）：修前e464fa98，三件商品跨模式后同模式重复反例17例5失败；修后17例全绿，另9例H2真实Mapper历史购买回归全绿，合计26/0/0/0。
- 不改B5主规则口径、B8 26h预热延迟；不改前端、生产配置和全量回溯。

## TEST 实际接口（仅当时部署版本）

目标 test-gtbg-dev-3；product-b 镜像 feature-xuban-pure-relation-20261102-07ba05df-20261105102154、cart镜像 feature-xuban-pure-relation-20261102-7bb1fb92-20261104234532，均UP。

| 入口及对象 | 预期/实际 | 证据 |
|---|---|---|
| product-b 关联list，主585960797778243584 | 从586116340522184704，字符串ID、adminList/adminName；code0，符合 | trace 2e78a421-4f0d-4b3f-9724-06752c06c409.0.3；relation-list.json |
| product-b list，number中文逗号主/从两个ID | 精确2条、两计划均进行中、测试数据；code0符合 | trace 2cfdf0ae-617d-4266-8d10-1ff5e387368b.0.3；plan-batch.json |
| 同list，number=not-a-plan | 0条，不退化全量；code0符合 | trace 3bbcfaa1-f95d-4f85-bd6e-c0cef6edb3b4.0.3；plan-invalid.json |
| cart五参getRenewalDetail，7658127801/A | 大班商品585960755422160896/type2与小班586097025945298944/type6004同现 | trace cart_gaotu100_com.292.17938470529730404；cart-current-interface.json。大班sign_up=1，不当新下单样本 |

稳定证据见 [artifacts/20261105-diff-p0](artifacts/20261105-diff-p0/)。完整执行日志在 `/tmp/w1-13ca5996/`；归档保留测试摘要及去除环境属性的Surefire XML。首次探测路由前缀/分页参数错误已修正重跑，不计为产品缺陷；只列最终符合契约的请求。关联list是GET query参数renewMasterNumber，分页current，不是pageNum。

## 已验证、推断未验证、没做

**已验证**：上列本地聚焦测试和固定版本接口；PRD全文/原图、前端固定分支diff和原函数执行、生产iris静态资源读取。

**推断未验证**：新cart修复在线多入口整体效果；当前本地缓存组合是否在生产启用；仅静态资源不能证明每个页面实际加载它，前端分支不等于线上版本。

**没做**：新cart/order部署及新版接口/完整下单；页面实际渲染与标签备注写入；生产DDL/GAIA/ES配置变更与历史全量回溯；全仓测试/并发压测。旧版本历史trace仅作补充，不冒充新版运行结果。部分P0现场账号/样本未准备，文档逐条标明。

## 数据与资源

本轮主worker未写业务表、Apollo或测试购物车，无业务数据需要恢复。子任务亦未部署/业务写入。本轮两子任务及全部构建均已完成，无在途部署/业务写操作。cart a34016fdf206d0163b1dd473c67ac10674ecb4b5、order 0cc8ef68b6c29f1d3101f5fa08ea7ec634050bf9 均已推送同名origin分支，local=remote，工作区干净。AICR查询若为暂无任务只记跳过，不当评审通过。

## 前端版本与剩余差异

- promotions指定分支 `ba1cf8f9`：批量ID、管理员、默认筛选已实现；未保存的新选集合仍按点击顺序，选择阶段未限制第11项；移除确认仅在最终保存阶段，和PRD点击移除即确认有差异。交金瑞琳；是否接受确认时机差异由产品/owner决定。本轮未发消息。
- cronus实际需求分支 `feature-wecom-ban-optimization` / `17ee81cc`：大小班及大班Legacy批量标签/备注、单人标签编辑、studentTags筛选转换均已源码接入，三条formatFilter函数实测通过；不能拿master缺失当未开发。
- iris生产静态群发组件仍旧文案；cronus新分支reach-widget已升0.1.5-beta.4，该包说明链接实现未核。未取得promotions/cronus线上Git SHA，页面效果没做。
- 完整25项契约及来源： [前端/PRD报告](artifacts/20261105-diff-p0/frontend-review.md)。cart映射：[cart报告](artifacts/20261105-diff-p0/cart-review.md)。大班旧腾讯引用正文仍OAuth拦截，已读本次PRD全文及14张原图、3份其他引用全文。

## 需求点 ↔ 实现 ↔ 证据收尾

| 需求编号 | 实现与交付 | 证据/未覆盖 |
|---|---|---|
| Q1-Q4 标签/备注/编辑/筛选 | cronus 17ee81cc接入；student-center/GAIA既有TEST配置 | 三路径函数验证；页面、企微异步结果、ES落值本轮没做 |
| Q5 历史数据回溯 | 沿用min(begin_time)≥2026-01-01方案、圈班→学员 | 大数据任务/字段集/Job外部前置；未执行 |
| Q6-Q7 统一说明链接 | iris/reach-widget两条组件链独立 | 生产iris旧文案已读；新widget内容/发布映射未验证 |
| Q8-Q9 取消/运营规范 | 阶段反馈退费取消；说明规则不扩展为新限流 | PRD253与两份规范全文；不新增无依据代码 |
| E1-E4 单向范围/原规则/去重/扩科 | cart a34016fd隔离缓存并固定主计划课程来源；既有双向库存/订单旁路 | 94例子集全绿；旧部署五参双模式真实返回，新版线上链路未验 |
| E5-E13 管理配置权限/状态/展示/搜索/保存 | product-server 07ba05df；promotions ba1cf8f | product20例、3HTTP查询；三项前端交互差异保留 |
| E14 多入口一致 | cart5/7参及大小班预热路径已核；新修复保留主课程上下文 | 组件回归通过，未逐页面验全入口；大班完整预热RPC未验 |
| E15 下单/主体/优惠 | order 0cc8ef68b6修漏判，主体/优惠逻辑不改 | 17新反例+9H2回归全绿；新版HTTP下单没做，不称端到端通过 |
| E16 B8 | 明确保留26h旧预热窗口 | owner既定决定，未擅自修复或清缓存规避 |

140例=cart94+product20+order26，均0失败/错误/跳过。新增27例（cart10、order17）；不是全仓测试。程序测试不等于12张P0现场卡全部执行。

## 文档回读

P0-case.md 12卡逐条检查均包含现场步骤、通过判据、恢复和实际结果；README/tasks当前进度T6/7一致。归档审计0 ERROR；3 WARN来自既有长README和历史措辞，本轮保留已有成果、以首屏当前快照及本文件为准，不扩大为归档迁移。
