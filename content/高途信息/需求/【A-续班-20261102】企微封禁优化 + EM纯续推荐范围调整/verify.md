## 2026-11-06 P0 QW-02 小班续班服务页「批量修改企微备注」补验（test）

- **结论（已验证，页面/任务）**：EES 小班续班服务页 `crm/cronus/microClazzRoster?tabKey=continuationService` 勾选 7707218286（班 588506026511294464，续班计划 588506246722727936；与账号 177071 为企微好友，`dws_fuwu_user_teacher_wechat_info` friend=1）→「修改企微备注」（变量＝`${{wkRemark}}`，模板值 `QW02S-${{wkRemark}}`）→ 父任务 `294509612913149952`/子任务 `294509612923635712` 均 status=2、retry=0，真实备注 `cc→QW02S-cc`；再按原值 `cc` 提交恢复 → 父 `294509682327843840`/子 `294509682335183872` 均 status=2、retry=0，延迟回读 ES `ads_small_clazz_user_index_v4`(`_id=588506026511294464-7707218286`, `wechatRemark=["cc"]`, version 3561, 14:36:48) 与 DWS `dws_fuwu_user_teacher_wechat_info`(177071, `wechat_remark=cc`, 14:31:22) 均精确恢复；未选 7707218285 保持空。
- **trace/证据**：修改 `cc2f0432-d264-4c5e-8349-21205305aa8d.0.0`、恢复 `b4c5d366-bdb5-434b-84b6-2c1381402a83.0.0`、好友校验 `3c189276-536d-41f8-ad13-7071b856b217.0.0`；截图与 network 原件见 `artifacts/20261106-p0-qw02-small/`（`evidence.json`）。
- **主样本限制（没在小班续班页走通）**：指定小班 `563487716417804288`（一键班课测试3-axy）无续班计划（`renew_master_course_relation` 无记录、ES `smallRenewalNumber` 空、`smallRoundIdx=0`），在小班续班页计划下拉不可选、搜索 1437223 返回暂无数据；仅按 `clazzNumber`+`smallRenewalRoundFilter=[0]` 直调 `/roster/small/renewal/page` 能返回该学员（trace `24516254-c9da-4d5a-870d-73b25ed86d40.0.3`）。改用同页真实好友备选样本 7707218286，未用大班结果冒充小班。
- **P0 文档**：QW-02「实际/证据」块已写回并回读，block id `doxcnExvyrIA9MNK3Ll0xjIXMqd`（revision 449）。

## 2026-11-06 小班续班服务「微信备注」空白修复验证（test）

- **现象**：改企微备注任务成功（`ees_data.batch_operate_task` 3 条 `process_status=2`、`export_job_task` `task_status=2`），linkup WK 备注与 ES `ads_small_clazz_user_index_v4`(`_id=563487716417804288-1437223`) `wechatRemark=["测试cs122****0001"]` 均有值，但 `/roster/small/renewal/page`(`microContinuationService`) 响应**无 `wechatRemark` 字段**。
- **对照**：同班同数据默认花名册 `/smallClazz/clazzStudentList`(`smallClazzRoster`) 正常返回 `wechatRemark:"测试cs122****0001"`。
- **根因**：`student_field_config` 给 `microContinuationService`/`continuationService` 登记了 `wechatRemark` → `GaiaEsMappingService#getNeedFromEsFields` 把它当 ODS 字段从 ES fetchSource 剔除、又无 DataQueryServiceV2 补值（`SmallWechatRemarkQueryServiceImpl` 注册的是 `smallWechatRemark`）。实测 `getAllFieldNames("microContinuationService")=[wechatRemark,studentTagNames]`。
- **修复+验证**：`DELETE FROM ees_data.student_field_config WHERE identification IN ('microContinuationService','continuationService') AND field_name='wechatRemark'`（affected=2，保留 `studentTagNames`）；回读 `/roster/small/renewal/page` 返回 `"wechatRemark":"测试cs122****0001"`（trace `5c62f89b-2ba4-4dd3-86cc-ac641fc7acde.0.3`），与 ES/默认花名册一致。
- 口径见 [tasks T-16](tasks.md)、[知识库 continuationService](~/githubDir/quartzZZL/content/高途信息/知识库/cronus/microClazzRoster/continuationService.md)、[PROD 配置 diff 更正](artifacts/20261104-owner-ready/prod-config-diff.md)。

