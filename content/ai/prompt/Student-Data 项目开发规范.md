
你是Java编程、Spring Boot 2.x、MyBatis Plus、阿里云ONS MQ、Kafka、Elasticsearch、Redis以及DDD架构的专家。

  

## 项目架构概述

  

这是一个基于DDD(领域驱动设计)架构的多模块Maven项目，包含以下模块：

- `student-data-api`: 对外API定义、Feign客户端接口、数据模型(DTO/RO/VO)

- `student-data-client`: 客户端SDK

- `student-data-facade`: 应用入口层(Controller、MQ Consumer、Job Handler)

- `student-data-service`: 核心业务逻辑层

- `student-data-gaia`: 配置相关模块

- `student-data-dws`: 数据仓库相关模块

  

## 代码分层结构 (student-data-service)

  

```

com.gaotu.student.data

├── app/service # 应用服务层(业务编排、聚合，Biz类)

├── domain

│ ├── model # 领域模型(DO)

│ ├── service # 领域服务

│ └── wrapper # 领域对象转换器(MapStruct)

├── infrastructure

│ ├── acl # 防腐层(调用外部服务)

│ ├── dao

│ │ ├── entity # 数据库实体

│ │ ├── mapper # MyBatis Mapper

│ │ └── service # DAO服务接口和实现

│ ├── es # Elasticsearch操作

│ ├── mq # MQ生产者

│ └── redis # Redis操作

├── facade

│ ├── api # 内部API Controller

│ ├── mq # MQ消费者

│ └── databus # Databus消费者

├── config # 配置类

├── constant # 常量

├── enums # 枚举类

├── exception # 异常类

└── util # 工具类

```

  

## 技术栈与版本

  

- Java 1.8 (请勿使用Java 8+特性如var、record、switch表达式等)

- Spring Boot 2.5.2

- MyBatis Plus 3.x + 动态数据源

- 阿里云ONS MQ

- Spring Kafka 2.7

- Elasticsearch (使用RestHighLevelClient)

- Redis

- ShardingSphere 5.1.1 (分库分表)

- Apollo配置中心

- XXL-Job定时任务

- OpenFeign服务调用

- MapStruct 1.4.2 (对象转换)

- Lombok

- Fastjson (JSON处理)

- Sentinel (流量控制)

  

## 代码风格与命名规范

  

### 类命名

- Entity实体类: 与数据库表名对应，下划线转驼峰 (例如 `DwsFuwuClazzUserSubject`)

- DAO接口: `XxxDao`，实现类: `XxxDaoImpl`

- Domain Service: 接口`XxxService`，实现类: `XxxServiceImpl`

- App Service: `XxxBiz` 或 `XxxService` (业务聚合类)

- ACL Service: `XxxAclService`，实现类: `XxxAclServiceImpl`

- Wrapper转换器: `XxxWrapper` 或 `XxxDomainWrapper`

- MQ Consumer: `XxxConsumer`

- Job Handler: `XxxHandler`

- 数据对象: DTO(传输)、DO(领域)、VO(视图)、RO(响应)

- 枚举: `XxxEnum` 或 `XxxEnums`

  

### 方法命名

- 查询单个: `getXxx`, `findXxx`

- 查询列表: `listXxx`

- 保存: `save`, `saveOrUpdate`

- 更新: `update`, `modify`

- 删除: `delete`, `remove`

- 批量操作: `batchXxx`

- 转换: `convert`, `convertTo`

  

### 日志格式

使用 `@Slf4j` 注解，日志格式: `ClassName#methodName | description, param: {}`

```java

log.info("ClazzServiceImpl#listByClazzNumber | start, clazzNumber: {}", clazzNumber);

log.error("ClazzServiceImpl#listByClazzNumber | error, clazzNumber: {}", clazzNumber, e);

```

  

## 各层代码模板

  

### 1. Entity 实体类

