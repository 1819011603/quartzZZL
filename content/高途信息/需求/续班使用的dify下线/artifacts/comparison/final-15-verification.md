# 15场景最终验收检查点

范围13非知识库＋2降退费workflow，排除两个403问题建议。当前代码/TEST部署47b3dcb7；普通链路有效历史证据复用，不声称15项最新版本全量重跑。当前尚未全部收束，见final-15-verification.json。

|本轮必补项|结论|证据|
|---|---|---|
|素养分层旧完整HTTP|已取得，messages全等，stream=true，max_tokens/thinking省略；model按映射比对，新response_format=text为已确认差异|final-15-evidence/suyang-tier-old-http.json及http-comparison.json；旧trace71b44f24-f24a-45f5-8200-d63615400d9b.0.3|
|精品旅程正式当前模板独立对照|已独立复制正式2482字模板、通用core、空后处理；旧新完整messages及参数全等，system实收2483字|final-15-evidence/精品旅程/；旧ff9508f8，新1ae3e73d|
|素养NPS新完整HTTP索引|已从原trace取得，stream=true、thinking.enabled、无max_tokens|final-15-evidence/suyang-nps-new-http.json；acc2dcbd-8623-4081-9d9b-248fb93df2ef.0.3|
|真正SOP自动老师→发送头|已同次验证，非人工RunUser：AiSopAnalysisGenerator.generate→SubClazzHelper返回gongxuemeng@gaotu.cn→jsonPost头gongxuemeng；同trace及body SHA256|sop-auto-invoke.json、sop-auto-helper-watch.txt、sop-auto-header-watch.txt，trace d7043e0b-db14-4cca-bb6a-8cf3e91e8e03.0.3|
|SOP结果落库|新增TEST档案7530633600362874200，生成后结果3785字、刷新时间2026-11-25 10:06:43|sop-result-readback.json|

## 安全交接

用户上下文80%指令要求停止扩展，本轮到安全步骤收束。无业务阻塞，不新增权限要求。当前无在途进程；Arthas reset两类并--stop完成，watch-cleanup.txt。没有代码修改、提交或部署，worktree仍47b3dcb7。TEST新增精品旅程应用7530633600362874100，复用素养旅程独立agent参数；消息格式Apollo发布20261125100013-188aa6ecfba6976e并回读，不能重复创建。旧Dify TEST app spcynF7tYh4ROXnG8Xg_09fa590a-c1cb-40df-bc06-a826632b17b1；密钥保留.codex/private/dify-dataset-migration/精品旅程-final-key.json，0600，不入报告正文。原生产只读获取配置，没有生产生成/配置写入。

## 剩余有限事项

1. 退款业务路径自动身份同次关联：真实入口RefundReasoningService.refundReasoningEvent。queryRunUser私有方法按subclazz→assistantNumber→teacher.baseInfo.email；不能用人工命令替代。当前尚未为其选择真实可用TEST事件，上下文/班级/订单/时间窗口/模块开关应按既有数据找到可用样本，不扩大为全场景重跑。
2. 两workflow费用头证据优先复用，若需代表性自动身份补证，沿用同次ASCII trace+header+body SHA方式，不追下游计费。
3. 将final-15-gap-matrix.json中的15项路径统一到最终机器矩阵，补本轮覆盖，逐一核验文件存在、旧新完整HTTP与输出。当前final-15-verification.json是缺口闭合检查点，还不是15行最终矩阵。
4. 本轮SOP同次完整HTTP尚未再次检索，现已有调用/Helper/header/body SHA及结果落库足以证明身份；若需body对齐，使用原trace只读查日志，不重跑generate。

可复用脚本/tmp/final_journey_setup.py（有创建幂等但不要无故重发配置）、final_journey_run.py（不幂等，不重跑）、final_journey_collect.py、final_sop_auto.py（不重跑）。旧证据大日志/tmp/final-tier-enduser-test.txt、/tmp/final-nps-new-http-log.txt已抽出安全完整HTTP入归档。新旧相同输入和输出在各invoke/request/response中。

主Worker负责README和飞书，本子任务未改。两个403问题建议不再调查。
