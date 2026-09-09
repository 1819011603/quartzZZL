---
title: 续班预报名使用膨胀券 · 链接中心
tags: [需求, 链接]
---

# 链接中心

> 这个需求的所有外部入口。新链接一律追加到这里，别散在正文。

## 需求与方案

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 需求wiki节点 | 【续班】预报名使用膨胀劵（父节点，下挂 5 份子文档） | https://gaotuedu.feishu.cn/wiki/W3SSwxr1AieysikF0D3csT4EnBh | 2026-09-08 |
| PRD | 【PRD】续班预报名使用膨胀券 V1.0（2026-08-25） | https://gaotuedu.feishu.cn/wiki/N58DwzUDoi3sK3k1nCqcPOBMn3d | 2026-09-08 |
| PRD | 膨胀券（定金膨胀）购买 PRD —— 券本体的售卖与配置 | https://gaotuedu.feishu.cn/wiki/UJf9w72zoinjMSk63DNcKkRTnOc | 2026-09-08 |
| 技术反讲 | 预报名使用膨胀劵-**后端反讲文档**（v0.2，主文档） | https://gaotuedu.feishu.cn/wiki/RC4DwjusfinikRk9IM9c88l1nZW | 2026-09-08 |
| 技术反讲 | 预报名整体技术方案 | https://gaotuedu.feishu.cn/wiki/BLlgwXUSniQ2DpkpKnmc8MeCnWe | 2026-09-08 |
| 调研 | 预报名技术依赖梳理 | https://gaotuedu.feishu.cn/wiki/EkoFwKIVoi89U9kaYtic7l2gnIb | 2026-09-08 |
| 调研 | 预报名前置 —— 需求解读与现状梳理（逐仓库代码核对结论） | https://gaotuedu.feishu.cn/wiki/ChowwoNm7iiPZukHmGDcVs7inlb | 2026-09-08 |
| 前端反讲 | 续班预报名使用膨胀券-前端 EES & C 端部分 | https://gaotuedu.feishu.cn/wiki/GYLCw7WW6ikq1Ak30omcpK3XnIg | 2026-09-08 |
| 前端反讲 | 预报名使用膨胀券—前端续班管理 & 预报名管理部分 | https://gaotuedu.feishu.cn/wiki/ZxPJwmDbaiNwPrkLdRFcDCQknzc | 2026-09-08 |
| 待办表 | 教学服务迭代待办 ·【预报名】预报名支持膨胀劵（21 条） | https://gaotuedu.feishu.cn/wiki/VgbOwav5TigsvDkr0cYcVnF6nsh?table=tblWl0uXntBAdIHq | 2026-09-08 |
| 其他 | 4. 订单域领域事件 | https://gaotuedu.feishu.cn/wiki/VHm7woAzyihahKkXGDvct7tbndd | 2026-09-08 |
| 其他 | 开发操作SOP | https://gaotuedu.feishu.cn/wiki/IJ5VwuzBciJ8uNkY3fOcYNpYnuh | 2026-09-08 |

## spec（每仓库一份，按上线依赖排序）

> 路径统一 `specs/004-xuban-pre/tech_spec.md`，分支统一 `feature-xuban-pre`。

| 类型 | 仓库 | 链接 | 记录日期 |
|---|---|---|---|
| spec | promotion | https://git.baijia.com/gaotu/promotion/-/blob/feature-xuban-pre/specs/004-xuban-pre/tech_spec.md | 2026-09-08 |
| spec | product-server | https://git.baijia.com/gaotu/product-server/-/blob/feature-xuban-pre/specs/004-xuban-pre/tech_spec.md | 2026-09-08 |
| spec | order | https://git.baijia.com/gaotu/order/-/blob/feature-xuban-pre/specs/004-xuban-pre/tech_spec.md | 2026-09-08 |
| spec | cart | https://git.baijia.com/gaotu/cart/-/blob/feature-xuban-pre/specs/004-xuban-pre/tech_spec.md | 2026-09-08 |
| spec | student-center | https://git.baijia.com/gaotu/yunying_workbench/student-center/-/blob/feature-xuban-pre/specs/004-xuban-pre/tech_spec.md | 2026-09-08 |
| spec | student-data | https://git.baijia.com/gaotu/yunying_workbench/student-data/-/blob/feature-xuban-pre/specs/004-xuban-pre/tech_spec.md | 2026-09-08 |
| spec | **promotion-app**（反讲文档漏掉的第六个服务，满赠校验在此） | https://git.baijia.com/gaotu/promotion-app/-/blob/feature-xuban-pre/specs/004-xuban-pre/tech_spec.md | 2026-09-08 |
| 其他 | ~~TODO-券信息接口~~（历史文件名，🔴 **已过时**：电商接口已于 2026-09-09 接通，mock 已全部删除，见 [[links]]「电商膨胀券接口」段的真实接口文档） | https://git.baijia.com/gaotu/yunying_workbench/student-center/-/blob/feature-xuban-pre/specs/004-xuban-pre/TODO-券信息接口.md | 2026-09-08 |

