


找出所有位于 `com.gaotu.client.feign` 包下的 FeignClient 接口 和 *name 为"COURSE-SETTING.GAOTU100.COM"的FeignClient   增加 pringBasedBalancerConfiguration 和 SpringBasedDiffBeanConfiguration 的配置类 
总结以下内容：

### 依赖说明
项目依赖：
```xml
<dependency>  
    <groupId>com.gaotu</groupId>  
    <artifactId>blocks-tools-starter</artifactId>  
    <version>2.0.3</version>  
</dependency>
```



这两个基类来自 blocks-tools-starter，不需要生成分析报告 不需要生成md文件 直接改造

### 1. 配置类结构

#### 1.1 SpringBasedBalancerConfiguration 配置类模式
找出所有继承 SpringBasedBalancerConfiguration 的配置类，记录：
- 配置类名称（如：BalanceSubClazzDiffConfiguration）
- CONFIG_KEY_PRE 常量值（如："student.center.replace.balancer."）
- @Bean 方法名称和返回类型
- first 参数类型（老实现类，如：SubClazzAclServiceImpl）
- second 参数类型（新实现类，如：SubClazzAclServiceV1Impl）
- 接口类型（Service 接口，如：SubClazzAclService）
- @Resource 注入的 DiffProxy 名称（如：replaceSubClazzDiff）
- 是否使用 @Primary 注解
- 是否使用 @Lazy 注解

配置类模板结构：
```java
@Configuration
@Lazy  // 可选
public class XxxBalancerBeanConfiguration extends SpringBasedBalancerConfiguration {
    public static final String CONFIG_KEY_PRE = "xxx.balancer.";
    
    @Resource(name = "xxxDiffProxy")
    private XxxService xxxDiffProxy;
    
    @Bean
    @Primary
    public XxxService xxxBalancer(XxxServiceImpl first, XxxServiceV1Impl second) {
        return createGrayscaleProxy(xxxDiffProxy, second, XxxService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());
    }
}
```

#### 1.2 SpringBasedDiffBeanConfiguration 配置类模式
找出所有继承 SpringBasedDiffBeanConfiguration 的配置类，记录：
- 配置类名称（如：ReplaceSubClazzDiffConfiguration）
- CONFIG_KEY_PRE 常量值（如："student.center.replace.diff."）
- @Bean 方法名称和返回类型
- Bean 名称（name 属性，如："replaceSubClazzDiff"）
- first 参数类型（老实现类）
- second 参数类型（新实现类）
- 接口类型
- 是否使用 @Lazy 注解

配置类模板结构：
```java
@Configuration
@Lazy  // 可选
public class XxxDiffBeanConfiguration extends SpringBasedDiffBeanConfiguration {
    public static final String CONFIG_KEY_PRE = "xxx.diff.";
    
    @Bean(name = "xxxDiffProxy")
    public XxxService xxxDiffProxy(XxxServiceImpl first, XxxServiceV1Impl second) {
        return createProxy(first, second, XxxService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());
    }
}
```

### 2. 实现类关系

对于每个配置类涉及的实现类，记录：

#### 2.1 接口定义
- 接口名称：XxxService 或 XxxAclService
- 接口包路径
- 接口方法签名

#### 2.2 老实现类（Impl）
- 类名：XxxServiceImpl 或 XxxAclServiceImpl
- 包路径
- 实现的接口
- @Service 注解信息
- @Qualifier 注解值（如果有，如："subclazzAclServiceImpl"）
- 主要依赖和实现逻辑

#### 2.3 新实现类（V1Impl）
- 类名：XxxServiceV1Impl 或 XxxAclServiceV1Impl
- 包路径
- **继承关系：继承老实现类（XxxServiceImpl）**
- @Service 注解信息
- @Qualifier 注解值（如果有，如："subclazzAclServiceV1Impl"）
- 主要依赖和实现逻辑
- **注意：V1Impl 暂时直接继承 Impl，而不是实现接口**

### 3. FeignClient 改造范围

