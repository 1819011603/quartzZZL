# 素养 NPS 实收补证

2026-11-23，仅复用22:27的TEST副本compare调用；student-data版本91012878、test-gtbg-dev-1。未重跑业务或修改配置代码。

## 已验证

真实共用trace：`8c802dc4-ed69-4533-b63a-3851e20bb83d.0.3`。旧Dify messageId `92f54eec-345e-4e58-829a-dc8504f4bb4c`由Dify聚合日志映射到该trace；新响应messageId `22df5821-d4ed-4856-ac9d-229e04cb1bc4.0.3`对应同trace下LiteLLM响应id（响应原id不含.0.3）。两者均不是应直接检索的trace。

旧侧LiteLLM请求22:27:31.985，caller_0167，日志位于prod SLS；新侧22:27:57.809，gps-ai，位于test SLS。prod是共享Dify/LLM日志归属，不表示本轮调用了生产业务应用。

完整messages不相等。两侧真正角色均为system+user；321字主指令旧侧多一个末尾换行。旧user是伪JSON文本，内含system文本“请按要求分析用户数据”和user业务正文；新user为拆包后的业务正文。解析旧包装后业务正文逐字一致（包括末尾四个换行）。旧内嵌通用指令没有进入新messages；不能说所有指令逐字相同，也没有遗漏321字主模板。

这与旧链路把query字符串直接交给Dify、新链路拆解query正文的处理边界一致。差异已明确，本轮不扩展为角色统一修正或输出质量验收。

原始实收：suyang-old-received.json、suyang-new-received.json；机器比对：suyang-received-comparison.json。请求参数另可见旧stream/thinking/model/user与新stop/max_tokens/model不同；不将messages核对等同全参数或模型路由等价。

仅覆盖此TEST副本样本，不代表素养全量生产输入。此前suyang-nps-copy-validation.md的“日志未命中”是历史状态，现由本补证更新。
