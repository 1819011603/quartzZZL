# P0-05 / P0-06 / P0-09：cart 已执行测试的精确对象

本次只提取既有证据，未改代码、未重跑测试、未调用远端接口。核对时 cart 工作区干净，分支 `feature-xuban-pure-relation-20261102`，HEAD=`a34016fdf206d0163b1dd473c67ac10674ecb4b5`，与上轮验证提交相同。

**下面第一至第三节全部为 Java 内存 fixture，不是真实 TEST 续班计划/班级/学员，不可用这些短数字在 EES 查询。** 每个测试独立创建对象；相同数字在不同测试可代表不同字段，不能串成一套真实数据。fixture 的计划名、课程名、商品名、班级名、学员姓名/手机、登录员工、实际开班/计划时间均为「不适用：未设置且未依赖」。年级7/8/9、学期字符串1/2均为测试原值，不能擅自译为现实年级/学期名称。数量指对象/结果条数，不是库存或购买份数，后两者未设。

上轮实际执行环境：本机 JDK1.8.0_202 / Maven3.9.9（mvn8），2026-11-05 10:52:14 +08:00 完成；11类94例，0失败/错误/跳过。总日志 [cart-final-tests.log](/tmp/w1-13ca5996/cart-final-tests.log:224)，每个方法的结果链接指向上轮保存的XML。此文中“实际=预期”指源码断言经该运行通过，不代表存在完整响应JSON快照；未断言的字段明确不扩张。

## 一、P0-05：主计划扩科年级及学年学期

### 共同内存对象（scope 类）

来源：`ExpandSubjectRecommendServiceMainOwnPreCourseTest.java:130` 的 buildContext，`:158`/`:166`/`:172` 三个构造器。

|字段|实际 fixture|
|---|---|
|主/从计划ID|都未设置（null）；该测试绕过计划DTO，直接构造推荐上下文。100/101是**课程ID，不是计划ID**|
|userId|1；学员姓名/手机不适用|
|主前置课程|100；从前置课程101|
|关系|100→后置课程201；101→后置课程202，共2个关系键，每键1门后置课|
|后置课程年级|201:[7]；202:[9]；课程科目列表均为空|
|扩科商品配置|1001/type6004/grade7/subject3；1002/type6004/grade9/subject3，共2条|
|班级ID|preClass.clazzNumber未设置；商品编号不可冒充实际班级记录|
|开关|config.expandSubject=true；主来源集合逐例指定；pureRelationEnabled/Apollo无参与；学年学期反例另设expandExcludeSwitch=true、excludeMode=1|
|已购/结果数量|purchasedPostClazzSkuNumbers为空集合；数量见逐例|
|学年学期|基础fixture未设置；仅下表两例另加前置CourseDTO的2026/"1"与2027/"2"|

