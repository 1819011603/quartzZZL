# thinking后续核对与TEST修正

版本91012878；TEST/test-gtbg-dev-1；未改代码/生产。

## SOP不修改：纠正旧报告前提
普通compare的`sop-prod-received.json`和`sop-prod-logs-litellm.json`证明旧模型是doubao/Doubao-Seed-1-6，并非1.5。其redirect到doubao-seed-2-0-lite-260428；旧reasoning_tokens=817，新634。真实V2 fixture的应用256327049255322624，证据sop-real-entry.md及sop-v2-*，旧同样Seed-1-6，旧/新reasoning_tokens=1764/1896。两入口并不存在“一侧1.5、一侧1.6”的已知冲突。沿用已有映射为agent256325360053917696，未改变其任何参数，不把正常推理关闭。原report.md“旧路均1.5”应由主Worker纠正。

## 分层实际差异与修正
旧有效样本tier-valid-prod-received.json是doubao/Doubao-1-5-pro-32k，usage.json旧reasoning_tokens=0，新252；text格式修正后tier-fix-llm-response.json仍有380。旧1.5重定向强制thinking.disabled规则复用trace-recheck-20261123的既有核验与model-redirect-evidence.json，直用新模型绕过该规则。依据实际差异，仅对agent262172718139452416新增params.thinking={"type":"disabled"}。

读取最新TEST已发布map后合并；此前dry-run无草稿；修改后仅目标key。releaseKey=20261123193207-188aa6ecfba69670。发布后完整map回读与target一致，分层response_format=text保留；画像disabled及所有其他agent不变。

## 同有效样本复验
复用tier-valid-request.json，trace=7a05052d-9094-4a00-aa88-bf44dcf0eb61.0.3，2026-11-23 19:32前后。仅TEST业务调用，日志TEST/SLS/app过滤service=litellm。实收thinking.disabled与response_format.text；响应stop，无reasoning_content，reasoning_tokens=null（不是0）。业务双路完整响应见thinking-response.json。现有契约清理围栏后仍是原因文本。

证据thinking-before/target.json、thinking-dry-before/dry-after/release/readback.txt、thinking-headers.txt、thinking-response.json、thinking-test-logs.txt、thinking-received.json、thinking-llm-response.json。

## 边界
未重跑SOP：实际证据不支持关闭推理，保持原配置与已完成V2验证有效。分层此次未做事件落库或部门路由验证。null计数不能写成零；禁用推理不保证措辞相同。

配置页：https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default
