---
title: 【A-续班-20260902】续班优化 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

---

## 2026-09-21（反讲 v0.4 全量核验 + 产品口径确认）

### 🤖 Claude
- **反讲按 `origin/master` 全量核验**（4 组并行 subagent、~90 处 path:line），升 v0.4 订正 8 处：`UnificationSwitchService` 实际在 student-center、`RenewalInfoServiceImpl` 最终 subtract 为 :236-238、`refactorMainTeacherStudentInfo` 无角色分支、`QuestionnaireRecordService:171-177` 是 DB 查询非"解析"、`ProcessController`/`NodeExtConfigVO` 行号偏移、`DwsRenewalQuestionnaireConsumer` 消费在 :187、退款口径两套都在 student-data、**移除 origin/master 不存在的 `predictLevelReason`**。
- 补「目标」正文并把误置于 Non-goals 的目标条目归位；子需求2 统一为「现状 OR 已满足 PRD、本批无需开发」；问卷匹配 MySQL DDL 由「否」改「是」；补《发问卷整体技术方案》7 项现状/风险（归因在 product-task、`compute.rule.name.list` 线上未配置、共享开关默认 true 短路、扇出各班意向可能不同、`recordId` 缺唯一索引、兜底表无人读、前置课程列表三口径）。
- 新建飞书**《待产品确认清单》**（21 条，按 5 子需求分组）https://gaotuedu.feishu.cn/docx/L2yrdOPEAoIOMux1JLXcGtR4nde ，挂在需求总入口下。

### 👤 我（产品口径答复）
- 子需求1：①同名/一号多孩**不做产品侧解法**，按规则写；②改派**在问**→ 后经王永诗确认**不用做**（手工绑定维持现状）；③「同一手机号多次提交只展示最新」**EES 已有**（已核 teacher-tool `QuestionnaireConsumer#handleRenewalQuestion`）；④明细班级名称/ID 字段**已有**；⑤teacher-tool **不加**续班计划列。
- 子需求2：⑥下单优化本期**不做**；⑦主讲适配**确认无需开发**；⑧统计口径**实时**（《小班课字段+指标》指标页 6-9 行）。
- 子需求3：⑨【推荐排除】为**新增配置**（不合并）；⑩粒度 **续班计划级**；⑪下单页选品 + B 端 `recommendProductList` + C 端**均按「纯续+扩科推荐范围」展示**；⑫「在读」口径**不变**（只是推荐商品少几个），退款状态口径不变。
- 子需求5：⑯配置入口**先用 Apollo 后端配置**（先搞简单点）—— 续班/退费各一个 `Map<虚拟架构部门, Set<模块>>`（如 `{虚拟架构部门A:[1,2,3], 虚拟架构部门B:[1,2,3,4,5]}`）；王永诗曾建议用 GAIA 统一，用户 2026-09-21 定"先 Apollo，能按部门配就行"；⑰部门 key = **contains**；⑱「用户反馈」「主管点评」算 AI 模块；⑲无需枚举映射；⑳「不展示」落点 = 前端仓 `ees/aianalysisinformations`（分支 `feature-refund-reason-20260825`）的接口；㉑关闭模块后历史数据按**隐藏**。
- 子需求4（13-15 数据落表）：本批不做，仅登记，未答。

### 👤 我（飞书群 · 王永诗答复）
- 「问卷匹配规则改成续班计划维度，手工绑定只能改学员、不能改班级，要改吗」→ 王永诗：**不用**。
- 「AI 模块配置化要做新页面配权限，还是用 GAIA」→ 王永诗：**能用 GAIA 就用这个，统一**。
- 用户后续定：AI 配置入口**先用 Apollo 后端配置**（"先搞简单点"），GAIA 页面后续再议。

