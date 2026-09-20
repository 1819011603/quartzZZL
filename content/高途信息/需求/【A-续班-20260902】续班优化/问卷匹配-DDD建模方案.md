---
title: 问卷匹配优化 · DDD 建模方案
scope: product-server 为主（questionnaire 域），student-data / teacher-tool 为下游
status: 设计草案
owner: zhangzeling
updated: 2026-09-18
tags: [设计, DDD]
---

# 问卷匹配优化 · DDD 建模方案

> 本文是 [[README|需求 README]] 子需求1「问卷匹配优化」的**领域建模素材**——按 `tech-review-doc` 规范，它是飞书技术反讲的 `# 领域建模` **一节**，不单独成文；反讲落笔时并入即可。
> 代码位置以 product-server `feature-xuban-pre`（= `origin/master`，问卷匹配未在本需求分支改动）为准。
> 配套：[[README|最终口径/改动清单]] · [[changelog|决策摘要]]。

## 0. 先划边界：这套东西用在哪、不用在哪

**结论：只有「问卷匹配」这一个子域适合 DDD。** 五个子需求里：

| 子需求 | 复杂度来源 | 用 DDD？ |
|---|---|---|
| 1 问卷匹配优化 | **业务规则**（范围收紧 + 6 级优先级 + 调班同步） | ✅ 靶心 |
| 2 小班主讲数据 | 权限口径（角色分支） | ❌ 工程问题 |
| 3 扩科推荐优化 | **业务规则**（在读 8 条件 + 推荐排除枚举） | ✅ 可参照本文，但简单得多 |
| 4 数据落表 | ETL | ❌ |
| 5 AI 模块配置化 | 配置化 | ❌ |

本文只覆盖子需求 1。**不要拿它去套 2/4/5**——那是给 CRUD 套壳，反而制造熵。

## 1. 现状诊断：为什么这段代码"熵增"

现状类（product-server-domain，`service/renewal/questionnaire/`）：

| 类 | 行数 | 角色 |
|---|---|---|
| `ComputeUserService` | 43 | 规则链编排 |
| `ComputeRuleService` | 11 | 规则接口 |
| `OriginUserRuleService` / `MobileRuleService` / `NameRuleService` / `RelationIdService` | 49~82 | 4 条"班内"规则 |
| `QuestionnaireRecordService` | **844** | 上帝服务 |
| `QuestionnaireService` | **1721** | 上帝服务 |

四条"病"逐条对得上：

1. **语言不一致**：`compute` / `dealNotExistedComputeUserId` / `no_existed_compute_user_submit` / `computedUserId` —— 业务上说的是"这次提交该归到哪个学员"，代码里叫"计算用户"。新人（和 AI）都得先反推语义。
2. **贫血 + 规则散落**：`ComputeResult` 只有 `id + userId`（`model/ComputeResult.java:8-14`），**丢了"凭什么匹配"**。`ComputeParams` 只有 `id/originUserId/clazzNumber/mobile/studentName`（`model/ComputeParams.java:9-17`），**没有续班计划维度**——而"匹配范围收紧到续班计划"正是本需求的核心。
3. **重复即熵**：`OriginUserRuleService:27-33`、`MobileRuleService:36-40`、`RelationIdService:35-39` 三处**逐字重复**"按 clazzNumber 分组 + `listSubclazzStudentByUserIdsAndClazzNumber`"。加 3 条 plan 级规则 = 再抄 3 遍。
4. **兜底掩盖不确定性**：`QuestionnaireRecordService:322-325`

   ```java
   SubclazzDTO subclazzDTO = subclazzDTOOptional.orElseGet(() -> {
       log.warn("... no account subclazz use default: {}", ...);
       return subclazzDTOS.get(0);   // ← 熵的源头
   });
   ```

   "选不到就取第一个"把**无法确定**伪装成**已确定**，错误被静默吞掉，下游拿到一个看起来正常但可能是错的人。README 里「同名/亲属手机号歧义无解」和「重试 Job 被淹没」两个待确认项，根因都在这里。

**一句话**：这段代码的核心难点是"**这次问卷提交属于哪个学员**"这条业务规则，它现在散在 2 个上帝服务 + 4 个规则类 + 1 处兜底里。这正是 DDD 的靶心。

