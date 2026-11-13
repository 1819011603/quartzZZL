---
title: 日常回访订正规则（GPS 1v1） · 决策摘要
tags: [需求, 决策]
---

# 决策摘要

> 只记会影响后续设计判断的理由，不记流水账。**日期倒序（最新在前）。**

## 2026-11-13｜鸿途定向 xjob 去掉人名后缀（prod/test 均**改名保留，不删**）

- **触发**：owner 要求 **xjob/Glue 命名不加人名后缀**；原 prod jobDesc = `日常回访_鸿途定向GLUE_masheng`。owner 先说「删」，**最新改为「不要删，改名即可」**（以最新为准）。
- **`masheng` 来源（给依据）**：来自**建任务时写进 `jobDesc` 的后缀**，**不是** Glue 类名/handler（类名 = `DailyVisitHongtuGlueHandler`，无 masheng；GLUE 任务 handler 为空）。Glue 源码里另有一处 `@author masheng`（作者注释，非命名后缀）。
- **处置**：
  - prod job `13270`（组 314）→ 改名 `日常回访_鸿途定向GLUE`；`jobGroup/executor/cron/glueType/triggerStatus(已停止)` 均不变（回读）。
  - test job `10005`（组 688）**上一轮曾被删除**；按最新「不要删」**已重建** → 新 id `10029`，同名 `日常回访_鸿途定向GLUE`、组 688、`GLUE_GROOVY`、`cron 0 0 3 * * ?`、已停止（回读）。
  - Glue 源码 `@author masheng` → `@author zhangzeling`（**逻辑不变**；prod GLUE 已重新保存并回读，`masheng`=0）。
- **数据不受影响（回读）**：`first_call_task_ext`（ext_type=4, ext_value=`202611_hongtu`）= **994** 条。
- **规则落实**：`~/.claude/skills/xjob-admin/SKILL.md` 新增「🚫 命名不加人名后缀（owner 规则）」（回读已确认）。
- **遗留**：prod job `13270`、test job `10029` 均**保留**（已停止、不自跑）。

## 2026-11-12｜排查：学员 5281257910「无课时仍生成回访任务」

- **结论（非缺陷）**：该学员在班主任 **142561** 名下的 1v1 辅导班 `529467966748690432` **仍有 2 课时未消**（total 4 / cost 2），其余 6 个在读 1v1 辅导班均为 0；老链路「剩余课时>0」校验按**辅导班口径求和** → 命中 2>0 → **正常生成**。owner 看到的"无课时"与老链路口径不一致（漏看了这 2 课时）。
- **任务来源**：老链路 `DailyVisitScheduleJob` 的 **11/10 补跑批次 `202611_3`**（taskCode `own_294974604432132096`，account 142561，create 2026-11-11 17:40，ruleType=3）；非鸿途 GLUE、非新链路。新链路 `first_call_task_1v1`=0（学员**无 1v1 容器**）。
- **代码依据**：`AbstractScheduledTaskJob#processAccount` 的课时校验（`totalAvailableHour<=0 → skip`）为**历史既有**（commit `9482d517f feat: 日常家长会任务`）；口径 = `TaskBizCommonQueryService#calculateUserTotalAvailableHourBySubclazz`：学员在该班主任名下**有效 1v1 辅导班的 Σ(totalHour−costHour)**。本次 dailyVisit 需求未改该口径。
- **数据**：7 个在读 1v1 辅导班 (total/cost)：`430693827387428864`(1/1)、`433232018633981952`(160/160)、`438313070230781952`(6/6)、`493751047830206464`(2/2)、`494084437772900352`(150/150)、`527438327033702400`(20/20)、**`529467966748690432`(4/2 → 剩 2)**；`getAccountIdByUserIdAndClazzNumber(5281257910, 529467966748690432)=142561`。
- **定性**：**预期内 / 历史既有**（非本次改动回归）。
- **影响面**：只有"存在任一有效 1v1 辅导班剩余课时>0"的学员才会生成；全部为 0 的学员不会被老链路生成。该学员属「仍有少量课时」被漏看。
- **建议**：无需改代码。若产品口径期望"按 1v1 子产品/容器剩余课时≤0 即不生成"（=**新链路口径**），与老链路辅导班口径不同，需产品明确是否统一（归入口径待决项）。

## 2026-11-12｜鸿途定向生成：Xjob Java GLUE 实施与产出（owner 选 B）

