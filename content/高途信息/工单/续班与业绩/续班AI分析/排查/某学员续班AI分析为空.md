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

### 5. 上游圈选条件（决定性，需 `consultant_assistant` 库只读权限）
```sql
SELECT type,user_number,email_prefix,status,update_time
FROM consultant_assistant.assistant_analyze_select_condition
WHERE user_number IN (<学员id>,<同班对照学员id>) AND type IN (21,22,23,30)
ORDER BY user_number,type;
```
续班类型：21=用户画像、22=沟通摘要、23=沟通建议评分、30=续班特征提取；`status` 0=生效/1=失效。
- **对照学员有、目标学员 0 条 → 该学员的续班圈选条件从未发给上游**，上游无东西可分析（本例即此）。发送方 = student-data `AdsRenewalAiGrayRealtimeSendSelectConsumer`：**学员入班事件**（topic `student-data_ads_large_clazz_user_ordered_prod`，tag `clazz_user_tag`）触发，闸 = `renewal.ai.gray.sync.assistant.switch`(true) + 事件里**老师主岗部门**命中 `renewal.ai.gray.sync.assistant.department.list`；不命中则 `log "...assistant not in gray department, skip"` 直接不发。
- 有圈选条件却仍无分析 → 查 `consultant_assistant.assistant_call_data`（时长 ≥ `callDurationMin`、时间窗）与 `assistant_ai_analyze_result`（是否分析成功/回传）。

**补发（修复缺条件）** —— student-data 提供 4 个补发接口（定义 `AiCommExtInfoClient`，实现 `AiCommExtInfoController`）。本地留档如下（原文见飞书《续班 AI 圈选条件重新发送接口说明》 https://gaotuedu.feishu.cn/docx/RmnXdVRfaoJm3VxUBe4c1wvznEh ，若失效以本节为准）。

> ⚠️ **4 个接口都不做参数校验**：漏传必填字段也返回成功，但实际什么都不发（下"必填"指按代码逻辑不传就不生效，接口不报错）。
> ⚠️ `/feign/aiComm/app/retry`、`/feign/aiComm/app/retry/clazz` 是**重跑 AI 应用（画像/摘要分析）**，**不是**重发圈选条件。

| 场景 | 接口 | 说明 |
|---|---|---|
| 补单个学员（推荐） | `POST /feign/aiComm/select/realtime` | 与线上 MQ 实时入口同一套逻辑，**同步**执行 |
| 补单个学员、不知道班级 | `POST /feign/aiComm/select/history` | 自动取学员最近进的大班辅导班，**同步**执行 |
| 按班级/辅导班批量补 | `POST /feign/aiComm/select/history/clazz` | 逐个学员走历史圈选，**异步**执行 |
| 按历史回溯表重跑 | `POST /feign/aiComm/select/byIdRange` | 按 `ai_renewal_comm_select_history` 主键区间重发，**异步**执行 |

**① `select/realtime`（推荐）** — 同步；走灰度部门/班级排除/学员排除。场景码读 Apollo `renewal.ai.select.scene.list`。
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `userId` | Long | 是 | 学员 ID，查其所有在班(status=1)大班辅导班 |
| `clazzNumber` | Long | 是 | 班级号，查班级/课程→灰度部门/各项过滤/班级排除；不传则查不到班级、直接跳过 |
| `subClazzNumber` | Long | 是 | 辅导班号，取进班时间作圈选开始时间；不传/传错不报错，但开始时间退化成当前时间、窗口不对 |
```json
{"userId": 7406856331, "clazzNumber": 547712569694074880, "subClazzNumber": 34291384908382592}
```
> 该接口**不走**按老师的灰度闸（`renewal.ai.gray.sync.assistant.switch` / `...department.list`，那只在 MQ 消费者 `AdsRenewalAiGrayRealtimeSendSelectConsumer` 里判）→ 手动补发能补上被"老师灰度"挡掉的学员。

