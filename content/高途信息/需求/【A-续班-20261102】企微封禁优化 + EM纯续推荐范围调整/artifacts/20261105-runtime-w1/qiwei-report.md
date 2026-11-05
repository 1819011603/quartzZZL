# 企微与 PRD/Banshan 核查（2026-11-05，已收口）

**最新结论**：默认TEST固定IP/镜像的续班标签读取正例已真实验证，未证实新后端缺陷；两PRD全文及14张原图、Banshan已核。历史错误班号行120554初次读为1,2、后续被外部变为空串，不能当本任务恢复。无本子任务成功写入或在途写操作；标签写入/幂等/恢复因样本并发与独占对象不足停止，备注成功及页面/回溯保留缺口。以下旧快照按采样顺序保留，最终状态见末节。

## 可提前整合的事实

1. **历史标签遗留的实际目标与文档不一致**。TEST DMS cluster149/gaotu-polar-test-02，`ees_data.user_clazz_mark_info` 读到 id=120554、user_id=7658127801、**clazz_number=585960582537144300**、account_id=109942、tags=`1,2`、color=0、layer=0；create_time=update_time=`2026-11-05 14:22:33`。按正确班号 `585960582537144320` 查无行。CAST AS CHAR 与 HEX=821C00B9681E7EC 双重核实，正确班号的 HEX 应为821C00B9681E800。`xbk.user_clazz_mark_info` 同用户无行。不能把接口 code0 当正确对象已落值；是否由原请求数字精度丢失造成尚待原始请求/trace核实。
2. 当前原值证据：目标错误班号这一行创建与更新时间相同，支持“本次新建行”的推断；**不是写前快照，不能据此擅自删行或恢复 tags**。本轮不做恢复。原班号无行仅证明当前状态，不证明写前一定不存在。
3. **真实只读 HTTP 好友校验已完成**：POST `https://test-fuwu.baijia.com/bgwApi/student-center/remark/check/wk/friend`，headers traffic-env=test-gtbg-dev-3、b_client=EES；body `{"userIds":["7658127801"]}`；HTTP200，code0，data.resultStatus=false，trace `6aa83947-e018-4df1-86e1-ff5b8efa5091.0.3`，gapmApp=student-center。只能证明该登录请求未通过企微好友前置，**不证明账号封禁、不证明任务创建、更不证明备注成功**。网关命中实例/镜像尚待日志确认。
4. **标签等效查询已真实调用，但发生泳道 fallback，不算目标版本**：`RenewalService#getStudentRenewalInfosByUserIds("585960582537144320",["7658127801"],["userId","studentTags","studentTagNames","wechatRemark"])`，请求test-gtbg-dev-3，实际 `10.218.250.60:28688` / `student-center-6968ddb64f-8czxj:student-center:28688:@test-eco-1`；trace `student-center.20413993.17938611290030007`，rvoCode0，一行id=36622538973250048-7658127801，不含studentTags/studentTagNames/wechatRemark。明确改为test后另一次命中default `10.255.176.174:28688` / student-center-5d84df769-gxbql，trace `student-center.900337.17938611290041532`，同样无标签字段。均不能据此认定目标泳道后端缺陷。
5. 补充 EM 真实只读调用（不替代主 Worker 推荐验收）：cart `10.218.237.47:28688/test/acl/compare/service`，Host CART.GAOTU100.COM，目标及实际instance均test-gtbg-dev-3，pod `cart-gaotu100-com-79789ddcf4-vqnpj`（历史镜像映射a34016fd，当前镜像未重查）。`com.gaotu.renewal.RenewalService#getRenewalDetail` params=["7658127801","585960797778243584",false,false,null]，trace `cart_gaotu100_com.298.17938610073420112`，rvoCode0；返回grade16大班SKU585960755422160896/type2/sign_up1 + grade11小班SKU586097025945298944/type6004/sign_up0，后者price=-1。getContext=true trace `cart_gaotu100_com.299.17938610073500118` 明确主从前置均过订单过滤并各命中后置。只证明本样本双模式并集，不证明扩科不变/所有时间年级/可下单。

