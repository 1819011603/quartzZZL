# 链接中心

- 需求：`【A-续班-20261102】企微封禁优化 + EM纯续推荐范围调整`
- 子项1 PRD：https://gaotuedu.feishu.cn/wiki/ZiRZwGOJGi3CtnksQg1cJwZsn9b
- 子项2 PRD：https://gaotuedu.feishu.cn/wiki/UewqwsMWOiunOgk9Kloce1Jrn52
- 技术方案（含表结构+接口协议）：https://gaotuedu.feishu.cn/docx/AQEtdIeKzo7P5IxeQEzc7EpxnBe

## 检索锚点

- PRD token：ZiRZwGOJGi3CtnksQg1cJwZsn9b、UewqwsMWOiunOgk9Kloce1Jrn52
- 方案 token：AQEtdIeKzo7P5IxeQEzc7EpxnBe
- 分支：product-server/student-center/cart/order `feature-xuban-pure-relation-20261102`


## 只读对照交付（2026-11-04）

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 问题记录 | 两子项前后端决策清单 | [decision-review.md](artifacts/20261104-readonly-review/decision-review.md) | 2026-11-04 |
| 调研 | 企微前后端、配置与生产静态产物 | [qiwei-review.md](artifacts/20261104-readonly-review/qiwei-review.md) | 2026-11-04 |
| 调研 | 纯续管理前后端契约与只读查询 | [em-review.md](artifacts/20261104-readonly-review/em-review.md) | 2026-11-04 |
| 调研 | cart/order推荐与缓存影响 | [shared-backend-review.md](artifacts/20261104-readonly-review/shared-backend-review.md) | 2026-11-04 |
| 其他 | 子任务最终状态、33单测与配置证据 | [verification-evidence.json](artifacts/20261104-readonly-review/verification-evidence.json) | 2026-11-04 |

## 2026-11-05 核对与P0交付

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| case | P0现场步骤与执行边界 | [P0-case.md](P0-case.md) | 2026-11-05 |
| 其他 | 当前验证与版本证据 | [verify.md](verify.md) | 2026-11-05 |
| 调研 | 当前前端PRD及25项契约 | [frontend-review.md](artifacts/20261105-diff-p0/frontend-review.md) | 2026-11-05 |
| 调研 | cart修复、测试与边界 | [cart-review.md](artifacts/20261105-diff-p0/cart-review.md) | 2026-11-05 |
| case | P0对象及逐步证据版（飞书，revision146回读） | [在线文档](https://gaotuedu.feishu.cn/docx/ZQUXdlDxWoknJhxu914c2uVYnBr) | 2026-11-05 |
| case | P0 精简版 v2（revision395，按代码改动，步骤在前） | [在线文档](https://gaotuedu.feishu.cn/wiki/KeCZwdJTBiIJDJkX8lRcGb9gnCs) | 2026-11-05 |
| 其他 | C 端纯续链接验证方法（入口/选品/价格/跨模式/mock 支付/坑） | [C端验证方法.md](C端验证方法.md) | 2026-11-05 |
| 其他 | 精简版前后端验证证据（trace/入参/响应/阻塞） | [verification.json](artifacts/20261105-p0-concise/verification.json) | 2026-11-05 |
| 其他 | 旧版 revision319 全文备份 | [feishu-revision-before.xml](artifacts/20261105-p0-concise/feishu-revision-before.xml) | 2026-11-05 |

| 需求wiki节点 | 当前P0执行文档（同一对象） | https://gaotuedu.feishu.cn/wiki/KeCZwdJTBiIJDJkX8lRcGb9gnCs | 2026-11-05 |

## 本轮运行证据（任务e9aebdb9）

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 调研 | 两子项真实链路与交付核对 | [运行核验](artifacts/20261105-runtime-w1/runtime-review.md) | 2026-11-05 |
| 其他 | 飞书revision99回读及结构核对 | [document-verification.json](artifacts/20261105-runtime-w1/document-verification.json) | 2026-11-05 |
| 其他 | 原始请求响应/日志文件校验值 | [manifest.json](artifacts/20261105-runtime-w1/manifest.json) | 2026-11-05 |

## P0逐步证据补全（任务243aa61a）

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| case | 12卡/36步/原30条P0及附件回读核验 | [document-verification.json](artifacts/20261105-p0-detail/document-verification.json) | 2026-11-05 |
| 其他 | 外部文档同一证据附件（30份文件） | [p0-evidence-243aa61a.zip](artifacts/20261105-p0-detail/p0-evidence-243aa61a.zip) | 2026-11-05 |

| 调研 | B侧班名与同名不同班ID补证（本轮安全交接） | [verification.json](artifacts/20261105-p0-detail-round2/verification.json) | 2026-11-05 |

- [他人企微MR1528静态比较（feature-weixin-opt，仅评估）](artifacts/20261105-p0-detail-round3/mr-comparison.md)：[远端MR](https://git.baijia.com/gaotu/yunying_workbench/student-center/-/merge_requests/1528/diffs)。

- [P0信息分档与逐卡缺口](artifacts/20261105-p0-detail-round3/information-gaps.md)：[30条机器映射](artifacts/20261105-p0-detail-round3/reproducibility.json)，[只读查询manifest](artifacts/20261105-p0-detail-round3/qiwei-source-evidence.json)，[增量证据附件](https://gaotuedu.feishu.cn/docx/ZQUXdlDxWoknJhxu914c2uVYnBr#doxcnyPfjduHoRRZu6yBFyF3UDh)。

## 当前P0与对照

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| case | 测试侧P0对照50162/72344（原集只读） | https://qa.baijia.com/banshan/#/caseManager/171/50162/72344/3 | 2026-11-05 |
| case | 当前P0 revision247及集中证据 | https://gaotuedu.feishu.cn/wiki/KeCZwdJTBiIJDJkX8lRcGb9gnCs | 2026-11-05 |
| 其他 | 本轮逐卡核验与计算/编号自检 | [document-verification.json](artifacts/20261105-p0-execution-round7/document-verification.json) | 2026-11-05 |
