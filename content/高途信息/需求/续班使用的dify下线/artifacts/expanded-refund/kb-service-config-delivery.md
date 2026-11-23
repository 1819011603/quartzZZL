# TEST服务配置与隔离应用交付

2026-11-24；仅TEST/default/application及TEST ees_data。采用主Worker确认AiApplicationExecutor方式，不改生产或原四路由。

应用名 `TEST-KB-ServiceAPI-20261124`，application=1795457739670157，agent=1795457739670155，prompt_config=1795457739670159。三个新对象均隔离。agent平台2、无旧Dify访问key；新模型覆盖deepseek-flash、params.stop=[]。克隆素养应用结构，替换为独立prompt_config/version与gateway_core_prompt，retry_times=0、after_plugin_config空。

prompt_config.core_prompt及application.gateway_core_prompt均完整1390字符素养生产模板，SHA256=e24fb960acf9d089e68bc69a4372260e1e879840d70179414b77fce38d4c9ce2。独立prompt_config.after_processor_prompt_config与dependency_metadata_config均空。按当前DynamicPromptGenerator代码，新链路优先gateway_core_prompt，没有额外后处理提示词或动态数据拼入；保留模板中的sys.query占位及末尾//原文，实际业务与检索内容从user消息传入，非Dify模板替换器。

Apollo新增7项ai.dify.dataset.retrieve.*：enabled=true，environment=test，base-url=https://test-dify-open.baijia.com/dify/api/v1，api-key为TEST dataset凭据（不回显），top-k=4，reranking-enabled=false，search-method=keyword_search。现有override map只新增本agent，其他条目完全相等。

发布前草稿与已发布无差异；设置后检查仅7项新增与override map修改，无删除、无外部夹带；dry-run后发布。releaseTitle=20261124021612-release，releaseKey=20261124021612-188aa6ecfba6968e。独立config-server回读8项全部相等；密钥仅报告长度32及哈希，见kb-service-config-published.json。数据库另一次只读查询复核system长度、SHA及两个空配置。

本交付证明配置与DB已落地，不证明尚在途Java已部署或新TestService已业务生效；主Worker下一步部署调用retrieveAndComplete，aiApplicationName传上述应用名。dataset传0105aec9-ef88-4a45-8f4a-fb1b5a3f12ce。

恢复状态：新增配置及三个DB对象保留；若收回试验，只移除7项、新agent覆盖及三个隔离对象，不覆盖其他人的map变更。未执行恢复。临时TEST凭据文件仍0600保留，Apollo已有副本，后续按主Worker集成/清理节奏处理。

https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default
