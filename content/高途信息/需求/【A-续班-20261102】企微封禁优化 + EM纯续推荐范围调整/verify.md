# 当前验证与续接（2026-11-05）

P0已保存并全文回读revision247；同源导出只规范Markdown标题层级，不改文本/证据。

本轮交付限TEST受控样本与对应执行、P0/skill改写；无业务代码、服务部署、生产写入、对外消息。整体任务仍未全验收。外部P0是逐条判据真相源；本文件记录当前环境/样本/证据与续接限制。

## 改动与证据

- 表达规范：测试侧简洁前置/操作/预期/实际；完整证据集中引用。金额/数量保留真实输入、规则、简短代入、结果，单位/边界/去重/取整按影响说明。筛选范围说明纳入/排除，不伪造数学公式。
- 25项契约、原30条与12卡映射保留；Banshan完整功能120条、线上30、冒烟30只读比较，无可复用执行结果；7处细化并入原卡，没有新增业务规则。见[比较](artifacts/20261105-p0-execution-round7/banshan-comparison.md)。
- banshan-case源/安装入口和模板逐字一致；结构审计及84条路由0失败，真实金额/筛选/缺编号/未测边界走读见[自检](artifacts/20261105-p0-execution-round7/skill-concise-final-check.json)。规则走读不等于业务执行。
- 最新信息完整性：12卡1/1/10；原30条4/17/9，详见[分类](artifacts/20261105-p0-execution-round7/reproducibility-current.json)。实际业务结论单列于每卡/原30对账，不以此数字当通过数。

## 已验证：环境与编号

- TEST/test-gtbg-dev-3：product-b07ba05df、cart a34016fd、order/order-b0cc8ef68；17:48实例Running/UP见[versions.json](artifacts/20261105-p0-execution-round7/versions.json)。不把仓库HEAD代替实际版本。
- 企微实际默认TEST release-5dce9cdb；浏览器Gong177071/课程顾问及班级权限真实确认，独立准备账号张泽灵109942。目标feature部署未确认，不能当需求分支整体验收。
- 使用的接口没有同名bizId；number对应clazzNumber/选课SKU，bizNumber对应业务编码；数据库主键另列。大班“续班归因-正经前置班-0820”number574882679202260992/bizNumber32YYTS25D6LS11002，course_center.id208807、gaotu.id20503472。小班586097025945298944的number/bizNumber相同、DBid218726只是该样本事实。见[class mapping](artifacts/20261105-p0-execution-round7/qiwei-class-identifier-mapping.json)。两个扩科结果的完整班名/bizNumber标缺，未用SKU充数。

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

- 确认环境阻塞：续班ES父熔断5.8GB>5.7GB，写前已发生，trace ab2ed085-38a9-4d94-ae7c-d8119fd1fc54.0.0。默认页吞错0人不当筛选通过；先恢复可用ES/核目标版本再补ID/名称集合及老师联合约束，不重复同法失败调用、不自行部署。
- 其余没做：status1管理员页面、真实不同年/学期和有值从扩科、跨年级/纯续扩科碰撞、同号跨模式第三件重复、本地缓存组合/负缓存/故障/关闭、优惠/异主体/C端与其余页面；小班2+1/同班备注页面及默认模板，历史min(begin_time)阈值/回溯。当前并未证明这些都需人工，身份/官方好友已取得不再列人工条件。
- 既有140例聚焦程序结果（20+94+26）沿用原版本证据，不重跑、不当页面/端到端；MR静态结论不当业务运行。
- 保留专用计划、两班/真实课节/老师、额外辅导班及受控订单学员供续接；不退款/删单/关闭共享班。fixture登记已更新两班可售并附业务证据；主关联A/B是预设保留状态，碰撞已恢复，备注恢复，标签空行保留。没有在途父支付/子任务/部署。

## 文档与证据检查

- [本轮278文件证据包](artifacts/20261105-p0-execution-round7/p0-test-evidence-243aa61a-round7.zip)，上传原P0并下载逐字一致，SHA256 f21e810d477a2939c2b152aa3cadc8eaa67cebbfff1dd77f333ae239cbf5c0be；敏感文本文件不分发，manifest说明，未伪称未分发原件已公开。
- 最终外部回读、25契约/30映射/12卡与集中附录、锚点/资源/链接及计算语义结果见[文档核验](artifacts/20261105-p0-execution-round7/document-verification.json)。原两附件保留；这只证明保存/可追溯，不提高业务通过数。

## 本轮版本核实与必要增量（round8）

- 18:54核实product-b07ba05df、cart a34016fd、order/order-b0cc8ef68仍在test-gtbg-dev-3 Running/UP，远端需求分支SHA与镜像一致。既有主计划只读桥及三来源推荐code0，trace product-b.253.17938761501380025 / cart_gaotu100_com.305.17938761501370274。仅当前受控对象与观察层。
- 已补REN-B01-002接口正例：新受控计划588872241920421888“W1-P0-243aa61a-待开始状态正例”，开始2026-11-06 19:01（+08:00）、status1/is_test_data1，管理员唐稳01/90247。正常复用自建暑假后课588861400563212288作唯一前课、正常配置后课585960751831836672并发布计划；没有新建班/订单、不改已有课程发布状态。保存从A585960797778243584成功，DB独立回读唯一关联；trace554793cb-8220-41c8-86d7-8c2d148b48b1.0.3。已正常保存空集并DB确认清空，trace6ff75cb7-e78d-4073-8676-be39c2d91c07.0.3。新计划/绑定/新增映射登记保留，供真实不同学期场景；状态1仅在开始前成立，未来复跑须重核，不能将来仍当待开始。
- 入口核实：网关cart operation/cart返回700登录要求；匹配pod直连HTTP返回status1未知错误，尚在查trace，均未记入口通过。order-b正常prepare对7658129872两目标各1成功，预览100分，未新创建订单或支付。桥健康不替代页面/网关健康。
- 证据：[status1](artifacts/20261105-p0-version-round8/status1-main-case.json)、[部署](artifacts/20261105-p0-version-round8/em-versions-current.json)、[最小调用](artifacts/20261105-p0-version-round8/em-minimal-route.json)。没有服务部署/ES参数修改；企微版本与ES由原子任务只读核实中，最终结论待整合。