## 2. 战略设计

### 2.1 限界上下文

**续班问卷匹配上下文（Renewal Questionnaire Matching）**

职责：给定「一次问卷提交」+「链接绑定信息」，在**确定的范围内**判定它属于哪个学员；判不出来就显式标记为"未归属"，交人工/重试。

它**不负责**：问卷定义与绑定管理（`QuestionnaireService` 的 bind/validate/detail）、续班计划配置、学员主数据、班级归属。这些是上游上下文。

### 2.2 通用语言（Ubiquitous Language）

**这张表就是本方案最重要的产出**——先统一词，再动代码。

| 术语 | 含义 | 现状对应 | 现状问题 |
|---|---|---|---|
| 提交 Submission | 一次问卷表单提交 | `FormSubmitMqDTO` | 无领域名 |
| 绑定 Binding | 链接 ↔ 班级/问卷/辅导老师 | `QuestionnaireBindData` | 可 |
| 续班计划 RenewalPlan | 提交应当归属的计划 | `ProcessConfig.renewalNumber` | 散落 |
| 计划范围 PlanScope | 计划下全部前置课程 | `preCourseNumbers`（只在兜底方法里算） | 被埋在 `dealNotExistedComputeUserId` |
| 归属 Attribution | 判定提交属于哪个学员 | `computeUserId`（叫"计算用户"） | 词不达意 |
| 匹配依据 Evidence | 凭什么判定（哪条规则/什么范围/命中值） | **不存在** | 不可解释、不可审计 |
| 匹配范围 MatchScope | 在班内还是计划内找 | **不存在**（4 条规则硬编码班内） | 本需求要加 plan 级，无处安放 |
| 候选人 Candidate | 可能归属的学员 | 局部变量 `userIds` | 无模型 |
| 未归属 Unattributed | 无法唯一确定 | `computedUserId=0`（隐式） | 与"还没算"混为一谈 |

### 2.3 上下文映射（Context Map）

```
学员身份上下文 ──ACL──┐
(standard-user/id-query)│
班级上下文 ──────ACL──┼──▶ 续班问卷匹配上下文 ──领域事件(MQ)──▶ student-data / teacher-tool
(clazz-distribution)  │         ▲
续班计划上下文 ───ACL──┘         │
(renewal)                  调班事件(TRANSFER_TOUCH_EVENT)
```

- 对上游全部走 **防腐层**：现有 `UserAclService` / `IdQueryAclService` / `ClazzDistributionFeignService` / `TeacherAclService` 已经在做这件事，**保留**。
- 对下游只发**领域事件**（现状是 MQ tag：`user_submit` / `no_existed_compute_user_submit` / `no_bind_data_user_commit` / `cds_no_user_submit`）——这些 tag 应该收敛成有语义的事件名。

## 3. 战术设计

### 3.1 聚合

**`QuestionnaireRecord`（问卷提交记录）—— 聚合根**，身份 = `number`（业务唯一键 `recordId`）。

- 生命周期（当前是隐式的，要显式化）：
  `待归属 PENDING → 已归属 ATTRIBUTED / 未归属 UNATTRIBUTED（终态） → 调班后重新归属`
- 不变量（Invariants）：
  1. 一次提交最多归属一个学员；
  2. 归属候选必须落在**该问卷所属续班计划**的范围内（本需求的核心收紧点）；
  3. `UNATTRIBUTED` 是终态，不允许被"取第一个"覆盖。
- **注意**：不要为了聚合把 `QuestionnaireRecord` 的 DAO/Entity 大改。聚合边界体现在**行为归属**上，不是新建一个类。

### 3.2 值对象

| 值对象 | 字段 | 替代现状 |
|---|---|---|
| `SubmissionIdentity` | originUserId, mobile, studentName | `ComputeParams` 的前 3 个字段（语义化） |
| `MatchScope` | type ∈ {IN_CLAZZ, IN_PLAN}, clazzNumber, planCourseNumbers | **新增**，消除三处重复的"按班查" |
| `MatchEvidence` | rule, scope, matchedValue, candidateUserId | **新增**，`ComputeResult` 只有 id+userId 的缺口 |
| `AttributionResult` | recordId, userId(可空), evidence | `ComputeResult` |

