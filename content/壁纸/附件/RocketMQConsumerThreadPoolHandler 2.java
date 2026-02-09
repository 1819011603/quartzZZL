package com.gaotu.student.data.facade.mq;

import com.alibaba.fastjson.JSONObject;
import com.ctrip.framework.apollo.model.ConfigChange;
import com.ctrip.framework.apollo.model.ConfigChangeEvent;
import com.ctrip.framework.apollo.spring.annotation.ApolloConfigChangeListener;
import com.ctrip.framework.apollo.spring.annotation.ApolloJsonValue;
import com.gaotu.arch.ons.config.OnsBatchMessageListenerContainer;
import com.gaotu.arch.ons.config.OnsMessageListenerContainer;
import com.gaotu.arch.ons.config.OnsMessageOrderListenerContainer;
import com.xxl.job.core.biz.model.ReturnT;
import com.xxl.job.core.handler.IJobHandler;
import com.xxl.job.core.handler.annotation.JobHandler;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.lang.reflect.Field;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

@Slf4j
@Component
@JobHandler(value = "rocketMQConsumerThreadPoolHandler")
public class RocketMQConsumerThreadPoolHandler extends IJobHandler implements ApplicationContextAware {

    private ApplicationContext applicationContext;
    private final Map<String, ThreadPoolExecutor> threadPoolRegistry = new ConcurrentHashMap<>();
    private final Map<String, Object> registryLocks = new ConcurrentHashMap<>();
    /** 记录每个线程池的初始最大线程数，用于动态调整范围计算 */
    private final Map<String, Integer> initialMaxPoolSizeRegistry = new ConcurrentHashMap<>();

    /** 定时调度线程池，用于自动扩缩容（改为实例变量避免热重启问题） */
    private ScheduledThreadPoolExecutor scheduledThreadPoolExecutor;
    /** 定时任务句柄，用于取消任务 */
    private volatile ScheduledFuture<?> autoScaleTaskFuture;
    /** 防止重复初始化 */
    private final AtomicBoolean initialized = new AtomicBoolean(false);

    @Value("${rocketmq.consumer.threadpool.init.delay.ms:180000}")
    private long initDelayMs = 180000;

    @Value("${rocketmq.consumer.threadpool.userClazzName.enabled:true}")
    private boolean userClazzNameEnabled;

    /** 自动扩缩容开关 */
    @Value("${rocketmq.consumer.threadpool.autoScale.enabled:true}")
    private volatile boolean autoScaleEnabled;

    /** 自动扩缩容检查间隔（秒） */
    @Value("${rocketmq.consumer.threadpool.autoScale.interval.seconds:120}")
    private long autoScaleIntervalSeconds;

    /** 扩容步长 */
    @Value("${rocketmq.consumer.threadpool.scale.up.step:4}")
    private int scaleUpStep;

    /** 缩容步长（温和缩减） */
    @Value("${rocketmq.consumer.threadpool.scale.down.step:2}")
    private int scaleDownStep;

    /** 空闲时线程保活时间（秒） */
    @Value("${rocketmq.consumer.threadpool.keepAlive.seconds:60}")
    private long keepAliveSeconds;

    /** 队列积压阈值倍数（queueSize >= corePoolSize * 此值 触发扩容） */
    @Value("${rocketmq.consumer.threadpool.queue.threshold.ratio:2}")
    private int queueThresholdRatio;

    /** 连续空闲次数阈值，达到后才缩容（避免抖动） */
    @Value("${rocketmq.consumer.threadpool.idle.count.threshold:3}")
    private int idleCountThreshold;

    @Value("${rocketmq.consumer.threadpool.min.pool.size:2}")
    private int globalMinPoolSize;

    @Value("${rocketmq.consumer.threadpool.max.pool.size:32}")
    private int globalMaxPoolSize;

    @Value("${rocketmq.consumer.threadpool.max.multi:3}")
    private int maxMulti;

    /** 记录每个线程池连续空闲的次数 */
    private final Map<String, Integer> idleCountRegistry = new ConcurrentHashMap<>();

