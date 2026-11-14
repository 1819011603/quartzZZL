# 2026-11-15 造数补验：批量路径从计划条目（role=2）写入 + 主从合并 + 回退态读取（W1）

> 回应 owner「数据你可以使用造数项目验全一点」：补齐上轮唯一缺口——批量预热路径没有直接
> 验证到从计划条目（renewalRole=2）的写入（当时从计划对该批用户无可售商品，靠单用户
> TID 17946706331600008 + 同代码路径论证）。

## 样本来源：复用存量 fixture（造数 skill 铁律「先复用现成」优先于全新造数）

- 样本 = 上轮单用户验证已实证能产生 role=1+2 的存量计划 `589037361072007168`
  （1 主 + 4 从：589037362856683520 / 589721954597011456 / 589177989139464192 / 589178077949657088，
  5 门前置课去重已付用户仅 6 人，规模可控）。
- 全新造数路径评估后不选：造数项目缺「主从关联 save」「购课下单」两个 scenario
  （可由 product-b 接口 + order 直连补，但链路 20+ 分钟且带可售门槛风险）；
  复用存量数据 role=1+2 产出能力已实证，验证等价且更稳。已登记 fixture registry（plan:589037361072007168）。
- Job 完整入口（isTestData/activity 过滤 + 计划循环）已由上轮真实计划 545361759016388608 验证；
  本计划 is_test=1、无联报活动，Job 入口会过滤，故走 `RenewalV2Service#preheatByRenewalNumber`
  （Job 过滤后调用的批量预热本体，全量用户遍历同一段代码）——入口逻辑不重复验，补的是数据场景。

## 验证矩阵（test-eco-8 @3b49fda6，pod cart-gaotu100-com-7b989f97d-7nw7q）

前置开关（回退态读取条件齐备）：`renewal.recommend.v2.enabled=false`（老链路）、
`preheat.cache.enabled=true`（读缓存）——均为 TEST 当前值，未动。

1. Apollo：`renewal.preheat.v2.enabled` false→true + `renewal.preheat.v2.prefix.enabled` true→false
   （写老 key 供老链路读）→ 发布 release `20261115020220`。
2. 桥调 `RenewalV2Service#preheatByRenewalNumber("589037361072007168")` → 正常返回（void）。
3. **Redis 老 key 验证（arthas，pod 内 StringRedisTemplate）**：
   - `renewal:preheat:589037361072007168:7704848531` = **5 条目：1 主（role=1）+ 4 从（role=2）**，
     含 product_type=51 组合条目完整结构（班号/老师/价格/norm_desc_list）——**批量路径 role=2 写入 +
     主从合并结构直接实证**；
   - 7704848533/7704850492：仅主条目 role=1（只购主前置课，符合预期）；
   - 7704850493/7704850494/7714163148：null（只购从计划前置课——`queryPlanUserIds` 只处理主计划学员，
     符合设计「只处理 A 计划自己的学员，不遍历从计划学员」）。
4. **回退态老链路读取（C 端 `/web/renewal/cart`，appointUserId=7704848531，
   TID `cart_gaotu100_com.292.17946794980070108`）**：
   - `code=0` 无异常（P0 不回归再确认，对照 c98c4158 同场景 NPE）；
   - 高一（grade 31）6 条：`renewalRole=1`×1（数学大班主计划）+ `renewalRole=2`×3（英语从计划 +
     去重同名数学×2）+ `renewalRole=null`×2（老链路实时补充条目，null 兼容正常）；
   - 缓存中 51 组合条目（QA-小班组合能力集成）被老链路判空安全跳过（上轮已验行为）。
5. 恢复：两开关发布 release `20261115020519` 回 `v2=false / prefix=true`，
   桥回读 `isPreheatV2Enabled=false` 确认。

## 结论

上轮遗留的「批量路径 role=2 写入缺直接证据」缺口**关闭**：批量预热对含可售从计划的场景，
主+从合并值（role=1/2 混合）正确写入老 key，回退态老链路读取该值 code=0、条目正确展示、
51 条目安全跳过。至此批量路径与单用户路径（TID 17946706331600008）证据对齐。

## 未覆盖（如实）

- Job 入口对「从计划有可售商品」计划的完整过滤链路（需 is_test=0 且有联报活动的此类计划；
  本计划被 is_test/无联报过滤，入口逻辑由上轮 545361759016388608 验证，数据场景由本轮补齐，
  两者拼合覆盖完整链路）。
- 造数项目全新链路（clone+build+关联+下单+支付）未执行（按铁律优先复用；能力缺口=关联 save 与
  购课下单无现成 scenario）。
