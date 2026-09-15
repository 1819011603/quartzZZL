---
title: 续班预报名使用膨胀券 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

> 只保留仍能解释当前设计的决定。最终口径以 README/apis/verify/tasks 为准。

## 2026-09-15

- **`presaleOrderTime` 口径由「取最早」订正为「取最新」**，依据需求《大班课字段及数据指标》
  「续班服务-花名册」第 75 行：「如果预报名多个班级，取最新下单」「如果下单多个膨胀券，取最新下单」
  「两种方式都配置，取最新时间」。原实现是**有意**取最早（注释写「语义上取学员首次预报名下单的时间」），
  与需求相反。共改 6 处 `min → max`，分布在 4 个文件——增量链路与全量(回溯)链路、大班与小班都必须同步改，
  只改一边会让 ES 值在两条链路之间来回跳：
  `PresaleSubjectServiceImpl#calcPresaleOrderTime`、`PresaleSubjectDataQueryServiceV2#getPresaleOrderTime`、
  `SmallPresaleSubjectServiceImpl#getPresaleOrderTime`、`SmallPresaleStatusDataQueryServiceV2#getPresaleOrderTime`。
  `RenewalOrderTimeQueryService#getLatestOrderTime` 未动（内部本就是 `max`）。4 个钉住旧口径的单测同步改名并翻转期望值。
  **存量数据不会自动纠正**，需跑回溯才会刷成新口径；当前券表仅 2 个学员且无跨形态并存数据，实际无存量待刷。
  待与马胜确认原「取最早」是否另有未写进注释的上下文。
- **发现「取并集」规则零数据覆盖**：券表与订金班表按「学员+学年+学期」交集为 0 行，
  这条需求规则从未被真实数据走过——也是上面口径分歧长期未暴露的原因。造数方案记入 [[verify]]。
- `listScopeByCouponSkuNumbers` 入参最终定为裸 `List<Long>`，不用包装 DTO：根因是 controller 用
  `implements XxxFeignClient` 复用接口方法时必须在实现类自己的方法上重声明 `@RequestBody`/`@PostMapping`，
  Spring 不从接口继承参数注解，漏了会静默退化成表单绑定；此前怀疑的 FastJson/JaCoCo 冲突是误诊，见 [[apis]]。
- 一个预报名活动只应绑定一个续班计划：`578842182125903872` 曾被误绑两个，已删除无效的那个（详见 [[verify]]）。
- `RenewalServiceImpl#listRenewalMasterByNumbers` 遗漏前置课关系、course-center 的 `calculate_renewal_type`
  测试值配错，两处都是既有代码/数据问题而非本需求引入，顺手修复，是否合并到 master 待评估（见 README 下一步）。

## 2026-09-14

- 复核可用券基线：`total=40`，全部 `couponStatus=1` + `saleStatus=2` + `selectable=true`，
  常用 5 张记入 [[verify]]。当前**无售罄券**，T-33 只能靠造数或买满小库存券解锁。
- 确认下单所需的 `test` 泳道运行 master 镜像，不含本需求代码（接口 404 / 反射找不到实现类）。
  券数据在 coupon-a 跨泳道共享，缺的是代码，下单验证前必须先发版到 `test`。

- B/C 端默认只展示 `couponStatus=1` 且 `saleStatus=2` 的券；两个白名单均支持 Apollo 配置，状态为空不展示。
- coupon-a 已支持 `couponStatuses`/`saleStatuses` 服务端过滤，student-center 直接透传条件并删除本地二次过滤，保证分页 `total` 与列表一致。
- 采用服务端过滤，因为分页后本地过滤会导致总数和页内容不一致。

## 2026-09-11

- 券有两个正交状态：`couponStatus` 表示券本身状态，`saleStatus` 表示商品售卖状态；展示必须同时满足两个白名单。
- 建券人通过 `creatorEmployeeId -> accountId -> CAS displayName` 两跳批量转换，查不到时保留工号。
- 活动保存增加售罄券和满班课程服务端校验，避免只依赖前端不可选状态。

## 2026-09-10

- B 端膨胀券 tab 始终展示；`renewMasterNumber` 只控制三者交集范围过滤，没有可展示券时返回空列表。
- 三者交集统一由 product-server 的 `PreOrderCouponIntersectService` 计算，其他服务只消费结果。
- promotion 的 B/C 两条读取链路都必须补齐券字段与 scopes，跨服务返回使用扁平行和 `RestTraceResponse<T>` 信封。

## 2026-09-09

- 券信息实时读取 coupon-a，不落业务库、不使用 mock；`couponStatusDesc` 由本地枚举维护。
- 券范围表由 promotion-b 在事务内调用 product-b 的专用接口写入，Feign 失败回滚活动，避免循环调用。
- 范围唯一键按活动级 `(activity_number, grade_code, subject_code)`，允许同一张券跨活动使用。

## 2026-09-08

- 膨胀券商品类型定为 `8014`；券不参与满赠。
- 落地页继续使用 `/preSignUp`，不按活动形式拆分 path。
- order 侧范围限定为加购与购物车总价；订单后续链路和 student-data 收数由对应团队负责。