- **决策**：owner 选 B —— 新建 Xjob Java GLUE 只对【一对一学部_鸿途项目_班主任组】定向生成日常回访任务，**不动线上 config12/调度**。
- **实现**：`GLUE_GROOVY` 类 `DailyVisitHongtuGlueHandler`（源码 `/tmp/hongtu_glue_prod.java`，307 行）；复用老链路(辅导班)/新链路(容器)两条既有生成逻辑 + 现有任务级防重；只圈 org `112619412210993665`；校验命中 config `12`；独立批次 `executionSeq=202611_hongtu`（避撞 `202611_x`/`1v1_202611_x`）；`executorParam` 含 `dry` 只打印。**仓库零改动**（GLUE 在 xjob 内）。
- **注册**：test job `10005`（组 688）/ prod job `13270`（组 314「高途-运营工作台-student-data」），均 GLUE_GROOVY、`cron 0 0 3 * * ?`、**已停止**（不自跑）。
- **test**：dry / real / 二次触发 均 `handleCode=200`；二次 old=new=0（幂等）。
- **prod 产出（回读）**：real `handleCode=200` → **老链路 `first_call_task` 生成 994 条**（`task_generate_rule_type=3`、`execution_seq=202611_hongtu`、`isdel=0`），落 **10 个账号**(79877/233084/265665/257429/267090/174961/252942/259546/267359/180960)，org 均属鸿途_班主任组；有效期至 `2026-11-25 00:00`；`first_call_task_1v1`(新链路)=**0**（这些老师名下无 GPS 容器）。
- **影响面**：11/12 当日 ruleType=3 新任务 = **994，全部为鸿途**；**【班主任部】零新增**；与 11/10 批次 `202611_3` **零重叠**（这批账号此前无任何日常回访任务）。
- **待确认**：鸿途任务落**老链路** `first_call_task`；若业务期望进**新链路**(容器/新表)或新页面，当前不会产生——需确认页面读老表还是新表。
- 备注：config12 已含鸿途，故 **11/25 正常批次也会覆盖鸿途**；本 GLUE 属当期一次性补齐。

## 2026-11-12｜「只生成鸿途、不动班主任部」方案评估：配置 vs Xjob Java Glue

> owner 问：配置方式行不行？不行能否直接建一个 Xjob Java Glue？只读评估 + 方案，未实现、未改配置、未触发。

**Q1. 现有配置方式（把鸿途加进 config12 org）能否满足「只生成鸿途、不动班主任部」？→ 不能（干净地）。**
- 圈人范围 = config 的 `org_numbers` 集合。要保持"班主任部不动"，就不能把班主任部从 config 移除；只要班主任部还在 config 里，**一次触发即两边都生成**（不是只鸿途）。
- 若要把一次触发限制成"只鸿途"，只能把 config 改成仅 `112619412210993665` → 但该批次（及后续自动批次）**班主任部不再被覆盖**，并非"不动班主任部"。
- 且**批次级防重**（`hasExecuted(type,configId,executionSeq)`）会让"改完 org 再重跑已执行批次"整配置跳过。故配置方式无法同时满足"只鸿途 + 不影响班主任部"。

**Q2. 新建 Xjob Java Glue 实现 → 可行。**
- 平台支持 Java GLUE：`xjob_glue_code` / `xjob_save_glue_code`（全量覆盖脚本、下次触发即生效），在服务端 JVM 内**可直接取 Spring Bean**。已有同类先例——GPS1v1 首call 的 GLUE 补数（glue 里取 `TaskBizService` 调 `insertFirstCall1v1Task`，走真实过滤链路、幂等）。
- 可复用现有生成逻辑：`StaffAclService#listStaffByOrgNumbers([鸿途 org])` 圈人 →（新链路）`ClazzDistUserAssignAclService#queryContainerByAccountId` + `DailyVisit1v1ScheduleJob#filterCandidates`(大班课/课时) + `DailyVisitTaskCreateService#filterContainers`(资格) + `FairyAclService#createDailyVisit1v1Tasks`；或（老链路）`TaskBizCommonQueryService`(辅导班/学员/课时) + `DailyVisitTaskCreateService#filterLegacyUsers` + `createTask`。
- 防重：任务级防重保证幂等（老 `DailyVisitDuplicateChecker` 按 account+user+executionSeq；新 `first_call_task_1v1` 唯一键）。`executionSeq` 用**独立可追溯值**（如 `202611_glue_hongtu`）区分批次。
- 工作量约 **0.5–1 人天**（写 GLUE + test 环境 dry-run 验证 + prod 受控执行）；风险**中**：生产写操作、必须**选对链路**（老 `first_call_task` vs 新 `first_call_task_1v1`，避免新老重叠）、seq 独立避免与自动批次串号。

