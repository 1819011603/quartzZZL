> 数据全部为 TEST 环境真实 ID，取自造数台账与覆盖报告，未编造。  
> 每个场景给出「续班计划号 / 学员ID / 班级或课程 / 验证功能 / 操作步骤 / 预期结果」，最后一列留空供你填。  
> 环境：TEST，泳道 `test-eco-8`。前端入口路径一般形如 `/web/renewal/cart?renewalNumber=\<计划号\>&userId=\<学员\>`（B 端可能不同，按你习惯的入口点即可）。

> **「在读前置班」口径说明**  
> 大班 bizId 取自 `gaotu.clazz.biz_number`（字母+数字）；小班 bizId 取自 `course_center.clazz.biz_number`（纯数字，且等于班级号本身）。  
> **小班特别注意**：小班学员在 `gaotu.subclazz_student` 和 `course_center.clazz_student` 两张关系表里都是 **0 条记录**，所以小班的「在读」只能靠 `gaotu.order_item` 已支付订单（`order_status=2`）佐证，没有学员-班级关系行可以交叉验证。大班两边都有：`subclazz_student` 关系行（`status=1`）+ 订单。

---

### 1. 老链路-大班联报 23

| 项 | 值 |
|-|-|
| 续班计划号 | `591020372877623296` |
| 学员ID | `7746793735`（备用 `7746793736`） |
| 班级/课程 | 联报活动 `591020757501380608`；后置班 A `591020573128196096`、后置班 B `591020573595860992`；前置班 `591020573289676800`,15YW26CHB911002 |
| 在读前置班（bizId） | 大班前置班 `591020573289676800` → bizId `15YW26CHB911002`（M23前置班语文1117，五年级，在读）  <br/>大班前置班 `591020573124001792` → bizId `15YW26CV6011002`（S2前置班语文1117，五年级，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=591020372877623296&userId=7746793735) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=591020372877623296&userId=7746793735&fromC=1) |
| 验证功能 | 大班联报（productType=23）单品形态推荐 |
| 操作步骤 | 确认 V2 开关**关闭** → 以该学员打开该计划的续班购物车页 |
| 预期结果 | 出现 1 条联报商品（productType=23），活动号 591020757501380608，年级 15（五年级语文），未报名标记 allSignUp=0 |
| 实际结果 |  |

### 2. 老链路-大班从计划 2（班级 2）

| 项 | 值 |
|-|-|
| 续班计划号 | `591020374322561024` |
| 学员ID | `7746793735`（备用 `7746793736`） |
| 班级/课程 | 后置班 `591020573457448960`；前置班 `591020573124001792`,15YW26CV6011002 |
| 在读前置班（bizId） | 大班前置班 `591020573124001792` → bizId `15YW26CV6011002`（S2前置班语文1117，五年级，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=591020374322561024&appointUserId=7746793735&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=591020374322561024&appointUserId=7746793735&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=591020374322561024&userId=7746793735) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=591020374322561024&userId=7746793735&fromC=1) |
| 验证功能 | 大班普通班级（productType=2）推荐 |
| 操作步骤 | V2 关闭 → 以该学员打开该计划 |
| 预期结果 | 1 条 productType=2 的商品，年级 15，未报名 |
| 实际结果 |  |

### 3. 老链路-小班 6004

| 项 | 值 |
|-|-|
| 续班计划号 | `586116340522184704` |
| 学员ID | `7746791494`（备用 `7746791496`） |
| 班级/课程 | 前置 SKU `586084334251927552`；该计划挂大班从计划 `585960797778243584` |
| 在读前置班（bizId） | 小班前置班 `586084334251927552` → bizId `586084334251927552`（dcg-小班扩科排除-数学，纯数字 bizId，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=586116340522184704&appointUserId=7746791494&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=586116340522184704&appointUserId=7746791494&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=586116340522184704&userId=7746791494) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=586116340522184704&userId=7746791494&fromC=1) |
| 验证功能 | 小班课（productType=6004）推荐 + 扩科展示 |
| 操作步骤 | V2 关闭 → 以该学员打开该计划 |
| 预期结果 | 出现小班课商品 + 若干扩科项；不报错 |
| 实际结果 |  |

### 4. 老链路-预热写入后命中缓存

| 项 | 值 |
|-|-|
| 续班计划号 | `591020372877623296` |
| 学员ID | `7746793735` |
| 班级/课程 | 前置课 `591020433489467393` → 联报 `591020757501380608` / 班 `591020573128196096` |
| 在读前置班（bizId） | 大班前置班 `591020573289676800` → bizId `15YW26CHB911002`（M23前置班语文1117，五年级，在读）  <br/>大班前置班 `591020573124001792` → bizId `15YW26CV6011002`（S2前置班语文1117，五年级，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=591020372877623296&userId=7746793735) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=591020372877623296&userId=7746793735&fromC=1) |
| 验证功能 | 预热写缓存后，C 端读取命中预热数据（不重复计算） |
| 操作步骤 | V2 关闭 → 先由我执行一次该学员的预热（或你触发计划级预热）→ 再打开该学员的续班页 |
| 预期结果 | 页面返回与预热内容一致（联报 23 + 对应班级），不出现空推荐 |
| 实际结果 |  |

### 5. P1 修复-小班命中预热缓存后扩科展示

| 项 | 值 |
|-|-|
| 续班计划号 | `586116340522184704` |
| 学员ID | `7746791494` |
| 班级/课程 | 前置 SKU `586084334251927552` |
| 在读前置班（bizId） | 小班前置班 `586084334251927552` → bizId `586084334251927552`（dcg-小班扩科排除-数学，纯数字 bizId，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=586116340522184704&appointUserId=7746791494&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=586116340522184704&appointUserId=7746791494&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=586116340522184704&userId=7746791494) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=586116340522184704&userId=7746791494&fromC=1) |
| 验证功能 | **P1 修复核心**：命中预热缓存后，扩科/加购不丢失 |
| 操作步骤 | V2 关闭 → 先预热该学员（写 key `renewal:preheat:586116340522184704:7746791494`）→ 再打开续班页 |
| 预期结果 | 命中缓存时仍展示 **1 条纯续 + 4 条扩科**，与未命中缓存时结果一致 |
| 实际结果 |  |

