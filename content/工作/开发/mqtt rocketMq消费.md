


1. 获取topic的partition数量  (使用MessageListener方式) 直接搜topic名称就知道partition数量了


调用该命令获取

```shell
sc -d com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.factory.MQClientInstance
```


循环 arthas 获取对象
```shell
vmtool -x 3 --action getInstances --className com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.factory.MQClientInstance  --express '@com.alibaba.fastjson.JSONObject@toJSONString(instances.{topicRouteTable})'  -c 22db8f4
```


使用策略模式

```
sc -d org.apache.rocketmq.client.impl.factory.MQClientInstance
```

```
vmtool -x 3 --action getInstances --className org.apache.rocketmq.client.impl.factory.MQClientInstance  --express '@com.alibaba.fastjson.JSONObject@toJSONString(instances.{topicRouteTable})'  -c 22db8f4
```

![[../壁纸/附件/Pasted image 20250310102331.png]]


### MQ隔离 泳道

反编译网站:  https://www.decompiler.com/   需要开启clash

MqIsolationUtil


###  艾明 我还有一个问题 刚刚的这个dropMsg方法 我怎么没有看到调用方  发送方这个parentEnv是怎么染上去的

在plugin里面的rocketmq的plugin里

produce interceptor

获取plugin路径
```
vmtool -x 3 --action getInstances --className com.baijia.gapm.apm.agent.core.plugin.PluginResourcesResolver  --express '@com.baijia.gapm.apm.agent.core.util.GsonUtil@toJson(new com.baijia.gapm.apm.agent.core.plugin.PluginResourcesResolver().getResources())'  -c 18b4aac2

```
结果

```json
["jar:file:/apps/srv/instance/multi-test/plugins/apm-spring-core-patch-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-jdbc-commons-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-jdk-threading-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-springmvc-annotation-4.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/lettuce-5.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/gateway-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/spring-context-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/graceful-shutdown-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/rocketmq-ons-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-jdk-http-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/openfeign-3.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-mysql-5.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-springmvc-annotation-3.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/elastic-job-3.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-httpclient-3.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/tomcat-7.x-8.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-mysql-6.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/netflix-eureka-client-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/hikaricp-3.x-4.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-httpClient-4.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-hystrix-1.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-jedis-2.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/grpc-1.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-redisson-3.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/openfeign-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-kafka-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-feign-default-http-9.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/netflix-ribbon-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/okhttp-4.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/spring-annotation-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-okhttp-3.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/druid-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-mongodb-3.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/testa-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/spring-loadbalancer-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/spring-loadbalancer-common-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/spring-job-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-mysql-8.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/elastic-job-2.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-hbase-1.x-2.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-spring-kafka-2.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-elasticsearch-6.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-mongodb-2.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-elasticsearch-5.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/rocketmq-ons-drop-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apache-rocketmq-4.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-spring-kafka-1.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/mybatis-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/apm-springmvc-annotation-5.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/xxl-job-2.x-plugin-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/plugins/elasticsearch-common-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/activations/apm-toolkit-log4j-1.x-activation-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/activations/apm-toolkit-trace-activation-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/activations/apm-toolkit-log4j-2.x-activation-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/activations/apm-toolkit-logback-1.x-activation-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/spi/openfeign-spi-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/spi/kafka-spi-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/spi/druid-spi-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/spi/openfeign-3.x-spi-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/spi/hikaricp-3.x-4.x-spi-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/spi/gateway-spi-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/spi/rocketmq-ons-spi-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/spi/jdbc-commons-spi-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def","jar:file:/apps/srv/instance/multi-test/spi/tomcat-7.x-8.x-spi-7.0.0-SNAPSHOT.jar!/skywalking-plugin.def"]
```


查看MqIsolationUtil.dropMsg 是被谁调用的

```
stack com.baijia.gapm.apm.agent.core.uqun.config.MqIsolationUtil  dropMsg  -n 5 
Press Q or Ctrl+C to abort.
Affect(class count: 1 , method count: 1) cost in 732 ms, listenerId: 1
ts=2025-04-11 10:26:48.061;thread_name=ConsumeMessageThread_1;id=1174;is_daemon=false;priority=5;TCCL=org.springframework.boot.loader.LaunchedURLClassLoader@783efb48
    @com.baijia.gapm.apm.agent.core.uqun.config.MqIsolationUtil.dropMsg()
        at com.baijia.gapm.spi.plugin.alibaba.rocketmq.ons.MessageConsumeDropInterceptor.beforeApmMethod(MessageConsumeDropInterceptor.java:42)
        at com.baijia.gapm.apm.agent.core.plugin.interceptor.enhance.SwitchAwareInstanceMethodsAroundInterceptor.beforeMethodDo(SwitchAwareInstanceMethodsAroundInterceptor.java:29)
        at com.baijia.gapm.apm.agent.core.plugin.interceptor.enhance.InstMethodsInter.intercept(InstMethodsInter.java:78)
        at com.aliyun.openservices.ons.api.impl.rocketmq.ConsumerImpl$MessageListenerImpl.consumeMessage(ConsumerImpl.java:-1)
        at com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.consumer.ConsumeMessageConcurrentlyService$ConsumeRequest.run(ConsumeMessageConcurrentlyService.java:710)
        at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
        at java.util.concurrent.FutureTask.run(FutureTask.java:266)
        at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
        at java.lang.Thread.run(Thread.java:750)
```

可以发现调用方是com.baijia.gapm.spi.plugin.alibaba.rocketmq.ons.MessageConsumeDropInterceptor.beforeApmMethod(MessageConsumeDropInterceptor.java:42)


查看是哪个plugin的类
```

find  /apps/srv/instance -name "*.jar" -exec sh -c '
  for jar; do
    if unzip -p "$jar" | strings | grep -qF "AbstractConsumeMessageDropInterceptor"; then
      echo "$jar"
    fi
  done
' sh {} +

```

结果是/apps/srv/instance/multi-test/spi/rocketmq-ons-drop-spi-7.0.0-SNAPSHOT.jar 插件


