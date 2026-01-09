  
找出所有位于 `com.gaotu.client.feign` 包下的 FeignClient 接口 和 *name 为"COURSE-SETTING.GAOTU100.COM"的FeignClient   增加 pringBasedBalancerConfiguration 和 SpringBasedDiffBeanConfiguration 的配置类 
  
## 依赖说明  
  
项目依赖：  
```xml  
<dependency>    
    <groupId>com.gaotu</groupId>    
    <artifactId>blocks-tools-starter</artifactId>    
    <version>2.0.3</version>    
</dependency>  

<dependency>  
    <groupId>org.apache.commons</groupId>  
    <artifactId>commons-lang3</artifactId>  
    <version>3.8.1</version>  
</dependency>
```  
  
这两个基类来自 blocks-tools-starter：  
- `com.gaotu.blocks.starter.diff.SpringBasedDiffBeanConfiguration`  
- `com.gaotu.blocks.starter.balancer.SpringBasedBalancerConfiguration`  
检查commons-lang3包是否存在 如果包版本低于3.8.1, 改为3.8.1,  高于3.8.1则不用修改
**不需要生成分析报告，不需要生成 md 文件，直接改造代码。**  
  
## 1. 配置类结构（解决循环依赖的关键）  
  
### 1.1 SpringBasedBalancerConfiguration 配置类模式  
  
**关键点：必须在 @Bean 方法参数上使用 @Qualifier 注解，明确指定 Bean 名称，避免循环依赖问题。**  
  
配置类模板结构：  
```java  
/**  
 * Xxx服务 ACL Balancer 配置类  
 */  
@Configuration  
public class XxxBalancerBeanConfiguration extends SpringBasedBalancerConfiguration {  
    public static final String CONFIG_KEY_PRE = "xxx.balancer.";  
      
    @Resource(name = "xxxDiffProxy")  
    private XxxService xxxDiffProxy;  
      
    @Bean  
    @Primary  
    public XxxService xxxBalancer(  
            @Qualifier("xxxServiceImpl") XxxServiceImpl first,  
            @Qualifier("xxxServiceV1Impl") XxxServiceV1Impl second) {  
        return createGrayscaleProxy(xxxDiffProxy, second, XxxService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
    }  
}  
```  
  
**重要说明**：  
- 必须导入 `org.springframework.beans.factory.annotation.Qualifier`  
- `@Bean` 方法的 `first` 和 `second` 参数必须使用 `@Qualifier` 注解指定 Bean 名称  
- Bean 名称必须与实现类上的 `@Service` 和 `@Qualifier` 注解值完全一致  
- 这样可以避免 Spring 在解析依赖时的循环依赖问题  
  
### 1.2 SpringBasedDiffBeanConfiguration 配置类模式  
  
**关键点：同样需要在 @Bean 方法参数上使用 @Qualifier 注解。**  
  
配置类模板结构：  
```java  
/**  
 * Xxx服务 ACL Diff 配置类  
 */  
@Configuration  
public class XxxDiffBeanConfiguration extends SpringBasedDiffBeanConfiguration {  
    public static final String CONFIG_KEY_PRE = "xxx.diff.";  
      
    @Bean(name = "xxxDiffProxy")  
    public XxxService xxxDiffProxy(  
            @Qualifier("xxxServiceImpl") XxxServiceImpl first,  
            @Qualifier("xxxServiceV1Impl") XxxServiceV1Impl second) {  
        return createProxy(first, second, XxxService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
    }  
}  
```  
  
**重要说明**：  
- `@Bean` 方法的 `first` 和 `second` 参数必须使用 `@Qualifier` 注解  
- Bean 名称必须与实现类上的注解值完全一致  
  
## 2. 实现类关系  
  
### 2.1 接口定义  
- 接口名称：XxxService 或 XxxAclService  
- 接口包路径  
- 接口方法签名  
  
### 2.2 老实现类（Impl）  
  
**必须添加 @Qualifier 注解，Bean 名称用于配置类中的 @Qualifier 引用。**  
  
```java  
@Service("xxxServiceImpl")  
@Qualifier("xxxServiceImpl")  
public class XxxServiceImpl implements XxxService {  
    // 实现逻辑  
}  
```  
  
