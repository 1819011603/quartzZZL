# 子项2 EM纯续推荐范围调整：只读问题清单

> **最终状态以§8补查为准**：16:05:40 TEST关联ID已为字符串，旧B1不再列为当前未解决问题；新源码已改自关联报错（旧B6），未发save验证；管理员当前真实字段为`admin_list`，与前端不匹配。下文592e旧基线对照保留证据，不能混作7da8新源码结论。


首轮核查时间：2026-11-04 15:59（Asia/Shanghai）。交付对象：主 W1。状态：只读对照与三个 HTTP 查询已完成；不是功能修复完成。

**续接补充已完成，见 §8：10 张原图已逐张视觉核查；小班引用规则已完整补读；大班腾讯文档被 OAuth 登录重定向阻断并记录证据；16:05:40 唯一一次关联列表回读已经返回字符串 ID，但管理员实际输出 `admin_list`，与前端 `adminName/adminList` 不匹配。下文 §0–§7 保留首轮固定基线和历史观测，涉及“未看图片/数字 ID 响应”的当下状态以 §8 为准。**

## 0. 范围、版本与实际操作

- 遵循最新指令：前后端均不改代码，不部署、不写业务数据、不新增测试、不 commit/push，不生成使用说明、不询问详略、不派生 Agent。**本子任务没有执行上述任何写操作。**
- 本子任务仅建立获准的独立前端 clone `/tmp/w1-e0be7208/em-frontend`，并写本报告；未改归档、共享 Git 引用或共享工作区。
- 后端固定审查基线：`/Users/gaotu/IdeaProjects/JavaProject/product-server`，登记分支 `feature-xuban-pure-relation-20261102`，提交 **`592e96a091a775afc44bbc604a31eb769540a698`**。核查期间 `git ls-remote` 曾确认远端同 SHA。
- 前端真实仓库：`http://git.baijia.com/gaotu-fe/gaotu-btech-fe/gaotu-fe-promotions.git`；用户指定远端分支 `feature-pre-register-coupon-recommend-deduction`；`ls-remote` 与独立 clone 均为 **`bfadc6fde5e165a2d72baecdc9e5cf76ce674fd1`**。只读查询 cronus、gaotu-fe-goodsmanage 同名远端分支未命中。不将此分支当线上版本。
- 共享现场单独记录：首次看到 Controller、VO、Service 三个未提交文件；之后 Service 出现完整 `listSubPlanAdmins` 和自关联报错；再读 HEAD 变为 **`7da8a1432a22b26694d05ef2bb12a8e661ae21f6`** 且工作区干净。**不是本子任务写入或提交，执行者不明，未覆盖/回滚。**以下后端行号均引用固定 `592e96a09`，不得用当前磁盘行号替代；新增提交未作为已部署/已验证修复。
- 运行态证据来自 **TEST，traffic-env=test-gtbg-dev-3，product-b 网关**。未取得该时刻 pod 镜像 SHA，也未取得前后端生产发布 SHA；不能声称测试环境就是固定源码 SHA，不能声称问题已在线上发生。

## 1. 需求材料与成功条件

独立完整读取子项2 PRD：<https://gaotuedu.feishu.cn/wiki/UewqwsMWOiunOgk9Kloce1Jrn52>，底层文档 `WDYOddTNloOrunxiCzmcnNzJnFe`，**revision 659**。读取技术方案 <https://gaotuedu.feishu.cn/docx/AQEtdIeKzo7P5IxeQEzc7EpxnBe>，**revision 72**（共享原文 `/tmp/w1-e0be7208/tech.xml`）。已先读归档 README，再读 links/tasks/changelog/e2e；历史知识参考 `高途信息/知识库/续班科目/续班推荐业务逻辑（纯续-扩科-推荐排除）.md`。

PRD 的本子项成功条件：

1. 主计划 A 关联 B/C/D 后，A 的纯续推荐覆盖学员在 A/B/C/D 的在读班级所对应的全部纯续商品；从计划本身不反向获得 A 的范围。
2. 大小班各自推荐逻辑不变，不做同科目排斥，同商品不重复展示；扩科仍各计划只推荐自己扩科。历史 owner 补充“同年级同商品”去重，应保留。
3. 入口仅待开始(1)/进行中(2)可操作；计划管理员可操作，其他人提示“仅续班计划管理员可操作”。方案另约定 Apollo 管理员白名单。
4. 当前计划、搜索结果、已关联计划展示状态/名称/ID/管理员；搜索名称模糊、ID 批量精确；搜索仅状态 1/2，按计划创建时间倒序；已选也按创建时间倒序。
5. 最多 10 个（上限可配）；相同计划不可重复绑定、已有计划回显绑定状态；移除有二次确认；最终确认全量保存，取消不能落库。
6. 四类入口受益：大小班批量/单项推荐链接、大小班下单推荐页、大班通用推荐链接、大小班 C 端纯续链接。
7. **PRD 备注明确不同主体不能一次下单，只看主体**。不能把旧技术方案中“放行 PAYMENT_SIZE”的文字当成取消收款主体校验的授权；cart/order 由主 W1 审查，本报告不重复深入。