### 👤 我（内部 / 评审口径）
- 跨仓承接方：product-server / teacher-tool 改动**归本团队**。
- 调课调班同步承接方：**student-data**；旧班 A 来源 = 报文 `LlsTransferCourseMessageDto.originalOrderInfo.clazzNumber`（已核实该字段存在）。
- 【扩科】就是**加个过滤**，但位置订正：**扩科推荐本来就在 cart 算**（`ExpandSubjectRecommendService#recommend`，小班 :32 / 大班 :69，只按年级匹配）→ 过滤加在**这两个重载**里；`recommendProductList` 只是把 cart 结果转成 B 端列表。**student-data 的扩科科目 subtract 只服务花名册「大小班扩课科目」展示字段，不是推荐收口点**（此前反讲把它当推荐收口点，属误判，已订正）。
- 【扩科】深挖现状：cart 扩科算法 = 读扩科配置 → `collectStudentPostGrades` 取后置年级 → `studentPostGrades.contains(recommend.getGrade())` 年级匹配，**仅此一步**。**难点**：cart 现有 context **没有"在读学科"**（全仓无在班/在读查询），拿「对方模式在读学科」要么 cart 复刻 PRD 8 条件（口径漂移），要么由 student-data 透出（建议）。已把「现状算法 + 改动难点」写进反讲「详细设计·扩科推荐」。
- 【扩科】**「在读」口径核实（订正）**：PRD 9 条件里 student-data 现有在读科目链路只覆盖 6 条（非成人 / 专题系列课 / 不含赠课标签 / 非纯预售 / 相同学年学期靠 yearTermGrade 分组 / 授课模式靠数据源），**缺「上课形式为线上(operationMode)」与「订单未全部退款」2 条**（operationMode 过滤只在 student-data 别的链路有）。此前记"口径不变/均已具备"有误，已订正。
- 【扩科】**「在读科目」数据来源核实**：来自 **student-data 自己的表**（小班 `dws_small_clazz_user_subject`、大班 `dws_fuwu_clazz_user_subject`），查询走本地 DAO，不是调外部接口；表的原料才是外部的（进/退班 MQ `gaotu_subclazz_student_event_test` + 课程中心 + 订单）。→ 「对方模式在读学科」集合可由 student-data 直接透出给 cart。已写入反讲「详细设计·扩科推荐」。
- 【AI】部门→模块配置放 **student-center 的 Apollo**（问卷匹配的 `compute.rule.name.list` 仍需在 product 公共 namespace `gt.product-public-app` 新增）。
- 【问卷匹配】重试 Job = product-server `QuestionnaireRecordService#dealNotExistedComputeUser`（每轮重跑 3 天内 `computed_user_id=0` 记录）—— 是否同批改造仍待评审。
- 【AI】部门匹配**有现成先例**：`RenewalAiCommRealTimeSelectHandleService#getDeptAiConfig:214-224` 即 `departmentPath.contains(configKey)` + `@ApolloJsonValue Map`（部门取课程/班级 `courseDO.getDepartmentIdPaths().get(0)`）。待定：①用班级部门还是老师部门（展示侧要同口径）；②`contains` 子串匹配对数字部门 id 会前缀误命中，需带分隔符。已写入反讲「详细设计·AI」。
- 【扩科】在读科目表**可能不准 & 回溯手段**：表由 MQ+外部数据拼成（消息丢失/乱序、课程缓存过期、退款未同步、判定变更后未重算、is_del 不一致）。回溯：大班 `dws_fuwu_clazz_user_subject` → XXL-Job `BackClazzUserSubjectHandler`（按 clazzNumbers 或 beginId/endId）；小班 `dws_small_clazz_user_subject` → 手动接口 `/gps/manual/back/smallClazzUser/subject` 等（校验 `/gps/manual/check/smallClazzUser/subject`）。已写入反讲。
- 【扩科】风险应对**结论：加开关、不新写回溯逻辑** —— 配置本身即 per-计划开关，再加全局 Apollo 降级开关（脏数据一键回退【无排除】）；回溯沿用现成 Job/接口、不内联进推荐链路（C 端高频 + 口径重复）；要自动只做离线对账。已写入反讲「风险管理」。

