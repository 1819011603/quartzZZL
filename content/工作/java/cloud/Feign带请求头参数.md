
1. 在Feign调用之前, 使用TransmittableThreadLocal将LinkTraceBean塞入ThreadLocal (使用HystrixConcurrencyStrategy策略实现)
2. 在Feign调用之前,使用RequestInterceptor拦截请求,  使用TransmittableThreadLocal获取LinkTraceBean, 将参数塞入请求体, 统一处理

3. 使用TransmittableThreadLocal

```java
import com.alibaba.ttl.TransmittableThreadLocal;  
import com.baijia.tongbao.bo.LinkTraceBean;  
  
import java.util.Map;  
  
/**  
 * @author: zhangzeling  
 * @date: 2024/7/29  
 * @description: CustomThreadLocalContext  
 */public class CustomFeignContext {  
    private static final ThreadLocal<LinkTraceBean> CUSTOM_VALUE_HOLDER = new TransmittableThreadLocal<>();  
  
    public static void setCustomValue(LinkTraceBean value) {  
        CUSTOM_VALUE_HOLDER.set(value);  
    }  
  
    public static LinkTraceBean getCustomValue() {  
        return CUSTOM_VALUE_HOLDER.get();  
    }  
  
    public static void clear() {  
        CUSTOM_VALUE_HOLDER.remove();  
    }  
}
```


2. HystrixPlugins 重新设置插件
这样能重新设置Runnable包装类
```java
import com.baijia.tongbao.utils.bean.FeignCallable;  
import com.netflix.hystrix.strategy.HystrixPlugins;  
import com.netflix.hystrix.strategy.concurrency.HystrixConcurrencyStrategy;  
import org.springframework.stereotype.Component;  
  
import java.util.concurrent.Callable;  
  
/**  
 * @author: zhangzeling  
 * @date: 2024/7/29  
 * @description: CustomHystrixConcurrencyStrategy  
 */@Component  
public class CustomHystrixConcurrencyStrategy extends HystrixConcurrencyStrategy {  
    private final HystrixConcurrencyStrategy existingConcurrencyStrategy;  
  
    public CustomHystrixConcurrencyStrategy() {  
        this.existingConcurrencyStrategy = HystrixPlugins.getInstance().getConcurrencyStrategy();  
        if (this.existingConcurrencyStrategy instanceof CustomHystrixConcurrencyStrategy) {  
            // 防止重复注册  
            return;  
        }  
        // 重置插件并注册新的并发策略  
        HystrixPlugins.reset();  
        HystrixPlugins.getInstance().registerConcurrencyStrategy(this);  
    }  
  
    @Override  
    public <T> Callable<T> wrapCallable(Callable<T> callable) {  
        return new FeignCallable<>(callable);  
    }  
}
```

3.  使用FeignCallable包装类记录线程上下文, finally中删除上下文信息

```java
import com.alibaba.ttl.TtlCallable;  
import com.baijia.tongbao.intecept.CustomFeignContext;  
  
import java.util.concurrent.Callable;  
  
/**  
 * @author: zhangzeling  
 * @date: 2024/7/29  
 * @description: CustomCallable  
 */public class FeignCallable<T> implements Callable<T> {  
    private final Callable<T> actual;  
  
    public FeignCallable(Callable<T> actual) {  
        this.actual = TtlCallable.get(actual);  
    }  
    @Override  
    public T call() throws Exception {  
        try {  
            // 执行实际的任务  
            return this.actual.call();  
        } finally {  
            CustomFeignContext.clear();  
        }  
    }  
}
```

4. 实现RequestInterceptor接口 拦截接口请求, 添加请求头.

```java
import com.baijia.tongbao.bo.LinkTraceBean;  
import feign.RequestInterceptor;  
import feign.RequestTemplate;  
import org.slf4j.Logger;  
import org.slf4j.LoggerFactory;  
import org.springframework.stereotype.Component;  
  
import java.util.Map;  
  
/**  
 * @author: zhangzeling  
 * @date: 2024/7/29  
 * @description: CustomFeignRequestInterceptor  
 */
@Component  
public class CustomFeignRequestInterceptor implements RequestInterceptor {  
    private static final Logger log = LoggerFactory.getLogger(CustomFeignRequestInterceptor.class);  
  
    @ApolloJsonValue("${feign.header.modify.paths:[\"/robotfacade/chat/sendSingleMsg\",\"/robotfacade/chat/sendRoomMsgSpecify\"]}") 
    private Set<String> modifyPaths;  
  
    @Override  
    public void apply(RequestTemplate template) {  
        Request request = template.request();  
        String url = request.url();  
        if (!modifyPaths.contains(url)) {  
            return;  
        }  
        LinkTraceBean customValue = CustomFeignContext.getCustomValue();  
        if (customValue == null) {  
            return;  
        }  
        log.info("CustomFeignRequestInterceptor {}", customValue);  
        template.header("sourceDesc", customValue.getSourceDesc());  
    }  
}
```

5. bean类
```java
import lombok.Builder;  
import lombok.Data;  
  
/**  
 * @author: zhangzeling  
 * @date: 2024/7/29  
 * @description: LinkTraceBean  
 */@Builder  
@Data  
public class LinkTraceBean {  
    private String sourceDesc;  
}
```