材料边界：PRD 含 10 张图片，XML 已读其 alt 和 token；没有新增文件附件/嵌入表格。技术方案 8 个 Mermaid 画板的源码已随全文读到。**本子任务没有逐张视觉打开原型图**；正文是问题判定依据，图片 alt 不冒充截图验证。PRD 引用的小班历史文档 `LNgKwBWKoimlk6kRX46chMILnec` 可读（底层 `VqR3dSRFooGQBpxl1yrcCPUunKc`，revision 3368），已核到单班/组合推荐、主讲与时间优先级等规则；未将它扩展为本子任务全链路回归。大班腾讯旧文档未展开，历史规则以知识库与主 W1 的推荐引擎核查补足。

## 2. 优先结论

| 编号 | 归属 | 结论/分类 | 优先级 |
|---|---|---|---|
| B1 | 后端契约（前端直接受影响） | 关联列表数字 ID 与搜索字符串 ID 不一致；TEST 实测 + Node 解析证明精度丢失 | 高 |
| F1 | 前端 | 批量 ID 未转 numberList，发送到 Long number；TEST 复现未知错误 | 高 |
| F2 | 前端 | 搜索管理员列读 adminName，后端提供 adminList；契约已证实不匹配 | 中 |
| B2 | 后端/历史口径 | 已关联列表缺管理员；PRD 有要求，但旧归档说 owner 不加字段，需 owner 定最终口径 | 待决定 |
| B3 | 后端 | 状态校验只验证查到的计划，不校验请求计划齐全；可遗漏不存在/已删除计划 | 高，源码确认，未写入复现 |
| B4 | 后端 | 已关联列表没有 ORDER BY，不能保证计划创建时间倒序 | 中，源码确认 |
| B5 | 后端 | 全量保存没有事务/同主计划串行保护；故障部分落库、并发突破上限风险 | 高，源码风险，未故障/并发实测 |
| B6 | 前后端组合 | FE 可选择自己；固定后端基线静默剔除自己，可“成功”但未关联/清空原集合 | 中，源码确认 |
| F3 | 前端 | 新增已选按勾选顺序追加，不保证计划创建时间倒序 | 中，源码确认 |
| F4 | 前端 | 超上限只在后端最终保存拦截，UI 仍可选择 11+ | 体验差异，owner 决定 |
| F5 | 前端 | 点击移除不当场确认，只在最终保存时确认既有关联移除 | PRD 交互时机差异，owner 决定 |

## 3. 后端问题详情（固定 592e96a09）

以下短路径均相对 product-server；Service=`product-server-domain/src/main/java/com/gaotu/product/service/renewal/RenewalMasterRelationService.java`；Mapper XML=`product-server-infrastructure/src/main/java/com/gaotu/product/mapper/manual/RenewMasterRelationBizMapper.xml`；Controller=`product-server-b/src/main/java/com/gaotu/product/controller/process/RenewalMasterRelationController.java`。

### B1. 关联 ID 数字化导致浏览器精度和回显契约错误【已证实】

- 需求预期：已绑定计划正确回显、不可重复绑定，保存原有集合不会换错计划号。
- 实际：Controller:35-45 返回 `RestTraceResponse<List<RenewalMasterRelationVO>>`；VO:14 为 Long number，未做字符串序列化。普通搜索 `/b/renewMaster/list` 使用 RestResponse，返回 number 字符串。`SuperSpringConfig:78-94,103-121` 两种响应走不同转换器：RestResponse 的 Gson 配置 `setLongString()`；RestTraceResponse 默认 FastJSON 配置没有 Long 转字符串。
- TEST GET 关联列表实际返回 `"number":586116340522184704`（无引号），普通搜索返回 `"number":"586116340522184704"`。
- Node 标准 JSON 解析该真实数字后 `String(number)` 为 `586116340522184700`；与搜索行字符串严格比较为 false；再次 JSON.stringify 保存数组得到 `[586116340522184700]`。FE `PureRenewRelation:169-170,200,219-223,232,248` 直接使用 number 且严格比较，无可逆的大数处理。
- 触发：打开已有 18 位计划关联，再搜索/勾选/保存。影响：已有绑定不能可靠选中、可出现同计划双条，保存带错号；结合 B3 可能将有效关联替换成不存在的号（**最后一项是源码推演，没有发 save 实测**）。
- 建议：接口明确将计划 ID 统一输出字符串，保持搜索/关联接口类型一致；不能等 JS 解析后再 `String(number)`。不改：正常编辑已有集合就可能出错。
- 现场增量：外部提交 `7da8a1432` 已将 VO number 改 String，但本子任务未验证它部署、生效或完整契约。

