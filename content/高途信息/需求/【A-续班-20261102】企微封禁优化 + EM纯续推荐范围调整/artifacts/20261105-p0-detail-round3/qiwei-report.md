# P0-10/11 标签与备注只读交接（round3）

采样范围：复用已有 TEST 只读原件，未发起新业务查询；本轮没有写接口、造数、数据库写入、外部文档或 skill 修改。B 侧三个 course_center 班名沿用主 Worker 已确认的 `/tmp/w1-p0-243aa61a/round2/b-class-dms.json`，本报告不重复查询。

## 已确认的真实对象

### P0-10 标签读取正例（已验证子集）

- 环境/实例：TEST 默认泳道；`student-center-5d84df769-gxbql:student-center:28688:@default`，`10.255.176.174:28688`，镜像 `release-5dce9cdb-20261103201632`，Running/UP。目标泳道 `test-gtbg-dev-3` 当时没有 student-center 实例，因此该结果只属于默认 TEST 等效读取。
- 班级：`574882679202260992`，名称 `续班归因-正经前置班-0820`；辅导班/子班号 `35930168009949440`。
- 学员：`7489648821`；数据库 `name` 为空，必须按 ID 定位，不能补姓名。已有 `grade=13`、`user_status=0` 仅是用户表字段，不替代班级/页面身份。
- 标签原值：`ees_data.user_clazz_mark_info` 行 `id=120542`，`user_id=7489648821`，`clazz_number=574882679202260992`，`account_id=90247`，`tags='2'`，采样时间见 `tag-baseline.txt`/`sample-readback.json`。
- 标签名称：真实调用 `RenewalService#getStudentRenewalInfosByUserIds` 返回 `studentTags=[2]`、`studentTagNames=["需中关注"]`，返回班号、子班号、学员 ID 一致；trace `student-center.900338.17938614686501583`。
- 证据原件：`/tmp/w1-e9aebdb9/tag-known-positive-default.txt`、`/tmp/w1-e9aebdb9/tag-baseline.txt`、`/tmp/w1-p0-243aa61a/sample-readback.json`、`/tmp/w1-e9aebdb9/student-center-pods-detail.json`。这只证明该样本的服务层读取与 DB 标签值一致，不证明批量保存、单人编辑、刷新、筛选、ES 或页面权限。

### 共享学员历史标签行（不可作为可复跑正例）

- 已读到 `user_id=7658127801` 的 `user_clazz_mark_info` 行 `id=120554`，实际 `clazz_number=585960582537144300`（不是此前误列的 `585960582537144320`），`account_id=109942`。历史快照先见 `tags='1,2'`，后续采样已变为空串，`update_time=2026-11-05 14:43:16`。
- 正确班号当前无对应行；没有写前快照，也没有原始写请求/trace，不能判定谁创建、谁清理或是否发生精度丢失。本任务未删除、恢复或改写该共享行。
- `7658127801` 的姓名/页面可见身份、完整原标签名称集合、好友关系和原备注没有同一份可信原件。不能用该行承担 P0-11 的成功备注样本。

### 另一个候选学员

- 既有归档记载 `7658129872` 页面/用户姓名为“续班扩科隔离测试”，但本轮没有对应标签原集合、可见老师身份、好友关系或备注原值的独立只读原件；只能作为待准备候选，不作为已验证对象。
- 相关 B 侧班级 ID/名称由主 Worker 已从 TEST `course_center.clazz` 精确读回，见 `/tmp/w1-p0-243aa61a/round2/b-class-dms.json`；班名查询不证明可售性、页面可用性或企微好友关系。

## P0-11 备注/好友前置