**Q3. 推荐方案。**
- 若只是"让鸿途按周期出数据"：**保持 config = 两个 org、正常跑即可**，不必 GLUE（班主任部本就每轮生成，不是额外副作用）。
- 若必须"只出鸿途、且完全不动线上配置/调度（一次性/定向补齐）"：**推荐 Xjob Java Glue**（优于临时改配置——不改线上调度、可复用现有过滤与防重、可精确限定到鸿途 org）。
- GLUE 改动点（供后续授权）：① 圈人 `listStaffByOrgNumbers(鸿途 org)`；② 按实际链路复用对应 service（含大班课/课时/资格过滤）；③ 独立 `executionSeq` 写入任务 ext 参与防重；④ 先 `dry-run`（只打印）核对范围与条数，再真跑；⑤ 执行前确认鸿途走老链路还是新链路。

## 2026-11-12｜配置已加鸿途：生成覆盖与防重问答（张梦燚问）

> 背景：刘金金已在 config 12 加上鸿途；张梦燚确认「需要鸿途数据」，并问「生成时是只生成鸿途，还是班主任部也会覆盖」。只读排查，未改配置、未触发。

**配置现状（读回）**：`task_rule_config` id=12「日常回访」`org_numbers = 97353074458795824,112619412210993665`（= **一对一学部_班主任部** + **一对一学部_鸿途项目_班主任组**，已加），`role_labels=4-216`，`task_generate_rule_type=3`，`task_day_limit=0`，`task_expire_hour=384`，执行日 `[10,25]`，`update_time=2026-11-12 21:36`。

**Q. 一次触发会不会同时生成班主任部 + 鸿途？**
- 会。一次触发按执行日生成一个批次，覆盖配置里**所有 org（含各自子组织）**——不是只生成鸿途。依据 `AbstractScheduledTaskJob#getMatchedAccounts`：遍历配置所有 `org_numbers`（`StaffAclService#listStaffByOrgNumbers` 取每个 org + 全部子组织的员工）→ 逐个 accountId 做虚拟架构就近匹配 → 命中 config 12 的全部取用。两个 org 都挂在同一 config 12 上，故都生成。

**Q. 只想生成鸿途，当前能否做到 / 对班主任部影响？**
- 能，但需临时把 `org_numbers` 设为**仅** `112619412210993665` 再触发一个**未跑过的批次**；此批次【班主任部】不会生成（范围不包含）。
- 防重（都会拦住，不会重复、也不会静默覆盖）：
  - **批次级**：`AbstractScheduledTaskJob#processConfig` 用 `scheduledTaskExecutionLogDao.hasExecuted(ruleType, configId, executionSeq)`，同一 executionSeq（如 `202611_x` / `1v1_202611_x`）已成功执行则整配置跳过——**重跑同批次不会再补、也不会重复**。
  - **任务级**：老链路 `DailyVisitDuplicateChecker`（同 account+user+executionSeq 跳过）；新链路落 `first_call_task_1v1` 由唯一键（`uq_task_code` / 同(班主任,学员)批内唯一）保证「同轮次不重复、跨轮次各 1 条」。
- 注意：若班主任部本批次已生成过（如 11/10 批次 `202611_3`/`1v1_202611_3` 已在），事后想「只补鸿途」会被**批次级防重**拦（同 executionSeq 已执行）——需换一个未执行批次，或删除该批次执行记录后再跑（届时班主任部会一并重算，但任务级防重使其幂等、不重复）。

**建议（要给鸿途数据、又不折腾）**：保持 config = 两个 org，按授权触发所需批次；一次即同时覆盖【班主任部】+【鸿途项目_班主任组】（班主任部本就每轮生成，不算额外影响）。

## 2026-11-12｜回访任务常见口径问答（电话次数 / 组织覆盖 / 完成条件 / 11-10 为 0）

> 本轮 owner 转来的一线提问与查证结论（只读排查，未改配置/代码）。

**Q1. EES 任务列表里的「电话次数」统计范围是多久？**
- 结论：该班主任与该学员**历史累计的有效通话次数**（单次通话时长 ≥ 60 秒算 1 次），**不限时间范围**——不是任务有效期、不是自然月、不是近 N 天；「最近电话」= 这些有效通话里最晚一次。老/新链路口径一致。
- 依据：页面接口 `POST /feign/taskPlatform/task/list` → `PlatformTaskPageResponse.callCount`；计算在 `PlatformTaskResponseConverter#queryCallRecords`（仅按 `user_id + account_id + isDel` 过滤 + `call_duration ≥ 60s`，**无时间条件**）、`FirstCallUserCallRecordDaoImpl#listByUserIdsAndAccountIds`。数据佐证：userId=11072460099132 / account=215616 历史记录中 ≥60s 通话 = **58** 条、最晚 **2026-10-29 20:03:06**，与截图完全一致（任务筛选区间为 11-10~11-24 却显示 10-29 的通话，即累计证据）。

