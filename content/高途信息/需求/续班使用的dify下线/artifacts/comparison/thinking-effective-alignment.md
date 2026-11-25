# Thinking最终基准与配置

当前生产画像v7直呼doubao-seed-2-0-lite-260428；已在TEST正常注册该模型、将既有副本改回原model，完整配置回读仅人员时间和扩展名顺序不同。未改共享网关或生产。此前用旧别名复制引入force thinking.disabled，造成0对1202的测试基准偏差，不是生产画像本身关闭thinking的证据。

|同原数据实测|trace|reasoning tokens|messages|
|---|---|---|---|
|生产配置TEST旧Dify直呼|cff96ffc-9522-4b87-ba4b-3ccf50b0dc84.0.3|1593|与新逐字相等|
|新画像普通入口|3fce4abd-3895-4b68-bb90-54777ac6d680.0.3|753|保持原样|
|共享agent新摘要回归|66c8b9fa-a1d0-4fa2-a305-6e24548ef9ce.0.3|751|与摘要原样本相等|

三者均有reasoning_content，入口省略thinking；tokens数值不要求相等。最终已撤回共享TEST agent255107338300556288的实验disabled，发布回读与目标一致，保留response_format=json_object、stream=true及omitMaxTokens。旧别名0-token实验保留在thinking-effective-alignment目录，不能作为当前生产画像基准。

完整直呼请求/响应见profile-direct-baseline/，真实配置回读见profile-real-baseline/direct-test-detail.json、direct-test-publish.json；最终发布见profile-direct-baseline/thinking-direct-release.txt。新旧业务输出不要求逐字相同，思考开关一致不证明所有输出语义等价。生产画像与摘要独立应用不能单凭共享TEST agent外推全部生产行为；分层未随之修改，应按独立旧别名基准审查处理。

未改代码/部署/README/飞书；无在途操作。TEST provider复用既有合法网关凭据，秘密未归档。

Apollo：https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default
