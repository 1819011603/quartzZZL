x-job 原理

https://maling.io/posts/xxl-job/

https://xjob-admin.baijia.com/;jsessionid=889FA47C4B55189BFB81936B4C26DE39

html转pdf
https://tools.pdf24.org/zh/webpage-to-pdf

以Bean为例:   XxlJobSpringExecutor -> 会执行父类 `XxlJobExecutor` 中的 `start()`-> `initEmbedServer()` 方法，该方法会利用 Netty 框架启动一个 HTTP Server，并将自己注册到调度中心。核心实现如下：->  执行器启动后，便可接收来自调度中心的 HTTP 请求。当执行器收到来自调度中心的指令时，会把请求交给 `ExecutorBiz` 处理。`ExecutorBiz` 定义了执行器支持的所有方法： -> `ExecutorBiz` 有两个实现类，分别是 `ExecutorBizImpl` 和 `ExecutorBizClient`。其中：

- `ExecutorBizImpl` 是由执行器使用，负责处理来自调度中心的请求；
- `ExecutorBizClient` 由==调度中心使用，负责发送相应的命令==。  -> 定时任务的抽象类是 `IJobHandler`，XXL-JOB 提供了三个默认实现：

- `MethodJobHandler`：用于执行 `BEAN` 模式创建的任务；
- `GlueJobHandler`：用于执行 `GLUE` 模式下的 Java 任务；
- `ScriptJobHandler`：用于执行除 `GLUE(Java)` 模式外的其它 `GLUE` 脚本任务，例如 `GLUE(Shell)`、`GLUE(Python)` 等。  -> XXL-JOB 提供了一个 `@XxlJob` 注解，执行器启动时会从 Spring 容器中寻找被该注解标记的 Bean-> `EmbedHttpServerHandler#channelRead0()` 会解析来自调度中心的请求，并交给线程池处理：->  `process()` 通过请求的 url 来区分命令类型，进而调用 `ExecutorBiz` 实现类中的方法处理命令。以运行任务的 `run` 命令为例，该方法的实现如下： ->  由于定时任务的执行可能十分耗时，而执行器作为一个 HTTP Server，不适合长时间阻塞（否则会触发超时）。所以上述代码在第 8 步将参数添加到阻塞队列后就直接返回了，`JobThread` 在自己的循环中再不断拉取阻塞队列中的任务进行处理： ->  执行器收到触发指令后会直接返回 HTTP 响应，具体的任务是异步处理的，当任务执行完毕后，还需要发送回调请求将执行结果上报调度中心，这个过程也是异步的：


调度中心： 
调度中心会在 `XxlJobAdminConfig` 的后置处理器中启动一个**调度线程**，该线程会**每秒**查询一次 `xxl_job_info` 表内 `nowTime + PRE_READ_MS` 之前的待处理任务，最多 `preReadCount` 个：
->  调度中心支持集群部署，所以每个节点在处理前要通过锁表抢占资源

- **`xxl_job_lock`：调度中心支持集群部署，每个节点在处理前通过锁表抢占资源；**
- `nowTime + PRE_READ_MS`：未来 5s 的时间窗口；
- `preReadCount`：每次最多查询任务数，计算方法： treadpool-size * trigger-qps (each trigger cost 50ms, qps = 1000/50 = 20)。
拿到待处理的任务列表后，调度线程会将这些任务根据触发时间划分为三个部分：

1. 任务过期时间已经超过 5s；
2. 任务已经过时，但是过时时间不足 5s；
3. 任务未超时，且下次触发时间在未来 5s 内。

调度线程理论上一秒轮训一次，但实际的循环间隔并不精确：
原因有以下几个：

- 如果当次任务执行时间超过了 1s，那么下次轮训自然而然会被推迟；
- 即便当次任务在 1s 内执行完毕，`TimeUnit.MILLISECONDS.sleep` 也无法准确的让线程休眠指定毫秒，因为该方法内部还是调用的 `Thread.sleep`。

对于第一部分过期时间超过 5s 的任务，会根据任务配置的**调度过期策略**来选择要不要触发：
对于第二部分过期时间小于 5s 的任务，会立马触发一次。如果判断下一次触发时间就在 5s 内，就将这个任务放到一个时间轮里，等待下一次触发执行：
对于第三部分任务，由于还没到触发时间，所以直接放到时间轮里等待处理。



### 时间轮的原理与实现

时间轮 (Time Ring) 是一种用于处理时间相关事件的数据结构，它会将时间划分为一系列的时间槽 (slots)，每个时间槽代表一段时间间隔，例如毫秒或秒。时间轮上有多个槽，它们形成一个环形结构，类似于钟表的刻度。

在具体的实现中，时间轮是一种线程安全的 HashMap，其中键 (Key) 表示时间刻度，而值 (Value) 则表示待执行的任务 ID 列表：

当调度线程将待执行任务放置到其下次触发时间所在的刻度上时，时间轮处理线程 `ringThread` 即可开始消费这些任务：

该时间轮一共划分了 **60** 个刻度，分别对应一分钟内的 60 秒。每次处理时，都会将**当前秒**跟**前一秒**这两个刻度的任务取下来处理。之所以要往前取一个刻度，是为了避免上次处理耗时超过了 1s，导致任务被遗漏。

无论是立即触发任务，还是交由时间轮去触发，最终都是由 `JobTriggerPoolHelper` 处理的。`JobTriggerPoolHelper` 是任务的异步触发器，它内部维护了一快一慢两个线程池：

`JobTriggerPoolHelper` 默认情况下会将任务交给 `fastTriggerPool` 处理，同时记录任务的**慢触发次数（触发时间超过 500ms）**：
如果该任务一分钟内慢触发次数超过 10 次，就将这次触发任务交给 `slowTriggerPool` 处理：
快慢线程优化机制通过隔离操作，有效避免了慢任务阻塞其他任务的触发。


![[../../壁纸/附件/pdf24_converted.pdf]]