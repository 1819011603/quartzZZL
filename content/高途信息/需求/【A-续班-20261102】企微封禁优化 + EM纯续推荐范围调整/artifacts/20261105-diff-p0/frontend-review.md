# A-续班-20261102 前端与PRD核对（2026-11-05）

结论：指定前端分支已更新，旧批量ID/搜索管理员缺陷不能继续沿用；仍有已选排序、选择上限、移除确认时机差异。**企微实际需求分支 `feature-wecom-ban-optimization@17ee81c` 已实现Q1–Q4源码接入（含大班Legacy），master未合入不能当作尚未开发；Q6仍依赖iris，Q7升级了新依赖但内容未验证。**生产iris旧文案证据保留为此前采样事实。本报告完成只读调查和页面 P0 操作设计，**不等于页面验收通过**。

## 1. 固定版本、diff 与来源

| 对象 | 本轮证据 | 边界 |
|---|---|---|
| gaotu-fe-promotions 指定远端分支 `feature-pre-register-coupon-recommend-deduction` | `ba1cf8f9ffee5269e49331e7f7f2bd42e5137183`，独立 checkout `/tmp/w1-13ca5996/frontend-readonly`，工作区干净 | 不代表线上发布版本 |
| 相对上轮 `bfadc6fde5e165a2d72baecdc9e5cf76ce674fd1` | 2文件，+56/-26；新增状态/测试数据筛选、搜索管理员渲染、全量保存确认；去掉ID单数字校验 | `frontend-vs-previous.diff`，新增提交 e380e34、bc2cbf5、ba1cf8f |
| 相对最新 master `04e53e355152733164da65c2ba86a00c19eaa690` | merge-base 即该 master；6文件，+672/-26；新增纯续抽屉/样式、列表入口、list/save API、mock、反讲文档 | `frontend-vs-master.diff`；相对 release `00d72b53d9b26d0bbc9d5cbfd49efa873da08166` 的共同祖先 diff 同统计。未改推荐页/C端页面 |
| cronus | 远端 master `ca7039277d44571f111b0756e7d5662c34453328`，与上轮相同；release `e2bc7f92fb0a92615c8d5a377ec40f04a77b69de`；无用户指定同名分支 | 复用干净 `/tmp/w1-e0be7208/cronus-remote-master`。结论限 master，不能断言其他开发分支均未做 |
| cronus 实际需求分支（本次补核） | `feature-wecom-ban-optimization@17ee81ccb44b95655f1a55494c4d9372b604cc34`；相对上列master 27文件+551/-220；独立checkout `cronus-feature-readonly` | Q1–Q4已实现源码接入；未核上线/未做页面。详见§7 |
| product-server（仅契约交叉核对） | 本地 `07ba05df6cfabcf0472e1ad27e26ff95cff98467`；主 Worker 最新确认 TEST product-b 同版本实际HTTP | 后端修复与测试归主 Worker；不重复调查 order |