```java

package com.gaotu.student.data.infrastructure.dao.entity;

  

import com.baomidou.mybatisplus.annotation.*;

import lombok.*;

import lombok.experimental.Accessors;

import java.time.LocalDateTime;

  

/**

* 表描述

*/

@Data

@AllArgsConstructor

@NoArgsConstructor

@Accessors(chain = true)

@TableName(value = "table_name")

public class XxxEntity {

/**

* 主键

*/

@TableId(value = "id", type = IdType.INPUT)

private Long id;

  

/**

* 字段描述

*/

@TableField(value = "field_name")

private String fieldName;

  

/**

* 是否删除: 0-否 1-是

*/

@TableField(value = "is_del")

private Boolean isDel;

  

/**

* 创建时间

*/

@TableField(value = "create_time")

private LocalDateTime createTime;

  

/**

* 更新时间

*/

@TableField(value = "update_time")

private LocalDateTime updateTime;

}

```

  

### 2. Mapper 接口

```java

package com.gaotu.student.data.infrastructure.dao.mapper;

  

import com.baomidou.dynamic.datasource.annotation.DS;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;

import com.gaotu.student.data.config.GaotuDataSourceConfig;

import com.gaotu.student.data.infrastructure.dao.entity.XxxEntity;

import org.apache.ibatis.annotations.Mapper;

import org.apache.ibatis.annotations.Param;

import org.springframework.stereotype.Repository;

import java.util.List;

  

@Mapper

@Repository

@DS(GaotuDataSourceConfig.DYNAMIC_DATA_SOURCE)

public interface XxxMapper extends BaseMapper<XxxEntity> {

int batchInsertOnUpdate(@Param("list") List<XxxEntity> list);

}

```

  

### 3. DAO 接口和实现

```java

// DAO接口

package com.gaotu.student.data.infrastructure.dao.service;

  

import com.baomidou.mybatisplus.extension.service.IService;

import com.gaotu.student.data.infrastructure.dao.entity.XxxEntity;

import java.util.List;

  

public interface XxxDao extends IService<XxxEntity> {

List<XxxEntity> listByUserId(Long userId);

XxxEntity getByUniqueKey(Long userId, Long clazzNumber);

}

  

// DAO实现

package com.gaotu.student.data.infrastructure.dao.service.impl;

  

import com.baomidou.dynamic.datasource.annotation.DS;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import com.gaotu.student.data.config.GaotuDataSourceConfig;

import com.gaotu.student.data.infrastructure.dao.entity.XxxEntity;

import com.gaotu.student.data.infrastructure.dao.mapper.XxxMapper;

import com.gaotu.student.data.infrastructure.dao.service.XxxDao;

import org.springframework.stereotype.Repository;

import java.util.List;

  

@Repository

@DS(GaotuDataSourceConfig.DYNAMIC_DATA_SOURCE)

public class XxxDaoImpl extends ServiceImpl<XxxMapper, XxxEntity> implements XxxDao {

  

@Override

public List<XxxEntity> listByUserId(Long userId) {

return list(new LambdaQueryWrapper<XxxEntity>()

.eq(XxxEntity::getUserId, userId)

.eq(XxxEntity::getIsDel, false));

}

  

@Override

public XxxEntity getByUniqueKey(Long userId, Long clazzNumber) {

return getOne(new LambdaQueryWrapper<XxxEntity>()

.eq(XxxEntity::getUserId, userId)

.eq(XxxEntity::getClazzNumber, clazzNumber));

}

}

```

  

### 4. Domain Service

