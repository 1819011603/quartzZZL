# 企微 TEST 执行安全交接（round4）

收束原因：所有者要求停止新增业务调用、造数和验证。本轮只保留已完成只读结果，不扩大动作范围。

## 身份与全局状态

- 未切换全局 cosplay/login 状态；未调用代课登录、未写 Cookie、未使用生产或 BETA。
- 本轮没有以页面登录身份提交业务写入。候选读取走 TEST 固定 student-center 直连 ACL compare，属于只读服务调用；不能据此宣称页面权限或老师身份已验证。
- 未联系真实员工/学员，未访问或伪造 external_userid，未创建企微好友。

## 已完成只读调用与证据

- 固定 TEST 实例：`10.255.176.174:28688`，`student-center-5d84df769-gxbql`，镜像 `release-5dce9cdb-20261103201632`，`traffic-env=test`，Running/UP；沿用既有证据 `/tmp/w1-e9aebdb9/student-center-pods-detail.json`。
- 读取大班候选：方法 `com.gaotu.yunying.student.center.domain.service.roster.RenewalService#getStudentRenewalInfosByUserIds`，班号 `585960582537144320`，学员 `7658127801`、`7658129872`，字段包含 userId/clazzNumber/subclazzNumber/joinClazzTime/studentTags/studentTagNames/wechatRemark/clazzName。结果 code=0：两人均返回班名 `dcg-扩科排除-前置-五年级语文`、子班号 `36622538973250048`、精确 user/clazz 关系；未返回标签/备注字段。原始结果：`/tmp/w1-p0-243aa61a/round4/qiwei-candidate-large.json`。
- 读取小班候选：同方法，班号 `586084334251927552`，同两学员；结果 code=0、空数组，原始结果：`/tmp/w1-p0-243aa61a/round4/qiwei-candidate-small.json`。这只证明该接口当前返回空关系，不证明页面/ES/标签为空。
- 两次 curl 均已退出，无 trace 字段回传；无业务写 runID。

## 写入、对象与恢复状态

- 已创建对象：无。
- 已修改标签/备注/好友关系/数据库/ES：无。
- 原值快照：未产生新的可写快照；历史共享行 `id=120554` 未触碰。
- 恢复动作：无须执行；没有临时写入、没有待恢复配置或购物车。
- 备注/标签任务：未调用 `/batchOperate/tag/save`、`/remark/creat/edit/task` 或任何异步任务；无 task number/runID。

## 未结束操作

- 无在途 curl、mcpcli 查询、造数 run、页面操作或持久会话。本机 `mysql_query.py` 常驻进程为 MCP server，不对应本轮未完成请求；未发送待处理写任务。

## 结论与剩余缺口

- 已补充“候选大班确有同班学员关系、小班候选接口当前无返回”的只读证据。
- 仍未取得真实老师页面身份/权限、受控企微好友成功关系、原备注、标签写后 DB/ES/页面读回；未执行批量/单人/筛选/清空/取消/恢复。
- 不能把大班读取结果称为 P0-10/11 整卡通过，也不能把小班空数组称为页面空标签或好友不存在。
