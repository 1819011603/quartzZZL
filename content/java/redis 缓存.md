

```

  
import com.google.common.collect.Lists;  
import lombok.extern.slf4j.Slf4j;  
import org.springframework.beans.factory.annotation.Autowired;  
import org.springframework.beans.factory.annotation.Value;  
import org.springframework.data.redis.core.RedisCallback;  
import org.springframework.data.redis.core.RedisTemplate;  
import org.springframework.data.redis.serializer.RedisSerializer;  
import org.springframework.stereotype.Component;  
import org.springframework.util.CollectionUtils;  
  
import javax.annotation.PostConstruct;  
import java.util.*;  
import java.util.concurrent.SynchronousQueue;  
import java.util.concurrent.ThreadPoolExecutor;  
import java.util.concurrent.TimeUnit;  
import java.util.function.Function;  
import java.util.stream.Collectors;  
import java.util.stream.IntStream;  
  
/**  
 * @author: zhangzeling  
 * @date: 2025/6/19  
 * @description: RedisCacheUtil  
 */@Component  
@Slf4j  
public class RedisCacheUtil {  
    private static RedisTemplate<String, Object> redisTemplate;  
    private static ThreadPoolExecutor setCacheThreadPoolExecutor;  
    private static Integer batchSize;  
    private static Boolean usePipeline;  
    private static Boolean cacheSwitch;  
    @Value("${redis.cache.setCacheThreadPoolExecutor.max.pool.size:3}")  
    private Integer maxSize;  
    @Value("${redis.cache.setCacheThreadPoolExecutor.core.pool.size:3}")  
    private Integer coreSize;  
    @Value("${redis.cache.setCacheThreadPoolExecutor.keepAliveTime:60}")  
    private Integer keepAliveTime;  
  
    public static <T, U> List<T> listByKeysCache(  
            List<U> keys,  
            Function<List<U>, List<T>> loader,  
            Class<T> clazz,  
            String keyPattern,  
            long cacheTime,  
            TimeUnit timeUnit  
    ) {  
        return listByKeysCache(keys, loader, keyPattern, cacheTime, timeUnit, false);  
    }  
  
    public static <T, U> List<T> listByKeysCache(  
            List<U> keys,  
            Function<List<U>, List<T>> loader,  
            String keyPattern,  
            long cacheTime,  
            TimeUnit timeUnit  
    ) {  
        return listByKeysCache(keys, loader, keyPattern, cacheTime, timeUnit, false);  
    }  
  
  
    public static <T, U> List<T> listByKeysCacheForceUpdate(  
            List<U> keys,  
            Function<List<U>, List<T>> loader,  
            String keyPattern,  
            long cacheTime,  
            TimeUnit timeUnit  
    ) {  
        return listByKeysCache(keys, loader, keyPattern, cacheTime, timeUnit, true);  
    }  
  
    /**  
     * 通用缓存加载框架  
     * loader 每个U产生的T的顺序要一一对应才可以使用  
     *  
     * @param <T> 返回对象类型  
     * @param <U> Key 类型（比如 Long,String 等）  
     */  
    private static <T, U> List<T> listByKeysCache(  
            List<U> keys,  
            Function<List<U>, List<T>> loader,  
            String keyPattern,  
            long cacheTime,  
            TimeUnit timeUnit,  
            boolean forceUpdate  
    ) {  
        if (CollectionUtils.isEmpty(keys)) {  
            return Collections.emptyList();  
        }  
        // 不走缓存，直接调用 loader        if (cacheTime <= 0L || !cacheSwitch) {  
            return loader.apply(keys);  
        }  
  
        // 1. 先从 Redis 批量读  
        List<String> redisKeys = keys.stream()  
                .map(k -> String.format(keyPattern, k))  
                .collect(Collectors.toList());  
        List<T> cachedJsons =  Collections.emptyList();  
        try {  
            cachedJsons = forceUpdate ? Collections.emptyList() : ((RedisTemplate<String, T>)redisTemplate).opsForValue().multiGet(redisKeys);  
        } catch (Exception ignored) {  
        }        if (cachedJsons == null) {  
            cachedJsons = Collections.emptyList();  
        }  
  
        // 2. 反序列化 + 找出漏掉的 keys        Map<U, T> resultMap = new LinkedHashMap<>(keys.size());  
        List<U> missingKeys = new ArrayList<>();  
        T json;  
        for (int i = 0; i < keys.size(); i++) {  
            U k = keys.get(i);  
            if (i < cachedJsons.size() && (json = cachedJsons.get(i)) != null) {  
                try {  
                    resultMap.put(k, json);  
                } catch (Exception e) {  
                    missingKeys.add(k);  
                }  
            } else {  
                missingKeys.add(k);  
            }  
        }  
  
        // 3. 对漏掉的 keys 调用 loader，再写入缓存  
        if (!missingKeys.isEmpty()) {  
            List<T> loaded = loader.apply(missingKeys);  
            if (loaded == null || loaded.size() != missingKeys.size()) {  
                log.error("Loader 返回结果数量与缺失 key 数量不一致, 不能走缓存 重新获取, missingKeys: {}", missingKeys);  
                return loader.apply(keys);  
            }  
            // 用 keyExtractor 把它们放到 resultMap，并写缓存  
            for (int i = 0; i < missingKeys.size(); i++) {  
                U k = missingKeys.get(i);  
                T obj = loaded.get(i);  
                resultMap.put(k, obj);  
            }  
  
            // 写入redis  
            batchSetCache(missingKeys, loaded, keyPattern, cacheTime, timeUnit);  
        }  
  
        // 4. 保持原 keys 顺序返回 List<T>        return keys.stream()  
                .map(resultMap::get)  
                .collect(Collectors.toList());  
    }  
  
    /**  
     * 批量设置缓存 - 优化版本  
     */  
    public static <T, U> void batchSetCache(List<U> keys, List<T> values, String keyPattern,  
                                            long cacheTime, TimeUnit timeUnit) {  
        if (CollectionUtils.isEmpty(keys) || CollectionUtils.isEmpty(values) || keys.size() != values.size()) {  
            return;  
        }  
  
        // 分批处理，避免单次操作数据量过大  
        Lists.partition(IntStream.range(0, keys.size()).boxed().collect(Collectors.toList()), batchSize)  
                .forEach(batch -> {  
                    if (usePipeline && batch.size() > 1) {  
                        batchSetWithPipeline(keys, values, batch, keyPattern, cacheTime, timeUnit);  
                    } else {  
                        batchSetWithConcurrency(keys, values, batch, keyPattern, cacheTime, timeUnit);  
                    }  
                });  
    }  
  
    /**  
     * 使用Pipeline批量设置  
     */  
    private static <T, U> void batchSetWithPipeline(List<U> keys, List<T> values, List<Integer> indices,  
                                                    String keyPattern, long cacheTime, TimeUnit timeUnit) {  
        try {  
            RedisTemplate<String, T> template = ((RedisTemplate<String, T>)redisTemplate);  
            RedisSerializer<String> keySerializer = (RedisSerializer<String>) template.getKeySerializer();  
            RedisSerializer<T> valueSerializer = (RedisSerializer<T>) template.getValueSerializer();  
            template.executePipelined((RedisCallback<Object>) connection -> {  
                indices.forEach(i -> {  
                    try {  
                        String key = String.format(keyPattern, keys.get(i));  
                        T object = values.get(i);  
                        byte[] k = keySerializer.serialize(key);  
                        byte[] v = valueSerializer.serialize(object);  
                        if (k == null || v == null) {  
                            return;  
                        }  
                        if (cacheTime > 0) {  
                            connection.setEx(k, timeUnit.toSeconds(cacheTime), v);  
                        } else {  
                            connection.set(k, v);  
                        }  
                    } catch (Exception e) {  
                        log.error("Pipeline set cache error for index: {}", i, e);  
                    }  
                });  
                return null;  
            });  
        } catch (Exception e) {  
            log.error("Pipeline batch set cache error", e);  
            // Pipeline失败时降级为并发处理  
            batchSetWithConcurrency(keys, values, indices, keyPattern, cacheTime, timeUnit);  
        }  
    }  
  
    /**  
     * 使用并发批量设置（原有方式的优化版本）  
     */  
    private static <T, U> void batchSetWithConcurrency(List<U> keys, List<T> values, List<Integer> indices,  
                                                       String keyPattern, long cacheTime, TimeUnit timeUnit) {  
        CompletableFutureUtils.runAsyncWithIndex(  
                indices, setCacheThreadPoolExecutor, (idx, i) -> {  
                    try {  
                        U key = keys.get(i);  
                        T obj = values.get(i);  
                        ((RedisTemplate<String, T>)redisTemplate).opsForValue()  
                                .set(String.format(keyPattern, key), obj, cacheTime, timeUnit);  
                    } catch (Exception e) {  
                        log.error("Concurrent set cache error for key: {}", keys.get(i), e);  
                    }  
                }  
        );  
    }  
  
    @PostConstruct  
    public void init() {  
        setCacheThreadPoolExecutor = new ThreadPoolExecutor(coreSize, maxSize, keepAliveTime, TimeUnit.SECONDS, new SynchronousQueue<>(),  
                new ThreadPoolExecutor.CallerRunsPolicy());  
        setCacheThreadPoolExecutor.allowCoreThreadTimeOut(true);  
    }  
  
    @Value("${redis.cache.batch.size:200}")  
    public void setBatchSize(Integer batchSize) {  
        RedisCacheUtil.batchSize = batchSize;  
    }  
  
    @Value("${redis.cache.use.pipeline:false}")  
    public void setUsePipeline(Boolean usePipeline) {  
        RedisCacheUtil.usePipeline = usePipeline;  
    }  
    @Value("${redis.cache.use.cacheSwitch:false}")  
    public void setCacheSwitch(Boolean cacheSwitch) {  
        RedisCacheUtil.cacheSwitch = cacheSwitch;  
    }  
  
    @Autowired  
    public void setRedisTemplate(RedisTemplate<String, Object> redisTemplate) {  
        RedisCacheUtil.redisTemplate = redisTemplate;  
    }  
  
  
}
```