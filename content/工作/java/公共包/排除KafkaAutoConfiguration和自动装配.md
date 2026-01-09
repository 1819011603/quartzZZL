
@EnableAutoConfiguration(exclude = {KafkaAutoConfiguration.class})  进行排除

注意事项就是有没有可能会将原先需要kafka的排除掉了

```java

import org.springframework.boot.autoconfigure.EnableAutoConfiguration;  
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;  
import org.springframework.boot.autoconfigure.kafka.KafkaAutoConfiguration;  
import org.springframework.context.annotation.Conditional;  
import org.springframework.context.annotation.Configuration;  
import org.springframework.kafka.core.KafkaTemplate;  
  
/**  
 * @author: zhangzeling  
 * @date: 2024/10/28  
 * @description: KafkaAutoExcludeConfiguration  
 */
@EnableAutoConfiguration(exclude = {KafkaAutoConfiguration.class})  
@Configuration  
@Conditional(CustomKafkaCondition.class)  
@ConditionalOnMissingBean(KafkaTemplate.class)  
public class KafkaAutoExcludeConfiguration {  
}
```



组合条件解决

```java

import org.springframework.boot.autoconfigure.condition.ConditionOutcome;  
import org.springframework.boot.autoconfigure.condition.SpringBootCondition;  
import org.springframework.context.annotation.ConditionContext;  
import org.springframework.core.type.AnnotatedTypeMetadata;  
  
public class CustomKafkaCondition extends SpringBootCondition {  
  
    @Override  
    public ConditionOutcome getMatchOutcome(ConditionContext context, AnnotatedTypeMetadata metadata) {  
        // 从 ConditionContext 获取 Environment        Environment environment = context.getEnvironment();  
        String topic = environment.getProperty("wly.operation.log.kafka.topic");  
        String bootstrapServers = environment.getProperty("spring.kafka.bootstrap-servers");  
  
        // 检查条件  
        boolean isTopicMissing = (topic == null || topic.isEmpty());  
        boolean isBootstrapServerDifferent = !("localhost:9092".equals(bootstrapServers));  
  
        // 只有当两个条件同时满足时返回匹配  
        return new ConditionOutcome(isTopicMissing && isBootstrapServerDifferent, "Kafka conditions are met.");  
    }  
}
```


```java

import org.springframework.boot.autoconfigure.EnableAutoConfiguration;  
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;  
import org.springframework.boot.autoconfigure.kafka.KafkaAutoConfiguration;  
import org.springframework.context.annotation.Conditional;  
import org.springframework.context.annotation.Configuration;  
import org.springframework.kafka.core.KafkaTemplate;  
  
/**  
 * @author: zhangzeling  
 * @date: 2024/10/28  
 * @description: KafkaAutoExcludeConfiguration  
 */
@EnableAutoConfiguration(exclude = {KafkaAutoConfiguration.class})  
@Configuration  
@Conditional(CustomKafkaCondition.class)  
@ConditionalOnMissingBean(KafkaTemplate.class)  
public class KafkaAutoExcludeConfiguration {  
}
```





### 自动装配

https://blog.csdn.net/MaoTongBin/article/details/129411740


`TypeExcludeFilter` 是 Spring 框架中的一个过滤器类，主要用于在组件扫描时排除特定类型的类。它通常与 `@ComponentScan` 注解一起使用，帮助开发者定义哪些类不应该被 Spring 容器管理。


`AutoConfigurationExcludeFilter` 主要用于自动配置的排除。这意味着在 Spring Boot 的自动配置过程中，如果某个条件不满足，开发者可以通过此过滤器排除特定的自动配置类。

AutoConfigurationExcludeFilter类会扫描所有的EnableAutoConfiguration注解修饰的类, 获取所有的exclude和excludeName的类进行排除


### 总结

- **适用范围**: `AutoConfigurationExcludeFilter` 主要用于 Spring Boot 的自动配置，而 `TypeExcludeFilter` 则更广泛，适用于所有类型的组件扫描。
- **使用场景**: 当你需要控制自动配置类的加载时，使用 `AutoConfigurationExcludeFilter`；而当你需要在组件扫描中排除特定的类时，使用 `TypeExcludeFilter`。
- **实现方式**: `AutoConfigurationExcludeFilter` 通常通过 `@EnableAutoConfiguration` 的 `exclude` 属性使用，而 `TypeExcludeFilter` 通过 `@ComponentScan` 的 `excludeFilters` 属性来定义。





##### AutoConfigurationImportSelector








### ComponentScan注解的basePackages和basePackageClasses字段有什么区别

- **`basePackages`**: 适用于明确指定一个或多个包名进行扫描。
- **`basePackageClasses`**: 适用于通过类的存在间接指定包位置，能够使代码更具可维护性（因为类的位置不会随包的重命名而变化）。