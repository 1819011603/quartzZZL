# 当前验证与证据（2026-11-05）

## 当前核查结果（任务e9aebdb9，2026-11-05）

- 完整工作单与证据入口：[运行核验](artifacts/20261105-runtime-w1/runtime-review.md)，[backend-report.md](artifacts/20261105-runtime-w1/backend-report.md)，[qiwei-report.md](artifacts/20261105-runtime-w1/qiwei-report.md)。本节为当前状态，后续轮次记录按各自时间/版本复用，不将旧“未部署/未找到表”继续作为当前事实。
- owner硬约束已落实：两个子项分别真实调用；无运行证据确认问题不改/提交；直连先核Pod/Eureka的IP端口/版本/泳道，失败两次换入口或报阻塞。本轮无代码改动、业务写入、部署或Apollo修改。
- **已验证：EM管理**。product-b 07ba05df，10.218.248.248:28688，Host PRODUCT-B、traffic-env=test-gtbg-dev-3、b_client=EES；A关联返回B及字符串ID/管理员，trace product-b.258.17938612055100011；文档curl复跑.261.17938612536690012。网关批量A/B total2（e919e0e0）、非法total0（a345a13d）、B关联空（4899b6bb）。原始文件均在上述目录。
- **已验证：EM推荐子集**。cart a34016fd，10.218.237.47:28688；A五/七参双模式，七参纯续2件、扩科仅主grade16两件（cart_gaotu100_com.298.17938612420770116）；B只自身小班（.299.17938612431590122）。重复A trace .301.17938612443150115的Pod日志证实前置课/订单旁路正缓存hit=true；A自身课程回读未混入B。
- **已复用：显式B→A反向接口**。原始保存458e4e7b、推荐cart_gaotu100_com.299.17938604090680110、清理094a3ee4日志已定位，同a34016fd，不重放；DB id14软删/Apollo恢复原件本轮未找到，仅归档记录。当前B为空且只自身已另验。
- **已验证：企微读取子集**。student-center无test-gtbg-dev-3实例；固定默认TEST 10.255.176.174:28688、release-5dce9cdb，学员7489648821/班574882679202260992返回标签[2]/需中关注，与DB id120542一致，trace student-center.900338.17938614686501583。不是目标泳道/页面/新写标签验收。
- **已核实失败前置**：默认TEST好友接口直连code3（student-center.900339.17938614405711575）；真实网关code0/resultStatus=false（6aa83947）。不能称备注成功或账号被封禁。错误班号行120554实际末尾4300，非目标4320；初读tags=1,2、后续外部变空，不由本轮恢复，原请求精度原因未验证。
- **已核版本**：cart a34016fd、order/order-b 0cc8ef68、product-b 07ba05df均目标泳道UP；product-c仍ab120d4e。product/cart/order本地=远端且干净；student-center本地同名分支无差异且远端无同名分支，不创建占位。
- **程序测试记录**：140例既有计数(20+94+26)无失败，未重跑。单测不能证明运行修复生效；order既有跨模式/真重复trace只复用归档，未重新下单。
- **推断未验证/没做**：不同学年学期及从年级扩科候选隔离、碰撞去重/跨年级、本地缓存组合/负缓存/异常/回退、新版完整下单/主体/优惠；企微标签写-幂等-恢复、真实好友备注和封禁对照、页面筛选/说明链接、ES与历史全量回溯。需独占测试对象/HTTP身份及外部交付，不冒称全测通。
- P0 Wiki KeCZwdJTBiIJDJkX8lRcGb9gnCs对应docx ZQUXdlDxWoknJhxu914c2uVYnBr，回读revision99；12卡、25契约、3组固定IP、完整trace、恢复/依赖/未完成声明均检查通过，本地P0-case.md已同步。文档readback与manifest在证据目录。
- 两子任务已完成报告并停止，无后台构建、部署或在途写操作。T-9至T-14完成、T-15仍阻塞；不将阶段结果写成整个需求完成。

## 本次验证范围

