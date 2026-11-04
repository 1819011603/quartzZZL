# 子项1：企微封禁优化——只读需求对照与问题清单

> **主W1补充**：FE-4的锁定依赖包内部实现已补读，0.1.3 tarball与lock完整性一致，该版本发送方式区没有使用说明链接；见末节。生产cronus包版本/构建映射仍未确认。


核查时间：2026-11-04。子任务 W1-3558a8。状态：**本轮只读调查和报告已完成；功能没有被宣称修复或验收完成**。

## 1. 范围与写入审计

按最新所有者要求，仅调查、读取现有源码/配置/静态产物与运行无业务副作用的验证。没有修改前后端代码、没有新增测试代码、没有部署、没有写业务数据、没有执行标签/备注/群发/重放/回溯、没有 commit/push，没有修改共享仓库引用或归档，没有派生 Agent。

本 Agent 实际写入只有 `/tmp/w1-e0be7208/`：本报告、飞书/查询响应及图片取证副本、独立 cronus 只读 clone。既有现场未回滚或覆盖。一次带 `rm -rf` 的准备命令被工具拒绝，**整条未执行**；改用不存在的新临时目录后成功，不发生删除。独立 iris clone 经代理返回 repository not found，未取得远端 checkout；后续改从生产公开静态入口取证，没有改权限或绕过业务登录。

## 2. 真相源、真实版本和成功条件

### 文档

- PRD：https://gaotuedu.feishu.cn/wiki/ZiRZwGOJGi3CtnksQg1cJwZsn9b ，底层 `W4ftd48kFoq1LyxMrVYc1AhynFe`，**revision 253**。复用主 W1 已成功取回的 `/tmp/w1-e0be7208/qiwei-prd.json`，未重复抓取。
- 技术方案：https://gaotuedu.feishu.cn/docx/AQEtdIeKzo7P5IxeQEzc7EpxnBe ，**revision 72**；完整副本 `docs/technical.json` / `docs/technical.md`，精读子项1、字段、回溯、验证和后续修正有关内容。
- 二讲引用：https://gaotuedu.feishu.cn/wiki/Af3VwjizwiKxDhkUFtEcvpZpn4P ，底层 `PNmhdMV9xofb1xxLL3qcZBOQnsb`，**revision 562**。
- 顾问引用：https://gaotuedu.feishu.cn/docx/Ar7YdcPqsowMITxRBNacwjkpn3d ，**revision 465**。
- 两份引用全文已读；官方企微入口不依赖微信助手、群发任务创建后需要在企微确认发送、不同主体有每周7条/按月天数等差异，说明把静态限额文案改为使用规范链接有实质意义。链接显示方式（按身份选一份还是并列）PRD未进一步定义，不自行扩成业务规则。
- PRD 4 张图已实际下载并查看：`SaM0...YnSg` 默认页按钮、`Gw0x...mnPb` 续班页新增按钮、`J8dL...TnS2` 私聊群发顶栏文案替换、`YHSr...enac` 联系学员企微官方私聊/群聊类型旁的链接。两份引用中与标签/备注复用直接相关的图片 `Juz7...DnKb` / `KO4l...0nUb` 也已查看（内容相同）；引用文档中其它企微手机操作图仅阅读其图注，未逐张下载。无表格/多维表格或需下钻的附件。

### 版本边界