- 网关只读好友校验：`POST /bgwApi/student-center/remark/check/wk/friend`，`traffic-env=test-gtbg-dev-3`、`b_client=EES`、`userIds=["7658127801"]`，HTTP 200/code 0、`resultStatus=false`，trace `6aa83947-e018-4df1-86e1-ff5b8efa5091.0.3`，原件 `/tmp/w1-e9aebdb9/qiwei-friend-trace.txt`。这只说明该登录请求未通过好友前置；具体后端实例、真实身份、备注值和封禁状态均未证实。
- 默认 TEST 固定 IP 直连同类 endpoint 返回 HTTP 200 但 code 3“登陆信息获取异常”，trace `student-center.900339.17938614405711575`，原件 `/tmp/w1-e9aebdb9/friend-default-direct.txt`。HTTP 200 不算备注成功，也不能绕过鉴权。
- 没有成功好友样本、正常/封禁账号对照、可见老师账号/角色、原备注值或备注写后读回。P0-11 仍需人工提供有权限的 TEST 老师身份与已核验企微好友；写前还需独占预约和再次快照，独占性不能由当前 DB 只读证明。

## MR1528 静态结论与 P0-10 纠正建议

owner 提供的 `student-center!1528`、`feature-weixin-opt`、commit `7f9bca38` 静态核对结论已另存 `/tmp/w1-p0-243aa61a/round3/qiwei-mr1528-note.json`：只涉及标签回溯/空标签处理，未涉及好友或备注 API。结合现有 `user_clazz_mark_info` 行字段与 MR 说明，P0-10 的对象定位应写成：

- **业务定位键是二元组**：`(user_id, clazz_number)`；`account_id` 写为操作来源/审计上下文，用于说明谁产生或操作该标签记录，不把它写成第三个业务隔离键。现有行 `id=120542` 的 `account_id=90247` 不能证明账号维度隔离；行 `id=120554` 的不同班号也不能证明好友或页面权限。
- 该结论只覆盖 MR 静态说明与已读 schema/行字段；未取得 DAO 源码片段或运行写入证据，不把“唯一键”扩展为未核实的数据库约束名称。执行卡应同时记录用户 ID、班级 ID/名称，并单列操作账号/角色字段。
- **清空边界必须明确**：清空标签后，返回的标签 ID 集合为空、标签名称集合也为空；原来按该标签筛选的学员不再命中。该边界尚未通过本轮运行写入/筛选实测。
- “只选择临时标签而不清除原业务标签集合”的行为没有在现有代码/运行原件中核实；不要仅凭 MR 文字写成规则。若后续要纳入，需先取得既有代码判定和真实运行证据。

## P0-10/11 分类与缺口

| 子场景 | 分类 | 目前能证明什么 | 仍缺什么 |
|---|---|---|---|
| P0-10 标签读取：7489648821 / 574882679202260992 | 已验证子集 | 真实班、学员 ID、标签 ID/名称、DB 行和服务读取一致 | 全量标签集合、未选人对照、写/幂等/恢复、页面权限/筛选/ES、独占性 |
| P0-10 标签写/清空边界 | 前置准备后可执行 | MR 静态方向和清空后的断言已明确 | 独占 TEST 对象、写前快照、真实写鉴权、DB/ES/列表回读；当前未执行 |
| P0-10 候选 7658127801 / 7658129872 | 信息仍缺失 | 可定位候选 ID；7658127801 错误班号历史行已标明风险，7658129872 有归档姓名线索 | 正确班级关系、可见身份、标签原集合/名称、页面权限和稳定班样本 |
| P0-11 好友成功及备注 | 前置准备后可执行 | 网关好友校验 false 和默认直连 code3 的失败边界 | 有权限老师账号/角色、真实好友成功样本、正常/封禁对照、原备注和写后读回 |
| P0-11 非好友/鉴权失败 | 已验证阻塞子集 | resultStatus=false 或 code3 的实际返回及 trace | 不能把它升级为“备注失败规则”或“账号封禁”结论 |

## 未覆盖与当前操作状态

- 未查到可公开确认的真实老师账号/角色、企微好友关系、好友成功样本、原备注值；没有把 `account_id` 当作老师登录身份。
- 未执行浏览器页面、标签保存/清空/筛选、备注写入、ES 读回、好友关系建立、恢复或独占预约。
- 未调用任何保存/备注任务；本轮无在途查询、写操作、部署或持久会话。
- 所有结论均为已验证子集、前置准备后可执行或信息仍缺失，不代表 P0-10/11 整卡通过。

## 增量补证：候选标签与老师/企微关系（只读）

**查询时点**：见 `qiwei-source-evidence.json` 的 `query_time_utc`（UTC）。环境统一为 TEST，调用 `/Users/gaotu/.local/mcp-servers/mcpcli.py`（venv Python），没有调用写工具。