#### 3.1 FeignClient 结构
找出所有位于 `com.gaotu.client.feign` 包下的 FeignClient 接口，以及所有使用 `name = "XXX.GAOTU100.COM"` 格式的 @FeignClient 注解，记录：
- FeignClient 接口名称（如：ISkuService, ICourseService）
- FeignClient 接口包路径（如：com.gaotu.client.feign.commodity.sku.ISkuService）
- Adapter 类名称（如：ISkuServiceAdapter, CourseAdapter）
- Adapter 类包路径
- @FeignClient 注解信息：
  * contextId（如果有）
  * name 值（如："COURSE-SETTING.GAOTU100.COM"）
  * path 值（如："/feign/sku"）
  * configuration 配置类
- Adapter 继承的 FeignClient 接口

#### 3.2 FeignClient 改造模式
对于需要改造的 FeignClient：

**老实现（Adapter）**：
- Adapter 接口继承 com.gaotu.client.feign 下的接口
- 添加 @FeignClient 注解，name 格式为 "XXX.GAOTU100.COM"
- 在 Service 实现类中注入并使用该 Adapter

**新实现（V1Impl）**：
- **暂时不创建 V1Adapter**
- V1Impl 继承 Impl，继续使用原有的 Adapter
- 在需要时重写特定方法，实现新的业务逻辑

**改造步骤**：
1. 保持原有 Adapter 不变（作为老实现和新实现的共同依赖）
2. **不需要创建 V1Adapter**
3. 创建 V1Impl，继承 Impl，继续使用原 Adapter
4. 按照标准模式创建 Diff 和 Balancer 配置类

**示例**：
```java
// 老实现 - ISkuServiceAdapter（保持不变，V1Impl 也使用它）
@FeignClient(
    contextId = "isku",
    name = "COURSE-SETTING.GAOTU100.COM",
    path = "/feign/sku",
    configuration = {CourseSettingFeignConfig.class}
)
public interface ISkuServiceAdapter extends ISkuService {
}

// Service 接口
public interface SkuAclService {
    SkuVO getSkuInfo(Long skuId);
}

// 老实现
@Service("skuAclServiceImpl")
@Qualifier("skuAclServiceImpl")
public class SkuAclServiceImpl implements SkuAclService {
    @Resource
    private ISkuServiceAdapter skuServiceAdapter;
    
    @Override
    public SkuVO getSkuInfo(Long skuId) {
        return skuServiceAdapter.getSkuInfo(skuId);
    }
}

// 新实现 - 继承 Impl，使用相同的 Adapter
@Service("skuAclServiceV1Impl")
@Qualifier("skuAclServiceV1Impl")
public class SkuAclServiceV1Impl extends SkuAclServiceImpl {
    // 继承父类的 skuServiceAdapter
    // 可以重写特定方法实现新逻辑
    @Override
    public SkuVO getSkuInfo(Long skuId) {
        // 新的实现逻辑
        return super.getSkuInfo(skuId);  // 或完全重写
    }
}
```

### 4. 扫描包配置

在 @SpringBootApplication 中需要添加扫描包配置，确保配置类能被扫描到：
```java
@SpringBootApplication(
    scanBasePackages = {
        "com.gaotu.crm",  // 项目主包
        "com.gaotu.student.data.gaia",  // 其他需要扫描的包
        "com.gaotu.blocks.starter"  // 必须包含，用于扫描配置类
    }
)
```

注意：如果配置类在项目主包下，通常主包已经在扫描范围内，但必须确保包含 "com.gaotu.blocks.starter"。

### 5. 在目标项目中应用

#### 5.1 单类服务改造为接口+实现类模式

如果服务只有单个实现类（没有接口），需要按以下步骤改造：

**步骤1：提取接口**
- 创建接口：XxxService 或 XxxAclService
- 将所有公共方法提取到接口中
- 接口放在 acl 包下（如：com.gaotu.base.acl.XxxService）

**步骤2：重命名原实现类**
- 将原类改为 XxxServiceImpl
- 实现新创建的接口
- 添加 @Service("xxxServiceImpl") 和 @Qualifier("xxxServiceImpl")
- 保持原有实现逻辑不变