| 对象 | 实际证据 | 可支持结论 / 不可支持结论 |
|---|---|---|
| 用户指定前端分支 | `git ls-remote`：`gaotu-fe-promotions` 的 `feature-pre-register-coupon-recommend-deduction` = **bfadc6fde5e165a2d72baecdc9e5cf76ce674fd1** | 真实所属仓库是 OES `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/gaotu-fe-promotions.git`；不属于本子项 EES cronus。子项2由兄弟任务负责，因此没有重复 checkout/审查其实现 |
| cronus 指定分支 | cronus `ls-remote --heads origin <指定分支>` 返回空；普通 heads 查询成功 | cronus 无同名远端分支；不能据指定分支断言子项1前端已做/未做 |
| cronus 可读远端 master | 独立 `/tmp/w1-e0be7208/cronus-remote-master`，**ca7039277d44571f111b0756e7d5662c34453328**，2026-10-27，工作树干净 | 下文 FE-1/2 是该远端源码的确认缺口；尚未映射到 cronus 当前线上发布产物，也未查询其它未指定需求分支，不能称为所有开发分支均缺失 |
| cronus 共享本地 | HEAD f0723b9806a00984dbe3805472c7e88db241ccac；缓存 origin/master 599728cd77b42d518e25449c2c6113ca9cd59311；干净 | 仅版本检查；不以该滞后本地副本代替上述远端源码 |
| student-center | `/Users/gaotu/IdeaProjects/JavaProject/student-center`，**396d84f076d066c652a49ce39e68b9b917c242e0**，`feature-xuban-pure-relation-20261102`，干净 | 已读实现，不代表当前部署 SHA；下文配置组合的运行时影响仍需正确环境的只读列表样本确认 |
| iris 本地 | `/Users/gaotu/IdeaProjects/WebProject/iris`，**e6c1abb5689b4e30775376ebe8e0d02cfff91f40**（release，干净） | 用于源码定位；远端 ls-remote master=086ed85df179ce16675eb81372424e081a325986，release=dcf386181f1bb8128dbf2291418f1c649a80c3c8；没有以本地源码冒充线上版本 |
| iris 生产静态产物 | `https://fuwu.baijia.com/micro-iris/moduleFederation/iris_remoteEntry.js` 当前指向 `https://gaotu-fuwu.gsxcdn.com/prod/iris/iris.release.prod.WechatBatchSending.ca2897a415468128bd26.js` | 生产入口和具体 chunk 已读取；这是 FE-3 的线上产物证据。未获得构建对应 Git SHA，未打开真实业务抽屉渲染 |
| GAIA/字段配置 | 本轮 **test** 只读回读；无生产 GAIA配置查询/写入 | 不把 test 的 number 或完成记录等同 prod |

iris chunk 长度 70,549 bytes，SHA256 `3c609eafdb78e46f8353afb5df14b34c5566da41e562fda6642f958250ea471c`。副本 `docs/iris-prod-entry.js`、`docs/iris-prod-wechat.js`；中文在压缩 JS 中为 Unicode escape，解码后核实旧提示。

### PRD 成功条件逐点对照

| PRD revision 253 要求 | 本轮证据与判断 |
|---|---|
| 大班、小班续班服务均复制默认花名册批量添加标签 | cronus 远端 master 两 tab 均未接入；见 FE-1。student-center 写接口存在 |
| 两模式均复制批量修改企微备注 | 同上 FE-1；后端异步任务/官方备注链存在 |
| 学员标签展示批量添加值，支持单个编辑 | 两 tab 无默认页 StudentTags/TagsModal 专用渲染及事件；test GAIA小班布局已有字段但不能替代前端编辑链；见 FE-1、BE-1 |
| 学员标签可筛选 | 两 tab `formatFilter` 未将 studentTagNames 转为 studentTags；已直接运行现有函数证明输出；见 FE-2、BE-1 |
| **回溯班级创建时间20260101及以后** | 技术方案仍写“通常不需要/缺失补偿”，未看到含此日期范围的完成清单/对账证据；见 BE-2。没有自行执行回溯 |
| 私聊、群聊所有页面统一组件改文档链接 | 找到真实共享组件在 iris，线上 chunk 保留旧固定限额；见 FE-3 |
| 联系学员等弹窗 EES 内统一更新 | 实际依赖 `@gaotu/reach-widget`，不能把 iris 修订视为覆盖此路径；现有版本是否具备链接待核对，见 FE-4 |
| 阶段反馈、退费管控一起加按钮 | PRD删除线且明确“取消，本期不做”；不纳入按钮改造。其共享群发组件仍属于“所有页面统一组件”范围 |

## 3. 前端问题清单

所有 cronus 文件均以独立远端 master ca703927 为准，路径前缀 `/tmp/w1-e0be7208/cronus-remote-master/`。

### FE-1：两续班 tab 未复用批量按钮和标签单项编辑（源码已证实，线上覆盖待确认）