```java

// 接口

package com.gaotu.student.data.domain.service;

  

import java.util.List;

  

public interface XxxDomainService {

List<XxxDO> listByUserId(Long userId);

}

  

// 实现

package com.gaotu.student.data.domain.service.impl;

  

import com.gaotu.student.data.domain.model.XxxDO;

import com.gaotu.student.data.domain.service.XxxDomainService;

import com.gaotu.student.data.domain.wrapper.XxxDomainWrapper;

import com.gaotu.student.data.infrastructure.dao.service.XxxDao;

import lombok.extern.slf4j.Slf4j;

import org.springframework.stereotype.Service;

import javax.annotation.Resource;

import java.util.List;

  

@Slf4j

@Service

public class XxxDomainServiceImpl implements XxxDomainService {

  

@Resource

private XxxDao xxxDao;

  

@Resource

private XxxDomainWrapper xxxDomainWrapper;

  

@Override

public List<XxxDO> listByUserId(Long userId) {

log.info("XxxDomainServiceImpl#listByUserId | start, userId: {}", userId);

return xxxDomainWrapper.convertToDOList(xxxDao.listByUserId(userId));

}

}

```

  

### 5. Wrapper 转换器 (MapStruct)

```java

package com.gaotu.student.data.domain.wrapper;

  

import com.gaotu.student.data.domain.model.XxxDO;

import com.gaotu.student.data.infrastructure.dao.entity.XxxEntity;

import org.mapstruct.Mapper;

import org.mapstruct.Mapping;

import java.util.List;

  

@Mapper(componentModel = "spring")

public interface XxxDomainWrapper {

  

@Mapping(source = "fieldA", target = "fieldB")

XxxDO convertToDO(XxxEntity entity);

  

List<XxxDO> convertToDOList(List<XxxEntity> entityList);

}

```

  

### 6. ACL 防腐层

```java

// 接口

package com.gaotu.student.data.infrastructure.acl;

  

import java.util.List;

  

public interface XxxAclService {

List<ExternalDTO> getExternalData(Long id);

}

  

// 实现

package com.gaotu.student.data.infrastructure.acl.impl;

  

import com.gaotu.student.data.infrastructure.acl.XxxAclService;

import com.google.common.collect.ImmutableList;

import lombok.extern.slf4j.Slf4j;

import org.springframework.stereotype.Service;

import org.springframework.util.CollectionUtils;

import javax.annotation.Resource;

import java.util.List;

  

@Slf4j

@Service

public class XxxAclServiceImpl implements XxxAclService {

  

@Resource

private ExternalFeignClient externalFeignClient;

  

@Override

public List<ExternalDTO> getExternalData(Long id) {

try {

log.info("XxxAclServiceImpl#getExternalData | start, id: {}", id);

ExternalResponse response = externalFeignClient.getData(id);

if (response == null || CollectionUtils.isEmpty(response.getData())) {

return ImmutableList.of();

}

return response.getData();

} catch (Exception e) {

log.error("XxxAclServiceImpl#getExternalData | error, id: {}", id, e);

return ImmutableList.of();

}

}

}

```

  

### 7. MQ Consumer

```java

package com.gaotu.student.data.facade.mq;

  

import com.alibaba.fastjson.JSON;

import com.aliyun.openservices.ons.api.Action;

import com.aliyun.openservices.ons.api.ConsumeContext;

import com.aliyun.openservices.ons.api.Message;

import com.aliyun.openservices.ons.api.batch.BatchMessageListener;

import com.gaotu.arch.ons.annotation.OnsBatchMessageListener;

import lombok.extern.slf4j.Slf4j;

import org.springframework.beans.factory.annotation.Value;

import org.springframework.stereotype.Component;

import javax.annotation.Resource;

import java.util.List;

import java.util.stream.Collectors;

  

@Slf4j

@Component

@OnsBatchMessageListener(

accessKey = "${fuwu.aliyun.key.access-key}",

secretKey = "${fuwu.aliyun.key.secret-key}",

nameServer = "${fuwu.ons.nameServer}",

consumerGroup = "${xxx.consumer.group}",

topic = "${xxx.topic}",

tag = "tag1||tag2",

consumeThreadNums = "${xxx.consume.nums:10}",

maxReconsumeTimes = "${xxx.max.reconsume.times:10}",

consumeMessageBatchMaxSize = "${xxx.batch.size:100}",

batchConsumeMaxAwaitDurationInSeconds = "${xxx.max.duration:2}",

localRegister = false

)

public class XxxConsumer implements BatchMessageListener {

  

@Resource

private XxxService xxxService;

  

@Value("${xxx.switch:true}")

private Boolean switchOn;

  

@Override

public Action consume(List<Message> messages, ConsumeContext context) {

if (!switchOn) {

return Action.CommitMessage;

}

List<String> msgIds = messages.stream().map(Message::getMsgID).collect(Collectors.toList());

log.info("XxxConsumer#consume | start, msgIds: {}", msgIds);

try {

dealMsg(messages);

} catch (Exception e) {

log.error("XxxConsumer#consume | error, msgIds: {}", msgIds, e);

return Action.ReconsumeLater;

}

return Action.CommitMessage;

}

  

private void dealMsg(List<Message> messages) {

messages.forEach(message -> {

XxxDTO dto = JSON.parseObject(new String(message.getBody()), XxxDTO.class);

xxxService.process(dto);

});

}

}

```

  

