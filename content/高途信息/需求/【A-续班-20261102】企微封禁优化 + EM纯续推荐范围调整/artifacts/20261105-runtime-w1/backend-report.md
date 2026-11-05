# cart/order 当前交付与真实链路核验

核验时间：2026-11-05 14:41—14:50（Asia/Shanghai）。范围：当前版本核实、已有证据复用、EM 推荐同IP只读调用。未改代码/commit/push、未部署、未改Apollo或前端、未新增业务订单/购物车/关联数据；无恢复项或在途操作。以下完成仅指本子任务核验报告，不代表整需求/P0全部通过。

## 结论

当前 cart 正向纯续并集、无反向关联时B保持自身、五/七参本样本行为符合预期；七参有纯续/扩科类型区分，日志证实关系前置课及订单旁路缓存命中。没有本轮运行实证缺陷，因此不新增修复。扩科学年学期隔离、开启本地缓存后的污染/回退反例、碰撞去重等仍未完整验收，不能以历史140例或当前正常样本替代。

## 精确版本与目标

青舟只读 `find_namespace_group(service,'test-gtbg-dev-3','dev')` 原始字段在 `backend-pods.json`；logicEnv为dev、namespace为test-gtbg-dev-3，均Running/Eureka UP。

|服务|Pod|IP|imageName|
|---|---|---|---|
|cart|cart-gaotu100-com-79789ddcf4-vqnpj|10.218.237.47|feature-xuban-pure-relation-20261102-a34016fd-20261105114326|
|order|order-gaotu100-com-756b5754fd-jzk6p|10.218.236.236|feature-xuban-pure-relation-20261102-0cc8ef68-20261105114818|
|order-b|order-b-gaotu100-com-555655ff-kxfxv|10.218.237.111|feature-xuban-pure-relation-20261102-0cc8ef68-20261105114404|
|product-c|product-gaotu100-com-5fbb74bd96-fxxng|10.218.251.115|feature-xuban-pure-relation-20261102-ab120d4e-20261103232835|
|product-c|product-gaotu100-com-5fbb74bd96-2h6n9|10.218.238.47|同上|

**product-c不是product-b的07ba05df，文档应按部署服务分列SHA**。product-b由主Worker核实，不重复。

cart实际HTTP端口28688来自Eureka桥实际返回及成功请求；instanceId=`cart-gaotu100-com-79789ddcf4-vqnpj:cart.gaotu100.com:28688:@test-gtbg-dev-3`。最初用pod命令`--env test`取到的是默认test实例，已排除，不能混算目标泳道。正确Pod读取为`--env dev --pod-name cart-gaotu100-com-79789ddcf4-vqnpj`。

本地及实时远端同名需求分支一致、工作区干净（`cart-git.json` / `order-git.json`）：cart `a34016fdf206d0163b1dd473c67ac10674ecb4b5`；order `0cc8ef68b6c29f1d3101f5fa08ea7ec634050bf9`。只读取远端；credential-helper发出failed to store警告但ls-remote取得上述SHA。

路由查询正常：cart appId `cart.gaotu100.com` 的 `/cart/**`，StripPrefix=1，查询给出fuwuBase=`https://test-fuwu.baijia.com/bgwApi/cart`；order-b的 `/orderComponent/**` 无rewrite，fuwuBase=`https://test-fuwu.baijia.com/bgwApi/orderComponent`。本轮推荐直接用已核实IP，未依赖网关fallback。

## 本轮真实调用（完整输入、响应、headers与trace均落JSON）

统一URL `http://10.218.237.47:28688/test/acl/compare/service`，POST；请求头`Host:CART.GAOTU100.COM`、`traffic-env:test-gtbg-dev-3`、JSON Content-Type。全部HTTP200/code0。

统一学员U=`7658127801`，A=`585960797778243584`，B=`586116340522184704`。七参含`getContext=true`，不清预热、不切开关。

|文件|serviceNameAndMethodName/params|实际关键响应|trace|
|---|---|---|---|
|cart-A-five.json|com.gaotu.renewal.RenewalService#getRenewalDetail / [U,A,false,false,null]|grade16/SKU585960755422160896/type2/sign_up1；grade11/SKU586097025945298944/type6004/sign_up0|cart_gaotu100_com.297.17938612416400117|
|cart-A-seven.json|同方法 / [U,A,true,false,null,null,false]|上述两项recommend_type=1；另grade16下SKU585963387758962688和585963404555053056为recommend_type=2，type2；未出现grade11/12扩科|cart_gaotu100_com.298.17938612420770116|
|cart-B-seven.json|同方法 / [U,B,true,false,null,null,false]|仅grade12/SKU586090628920764416/type6004/recommend_type1；无A大班SKU|cart_gaotu100_com.299.17938612431590122|
|cart-A-seven-repeat.json|同A七参|与首次七参业务结果相同|cart_gaotu100_com.301.17938612443150115|
|cart-A-plan.json|com.gaotu.renewal.RenewalDataService#listRenewalMasterByRenewalNumber / [A]|course_numbers=[585960577856301056]，related_renew_master_numbers=[B]；重复合并请求后原始计划自身课程未出现B|cart_gaotu100_com.300.17938613026340113|
|cart-B-plan.json|同DataService方法 / [B]|course_numbers=[18314034380997173]，related_renew_master_numbers=[]|cart_gaotu100_com.299.17938613028070124|