- **预期**：与默认花名册完全一致，大小班都能批量加标签、改备注，标签单个可编辑。
- **实际/位置**：大班 `src/pages/roster/ContinuationService/config.js:250` footer 仅现有发问卷/链接/学币/联系学员/颜色等，`hooks/useExtendComponents.js:14` 未注册 SettingTags/ModifyWechatNote；小班 `src/pages/microClazzRoster/ContinuationService/config.js:241` 和 `hooks/useExtendComponents.js:8` 同样没有。两目录及 Legacy 路径搜索无 `studentTagNames/StudentTags/TagsModal/SettingTags/ModifyWechatNote` 接入（无命中的具体全文检查已做）。
- **参照**：小班默认 `DefaultRoster/config.js:248/268`（组件名分别261/280）、`hooks/useExtendComponents.js:6`；`custom/fields.js:31` 使用 StudentTags 和 `openTagsModal`，`custom/hooks/useCustomEventDom.js:98/163` 接 TagsModal。
- **触发/影响**：用户进入任一续班 tab；功能入口缺失，不能就地完成标签/备注操作。仅配 GAIA字段不等于注册专用编辑事件。
- **建议**：复用默认页的按钮、组件注册、记录参数、标签编辑事件和完成刷新；大班还有 `roster/index.js:19` 灰度 Legacy 回退，需明确实际发布/灰度分支覆盖。
- **不改影响**：仍需切默认花名册操作，PRD入口目标未实现。**本轮没有改变任何前端**。

### FE-2：标签筛选字段名未转换（现有函数执行已证实；页面/ES联测未做）

- **预期**：GAIA列名 studentTagNames 的标签选项最终按 ES ID 字段 `studentTags` 筛选，与默认页一致。
- **实际**：大班 config `formatForRequestHandle:553` / `formatFilter:588`、小班 `:477/:504` 均未配置转换；未知 key 原样保留。参照默认页 `DefaultRoster/config.js:478` 显式返回 `{studentTags: origin}`。
- **验证**：用 Node vm 只读提取并执行源文件原函数（不生成测试文件、不写业务状态）：输入 `{studentTagNames:[101,102]}`，两函数均返回 **`{"studentTagNames":[101,102]}`**。
- **触发**：GAIA已加学员标签字段后选择标签筛选；小班 test 的真实布局使用此字段名和标签 ID选项，`docs/gaia-small-scene-detail.json` 可回读。
- **影响**：发送的字段名不符合既有 `studentTags` 基础筛选链；结合 test 配置，可能走 StudentFieldFilterService 对 `studentTagNames` 本身 terms 查询，而真实标签在 `studentTags`，导致漏筛/空结果。**错误字段发送已证明，具体返回人数未跑 HTTP，不把推断写成已复现空结果**。
- **建议**：两 tab 补与默认页相同转换，同时验证 BE-1 的大班必取/筛选配置。避免只加筛选框。
- **不改影响**：标签筛选外观存在但语义不可靠。

### FE-3：统一私聊/群聊仍显示旧限额文案，未换两份使用规范链接（生产静态产物已证实）

- **预期**：PRD第2项+第三张图，旧文案移除、提供二讲/顾问规范链接；默认花名册、课节学员、我的线索等共享组件统一。
- **实际链路**：cronus `components/Actions/component/BatchSending/index.js:45/64` 选择 privateSend/groupSend → `components/WechatBatchSending/index.js:21` 模块联邦 `mf_iris ./WechatBatchSending`；`config/config.js:94/120` 生产 host `https://fuwu.baijia.com/micro-iris`。真实实现仓库为 **iris**，不是只在 cronus 改调用方。
- **生产证据**：上述当前 remoteEntry 指向具体 chunk；chunk 解码仍含“每个学员/每个群聊 可接收的企微群发上限是每月30条（各端发送总和），超过限制将无法接收，请注意发送次数”，且该 chunk无 `使用说明`、`Af3Vwj...`、`Ar7Ydc...`。旧提示位于同一个私聊/群聊共享顶栏渲染；本地定位 `iris/src/exports/WechatBatchSending/index.js:989-1000` 与产物对应。
- **触发/影响**：使用此生产 remoteEntry 的任一页面打开私聊或群聊群发；仍给统一“每月30条”提示，与引用文档按企微主体区分规则不一致，无法从此处直达最新规范。
- **建议**：在 iris 共享组件做链接替换并核对二讲/顾问上下文选择；验所有依赖页面，不逐页复制旧文案。
- **不改影响**：同一错误提示继续覆盖多个入口。未验证浏览器真实渲染，也未从 chunk反推Git SHA。

### FE-4：联系学员是另一共享组件，更新覆盖未获证据（待验证，不冒充已证实缺陷）

