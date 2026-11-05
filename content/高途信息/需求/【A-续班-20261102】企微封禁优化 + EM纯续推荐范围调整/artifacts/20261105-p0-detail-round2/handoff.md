# W1 本轮安全交接（任务243aa61a，attempt2）

## 已完成与实际证据

- 沿用统一主需求/两个子项、25项契约、原30条P0、12张卡/36步；上一轮全篇revision146及skill验证不重做。前端分支归属和固定SHA已核，线上映射仍未取得。
- **本轮已补B侧真实班名并写回飞书revision147**，仅回读受影响P0-04小节，见`verification.json`、`b-name-readback.json`。外部URL：https://gaotuedu.feishu.cn/wiki/KeCZwdJTBiIJDJkX8lRcGb9gnCs （docx ZQUXdlDxWoknJhxu914c2uVYnBr）。
- 正确查询位置是 **TEST DMS cluster153 / course_center.clazz**，不是gaotu.clazz。原件`b-class-dms.json`：586090628920764416名“dcg-小班扩科排除-数学-后置”、课程18314034380997186；586097025945298944同名、课程18314034380997207；前置586084334251927552名“dcg-小班扩科排除-数学”、课程18314034380997173。三条展示课期/时段均为空。已明确同名不等于同班，不把“默认规格”当班名；不据此推定排课/可售/页面可见。
- 查询方式：mcpcli mysql_query mysql_query，env=test、cluster_id=153、db_name=course_center，按上述3个number精确SELECT。默认resolve_rw_dsn('course_center')返回None，随后换DMS一次成功；不要重复查gaotu.clazz或把该失败当对象不存在。
- 本地P0-case.md、README.md、links.md同步本次补证。无业务代码、造数、部署、业务写入或对外联系。

## 尚未完成，下一执行者应继续的最小范围

1. **P0-10/11现有对象信息**：定向补班级/学员与可见老师、标签原集合/名称、真实身份/好友/原备注。优先已有对象7489648821/574882679202260992（标签2“需中关注”，name空，源行120542/account90247），7658127801/7658129872及前置班585960582537144320/586084334251927552；现有订单不证明好友，字段空不能编造。只读不能证明无人并发写，独占应写成执行前预约/再次快照条件，而非凭空缺失所有对象信息。复用上一轮`artifacts/20261105-p0-detail/sample-readback.json`等，不重跑全链路。
2. **区分信息不足与尚未执行业务**：没执行可写“没做”，但仍须填完整前置/预期/具体操作。历史HTTP原件无法恢复只限制历史证明，不替代当前对象信息调查，不重放成功写操作补历史证据。
3. **逐项信息缺口表**：写具体卡号/原P0编号、缺字段、查过的入口与结果、是否需造数/写入或人工身份、替代材料能证明什么。现有总缺口在revision146的30条映射和上一轮result.json，不重新全链路调查。
4. **复现程度数量未完成**：尚未最终定义并统计“完整可复现 / 前置准备后可执行 / 信息仍缺失”的数量及编号；不要拿“12卡/30原P0已映射”冒充这些数量。建议同时给12张合并卡和原30条P0两种口径，整卡按其必验子项最弱条件判级，类别不等于业务通过。补完信息后统一回读受影响小节。

## Skill 已完成，直接复用

专用skill为banshan-case。源文件：
- /Users/gaotu/bridge/payload/skills-cold/banshan-case/SKILL.md
- /Users/gaotu/bridge/payload/skills-cold/banshan-case/references/doc-templates.md

安装副本：
- /Users/gaotu/.claude/skills-cold/banshan-case/SKILL.md
- /Users/gaotu/.claude/skills-cold/banshan-case/references/doc-templates.md

上一轮`artifacts/20261105-p0-detail/skill-readback.json`及`skill-final-*.log`证明源/安装一致、语义/链接通过、84条路由0失败；`skill-source-root-audit.log`正确skills根目录审计0错误/0警告。无需再改skill或重跑自检。错误地以skills-cold为审计root产生的25条toolbox误报已纠正，不是25项真实故障。

## 子任务与未结束操作

- 复用子任务 W1-e4187e 承担P0-10/11只读补查，已按所有者收束指令收窄为只读交接并停止，运行时回执status=stopped、result_seq=3；result_path=/Users/gaotu/.local/feishu-bot/logs/managed/subagents/W1-e4187e/result-2.json。
- 其本轮仅回读既有证据/规范，**尚无新增成功业务查询结论可吸收**；不能把“计划查好友/原备注”算已查。回报明确当前没有在途调用。`qiwei-handoff.md`若不存在，以上stopped回报即本轮交接依据；后续同链继续复用此子任务ID，不新建。
- 主Worker无在途命令、文档写入、部署、数据库事务或业务任务；只读连接已结束，文档写入已回读。后续继续仍限只读调查+文档，禁止造数/部署/生产写入/对外联系。