### B2. 已关联计划缺管理员【需求差异已证实；历史口径需决定】

- PRD “已选择的续班计划”明确包含管理员；实际 Controller:38-44 / VO:14-18 仅 number/name/status；TEST 响应同样没有 adminName/adminList。
- FE 已关联标签详情 `PureRenewRelation:28-29,94-107` 能读 adminName 或 adminList，但当前响应两者都无，显示 `--`。
- 历史归档 changelog 2026-11-04 记“owner 澄清 relation/list 不加管理员字段”。这与当前 PRD 正文冲突；本子任务**不自行推翻 owner 决定，也不自动将补字段作为批准修复**。
- 建议 owner 判断：坚持 PRD 展示要求则后端提供一致的 adminList；若保留“不加字段”约定，需明确前端是否另取管理员或接受不展示。不改且无替代：已关联区域永远无法显示管理员。
- 外部并发提交 `7da8a1432` 出现 adminList 补充。另一个待核风险：RestTraceResponse 默认 FastJSON SnakeCase 配置，而新 VO 未显式 camel 命名，真实输出是否为 `admin_list` 需使用该版本 HTTP 验证；**本轮没有把源码字段名当成已生效 JSON 字段名**。

### B3. 请求计划存在性漏验【源码确定，未进行写入复现】

- 预期：只能关联真实且未删除、状态为 1/2 的主从计划。
- Service:197-206 只遍历 SQL 返回项校验状态，未比较请求 numbers 与返回 numbers；Mapper:44-49 `number in (...) and isdel=0` 自动排除不存在/软删行。Service:155-169 仍按原 finalSubs 插入。
- 触发：真实主计划管理员提交不存在/软删的从计划；白名单人员还可能提交不存在的主计划；从集合含 null 也未在入口拒绝（可能 DB 层异常）。
- 影响：无效关联可进入写分支，list 的 INNER JOIN 又会隐藏该关系，而 listSubNumbers 直接读关系表会下发它；B1 错号使这个缺口可被普通 UI 触发。未发保存请求，未证明现库已存在这种脏数据。
- 最小建议：在任何写入前校验主从非空、主从存在且未删除、返回 ID 集合与请求集合一致，再检查状态。保留幂等去重。若不改：状态过滤不能保证引用的计划有效。

### B4. 已关联计划未按创建时间倒序【源码确定】

- PRD 要求已选按计划创建时间倒序；Mapper:52-60 查询无 ORDER BY，Service:131-135 / Controller:38-45 不排序；FE 原序显示。
- 触发：多条关联，计划创建时间顺序与关系行/执行计划顺序不同。影响：排序不符合预期，不能以某次恰好正确的返回顺序认定保证成立。
- 建议在关联列表 SQL 明确 `ORDER BY m.create_time DESC`，可加稳定次序；按计划创建时间，不能误用关联创建时间。不改：多项顺序不稳定。现有样本只有一条，从运行态无法证明逆序错位。

### B5. 全量保存的原子性、并发上限风险【代码结构确定，实际损坏待验证】

- 需求/方案将 save 定义为“最终集合全量差分”；Service:138-184 无事务注解，Controller:52-55 直接调用；写入逐条完成后才删 Redis。
- 故障场景：新增第 1 项成功、第 2 项 DB 报错，则前一项可能已落库，移除步骤和失效步骤不执行，接口虽失败仍可能改了集合。没有进行故障注入。
- 并发场景：两个请求同时读同一 currentSubs，各自 finalSubs <=10，但分别新增不同集合；无同主锁/版本号/串行化，最终可能保留两请求并集超过 10，或返回成功但集合不是任一请求的最终集合。唯一键只能防同一 pair 重复，不能保证集合替换语义。没有并发压测。
- 建议 owner 评估风险后，最小方案为事务内锁住主计划稳定行、核验并执行集合差分；事务提交后失效关联缓存。单独加事务不解决并发最终集合问题，单独 synchronized 不解决多 pod。
- 不改：低频并发/中途错误仍可能导致“保存失败已改一半”或上限失效；不能把历史顺序 save 成功当作此项通过。