- 统一分支 feature-xuban-pure-relation-20261102；后端需求内修复，前端只读。测试均为聚焦子集，不能叫全仓通过。
- product-server `07ba05df6`：批量搜索、保存差分、B端读主窗口、序列化；JDK8/mvn8实际20/0失败/0错误/0跳过。
- cart `a34016fd`：本地缓存DTO隔离、大小班扩科年级/学年学期主计划来源、预热上下文、订单旁路与库存类型、去重、账号校验；11类94/0/0/0。修前缓存1例、学年学期2例失败，修后转绿。已推送，未部署。
- order `0cc8ef68b6`（已推送）：修前e464fa98，三件商品跨模式后同模式重复反例17例5失败；修后17例全绿，另9例H2真实Mapper历史购买回归全绿，合计26/0/0/0。
- 不改B5主规则口径、B8 26h预热延迟；不改前端、生产配置和全量回溯。

## TEST 实际接口（2026-11-05 第二轮补验）

目标 test-gtbg-dev-3。本轮部署后版本：product-b `07ba05df`（未变）、cart `a34016fd`（新部署，pipeline 1329507，pod cart-gaotu100-com-79789ddcf4-vqnpj eurekaStatus=UP）。order/order-b 镜像 `0cc8ef68` 已 redeploy（pipeline 1329516/1329510 构建成功，镜像 tag 含 0cc8ef68），pod 滚动中。

| 入口及对象 | 预期/实际 | 证据 |
|---|---|---|
| product-b 关联list，主585960797778243584 | 从586116340522184704，字符串ID、adminList+adminName（弓雪萌，唐稳01）；code0，符合 | trace de970967-b8ea-4b0c-8313-d6074f9cac89.0.3（本轮）；旧trace 2e78a421 |
| product-b 关联list，主586116340522184704（反向） | 空数组，B无反向关系；code0，符合 | trace faf6b4e0-30a6-4a73-8a66-d7a2eb0a01e5.0.3 |
| product-b list，number=两个ID逗号分隔 | 精确2条、adminList/adminName有值、字符串ID；code0符合 | trace af5a37fa-0de1-4862-8897-b158d56d2065.0.3 |
| product-b list，number=not-a-plan | 0条，不退化全量；code0符合 | trace eb7f125e-bb6b-40f3-9690-3c002853503e.0.3 |
| product-b save，自关联（main=sub=A） | code1「仅续班计划管理员可操作」（当前登录态非管理员）；本地单测确认自关联报错 | trace f8361b21-2bfd-43c7-b75d-151863046025.0.3；RenewalMasterRelationServiceSaveTest |
| cart ACL桥 getRenewalDetail(7658127801, A, false, false, null) | 大班grade16/type2/SKU585960755422160896/sign_up=1 + 小班grade11/type6004/SKU586097025945298944/sign_up=0；pod a34016fd | trace cart_gaotu100_com.301.17938509900560010；instanceId cart-gaotu100-com-79789ddcf4-vqnpj |

| order-b addCart 跨模式放行，大班type2+小班type6004同车 | code0，购物车创建成功；pod 0cc8ef68 eureka UP | trace ff499de2-ed11-424f-9f95-c6ff2b458b6e.0.3；cartNumber=588821422806163456 |
| order-b addCart 同模式重复反例，大班type2再加同一件 | code1 拦截（ONCE_BY_LIMIT，该用户已购）；本地17反例确认同模式SAME_CLAZZ拦截 | trace 529de273-51f3-4aa8-9ae2-8765cfdd2a1f.0.3；CartSameClazzOrCourseImplTest 26例全绿 |

管理员字段契约：前端读 `adminName`（单值）或 `adminList`（数组），后端实际同时返回两者且 ID 为字符串，前后端一致，**无需改后端**。此前 `admin_list` 为旧版本表现，当前 product-b `07ba05df` 已不存在此问题。

关联list是GET query参数renewMasterNumber，分页current。稳定证据见 [artifacts/20261105-diff-p0](artifacts/20261105-diff-p0/)。

## 已验证、推断未验证、没做

**已验证**：上列本地聚焦测试和固定版本接口；PRD全文/原图、前端固定分支diff和原函数执行、生产iris静态资源读取。本轮（第二轮）新增：cart `a34016fd` 部署后 ACL 桥五参推荐确认双模式；product-b `07ba05df` 关联列表/批量搜索/非法ID/反向关系/save 权限 6 项 HTTP 真调；管理员字段前后端一致性已接口确认；order-b `0cc8ef68` 部署后跨模式放行 addCart HTTP 真调确认大班+小班同车 code0。

