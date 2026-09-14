---
title: 续班预报名使用膨胀券 · 决策摘要
tags: [需求, 日志]
---

# 决策摘要

> 只保留仍能解释当前设计的决定。最终口径以 README/apis/verify/tasks 为准。

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