### B6. 自关联被静默删除【固定基线源码确定】

- 方案明确 main != sub；FE `PureRenewRelation:245-251` 不禁用本计划，注释称由后端校验；Service:146 却 `finalSubs.remove(main)`，随后继续保存成功。
- 触发：搜索选中当前主计划；若提交仅主计划，后端等价于空集合，会走移除既有关联分支。影响：前端“已选择自己”的操作结果与成功响应不一致，可能意外清空集合。
- 建议明确业务错误，并在前端禁选自己；不改：错误操作可被静默当有效全量保存。外部并发提交已出现报错逻辑，但不是本子任务修复，未实测。

## 4. 前端问题详情（固定 bfadc6fde5e165a2d72baecdc9e5cf76ce674fd1）

前端文件 F=`src/pages/continuationClasses/components/PureRenewRelation/index.js`；入口=`src/pages/continuationClasses/list/index.js:257,329`；API=`src/services/continuationClasses.js:231-248`。

### F1. 批量 ID 搜索请求字段错误【源码+TEST响应已证实】

- PRD：计划 ID 批量、精确。F:211-216 只 trim `params.number`，F:317 仍是单文本 name=number；没有拆分成 numberList。
- 后端 `RenewalMasterListRequest:18,23` 的 number=Long，numberList=List<Long>；Mapper 正确支持 numberList，普通列表的创建时间倒序已实现。
- 实测同查询条件：`numberList:["585960797778243584","586116340522184704"]` 返回 code0、total2；`number:"585960797778243584,586116340522184704"` 返回 `{"status":1,"error_info":"未知错误"}`。
- 影响：粘贴多 ID 的需求不可用。建议前端按约定分隔符拆字符串数组、去空去重，用 numberList，清除 number；后端可改善非法输入错误提示，但不应要求 Long 接受多个值。不改：用户仍只能单 ID 查，批量输入报错。

### F2. 搜索管理员列字段错误【契约已证实】

- PRD：搜索结果展示管理员。F:60 `dataIndex:'adminName'`，只将单值交给省略渲染器；FeituData:305-308 没有 adminList→adminName 格式转换。
- 后端查询响应实际提供 `adminList:[{id,name},...]`，无 adminName；同仓普通计划列表:240-244 正是取 adminList 并 join 名称。F 的 adminName helper 仅用于标签/主计划卡，没有用于搜索列。
- 触发：打开搜索结果，实际行有管理员。影响：搜索管理员列缺失，即使后端给 relation/list 补 adminList 也解决不了此列。
- 建议复用列表页对 adminList 的展示；不改：仍缺管理员。未启动 React 页面，不声称有浏览器截图，但输入响应与 dataIndex 确定不匹配。

### F3. 新选择集合按勾选顺序，不按创建时间【源码确定】

- F:219-220 `[...prev,row]`；F:299-300 原序展示；没有排序。后端已选列表也缺排序，见 B4。
- 触发：先选旧计划后选新计划，或跨页选择；即使搜索每页创建时间倒序，点击顺序仍可能相反。
- 建议统一创建时间排序且接口下发必要排序信息；仅修后端已关联列表，保存前的新选择区仍不满足要求。不改：已选区排序与 PRD 不一致。

### F4. 选择上限只在保存时拦截【体验差异，待owner决定】

- PRD 写“最多选择10个（上限可配置）”；F:219-251 没有选择数量限制、max 配置或上限提示，后端 Service:149-150 才拒绝超限并返回配置值文案。
- 触发：勾选第 11 项；可继续选但保存失败。数据上限在单请求时由后端保护，不能说“单次可保存超过10”。
- 建议若需符合选择阶段限制，提供真实 max 给前端并在第 max+1 次选择提示；不能前端硬编码10而后端可配。不改：用户到最后一步才发现超限。

### F5. 移除确认时机与PRD不同【差异确定，是否接受待owner】

- PRD 写“移除，点击二次弹窗确认”；F:121-127、223 立即从本地 selected 移除；F:234-242 仅最终保存检测 initNumbers 中被删除项并统一确认。
- 已有关联不会点击标签就写库；取消抽屉丢弃本地修改。这是有效保护，不应误报为无确认直接删除数据库。
- 建议 owner 决定接受“最终保存统一确认”还是按 PRD 点击移除即确认；新选项移除是否也需确认同样明确。不改：仅交互时机不符，最终已有绑定移除仍受确认保护。

### 其他前端对齐/条件风险

