# 业绩判出来了，但 CRM 排行榜显示 0

触发条件：判单侧正常、业绩已落库，但排行榜/业绩显示是 0 时读。**这不是判单问题，是取数问题。**

这一类**不是判单问题**，是**取数链路问题**。判单侧一切正常，业绩也落库了，但落在了排行榜数据源之外的表里。

### 8.-1 ⛔ 开工第一句话：先问「排行榜右上角的时间筛选选的是哪个区间」

排行榜/业绩显示**全部按时间区间聚合**。同一个人：8/18 单日 = ¥0.00 排第 3，8 月整月 = 26.9 万排第 1，
全年 = 244 万排第 1。**分析前必须先确认查询区间。**

**主动向用户要这三样，缺一个就先问再动手**：
1. 排行榜右上角筛选的**时间区间**（起止日期）
2. 看的是**本组**还是**部门**（对应 `type=1` / `type=2`）
3. 涉事**订单号**

拿到区间后**用那个区间打接口**（见 8.7），别用自己顺手编的区间。

### 8.1 结论先行：非课程类订单（物理商品/OMO）的业绩进不了排行榜

- CRM 业绩排行榜 / 业绩显示走 **ES 宽表**，宽表**只由 `performance_order_attribution_total` 构建** —— 见 `PerformanceDashboardAttributionDocumentConstructor.construct`（唯一数据源 `performanceOrderAttributionTotalMapper.selectByIdsIsDel`）。
- 触发同步的是 MQ tag **`OrderAttributionPaidEvent`**（`PerformanceAttributionPaidMsg`）→ `PerformanceDashboardOrderAttributionListener`。
- 而**非课程类订单**（订单管理→非课程类订单，`sku_type/productType=8027` 这类）判单走 `OmoPerformanceAttributionJudgeTemplate`：
  - 落库表是 **`gaotu_stat.performance_physical_attribution`**（待支付：`performance_physical_attribution_no_pay`），**不写 `performance_order_attribution` / `_adult` / `_total`**
  - 发的是 **`ItemAttributionPaidMsg`**（`sendItemAttributionPaidMsg`），**不是** `OrderAttributionPaidEvent`
- ⇒ **物理商品业绩从来不进 ES 宽表，排行榜/业绩显示天然算不到它。** 这是设计缺口，不是数据丢了，不要去跑判单回溯（回溯也不会补）。

### 8.2 判定这一类的三个特征（凑齐就是它）

1. `performance_order_attribution` / `_adult` / `_total` / `_no_pay*` **全查不到**该订单；
2. 但 `performance_attribution_judge_reason` **有 scene=1 和 scene=2 两条**、策略结果正常（如「拉新类型-命中」）；
3. `performance_physical_attribution` **有行**，`employee_email` 就是老师本人，`performance_price` 就是实付金额。

日志里对应的 smoking gun（`OmoPerformanceAttributionJudgeTemplate`）：
```
[OMO] insert no pay physical attribution: [PerformancePhysicalAttributionNoPay(... employeeEmail=xxx ...)]
[OMO] insert pay physical attribution:    [PerformancePhysicalAttribution(... type=24, employeeEmail=xxx ...)]
```

### 8.3 ⚠️ 红鲱鱼：`[ItemRouter] no template matched`（8027 是**故意**不匹配的）

同一笔单必然还会打这两条 WARN：
```
DefaultItemAttributionJudgeTemplateRouter.route  [ItemRouter] no template matched, credential = ItemAttributionCredential(... productType=8027 ...)
AbstractProductCenterOrderHandler.consumerOrder  ProductCenterOrderHandler no template matched, ...
```

**这是设计使然，不是 bug、不是漏配**，已核到具体代码：

- `GenericItemAttributionJudgeTemplate`（本该兜底 order=0）把 8027 **显式排除**：
  ```java
  @ApolloJsonValue("${performance.attribution.item.template.generic.excluded-sku-types:[8027]}")
  private Set<Integer> excludedSkuTypes;
  // doSupports: skuType >= skuTypeFloor(默认8007) && !excludedSkuTypes.contains(skuType)
  ```
  Apollo PROD **未配该 key** → 吃代码默认值 `[8027]`（`apollo_get_key` 查 419 项 miss 即可确认）。
