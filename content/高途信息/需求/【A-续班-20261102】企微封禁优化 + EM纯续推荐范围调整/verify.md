## 2026-11-07 从计划状态变化（已修复并实测）

## 2026-11-09 Order !2391 完整回滚验证

- 回滚MR：[!2392](https://git.baijia.com/gaotu/order/-/merge_requests/2392)，分支 `feature-revert-order-mr2391-20261109` → `release`，提交 `fad87492bd35346def21e5d79212ee87f855a476`。GitLab独立回读为opened，source/target/head与本地及远端一致；未合并、未部署。
- 使用 `git revert --no-commit -m 1 486b3152` 生成完整逆向改动，仅两个原MR文件；暂存树哈希与合并前 `a9790414` 完全一致，恢复原有班级/课程编号重复校验，删除该MR新增的放行测试。
- `mvn8 -pl order-app -am -DskipTests compile` BUILD SUCCESS。基于本次编译产物用JDK8运行独立校验程序，9项检查通过：不同编号放行、跨模式同课程双向拦截、跨模式同班级拦截、大小班各自同模式重复拦截、已有购物车重复、空输入、降级开关。该程序不纳入MR，保证回滚内容与原MR严格对应；未声称运行全量单测。
- AICR截至创建后查询尚无该分支任务/评审结论，不能写成评审已通过。此前旧release运行对照仍见下节。

## 2026-11-09 Order 新旧版本对照：已实测

- 旧版已部署到空闲的 `test-eco-10`：Order/Order-b 均为历史 release `317482f9`，目标实例均 Running/Eureka UP。与合并前 `a9790414` 仅差 `paving/roads.yaml`，业务代码一致。新版为 dev3 `0cc8ef68`；默认 test 已合入 `486b3152`，未用作旧版对照。
- 使用不同测试学员：旧版 `7704852575`，新版 `7704852569`；共同在售商品大班 `589537362151786496`（2，100分）、小班 `586097025945298944`（6004，0分）。原收费大班 `588861402658267136` 已停止售卖，不能沿用原成功样本作为当前购买预期；未修改共享商品状态/价格。
- **真实购物车：两版均未通过**。固定调用各版本 Order-b `/orderComponent/b/cart/addCart`，大班成功、小班返回 `PAYMENT_SIZE`。旧实例日志明确资金账户 `[66,75]` 不一致。独立DB回读两学员购物车均仅大班；本次代码未修改该支付校验，不将其归因为新代码回归。
- **批量下单：两版均成功**。调用 `/order/boss/facade/batch/createOrder.do`，分别携带对应泳道；旧版创建日志在 `order-b-gaotu100-com-75cd9c7d68-x5t6h`（10.218.237.155）确认，trace `ab1ca201-cad7-4a82-b276-29b04e370dab.0.3`，排除旧版请求回落默认test。该入口结果不能替代购物车链路通过。

| 版本 | 支付单 | 大班订单 | 小班订单 |
|---|---|---|---|
| 旧版317482f9 | 434016293634441483 | 434016293634441995 | 434016293634442507 |
| 新版0cc8ef68 | 434016298995810375 | 434016298995810887 | 434016298995811399 |

- **Mock支付：两版均成功**。固定调用旧 Order 10.218.237.117、新 Order 10.218.250.77 的 `/demo/mockPay?payNumber=...`（TEST内部模拟支付，pay_channel=58；未调用真钱支付或钱鸟网关）。独立DB确认两支付单 `pay_status=1,real_price=100`，各自关联的两业务订单均 `order_status=2`。这是旧版本也支持批量大小班同支付单的直接证据，不能扩展成所有入口或所有商品组合都支持。
- **相同编号规则：运行中校验器构造输入对照**。分别在旧/新Order-b实例执行 `CartSameClazzOrCourseImpl.execute`，不改bean字段、不写商品/关系数据：不同编号两版放行；跨模式同courseNumber旧版 `SAME_COURSE`、新版放行；跨模式同clazzNumber旧版 `SAME_CLAZZ`、新版放行；同模式重复两版仍拦截。此项证明校验规则差异，尚非真实同编号商品的页面购买链路。
- 最终口径：本次Order变更不是新增“大小班一起下单/合并支付”能力，而是解除跨模式相同课程/班级编号的重复拦截；支付账户限制仍独立存在。本轮未关闭支付校验/Apollo，不把批量下单成功写成购物车购买通过。
- 旧版对照泳道保留供复验；测试学员订单与购物车数据保留。详见[版本、请求、DB及运行校验证据](artifacts/20261109-order-comparison.json)。

## 2026-11-09 PROD es_query_config 补数据（待审批）

- 工单 [148118](https://sre.baijia.com/dms/mySql/detail?id=148118&env=/prod-sql)：`ees_data.es_query_config` 补 `continuationService` 的 `studentTags`(basic/necessary)+`studentTagNames`(extra) 共 3 条。待 SRE 审批发布；生效后 `/roster/renewal/page`(continuationService) 应返回 `studentTagNames` 字段，≤5min Caffeine 缓存自动失效。
- 根因（唐稳反馈 traceId `3df09a43-...`）：写侧全成功（DB+ES 145 条 bulk），调用链 0 error、HTTP 200；读侧因 PROD 缺这 3 条配置，`GaiaEsMappingService` 不取 `studentTags`，列恒空。小班 `microContinuationService` 线上 3 条齐全。

## 2026-11-07 缺陷1485167修复与回退验证

- 售卖修复提交 `7f749e65` 已包含在当前Cart `04022be8` 中，部署坐标见上节。[改前后原件与断言](artifacts/20261107-sale-status-fix.json)。TAPD1485167已回读为resolved，等待QA复测，未关闭。
- 根因：大班路径用ClazzDTO.saleStatus=50过滤掉商品SKU.sale_status=40的关联小班；同根因另影响换班列表、筛选项和预热。已统一关联小班的SKU售卖判断；大班原判据、无关联计划和关闭总开关时原逻辑不变。非空关联缓存版本追加sale-v2隔离旧错误预热，不修改普通计划键。
- 漏测原因：既有复核artifacts/20261106-followup-review.md中三个候选班级sale_status均40（含小班586097025945298944），没有覆盖两套状态冲突。210项本地测试0失败，新增在售/非在售/缺SKU/开关/普通计划/旧预热迁移边界；不能把覆盖率当业务正确性证明。
- 原缺陷数据：陈晨7704848531，A589037361072007168、B589164864470188032、C589037362856683520；小班SKU589048589437788160、前课18405861174936317、后课18405861174936327。未修改订单、关系、班级售卖状态或库存。
- 当前10项运行断言通过：A返回大班589041202037415936和小班589048589437788160；B只返回小班；周周7714162980从A只返回小班；B端A返回两门；无关联C计划完整响应与改前一致；换班列表返回小班、筛选项有老师；旧版本缓存隔离、预热及预热后推荐均正确。只统计recommendType=1；A→C已移除，三门结果仅为此前证据，复跑以当前关系为准。
- 回退对照：指定Cart TEST JVM的相关总开关字段临时false，B/C入口均仅返回A自身，只有B资格学员从A返回空；所有字段恢复true并回读后，当前A+B两门推荐恢复。最新恢复trace cart_gaotu100_com.288.17940218688480020。使用ACL调用控制器对应业务方法，不冒称真实学员HTTP/UI发链验证；Apollo已发布值未改。
- 回退配置：四个Apollo应用cart.gaotu100.com、product、product-b、order.gaotu100.com分别配置`renewal.pure.relation.enabled=false`并发布，默认true。Cart控制B/C推荐并集、资格及关联缓存路径；Product C/B控制关联下发/缓存版本；Order关闭跨模式重复校验放行。只能停用这些运行行为，不删除关联数据、不隐藏EM维护入口、不撤销企微标签/备注。`renewal.pure.relation.cache.invalidate.enabled`不是总开关。
- Cart实测Apollo cluster=test-gtbg-dev-3-BJ-Ve1。只读已发布结果：该TEST cluster上Cart=true、Product C未配置、Product B=false、Order未配置；PROD/application查询四应用均未配置key。发布回退前按各实例实际cluster和namespace核对，不把“未配置”当false；本轮只做Cart运行时关闭/恢复，未执行四应用Apollo联动发布。
- 本批修复后的青舟覆盖率尚未重算；下节64%是前一版本已完成报告。未改阈值或排除项。UI矩阵和QA复测仍由测试推进。

## 2026-11-07 后端准入覆盖率

- 发布计划24210、策略37、TEST/test-gtbg-dev-3：`COVERAGE_BE=64%`、`passed=true`、`running=false`，达到真实策略阈值60%。[最终报告与请求证据](artifacts/20261107-coverage-final.json)。
- Product **72.57%（209/288）**，ccm40792；Cart **64.42%（947/1470）**，ccm40793；Order **65.38%（17/26）**，ccm40794；同仓多部署逐行检查均达标。
- 补跑对象：学员7658127801；主计划588858850300473344、小班计划586116340522184704、无关联计划588872241920421888。Cart实际调用7参数getRenewalDetail的新推荐路径；Product真实HTTP执行主计划同集合保存、关联列表及批量/非法编号查询。返回断言通过，主计划关联前后均为585960797778243584和586116340522184704。
- 本轮不改业务代码、阈值、排除项或Apollo；此前本地191项测试通过独立记录，不能计作远端运行覆盖率。幂等保存改变缓存提交版本，未改变关联集合。
- 青舟“刷新”前端处理为读取`getResultSummaryAndDetail`并调用`syncBugStatusByReleasePlanId`，本轮已执行同接口并回读。唯一剩余强卡`USER_CASE=0%`；功能记录72430为88/88、线上回归72431为17/17，冒烟72429为0/17，原因待核实。平台状态不等于本轮实际执行，尚未正式提测。

## 2026-11-06 后端最终生效核验

- 本次后端改动已实际部署到 TEST/test-gtbg-dev-3：cart `4de323d2`、product C/B `455e8ba8`，目标实例均 Eureka UP；cart 首次发布因 Jenkins checkout 连接中断失败，重试后 pipeline 1332530 成功，非代码构建错误。
- cart 定向测试 26 项通过，product 关联测试 16 项通过，order `CartSameClazzOrCourseImplTest` 17 项通过。
- 运行回读：product C 关联计划返回非空版本；无关联计划返回空版本；product-b 关闭纯续开关时保持旧缓存协议；cart 推荐返回主计划+关联计划商品。
- 关联修改后真实预热缓存链路已验证：清空关联后旧预热不再命中，恢复关联并重新预热后命中新结果；无关联老计划保持原缓存键与原规则。
- Order 本次只影响购物车 ADD_CART/CART_DETAIL 的续班跨模式重复校验，未改订单创建、支付、退款等通用订单流程；跨模式加购/下单和同模式重复拦截均已验证。
- 计划编号前端使用文本框按字符串传输，后端 `String` 保留 18 位 ID 与批量精确查询能力，未发现仓内 Long getter 消费者。
- 造数样本已独立回读计划、关联、班级售卖、课节、教师和订单状态；已购用户未再作为未报名样本。

当前需求处于**联调中**：1485167已修复部署并完成接口层回归，等待QA复测；生产配置、QA 用例、历史回溯和部分页面矩阵仍按上线清单推进。

## 本批修复验证（2026-11-06，T-18已完成）

- **最终版本**：TEST/test-gtbg-dev-3，cart1ebd315d（10.218.237.132）、product-b2593dae78（10.218.238.105）、product-c2593dae78（10.218.250.0/26），全部目标实例UP；原MR随推送更新。[版本回读](artifacts/20261106-relation-fix/after/final-versions.json)。
- **改前后同输入**：[9组最终对照](artifacts/20261106-relation-fix/after/comparison.json)：换班报错→返回6004/price0/sign_up1；正反向已购0→1；两已购学员主all_sign_up1；自身小班保持1、未购扩科保持0；主course_numbers未污染。C分支为服务级实测，不称浏览器端到端。
- **缓存**：本地提交/回滚/旧读回填反例11项通过；运行同集合save成功（8b5dd1e4-e2ab-4048-8cc2-888d0f1abf80.0.3），C端读取版本切换、miss→hit均有[日志证据](artifacts/20261106-relation-fix/after/cache-version-evidence.json)。TEST未注入并发故障。
- **受影响旧行为**：本地普通计划null库存不可售/库存异常继续抛出、总开关关闭不补查；关联场景兜底保留。cart65项+product11项均通过，追加字段后相关7项重跑通过（不重复计覆盖）。
- **数据终态**：[独立DB回读](artifacts/20261106-relation-fix/after/db-current.json)与before完全一致，关系集合/两学员订单退款状态未变；无新增支付/退款/库存/Apollo修改，仅同集合save验证缓存。全部部署结束，无待恢复业务数据。
- 本批仅完成T-18；全集保存并发明确不改，order/client不改；其余P0边界仍在T-15。详细改动与限制见[报告](artifacts/20261106-relation-fix/README.md)。

## 关联修改与预热缓存联动（进行中）

2026-11-06 TEST/test-gtbg-dev-3，cart 1ebd315d：真实单用户预热后清空主计划588858850300473344关联，配置已空（trace `cart_gaotu100_com.287.17939638972200038`），但 `corePreheatCache` 仍返回从计划小班586097025945298944（trace `.295.17939638975290037`）；B默认入口fromBCart=true已仅返回主计划。关联全集已恢复并回读，未动订单。原件[缓存基线](artifacts/20261106-cache-invalidation/before/before-cleared-cache.json)。拟增加默认true的Apollo缓存失效开关，让配置/预热键跟随关联提交版本；从未关联的计划保持原缓存键与规则，小班不引入整份推荐结果缓存。已完成实现与TEST验证：真实预热→清空关联→旧预热不命中→恢复→重新预热命中新版本，B端清空后只返回主计划；无关联老计划仍走原缓存键。证据见[缓存失效报告](artifacts/20261106-cache-invalidation/README.md)。Apollo key `renewal.pure.relation.cache.invalidate.enabled` 代码默认true，未配置即启用，false仅回滚。

## 原有排序与筛选兼容性补验（2026-11-06）

当前 cart 1ebd315d 补跑 12 类、125 项聚焦测试，0 失败/错误/跳过，覆盖已购优先、白名单、同科目/同主讲/同时间评分、开课时间及 ID 排序、组合商品、筛选分页、扩科来源及普通计划库存语义。证据：[回归日志](artifacts/20261106-relation-fix/compatibility/regression.log)。MR公共基线与当前类同输入运行确认：原C端展示比较器结果一致；`productList` 实测未购在前、已购沉底、同组保序。owner确认这是原有业务规则，接口排序调用与规则一致，不属于破坏旧逻辑，不应收窄到关联计划。方法级基线的返回顺序差异不等同于产品业务规则变更。方法、输入及原件见[补验结论](artifacts/20261106-relation-fix/README.md#排序与旧逻辑补验2026-11-06)。

## 改前定向运行基线（2026-11-06）

- TEST/test-gtbg-dev-3 当前 cart 镜像 d5729426（IP 10.218.238.95），与 MR284 head 一致；product-b07ba05df、order-b0cc8ef68。证据 [版本](artifacts/20261106-runtime-review/versions.json)。
- 复用主588858850300473344、小班从586116340522184704、学员7707220467和7658129872；DB确认主关联A/B有效，小班后SKU586097025945298944均有order_item/status2/refund0。两班sale40/课节>0/老师非空。没有新造数、订单、支付或修改关联。
- **已复现已购识别不一致**：7707220467在大班主计划返回小班sign_up0/all_sign_up0，自身小班计划返回同SKU sign_up1/all_sign_up1；trace .293.17939592962910012 与 .293.17939593176710014（前缀cart_gaotu100_com）。7658129872亦复现。原件 [主计划](artifacts/20261106-runtime-review/recommend-7707220467.json)、[小班自身](artifacts/20261106-runtime-review/recommend-small-own.json)、[独立DB](artifacts/20261106-runtime-review/db-current.json)。这是当前版本运行事实，覆盖旧“仅静态推断”表述；不推断重复支付一定成功。
- **已复现跨模式换班报错**：相同学员/前后课/SKU，只替换renewalNumber，大班主计划productSelect报“部分商品不存在”，小班自身计划正常返回1件；trace .297.17939593176870012 / .292.17939593176870014。原件 [跨模式](artifacts/20261106-runtime-review/select-cross.json)、[对照](artifacts/20261106-runtime-review/select-small-own.json)。桥rvoCode0不算成功，按errors字段判失败。
- **追加C端计算分支与库存对照**：7参getRenewalDetail同SKU在主计划sign_up0、从计划sign_up1（trace .301.17939593801720014/.293.17939593801680018）；不是浏览器端到端。目标SKU按6004库存18/锁0/已用2，按2报错（.292.17939593801680017/.295.17939593803870015）。主配置回读仍仅自身课。完整结论及优化优先级见[更新审查](artifacts/20261106-mr-diff-review.md)。
- 本轮调用查询方法与独立数据库只读回查；并发保存/事务缓存竞争尚未做运行复现，不将其与上述两项实测等同。

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