A七参`msg`提供真实上下文：前后置关系同时含主前置585960577856301056与从前置18314034380997173；订单过滤后仍为两者；后置库存/售卖过滤后候选585960755422160896与586097025945298944，最终各命中一项。由此可证明订单过滤没有丢失从计划，而不只是“返回两个SKU”的推断。

期望依据：已确认A→B只把B前置课程并入A的纯续；从计划规则不独立替换主规则；扩科保持主配置。只有A→B时B不应反向扩大，显式B→A后才应B∪A。当前B关联为空且推荐只有自身，符合该边界。本次不再次写B→A，历史显式反向证据单独引用，不能宣称本次双向整卡都测。

## 缓存、扩科与N+1的证据边界

`cart-runtime-log.txt`是从上述目标Pod提取、与A重复七参同一trace的原日志：
- `renewal relation precourse cache read ...586116340522184704, hit=true, empty=false`
- `EM pure relation merged courseNumbers ... size=2`
- `renewal cross-mode order cache read ...7658127801:i2i:90bd4dd855c5eaf74fcb223d3b5db57b, hit=true, empty=false`
- `扩科推荐完成(大班课), matchCount=2`

已验证的是关系前置课缓存、订单旁路正缓存命中，不能外推为Guava主计划缓存隔离、负缓存、Redis异常、开关关闭、TTL、预热失效全通过。连续请求后A原始课程仍仅主课已读回，但未开启/改动本地缓存组合，故不能声称复现并验证了缓存污染条件。

A两项扩科均grade16，纯续从计划为grade11；真实结果符合当前配置。然而主从前置课学年学期均为2026/C，且没有从年级的隔离候选，不具有证明不同学年学期来源正确的区分力；该反例仍未覆盖。

N+1量级（代码结构说明，**不是本轮多从计划压测结果**）：`RenewalDataService.resolveRelatedPreCourses` 对N个从计划逐个读缓存；多于1个miss正常走一次批量RPC，单个miss走一次单查，批量异常才回退最多N次单查。订单旁路对合并课程集合一次查询/缓存，不按从计划逐条查。N≤10时，计划查询正常约主1+从批量1，失败退化主1+N；缓存读写仍O(N)。本轮N=1且命中正缓存，只实证无从计划加载RPC需求的命中路径，不证明N=10性能或所有下游调用总数。

## order复用证据及owner口径

归档verify第三轮记录同一已部署0cc8ef68真实HTTP，避免重复业务写入：
- 跨模式user7658127801，大班585960755422160896/type2+小班586097025945298944/type6004，code0/cart588822622182119424，trace `075b6713-5905-47b5-ad4b-208d9434bcc7.0.3`。
- 已有同课程两个不同班级商品587571298255841280和587571308498331648，再加同商品587571298255841280，code1，data包含SAME_CLAZZ/SAME_COURSE，trace `961693ca-b5a0-4542-948d-0b11fe9eafd9.0.3`；该证据不是ONCE_BY_LIMIT提前拦截。
- 同次加入上述两个不同班级商品code0，trace `9f7e90f4-7665-4f52-bf3e-9024cf44e069.0.3`。**owner已确认不同班级=不同商品合法加购，不能以SAME_COURSE静态分析把它改成禁止。**
- 清理证据归档记录removeCart两次、b_cart有效行读回，trace `6c05e409-f21b-4540-a13c-b46292e5f393.0.3` / `66b0fdde-6eef-45e4-946b-7301464caadb.0.3`。

本轮仅复用归档记录并核镜像相同，不宣称新执行order写入。当前目标Pod app.log按这三条历史trace未匹配到记录，`order-original-runtime-log.txt`仅记录查询命令回显，**不是原始成功日志证据**。完整原始HTTP文件本轮未找到，此项保留归档证据等级；未为补原始日志重新加购。

## 已有代码和测试证据（未重跑）

cart本轮进入时最新提交a34016fd：4生产文件（RenewalDataService、RenewalService、ExpandSubjectRecommendService、SmallRenewalPreheatService）+4既有测试文件，200增/10删；整个需求分支相对本地origin/release为21文件1505增/39删。order最新0cc8ef68：CartSameClazzOrCourseImpl及其Test两文件，120增/16删；整个需求分支两文件160增/16删。本子任务新增代码文件=0，仅写/tmp证据。