**Q2. 回访是否只覆盖【一对一学部——班主任部】？【一对一学部——鸿途项目——班主任组】查不到任务。**
- 结论：线上日常回访**只圈了【一对一学部——班主任部】**（虚拟架构 org `97353074458795824`），故【一对一学部——鸿途项目——班主任组】（org `112619412210993665`）**不在范围内、不生成任务**——是组织范围没包含，不是学员/容器不满足。
- 依据：`task_rule_config` id=12「日常回访」（`task_generate_rule_type=3`）`org_numbers=97353074458795824`、`role_labels=4-216`、执行日 `[10,25]`；解析 `ees_data.virtual_employee_info`：`97353074458795824 = 高途课堂_高途_H业务线_一对一学部_班主任部`；`112619412210993665 = 虚拟架构_高途_H业务线_一对一学部_鸿途项目_班主任组`（路径 `一对一学部→鸿途项目→班主任组`，与「班主任部」是**一对一学部下的并列分支**）。圈人链路 `AbstractScheduledTaskJob#getMatchedAccounts`：配置 org（含全部子组织）→ 员工 → accountId → 虚拟架构就近匹配 → 老链路取老师名下辅导班学员 / 新链路取老师名下起效容器。
- 若要覆盖：在 config 12 的 `org_numbers` 追加 `鸿途项目(111441651978733568)` 或 `鸿途项目_班主任组(112619412210993665)` 即可（父级自动含全部子组织）。
- 备注：prod 另有测试配置 id=9（org 含 `115518527455104020`、`97353215785868807`），非生产生效范围。

**Q3. 任务完成的单次通话要求 ≥5min，呼入/呼出是否都算？**
- 结论：现状**不区分方向，家长呼入与班主任呼出都计入**（双向）；需求未规定方向，建议维持双向；若要「仅限班主任呼出」需产品明确后再改。
- 依据：student-data 日常回访通话过滤 `DailyVisitCallRecordFilter#filterValidCalls` 只按任务有效期 `[startTime, expireTime]` 过滤，**不看 `call_type`**；fairy 日常回访完成判定（`FirstCall1v1StatusCheckService` / `SubTaskUpdateService`）亦无呼入/呼出方向过滤。完成条件本身为 `task_finish_condition = {"requiredRuleList":[{"type":1,"value":5}]}`。

**Q4. 为什么 11/10（10 号）那批回访任务为 0？**
- 结论：11/10 **没有自动触发**——当时配置的执行日不含 10 号（被配成 25/26），故 10 号未跑；随后**还原执行日为 `[10,25]` 并手动补跑**，11/10 批次已生成（老 **13742** / 新 **40**）。
- 依据：`platform_task_scheduled_execution_log` config_id=12 无 `execution_date=2026-11-10` 的自动执行记录（自动批次 10/10、10/25 于 00:00 触发；11/03、11/10 均为手动，时间 14:30、17:18）；`task_rule_config#12` 当前 `taskFrequency=[10,25]`、`update_time=2026-11-11 17:49`（补跑后还原）。

## 2026-11-03｜青舟流水线「合并代码到master分支」步骤标记完成
- 背景：release→master 已真合并（fairy codeMerge `205822`、student-data `205823`，均 code 200），但**流水线步骤未自动翻状态**（页面仍显示「未开始」）。
- 按 owner 要求，用 `release.py mark-done --pipeline-id <id> --pipeline-status`（`updatePipelineRecordStatus` + `updatePipelineStatus`，`status=4`=「标记完成」）标记：
  - fairy **1324925**、student-data **1324917**、student-data **1324918**（同仓多流水线，一并标记）——均 code 200。
- 回读（`getPipelineList` templateId=7）：三条 `stepName=合并代码到master分支`、`status=4`。
- 说明：skill 中 `mark-done` 即「手动把流水线记录/状态标完成」（SKILL.md 第 24 行）；青舟「合并代码到master分支」步骤的「标记完成」对应此接口。