**步骤3：创建新实现类**
- 创建 XxxServiceV1Impl
- **继承 XxxServiceImpl（而不是实现接口）**
- 添加 @Service("xxxServiceV1Impl") 和 @Qualifier("xxxServiceV1Impl")
- 可以重写父类方法实现新的业务逻辑，或保持继承关系不变

**步骤4：创建 Diff 配置类**
- 创建 XxxServiceDiffBeanConfiguration
- 继承 SpringBasedDiffBeanConfiguration
- 定义 CONFIG_KEY_PRE = "fairy.diff."
- 创建 @Bean 方法，返回 DiffProxy
- Bean 名称格式：xxxServiceDiffProxy（首字母小写）

**步骤5：创建 Balancer 配置类**
- 创建 XxxServiceBalancerBeanConfiguration
- 继承 SpringBasedBalancerConfiguration
- 定义 CONFIG_KEY_PRE = "fairy.balancer."
- 注入 DiffProxy（@Resource(name = "xxxServiceDiffProxy")）
- 创建 @Bean 方法，使用 @Primary，调用 createGrayscaleProxy

**步骤6：更新依赖注入**
- 将所有直接注入实现类的地方改为注入接口
- 使用 @Qualifier 指定具体实现（如果需要）

**步骤7：更新扫描包配置**
- 在 @SpringBootApplication 中添加 "com.gaotu.blocks.starter" 到 scanBasePackages

#### 5.2 FeignClient 服务改造

如果服务依赖 FeignClient（位于 com.gaotu.client.feign 包下或使用 name = "XXX.GAOTU100.COM" 格式），需要按以下步骤改造：

**步骤1：找出现有 FeignClient**
- 找出 com.gaotu.client.feign 包下的接口（如：ISkuService）
- 找出对应的 Adapter 类（如：ISkuServiceAdapter）
- 记录 @FeignClient 注解配置（name、path、configuration 等）

**步骤2：保持 Adapter 不变**
- **不需要创建 V1Adapter**
- 原有的 Adapter 继续使用，V1Impl 也使用同一个 Adapter

**步骤3：改造 Service 实现类**
- 老实现（XxxServiceImpl）：使用原 Adapter
- 新实现（XxxServiceV1Impl）：**继承 XxxServiceImpl，继续使用原 Adapter**
- 确保两个实现类实现相同的接口

**步骤4：创建配置类**
- 按照标准模式创建 Diff 和 Balancer 配置类
- 配置类中的 first 和 second 参数分别是 XxxServiceImpl 和 XxxServiceV1Impl

**示例改造**：
```java
// 1. Adapter（保持不变，V1Impl 也使用它）
@FeignClient(
    contextId = "isku",
    name = "COURSE-SETTING.GAOTU100.COM",
    path = "/feign/sku",
    configuration = {CourseSettingFeignConfig.class}
)
public interface ISkuServiceAdapter extends ISkuService {
}

// 2. Service 接口
public interface SkuAclService {
    SkuVO getSkuInfo(Long skuId);
}

// 3. 老实现
@Service("skuAclServiceImpl")
@Qualifier("skuAclServiceImpl")
public class SkuAclServiceImpl implements SkuAclService {
    @Resource
    private ISkuServiceAdapter skuServiceAdapter;
    
    @Override
    public SkuVO getSkuInfo(Long skuId) {
        return skuServiceAdapter.getSkuInfo(skuId);
    }
}

// 4. 新实现 - 继承 Impl，使用相同的 Adapter
@Service("skuAclServiceV1Impl")
@Qualifier("skuAclServiceV1Impl")
public class SkuAclServiceV1Impl extends SkuAclServiceImpl {
    // 继承父类的 skuServiceAdapter，无需重新注入
    // 可以重写特定方法实现新逻辑，或保持继承关系不变
}

// 5. Diff 配置
@Configuration
public class SkuAclServiceDiffBeanConfiguration extends SpringBasedDiffBeanConfiguration {
    public static final String CONFIG_KEY_PRE = "fairy.diff.";
    
    @Bean(name = "skuAclServiceDiffProxy")
    public SkuAclService skuAclServiceDiffProxy(SkuAclServiceImpl first, SkuAclServiceV1Impl second) {
        return createProxy(first, second, SkuAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());
    }
}

// 6. Balancer 配置
@Configuration
public class SkuAclServiceBalancerBeanConfiguration extends SpringBasedBalancerConfiguration {
    public static final String CONFIG_KEY_PRE = "fairy.balancer.";
    
    @Resource(name = "skuAclServiceDiffProxy")
    private SkuAclService skuAclServiceDiffProxy;
    
    @Bean
    @Primary
    public SkuAclService skuAclService(SkuAclServiceImpl first, SkuAclServiceV1Impl second) {
        return createGrayscaleProxy(skuAclServiceDiffProxy, second, SkuAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());
    }
}
```

