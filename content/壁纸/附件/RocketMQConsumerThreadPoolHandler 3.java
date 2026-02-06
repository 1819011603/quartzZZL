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
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
@JobHandler(value = "rocketMQConsumerThreadPoolHandler")
public class RocketMQConsumerThreadPoolHandler extends IJobHandler implements ApplicationContextAware {

    private ApplicationContext applicationContext;
    private final Map<String, ThreadPoolExecutor> threadPoolRegistry = new ConcurrentHashMap<>();
    private final Map<String, Object> registryLocks = new ConcurrentHashMap<>();
    /** 记录每个线程池的初始最大线程数，用于动态调整范围计算 */
    private final Map<String, Integer> initialMaxPoolSizeRegistry = new ConcurrentHashMap<>();

    /** 定时调度线程池，用于自动扩缩容 */
    private static final ScheduledThreadPoolExecutor scheduledThreadPoolExecutor = new ScheduledThreadPoolExecutor(2);

    @Value("${rocketmq.consumer.threadpool.init.delay.ms:180000}")
    private long initDelayMs = 180000;

    @Value("${rocketmq.consumer.threadpool.userClazzName.enabled:true}")
    private boolean userClazzNameEnabled;

    /** 自动扩缩容开关 */
    @Value("${rocketmq.consumer.threadpool.autoScale.enabled:true}")
    private boolean autoScaleEnabled;

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


    @Value("${rocketmq.consumer.threadpool.min.pool.size:2}")
    private int minPoolSize;

    @Value("${rocketmq.consumer.threadpool.max.pool.size:32}")
    private int maxPoolSize;


    @Value("${rocketmq.consumer.threadpool.max.multi:3}")
    private int maxMulti;

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
        try {
            scheduledThreadPoolExecutor.shutdown();
            if (!scheduledThreadPoolExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduledThreadPoolExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduledThreadPoolExecutor.shutdownNow();
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
        scheduledThreadPoolExecutor.scheduleWithFixedDelay(
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
     * 扩容触发条件: 活跃线程数 >= corePoolSize * 1/3 且 队列大小 >= corePoolSize
     * 缩容触发条件: 活跃线程数 == 0 且 队列大小 == 0
     */
    private void autoAdjustThreadNum(String name, ThreadPoolExecutor threadPoolExecutor) {

        if (!autoScaleEnabled) {
            return;
        }
        int currentCore = threadPoolExecutor.getCorePoolSize();
        int currentMax = threadPoolExecutor.getMaximumPoolSize();
        Integer activeCount = null;
        int poolSize = threadPoolExecutor.getPoolSize();
        int queueSize = threadPoolExecutor.getQueue().size();

        // 获取线程池范围配置
        ThreadPoolRangeConfig rangeConfig = getThreadPoolRange(name);
        int minPoolSize = rangeConfig.getMin();
        int maxPoolSize = rangeConfig.getMax();

        // 扩容判断: 活跃线程数 * 3 >= 2 * corePoolSize 且 队列积压 >= corePoolSize
        if (queueSize >= currentCore * currentCore && (activeCount = threadPoolExecutor.getActiveCount()) * 3 >= 2 * currentCore ) {
            if (currentCore < maxPoolSize && poolSize < maxPoolSize) {
                int newCore = Math.min(Math.max(currentCore, poolSize) + scaleUpStep, maxPoolSize);
                int max = Math.max(newCore, currentMax);
                safeSetCoreAndMax(threadPoolExecutor, newCore, max);
                log.info("ThreadPool scaled up: {}, core: {} -> {}, max: {} -> {}, active={}, queue={}",
                        name, currentCore, newCore, currentMax, max, activeCount, queueSize);
            }
        }
        else if (queueSize == 0 && (activeCount = activeCount == null? threadPoolExecutor.getActiveCount() : activeCount) <= 1 ) {
            int newCore = Math.max(minPoolSize, currentCore - scaleDownStep);
            if (newCore < currentCore) {
                int max = Math.max(newCore, currentMax);
                safeSetCoreAndMax(threadPoolExecutor, newCore, max);
                // 设置空闲线程回收时间
                threadPoolExecutor.setKeepAliveTime(keepAliveSeconds, TimeUnit.SECONDS);
                log.info("ThreadPool scaled down: {}, core: {} -> {}, max: {} -> {}, keepAlive={}s, active={}, queue={}",
                        name, currentCore, newCore,  currentMax, max, keepAliveSeconds, activeCount, queueSize);
            }
        }

        log.debug("ThreadPool status: {}, core={}, max={}, active={}, pool={}, queue={}",
                name, threadPoolExecutor.getCorePoolSize(), threadPoolExecutor.getMaximumPoolSize(),
                activeCount, poolSize, queueSize);
    }

    /**
     * 获取线程池范围配置
     * 优先从Apollo配置读取，没有配置则使用默认范围: [初始max, 初始max*2]
     */
    private ThreadPoolRangeConfig getThreadPoolRange(String name) {
        // 优先从Apollo配置读取
        if (threadPoolRangeConfigMap != null && threadPoolRangeConfigMap.containsKey(name)) {
            return threadPoolRangeConfigMap.get(name);
        }

        // 没有配置则使用默认范围
        Integer initialMax = initialMaxPoolSizeRegistry.get(name);
        if (initialMax == null || initialMax <= 0) {
            initialMax = minPoolSize;
        }
        ThreadPoolRangeConfig defaultConfig = new ThreadPoolRangeConfig();
        defaultConfig.setMin(initialMax);
        defaultConfig.setMax(Math.min(initialMax * maxMulti, maxPoolSize));
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
        return new ReturnT<String>("自动扩缩容已" + (enabled ? "开启" : "关闭"));
    }

    private ReturnT<String> getAllStatus() {
        StringBuilder sb = new StringBuilder("线程池状态:\n");
        for (Map.Entry<String, ThreadPoolExecutor> entry : threadPoolRegistry.entrySet()) {
            ThreadPoolExecutor tp = entry.getValue();
            ThreadPoolRangeConfig range = getThreadPoolRange(entry.getKey());
            sb.append(String.format("%s: core=%d, max=%d, active=%d, pool=%d, queue=%d, range=[%d,%d]\n",
                    entry.getKey(), tp.getCorePoolSize(), tp.getMaximumPoolSize(),
                    tp.getActiveCount(), tp.getPoolSize(), tp.getQueue().size(),
                    range.getMin(), range.getMax()));
        }
        sb.append("自动扩缩容: ").append(autoScaleEnabled ? "开启" : "关闭");
        return new ReturnT<String>(sb.toString());
    }

    private ReturnT<String> getStatus(String name) {
        ThreadPoolExecutor tp = getThreadPoolExecutor(name);
        if (tp == null) return new ReturnT<String>(500, "未找到: " + name);
        ThreadPoolRangeConfig range = getThreadPoolRange(name);
        return new ReturnT<String>(String.format("%s: core=%d, max=%d, active=%d, pool=%d, queue=%d, range=[%d,%d]",
                name, tp.getCorePoolSize(), tp.getMaximumPoolSize(),
                tp.getActiveCount(), tp.getPoolSize(), tp.getQueue().size(),
                range.getMin(), range.getMax()));
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