- item 链路唯一的具体子类 `ThetaCardAttributionJudgeTemplate` 只认 `theta.sku-type` 默认 **8007**。
- 8027 实际由**另一条链路**接走：`DefaultCourseOrderCreatedEventHandler` 的
  `@ApolloJsonValue("${default.course.handle.sku.type:[8027]}")` → `OmoPerformanceAttributionJudgeTemplate`。

⇒ 看到这条 WARN 别去改 `excluded-sku-types`、别去补 item 模板，**先去 `performance_physical_attribution` 找业绩**。

### 8.3.1 为什么 physical 永远进不了宽表（两处硬证据）

1. `PerformanceDashboardSyncSceneEnum` 只有三个场景 `PERFORMANCE_SYNC(1)/STAFF(2)/BACK(3)`，
   **全部只挂 `PerformanceDashboardAttributionDocumentConstructor`**，没有任何 physical/OMO 场景。
2. 写 `performance_order_attribution_total` 的只有 K12/Adult 判单模板
   （`AdultPerformanceAttributionJudgeTemplate` 等）；OMO 模板 override 成写 physical 表。
   **全仓没有任何把 physical 搬进 `_total` 的链路** —— 所以「等一会儿会不会同步过来」的答案是**永远不会**。

### 8.4 排查动作（照抄）

```sql
-- cluster 259 / gaotu_stat
-- ① 常规业绩表（都会是空）
SELECT * FROM performance_order_attribution        WHERE order_number='<单号>';
SELECT * FROM performance_order_attribution_adult  WHERE order_number='<单号>';
SELECT * FROM performance_order_attribution_total  WHERE order_number='<单号>';
-- ② 判单原因（会有 scene=1/2 两条 → 证明判单跑了）
SELECT order_number,scene,LEFT(rule_result,120),create_time FROM performance_attribution_judge_reason WHERE order_number='<单号>';
-- ③ 物理商品业绩（真正落库的地方）★
SELECT * FROM performance_physical_attribution WHERE order_number='<单号>';
```
日志（`serviceName: performance-attribution`，logType `app`）：
```
queryStr: "<单号>" and ("no template matched" or "insert pay physical attribution" or "insert no pay physical attribution")
```
> 直接用 `keyword=<单号>` 捞会被订单消息体撑爆（单条几 KB，20 条就落盘），**一定用上面的 queryStr 收窄**。

做完 ①②③ 还**不能收工**：必须再做 8.7（打线上接口复现）+ 8.5（SQL 与接口数字对账）。
只有数字对上了，「这单不进排行榜」才是证据，否则只是读代码得出的猜想。

### 8.5 ★ 必做：打线上接口 + 与 `_total` 表对账（别只靠读代码推演）

**光看代码推「宽表只读 _total」不算证据。** 决定性做法是：打一次线上排行榜接口拿到数字，
再用 SQL 在 `_total` 表上**复刻 ES 的聚合口径**，看两边是否分毫不差。相等 ⇒ 排行榜确实只吃 `_total`，
那笔不在 `_total` 的单贡献必为 0，结论闭环。

ES 聚合口径（`convertAggregationBuilderForRankList` + `convertQueryBuilderForRankList`）翻译成 SQL：
```sql
-- cluster 259 / gaotu_stat，时间区间与接口 beginTime/endTime 保持一致
SELECT SUM(CASE WHEN trade_status=1 THEN performance_price ELSE 0 END)  AS s1,
       SUM(CASE WHEN trade_status IN (2,3,4) THEN performance_price ELSE 0 END) AS s24,
       SUM(CASE WHEN trade_status=1 THEN performance_price ELSE -performance_price END) AS net,
       COUNT(*) c
FROM performance_order_attribution_total
WHERE employee_email='<邮箱前缀>' AND isdel=0
  AND type<>0                      -- 对应 mustNot(performanceType=0)
  AND trade_status IN (1,2,3,4)
  AND trade_time>='<begin>' AND trade_time<'<end>';
-- net 必须等于接口返回的 performancePrice（单位：分）
```
2026-08-21 实测：接口 `performancePrice=243942700`，SQL `net=243942700.00` —— 完全相等，
`c=372` 行全部来自 `_total`；而涉事的 8027 单在 `performance_physical_attribution` 里，故贡献 0。