## 本轮操作边界

- 仅本报告与同前缀证据文件允许写；未修改代码/配置/部署/共享归档/飞书/Banshan状态。
- 一次误列入批量调用的 `/batchOperate/tag/save` 未带注册路由前缀，工具返回 `路由解析失败(no_match)`，**未形成HTTP调用**；未重试写接口。完整披露，后续仅查询。
- 企微封禁优化是补齐续班标签/备注与规范提示，不是自动解封功能。好友false不能替代封禁/正常账号对照。
- Q6 iris与Q7 reach-widget仍属需求验收范围；前端不改仅限制实施归属。

## 待补

该阶段待补已在后续章节补齐；当前不把历史静态核对算本轮运行态验证。

## 14:51 增量：状态变化与版本边界

- 最新只读快照 `tag-baseline.txt` 显示历史 id120554 的 tags 已变为空串、update_time=2026-11-05 14:43:16；本子任务没有发出有效写请求、没有清理此行。初次读回1,2与后续空串应按时间分别保留，不能说“本轮已恢复”；变更来源待主 Worker 协调。
- Eureka当前14实例 **无 test-gtbg-dev-3**；完整实例 metadata见student-center-eureka.json。默认TEST有两版本，选择并固定 `10.255.176.174:28688` / student-center-5d84df769-gxbql，实际镜像 `release-5dce9cdb-20261103201632`，UP，证据student-center-pods-detail.json。另默认实例10.218.238.176是df66fed8，不可混用。
- TEST配置实查：es_query_config中大班872/873/874分别studentTags necessary、studentTagNames extra、studentTags basic，均is_del0；小班562/599/621同类配置存在。student_field_config1834–1837大小班studentTagNames/微信备注均存在、editable1/filter1；备注field_number=238628096341720064，标签193322071548238848。证据es-config.txt、field-config.txt。配置存在不等于页面/ES效果已验。
- 两PRD本轮全文读取：企微W4ftd48kFoq1LyxMrVYc1AhynFe rev253、纯续WDYOddTNloOrunxiCzmcnNzJnFe rev675。Banshan 2026-11-05 14:47:45 拉取case50162/record72343，377节点/120测试点，原始priority=1计30、2计75、3计15，未出现0。不能声称平台120条皆P0。仅选与核心需求对应项目组成精简P0；平台未执行/未回写。

## 最终真实验证：默认 TEST 固定实例标签读取正例

**已验证（本次真实链路，不是单测）**：固定目标 `http://10.255.176.174:28688/test/acl/compare/service`，Host STUDENT-CENTER、traffic-env=test；instanceId=`student-center-5d84df769-gxbql:student-center:28688:@default`，metadata.trafficEnv=test，镜像`release-5dce9cdb-20261103201632`，Running/UP（Pod与Eureka双证）。

完整请求：
```json
{"serviceNameAndMethodName":"com.gaotu.yunying.student.center.domain.service.roster.RenewalService#getStudentRenewalInfosByUserIds","params":["574882679202260992",["7489648821"],["userId","clazzNumber","subclazzNumber","joinClazzTime","studentTags","studentTagNames","wechatRemark"]]}
```
实际：HTTP200、rvoCode0；trace=`student-center.900338.17938614686501583`；返回`clazzName=续班归因-正经前置班-0820`、clazzNumber=`574882679202260992`、subclazzNumber=`35930168009949440`、userId=7489648821、id=`35930168009949440-7489648821`、studentTags=[2]、studentTagNames=["需中关注"]。同次DB证据：ees_data.user_clazz_mark_info id120542同user/clazz、tags='2'、account_id90247。原始完整响应与复现curl：`tag-known-positive-default.txt`。

预期依据：企微PRD253要求续班服务标签值与默认花名册一致，存量TEST样本已有标签2。**本次返回标签ID与标签名、DB现值一致，未证实该读链路存在缺陷，不修改后端。**覆盖限该大班样本的服务层读取；没有经过浏览器、GAIA可见字段/老师行权限/筛选接口，也不是新写标签的读后写验证。未查原始ES GET，故不宣称全ES及页面通过。

