package com.gaotu.linkup.wechat.pc.adapter.feign;

import com.alibaba.fastjson.JSONObject;
import com.google.common.collect.Lists;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisCallback;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.RedisSerializer;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

import java.util.*;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Collectors;

/**
 * Redis缓存工具类
 *
 * @author system
 * @date 2025/01/01
 */
@Slf4j
@Component
public class RedisCacheUtil {

    private static RedisTemplate<String, String> redisTemplate;
    private static ThreadPoolExecutor setCacheThreadPoolExecutor;
    private static Integer batchSize;
    private static Boolean usePipeline;
    private static Integer pipelineMinBatchSize;
    private static Boolean cacheSwitch;

    @Value("${redis.cache.batch.size:200}")
    public void setBatchSize(Integer batchSize) {
        RedisCacheUtil.batchSize = batchSize;
    }

    @Value("${redis.cache.use.pipeline:true}")
    public void setUsePipeline(Boolean usePipeline) {
        RedisCacheUtil.usePipeline = usePipeline;
    }

    @Value("${redis.cache.pipeline.min.batch.size:10}")
    public void setPipelineMinBatchSize(Integer pipelineMinBatchSize) {
        RedisCacheUtil.pipelineMinBatchSize = pipelineMinBatchSize;
    }

    @Value("${redis.cache.use.cacheSwitch:true}")
    public void setCacheSwitch(Boolean cacheSwitch) {
        RedisCacheUtil.cacheSwitch = cacheSwitch;
    }

    public static <T, U> List<T> listByKeysCache(
            List<U> keys,
            Function<List<U>, List<T>> loader,
            Function<T, U> keyMapper,
            String keyPrefixPattern,
            long cacheTime,
            TimeUnit timeUnit,
            Class<T> clazz) {
        try {
            return listByKeysCache(keys, loader, keyMapper, keyPrefixPattern, cacheTime, timeUnit, false, clazz);
        } catch (Exception e) {
            log.error("listByKeysCache error for keys: {}, error: {}", keys, e.getMessage(), e);
            return loader.apply(keys);
        }
    }

    public static <T, U> List<T> listByKeysCacheForForceUpdate(
            List<U> keys,
            Function<List<U>, List<T>> loader,
            Function<T, U> keyMapper,
            String keyPrefixPattern,
            long cacheTime,
            TimeUnit timeUnit,
            Class<T> clazz) {
        try {
            return listByKeysCache(keys, loader, keyMapper, keyPrefixPattern, cacheTime, timeUnit, true, clazz);
        } catch (Exception e) {
            log.error("listByKeysCacheForForceUpdate error for keys: {}, error: {}", keys, e.getMessage(), e);
            return loader.apply(keys);
        }
    }

    /**
     * 支持一个U生成List<T>的缓存方法，最后将所有结果合并到List<T>
     * loader接收List<U>批量加载，返回List<T>，通过keyMapper将T分组到对应的U下
     * 
     * @param keys             键列表
     * @param loader           批量加载函数，接收List<U>返回List<T>
     * @param keyMapper        从T中提取U的函数
     * @param keyPrefixPattern 缓存key前缀模式
     * @param cacheTime        缓存时间
     * @param timeUnit         时间单位
     * @param clazz            返回对象类型的Class，用于反序列化
     * @param <T>              返回对象类型
     * @param <U>              Key类型
     * @return 合并后的List<T>
     */
    public static <T, U> List<T> listByKeysCacheWithListLoader(
            List<U> keys,
            Function<List<U>, List<T>> loader,
            Function<T, U> keyMapper,
            String keyPrefixPattern,
            long cacheTime,
            TimeUnit timeUnit,
            Class<T> clazz) {
        try {
            return listByKeysCacheWithListLoader(keys, loader, keyMapper, keyPrefixPattern, cacheTime, timeUnit, false,
                    clazz);
        } catch (Exception e) {
            log.error("listByKeysCacheWithListLoader error for keys: {}, error: {}", keys, e.getMessage(), e);
            return loader.apply(keys);
        }
    }