**关键点**：  
- `@Service` 注解必须指定 Bean 名称（如：`"xxxServiceImpl"`）  
- 必须添加 `@Qualifier` 注解，值与 `@Service` 中的名称一致  
- Bean 名称将用于配置类中的 `@Qualifier` 引用  
  
### 2.3 新实现类（V1Impl）  
  
**继承老实现类，同样需要添加 @Qualifier 注解。**  
  
```java  
@Service("xxxServiceV1Impl")  
@Qualifier("xxxServiceV1Impl")  
public class XxxServiceV1Impl extends XxxServiceImpl {  
    // V1Impl 继承 Impl，继续使用原有的 Adapter    // 可以重写特定方法实现新逻辑，或保持继承关系不变  
}  
```  
  
**关键点**：  
- **V1Impl 继承 Impl，而不是实现接口**  
- 必须添加 `@Service("xxxServiceV1Impl")` 和 `@Qualifier("xxxServiceV1Impl")`  
- Bean 名称将用于配置类中的 `@Qualifier` 引用  
  
## 3. FeignClient 改造范围  
  
### 3.1 FeignClient 结构  
  
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
  
### 3.2 FeignClient 改造模式  
  
**重要原则**：  
1. **不需要创建 V1Adapter**，V1Impl 使用原有的 Adapter  
2. V1Impl 继承 Impl，继续使用原 Adapter  
3. 配置类中使用 @Qualifier 明确指定 Bean 依赖  
  
**完整示例**：  
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
  
// 3. 老实现 - 必须添加 @Qualifier@Service("skuAclServiceImpl")  
@Qualifier("skuAclServiceImpl")  
public class SkuAclServiceImpl implements SkuAclService {  
    @Resource  
    private ISkuServiceAdapter skuServiceAdapter;  
      
    @Override  
    public SkuVO getSkuInfo(Long skuId) {  
        return skuServiceAdapter.getSkuInfo(skuId);  
    }  
}  
  
// 4. 新实现 - 继承 Impl，使用相同的 Adapter，必须添加 @Qualifier@Service("skuAclServiceV1Impl")  
@Qualifier("skuAclServiceV1Impl")  
public class SkuAclServiceV1Impl extends SkuAclServiceImpl {  
    // 继承父类的 skuServiceAdapter，无需重新注入  
    // 可以重写特定方法实现新逻辑，或保持继承关系不变  
}  
  
// 5. Diff 配置 - 关键：使用 @Qualifier 明确指定 Bean@Configuration  
public class SkuAclServiceDiffBeanConfiguration extends SpringBasedDiffBeanConfiguration {  
    public static final String CONFIG_KEY_PRE = "task.center.diff.";  
      
    @Bean(name = "skuAclServiceDiffProxy")  
    public SkuAclService skuAclServiceDiffProxy(  
            @Qualifier("skuAclServiceImpl") SkuAclServiceImpl first,  
            @Qualifier("skuAclServiceV1Impl") SkuAclServiceV1Impl second) {  
        return createProxy(first, second, SkuAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
    }  
}  
  
// 6. Balancer 配置 - 关键：使用 @Qualifier 明确指定 Bean@Configuration  
public class SkuAclServiceBalancerBeanConfiguration extends SpringBasedBalancerConfiguration {  
    public static final String CONFIG_KEY_PRE = "task.center.balancer.";  
      
    @Resource(name = "skuAclServiceDiffProxy")  
    private SkuAclService skuAclServiceDiffProxy;  
      
    @Bean  
    @Primary  
    public SkuAclService skuAclService(  
            @Qualifier("skuAclServiceImpl") SkuAclServiceImpl first,  
            @Qualifier("skuAclServiceV1Impl") SkuAclServiceV1Impl second) {  
        return createGrayscaleProxy(skuAclServiceDiffProxy, second, SkuAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
    }  
}  
```  
  
## 4. 改造步骤（完整流程）  
  
### 步骤1：为现有实现类添加 @Qualifier 注解  
  
**必须为所有现有的 Impl 类添加 @Qualifier 注解**：  
  
```java  
// 修改前  
@Service  
public class XxxServiceImpl implements XxxService {  
    // ...}  
  
// 修改后  
@Service("xxxServiceImpl")  
@Qualifier("xxxServiceImpl")  
public class XxxServiceImpl implements XxxService {  
    // ...}  
```  
  
### 步骤2：创建 V1Impl 实现类  
  
```java  
@Service("xxxServiceV1Impl")  
@Qualifier("xxxServiceV1Impl")  
public class XxxServiceV1Impl extends XxxServiceImpl {  
    // V1Impl 继承 Impl，继续使用原有的 Adapter    // 可以重写特定方法实现新逻辑，或保持继承关系不变  
}  
```  
  
### 步骤3：创建 Diff 配置类  
  
**关键：方法参数必须使用 @Qualifier 注解**  
  
```java  
import org.springframework.beans.factory.annotation.Qualifier;  
  
@Configuration  
public class XxxServiceDiffBeanConfiguration extends SpringBasedDiffBeanConfiguration {  
    public static final String CONFIG_KEY_PRE = "task.center.diff.";  
  