拉取下jar包 进行反编译包
使用这个文件进行拉取  http://genshuixue-public.oss-cn-beijing.aliyuncs.com/origin_test/2024-06-26/ce6abfc1fd6677f9c69b634e17ed4055/ossUpload

最终jar包路径:  http://genshuixue-public.oss-cn-beijing.aliyuncs.com/origin_test/2025-04-11/db7a287250dc131206ad9ece624fee6d/rocketmq-ons-drop-spi-7.0.0-SNAPSHOT.jar


进行反编译 https://www.decompiler.com/  
http://www.javadecompilers.com/
```
反编译网站:  https://www.decompiler.com/   需要开启clash
```


可以看到是调用MqIsolationUtil.dropMsg 返回true 就不处理这条MQ
![[../壁纸/附件/Pasted image 20250411105551.png]]


消费的时候如何拿到traffic-env


按-进行分隔 再对Base64 进行解码 对sw8和sw7字段进行解析 把结果输出


![[../壁纸/附件/Pasted image 20250411183833.png]]

```
[arthas@1]$  watch com.aliyun.openservices.ons.api.MessageListener consume '{@com.alibaba.fastjson.JSON@toJSONString(params)}'  -n 5  -x 3 
Press Q or Ctrl+C to abort.
Affect(class count: 9 , method count: 8) cost in 2713 ms, listenerId: 18
method=com.gaotu.student.data.facade.mq.ads.delaycheck.solo.assistant.SoloAssistantDelayCheckConsumer.consume location=AtExit
ts=2025-04-11 18:36:19.400; [cost=358.151461ms] result=@ArrayList[
    @String[[{"body":"eyJzaGFyZGluZ0tleSI6Ijg2NDUxLTYwMTE0MjEwMjQifQ==","bornHost":"/123.57.250.5:26698","bornTimestamp":1744367178678,"key":"","msgID":"0AFFBBC500017578E06A377473B6EE56","offset":32244,"reconsumeTimes":0,"shardingKey":"","startDeliverTime":1744367778675,"tag":"user_init_tag","topic":"student-data_ads_solo_assistant_user_delay_check_test","topicPartition":{"partition":"cn-qingdao-public-share-19-1#4","topic":"student-data_ads_solo_assistant_user_delay_check_test"},"userProperties":{"MSG_REGION":"cn-qingdao-publictest","UNIQ_KEY":"0AFFBBC500017578E06A377473B6EE56","TRACE_ON":"true","sw8":"1-c3R1ZGVudC1kYXRhLjgyNjEuMTc0NDM2NzE3ODM2MzAwMDk=-c3R1ZGVudC1kYXRhLjI0MTIuMTc0NDM2NzE3ODY2NzAxMTE=-11-c3R1ZGVudC1kYXRh-c3R1ZGVudC1kYXRhLTdmYjQ2NGI1NDUtZ2NteHovMTAuMjU1LjE4Ny4xOTc=-L3N0dWRlbnQtZGF0YV9hZHNfc29sb19hc3Npc3RhbnRfdXNlcl9vcmRlcmVkX3Rlc3QvR0lEX3N0dWRlbnQtZGF0YV9hZHNfc29sb19hc3Npc3RhbnRfdXNlcl9lbnRlcl9vcg==-Ti9B","sw7":"v2-c3R1ZGVudC1kYXRhLjgyNjEuMTc0NDM2NzE3ODM2MzAwMDk=-c3R1ZGVudC1kYXRhLjI0MTIuMTc0NDM2NzE3ODY2NzAxMTE=-MTE=-c3R1ZGVudC1kYXRh-dGVzdA==-dGVzdA==-MA==","CONSUME_START_TIME":"1744367779032","TIMER_ENQUEUE_MS":"1744367178000","TIMER_DELIVER_MS":"1744367778675","__MESSAGE_DECODED_TIME":"1744367779031","__CRC32#":"0232302610","__FQN_TOPIC":"student-data_ads_solo_assistant_user_delay_check_test","TIMER_OUT_MS":"1744367778000","TIMER_DEQUEUE_MS":"1744367779022"}},{"acknowledgeIndex":2147483647}]],
]
```



输出是否有被代理
```

  echo "v2-ZjU2YTJmN2QtYjFhNy00NzU5LTlmNDItOWE4MjRlOTIyOGRmLjAuMw==-dGVhY2hlci10b29sLjE5MS4xNzU4MTc2NjM0ODYyMDAzMw==-MTQ=-dGVhY2hlci10b29s-dGVzdC1jcm0tZGV2LTM=-dGVzdC1jcm0tZGV2LTM=-MA==" \
| tr '-' '\n' \
| while read part; do
    decoded_part=$(echo "$part" | base64 --decode 2>/dev/null || echo "(原文)")    
    printf "%s -> %s\n" "$part" "$decoded_part"
  done

```



结果: 
解析是通过
com.baijia.gapm.apm.agent.core.context.ContextCarrier  deserialize 方法

```

==== sw8 解码结果 ====
v2 => (无法解码)
c3R1ZGVudC1kYXRhLjI2MDE5LjE3NDQzNjQ0MjA2OTAwMDI5 => student-data.26019.17443644206900029
c3R1ZGVudC1kYXRhLjI2MDE5LjE3NDQzNjQ0MjA2OTAwMDI4 => student-data.26019.17443644206900028
MA== => 0
c3R1ZGVudC1kYXRh => student-data
dGVzdA== => test
dGVzdA== => test
MA== => 0

==== sw7 解码结果 ====
1 => (无法解码)
c3R1ZGVudC1kYXRhLjI2MDE5LjE3NDQzNjQ0MjA2OTAwMDI5 => student-data.26019.17443644206900029
c3R1ZGVudC1kYXRhLjI2MDE5LjE3NDQzNjQ0MjA2OTAwMDI4 => student-data.26019.17443644206900028
0 => (无法解码)
c3R1ZGVudC1kYXRh => student-data
c3R1ZGVudC1kYXRhLTdmYjQ2NGI1NDUtemRmd2wvMTAuMjU1LjE2MC4xMjE= => student-data-7fb464b545-zdfwl/10.255.160.121
L2R3c19mdXd1X2xlYXJuX3N0YXRpc3RpY19kYXRhX3Rlc3Q= => /dws_fuwu_learn_statistic_data_test
Ti9B => N/A
```








