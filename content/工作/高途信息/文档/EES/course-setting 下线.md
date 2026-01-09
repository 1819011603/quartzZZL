https://docs.baijia.com/sheet/DQVhJV0RvTFJvcFlC?nlc=1&tab=000001

https://docs.baijia.com/sheet/DQUZub1F0TVJuU0NB?tab=000001


diff 日志:

2025-05-09 07:05:42.258 WARN [_**DefaultContentChecker**_:85][AdbCourseAclServiceImpl-diff-check-thread-1] - [TID: N/A] DIFF请求内容规则比对不一致 类：

```
// 对比新老接口有数据diff
"DefaultContentChecker" and __tag__:deployment: student-data
// 对比新老接口耗时
"DefaultCostTimeChecker" and __tag__:deployment: student-data
// 对比新接口是否有报错
"DefaultExceptionChecker" and __tag__:deployment: student-data
```


```

<dependency>  
    <groupId>com.gaotu</groupId>  
    <artifactId>blocks-tools-starter</artifactId>  
    <version>2.0.3</version>  
</dependency>



@SpringBootApplication(scanBasePackages = {"com.gaotu.crm", "com.gaotu.student.data.gaia", "com.gaotu.blocks.starter"},
```


```




```

最新的 



![[../../../壁纸/附件/AclServiceCompareController.java]]




![[../../../壁纸/附件/RedisCacheUtil.java]]


```
// 对于Map<U,T>类型参数，使用parseObject并保留原始类型  
// 创建一个ParameterizedTypeImpl来保留泛型信息  
Type mapType = new com.alibaba.fastjson.util.ParameterizedTypeImpl(  
    new Type[]{typeArgs[0], typeArgs[1]},   
    null,   
    Map.class);  
objects[i] = JSON.parseObject(JSONObject.toJSONString(params.get(i)), mapType);
```

```

按照ClazzAclServiceBalancerBeanConfiguration和ClazzAclServiceDiffBeanConfiguration 对等处理 IClazzCommerceService, 他们都有两个子类, 带有V1的是新的实现类, 每个接口分别创建一个 DiffBeanConfiguration和BalancerBeanConfiguration 生成两个子类 IClazzCommerceServiceImpl IClazzCommerceServiceV1Impl IClazzCommerceService 接口 替换为 com.gaotu.course.center.client.service.clazz.ClazzQueryApiFeignClient#listByNumbers
```


```
按照ClazzAclServiceBalancerBeanConfiguration和ClazzAclServiceDiffBeanConfiguration 对等处理 ClazzLessonAclService,CourseAclService,ParentsMeetingAclService,SubclazzAclServiceV1 他们都有两个子类, 带有V1的是新的实现类, 每个接口分别创建一个 DiffBeanConfiguration和BalancerBeanConfiguration 生成两个子类 名称后缀分别为ServiceImpl和ServiceV1Impl
```


```
com.gaotu.underlink.infrastructure.rpc.client.PeriodFeignClient 找到他所有的使用地方 创建一个AclService接口防腐层来实现他的功能 按照ClazzAclServiceBalancerBeanConfiguration和ClazzAclServiceDiffBeanConfiguration 对等处理  他们都有两个子类, 带有V1的是新的实现类(没有V1则复制一个), 每个接口分别创建一个 DiffBeanConfiguration和BalancerBeanConfiguration 生成两个子类 名称后缀分别为ServiceImpl和ServiceV1Impl

  
import com.gaotu.blocks.starter.balancer.SpringBasedBalancerConfiguration;  
import com.gaotu.subclazz.acl.ClazzAclService;  
import com.gaotu.subclazz.service.ClazzAclServiceImpl;  
import com.gaotu.subclazz.service.ClazzAclServiceV1Impl;  
import org.springframework.beans.factory.annotation.Qualifier;  
import org.springframework.context.annotation.Bean;  
import org.springframework.context.annotation.Configuration;  
import org.springframework.context.annotation.Primary;  
  
import javax.annotation.Resource;  
  
/**  
 * ClazzAclService的Balancer配置  
 * 管理ClazzAclServiceImpl(旧实现)到ClazzAclServiceV1Impl(新实现)的灰度切换  
 *   
* @author system  
 * @date 2024/12/17  
 */@Configuration  
public class ClazzAclServiceBalancerBeanConfiguration extends SpringBasedBalancerConfiguration {  
  
    public static final String CONFIG_KEY_PRE = "fairy.balancer.";  
  
    @Resource(name = "clazzAclServiceDiffProxy")  
    private ClazzAclService clazzAclServiceDiffProxy;  
  
    /**  
     * ClazzAclService的Balancer代理  
     * @param first 原方法 - ClazzAclServiceImpl  
     * @param second 新方法 - ClazzAclServiceV1Impl  
     * @return  
     */  
    @Bean  
    @Primary    public ClazzAclService clazzAclService(@Qualifier("clazzAclServiceImpl") ClazzAclServiceImpl first,  
                                           @Qualifier("clazzAclServiceV1Impl") ClazzAclServiceV1Impl second) {  
        return createGrayscaleProxy(clazzAclServiceDiffProxy, second, ClazzAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
    }  
}

  
import com.gaotu.blocks.starter.diff.SpringBasedDiffBeanConfiguration;  
import com.gaotu.subclazz.acl.ClazzAclService;  
import com.gaotu.subclazz.service.ClazzAclServiceImpl;  
import com.gaotu.subclazz.service.ClazzAclServiceV1Impl;  
import org.springframework.beans.factory.annotation.Qualifier;  
import org.springframework.context.annotation.Bean;  
import org.springframework.context.annotation.Configuration;  
  
@Configuration  
public class ClazzAclServiceDiffBeanConfiguration extends SpringBasedDiffBeanConfiguration {  
  
    public static final String CONFIG_KEY_PRE = "fairy.diff.";  
      
    /**  
     * ClazzAclService的Diff代理  
     * @param first 原方法 - ClazzAclServiceImpl  
     * @param second 新方法 - ClazzAclServiceV1Impl  
     * @return  
     */  
    @Bean(name = "clazzAclServiceDiffProxy")  
    public ClazzAclService clazzAclService(@Qualifier("clazzAclServiceImpl") ClazzAclServiceImpl first,  
                                           @Qualifier("clazzAclServiceV1Impl") ClazzAclServiceV1Impl second) {  
        return createProxy(first, second, ClazzAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
    }  
}
```

