# 本轮信息缺口与MR比较证据包（任务243aa61a）

先读 information-gaps.md（逐卡缺口/尝试/最小条件），再看 reproducibility.json（原30条/12卡的最终文档信息分类）；这些分类不等于业务通过数。完整可复现原30条2条、前置准备后可执行10条、信息仍缺失18条；12卡分别1/1/10。

- MR：mr-comparison.md 为结论；mr-meta.json / target-branch.json / mr-diffs.json / mr.diff / mr-verification.json 为源7f9bca38、目标release基线5dce9cdb及8文件的只读证据。仅静态比较，未运行其代码。
- 企微：qiwei-source-evidence.json 给实际TEST SQL、过滤、时点及源代码边界；qiwei-mark-candidates.json 与 qiwei-wechat-shards.json 是原始响应（标签查询末尾含工具total_count说明，不是纯JSON）。两候选×两正确班级组合无标签源行、两候选的27关系分表均无行。无行不等于ES/页面空标签或原备注为空。
- qiwei-report.md保留子任务初版与后续增量，当前事实见“增量补证”，整卡分类以reproducibility.json为准；未知身份/好友/原值仍属于信息缺失。
- b-class-dms.json 是上一轮TEST course_center.clazz的3个真实班名/课程ID原件，直接复用，不重查。正常商品资格/页面适用性并未由班名查询证明。
- 文件中原证据路径为采集机路径；本ZIP根目录提供同名文件，可按文件名打开。本包没有登录凭据、Cookie、DSN密码、业务写入、任务执行或新造数。

未执行的标签/备注/订单写入、页面、回溯保持“没做”，不补造任务ID或trace。原完整运行证据包及对应版本边界继续沿用文档原附件。