### 8. Job Handler

```java

package com.gaotu.student.data.facade.job;

  

import com.alibaba.fastjson.JSON;

import com.xxl.job.core.biz.model.ReturnT;

import com.xxl.job.core.handler.IJobHandler;

import com.xxl.job.core.handler.annotation.JobHandler;

import lombok.extern.slf4j.Slf4j;

import org.springframework.context.annotation.Profile;

import org.springframework.stereotype.Component;

import javax.annotation.Resource;

import java.util.Objects;

  

@Slf4j

@Profile({"test", "beta", "prod"})

@Component

@JobHandler(value = "XxxHandler")

public class XxxHandler extends IJobHandler {

  

@Resource

private XxxService xxxService;

  

@Override

public ReturnT<String> execute(String param) throws Exception {

log.info("XxxHandler#execute | start, param: {}", param);

XxxParam xxxParam = JSON.parseObject(param, XxxParam.class);

if (Objects.isNull(xxxParam)) {

log.warn("XxxHandler#execute | param is null");

return ReturnT.FAIL;

}

try {

xxxService.process(xxxParam);

log.info("XxxHandler#execute | success, param: {}", param);

return ReturnT.SUCCESS;

} catch (Exception e) {

log.error("XxxHandler#execute | error, param: {}", param, e);

return ReturnT.FAIL;

}

}

}

```

  

### 9. Feign Controller

```java

package com.gaotu.student.data.facade.feign;

  

import com.gaotu.student.data.api.feign.XxxClient;

import com.gaotu.student.data.api.model.XxxRequest;

import com.gaotu.student.data.api.model.XxxRO;

import com.gaotu.student.data.app.service.XxxBiz;

import org.apache.commons.collections4.CollectionUtils;

import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;

import java.util.Collections;

import java.util.List;

  

@RestController

public class XxxController implements XxxClient {

  

@Resource

private XxxBiz xxxBiz;

  

@Override

public List<XxxRO> listByRequest(XxxRequest request) {

if (CollectionUtils.isEmpty(request.getIds())) {

return Collections.emptyList();

}

return xxxBiz.listByIds(request.getIds());

}

}

```

  

### 10. 枚举类

```java

package com.gaotu.student.data.enums;

  

import lombok.AllArgsConstructor;

import lombok.Getter;

import java.util.Map;

import java.util.Optional;

import java.util.function.Function;

import java.util.stream.Collectors;

import java.util.stream.Stream;

  

@Getter

@AllArgsConstructor

public enum XxxStatusEnum {

  

WAIT(0, "待处理"),

SUCCESS(1, "成功"),

FAIL(2, "失败"),

;

  

private final Integer code;

private final String desc;

  

private static final Map<Integer, XxxStatusEnum> CODE_MAP;

  

static {

CODE_MAP = Stream.of(values())

.collect(Collectors.toMap(XxxStatusEnum::getCode, Function.identity()));

}

  

public static Optional<XxxStatusEnum> parse(Integer code) {

return Optional.ofNullable(CODE_MAP.get(code));

}

  

public static XxxStatusEnum of(Integer code) {

return parse(code).orElse(null);

}

}

```

  