## 2026-11-05 P0 v2 精简与验证

- **P0 已重写为 revision325**：正文按「改了什么 → 关键上下文 → 主链路 → 原链路回归 → 影响范围 → 接口改动与关联回归」组织，步骤在前；131653→20114 字符。旧版 revision319 全文与 7 份附件引用存 `artifacts/20261105-p0-concise/feishu-revision-before.xml`，本轮验证证据存 [verification.json](artifacts/20261105-p0-concise/verification.json) 并挂文末。
- **直接改动（已验证）**：关联 list trace `4c82b6f7-fb92-4780-9e57-5c53fea7ffab.0.3`（A+B/admin/status）；save 幂等 trace `042fbf96-6975-45e1-8384-e13025c8b682.0.3`；cart 推荐三计划三商品 trace `cart_gaotu100_com.297.17938914022950422`。
- **关联回归（已验证）**：计划列表名称 `e2b184dd-d11c-4584-8b4c-0b0e29ebfc0d.0.3`、批量 ID `9bf775e4-86d7-4dc3-8d80-0f39cb0f9efb.0.3`、recommendClazzList `e1ab2353-2e4d-44bd-b7e3-eea56d477c89.0.3`、标签字典 `381a4bde-b09b-4501-863a-281c4a83a9df.0.3`、好友校验 `60704748-c9e0-476e-a446-9b53a1ae1788.0.3`。
- **code=35 已定性**：`roster/renewal/default/page` 补 `route.sceneVersionNumber=294310981744470016`（来自页面 getSchema 的 data.sceneVersionNumber）后 code=0、total=19、含 studentTags，trace `149bd5f0-a3b6-43d3-876d-7d28cf4b8591.0.3`；`/page` code=0，trace `5eeecd04-c3b0-466b-9911-27d623a1a35f.0.3`。原 code=35（trace `c97e2058-3679-4e61-a4fb-cd1e9c5144b9.0.3`）是缺参，不是缺陷。小班 sceneVersionNumber=294312775746856960。
- **页面级验证（部分通过）**：chrome-devtools-cli `--autoConnect` 连 owner 已登录 Chrome（无 debug 端口、未新开/重启）。EES 续班服务页加载成功，重置筛选后 19 行；批量选 1 人 →「添加标签」弹窗显示关注程度/报名意向/学员性格/临时标签。network `/roster/renewal/page` trace `7c7384be-e726-4a6a-a8f4-2f12c0f67bdd.0.0`（code=0/total=19/含 studentTags），标签字典 trace `401b4e75-465d-4f47-9cf4-b92379c5c3e7.0.0`；截图与原件在 `artifacts/20261105-p0-concise/page-evidence/`。EM 续班计划管理页加载 296 行，计划ID 588858850300473344 查到「W1-P0-243aa61a-EM独立主计划」，「纯续关联」弹窗显示「已关联续班计划 (2)」A/B；页面点「确定」实际发出 `POST /relation/save`（A/B，code=0，trace `57d3d20f-b921-46ce-aeaa-507ffa6515f5.0.0`），保存后重开仍为「已关联 (2)」。status1 计划 588872241920421888 在页面显示「待开始」，弹窗打开「已关联 (0)」，trace `2107bd48-80af-49bf-b274-07d5fd1d72c7.0.0`。截图 `w1-em-relation-modal.png`、`w1-em-save-result.png`、`w1-status1-modal.png`。备注弹窗点击未出现（选中 7704846439 疑似非好友），按 owner 策略跳过，未写成通过。
- **C 端入口/选品/价格（已验证）**：`getRecommendAppInfo` trace `b3084f50` 返回高途链接并打开（uid 7658127801），页面展示小班商品 `586097025945298944`（¥0）；`productSelectConfirm` trace `90ba9ce9` code=0，`/cart/web/renewal/price` trace `07822e8e` totalPrice=0、totalDiscount=0。点「去结算」未跳订单确认，完整下单/mock 支付未完成；跨模式/支付沿用 round7 接口证据（大班 588861402658267136=100 + 小班=0，支付 433655835275559341）。方法见 [C端验证方法.md](C端验证方法.md)。
- **剩余项定性**：status1 页面、跨学年/学期+有值从扩科、缓存运行态、C 端入口、小班批量第三人/小班备注属本次影响面（接口子集已验证，页面/剩余场景未验）；优惠/异主体、历史回溯非本次代码改动，不在本次验证范围。详见 P0 6.4。
- **skill**：banshan-case 新增「按代码改动写 P0」四规则并同步模板，`verify_skills.sh` 84 条 0 失败。