### 6. Apollo 配置生成规则

#### 6.1 SpringBasedBalancerConfiguration 配置规则

**规则**：
```
{CONFIG_KEY_PRE}{first.getClass().getSimpleName()}.grayscale={"sql":100,"rpc":0}
```

**说明**：
- CONFIG_KEY_PRE：配置类中定义的常量值
- first.getClass().getSimpleName()：老实现类的简单类名（不是接口名）
- grayscale：固定后缀
- 值格式：{"sql":100,"rpc":0}，sql 和 rpc 表示不同调用方式的灰度比例

**示例**：
- 配置类：BalanceSubClazzDiffConfiguration
- CONFIG_KEY_PRE = "student.center.replace.balancer."
- first = SubClazzAclServiceImpl
- 生成的配置：`student.center.replace.balancer.SubClazzAclServiceImpl.grayscale={"sql":100,"rpc":0}`

#### 6.2 SpringBasedDiffBeanConfiguration 配置规则

**规则**：
```
{CONFIG_KEY_PRE}{first.getClass().getSimpleName()}.enable=true
```

**说明**：
- CONFIG_KEY_PRE：配置类中定义的常量值
- first.getClass().getSimpleName()：老实现类的简单类名（不是接口名）
- enable：固定后缀
- 值：true 表示启用新实现，false 表示使用老实现

**示例**：
- 配置类：ReplaceSubClazzDiffConfiguration
- CONFIG_KEY_PRE = "student.center.replace.diff."
- first = SubClazzAclServiceImpl
- 生成的配置：`student.center.replace.diff.SubClazzAclServiceImpl.enable=true`

**注意**：配置 key 中的类名必须是 first 参数的类名（老实现类名），不是接口名。

### 7. 输出要求

