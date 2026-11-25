# thinking有效行为修正安全交接

按主Worker最新停止指令收束；本轮仅只读调查，未写Apollo、未发布、未修改代码、未部署、未新增生成或复验。无在途工具会话/业务请求，无需取消或恢复配置。

## 已做与证据

- 已读apollo-config技能，复查现有辅助脚本；未执行旧strict_v2_apollo_set.py（该历史脚本还含费用兜底，禁止直接复用）。
- 已读取student-data / TEST / application已发布ai.agent.accessor.override.map，原文thinking-effective-alignment/test-map-before.txt（同/tmp/thinking-map-before.txt）。画像/摘要共享agent255107338300556288当前model=doubao-seed-2-0-lite-260428，params包含response_format=json_object、stream=true，无thinking；omitMaxTokens=true。
- 用户给出的实际响应差异必须作为未解决问题：旧真实副本trace2a220458 reasoning_content=null、reasoning_tokens=0；新f2e3ea9d有reasoning_content、reasoning_tokens=1202。入口均省略thinking不等于最终有效行为相同。
- 已找到待复用控制面线索：strict-v2-model-map.md、model-param-audit.md/json等包含旧别名force thinking.disabled记录，但本轮尚未重新核实运行注入路径，不把线索当已闭合因果。

## 续接步骤（当前不执行）

1. 结合旧新完整响应及网关控制面只读证据，确认旧别名force thinking.disabled注入路径；对共享agent影响的画像/摘要按审查矩阵限定范围。
2. 仅在student-data TEST局部新增thinking.disabled，保持model/callerRoute/prompt及费用身份不变；先现值和草稿差异回读，避免覆盖他人修改。按既有授权dry_run、发布、回读。
3. 复用profile-real-baseline旧真实配置副本及旧成功调用，不重建、不重跑旧侧；新普通入口按保存的原始params定向复验，检验messages不变、reasoning_content为空和reasoning_tokens=0，不能只检查HTTP入口字段。
4. 仅证据确认同因场景才补验；新代码确有必要时再按技能处理提交部署/AICR。

## 状态与恢复

当前本轮配置修改数0、发布数0、代码修改数0、业务生成数0。无在途句柄，未挂Arthas。已有真实基准和私有key保持原样；不将秘密写入报告。47b3dcb7为此前已确认版本，本轮没有重新查部署状态，不冒称新版本验证。后续继续前重读当前配置。

Apollo：https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default


## 主Worker合流交接

owner明确要求上下文80%安全收束，非业务阻塞。两子任务均已结束，无在途操作。本轮未更新飞书，当前仍revision186；不得将旧文档参数对齐表述视为有效thinking已对齐。

已证：画像旧trace2a220458-cfd5-4547-82a0-295b5f386335.0.3 reasoning_tokens=0、reasoning_content=null；新f2e3ea9d-eb41-41a8-b041-63d20fba2554.0.3 reasoning_tokens=1202。strict-v2-model-map.md第9/48行保存旧豆包1.5别名force thinking.disabled；仍需核验实际注入路径。TEST当前画像/摘要共享agent省略thinking。

下一步：先读thinking-impact-review.md/json与test-map-before.txt，回读配置现值；仅TEST局部对齐有效thinking，发布回读，同原数据复验实际推理状态和完整messages。画像优先；摘要、高中分层、素养分层为有证据同因候选，新reasoning tokens736/338/410，旧完整usage尚需补，不把缺失当0。其他场景按矩阵裁决，不全量重跑。真实画像生产配置副本和所有key复用，不重建；生产共享路由不得修改。

修正后更新完整HTTP/原始响应/业务输出及trace，原归档与飞书采用当前结论替换，不追加流水。新代码如必要按既有commit+push/AICR；仅配置修正无需伪造代码提交。