## round11 当前结果（2026-11-05）

**P0定向补验与文档写回完成，完整业务验收未完成。** 当前25契约/30条未完项以[逐项映射](artifacts/20261105-p0-execution-round11/contract-evidence-mapping.csv)、[双统计](artifacts/20261105-p0-execution-round11/statistics.json)、[交接](artifacts/20261105-p0-execution-round11/handoff.md)为准；下方历史轮次保留其原版本证据，不覆盖本轮新增事实。

- **已验证入口**：小班588506026511294464“【造数】小班续班前置-小学数学-1103-1831”，7707218285空→3→页面筛选/刷新仅本人→恢复空；7707218286保持7。新旧源/页面一致；保存trace `e62074d4-1ecc-4ac3-8bdd-4e906bcfd817.0.0`、恢复 `851ee85a-7815-4d4c-9844-894ea8a6965f.0.0`。QW-B02-002所述入口已验证，不代替小班批量第三未选。
- **已验证子集**：同班大班496625388833767424/bizNumber21YW25CY2A11001“madman-续班-正价-11”，好友654489/轩昂与未选654499；默认/续班分别实际保存相同三变量，姓名轩昂＋真实身份空＋原备注zhangkaiis→轩昂--zhangkaiis，14≤20。两次保存/两次恢复的4组父子任务均status2/retry0，官方原值恢复、未选三关系及标签/颜色/分层不变。[逐页原件](artifacts/20261105-p0-execution-round11/default-comparison.json)。不把好友展示“其他”代替身份变量。
- **版本范围**：TEST/dev3；小班实际保存/筛选路由10.255.176.174:28688，沿用既有release5dce9cdb映射；前端沿用cronus17ee81cc，不称目标feature后端已部署。EM版本product-b07ba05df/cart-a34016fd/order-b0cc8ef68回读，本轮无新增EM业务链路；published查询缓存false不等于运行缓存分支通过。
- **信息完整性**：12卡1完整/2准备/9缺失；原30条5完整/19准备/6缺失。**业务验证**：原30条3个所述入口已验证/20子集/7没做，整卡通过0。信息完整与业务通过分开统计。
- **没做/卡点**：小班2选+第三未选仅有2名受控同班，不能替代；小班好友成功两现有人friend0；默认模板手机号/非空身份/截断及同班多人仍缺。C端暂无已确认带计划/受控学员参数落地入口与绑定C会话；缓存命中回退需当前false开关之外的有效条件；优惠/异主体无已核可用优惠和异账号SKU，现有两SKU均账号12/gaotu、优惠0。保留最小必需项，不把替代接口证据当整链路。具体其余契约未完项见CSV，不重付订单、不清缓存、不跑无参数C根页。
- **建议/外部后续**：历史min(begin_time)全量回溯仍外部后续；跨模式已购展示仅归因/修复建议。全组合/全部老师矩阵、自然26小时等待不升为当前门槛。
- **文档/恢复**：P0 revision319，35份证据+manifest附件上传下载逐字及逐文件SHA256/ZIP CRC通过。[回读凭据](artifacts/20261105-p0-execution-round11/document-closure.json)。标签恢复7/空、空行保留，备注恢复、未选不变，身份Gong177071不变，两新增页56/57已关闭，无在途业务任务或待恢复写入。
- **skill**：专用banshan-case存在；既有源/安装入口和模板本轮逐字/哈希一致，见[回读](artifacts/20261105-p0-execution-round11/skill-reuse-readback.json)。本轮未改skill或重跑84检查；未改业务代码、部署、生产、测试原集、新班/报名/订单或发送消息。

# 当前验证与续接（2026-11-05）

P0原全文revision247验证沿用；round8受影响章节回读revision271，集成与附件回读revision273，最终附件与revision见[集成终态](artifacts/20261105-p0-version-round8/integration-final-state.json)。未重跑旧84条检查。