    /**
     * 支持一个U生成List<T>的缓存方法（强制更新版本）
     */
    public static <T, U> List<T> listByKeysCacheWithListLoaderForForceUpdate(
            List<U> keys,
            Function<List<U>, List<T>> loader,
            Function<T, U> keyMapper,
            String keyPrefixPattern,
            long cacheTime,
            TimeUnit timeUnit,
            Class<T> clazz) {
        try {
            return listByKeysCacheWithListLoader(keys, loader, keyMapper, keyPrefixPattern, cacheTime, timeUnit, true,
                    clazz);
        } catch (Exception e) {
            log.error("listByKeysCacheWithListLoaderForForceUpdate error for keys: {}, error: {}", keys, e.getMessage(),
                    e);
            return loader.apply(keys);
        }
    }

    /**
     * 支持一个U生成List<T>的缓存加载框架
     * loader接收List<U>批量加载，返回List<T>，通过keyMapper将T分组到对应的U下
     * 每个U对应一个List<T>，最后合并所有结果
     *
     * @param <T>   返回对象类型
     * @param <U>   Key 类型（比如 Long,String 等）
     * @param clazz 返回对象类型的Class，用于反序列化
     */
    private static <T, U> List<T> listByKeysCacheWithListLoader(
            List<U> keys,
            Function<List<U>, List<T>> loader,
            Function<T, U> keyMapper,
            String keyPattern,
            long cacheTime,
            TimeUnit timeUnit,
            boolean forceUpdate,
            Class<T> clazz) {
        if (CollectionUtils.isEmpty(keys)) {
            return Collections.emptyList();
        }
        // 不走缓存，直接调用 loader
        if (cacheTime <= 0L || !Boolean.TRUE.equals(cacheSwitch)) {
            return loader.apply(keys);
        }

        // 1. 先从 Redis 批量读
        List<String> redisKeys = keys.stream()
                .map(k -> keyPattern + k)
                .collect(Collectors.toList());
        Map<U, List<T>> cachedMap = new HashMap<>();
        try {
            if (!forceUpdate) {
                List<String> stringList = redisTemplate.opsForValue().multiGet(redisKeys);
                if (CollectionUtils.isEmpty(stringList)) {
                    stringList = Collections.emptyList();
                }
                for (int i = 0; i < keys.size() && i < stringList.size(); i++) {
                    String str = stringList.get(i);
                    if (str != null) {
                        try {
                            List<T> parsed = JSONObject.parseArray(str, clazz);
                            if (!CollectionUtils.isEmpty(parsed)) {
                                cachedMap.put(keys.get(i), parsed);
                            }
                        } catch (Exception e) {
                            log.warn("解析缓存数据失败, str: {}, clazz: {}, error: {}", str, clazz.getName(), e.getMessage());
                        }
                    }
                }
            }
        } catch (Exception ignored) {
            log.warn("批量获取缓存失败, keys: {}", redisKeys);
        }

        // 2. 找出漏掉的 keys
        List<U> missingKeys = new ArrayList<>();
        for (U k : keys) {
            if (!cachedMap.containsKey(k)) {
                missingKeys.add(k);
            }
        }

        // 3. 批量加载缺失的数据
        if (!missingKeys.isEmpty()) {
            List<T> loaded = loader.apply(missingKeys);
            // 通过keyMapper将T分组到对应的U下
            Map<U, List<T>> loadedMap = new HashMap<>();
            for (T item : loaded) {
                if (item != null) {
                    U k = keyMapper.apply(item);
                    if (k != null) {
                        loadedMap.computeIfAbsent(k, key -> new ArrayList<>()).add(item);
                    }
                }
            }

            // 写入缓存并更新cachedMap
            for (U key : missingKeys) {
                List<T> list = loadedMap.get(key);
                if (list != null && !list.isEmpty()) {
                    cachedMap.put(key, list);
                    // 写入缓存
                    String redisKey = keyPattern + key;
                    String value = JSONObject.toJSONString(list);
                    try {
                        redisTemplate.opsForValue().set(redisKey, value, cacheTime, timeUnit);
                    } catch (Exception e) {
                        log.error("写入缓存失败, key: {}, error: {}", redisKey, e.getMessage(), e);
                    }
                }
            }
        }

        // 4. 合并所有结果返回
        return keys.stream()
                .flatMap(key -> {
                    List<T> list = cachedMap.get(key);
                    return list != null ? list.stream() : java.util.stream.Stream.empty();
                })
                .collect(Collectors.toList());
    }

