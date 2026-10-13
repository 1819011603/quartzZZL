# 续班AI分析 · 某学员续班AI分析（用户画像/沟通摘要）为空

> **只解决**：单个学员在【学员详情页 AI分析 tab / 班级花名册】的「续班用户画像」「沟通概况/沟通总结」等模块**一屏都是 `--` / "暂无"**，而同班其他学员有内容；或产品问"某学员有沟通记录为什么没有 AI 分析"。
> 整班/整部门都没数据（不是个别学员）走部门灰度配置方向，与本文无关；续班 tab 打不开/提示无法分析看 `ai/needAnalyze` 的 hint。

## 判定入口

页面 = 学员详情页 AI分析 tab（GAIA 微组件 `aianalysisinformations`，`tabs/renewal`），后端 student-center。
关键接口：
- 续班用户画像：`POST /component/student-center/ai/clazzUser/userPortrait`
- 沟通概况/总结：`POST /component/student-center/ai/clazzUser/commSummary`

画像/摘要**不是**直接读页面上看到的"通话记录"，数据链路：

```
沟通(电话/微信语音/微信聊天) 被 AI 沟通分析平台(consultant-assistant / ss-robot-facade 精灵) 抓取
  → 分析前回调 student-data /feign/aiComm/extInfo 判定 needAnalysis
  → 平台分析完推送 MQ topic ai_analyze_result, tag ees_xb_analyze (AnalyzeResultMsg)
  → student-data-dws 消费，写 ees_data.ai_renewal_cdp_user_comm_base / _scene
  → student-data 异步走 AI 基座生成画像/摘要，回写 ees_data.ai_app_clazz_user_scene
  → userPortrait 接口读 ai_app_clazz_user_scene(scene_type=1) / commSummary(scene_type=2)
```

判定顺序：**先看结果表有没有行，再看输入表有没有行**。输入表空 = 分析根本没跑，跟页面/接口无关。

## 排查

### 1. 结果表（页面直接读的）
```sql
SELECT clazz_number,user_id,app_scene_type,app_scene_key,create_time,update_time
FROM ees_data.ai_app_clazz_user_scene
WHERE user_id IN (<学员id>, <同班对照学员id>) ORDER BY user_id,app_scene_type;
```
scene_type：1=用户画像、2=沟通摘要、3=沟通建议评分、4=服务建议评分。目标学员 0 行 = 没有可展示的 AI 结果（页面渲染兜底空态，符合预期，非白屏 bug）。

### 2. 输入表（分析产物落库处）
```sql
SELECT clazz_number,subclazz_number,user_id,account_id,email_prefix,comm_type,comm_tag,
       FROM_UNIXTIME(comm_time/1000) ct,comm_duration
FROM ees_data.ai_renewal_cdp_user_comm_base
WHERE user_id IN (<学员id>, <同班对照学员id>) ORDER BY user_id,comm_time;
-- 中间结果同理：ees_data.ai_renewal_cdp_user_comm_scene
```
输入表也 0 行 → 该学员的沟通数据从未进入分析链路，问题在**上游**，不在 student-center/student-data 的读侧。

### 3. 排除"是不是 student-data 拦了" —— 线上实测 extInfo 判定
`/feign/aiComm/extInfo` 是分析平台分析前的回调，返回 `needAnalysis`。用学员真实通话回放（prod，读操作）：
```
POST https://fuwu.baijia.com/bgwApi/student-data/feign/aiComm/extInfo
{"userNumber":<学员id>,"uniqueKey":"probe","callDataType":1,
 "callTime":<该通话毫秒时间戳>,"emailPrefix":"<通话老师邮箱前缀>"}
```
`callDataType`：0 电话 / 1 微信语音 / 2 微信聊天。返回 `needAnalysis=true`（且 clazzNumber/subClazzNumber/teacherRole 正确）→ student-data 侧放行，断点在上游平台；返回 false → 按下面过滤条件逐条对。

### 4. 对象的班级/辅导班/老师基线
```sql
-- 学员在某班的辅导班归属、在班状态、入班时间（按 clazz_number 哈希分 64 张分表）
SELECT clazz_number,user_id,subclazz_number,clazz_student_status,join_clazz_time
FROM student_dw_data.dws_fuwu_course_clazz_user_<shard>
WHERE clazz_number=<班级号> AND user_id=<学员id>;
-- 辅导班带班老师 account
SELECT subclazz_number,subclazz_name,assistant_account_id,subclazz_status
FROM ees_data.dws_fuwu_course_subclazz WHERE clazz_number=<班级号>;
-- 通话记录（老师 account 是否=带班老师，见 dws_fuwu_call_record.account_id）
SELECT user_id,account_id,msg_type_name,call_status,call_duration,call_time,
       (call_url IS NOT NULL AND call_url<>'') has_url
FROM ees_data.dws_fuwu_call_record WHERE user_id=<学员id> ORDER BY call_time;
```
分表 `<shard>` = clazz_number 的哈希分片；定位分片可先对 0..63 各分表按 clazz_number 计数找出非空分片（`ees_data`/`student_dw_data` 同一 cluster 336）。

## 会被过滤掉的常见原因（逐条排除）

1. **老师角色不匹配**：通话老师 account 必须 = 该学员辅导班的**带班老师**（`assistant_account_id`）或该订单的**业绩归属人**；客户角色/顾问角色不同判定分支不同。
2. **时间窗外**：实时圈选开始时间 = 该学员在该辅导班的 `joinClazzTime` 往前推 N 天（部门配置 `beforeDays`），且 ≥ 当前时间往前 `renewal.ai.sync.dirtyJoinTimeBeforeDays` 天；结束时间 = 班级 endTime。入班前的通话不分析。
3. **部门/课程灰度**：`renewal.ai.sync.course.department.list` 命中的部门、且 `needHandle`（系列课 `courseTypeIncludeList`、排除 `courseTagExcludeList`、班级名/学季/专项过滤）通过；同班对照学员有数据即说明班级层面通过。
4. **圈选通话类型/时长**：部门配置 `renewal.ai.select.dept.config` 的 `callTypeList` / `callDurationMin` / `wechatChatUserReplyMin`。
5. **排除名单**：`renewal.ai.sync.clazz.exclude.list` / `renewal.ai.sync.user.exclude.list`。
6. **上游平台没产出**：平台没抓到该学员沟通、或 ASR/对话失败 → 无 `AnalyzeResultMsg`，base/scene 永远为空（此时 student-data 侧 extInfo 是 true，需转上游平台查该 userId 的沟通任务/圈选记录）。

配置在 student-data Apollo（`renewal.ai.*`），key 清单见 `RenewalAiCommSceneConfigService`。

## 验证

- 结论成立：`ai_renewal_cdp_user_comm_base` 对目标学员 0 行、对照学员有行，且 extInfo 回放返回 needAnalysis=true（→ 断点在上游）。
- 常见"成功信号"不算业务生效：接口 HTTP 200、返回 `{}`（就是空态本身）、`ai_app_clazz_user_scene` 有旧 `create_time` 但 `update_time` 很老。
- 若输入表有行但结果表没有：看 `renewal.ai.analyze.realtime.enable` 是否开启、AI 基座异步任务是否成功回写。