|方法及证据|精确输入/变化|预期|上轮实际及断言边界|
|---|---|---|---|
|[ExpandSubjectRecommendServiceMainOwnPreCourseTest#should_only_collect_main_own_post_grades_when_mainOwnPreCourseNumbers_set](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceMainOwnPreCourseTest.java:52)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:124)|mainOwnPreCourseNumbers={100}；前置顺序[100,101]|结果1条，productId=1001|等于预期；过滤掉从课年级9的候选|
|[ExpandSubjectRecommendServiceMainOwnPreCourseTest#should_collect_all_grades_when_mainOwnPreCourseNumbers_empty](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceMainOwnPreCourseTest.java:64)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:123)|mainOwnPreCourseNumbers={}；其余共同fixture|结果2条（旧行为）|size=2断言通过；没有逐项断言商品ID|
|[ExpandSubjectRecommendServiceMainOwnPreCourseTest#should_collect_all_grades_when_mainOwnPreCourseNumbers_null](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceMainOwnPreCourseTest.java:75)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:125)|mainOwnPreCourseNumbers=null|结果2条（旧行为）|size=2断言通过；没有逐项断言商品ID|
|[ExpandSubjectRecommendServiceMainOwnPreCourseTest#should_use_main_year_term_when_related_course_is_first](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceMainOwnPreCourseTest.java:85)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:127)|主来源{100}；前置顺序[101,100]；CourseDTO100:grade7/year2026/term"1"；101:grade9/year2027/term"2"；excludeMode=1，expandExcludeSwitch=true|捕获排除在读请求schoolYearId=2026、schoolTermId="1"|两个字段断言通过；request userId来自context=1，未在此逐字段断言；没有断言最终推荐数量|
|[ExpandSubjectRecommendServiceMainOwnPreCourseTest#should_keep_missing_main_term_when_only_related_term_exists](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceMainOwnPreCourseTest.java:105)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:126)|主来源{100}；前置顺序[100,101]；courseMap只添加101:year2027/term"2"，没有100的CourseDTO；排除开关同上|捕获排除请求schoolYearId=null、schoolTermId=null|两个null断言通过；这是主CourseDTO完全缺失，不是一个已存在DTO仅两个字段为空|

修前对照：`cart-b7-red.log:127` 缺失主课例实际year=2027而预期null；`:135` 从课在前例实际year=2027而预期2026。第一处断言就失败，因此修前日志**没有独立证明term实际值**，不要写成修前term也被断言证实。修前生产基线7bb1fb92，修后a34016fd。

### 大班来源辅助方法和预热保留

以下测试彼此独立，不复用上表对象。

|方法及证据|精确对象/输入|预期与上轮实际|
|---|---|---|
|[RenewalServiceNewLogicTest#should_not_use_related_term_when_main_term_missing](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalServiceNewLogicTest.java:114)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:167)|RecommendContext(userId=1, renewalNumber=100)；主课程列表[100]；courseMap只有键200→CourseDTO(year2027,term"2")，DTO.number未设置；班级/商品/年级/开关均未设置|resolveCurrentPreCourse返回null，assertNull通过；100同时是计划号与主课程键，两个字段各自赋值，不是同一业务对象|
|[RenewalServiceNewLogicTest#should_use_main_term_when_resolving_large_class_expansion](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalServiceNewLogicTest.java:128)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:162)|RecommendContext(userId=1,renewalNumber=100)；主列表[100]；courseMap键100→主DTO(year2026,term"1")，DTO.number未设置；其余同上|返回同一主DTO对象，assertSame通过；未执行完整大班门面推荐|
|[SmallRenewalPreheatServiceTest#should_preserve_main_scope_when_preheating_related_courses](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/SmallRenewalPreheatServiceTest.java:230)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:89)|计划9001，userId参数10001；config初始课程[101]；mock合并赋值[101,102]，未设从计划ID；context仅含1个前置班clazzNumber=201，其courseNumber未设；推荐mock结果为空，context.userId未设；无年级/学期/商品/开关|preheatInternal(10001,9001)后mainOwnPreCourseNumbers={101}、config.courseNumbers=[101,102]，调用expand.recommend(context)；三项断言/verify通过，未断言扩科结果数量|

### 原有扩科服务回归（7例，不代表真实主从计划联测）

此类未创建续班计划ID/班级ID/姓名。字段未提及者未设置；主来源限制字段均未设置。学年/学期均未设置、排除模式未启用。

|方法及证据|精确输入|预期与上轮实际|
|---|---|---|
|[ExpandSubjectRecommendServiceTest#should_returnEmpty_when_expandConfigIsNull](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceTest.java:35)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:82)|空context，userId=null，config=null|0条，对应断言均通过|
|[ExpandSubjectRecommendServiceTest#should_returnEmpty_when_expandSubjectIsFalse](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceTest.java:42)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:81)|config.expandSubject=false，userId=null|0条，对应断言均通过|
|[ExpandSubjectRecommendServiceTest#should_returnEmpty_when_recommendListIsEmpty](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceTest.java:52)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:83)|expandSubject=true，recommendList=[]，userId=null|0条，对应断言均通过|
|[ExpandSubjectRecommendServiceTest#should_matchByGrade_when_contextPath](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceTest.java:63)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:87)|userId=1；前课100→后课200，200.grade=[8]/subject=[3]；候选1001/type6004/grade8/subject3及1002/type6004/grade9/subject3；expandSubject=true、forceBuy=true、已购集合{}|1条，productId1001、EXPAND_SUBJECT、forceBuy=true、signUp=0，对应断言均通过|
|[ExpandSubjectRecommendServiceTest#should_markSignUp_when_alreadyPurchased](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceTest.java:106)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:86)|userId=1；100→200、grade8/subject3；候选1001/type6004/grade8/subject3；expandSubject=true；已购{1001}|1条、signUp=1；没有再次断言productId，对应断言均通过|
|[ExpandSubjectRecommendServiceTest#should_returnEmpty_when_configIsNull_largeClass](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceTest.java:145)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:84)|userId参数1、config=null、courseMap={}、currentCourse=null、已购{}|0条，对应断言均通过|
|[ExpandSubjectRecommendServiceTest#should_matchByGrade_when_largeClassPath](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/ExpandSubjectRecommendServiceTest.java:152)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:85)|userId参数1；courseMap键300→DTO(grade[9],subject[3])，DTO.number未设；候选2001/type6004/grade8/subject3及2002/type6004/grade9/subject3；expandSubject=true、forceBuy=false；currentCourse=null、已购{}|1条、productId2002、forceBuy=false，对应断言均通过|

## 二、P0-06：同年级商品去重与三路优先级

### 最终年级组去重（logic 类）

这些用例仅创建 `Map<Integer,List<ClazzDetailDTO>>`，DTO只设置productSkuNumber；计划ID/userId/课程ID/独立clazzNumber/productType/学年学期/开关**全部未设、不适用**。不存在有效订单或真实班级；构造器见 `RenewalServiceNewLogicTest.java:203`。通过反射调用dedupClazzByGradeByProduct。

|方法及证据|实际输入|预期与上轮实际|
|---|---|---|
|[RenewalServiceNewLogicTest#should_keep_single_when_same_grade_same_product](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalServiceNewLogicTest.java:70)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:168)|{7:[1001,1001,1002]}，3个DTO|{7:[1001,1002]}，size=2且顺序/ID均断言通过|
|[RenewalServiceNewLogicTest#should_not_dedup_when_same_product_across_grades](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalServiceNewLogicTest.java:85)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:164)|{7:[1001],8:[1001]}，共2个DTO|两个年级各1条，size断言通过；此例未单独再次断言ID|
|[RenewalServiceNewLogicTest#should_remove_null_element_and_dedup_product](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalServiceNewLogicTest.java:98)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:166)|{9:[null,1001,1001]}，3个列表元素，其中2个DTO|{9:[1001]}，size=1与ID断言通过|

### 三路合并与保留行为（merge 类7例）

计划ID/userId/独立班级ID/学年学期/姓名均未设。buildResult只设ProductKey(productType,productId)与recommendType，见 `RecommendMergeServiceTest.java:190`；configuredGrade未设置(null)。下面“商品ID”不能称为实际班级号。

|方法及证据|实际输入/配置|预期与上轮实际|
|---|---|---|
|[RecommendMergeServiceTest#should_mergeAll_when_noDuplicates](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/RecommendMergeServiceTest.java:33)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:131)|纯续1001、扩科1002、加购1003，各1条type6004；配置null、context空|3条，size断言通过|
|[RecommendMergeServiceTest#should_dedupByProductId_renewalWins](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/RecommendMergeServiceTest.java:51)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:134)|三路各1条商品1001/type6004，配置null、context空|1条、recommendType=RENEWAL，断言通过；未设年级，此例证明优先级，不单独证明同年级规则|
|[RecommendMergeServiceTest#should_dedupByProductId_expandWinsOverPurchase](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/RecommendMergeServiceTest.java:70)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:128)|纯续空；扩科与加购各1条2001/type6004，配置null|1条、EXPAND_SUBJECT，断言通过|
|[RecommendMergeServiceTest#should_dedupByGradeSubject_when_allowDuplicateIsFalse](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/RecommendMergeServiceTest.java:88)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:129)|纯续1001/type6004，postClass.courseNumber=100/subjectIds=[3]；扩科1002/type6004；courseMap100→DTO(number100,grades[8])；expand.allowDuplicate=false，recommend配置1002/grade8/subject3|1条、RENEWAL，断言通过；两商品不同，是已有年级科目规则|
|[RecommendMergeServiceTest#should_keepDuplicateGradeSubject_when_allowDuplicateIsTrue](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/RecommendMergeServiceTest.java:131)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:132)|与上一例同样1001、1002、课程100/grade8/subject3，但allowDuplicate=true|2条，size断言通过；不能把此既有开关规则写成无条件按学科去重|
|[RecommendMergeServiceTest#should_handleAllNullInputs](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/RecommendMergeServiceTest.java:171)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:130)|三路list均null，config=null，context空|0条|
|[RecommendMergeServiceTest#should_handleAllEmptyInputs](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/small/service/RecommendMergeServiceTest.java:179)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:133)|三路list均[]，config=null，context空|0条|

## 三、P0-09：缓存隔离/开关/异常——cache 类全部10例

共同fixture来源 `RenewalDataServicePureRelationMergeCacheTest.java:59` setup及`:69` main：主计划number=100，courseNumbers=[1]；从计划号列表[200]；mock单查返回DTO只设课程列表（返回DTO.renewalNumber未设，接口入参200才是从计划ID）。**没有userId参数/学员对象、班级、商品、年级、学年学期、订单或姓名。** 所有Redis/Feign/CsCacheWarden均Mock，不访问TEST Redis或数据库。

共同字段开关：pureRelationEnabled=true；renewalCacheEnabled=false；renewalLocalCacheEnabled=false；pureRelationMergeCacheEnabled=true；正TTL=300秒，空TTL=60秒。对应Apollo key依次为renewal.pure.relation.enabled、renewal.query.cache.enabled、renewal.query.local.cache.enabled、renewal.pure.relation.merge.cache.enabled；测试通过Reflection设置字段，不是改Apollo。每例独立重新setup；下表列出覆盖值。

|方法及证据|实际输入/变化|预期与上轮实际/精确验证范围|
|---|---|---|
|[RenewalDataServicePureRelationMergeCacheTest#should_load_and_cache_when_cache_miss](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:85)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:160)|GET renewal:relation:precourse:200→null；单查200→课程[2]|合并课程[1,2]，2门；verify单查200一次；SET同key="[2]"/300秒一次，均通过|
|[RenewalDataServicePureRelationMergeCacheTest#should_use_cache_hit_without_rpc](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:99)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:151)|GET同key→"[2]"|合并[1,2]；verify单查never；无专门验证批量never|
|[RenewalDataServicePureRelationMergeCacheTest#should_treat_empty_sentinel_as_empty](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:111)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:155)|GET同key→"__EMPTY__"|合并仍[1]，1门；单查never；只测读取已存空值，不测空值写入|
|[RenewalDataServicePureRelationMergeCacheTest#should_bypass_cache_when_disabled](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:123)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:152)|pureRelationMergeCacheEnabled=false；单查200→[2]|合并[1,2]；单查200一次；SET never；源码应不读，但本例没有verify GET never|
|[RenewalDataServicePureRelationMergeCacheTest#should_batch_load_when_multiple_misses](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:137)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:153)|从计划列表[200,300]；两次GET默认null；批量入参[200,300]→{200:[2],300:[3]}|合并[1,2,3]，3门；批量一次、单查never；两key各写[2]/[3]及300秒|
|[RenewalDataServicePureRelationMergeCacheTest#should_preserve_main_courses_when_merging_locally_cached_plan](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:156)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:156)|renewalCacheEnabled=true、renewalLocalCacheEnabled=true；CsCacheWarden返回同一个主DTO；GET200→"[2]"；先开关联读取/合并一次，再pureRelationEnabled=false读取/合并一次|第一次请求[1,2]；缓存原对象保持[1]；关总开关后第二次请求[1]，三项assertEquals通过；不是连续两次关联开启|
|[RenewalDataServicePureRelationMergeCacheTest#should_retry_singles_when_batch_lookup_fails](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:175)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:159)|从计划[200,300]；批量抛IllegalStateException("batch unavailable")；单查200→[2]、300→[3]|合并[1,2,3]；只断言结果，未verify每条单查调用次数或写缓存次数|
|[RenewalDataServicePureRelationMergeCacheTest#should_not_cache_failed_lookup_when_single_rpc_fails](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:187)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:157)|单查200抛IllegalStateException("single unavailable")|保持[1]；SET never；故障是单查Feign mock，不是Redis异常|
|[RenewalDataServicePureRelationMergeCacheTest#should_keep_original_when_relation_switch_off](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:197)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:158)|pureRelationEnabled=false，其余共同fixture|保持[1]；单查never、GET never|
|[RenewalDataServicePureRelationMergeCacheTest#should_filter_invalid_relations_and_dedup_courses_when_merging](/Users/gaotu/IdeaProjects/JavaProject/cart/cart-app/src/test/java/com/gaotu/renewal/RenewalDataServicePureRelationMergeCacheTest.java:207)；[通过记录](/tmp/w1-13ca5996/cart-final-TestSuite.xml:154)|从列表[null,100,200,200]；100为自关联；GET200→"[1,2,2]"|合并[1,2]；GET200一次，过滤null/自关联/重复计划且课程去重|

修前日志：[cart-cache-red-rerun.log](/tmp/w1-13ca5996/cart-cache-red-rerun.log:127) 预期缓存[1]、实际[1,2]，在缓存断言处失败；因此修前**没有运行到关开关的后续断言**。修前基线7bb1fb92，修后a34016fd。

**P0-09文案必须标未覆盖的内容**：连续两次都保持关联开启的独立重复请求；无从计划集合null/空的独立用例；Redis GET/SET抛异常；从计划空结果回源后SET __EMPTY__/60秒（目前仅测试哨兵命中读取）。没有这些用例的成功记录，不应把它们写为已执行。60秒是setup配置值，不是本轮已验证的空值写入TTL。

## 四、可引用的历史/旧版本接口对象（与上述内存fixture严格分开）

本节只读取现有文件/归档，未新调用接口。**均不能证明a34016fd已部署或当前实时仍有这些对象。** 下列真实TEST数字不可以回填到上述本地测试“实际输入”栏。

### 已保存的2026-11-05旧版本接口快照

来源 `/tmp/w1-13ca5996/cart-current-interface.json`、`deployed-versions.json`、`plan-batch.json`。cart镜像 `feature-xuban-pure-relation-20261102-7bb1fb92-20261104234532`，pod `cart-gaotu100-com-698968b48f-zj59h`，泳道test-gtbg-dev-3。主Worker此前采集，不是本子任务重测。

- 实际5参调用：`RenewalService#getRenewalDetail(7658127801,585960797778243584,false,false,null)`；traceId=`cart_gaotu100_com.292.17938470529730404`，rvoCode=0。只能证明该旧版本当时返回两模式，不能证明P0-05年级/学期反例或P0-09缓存隔离。
- 学员userId=7658127801；接口快照没有学员姓名/手机，写“未提供”，不要把老师/管理员姓名当学员姓名。

|角色|计划ID及有据名称|前置课程|后置课程|班级/商品|返回结果|
|---|---|---|---|---|---|
|主大班|585960797778243584；dcg-扩科排除-大班计划-1020（plan-batch）|585960577856301056|本响应未给；历史共享后置课记录为585960751831836672，须注明历史|clazz_number/product_sku_number均585960755422160896；本响应无名称|type2、grade16/六年级、signUp=1，1条|
|从小班|586116340522184704；dcg-小班扩科排除-计划（plan-batch）|18314034380997173|18314034380997207|product_sku_number=586097025945298944；dcg-小班扩科排除-数学-后置；响应未单独给clazz_number，按SKU原字段记|type6004、grade11/一年级、signUp=0，1条|

两个计划快照均status=2、isTestData=1；计划schoolYear.id=2026/name2026-2027，schoolTerm=C/春季。主目标2026/X暑假，从目标2027/X暑假。**这些是计划元数据，不是本地反例课程的学期"1"/"2"，也不是已经查证的课程DTO学年学期。** 主计划beginTime=1791561600000/endTime=1798732799000；从计划beginTime=1792476001000/endTime=1795154401000（毫秒原值）。不将计划时段当班级开课时间。请求未提供开关值，不能仅凭该响应宣称某个Apollo配置已被本轮回读。

### P0-06 共享后置课历史已执行样本（2026-11-04）

归档README.md:195开始的“纯并集共享后置课”段：主计划585960797778243584、从计划586116340522184704、学员7658127801；主前置585960577856301056与从前置18314034380997173均映射后置课程585960751831836672，命中班级/商品585960755422160896、grade16。临时course_relation_map行id6584（relation_type=1、calculate_renewal_type=1）令从前置也映射主后置。`getRenewalDetail(...,getContext=true)`返回同grade16商品1次，trace=`cart_gaotu100_com.290.17937312480010090`。当时临时关course.renewal.cache.enabled绕旧关系缓存；已删除6584并恢复true。清理复查trace=`cart_gaotu100_com.298.17937313022720084`。该段未单独记录精确部署SHA，不能自行指定a34016fd；此样本已清理，不能照抄ID声称现在仍具备共享映射。

### P0-05 年级收口历史样本（2026-11-04）

归档README.md:328“小班主路径补”：主小班586116340522184704、从大班585960797778243584，历史学员7658127801（结合相邻同批样本记录；该复验句未重列userId，需原trace确认才可称逐请求完整入参）。主计划临时扩科grade16、商品585963387758962688。修前60468ec8出现该扩科，trace=`cart_gaotu100_com.292.17937852075840016`；修后08228297不再出现、从计划大班纯续保留、主grade11/12扩科不变，trace=`cart_gaotu100_com.291.17937858129660007`。临时扩科id110/反向关系已清理。本历史是**年级**反例，不是2026/1对2027/2学期反例；本段没有可据的商品名/班级名/学员姓名，均不得补造。

### P0-09 历史关联开关对照（不等于本地缓存隔离验收）

归档README.md:204起：同学员7658127801、主计划585960797778243584，关联开→grade16/type2/商品585960755422160896与grade11/type6004/商品586097025945298944；trace=`cart_gaotu100_com.299.1793755522658007`。关联关→仅大班；trace=`cart_gaotu100_com.295.17937555754260008`；已恢复true。该历史没有证明计划Guava缓存组合开启，因此不能替代本轮缓存污染反例验证。B8预热最长26h的接受边界仍保持。

## 五、交给主Worker的文档修订重点

1. P0-05真实TEST隔离反例对象尚未准备；本地已用的课程/商品/userId逐项如上，不得伪装成可登录的真实学员。明确小班缺失用例是CourseDTO整体缺失。
2. P0-06已有去重及优先级组件证据，但三路+共享后置课的完整新版本页面场景未执行；历史共享映射已清理。
3. P0-09已执行的10个方法逐项可追溯；Redis异常、负缓存写入和连续两次关联开启等步骤列为未执行，不报通过。
4. 只将本文件内容整合到共享P0/飞书文档；本子任务没有改共享文档、没有发送飞书消息、没有重跑成功测试。