### 🤖 Claude（订正产物）
- 飞书清单已按答复回填 ✅（1/3/4/5/6/7/8），并在顶部加「确认进度」callout；反讲「待确认项」#2/#3/#5 与 14-20 段同步回填。
- 本地 `README.md` 新增「已定（2026-09-21 产品/数据确认）」小节并从「待确认」移出已闭环项；`links.md` 登记清单文档；`tasks.md` 补 R-01~R-04。

---

## 2026-09-18（晚 · 扩科推荐重新纳入）

### 🤖 Claude
- 用户更正：**子需求3 扩科推荐要做**（此前误判为不做）。范围由 1/2/5 改为 **1/2/3/5**。
- 派 2 个只读 agent 重新探索扩科推荐，产出精确证据并补进反讲（现状 / 方案对比 / 详细设计 / 接口 / 影响面 / 风险 / 待确认）：
  - 配置侧：`ExpandSubjectConfigDTO`（product-server-client，字段 expandSubject/forceBuy/allowDuplicate/beginTime/endTime/recommendList）、B 端 `NodeExtConfigVO.extConfig`、表 `node_config.ext_config` + `renewal_expand_subject_recommend`；B 端 `ProcessController#edit/list/expandSubject*`。**三仓 grep `推荐排除/excludeSubject` 零命中 → 该字段不存在，需新建。**
  - 计算侧：student-data 扩科集合收口点 = 大班 `RenewalInfoServiceImpl#groupGradeCurrentRenewalSubjectMap`（最终 subtract）、小班 `SmallRenewalSubjectService#getRenewalSubjectInfo`（:474-483）。PRD「在读」8 条件中 5 项已有过滤器，仅「授课模式/上课形式线上/订单未全部退款」3 项需新建。
  - 推荐侧：cart `RenewalService#getRenewalDetail:217`→`ExpandSubjectRecommendService#recommend`（**仅按年级过滤**）；B 端 `recommendProductList`/`recommendClazzList` 结果来自 cart；**下单页选品与推荐不共用扩科逻辑**。
  - 短链：`recommendUrl` 短链实际走 REACH-SERVICE（README 原说 PROMOTION-B 只对 appInfo 成立）。
- 反讲补：标题/摘要改 1/2/3/5；新增子需求3 现状+方案+详细设计（各带 mermaid 图）；接口变更补扩科（`/product-b/b/renewal/process/edit` 保存、`/process/list` 查看回显、`expandSubject/*`、cart 推荐/选品、B 端 recommend*）；影响面加扩科行；风险/规避/待确认各补；变更历史加 v0.2；依赖的接口补 cart C 端推荐 + B 端老师推荐。
- 用户补充接口：C 端推荐 `GET /cart/web/renewal/cart`、B 端老师推荐 `POST /product-b/b/renewMaster/recommendProductList`、B 端 `POST /product-b/b/renewal/process/edit`（保存）与 `/process/list`（查看）也要改。

### 👤 我
- 「3 要做 我弄错了，再加一个，都改一下」；给出推荐链接、cart C 端 curl、B 端老师推荐接口、B 端 process/edit 接口；给出扩科 PRD 原文与链接（LYCYwqS7ziljApknUlbclPSrnzh），指出「扩科班级不区分大小班可随意选，所以才加配置」。

### 🤖 Claude（读 PRD 原文订正扩科口径）
- 读扩科 PRD 原文，解除歧义：**【推荐排除】不是手填清单，而是扩科推荐为【是】时可编辑、默认空、单选的枚举【无排除】/【排除不同授课模式在读】**；选后者按「不同授课模式在读学科」动态排除（当前课程大班→排小班在读学科；小班→排大班在读学科）。问题根源=扩科班级/商品不区分大小班可随意选。B端/C端按「纯续+扩科推荐范围」展示。
- 反讲订正：现状加问题根源与跨模式重复推荐；方案一改为 PRD 精确口径；详细设计改动点 1/2/4 重写、补 B端/C端展示适配；待确认 11 改为「过滤收口层」、12 改为「选品是否同过滤」，删除已解决的粒度/维度问题。

