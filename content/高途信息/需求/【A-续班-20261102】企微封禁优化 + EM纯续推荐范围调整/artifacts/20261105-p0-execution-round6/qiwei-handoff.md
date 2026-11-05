# round6 企微 TEST 安全交接

## 结论与停止来源

2026-11-05 17:41（Asia/Shanghai）按父 Worker 最新「运行时80%安全交接」指令收束；这是运行时交接，不是所有者业务暂停，也不撤销 TEST 最小样本准备与对应操作授权。收到后没有新增业务验证/造数，仅退出本轮代课并读取恢复身份。当前无在途操作，无业务标签/备注/好友/DB/ES 写入，无造数 runID、备注 task number 或 MQ。

本轮实质增量：候选 zhangzeling109942 的 EES/OS 代课申请已实际尝试且受理成功；实际 TEST 接口与页面身份仍是 gongxuemeng（177071），不能声称已取得张泽灵身份。真实 Chrome 可用，已打开大班续班服务，能看到「添加标签」「修改企微备注」「学员标签」入口及16行；仅为入口可见证据，尚未执行标签或备注。没有新发现必须 owner 提供的确认阻塞。

## 当前版本/环境及成功证据

- 17:36:52 Eureka：固定候选 `student-center-5d84df769-gxbql` / `10.255.176.174:28688` / metadata.trafficEnv=`test` / UP。`qiwei-instances.json`。
- 17:40:06 青舟 TEST Pod 回读：上述实例镜像 `release-5dce9cdb-20261103201632`，Running/UP；同名默认 TEST 另有 `10.218.238.176`、`feature-regular-course-query-df66fed8-20261102114739`，不能把网关响应都指定到固定5dce9实例。`qiwei-pods.json`。本轮未查到 test-gtbg-dev-3 实例（Eureka列表无该泳道），不称目标分支验收。
- 当前本地 student-center HEAD `396d84f07`，本轮只读源码；与历史 worktree `889354d6`、MR1528固定head `7f9bca38`、实际部署版本分开。未改业务代码、skill、外部P0、需求归档或主Worker EM对象。
- 17:36:52 `POST https://test-fuwu.baijia.com/bgwApi/student-center/teacher/current/account/info`，body=`[]`，traffic-env=`test`，b_client=`EES`：HTTP200/code0，弓雪萌的辅导/销售/主讲等老师记录。trace `afd21fd4-d7a2-4cbe-8a46-8897fceee5da.0.3`，`qiwei-identity-before.json`。
- 17:37:14 本轮唯一外部写：`https://sd.baijia.com/suda/cosplay/apply/addNoAudit`，账号 `zhangzeling109942`，项目3/accessPermission2、项目4/accessPermission4，均 code0「添加成功」。`qiwei-cosplay-login.json`。这是已授权全局代课控制操作，不是PROD业务写。
- 17:37:26 同一 TEST teacher/current/account/info 仍返回弓雪萌。trace `f9b3831d-42f9-403d-a0c7-eca5a36d14e4.0.3`，`qiwei-identity-after.json`。申请成功不证明 TEST 身份切换；未继续解释为权限失败。
- Chrome 先连接临时 about:blank，随后 `chrome-devtools start --autoConnect` 成功复用已有真实Chrome。`qiwei-browser-connect.txt`、`qiwei-browser-real-pages.txt`（敏感查询参数已遮盖）。CUA因Sky服务启动失败无surface，已换专用CLI，不是页面无权限。
- 原浏览器 tab34：`https://test-fuwu.baijia.com/crm/cronus/clazzRosterOL`。只读提取业务身份字段为 account177071/name gongxuemeng/displayName弓雪萌/currentRoleTag gaotu_boss_sales_/课程顾问，未读取Cookie/密钥。`qiwei-browser-identity.txt`。
- 点击「续班服务」后 tab34 当前URL `https://test-fuwu.baijia.com/crm/cronus/clazzRosterOL?tabKey=continuationService`。页面带班老师弓雪萌、在读且本人辅导班，已有选择名「续班归因-正经前置班-0820」，16行、均不可续，添加标签/修改备注按钮及学员标签列可见。`qiwei-renewal-loaded.txt`。未选择学员或提交；班名不能独立证明当前页面行的班号（未取得网络原件/展开班号），不把历史ID自动嫁接为本轮页面精确对象。

## 查询结果、失败及边界

原件 `qiwei-db-schema.json`、脚本 `qiwei-db-read.py`，TEST Apollo DSN、只读事务，均rollback并关闭连接。未写库。