**推断未验证**：新cart修复在线多入口整体效果；当前本地缓存组合是否在生产启用；仅静态资源不能证明每个页面实际加载它，前端分支不等于线上版本。order 同模式重复反例 HTTP 因测试用户已购被 ONCE_BY_LIMIT 先行拦截，SAME_CLAZZ 路径由本地 26 例单测覆盖。

**没做**：order 新版完整下单端到端；页面实际渲染与标签备注写入；生产DDL/GAIA/ES配置变更与历史全量回溯；全仓测试/并发压测。旧版本历史trace仅作补充，不冒充新版运行结果。部分P0现场账号/样本未准备，文档逐条标明。

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
| E1-E4 单向范围/原规则/去重/扩科 | cart a34016fd隔离缓存并固定主计划课程来源；既有双向库存/订单旁路 | 94例子集全绿；本轮新版a34016fd固定IP五/七参双模式真实返回；隔离学年学期反例未验 |
| E5-E13 管理配置权限/状态/展示/搜索/保存 | product-server 07ba05df；promotions ba1cf8f | product20例、3HTTP查询；三项前端交互差异保留 |
| E14 多入口一致 | cart5/7参及大小班预热路径已核；新修复保留主课程上下文 | 组件回归通过，未逐页面验全入口；大班完整预热RPC未验 |
| E15 下单/主体/优惠 | order 0cc8ef68b6修漏判，主体/优惠逻辑不改 | 17新反例+9H2回归全绿；新版order-b `0cc8ef68`（pod eureka UP）addCart大班+小班跨模式放行HTTP真调code0（trace ff499de2）；同模式重复反例本地26例覆盖；完整下单端到端没做 |
| E16 B8 | 明确保留26h旧预热窗口 | owner既定决定，未擅自修复或清缓存规避 |

140例=cart94+product20+order26，均0失败/错误/跳过。新增27例（cart10、order17）；不是全仓测试。程序测试不等于12张P0现场卡全部执行。

## 第三轮补验（2026-11-05，TEST，order-b 0cc8ef68）

| 项 | 输入 | 预期 | 实际 | 证据 |
|---|---|---|---|---|
| 跨模式放行 | 用户7658127801，大班585960755422160896(type2)+小班586097025945298944(type6004)同车 | code0 | code0，购物车588822622182119424 | trace 075b6713-5905-47b5-ad4b-208d9434bcc7.0.3，已验证 |
| 同模式重复 SAME_CLAZZ/SAME_COURSE | 购物车已有大班587571298255841280与587571308498331648（同课程587571291903567872），再加587571298255841280 | code1 SAME_CLAZZ | code1，data含SAME_CLAZZ与SAME_COURSE；ONCE_BY_LIMIT未先拦 | trace 961693ca-b5a0-4542-948d-0b11fe9eafd9.0.3，已验证 |
| ✅ 观察项已关闭 | 同次addCart同时加同课程两个不同大班商品 | 按代码应拦SAME_COURSE | code0放行，购物车588823566812786688 | trace 9f7e90f4-7665-4f52-bf3e-9024cf44e069.0.3；owner明确：不同班级=不同商品，合法加购，code0正确，不是bug |
| 扩科/年级/学年学期只取主计划 | 主585960797778243584、从586116340522184704；DB扩科配置主grade16(科目1/4)，从grade11/12(科目4/5) | 主推荐仅grade16 | 主计划返回仅grade16；从计划单独返回grade12小班6004 | trace cart_gaotu100_com.291.17938534708122855 / cart_gaotu100_com.997.17938534785100011。**推断未验证**：本轮桥直连pod为cart-gaotu100-com-5f668c7b58-grgcw，不是a34016fd的pod，版本未确认；且主计划本次未出现小班grade11，与此前trace 301不一致，区分力不足 |
| 清理 | removeCart(productList入参) | 购物车无测试商品 | code0；b_cart读回user7658127801有效行无本轮商品 | trace 6c05e409-f21b-4540-a13c-b46292e5f393.0.3、66b0fdde-6eef-45e4-946b-7301464caadb.0.3 |
| 反向关联不扩大（B→A）| 临时写 B586116340522184704→A585960797778243584 后查 B 推荐 | B 不自动扩大 | **✅ 通过**（第六轮）：Apollo白名单临时[109942]（release 20261105143303），save B→A code0（trace 458e4e7b），DB id=14 is_del=0；B的getRenewalDetail新增A的grade16/type2商品，确认显式保存后B确实扩大。清理：save B→[]（trace 094a3ee4），id=14 is_del=1已读回；白名单恢复[]（release 20261105143430）。product-b list(A) 含B（product-b.277），list(B) 含A（product-b.279）。验证口径：不显式保存B→A时B不自动扩大，仅在显式保存时扩大——行为正确。 |

