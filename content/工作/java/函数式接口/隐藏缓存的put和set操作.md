

```java
public class CacheUtil {  
  
    private final static Cache<String, Supplier<?>> caffeineCache = Caffeine.newBuilder()  
            .softValues()  
            // 设置最后一次写入或访问后经过固定时间过期  
            .expireAfterWrite(60, TimeUnit.SECONDS)  
            .initialCapacity(100)  
            // 缓存的最大条数  
            .maximumSize(10000)  
            .build();  
  
    @SuppressWarnings("unchecked")  
    public static   <T,U> U  getCacheByKey(String key, Supplier<T> generatorCache, Function<T,U> hasCacheConsumer) {  
        String intern = key.intern();  
        Supplier<T>  value = (Supplier<T>) caffeineCache.getIfPresent(intern);  
        T t;  
        if (value == null) {  
            synchronized (intern.intern()) {  
                if ((value = (Supplier<T>) caffeineCache.getIfPresent(intern)) == null) {  
                    t = generatorCache.get();  
                    T finalT = t;  
                    caffeineCache.put(intern, value = () -> finalT);  
                }  
            }  
        }  
        return hasCacheConsumer.apply(value.get());  
    }  
  
  
    public static  <T> T getCacheByKey(String key, Supplier<T> generatorCache) {  
        return getCacheByKey(key,generatorCache,Function.identity());  
    }  
    private final static Cache<String, Object> caffeineCache1 = Caffeine.newBuilder()  
        .softValues()  
        // 设置最后一次写入或访问后经过固定时间过期  
        .expireAfterWrite(60, TimeUnit.SECONDS)  
        .initialCapacity(100)  
        // 缓存的最大条数  
        .maximumSize(10000)  
        .build();
    @SuppressWarnings("unchecked")  
public static   <T,U> U  getCacheByKey1(String key, Supplier<T> generatorCache, Function<T,U> hasCacheConsumer) {  
    String intern = key.intern();  
    T  value = (T) caffeineCache1.getIfPresent(intern);  
    if (value == null) {  
        synchronized (intern.intern()) {  
            if ((value = (T) caffeineCache1.getIfPresent(intern)) == null) {  
                caffeineCache1.put(intern, value = generatorCache.get());  
            }  
        }  
    }  
    return hasCacheConsumer.apply(value);  
}
  
}
```
