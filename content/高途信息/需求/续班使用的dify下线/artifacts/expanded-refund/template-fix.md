# 两应用TEST模板修正
代码91012878，test-gtbg-dev-1；仅修改ees_data.ai_application两行gateway_core_prompt。
255743654696597504降退费服务建议、261424322528162816素养服务建议：仅将{{#sys.query#}}替换为“请使用本次 user 消息中的输入信息。”，无动态输入固化，其他指令未改。保存template-before.json；按原值BINARY条件更新，两行各影响1行并commit，再独立只读连接查询，见template-readback.json。
旧素养system内模板已由Dify展开为完整flat输入；新路已经独立user承载同一业务正文，故指向user保留输入语义。降退费旧有独立user，新增提示也仅指向已有正文。
首次误用目录input.json，与旧实收文字不完全一致，不计同输入验收。最终重新使用exact-降退费-test-1.json的完整user去掉生成器追加的两个换行作为query；以下最终两例逐字段断言user相等。

降退费服务建议：trace=25046ce3-eb13-43e3-88ae-78859fd34e33.0.3；双路清理后合法JSON，包含suggestion/recallSuccessRate/recallReason。TEST LiteLLM实收无模板引用、包含新指向说明，user与原实收逐字段相等。

素养服务建议：trace=cd3eed1b-00db-4c9d-bdd4-a4cf7ad22c33.0.3；双路清理后合法JSON，包含suggestion/recallSuccessRate/recallReason。TEST LiteLLM实收无模板引用、包含新指向说明，user与原实收逐字段相等。

证据template-应用名-request.json/headers.txt/response.json/logs.txt/received.json；日志过滤service=litellm的Chat_completion request。

未改Apollo、代码、检索配置或生产。降退费旧两轮检索→新一轮无tools的缺口未解决；模板修正不代表迁移等价。未验证业务事件落库或多次质量统计。