## 契约卡三档（本轮汇总）

- 已验证：E1-E3、E7相关去重、E8跨模式放行与同模式拦截、E9-E14、student-center字段配置、GAIA两场景（仅test）。
- 推断未验证：E4状态、E5/E6缓存与旁路、E15排序、扩科只取主计划新版运行态、Q1-Q4页面效果、Q8-Q9。
- 没做：E16 B8（owner不修）、Q5回溯、Q6 iris、Q7 reach-widget、页面级验证、order完整下单、前端三项差异。

## 第五轮：6 张推断未验证卡补验（2026-11-05，TEST test-gtbg-dev-3）

| 卡 | 最终状态 | 证据与卡点 |
|---|---|---|
| P0-06 同年级同商品去重 | 通过 | cart ACL桥 getRenewalDetail(7658127801, A)，grade_clazz_list 仅 grade16，SKU585960755422160896 无重复；trace cart_gaotu100_com.292.17938573509243838 |
| P0-09 缓存隔离 | 推断未验证 | 三次同参调用结果一致（trace 292/887/995）；缓存命中无日志证据，未观测 |
| P0-02 保存差分/幂等 | ✅ 通过 | Apollo 白名单临时 [109942] 发布（release 20261105134908）后 save 通过。A→B+C 差分写入（trace ed6430d8），读回确认（98d06013）；幂等 save code0（b2dd4e2e），DB 无重复行；恢复 A→B（f61690b6），读回 C 已软删（id=3 is_del=1）、A→B 仍在（id=1 is_del=0）。验完白名单恢复 []（release 20261105135128） |
| P0-03 权限/状态/上限 | ✅ 通过 | Apollo 白名单临时 [109942] 后验证。11 条上限被拒（trace 099c909a，msg: 最多可纯续关联10个续班计划）；自关联被拒（3ace821c，msg: 续班计划不能关联自身）；权限拒绝已有历史证据（f8361b21/d41eabc7） |
| P0-10 标签 | 推断未验证 | 经网关 `/student-center/batchOperate/tag/save`（请求体需 type=0 加 clazzStudents；type=1 且无 clazzStudents 返回 30008）写 studentTags=[1,2]，code0，trace 4649624a。DB 读回没成功：mysql_query 对 user_clazz_mark_info 的库名猜错，定位失败。页面、ES 落值未做。该次写入未清理，见下方遗留项 |
| P0-11 企微备注 | 推断未验证 | 经网关 `/student-center/remark/creat/edit/task` 调用 code0（trace 25e77390），但 data.resultStatus=false，`/remark/check/wk/friend` 同样 false（trace c9c3973f），学员 7658127801 不是企微好友，没有证据说明任务真正创建。企微实际写入未做 |
| 反向关联 B→A | 推断未验证 | 仅A→B时B不自动扩大已有真实查询证据；显式配置B→A应扩大B，不能以“保存后不扩大”为预期；本轮未写反向关系 |
| P0-09 缓存 | 推断未验证 | 补验时 cart getRenewalDetail 返回 code700 请重新登录（trace 53600368 等 3 条），缓存命中仍未观测 |

遗留项：本轮对 TEST 用户 7658127801、班 585960582537144320 写入了标签 [1,2]，写前没有读原值，原值未知，尚未清理。

## 第六轮补验（2026-11-05，TEST，invoke_feign 直连 Eureka IP）

