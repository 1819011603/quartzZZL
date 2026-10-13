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

1. 以该老师登录态调 `POST /component/student-center/ai/gray/merge`：`renewal=false` → **确定是灰度名单问题**（与班级无关，文案"您所带班级"是误导）。
2. 定位老师为何不在名单：查其**主岗部门**与**是否有二讲标签(216)**，对照 `ai.gray.merge.map.renewal` 的 `allSwitch` / `grayDeptList` / `onlyAssistant`（prod 2026-10-13 快照见案例）。
3. 不在名单 = **配置问题**（要不要把该部门加进 `grayDeptList` 由产品/运营决定），不是代码 bug。
4. 仅当 `gray/merge.renewal=true` 却仍进不去时，再查班级级 `needAnalyze`（下一节）。

公司组织/标签查询走 `OrganizationAclService`（staff 域）；登录态可直接用 `baijia-proxy` + Cookie 复现该老师。

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