- **实际**：大班 `config.js:492`、小班 `:395` module ReachBusiness，anchorCode分别 `renewal` / `small_clazz_renewal`，reachSceneCode=`renewal_contact_student`；各 wrapper → `components/ReachBusiness/index.jsx:5` 动态导入 `@gaotu/reach-widget/es/components/reach-business`。cronus package.json:38声明 `^0.1.3`，lock锁 `0.1.3`。
- **缺口**：目前只核到调用链，未取得该包当前生产产物/源码的文案实现，不能确认链接存在或缺失。cronus wrapper本身未传两份文档URL，但包内可自带，故“wrapper没链接”不等于缺陷。
- **建议/影响**：所有者安排该公共包核对统一入口。只修 iris 不足以证明联系学员覆盖，若此包仍保留旧文案，则EES联系弹窗仍不符合PRD。

## 4. 后端与配置问题清单

### BE-1：test 大班标签数据读取/筛选配置与现有标准链不完整（配置事实已证实，影响为强静态推断）

- **预期**：显示、编辑、筛选都围绕实际存储字段 `studentTags`；名称 `studentTagNames` 查询期派生。默认花名册行为完全一致。
- **本轮现查**：`ees_data.student_field_config` 两 identification 已有 `studentTagNames`(193322071548238848,type8)、`wechatRemark`(238628096341720064,type1)；不存在“当前两套都缺字段配置”。两套 tag行 `filter/advanced_filter/sorter=1`。响应 `docs/field-config-test.json`、`docs/tag-config-flags-test.json`。
- **另表关键差异**：test `ees_data.es_query_config` 中：
  - `microContinuationService`、`smallClazzRoster` 均有 `(studentTags,type2,basic)`、`(studentTagNames,type6,extra)`、`(studentTags,type6,necessary)`；
  - **continuationService 对 studentTags/studentTagNames 以及二者作为command的活跃记录均0条**。
  - 原始SQL/回包在 `docs/es-query-config-test.json`。这是已确认配置差异，未擅自修改。
- **源码依据（student-center 396d84f）**：`domain/service/es/GaiaEsMappingService.java:46` 合并GAIA显示字段和necessary，`:99` 从ES取字段并排除student_field_config字段；`domain/service/roster/RenewalService.java:1169` 将此结果传 fetchSource，`:1322` 查额外字段；`sync/data/FieldsConvertDataQueryServiceImpl.java:75` 只有输入map已有studentTags才派生studentTagNames；`es/filter/common/BasicFilterService.java:73` 依赖type2 basic；`StudentFieldFilterService.java:38/45/60` 根据student_field_config直接筛选同名ES字段。`StudentFieldDataQueryServiceV2.java:54-85` 走学情动态字段查询，并非“给studentTagNames配置一行就自动读取studentTags”。
- **触发/影响推断**：大班GAIA仅显示studentTagNames、没有其它路径把studentTags并入 fetchSource时，即使ES已有标签也可能无法派生名称；按修正后的studentTags提交仍缺大班basic配置。当前FE-2原样提交studentTagNames又可能命中错误字段。未做部署SHA对齐和实际列表请求，因此不宣称运行时已复现。
- **建议最小方向**：对齐标准小班/默认页的 ES原字段necessary、派生extra和basic筛选配置；复核此前把派生字段加入 student_field_config 是否把它错误地当作学情自定义字段。以已有带标签学员只读请求（展示/筛选）验证，再由所有者决定配置调整；不建议先写新后端接口。
- **不改影响**：配置回读“有学员标签”仍不能证明显示/筛选生效；容易把UI上线误报为闭环。

### BE-2：PRD指定历史回溯范围没有完成证据（已证实方案遗漏；具体缺失数据待验证）

- **预期**：PRD明确“回溯数据：班级创建时间20260101及以后”，是本子项验收条件，不是按技术方案自行降为可选。
- **实际材料**：技术方案 revision72 `technical.md:310-321` 写“通常不需要”，只说缺studentTags文档、没有创建时间2026-01-01下界；`:318` 又说明quickBack不含studentTags、需重放标记消息。归档没有此范围的源表/ES总量差异、回溯批次或完成对账。
- **已知链路**：标签新变更有实时路径，**实时存在不证明历史补齐**。源码/旧归档确认大班续班索引`ads_large_subclazz_user_index`、小班`ads_small_clazz_user`，派生名称在student-center。student-data本轮只被少量只读定位，未做其业务修改；主W1掌握共享现场版本，不把其既有改动算本子任务产物。
- **建议**：先只读核实创建时间边界（包含2026-01-01）、目标班级和标签源/ES差异，明确空标签与缺字段口径，再由所有者决定是否执行有范围的补偿；无差异也要留覆盖证据。不能仅以“官方接口正常”或“实时消费者已有”替代回溯验收。
- **不改影响**：2026年新建的存量班级可能仍显示空/旧标签，或无法证明PRD数据目标已满足。**本轮未执行任何回溯，未证明实际漏数规模**。