![[../../../壁纸/附件/Pasted image 20250725104722.png]]



```


import com.gaotu.blocks.starter.balancer.SpringBasedBalancerConfiguration;

import com.gaotu.reach.adapter.business.course.service.CourseAclService;
import com.gaotu.reach.adapter.business.course.service.impl.CourseAclServiceImpl;
import com.gaotu.reach.adapter.business.course.service.impl.CourseAclServiceV1Impl;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import javax.annotation.Resource;

/**
 * CourseAclService的Balancer配置
 * 管理CourseAclServiceImpl(旧实现)到CourseAclServiceV1Impl(新实现)的灰度切换
 * 
 * @author system
 * @date 2024/12/17
 */
@Configuration
public class CourseAclServiceBalancerBeanConfiguration extends SpringBasedBalancerConfiguration {

    public static final String CONFIG_KEY_PRE = "reach.service.balancer.";

    @Resource(name = "courseAclServiceDiffProxy")
    private CourseAclService courseAclServiceDiffProxy;

    /**
     * CourseAclService的Balancer代理
     * @param first 原方法 - CourseAclServiceImpl
     * @param second 新方法 - CourseAclServiceV1Impl
     * @return
     */
    @Bean
    @Primary
    public CourseAclService courseAclService(
            @Qualifier("courseAclServiceImpl") CourseAclServiceImpl first,
            @Qualifier("courseAclServiceV1Impl") CourseAclServiceV1Impl second) {
        return createGrayscaleProxy(courseAclServiceDiffProxy, second, CourseAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());
    }
}

import com.gaotu.blocks.starter.diff.SpringBasedDiffBeanConfiguration;
import com.gaotu.reach.adapter.business.course.service.CourseAclService;
import com.gaotu.reach.adapter.business.course.service.impl.CourseAclServiceImpl;
import com.gaotu.reach.adapter.business.course.service.impl.CourseAclServiceV1Impl;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * CourseAclService的Diff配置
 * 用于比较CourseAclServiceImpl(旧实现)和CourseAclServiceV1Impl(新实现)的差异
 * 
 * @author system
 * @date 2024/12/17
 */
@Configuration
public class CourseAclServiceDiffBeanConfiguration extends SpringBasedDiffBeanConfiguration {

    public static final String CONFIG_KEY_PRE = "reach.service.diff.";
    
    /**
     * CourseAclService的Diff代理
     * @param first 原方法 - CourseAclServiceImpl
     * @param second 新方法 - CourseAclServiceV1Impl
     * @return
     */
    @Bean(name = "courseAclServiceDiffProxy")
    public CourseAclService courseAclService(
            @Qualifier("courseAclServiceImpl") CourseAclServiceImpl first,
            @Qualifier("courseAclServiceV1Impl") CourseAclServiceV1Impl second) {
        return createProxy(first, second, CourseAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());
    }
}



现在使用的是com.gaotu.client.feign.IClazzService  麻烦常见一个防腐层方法 命名为ClazzAclService 再 按照CourseAclServiceBalancerBeanConfiguration和CourseAclServiceDiffBeanConfiguration 对等处理 ClazzAclService, 他们都有两个子类, 带有V1的是新的实现类, 每个接口分别创建一个 DiffBeanConfiguration和BalancerBeanConfiguration 
```




```

com.gaotu.client.feign.IClazzService 找到他所有的使用地方 创建一个ClazzAclService接口防腐层来实现他的功能 找到com.gaotu.client.feign下所有的类 都按照这个防腐层实现
麻烦将防腐层 如果报错 打印错误日志并抛出course-setting查询异常 打印出接口的请求参数 使用fastJson序列化对象打印
```








