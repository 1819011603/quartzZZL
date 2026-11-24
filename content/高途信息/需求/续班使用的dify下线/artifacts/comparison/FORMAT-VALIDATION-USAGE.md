# 格式实收验证材料

仅本地准备，无业务调用、部署、配置或飞书变更。主 Worker 先确认实际部署 commit、test-gtbg-dev-1 泳道及 TEST 应用绑定；脚本的 commit 仅为记录标签，不自动核验部署。

```sh
python3 artifacts/comparison/validate_format.py list
python3 artifacts/comparison/validate_format.py run --case '课程体验' --commit '<已确认部署commit>'
python3 artifacts/comparison/validate_format.py extract --case '课程体验' --run '<该次run.json>' --log '<完整TEST新侧日志>'
```

所有场景仅调用 quickTestAiApplication，新侧走已配置网关；执行前主 Worker 核实 TEST 路由。根因不再调用 compare，不允许旧侧新推理。根因输入从历史实收 user 包装中的业务正文重建，保留旧完整 messages 基准。

```sh
python3 artifacts/comparison/validate_format.py run --case '退费根因' --commit '<已确认部署commit>'
python3 artifacts/comparison/validate_format.py extract --case '退费根因' --run '<该次run.json>' --log '<新侧完整日志>'
```

重建输入不等于原入口请求逐字段相同，也不是新侧实收证据。最终新侧实际完整 messages 与历史旧 messages 逐字相等，才能证明该样本下游业务输入和格式一致；不相等则保留具体差异，不能提前宣称成功。原请求缺失不阻塞此项验证。旧 compare 样本已移除，脚本只允许 quickTest。

run 保存 request、完整HTTP响应、headers、run.json。业务需 code=0 且各侧有非ERROR answer，HTTP200不算成功；失败先查 trace，不能直接重跑。日志通过既有 mcpcli qingzhou_observe get_log_v2 仅按完整 trace 查询，客户端筛选 service=litellm（SLS不支持service键值索引），保留请求与 Response received by LiteLLM，勿仅筛请求。只读日志检索环境标签不等同于业务应用环境，不得触发生产推理。

extract 强制 --run，核对 case 和每条请求/响应的完整 TID；要求各侧恰好一条完整 request 与 response，100条结果或多轮停止人工核对。生成 .received.json 保存完整请求参数及响应（包含原有usage），另保存原始messages和逐行diff，不合并角色或展开包装。

11组：7组历史ready quickTest，1组根因重建输入quickTest，SOP V2未改则复用原syncRequestTaskV2证据，2组知识库样本排除；四个知识库正式应用继续Dify。画像、分层、摘要正文为动态数据，变化单列，不归因格式修复。旅程旧TEST模板落后生产2482字模板，保留resolved字段，模板冲突和格式差异分开报告。素养NPS原请求已固化在format-samples内。

离线证据 format-offline-check/parser-v2-check.json：历史课程体验提取完整request/response及usage成功，错trace拒绝。historical-run.json明确为历史解析夹具，不能冒充当前部署run。未调用业务，未验证当前格式修复。
