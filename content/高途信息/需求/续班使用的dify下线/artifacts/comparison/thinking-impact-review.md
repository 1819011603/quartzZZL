# Thinking影响当前结论

|场景|当前生产配置TEST旧/新tokens|结果|
|---|---|---|
|画像|1593 / 753|原目标模型，均开启thinking，messages相等|
|摘要|806 / 751|独立生产生成配置TEST旧基准已补，均开启thinking，messages相等|
|高中分层|0 / 0|生产仍用旧别名，新显式disabled保留有效行为，messages相等|
|素养分层|0 / 0|同上；历史旧完整实收复用，messages相等|

四组有限TEST有效thinking验收完成。画像/摘要实验disabled已撤回，两分层TEST配置单独disabled；不凭入口都省略thinking判一致。证据thinking-effective-alignment.json、thinking-related/result.json及thinking-related-verification.md，完整输入输出在final-15-comparisons.json。历史旧别名0-token实验保留原始文件，不作为当前生产画像模型基准。

其余场景既有证据复用，不全量重跑。15个有限TEST场景完成不代表生产全量等价或输出语义普遍相同。两问题建议403排除；两降退费仅同隔离库对照且旧新均未注入片段，不保证生产召回或知识增强。此次仅归档合并，无业务调用/配置修改/飞书写入，无在途操作。
