

```

vmtool -x 3 \
  --action getInstances \
  --className java.util.concurrent.ThreadPoolExecutor \
  --express 'instances.{ 
      #this.toString() 
      + " | core=" + #this.corePoolSize 
      + ", max=" + #this.maximumPoolSize 
      + ", poolSize=" + #this.poolSize 
      + ", active=" + #this.activeCount 
      + ", queue=" + #this.queue.size() 
  }'

```



统计线程哪个最多

```

thread -n 5000  > 1.txt


thread -n 000 --state=WAITING,TIMED_WAITING > 1.txt

退出arthas 


grep -oP '"(.*)(?=.\d+)?"' 2.txt   | sort | uniq -c | sort -nr

  158 "RebalanceService"
    158 "PullMessageService"
    158 "NettyClientWorkerThread_1"
    158 "NettyClientSelector_1"
    158 "MQClientFactoryScheduledThread1"
    158 "ClientHouseKeepingService"
    150 "NettyClientWorkerThread_2"
    147 "NettyClientWorkerThread_4"
    147 "NettyClientWorkerThread_3"
    147 "NettyClientPublicExecutor_8"
    147 "NettyClientPublicExecutor_7"
    147 "NettyClientPublicExecutor_6"
    147 "NettyClientPublicExecutor_5"
    147 "NettyClientPublicExecutor_4"
    147 "NettyClientPublicExecutor_3"
    147 "NettyClientPublicExecutor_2"
    147 "NettyClientPublicExecutor_1"
    146 "PullMessageServiceScheduledThread"
    100 "CleanExpireMsgScheduledThread_1"

```


com.aliyun.openservices.shade.com.alibaba.rocketmq.remoting.netty.NettyRemotingClient#publicExecutor




问题的根源 **100% 可以确定**：您在应用程序中创建了大约 **158 个独立的 RocketMQ 客户端实例 (MQClientInstance / MQClientFactory)**。

**为什么能这么肯定？**

RocketMQ 客户端的设计是，**一个客户端实例（`MQClientInstance`）会创建并管理一套完整的后台线程**，用于网络通信、心跳、拉取消息、负载均衡等。这些后台线程对于一个客户端实例来说，大多数都是**单例**的。

让我们来分析一下您列表中的线程：

|线程名前缀|正常情况下每个客户端实例的数量|您的统计数量|**分析结论 (铁证)**|
|---|---|---|---|
|`RebalanceService`|1|158|**铁证#1**：负责消费者负载均衡，每个实例1个。|
|`PullMessageService`|1|158|**铁证#2**：负责拉取消息，每个实例1个。|
|`ClientHouseKeepingService`|1|158|**铁证#3**：负责客户端内部维护（心跳等），每个实例1个。|
|`MQClientFactoryScheduledThread`|1|158|**铁证#4**：客户端工厂的调度线程，每个实例1个。|
|`NettyClientSelector`|1|158|**铁证#5**：Netty的Selector线程，每个实例1个。|
|`ConsumeMessageThread`|N (可配置)|400+|这是实际处理消息的线程，总数多是正常的。但它们的**分组**（`_1`, `_2`...）也暗示了存在多个线程池，即多个消费者实例。|

**简单来说：您本应只有一个`RebalanceService`，但现在有158个。这意味着您无意中启动了158次RocketMQ客户端的核心服务。**



查看clientId
```
vmtool -x 3 --action getInstances --className com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.factory.MQClientInstance  --express 'instances.{clientId}'  -c 7577b641


vmtool -x 3 --action getInstances --className org.apache.rocketmq.client.impl.factory.MQClientInstance  --express 'instances.{clientId}'  -c 7577b641

```




### 每新建一个 Consumer 会创建多少线程？

大体来说：

1. **核心线程**（Rebalance + Pull + HouseKeeping）
    
    - 每个 Consumer 独享：
        
        - 1 个 `RebalanceService`
            
        - 1 个 `PullMessageService`
            
        - 1 个 `ClientHouseKeepingService`
            
2. **Netty 线程**
    
    - `NettyClientWorkerThread`：默认 4 个（可配置 `clientWorkerThreads`）
        
    - `NettyClientSelector`：默认 1 个
        
    - `NettyClientPublicExecutor`：默认 4-8 个（可配置 `clientCallbackExecutorThreads`）
        