**顺带一条纪律**：老师说「我业绩是 0」时，先确认**她看的时间区间**，然后**按那个区间打一次接口**。
8/18 单日接口结果与截图一致（她 ¥0.00 排第 3，前两名孙超、刘杨威），而整月或全年结果为第 1。
「某天窗口恰好只有这一单」在打接口之前只是推测，**打完才是结论** —— 别跳过这一步直接写结论。

辅助：看她每天的业绩分布，判断哪个窗口会显示 0
```sql
SELECT DATE(trade_time) d,type,trade_status,COUNT(*) c,SUM(performance_price) sp
FROM performance_order_attribution_total
WHERE employee_email='<邮箱前缀>' AND trade_time>='2026-08-01' AND isdel=0
GROUP BY DATE(trade_time),type,trade_status ORDER BY d;
```

### 8.6 取数链路代码地图

```
CRM 前端 → student-center
  web/api/HomePageController        /homePage/getPerformanceRankingList
  app/service/HomePageBiz:329       getPerformanceRankingList（灰度开关 graySwitch 命中直接返回空！）
      :346 permissionStaffSwitch && (bClient==null||bClient==1) → 走组织架构 staff 新逻辑
      type: PerformanceDimensionEnum  GROUP=本组 / DEPARTMENT=部门（部门维度只看主岗 jobType==1）
  domain/service/impl/PerformanceRankServiceImpl:52  → Feign performanceAttributionAdapter.getPerformanceRank
      rankCondition.talentType 默认 1（学习顾问），来自 student.center.homePage.performanceRankingList.roleTag

performance-attribution
  domain/service/performance/impl/PerformanceBaseServiceImpl
    :927  queryPerformanceRankList
    :974  listPerformanceRankListByStaff        ← 查 ES，不查 MySQL
    :1010 convertAggregationBuilderForRankList  净业绩 = sum(tradeStatus=1) - sum(tradeStatus in 2,3,4)
    :1055 convertQueryBuilderForRankList        过滤：tradeTime 区间 / tradeStatus in(1,2,3,4)
                                                     / mustNot(performanceType=0) / hrStatus=true(在职)
                                                     / roleTag=talentType / 部门 nested(jobList.orgPath|orgPaths)
    :1171 getSelfPerformanceByStaff             ES 查不到时 :1200「查不到给默认值」→ 就是那个 ¥0.00
  domain/listener/PerformanceDashboardOrderAttributionListener   tag=OrderAttributionPaidEvent，喂 ES 宽表
  domain/query/constructor/PerformanceDashboardAttributionDocumentConstructor  宽表字段全部来自 _total 表
```

**排行榜显示 0 的可能原因，按排查顺序**：
1. 业绩落在 `performance_physical_attribution`（本节主因，非课程类订单）
2. 时间区间内该老师本就没单（8.5）
3. `graySwitch` 命中灰度 → 整个排行榜返回空
4. ES 宽表没同步（`_total` 有行但 ES 无 doc）→ 走 `getSelfPerformanceByStaff` 默认值 0
5. 员工侧过滤打掉：`hrStatus=false`（已离职）、`roleTag != 1`（非学习顾问）、部门 orgPath 对不上、部门维度下无主岗

### 8.7 复现接口（线上，已实测可用）

**这一步不可省。** 走 baijia-proxy 注入 Cookie，不要手拼 Cookie 串：

