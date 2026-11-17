# W1 矩阵造数台账 2026-11-17（TEST）
- M23 大班主(联报23) 591020372877623296  clone-plan src=590563861447557120 keep-dept
- S2  大班从(班级2)  591020374322561024  clone-plan src=590563861447557120 keep-dept
- build(语文,price100,published): M23 pre_course 591020433489467393 / post 591020448289069056,591020455996102656 ; S2 pre 591020433489467392 / post 591020448295360512（build 自带班不可售，不用）
- 正经可售班(create_renewal_regression_clazz, 100分): M23pre 591020573289676800 / M23postA 591020573128196096 / M23postB 591020573595860992 / S2pre 591020573124001792 / S2post 591020573457448960
- 联报活动 A23 591020757501380608 = {M23postA,M23postB} 价100
- 联报ID文件 https://test-i.gsxcdn.com/11499079_n6g6vnnj.xlsx (fid 11499079, 内容: 联报ID / 591020757501380608)
- 新建学员: stu1 7746793735(1211717117) stu2 7746793736(1211717217) stu3 7746791482(1211717317)
- 6单已付(order_status=2):M23pre(591020573289676800)×stu1/2/3, S2pre(591020573124001792)×stu1/2/3
- M23→[S2(591020374322561024),小班(588506246722727936)] 关联已绑 verified=true
- M23 effective=true,productType=23,productNumberList=[591020757501380608]
- S2 effective=true,productType=2
- 旧路径基线(V2关) getRenewalDetail M23 stu1 tid=cart_gaotu100_com.283.17949014046100015: code=0,productType=23,activityNumber=591020757501380608,clazzA 591020573128196096,grade=15(五年级语文),allSignUp=0,signUp=0 ✓
## 旧路径(V2关)基线验证(test-eco-8 d95f0512)
- M23 stu1 7746793735: productType=23, activityNumber=591020757501380608, clazzA, grade=15, allSignUp=0, signUp=0, status=0 ✓ TID=cart_gaotu100_com.283.17949014046100015
- M23 stu2 7746793736: same 1条23型 grade=15, status=0 ✓ TID=cart_gaotu100_com.288.17949014418970012
- S2 stu1 7746793735: productType=2, clazz=591020573457448960, grade=15, status=0 ✓ TID=cart_gaotu100_com.290.17949014424910018
- S2 stu2 7746793736: productType=2, 1条, grade=15 ✓ TID=cart_gaotu100_com.292.17949014620980010
- M23 stu3 7746791482: productType=23, 1条 grade=15 ✓ TID=cart_gaotu100_com.285.17949014612630013
## 旧路径基线(续)
- S2 stu3 7746791482: productType=2, 1条, grade=15 ✓ TID=cart_gaotu100_com.289.17949014804290015
- 7704848531无前置单→M23主计划591020372877623296: status=0,grade_clazz_list=空 ✓ 预期
- 小班(588671894562123776) 7704848531: status=0,无grade_clazz_list → 该计划前置班无7704848531订单,符合预期
- T-26存量 7704848531→590563861447557120(大班主+从): role1 590564278055026688(主后置) + role2 590564441871958016(从后置) ✓ TID=cart_gaotu100_com.289.17949016050610027
- preheat(7746793735,591020372877623296) 写缓存: 前置课591020433489467393→联报591020757501380608/班591020573128196096 ✓ TID=cart_gaotu100_com.290.17949015638070043
- 新建学员 stu4 7746791494(12117171417) stu5 7746791496(12117171517)
- 小班6004前置SKU 588506026511294464(计划588506246722727936) 0元单: stu1 pay 434760008023933221 / stu2 pay 434760012310511787, order_item.order_status=2 ✓
- 小班6004前置SKU 586084334251927552(计划586116340522184704,up_status=0也可下单) 0元单: stu4 434760170150559851 / stu5 434760174445527226
## e6199773 (pod 78d4855cbb) 测试
- 旧链路23 预热→C端读命中: log RenewalService:1322 renewal-data-from-preheat TID cart_gaotu100_com.283.17949016949660031 ✓
- 小班6004从计划 stu1 → 588506155490336768 grade11 ✓ TID .283.17949018423020034
- V2组件: resolveRelated(M23)→从[S2 pt2, 小班 pt6004] ✓ TID .290.17949018785500050; 60s内重复调用无下游RPC(缓存命中) TID .289.17949020796600034 vs 未命中 .291.17949020641030044 ✓
- V2组件: getRelatedPlanDetail S2→pt2 ✓ .286.17949018663040032; 小班从→6004 ✓ .292.17949020653270036; getMainPlanDetailSkipPreheat M23→23 ✓ .287.17949020663270037
- P1: stu4@586116340522184704 未命中 1纯续+4扩科 TID .292.17949019848590033; preheatAndCache 写 key renewal:preheat:586116340522184704:7746791494 TID .284.17949019988990039; 命中(log small preheat cache hit) 1纯续+4扩科一致 TID .291.17949020108120042 ✓
- 新发现: 小班缓存payload含debug_info日志(PROD renewal.small.builder.debug.enabled=true)
- ~~51计划589721954597011456推不出: 组合SKU 589762111522013184 sale_status=1/up0, 子班saleStatus=50 salable=false (存量数据问题)~~
  **【2026-11-17 已推翻】** 真实入口 `RenewalService#getRenewalDetail`(7704848531, 589721954597011456) **正常返回 1 条 product_type=51**(sku 589762111522013184, grade=11, price=0, all_sign_up=0)，trace `cart_gaotu100_com.289.17949067348720087`。
  当时推不出是因为缺续班关系(`18405861174936317 → 18405861174936327`)：补关系后即可返回。组合 SKU `sale_status=1`/`can_be_sold=false` **不是阻断项**——`can_be_sold` 是派生字段非持久化列；cart 消费 `canBeSold` 仅 `SmallClazzAgger:59`(单商品)与 `SmallRenewalService:423`(**SPU**, 值 true)，组合 SKU 自身无人消费；`isCombineCanSale` 判 SPU.canBeSold + 组合库存(capacity=-1 不校验)。**无需数据修正，0 次写入。**
- 关系方向(已核实, 代码依据 `RenewalService.java:3162-3172` 注释「前置获取后置课程」+ `RenewalCourseDTO` 字段语义): `18405861174936317` 是**前置**课程，`18405861174936327` 是**后置**课程。trace `cart_gaotu100_com.285.17949067511850106`。
- 组合字段只读回读 trace `cart_gaotu100_com.288.17949067043950084`：SKU type=51/sale_status=1/up_status=0/can_be_sold=false/capacity=-1；SPU 589762111519916032 sale_status=40/saleable=0/can_be_sold=**true**；子 SKU 589048589437788160 sale_status=40/up=1/cap=20；子 SKU 587755482459084800 sale_status=40/up=0/cap=32。
- 完整覆盖报告见 `artifacts/20261117-v2-test-coverage-report.md`。