## 开发与测试

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| TAPD | 续班预报名增加膨胀券形式 · story 1122531521001392077 | https://www.tapd.cn/tapd_fe/22531521/story/detail/1122531521001392077?from_iteration_id=1122531521001014792 | 2026-09-08 |
| case |  |  |  |
| MR |  |  |  |
| 接口文档 |  |  |  |

## 上线

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 上线checklist |  |  |  |
| 发布计划 |  |  |  |
| 工单 |  |  |  |

## 跨会话检索锚点

> 需求会改名，这些 ID / 分支名不会。`rg -l "<锚点>" 需求根目录` 即可反查到本目录。

- **分支名（6 仓库统一）**：`feature-xuban-pre`
- **spec 目录名**：`004-xuban-pre`
- 需求 wiki 节点 token：`W3SSwxr1AieysikF0D3csT4EnBh`
- 后端反讲 token：`RC4DwjusfinikRk9IM9c88l1nZW`
- PRD token：`N58DwzUDoi3sK3k1nCqcPOBMn3d`
- 待办表：base `VaqXbgkElanMhbs8ZCmcnNtJnog` / table `tblWl0uXntBAdIHq`
- TAPD story_id：`1122531521001392077`（workspace `22531521`，iteration `1122531521001014792`）

## 只存链接，不镜像明细

这几处的**真相源都在外部**，本地抄一份必然过期：

- **待办表**（阶段 初评/细评/技术反讲/开发阶段/测试阶段，状态 TODO/DOING/DONE）→ 飞书多维表格
- **反讲 TODO** → 飞书后端反讲文档
- **TAPD 工时任务** → TAPD 服务端，用 `tapd-task` 现查
- **case** → case 平台，用 `banshan-case` 现查

## Apifox

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 其他 | Apifox 项目（自测接口导入到这里，按需求建目录） | https://app.apifox.com/project/8815485 | 2026-09-09 |

> 导入源（择一）：
> - **`apifox-openapi.json`（推荐）** —— OpenAPI 3.0，9 接口一次性导入，带分组与实测示例
> - [[curl]] —— cURL 逐条粘，仅临时试单条时用
>
> `apifox-mcp-server` 只有只读工具，无法由 Claude 写入 Apifox，故只能手动导入。

## 电商膨胀券接口（券信息权威源）

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 接口文档 | coupon-a 膨胀券列表分页查询 `POST /feign/expandCoupon/queryList` | https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5453936&appId=coupon-a.gaotu100.com&branchName=feature-expand-coupon | 2026-09-09 |
| 接口文档 | coupon-a 按膨胀券商品订单项批量查券 `POST /feign/expandCoupon/queryByOrderItems` | https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=5453954&appId=coupon-a.gaotu100.com&branchName=feature-expand-coupon | 2026-09-09 |

**依赖**：`com.gaotu:coupon-a-client:1.3.15`（分支 `feature-expand-coupon`）

> **契约以 jar 为准，不以任何文档为准**：
> `com.gaotu.coupon.a.client.feign.ExpandCouponFeignService#queryList`
> 入参 `ExpandCouponQueryRequest` / 出参 `ExpandCouponPageDto<ExpandCouponDetailDto>`。
> 反编译：`mcp java-decompiler java_decompile_class`。
>
> 券状态：**1 使用中 / 2 已失效 / 3 审核中 / 4 已暂停**（无「待开始」）。
> 券名称是**左匹配**模糊（`name like '关键字%'`），不是全模糊。

## promotion-management（B 端入口服务）

| 类型 | 标题 | 链接 | 记录日期 |
|---|---|---|---|
| 其他 | promotion-management 仓库（本需求新增的第 7 个仓库） | http://git.baijia.com/gaotu/promotion-management | 2026-09-09 |

> serviceCode `gaotu_promotion_management` · appId `promotionmanagement.gaotu100.com`
> 链路位置：`OES 页面 → promotion-management → promotion-b`