    @Bean(name = "xxxServiceDiffProxy")  
    public XxxService xxxServiceDiffProxy(  
            @Qualifier("xxxServiceImpl") XxxServiceImpl first,  
            @Qualifier("xxxServiceV1Impl") XxxServiceV1Impl second) {  
        return createProxy(first, second, XxxService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
    }  
}  
```  
  
### 步骤4：创建 Balancer 配置类  
  
**关键：方法参数必须使用 @Qualifier 注解**  
  
```java  
import org.springframework.beans.factory.annotation.Qualifier;  
  
@Configuration  
public class XxxServiceBalancerBeanConfiguration extends SpringBasedBalancerConfiguration {  
    public static final String CONFIG_KEY_PRE = "task.center.balancer.";  
  
    @Resource(name = "xxxServiceDiffProxy")  
    private XxxService xxxServiceDiffProxy;  
  
    @Bean  
    @Primary  
    public XxxService xxxService(  
            @Qualifier("xxxServiceImpl") XxxServiceImpl first,  
            @Qualifier("xxxServiceV1Impl") XxxServiceV1Impl second) {  
        return createGrayscaleProxy(xxxServiceDiffProxy, second, XxxService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
    }  
}  
```  
  
### 步骤5：更新 pom.xml 添加依赖  
  
```xml  
<dependency>  
    <groupId>com.gaotu</groupId>  
    <artifactId>blocks-tools-starter</artifactId>  
    <version>2.0.3</version>  
</dependency>  
```  
  
### 步骤6：更新扫描包配置  
  
在 `@SpringBootApplication` 中添加扫描包：  
  
```java  
@SpringBootApplication(  
    scanBasePackages = {  
        "com.gaotu.yunying.task.center",  // 项目主包  
        "com.gaotu.yunying.gaia.center.api",  // 其他需要扫描的包  
        "com.gaotu.blocks.starter"  // 必须包含，用于扫描配置类  
    }  
)  
public class TaskCenterApplication {  
    // ...}  
```  
  
## 5. 解决循环依赖的关键点总结  
  
### 问题原因  
当 Spring 容器在创建 Bean 时，如果配置类的 @Bean 方法参数没有明确指定要注入的 Bean 名称，Spring 可能会尝试通过类型匹配来解析依赖，这可能导致循环依赖问题。  
  
### 解决方案  
**在配置类的 @Bean 方法参数上使用 @Qualifier 注解，明确指定要注入的 Bean 名称。**  
  
### 必须遵循的规则  
  
1. **实现类必须添加 @Qualifier 注解**：  
   ```java  
   @Service("xxxServiceImpl")  
   @Qualifier("xxxServiceImpl")  // 必须添加  
   public class XxxServiceImpl implements XxxService {  
   }  
   ```  
  
2. **配置类方法参数必须使用 @Qualifier**：  
   ```java  
   @Bean  
   public XxxService xxxService(  
           @Qualifier("xxxServiceImpl") XxxServiceImpl first,  // 必须使用 @Qualifier           @Qualifier("xxxServiceV1Impl") XxxServiceV1Impl second) {  // 必须使用 @Qualifier       // ...   }  
   ```  
  
3. **Bean 名称必须完全一致**：  
   - 实现类上的 `@Service("xxxServiceImpl")` 中的名称  
   - 实现类上的 `@Qualifier("xxxServiceImpl")` 中的名称  
   - 配置类中 `@Qualifier("xxxServiceImpl")` 中的名称  
   - 这三个名称必须完全一致（区分大小写）  
  
## 6. Apollo 配置生成规则  
  
### 6.1 SpringBasedBalancerConfiguration 配置规则  
  
**规则**：  
```  
{CONFIG_KEY_PRE}{first.getClass().getSimpleName()}.grayscale={"sql":100,"rpc":0}  
```  
  
**说明**：  
- CONFIG_KEY_PRE：配置类中定义的常量值  
- first.getClass().getSimpleName()：老实现类的简单类名（不是接口名）  
- grayscale：固定后缀  
- 值格式：{"sql":100,"rpc":0}  
  
**示例**：  
- 配置类：`IPeriodAclServiceBalancerBeanConfiguration`  
- CONFIG_KEY_PRE = `"task.center.balancer."`  
- first = `IPeriodAclServiceImpl`  
- 生成的配置：`task.center.balancer.IPeriodAclServiceImpl.grayscale={"sql":100,"rpc":0}`  
  
### 6.2 SpringBasedDiffBeanConfiguration 配置规则  
  
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
- 配置类：`IPeriodAclServiceDiffBeanConfiguration`  
- CONFIG_KEY_PRE = `"task.center.diff."`  
- first = `IPeriodAclServiceImpl`  
- 生成的配置：`task.center.diff.IPeriodAclServiceImpl.enable=true`  
  
## 7. 完整改造检查清单  
  
- [ ] 找到所有 `com.gaotu.client.feign` 包下的 FeignClient 接口  
- [ ] 找到所有 `name = "XXX.GAOTU100.COM"` 格式的 @FeignClient  
- [ ] 为现有 Impl 类添加 `@Service("xxxServiceImpl")` 和 `@Qualifier("xxxServiceImpl")`  
- [ ] 创建 V1Impl 类，继承 Impl，添加 `@Service("xxxServiceV1Impl")` 和 `@Qualifier("xxxServiceV1Impl")`  
- [ ] 创建 Diff 配置类，方法参数使用 `@Qualifier` 注解  
- [ ] 创建 Balancer 配置类，方法参数使用 `@Qualifier` 注解  
- [ ] 在 pom.xml 中添加 `blocks-tools-starter` 依赖  
- [ ] 在 `@SpringBootApplication` 中添加 `"com.gaotu.blocks.starter"` 到 `scanBasePackages`  
- [ ] 验证所有 Bean 名称的一致性（@Service、@Qualifier、配置类中的 @Qualifier）  
- [ ] 生成 Apollo 配置列表  
  
## 8. 注意事项  
  
1. **循环依赖解决**：必须使用 @Qualifier 明确指定 Bean 名称，这是解决循环依赖的关键  
2. **Bean 名称一致性**：确保 @Service、@Qualifier 和配置类中的 @Qualifier 名称完全一致  
3. **V1Impl 继承关系**：V1Impl 继承 Impl，不实现接口  
4. **不需要创建 V1Adapter**：V1Impl 使用原有的 Adapter  
5. **包路径**：确保导入正确的包路径  
   - `com.gaotu.blocks.starter.diff.SpringBasedDiffBeanConfiguration`  
   - `com.gaotu.blocks.starter.balancer.SpringBasedBalancerConfiguration`  
6. **扫描包配置**：必须包含 `"com.gaotu.blocks.starter"` 才能扫描到配置类  
  
## 9. 常见错误避免  
  
1. **错误**：配置类方法参数没有使用 @Qualifier  
   ```java  
   // 错误示例  
   public XxxService xxxService(XxxServiceImpl first, XxxServiceV1Impl second) {  
   }  
     
   // 正确示例  
   public XxxService xxxService(  
           @Qualifier("xxxServiceImpl") XxxServiceImpl first,  
           @Qualifier("xxxServiceV1Impl") XxxServiceV1Impl second) {  
   }  
   ```  
  
2. **错误**：实现类没有添加 @Qualifier  
   ```java  
   // 错误示例  
   @Service  
   public class XxxServiceImpl implements XxxService {  
   }  
     
   // 正确示例  
   @Service("xxxServiceImpl")  
   @Qualifier("xxxServiceImpl")  
   public class XxxServiceImpl implements XxxService {  
   }  
   ```  
  
3. **错误**：Bean 名称不一致  
   ```java  
   // 错误示例：名称不一致  
   @Service("xxxServiceImpl")  
   @Qualifier("xxxService")  // 名称不一致  
   // 正确示例：名称一致  
   @Service("xxxServiceImpl")  
   @Qualifier("xxxServiceImpl")  // 名称一致  
   ```