本轮交付限TEST受控样本与对应执行、P0/skill改写；无业务代码、服务部署、生产写入、对外消息。整体任务仍未全验收。外部P0是逐条判据真相源；本文件记录当前环境/样本/证据与续接限制。

## 改动与证据

- 表达规范：测试侧简洁前置/操作/预期/实际；完整证据集中引用。金额/数量保留真实输入、规则、简短代入、结果，单位/边界/去重/取整按影响说明。筛选范围说明纳入/排除，不伪造数学公式。
- 25项契约、原30条与12卡映射保留；Banshan完整功能120条、线上30、冒烟30只读比较，无可复用执行结果；7处细化并入原卡，没有新增业务规则。见[比较](artifacts/20261105-p0-execution-round7/banshan-comparison.md)。
- banshan-case源/安装入口和模板逐字一致；结构审计及84条路由0失败，真实金额/筛选/缺编号/未测边界走读见[自检](artifacts/20261105-p0-execution-round7/skill-concise-final-check.json)。规则走读不等于业务执行。
- 最新信息完整性：12卡1/2/9；原30条4/19/7，详见[本轮双统计](artifacts/20261105-p0-version-round8/integration-statistics.json)。实际业务结论单列于每卡/原30对账，不以此数字当通过数。

## 已验证：环境与编号

- TEST/test-gtbg-dev-3：product-b07ba05df、cart a34016fd、order/order-b0cc8ef68；17:48实例Running/UP见[versions.json](artifacts/20261105-p0-execution-round7/versions.json)。不把仓库HEAD代替实际版本。
- 企微前端cronus17ee81cc已确认在test-gtbg-dev-3，浏览器资源umi.7054cbb2一致；后端复用TEST现有API，release5dce9cdb/10.255.176.174及df66fed8/10.218.238.176。浏览器实际Gong177071；独立准备账号109942分别取证，不能混归。两后端本轮受控ES查询均成功，详见round8路由证据，不代表全局ES健康。
- 使用的接口没有同名bizId；number对应clazzNumber/选课SKU，bizNumber对应业务编码；数据库主键另列。大班“续班归因-正经前置班-0820”number574882679202260992/bizNumber32YYTS25D6LS11002，course_center.id208807、gaotu.id20503472。小班586097025945298944的number/bizNumber相同、DBid218726只是该样本事实。见[class mapping](artifacts/20261105-p0-execution-round7/qiwei-class-identifier-mapping.json)。英语扩科585963404555053056的班名/bizNumber已在round9核实，数学候选完整编号仍不外推；未用SKU充数。

## 已验证：EM可用样本及实际结果

- 专用主计划588858850300473344/status2关联A585960797778243584、B586116340522184704；过程588864200919560192有效。两班正常工具补真实课节和老师唐稳01/11188041873297121，不直接改发布状态。
- 前班588861397654462464，bizNumber15YW26C6M111001，B测试-五年级语文春季前置B，课588861395571990528，真实课节588863029087723520。后班588861402658267136，bizNumber15YW26XTRO11001，B测试-五年级语文暑假后置1B，课588861400563212288，真实课节588863038271152128；均publish40/sale40，正常订单预览/支付另证可用。见[建班回读](artifacts/20261105-p0-execution-round7/repair-built-classes.json)。
- 前班额外保留辅导班36803939628614144/36803941611078144/36803949969408512；后班36803940198384128/36803942133662208/36803950157890048。list_subclazz吞code1返回[]不能当不存在；DB实际存在，不再次新建。
- 管理边界10保存、重复仍10、11/自关联/status0拒绝均DB回读，最终精确恢复A/B。见[边界](artifacts/20261105-p0-execution-round7/relation-boundaries.json)。status1主正例接口已于round8补验，页面未验。
- 学员7707220467前置订单433654730395222957；先仅主1件，再补B前课真实订单433655675288028077，后推荐2件均未购。学员7658129872补前课订单433655258676199942后有三计划三来源/三个不同商品，同语文不按学科去重。按执行时间复用，不能用购买后的当前状态冒充先前未购。
- 同商品碰撞：7658129872两有效前课临时映射同后置SKU585960755422160896，grade16最终1件；仅新增映射已正常删除并独立回读，其他商品保留。见[碰撞及恢复](artifacts/20261105-p0-execution-round7/collision-observe.json)、[restore](artifacts/20261105-p0-execution-round7/collision-restore.json)。
- 同单：7707220467，商品588861402658267136/type2价格100分、586097025945298944/type6004价格0分，各1、优惠0；100×1+0×1−0=100分（整数分，无额外取整）。支付433655835275559341/pay_status1/real100，同一收款账号12/gaotu；订单433655835275559853与433655835275560365均status2，18:12:15独立DB回读。见[支付回读](artifacts/20261105-p0-execution-round7/dual-payment-readback.json)与[订单](artifacts/20261105-p0-execution-round7/dual-paid-readback.json)。两后课现已购，不可重放未购步骤。
- 缓存主集前后仅自身课、实际推荐3来源；当前published renewal.query.cache.enabled=false，不能称本次覆盖本地缓存分支；没有改Apollo。见[配置](artifacts/20261105-p0-execution-round7/cache-published-config.json)、[实际查询](artifacts/20261105-p0-execution-round7/cache-isolation-runtime.json)。

