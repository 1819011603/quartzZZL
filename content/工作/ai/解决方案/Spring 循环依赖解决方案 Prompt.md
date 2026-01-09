
## 问题场景

  

当 Spring Bean 之间存在循环依赖时，会出现 `BeanCreationException` 错误，特别是当使用 JDK 动态代理（如 `SpringBasedBalancerConfiguration`）时，`@Lazy` 注解可能无法正常工作，导致 `NullPointerException`。

  

## 解决方案：使用 Helper 类解耦

  

### 核心思路

  

1. **识别循环依赖链**：找出互相依赖的 Service 类

2. **创建 Helper 类**：将公共方法提取到独立的 Helper 类中

3. **重构实现类**：让实现类复用 Helper 类的方法，移除直接依赖

4. **确保 Helper 类只依赖 Gateway**：Helper 类不应该依赖其他 Service，只依赖 Gateway/API

  

### 实施步骤

  

#### 步骤 1：识别循环依赖

  

检查以下情况：

- Service A 依赖 Service B

- Service B 依赖 Service A（直接或间接）

- 配置类（Balancer/Diff）创建代理时需要这些 Service

  

#### 步骤 2：创建 Helper 类

  

**命名规范**：`{ServiceName}QueryHelper` 或 `{ServiceName}Helper`

  

**位置**：`com.gaotu.crm.server.domain.reach.adapter.{module}.helper`

  

**特点**：

- 使用 `@Component` 注解

- 只依赖 Gateway、API 或其他 Helper（不依赖 Service）

- 提供 public 方法供其他类复用

- 将转换逻辑、查询逻辑等公共方法集中管理

  

**示例结构**：

```java

@Component

@Slf4j

public class XxxQueryHelper {

@Resource

private XxxGateway xxxGateway; // 只依赖 Gateway

@Resource

private OtherHelper otherHelper; // 可以依赖其他 Helper

// 公共方法，供 Service 复用

public List<XxxVO> getXxxInfoByNumbers(List<Long> numbers) {

// 实现逻辑

}

// 转换方法（public，可复用）

public XxxVO convertToXxxVO(NewXxxVO newVo) {

// 转换逻辑

}

}

```

  

#### 步骤 3：重构实现类

  

**原则**：

- 移除对 Service 的直接依赖（改为依赖 Helper）

- 移除重复的转换逻辑、查询逻辑

- 只保留业务逻辑和日志记录

- 所有公共方法调用都通过 Helper

  

**示例**：

```java

@Service

public class XxxServiceV1Impl extends XxxServiceImpl {

// ❌ 移除：@Resource private OtherService otherService;

// ✅ 改为：@Resource private XxxQueryHelper xxxQueryHelper;

@Override

public List<XxxVO> getXxxInfo(List<Long> numbers) {

// 复用 Helper 的方法

return xxxQueryHelper.getXxxInfoByNumbers(numbers);

}

}

```

  

#### 步骤 4：扩展 Helper 类的方法

  

**原则**：

- 将实现类中的公共方法提取到 Helper

- 将转换逻辑提取为 public 方法

- 确保方法签名清晰，便于复用

  

**示例**：

```java

// Helper 类中

public List<XxxVO> getXxxInfoByNumbers(List<Long> numbers) {

// 查询逻辑

}

  

public XxxVO convertToXxxVO(NewXxxVO newVo) {

// 转换逻辑（public，可复用）

}

```

  

### 完整示例

  

#### 场景：ClazzAclServiceV1Impl 和 ClazzLessonAclService 循环依赖

  

**问题**：

- `ClazzAclServiceV1Impl` 依赖 `ClazzLessonAclService`

- `ClazzLessonAclService` 的 Balancer 配置需要 `ClazzAclServiceV1Impl`

- 形成循环依赖

  

**解决**：

  

1. **创建 ClazzLessonQueryHelper**：

```java

@Component

@Slf4j

public class ClazzLessonQueryHelper {

@Resource

private ClazzLessonQueryGateway clazzLessonQueryGateway; // 只依赖 Gateway

public List<ClazzLessonVO> getClazzLessonsByClazzNumbers(List<Long> clazzNumbers) {

// 实现查询逻辑

}

}

```

  

2. **重构 ClazzAclServiceV1Impl**：

```java

@Service

public class ClazzAclServiceV1Impl extends ClazzAclServiceImpl {

// ❌ 移除：@Resource private ClazzLessonAclService clazzLessonAclService;

// ✅ 改为：

@Resource

private ClazzLessonQueryHelper clazzLessonQueryHelper;

private List<ClazzLessonVO> getClazzLessonVOS(List<Long> clazzNumbers) {

// 复用 Helper 的方法

return clazzLessonQueryHelper.getClazzLessonsByClazzNumbers(clazzNumbers);

}

}

```

  

### 检查清单

  

完成重构后，检查以下内容：

  

- [ ] Helper 类只依赖 Gateway/API，不依赖其他 Service

- [ ] 实现类移除了对 Service 的直接依赖

- [ ] 所有重复代码已提取到 Helper 类

- [ ] Helper 类的公共方法都是 public

- [ ] 实现类代码量显著减少（通常减少 50%+）

- [ ] 没有编译错误和 Linter 错误

  

### 注意事项

  

1. **不要使用 @Lazy**：当使用 JDK 动态代理（如 Balancer）时，`@Lazy` 可能导致 `NullPointerException`

2. **不要使用 ObjectProvider**：虽然可以延迟加载，但代码复杂度增加，不如 Helper 类清晰

3. **Helper 类应该是无状态的**：只提供查询和转换方法，不保存状态

4. **保持方法粒度适中**：既不要太大（难以复用），也不要太小（过度拆分）

  

### 适用场景

  

- ✅ Service 之间存在循环依赖

- ✅ 需要解耦 Service 之间的直接依赖

- ✅ 有重复的查询逻辑或转换逻辑需要复用

  

### 不适用场景

  

- ❌ Service 之间没有循环依赖（可以直接依赖）

- ❌ 需要事务管理的场景（Helper 类通常不参与事务）

- ❌ 需要 AOP 切面的场景（Helper 类可能无法被切面拦截）

  

## 使用示例

  

当遇到循环依赖问题时，按照以下 prompt 操作：

  

```

我遇到了 Spring 循环依赖问题：

- Service A: {描述}

- Service B: {描述}

- 错误信息: {错误信息}

  

请按照循环依赖解决方案：

1. 创建 Helper 类来解耦

2. 重构实现类复用 Helper 的方法

3. 确保 Helper 类只依赖 Gateway，不依赖其他 Service

4. 移除所有重复代码

```