```bash
curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" \
 'https://fuwu.baijia.com/bgwApi/fairy/student-center/homePage/getPerformanceRankingList?beginTime=1767196800000&endTime=1830268799000&type=1' \
 -H 'accept: */*' -H 'b_client: EES' \
 -H 'ingress-traffic-env: test-eco-7' -H 'traffic-env: test-eco-7' \
 -H 'referer: https://fuwu.baijia.com/crm/cronus/pageIndex'
```
返回：
```json
{"code":0,"data":{"selfPerformance":{"performancePrice":243942700,"rank":"1","name":"潘佳玉","emailPrefix":"panjiayu"},
 "performanceRankingList":[...5 条...],"size":10,"total":50},"msg":""}
```

要点：
- `beginTime`/`endTime` 是**毫秒时间戳**，`performancePrice` 单位是**分**。**先按业务方看的区间打一次**，
  再按可疑的单日区间打一次做对比 —— 全年 vs 单日结果可能一个是第 1、一个是 0。
- `type`：`1`=本组、`2`=部门（部门维度只看主岗 `jobType==1`）。
- 必带 `b_client: EES`；缺了会走到另一条 `bClient` 分支。
- 测试环境把 host 换成 `https://test-fuwu.baijia.com`，泳道用 `ingress-traffic-env`/`traffic-env`。

**实测三个区间（2026-08-21，panjiayu）**——同一个人，区间不同结论完全相反：

| 区间 | performancePrice（分） | rank | 榜单 |
|---|---|---|---|
| 8/18 单日 | **0** | 3 | 孙超 1830000 / 刘杨威 60000 / 潘佳玉 0 |
| 8/19 单日 | 20000 | 1 | 只有她 |
| 8 月整月 | 26932600 | 1 | 5 人 |
| 全年 | 243942700 | 1 | 5 人 |

⇒ **一定要按业务方截图的那个区间打**。8/18 单日一打就和截图（三个人、她 ¥0.00 排第 3）逐字对上，
换成整月/全年她就是第 1 —— 区间搞错就会得出完全相反的结论。

#### 代课登录（身份 = 代理注入的 `_cas_user_`）

要以某老师身份打线上，先代课。优先用 `baijia-invoke` MCP 的 `cosplay_login` / `cosplay_logout`
（已改成默认一次申请/取消全部项目码）。MCP 不可用时裸打接口，`{"code":0,"msg":"添加成功"}` 即成功。

**代课必须打两次**（projectCode 3 和 4 各一次，`accessPermission` 与之绑定不能互换），
只申请一个会有页面拿不到该老师身份：

```bash
# 登录：3/2 与 4/4 各一次
for pc_ap in "3 2" "4 4"; do
  set -- ${=pc_ap}   # zsh 不做单词分割，必须 ${=var}
  curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" -XPOST \
   'https://sd.baijia.com/suda/cosplay/apply/addNoAudit' \
   -H 'content-type: application/json' -H 'Accept: */*' -H 'identification: microLessonStudent' \
   --data-raw "{\"projectCode\":\"$1\",\"accessPermission\":\"$2\",\"cosAccountName\":\"panjiayu\"}"
done
# 取消（查完务必还原，deleteNoAudit 只认 projectCode）
for pc in 3 4; do
  curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" -XPOST \
   'https://sd.baijia.com/suda/cosplay/apply/deleteNoAudit' \
   -H 'content-type: application/json' --data-raw "{\"projectCode\":\"$pc\"}"
done
```

⚠️ **代课前必须先拿到用户明确授权**，否则 auto-mode 分类器会拦
（提示语大意：impersonating employee X's session … needs explicit user authorization）。
注意：用户一句反问式的「你可以代课 XX 我告诉过你吗」**会被判成质疑而非授权** —— 这时用
AskUserQuestion 要一个明确的「授权」再动手，被拦时不要绕，可先用 8.5 的 SQL 对账顶上。

### 8.8 给业务方的口径

「业绩判对了、归属人是本人、金额也对，落在**物理商品业绩表**里；但 CRM 业绩排行榜的数据源只包含课程类订单业绩，所以非课程类订单（如冲刺营这类商品单元）不会计入排行榜。这是取数链路的覆盖缺口，**不是数据丢失，也不能通过回溯补** —— 要修得让 OMO 判单也发 `OrderAttributionPaidEvent`／把 `performance_physical_attribution` 纳入宽表构造，属需求改动。」