    /**
     * 每个消费者的线程池范围配置
     * 格式: {"consumerName": {"min": 10, "max": 100}, ...}
     */
    @ApolloJsonValue("${rocketmq.consumer.threadpool.range.config:{}}")
    private Map<String, ThreadPoolRangeConfig> threadPoolRangeConfigMap;

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
    }

    @Override
    @PostConstruct
    public void init() {
        if (!initialized.compareAndSet(false, true)) {
            log.warn("RocketMQ ThreadPool already initialized, skip");
            return;
        }
        // 初始化调度线程池
        scheduledThreadPoolExecutor = new ScheduledThreadPoolExecutor(1);
        scheduledThreadPoolExecutor.setRemoveOnCancelPolicy(true);
        
        scheduledThreadPoolExecutor.schedule(() -> {
            try {
                doInit();
                // 初始化完成后启动自动扩缩容定时任务
                if (autoScaleEnabled) {
                    startAutoScaleTask();
                }
            } catch (Exception e) {
                log.error("RocketMQ ThreadPool init failed", e);
            }
        }, initDelayMs, TimeUnit.MILLISECONDS);
    }

    @PreDestroy
    public void destroy() {
        if (scheduledThreadPoolExecutor == null) {
            return;
        }
        try {
            // 先取消定时任务
            if (autoScaleTaskFuture != null) {
                autoScaleTaskFuture.cancel(false);
            }
            scheduledThreadPoolExecutor.shutdown();
            if (!scheduledThreadPoolExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduledThreadPoolExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduledThreadPoolExecutor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    private void doInit() {
        try {
            registerFromContainers(OnsMessageListenerContainer.class, "consumer");
            registerFromContainers(OnsMessageOrderListenerContainer.class, "orderConsumer");
            registerFromContainers(OnsBatchMessageListenerContainer.class, "batchConsumer");
            log.info("RocketMQ ThreadPool init done, registered {} consumers", threadPoolRegistry.size());
        } catch (Exception e) {
            log.error("RocketMQ ThreadPool init failed", e);
        }
    }

    /**
     * 启动自动扩缩容定时任务
     */
    private void startAutoScaleTask() {
        if (autoScaleTaskFuture != null) {
            autoScaleTaskFuture.cancel(false);
        }
        autoScaleTaskFuture = scheduledThreadPoolExecutor.scheduleWithFixedDelay(
                this::autoScaleAllThreadPools,
                autoScaleIntervalSeconds,
                autoScaleIntervalSeconds,
                TimeUnit.SECONDS
        );
        log.info("Auto scale task started, interval={}s", autoScaleIntervalSeconds);
    }

    /**
     * 自动扩缩容所有注册的线程池
     */
    private void autoScaleAllThreadPools() {
        for (Map.Entry<String, ThreadPoolExecutor> entry : threadPoolRegistry.entrySet()) {
            try {
                autoAdjustThreadNum(entry.getKey(), entry.getValue());
            } catch (Exception e) {
                log.error("Auto scale failed for: {}", entry.getKey(), e);
            }
        }
    }

    /**
     * 自动调整线程池参数
     * 扩容触发条件: 活跃线程数 * 3 >= 2 * corePoolSize 且 队列积压 >= corePoolSize * queueThresholdRatio
     * 缩容触发条件: 连续 idleCountThreshold 次检测到空闲（active <= 1 且 queue == 0）
     */
    private void autoAdjustThreadNum(String name, ThreadPoolExecutor threadPoolExecutor) {
        if (!autoScaleEnabled) {
            return;
        }
        
        int currentCore = threadPoolExecutor.getCorePoolSize();
        int currentMax = threadPoolExecutor.getMaximumPoolSize();
        int activeCount = threadPoolExecutor.getActiveCount();
        int poolSize = threadPoolExecutor.getPoolSize();
        int queueSize = threadPoolExecutor.getQueue().size();

        // 获取线程池范围配置
        ThreadPoolRangeConfig rangeConfig = getThreadPoolRange(name);
        int configMinPoolSize = rangeConfig.getMin();
        int configMaxPoolSize = rangeConfig.getMax();

        // 扩容判断: 活跃线程数 * 3 >= 2 * corePoolSize 且 队列积压 >= corePoolSize * queueThresholdRatio
        if (queueSize >= currentCore * queueThresholdRatio && activeCount * 3 >= 2 * currentCore) {
            // 有负载，清空空闲计数
            idleCountRegistry.remove(name);
            
            if (currentCore < configMaxPoolSize && poolSize < configMaxPoolSize) {
                int newCore = Math.min(Math.max(currentCore, poolSize) + scaleUpStep, configMaxPoolSize);
                int newMax = Math.max(newCore, currentMax);
                safeSetCoreAndMax(threadPoolExecutor, newCore, newMax);
                log.info("ThreadPool scaled UP: {}, core: {} -> {}, max: {} -> {}, active={}, queue={}",
                        name, currentCore, newCore, currentMax, newMax, activeCount, queueSize);
            }
        }
        // 缩容判断: 空闲状态（active <= 1 且 queue == 0）
        else if (queueSize == 0 && activeCount <= 1) {
            // 累加空闲计数
            int idleCount = idleCountRegistry.merge(name, 1, Integer::sum);
            
            // 连续空闲达到阈值才缩容，避免抖动
            if (idleCount >= idleCountThreshold && currentCore > configMinPoolSize) {
                int newCore = Math.max(configMinPoolSize, currentCore - scaleDownStep);
                // 缩容时 max 也要同步缩小，避免 max 持续膨胀
                int newMax = Math.min(currentMax, newCore);
                
                if (newCore < currentCore) {
                    safeSetCoreAndMax(threadPoolExecutor, newCore, newMax);
                    // 设置空闲线程回收时间，并开启核心线程超时
                    threadPoolExecutor.setKeepAliveTime(keepAliveSeconds, TimeUnit.SECONDS);
                    threadPoolExecutor.allowCoreThreadTimeOut(true);
                    // 缩容后重置计数
                    idleCountRegistry.put(name, 0);
                    log.info("ThreadPool scaled DOWN: {}, core: {} -> {}, max: {} -> {}, keepAlive={}s, idleCount={}, active={}, queue={}",
                            name, currentCore, newCore, currentMax, newMax, keepAliveSeconds, idleCount, activeCount, queueSize);
                }
            } else {
                log.debug("ThreadPool idle: {}, idleCount={}/{}, core={}, active={}, queue={}",
                        name, idleCount, idleCountThreshold, currentCore, activeCount, queueSize);
            }
        } else {
            // 非空闲状态，清空空闲计数
            idleCountRegistry.remove(name);
        }

        log.debug("ThreadPool status: {}, core={}, max={}, active={}, pool={}, queue={}",
                name, threadPoolExecutor.getCorePoolSize(), threadPoolExecutor.getMaximumPoolSize(),
                activeCount, poolSize, queueSize);
    }

    /**
     * 获取线程池范围配置
     * 优先从Apollo配置读取，没有配置则使用默认范围: [初始max, 初始max * maxMulti]
     */
    private ThreadPoolRangeConfig getThreadPoolRange(String name) {
        // 优先从Apollo配置读取
        if (threadPoolRangeConfigMap != null && threadPoolRangeConfigMap.containsKey(name)) {
            ThreadPoolRangeConfig config = threadPoolRangeConfigMap.get(name);
            // 校验配置有效性
            if (config.getMin() > 0 && config.getMax() >= config.getMin()) {
                return config;
            }
            log.warn("Invalid ThreadPoolRangeConfig for {}: min={}, max={}, use default", 
                    name, config.getMin(), config.getMax());
        }

        // 没有配置则使用默认范围
        Integer initialMax = initialMaxPoolSizeRegistry.get(name);
        if (initialMax == null || initialMax <= 0) {
            initialMax = globalMinPoolSize;
        }
        ThreadPoolRangeConfig defaultConfig = new ThreadPoolRangeConfig();
        defaultConfig.setMin(Math.max(globalMinPoolSize, initialMax));
        defaultConfig.setMax(Math.min(initialMax * maxMulti, globalMaxPoolSize));
        return defaultConfig;
    }

    /**
     * 安全设置核心线程数和最大线程数，避免IllegalArgumentException
     */
    private void safeSetCoreAndMax(ThreadPoolExecutor executor, int core, int max) {
        if (max > executor.getMaximumPoolSize()) {
            executor.setMaximumPoolSize(max);
            executor.setCorePoolSize(core);
        } else if (core < executor.getCorePoolSize()) {
            executor.setCorePoolSize(core);
            executor.setMaximumPoolSize(max);
        } else {
            executor.setCorePoolSize(core);
            executor.setMaximumPoolSize(max);
        }
    }

    private void registerFromContainers(Class<?> containerClass, String consumerFieldName) {
        String[] beanNames = applicationContext.getBeanNamesForType(containerClass);
        for (String beanName : beanNames) {
            try {
                Object container = applicationContext.getBean(beanName);
                String listenerName = extractListenerBeanName(container);
                String key = listenerName != null ? listenerName : beanName;
                if (!threadPoolRegistry.containsKey(key)) {
                    ThreadPoolExecutor executor = extractConsumeExecutor(container, consumerFieldName);
                    if (executor != null) {
                        registerThreadPool(key, executor);
                    }
                }

            } catch (Exception e) {
                log.error("Register from container failed: {}", beanName, e);
            }
        }
    }

    /**
     * container.consumerBean -> consumerBean.{consumer/orderConsumer/batchConsumer}
     * -> onsConsumer.defaultMQPushConsumer -> defaultMQPushConsumerImpl
     * -> consumeMessageService -> consumeExecutor (ThreadPoolExecutor)
     */
    private ThreadPoolExecutor extractConsumeExecutor(Object container, String consumerFieldName) {
        try {
            Object consumerBean = getFieldValue(container, "consumerBean");
            if (consumerBean == null) return null;

            Object onsConsumer = getFieldValue(consumerBean, consumerFieldName);
            if (onsConsumer == null) return null;

            Object defaultMQPushConsumer = getFieldValue(onsConsumer, "defaultMQPushConsumer");
            if (defaultMQPushConsumer == null) return null;

            Object defaultMQPushConsumerImpl = getFieldValue(defaultMQPushConsumer, "defaultMQPushConsumerImpl");
            if (defaultMQPushConsumerImpl == null) return null;

            Object consumeMessageService = getFieldValue(defaultMQPushConsumerImpl, "consumeMessageService");
            if (consumeMessageService == null) return null;

            Object consumeExecutor = getFieldValue(consumeMessageService, "consumeExecutor");
            if (consumeExecutor instanceof ThreadPoolExecutor) {
                return (ThreadPoolExecutor) consumeExecutor;
            }
            return null;
        } catch (Exception e) {
            log.error("Extract consumeExecutor failed", e);
            return null;
        }
    }

    private String extractListenerBeanName(Object container) {
        try {
            List listener = (List) getFieldValue(container, "messageListenerList");
            if (listener == null) listener = (List) getFieldValue(container, "batchMessageListenerList");
            if (listener == null) listener = (List) getFieldValue(container, "messageOrderListenerList");
            if (CollectionUtils.isEmpty(listener)) return null;
            if (userClazzNameEnabled) {
                return listener.get(0).getClass().getSimpleName();
            }
            String[] names = applicationContext.getBeanNamesForType(listener.get(0).getClass());
            return names.length > 0 ? names[0] : listener.getClass().getSimpleName();
        } catch (Exception e) {
            return null;
        }
    }

    private Object getFieldValue(Object obj, String fieldName) {
        try {
            Field field = findField(obj.getClass(), fieldName);
            if (field == null) return null;
            field.setAccessible(true);
            return field.get(obj);
        } catch (Exception e) {
            return null;
        }
    }

    private Field findField(Class<?> clazz, String fieldName) {
        Class<?> current = clazz;
        while (current != null && current != Object.class) {
            try {
                return current.getDeclaredField(fieldName);
            } catch (NoSuchFieldException e) {
                current = current.getSuperclass();
            }
        }
        return null;
    }

    private void registerThreadPool(String name, ThreadPoolExecutor executor) {
        if (StringUtils.isBlank(name) || executor == null) return;
        if (threadPoolRegistry.containsKey(name)) return;
        Object lock = registryLocks.computeIfAbsent(name, k -> new Object());
        synchronized (lock) {
            if (threadPoolRegistry.containsKey(name)) return;
            threadPoolRegistry.put(name, executor);
            // 记录初始最大线程数，用于默认范围计算
            initialMaxPoolSizeRegistry.put(name, executor.getMaximumPoolSize());
            log.info("Consumer registered: {}, core={}, max={}",
                    name, executor.getCorePoolSize(), executor.getMaximumPoolSize());
        }
    }

    public void adjustThreadPool(String name, int core, int max) {
        doInit();
        ThreadPoolExecutor tp = getThreadPoolExecutor(name);
        if (tp == null) {
            log.warn("ThreadPool not found: {}", name);
            return;
        }
        if (core <= 0 || max <= 0 || core > max) {
            log.error("Invalid params: core={}, max={}", core, max);
            return;
        }
        try {
            safeSetCoreAndMax(tp, core, max);
            log.info("ThreadPool adjusted: {}, core={}, max={}", name, core, max);
        } catch (Exception e) {
            log.error("Adjust failed: {}", name, e);
        }
    }

    private ThreadPoolExecutor getThreadPoolExecutor(String name) {
        return threadPoolRegistry.get(name);
    }

    @ApolloConfigChangeListener
    public void onApolloConfigChange(ConfigChangeEvent changeEvent) {
        if (!"application".equals(changeEvent.getNamespace())) return;
        for (String name : threadPoolRegistry.keySet()) {
            ConfigChange change = changeEvent.getChange(name + ".thread.pool.size");
            if (change == null) continue;
            if (change.getChangeType() != com.ctrip.framework.apollo.enums.PropertyChangeType.MODIFIED
                    && change.getChangeType() != com.ctrip.framework.apollo.enums.PropertyChangeType.ADDED) continue;
            try {
                String[] parts = change.getNewValue().split(",");
                int core = Integer.parseInt(parts[0].trim());
                int max = parts.length == 2 ? Integer.parseInt(parts[1].trim()) : core;
                adjustThreadPool(name, core, max);
                log.info("Apollo changed: {}, old={}, new={}", name, change.getOldValue(), change.getNewValue());
            } catch (Exception e) {
                log.error("Parse config failed: {}, change={}", name, JSONObject.toJSONString(change), e);
            }
        }
    }

    @Override
    public ReturnT<String> execute(String param) {
        try {
            if (StringUtils.isBlank(param)) {
                return new ReturnT<String>(500, "用法: status[:name] | adjust:name:core:max | autoScale:on|off");
            }
            String[] parts = param.trim().split(":");
            if ("status".equals(parts[0])) {
                return parts.length == 1 ? getAllStatus() : getStatus(parts[1]);
            } else if ("adjust".equals(parts[0]) && parts.length == 4) {
                adjustThreadPool(parts[1], Integer.parseInt(parts[2]), Integer.parseInt(parts[3]));
                return new ReturnT<String>(String.format("调整成功: %s, core=%s, max=%s", parts[1], parts[2], parts[3]));
            } else if ("autoScale".equals(parts[0]) && parts.length == 2) {
                return setAutoScale("on".equalsIgnoreCase(parts[1]));
            }
            return new ReturnT<String>(500, "未知操作: " + param);
        } catch (Exception e) {
            log.error("Execute failed: {}", param, e);
            return new ReturnT<String>(500, "执行失败: " + e.getMessage());
        }
    }

    private ReturnT<String> setAutoScale(boolean enabled) {
        this.autoScaleEnabled = enabled;
        // 开启时确保定时任务在运行
        if (enabled && autoScaleTaskFuture == null && scheduledThreadPoolExecutor != null) {
            startAutoScaleTask();
        }
        return new ReturnT<String>("自动扩缩容已" + (enabled ? "开启" : "关闭"));
    }

    private ReturnT<String> getAllStatus() {
        StringBuilder sb = new StringBuilder("线程池状态:\n");
        for (Map.Entry<String, ThreadPoolExecutor> entry : threadPoolRegistry.entrySet()) {
            String name = entry.getKey();
            ThreadPoolExecutor tp = entry.getValue();
            ThreadPoolRangeConfig range = getThreadPoolRange(name);
            int idleCount = idleCountRegistry.getOrDefault(name, 0);
            sb.append(String.format("%s: core=%d, max=%d, active=%d, pool=%d, queue=%d, range=[%d,%d], idle=%d/%d\n",
                    name, tp.getCorePoolSize(), tp.getMaximumPoolSize(),
                    tp.getActiveCount(), tp.getPoolSize(), tp.getQueue().size(),
                    range.getMin(), range.getMax(), idleCount, idleCountThreshold));
        }
        sb.append("自动扩缩容: ").append(autoScaleEnabled ? "开启" : "关闭");
        sb.append(", 检查间隔: ").append(autoScaleIntervalSeconds).append("s");
        return new ReturnT<String>(sb.toString());
    }

    private ReturnT<String> getStatus(String name) {
        ThreadPoolExecutor tp = getThreadPoolExecutor(name);
        if (tp == null) return new ReturnT<String>(500, "未找到: " + name);
        ThreadPoolRangeConfig range = getThreadPoolRange(name);
        int idleCount = idleCountRegistry.getOrDefault(name, 0);
        return new ReturnT<String>(String.format("%s: core=%d, max=%d, active=%d, pool=%d, queue=%d, range=[%d,%d], idle=%d/%d",
                name, tp.getCorePoolSize(), tp.getMaximumPoolSize(),
                tp.getActiveCount(), tp.getPoolSize(), tp.getQueue().size(),
                range.getMin(), range.getMax(), idleCount, idleCountThreshold));
    }

    /**
     * 线程池范围配置
     */
    @Data
    public static class ThreadPoolRangeConfig {
        /** 最小核心线程数 */
        private int min = 2;
        /** 最大线程数上限 */
        private int max = 32;
    }
}