    /**
     * 通用缓存加载框架
     * loader 每个U产生的T的顺序要一一对应才可以使用
     *
     * @param <T>   返回对象类型
     * @param <U>   Key 类型（比如 Long,String 等）
     * @param clazz 返回对象类型的Class，用于反序列化
     */
    private static <T, U> List<T> listByKeysCache(
            List<U> keys,
            Function<List<U>, List<T>> loader,
            Function<T, U> keyMapper,
            String keyPattern,
            long cacheTime,
            TimeUnit timeUnit,
            boolean forceUpdate,
            Class<T> clazz) {
        if (CollectionUtils.isEmpty(keys)) {
            return Collections.emptyList();
        }
        // 不走缓存，直接调用 loader
        if (cacheTime <= 0L || !Boolean.TRUE.equals(cacheSwitch)) {
            return loader.apply(keys);
        }

        // 1. 先从 Redis 批量读
        List<String> redisKeys = keys.stream()
                .map(k -> keyPattern + k)
                .collect(Collectors.toList());
        List<T> cachedJsons = new ArrayList<>();
        try {
            if (!forceUpdate) {
                List<String> stringList = redisTemplate.opsForValue().multiGet(redisKeys);
                if (CollectionUtils.isEmpty(stringList)) {
                    stringList = Collections.emptyList();
                }
                for (String str : stringList) {
                    if (str != null) {
                        try {
                            T parsed = JSONObject.parseObject(str, clazz);
                            if (parsed != null) {
                                cachedJsons.add(parsed);
                            }
                        } catch (Exception e) {
                            log.warn("解析缓存数据失败, str: {}, clazz: {}, error: {}", str, clazz.getName(), e.getMessage());
                        }
                    }
                }
            }
        } catch (Exception ignored) {
            log.warn("批量获取缓存失败, keys: {}", redisKeys);
        }
        Map<U, T> cachedMap = new HashMap<>();
        for (T json : cachedJsons) {
            if (json != null) {
                U k = keyMapper.apply(json);
                cachedMap.put(k, json);
            }
        }
        // 2. 反序列化 + 找出漏掉的 keys
        Map<U, T> resultMap = new LinkedHashMap<>(keys.size());
        List<U> missingKeys = new ArrayList<>();
        T json;
        for (U k : keys) {
            if (cachedMap.get(k) != null) {
                json = cachedMap.get(k);
                try {
                    resultMap.put(k, json);
                } catch (Exception e) {
                    missingKeys.add(k);
                }
            } else {
                missingKeys.add(k);
            }
        }

        if (!missingKeys.isEmpty()) {
            List<T> loaded = loader.apply(missingKeys);
            for (T item : loaded) {
                U k = keyMapper.apply(item);
                resultMap.put(k, item);
            }
            batchSetCache(keyMapper, loaded, keyPattern, cacheTime, timeUnit);
        }

        // 4. 保持原 keys 顺序返回 List<T>
        return keys.stream()
                .map(resultMap::get)
                .filter(Objects::nonNull)
                .collect(Collectors.toList());
    }

    /**
     * 批量设置缓存 - 优化版本
     * 根据配置选择使用 Pipeline 或普通方式
     */
    public static <T, U> void batchSetCache(Function<T, U> keyMapper, List<T> values, String keyPattern,
            long cacheTime, TimeUnit timeUnit) {
        if (CollectionUtils.isEmpty(values)) {
            return;
        }

        int actualBatchSize = batchSize != null ? batchSize : 200;
        int minPipelineSize = pipelineMinBatchSize != null ? pipelineMinBatchSize : 10;
        Lists.partition(values, actualBatchSize).forEach(batch -> {
            // 只有当启用Pipeline且批次大小达到阈值时才使用Pipeline
            if (Boolean.TRUE.equals(usePipeline) && !batch.isEmpty() && batch.size() >= minPipelineSize) {
                batchSetWithPipeline(keyMapper, batch, keyPattern, cacheTime, timeUnit);
            } else {
                batchSetWithoutPipeline(keyMapper, batch, keyPattern, cacheTime, timeUnit);
            }
        });
    }

