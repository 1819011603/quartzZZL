


### # feign.RetryableException: connect timed out executing GET / POST / CONNECT 一会儿超时，一会儿不超时

https://blog.csdn.net/Oranger7/article/details/113244172

```

##Ribbon超时重试配置
ribbon:
  ConnectTimeout: 20000  #毫秒    连接超时时间
  ReadTimeout: 20000     #毫秒      逻辑处理超时时间
  OkToRetryOnAllOperations: true    # 是否对所有操作都进行重试
  MaxAutoRetries: 2     # 对当前实例的最大重试次数(请求服务超时6s则会再请求一次)
  MaxAutoRetriesNextServer: 1     # 切换实例的最大重试次数(如果还失败就切换下

```

```
ribbon.ConnectTimeout=20000             # 连接超时时间（以毫秒为单位） ribbon.ReadTimeout=20000                # 逻辑处理超时时间（以毫秒为单位） ribbon.OkToRetryOnAllOperations=true    # 是否对所有操作都进行重试 ribbon.MaxAutoRetries=2                 # 对同一实例的最大重试次数 ribbon.MaxAutoRetriesNextServer=1       # 切换到下一个实例的最大重试次数


```

<mark class="hltr-yellow">重启服务器</mark>


![[../../壁纸/附件/Pasted image 20240903165108.png]]

### 其他注意事项

- **服务实例的健康检查**：Ribbon 依赖 Eureka 或其他服务发现机制来获取可用的服务实例。配置重试时，需要确保服务实例的健康检查配置正确，以避免重试到不健康的实例上。
    
- **负载均衡策略**：Ribbon 提供了多种负载均衡策略，如轮询、随机、基于响应时间等。根据业务需求，可以自定义负载均衡策略，以更好地配合重试机制。
    
- **Hystrix 配置**：在使用 Ribbon 时，通常也会结合 Hystrix 来提供熔断和降级机制。确保 Hystrix 的超时和重试配置与 Ribbon 的配置兼容，以避免冲突。



###  Feign 支持的 HTTP 客户端工具包


feign.okhttp.enabled=true

1. **默认的 HTTP 客户端**
    
    - Feign 内置了一个非常简单的 `HttpURLConnection` 实现作为默认的 HTTP 客户端。
    - **特点**：简单且无外部依赖，但在性能、连接管理、超时处理等方面比较基础，不适用于生产环境。
2. **OkHttp**
    
    - **特点**：OkHttp 是一个现代化的 HTTP 客户端库，支持 HTTP/2、WebSocket，并内置了连接池管理、请求重试等功能。它的异步能力强，适合高并发场景。
    - **典型场景**：在需要高效异步请求或需要 HTTP/2 支持的情况下，OkHttp 是一个不错的选择。
3. **Apache HttpClient**
    
    - **特点**：Apache HttpClient 是一个功能丰富的 HTTP 客户端库，支持连接池管理、代理设置、重试机制、认证、Cookie 管理等多种功能。它在企业级应用中广泛使用，提供了非常强大的配置和扩展能力。
    - **典型场景**：在需要高级 HTTP 功能（如代理配置、复杂的认证机制、细粒度的超时设置）时，Apache HttpClient 是一个稳健的选择。

###  SS-ROBOT-FACADE 在扩缩容出现这个问题 如何解决 在调用方解决还是SS-ROBOT-FACADE解决



SS-ROBOT-FACADE 在扩缩容时出现 "Load balancer does not have available server for client" 的问题，**根本原因在于服务调用方和服务提供方之间的信息同步出现了滞后**，导致调用方仍然持有已失效的服务实例信息。

**解决这个问题需要结合调用方和服务提供方两方面进行优化：**

**1. 服务提供方 (SS-ROBOT-FACADE):**

* **优雅下线**:  在服务实例下线时，应该先从注册中心注销自身，并等待一段时间，确保调用方不再持有该实例信息后再真正下线。可以使用 Spring Cloud 的 `@PreDestroy` 注解或实现 `Lifecycle` 接口来实现优雅下线逻辑。
* **健康检查**: 配置合理的健康检查机制，及时将不健康的实例从服务列表中剔除。

**2. 服务调用方:**

* **缓存刷新**: 及时刷新本地缓存的服务实例列表。可以使用 Spring Cloud 的 `DiscoveryClient` 接口主动获取最新的服务列表，或配置合理的缓存失效时间。
* **重试机制**:  配置合理的重试机制，在第一次调用失败时，可以尝试重新获取服务列表并进行重试。可以使用 Spring Retry 或 Resilience4j 等工具实现重试逻辑。
* **熔断降级**:  对于非核心业务，可以考虑引入熔断降级机制，在 SS-ROBOT-FACADE 服务不可用时，执行预设的降级逻辑，避免级联故障。可以使用 Hystrix 或 Sentinel 等工具实现熔断降级功能。

**总结:**

* 这个问题的解决需要服务提供方和调用方协同配合。
* 服务提供方需要做好优雅下线和健康检查，确保服务实例状态的及时同步。
* 服务调用方需要及时刷新服务列表缓存，并配置合理的重试和熔断降级机制，增强系统的容错能力。

**最终目标是尽可能缩短服务信息同步的滞后时间，提高系统的可用性和稳定性。**



### ERROR [FacadeOpenApiManagerImpl:522][ConsumeMessageThread_10] - [TID: tb-wechat-assist.278.17213545302850011] invoke error com.netflix.hystrix.exception.HystrixRuntimeException: RobotInfoClient#queryRobotsByUsernames(RobotInfoRequest) fallback execution rejected.

RocketMQ的消费类上的太早 服务还没上线


eureka已经上线了
![[../../壁纸/附件/Pasted image 20240719125919.png]]

还是报错
javax.ws.rs.WebApplicationException: com.fasterxml.jackson.core.JsonParseException: processing aborted

![[../../壁纸/附件/Pasted image 20240719125947.png]]



要让负载均衡器立即重新刷新缓存，确保负载均衡器能快速识别新注册的服务实例



负载均衡器无法发现某些实例的原因可能包括以下几点：

1. **缓存问题**：
    
    - 负载均衡器或客户端会缓存服务实例列表。如果缓存未及时刷新，可能会导致负载均衡器无法发现新实例。
2. **健康检查失败**：
    
    - 负载均衡器通常会对实例进行健康检查。如果实例未通过健康检查，负载均衡器会认为这些实例不可用，从而不会将请求分配给它们。
3. **注册中心同步问题**：
    
    - 如果负载均衡器依赖的服务注册中心（如 Eureka、Consul 等）未及时同步所有实例信息，负载均衡器可能无法获取最新的实例列表。
4. **网络问题**：
    
    - 网络延迟或中断可能会导致负载均衡器无法与服务注册中心或实例进行通信，从而无法获取最新的实例列表。
5. **配置错误**：
    
    - 负载均衡器或服务注册中心的配置错误可能会导致负载均衡器无法正确获取实例列表。例如，实例过滤条件不正确、实例标签不匹配等。
6. **实例启动延迟**：
    
    - 新实例在启动过程中可能会有短暂的延迟，在此期间负载均衡器可能无法发现这些实例。