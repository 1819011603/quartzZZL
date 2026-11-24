# 格式实收验证材料

仅本地准备，无业务调用、部署、配置或飞书变更。主 Worker 先确认实际部署 commit、test-gtbg-dev-1 泳道及 TEST 应用绑定；脚本的 commit 仅为记录标签，不自动核验部署。

```sh
python3 artifacts/comparison/validate_format.py list
python3 artifacts/comparison/validate_format.py run --case '课程体验' --commit '<已确认部署commit>'
python3 artifacts/comparison/validate_format.py extract --case '课程体验' --run '<该次run.json>' --log '<完整TEST新侧日志>'
```

普通场景只调用 quickTest。根因为明确标记的新受控合成样本，单独调用 compareAiApplication，固定应用名退费根因分析、参数环境 test 和 test-fuwu 入口。运行前须核实该 TEST 应用的 Dify 绑定仍为 TEST 应用；脚本不能通过域名自动证明 Dify 目标身份。

```sh
python3 artifacts/comparison/validate_format.py run --case '退费根因' --commit '<已确认部署commit>'
python3 artifacts/comparison/validate_format.py extract --case '退费根因' --run '<该次run.json>' --log '<新侧完整日志>' --old-log '<同次旧TEST Dify侧完整日志>'
```

根因不再要求复用历史输入，不允许用历史旧 messages 作基准。两侧必须是本次同一完整 trace 的不同日志文件。日志所属旧/新侧及 TEST 应用归属仍由操作者按调用链核实，trace 相同本身不证明侧别。

run 保存 request、完整HTTP响应、headers、run.json。业务需 code=0 且各侧有非ERROR answer，HTTP200不算成功；失败先查 trace，不能直接重跑。日志通过既有 mcpcli qingzhou_observe get_log_v2 按完整 trace 和 service=litellm 查询，保留请求与 Response received by LiteLLM，勿仅筛请求。只读日志检索环境标签不等同于业务应用环境，不得触发生产推理。

extract 强制 --run，核对 case 和每条请求/响应的完整 TID；要求各侧恰好一条完整 request 与 response，100条结果或多轮停止人工核对。生成 .received.json 保存完整请求参数及响应（包含原有usage），另保存原始messages和逐行diff，不合并角色或展开包装。

11组：7组历史ready quickTest，1组新样本compare，SOP V2未改则复用原syncRequestTaskV2证据，2组知识库样本排除；四个知识库正式应用继续Dify。画像、分层、摘要正文为动态数据，变化单列，不归因格式修复。旅程旧TEST模板落后生产2482字模板，保留resolved字段，模板冲突和格式差异分开报告。素养NPS原请求已固化在format-samples内。

离线证据 format-offline-check/parser-v2-check.json：历史课程体验提取完整request/response及usage成功，错trace拒绝。historical-run.json明确为历史解析夹具，不能冒充当前部署run。未调用业务，未验证当前格式修复。