- 状态常量 1/2 与后端一致；入口 F:155 根据 isAdmin+状态禁用；父级 list:257 用 adminList 与 accountId 判断，符合 PRD 计划管理员口径。非管理员有相同提示 tooltip。
- Apollo 白名单不是计划 adminList；若业务希望白名单也从 UI 操作，现有入口仍禁用，属于技术方案与 UI 的条件不一致；若白名单仅运维后台使用则无需改 UI，不能直接定为 PRD bug。
- 加载失败不允许保存：F:175-182、226-227、279；取消仅关闭抽屉、不发 save；全量差分提交字段与后端一致。
- 已有关联选中状态依赖 row key 同值同类型，B1 会使“不可重复绑定/已绑定回显”一起失败；不要把所有故障归因于前端勾选组件。
- 未发现该仓库存在 `productSelect`、`beforeCourseNumber`、`productCourseNumber` 的真实换班请求。此仓主要是 OES 续班计划管理；不能据此推断 C端/续班下单没有换班。换班请求证据仍需对应 C端/下单组件仓库，交主 W1，不扩展抓取其他未指定分支。

## 5. 逐点核对与缓存边界

| 条目 | 固定代码结论 | 本轮验证/边界 |
|---|---|---|
| 主→从单向存储 | selectByMain 只按 main 查，无反向 JOIN | 源码确认；未重复跑推荐 |
| 名称模糊、ID批量精确搜索 | 后端 list 支持；FE numberList 契约漏接 | numberList total2 实测；逗号 number 错误实测 |
| 搜索只状态1/2+倒序 | FE传statusList=[1,2]，普通列表SQL支持且 create_time DESC | 源码；真实样本均状态2 |
| 计划管理员/白名单 | checkAdmin 用登录账号与 renew_master_ext ADMIN，或 Apollo 白名单 | 源码；复用历史非管理员实测，本轮不调用save |
| 主从状态1/2 | 已查到项校验正确，但缺存在性 | 见B3；不把源码当完整状态实测 |
| 上限/重复 | 默认10可配；LinkedHashSet去重；唯一键防pair重复 | 单请求源码正确，FE上限/并发见F4/B5 |
| 全量新增、软删复位、移除 | Service依finalSubs逐条差分 | 历史有顺序验证，本轮不再写数据 |
| 关联list展示 | number/name/status；管理员/类型/排序差异 | B1/B2/B4 |
| 缓存正常读写 | relation:{main}；非空1800s/空哨兵60s；Redis失败回源 | Service:82-116源码；本轮不触发缓存回填读接口 |
| 保存后缓存失效 | 全部DB步骤结束后delete；失败仅warn | Service:178-182；无新保存/Redis写入 |
| 开关 | 默认true；service.listSubNumbers关时直查DB；真正下发由RenewalServiceImpl:763门控 | 管理列表不会因推荐回滚开关隐藏，是配置管理与推荐门控之别 |
| 从计划后续状态变化 | list展示已关联非删除计划，不自动剔已结束；save会对最终保留集再次检查状态 | 是否允许保留过期关联后保存其他修改，PRD未明确，待owner口径 |
| 预热/最终推荐缓存 | 本Service只清product关系key，不清cart结果缓存 | 主W1已调查，避免重复；只能列触发条件，不声称线上发生 |

缓存条件风险（未新增验证）：Redis 删除失败会留下旧值直到TTL；并发 cache-miss 的旧DB结果可能晚于 save-delete 回填。现代码接受读写异常降级，是否要求保存后强一致需 owner 决定；不将这些都包装为已复现线上故障。主 W1 已给出 TEST queryCache=false/preheat=false、PROD queryCache=false/preheat=true，应用这些条件解释风险，不能说缓存污染无条件发生。

## 6. 本轮真实执行证据

均为只读、没有发送 save/add/remove/createOrder：

1. 飞书读取：主 PRD revision659 全文；方案 revision72 全文；历史知识库读取；原型图片仅读取XML alt/token，Mermaid读取源码。
2. Git：`ls-remote` 确认前端精确 SHA；独立单分支浅 clone，工作区 `git status --short` 为空；后端用 `git show 592e96a09:<path>` 定位固定文件/行号。未 fetch/checkout 共享仓库。
3. TEST HTTP（均经本地 Cookie 代理，header `traffic-env:test-gtbg-dev-3`）：
   - `GET https://test-fuwu.baijia.com/bgwApi/product-b/b/renewMaster/relation/list?renewMasterNumber=585960797778243584` → `{"code":0,"data":[{"name":"dcg-小班扩科排除-计划","number":586116340522184704,"status":2}],"msg":"success！"}`。
   - `POST .../b/renewMaster/list` 查询 body `{"numberList":["585960797778243584","586116340522184704"],"statusList":[1,2],"pager":{"current":1,"pageSize":10}}` → code0，total="2"；两个 number 都是字符串，adminList 均存在，均无 adminName。
   - 相同查询改为 `number:"585960797778243584,586116340522184704"`（无numberList）→ `{"status":1,"error_info":"未知错误"}`。请求是查询而非数据修改。