`MatchScope` 是本方案的**杠杆点**：它把"在多大范围内找"从一个**隐含假设**变成一个**可传递、可测试的值**。现状 4 条规则全部硬编码 `IN_CLAZZ`；本需求要的 plan 级规则，本质就是"同一个规则 + 另一个 scope"。

### 3.3 领域服务

**`QuestionnaireAttributionService`**（由 `ComputeUserService` 升级）：

```
attribute(SubmissionIdentity, MatchScope) -> AttributionResult
  for rule in rules (按 priority 升序):
      candidates = rule.candidates(identity, scope)   // 规则只负责"找候选人"
      if 唯一命中: return AttributionResult.attributed(rule, scope, candidate)
      if 多命中:   记录 evidence，继续下一条（或按规则语义判定）
  return AttributionResult.unattributed(evidence 全量)   // ← 不再 get(0)
```

**`AttributionRule`**（由 `ComputeRuleService` 升级）：

```
interface AttributionRule {
    int priority();                        // 显式优先级，替代 Apollo list 的隐式顺序
    MatchScope.Type supportedScope();      // 或 supports(MatchScope)
    List<MatchCandidate> candidates(SubmissionIdentity, MatchScope);
}
```

**关键设计决策：6 条规则 ≠ 6 个类。** PRD 的 6 级 = 3 种"依据"（手机号/姓名/亲属手机号）× 2 种"范围"（同班/同计划）。正确做法是**抽 `AbstractAttributionRule`，把"查范围"下沉给 `MatchScope`**：

```
candidates(identity, scope) {
    candidateUserIds = resolve(identity);          // 依据：手机号/姓名/亲属号，各规则实现
    return scope.queryStudents(candidateUserIds);  // 范围：由 scope 决定查哪个 ACL
}
```

- `IN_CLAZZ` → `listSubclazzStudentByUserIdsAndClazzNumber`（现状 4 条规则用的）
- `IN_PLAN`  → `listSubclazzStudentByCourseNumbersAndUserId`（现状只在兜底方法里用过，:300）

这样新增 plan 级规则**不用抄代码**，直接复用现有 3 条规则的"依据"实现 + 换 scope。

### 3.4 仓储

`QuestionnaireRecordDao` 等**保持现状，不抽 Repository 接口**（理由见 §6）。

### 3.5 领域事件

| 事件 | 触发 | 替代现状 tag |
|---|---|---|
| `QuestionnaireAttributed` | 唯一命中 | `user_submit` |
| `QuestionnaireUnattributed` | 无法唯一确定 | `no_existed_compute_user_submit` |
| `ClazzTransferred` | 调课调班（新消费 `TRANSFER_TOUCH_EVENT`） | 无（新增） |

事件名要能表达"发生了什么"，不是"哪个方法处理的"。

## 4. 落地路线（分阶段，每阶段可独立上线）

> 原则：**先语义、再战略、后战术**。每一阶段都不改变对外行为（除 Phase 2 明确去掉兜底），可单独验证、可回滚。

### Phase 0 · 语义化（不改行为，1 天）

- `ComputeParams` → `SubmissionIdentity`，`ComputeResult` → `AttributionResult`
- 抽 `AbstractAttributionRule`，消除 `OriginUserRuleService:27-33` / `MobileRuleService:36-40` / `RelationIdService:35-39` 三处重复
- **验证**：现有单测全绿 + 线上日志对比归属结果一致

### Phase 1 · 战略：引入 MatchScope（不改行为，2-3 天）

- 新增 `MatchScope` 值对象；4 条现有规则显式声明 `IN_CLAZZ`
- 把"计划范围解析"（`renewalNumber` + `preCourseNumbers`）从 `dealNotExistedComputeUserId` 前移到 `dealCDSMsg`（README 改动清单第 2 条），作为 `MatchScope.planCourseNumbers` 传入
- **验证**：`IN_CLAZZ` 行为与线上完全一致；plan 范围可打印、可断言

### Phase 2 · 战术：6 级优先级 + 去兜底（本需求主体）

