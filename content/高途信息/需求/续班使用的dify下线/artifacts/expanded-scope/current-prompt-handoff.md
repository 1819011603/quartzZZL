
> **2026-11-24 最新裁决**：允许合理格式差异，以核心指令、业务数据、约束及业务作用保留为准。已有单次场景样本可接受TEST替换；素养NPS实收已补齐。历史“不完全一致”仅是字面差异记录，不代表不通过；4个知识库应用仍保留Dify。详见 [最新逐场景裁决](semantic-acceptance.md)。

# 当前范围与prompt交接

所有者最新决定：前置知识库暂不替换；问题建议高中/素养、降退费精品/素养4个生产应用保留Dify。剩13生产应用、8类场景仅核输入一致性；不再建设检索、不再问范围、不加质量/供应商HTTP门槛。生产只读。

## 已完成
- TEST建议两agent恢复Dify，releaseKey20261123203513-188a49b33afd47c6。正常quickTest trace f558b680-5ab8-461f-9a49-5c29e04fadef.0.3、3bacf406-b5f0-4034-bef2-55732d412b1f.0.3；event=message，独立map回读，其他7agent未变。kb-retained-verification.md。
- 续班prompt-current-renewal.md/json：SOP V2完整messages逐字段相等，正文13647字。画像/摘要/分层完整messages不等，拆分指令2272/466/2715字及业务1124/1493/5601字均逐字相等；原单user flat改真system/user。已查代码原因，无需为包装盲改。
- sop-context-clarification.md：student-data已读取SOP规则后再走两路，规则新旧完整保留，不是Dify额外检索遗漏；本fixture输入一致按owner口径收束。
- prompt-current-refund.md：根因/旅程/体验/NPS精品完整messages均不等；业务保留，flat拆包、去标签、尾换行、后处理位置不同。旅程当前生产两学部2482字均含已解决原因字段，与迁移模板相同；旧TEST模板落后，不能盲删生产字段。
- NPS生产精品473字/素养321字不同；TEST仅有精品映射。已核对生产绑定、TEST Apollo 映射和可用 trace，尝试过本地确定性生成；因无TEST素养旧Dify映射且不能用生产key发推理，缺旧新素养双侧实收，不标通过。详见 `expanded-renewal/nps-suyang-evidence-boundary.md`。
- 飞书 https://gaotuedu.feishu.cn/docx/EWI6dsdvPokck0xy89ccJDuEnhg 第9节已写本轮完整清单/一致性原因/保留决定；revision8，新增全文回读相同。证据prompt-feishu-readback.json。原README/tasks已更新范围。

## 剩余与交接
当前没有在途业务/部署/写操作，三个子任务均交付。未改业务代码，无新commit，无生产修改。按80%指令收束。
文档清理和逐场景裁决已完成。当前有效结论是已决定保留知识库，不再构成本轮阻塞；SOP一致，其余明确不一致及原因，不能称全部一致。素养NPS已完成可行取证尝试但缺双侧实收，具体缺口和所需条件见 `expanded-renewal/nps-suyang-evidence-boundary.md`；不使用生产app/key发推理，也不把本地生成冒充实收。计数口径见 `expanded-scope/scope-reconciliation.md`。生产DDL仅后续发布前置。