1. 列出所有 SpringBasedBalancerConfiguration 配置类的完整信息（类名、CONFIG_KEY_PRE、Bean 方法、参数类型等）
2. 列出所有 SpringBasedDiffBeanConfiguration 配置类的完整信息
3. 列出所有实现类的映射关系（接口、Impl、V1Impl），**注意 V1Impl 继承 Impl**
4. 列出所有 FeignClient 的映射关系（com.gaotu.client.feign 接口、Adapter），**注意不需要创建 V1Adapter**
5. 列出所有使用 name = "XXX.GAOTU100.COM" 格式的 @FeignClient
6. 生成完整的 Apollo 配置列表（按配置规则生成）
7. 对于目标项目改造，提供具体的代码模板和步骤说明（包括普通服务和 FeignClient 服务），**注意 V1Impl 继承 Impl，不创建 V1Adapter**
8. 说明扫描包配置的注意事项
```

---

## Apollo 配置生成规则和示例

### 规则说明

#### SpringBasedBalancerConfiguration 配置规则
```
格式：{CONFIG_KEY_PRE}{Impl类名}.grayscale={"sql":100,"rpc":0}
```

**生成步骤**：
1. 取配置类中的 `CONFIG_KEY_PRE` 常量值
2. 取 `@Bean` 方法中 `first` 参数的类名（使用 `getSimpleName()`）
3. 拼接格式：`{CONFIG_KEY_PRE}{类名}.grayscale={"sql":100,"rpc":0}`

**示例**：
- 配置类：`SubclazzAclServiceBalancerBeanConfiguration`
- CONFIG_KEY_PRE = `"fairy.balancer."`
- first = `SubclazzAclServiceImpl`
- 生成：`fairy.balancer.SubclazzAclServiceImpl.grayscale={"sql":100,"rpc":0}`

#### SpringBasedDiffBeanConfiguration 配置规则
```
格式：{CONFIG_KEY_PRE}{Impl类名}.enable=true
```

**生成步骤**：
1. 取配置类中的 `CONFIG_KEY_PRE` 常量值
2. 取 `@Bean` 方法中 `first` 参数的类名（使用 `getSimpleName()`）
3. 拼接格式：`{CONFIG_KEY_PRE}{类名}.enable=true`

**示例**：
- 配置类：`SubclazzAclServiceDiffBeanConfiguration`
- CONFIG_KEY_PRE = `"fairy.diff."`
- first = `SubclazzAclServiceImpl`
- 生成：`fairy.diff.SubclazzAclServiceImpl.enable=true`

### 完整 Apollo 配置示例

#### Fairy 项目配置

**Balancer 配置（灰度）**：
```
fairy.balancer.SubclazzAclServiceImpl.grayscale={"sql":100,"rpc":0}
fairy.balancer.SkuAclServiceImpl.grayscale={"sql":100,"rpc":0}
fairy.balancer.ParentsMeetingAclServiceImpl.grayscale={"sql":100,"rpc":0}
fairy.balancer.CourseAclServiceImpl.grayscale={"sql":100,"rpc":0}
fairy.balancer.ClazzLessonAclServiceImpl.grayscale={"sql":100,"rpc":0}
fairy.balancer.ClazzAclServiceImpl.grayscale={"sql":100,"rpc":0}
```

**Diff 配置（功能开关）**：
```
fairy.diff.SubclazzAclServiceImpl.enable=true
fairy.diff.SkuAclServiceImpl.enable=true
fairy.diff.ParentsMeetingAclServiceImpl.enable=true
fairy.diff.CourseAclServiceImpl.enable=true
fairy.diff.ClazzLessonAclServiceImpl.enable=true
fairy.diff.ClazzAclServiceImpl.enable=true
```

#### Student-Center 项目配置

**Balancer 配置（灰度）**：
```
student.center.replace.balancer.OldCourseService.grayscale={"sql":100,"rpc":0}
student.center.replace.balancer.SubClazzAclServiceImpl.grayscale={"sql":100,"rpc":0}
student.center.replace.balancer.CourseAclServiceImpl.grayscale={"sql":100,"rpc":0}
student.center.replace.balancer.ClazzLessonAclServiceImpl.grayscale={"sql":100,"rpc":0}
student.center.replace.balancer.ClazzAclServiceImpl.grayscale={"sql":100,"rpc":0}
```

**Diff 配置（功能开关）**：
```
student.center.replace.diff.OldCourseService.enable=true
student.center.replace.diff.SubClazzAclServiceImpl.enable=true
student.center.replace.diff.CourseAclServiceImpl.enable=true
student.center.replace.diff.ClazzLessonAclServiceImpl.enable=true
student.center.replace.diff.ClazzAclServiceImpl.enable=true
```

### 扫描包配置示例

```java
@SpringBootApplication(
    scanBasePackages = {
        "com.gaotu.crm",  // 项目主包
        "com.gaotu.student.data.gaia",  // 其他需要扫描的包
        "com.gaotu.blocks.starter"  // 必须包含，用于扫描配置类
    }
)
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**注意事项**：
- 必须包含 `"com.gaotu.blocks.starter"` 才能扫描到配置类
- 如果配置类在主包下，主包通常已在扫描范围内
- 确保所有配置类所在的包都在扫描范围内
- 如果使用 FeignClient，确保 @EnableFeignClients 的 basePackages 包含相应的包路径
- **V1Impl 继承 Impl，不需要实现接口**
- **不需要创建 V1Adapter，V1Impl 使用原有的 Adapter**
- 找到替换的FeignClient的使用的可替换的所有地方, 都用ACL类替换 ,没有的接口就创建接口 ,能复用的接口就复用原来的
```