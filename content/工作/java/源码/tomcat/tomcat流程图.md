
![[../../../壁纸/附件/Pasted image 20250208164631.png]]


在Servlet中调用服务方法之前，包装器的基本阀将调用过滤器链，我们可以在其中执行一些业务逻辑，例如，身份验证，架构验证等。以下代码是StandardWrapperValve Invoke方法的PICE。
![[../../../壁纸/附件/Pasted image 20250208164926.png]]

ApplicationFilterChain  会处理完所有Filter之后 调用servlet.service(request, response);来执行执行器逻辑
![[../../../壁纸/附件/Pasted image 20250208165111.png]]

![[../../../壁纸/附件/Pasted image 20250208165126.png]]









![[../../../壁纸/附件/Pasted image 20250208164448.png]]


![[../../../壁纸/附件/Pasted image 20250208165339.png]]



### what’s the difference between Valve pipeline and FilterChain?

气门管道和过滤链有什么区别？

阀门属于Tomcat框架，而过滤器链是为用户设计的。每当请求到达时，都会调用阀门。




**Tomcat 如何在一个端口上运行多个 Web 应用程序？**

Tomcat 能够在一个端口上运行多个 Web 应用程序，主要依赖于两个关键机制： **虚拟主机 (Virtual Hosts)** 和 **上下文路径 (Context Paths)**。

- **虚拟主机 (Virtual Hosts):**
    
    - 虚拟主机允许你在**同一个 Tomcat 实例上配置多个域名（或IP地址）**。 每个虚拟主机 (在 Tomcat 中用 `<Host>` 元素配置) 可以绑定一个或多个域名。
    - 当客户端发送请求时，请求头 (Host header) 中会包含域名信息。 Tomcat 会根据请求头中的域名，将请求路由到**匹配的虚拟主机**进行处理。
    - 即使使用同一个端口，只要域名不同，Tomcat 就可以区分请求应该由哪个虚拟主机下的 Web 应用程序处理。
- **上下文路径 (Context Paths):**
    
    - 在每个虚拟主机 ( `<Host>`) 下，可以部署多个 Web 应用程序 (用 `<Context>` 元素配置)。 每个 Web 应用程序都必须定义一个**唯一的上下文路径 (Context Path)**。
    - 上下文路径是 URL 中域名之后、Servlet 路径之前的部分，用来标识不同的 Web 应用程序。 例如，在 URL `http://www.example.com/app1/servlet/example` 中，`/app1` 就是上下文路径。
    - 当请求到达 Tomcat 的某个虚拟主机后，Tomcat 会**根据请求 URL 的上下文路径**，将请求进一步路由到**匹配的 Web 应用程序 (Context)** 进行处理。



| 特性       | Tomcat 虚拟主机 (Virtual Host) | Spring Boot Controller    |
| -------- | -------------------------- | ------------------------- |
| **概念层级** | Tomcat 服务器级别               | Spring Boot 应用程序级别        |
| **作用范围** | 管理多个网站/Web 应用              | 处理单个 Web 应用内的请求           |
| **配置位置** | `server.xml` 配置文件          | Spring Boot 应用程序代码 (Java) |
| **关注点**  | 域名/IP 地址、网站根目录             | URL 路径、业务逻辑               |
| **类比**   | 多个独立的网站托管在同一服务器            | 单个网站的不同功能模块/页面            |





通过以上几个例子，希望你能够更直观地理解 Tomcat 不同类加载器的作用：

- **WebAppClassLoader:** 实现 **Web 应用程序之间的类隔离**，避免版本冲突，支持热部署。 (隔离性)
- **CommonClassLoader:** 实现 **Tomcat 服务器级别通用类库的共享**，方便代码复用。 (共享性)
- **CatalinaClassLoader:** 实现 **Tomcat 服务器自身类库的隔离**，保证服务器的稳定性和安全性。 (隔离性)
- **SharedClassLoader:** 实现 **Web 应用程序之间共享类库** (可选)。 (共享性，但范围比 CommonClassLoader 小)
- **WebApp-First 加载顺序:** 保证 **Web 应用程序优先加载自身携带的类库**，增强 Web 应用的独立性和灵活性。 (加载顺序)



