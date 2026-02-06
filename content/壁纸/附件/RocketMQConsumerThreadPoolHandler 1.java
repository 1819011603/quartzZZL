package com.gaotu.student.data.facade.job;

import com.alibaba.fastjson.JSONObject;
import com.ctrip.framework.apollo.model.ConfigChange;
import com.ctrip.framework.apollo.model.ConfigChangeEvent;
import com.ctrip.framework.apollo.spring.annotation.ApolloConfigChangeListener;
import com.gaotu.arch.ons.config.OnsBatchMessageListenerContainer;
import com.gaotu.arch.ons.config.OnsMessageListenerContainer;
import com.gaotu.arch.ons.config.OnsMessageOrderListenerContainer;
import com.xxl.job.core.biz.model.ReturnT;
import com.xxl.job.core.handler.IJobHandler;
import com.xxl.job.core.handler.annotation.JobHandler;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import java.lang.reflect.Field;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadPoolExecutor;

@Slf4j
@Component
@JobHandler(value = "rocketMQConsumerThreadPoolHandler")
public class RocketMQConsumerThreadPoolHandler extends IJobHandler implements ApplicationContextAware {

    private ApplicationContext applicationContext;
    private final Map<String, ThreadPoolExecutor> threadPoolRegistry = new ConcurrentHashMap<>();
    private final Map<String, Object> registryLocks = new ConcurrentHashMap<>();

    @Value("${rocketmq.consumer.threadpool.init.delay.ms:30000}")
    private long initDelayMs;

    @Value("${rocketmq.consumer.threadpool.userClazzName.enabled:true}")
    private boolean userClazzNameEnabled;

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
    }

    @PostConstruct
    public void init() {
        CompletableFuture.runAsync(()-> {
            try {
                Thread.sleep(initDelayMs);
                doInit();
            } catch (InterruptedException ignored) {
            }
        });
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
            log.info("Consumer registered: {}, core={}, max={}",
                    name, executor.getCorePoolSize(), executor.getMaximumPoolSize());
        }
    }

    public void adjustThreadPool(String name, int core, int max) {
        doInit();
        ThreadPoolExecutor tp = threadPoolRegistry.get(name);
        if (tp == null) {
            log.warn("ThreadPool not found: {}", name);
            return;
        }
        if (core <= 0 || max <= 0 || core > max) {
            log.error("Invalid params: core={}, max={}", core, max);
            return;
        }
        try {
            if (max > tp.getMaximumPoolSize()) {
                tp.setMaximumPoolSize(max);
                tp.setCorePoolSize(core);
            } else if (core < tp.getCorePoolSize()) {
                tp.setCorePoolSize(core);
                tp.setMaximumPoolSize(max);
            } else {
                tp.setCorePoolSize(core);
                tp.setMaximumPoolSize(max);
            }
            log.info("ThreadPool adjusted: {}, core={}, max={}", name, core, max);
        } catch (Exception e) {
            log.error("Adjust failed: {}", name, e);
        }
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
                return new ReturnT<String>(500, "用法: status[:name] | adjust:name:core:max");
            }
            String[] parts = param.trim().split(":");
            if ("status".equals(parts[0])) {
                return parts.length == 1 ? getAllStatus() : getStatus(parts[1]);
            } else if ("adjust".equals(parts[0]) && parts.length == 4) {
                adjustThreadPool(parts[1], Integer.parseInt(parts[2]), Integer.parseInt(parts[3]));
                return new ReturnT<String>(String.format("调整成功: %s, core=%s, max=%s", parts[1], parts[2], parts[3]));
            }
            return new ReturnT<String>(500, "未知操作: " + param);
        } catch (Exception e) {
            log.error("Execute failed: {}", param, e);
            return new ReturnT<String>(500, "执行失败: " + e.getMessage());
        }
    }

    private ReturnT<String> getAllStatus() {
        StringBuilder sb = new StringBuilder("线程池状态:\n");
        for (Map.Entry<String, ThreadPoolExecutor> entry : threadPoolRegistry.entrySet()) {
            ThreadPoolExecutor tp = entry.getValue();
            sb.append(String.format("%s: core=%d, max=%d, active=%d, pool=%d, queue=%d\n",
                    entry.getKey(), tp.getCorePoolSize(), tp.getMaximumPoolSize(),
                    tp.getActiveCount(), tp.getPoolSize(), tp.getQueue().size()));
        }
        return new ReturnT<String>(sb.toString());
    }

    private ReturnT<String> getStatus(String name) {
        ThreadPoolExecutor tp = threadPoolRegistry.get(name);
        if (tp == null) return new ReturnT<String>(500, "未找到: " + name);
        return new ReturnT<String>(String.format("%s: core=%d, max=%d, active=%d, pool=%d, queue=%d",
                name, tp.getCorePoolSize(), tp.getMaximumPoolSize(),
                tp.getActiveCount(), tp.getPoolSize(), tp.getQueue().size()));
    }
}