MessageSendInterceptor

```

ts=2025-06-23 15:06:26.260;thread_name=MQTraceSendThread_0_3;id=2160;is_daemon=false;priority=5;TCCL=org.springframework.boot.loader.LaunchedURLClassLoader@1532c619
    @com.baijia.gapm.apm.agent.core.context.ContextCarrier.serialize()
        at com.baijia.gapm.apm.agent.core.context.GapmCarrierItem.<init>(GapmCarrierItem.java:14)
        at com.baijia.gapm.apm.agent.core.context.ContextCarrier.items(ContextCarrier.java:148)
        at com.baijia.gapm.apm.plugin.alibaba.rocketmq.ons.MessageSendInterceptor.beforeMethod(MessageSendInterceptor.java:51)
        at com.baijia.gapm.apm.agent.core.plugin.interceptor.enhance.SwitchAwareInstanceMethodsAroundInterceptor.beforeMethodDo(SwitchAwareInstanceMethodsAroundInterceptor.java:41)
        at com.baijia.gapm.apm.agent.core.plugin.interceptor.enhance.InstMethodsInter.intercept(InstMethodsInter.java:78)
        at com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.MQClientAPIImpl.sendMessage(MQClientAPIImpl.java:-1)
        at com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.producer.DefaultMQProducerImpl.sendKernelImpl(DefaultMQProducerImpl.java:773)
        at com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.producer.DefaultMQProducerImpl.sendDefaultImpl(DefaultMQProducerImpl.java:565)
        at com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.producer.DefaultMQProducerImpl.sendDefaultImpl(DefaultMQProducerImpl.java:520)
        at com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.producer.DefaultMQProducerImpl.send(DefaultMQProducerImpl.java:498)
        at com.aliyun.openservices.shade.com.alibaba.rocketmq.client.producer.DefaultMQProducer.send(DefaultMQProducer.java:344)
        at com.alibaba.ons.open.trace.core.dispatch.impl.InnerTraceProducer$AsyncAppenderRequest.sendTraceDataByMQ(InnerTraceProducer.java:407)
        at com.alibaba.ons.open.trace.core.dispatch.impl.InnerTraceProducer$AsyncAppenderRequest.flushData(InnerTraceProducer.java:371)
        at com.alibaba.ons.open.trace.core.dispatch.impl.InnerTraceProducer$AsyncAppenderRequest.sendTraceData(InnerTraceProducer.java:340)
        at com.alibaba.ons.open.trace.core.dispatch.impl.InnerTraceProducer$AsyncAppenderRequest.run(InnerTraceProducer.java:311)
        at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:511)
        at java.util.concurrent.FutureTask.run(FutureTask.java:266)
        at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
        at java.lang.Thread.run(Thread.java:750)
```


apache-rocketmq-4.x-plugin-7.0.0-SNAPSHOT.jar

![[../壁纸/附件/Pasted image 20250623151808.png]]



watch com.baijia.gapm.apm.plugin.alibaba.rocketmq.ons.MessageSendInterceptor beforeMethod '{@Thread@currentThread().getName(),@com.alibaba.fastjson.JSON@toJSONString(params[3])}'  -n 5  -x 3 


![[../壁纸/附件/Pasted image 20250623152737.png]]


```
KEYS1174735937867874304 0AFFB8400001323659F874A99E307E1FUNIQ_KEY0AFFA21200011532C61974A99E39B535WAITtruesw81-c3R1ZGVudC1kYXRhLWR3cy4yMTc0LjE3NTA2NjQ0NzMxNDUzNTg0-c3R1ZGVudC1kYXRhLWR3cy4yMTc0LjE3NTA2NjQ0NzMxNDUzNTg0-0-c3R1ZGVudC1kYXRhLWR3cw==-c3R1ZGVudC1kYXRhLWR3cy01OWY1Y2M5N2M1LXdsejcyLzEwLjI1NS4xNjIuMTg=-c3R1ZGVudC1kYXRhLWR3cw==-Ti9Bsw7v2-c3R1ZGVudC1kYXRhLWR3cy4yMTc0LjE3NTA2NjQ0NzMxNDUzNTg0-c3R1ZGVudC1kYXRhLWR3cy4yMTc0LjE3NTA2NjQ0NzMxNDUzNTg0-MA==-c3R1ZGVudC1kYXRhLWR3cw==-dGVzdA==-dGVzdA==-MQ==
```

![[../壁纸/附件/Pasted image 20250623154355.png]]



### 如何使用泳道隔离

1. 发送方  
![[../壁纸/附件/Pasted image 20250624111103.png]]

2. 消费方

![[../壁纸/附件/Pasted image 20250624111125.png]]







### 如何在消费者启动前修改groupId agent方式


```
要在消费者启动前通过 **Agent** 修改 `groupId`，你可以利用 **Java Instrumentation** 和 **Java Agent** 技术来动态修改应用程序的字节码。这样你可以在消费者启动之前拦截和修改代码中的 `groupId` 配置。具体的步骤如下：

### **步骤概述**

1. **编写 Agent 类**：这个 Agent 类可以在应用启动时，通过 `Java Agent` 来拦截并修改 `RocketMQ` 消费者的 `groupId` 配置。
    
2. **使用 Instrumentation 机制**：通过 Instrumentation API，在类加载时修改消费者的 `groupId`。
    
3. **将 Agent 包含到启动参数中**：确保应用启动时加载 Agent，通常通过 JVM 参数来指定。

```