### 6. 关联缓存命中路径

| 项 | 值 |
|-|-|
| 续班计划号 | `591020372877623296` |
| 学员ID | `7746793735` |
| 班级/课程 | 从计划 `591020374322561024`(pt2)、`588506246722727936`(pt6004) |
| 在读前置班（bizId） | 大班前置班 `591020573289676800` → bizId `15YW26CHB911002`（M23前置班语文1117，在读）  <br/>大班前置班 `591020573124001792` → bizId `15YW26CV6011002`（S2前置班语文1117，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=591020372877623296&userId=7746793735) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=591020372877623296&userId=7746793735&fromC=1) |
| 验证功能 | 计划关联查询 60s 本地缓存命中（第二次请求不再走下游 RPC） |
| 操作步骤 | 连续两次打开同一个续班页（间隔 <60s） |
| 预期结果 | 两次结果完全一致；第二次响应明显更快（无关联查询 RPC） |
| 实际结果 |  |

### 7. 关联缓存未命中路径

| 项 | 值 |
|-|-|
| 续班计划号 | `591020372877623296` |
| 学员ID | `7746793736` |
| 班级/课程 | 同上 |
| 在读前置班（bizId） | 大班前置班 `591020573289676800` → bizId `15YW26CHB911002`（M23前置班语文1117，在读）  <br/>大班前置班 `591020573124001792` → bizId `15YW26CV6011002`（S2前置班语文1117，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=591020372877623296&appointUserId=7746793736&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=591020372877623296&appointUserId=7746793736&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=591020372877623296&userId=7746793736) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=591020372877623296&userId=7746793736&fromC=1) |
| 验证功能 | 缓存首次未命中时正常回源，结果正确 |
| 操作步骤 | 等待 >60s（缓存过期）后首次打开 |
| 预期结果 | 结果与缓存命中时一致，无报错、无缺项 |
| 实际结果 |  |

### 8. 组合 51 在老链路真实入口返回

| 项 | 值 |
|-|-|
| 续班计划号 | `589721954597011456` |
| 学员ID | `7704848531`（备用 `7714162980`） |
| 班级/课程 | 组合 SKU `589762111522013184`；子班 SKU `589048589437788160`、`587755482459084800` |
| 在读前置班（bizId） | 小班前置班 `589047959231029248` → bizId `589047959231029248`（50191-1106-数学小班-pre，纯数字 bizId，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=589721954597011456&appointUserId=7704848531&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=589721954597011456&appointUserId=7704848531&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=589721954597011456&userId=7704848531) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=589721954597011456&userId=7704848531&fromC=1) |
| 验证功能 | 小班组合商品（productType=51）能否正常返回 |
| 操作步骤 | V2 关闭 → 以该学员打开该计划 |
| 预期结果 | 出现 1 条 productType=51 的组合商品，年级 11，价格 0 |
| 实际结果 |  |

### 9. V2-C 端 23+2+6004 跨类型合并（需开 V2 开关）

| 项 | 值 |
|-|-|
| 续班计划号 | `591020372877623296` |
| 学员ID | `7746793735` |
| 班级/课程 | 联报 `591020757501380608`；大班从 `591020573457448960`；小班从 `588506155490336768` |
| 在读前置班（bizId） | 大班前置班 `591020573289676800` → bizId `15YW26CHB911002`（M23前置班语文1117，在读）  <br/>大班前置班 `591020573124001792` → bizId `15YW26CV6011002`（S2前置班语文1117，在读）  <br/>小班前置班 `588506026511294464` → bizId `588506026511294464`（【造数】小班续班前置-小学数学-1103-1831，纯数字 bizId） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=591020372877623296&userId=7746793735) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=591020372877623296&userId=7746793735&fromC=1) |
| 验证功能 | V2 主从合并：主计划 23 + 大班从 2 + 小班从 6004 同时出现 |
| 操作步骤 | **开启 V2 开关** → 打开该学员的该计划 |
| 预期结果 | 2 个年级共 3 条：grade11 小班 6004、grade15 联报 23 + 大班从 2 |
| 实际结果 |  |

### 10. V2-小→大主从合并（需开 V2 开关）

| 项 | 值 |
|-|-|
| 续班计划号 | `589721954597011456`（小班主计划，pt=51） |
| 学员ID | `7704848531` |
| 班级/课程 | 4 个大班从计划：`589037361072007168`、`589037362856683520`、`589177989139464192`、`589178077949657088` |
| 在读前置班（bizId） | 大班前置班 `589041192111595520` → bizId `31SX26C1FG11001`（50191-1106-数学大班主计划-pre，在读）  <br/>大班前置班 `589041213120864256` → bizId `31YY26CZ5Q11001`（50191-1106-英语从计划-pre，在读）  <br/>大班前置班 `589041231286394880` → bizId `31WL26C11J11001`（50191-1106-物理未关联对照-pre，在读）  <br/>大班前置班 `589211941652815872` → bizId `31SX26C8K011001`（50191-1107-去重独立前置0，在读）  <br/>大班前置班 `589211950196613120` → bizId `31SX26CWFM11001`（50191-1107-去重独立前置1，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=589721954597011456&appointUserId=7704848531&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=589721954597011456&appointUserId=7704848531&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=589721954597011456&userId=7704848531) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=589721954597011456&userId=7704848531&fromC=1) |
| 验证功能 | 主计划是小班时，V2 能否带上大班从计划 |
| 操作步骤 | 开启 V2 → 打开该计划 |
| 预期结果 | 2 个年级共 5 条：grade11 组合 51；grade31 共 4 条大班 pt=2。**对比老链路只有 1 条** |
| 实际结果 |  |