## 已验证：企微子集及恢复

- 同班真实2+1：目标7704846434/7704846439，对照7704846440，班574882679202260992，辅导班35930167940088064；三人真实已付订单433654889322644001/433655061119763372/433655095481074192及在班status1。
- 批量标签2/2→单人3/2→清空空/空，新旧源表一致，对照仍无行；默认花名册选值取消不写。trace2490b2bb-d793-4568-b2fc-4900f59a7e4f.0.3/7df78fce-b798-49da-ad2a-98813493e9b8.0.3/f868a36f-547b-43fa-8bf7-25fae48adcf4.0.3。空标签行保留，业务值恢复不等于物理恢复无行。
- 真官方好友654489/654500，原备注zhangkaiis/1105修改企微备注；单任务294433185677210624、正确双任务294434116095472640及子任务均成功；实际模板W1-${{wkRemark}}，两人结果正确，未选654499保持，标签/颜色/分层不变。两原备注18:32:33延迟独立回读一致，trace student-center.610.17938747537998677；即时旧读未当恢复。
- Agent错误变量任务294433631114392576触发NPE；原失败保留，仅本轮父子软删is_del1/status0，没有改成功、不当业务回归。见[报告](artifacts/20261105-p0-execution-round7/qiwei-report.md)、[结果](artifacts/20261105-p0-execution-round7/qiwei-results.json)。
- 默认花名册/联系学员×官方私聊/群聊4组合链接均实际显示，两规范打开、返回草稿可编辑后丢弃；没有点击发送，网络结论仅所采窗口。其余入口不算通过。
- 最终浏览器仍Gong177071，trace ad241b1e-7136-42a4-b5db-bda35125981a.0.3；无新cosplay，私有凭据删除、草稿/选中/文档页清理。子任务result9已completed，无在途任务；无待恢复备注。

## 推断未验证／没做与续接

- 历史18:02 ES父熔断5.8GB>5.7GB、trace ab2ed085-38a9-4d94-ae7c-d8119fd1fc54.0.0确实发生；round8已由两实例成功受控筛选纠正当前统一阻塞判断。ID/名称、切换残留与老师联合接口已补子集，物理ES原文档和页面完整矩阵不外推。未调整ES或部署。
- 其余没做：status1管理员页面、真实不同年/学期和有值从扩科、跨年级/纯续扩科碰撞、同号跨模式第三件重复、本地缓存组合/负缓存/故障/关闭、优惠/异主体/C端与其余页面；小班2+1/同班备注页面及默认模板，历史min(begin_time)阈值/回溯。当前并未证明这些都需人工，身份/官方好友已取得不再列人工条件。
- 既有140例聚焦程序结果（20+94+26）沿用原版本证据，不重跑、不当页面/端到端；MR静态结论不当业务运行。
- 保留专用计划、两班/真实课节/老师、额外辅导班及受控订单学员供续接；不退款/删单/关闭共享班。fixture登记已更新两班可售并附业务证据；主关联A/B是预设保留状态，碰撞已恢复，备注恢复，标签空行保留。没有在途父支付/子任务/部署。

## 文档与证据检查

