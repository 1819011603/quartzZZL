# 旧Dify输入格式对齐：本轮交接

最新口径：从语义近似改为旧Dify实际LiteLLM消息格式对齐，包含角色/顺序/内容位置/包装/通用句/场景标签；不要求输出逐字一致。范围仍13个非知识库目标应用，4个知识库保留Dify。生产不改、不生成、不上线；参数既有修复不回退，旅程既有字段不删除。

本轮已做：读取git-branch-convention、requirement-docs及student-data开发规则；核对worktree干净；读取DynamicPromptGenerator。generate()已有旧flat拼装，generatePayload()当前将覆盖后的system和业务user拆为两消息。候选最小实现应复用旧flat而非另拼伪JSON，按应用限制影响，旧Dify系统模板独立承载避免重复。方案尚待最终确定，不算已实现。

已有真实差异依据：artifacts/comparison/pairs.json、user-diff-audit.json；飞书revision56，11表143代码块已完整回读。仅SOP V2真实user相同，其余10组不同；历史知识库样本不扩大正式迁移范围。差异来自之前真实调用，按原授权可复用，不重复无关调用。

执行负责人：子任务W1-073b38已接到实现+单测+编译+commit push任务（唯一代码写入者），主Worker拟负责配置和统一部署/运行验证。因owner上下文80%收束，已发送scope收窄：仅安全收束当前步骤并交接，暂停新增提交推送部署/业务调用。新worker先查子任务状态和结果，复用同会话，不重复写同文件。截至主Worker末次git status工作区仍干净，未观察到新代码产物；不能据此断言子任务后续绝无改动。

代码worktree：/private/tmp/student-data-xuban-review-20261123；分支feature-xuban-dify-offline；此前已部署6909717c（包含87124f42）。本轮没有部署、Apollo发布、业务调用、commit/push或新增测试结果。

剩余：核定当前各应用旧格式与模板映射→按应用的最小实现及反例测试→编译commit push并检查评审→TEST配置及部署回读版本→同输入LiteLLM实际messages核验（SOP条件未变复用）→表内更新完整对照与trace。旧生产模板与历史TEST模板冲突要具体列差异，不盲目覆盖现行业务增强。当前无新外部阻塞；生产dataset凭据事项与本目标独立。