**② `select/history`（不知道班级）** — 同步；走灰度部门/学员排除，**不看**班级排除。窗口：开始固定取 Apollo `renewal.ai.sync.history.beginTime`（与进班时间无关），结束取在读大班最晚结班时间；学员 status 1/2 的大班辅导班先过班级过滤、再取进班最晚者判灰度部门；场景码读 `renewal.ai.select.scene.history.list`。
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `userId` | Long | 是 | 学员 ID，不用传班级 |
```json
{"userId": 7406856331}
```

**③ `select/history/clazz`（按班/辅导班批量）** — 异步，立刻返回；按辅导班拉全部学员逐个走历史圈选，间隔 `renewal.ai.sync.history.select.send.interval.ms`（prod 10ms）串行。**班级排除名单不生效**（只在实时接口生效）。
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `subClazzNumberList` | List<Long> | 二选一 | 辅导班号列表；与 `clazzNumberList` 都传时只认这个 |
| `clazzNumberList` | List<Long> | 二选一 | 班级号列表，展开成班级下所有辅导班，覆盖面大 |
> 两个都不传 → 接口啥也不做。
```json
{"subClazzNumberList": [34291384908382592]}
```

**④ `select/byIdRange`（按历史表重跑）** — 先同步查 `ees_data.ai_renewal_comm_select_history`，查到后异步逐个走历史圈选，每发完一个把该学员圈选状态更新为 1。
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `startId` | Long | 是 | 主键起点，含（`id >= startId`） |
| `endId` | Long | 是 | 主键终点，含（`id <= endId`） |
> 任一为空或 `startId > endId` → 查询为空、只打一条 info、接口仍返回成功。
```json
{"startId": 1000, "endId": 2000}
```

**发送后怎么确认**：① SLS 搜 `AiCommOnsMqProducer and <userId>` 确认圈选消息已发；② 批量进度搜 `selectAiCommHistoryBySubClazzNumber success|error`；③ 没发出搜 `RenewalAiJudgeNeedHandleService rejected by` 看是否被灰度部门/过滤挡住，或找同班对照学员比对。

**用到的 Apollo（student-data，PROD，2026-10-13 核对）**：`renewal.ai.select.scene.list`=`21,22,23,30`、`renewal.ai.select.scene.history.list`=`21,22,23,30`、`renewal.ai.sync.history.beginTime`=`1777564800000`(2026-05-01)、`renewal.ai.sync.history.select.send.interval.ms`=`10`、`renewal.ai.sync.course.department.list`=7 个部门 ID（为空则整链路不发）、`renewal.ai.sync.clazz.exclude.list`/`renewal.ai.sync.user.exclude.list`=未配置、`renewal.ai.sync.dirtyJoinTimeBeforeDays`=未配置(默认 60)、`renewal.ai.select.dept.config`=`{}`(默认：开始时间=进班时间-30天、电话/微信电话/微信聊天都纳入、通话≥60s、微信回复≥5次)、`ai.comm.select.topic`=`ai_analyze_select_call_data_prod`。

### 6. 批量找"该有分析却没有圈选条件"的学员 + 根因（老师灰度 skip 日志）
实时圈选的**老师主岗部门灰度**是自动发送的闸：老师主岗部门不在 `renewal.ai.gray.sync.assistant.department.list`（prod 5 个部门）里、或事件 tag 为空 `-` → 该学员入班事件被 skip → 无续班圈选条件 → 无分析。**这是灰度设计，不是 bug**（课程部门白名单有 7 个，老师灰度只有 5 个，两套口径不一致）。

**批量捞（SLS）**：搜 `"assistant not in gray department"`（近 10 天实测有量），日志里带 `largeClazzEnterEntity(subclazzNumber=…, assistantMainPostTag=…, userId=X, clazzNumber=Y, …)`，命中即受影响学员/班级。
- 示例 2026-10-04~14：100 条里 **37 个学员 / 90 个班级**被 skip；tag 多为 `-` 或精品班学部下的子部门，均不含那 5 个灰度部门。
- 捞到后对这些学员走第 5 步补发接口。