```java
import java.lang.instrument.Instrumentation;
import java.lang.reflect.Field;

public class RocketMQAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        // 通过代理修改 RocketMQ 消费者的 groupId
        inst.addTransformer((loader, className, classBeingRedefined, protectionDomain, classfileBuffer) -> {
            // 检查类名是否是 RocketMQ Consumer 类
            if (className.equals("org/apache/rocketmq/consumer/DefaultMQPushConsumer")) {
                // 通过反射修改该类的 groupId 属性
                try {
                    Class<?> consumerClass = Class.forName("org.apache.rocketmq.client.consumer.DefaultMQPushConsumer");
                    Field groupIdField = consumerClass.getDeclaredField("consumerGroup");
                    groupIdField.setAccessible(true);

                    // 你可以在这里修改 groupId 的值，例如根据某些条件来确定 groupId
                    String newGroupId = "newGroupId-" + System.currentTimeMillis();  // 示例动态生成 groupId
                    groupIdField.set(null, newGroupId);

                    System.out.println("GroupId set to: " + newGroupId);  // 打印新设置的 groupId
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
            return classfileBuffer; // 不修改字节码则返回原始字节码
        });
    }
}

```



下面是一个 **自定义 Producer 拦截器**，它在消息发送前 **给消息增加 "source" 标记**，并在发送后 **打印发送结果**。 ProducerInterceptor

## **什么是 RocketMQ Consumer Interceptor？**

RocketMQ 提供了 `org.apache.rocketmq.client.consumer.interceptor.ConsumeMessageInterceptor` 接口，它可以拦截 **消息消费的过程**。

拦截器可以：

- **修改消息内容**（如添加解密逻辑）
    
- **记录日志**（跟踪消息消费）
    
- **埋点监控**（统计消费成功率、耗时等）
    
- **异常处理**（异常信息捕获）
    
- **进行消费权限控制**


GAPM-16-测试环境MQ group自动创建:  https://wiki.baijia.com/pages/viewpage.action?pageId=204147206

### 方案设计：基于 **单Topic + 多GroupId** 实现泳道隔离

**核心思路**：

1. **单Topic多泳道**：所有泳道的消息发送到同一个 Topic。
2. **消息染色**：生产者 Agent 自动在消息属性（Properties）中注入泳道标识。
3. **动态GroupId**：消费者 Agent 为每个泳道生成唯一 GroupId，并基于 SQL 过滤仅消费本泳道消息。


配了策略 即便策略没有命中 并且应用隔离为True 即便这个泳道没有起 test环境也会去消费


```shell

vmtool -x 3 --action getInstances --className com.baijia.gapm.apm.agent.core.uqun.report.HttpConfigReporter  --express '@com.baijia.gapm.apm.agent.core.util.GsonUtil@toJson(instances[0].appConfig())'  -c 18b4aac2

vmtool -x 3 --action getInstances --className com.baijia.gapm.apm.agent.core.uqun.report.HttpConfigReporter  --express '@com.baijia.gapm.apm.agent.core.util.GsonUtil@toJson(instances[0].longPoolingConfigChange(@com.baijia.gapm.apm.agent.core.util.GsonUtil@fromJson("{\"serviceName\":\"student-data\",\"hostIp\":\"10.255.180.205\",\"envName\":\"test-BJ-Ali1\",\"subEnv\":\"test\",\"inContainer\":true,\"version\":\"v7.0.0_241225\",\"heartbeatMillis\":1743660153092,\"configVersion\":\"031f5da2e9e822d8a36be6b47b6e94e1\",\"profile\":\"test\"}",@com.baijia.gapm.apm.agent.core.uqun.report.AppConfig@class)))'  -c 18b4aac2


getstatic com.baijia.gapm.apm.agent.core.config.Config$Agent REPORT_FETCH_URL -x 3

获取服务对应的配置  configVersion在这个里面
curl --location --request POST 'https://test-qingzhou.baijia.com/qingzhou/gapm/agent/heartbeat/open/checkin' \
--header 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36' \
--header 'Content-Type: application/json' \
--header 'Accept: */*' \
--header 'Host: test-qingzhou.baijia.com' \
--header 'Connection: keep-alive' \
--data-raw '{"serviceName":"student-data","hostIp":"10.255.180.205","envName":"test-BJ-Ali1","subEnv":"test","inContainer":true,"version":"v7.0.0_241225","heartbeatMillis":1743660153092,"configVersion":"031f5da2e9e822d8a36be6b47b6e94e1","profile":"test"}'





获取Config.Agent.PROFILE的值
getstatic com.baijia.gapm.apm.agent.core.config.Config$Agent PROFILE -x 3
getstatic com.baijia.gapm.apm.agent.core.config.Config$Route DEFAULT_TRAFFIC_ENV -x 3


获取每个topic的隔离配置
vmtool -x 3 --action getInstances --className com.baijia.gapm.apm.agent.core.uqun.config.AppConfigHolder  --express '@com.baijia.gapm.apm.agent.core.util.GsonUtil@toJson(instances[0].mqTopicConfigMap())'  -c 18b4aac2

{"gaotu_dynamic_form_config_event_test":{"topic":"gaotu_dynamic_form_config_event_test","envIsolation":false,"strategies":[]},"gaotu_contentReport_event_test":{"topic":"gaotu_contentReport_event_test","envIsolation":true,"strategies":[]}}



```




MQ手动验证时 会使用公共的线程池的线程进行消费, 不会使用对应的Consumer的线程池


![[../壁纸/附件/Pasted image 20250403160457.png]]






### java RocketMQ的线程池是针对group的, 还是针对于每一个topic的