3. **Scheduled/定时线程**
    
    - `MQClientFactoryScheduledThreadX`：1~2 个
        
    - `PullMessageServiceScheduledThread`：1 个
        
    - `CleanExpireMsgScheduledThread_1`：1 个
        

所以，一个 Consumer 启动后大约会 **增加 10~20 个线程**（具体数量取决于你配置的 `clientWorkerThreads` 和 `clientCallbackExecutorThreads`）。

---

### 3️⃣ 注意事项

- 如果你 **启动了大量 Consumer 实例**，线程数会线性增加，可能会导致 **JVM 线程过多**，影响性能。
    
- 通常在同一进程里，只需要一个 Consumer 实例，多个 Topic 可以共享 Consumer。
    
- Netty 的 Worker/Selector 可以在同一个 JVM 客户端共享，所以不必每个 Consumer 都额外创建大量线程，但 RocketMQ 默认实现是 **每个 MQClientInstance 独立**，因此线程会复制。
    

---

💡 总结：

> 每新建一个 Consumer，会增加核心线程 + Netty IO 线程 + 定时线程，总计大约 10~20 条，取决于你的配置参数。








###  MQ复用逻辑
```

com.aliyun.openservices.shade.com.alibaba.rocketmq.client.impl.MQClientManager#getAndCreateMQClientInstance(com.aliyun.openservices.shade.com.alibaba.rocketmq.client.ClientConfig, com.aliyun.openservices.shade.com.alibaba.rocketmq.remoting.RPCHook, com.aliyun.openservices.shade.io.netty.channel.EventLoopGroup, com.aliyun.openservices.shade.io.netty.util.concurrent.EventExecutorGroup)



```
![[../../壁纸/附件/Pasted image 20260129094853.png]]

### 分组数量建议

| 容器类型          | 当前配置 | 建议  | 原因               |
| ------------- | ---- | --- | ---------------- |
| NORMAL (普通消息) | 4    | 4-8 | 普通消息并发度高，可以多共享   |
| ORDER (顺序消息)  | 4    | 2-4 | 顺序消息对时序敏感，不宜过多共享 |
| BATCH (批量消息)  | 2    | 2-4 | 批量消息吞吐量大，适度共享    |




### 注册MQ gaotu包 
com.gaotu.arch.ons.config.MessageListenerRegister#createOnsMessageOrderListenerContainerBeanDefinition

![[../../壁纸/附件/Pasted image 20260129095013.png]]
这里设置属性 但是没有设置instanceName

![[../../壁纸/附件/Pasted image 20260129095041.png]]


使用 com.gaotu.student.data.facade.config.RocketMQThreadOptimizerProcessor#postProcessAfterInitialization 对实例增加属性  

![[../../壁纸/附件/Pasted image 20260129110540.png]]
本质是使用的BatchConsumerBean  (com.aliyun.openservices.ons.api.bean.BatchConsumerBean)进行创建对象 

普通: com.aliyun.openservices.ons.api.bean.ConsumerBean
顺序: com.aliyun.openservices.ons.api.bean.OrderConsumerBean
![[../../壁纸/附件/Pasted image 20260129110625.png]]

RocketMQThreadOptimizerProcessor是在调用consumer.start之前修改properties的instanceName属性
使其复用MQClientInstance对象 


### MQClientInstance 包含的线程资源

|线程/线程池|线程数|作用|是否共享|
|---|---|---|---|
|scheduledExecutorService|1-4|定时任务：更新路由、发送心跳、持久化消费进度|✅ 共享|
|pullMessageService|1|拉取消息服务|✅ 共享|
|rebalanceService|1|负载均衡服务|✅ 共享|
|Netty eventLoopGroupWorker|3 (默认)|网络 IO 处理|✅ 共享|
|Netty eventLoopGroupSelector|3 (默认)|网络连接选择器|✅ 共享|
|publicExecutor|4 (默认)|回调处理|✅ 共享|
|consumeMessageService|20 (默认)|消费线程池|❌ 每个 Consumer 独立|
MQClientInstance 中包含的主要线程池和资源：