4. Node 内存诊断真实响应数字：`JSON.parse`→`String`/严格比较/`JSON.stringify`，输出 `{"relationNumber":"586116340522184700","searchNumber":"586116340522184704","sameRowKey":false,"roundTrip":"{\"subRenewMasterNumbers\":[586116340522184700]}"}`。未新增测试文件，未发保存请求。

这些响应没有 traceId，不编造；证据来自本轮工具输出且已将关键请求/响应精确写入本报告。**未运行 Maven/前端构建、未新增/执行写接口测试、未开启页面、未并发压测、未验证生产版本。**历史归档的管理员/上限/状态/顺序差分/推荐下单成功证据标为历史复用，不能覆盖本轮尚未验证的不同场景，也不能把旧“未完成下单”沿用为当前阻塞。

## 7. 交主W1整合与owner判断

- 可以直接报告的重点：B1（已有列表编辑大数问题）、F1（批量搜索不可用）、F2（搜索管理员列）、B3（存在性漏验）、B4/F3（排序）、B6（固定基线自关联静默成功）；说明每项是HTTP实测、源码确定还是后果推演。
- 需owner口径：PRD管理员展示与历史“不加字段”的冲突；选择时还是最终保存拦上限；移除确认时机；白名单是否应可从UI操作；已结束从计划保留行为。
- 风险待验证：B5原子性/并发最终集合；Redis失效竞争；外部新提交的HTTP序列化（adminList vs admin_list）及部署状态；推荐/换班/预热影响由主W1统一整合。
- 最小建议仅供判断，没有执行：统一字符串ID与JSON字段契约；FE批量numberList和管理员列；BE存在性校验与创建时间排序；必要时事务+同主锁+提交后失效。不要修全局序列化或泛化重构以顺带解决本需求。
- 子任务完成依据：指定PRD/方案/归档、固定product基线、精确云端FE分支已对照；有真实查询与解析证据；所有未验证边界明示；只有独立报告写入。**当前无阻塞于继续交付问题清单；线上SHA、图片视觉、完整浏览器和写链路均为证据边界，不宣称功能验收通过。**

## 8. 续接补充：材料视觉、三个新提交文件与一次当前回读

本节仅执行主 W1 追加的三项补查。未扩展 cart/order 调查，未重复首轮两个搜索接口查询，未改前后端代码/配置/业务数据，未新增测试代码，未 commit/push/部署。续接起点 product-server HEAD=`7da8a1432a22b26694d05ef2bb12a8e661ae21f6`，`git status --short` 为空；只读 `git show 7da8a1432 -- <三个指定文件>`。新提交不是本子任务产生。

### 8.1 原 PRD 10 张图片全部视觉核查

材料目录：`/tmp/w1-e0be7208/em-materials/`，文件名为以下 token 加 `.png`。首次 `lark-cli docs +media-download --as user` 对10张均返回 HTTP403；按 lark-doc 指引改用 `+media-preview` 后10张全部 `ok:true`、实际 PNG 落盘，并用 view_image 逐张查看。不是仅引用 alt。直接下载失败首图 log_id=`20261104160540E8EBD68DC24BD4B7ADD3`，尾图=`20261104160541A1C35E5E0514B9CE78D9`；预览读取成功，因此无需把403当作最终图片阻塞。