```markdown
在 Java 的 RocketMQ 客户端中，线程池一般是**针对 Consumer Group（消费组）**的，而不是针对每个 Topic 的。这是因为在 RocketMQ 中，消息的消费是以消费组为基本单位进行的，而不是以 Topic 为单位的。

### 具体机制说明

- **Consumer Group** 是一组消费者的集合，RocketMQ 会确保同一 Consumer Group 内的每个消息只会被其中一个消费者消费一次。不同 Consumer Group 则可以独立消费同一个 Topic 的消息。
- 每个消费组在启动时会创建一个独立的线程池用于处理消息消费，消费线程池的大小可以通过设置参数 `consumeThreadMin` 和 `consumeThreadMax` 来控制。

### 消费线程池的配置

- 在每个 `Consumer Group` 内可以消费多个 Topic，但这些 Topic 共享同一个线程池。  
- 具体来说，RocketMQ 的消费线程池是通过 `DefaultMQPushConsumer` 的 `consumeThreadMin` 和 `consumeThreadMax` 来管理线程数量，这些线程会根据分配给该 Consumer Group 的队列来并发消费消息。  
- 因此，**如果同一个 Consumer Group 消费多个 Topic 的消息，这些 Topic 的消息会在同一个线程池中处理**。

### 举例说明

假设一个消费组 `GroupA` 同时订阅了 `Topic1` 和 `Topic2`，则 `GroupA` 的消费者实例会通过其内部的消费线程池来并发处理来自 `Topic1` 和 `Topic2` 的消息。此时，不会为 `Topic1` 和 `Topic2` 分配单独的线程池。

### 结论

RocketMQ 中消费线程池的粒度是**基于消费组**的，而不是基于每个 Topic。
```

### 停止服务消费

java -jar arthas-boot.jar --use-version 3.7.2

sc -d com.baijia.ss.msg.center.lib.consumer.AbsConsumer

getstatic com.baijia.ss.msg.center.lib.consumer.AbsConsumer topicAndTag2Consumer -x 1
ognl '@com.baijia.ss.msg.center.lib.consumer.AbsConsumer@topicAndTag2Consumer.remove("test-ss-msg-qi-chatroom-chat-detail:qi-chatroom-chat-detail")' -c 3bfc6a5e
ognl '@com.baijia.ss.msg.center.lib.consumer.AbsConsumer@topicAndTag2Consumer.remove("test-ss-msg-qi-chatroom-chat-detail:wk-qi-chatroom-chat-detail")' -c 3bfc6a5e

ognl '@com.baijia.ss.msg.center.lib.consumer.AbsConsumer@topicAndTag2Consumer.get("test-ss-msg-qi-chatroom-chat-detail:wk-qi-chatroom-chat-detail")' -c 3a5c2626

```java
@ConcurrentHashMap[
    @String[test-ss-msg-chatroom-join-none-repeat:out-chatroom-join-none-repeat]:@JoinChatroomConsumer[com.baijia.tongbao.rocketmq.JoinChatroomConsumer@7e9cbcde],
    @String[test-ss-msg-friend-request:wk-friend-request]:@RobotApplyFriendRequestConsumer[com.baijia.tongbao.rocketmq.RobotApplyFriendRequestConsumer@32ee748e],
    @String[test-ss-msg-win-friend-chat:wk-win-friend-voice-chat]:@VoiceSilkConsumer[com.baijia.tongbao.rocketmq.VoiceSilkConsumer@6c2a8baf],
    @String[test-ss-msg-friend-request:friend-request]:@RobotApplyFriendRequestConsumer[com.baijia.tongbao.rocketmq.RobotApplyFriendRequestConsumer@32ee748e],
    @String[test-ss-msg-chatroom-join-none-repeat:chatroom-join-none-repeat]:@JoinChatroomConsumer[com.baijia.tongbao.rocketmq.JoinChatroomConsumer@7e9cbcde],
    @String[test-ss-msg-qi-friend-chat-detail:wk-qi-friend-chat-detail]:@WindowsFriendMsgConsumer[com.baijia.tongbao.rocketmq.WindowsFriendMsgConsumer@6f7c04f5],
    @String[test-ss-msg-robot-task:robot-task]:@RobotTaskConsumer[com.baijia.tongbao.rocketmq.RobotTaskConsumer@52a98a2b],
    @String[test-ss-msg-qi-friend-chat-detail:qi-friend-chat-detail]:@WindowsFriendMsgConsumer[com.baijia.tongbao.rocketmq.WindowsFriendMsgConsumer@6f7c04f5],
    @String[test-ss-msg-databus:storm-sun-device]:@RobotRecordStormSunDeviceConsumer[com.baijia.tongbao.rocketmq.RobotRecordStormSunDeviceConsumer@efa475c],
    @String[test-ss-msg-friend-add:wk-friend-add]:@RobotReplyFriendRequestConsumer[com.baijia.tongbao.rocketmq.RobotReplyFriendRequestConsumer@11d8889c],
    @String[test-ss-msg-friend-add:friend-add]:@RobotReplyFriendRequestConsumer[com.baijia.tongbao.rocketmq.RobotReplyFriendRequestConsumer@11d8889c],
    @String[test-ss-msg-chatroom-join-none-repeat:wk-chatroom-join-none-repeat]:@JoinChatroomConsumer[com.baijia.tongbao.rocketmq.JoinChatroomConsumer@7e9cbcde],
    @String[test-ss-msg-win-friend-chat:friend-chat]:@RobotRecordFriendWinMsgConsumer[com.baijia.tongbao.rocketmq.RobotRecordFriendWinMsgConsumer@6397145b],
    @String[test-ss-msg-qi-chatroom-chat-detail:wk-qi-chatroom-chat-detail]:@WindowsChatroomMsgConsumer[com.baijia.tongbao.rocketmq.WindowsChatroomMsgConsumer@4499a7a3],
    @String[test-ss-msg-system-msg:system-msg]:@TbSalesCommonSystemMsgConsumer[com.baijia.tongbao.rocketmq.TbSalesCommonSystemMsgConsumer@d3b355],
    @String[test-ss-msg-qi-chatroom-chat-detail:qi-chatroom-chat-detail]:@WindowsChatroomMsgConsumer[com.baijia.tongbao.rocketmq.WindowsChatroomMsgConsumer@4499a7a3],
]
```


### 让 `unsubscribe()` 立即生效的步骤

sc -d com.baijia.ss.msg.center.lib.consumer.AbsConsumer

ognl -x 3 '@com.baijia.ss.msg.center.lib.consumer.AbsConsumer@topicAndTag2Consumer.remove("test-ss-msg-chatroom-join-none-repeat")' -c 24b4d544

sc -d com.baijia.tongbao.rocketmq.base.AbsBaseConsumer