### BE-3：直接复用批量标签组件不带scene，立即刷新可能仅依赖异步同步（既有行为/集成风险，非新代码bug）

- cronus `components/Actions/component/SettingTags/TagsModal.jsx:56` POST只带 `clazzStudents/studentTags/type/userIds`，不带scene；`src/app.js:28` 请求拦截仅拼ApiRoot，不补scene。单项TagsModal则在 `pages/clazzRosterOnLine/components/StudentTags/TagsModal.js:58` 明确带scene。
- student-center `UserClazzMarkBiz.java:200` 使用request.scene走直写；`:309-315` 大小班续班均已有直写分支，scene为空不命中。业务标签数据库仍会保存（`:195`），异步CDC/MQ仍可能同步，所以不能把它说成“标签丢失”。
- 建议复用时透传两场景scene并验证完成后的可见延迟；属于需求“批量添加后展示值”的集成检查项。是否需调整由所有者判断，未做写接口验证。

### 配置已完成部分与避免误报

- test字段配置当前已有且备注number已改成活跃238628096341720064；不要沿用旧日志“废弃字段/两套缺配置”的结论。
- GAIA `gaia_display_search(name=studentTagNames)`仍只查到通用字段显示实体，这**不能证明场景未配置**。该工具查的是fields，不是scene.layoutSchema。
- 本轮用正确pageNumber+sceneNumber只读 `scene/getDetail` 成功回读小班 `263719917126160384` / page `263719457028837376`，layoutSchema已有studentTagNames、GroupSelect筛选、getAllStudentTags数据源，editable=false、visible=false、display=true。这些flag不单独判为错误，需结合自定义渲染与个人列配置；真正编辑事件见FE-1。
- 大班GAIA已加字段复用2026-11-04归档/技能里的owner回读记录，本轮未重复写或查构建发布；不把该历史记录扩大到生产。

## 5. 已核实的后端接口链（无需凭名称猜测）

1. **列路由**：cronus routes `config/routes.js:48` `/clazzRosterOL -> ./roster`，tabKey continuationService；`:154` `/microClazzRoster`，小班tab。大班 `services/continuationService.js:5` → `/bgwApi/component/student-center/roster/renewal/page`，小班对应 `/roster/small/renewal/page`；请求带identification/filter/quickFilter/pager/route，响应data.list+paging。历史知识库两页面文档明确两种索引，不混用班级维度与辅导班维度。
2. **标签候选**：`services/actions.js:36` → `/fairy/student-center/subclazz/learnSituation/getAllStudentTags`；前端取 `data.filterDropdown.filters`。支持temporaryTags。
3. **批量/单个标签写**：同文件`:44` → `/component/student-center/batchOperate/tag/save`，`student-center-web/.../BatchOperateController.java:71` → `UserClazzMarkBiz#saveTagDetail:176`。type1=班级×学员、type2=老师×学员。**业务标签和临时标签不同**：业务标签存表/同步索引，临时标签 `TemporaryStudentTagServiceImpl#saveTags` 走企微；不能笼统写成“所有标签均直接推企微、均应在学员标签列持久显示”。PRD“同默认花名册”应继承此既有语义，若要求临时标签也显示则需业务澄清。
4. **备注校验/任务**：`services/clazzRosterOL.js:256/264` → `/remark/check/wk/friend`、`/remark/creat/edit/task`；widget读 `data.resultStatus`。modal`:69-76` 把姓名/手机号/身份/原企微备注替换为后端模板，传userIds+wkRemarkTemplate；`:79-80` 明示“正在修改，请到消息查看结果”。`WechatRemarkController.java:37/48` → `WechatRelationService` → BatchOperate任务 → `EditWkRemarkExportTaskService.java:197-203/321-330` 调官方备注；任务受理成功≠全部学员备注成功。本轮未调用这类写接口。
5. **标签名称与筛选**：ES studentTags → FieldsConvertDataQueryServiceImpl派生名称；前端默认页把显示字段筛选转为studentTags；BE-1/FE-2必须组合看，单看student_field_config和GAIA字段存在不足以验收。