**防复发（怎么扩 + Apollo 联动）**：实时圈选的**老师主岗部门**在两个 app 各配一份、同源，必须同步：
| 控制点 | app / key | 作用 |
|---|---|---|
| 自动实时圈选发送（学员会不会自动有分析） | student-data `renewal.ai.gray.sync.assistant.switch` + `renewal.ai.gray.sync.assistant.department.list` | 入班事件里**带班老师主岗部门**命中才发 |
| 老师端续班AI入口可见 | student-center `ai.gray.merge.map` → `renewal.grayDeptList` | 登录老师部门命中(+二讲标签216)才显示入口 |

- 两个 key 用**同一套组织架构部门号**（97xxx 那套），扩名单要**两处一起加同一个号**再各自发布，否则"入口能看到却没分析/反之"。prod 现状已漂移：student-center 比 student-data 多一个 `115518527455104020`。
- ⚠️ 别与**课程部门白名单**混：`renewal.ai.sync.course.department.list`（student-data 与 student-center 各一份、值相同）=`10013518,10019477,10019479,10014349,10016655,10021063,30001264`，用的是**另一套 ID（课程主数据部门号）**，是第二道按班级/课程的闸（各学部专项 `…special.list.*`=10013429/10013431/10012667/10019475…）。"看着在范围却没分析" = 课程部门过了、老师主岗部门没过。

## 会被过滤掉的常见原因（逐条排除）

1. **老师角色不匹配**：通话老师 account 必须 = 该学员辅导班的**带班老师**（`assistant_account_id`）或该订单的**业绩归属人**；客户角色/顾问角色不同判定分支不同。
2. **时间窗外**：实时圈选开始时间 = 该学员在该辅导班的 `joinClazzTime` 往前推 N 天（部门配置 `beforeDays`），且 ≥ 当前时间往前 `renewal.ai.sync.dirtyJoinTimeBeforeDays` 天；结束时间 = 班级 endTime。入班前的通话不分析。
3. **部门/课程灰度**：`renewal.ai.sync.course.department.list` 命中的部门、且 `needHandle`（系列课 `courseTypeIncludeList`、排除 `courseTagExcludeList`、班级名/学季/专项过滤）通过；同班对照学员有数据即说明班级层面通过。
4. **圈选通话类型/时长**：部门配置 `renewal.ai.select.dept.config` 的 `callTypeList` / `callDurationMin` / `wechatChatUserReplyMin`。
5. **排除名单**：`renewal.ai.sync.clazz.exclude.list` / `renewal.ai.sync.user.exclude.list`。
6. **上游平台没产出**：平台没抓到该学员沟通、或 ASR/对话失败 → 无 `AnalyzeResultMsg`，base/scene 永远为空（此时 student-data 侧 extInfo 是 true，需转上游平台查该 userId 的沟通任务/圈选记录）。**最常见的是"没有续班圈选条件"（见第 5 步）**——入班事件没到/被跳过，或回溯圈选没覆盖该学员。

配置在 student-data Apollo（`renewal.ai.*`），key 清单见 `RenewalAiCommSceneConfigService`。

## 验证

- 结论成立：`ai_renewal_cdp_user_comm_base` 对目标学员 0 行、对照学员有行，且 extInfo 回放返回 needAnalysis=true（→ 断点在上游）。
- 常见"成功信号"不算业务生效：接口 HTTP 200、返回 `{}`（就是空态本身）、`ai_app_clazz_user_scene` 有旧 `create_time` 但 `update_time` 很老。
- 若输入表有行但结果表没有：看 `renewal.ai.analyze.realtime.enable` 是否开启、AI 基座异步任务是否成功回写。