1. scheduledExecutorService - 定时任务线程池

	- 用于定期更新 NameServer 地址
	
	- 用于定期从 NameServer 获取路由信息
	
	- 用于定期发送心跳
	
	- 用于定期持久化消费进度
	
	- 用于定期调整线程池
	
	- 通常是单线程

2. pullMessageService - 拉取消息服务

	- 内部有一个线程用于拉取消息
	
	- 一个 MQClientInstance 一个

3. rebalanceService - 负载均衡服务

	- 内部有一个线程用于负载均衡
	
	- 一个 MQClientInstance 一个

4. NettyRemotingClient (mQClientAPIImpl 内部)

	- publicExecutor - 公共线程池，处理回调
	
	- eventLoopGroupWorker - Netty worker 线程组
	
	- eventLoopGroupSelector - Netty selector 线程组
	
	- channelEventListener - 通道事件监听线程

5. DefaultMQPushConsumerImpl (每个 Consumer)

	- consumeMessageService - 消费消息服务线程池
	
	- ConsumeMessageConcurrentlyService: 默认 20 个线程
	
	- ConsumeMessageOrderlyService: 默认 20 个线程
	
	- 这个线程池是每个 Consumer 独立的，不会因为共享 MQClientInstance 而共享


![[../../壁纸/附件/Pasted image 20260129111756.png]]

![[../../壁纸/附件/RocketMQThreadOptimizerProcessor.java]]

使用桶算法优化 
![[../../壁纸/附件/RocketMQThreadOptimizerProcessor 1.java]]


支持apollo配置
![[../../壁纸/附件/RocketMQThreadOptimizerProcessor 2.java]]


### 使用requests获取apollo配置

url = f"{apollo_server_url}/configs/{app_id}/default/{namespace}"

```python
import requests  
  
response = requests.get("http://apollo-meta.baijia.com/configs/ai-sop/test/application")  
  
print(response.text)
```

获取一个appId下的所有namespace

```cobol
https://apollo-portal.baijia.com/apps/tb-wechat-assist/envs/TEST/clusters/default/namespaces?debug=
```



