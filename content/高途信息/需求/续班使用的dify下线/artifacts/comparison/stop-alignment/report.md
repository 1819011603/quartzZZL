# TEST stop及enable_thinking省略对齐

56b53f3c5 / test-gtbg-dev-1；无Java修改或新部署。只删8个迁移agent的params.stop及根因/旅程的params.enable_thinking，其他配置保留，知识库隔离agent未改。

发布：20261124134541-188aa6ecfba696dc, 20261124134735-188a49b33afd483d

已发布值独立回读与目标完全相等；不将省略enable_thinking解释为关闭思考或默认等价。

|场景|trace|变化字段|messages|结束|
|---|---|---|---|---|
|画像|cd8c704d-6af7-4e08-b948-b8a34ec50f70.0.3|stop|与上次逐字相同|stop|
|分层修正后|280a3c46-faf8-41da-bee2-56fa5ed218f1.0.3|stop|与上次逐字相同|stop|
|摘要|56b26778-3603-4269-a8cc-169c1036a5ac.0.3|stop|与上次逐字相同|stop|
|素养NPS|98b31236-b06f-4f31-845f-143093719806.0.3|stop|与上次逐字相同|stop|
|退费根因|7b4f7ec9-267a-4ae5-9b06-b7b8e558eda8.0.3|stop,enable_thinking|与上次逐字相同|stop|
|旅程|06c70104-ed02-4e0a-91ef-deec792dfe54.0.3|stop,enable_thinking|与上次逐字相同|stop|
|课程体验|c3a2c06e-e022-42a1-8043-cb09002f2aca.0.3|stop|与上次逐字相同|stop|
|NPS|df23d1b0-3954-487e-8305-ddba5ac84cd4.0.3|stop|与上次逐字相同|stop|
|SOP V2|652582eb-c231-455e-81c1-308af5451819.0.3|stop|与上次逐字相同|stop|

首次原entryKey重复，未进入模型；仅替换entryKey后原V2入口成功，完整messages不变。

全部9例完整request/response/usage见各目录sls-full.received.json（素养NPS为sls.received.json）。即时日志响应未入库只补查日志，没有因此重复生成。

Portal: https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default