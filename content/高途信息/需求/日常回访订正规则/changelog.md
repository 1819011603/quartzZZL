---
title: 日常回访订正规则（GPS 1v1） · 决策摘要
tags: [需求, 决策]
---

# 决策摘要

> 只记会影响后续设计判断的理由，不记流水账。**日期倒序（最新在前）。**

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