ognl -x 3 '@com.baijia.tongbao.rocketmq.base.AbsBaseConsumer@topic2Class.remove("test-ss-msg-chatroomJoinReply-send")'  -c  5fac521d



- 1. **调用 `unsubscribe()`：**
        
    `consumer.unsubscribe("YourTopic");`
    
    这将告诉消费者不再订阅指定的主题。
    
- 2. **手动触发消费者的刷新：** 你可以通过调用消费者的 `shutdown()` 方法来停止消费者的运行，随后再重新启动消费者以使得 `unsubscribe()` 生效。这是一种确保取消订阅立即生效的方法：
    
    
    `consumer.shutdown();  // 停止消费者 
     consumer.start();     // 重新启动消费者`
    
- **等待短暂时间：** RocketMQ 可能需要一些时间来处理取消订阅的操作，因此，虽然 `unsubscribe()` 会立即更新订阅列表，但实际的消费者停止从该主题拉取消息可能需要一些时间。你可以结合消费者的日志和状态来检查何时取消订阅已生效。




https://blog.csdn.net/WKzhangliang123/article/details/118337227

5. 实战时遇到问题了，因为我们用的商业版SDK，看源代码中默认写死了AllocateMessageQueueAveragely，阿里api中没有让设置的选项，难道要换成社区版？

AllocateMessageQueueAveragely （默认，也就是上图所示分配策略）  
AllocateMessageQueueAveragelyByCircle （我想要的，下图分配策略）  
AllocateMessageQueueByConfig  
AllocateMessageQueueByMachineRoom  
AllocateMessageQueueConsistentHash




协议层限制，Mqtt最大控制报文（含payload）不得超过268435455bytes（256m），限制无法修改 2、配置限制，配置文件中定义消息payload不得超过65536bytes（64k），可通过修改NETTY_MAX_PAYLOAD_SIZE大小扩大限制 3、消息队列限制，使用**微服务架构**进行部署时，如果transport消息无法正常写入消息中间件，判断为异常，中断相关Mqtt连接，需要通过扩展消息队列配置进行修改
![[../壁纸/附件/Pasted image 20240222142431.png]]

![[../壁纸/附件/Pasted image 20240222143136.png]]


https://ons.console.aliyun.com/region/cn-beijing/instance/MQ_INST_1941505946323830_BcNbyp3U/group/GID-win-server-pro/detail

![[../壁纸/附件/Pasted image 20240125163729.png]]

![[../壁纸/附件/Pasted image 20240125164355.png]]



https://mqtt.console.aliyun.com/?spm=5176.12818093_47.ProductAndResource--ali--widget-product-recent.32.57ea16d0o8xCj5#/ResourceRexport?topic=robot-wx-win-pro&instanceId=mqtt-cn-v0h1klv0a02&regionId=cn-beijing

https://ons.console.aliyun.com/region/cn-beijing/instance/MQ_INST_1941505946323830_BbSi3Pog/group/GID_ss-msg-center-pro-1/detail




https://ons.console.aliyun.com/region/cn-beijing/instance/MQ_INST_1941505946323830_BbSi3Pog/group/GID_ss-msg-center-pro-1/detail

https://ons.console.aliyun.com/region/cn-beijing/instance/MQ_INST_1941505946323830_BbSi3Pog/dashboard



cloud:  https://ons.console.aliyun.com/region/cn-beijing/instance/MQ_INST_1941505946323830_BcNbyp3U/detail



https://console.cloud.tencent.com/ckafka/detail?rid=8&id=ckafka-w4vk8akn&tab=monitor&monitorTab=consumerGroup&consumerId=prod_uqun_event_platform_bdgDefaultUserFlowData_group&rankType=INSTANCE_EVENT&setConsumerSearch=event


#####  基本概念

https://help.aliyun.com/zh/apsaramq-for-rocketmq/cloud-message-queue-rocketmq-4-x-series/product-overview/terms?spm=a2c4g.11186623.0.i27

![[../壁纸/附件/Pasted image 20240202234451.png]]


##### 消息堆积和延迟问题：
https://help.aliyun.com/zh/apsaramq-for-rocketmq/cloud-message-queue-rocketmq-4-x-series/use-cases/message-accumulation-and-latency?spm=a2c4g.11186623.0.i6




![[../壁纸/附件/Pasted image 20240202231016.png]]


### 最佳线程数

单节点的并发度需要谨慎设置，不能盲目直接调大线程数，设置过大的线程数反而会带来大量的线程切换的开销。理想环境下单节点的最优线程数计算模型如下：

- 单机vCPU核数为C。
- 线程切换耗时忽略不计，I/O操作不消耗CPU。
- 线程有足够消息等待处理，且内存充足。
- 逻辑中CPU计算耗时为T1，外部I/O操作为T2。

则单个线程能达到的TPS为1/（T1+T2），如果CPU使用率达到理想状态100%，那么单机达到最大能力时需要设置C*（T1+T2）/T1个线程。


#### 消费并发度

在 


RocketMQ 中，如果你的消息为非顺序消息，那么消费的并发度是受限于 Topic 分区数的。这是因为非顺序消费下，多个线程可以并行地从不同的分区拉取和消费消息，所以消费的并发度受限于分区数。  
  
但如果你选定的是顺序消息，那么任何时候同一个分区（称为MessageQueue）只会在一个消费者线程中进行消费。这是为了保证其在该 MessageQueue 的顺序性。  
  
在上述场景中，你的服务有40个线程池来消费消息，Topic有100个分区，那么在非顺序消费下，每个服务（如果在同一个消费者组）大致会消费10个分区的消息，所以并发度最多是10，多余的线程会处于空闲状态，不参与消费。同时，为了提高消费并发度，你可以增加分区数。  
  
总结：在顺序消费模式下，消费并发度受每个Topic的分区数限制，一个分区同一时间只能被一个消费者线程消费，所以并发度最多是1。在非顺序消费模式下，消费并发度也是受每个Topic的分区数限制，一个分区可以被一个消费者线程消费，多个分区可以被多个消费者线程并行消费。


### 顺序消费和非顺序消费


