

```java
{"code":400,"msg":"Task java.util.concurrent.FutureTask@697c07b7 rejected from java.util.concurrent.ThreadPoolExecutor@38e813f7[Running, pool size = 100, active threads = 100, queued tasks = 0, completed tasks = 899365]"
```


eureka注册上和 eureka可以拉取所有服务的信息  这个是不同的阶段.
由于注册快于拉取服务, 导致MQ信息进来之后 无法访问其他服务, 直接被hystrix熔断并报错.



![[../../壁纸/附件/Pasted image 20240726173413.png]]


![[../../壁纸/附件/Pasted image 20240723155724.png]]



由于 Hystrix 的线程池被打满导致的。Hystrix 是 Netflix 开发的一个用于处理分布式系统的延迟和容错的开源库，它通过线程池隔离的方式来防止级联故障。

既然您已经确定了问题的根源，那么调整 Hystrix 的线程池参数确实是一个很好的解决方案。以下是一些可以考虑的配置参数：

1. 增加线程池大小：

```yaml
hystrix.threadpool.default.coreSize: 20
hystrix.threadpool.default.maximumSize: 30
hystrix.threadpool.default.allowMaximumSizeToDivergeFromCoreSize: true
```

2. 增加队列大小：

```yaml
hystrix.threadpool.default.maxQueueSize: 100
```

3. 调整超时时间：

```yaml
hystrix.command.default.execution.isolation.thread.timeoutInMilliseconds: 5000
```

4. 调整熔断器参数：

```yaml
hystrix.command.default.circuitBreaker.requestVolumeThreshold: 20
hystrix.command.default.circuitBreaker.errorThresholdPercentage: 50
hystrix.command.default.circuitBreaker.sleepWindowInMilliseconds: 5000
```

5. 如果需要为特定的 Feign 客户端配置，可以替换 `default` 为具体的 commandKey：

```yaml
hystrix.threadpool.YourCommandKey.coreSize: 30
```




修改后: 

![[../../壁纸/附件/Pasted image 20240723160250.png]]



如何查看修改是否成功    

### 必须重启才能重新赋值




类名 :  HystrixThreadPoolProperties

使用arthas查看

vmtool -x 3 --action getInstances --className com.netflix.hystrix.HystrixThreadPoolProperties  --express 'instances[0].maximumPoolSize'  -c 10b3df93


![[../../壁纸/附件/Pasted image 20240723163055.png]]


艾明 为什么有一部分请求的traceId是这个default_service_name开头的

![[../../壁纸/附件/Pasted image 20240726153919.png]]

链路上游也是这个影响的

![[../../壁纸/附件/Pasted image 20240726154049.png]]