PRD 最新全文已读取：
- [企微 PRD](https://gaotuedu.feishu.cn/wiki/ZiRZwGOJGi3CtnksQg1cJwZsn9b)：revision **253**，`qiwei-prd-current.json/.xml`。
- [纯续 PRD](https://gaotuedu.feishu.cn/wiki/UewqwsMWOiunOgk9Kloce1Jrn52)：revision **675**（上轮659），`em-prd-current.json/.xml`。新增明确“状态默认待开始/进行中、过滤测试数据默认是”。
- [二讲规范](https://gaotuedu.feishu.cn/wiki/Af3VwjizwiKxDhkUFtEcvpZpn4P) revision562、[顾问规范](https://gaotuedu.feishu.cn/docx/Ar7YdcPqsowMITxRBNacwjkpn3d) revision465，全文分别见 `qiwei-guide-teacher/adviser.json/.xml`。
- [小班既有纯续规则](https://gaotuedu.feishu.cn/wiki/LNgKwBWKoimlk6kRX46chMILnec) revision3368，全文 `em-small-guide.json/.xml`。按白名单/同科目→同主讲→同时间等既有规则理解，本需求不重做旧功能。
- [大班既有规则](https://docs.baijia.com/doc/DQWJDTm1wdGlNbUx4UWFhZ1Bw)：经代理GET仍302到OAuth，未获正文；访问限制见 `em-large-guide.headers`（已去Cookie）。未继续追登录。
- 两PRD没有文件附件或嵌入sheet/base；当前14个图片token与旧副本一致，**4张企微+10张纯续原图本轮均实际打开查看**，复用 `/tmp/w1-e0be7208/docs/*.png`、`em-materials/*.png`。原型仍有“上限5/已结束可选”等旧示意，验收取最新正文10/状态1、2，不照图覆盖正文。引用规范中全部手机操作图片未逐张复验。

## 2. 完整需求编号表

| 编号 | 当前需求/有效口径 | 当前对照与验收归属 |
|---|---|---|
| Q1 | 大/小班续班服务复制默认花名册批量添加标签 | **实际需求分支已接入**（含大班Legacy）；master未合入，详见§7 |
| Q2 | 大/小班续班服务复制批量修改企微备注，行为完全一致 | **实际需求分支已接入**；任务受理不等于备注全部完成 |
| Q3 | 学员标签显示批量值、支持单人编辑 | **实际需求分支已接StudentTags/TagsModal和刷新**；仍需真实字段配置/页面验证 |
| Q4 | 学员标签可筛选 | **实际需求分支三条路径均转studentTags，本轮原函数执行通过**；旧master原键证据仅为基线 |
| Q5 | 历史回溯阈值2026-01-01（含当天） | **最终owner覆盖PRD“创建时间”：班级开始时间=min(课节begin_time)**；圈班后更新学员，不额外按模式过滤；studentTags需补、不补clazzRoomType；本轮不改线上/不跑全量。覆盖结果由主Worker整合 |
| Q6 | 私聊/群聊官方群发所有页面统一换规范链接，含默认花名册、课节管理学员默认、我的线索 | iris生产chunk仍旧“每月30条”；见§4 |
| Q7 | EES联系学员等弹窗统一换规范链接 | 实际需求分支升至 **0.1.5-beta.4**；本次未读新包内部，不能沿用0.1.3无链接结论；与iris两条链独立 |
| Q8 | 阶段反馈、退费管控增加按钮 | **明确取消、本期不做**；不影响Q6共享组件统一覆盖要求 |
| Q9 | 运营规范项 | 禁止/暂停微信助手；续班前尽量少用官方额度；主体周7条或按月天数限额；官方群发需企微确认发送；备注/标签不依赖微信助手。属引用说明内容，不新增本期产品限流/发送规则 |
| E1 | A主关联BCD，A覆盖学员在ABCD在读前置班对应纯续；BCD不反向扩大 | owner最终口径：**从计划只并前置课，推荐规则/白名单等按主计划**；主Worker验证引擎 |
| E2 | 大/小班既有推荐规则不变，不按相同科目互斥 | 测试同科不同商品均在；不把旧小班PRD取消功能重加进来 |
| E3 | 同商品不重复展示 | owner补充同年级同商品去重，不跨年级误删；推荐页验证归主Worker |
| E4 | 扩科不变，各计划只推自己扩科 | 应比较同一学员/配置前后完整扩科集合；不能并入从计划扩科或让从计划年级改变主扩科 |
| E5 | 入口仅待开始/进行中可操作，其他置灰；仅计划管理员，其他提示“仅续班计划管理员可操作” | 当前PureRenewRelation:163-164、父列表:250/322已接。白名单是后端运维例外，UI未因此自动授权 |
| E6 | 当前计划显示状态/名称/ID/管理员 | :72-88已实现；ID统一字符串防18位精度损失 |
| E7 | 名称单项模糊、ID批量精确；状态默认1/2、可选范围1/2；过滤测试数据默认是 | :217-224、325-355；前端number原串传递，后端现已支持拆分，旧“必须改numberList”建议作废 |
| E8 | 搜索结果状态/名称/ID/管理员，按计划创建时间倒序 | :59-68管理员已修；后端搜索排序由主Worker验证 |
| E9 | 多选最多10（可配置），错误提示“最多可纯续关联X个续班计划” | :227-265无选择阶段限制，最终保存依后端拦截；仍为交互差异 |
| E10 | 同主不可重复绑定、已有绑定回显 | selectedRowKeys使用原ID；当前后端number字符串已对齐，实际HTTP由主Worker证明；页面跨页勾选未验 |
| E11 | 已选状态/名称/ID/管理员，创建时间倒序 | 已选悬浮详情已接adminList/adminName；后端已保存列表ORDER BY已补；**新增选择仍按点击顺序追加** |
| E12 | 点击移除二次确认；最终确认全量保存、取消不落库 | 当前移除立即改本地集合；所有最终保存均弹确认列最终计划名（空集合明示清空），并非点击移除当场确认。取消不调用save |
| E13 | 仅操作弹窗展示关联结果；未绑定空、有绑定回显 | :170-188、301-316已实现；加载失败禁止保存 |
| E14 | 四类入口：大小班批量/单项推荐链接、大小班下单推荐、大班通用推荐、大小班C端纯续 | 该前端diff只管理入口，不可据此声称所有推荐展示页已验；§5提供页面覆盖步骤 |
| E15 | 不同主体不能一起下单，只看主体；优惠无影响 | 保留校验；order具体修复/验证由主Worker处理 |
| E16 | B8缓存延迟 | owner明确**不修，接受既有最长约26h缓存延迟**；不是即时刷新验收条件，不能擅自清缓存后声称自然生效 |

## 3. 已修与仍缺：当前证据位置

路径缩写 F=`/tmp/w1-13ca5996/frontend-readonly/src/pages/continuationClasses/components/PureRenewRelation/index.js`；C=`/tmp/w1-e0be7208/cronus-remote-master`。

**已修/旧结论撤回**：
1. F:31-32、63-67 已用 `adminName(item)` 渲染搜索管理员；本轮提取原函数输入adminList两人，输出“甲，乙”。关联展示F:86/115也兼容camelCase adminList/adminName。
2. F:331-334已去单数字校验，:223保留批量number字符串。后端 `product-server-client/.../RenewalMasterListRequest.java:18` 为String，`product-server-infrastructure/.../RenewalMasterListQueryBO.java:71-74,124-141`拆列表。本地执行确认18位字符串原样传递。主Worker真实HTTP `plan-batch.json` 返回2条，`plan-invalid.json`返回0条，旧F1不可继续报未修。
3. 后端 `RenewalMasterRelationVO.java` 明确String number、`@JSONField(name="adminList"/"adminName")`；主Worker `relation-list.json`已确认真实JSON。上轮admin_list缺陷不可继续报当前未修。
4. 后端 `RenewMasterRelationBizMapper.xml:52-60` 已 `order by m.create_time desc`，旧B4“后端无排序”作废；F新选择排序是独立问题。
5. 新筛选默认及全量保存确认见上述diff。不得把“有确认”误报“无保护直接删库”。

**仍有前端差异（均源码确认，非浏览器复现；下列C基线两条由§7实际需求分支结果取代，不列当前开发缺口）**：
- F:227-231、314：勾选追加 `[...prev,row]`、原序展示；先旧后新或跨页选会违背已选创建倒序。后端list修复只保证重新打开已有集合，不能覆盖未保存选择。
- F:227-265：可勾第11个，未读动态max；最终后端拦不等于选择阶段限制。建议前端显示/消费真实上限，避免硬编码。
- F:129-135、231、242-256：移除时不确认，最终保存统一确认。是否接受需owner决定；PRD仍要求移除当场确认。
- F:260-265：自己仍可勾，后端保存校验；属体验补强建议，不再沿用“后端静默清空”旧结论。
- C `src/pages/roster/ContinuationService/config.js:250`、`hooks/useExtendComponents.js:14` 与 `src/pages/microClazzRoster/ContinuationService/config.js:241`、`hooks/useExtendComponents.js:8`：未注册SettingTags/ModifyWechatNote及StudentTags编辑。默认小班参照 `DefaultRoster/config.js:261,280`。
- C 两续班config :553-593 / :477-509：未将studentTagNames转studentTags；本轮Node执行均输出原键，标准默认页 :478有转换。**字段发送错误已证；具体页面空结果/人数未验**。
- 旧报告的test字段配置/GAIA/ES配置不能视为本次现查，不重复后端工作；本轮未查生产配置或回溯覆盖。

## 4. 线上版本能证明到哪里

2026-11-05重新GET [iris生产remoteEntry](https://fuwu.baijia.com/micro-iris/moduleFederation/iris_remoteEntry.js)，内容与上轮完全一致，仍指向 [WechatBatchSending chunk](https://gaotu-fuwu.gsxcdn.com/prod/iris/iris.release.prod.WechatBatchSending.ca2897a415468128bd26.js)。重新下载chunk SHA256=`3c609eafdb78e46f8353afb5df14b34c5566da41e562fda6642f958250ea471c`，Unicode解码后仍有“每个学员/每个群聊…每月30条…”，两份文档token及“使用说明”均无命中。副本 `iris-prod-entry.js`、`iris-prod-wechat.js`。**证明当前生产静态资源仍旧文案，不证明所有页面实际加载此资源，也未取得Git构建SHA或浏览器截图**。

cronus `config/config.js:100` 指向该生产iris；`components/WechatBatchSending/index.js:21`使用模块联邦；联系学员则 `components/ReachBusiness/index.jsx:5`走 `@gaotu/reach-widget`。package.json:38、pnpm-lock.yaml:1498仍锁0.1.3，复用已验tarball，`/tmp/w1-e0be7208/reach-widget-readonly/package/es/common/reach-type/index.js:75`渲染方式/类型区域无说明链接。仅能确认**master锁定旧依赖**缺失；实际需求分支已改0.1.5-beta.4，新包内部未验，不能继续认定Q7未实现；当前线上cronus的实际包版本未映射。

**未获得 promotions、cronus 当前线上 SHA；用户指定分支≠线上版本，master≠已发布。**

## 5. 页面P0卡（交主Worker整合；全部未执行页面）

使用 banshan-case 的现场执行卡结构，仅提供本子任务覆盖的页面部分。环境候选为历史 `TEST / test-gtbg-dev-3`，最终部署/前端资源地址须由主Worker以本轮证据填入；本报告不虚构登录名、商品名或有效订单。真实登录态已验证为张泽灵（飞书身份），**不能据此认定其OES管理员/EES二讲权限**。历史业务账号accountId=125756仅线索，尚无本轮可输入登录名/角色映射。历史计划/学员候选见下，必须由主Worker复用本轮数据表后回填卡片；当前不能宣称拿本节即可直接现场执行。

可定位入口：OES→续班管理→续班计划管理（`src/pages/continuationClasses/list/index.js`）；EES→学员→班级花名册→续班服务，大班路由 `/clazzRosterOL`，小班 `/microClazzRoster`（C `config/routes.js:48,154`，tabKey continuationService）。完整TEST入口域名/微前端挂载由主Worker提供，不能把相对路由拼成未经验证URL。

历史候选（非本轮有效性证明）：A大班计划`585960797778243584`、B小班计划`586116340522184704`，学员`7658127801`（姓名未确认，按ID定位），前置大班课`585960577856301056`、小班课`18314034380997173`；大班后置班`585960755422160896`“dcg-扩科排除-后置-六年级语文”、小班后置`586090628920764416`（名称需回填）。不要用PRD截图中的唐超01/真真正正当测试账号与样本。

### P0-F01 关联管理保存与取消（E5-E13）
**现场过 case：照着做**
- 登录谁/前置：主Worker确认的A管理员和一名非管理员；A/B有效状态1或2，记录原关联全集；另备未发布/已结束计划。登录名/计划名称待主Worker本轮样本回填。
- 从哪里进：OES→续班管理→续班计划管理，按A的18位ID精确查询；测试数据样本将“过滤测试数据”改否。
1. 非管理员查看A，再用管理员查看非可操作状态计划。应分别禁用并提示管理员限制、禁用其他状态；管理员对1/2状态可打开。
2. 打开A纯续关联，核当前卡和已关联项状态/名称/完整ID/管理员；搜索默认状态仅待开始+进行中、过滤测试数据=是。
3. 输入A、B两ID（英文逗号，另测中文逗号/空白）并查询，应仅返回精确匹配项；非法ID应空结果，不回全量；名称片段可模糊匹配。测试样本需先把过滤测试数据改否。
4. 搜索已有B，确认选中态，跨页再回不重复；选择允许的从计划，点确定，核最终集合确认框；取消确认/关闭抽屉再开，应仍是原集合。
5. 再修改并最终确认，重新打开应是目标全集且字符串ID不变、管理员有值；空集保存确认应明确最终不绑定；保存后若读旧值需记录时间和响应，不能擅自归因B8（B端关联list与C端推荐缓存不同）。
**通过判据**：权限、批量精确搜索、最终集合/取消、回显均符合；已选倒序/移除当场确认/第11项限制按需求记录偏差，不能因主路径通过抹掉。
**恢复**：用A管理员恢复原关联全集并回读。**本次实际**：仅原函数和契约核对；真实HTTP见主Worker3份JSON，页面未跑。

### P0-F02 主从跨模式推荐及扩科保留（E1-E4/E14/E16）
**现场过 case：照着做**
- 登录谁/前置：主Worker确认的EES二讲和学员本人TEST登录；A/B主从关系，学员有两侧有效在读前置订单、可售后置、主计划节点生效。样本候选见上，需补真实账号、计划名、当前商品集合及订单状态；规则全部按A。
- 从哪里进：大小班续班服务；筛选对应前置班，取消阻碍定位的“仅本人”筛选须由有权限账号执行，按学员ID定位。
1. A侧分别打开单项发链接→推荐链接、勾选学员后批量发链接→推荐链接；只预览/复制，不点击真实发送。应含A+B有效前置对应纯续，同科不同商品均在、同年级同商品只一份。
2. A侧点下单→推荐页，比较同一学员同一配置下商品ID集合；大班另点通用链接→推荐链接。打开生成的TEST C端链接，以同一学员登录，逐年级检查同集合。
3. B侧同类入口比较，应只有B自身纯续；扩科A仅A、B仅B，关联前后完整扩科集合不变（包含从计划年级配置反例）。
4. 更换A/B角色后再测小班主、大班从；不得把从计划白名单/节点规则并入。
**通过判据**：四类入口逐项有页面证据，主从单向、跨模式、同科、去重、扩科均符合。已有缓存样本允许owner确认的26h延迟；记录缓存前提/观察时间，不以刚改关系即时不变报B8，也不能通过清缓存代替自然行为。
**恢复**：恢复原关联/页面选择；购物车副作用由主Worker测试卡统一恢复。**本次实际**：未打开这些页面，代码diff不覆盖C端，推荐/下单后端测试归主Worker。

### P0-F03 大小班标签批量、单人编辑与筛选（Q1/Q3/Q4）
**现场过 case：照着做**
- 登录谁/前置：主Worker确认可管理两模式班级的EES二讲；每模式两名可见学员、一个已存在业务标签，原标签/备注快照；具体账号、班名/班号、学员名/ID、标签名/ID须本轮补齐，当前缺。
- 从哪里进：EES→学员→大班或小班花名册→续班服务，按前置班和学员ID定位，并在列设置显示“学员标签”。
1. 同模式选两人→添加标签→选该业务标签→确认；完成后刷新，两个目标人显示新增标签，未选人不受影响。
2. 点其中一人学员标签编辑，只修改此人；刷新保持，另一人标签保持原结果。
3. 按该标签筛选，核目标学员集合；取消筛选恢复。大小班各执行一次，和默认花名册结果对照。
**通过判据**：入口、保存后显示、单人作用域、筛选集合全部正确；业务标签/临时企微标签按默认花名册现行语义区分。
**恢复**：按原值恢复本轮改动的业务标签并回读。**本次实际**：无业务写；实际需求分支已接入口且三路径函数验证均转studentTags；原master缺口不再代表当前需求分支，页面未跑。

### P0-F04 批量企微备注异步结果（Q2）
**现场过 case：照着做**
- 登录谁/前置：同F03二讲，拥有可用官方企微关系的TEST学员，两模式各一组；补齐账号、好友关系和原备注，不能借生产学员试发。
- 从哪里进：对应续班服务勾选学员→修改企微备注。
1. 按默认花名册既有模板规则输入可识别测试备注，预览/确认仅目标学员。
2. 提交后应提示处理中；到消息/任务结果确认各学员成功或明确失败原因，再刷新备注/官方结果。受理成功不能判全部成功。
3. 大小班分别验证；缺好友/失败学员应按既有规则明确提示，不显示伪成功。
**通过判据**：目标正确、模板正确、任务完成结果和可见备注一致。**恢复**：恢复原备注并确认任务完成。**本次实际**：未提交任务；所需好友样本未核，页面待测。

### P0-F05 统一规范链接（Q6/Q7/Q9）
**现场过 case：照着做**
- 登录谁/前置：主Worker确认有EES/CRM页面访问权限的二讲/顾问；可打开抽屉的TEST样本（具体身份和对象待补），不需要实际发送。
- 从哪里进：默认花名册、课节管理→学员→默认、CRM我的线索的企微群发；EES续班服务的联系学员。
1. 逐入口打开私聊/群聊群发，旧统一“每月30条”提示应被规范链接替换；点击后到正确二讲/顾问文档且可读。
2. EES联系学员→企微官方→私聊/群聊，类型旁也应有规范链接，不能只修iris后漏reach-widget。
3. 关闭弹窗，不发送消息。两个身份都核对目标文档，正文按主体周/月额度，不新增产品限流规则。
**通过判据**：列出的共享入口及两组件链全部有链接并可访问。**恢复**：无数据变更。**本次实际**：生产静态chunk确认仍旧文案；未逐页面渲染验证。

### P0-F06 历史标签展示与日期边界（Q5）
**现场过 case：照着做**
- 登录谁/前置：同F03二讲；主Worker/数据owner提供两模式历史学员及按 `min(begin_time)` 划分的2025-12-31、2026-01-01、之后班级（实际班名/号、学员名/ID和源标签清单待补）。**不要用创建时间或某个晚课节命中代替班级min时间**。
- 从哪里进：EES大小班续班服务，分别按样本班/学员定位。
1. 对阈值当天及之后样本，对照源标签与列表显示，再按标签筛选应命中。
2. 阈值前班不应被本次圈班范围误包含；原数据已有标签可正常显示，不能把“有标签”当错误更新证据；以回溯批次/圈班清单证明范围。
**通过判据**：目标历史数据源/ES/页面一致，日期边界和大小班覆盖有证据。**恢复**：只读，无恢复动作。**本次实际**：未执行全量回溯，未查真实边界样本，主Worker整合数据侧证据；“实时同步正常”不能替代历史覆盖。

## 6. 实际验证清单与缺口

- 已完成：最新PRD/3份引用全文、14张PRD原图阅读；远端SHA和隔离diff；现有原函数执行（adminList渲染、18位批量请求/状态默认、两模式标签筛选），输出 `frontend-local-verification.json`；重新GET iris生产静态资源并核SHA。
- 已复用主Worker最新HTTP事实（非本子任务执行）：TEST product-b@07ba05df，`relation-list.json`、`plan-batch.json`、`plan-invalid.json`；不重复联调。
- 未做：前端build/依赖安装、新增测试代码、浏览器页面、下单/群发/标签/备注写、DB/GAIA生产查询、回溯；没有把源码或HTTP算成页面通过。仅写独立报告、证据和临时checkout。
- 访问限制：大班旧腾讯规则正文需有效docs登录态；未穷追附件。历史手机号/账号权限/样本有效性缺口已显式列出，需主Worker把自己的本轮造数/登录/部署表填入P0卡，不能交付为“已全部可现场直接跑”。
- 决策项仅前端：①移除当场确认是否接受最终统一确认；②选择阶段上限交互；③确认cronus需求分支真实发布版本、iris链接修订及reach-widget新包链接内容；排序为明确PRD差异。B8不再提修复决策。


## 7. 增量补核：cronus真实需求分支（本节修正master推断）

依据归档changelog已记录的 `feature-wecom-ban-optimization`，只读ls-remote/fetch确认当前SHA **17ee81ccb44b95655f1a55494c4d9372b604cc34**（提交主题“续班服务支持标签和企微备注”）。独立checkout `/tmp/w1-13ca5996/cronus-feature-readonly` 干净。相对master ca703927的工作树diff共27文件+551/-220，代码及依赖差异落盘 `cronus-feature-vs-master.diff`。**下述仅分支源码结论，不代表构建/部署/页面生效；本增量没重查PRD和线上资源。**

以下路径均相对该独立checkout；准确落点：

| 需求 | 当前分支核对 | 文件/行号 |
|---|---|---|
| Q1 批量标签 | **已接入**大小班及大班Legacy；传userId/clazzNumber/subclazzNumber、type=1、scene=identification；widget完成要求刷新 | `src/pages/roster/ContinuationService/config.js:527`、小班`src/pages/microClazzRoster/ContinuationService/config.js:447`、Legacy`src/pages/roster/ContinuationServiceLegacy/config.js:529`；各自`hooks/useExtendComponents.js:30/19/28`注册；共享`src/components/Actions/component/SettingTags/widget.js:26`→`TagsModal.jsx:65`透传scene |
| Q2 批量备注 | **已接入**三路径复用ModifyWechatNote，保留好友校验及原备注任务弹窗；position区分场景 | 大班`config.js:549`、小班`:469`、Legacy`:551`；`src/components/Actions/component/ModifyWechatNote/widget.js:12,70` |
| Q3 标签展示/单人编辑 | **已接入**StudentTags可编辑列、事件、TagsModal、scene和完成刷新 | 大班`custom/fields.js:241`、小班`custom/fields.js:15`、Legacy`custom/fields.js:240`；三者`custom/hooks/useCustomEventDom.js:76,126,186`附近均处理刷新/弹窗，scene明确传递。刷新取值最终仍依赖真实API/GAIA/ES，不标页面通过 |
| Q4 标签筛选 | **已修**studentTagNames→studentTags，三路径原函数实际执行均得到 `{studentTags:[101,102]}` | 大班`config.js:628`、小班`:544`、Legacy`:631`；结果 `cronus-feature-verification.json`。本轮旧master函数证据保留作前后对照，不作当前缺陷 |
| Q6 全局私聊/群聊规范链接 | cronus调用方**没有此项代码变更**；仍动态加载iris，不能仅据cronus判断iris开发是否完成 | `src/components/WechatBatchSending/index.js:21`未改；该分支src中无两文档token/“使用说明”命中。此前已采样生产iris旧文案仍为有效的采样时刻证据；本增量不重查线上 |
| Q7 联系学员规范链接 | **未确认**，旧0.1.3结论撤回为仅master事实：该分支升级到0.1.5-beta.4，可能由新包内置实现 | `package.json:38`、`pnpm-lock.yaml:55,1498`；`src/components/ReachBusiness/index.jsx:5`仍导入该包。未读取新包内部/未跑页面，不把“wrapper无链接”当作新包缺陷 |

另已观察三条页面入口将Dva远端layoutSchema的events/configAbleOperateColumns用本地当前配置覆盖（大班`index.js:69`、Legacy`:69`，小班同类renderSchema），避免切tab复用旧事件；这是已实现代码，不等于已验证切tab行为。

**结论修正**：不要向owner报告“企微标签/备注前端尚未开发”。应报告“实际需求分支已开发Q1–Q4，三路径标签筛选函数通过；真实部署、GAIA/接口字段与页面仍待验证。Q6是iris共享实现/发布核对项；Q7因依赖已升级，需验证0.1.5-beta.4内部或页面，现不能下缺失结论。”AICR#24154仅为历史定位线索，本轮未查询当前评审状态，不追加修复/阻塞结论。
