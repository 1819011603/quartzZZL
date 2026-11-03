# 任务板

## 待办 / 阻塞

- [ ] T-4 GAIA：为 `continuationService`/`microContinuationService` 创建 `studentTagNames` 显示记录（**阻塞**：无新建显示记录入口，需 GAIA 后台/管理员）
- [ ] T-5 student-center：放开两套续班字段配置（**阻塞**：配置/管理员操作）
- [ ] **product-c 下发开关**：Apollo app `product` **无发布权限**（负责人 litao04）→ 无法在 test 打开 `renewal.pure.relation.enabled`，cart 并集端到端无法验证
- [ ] **order 放行开关**：Apollo app `order.gaotu100.com` **无权限**（litao04）→ order 跨模式放行无法在 test 打开
- [ ] cart 并集端到端 + order 跨模式放行（依赖上两条开关，未验证）
- [ ] 跨模式并集代码级风险：cart 大班路径 `coreHandle` 按 `course.filter.type:30,40` 过滤后置课程，小班后置课可能被排除 → 需开关可开后实测

## 已完成

- [x] 4 仓分支 `feature-xuban-pure-relation-20261102`（origin/release,--no-track）;cart 已切统一分支,原 `feature-xuban-expand-exclude` 未提交现场已 `git stash` 保留
- [x] test 建表 `gaotu.renew_master_relation`（`SHOW CREATE TABLE` 已回读）
- [x] 编译:cart / product-server-b / order-app 均 EXIT=0
- [x] 部署 `test-gtbg-dev-3` 并 **eureka UP**:cart `9781f993`、product-b `d99e9162`、product-c `473b26b7`、order `0aaa0f44`
- [x] product-server 关系持久层/服务/控制器 + DTO 下发填充;`/b/renewMaster/list` 支持 numberList
- [x] **修复**:`RenewalMasterRelationController` 改走 `RestTraceResponse`+`RestTraceResponseUtils.handleRequest`（原直返 `RestResponse` 非管理员报「未知错误」→ CCE）;编译通过,push `d99e9162`
- [x] **修复**:`RenewalMasterRelationService#save` 落库 `create_account_id`（登录上下文兜底 accountId）;编译通过,push `116175f00`,重发 product-b（pipeline 1326328）
- [x] **cart 过滤风险核实**:`course.filter.type{30,40}`=课程类别(专题/系列),非授课模式;`coreHandle` 无 `clazzRoomType` 过滤 → 跨模式小班并集课程不被该过滤掉（无误读中的风险,无需改码）
- [x] 端到端测试步骤归档 `e2e.md`
- [x] 文档表结构与接口协议章节

## 已验证（test / test-gtbg-dev-3）

- [x] product-b 桥:非管理员 `save` → `仅续班计划管理员可操作`（人员限制）
- [x] product-b HTTP:白名单账号 `save` 成功;`list` 返回从计划;全量差分（增/软删/软删复位）、上限与状态校验代码路径
- [x] product-b 桥:`listSubNumbers` 开关开返回从计划号（Redis 缓存 + save 后失效）
- [x] product-b 桥:`listRenewalMasterByRenewalNumber` 开关开含 `related_renewMasterNumbers`;开关关不含
- [x] product-c 桥:`listRenewalMasterByRenewalNumber` 开关关 = 无 `related_renewMasterNumbers`（回旧行为）
- [x] 边界（product-b HTTP，白名单 [125756]）：状态非可编辑 → `仅待开始/进行中的续班计划可关联`；超上限10 → `最多可纯续关联10个续班计划`；空白名单非管理员 → `仅续班计划管理员可操作`
