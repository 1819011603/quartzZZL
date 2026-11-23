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

## 子任务（保留复用，勿重复创建）
- W1-073b38：运行中，负责用户画像-test/服务SOP分析/预测分层原因，双路实收/响应/有效样本，写artifacts/expanded-renewal/。已见trace e3197197-27eb-4b23-8b1e-2f8b83d16ff5.0.3查询进展，尚无最终报告。
- W1-d759ca：运行中，负责退费旅程/体验/NPS/降退费/素养服务建议，写artifacts/expanded-refund/，正执行/tmp/run_refund_compare.py。已要求核对学部变体映射，不得把6个TEST等同生产10个。
- W1-d5f701：完成且可复用，精确两例diff及11文件只读审查。报告已读采用；result=/Users/gaotu/.local/feishu-bot/logs/managed/subagents/W1-d5f701/result-1.json。
子任务不改公共Apollo/代码/README/verify；主Worker负责必要修正与整合。

## 待做与合流点
1. 接收两条运行验证报告，按实际完成/失败/未覆盖逐场景覆盖表；不足有效样本或学部模板差异要定向补，不能空数据算通过。
2. 独立审查风险需核实适用性：extraParams允许stream=true但客户端解析JSON；显式prompt重载不加gatewayCorePrompt；新列DDL无条件依赖；空gatewayCorePrompt回退标签；compare两次动态取数可能不冻结。它们当前是静态风险，修代码前必须真实运行证据。
3. 我已查到RefundReasoningService.java:214调用syncRequestTask(traceToken, command, Maps.newHashMap(), gson.toJson(context))；第四参数是extraInfo，不是显式prompt，勿误判为缺system的重载。需继续核对调用图。
4. 基于场景报告判断具体缺陷再最小改动/同入口复验；保留共有质量风险、不擅自扩大业务规则。
5. 更新README/verify/tasks的当前结论（原文件有多轮互相覆盖的陈旧表述，应收敛），明确可迁/不可直接迁/未覆盖与适用最佳实践。勿将提供商HTTP缺观测用作LiteLLM层不能对比借口。

## 在途操作
无主Worker后台构建或业务请求；两子Agent仍运行且各自管理业务compare/日志。未发停止，不取消其工作。此次按owner上下文80%指令交接，不是任务完成。
