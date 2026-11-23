# TEST知识库场景保留Dify落实

2026-11-23，student-data / TEST / default / application；test-gtbg-dev-1（既有部署91012878，本轮未部署代码）。

owner决定：有前置知识库暂不替换，不再建设替代检索。本轮仅移除ai.agent.accessor.override.map中255743632420648960（降退费服务建议）、261423990261694464（素养服务建议）两个网关覆盖条目，回落数据库platform_type=1。其他7个agent配置逐对象相等；高中/素养问题建议255465773531663360、255465673062353920原本无覆盖条目。

发布前dry-run无已有草稿变更；写后dry-run仅该key变化；发布releaseTitle=20261123203513-release，releaseKey=20261123203513-188a49b33afd47c6。独立config-server回读与目标JSON完全相同。

正常quickTestAiApplication入口（未使用强制compare）验证：
|应用|响应|traceId|Dify messageId|
|---|---|---|---|
|降退费服务建议|code=0,event=message,answer非空|f558b680-5ab8-461f-9a49-5c29e04fadef.0.3|4d75ac12-0bee-42c6-ad8a-408590d37ab9|
|素养服务建议|code=0,event=message,answer非空|3bacf406-b5f0-4034-bef2-55732d412b1f.0.3|993f0b0d-6860-4405-a48f-7165ebdc2ff1|

完整请求、响应头、响应为kb-quick-*；配置前后、dry-run、release为kb-route-*。TEST通用降退费仍回到数据库原绑定【废弃】应用，未修改其app/key映射；本轮确认Dify路由恢复，并非把旧TEST应用替换为生产工作流。生产两个建议目标均前置检索，按owner决定暂不迁；生产配置/代码/数据未改。

Apollo页面：https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default