另一次固定同IP真实HTTP POST `/remark/check/wk/friend`，body={"userIds":["7658127801"]}、Host STUDENT-CENTER、traffic-env=test、b_client=EES，返回HTTP200但**code3/登陆信息获取异常**，trace=`student-center.900339.17938614405711575`，见`friend-default-direct.txt`。这是直连缺登录上下文，不能把HTTP200记成功；没有伪造鉴权头绕过。网关好友false已由前文真实请求证明；对应trace_tree仅采到网关/CAS层，SLS/TLS error查询均0，未确认网关后端pod，因此不声称命中上述固定实例。

**写测试状态**：本轮未成功提交任何标签写请求、未创建业务行、未清理120554；无在途写操作。7658127801出现外部并发修改后已停止全部写入/恢复准备，按主Worker要求保留现状。现有7489648821只作只读正例，非独占测试对象，不拿它尝试写入。正向保存、同值幂等、原值恢复尚未执行；下一步需独占TEST班级/学员（原行及关联表/ES基线明确）和可用真实HTTP鉴权链路。该缺口不是后端bug证明。

## 原始材料与附件完整性

- 已完整读两PRD当前正文，分别`qiwei-prd.json`（docx W4ftd48kFoq1LyxMrVYc1AhynFe rev253）与`em-prd.json`（docx WDYOddTNloOrunxiCzmcnNzJnFe rev675），Wiki已分别解包。
- 两PRD正文共有14张图片：企微4、纯续10；本轮全部用lark-cli实际下载且逐张打开查看，文件`qiwei-img-1..4.png`和`em-img-1..10.png`，SHA256清单`media-manifest.json`、下载回执`media-receipts.json`。未发现source文件附件、sheet、bitable、whiteboard。
- 已确认图片差异：em-img-3仍写“最多可绑定5个”，em-img-4示意含已结束/单选；最新正文明确最多10可配置、仅待开始/进行中、多选，验收以正文为准。企微图3/4明确说明链接属于提示区，不能作为待发送内容/可编辑输入。
- 引用文档（二讲规范、顾问规范、小班旧规则）复用frontend-review.md此前全文核对事实，本轮没有重新完整读取其图片；大班旧规则docs.baijia.com此前OAuth拦截仍是引用材料缺口，本轮未重复尝试。不能宣称所有引用附件均已本轮完整读取。
- 没有重新拉取或改写主Worker负责的P0 Wiki。前端版本/代码结论复用共享frontend-review.md：cronus feature-wecom-ban-optimization@17ee81ccb44b95655f1a55494c4d9372b604cc34已接Q1-Q4、reach-widget0.1.5-beta.4；本轮未核远端SHA、未重跑同版本函数测试。页面部署版本仍未知；iris旧生产chunk仅历史采样，不当本轮新版缺陷证据。

## Banshan 核对及精简P0建议

原始脑图`banshan.json`、索引`banshan-index.json`、精选节点全文`banshan-selected.json`。case标题“纯续关联推荐-业务场景测试用例”，record功能用例；拉取时passCount/successCount/blockCount均0；没有执行或写回状态。原始priority只有1/2/3（30/75/15），本报告按需求风险重新精简P0，不机械把优先级数字转成“已验P0”。

必须纠正的用例前提：

1. **历史回溯按创建时间的QW-G003/QW-B04-001..004及公共前置需要替换**：owner最终有效口径是班级最早课节开始时间min(begin_time)≥2026-01-01，包含当天、含大小班，不按学员报名时间、不额外补clazzRoomType。至少两侧边界：2025-12-31最后时刻不入本批，2026-01-01 00:00:00入本批；同时使用“创建时间与开课时间跨边界”的反例区分字段。回溯任务输入、源标签、目标ES和数量需核对，不把实时读取正例当历史全量完成。
2. **QW-G001/G004与部分链接用例的实际发消息步骤不纳入本轮**：保留标签/筛选/打开规范/切换私聊群聊、取消无写入；当前授权不发送消息。群发回执不是本次新规范链接功能的必要验证。
3. Banshan张老师/陈晨/10001/D101/U101等为说明性占位数据，不是已存在真实TEST账号/商品；不能直接抄成现场卡。已有真实样本表与权限/好友前置仍需补齐。
4. REN-B07-006“不同部门或主体组合沿用原限制”需以PRD澄清：只按收款主体限制，不能新增按部门互斥；TC-G005等移除后立即看到新结果需保留已接受B8的26h预热窗口，使用未预热样本或明确等待，不承诺立即全入口刷新。