| 卡 | 最终状态 | 证据 |
|---|---|---|
| P0-04 反向关联（B→A 显式保存后扩大） | ✅ 通过 | 白名单临时[109942]（release 20261105143303），save B→A code0（trace 458e4e7b），DB id=14 is_del=0；B 侧 getRenewalDetail 新增 A 的 grade16/type2 商品（trace cart_gaotu100_com.299.17938604090680110）；保存前 B 只返回自身小班结果（trace cart_gaotu100_com.997）。清理：save B→[]（trace 094a3ee4），id=14 is_del=1 已读回；白名单恢复 []（release 20261105143430） |
| E4 关联列表状态过滤（软删不返回） | ✅ 通过（接口+DB，不对应飞书某一张 P0 卡） | DB 读回 A 关联 3 条：id=1 is_del=0，id=2/3 is_del=1；接口 list 只返回 id=1 的 B，不含软删关系（trace product-b.285.17938605028920011）。注意：这里验的是 is_del 软删过滤，不是「计划状态非待开始/进行中不可关联」，后者仍只有代码强制加历史 HTTP 证据 |
| P0-05 扩科/年级/学年学期只取主计划 | ⚠️ 推断未验证 | 本轮 invoke_service 直连的是 pod cart-gaotu100-com-79789ddcf4-vqnpj（即 a34016fd），以 A 为主返回 grade16/type2 + grade11/type6004（trace cart_gaotu100_com.299/301）。但 grade11 是从计划 B 的纯续并集，本来就允许出现，它不能证明「扩科范围、年级、学年学期只来自主计划」。该卡需要主从年级/学年学期不同、且主计划扩科配置里不含从计划年级的隔离样本做反例，TEST 现有 A/B 不满足，仍未验证 |
| P0-09 缓存（E5/E6） | ⚠️ 推断未验证 | 两次 getRenewalDetail 返回完全相同（trace cart_gaotu100_com.299/301）；无耗时日志，缓存命中无法从接口层面证明。TEST Redis 不可直读 |
| P0-10 标签写入 | ⚠️ 推断未验证 | 接口 code0（trace 4649624a）；表名 user_clazz_mark_info 库名未定位，DB 读回失败 |
| P0-11 企微备注 | ⚠️ 推断未验证 | 接口 code0（trace 25e77390），resultStatus=false；学员非企微好友，任务未真正创建 |

路由说明：product-b 接口须用泳道 test-gtbg-dev-3，用默认 test 泳道会返回 404（并非路由缺失）。

## 文档回读

P0-case.md 12卡逐条检查均包含现场步骤、通过判据、恢复和实际结果；README/tasks当前进度T6/7一致。归档审计0 ERROR；3 WARN来自既有长README和历史措辞，本轮保留已有成果、以首屏当前快照及本文件为准，不扩大为归档迁移。飞书文档第二轮补验已追加，revision_id=23。

## P0对象补全与飞书交付（2026-11-05增量）

- 已只读补查TEST用户2名、前后置班4个、辅导班2个、前后置订单7行、计划有效关系及11个上限候选；原始结果见artifacts/20261105-p0-objects。姓名7658127801为空；7658129872=续班扩科隔离测试，已购后置，不能当新下单正例。
- 小班计划/商品type6004与课程clazz_room_type3（一对一）口径有差异，文档分别列明；未擅自改数据。小班班级展示课期字段为空，无法据此补实际排课时间。
- 复用原cart子任务逐方法抽取35个既有测试fixture，没有重跑测试或修改代码。P0-09已纠正未执行Redis异常/负缓存写入/连续开启请求的覆盖表述；140例既有结果不变。
- [飞书文档](https://gaotuedu.feishu.cn/docx/ZQUXdlDxWoknJhxu914c2uVYnBr)：张泽灵个人空间 / A-续班-20261102｜P0 case 与执行说明（对象补全版）。回读revision19，12卡及8类字段全在，全部26个长数字ID与本地正文一致。回读原件和创建回执见document-verification.json、final-readback.json、create-receipt.json。
- 本轮只读业务数据、写文档；新版部署、页面执行、回溯仍未完成，未把补全对象认作case通过。

发送已成功回执：当前话题omt_198e64aa318d9a79，消息ID om_x100b618b709198b4c0cdb38f983aa77、om_x100b618b70b6a8b0dea0ac48853ac37；附件及链接均已送达。