---

## 2026-09-18（晚）

### 🤖 Claude
- 产出【A-续班-20260902】续班优化 技术反讲（子需求 1/2/5 合并，评审前草案）：https://gaotuedu.feishu.cn/wiki/EC45wOefUi0buMkO7O0cipp9nEc（docx `GiqcdeCakoAsvfxH43accvD4nHf`）。含交接摘要、背景/名词/关联方、现状链路、方案对比（每子需求方案一/二+建议）、详细设计与 `path:line`、接口清单、影响面、风险、发布计划、待确认，7 张 mermaid 图。
- **位置规则（用户明确）**：反讲必须挂在**需求总入口 `Qox8wFcmHiXBgnkxFBtcd82gnsh`**（【A-续班-20260902】续班优化）下面，不是个人空间根目录。已写进 skill `tech-review-doc`。
- **删除此前 5 个「现状·改动·风险」子页面**（问卷匹配/主讲数据+下单/扩科推荐/数据落表/AI模块配置化）。核对出入：主讲页仍写"快速加购/续班确认表属新功能、要做"（实际下单优化不做、底层已存在）、权限字段名写成 `EsGaiaMapping`（实际 DB 表 `es_query_config`）；AI 页 8 模块清单与"6+2"口径不一致、"关闭后历史数据待定"（已定隐藏）。
- 建 skill `tech-review-doc` 并把「换会话能续接」「反讲挂原需求节点下」定为硬要求。

### 👤 我
- 要求：只做 1/2/5；写飞书技术反讲（一篇合并、评审前草案）；反讲要清晰、有图、有代码位置/接口/影响范围；换 AI 会话后能接住上下文；建一个专门写技术反讲的 skill；反讲要挂在原需求下面；旧的 5 个子页面可删。

---

## 2026-09-18（晚 · 代码深挖）

### 🤖 Claude
- **【主讲数据+下单】组合商品加购底层链路 master 已存在**（order `CombinedProductCartHelper`/`CartService#getProductInfos` 的 `COMBINE_PRODUCT` 分支、product-server `CombinedProductFeignController#searchNoAuth`/`ProductEsDao` 组合过滤、student-data `CartEventService#resolveCombineProductClazzNumbers`/`CartEventConsumer`），原"快速加购组合商品属全新功能"作废；"快速加购"具体新增什么待需求方明确。续班确认表确实无实现。
  - **【AI模块配置化】`AiAppSceneEnum` 仅 6 个(1-6)非 8 个**；退费侧 `RefundReasoningEnum` 5 个 + `RefundPredictionService` 1 个 = 6 个吻合。续班第 7/8 个模块 PRD 明细本地无存档。
- 同时核实接口/消息准确路径与行号（反讲素材）：`/feign/questionnaire/match`、teacher-tool `/feign/questionnaire/user/page/multiByClazz`、`/orderComponent/b/cart/addCart`、`ai/clazzUser/userPortrait` 等；product-server 确认不消费 `TRANSFER_TOUCH_EVENT`，student-data `DwsAfterSaleSyncConsumer` 只处理退费 tag。
- 待确认新增 5 项（快速加购定义、续班AI 8 模块清单、部门 key 口径、展示侧 type3/4 无接口、UserFeedbackController 归类）。
- 建 skill `tech-review-doc`：固化反讲骨架、接口七列表、影响面六项、图规范，并把「换会话能续接」定为硬要求（正文最前必须放交接摘要）。

### 👤 我
- 要求：只做 1/2/5 三个子需求；写飞书技术反讲（一篇合并、个人空间新建、评审前草案）；反讲要清晰、有图、有代码位置/接口/影响范围；换 AI 会话后能接住上下文；先派 agent 深挖代码再汇总问缺口；并建一个专门写技术反讲的 skill。

---