在RocketMQ中，消息的消费方式（顺序或者非顺序）是由消费者端决定的，而不是在主题（Topic）级别设定的。因此，我们并不能直接在Topic上看到消息是顺序消费还是非顺序消费。

消费者在消费消息时，选择使用顺序消息监听器（MessageListenerOrderly）还是并行消息监听器（MessageListenerConcurrently）来确定消息是顺序消费还是并行消费。所以，要查看消息是顺序消费还是非顺序消费，你需要查看消费者的代码。

如果消费者使用MessageListenerOrderly，那么消息将被顺序消费；如果使用MessageListenerConcurrently，消息将被并发消费。这是通过消费者端的相关配置来决定的，而并非由Topic决定。

具体来说，如果你使用的是RocketMQ的Java客户端，那么你可以通过查看业务代码实现来确定消费模式。例如，在创建DefaultMQPushConsumer后，设置MessageListener为MessageListenerOrderly或MessageListenerConcurrently来指定消费模式。

```java
// 顺序消费
consumer.registerMessageListener(new MessageListenerOrderly() {...}) 
// 并行消费 
consumer.registerMessageListener(new MessageListenerConcurrently() {...})
```


#### 如果一个group组 消费的topic越多， 受分区数的影响就越小， 线程池的线程就不太会空闲 是这个意思吗

```
是的，你的理解是正确的。在RocketMQ中，每个消息分区（分区数是在创建Topic时设定）在任何时间只能由一个消费者线程进行处理，这是为了保障消费的顺序性。因此，如果一个消费者组（Consumer Group）订阅的Topic数量越多，对应的消息分区总数就越多，那么可以同时并发消费的线程数量就会更多。  
  
例如，如果你有一个40线程的线程池，订阅的每个Topic都有10个分区，那么你只订阅一个Topic时，只能启动10个线程进行处理；但如果你订阅了4个这样的Topic，那么线程池中的所有40个线程就都可以启动进行处理了。  
  
但是请注意，虽然增加订阅的Topic数量可以让更多的线程得到利用，但这同时也会增大消费者处理的负载，可能导致处理瓶颈。在实际使用时需要做好负载评估，合理配置消费者数量、线程池大小和Topic的分区数。
```


##### 这段话是什么意思 帮我分析一下
```java
consumer = new DefaultMQPushConsumer(groupId,  
new AclClientRPCHook(new SessionCredentials(accessKey, secretKey)),  
new AllocateMessageQueueAveragely());
```

```
这段代码是创建一个新的RocketMQ消费者实例的过程。详解如下：

- `DefaultMQPushConsumer`：RocketMQ中的一种Consumer类型，它是一种消息的推送型消费模式，即由RocketMQ服务器自动地向消费者推送消息，消费者接收到推送的消息后再进行相应的消费处理。
    
- `groupId`: 消费者组ID。RocketMQ通过消费者组来支持一个Topic消息的广播消费和集群消费两种消费模式。消费者需给出一个组名（此处变量为groupId）来标识自身所在的消费者组。
    
- `AclClientRPCHook`: 它是RocketMQ客户端的一个钩子（Hook），用于在RocketMQ网络请求的前（send request）后（receive response）做一些事情。此处，AclClientRPCHook用来进行权限控制的相关操作。
    
- `SessionCredentials(accessKey, secretKey)`: 用来进行权限控制的密钥对，accessKey是公钥，secretKey是私钥。
    
- `new AllocateMessageQueueAveragely()`: 这是一种消息队列的分配策略。RocketMQ允许你自定义消息队列的分配策略，在一个消费者组内如何分配队列给该组内的各个消费者，是通过队列分配策略来定义的。AllocateMessageQueueAveragely是RocketMQ的内置策略之一，指的是消息队列在消费者之间均等分配。
    

所以总结起来，这段代码的作用是创建了一个RocketMQ默认的推式消费者，设置了消费者的组ID，权限控制钩子和队列的分配策略。
```



#### 两种消息队列的负载分配策略

```
RocketMQ 默认提供了两种消息队列的负载分配策略，分别是 AllocateMessageQueueAveragely和AllocateMessageQueueConsistentHash。

- AllocateMessageQueueAveragely：平均分配消息队列。这是默认的分配策略。它尝试将所有的消息队列平均分配给所有的消费者。如果不能平均分配，那么会有一些消费者分配到多一个队列。
    
- AllocateMessageQueueConsistentHash：基于一致性哈希的分配。这种策略在分配消息队列时，尽管消费者数量发生变化，但某个消息队列的归属只会受到极小的影响。
    

除此之外，你也可以实现自己的消息队列分配策略。要实现自定义策略，需要实现AllocateMessageQueueStrategy接口并覆盖其allocate方法。

在实践中应当根据你的业务需求选择或者实现合适的分配策略，以尽可能高效地利用资源。
```

https://blog.csdn.net/Soda_lw/article/details/102975687

```

这两种消息队列分配策略在不同场景下可以提供不同的优势和适用性：

1. `AllocateMessageQueueAveragely`（平均分配策略）：
    
    - 适用于消费者数量相对较少，且希望尽可能均匀地分配消息队列给每个消费者的场景。
    - 优点是能够确保相对平均地将消息队列分配给消费者，避免部分消费者过于繁忙，而其他消费者空闲的情况。
    - 缺点是在消费者数量发生变化时，如果不能完全平均分配队列，可能会导致一些消费者比其他消费者多消费一个队列。
2. `AllocateMessageQueueConsistentHash`（一致性哈希分配策略）：
    
    - 适用于消费者数量较多，且希望保持较为稳定的队列分配给每个消费者的场景。
    - 一致性哈希算法能够保持较为稳定的哈希分配结果，即在消费者数量发生变化时，尽量保持队列的归属不变，以确保消费者能够继续消费其负责的队列。
    - 优点是即使在消费者数量发生变化时，仍然可以保持较为稳定的队列分配，避免大规模的队列重新分配和消费进度的重置。
    - 缺点是在部分消费者数量较少的情况下，可能会导致负载不均衡的情况，其中一些消费者分配到的队列较多而另一些较少。

需要根据具体的业务场景和需求来选择合适的分配策略。如果以上预设的策略无法满足需求，也可以自行实现一种适合自己业务的分配策略。
```



