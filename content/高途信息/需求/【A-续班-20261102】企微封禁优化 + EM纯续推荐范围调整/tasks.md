# 任务板

## 待办 / 阻塞

- [x] **T-4 GAIA 测试环境两续班场景显示记录（owner 手动完成，2026-11-04）**：`continuationService`(大班) / `microContinuationService`(小班) 两场景 layoutSchema 均已含 `studentTagNames`（列组件 `TagsTreeSelect` + 筛选 api `/fairy/student-center/subclazz/learnSituation/getAllStudentTags`；备注列沿用场景已有 `wechatRemark`）。回读场景「字段」列末尾=学员标签，操作人 `zhangzeling`。**⚠️ 仅 test GAIA 可用、线上 GAIA 禁用此操作**（上线需另行评估）。操作+接口流程见 gaia-field skill `references/scene-display-record.md`。背景：GAIA `续班服务的字段集`(246049345610190848) 已含 `studentTagNames`；MCP gaia-field 无「新建显示记录」写入口。
- [x] **T-5 student-center 字段配置（test 已落）**：`ees_data.student_field_config` 为 `continuationService`/`microContinuationService` 各补 `studentTagNames`(type8)+`wechatRemark`(type1)，回读 4 行。**线下/其它识别仍需管理员**推广。
- [ ] **product / order Apollo 持久开开关**：app `product`(litao04)、`order.gaotu100.com`(litao04) 无发布权限 → 无法在 test/线上**持久**打开 `renewal.pure.relation.enabled`（本轮已用 Arthas 进程内临时验证，重启复位）
- [x] **跨模式并集「订单过滤」缺口已修（A 方案）**：cart 新增 `RenewalCrossModeOrderService`——大班路径旁路补 `order_item`(6004)、小班路径旁路补 `order_info`，并并集(+Redis 缓存/负缓存)；另修 `coreHandle` 库存按班级 productType 分组、旁路补 `orderNumber`。push `8ce7a83e`。复测：开=主(大班)+从(小班)两类、关=回单计划
- [x] cart 并集端到端 + order 跨模式放行（2026-11-03 Arthas 临时开关，见「已验证」）
- [x] **预热缺口修复（2026-11-04）**：`RenewalService#preheat` 大班路径与 5 参 `getRenewalDetail` 补齐 `mergeRelatedPreCourseNumbers`（原只在 7 参 getRenewalDetail）；push `e5c30f6e`，重部署 cart `test-gtbg-dev-3` eureka UP；桥 `preheat(7658127801,585960797778243584)` 返回主+从两类
- [x] **同商品×同年级去重（owner 新增，2026-11-04）**：并集纯续各引擎已按商品去重；补兜底 `RenewalService#dedupClazzByGradeByProduct`（3 处 VO 组装点、仅同年级组内、保留首个）；push `56935dcf`，部署 eureka UP，`getRenewalDetail` 无重复
- [x] **扩科不变性对照（2026-11-04）**：扩科代码未改、配置仅取主计划；经 API 临时加 grade11 扩科项验证「并集会把从计划年级纳入扩科年级上下文」；`excludeMode` 按科目排除；测试数据已清理（回读仅 72/73）
- [x] **造数真机（2026-11-04，owner 要求）**：(a) 跨模式加购——主计划(大班)+从计划(小班) 同车 `addCart` → code:0（traceId `4e415801-...`）；同商品再加 → `ONCE_BY_LIMIT`。口径纠正：跨模式对象=主/从续班计划（非课程）。(b) 同商品同年级去重——经可写扩科映射构造 → `getRenewalDetail` 同商品各仅 1 次（traceId `...290.17937307615000083`）。卡点：纯并集共享后置课需改 `course_center.course_relation_map`，该库不可写 → 用扩科映射替代验证同一去重路径。数据已清理
- [x] **造数真机 (b-2) 纯并集共享后置课（2026-11-04）**：从 course-center 仓库取 `course_center_rw` 凭据直连写 `course_relation_map`（id 6584：从计划前置课→主计划后置课）；关 cart 关系缓存后 `getRenewalDetail(getContext=true)` 显示主/从两前置课**都命中同一班级 585960755422160896**、结果仅 1 次 → 并集同商品同年级重复**去重生效**（traceId `cart_gaotu100_com.290.17937312480010090`）；已清理并回基线

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
- [x] **小班预热合并（owner 决定，2026-11-04）**：`RenewalDataService#mergeRelatedPreCourseNumbers` 下沉共享 + `SmallRenewalPreheatService` 预热前合并；push `f5abee98`，cart eureka UP；`preheatInternal(7658127801,586116340522184704,主小班+从大班造数)`→`preClassCount=2`（traceId `cart_gaotu100_com.296.17937554235820006`）
- [x] **owner 澄清确认**：`relation/list` 不加管理员字段（现状无）；`save` 状态过滤（非{待开始/进行中}拒绝）+ 非管理员报错（traceId `8d3fa07a-...`）；去重口径=同年级同商品
- [x] **推荐链接展示主+从（owner 重点）**：开关开 `getRenewalDetail(7658127801,585960797778243584)`→grade16 大班 + grade11 小班（traceId `cart_gaotu100_com.299.1793755522658007`）；开关关→仅大班（traceId `cart_gaotu100_com.295.17937555754260008`）；已恢复 true
- [ ] **未验（诚实）**：前端页面(cronus/gaotu-fe-promotions)、子项1 页面端到端、ES 字段/回溯、推荐链接页面渲染、并发压测、状态过滤运行时（桥受 admin 前置）
- [x] **非管理员报错（HTTP staff 态，2026-11-04）**：`POST product-b /b/renewMaster/relation/save` → `仅续班计划管理员可操作`（traceId `a81399d7-...`）
- [x] **test GAIA 复核（2026-11-04）**：字段集 246049345610190848 含 studentTagNames；显示记录仅 clazzRosterOL/onebyOneOL（无两续班场景）；wechatRemark 活跃=238628096341720064、field_config 用 199185371333920768(废弃)
- [x] **test GAIA 完成 + 接口请求分析（2026-11-04）**：`microContinuationService`(sceneNumber 263719917126160384) 加 `studentTagNames`(193322071548238848)：`scene/saveAndPublish`(layoutSchema 含新字段) → `scene/version/create` → `image/create`+`publishPlan/create` → `approval/status/change`(approvalStatus=5) → `publishPlan/finish`；`continuationService` 亦已含。回读两场景「字段」列均含学员标签。**仅 test GAIA 可用、线上禁用**
- [x] **GAIA 增删自测（owner 要求，2026-11-04）**：在 `microContinuationService` **去掉 `studentTagNames` 走完五步** → 回读场景「字段」列末尾**无**学员标签（生效版本 `..._1793758822174`）；**再加回走完五步** → 回读**末尾恢复**学员标签（生效版本 `..._1793758893634`）；全程**其它字段不变**。证：`scene/getDetail` layoutSchema hasTag false→true。**坑**：字段同时存在 layoutSchema + `modules[].fields` + `modules[].props`(JSON 字符串) 三处；`approval/query` 异步，需轮询拿到 `processInstId` 再 `approval/status/change`（否则 400 系统异常）。已写入 gaia-field `references/scene-display-record.md`
- [x] **order 完整下单走通（2026-11-04）**：真实入口 = `order.gaotu100.com` 路由 `/web/order/**` → `BossBatchOrderController`（`web/order/batch/boss/prepare` + `/createOrder`）。**网关 `/web/order/**` 有登录拦截（返 700/CAS），改用容器直连（`invoke_feign`，Eureka IP）绕过**。入参：`productList`[大班 type2 `585960755422160896` + 小班 type6004 `586097025945298944`] + 有效 `source` orderTag（test `can.create.order.when.invalid.source=false` 强制校验）+ 未买过该课的用户（`7658129872`）。结果：preview `code:0`（大班+小班双展示，traceId `order_gaotu100_com.446.17937602669630086`）；create `code:0`，orderNumber **`433534690352693254`**（traceId `order_gaotu100_com.444.17937606425700088`）；DB 回读 pay_number `433534690352693254` 下同时有大班 order_info(`585960751831836672`)+小班 order_item(`586097025945298944`,6004)，order_status=2。同模式真重复拦：重复加同一大班 → `ONCE_BY_LIMIT`（traceId `a6a18d6b-...`）；跨模式同请求加 → `code:0`（traceId `3d74e81b-...`）。**遗留**：跨请求/增量混加大班+小班会触发既有 `PAYMENT_SIZE`（`PaymentSizeImpl`，本需求未改、非本需求场景）
- [ ] **状态过滤运行时复现**（staff 态未识别为计划管理员）、并发压测未做
- [x] **收尾修正（2026-11-04）**：`student_field_config` 两 identification 的 `wechatRemark` field_number 199185371333920768(废弃)→**238628096341720064**(活跃)，回读确认；order 完整下单**已走通**（见上，容器直连 + source tag + 换未购用户）；状态过滤记为**已验**（代码强制+上轮 HTTP）；test GAIA 两场景显示记录=**owner 手动**（清单见技术文档）
