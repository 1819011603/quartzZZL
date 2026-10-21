# 续班AI分析 · 老师反馈"您所带班级不在试用范围 / 没有权限"

> **只解决**：老师在【班级花名册·续班服务】看到续班 AI 入口被挡，提示「**您所带班级不在试用范围，后续开通后将第一时间通知，敬请期待**」（或说"没有权限"）。
> 学员能进 AI分析 tab、但某模块一屏 `--`/"暂无" → 走 [`某学员续班AI分析为空.md`](某学员续班AI分析为空.md)，与本文无关。

## 判定入口（先分清是哪道门）

**① "不在试用范围" = AI 灰度（试用）名单，按登录老师判定，与班级无关**

| 项 | 值 |
|---|---|
| 接口 | `POST /component/student-center/ai/gray/merge`（无入参，按登录态） |
| 返回 | `{ "new-enrollment": bool, "renewal": bool, "refund": bool }` |
| 前端 | `src/hooks/useAIAnalysis.ts`（请求 gray/merge）→ `pages/roster/ContinuationService/custom/hooks/useCustomEventDom.js` 用 `renewal` 控制是否挂「续班AI分析」入口 |
| 后端 | `AiGraySwitchServiceImpl.listGraySwitch()` / `getGraySwitch()` |
| 配置 | `ai.gray.merge.map`（场景 → `{allSwitch, onlyAssistant, grayDeptList}`）、`ai.gray.merge.assistant.tag.list`（默认 `216` 二讲标签）、`ai.gray.merge.org.types`（默认 `[1]`） |

判定逻辑：登录老师 `accountId` → 若 `allSwitch=true` 直接过；否则查老师是否在 `grayDeptList` 部门内 → 命中且（若 `onlyAssistant=true`）带二讲标签 `216` 才算命中。**任一不满足 → `renewal=false` → 前端显示"不在试用范围"。**

**② "班级不在分析范围" = 班级级门控**：`POST /ai/needAnalyze {clazzNumber}`（**只用 clazzNumber，userId 忽略**），返回 `{needAnalyze, hint}`。见文末。

## 排查

1. 以该老师登录态调灰度接口：`renewal=false` → **确定是灰度名单问题**（与班级无关，文案"您所带班级"是误导）。
   ```
   POST https://fuwu.baijia.com/bgwApi/component/student-center/ai/gray/merge   （无 body）
   → {"new-enrollment":false,"renewal":false,"refund":false}
   ```
2. 查老师组织与角色标签（走 student-center 的 acl 桥，见 `baijia-invoke` skill；**18 位 accountId/orgNumber 一律传字符串**避免精度截断）：
   ```
   POST https://fuwu.baijia.com/bgwApi/component/student-center/test/acl/compare/service
   {"serviceNameAndMethodName":"com.gaotu.yunying.student.center.acl.impl.OrganizationAclServiceImpl#listByAccountId",
    "params":[["<accountId>"]]}
   → data[0].orgList（部门链 orgNumber/orgName）、data[0].staffLabelGroupList（角色标签 val）

   {"serviceNameAndMethodName":"...OrganizationAclServiceImpl#getAccountInOrg",
    "params":[<accountId>,["<grayDeptList 里的部门号>"], [1]]}
   → results[].result = 该部门是否命中
   ```
   `grayDeptList` 取自 Apollo `ai.gray.merge.map.renewal.grayDeptList`。
3. 判因（按优先级）：
   - **部门不在 `grayDeptList`** → 加部门。⚠️ 判定**只看登录老师本人的主岗部门链**（`getAccountInOrg(accountId, grayDeptList)`）：「虚线负责的部门」「下属带班老师」都不参与判定；领导本人部门不在名单，即使有二讲标签、下属学员有分析，入口也不挂（2026-10-21 案例：huangmengyao01，TT 侧长期班二讲中心，6 部门全 false）。
   - **部门已命中、但 `onlyAssistant=true` 而老师角色标签不是 `216`**（线上实测见过 `221 学习顾问`）→ **卡在标签，加部门无效**：给老师补 `216` 二讲标签（人员侧），或把 `renewal.onlyAssistant` 改 `false`，或把该标签 val 加进 `ai.gray.merge.assistant.tag.list`。
   - 以上都命中 → 再查班级级 `needAnalyze`（下一节）。
   > 2026-10-13 实测：老师部门(学习规划部 97353074458795709)已在名单、`getAccountInOrg=true`，但角色标签=221 → `renewal=false`；结论是**老师缺二讲标签，student-center 配置不动**。

配置快照见对应案例。登录态可直接用 `baijia-proxy` + Cookie 复现该老师。

## 附：班级级范围判定（needAnalyze）

`RenewalAiJudgeNeedHandleService.needHandle` 过滤器链（配置驱动，均在 student-center Apollo）：
1. `CommonRuleFilter`：课程部门白名单 `renewal.ai.sync.course.department.list`、`operationMode=1`、`clazzRoomType=1`、`courseType∈40`、学期含春/秋/寒/暑、班名/标签黑名单；
2. 各**学部专项**（课程部门路径命中才执行）：班名 include + 学期课节数区间，如精品班/清北/素养/本地化大班/TT。

`needAnalyze=false` 时 `hint` = Apollo `ai.app.need.not.analyze.hint`（**通用兜底文案**，不指向具体规则）；要拿具体规则用返回 traceId 查 student-center 日志 `RenewalAiJudgeNeedHandleService#needHandle rejected by <Filter>, tag: not_need_handle_*`。

```sql
-- 班级ID(字符串) -> 数字班级号/课程/班型
SELECT clazz_number,clazz_biz_number,clazz_name,course_number,course_type,school_term_id,
       clazz_room_type,operation_mode,subclazz_number,assistant_account_id,subclazz_status
FROM ees_data.dws_fuwu_course_subclazz WHERE clazz_biz_number='<班级ID字符串>' LIMIT 20;
```

## 验证

- 判定成立：`gray/merge.renewal` 回放结果与老师反馈一致，且能对上"部门/标签是否在灰度名单"。
- 不算通过：只看接口 HTTP 200；把 `needAnalyze`（班级级）当成"试用范围"用（两者门不同）；只拿到通用 `hint` 就下结论。