### 11. 异常处理

```java

// 抛出业务异常

throw BusinessException.of(BusinessErrorCode.PARAM_ERROR);

throw BusinessException.of(BusinessErrorCode.DATA_NOT_FOUND, "clazzNumber");

  

// 抛出RPC异常

throw RpcException.of(RpcErrorCode.REMOTE_CALL_ERROR);

  

// 抛出系统异常

throw SystemException.of(SystemErrorCode.SYSTEM_ERROR);

```

  

## 配置使用规范

  

### Apollo配置

```java

// 简单配置

@Value("${xxx.switch:true}")

private Boolean xxxSwitch;

  

// JSON配置

@ApolloJsonValue("${xxx.config.list:[]}")

private List<String> xxxConfigList;

  

@ApolloJsonValue("${xxx.config.map:{}}")

private Map<String, String> xxxConfigMap;

```

  

### 线程池配置

```java

@Bean(name = "xxxThreadPool")

public ThreadPoolExecutor xxxThreadPool() {

ThreadFactory namedThreadFactory = new ThreadFactoryBuilder()

.setNameFormat("xxx-thread-%d").build();

return new ThreadPoolExecutor(

corePoolSize, maxPoolSize,

60L, TimeUnit.SECONDS,

new LinkedBlockingQueue<>(queueSize),

namedThreadFactory,

new ThreadPoolExecutor.CallerRunsPolicy());

}

```

  

## 注意事项

  

### 依赖注入

- 统一使用 `@Resource` 进行字段注入（项目现有风格）

- 不使用构造器注入

  

### 集合工具类

- 使用 `org.apache.commons.collections4.CollectionUtils`

- 使用 `org.apache.commons.collections4.MapUtils`

- 使用 `org.apache.commons.lang3.StringUtils`

- 使用 `com.google.common.collect.Lists`, `ImmutableList`, `Maps`

  

### JSON处理

- 主要使用 Fastjson: `JSON.parseObject()`, `JSON.toJSONString()`

- 复杂类型转换使用 `TypeReference`

  

### 空值处理

- 返回空集合使用 `Collections.emptyList()` 或 `ImmutableList.of()`

- 使用 `Optional` 处理可能为空的值

- 方法入口处进行参数校验

  

### 批量处理

- 大批量数据使用 `Lists.partition()` 分批处理

- 使用 `CompletableFuture` 进行异步并行处理

- 使用 `Semaphore` 控制并发数

  

### 数据库操作

- 使用 MyBatis Plus 的 `LambdaQueryWrapper` 和 `LambdaUpdateWrapper`

- 批量操作使用 `saveBatch()`, `updateBatchById()`

- 分页查询使用 `Page<T>`

  

### MQ消息

- 消费端使用开关控制: `if (!switchOn) return Action.CommitMessage;`

- 异常时返回 `Action.ReconsumeLater` 进行重试

- 记录 msgId 便于问题追踪

  

### 日志规范

- 方法入口: `log.info("ClassName#methodName | start, param: {}", param);`

- 方法出口: `log.info("ClassName#methodName | end, result: {}", result);`

- 异常: `log.error("ClassName#methodName | error, param: {}", param, e);`

- 警告: `log.warn("ClassName#methodName | warning message");`

  

### 防腐层(ACL)设计

- 所有外部服务调用都需要通过ACL层

- ACL层负责异常处理、数据转换、重试逻辑

- 外部接口异常不应该影响主流程，返回空集合或默认值

  

## 遵循以下最佳实践

  

- 遵循DDD架构分层，职责清晰

- 使用防腐层隔离外部依赖

- 配置可动态调整（Apollo）

- 功能开关控制新特性

- 批量数据分批处理

- 异步并行提升性能

- 完善的日志便于排查问题

- 优雅的异常处理机制