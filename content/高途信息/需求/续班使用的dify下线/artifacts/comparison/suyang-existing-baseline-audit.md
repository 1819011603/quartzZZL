# 四素养既有基准适用性核查

本轮仅核对既有文件，不重跑12例，不改模型。12例验收继续有效。

|场景|既有材料实际可证明|不能替代的证据|
|---|---|---|
|素养根因|本轮新messages与pairs中旧精品根因messages逐字相等；system等于素养Dify模板2254字加换行|旧精品trace不是素养应用独立执行，不能改名为素养旧实收|
|素养旅程|新system等于素养当前Dify模板2482字加换行|历史TEST旧system为2151字，缺已解决原因要求；旧user带场景专用core/后处理，正式素养配置是通用core且无后处理。不同版本/配置不能直接作逐字基准|
|素养体验|新system等于素养Dify模板2381字加换行，亦与历史精品外system相等|历史TEST user含JSON后处理约束，正式素养配置无该后处理，不能借精品user作为素养基准|
|素养分层|已有高中/default分层旧实收与素养应用各自配置|高中实收不能证明素养独立动态数据；另查本轮已成功旧Dify消息持久化取完整prompt|

来源：`pairs.json`的11组名称没有四素养独立旧样本；`format-application-map.md`明确应用/学部映射；`../expanded-renewal/refund-current-素养*.json`为原Dify配置；`remaining-current-runs/suyang/*/received.json`为当前新实收。程序化比较结果见`suyang-existing-baseline-audit.json`。

结论：原先仅写“HTTP400，无法对照”过于笼统。已有材料能够支持模板/角色/配置对齐，以及根因的跨场景相同输入交叉验证；它们不能自动变成四个素养旧应用相同输入的独立运行证据。静态模板按Dify机制重建属于推断，不能标记为最下游实际实收。三项HTTP400只阻断新建TEST旧应用独立重放，不否定已有材料的上述价值。