## 6. 实际验证、失败与未覆盖

| 实际操作 | 结果 |
|---|---|
| 读取归档README、相关tasks/links/changelog、技术方案与PRD引用 | 成功；旧记录与最新正文/配置已区分。E2E主为子项2，只作背景，未重复跑兄弟任务 |
| 原PRD四图+两张相关引用图预览 | 成功下载并实际查看；其它引用图仅读图注，未声称全量图片检查 |
| 远端分支定位 | cronus无指定分支；gaotu-fe-promotions有指定分支bfadc6f；独立cronus远端master clone成功且干净 |
| 两续班标签formatFilter原函数只读执行 | 两者均保留studentTagNames，证明转换缺口；非单元测试套件、无新增测试文件 |
| test字段配置/标签flag/es_query_config SELECT | 成功，保存3组响应；无DML/DDL |
| GAIA字段显示实体查询 | 成功；第一次误用property_name未过滤，不作结论；更正name后成功。不用fields/search推断scene缺失 |
| 小班GAIA scene/getDetail | 首次仅sceneNumber回30055“页面找不到”；补源码要求的pageNumber后code0，布局含标签。是入参问题，非业务失败 |
| iris生产remoteEntry和引用chunk GET | 成功；Unicode解码后证实旧提示；线上Git SHA与浏览器实际渲染未验证 |
| iris远端clone | 经代理repository not found；未扩权限，生产静态产物已替代支撑FE-3 |
| 后端标签/备注写与页面E2E | **未执行**（最新只读授权）；没有用写入型“验证”改变业务状态 |
| 回溯执行/抽样源ES对账/覆盖2026-01-01边界 | **未执行/未获完成证据**；列为BE-2 |
| unit/build测试 | 未运行（无代码改动，编译不能验证配置和UI缺口）；未新增测试代码 |

## 7. 给主 W1 的整合结论

1. 优先报告 **FE-3线上共享群发旧文案**（生产静态产物已证实）、**FE-1两续班tab缺入口/单项编辑**和 **FE-2筛选参数错名**（指定范围外cronus远端master源码/函数证据），明确版本层级。
2. 后端先报告 **BE-1 test大班查询/筛选配置缺口**，而不是“后端都已齐、只差前端”；现有标签和备注写接口已存在，最小建议偏配置和前端参数，不需贸然新建接口。
3. **BE-2回溯2026-01-01范围**是原PRD验收缺口，不能被旧技术方案“通常不需要”覆盖。
4. FE-4联系学员组件内部实现、cronus线上SHA、prod配置/数据覆盖仍待核查。其具体缺口已写清，本轮报告交付不等待这些条件，也不宣称整项功能完成。
5. 本轮只有报告/证据副本/独立checkout的本地写入，无业务/代码修改。后续修正均为建议，交所有者判断；不生成使用说明、不询问详略。


## 主W1整合补充：联系学员公共包的可核实版本

子任务FE-4的“包内部实现未取得”已由主W1补齐到**依赖包级**，生产映射仍未完成。只读GET npm.baijia.com的@gaotu/reach-widget/0.1.3元数据与tarball，SHA512为`F1pGKRGPDkLg5LZUorkEw7KPG8Dtl7FZqZ2JMpjEW0+FLkTLaEwc+1folDBlPiKSAS9c9MkedSCjfSrAmKXiIg==`，与cronus ca703927的pnpm-lock.yaml:1498完全一致。没有npm install、修改依赖文件或执行包脚本，只解压临时只读副本。

沿`es/components/reach-business/components/main-content/index.js`→`type-and-content/index.js`→`reach-type/index.js`→`es/common/reach-type/index.js:65`读取：发送方式/类型区域仅有选项、未登录提示和刷新，没有PRD所示使用说明链接。解码整个es目录Unicode后检索两份文档token、使用说明/说明文档均无命中；调用方wrapper亦未提供相关链接参数。由此可确认**该锁定依赖版本未实现要求的链接入口**，不再仅有“wrapper没传参”的推断。动态选项`label/desc`仅作文本/Tooltip显示，不替代所示规范链接。

建议同时安排reach-widget组件及消费端依赖版本更新，不能只修iris。若不改、继续构建此lock版本，联系学员入口仍不具备该链接；本轮未识别生产cronus实际使用的包版本，不声称线上页面已验证缺失。临时源副本：`/tmp/w1-e0be7208/reach-widget-readonly/package/es/`。
