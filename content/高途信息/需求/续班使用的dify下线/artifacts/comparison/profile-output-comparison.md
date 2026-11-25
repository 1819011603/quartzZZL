# 用户画像输出差异

截图左侧为旧LLM content文本（带Markdown JSON围栏），右侧为新执行器返回，业务文本在answer。外层usage/event/messageId不是业务字段。

按消费者规则清理后，两侧均可解析为renewalInterest、renewalResistance、portraitSummary三个非空字符串。但抗性归类有实际差异：旧侧把学习问题列为抗性，新侧仅保留待咨询疑虑，学习问题仍在新portraitSummary。不能直接归因为随机性，也未证明迁移Bug；模型映射及response_format不同也存在，单次样本不能分离原因。

结论：该样本请求对齐、字段格式兼容；输出语义等价未证明。该trace为syncRequestTask直调，无本次MQ消费/业务落库回读。DifyResponse去围栏后，画像消费者按字段原样写appSceneValue，不修正语义归类。

原始输出完整保留，飞书表增加同层归一化JSON比较。此次仅原证据分析和文档修正，未生成、部署或改业务配置。