## 2026-11-03｜release→master 合并完成（owner 授权；feature 不补合）
- **owner 明确**：`feature-1v1-daily-visit-job` 的 `07da7ae45`（AICR 修复）**不补合**，直接 `release`→`master`。
- **fairy**：`release.py merge --service fairy --pipeline-id 1324925` → `createMergeRequest` pipelineRecordId `1716949` → `codeMerge [205822]` **code 200**；master 新 tip **`fbf51ad8`** 含 release `54aa10d6` ✓。
- **student-data**：`merge --service student-data --pipeline-id 1324917 --image …release-4e3c5df4-…` → `createMergeRequest` `1716950` → `codeMerge [205823]` **code 200**（**同仓多服务只 merge 一次**，`markDoneIds` 空）；master 新 tip **`c9fc2c410`** 含 release `4e3c5df49` ✓。
- 顺序 fairy→student-data；**未 force push**；未动 service-dock、未动 service-dock。

## 2026-11-03｜抓真实「全量发布」接口 + 补发 prod-1
- **Chrome 抓包**（UI「全量发布」→确定，student-data prod-1）：`POST /qingzhou/tianti/operation/prod/serviceDeploy.ajax`，body `{"type":7,"grayType":"percentage","stepNum":1,"environment":"prod","envInfoId":100,"pipelineId":1324918,"imageCode":"acr.baijia.com/uqun/student-data:release-4e3c5df4-20261103110116"}` → **`{"data":1716651,"code":200,"msg":"success"}`**。
- **真因**：全量**逐泳道**发，且 **`pipelineId` 必须是该泳道对应的灰度流水线**（14→1324917、100→**1324918**）。此前 `full --pipeline-id 1324917` 对两个泳道都用了 14 的 pipeline，导致 100 被服务端判「灰度发布未完成」；**不是 eureka 豁免问题**，是**泳道↔pipeline 对应错误**。
- **prod-1 已全量（完成）**：经 UI 全量发布（code 200），prod-1 回读 = **2 pod 全 Running、全在新镜像 `release-4e3c5df4-20261103110116`**（无 eureka，符合预期）。至此 **student-data prod(14)+prod-1(100) 均在新镜像**。
- **skill 更新** `qingzhou-prod-release`：写入真实接口 + 「逐泳道各发、pipelineId 一对一、显式新 imageCode」+ 前置校验（泳道全集 / 泳道↔pipeline / 镜像=新产物 / 灰度就绪含无 eureka 用 Running / DDL 等）。

## 2026-11-03｜student-data 全量参数核实（只读）+ prod-1 未全量原因
- **student-data 有 2 个 prod 泳道**：`prod`(envInfoId=**14**, prod-BJ-Ali1) + `prod-1`(envInfoId=**100**, prod-1-BJ-Ali1)。依据 `qz_prod.prod_swimlanes()` = `env_infos(sc,'prod')`（只读实测返回 `[{14,prod-BJ-Ali1},{100,prod-1-BJ-Ali1}]`）。
- **正确参数**：`release.py full` 的 swimlane 默认 = 全部 prod 泳道（`env_info_ids = args.env_info_ids or [g.id for g in prod_swimlanes] or [14]`）→ 默认即 **[14,100]**；接口 = 每泳道一次 `POST /qingzhou/tianti/operation/prod/serviceDeploy.ajax`，body `{type:7, grayType:"percentage", envInfoId:<14|100>, imageCode, pipelineId, stepNum:1, environment:"prod"}`。
- **此前漏的参数**：① 我用了 `--env-info-ids 14` **显式限制为 14**，漏掉 **100**；② 未传 `--image`，`full` 默认取 `latest_image(release)`，student-data 该值为 **release-a1459ff1（旧）** → 镜像也错。
- **prod-1 未全量的原因**：①（我）`--env-info-ids 14` 漏 100；② 默认含 100 的 `full` 被**服务端 `code=400 灰度发布未完成`** 拦（prod-1 整组 eureka UNKNOWN）；③ prod(14) 上线新镜像是经其它流程完成。实测 prod-1 **常规部署仍为旧镜像 `release-a1459ff1`**（仅 `graytest` pod 是新镜像）→ 待补发。
- 未调用发布接口；结论=**必须含 `envInfoIds=[14,100]` 且显式 `--image`（新镜像）**；即便参数正确，prod-1 仍可能被服务端 UNKNOWN-eureka 校验拦，需平台豁免。

