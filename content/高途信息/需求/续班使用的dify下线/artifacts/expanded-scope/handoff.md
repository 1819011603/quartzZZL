# 扩大验证交接（2026-11-23，80%上下文收束）

## 当前目标
用户已扩大到其他迁移场景，必须核对LiteLLM实收提示词/参数具体差异与迁移风险；不能再用两例成功收尾。生产只读，测试可执行，禁止对外联系。未完成且不应标整体等价。

## 已有可复用运行成果
迁移版本91012878，test-gtbg-dev-1，Pod student-data-86c8f5db5d-cpwj9/10.218.238.186，流水线1360042已成功且UP。旧流水线1359971无须再操作。
两例原compare trace：续班15760243-f225-4246-a103-c9565c2652ba.0.3、退费a32fe4b6-6269-4882-8d39-81c76f8ca23e.0.3。Dify下游PROD/SLS/app；迁移下游TEST/SLS/app，service=litellm Chat_completion request。提示词/响应在artifacts/trace-recheck-20261123。
TEST仅agent255107338300556288的params补thinking.disabled，已发布回读，其余agent未动。复验f059219f-2d7c-46c5-945e-fd3a9cdab509.0.3请求disabled，响应stop/无reasoning，reasoning_tokens=null。无业务代码改动/生产写入。

## 本轮实做
- 只读查PROD模块/触发开关：部门模块map均{}，代码语义全放开；renewal.ai.analyze.realtime.enable=true、scheduled.tn.enable=false，仅关闭T+N不能当应用下线。refund.predict.change.switch/async.switch/task-fast.switch=true；fuwu.refund.reason.realtime.switch未配，该字段在所查类仅声明，不能据默认false判业务关闭。证据artifacts/expanded-scope/*enable.txt。
- TEST实际查询ai_application与ai_agent确认10个迁移应用映射存在；6个退费gateway_core_prompt非空。使用python3 ~/.claude/skills/mysql-query/scripts/query_via_apollo.py student-data TEST jdbc.ees.dataSource '<SELECT>'，生产别直连。
- 归档学部提示词比对：根因/旅程/体验两学部同文；NPS473 vs321字不同；降退费工作流1410 vs1412字不同。diff在artifacts/expanded-scope/。这是归档快照，不等于当前Dify配置已全量查过。
- 已完成独立审查见expanded-diff/report.md：续班拆出flat后system466/user1493字逐字一致，实际角色由单user变system+user；退费组合system3280→3272字，旧标签去除、长指令及输出约束提升至真实system。逐行diff/参数表均保存。
- 两例响应存在共有风险：续班两侧写多个用户，违背提示词；退费无分类清单的弱样本旧category=1-1、新=1-11，不能算业务枚举通过。不能归因迁移，也不能继续称整体质量通过。

## 当前续接状态（本轮更新）

- 画像/摘要thinking.disabled已有复验；分层已修response_format=text及thinking.disabled，最终releaseKey 20261123193207-188aa6ecfba69670，trace 7a05052d-9094-4a00-aa88-bf44dcf0eb61.0.3。详见expanded-renewal/tier-fix.md、thinking-followup.md。没有代码提交/生产修改。
- SOP普通compare和真实V2旧模型均Seed-1.6，两侧都有reasoning，不改thinking。原report“旧路均1.5”已纠正。V2 13647字符单user逐字一致，10项SOP；不覆盖generate外围业务，详见sop-real-entry.md。
- PROD DMS SHOW COLUMNS查gateway_core_prompt返回0行，发布前必须加列，本次生产只读。证据prod-ddl-check.txt。
- README/tasks/verify已纠正整体无损与旧部署结论，覆盖/实践见coverage.md。归档审计无ERROR，仍有篇幅/长行WARN。

## 在途与剩余

- W1-d759ca：继续退费5场景LiteLLM实收。已由messageId找回trace并保存TEST llm-full日志；c9335c5b恰100条需聚焦查询避免截断。继续查PROD旧侧全部轮次/tools/tool_calls及学部NPS变体，不以answer工具措辞断言执行。勿重复成功业务调用。
- W1-073b38：续班学部变体核对，当前配置/模板对照与TEST代表边界；此前SOP与分层验证无需重做。
- W1-d5f701：已完成thinking后续修正，无在途写操作。可复用但勿重派既有检查。

三项原子任务已合流，逐场景裁决与风险文档已收敛。不能标整体对等；应按当前prompt交接中的场景结论引用证据。

## 最新增量（继续前优先采用）

退费精确日志报告为expanded-refund/report-exact.md：仅降退费81e两轮dataset工具，旅程无tools。旧报告错误已纠正；五场景完整旧请求均已取得，不再有“旧请求日志缺失”阻塞。旅程有新增resolvedRefundReasonList要求，正在核实历史归属。

原在途任务均已交付：模板残留已修正并复验；旅程字段归属已确认；知识库保留决定已落实。生产不改。

## 当前合流状态

三个原子任务均已交付，无在途构建/业务请求/写操作。模板修正已完成，见expanded-refund/template-fix.md；dataset已完整取得69分段，Teable直读403。当前完整汇总review-result.md，不能套用上方旧在途状态。所有者已决定本轮保留4个知识库/检索应用的Dify，不建设替代检索；未据此修改路由，未将迁移标为生产完成。
