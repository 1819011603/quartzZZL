# V2 功能覆盖验证（老链路 vs V2）— 2026-11-18

版本：cart `feature-renewal-preheat-v2-20261112` @ `0528c192`，TEST test-eco-8，default 集群。飞书文档「V2 功能覆盖矩阵」一节（EaKXdTkzXoJTStxBJH3cX7Qinzh）。

## 结论
- 老链路功能 V2 全覆盖：C 端 25 用例 + B 端 13 用例，**老链路展示的每个 SKU 在 V2 中都在**。
- 无主从关系的计划：old == V2（字段 + 顺序全同）。有主从关系：V2 为超集（新增从计划条目）。
- 唯一字段变化：同一 SKU 被从计划产出在读推荐时，扩展(2)/二讲(3) → 在读(1)，beforeCourseNumber 换成从计划前置课，个别 select 0→1；老链路同 SKU 重复两条（扩展+二讲）V2 去重为一条（D_bc/F/F_bc）。属「纯续 > 扩科 > 加购」设计口径。
- V2 读缓存（上线配置）vs V2 不读缓存：C 端 25/25 一致；B 端 11/13 一致、2 个只差 msg 调试文案。
- 内容一致的 18 个用例原始顺序也一致。

## 方法
三阶段 Apollo（发布号）：old=全 false（233433 / 233847）→ v2=V2 true + cache false（233526 / 233903）→ real=全 true（233608 / 233925，即测前原状态，已回读）。
用例：`cases.json`（C 端 /web/renewal/cart）、`cases_b.json`（B 端 /web/renewal/operation/cart）；抓取 `cap.py`，比对 `cmp.py`（排序后全字段，仅排除 renewalRole/renewalStartTime/renewalEndTime/imageUrl），超集判定 `sup.py`；traceId 在 `index-*.json`。功能清单 `inventory.md`（26 项），样本盘点 `samples.md`。

## 缺口
- 未覆盖：从计划条目换课/换年级（疑似缺陷，代码确认，需写接口验证，待 owner 决定）；大班 23 完全无关联 + 已付学员（缺数据）；小→小 同学员两边前置（缺数据）；gradeDesc/白名单/库存不足/跨学年；跨计划（年级,学科）去重。
- 无法覆盖：从计划失败整页失败（需故障注入）；small.renewal.enabled=false（TEST/PROD 均 true）；小班 23 降级（PROD 无）；userId 缺失/指定学员≠登录人（入口层，与 V2 无关）。

前序覆盖审计（预热 vs 实时、路径效力边界）：`20261118-coverage-gap-audit.md`。

## 风险：从计划条目换课 / 换年级不生效（V2 新增）
- 写：RenewalService.productSelectConfirm（:3177）按 request.renewalNumber 保存；读：RenewalSinglePlanDetailService:1891 按从计划号读；合并结果只带主计划号（:257），条目无来源计划字段。
- 已验证：V2 下 F/A/D/E 从计划条目 canChangeCourse=true（trace 6b392760 / 23445f79 / 88a0095f / 73c11751）；TEST user_renewal_clazz id=1463 是主计划 F 下保存了从计划 D 前置课 18405861174936317 的换课记录（该学员已无有效订单，无法回放）。
- 未验证：换课后刷新不生效。需授权调用 productSelectConfirm 写 1 条记录（测完删除），并带登录态 sid 或走 acl 桥。
- 影响：PROD 有从计划的主计划（大班 4 个、小班 2 个）；无关联计划不受影响。建议：条目带来源计划号，或后端按前置课反查从计划；临时把从计划条目 canChangeCourse 置 false。待所有者决定，未改代码。

## 2026-11-18 23:55 补充：换课缺陷已实测证实（授权写 1 条，已清理）
- 样本：学员 7704848531，主计划 F 589037361072007168，从计划条目前置课 589178070450200576（从计划 589177989139464192），原推荐 SKU 589212673443520512，目标 SKU 589041202037415936（该前置课的合法后置课程 589037985069162496 下的班）。
- 写：acl 桥调 RenewalService#productSelectConfirm，renewalNumber 传主计划号（与前端行为一致），trace cart_gaotu100_com.294.17950173536280141；落库 user_renewal_clazz id=1476（renewal_number=主计划 F）。
- 读回：C 端 trace b93ec034-8249-49dc-ab63-ad1eed20e6f9、B 端 fromC=0 trace 5b987fc9-7b64-4405-8378-1a264a82f7ca、fromC=1 trace 579ac7dd-881f-449b-9caa-8978025f0a88——该条目均仍显示原推荐 589212673443520512，换课不生效（F 有关联，V2 下 C 端不读预热缓存，实时计算，排除缓存干扰）。
- 清理：同一接口 status=0 type=2 反向删除（trace cart_gaotu100_com.292.17950173993550146），回读 user_renewal_clazz 该学员仅剩原有 1468/1469；恢复后 C 端结果与换课前一致（trace d9540f8f-8c49-4750-ab4e-7efdae91e5e4）。
- 未做：按从计划号写入的对照实验（授权限写 1 条已用掉）；结论基于代码 key 不一致 + 主计划号写入路径实测，因果链已闭合。
- 结论：缺陷证实。是否修复由所有者决定（建议见上文）。