## 2026-11-03｜全量发布完成（四服务 prod 新镜像 Running）
- **前置**：DDL 工单 `147777` **已执行**（executed=true，两条 EXECUTED）；xjob 新 job `13157` 已建（仍**停止**，待上线切换老 job `10680`）。
- **全量（type=7, percentage）**：
  - fairy（pipeline `1324925`）→ 镜像 `release-54aa10d6-...`：prod **40 pod 全 Running/UP**。
  - student-data（pipeline `1324917`）→ `release-4e3c5df4-20261103110116`：prod **90 pod 全 Running/UP**；prod-1 **1 pod Running（无 eureka，符合预期）**。
  - dws（pipeline `1324922`）→ `release-4e3c5df4-...117`：**90 Running/UP**。
  - gps（pipeline `1324921`）→ `release-4e3c5df4-...119`：**19 Running/UP + 1 启动中**。
- **服务端拦截（已知）**：student-data 全量 API 返回 `code=400 灰度发布未完成`（因 **prod-1 整组 eureka 均 UNKNOWN**）；但 prod 实际已滚动到新镜像并经接口验证。兼容规则已写入 `qingzhou-prod-release` skill。
- **硬性验证**：prod 调 `getTeachProductTypeMap`（`traffic-env: prod`）→ HTTP 200 / rvoCode=0，返回 `{17641711169503747:3, 18043610911081577:1}`，traceId `c2f3461c-229e-417f-9d4f-30e5d92d87c3.0.1`。

## 2026-11-03｜灰度验证（prod-gray-test，仅 tangwen01、只读无损）
- **命中灰度 pod**：student-data-graytest-6d8c6897f-qwwsd（ip 10.243.46.228；JVM 元数据 `trafficEnv=grayTest`/`version=grayTest`/`groupId=prod-gray-test`，镜像 `release-4e3c5df4`）。带 `traffic-env: grayTest` 经 ACL 桥调用，traceId `f15f41be-5290-4200-b690-6060bdcc3aa1.0.1`、`8ef61b5d-dccf-40d3-bd9b-59bc24865a9b.0.1` **均出现在该灰度 pod 的 app.log**（各 4 行，含 RequestLogAspect）→ 确认命中灰度、非老 pod。
- **filterContainers（大班课·小班课剔除）**：输入 tangwen01（accountId **131951**）名下真实容器 3 条（子产品 17641412292575747=小班(3)、18003796307544604=大班(1)、18043610911081577=大班(1)）→ 实际返回 **`[]`（全部剔除）**，与预期一致（`allowedProductTypes=[2]` 仅 1v1）。traceId `f15f41be-…`。
- **getTeachProductTypeMap**：tangwen01 去重子产品类型 = 17641711169503769/17641412292575747/17641716516716545/17641711169503747→**3(小班)**，18033715231262209/18043610911081577/18003796307544604→**1(大班)**。traceId `8ef61b5d-…`。
- **未覆盖（如实说明，未造数、未用其它账号）**：tangwen01 名下**无 productType=2(1v1) 容器** → `1v1 保留`、`同老师多子产品取下单最近` 无数据可验。
- **转班/改派不删**：需真实 MQ 事件（有副作用）→ 本轮只读未触发；该行为已由源码 no-op + 单测 + test 隔离 E2E 覆盖。

## 2026-11-03｜灰度发布完成（四服务 prod-gray-test Running）
- **发布六步顺序落定**（写进 `deploy-image` / `qingzhou-prod-release` skill）：① 构建集成镜像 → ② 发测试环境 → ③ 等就绪 → ④ 发灰度 → ⑤ 等就绪 → ⑥ 全量（须 owner 确认）。三接口：`createOrUpdatePipeline.ajax`(构建, envInfoId=2/template=4/grayTest) / `serviceDeploy.ajax`(发布, type=1/stepNum=2/envInfoId=2) / `getPipelineList.ajax`(列表, template=4 测试/7 灰度)；发布前先查列表，未完成灰度非本人发起→与 owner 确认；**无 eureka 容器（如 student-data prod-1）不校验 eureka，用 pod Running**。
- **集成镜像**（含本需求代码，release 合并提交）：fairy `1324853`(`release-54aa10d6-...`) / student-data `1324871` / dws `1324872` / gps `1324873`(`release-4e3c5df4-...`)。
- **测试环境**：student-data/dws/gps 经 `serviceDeploy` 发布（fairy 由 owner 发），test 主泳道 eureka 均 UP。
- **灰度**（prod-gray-test，每服务 1 机器）：fairy `1324925` / student-data `1324917`(prod-BJ) + `1324918`(prod-1) / dws `1324922` / gps `1324921`。回读灰度 pod **均 Running**：fairy `...graytest-...nmkr9`(UP)、student-data `...graytest-...qwwsd`(UP) + `...prod-1-gray-test-...mz46q`(**无 eureka**)、dws `...graytest-...qsh82`(UP)、gps `...graytest-...q2glj`(UP)。
- 流水线列表核对：四服务**无「非本人发起的未完成灰度」**，无冲突。
- **未上全量**（等 owner 确认灰度验证通过）。