企微建议保留4张精简执行卡（每卡大小班分别记结果，不合并判通过）：

| 卡 | 复用节点 | 核心步骤和必要反例 | 当前实际覆盖/缺口 |
|---|---|---|---|
| 标签闭环 | QW-B01-001/002（5196c5bb8be84d54、bf3cb8e5e56240a4）+QW-B02-001/002（ec888e28ae7b4e9c、ec7f3c87e1d64e4e） | 在独占TEST同两名学员记录原集合，批量保存→刷新→只编辑一人→标签筛选；未选学员保持、取消无写入、长ID字符串精确落目标班；恢复原集合并回读 | 本次默认TEST大班标签读正例成功；批量/单人写、筛选、幂等、恢复未做，不能整卡通过 |
| 备注及前置 | QW-B03-001/002（b8cfbe7420674fb5、1775e43999594473）+未加好友199b8f1395154ae0 | 两名可操作TEST好友按默认花名册模板修改；任务完成后逐人核实际备注；混入未加好友只按原规则提示，不把任务受理/部分成功当全部成功；恢复原备注 | 网关好友false已实证；直连因code3失败；真实成功备注任务/正常与封禁账号对照未做。好友false不证明封禁 |
| 规范链接 | QW-B05-001/002（a3f0d910988349e4、23bebdb98448400b）并补顾问入口edac396a0f9b4f73 | 默认花名册/课节学员/我的线索/联系学员分别打开私聊群聊说明；二讲→Af3VwjizwiKxDhkUFtEcvpZpn4P、顾问→Ar7YdcPqsowMITxRBNacwjkpn3d；只打开/取消，不发送 | Q6/Q7属于需求内前端交付依赖，不能因禁止改前端标范围外；本轮页面没做 |
| 回溯边界 | QW-B04-001（da48bbe455394f5a）和修正后的002/003/004 | 用最早课节开始时间圈班，大小班边界正反例+源标签空值；核任务范围/完成失败量及ES与列表 | 外部任务/字段集/执行与ES全量证据仍缺；本轮不跑回溯 |

具体现场执行阻塞：未取得独占可恢复标签样本；未取得具备页面可见权限且已验证企微好友的正例；目标student-center泳道不存在；默认TEST直连HTTP需真实鉴权上下文；iris/reach-widget部署及各页面链接效果未验；回溯由大数据圈班/落任务表、EES补字段集和Job、执行者ES回读，当前不改配置/不跑任务。

## 最终三档与交接

- **已验证**：两PRD当前全文、14张原图、Banshan现状；TEST两表定位和标签遗留精确班号；配置10+4行；网关好友false；默认TEST固定IP/镜像的标签读取正例及DB一致；默认IP好友校验鉴权失败；cart指定泳道真实主从推荐正例（镜像映射此子项未重查，交主Worker合并）。
- **推断未验证**：错误班号来自历史原请求精度丢失；旧行初次创建说明写前无行；网关好友校验命中的具体版本；实际前端需求分支是否已经部署；这些均不作为修复依据。
- **没做/阻塞**：标签正向写-幂等-恢复；真实备注成功/封禁与正常账号对照；浏览器全入口/真实筛选；原始ES文档读取与全量回溯；生产配置；前端/后端改码、commit、部署、消息发送。**没有运行证据确认新后端bug，不修改代码。**
- 无本子任务在途业务写、部署或持久会话；主Worker可直接整合本报告与证据，历史120554变更来源需协调，不由本子任务恢复。