## 2026-09-18（下午）

### 🤖 Claude
- 确认【问卷匹配优化】的 product-server + teacher-tool 改动归属给我，产出逐文件改动清单（见 README 子需求1「改动清单」）：product-server 7 项（ComputeParams 扩字段、解析前移、3 条 plan 级规则、Apollo 6 级顺序、去掉 `subclazzDTOS.get(0)`、无绑定号路径收敛计划、fan-out 留给 student-data）；teacher-tool 3 项（续班计划列按需、改派能力、明细查询无需改）。
- 关键结论「范围扩大能否匹配正确」：**能解决"人在同计划其他班"（调班/发错链接）+ 手机号精确匹配**；**不能解决同名/亲属手机号歧义**（取 userId 小仍是猜），范围越大歧义面越大。plan 级必须限定"同一问卷的课程"而非全计划课程，否则会匹配到不同问卷的班。
- 明确"改不了/改不全"的边界：①同名/一号多孩根因（输入信息不足，算法无解，需产品决策）；②存量错配按 PRD 不回溯；③明细 A/B 两行 fan-out 在 student-data，不在我手上；④调课调班同步若由 product-server 承接需新增 consumer + DAO 方法；⑤teacher-tool 加续班计划列需 DDL；⑥规则改动影响大班+小班全部续班问卷匹配，回归面大。
- **用户纠错并订正**：`TAG_Subclazz_Transfer` 是「转辅导班」（同班内换班主任，`SubclazzStudentMqDto.type=7`，消息只带一个 `clazzNumber` + old/new `subclazzNumber`），**不是** PRD 说的"班级 A 调课到班级 B"。真正的调课调班事件 = topic `gaotu_after_sale_event_test` + tag `TRANSFER_TOUCH_EVENT`（`LlsTransferCourseMessageDto`），目前**只有 reach-service 消费**（`TransferCourseClazzTriggerConsumer`，"只给触达使用"）；student-data `DwsAfterSaleSyncConsumer` 虽订了该 topic 但只处理退费 tag。故调课调班同步是**要新增消费**，此前"调班事件已存在且 student-data 已消费"的结论作废。已同步 README（设计草案/待确认/上线影响面/必须知道的坑）、飞书子页面、tasks T-09。
- 飞书 5 个子页面顶部各加一行跳转：「对应需求：<原始需求 wiki 节点>　所属需求文档：<需求总入口>」。
- 飞书导航补链接：①「需求」目录页写入指向需求文档【A-续班-20260902】续班优化的链接 + 子页面列表；②需求文档页追加「原始需求文档」区，列 5 个原始需求 wiki 节点 + 3 份参考 PRD + 跨班错配分析文档。
- 按用户要求完成 5 个子需求的飞书归档（个人空间）：建「需求」目录 → 把需求总入口移入 → 5 个子页面（问卷匹配 / 主讲数据+下单 / 扩科推荐 / 数据落表 / AI模块配置化）各写「现状·改动·风险·待办」。顺带**订正 links.md 里主讲/扩科/数据落表 3 个 wiki node token 互相错配**（node_token 与 document_id 对不上，已用 `wiki +node-get` 实测改正）。
- 按用户要求在飞书建档：父文档「【A-续班-20260902】续班优化」+ 子页面「问卷匹配优化：匹配逻辑现状·改动方案·风险」（写入匹配逻辑现状/改动方案/待办清单/风险点）。**注意落在个人空间 `my_library`（space 7485951460694425602）**——原需求 wiki 空间 `7521677387233722372` 无建节点权限（131006）。链接与 token 见 links。
- 同步本地：tasks.md 加 T-06~T-09（问卷匹配开发待办），links.md 加飞书入口与 token，README 导航加飞书总入口。
- 性能评估（3 个风险点）：①**重试 Job 放大**——`dealNotExistedComputeUser` 每轮重跑 `computedUserId=0` 且 3 天内的记录（100/批、16 线程），改"不唯一→0"后这批记录永远匹配不上、每轮重复处理，叠加规则链 4→7 条，负载上升，必须同步改造重试策略；②每条提交最坏 RPC 从 7-8 升到 11-12 且串行（`compute` 顺序 for，MQ 仅 5 线程），群发场景会排队；③plan 级姓名规则最贵（班内版已 scroll 2000/批 + listByUserIds），建议改走 `listByStudentName`(限100)+计划过滤。手机号/亲属号 plan 级成本可控（500/批，候选集小）；`compute.rule.name.list` 在 Apollo 可单独降级。
- 深挖【问卷匹配优化】现状：定位到真正匹配实现不在 student-data/student-center，而在 **product-server**（即 Feign 名 `product-b`）——绑定层 `QuestionnaireService#match:928`、记录归属层 `ComputeUserService` 规则链(`OriginUser`/`Mobile`/`Name`/`RelationId`，全部限定班级内)、跨班兜底 `QuestionnaireRecordService#dealNotExistedComputeUserId:253`（混候选取第一个 `subclazzDTOS.get(0)`）。订正原 README「6级规则本仓未实现需新建匹配服务」的表述：规则链已存在且 Apollo 可插拔，改造是扩规则而非从零新建。
- 补 teacher-tool 侧：明细表 `user_questionnaire_record` 无续班计划字段，查询 SQL 只按 `type+project_number+clazz_number+user_id` 过滤；手工绑定只能改 user 不能改 clazz。
- 调课调班同步订正：student-data `SubclazzUserSyncConsumer` 已消费 `TAG_Subclazz_Transfer`，但只刷续班状态/科目，未刷问卷字段。
- 用户提供飞书分析文档《续班问卷跨班错配问题：现状、成因与产品解法》，与代码结论互相印证（其描述的"扩范围+混候选+取第一个"即 `dealNotExistedComputeUserId`）；已登记 links。可借鉴点：根因论据、6级规则仅"少猜错"不能归零、"待认领+改派"与存量修复是需求未覆盖项。

