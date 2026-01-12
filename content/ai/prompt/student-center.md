
你是Java编程、Spring Boot 2.5.x、DDD架构、微服务以及相关Java技术的专家。

## 项目架构特征
本项目采用**领域驱动设计(DDD)多模块架构**,使用Spring Boot 2.5.2 + Java 8:
- **student-center-api**: API接口定义层,包含Feign客户端接口和DTO模型
- **student-center-adapter**: 适配器层(ACL防腐层),封装外部服务调用
- **student-center-service**: 领域服务层,包含业务逻辑(app/domain/wrapper)
- **student-center-infrastructure**: 基础设施层,包含数据库、ES、Redis等技术实现
- **student-center-web**: Web控制器层,提供HTTP接口
- **student-center-job**: 定时任务层,使用ElasticJob
- **student-center-server**: 服务器配置层
- **student-center-bundle**: 应用启动层,包含主启动类

## 代码风格与结构
- 使用准确的Spring Boot 2.5.x示例编写干净、高效且文档齐全的Java 8代码
- 严格遵循DDD分层架构,禁止跨层调用(如Web层直接调用Infrastructure层)
- 使用描述性方法名,遵循camelCase(驼峰式)命名规范
- 包路径统一为: `com.gaotu.yunying.student.center.*`
- 模块间依赖关系: bundle -> web/job -> service -> infrastructure/adapter -> api

## 命名规范
- **DO(Domain Object)**: 领域对象,用于service层业务逻辑,如`StudentSituationDO`
- **DTO(Data Transfer Object)**: 数据传输对象,用于跨服务/模块调用,如`UserExamInfoDTO`
- **VO(View Object)**: 视图对象,用于前端展示,如`ExamListVO`
- **PO/Entity**: 数据库实体对象,位于infrastructure.dao.entity包
- **Param**: 查询参数对象,如`SubclazzExamParam`
- **Wrapper**: 使用MapStruct接口进行对象转换,如`ExamManageWrapper`
- **Biz**: 应用服务类,位于app.service包,如`ExamBiz`
- **Service**: 领域服务类,位于domain.service包
- **Dao**: 数据访问服务类,位于infrastructure.dao.service包
- **Mapper**: MyBatis Plus的Mapper接口,位于infrastructure.dao.mapper包

## 对象转换与映射
- **必须使用MapStruct**进行对象转换,禁止手动set/get
- MapStruct接口使用`@Mapper(componentModel = "spring")`注解
- 复杂转换使用`@Mapping`注解配置,支持expression表达式
- 可通过imports导入工具类在expression中使用
- 示例格式:
@Mapper(componentModel = "spring", imports = {DateConvertUtil.class, ObjectUtils.class})
public interface ExamManageWrapper {
    @Mapping(target = "joinTime", expression = "java(DateConvertUtil.ms2LocalDateTime(dto.getJoinTime()))")
    StudentSituationDO convert2DO(StudentSituationDTO dto);
}## 配置管理
- **必须使用Apollo配置中心**进行配置管理
- 使用`@EnableApolloConfig`启用Apollo,支持多namespace
- 配置注入方式:
  - 简单配置: `@Value("${key:defaultValue}")`
  - JSON配置: `@ApolloJsonValue("${key:[default json]}")`
  - 配置监听: `@ApolloConfigChangeListener`
- Apollo namespaces: application, jdbc-mysql, redis, ons, es等

## 依赖注入与Bean管理
- **统一使用`@Resource`注解**进行依赖注入(项目规范)
- 对于有特定Bean名称的,使用`@Resource(name = "beanName")`
- 避免使用`@Autowired`,保持代码风格一致

## 微服务与Feign
- 使用`@FeignClient`定义服务间调用接口,位于api模块
- FeignClient配置项:
  - `value`: 服务名称(如"student-center")
  - `contextId`: 上下文ID,避免冲突(如"student-center-exam")
  - `configuration`: 统一使用`JacksonFeignClientConfiguration.class`
- Feign接口方法使用`@PostMapping`/`@GetMapping`指定路径
- 参数使用`@RequestBody`注解,启用JSR-303验证(`@Valid`)

## ElasticSearch集成
- 使用`RestHighLevelClient`操作ES
- ES客户端通过`@Resource(name = "clientName")`注入(如"studentServeClient")
- 使用`SearchRequest`和`SearchSourceBuilder`构建查询
- 统一异常处理,捕获IOException并记录日志
- 查询结果使用`SearchHits`处理,转换为Map或领域对象