| 图token | 实际视觉内容 | 对结论的影响 |
|---|---|---|
| ZVpCbFb2Po142vx2Hqocibu2n0e | 四步：列表“推荐关联”→主计划/搜索/已选弹窗→搜索结果→回列表 | 是流程示意，搜索结果中有管理员/状态；不能替代正文数量与状态约束 |
| G00sbAJMMozYskxWtBjcaGA4njg | 续班计划列表“推荐关联”按钮；未发布行也画了蓝色按钮 | 与正文只允许待开始/进行中不同，以正文为准，不据图要求开放未发布 |
| SiEHb6MebonCV5xjm09cOWC3nke | 已选两计划的表格和“移除”；右上写“最多可绑定5个续班计划” | **图为5，正文为10且可配**；不得据图改成5。图中已选表仅名称/ID/操作，不取消正文要求的管理员/状态 |
| H0rZbf72oogOZ8xCaBHcsq6unGg | 搜索列为名称/ID/管理员/状态；含“已结束”行，圆形单选样式 | 正文明确仅1/2、多选，不能照图开放已结束或改成单选；管理员搜索列的需求得到图文双证 |
| Z6eQbmz5zoIGIXxQvpzcQlewnkg | 截取未发布 test实验、18位计划ID | 仅局部字段示意，不构成允许未发布操作的证据 |
| VfkIbZsosoK4YMxxuC8c0Va3nPe | EES发推荐链接弹窗；底部批量发链接、单行发链接、通用链接被框出；售卖主体高途/途途课堂 | 直接支持推荐覆盖多个入口；主体选择仍存在 |
| N2W5bLfe1oDWEcxht8zcJpAUnyg | 创建订单页，“推荐”tab、商品类型列、加购区域和支付方式 | B端下单推荐入口证据；此图列表为空，不能据图声称跨模式已展示/下单通过 |
| Ft27blItRogfwMxWHkEc15RmnGc | 复制推荐链接弹窗，售卖主体与优惠活动渠道、可发班级群/朋友圈提示 | 通用/复制推荐入口与主体选项证据 |
| ALG8brAoao64jIxeG89cQc9JnJe | C端活动报名页，年级下拉、课程卡、“更换课程”、去结算 | **真实原型明确有更换课程入口**；与小班引用规则一致，但不是当前前端运行截图，不能提供真实API请求体 |
| XzSlbeiT8oCMCHxo8sKchWemnPa | 范围矩阵：A主时纯续ABC/扩科A、B纯续B扩科B、C纯续C扩科C；B主时纯续BAC/扩科B，A与C各自身 | 再次确认关联是主入口定向扩纯续，扩科不并；无传递关联示例，不自行补“递归”规则 |

图片中“推荐关联”旧标题与正文“纯续关联”也不一致；当前前端采用正文标题不是缺陷。上述图片均为PRD原型/截图，不是用户指定需求分支的线上运行证据。

### 8.2 引用的大/小班规则补查

**大班腾讯原文访问阻塞（具体证据）**：2026-11-04 16:05 左右，经现有 Cookie 代理 GET `https://docs.baijia.com/doc/DQWJDTm1wdGlNbUx4UWFhZ1Bw`，响应正文为 `Redirecting to <a href="/eid/gw/oauth2/v1/authorize?...">`，其中 redirect_uri 指向 `https://docs.baijia.com/eid-auth-callback/`，success_jump_url 回到同一文档。未拿到标题/正文。按 baijia-proxy 的登录重定向规则没有绕过认证或重复重试；后续读取缺口是 docs.baijia.com 的可用登录态。**不能声称已完整读大班旧规则**；本次已完成获准的尝试及证据记录，不因此扩大调查。

**小班历史PRD补读完成**：原链接 `https://gaotuedu.feishu.cn/wiki/LNgKwBWKoimlk6kRX46chMILnec`，底层文档 `VqR3dSRFooGQBpxl1yrcCPUunKc`，本次仍 revision3368。全文读取后只归纳与“各自推荐逻辑不变”相关规则，未继续追踪其无关引用：

1. 用户需有计划前置班级已支付订单；含部分退款，不含全退/调课调班退款，不含赠课订单。文档将“前置班级过滤赠课/模拟课堂”标记取消，改按订单判断；不能沿用已取消过滤。一个在读班级推荐一个后置单班或组合，多科形成合集。
2. 单班推荐的后置范围需满足续班关系、小班课、售卖中，去掉赠课标签和模拟课堂；白名单优先。未配置白名单时按同科目→同主讲→同星期和开始时间，命中唯一即取；某一步无候选则跳过该条件；最终并列取最早正式课开始。主讲ID匹配不到时使用绑定关系的运营主讲名称。
3. 组合推荐仍先使用白名单（组合需含小班课，否则走普通推荐）；再在该计划上传的组合范围中选择，过滤无小班课的组合；按子班同科目/同主讲/同时间匹配优先级，并列取全部小班课中开课时间最早的组合。组合子班不校验售卖状态，仍有赠课/模拟课堂过滤口径。**单班/组合配置和白名单是推荐规则的一部分，不只是courseNumbers范围**，可供主W1现有“只合前置课、未合从计划配置”问题引用。
4. 配置是计划正式报名流程节点级：商品类型可选小班课/组合；白名单可空；选择组合时组合清单必填。白名单文件前置班级不可重复；单班白名单要求前后置属于续班关系，组合白名单要求前置在关系、组合真实存在；上传限制xlsx/10M/1000行。本文不要求为本次重测这些既有上传规则。
5. EES批量与单项发送均走相同多科推荐；同学员多班合一次链接并预览全部在读班级推荐。发送校验学员、计划绑定、同计划选择、已发布续班流程；售卖主体与优惠渠道仍有选择。该旧规则不等于本次允许递归合并计划。
6. B端推荐和C端纯续链接使用同一推荐逻辑；旧文中“小班课范围调整/快速加购组合商品”已标本期不做，不能把它们引入本次验收。
7. C端开始前可看不可结算，期间可结算，结束后无班级操作；多年级优先最低年级并可切换；默认全选但可取消，保留历史选择；已购买后置商品标已报名、后置展示，全部买完显示已报名成功而不继续推荐新课。
8. **换班是既有能力**：范围为原班同年级同科目、且在续班关系后置范围内的班级/组合；可按主讲、星期、日期、教材版本、班型、难度筛选；选一项替换原推荐。结合本PRD原图ALG8的“更换课程”，主W1可将换班作为本次范围变化的必要影响项，但本子任务仍未获取实际页面请求体。