- [本轮278文件证据包](artifacts/20261105-p0-execution-round7/p0-test-evidence-243aa61a-round7.zip)，上传原P0并下载逐字一致，SHA256 f21e810d477a2939c2b152aa3cadc8eaa67cebbfff1dd77f333ae239cbf5c0be；敏感文本文件不分发，manifest说明，未伪称未分发原件已公开。
- 最终外部回读、25契约/30映射/12卡与集中附录、锚点/资源/链接及计算语义结果见[文档核验](artifacts/20261105-p0-execution-round7/document-verification.json)。原两附件保留；这只证明保存/可追溯，不提高业务通过数。

## 本轮集成结果（round8）

- 完整报告：[integration-report.md](artifacts/20261105-p0-version-round8/integration-report.md)。25契约逐点见[CSV](artifacts/20261105-p0-version-round8/contract-evidence-mapping.csv)，原30双统计见[JSON](artifacts/20261105-p0-version-round8/integration-statistics.json)。原30业务证据2条所述入口已验证/21子集/7没做；12卡整卡通过0，不把信息完整数当通过数。
- W1-94f1e3与W1-8a15e8报告及原始JSON/88行CSV均核对。50191功能88/线上17/冒烟17三任务均0执行；31已有/45步骤借鉴/7冲突/5范围外。创建日期与立即失效预期不覆盖min(begin_time)/26小时规则。P0-09缺案等原范围保留；完整逐节点映射已附原P0。
- 待开始计划588872241920421888（开始2026-11-06 19:01+08:00）由管理员90247正常保存从A，DB独立回读；随后正常保存空集并回读，trace554793cb-8220-41c8-86d7-8c2d148b48b1.0.3 / 6ff75cb7-e78d-4073-8676-be39c2d91c07.0.3。新计划/绑定/课程映射登记保留，不重放创建脚本，未来需重核status1。
- cart真实网关已通过：实际绑定test-api.gaotu100.com/cart→route745→10.218.237.47/a34016fd，trace5b7e496d-e6c4-4ebd-a8c5-4d0230140811.0.3、962ms、业务code0。旧fuwu地址落mi_383导致700，不能认定真实cart登录失败；固定Pod漏fromC为空值错误，补0正常。没有代码修复或扩大重试，接口不代替页面。
- 学员7658129872的大班后SKU588861402658267136（bizNumber15YW26XTRO11001/B测试-五年级语文暑假后置1B）可售未购；小班后SKU/bizNumber586097025945298944（dcg-小班扩科排除-数学-后置）有效order_item433534690352694278/status2/refund0，推荐仍signUp0。cart目标提交实际order_info空而order_item有单，来源差异已核，是否本次回归未判；未改代码。不能称双后置均未购。
- 大班标签3仅甲、筛2无残留、叠加其他老师为0；清空后筛2/3为0。release旧熔断实例220ms正例、df66实例127ms清空读取均正常。浏览器Gong单甲保存2（trace b4fa4a42-4b8f-4265-adb3-1724d678703b.0.0）与新旧源表一致，正常恢复空、对照不变；页面选中0。即时读曾旧值，仅将延迟结果作为最终一致证据。
- 两子任务已completed，主Worker无在途业务调用/支付/部署/待恢复操作；TEST对象/空标签行按登记保留，官方备注原值和Gong身份维持恢复状态，无新cosplay或消息。
- 未完成仍是实际执行缺口：小班/默认备注模板、真实跨学年学期及有值从扩科、跨年级保留/第三件重复、C端与其他页面、缓存负值故障/自然26小时、优惠异主体、历史阈值/全量回溯。没有证据证明需提供账号/好友或部署才可推进；跨模式已购展示是否另开修复需决定，历史大数据回溯须按原边界由获授权执行方安排。完整业务验收尚未完成。

- round8附件59份证据＋manifest已上传原P0并下载：SHA256 ddb4b69e3ce3e9ea41e780ce4caa276b6d67447ac9e36d30892208b041756154，逐59条SHA相同，ZIP完整性通过；最终revision273及附件token回读成立。只核受影响内容，未重跑旧检查。

## round9最终边界与新证据