### 👤 我
- 要求弄清【问卷匹配优化】的现状/改动/影响/代码改动，并提供此前写的跨班错配分析文档供借鉴。

---

## 2026-09-17

### 🤖 Claude
- 建档：付星/马胜在飞书一次性转发5个续班优化wiki链接，要求初评并记录需求。最初误判为5个独立需求分别建了5个目录，用户澄清"这五个需求是一个需求"后合并为单一目录 `续班优化(秋季批)`，旧名保留在 frontmatter `aliases` 里防止按旧目录名搜索时找不到。
- 5路 Explore agent 并行完成两仓库(student-data/student-center)代码定位，结论已整合进本文件「涉及的代码」按子需求分节呈现。
- 核对5份PRD原文后修正：子需求2补记续班确认表(P1)与快速加购组合商品(P0)、删去"等需求方补充方案"的失效待确认；扩科推荐历史数据口径改为条件句（当前不回溯）；补记调课调班同步前提与场景、各子项P级、PRD可点链接。
- 重跑两仓库代码定位核查（基准 `origin/master`，工作区在另一需求的 `feature-xuban-pre`）并抽查复核，订正 6 处关键结论：问卷状态刷新非唯一挂载点(共4条路径)、`StudentSubclazzQuestionnaire` 是零引用孤立实体、多次提交去重在 `pageQuestionnaire` 非 `pageQueryQuestionnaire`、`mainTeacherList` 由 `WideSmallClazzTeachingBinder` 绑定、`CartEventService` 是业务 Service 非 ACL 适配器、数据落表另有直连 Doris Stream Load 先例；并补实 C端推荐/选品在 cart、快速加购落 product-server+order、续班确认表改动面在 contentReport+reach-service。

### 👤 我
- 在飞书里转发5个续班优化需求wiki链接，要求初评并记录需求，同时看下应该怎么做、做下设计。
- 澄清：这五个需求是一个需求，文档只要记录在一个文件夹下。