### 候选标签精确查询

- 数据库/表：`ees_data.user_clazz_mark_info`。
- 实际 SQL：
  `SELECT id,user_id,clazz_number,account_id,color,layer,tags,create_time,update_time FROM ees_data.user_clazz_mark_info WHERE user_id IN (7658127801,7658129872) AND clazz_number IN (585960582537144320,586084334251927552)`。
- 过滤候选：学员 `7658127801`、`7658129872`；正确班号 `585960582537144320`、`586084334251927552`。
- 实际结果：`0 rows`，原始回执 `/tmp/w1-p0-243aa61a/round3/qiwei-mark-candidates.json`。先查索引确认 `uq_user_clazz_id` 的两列顺序为 `user_id` seq1、`clazz_number` seq2，另有主键 `id`；索引回执同本轮查询记录。
- 解释边界：查无源标签记录只说明查询时这两组精确 user/class pair 没有 `user_clazz_mark_info` 行；**不等于 ES/页面显示为空标签**，也不等于标签筛选已验证为空。

### 老师/企微关系精确查询

- 数据库/表：`dws_clazz_user.dws_fuwu_user_teacher_wechat_info_0` 至 `_26`，共 27 个分表。
- 每分表实际 SQL 模板：
  `SELECT id,user_wechat_id,account_wechat_id,user_id,account_id,friend,intimate_nickname,wechat_remark,wechat_type,create_time,update_time FROM dws_clazz_user.dws_fuwu_user_teacher_wechat_info_<shard> WHERE user_id IN (7658127801,7658129872)`。
- 候选过滤只按两个 `user_id` 精确查；没有取手机号或密钥。原始逐分表回执 `/tmp/w1-p0-243aa61a/round3/qiwei-wechat-shards.json`：shard `0..26` 每个 `exit=0`，响应均为 `[]`、`total_count=0`，无异常分表。
- `_0` 表结构已读，包含 `user_id`、`account_id`、`friend`、`intimate_nickname`、`wechat_remark`、`wechat_type`、时间字段；`friend=0` 表示非好友、`friend=1` 表示好友，`wechat_type=2` 表示企业微信。源码 DAO 同时按当前登录 `account_id`、候选 `user_id`、好友状态和企业微信类型过滤，见 `qiwei-source-evidence.json` 的源码路径/行号。
- 解释边界：27 分表查无候选关系只表示这些 user_id 在当前 TEST 源表快照下没有匹配关系行；**不等于系统没有其他账号的好友关系**，也不等于当前登录人的好友结果已通过；没有关系行不能猜原备注为空，`wechat_remark` 仍是未知。

### DAO / schema 口径补充

本地只读源码当前为 `feature-xuban-20261001@889354d6715f7ab31be44533313232233c3fea99`，不是 MR1528 fixed head `7f9bca38`，不冒充线上 MR 版本。旧 HEAD 的 `UserClazzMarkInfoMapper.xml` 对标签 upsert 使用 `(user_id, clazz_number, account_id, tags)`，`ON DUPLICATE KEY UPDATE tags=values(tags)`，pair 查询使用 `(user_id = ? AND clazz_number = ?)`；`account_id` 是写入字段/员工来源，不是第三个业务键。`WechatRelationServiceImpl`/DAO 则按当前登录 `account_id + user_id + friend + wechat_type` 查企业微信好友，不能由空结果推出备注或封禁结论。

## 增量后的 P0 分类调整

- P0-10：两个候选 pair 当前**无源标签行**，可作为“无 DB 标签记录”的数据前置结果；仍不能称页面/ES 空标签，清空后 ID 集合与名称集合都空、原筛选不命中仍需真实写后回读验证。
- P0-11：两个候选在 27 个分表均无老师/企微关系源行；分类仍为“信息仍缺失/前置准备后可执行”，不把该结果写成无好友全局结论。尚缺真实老师账号/角色、账号上下文下的好友成功样本、原备注和写后读回。
- 本轮没有取得原备注值；不得把 `0 rows` 或此前好友 `resultStatus=false` 改写成“原备注为空”。