"相对较少"的消费者实例数没有一个具体的数值，这主要还是取决于你的业务需求以及你所处理的消息队列数。  
  
如果你的消息队列数远大于你的消费者实例数，那么消费者实例数就可以被视为"相对较少"。那种情况下，选择AllocateMessageQueueAveragely策略可以更均衡地分配消息队列，使得每个消费者都有足够的消息来处理，不会有消费者空闲。  
  
相反，如果消费者实例数和消息队列数相当，或者消费者实例数超过消息队列数，那么你可能需要考虑使用AllocateMessageQueueConsistentHash策略，以保证消息队列的分配在消费者实例变动时保持稳定。  
  
需要注意的是，你的选择应基于实际的业务需求，考虑如消费者的处理能力、消息队列的数量、消费者实例的稳定性以及系统的扩展性等因素。在实现中可以做一些压力测试和性能测试来确定最适合的策略和配置。



<mark class="hltr-green">是的，这里的消息队列数量即是指的Topic的分区数。RocketMQ中的一个Topic会被分为多个消息队列（也叫分区），以便于并发处理。  </mark>
  
对于AllocateMessageQueueAveragely（平均分配策略）：比如你有100个消息队列（即Topic拥有100个分区），同时你有10个消费者实例，那么每个消费者实例平均可以分到10个消息队列。而如果你的消费者实例增加到20个，那么每个消费者实例平均只能分到5个消息队列。可以看得出来这个策略尝试将所有的消息队列平均分配给所有的消费者。  
  
对于 AllocateMessageQueueConsistentHash（一致性哈希分配策略）：这个策略在分配消息队列时，会保证即使消费者实例数量发生变化，消息队列的分配也会基本保持稳定。比如初始你有10个消费者实例，每个实例处理10个消息队列，当其中一个消费者实例失败后，这10个消息队列会被重新分配给其他的消费者实例，而其他消息队列的归属不会变化。同样的，如果新增一个消费者实例，那么系统会从其他消费者实例中选取部分消息队列交给新的消费者实例，而大部分消息队列的归属还会保持不变。  
  
具体的数据实例并没有固定的值，它会根据你的业务场景、消费者实例的性能、Topic的分区数、以及你期望达到的效果进行调整。



###  topic的分区数 （消息队列数）


请注意：如果Topic已经创建，且已经有生产或消费的行为，此时修改分区数并不能立即生效，已有的分区数将保持不变，新的分区数配置在重启broker后生效。未有消费和生产行为的topic在修改分区数量后立即生效。


![[../壁纸/附件/Pasted image 20240202234049.png]]


![[../壁纸/附件/Pasted image 20240202234424.png]]

你可能是在使用消息队列云服务，这些云服务可能会根据其自身的设计规则和使用情况，自动调整Topic的分区数以优化性能和弹性，而不允许用户手动更改分区数。  
  
关于这部分具体的行为，你将需要查看你使用的云服务提供商的相关文档。比如阿里云的RocketMQ服务，其Topic分区数会根据生产和消费的TPS来动态调整。具体的规则应该在阿里云RocketMQ的产品文档里有介绍。  
  
如果你是自建的RocketMQ，是可以手动设置Topic的分区数的，如我在前一个回答里所述。  
  
对于云服务的分区数动态调整的原理，一般是这样的：当发现当前的生产或消费负载超过了某个阈值，云服务会自动增加Topic的分区数，以提高并发处理能力。反之，如果发现负载过低，会减少分区数以节约资源。这样可以在不影响使用的前提下，自动优化系统性能和降低成本。具体的调整算法、时机和策略，会因为云服务提供商的设计而不同，你需要查阅相关文档或咨询服务提供商以获取确切信息。




#####  ONSFactory.createConsumer(properties) 相比于new DefaultMQPushConsumer( groupId(), new AclClientRPCHook(new SessionCredentials(accessKey, secretKey)), new AllocateMessageQueueAveragely());有什么区别


在阿里云的 RocketMQ 客户端中，`ONSFactory.createConsumer(properties)` 和 `new DefaultMQPushConsumer(groupId(), new AclClientRPCHook(new SessionCredentials(accessKey, secretKey)), new AllocateMessageQueueAveragely())` 都是用来创建消费者实例的方法，但是它们之间有一些区别：

1. **配置方式：**
    
    - `ONSFactory.createConsumer(properties)` 方法使用了 `Properties` 对象来传递配置信息，这种方式更加灵活，可以通过配置文件等方式来管理配置。
    - `DefaultMQPushConsumer` 构造函数直接传递了一系列参数，比较直接，但是配置不够灵活，需要在代码中硬编码。
2. **所属框架：**
    
    - `ONSFactory.createConsumer(properties)` 是 Aliyun RocketMQ 的官方 SDK 中的方法，专门为阿里云 RocketMQ 提供的消息队列服务设计。
    - `DefaultMQPushConsumer` 是 Apache RocketMQ 的客户端 API，不依赖阿里云平台，适用于在其他环境中使用 RocketMQ。
3. **功能扩展：**
    
    - `ONSFactory.createConsumer(properties)` 方法可能会提供一些阿里云特有的功能扩展，例如与阿里云其他服务的集成等。
    - `DefaultMQPushConsumer` 则更加通用，更容易扩展到其他平台。
4. **使用限制：**
    
    - `ONSFactory.createConsumer(properties)` 方法可能会有一些针对阿里云 RocketMQ 的使用限制，而 `DefaultMQPushConsumer` 则相对更加通用。

综上所述，选择使用哪种方式创建消费者实例取决于你的具体需求和使用场景。如果你在阿里云平台上使用 RocketMQ，且希望更加灵活地管理配置，那么可以选择 `ONSFactory.createConsumer(properties)` 方法；如果你更倾向于通用性和跨平台性，那么可以选择 `DefaultMQPushConsumer`。