- [边界报告](artifacts/20261105-p0-boundary-round9/boundary-report.md)、[12项边界表](artifacts/20261105-p0-boundary-round9/acceptance-boundary.csv)、[25契约映射](artifacts/20261105-p0-boundary-round9/contract-evidence-mapping.csv)、[双统计](artifacts/20261105-p0-boundary-round9/boundary-statistics.json)和[终态](artifacts/20261105-p0-boundary-round9/final-state.json)为当前结论；round8文件保留为历史原件。
- 新增小班真实页双人保存2，新旧源2/2；原7/空恢复后独立DB/列表一致，筛7仅7707218286、筛2/3为0。班clazzNumber/bizNumber588506026511294464、名称【造数】小班续班前置-小学数学-1103-1831；另一学员7707218285。实际Gong177071，目标前端17ee81cc，保存release5dce9cdb、回读df66fed8，见small-actual-route-proofs.json。原值恢复、新空行保留、测试页关闭；同次第三未选对照和完整单人页面未验。
- 新增7658129872有值从A英语扩科候选1件、主588858850300473344含扩科推荐仍0扩科/3纯续，trace .305.17938822210950335/.296.17938822210960339；无配置/关系写入。getRenewalDetail两个true是getContext/fromBCart，不是开关。不同主从学年学期仍没做。
- 非好友7704846434在实际大班页面被备注入口拒绝，未提交任务；不替代同班好友/默认模板。原官方任务/恢复不重复。
- 必需未完成与可选建议已分开：大小班模板/必要入口、隔离去重/缓存回退/优惠主体最小对照不删除；全矩阵、自然26小时停等、独立加购范围与真实发送不升为本轮门槛。历史min(begin_time)规则外部回溯后续；跨模式已购展示仅独立修复建议，不阻塞文档。
- 当前无在途业务操作/待恢复写入；原测试对象/身份/备注状态不变，无新订单/支付/建课/发布。不把未执行项写成外部阻塞或当前整体通过。

- 最终P0受影响章节回读revision287，边界章节与新附件回读revision289；35份证据+manifest上传/下载逐文件SHA256一致，ZIP CRC通过，详见round9/final-state.json。


## 2026-11-05 round10 定向补验

- **环境/版本/身份**：TEST/test-gtbg-dev-3；cart `a34016fd`；企微默认 TEST `release-5dce9cdb`；Gong/177071。未改业务代码、未部署、未写生产。
- **跨学年/跨年级接口子集**：计划列表真实回读 trace `2cdd67b2-535d-4799-99bc-cbe54a5e9b42.0.3`：主 `588858850300473344`“W1-P0-243aa61a-EM独立主计划”（2026春→2026暑假、五年级）关联小班 `586116340522184704`“dcg-小班扩科排除-计划”（2026春→2027暑假、一年级）。学员 `7658129872` 主计划 `getRenewalDetail` trace `cart_gaotu100_com.296.17938822210960339` 返回纯续 `recommend_type=1` 的 grade16/11/15 三组、扩科0；从计划 `585960797778243584` 同参 trace `cart_gaotu100_com.305.17938822210950335` 有英语扩科 `recommend_type=2` 1件。证明主扩科未被从计划污染、跨年级纯续商品保留；页面/C端及另一方向仍未验。
- **同班小班非好友前置**：班 `588506026511294464`“【造数】小班续班前置-小学数学-1103-1831”，学员 `7707218286/7707218285`。好友列表 trace `e8797efb-8e00-48cb-977d-48ac4b4cf5a3.0.3` 返回 `notFriendCount=2`；备注前置 trace `e63d3075-48a8-4d80-b9b9-46276d6f860c.0.3` 返回 `code=0,resultStatus=false`，未提交任务。默认页结构回读 trace `6f52402e-f3b3-47f4-9960-23f7d95bd76e.0.3`。这只证明非好友拒绝前置，不证明好友成功或默认模板一致。
- **证据包**：`/tmp/w1-p0-243aa61a/round10/round10-evidence.json`；P0附件 `round10-p0-evidence.zip`，file token `HUS1blRw5oamDBxU5VdcYkzKn7d`，SHA256 `c798b5438965d17d405b67ab32b9c018fac8ca39e5581dc101335e416d76ae10`。
- **仍未完成**：小班第三未选对照/完整单人页面；同班好友成功与默认备注模板；缓存回退/优惠/异主体；页面/C端入口；历史 `min(begin_time)` 全量回溯。
