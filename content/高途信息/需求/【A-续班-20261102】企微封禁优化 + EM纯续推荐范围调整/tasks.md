# 任务板

## 待办 / 阻塞

- [ ] T-4 GAIA：为 `continuationService`/`microContinuationService` 创建 `studentTagNames` 显示记录（**阻塞**：无新建显示记录入口，需 GAIA 后台/管理员）
- [ ] T-5 student-center：放开两套续班字段配置（**阻塞**：配置/管理员操作）
- [ ] **product / order Apollo 持久开开关**：app `product`(litao04)、`order.gaotu100.com`(litao04) 无发布权限 → 无法在 test/线上**持久**打开 `renewal.pure.relation.enabled`（本轮已用 Arthas 进程内临时验证，重启复位）
- [ ] **跨模式并集「订单过滤」缺口**（2026-11-03 实测）：cart 大班路径订单查询 `listByCourseNumbersAndUserIdAndStatus` 只读 `order_info`(大班)、小班路径 `listBySpuNumbersAndUserIdAndStatus` 只读 `order_item`(6004) → 合并进来的另一模式前置课被订单过滤剔除、不产出报价。需补齐另一模式订单查询（属**主流程**，与「不改主流程」口径冲突，**待决策**）
- [x] cart 并集端到端 + order 跨模式放行（2026-11-03 Arthas 临时开关，见「已验证」）

## 已完成

- [x] 4 仓分支 `feature-xuban-pure-relation-20261102`（origin/release,--no-track）;cart 已切统一分支,原 `feature-xuban-expand-exclude` 未提交现场已 `git stash` 保留
- [x] test 建表 `gaotu.renew_master_relation`（`SHOW CREATE TABLE` 已回读）
- [x] 编译:cart / product-server-b / order-app 均 EXIT=0
- [x] 部署 `test-gtbg-dev-3` 并 **eureka UP**:cart `9781f993`、product-b `d99e9162`、product-c `473b26b7`、order `0aaa0f44`
- [x] product-server 关系持久层/服务/控制器 + DTO 下发填充;`/b/renewMaster/list` 支持 numberList
- [x] **修复**:`RenewalMasterRelationController` 改走 `RestTraceResponse`+`RestTraceResponseUtils.handleRequest`（原直返 `RestResponse` 非管理员报「未知错误」→ CCE）;编译通过,push `d99e9162`
- [x] **修复**:`RenewalMasterRelationService#save` 落库 `create_account_id`（登录上下文兜底 accountId）;编译通过,push `116175f00`,重发 product-b（pipeline 1326328）
- [x] **cart 过滤风险核实**:`course.filter.type{30,40}`=课程类别(专题/系列),非授课模式;`coreHandle` 无 `clazzRoomType` 过滤 → 跨模式小班并集课程不被该过滤掉（无误读中的风险,无需改码）
- [x] **小班主计划核实**:`SmallRenewalCoreService`/`SmallRenewalContextBuilder` 链路无大班/小班模式或计划归属过滤（`ProductType` 分支仅 单课6004/组合51；白名单缺项降级非丢弃；一致性校验仅剔查不到课者）→ 并入的大班课不被丢弃，无需改码
- [x] 端到端测试步骤归档 `e2e.md`
- [x] 文档表结构与接口协议章节

## 已验证（test / test-gtbg-dev-3）

- [x] product-b 桥:非管理员 `save` → `仅续班计划管理员可操作`（人员限制）
- [x] product-b HTTP:白名单账号 `save` 成功;`list` 返回从计划;全量差分（增/软删/软删复位）、上限与状态校验代码路径
- [x] product-b 桥:`listSubNumbers` 开关开返回从计划号（Redis 缓存 + save 后失效）
- [x] product-b 桥:`listRenewalMasterByRenewalNumber` 开关开含 `related_renewMasterNumbers`;开关关不含
- [x] product-c 桥:`listRenewalMasterByRenewalNumber` 开关关 = 无 `related_renewMasterNumbers`（回旧行为）
- [x] 边界（product-b HTTP，白名单 [125756]）：状态非可编辑 → `仅待开始/进行中的续班计划可关联`；超上限10 → `最多可纯续关联10个续班计划`；空白名单非管理员 → `仅续班计划管理员可操作`
- [x] **端到端（Arthas 临时开关）**：① product-c 下发含 `related_renewMasterNumbers`（开关开）/无（关）；② cart 透传 `related_renew_master_numbers`；③ cart 合并日志 `EM pure relation merged courseNumbers ... size=2`（开）/无（关）；④ order 大班2+小班6004 同课程/同班级 → 放行，同模式2+2 同课程 → `SAME_COURSE` 拦，开关关 → 拦。**测后已复位**（product-c 两 pod / order pod 置 false 回读；cart 开关、product-b 白名单 Apollo 恢复并发布）