原始归档位置：`/Users/gaotu/githubDir/quartzZZL/content/高途信息/需求/【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整/artifacts/20261105-diff-p0/`：
- `cart-final-tests-summary.log`：2026-11-05 10:52:14，94/0/0/0 BUILD SUCCESS；`cart-test-counts.json`列11类94例。报告引用的完整cart-final-tests.log/TestSuite.xml本轮在归档目录未找到；现有summary含TestNG No test suite提示，但后续实际94例计数与BUILD SUCCESS明确，不据提示否定实际结果。
- `order-green-summary.log`：10:56:17，17规则+9历史H2回归=26/0/0/0 BUILD SUCCESS；`order-red-summary.log`为修前红灯。
- `product-tests-summary.log`：8+8+4=20例摘要，主Worker负责完整证据；其中混有早期依赖失败，不将全部命令说成一次成功构建。
- 因SHA未变，复用140例历史结果，不全量重跑、不把单测等同本轮接口修复验证。

## 收口分档与剩余

**已验证**：准确目标镜像/UP/IP与远端一致；A五参纯续双模式、A七参双模式纯续+主grade16扩科、B无反向关系且只自身推荐；A真实上下文证明双前置订单过滤后保留；关系前置课与跨模式订单正缓存命中；连续调用后A自身课程读回仍单主课。

**推断未验证/待专门样本**：不同学年学期/从年级扩科不扩大的反例、启用本地缓存组合后的隔离与关开关回退、真实重复候选去重与跨年级保留、多从计划批量和故障降级、全部入口/预热与order最新版完整下单。仅无重复输出不能给P0-06整卡通过；正向样本不能给P0-04全卡通过。

**没做**：显式反向写入复测、故障注入、清缓存/B8变更、部署、前端、生产、业务数据写入；没有运行证据新增缺陷所以没有后端修改。企微子项不在本次owner范围，由主Worker整合其他负责人的实证。

需主Worker决定：只需按上述证据等级纠正文档，不需要批准新修复或部署。复杂反例按最新指示不强造，本次范围内核验与报告完成。


## 增量：第六轮反向补验原始证据已定位（只读取既有日志）

本次续接先核cart HEAD仍a34016fd、工作区干净。限定检索/tmp/w1-e9aebdb9和本需求artifacts：只命中verify.md及card-state-current.json的文档叙述，未找到该轮原始HTTP文件。随后按**指定trace**读取已知目标cart/product-b的app.log，找到了真实历史请求和响应，不重放任何接口、保存、部署或Apollo操作。

1. **真实保存B→A**：product-b-7d48b8fb74-lxqvg（主Worker已核07ba05df，10.218.248.248）日志时间14:33:12.721；POST /b/renewMaster/relation/save，b_client=EES；请求 `{"subRenewMasterNumbers":["585960797778243584"],"mainRenewMasterNumber":"586116340522184704"}`；14:33:12.817响应 `{"msg":"success！","code":0}`；完整trace `458e4e7b-7243-45a7-a4d1-a0c62806eeae.0.3`。
2. **反向推荐确实扩大**：cart-gaotu100-com-79789ddcf4-vqnpj（已核a34016fd，10.218.237.47:28688）14:33:30.124原日志，Host=CART.GAOTU100.COM、traffic-env=test-gtbg-dev-3；ACL方法com.gaotu.renewal.RenewalService#getRenewalDetail，params=["7658127801","586116340522184704",false,false,null]；code0；grade16/SKU585960755422160896/type2/recommend_type1，before585960577856301056；同时grade12/SKU586090628920764416/type6004/recommend_type1，before18314034380997173。trace `cart_gaotu100_com.299.17938604090680110`。这是同镜像、同实例的历史真实反向样本，**可复用为小班主→大班从接口子集已验证**，不再仅依据归档文字。
3. **真实清理保存B→[]**：同product-b Pod 14:33:45.423请求同save入口，body `{"subRenewMasterNumbers":[],"mainRenewMasterNumber":"586116340522184704"}`；14:33:45.506响应code0；完整trace `094a3ee4-c692-4e79-bb3c-f47ae7e81852.0.3`。此外本子任务14:48的cart-B-plan.json已真实读到B.related_renew_master_numbers=[]，cart-B-seven.json只返回B自身小班，作为清理后运行态结果补充，**不替代DB id14软删的原始证据**。
4. **仍仅归档记录**：DB id14新增/软删的当时查询返回、Apollo release20261105143303/20261105143430及白名单恢复[]的发布回读，限定现有文件中未找到原始结果。本次不重查/修改Apollo，不补写DB，不宣称已独立复核这些恢复细节。

证据文件：cart-reverse-original-log.txt（含完整桥请求与业务响应）；product-reverse-save-cleanup-original-log.txt（4条真实请求/响应日志，身份header已脱敏，保留业务body和trace）；reverse-original-evidence.json（结构化提取，回读校验两次save均code0）。

最终口径：本轮已定位同版本反向接口证据，结合当前只有A→B时B不扩大，两种关系状态的业务表现都有真实记录；这些历史调用发生于本子任务之前，不能写成“本次重新执行”。P0-04接口方向子集可以补齐，四类页面入口、全场景及相关恢复原始DB/Apollo证据仍不能标整卡通过。无需新增修改或范围决定。