### Tomcat 组件与 Spring Boot Controller 的连接


Tomcat 的 `Host`, `Engine`, `Context`, `Wrapper` 组件为 Spring Boot Web 应用提供了 Servlet 容器的基础设施。 请求首先由 Tomcat 组件接收和路由，最终通过 `Wrapper` 组件将请求传递给 Spring MVC 的核心组件 `DispatcherServlet`，再由 `DispatcherServlet` 协调 Spring MVC 框架来调用 Spring Boot 的 `Controller` 处理业务逻辑。 理解这种连接关系，能够帮助你更好地理解 Spring Boot Web 应用的运行机制，以及如何在 Spring Boot 环境下进行更深入的 Tomcat 配置和定制化


- **Tomcat 组件 (Connector, Engine, Host, Context, Wrapper) 负责 Web 请求的底层处理和路由，构建了 Servlet 容器的基础框架。** 它们就像 HTTP 请求的“高速公路”和“交通枢纽”，负责接收、路由和传递请求到正确的目的地。
- **Tomcat `Wrapper` 组件是连接 Tomcat Servlet 容器和 Spring MVC 框架的关键桥梁。** `Wrapper` 负责实例化和调用 `DispatcherServlet`，将请求从 Tomcat 容器传递到 Spring MVC 框架。
- **Spring Boot `Controller` 则是 Spring MVC 框架中的 Handler，负责处理具体的业务逻辑，是 Web 请求的 “最终目的地”。** 它接收 `DispatcherServlet` 分发的请求，执行业务操作，并生成响应结果。


**形象比喻：快递服务**

- **Tomcat Connector:** 就像快递公司的 **揽件员**，负责接收包裹（HTTP 请求）。
- **Tomcat Engine/Host/Context:** 就像快递公司的 **分拣中心和运输网络**，负责根据地址（URL）将包裹路由到正确的区域和目的地（Web 应用）。
- **Tomcat Wrapper (DispatcherServlet):** 就像快递公司 **最后一公里配送站点的配送员**，负责将包裹（请求）送到最终的收件人手中 (Spring MVC DispatcherServlet)。
- **Spring Boot Controller:** 就像 **最终的收件人**，接收包裹（请求），并进行处理 (业务逻辑)。
- **Spring MVC 框架：** 就像快递公司的 **内部运营系统**，负责协调和管理包裹的整个配送流程，包括分拣、路由、配送等。




**图中步骤说明：**

1. **Client Request:** 客户端发送 HTTP 请求。
2. **Tomcat Connector:** Tomcat `Connector` 组件接收请求。
3. **Tomcat Engine/Host/Context:** Tomcat `Engine`, `Host`, `Context` 组件负责请求路由和 Web 应用定位。
4. **Tomcat Wrapper (DispatcherServlet):** Tomcat `Wrapper` 组件负责创建和调用 `DispatcherServlet` 实例。 **这是 Tomcat 组件与 Spring Boot 的连接点！**
5. **Spring MVC DispatcherServlet:** `DispatcherServlet` 接收请求，作为 Spring MVC 的前端控制器。
6. **Spring MVC Handler Mapping:** `DispatcherServlet` 使用 HandlerMapping 组件查找匹配的 Handler (Controller 方法)。
7. **Spring Boot Controller:** Spring Boot `Controller` (Handler) 处理业务逻辑。
8. **Spring MVC View Resolution (Optional):** Spring MVC 进行视图解析（如果需要）。
9. **HTTP Response:** Spring MVC 生成 HTTP 响应，通过 Tomcat 组件返回给客户端。


![[../../../壁纸/附件/Pasted image 20250208173118.png]]