# 关联三场景有效参数验收

已重新读取三者当前生产Dify配置：摘要直呼目标模型；高中/素养分层仍为doubao1.5旧别名。分别采用对应配置TEST副本，不能互套画像结论。

|场景|旧trace|新trace|旧/新reasoning tokens|messages|
|---|---|---|---|---|
|摘要|ffe40068-955e-4044-9eeb-ac8641740dfd.0.3|66c8b9fa-a1d0-4fa2-a305-6e24548ef9ce.0.3|806 / 751|逐字相等|
|高中分层|90111bbb-6122-4a4e-84a0-1af98e31eda1.0.3|c08756d7-169f-4a84-89c3-1b825f63ac04.0.3|0 / 0|逐字相等|
|素养分层|71b44f24-f24a-45f5-8200-d63615400d9b.0.3|95d2fb8f-d462-4449-839e-b6123dca4b16.0.3|0 / 0|逐字相等|

摘要复用既有直呼TEST副本，完整生成配置与摘要生产配置相同，差异仅创建修改元数据及file_upload扩展名顺序；新侧复用已完成66c8b9fa实际请求响应。两分层复用旧别名TEST副本，与当前生产生成配置相同，历史素养完整usage复用，高中旧usage无法取回，已仅补一次同数据旧TEST运行。两分层新侧显式disabled用于保留旧别名force注入的有效行为，画像摘要不设disabled。

仅修改student-data TEST agent262172718139452416.params.thinking，发布并回读完全一致，见related-release.txt和published-map.json。全部完整请求/响应/输入及生产配置在thinking-related目录。输出不要求逐字相等，本验收不代表生产生成或切换；无代码修改部署，无共享路由修改，无在途操作。

Apollo：https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default