### 11. V2-小→小主从合并（需开 V2 开关）

| 项 | 值 |
|-|-|
| 续班计划号 | `588671894562123776`（小班主，pt=6004） |
| 学员ID | `7704848531` |
| 班级/课程 | 从计划 `589721954597011456`（小班 pt=51） |
| 在读前置班（bizId） | 小班前置班 `588668593594589184` → bizId `588668593594589184`（B测试GPS小班续班1104A-preB，纯数字 bizId，在读）  <br/>小班前置班 `589047959231029248` → bizId `589047959231029248`（50191-1106-数学小班-pre，纯数字 bizId） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=588671894562123776&appointUserId=7704848531&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=588671894562123776&appointUserId=7704848531&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=588671894562123776&userId=7704848531) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=588671894562123776&userId=7704848531&fromC=1) |
| 验证功能 | 主从都是小班时的合并 |
| 操作步骤 | 开启 V2 → 打开该计划 |
| 预期结果 | grade11 共 2 条：主 pt=6004 `588669006324588544` + 从 pt=51 `589762111522013184` |
| 实际结果 |  |

### 12. V2-混合主从（主小同时挂大从+小从）（需开 V2 开关）

| 项 | 值 |
|-|-|
| 续班计划号 | `588671894562123776`（小班主，pt=6004） |
| 学员ID | `7704848531` |
| 班级/课程 | 小班从 `589721954597011456`(pt51) + **大班从 `591020374322561024`**(pt2，后置班 `591020573457448960`) |
| 在读前置班（bizId） | 小班前置班 `588668593594589184` → bizId `588668593594589184`（B测试GPS小班续班1104A-preB，纯数字 bizId，在读）  <br/>大班前置班 `591020573457448960` → bizId `15YW26XTU911002`（S2后置班语文1117，五年级）  <br/>小班前置班 `589047959231029248` → bizId `589047959231029248`（50191-1106-数学小班-pre，纯数字 bizId） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=588671894562123776&appointUserId=7704848531&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=588671894562123776&appointUserId=7704848531&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=588671894562123776&userId=7704848531) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=588671894562123776&userId=7704848531&fromC=1) |
| 验证功能 | **两类从计划同时合并**（本轮新造关联） |
| 操作步骤 | 开启 V2 → 打开该计划 |
| 预期结果 | 2 个年级共 3 条：grade11 主 6004 + 小从 51；grade15 大从 2（价格 100 分） |
| 实际结果 |  |

### 13. V2-关联/无关联共存（同一学员有关联+无关联计划）（需开 V2 开关）

| 项 | 值 |
|-|-|
| 续班计划号 | A=`591020372877623296`（有关联）；B=`588506246722727936`（无关联，但同时是 A 的从计划） |
| 学员ID | `7746793735`（同一人） |
| 班级/课程 | A 的从：`591020374322561024`、`588506246722727936`；B 自身后置班 `588506155490336768` |
| 在读前置班（bizId） | A 计划在读前置班 `591020573289676800` → bizId `15YW26CHB911002`（M23前置班语文1117，在读）  <br/>A 计划在读前置班 `591020573124001792` → bizId `15YW26CV6011002`（S2前置班语文1117，在读）  <br/>B 计划在读前置班 `588506026511294464` → bizId `588506026511294464`（【造数】小班续班前置-小学数学，纯数字 bizId，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=591020372877623296&appointUserId=7746793735&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=591020372877623296&userId=7746793735) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=591020372877623296&userId=7746793735&fromC=1) |
| 验证功能 | 同一学员下，有关联计划走合并、无关联计划走独立，互不干扰 |
| 操作步骤 | 开启 V2 → 先用该学员打开 A，再打开 B |
| 预期结果 | A：3 条合并（23 + 2 + 6004）；B：**独立 1 条** pt=6004，不被其「A 的从计划」身份污染 |
| 实际结果 |  |

### 14. V2-嵌套环状关联（无死循环无重复验证）（需开 V2 开关）

| 项 | 值 |
|-|-|
| 续班计划号 | `589037361072007168`（大班主，双向环的一端） |
| 学员ID | `7704848531` |
| 班级/课程 | 环：`589037361072007168` → 从含 `589721954597011456` → 从含 `589037361072007168`（反向） |
| 在读前置班（bizId） | 大班前置班 `589041192111595520` → bizId `31SX26C1FG11001`（50191-1106-数学大班主计划-pre，在读，环的一端）  <br/>大班前置班 `589041213120864256` → bizId `31YY26CZ5Q11001`（50191-1106-英语从计划-pre，在读）  <br/>大班前置班 `589041231286394880` → bizId `31WL26C11J11001`（50191-1106-物理未关联对照-pre，在读）  <br/>大班前置班 `589211941652815872` → bizId `31SX26C8K011001`（50191-1107-去重独立前置0，在读）  <br/>大班前置班 `589211950196613120` → bizId `31SX26CWFM11001`（50191-1107-去重独立前置1，在读） |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=589037361072007168&appointUserId=7704848531&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=589037361072007168&appointUserId=7704848531&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=589037361072007168&userId=7704848531) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=589037361072007168&userId=7704848531&fromC=1) |
| 验证功能 | 环状关联下不死循环、不重复条目 |
| 操作步骤 | 开启 V2 → 打开该计划 |
| 预期结果 | 2 个年级共 6 条：grade11 组合 51；grade31 共 5 条大班 pt=2。**无重复条目、页面不卡死** |
| 实际结果 |  |

### 15. 异常入参（不存在计划号 / null）

