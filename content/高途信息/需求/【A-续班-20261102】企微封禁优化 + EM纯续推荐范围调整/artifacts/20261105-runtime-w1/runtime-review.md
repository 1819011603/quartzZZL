# A-续班-20261102 本轮运行证据与交付核对

## 工作单状态

- **已完成：统一需求与材料**。同一主需求两子项，企微PRD rev253、EM rev675及14张原图已核；Banshan case50162/record72343 120条按风险选核心P0，未回写平台。需求契约Q1–Q9、E1–E16见P0-case.md及飞书同一文档。前端两个远端SHA仍与既有报告一致。
- **已完成：两子项修改前真实调用**。EM管理和推荐均绑定目标泳道/镜像/IP；企微目标泳道无实例，固定默认TEST等效服务完成标签读取+DB对照，好友直连鉴权失败与网关false如实记录。正常子集不改后端。
- **本轮未新增后端修改/commit/push**：无运行证据证明新的后端缺陷；不得把静态疑点改成代码。复用既有已推送product/cart/order交付，不冒称本轮修复或修后全通过。
- **已完成：P0文档维护与回读**。同一Wiki对应docx ZQUXdlDxWoknJhxu914c2uVYnBr，revision99；12卡、25项契约、直连命令、正反例/恢复/责任/缺口齐备；不是12卡全部执行通过。
- **未完成/阻塞：全需求验收**。标签写/幂等/恢复缺独占可恢复样本及真实HTTP鉴权；备注成功缺可用TEST好友与账号对照。EM不同学年学期隔离、碰撞去重、本地缓存组合/异常回退、新版完整下单与主体/优惠、页面/回溯未全验。

## 仓库、基线与既有交付

后端工作区均在 `/Users/gaotu/IdeaProjects/JavaProject/`；统一需求分支 `feature-xuban-pure-relation-20261102`。

|仓库|当前本地/远端|既有基线锚点|说明|
|---|---|---|---|
|product-server|07ba05df6cfabcf0472e1ad27e26ff95cff98467，同远端|bee4630d88c9dabca426cffa57dc8989e5f2cf68|工作区干净；本轮查询正常不再改|
|cart|a34016fdf206d0163b1dd473c67ac10674ecb4b5，同远端|3e1e366ca643a2c823abbfa9186589a3d4f65972|工作区干净；既有主缓存隔离与扩科上下文修复|
|order|0cc8ef68b6c29f1d3101f5fa08ea7ec634050bf9，同远端|a97904147c3f9793b94a4c453161609da08c20f4|工作区干净；既有跨模式后真重复漏检修复|
|student-center|仅本地同名分支396d84f076d066c652a49ce39e68b9b917c242e0|本地origin/release无diff|实时ls-remote无同名分支；没有本轮源码交付，不造占位远端分支|

product既有改动落点：RenewalMasterRelationController/Service、RenewMasterRelationBizMapper与XML、RenewalMasterListQueryBO及DTO/request。cart最近改动为RenewalDataService、RenewalService、ExpandSubjectRecommendService、SmallRenewalPreheatService及测试；order为CartSameClazzOrCourseImpl及测试。文件明细见backend-report.md与既有diff-p0报告。上述基线为归档锚点，本轮不更改基线或重新拉分支。

前端只读：gaotu-fe-promotions远端指定分支ba1cf8f9ffee5269e49331e7f7f2bd42e5137183；cronus需求分支17ee81ccb44b95655f1a55494c4d9372b604cc34。两者实时ls-remote未变，沿用既有源码核对；线上Git SHA/页面版本仍未映射，未改前端。

## 真实结果与证据

|子项/场景|环境/版本/输入|实际/关键证据|
|---|---|---|
|EM管理关联|product-b 07ba05df，test-gtbg-dev-3，10.218.248.248:28688，A585960797778243584|返回B586116340522184704、字符串ID及管理员；product-direct-current.json，trace product-b.258.17938612055100011；文档curl复跑.261.17938612536690012|
|批量/非法/反向关联查询|同泳道网关，A/B中文逗号、not-a-plan、B|total2/total0/B空，product-*-current.json，trace e919e0e0/a345a13d/4899b6bb|
|EM推荐与单向边界|cart a34016fd，10.218.237.47:28688，学员7658127801|A五/七参主大班+从小班；A扩科仅grade16；B只有自身小班。cart-A/B-*.json；完整trace与请求见backend-report.md|
|EM缓存命中|同IP重复A七参|前置课/旁路订单正缓存hit=true，cart-runtime-log.txt，同trace cart_gaotu100_com.301.17938612443150115；不代表负缓存/故障/Guava隔离全过|
|反向B→A|复用同版本14:33原始调用，不重放|save458e4e7b、推荐.299.17938604090680110、清理094a3ee4原始请求响应已定位；DB/Apollo恢复原件未找到，仅归档记录；当前B为空已另验|
|企微标签读取|默认TEST student-center release-5dce9cdb，10.255.176.174:28688，学员7489648821/班574882679202260992|studentTags=[2]、studentTagNames=[需中关注]，与DB id120542一致；tag-known-positive-default.txt，trace student-center.900338.17938614686501583|
|企微备注前置|默认TEST同IP，用户7658127801；另调用真实网关|直连code3登录异常（.900339.17938614405711575）；网关code0/resultStatus=false（6aa83947...），不证明备注成功或账号封禁|

完整执行输入、返回、版本、原始日志在本目录相应JSON/txt；已回读摘要见document-verification.json，文件校验值见manifest.json。两个子任务原报告各自保留证据范围；不把子任务complete当整需求完成。

## 程序测试与运行结果分开

既有140例（product20/cart94/order26）0失败/错误/跳过已核计数，未重跑。product/order XML保留在原artifacts/20261105-diff-p0；cart计数JSON与摘要可用，完整TestSuite原件本轮未找到。单测不证明运行态修复条件全覆盖，order历史原始HTTP文件未找到，不伪称本轮新下单。编译命令未重跑，因为本轮没有代码变化。

## 未完成、资源与责任

- student-center目标泳道无实例；默认TEST等效读取已验，HTTP写鉴权/老师好友和独占样本仍缺。共享用户7658127801有外部并发标签变更，不再写入/恢复该对象。
- 错误班号行120554的班号实际为585960582537144300，不是585960582537144320；初读tags=1,2，后续外部改为空串。没有原始写前快照，不推断本轮清理成功或后端精度bug。原请求/变更来源需协调。
- 前端交互及规范链接：金瑞琳；产品取舍：王永诗；历史回溯圈班与落表：大数据lichenhao02/闫旭，字段集/Job及ES验收由EES/student-data交付链负责。未联系他人、未发布、未修改生产。
- B8保留26小时；同课不同班级商品合法，不新增互斥。代码回退不自动恢复数据，执行前需原值快照。
- 本轮无成功业务写入、无新增订单/购物车/关联数据、无部署/Apollo修改、无在途后台任务；两子任务已结束。既有外部写入不能算本轮恢复。