### 8.3 7da8a1432 的三个文件与旧问题状态

只复核该提交的 Controller、VO、Service diff，不扩展其它业务代码：

| 旧问题 | 新源码变化 | 当前结论 |
|---|---|---|
| B1 ID数字序列化 | VO number由Long改String；Controller用String.valueOf填充 | **新源码已处理**。下方唯一HTTP回读也观察到字符串；不再将“当下仍是数字ID”作为结论，但旧592e基线事实保留 |
| B2 缺管理员 | Service新增listSubPlanAdmins，读从计划ext ADMIN，批量查账号名称；Controller填adminList，VO新增adminList | 数据填充已在新源码出现，但**实际JSON是admin_list**，前端只认adminName/adminList，展示契约仍未闭环；原PRD与历史“不加字段”决策冲突仍应由owner判断 |
| B6 静默剔除自身 | 删除finalSubs.remove(main)，权限通过后若包含main则抛“续班计划不能关联自身”，在状态检查和写入之前 | **新源码已处理静默成功问题**。本轮没有调用save或进行写操作，不宣称运行态校验通过 |

管理员命名判断从“可能风险”升级为**当下HTTP已证实的不匹配**。新VO没有显式 JSONField/JSONType camel 声明；原有 RestTraceResponse 的 FastJSON SnakeCase 解释与现象一致。仅在Java中添加camelCase字段不保证前端拿到camelCase JSON。

### 8.4 唯一一次当下 relation/list 回读

执行时间（请求前系统时间）：**2026-11-04 16:05:40 +0800**。

请求：`GET https://test-fuwu.baijia.com/bgwApi/product-b/b/renewMaster/relation/list?renewMasterNumber=585960797778243584`，header `traffic-env:test-gtbg-dev-3`，经既有Cookie代理；未带任何写动作。

实际完整响应：

```json
{"code":0,"data":[{"admin_list":[{"id":"177071","name":"弓雪萌"},{"id":"90247","name":"唐稳01"}],"name":"dcg-小班扩科排除-计划","number":"586116340522184704","status":2}],"msg":"success！"}
```

与首轮响应相比，ID已变字符串、管理员数据已出现。因此**不是仍旧响应**，但并不能由接口形状反推镜像SHA、部署人、部署时间或所有pod一致。前端固定 `bfadc6fd` 的 helper `item?.adminName || adminNames(item?.adminList)` 未读 `admin_list`，已关联详情仍显示缺管理员；搜索列F2的独立问题也不会被这次后端字段新增解决。

### 8.5 本次补充完成状态和写入范围

- 完成：10/10图片落盘并逐张视觉核查；小班相关完整规则补读；新提交仅三个文件复核；恰好一次关联列表回读；本报告原位补充并回读。
- 有证据的材料阻塞：大班腾讯文档登录重定向；未取得正文。未绕过、未重复请求，不影响本轮其它补查完成。
- 本轮仅新增获准的临时原图文件、更新本报告；**无源码、业务数据、配置写入；无提交、推送、部署、测试新增；没有触发使用说明流程。**
- 主结论整合时：B1/B6对固定旧基线成立，但新源码已经处理；当下测试列表字符串ID已观测；B2应更新为“admin_list实际序列化与前端命名不匹配”，不能再只说没返回管理员。大班规则全文仍是明确缺口，生产/镜像版本继续未确认。