| 项 | 值 |
|-|-|
| 续班计划号 | `999999999999999`（不存在） |
| 学员ID | `7746793735` |
| 班级/课程 | — |
| 在读前置班（bizId） | 无在读前置班（符合场景设计）——计划号 `999999999999999` 在 TEST 不存在，不会进入任何在读取数环节 |
| 点击验证链接 | **★对比接口（推荐）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheatCompare?renewalNumber=999999999999999&appointUserId=7746793735&includeBCart=false&sellerId=8645) —— 一次返回预热/实时两份完整结果 + 差异明细  <br/>①**实时计算（读预热缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/cart?renewalNumber=999999999999999&appointUserId=7746793735&includeBCart=false&sellerId=8645&p_client=1)  <br/>②**预热写入**[点这里](https://test-api.gaotu.cn/cart/web/renewal/preheat?renewalNumber=999999999999999&userId=7746793735) —— 仅触发写缓存、查看缓存值，**不作为对比结果**  <br/>③**纯实时（强制跳过缓存）**[点这里](https://test-api.gaotu.cn/cart/web/renewal/operation/cart?renewalNumber=999999999999999&userId=7746793735&fromC=1) |
| 验证功能 | 异常入参不 500、不白屏 |
| 操作步骤 | 打开 `renewalNumber=999999999999999` |
| 预期结果 | 返回空壳（banner 图 + renewalNumber + status=0），不抛 500 |
| 实际结果 |  |

---

# 如何开 V2 开关

**当前 TEST 实际状态（2026-11-18 16:53:19\~16:53:34 CST 只读实查 apollo_get_key，读的是已发布值）**：

- `renewal.recommend.v2.enabled`（C/B 端详情实时计算走 V2）= **true**
- `renewal.preheat.v2.enabled`（预热走 V2）= **true**
- 这两个 key 由 release **438174** 在 **2026-11-18 16:45:48** 从 `false` 改为 `true`（操作人 zhangzeling）。**不是本自验任务改的**，本任务全程没有动 Apollo。
- `renewal.preheat.v2.prefix.enabled` = `false`，保持不动。

**这意味着**：现在直接打开测试页，走的是 **V2 链路**，不是老链路基线。所以要验场景 1-8，**必须先把上面两个开关改回 false**。

开关的开启和恢复都由 owner 执行，我不动 Apollo。改完告知我，我再去核验并回读确认。

- `renewal.recommend.v2.enabled`（C/B 详情走 V2）
- `renewal.preheat.v2.enabled`（单用户预热走 V2）

`renewal.preheat.v2.prefix.enabled` 保持 `false`，不需要动。

改完我会告知你，你再去点。**验完我负责改回 `false` 并读回确认**，不用你操心恢复。

---

# 补充说明

- 场景 1-8 是 **V2 关闭**（老链路）基线，**必须在两个 V2 开关关闭时验证**。当前 TEST 两个开关是 **true**（2026-11-18 16:45:48 release 438174），所以**验之前要先把开关关掉**，由 owner 负责关闭，我不动 Apollo。
- 场景 9-14 必须开 V2（两个开关都是 true，也正是当前 TEST 的状态），**建议连在一起验**，避免反复开关。
- 场景 8（组合 51）与场景 10/11/12 有重叠的计划号，注意区分当前开关状态。
- 所有 ID 均来自 TEST 环境真实数据；若某计划已过期或数据被改动，告我一声我重新核。

---

# 预热怎么验

## 一、预热的三个入口

| 入口 | 地址 / 触发方式 | 说明 |
|-|-|-|
| 单用户 HTTP 预热 | `GET /renewal/preheat?userId=&renewalNumber=`  <br/>（`RenewalController#preheat`，Feign 同名 `RenewalFeignService#preheat`） | 按 `renewal.preheat.v2.enabled` 路由：true 走 `RenewalV2Service#preheat`，false 走老 `RenewalService#preheat` |
| 计划级批量预热（Feign） | `POST /renewal/preheatByRenewal`，body 为计划号数组 | 同样按 `renewal.preheat.v2.enabled` 路由到 V2 或老链路 |
| 定时 Job | XXL-Job `RenewalV2JobHandler`（V2）/ `RenewalJobHandler`（老） | V2 Job 启动即判断 `renewal.preheat.v2.enabled`，false 直接 `skipped` 返回；可传计划号数组，不传则取全部有效计划 |

## 二、写哪个 key、多久过期

key 格式由 `renewal.preheat.v2.prefix.enabled` 决定（大班 `RenewalV2PureRenewalService#cacheKey`、小班 `SmallRenewalPreheatCacheService#cacheKey` 同一套规则）：

- 前缀开关 `false`（TEST/PROD 当前都是 false）：`renewal:preheat:{续班计划号}:{学员ID}`
- 前缀开关 `true`：`renewal:preheat:v2:{续班计划号}:{学员ID}` —— 仅用于人工对比，不覆盖原 key
- TTL：`preheat.cache.time`，代码默认 **26 小时**
- 计算结果为空时**删除**该 key（不打空值），避免过期推荐残留到 TTL 结束

实际例子（本次 P1 验证实测）：`renewal:preheat:586116340522184704:7746791494`

## 三、怎么确认命中

| 链路 | 日志关键字（原文） | 位置 |
|-|-|-|
| 小班 V2 命中 | `small preheat cache hit, key={}, entries={}` | `SmallRenewalPreheatCacheService:93` |
| 大班 V2 / 老链路命中 | `renewal-data-from-preheat , renewalNumber is {}, userId is {}` | `RenewalService:1322` |
| 大班未命中 | `renewal-data-from-coreHandle-hit, key is {}, result string is empty{}` | `RenewalService:1314` |
| 小班写缓存成功 | `small preheat write done, key={}, entries={}` | `SmallRenewalPreheatCacheService:74` |
| 大班 V2 写缓存成功 | `renewal-v2 preheat done, key={}, entries={}` | `RenewalV2PureRenewalService:441` |
| 空结果删 key | `small preheat empty, delete stale key, key={}` / `renewal-v2 preheat empty, delete stale key, key={}` | 两个 Cache 服务内 |

**验法**：先调一次 `/renewal/preheat`，在日志里搜到 `preheat done ... entries=N`；再打开续班详情页，搜 `small preheat cache hit`（小班）或 `renewal-data-from-preheat`（大班）。两条日志出现在同一 trace 里，就是实锤命中。

## 四、大班和小班的预热差异

| 维度 | 大班 | 小班（type=2） |
|-|-|-|
| 写入内容 | `Map<前置课号, ClazzDetailDTO>`，带 `renewalRole`（1=主计划纯续，2=从计划纯续），主+从合并去重后整体写入 | `Payload{ results: List<SmallRenewalRecommendResult> }`，**只存纯续结果**；扩科/加购不写快照，读的时候现场重建 |
| 写入口（V2） | `RenewalV2PureRenewalService#preheat/writePreheat` | `SmallRenewalPreheatService#preheatAndCache`（单用户）、`#preheatByRenewalNumberAndCache`（计划级） |
| 老链路是否读写缓存 | 读写（`preheat.cache.enabled` 控制读） | **不写不读**，老链路行为完全不变 |
| 命中后仍要现算什么 | 按缓存的前置课批量补查班级/课程，组 `RecommendContext` | 完整重建 `SmallRenewalRecommendContext`（已购、关联关系、B 端加购都按当前请求现算），只复用纯续结果 |
| 触发条件 | 非 fromBCart、`preheat.cache.enabled=true`、非 skipPreheatRead、非 legacyPure | 同上，且 `small.renewal.enabled=true` |

---

# 实时计算怎么验

## 一、什么时候走实时计算

详情接口 `RenewalSinglePlanDetailService` 满足**任一**条件就走完整现算，不读预热缓存：

- `preheat.cache.enabled=false`（缓存读总开关关掉）
- `fromBCart=true`（B 端购物车场景）
- `skipPreheatRead=true`（从计划只取纯续展示数据的场景）
- `legacyPure=true`（老 B 端纯续兼容模式）
- Redis 里没有这个 key，或者 JSON 解析失败 / 空列表（`read()` 返回 null）

未命中后调用的是：小班 `SmallRenewalCoreService#recommendAll`；大班 `RenewalService#coreHandle`。

## 二、怎么确认走的是实时计算

实时计算**没有专门的「realtime」日志**，只能靠排除法 + 正向日志两头看：

| 看什么 | 怎么判 |
|-|-|
| 查不到命中日志 | trace 里**没有**`small preheat cache hit`（小班）或 `renewal-data-from-preheat`（大班） |
| 有实时路径的入口日志 | 大班搜 `renewal preheat start, renewalNumber is {}, userId is {}` 且其后无命中日志，即 `corePreheatCache` 返回 null 后回落到 `coreHandle` |
| 上下文构建日志 | 小班 `renewal.small.builder.debug.enabled=true` 时会打上下文构建明细；命中缓存的场景也会重建 context，所以这一条只能辅助、不能单独作判据 |
| Redis 侧确认 | 预热后用 `EXISTS renewal:preheat:{计划号}:{学员ID}` 确认 key 是否存在；`DEL` 掉再打开页面，即强制走实时 |

## 三、预热结果 vs 实时结果怎么对比

**最干净的对比法**（不依赖开关、不改代码）：

1. 先确保 key 存在：调 `/renewal/preheat?userId=&renewalNumber=`，日志确认 `preheat done ... entries=N`。
2. 打开详情页，拿到「命中」结果（页面商品列表 / 接口响应），记下条数、年级、productType、商品号。
3. 删掉该 key（或把 `preheat.cache.enabled` 置 false，或加 `fromBCart`/`skipPreheatRead` 参数）。
4. 再打开同一页面，拿到「实时」结果，逐条比对。

**必须相等的字段**：商品类型（productType）、商品/班级号、年级（grade）、价格、`renewalRole`（V2 下主/从标记）。

**允许不同的字段**：库存数量、开课时间之外的运营态字段（实时性原因）。

**小班特别注意**：命中缓存时**只复用纯续结果**，扩科/加购是现场重建的。所以「命中」和「实时」在扩科/加购条数上必须一致 —— 这正是 P1 修复要验的点，见场景 5。

**人工对比专用开关**：`renewal.preheat.v2.prefix.enabled=true` 时 V2 写 `renewal:preheat:v2:` 前缀的副本，不覆盖 `renewal:preheat:`。可以同时保留新老两份结果做对比，验完记得改回 false。

---

# Apollo 配置（实查）

> 查询方式：apollo-config `apollo_get_key`，读的是**已发布值**。  
> 应用 `cart.gaotu100.com`，namespace `application`。  
> 查询时间：**2026-11-18 16:53:19 \~ 16:53:34 CST**（TEST 和 PROD 各读一次，两次结果一致；TEST 另外做了全量 namespace 读取，共 168 项）。  
> 代码版本：`feature-renewal-preheat-v2-20261112` @ `5f0df948`。  
> 「不存在」= 该环境没配这个 key，运行时走代码 `@Value` 默认值。

## 一、V2 核心开关

| key | 作用 | 代码默认 | TEST 已发布值 | PROD 已发布值 |
|-|-|-|-|-|
| `renewal.recommend.v2.enabled` | C/B 端详情**实时计算**走 V2：主计划和有效从计划各自推荐，只合并纯续 | false | **true**（16:45:48 由 release 438174 从 false 改为 true） | 不存在 → 生效 false |
| `renewal.preheat.v2.enabled` | **预热**走 V2（单用户 / 计划级 / Job 全部受它控制） | false | **true**（同上一次发布一起改的） | 不存在 → 生效 false |
| `renewal.preheat.v2.prefix.enabled` | 对比用：true 时预热写 `renewal:preheat:v2:` 前缀副本，不覆盖原 key | false | false | 不存在 → 生效 false |
| `preheat.cache.enabled` | 详情接口**是否读**预热缓存 | true | true | true |
| `preheat.cache.time` | 预热缓存 TTL（小时） | 26 | 不存在 → 26 | 不存在 → 26 |

**重要**：TEST 两个 V2 开关**当前是 true**（2026-11-18 16:45:48 发布）。也就是说现在直接打开测试页走的是 V2 链路；要验老链路基线（场景 1-8），需要先改回 false。

## 二、缓存与超时

| key | 作用 | 默认 | TEST | PROD |
|-|-|-|-|-|
| `renewal.related.plan.cache.enabled` | 有效从计划（状态+前置课）关联查询的**本地缓存**开关，热生效 | true | 不存在 → true | 不存在 → true |
| `renewal.related.plan.cache.expire.seconds` | 上面这个本地缓存的过期秒数，≤0 等于关闭。**注：不是 `.ttl`** | 60 | 不存在 → 60 | 不存在 → 60 |
| `renewal.related.plan.timeout.seconds` | 实时计算时从计划**并行计算超时**秒数，超时视为失败并上抛 | 10 | 10 | 不存在 → 10 |
| `renewal.preheat.batch.timeout.seconds` | 批量预热单批等待超时秒数 | 600 | 不存在 → 600 | 不存在 → 600 |
| `renewal.relation.validate.cache.hours` | 关联校验结果缓存小时数 | 1 | 不存在 → 1 | 不存在 → 1 |

## 三、小班相关

| key | 作用 | 默认 | TEST | PROD |
|-|-|-|-|-|
| `small.renewal.enabled` | 小班续班**总开关**；关掉则前置课 type=2 走老 B 端兼容模式 | false | true | true |
| `renewal.small.builder.debug.enabled` | 小班上下文构建调试日志。**注意：`renewal.small.debug.enabled` 这个 key 代码里没有引用** | true | 不存在 → true | true |
| `renewal.small.validator.time-range.enabled` | 小班续班时间范围校验（不在窗口内则不出推荐） | true | **false**（TEST 特意关掉） | 不存在 → true |
| `renewal.small.gift.order.filter.enabled` | 赠课订单过滤（payChannel=30） | true | **false** | 不存在 → true |
| `small.renewal.preheat.maxThreads` | 小班预热线程数 | 10 | 不存在 → 10 | 不存在 → 10 |
| `small.renewal.preheat.batchSize` | 小班预热批大小 | 100 | 不存在 → 100 | 不存在 → 100 |
| `renewal.small.plugin.stock.match.enabled` | 小班库存过滤插件 | true | 不存在 → true | 不存在 → true |
| `renewal.small.plugin.whitelist.enabled` | 小班白名单插件 | true | 不存在 → true | 不存在 → true |

## 四、线程池 / 超时（启动时读，不热生效）

| key | 作用 | TEST | PROD |
|-|-|-|-|
| `renewal.context.build.corePoolSize` / `maxPoolSize` | SubBuilder 并行线程池 `renewalContextBuildExecutor`（20/40） | 不存在 → 20/40 | core 不存在 → 20；max=**40** |
| `rpc.parallel.executor.corePoolSize` / `maxPoolSize` | RPC 并行线程池 `rpcParallelExecutor`（20/40） | 不存在 → 20/40 | core 不存在 → 20；max=**80** |
| `hystrix...thread.timeoutInMilliseconds` | Feign/Hystrix 全局超时 | **100000** | **3000** |
| `ribbon.ReadTimeout` / `ConnectTimeout` | Ribbon 超时 | **100000** | **3000** |

**PROD 超时差异很大（3s vs TEST 100s）**：V2 的 10s 从计划并行超时在 PROD 其实会被上游 3s 的 Hystrix/Ribbon 先截断。但两个 V2 开关在 PROD 都是 false，目前不生效。

## 五、有配置但本分支代码没引用的 key

| key | TEST | PROD | 说明 |
|-|-|-|-|
| `renewal.pure.relation.enabled` | true | **false** | 本分支没有引用，**master 有引用**。本分支落后 master 11 个提交，合并后这个开关会重新生效，PROD 配的是 false |
| `renewal.cart.debug.appoint-user.enabled` | true | **true** | 打开时接口直接用入参 `appointUserId` 作为调用主体，**跳过登录校验**。PROD 已开，属于既有配置 |

---

# 开关组合：哪条链路、读哪类缓存

| 详情 V2 | 预热 V2 | prefix | 详情实时计算 | 预热写入 |
|-|-|-|-|-|
| false | false | 任意 | 老链路 | 老链路，写 `renewal:preheat:` |
| false | true | false | 老链路（仍会读 `renewal:preheat:`） | V2 写原 key |
| true | false | — | V2（主+从只合并纯续） | 老链路 |
| **true** | **true** | false | **V2** | **V2 写原 key（TEST 当前状态）** |
| 任意 | true | true | — | V2 写 `renewal:preheat:v2:` 副本，不污染原 key |

**场景 ↔ 需要的开关状态**

| 场景 | 详情 V2 开关 | 预热 V2 开关 |
|-|-|-|
| 1 – 8（老链路基线） | **false** | false |
| 4、5（预热写入后命中缓存） | false | false（用老 `/preheat` 写 `renewal:preheat:`） |
| 9 – 14（V2 主从合并） | **true** | **true** |
| 15（异常入参） | 任意 | 任意 |

`renewal.preheat.v2.prefix.enabled` 全程保持 **false**；`preheat.cache.enabled` 全程保持 **true**（场景里如果要强制实时对比，可以临时置 false）。

> **当前 TEST 状态提示**：两个 V2 开关在 2026-11-18 16:45:48 已被改成 **true**（release 438174）。所以现在直接点场景 1-8 会是 V2 链路，不是老链路基线。要验 1-8，需要先改回 false。  
> **开 V2 和恢复 V2 由 owner 执行**，我这边按 owner 通知的时间点核验，不擅自动 Apollo。

---

# 可直接点击的验证链接

> 全部链接为 TEST 环境，已逐条实测（HTTP 200 + status=0），返回结构与预期一致。  
> 测试时间：2026-11-18 17:2x CST。**点击前须知**：`/cart` 接口只有在 `appointUserId` 存在时才跳过登录校验（依赖 Apollo `renewal.cart.debug.appoint-user.enabled=true`，TEST 已开）。**不带 `appointUserId` 会直接返回 code=16「帐号长时间未登录已被退出」**——这是实测确认的，不是推断。

## 链接参数说明

| 参数 | 是否必填 | 实测结论 |
|-|-|-|
| `renewalNumber` | 必填 | 续班计划号，为空返回 400 结构 |
| `appointUserId` | **必填（实测）** | 不带时返回 `{"code":16,"msg":"您的帐号由于长时间未登录已被退出"}`；带上即正常返回。原因：TEST 的 `renewal.cart.debug.appoint-user.enabled=true`，接口直接用该参数作为调用主体 |
| `includeBCart` | 可选，默认 false | 是否带 B 端购物车（加购）数据。本清单统一 `false`，与预热口径一致 |
| `sellerId` | 可选 | 实测 `8645` / 不传 / `null` 三种返回**完全相同**，对本批场景无影响，沿用 owner 样例值 |
| `p_client` | 可选 | 实测有无均返回相同结构，保留以贴合前端真实调用 |

## 对比方法（二种方式）

**现在有二种对比方式，推荐用第一种。**

**方式一（推荐）：对比接口** —— 点每个场景里的「★对比接口（推荐）」链接，一次调用直接返回 `consistent` 和差异明细，不用人工比对。详见文末「预热/实时对比接口（新增）」章节。

**方式二：三步人工对比（对比接口不可用时的兜底）**

依据是代码 + 实测：B 端 `GET /web/renewal/operation/cart` 走的是 `getPurePlanDetailSkipPreheat` —> `getSinglePlanDetailInternal(..., skipPreheatRead=true, ...)`，**强制不读预热缓存**（`RenewalSinglePlanDetailService.java:1151-1158`）。所以它就是一条现成的「纯实时」通道。

**三步对比法**：

1. **先预热**：点「预热链接」（`GET /web/renewal/preheat?renewalNumber=&userId=`），把结果写进 `renewal:preheat:{计划号}:{学员ID}`。这个接口不校验登录态，直接返回 JSON。
2. **再读 C 端**：点「实时计算链接」（`/cart?appointUserId=...`），此时应命中预热缓存。
3. **看对比接口链接**：点「★对比接口」链接，直接读 `consistent` 与 `diffs`，判断是否一致。

**判定标准（对比接口）**：`consistent=true` 即两份完整接口结果逐字段一致（扩科、加购都参与比对）；`false` 时看 `diffs` 里的字段路径与两侧取值。**旧口径已废弃**：此前只比 `recommendType=1` 纯续，是因为当时的 `operation/cart` 不算扩科；现在对比的是整接口最终返回。

## 实测对比结果（缺陷修复后终测，2026-11-18 21:0x CST，15/15 一致）

| 场景 | consistent | diff 数 | traceId |
|-|-|-|-|
| 1 | ✅ 一致 | 0 | `9f45fd7b-166e-44b5-8804-511e7d86e5` |
| 2 | ✅ 一致 | 0 | `a9cdb550-aece-427e-9c45-07a3a29a4b` |
| 3 | ✅ 一致 | 0 | `2b732507-5ae5-4b34-b949-a0aac786bf` |
| 4 | ✅ 一致 | 0 | `ca78116d-280b-4c04-83d1-1028f3ebb1` |
| 5 | ✅ 一致 | 0 | `27606206-2c06-41a6-b227-1226937049` |
| 6 | ✅ 一致 | 0 | `509db7e1-26c6-43f0-b862-a18fe79a98` |
| 7 | ✅ 一致 | 0 | `acfc7680-6276-43d8-b409-1171cdb352` |
| 8 | ✅ 一致 | 0 | `44e846e0-8110-4490-a685-b62d3bf434` |
| 9 | ✅ 一致 | 0 | `de35f9c5-e388-4384-afe1-3e3934478a` |
| 10 | ✅ 一致 | 0 | `1be81477-ce60-4871-8ba2-76178bbe70` |
| 11 | ✅ 一致 | 0 | `b7e7b79f-2a8e-43c3-9046-e07dd2f069` |
| 12 | ✅ 一致 | 0 | `58331f4a-5496-4d89-8157-fc211dfaab` |
| 13 | ✅ 一致 | 0 | `2b83764e-1384-4b76-b1e7-8a3c28ea98` |
| 14 | ✅ 一致 | 0 | `6bbab343-0fd2-4537-8ebb-b40aa93644` |
| 15 | ✅ 一致 | 0 | `3d67eeb6-212a-4f17-935e-c61e71f8c1` |

**上面的结果说明**：预热写入后 C 端读到的纯续结果，与完全跳过缓存的实时计算结果逐条对齐，**6/6 通过**。场景 3 和 14 的差额是扩科条目，属于设计内行为（预热只存纯续，扩科每次现场重算）。

## 几点实测发现（使用前必读）

- **缺陷已修复，终测 15/15 场景一致（含此前失败的 6 个联报场景）**。  
**修复①**（commit ea1d6f91）：联报主计划读缓存组装时，收集联报号传下游前过滤 null——V2 合并缓存含从计划条目（非联报，activityNumber=null），null 传给联报订单/联报配置查询被参数校验拒绝。修复后 6 个联报场景不再报「activityNumber不能为空」。  
**修复②**（commit 0528c192）：单计划消费 V2 合并缓存只取本计划前置课条目（retainAll 过滤），从计划条目由 V2 编排现算补回——修复前整个合并缓存被当本计划结果组装，minGrade 被从计划低年级拉走，本计划联报条目成空壳（price/name/teacher 空）、从计划条目 sku 被置 null，与实时相差 20 处。老链路不受影响（老缓存本就是单计划值，过滤后全保留）。  
**终测（排序口径，commit 0528c192）**：15/15 consistent=true、diff=0，traceId 见上表；单测新增联报读缓存用例（未修复代码上失败、修复后通过），全量 592 项失败 15 项与基线一致。
- **小班预热接口固定返回 `{}`**（代码里 `return Collections.emptyMap()`），但缓存是**照常写入**的。所以小班场景不要用预热接口的返回判断成功，要看后续 C 端请求的表现。
- **B 端实时链接是 `LEGACY_PURE` 模式**：只算纯续，不算扩科、不算加购。所以它不能直接和 C 端的全部条目比，只能比纯续部分。
- 预热缓存 TTL 是 **26 小时**（`preheat.cache.time` 默认值）。要重新验「未命中」分支，得等过期或让 owner 清 key。

---

# 预热/实时对比接口（新增）

> 新增 GET 接口，一次调用即可拿到同一 `renewalNumber` + 学员的**预热路径**与**实时路径**两份完整接口结果，并给出逐字段差异。  
> 两条结果结构都和 `/web/renewal/cart` 完全一致（都是 `RenewalCartVO`），扩科、加购均参与比对。  
> 接口为**纯新增**：新建 Controller 与 Service，未修改任何已有接口或业务代码。

## 一、路径与参数

`GET https://test-api.gaotu.cn/cart/web/renewal/preheatCompare`

| 参数 | 必填 | 说明 |
|-|-|-|
| `renewalNumber` | 是 | 续班计划号 |
| `appointUserId` | 否 | 调用主体学员。传了就按该学员计算；不传则回落到登录态。TEST 的 `renewal.cart.debug.appoint-user.enabled=true`，所以浏览器直接点建议带上它 |
| `includeBCart` | 否 | 默认 `false`。是否带 B 端购物车（加购）数据 |
| `sellerId` | 否 | 老师 ID，透传。不影响对比结论 |

## 二、返回字段

| 字段 | 含义 |
|-|-|
| `preheatResult` | **预热路径**的完整返回（主计划读 `renewal:preheat:` 缓存），结构与 `/web/renewal/cart` 一致 |
| `realtimeResult` | **实时路径**的完整返回（强制跳过预热读、现场计算），结构与上面一致 |
| `consistent` | 两份结果是否逐字段一致。`true`=没有差异 |
| `diffs` | 差异明细数组，每项含 `path`（字段路径）、`preheatValue`、`realtimeValue` |
| `preheatPath` / `realtimePath` | 两条路径的说明文字 |
| `notes` | 结论说明，如「排序后逐字段一致」或「共 N 处字段差异」  <br/>`orderOnlyDiff`  <br/>**仅顺序不同**（排序后内容一致）的列表路径数组，**不计入 consistent=false**。据此判断顺序差异在业务上是否重要  <br/>`preheatTriggered`  <br/>对比前是否已自动触发一次预热写入；false 时 notes 会说明原因，此时预热结果是未命中缓存的实时兜底 |

## 三、比对口径

- **比对的是整个接口的最终返回**，不是 Redis 缓存值，也不是只比纯续子集。
- **扩科、加购全部参与比对** —— 它们是 C 端最终返回的一部分。两条路径的扩科/加购都由同一套现场逻辑重建，理应一致。
- 排除字段：renewalNumber、renewalStartTime、renewalEndTime、imageUrl、gradeDesc（请求侧回显/常量文案，必然相等）；以及 renewalRole（路径溯源标记：预热写入时对缓存条目打 1=主/2=从，实时组装的条目大多不打标——它不代表推荐内容不同）。
- 差异按**完整字段路径**定位，例如 `gradeClazzList[0].clazzDetailDTOList[1].price`，可直接对照两份结果看出问题。

## 四、开关

| key | 代码默认 | TEST | PROD |
|-|-|-|-|
| `renewal.preheat.compare.enabled` | **false** | **true**（release 20261118181633） | **未配置** → 生效 false |

开关关闭时接口**直接拒绝**，返回 `{"status":1,"msg":"preheat compare disabled"}`，不执行任何计算。PROD 未配置该 key，因此线上默认不可用。

## 五、排序规则（重要）

**对比前两份结果先按同一套确定规则排序，只有顺序不同不算不一致**，单独记入 `orderOnlyDiff`：

| 列表 | 排序键（依次） |
|-|-|
| `gradeClazzList`（年级组） | `grade` → `defaultSelect` |
| `clazzDetailDTOList`（商品列表） | `productType` → `productSkuNumber` → `afterCourseNumber` → `beforeCourseNumber` |
| 其余列表（teacherList、subjectNames、msg 等） | 整行 JSON 字符串（保证全序确定） |

排序只用于比对，不改变两份原始结果的返回顺序；「预热/实时在展示顺序上的差异」是真实存在的，只是不判为数据不一致。

## 六、内部四步流程

一次调用内部自动完成：**①实时结果 A**（跳过缓存现算）→ **②预热写入**（调 preheat 写缓存）→ **③预热路径 B**（读缓存组装完整返回）→ **④排序后对比**。`preheatTriggered` 字段显示第②步是否成功。