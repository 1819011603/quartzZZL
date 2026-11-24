# 当前八场景本地证据复核

复核时间：2026-11-24T19:21:35.319728+08:00。仅读取remaining-current-runs现存文件，不调用业务或修改TEST/飞书；四素养样本不在本次范围，未落盘项标待取证。

| 检查项 | 实际结论 |
|---|---|
| 八场景调用结果 | before/after invoke均已落盘；after八项rvoCode=0 |
| 入口结构 | 七项AiApplicationExecutor#syncRequestTask；SOP V2为syncRequestTaskV2。是ACL直调执行器，不是原业务前台入口全链路 |
| RunUser来源 | 八项invoke均显式传入gongxuemeng@gaotu.cn；可证明传入身份路径，不能单凭这些文件证明原业务入口自动从当前老师提取身份 |
| 完整body实收 | 八项received.json逐个解析，与同目录sls.txt的LiteLLM Chat_completion request JSON完全相等；充分采用 |
| 参数实收 | 八项stream=true、无max_tokens、无thinking；response_format按场景保留。不是仅Apollo配置推断 |
| model保持 | 前后Apollo九个agent键集合一致、model全部相同；本次七个目标agent参数改变，未更换模型 |
| 费用头 | after-watch有八个gongxuemeng及八个body，但未保存watch表达式/字段名/trace。现存文件不能独立严格证明该值为指定费用头且逐trace关联；待取证，不判业务失败 |
| 运行版本 | watch标识student-data-5f688c5bfb-xgx76、dev；invoke指test-gtbg-dev-1。目录内不足以独立绑定student-data镜像commit；不能仅按任务描述追认版本 |

## 八场景适用范围

画像、摘要、SOP V2、高中分层（目录名分层修正后）、精品退费根因、旅程、课程体验、NPS均有上述完整body与成功响应。后三个使用显式构造业务query；根因是短合成样本且context为空；不要写成全部是生产真实业务入口回放。summary.json的messages_equal=true可以作为已有作者断言，但本次目录未含旧链路基线及逐项比较来源，不能独立复算“旧Dify messages完全相同”。本次前后均为新链路，参数修正前后相同不等于新旧链路相同。

## 最小补证

1. 为费用头保留实际watch命令/表达式（明确读取哪个header）及可与对应body/trace关联的证据；不用重跑已充分的body验证。
2. 若要宣称原业务入口自动身份提取，补入口来源或既有源码/日志链；当前只能宣称显式RunUser透传路径。
3. 若要宣称当前commit逐场景通过，引用现有Pod→镜像commit证据；若要宣称新旧messages相等，指向旧基线文件和比较依据。均可复用已有证据，不要求重复业务调用。

注意after-watch包含21个U+FFFD替换字符，只有画像、摘要、旅程body与received精确相等；其它watch文本不适合逐字断言。应使用已验证完整的LiteLLM实收sls/received作为body证据，不把乱码误判为实际请求内容损坏。