```java
@Value("${ApolloConfig.minThreadNum:1}")  
private Integer minThreadNum;  
  
  
private static Map<String, DefaultMQPushConsumer> consumerMap = new ConcurrentHashMap<>();  
private static Map<String, ThreadPoolExecutor> threadPoolExecutorMap = new ConcurrentHashMap<>();  
private static ScheduledThreadPoolExecutor scheduledThreadPoolExecutor = new ScheduledThreadPoolExecutor(1);  
  
public void addConsumer(String key, DefaultMQPushConsumer consumer) {  
    consumerMap.put(key,consumer);  
    scheduledThreadPoolExecutor.submit(()-> {  
        getThreadPoolExecutor(consumer);  
    });  
}  
  
private ThreadPoolExecutor  getThreadPoolExecutor(DefaultMQPushConsumer defaultMQPushConsumer) {  
    try {  
        Class<? extends DefaultMQPushConsumer> defaultMQPushConsumerClass = defaultMQPushConsumer.getClass();  
        Field defaultMQPushConsumerImpl1 = defaultMQPushConsumerClass.getDeclaredField("defaultMQPushConsumerImpl");  
        defaultMQPushConsumerImpl1.setAccessible(true);  
        Object defaultMQPushConsumerImpl =  defaultMQPushConsumerImpl1.get(defaultMQPushConsumer);  
        Field consumeMessageService1 = defaultMQPushConsumerImpl.getClass().getDeclaredField("consumeMessageService");  
        consumeMessageService1.setAccessible(true);  
        Object consumeMessageService =  consumeMessageService1.get(defaultMQPushConsumerImpl);  
        Field consumeExecutor1 = consumeMessageService.getClass().getDeclaredField("consumeExecutor");  
        consumeExecutor1.setAccessible(true);  
        ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) consumeExecutor1.get(consumeMessageService);  
        scheduledThreadPoolExecutor.scheduleWithFixedDelay(()-> {  
            try {  
                adjustThreadNum(threadPoolExecutor, minThreadNum);  
            } catch (Exception e) {  
                log.info("adjustThreadNum error:", e);  
            }  
        },2,10,TimeUnit.SECONDS);  
        return threadPoolExecutor;  
    } catch (Exception e) {  
        log.error("getThreadPoolExecutor error：",e);  
        return null;    }  
}  
  
private static void adjustThreadNum(ThreadPoolExecutor threadPoolExecutor, int min) {  
    int maximumPoolSize1 = threadPoolExecutor.getMaximumPoolSize();  
    int corePoolSize1 = threadPoolExecutor.getCorePoolSize();  
    int max = Math.max(40, maximumPoolSize1);  
    int activeCount = threadPoolExecutor.getActiveCount();  
    int poolSize = threadPoolExecutor.getPoolSize();  
    if (activeCount * 3 >= corePoolSize1  
            && threadPoolExecutor.getQueue().size() >= corePoolSize1) {  
        if (corePoolSize1 < max && poolSize < max) {  
            int corePoolSize = Math.min(Math.max(corePoolSize1, poolSize) + 10, max);  
            threadPoolExecutor.setCorePoolSize(corePoolSize);  
            if (corePoolSize > threadPoolExecutor.getMaximumPoolSize()) {  
                threadPoolExecutor.setMaximumPoolSize(corePoolSize);  
            }  
        }  
    }  
    if (activeCount == 0  
            && threadPoolExecutor.getQueue().size() == 0) {  
        int currentMin = Math.max(min, corePoolSize1 -10);  
        if (currentMin < corePoolSize1) {  
            threadPoolExecutor.setCorePoolSize(currentMin);  
            threadPoolExecutor.setKeepAliveTime(1, TimeUnit.MINUTES);  
        }  
    }  
    log.info("getThreadPoolExecutor params," +  
                    "corePoolSize:{},maximumPoolSize:{}, activeCount:{}, queueSize:{}, poolSize:{}",  
            threadPoolExecutor.getCorePoolSize(), threadPoolExecutor.getMaximumPoolSize(),  
            threadPoolExecutor.getActiveCount(), threadPoolExecutor.getQueue().size(), threadPoolExecutor.getPoolSize());  
}  
  
  
@ApolloConfigChangeListener  
public void onChange(ConfigChangeEvent changeEvent) {  
    for (Map.Entry<String, DefaultMQPushConsumer> entry : consumerMap.entrySet()) {  
        dealChange(changeEvent, entry.getKey(), (oldValue, newValue) -> {  
            Integer threadNum = Integer.parseInt(newValue);  
            ThreadPoolExecutor poolExecutor = threadPoolExecutorMap.get(entry.getKey());  
            if (poolExecutor == null) {  
                poolExecutor = getThreadPoolExecutor(entry.getValue());  
                threadPoolExecutorMap.put(entry.getKey(), poolExecutor);  
            }  
            poolExecutor.setCorePoolSize(threadNum);  
            poolExecutor.setMaximumPoolSize(threadNum);  
            poolExecutor.setKeepAliveTime(1, TimeUnit.MINUTES);  
            poolExecutor.allowCoreThreadTimeOut(true);  
            log.info("apollo 更新线程池参数成功, key:{}, 线程池参数:{}", entry.getKey(), entry.getValue());  
        });  
    }  
  
}  
  
private static void dealChange(ConfigChangeEvent changeEvent, String value, BiConsumer<String,String> consumer) {  
    try {  
        ConfigChange change = getModifyConfigChange(changeEvent, value);  
        if (change == null) {  
            return;  
        }  
        consumer.accept(change.getOldValue(),change.getNewValue());  
        log.info("changeEvent: {}", JSONObject.toJSONString(change));  
    } catch (Exception e) {  
        log.error("apollo 更新失败: {}", JSONObject.toJSONString(changeEvent));  
    }  
}  
  
private static ConfigChange getModifyConfigChange(ConfigChangeEvent changeEvent, String value) {  
    ConfigChange change;  
    if (Objects.equals(changeEvent.getNamespace(),"application")) {  
        change = changeEvent.getChange(value);  
        if (Objects.equals(change.getChangeType(), PropertyChangeType.MODIFIED)  
                || Objects.equals(change.getChangeType(), PropertyChangeType.ADDED) ) {  
            return change;  
        }  
    }  
    return null;  
}
```