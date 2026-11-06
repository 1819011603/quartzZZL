# 企微备注在小班续班花名册不展示 — 排查记录（只读）

## 现象
在小班续班服务对学员(7707218286) 修改企微备注后，花名册 `studentRemark*` 仍为空。

## 证据
- 花名册 `POST https://test-fuwu.baijia.com/bgwApi/component/student-center/roster/small/renewal/page`
  - code=0，list=2；班级【造数】小班续班前置-小学数学-1103-1831(588506026511294464)
  - 学员(7707218286)：`studentRemark/One/Two/Three` 全为空
  - `mainTeacherStudentInfo=[{40731,mainTeacherWechatFriend:0},{0,mainTeacherWechatFriend:0}]`（非企微好友）
  - 学员(7707218285)：同样非好友、备注全空
- 备注接口 `POST /bgwApi/component/student-center/remark/creat/edit/task`（userIds=[7707218286]，模板「测试修改企微备注」）
  - 返回 code=0、data.resultStatus=true，trace `435f9289-36a0-452c-ab4d-a071fa7be453.0.3`
- 原 trace `cbc10b7e-6e85-476c-bf27-b7d73c169982.0.0`：
  - student-center `WechatRelationServiceImpl#createEditWkRemarkTask` → 查 `DwsFuwuUserTeacherWechatInfoMapper#selectList`（dws_clazz_user）→ 建 `BatchOperateTask` + `ExportJobTask`，无异常 span
- 等待 15s 后重查花名册，两名学员备注仍全空。

## 根因判断（推断未验证）
备注接口只受理异步任务（code=0 不代表写入成功）；花名册两学员与主讲老师均非企微好友（mainTeacherWechatFriend=0），备注写入依赖企微好友关系，非好友场景任务无对象可写或写入被跳过，故花名册无值。

## 未完成
- 对照实验缺失：本班 2 名学员均非好友，无 `mainTeacherWechatFriend=1` 样本；`dws_clazz_user.dws_fuwu_user_teacher_wechat_info` 只读权限不足，未能从库里找好友样本。
- 需一个「小班在读且与老师是企微好友」的学员重复同样两步，才能把「非好友导致」从推断升为已验证。

## 建议
- 若有小班好友样本：调备注接口 → 等任务完成 → 重查花名册 `studentRemark*` 是否出现「测试修改企微备注」。
- 若好友样本也不展示：再查任务表终态与花名册映射字段。

## 2026-11-06 好友关系生效后的最终对照（只读）

**已知（owner 确认）**：该学员企微备注已写成「测试修改企微备注」，在联系方式卡片可见；侧栏「学员备注」显示 `-`。

**重查结果**（`bash /tmp/roster_small.sh` → `/tmp/roster_small_friend.json`，4112 字节）：
- `code=0`，`list=2`
- 学员(7707218286)：
  - `mainTeacherStudentInfo = [{mainTeacherAccountId:40731, mainTeacherWechatFriend:0}, {mainTeacherAccountId:0, mainTeacherWechatFriend:0}]` —— **好友标记仍为 0**（与 owner「现在是好友关系」不一致，取数未刷新/未命中）
  - `studentRemark=''`、`studentRemarkOne=''`、`studentRemarkTwo=''`、`studentRemarkThree=''` —— **四个字段仍全空**

**根因判断**：
- 已验证：备注写入成功（owner 卡片可见 + 接口 code=0/resultStatus=true，trace `435f9289-36a0-452c-ab4d-a071fa7be453.0.3`）。
- 已验证：花名册四个 `studentRemark*` 字段均未返回该备注。
- 结论（推断，需代码确认）：**花名册查询/映射未包含企微备注字段**，属展示缺口，不是写入失败。
- 附带问题：花名册 `mainTeacherWechatFriend` 仍为 0，好友关系取数存在滞后或未命中（`dws_fuwu_user_teacher_wechat_info` 只读无权限，未能核对底层表）。

**建议**：
1. 查 student-center 花名册组装逻辑，确认 `studentRemark/One/Two/Three` 分别来自哪张表/哪个接口（是否企微好友备注），补映射或补查询。
2. 查 `mainTeacherWechatFriend` 的取数来源与缓存刷新时机，避免好友关系生效后仍显示 0。
3. 修复后同一用例复跑：花名册出现「测试修改企微备注」即闭环。

**证据文件**：`/tmp/roster_small_friend.json`、`/tmp/remark-nonfriend.json`、trace `435f9289-36a0-452c-ab4d-a071fa7be453.0.3`、`cbc10b7e-6e85-476c-bf27-b7d73c169982.0.0`。

## 代码定位（student-center / student-data 仓库，只读）

**仓库**：`/Users/gaotu/IdeaProjects/JavaProject/student-center`（接口在 student-center，不在 student-data）

1. **花名册入口**：`student-center-web/.../web/api/small/SmallRenewalController.java:68` `pageRenewal` → `SmallRenewalService.page`，返回 `Map<String,Object>`，字段由数据装配链填充。
2. **wechatRemark 装配**：`student-center-service/.../domain/service/sync/data/small/SmallWechatRemarkQueryServiceImpl.java:89-107`
   - 登录人是该行主讲 → 写 `wechatRemark`（可能为空串）；
   - 否则走 assistant 分支：只有 `assistantAccountId` 与学员有好友备注时才 `put("wechatRemark")`，否则 **`doc.remove("wechatRemark")`**。
   - 本次响应里**完全没有 `wechatRemark` 字段**，与登录账号 177071 非该行主讲、assistant 备注取不到的情况一致。
   - 该字段名是 `wechatRemark`，**不是** `studentRemark*`。
3. **studentRemark/One/Two/Three**：在 student-center/student-data 中未找到赋值点（student-data 仅 `MainTeacherStudentInfo` 有 mainTeacherWechatFriend）。推断这几个字段来自 ES/GAIA 配置的同步文档字段，与企微备注任务不连通。
4. **mainTeacherWechatFriend**：`student-data-service/.../app/service/syncdata/small/SmallClazzUserMainTeacherInfoDataQueryServiceImpl.java:140-153`
   - 取 `DwsFuwuUserTeacherRelation`（表 `dws_fuwu_user_teacher_relation`）按 (userId, mainTeacherAccountId) 查 `wk_friend/wx_friend`；
   - 查不到行 → 固定 `NOT_FRIEND(0)`；
   - 即好友标记来自 dws 离线表，同步滞后或关系未落到该 accountId 时恒为 0。

**根因（推断，待修复验证）**
- 备注展示缺口：花名册前端展示的 `studentRemark*` 与 `SmallWechatRemarkQueryServiceImpl` 产出的 `wechatRemark` 不是同一个字段，后者在本场景被 `remove`。
- 好友标记 0：dws_fuwu_user_teacher_relation 未及时同步/未按登录账号命中。

**最小修复方向（未实施）**
- 在 `SmallWechatRemarkQueryServiceImpl` 的 assistant 分支也写入空串（保持字段存在），并让花名册/前端读取 `wechatRemark`；或把 `wechatRemark` 映射到 `studentRemark*`（需确认前端契约）。
- 好友标记：确认写入 remark 的账号与 `mainTeacherAccountIds` 一致；dws 同步延迟需说明或改为实时查询。
