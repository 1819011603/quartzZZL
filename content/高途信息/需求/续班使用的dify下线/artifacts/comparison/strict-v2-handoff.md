# 五项严格对齐：80%安全交接

## 续接最新状态（覆盖下方旧暂停记录）

- 代码已提交推送 `f23459b399c2148e1ec84e888d9a2d0bc5d19869`，编译成功；`/tmp/sse-cost-junit.log`实际25项通过。尚不能用提交代替部署。
- W1-073b38负责TEST test-gtbg-dev-1部署、实际版本UP及AICR回读。
- W1-d5f701是唯一Apollo写入负责人，待新版本UP后验证已有旧名授权的素养NPS；准备严格参数、应用费用兜底及已核验身份映射。无其他worker写Apollo。
- W1-d759ca是唯一飞书写入负责人，更新原表模型、身份和tools事实，后续接入新实收。
- 模型阻塞：三条旧别名路由保存均被正常入口拒绝“模型不存在或已下线”，原14路由回读未变。不得重复尝试或绕过鉴权；严格9场景实收仍未完成。
- 真实身份：gongxuemeng邮箱映射已证相等；缺省费用主体随旧应用变化，不能设全局统一账号。当前受控映射实现未知身份失败，不能声称覆盖所有员工。


最新owner要求：response_format可额外保留；max_tokens/stream/thinking须对齐旧LiteLLM请求（旧无则不传）；x-tech-ai-user-id必须按旧真实费用身份传递；model须核线上映射；messages继续严格一致；降退费tools仅调查方案，4KB不切换。生产只读，不生成。此前允许8192/非流式/身份缺省的口径已失效。

## 当前现场
worktree /private/tmp/student-data-xuban-review-20261123；branch feature-xuban-dify-offline；HEAD及已部署56b53f3c5。本轮主worker没有配置写入、部署或生成调用。
W1-073b38唯一Java写入者，已修改Executor、Override、GatewayAccessor、CallOption/Response/DifyResponse/GatewayResponse，新增GatewaySseReader及测试；尚未收到最终交接，不能假定编译或实现完成。已发scope要求安全收束，暂停新增提交推送部署配置业务调用；接手先看最新result和git diff，避免覆盖。
W1-d5f701已完成tools方案，后续正查旧Dify费用身份，亦已通知收束；需收最新结果。
W1-d759ca模型调查已完成，无在途。

## 本轮已完成
1. strict-v2-model-map.md/json：实时只读PROD/TEST控制面安全模型映射、caller路由及9场景期望。旧Doubao1.5重定向强制disabled；旧Seed1.6映射同目标无该强制项；DeepSeek映射见文件。TEST gps-ai只明确列素养NPS旧别名，其他旧别名调用权限/重定向先后未生成验证，不能直接断言可调。
2. strict-v2-tools-plan.md：正式生产固定原因提取→知识检索→单LLM，不能照搬废弃TEST agent两轮tools。优先调用检索API再拼上下文；top_k4/rerank false。该项方案完成，不是正式迁移。
3. 费用来源实际只读调用：SubClazzHelper#getRunUserByClazzAndUser(500775385189890048,7404351741)返回gongxuemeng@gaotu.cn，trace2724e96a-5590-41b1-a4cb-d4d1d2eb7f24.0.3；证据strict-v2-cost-owner-readback.json。这是真实样本责任老师，不可硬编码。
4. 代码事实：退费queryRunUser(subclazzNumber)→assistantNumber→teacher.baseInfo.email；SOP用SubClazzHelper；旧DifyRequest传userTag及run_user；新resolveCostUserId优先command.costUserId否则RunUser.email前缀，GatewayAccessor已有x-tech-ai-user-id。quickTest未传runUser，TEST Apollo fallback-user未配。还没核到Dify部署如何将run_user映射下游user/费用头，不可把历史UUID当员工账号。
5. Pod只读入口baijia.base-tech.ai.teable.dify-api env prod，选到dify-api-78886c7f97-8lhxw，cwd /apps/srv/instance。/app/api路径不存在，grep无输出不证明没逻辑，身份子任务继续找正确部署路径。

## 接手必须完成
- 收两子任务交接，恢复明确scope；费用原链路真实身份映射及新头实收仍是必做，不能只看代码称完成。
- 完成SSE/省略参数实现与测试，审diff、commit push，统一TEST部署回读版本。
- 选择旧model别名或其他可证等价路线，使thinking在请求层不多发、后续redirect行为正确。验证TEST权限不足时查配置再解决，不回切Dify。
- 用真实样本身份通过已有Executor普通/V2请求，验证x-tech-ai-user-id实际发出/接收；若必须改实现交唯一写入者，不能用任意fallback凑数。
- 更新TEST配置（尚未做），受影响9样本验证完整请求max_tokens缺省、stream true、thinking仅素养NPS enabled，messages相等；response_format可保留。保留完整SSE聚合响应/usage/finish_reason证据。
- 飞书目前仍revision102，尚未写本轮前四项成功；完成后更新原表完整输入输出、费用和线上模型映射。README/tasks已有五项新契约。
- 未完成不能包装完成；4学部实例独立实收边界继续保留。

主Worker工具session1764已结束，返回只读责任人查询成功；无主Worker在途命令。子任务在途状态需最新result确认。所有旧messages/stop等成果复用，但受本轮参数协议改动影响需补验。