## 2026-11-03｜AICR 两条 high 修复 + 上线项落定（DDL/Apollo/xjob/表对齐）
- **AICR #779 两条 high（`ClazzTypeFeignServiceImpl#getTeachProductTypeMap` L604-607 / L632-635）**：owner 判定**真 bug、改**。修复口径：下游**业务失败（`isSuccess=false`/null）→ 抛 `BusinessException` 交调度重试**（对齐 `getCreateTimeOrThrow` L182-185 及 #18001 严格口径）；**成功但空数据 → 跳过**。补 4 个单测（失败/null 抛异常、空数据跳过），9/9 通过、BUILD SUCCESS；push 远端 HEAD `07da7ae45`。**注意：release 已含旧（含 bug）代码，需经 MR !1805(release) 再合入该修复。**
- **DDL 工单 147777（prod）已 EXECUTED**：`gaotu.first_call_task_1v1` 加 `execution_seq`/`task_dedup_owner` 生成列 + 唯一键 `uq_owner_user_rule_execution`，drop `uq_number`（cluster 211 gaotu-crm-prod）。回读 prod 唯一键 = PRIMARY + uq_owner_user_rule_execution。
- **Apollo PROD** 新增 3 key 已发布（releaseKey `20261103101642-188a560667e40670`）：`taskPlatform.dailyVisit1v1.allowedProductTypes=[2]`、`taskPlatform.dailyVisit1v1.create.batch.size=100`、`taskPlatform.dailyVisit.filterStoppedStudents=false`。
- **prod xjob**：新建 `DailyVisit1v1ScheduleJob` jobId **13157**（group 314，cron `0 0 * * * ?`，**默认已停止**）；上线时启本 job、停老 `DailyVisitScheduleJob`(10680)，二者不同时调度。
- **test 表结构对齐 prod**：删除 test 多余的 `uq_task_code`（`ALTER TABLE ... DROP INDEX uq_task_code`，已执行回读）；test 唯一键现与 prod 一致。（test 另有 6 个普通索引 idx_* prod 无，未在本次授权范围，待确认。）
- **MQ**：本需求**未新增**任何 topic/group；`GID_student-data_dailyVisit_subclazzQuit_prod`、`GID_gps_user_container_fairy_firstCall_group_prod` 生产均已存在且在线 → **无需申请**。
- **旧 MR** !1788(student-data)/!1101(fairy)：web/接口关闭被 CSRF 422（试 3 次），改由 owner 页面手动关。

## 2026-11-03｜filterLegacyUsers 属本需求、保留；MR 指向正式分支
- owner 明确：老链路 `DailyVisitScheduleJob.filterTaskUsers → DailyVisitEligibilityService.filterLegacyUsers`（生成前调 `validateDailyVisit` 资格）**属本需求范围，保留**；旧「老链路生成逻辑不动」口径以本条为准。
- owner 明确：本特性唯一新增 SNAPSHOT 依赖 `service-dock-api` 改 `1.0.11-RELEASE`（已编译 BUILD SUCCESS、push `2852ce84a`）。
- 分支规范：正式交付分支 = `feature-1v1-daily-visit-{job,task}`；`feat/1v1-daily-visit-{job,task}` 为旧分支（被正式分支完全包含、0 独有提交）。因 GitLab 不能就地改 MR 源分支，**关旧开新**：
  - student-data 新 MR **!1805**（`feature-1v1-daily-visit-job → release`）；旧 **!1788**（`feat/... → release`）待关。
  - fairy 新 MR **!1103**（`feature-1v1-daily-visit-task → release`）；旧 **!1101**（`feat/... → release`）待关。

## 2026-11-02｜统计沟通不需要回访任务（GLUE 补任务=错方向）
- 「统计 10.25–11.2 的沟通」直接查通话表 `first_call_user_call_record`（account_id/user_id/call_time/call_duration）按 `call_time` 过滤即可，**与回访任务无关**。
- 写 Java GLUE 直接往 `first_call_task(_1v1)` 伪造覆盖 10.25–11.2 的任务：窗覆盖后通话判定会通过（`DailyVisitCallRecordFilter`/`isWithinTaskPeriod`），但需再触发计数、绕过校验、维护唯一键/防重/子任务/ES/MQ，风险高、真实性差 → 不推荐。