- 新增 3 条 plan 级规则（复用 `AbstractAttributionRule` + `IN_PLAN`）
- `priority()` 显式化 6 级顺序；Apollo `compute.rule.name.list` 降级为**开关**（可单独停用任一条）
- **删除 `QuestionnaireRecordService:322-325` 的 `subclazzDTOS.get(0)`**，改为 `UNATTRIBUTED`
- `dealNotExistedQuestionBindNumber`（:378）把跨 bizId 的 preCourseNumbers 收敛到本问卷所属续班计划（README 改动清单第 6 条）
- **验证**：`@ParameterizedTest` 覆盖 6 级 × 命中/多命中/不命中；造同名、亲属号、跨班数据各验一遍

### Phase 3 · 事件化：未归属终态 + 调班重算（收尾）

- `UNATTRIBUTED` 加终态标记 + 重试次数，修掉"重试 Job 被淹没"（README 性能评估最高风险项）
- 新增 `TRANSFER_TOUCH_EVENT` 消费 → `ClazzTransferred` → 旧班 A / 新班 B 分别重算
- **验证**：未归属记录不再重复重跑；调班后 A/B 两班状态与明细正确

## 5. 与 README「改动清单」的对应

本方案**不是另起炉灶**，是给 README 改动清单一个结构：

| README 改动项 | 本方案落点 |
|---|---|
| 1. `ComputeParams` 加 renewalNumber + planCourseNumbers | Phase 1 · `SubmissionIdentity` + `MatchScope` |
| 2. 解析前移到 compute 之前 | Phase 1 |
| 3. 新增 3 条 plan 级规则 + 抽 `AbstractUserRuleService` | Phase 2 · `AbstractAttributionRule` + `IN_PLAN` |
| 4. `compute.rule.name.list` 改 6 级顺序 | Phase 2 · `priority()` 显式化 |
| 5. 去掉 `get(0)` 兜底 | Phase 2 |
| 6. 收敛 preCourseNumbers 到本计划 | Phase 2 |
| 7. 明细 A/B fan-out 在 student-data | Phase 3（事件驱动） |

## 6. 明确不做（反过度工程）

对齐本仓 AGENTS.md 第一条与「反过度工程」：

- ❌ **不抽 `QuestionnaireRecordRepository` 接口**——只有一个实现，直接 DAO（AGENTS.md 1.3）
- ❌ **不引入 Event Sourcing / CQRS**——没有审计追溯需求，MySQL + MQ 够用
- ❌ **不拆微服务**——上下文边界是**逻辑**的，不是部署边界
- ❌ **不动 `QuestionnaireService`（1721 行）里 bind/validate/detail 等无关部分**——只碰 `match` / `matchResult`
- ❌ **不给 Phase 0/1 引入新中间件或新依赖**

## 7. 这套东西的价值（反讲/晋升视角）

如果要在反讲或晋升材料里讲这件事，故事线是：

1. **识别**：五个子需求里，只有问卷匹配的复杂度来自业务规则——**没有全用 DDD，也没有全不用**。
2. **诊断**：用"语言不一致 / 贫血 / 重复 / 兜底掩盖不确定"四条给出**代码证据**（类名、行号），不是空谈理念。
3. **建模**：`MatchScope` 把隐含假设变成一等概念，`MatchEvidence` 让匹配可解释——**这两个值对象才是方案的核心**，不是"我们分了 domain 包"。
4. **取舍**：明确写出"不做什么"及理由（AGENTS.md 1.3），证明是**克制**的建模，不是套模板。
5. **风险控制**：Phase 0/1 不改行为、可独立上线，证明是**工程化落地**不是大爆炸重构。

**一句话**：DDD 在这里的产出不是目录结构，是"**把'凭什么这么匹配'变成代码里能读出来的东西**"。

## 待确认

- [ ] Phase 0/1 是否与本需求同批上线，还是先合 master 单独上（属通用重构，不依赖本需求）
      —— owner: zhangzeling；触发：评审定排期时
- [ ] `MatchEvidence` 是否要落库（用于线上排查"为什么匹配到这个人"），落则需 DDL
      —— owner: zhangzeling；触发：Phase 2 开工前
- [ ] plan 级姓名规则的成本（README 性能评估已标为最贵），是否加独立 Apollo 开关
      —— owner: zhangzeling；触发：压测出结果后
- [ ] `AbstractAttributionRule` 放 product-server-domain 还是抽到 client 供他仓复用（倾向前者，YAGNI）
      —— owner: zhangzeling；触发：Phase 0 开工时定
