# 代码入口地图（行号截至 2026-07-30 已核准）

触发条件：对完日志、要跳源码时读。只想快速看懂一次判单，读「主干一」的 ③ 即可。

### 主干一：消息进来 → 业绩落库

```
① MQ 消费分发
   web/mq/rocketmq/consumer/attribution/AttributionOrderEventConsumer.java:37  doConsume
     key = getConsumerPrefix() + tag + "Consumer"，据此找 @Component 名匹配的 handler
   具体订阅者：consumer/attribution/bigclazz/OrderEventConsumer.java（大班课 K12）
              bigclazz/OrderEventAdultConsumer.java（大班课成人）
              bigclazz/paySuccess/OrderPaySuccessDispatcher.java（支付事件另有 dispatcher）
              另有 soloClazz / smallClazz / def / productcenter / phsical 各一套

② Handler：构造凭证 + 触发判单        ★ 从这里开始读最直观
   handler/attribution/bigclazz/OrderCreatedEventHandler.java:53      建单，场景 UNPAID
   handler/attribution/bigclazz/OrderPaySuccessEventHandler.java:102  支付，场景 PAID
     · getOrderBaseInfoDto / getAttributionCredentials → 组 AttributionCredential
     · 模板路由 utils/PerformanceAttributionJudgeTemplateUtil.java:113 getJudgeTemplateBean
                                                        :92  getConfig

③ 判单主干                            ★★ 核心，所有早退点都在这 40 行里
   strategy/AbstractPerformanceAttributionJudgeTemplate.java:212 judgePerformanceAttribution
     ├ :215 filterAttributionCredentials:1237        早退点1「no orders need judge performance」
     │        ├ filterOnlineAttributionCredentials:1260   查 is_attribution（最高频真因）
     │        └ filterAttributionCredentialsByLocal:1287  线下走课程 dataLabel
     ├ :227 待支付凭证校验                            早退点2「no pay credentials does not exist」
     ├ :244 generateAttributionResultsList:1200
     │        ├ 调课单 → generateTransferAttributionResultList（抽象声明 :271）
     │        └ 普通单 → generateNoTransferAttributionResultList:302
     │                    ├ buildAttributionCredential（抽象声明 :281）
     │                    └ generatePerformanceAttribution:360
     │                         早退点3「no attribution configs found」在 :383
     └ :246 insertPerformanceAttribution（抽象声明 :290）

④ K12 大班课具体实现
   strategy/K12ClazzLessonSkuPerformanceAttributionJudgeTemplate.java:123
     generateTransferAttributionResultList —— 调课继承/重判全部逻辑
       :153 整批父单无业绩 → 继承
       :200 该单父单无业绩 → 继承
       :229 judgeSatisfyAllClazzRenewalConfig 决定 继承(:234) / 重判(:247)
   strategy/K12AllAbstractPerformanceAttributionJudgeTemplate.java
       :123 buildAttributionCredential   凭证在 :155 落库（调课单不走这里！）
       :187 insertPerformanceAttribution
       :521 insertK12Attribution → :530 按 orderStatus 分叉
              UNPAID → insertNoPayK12Attribution:575 → performance_order_attribution_no_pay
              其余   → insertPayK12Attribution       → performance_order_attribution
```

**只想快速看懂一次判单**：只读 ③ 的 `judgePerformanceAttribution:212`，四个早退点一目了然。**排查调课单**：再加 ④ 的 `:123`。

### 主干二：判单开关（最高频真因）

```
自动写入（建班 MQ 触发）
  domain/service/performanceconfig/impl/AttributionSettingServiceImpl.java
    :245 insertAttributionSettingByClazzNumber
    :265 → judgeOriginalClass:2152    ★ 规则本体：只有 course_type 30/40 才 =1
人工修改（云帆后台）
  web/controller/AttributionSettingController.java:105  POST /performance/management/setting/modify
    → AttributionSettingServiceImpl.modifyAttributionSetting:1528
    → :1636 起写审计 performance_attribution_setting_log + BOSS 操作日志
```

### 主干三：查询接口（"为什么显示 -"）

```
domain/service/performance/impl/PerformanceBaseServiceImpl.java
  :359  getSimplePerformanceAttributionByOrderNumbers   /feignPerformance/orderPerformance 落到这
  :2281 handleNotJudgeOrders     误导日志在 :2302
          :2344 按 performanceCalculateLimitInHour(24h) 决定输出 "-" 还是 "业绩正在计算中"
```

### 主干四：回溯

```
web/controller/SnowBallController.java
  :143 /test/backtrack/byOrderNumbers    测试后门，单单直打
  :414 /snowball/back/upload
  :422 /snowball/back/create
  :448 /snowball/back/trigger           正式三步流程
      → performance/impl/PerformanceBackToolServiceImpl.java:118 triggerPerformanceAttributionBack（@Async）
      → listener/AttributionBackExcelListener.java:89 backAttributionCanRenewal
            :91  backType=1 判单回溯
            :105 backType=2 可续回溯（另一条线）
底层汇聚点
  performance/impl/BackOrderAttributionController.java:444 backOrderAttributionByOrderNumberList
      :478 按 productType/orderStatus 筛可回溯订单
      :510 getTransferInfoMap —— 调课单在这里被识别
      :529 backCallOutRefundAndAttributionJudge
      :542 递归回溯调课子单
```

### 读码时的两个坑

1. **`BackOrderAttributionController` 不是 Controller** —— 它在 domain 层，是 `BackOrderAttributionService` 的实现类，方法上的 `@RequestBody` 是历史残留。别去 web 层找它。
2. **日志方法名带 `$original$xxx` 后缀**（如 `judgePerformanceAttribution$original$FNtNvIFu:217`）是 APM 字节码增强加的，对应源码就是原方法名，**行号仍然准**，可直接跳。