    /**
     * 使用Pipeline批量设置缓存
     * Pipeline方式可以批量执行多个命令，减少网络往返次数，提高性能
     */
    @SuppressWarnings("unchecked")
    private static <T, U> void batchSetWithPipeline(Function<T, U> keyMapper, List<T> batch,
            String keyPattern, long cacheTime, TimeUnit timeUnit) {
        try {
            RedisSerializer<String> keySerializer = (RedisSerializer<String>) redisTemplate.getKeySerializer();
            RedisSerializer<String> valueSerializer = (RedisSerializer<String>) redisTemplate.getValueSerializer();

            redisTemplate.executePipelined((RedisCallback<Object>) connection -> {
                for (T t : batch) {
                    try {
                        if (t == null) {
                            log.warn("Pipeline set cache: value is null, skipping");
                            continue;
                        }
                        U keyValue = keyMapper.apply(t);
                        if (keyValue == null) {
                            log.warn("Pipeline set cache: keyMapper returned null, skipping");
                            continue;
                        }
                        String key = keyPattern + keyValue;
                        String value = JSONObject.toJSONString(t);

                        byte[] k = keySerializer.serialize(key);
                        byte[] v = valueSerializer.serialize(value);

                        if (k == null || v == null) {
                            log.warn("Pipeline set cache: serialization failed for key: {}", key);
                            continue;
                        }

                        if (cacheTime > 0) {
                            connection.setEx(k, timeUnit.toSeconds(cacheTime), v);
                        } else {
                            connection.setEx(k, 60, v);
                        }
                    } catch (Exception e) {
                        log.error("Pipeline set cache error for value: {}, error: {}", t, e.getMessage(), e);
                    }
                }
                return null;
            });
        } catch (Exception e) {
            log.error("Pipeline batch set cache failed, batch size: {}, error: {}",
                    batch.size(), e.getMessage(), e);
        }
    }

    /**
     * 普通批量设置（不使用Pipeline）
     */
    private static <T, U> void batchSetWithoutPipeline(Function<T, U> keyMapper, List<T> batch,
            String keyPattern, long cacheTime, TimeUnit timeUnit) {
        try {
            for (T t : batch) {
                if (t == null) {
                    continue;
                }
                U keyValue = keyMapper.apply(t);
                if (keyValue == null) {
                    continue;
                }
                String key = keyPattern + keyValue;
                if (cacheTime > 0) {
                    redisTemplate.opsForValue().set(key, JSONObject.toJSONString(t), cacheTime, timeUnit);
                } else {
                    redisTemplate.opsForValue().set(key, JSONObject.toJSONString(t), 60, TimeUnit.SECONDS);
                }
            }
        } catch (Exception e) {
            log.error("Batch set cache error for batch size: {}, error: {}", batch.size(), e.getMessage(), e);
        }
    }

    /**
     * 缓存无参数或固定参数的方法调用结果（返回List）
     * 适用于固定参数或无参数的方法，结果直接缓存到指定的key
     *
     * @param supplier  数据加载函数（无参数）
     * @param cacheKey  缓存key
     * @param cacheTime 缓存时间
     * @param timeUnit  时间单位
     * @param clazz     返回对象类型的Class，用于反序列化
     * @param <T>       返回对象类型
     * @return 缓存或加载的数据列表
     */
    public static <T> List<T> cacheList(
            Supplier<List<T>> supplier,
            String cacheKey,
            long cacheTime,
            TimeUnit timeUnit,
            Class<T> clazz) {
        try {
            // 不走缓存，直接调用 supplier
            if (cacheTime <= 0L || !Boolean.TRUE.equals(cacheSwitch)) {
                return supplier.get();
            }

            // 1. 先从 Redis 读取缓存
            try {
                String cachedValue = redisTemplate.opsForValue().get(cacheKey);
                if (cachedValue != null) {
                    List<T> parsed = JSONObject.parseArray(cachedValue, clazz);
                    if (!CollectionUtils.isEmpty(parsed)) {
                        return parsed;
                    }
                }
            } catch (Exception e) {
                log.warn("读取缓存失败, key: {}, error: {}", cacheKey, e.getMessage());
            }

            // 2. 缓存未命中，调用 supplier 加载数据
            List<T> result = supplier.get();
            if (result == null) {
                result = Collections.emptyList();
            }

            // 3. 写入缓存
            try {
                String value = JSONObject.toJSONString(result);
                redisTemplate.opsForValue().set(cacheKey, value, cacheTime, timeUnit);
            } catch (Exception e) {
                log.error("写入缓存失败, key: {}, error: {}", cacheKey, e.getMessage(), e);
            }

            return result;
        } catch (Exception e) {
            log.error("cacheList error for key: {}, error: {}", cacheKey, e.getMessage(), e);
            return supplier.get();
        }
    }

    @Autowired
    public void setRedisTemplate(RedisTemplate<String, String> redisTemplate) {
        RedisCacheUtil.redisTemplate = redisTemplate;
    }

}