- `gaotu.subclazz_student` 索引包含 `idx_clazz_number_subclazz_number(clazz_number,subclazz_number)`、`idx_user_id_clazz_number(user_id,clazz_number)`，具备后续按精确班级/学员读关系的入口；本轮只看字段/索引，未查第三人。
- `ees_data.user_clazz_mark_info` 唯一键仍为 `uq_user_clazz_id(user_id,clazz_number)`，account_id只是写入来源；全字段及索引在原件。本轮未查询/保存新的标签集合。
- `gaotu.user` 字段/索引和三个既有候选读取报1146，原因是当前所连gaotu库没有user表，不是候选不存在。既有 `read-samples.py` 已明确 user 在 `super_class.user`，续接直接复用正确库，不重试错误SQL。
- `gaotu.employee` 查询包含不存在的name字段，报1054，尚未取得109942/177071的该表原件，不称无老师；后续先按真实schema选必要字段。
- 尝试解析 dws_clazz_user TEST DSN，但脚本 `if not dsn: ...;continue` 在落盘前跳过，使最终schema JSON没有该库条目；只能按脚本控制流判断DSN未解析，不能声称查过关系表或无权限/0行。本轮没有重跑历史27分表。下一次修临时脚本最终落盘位置，不能补造响应。
- 误试 `mcpcli.py qingzhou_ops --list` 只得到模块不存在（`qiwei-qz-tools.json`）；已改复用 deploy-image/poll_pods.fetch_groups 只读取Pod，不是部署。

历史可复用对象仍为 round3/4原件：大班585960582537144320（dcg-扩科排除-前置-五年级语文）与学员7658127801/7658129872，同辅导班36622538973250048；小班候选586084334251927552此前接口为空；标签正例7489648821/574882679202260992/account90247/tag2需中关注。它们本轮未重新快照，不称当前可写/独占。已知历史错误班号585960582537144300、id120554完全未动。

## 写入原值与恢复

- 本轮无业务原值变更，无新建用户/班级/订单/关系/标签源行/备注任务，无业务恢复需求。
- 原身份基线：teacher接口返回弓雪萌；浏览器业务缓存177071/gongxuemeng/课程顾问。原代课申请列表未读取，不宣称原全局授权清单已完整快照。
- 17:40:56 调用本轮项目3、4的 `cosplay_logout`，对应 `/suda/cosplay/apply/deleteNoAudit`，两项均 code0「删除成功」。`qiwei-cosplay-logout.json`。
- 17:41:21 必要恢复回读同一TEST teacher/current/account/info：HTTP200/code0，与before教师列表一致，trace `020d8c35-35c3-4a6d-a9e0-528ba2dc7f3a.0.3`，`qiwei-identity-restored.json`。已取消本轮两个项目代课申请、TEST身份基线保持。未声称浏览器重新登录为张泽灵。
- 浏览器保留 tab34 的续班服务页面，已改变查看tab/URL；无弹窗、无选中对象/待提交写表单，无需业务恢复。共享Chrome守护进程继续供其他任务使用，不擅自停止。

## 覆盖映射与尚缺前置

原7条QW：QW-G001、QW-B01-001/002、QW-B02-001/002、QW-B03-001/002，本轮均未新增业务通过。P0-10仅新增大班页面入口可见与当前可用身份事实，P0-11仅新增修改备注入口可见，P0-12未打开规范链接。原30条其余23条未触碰；12卡其余9卡未触碰。不得以入口可见或代课受理替代整卡。

下一会话按有效TEST授权继续：
1. 先检查文件/实例/身份有无变化；不要重放成功代课申请或任何历史写。若仍需109942，查明确的TEST身份切换机制；候选申请已尝试成功但未生效为其身份，现有Gong测试身份实际可用，可按页面权限决定能否使用。
2. 受控同班两目标+一未选对照尚未齐备；第三人可自主复用/最小造数，不列为owner必须提供。现成页面16行未核受控归属，不能随意写真实学员。
3. 写前按真实pair快照标签ID/名称、旧表/ES/默认页及续班页，再执行批量/单人/筛选/清空/取消/恢复。仅业务标签分支不依赖官方好友；临时标签才走官方外部关系，不能混为阻塞。
4. 好友候选源尚未定向扩查到受控TEST身份下可用对象，不能断言全系统无好友。官方备注/临时官方标签仅在同一受控官方老师+真实好友及原备注可恢复时操作；未取到外部联系人不得伪造friend=1或external_userid。
5. 终态入口已静态定位 `/export/list`（JobTaskListRequest），任务实体 `ees_data.batch_operate_task` number/process_status/task_result，子任务export_job_task；`remark/test`和test2是执行/完成写接口，不可误作查询。只查源码，不把该入口当已运行验证。
6. P0-12仅打开/切换/取消规范入口，不发送任何真实消息。继续不改前后端业务代码、不部署、不改外部P0/skill/主WorkerEM。

## 在途与责任

本轮所有exec会话（46685、24884、48524、16635、66851、25357、71879、86984、12407）已结束退出0；无后台数据agent run、无备注task、无数据库未提交事务、无在途网络请求。无待取消操作。当前交接责任交回父Worker；下轮接续人重新核当前范围，不把本次运行时交接当业务授权撤销。