## 2026-11-02｜生成基于跑时状态；任务有效期从生成时刻起算（不能统计 10.25–11.2）
- 生成基于**跑 job 那一刻**的容器/剩余课时/资格（代码：`DailyVisit1v1ScheduleJob.processAccount` 的 `queryContainerByAccountId`/`queryAvailableLessonCount` + `DailyVisitEligibilityService`；老链路 `AbstractScheduledTaskJob.processAccount` 同）。**不是 10.25 当天快照**；批号只是标签。
- 任务有效期 = 生成时刻 + `taskExpireHour`（config55=11h；实测 id1891-1898 start=2026-11-02 16:34:52、expired=2026-11-03 03:34:52）。通话只在 [start, expired] 内算有效（`DailyVisitCallRecordFilter.isCallInTaskPeriod`；fairy `TaskBizService.isWithinTaskPeriod`）→ **不能统计 10.25–11.2 的沟通**。
- 无「回填过去周期」口径。结论：要「10.25 批次号」可（传 `2026-10-25`）；要「按 10.25 当天状态 + 统计 10.25–11.2 沟通」不行。

## 2026-11-02｜批次号=年月_执行日序号；10.25 批次=202610_2（已实测）
- 执行日=25 生成 25 号批次；批次号 `execution_seq=年月_该执行日在配置执行日列表中的序号`。线上执行日 [10,25] → 10 号=…_1、**25 号=…_2 → 10.25 批次=202610_2**。
- 手动触发参数：只传 `25` 按**当前月**（11 月→202611_1）；要精确 10 月 25 日批次传完整日期 `2026-10-25`。
- 实测（test）：config55（执行日 10、25）触发参数 `2026-10-25` → 生成 **8 条**（execution_seq `202610_2`、execute_date 2026-10-25）；exec-log id=138。

## 2026-11-02｜生成口径 = 运行时当下；job 只按配置执行日跑（3 号实测）
- 日常回访任务生成依赖**跑的那一刻**的学员容器 + 剩余课时 + 资格（`AbstractScheduledTaskJob.processAccount`、`DailyVisit1v1ScheduleJob.processAccount/filterCandidates`、`DailyVisitEligibilityService`），**不是历史批次快照**。
- job 只在 config `taskFrequency`（执行日，1~28）命中时才跑；`executor_param` 只是把某天当执行日评估，**不能创造出配置里没有的执行日**。
- 线上执行日=10/25（无 3）→ 3 号跑=0 条。实测：test config55 执行日加 3 → 触发 → 命中执行日 2026-11-03、创建 8 条（毛萌 2 条），证明按当天状态生成。测试后 config55 已还原为 [25]。
- 注意：`execution_seq=yyyyMM_执行日在列表中的序号`；加更早的执行日会改序号排序，可能撞已跑批次被跳过。

## 2026-11-02｜上线准备
- 建 TAPD 免测需求 story `1122531521001397150`；建青舟免测发布编排 `24158`（fairy rank1 → student-data rank2；含 -dws/-gps 整仓）。

## 2026-11-02｜「转班/改派任务没了」根因 = 泳道未隔离（非代码 bug）
- 两例（老链路 王小品 7147120734、新链路 12509090003/7683682631）任务 `isdel=1` 系被**其它泳道跑旧代码的 pod** 消费同一 MQ 事件后删除（test 各泳道独立组各收一份、共享 DB）。
- 隔离 E2E（`ons_consume_verify` 只推给我们泳道组）证明：我们修复版消费转班/改派事件后任务 `isdel` 仍=0。

## 2026-10-30｜同老师多子产品也取下单最近
- 原实现只在「≥2 个不同班主任」时选举，同老师多子产品回退按 subProductId 最小 → 选错。放宽为「≥2 个可回访 1v1 子产品」均取下单最近（`b114af4b`）。

## 2026-10-29｜R2/R3：转退班不删任务
- owner 明确「转班不删除任务」。老链路消费者 `DailyVisitSubclazzQuitConsumer.consume()` 与 `DailyVisitTaskDeleteService.processQuitEvent()` 改 no-op；fairy 移除 `deleteDailyVisitTasks`。

## 2026-10-28｜GPS 规则落 student-data、老链路仅切开关
- 老链路 `DailyVisitScheduleJob` 按辅导班圈人，容器场景圈不到；新链路需按容器圈人，故新增 `DailyVisit1v1ScheduleJob` 落 student-data。
- 老链路代码不动：停课过滤仅由 Apollo `taskPlatform.dailyVisit.filterStoppedStudents`（默认 false）控制。
