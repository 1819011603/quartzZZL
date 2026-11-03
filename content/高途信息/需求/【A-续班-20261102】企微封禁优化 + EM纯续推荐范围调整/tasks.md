# 任务板

## 待办 / 阻塞

- [ ] T-4 GAIA：`续班服务的字段集`(246049345610190848) 已含 `studentTagNames`(学员标签)；`continuationService`/`microContinuationService` 无独立场景（为 student-center 场景页编码）。**待管理员**：为两续班服务场景补/放字段（含学员标签）；如需「修改企微备注」列，需先建 GAIA 字段（`gaia_field_list 企微备注` 命中 0）
- [x] **T-5 student-center 字段配置（test 已落）**：`ees_data.student_field_config` 为 `continuationService`/`microContinuationService` 各补 `studentTagNames`(type8)+`wechatRemark`(type1)，回读 4 行。**线下/其它识别仍需管理员**推广。
- [ ] **product / order Apollo 持久开开关**：app `product`(litao04)、`order.gaotu100.com`(litao04) 无发布权限 → 无法在 test/线上**持久**打开 `renewal.pure.relation.enabled`（本轮已用 Arthas 进程内临时验证，重启复位）
- [x] **跨模式并集「订单过滤」缺口已修（A 方案）**：cart 新增 `RenewalCrossModeOrderService`——大班路径旁路补 `order_item`(6004)、小班路径旁路补 `order_info`，并并集(+Redis 缓存/负缓存)；另修 `coreHandle` 库存按班级 productType 分组、旁路补 `orderNumber`。push `8ce7a83e`。复测：开=主(大班)+从(小班)两类、关=回单计划
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
- [x] **cart 实际报价（造数）**：学员 `7658127801`（主/从前置课均有 paid 订单）→ 初测小班从计划报价缺失；**A 方案修复后复测：开关开=主(大班)+从(小班 6004)两类纯续，开关关=回单计划**。测后 product-c/cart 开关复位
- [x] **联测 cart 加购→下单（跨模式）**：补部署 **order-b**（`orderComponent`/`CartSameClazzOrCourseImpl` 校验入口，此前只部署 gaotu_order）；真机 `POST /bgwApi/orderComponent/b/cart/addCart`：大班班+小班班同车 → `code:0`（traceId `7c22f266-...`）；同模式真重复 → `SAME_CLAZZ`+`SAME_COURSE`（traceId `81c9bc97-...`）。**未覆盖**：跨模式放行真机（test 计划大小班后置班 clazz/course 均不同，无冲突；逻辑层已验）。测后开关复位、购物车清理
- [x] **开关默认改 true（通用口径）**：product-server/cart/order 5 处 `@Value(...:true)`；push `ab120d4e5`/`4e126df5`/`e464fa98bd`；部署 product-b/product-c/cart/order/order-b 全 eureka UP。**验证**：不配开关即生效（product-c 下发含 related、cart 主+从）；cart Apollo `false` → 回单计划（回滚可用）