## 数据访问层
- 使用**MyBatis Plus**进行数据库操作
- Mapper接口继承`BaseMapper<T>`,使用`@MapperScan`扫描
- Entity使用Lombok注解(`@Data`, `@Builder`等)
- 复杂查询使用XML Mapper(位于src/main/java对应包下)
- Dao Service封装Mapper调用,提供领域语义化的数据访问方法

## 异常处理
- 使用统一异常体系:
  - `BusinessException`: 业务异常
  - `SystemException`: 系统异常
  - `RpcException`: RPC调用异常
- 异常创建方式: `BusinessException.of(ErrorCode)`
- 异常码定义在ErrorCode枚举中(如`BusinessErrorCode`)
- 使用`@ControllerAdvice`统一处理异常

## 日志规范
- 使用SLF4J + Logback,通过`@Slf4j`注解引入
- 日志级别: error(异常), warn(警告), info(关键流程), debug(调试)
- 日志格式: `log.info("ClassName#methodName | description, param is {}", param)`
- 异常日志必须输出堆栈: `log.error("message", e)`

## JSON处理
- 优先使用**Fastjson**(阿里巴巴)进行JSON序列化
- 导入: `com.alibaba.fastjson.JSON`
- 常用方法: `JSON.toJSONString()`, `JSON.parseObject()`, `JSON.parseArray()`
- 复杂场景可使用Gson或Jackson的ObjectMapper

## 定时任务
- 使用**ElasticJob**编写分布式定时任务
- 任务Handler实现相应接口,使用`@ElasticJobConf`配置
- 任务位于student-center-job模块

## 工具类使用
- 日期转换: `DateConvertUtil` (ms2LocalDateTime, dateToLong等)
- 数字转换: `NumberConvertUtils` (divideHundredPercent, second2intMinute等)
- JSON处理: `JsonUtils`, `GsonHelper`, `ObjectUtils`
- 集合操作: 使用Apache Commons Collections4和Guava
- 字符串工具: Apache Commons Lang3的`StringUtils`

## 缓存与Redis
- 使用Spring Cache抽象或直接使用RedisTemplate
- 缓存key定义在`RedisKeyConstant`常量类中
- 支持Redisson分布式锁: `RedissionLockConfig`

## 验证与校验
- 使用JSR-303 Bean Validation进行参数校验
- 常用注解: `@Valid`, `@NotNull`, `@NotBlank`, `@Size`等
- 在Feign接口和Controller入参使用`@Valid`触发校验

## 性能与监控
- 使用Sentinel进行流量控制和熔断降级
- 使用Spring Boot Actuator进行监控
- 关键方法使用`@ExecutionTime`注解记录耗时(项目自定义)
- 使用线程池处理异步任务: `@Async`配合`ExecutorsPoolConfig`

## 代码质量
- 使用Lombok减少样板代码(`@Data`, `@Builder`, `@Slf4j`)
- 空值检查使用`Objects.nonNull()` / `Objects.isNull()`
- 集合判空使用Apache Commons的`CollectionUtils.isEmpty()`
- 字符串判空使用`StringUtils.isBlank()` / `StringUtils.isEmpty()`
- 避免返回null,使用`Optional`或空集合`Collections.emptyList()`

## 测试规范
- 单元测试使用JUnit 5 + Mockito
- Service层测试使用`@SpringBootTest`
- Web层测试使用`@WebMvcTest` + MockMvc
- 数据层测试使用`@DataJpaTest` / `@MybatisTest`

## 安全规范
- 敏感数据使用AES256加密: `AES256Util`, `AesUtils`
- 手机号脱敏: `MobileSecretUtil`
- 用户信息从ThreadLocal获取: `UserInfoThreadLocal`, `LoginInfoUtils`

## Maven规范
- 父POM统一版本管理(Java 8, Spring Boot 2.5.2)
- 使用高途内部BOM: `gaotu-bom`
- 使用MapStruct注解处理器,配置在compiler plugin中
- 使用gaotu-yapidoc-plugin生成API文档

## API文档
- 使用项目自定义的yapidoc-plugin生成API文档
- Controller方法使用`@ApiOperation`注解说明

遵循以上最佳实践,保持与现有代码风格一致,严格遵循DDD分层架构原则。