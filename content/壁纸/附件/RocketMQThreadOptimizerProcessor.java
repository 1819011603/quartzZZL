package com.gaotu.student.data.facade.config;

/**
 * @author: zhangzeling
 * @date: 2026/1/28
 * @description: RocketMQThreadOptimizerProcessor
 */
import com.aliyun.openservices.ons.api.PropertyKeyConst;
import com.ctrip.framework.apollo.spring.annotation.ApolloJsonValue;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.beans.factory.config.BeanPostProcessor;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.Ordered;
import org.springframework.core.PriorityOrdered;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

import java.lang.management.ManagementFactory;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 专门用于解决 RocketMQ/ONS Consumer 线程爆炸问题的处理器
 * 强制统一 InstanceName，实现底层 MQClientInstance 复用
 * 
 * 使用 BeanPostProcessor 拦截 OnsMessageListenerContainer 的初始化阶段
 * 在 Bean 初始化后获取 consumerBean 属性，并通过 getProperties() 设置 instanceName
 * 
 * 目标类（各自独立分组）：
 * - com.gaotu.arch.ons.config.OnsMessageListenerContainer (普通消息)
 * - com.gaotu.arch.ons.config.OnsMessageOrderListenerContainer (顺序消息)
 * - com.gaotu.arch.ons.config.OnsBatchMessageListenerContainer (批量消息)
 * 
 * Apollo 配置项：
 * - rocketmq.optimizer.enabled: 是否启用优化，默认 true
 * - rocketmq.optimizer.id: 实例 ID，默认使用 PID
 * - rocketmq.optimizer.normal.group-size: 普通消息容器每组数量，默认 8
 * - rocketmq.optimizer.order.group-size: 顺序消息容器每组数量，默认 8
 * - rocketmq.optimizer.batch.group-size: 批量消息容器每组数量，默认 8
 * - rocketmq.optimizer.exclude-beans: 排除的 beanName 列表，JSON 数组格式
 */
@Configuration
@Slf4j
public class RocketMQThreadOptimizerProcessor implements BeanPostProcessor, PriorityOrdered {

    /**
     * 容器类型枚举
     */
    private enum ContainerType {
        /** 普通消息监听容器 */
        NORMAL("OnsMessageListenerContainer", "normal"),
        /** 顺序消息监听容器 */
        ORDER("OnsMessageOrderListenerContainer", "order"),
        /** 批量消息监听容器 */
        BATCH("OnsBatchMessageListenerContainer", "batch");

        private final String className;
        private final String configKey;

        ContainerType(String className, String configKey) {
            this.className = className;
            this.configKey = configKey;
        }

        public String getConfigKey() {
            return configKey;
        }

        /**
         * 根据类名获取容器类型
         */
        public static ContainerType fromClass(Class<?> clazz) {
            String simpleName = clazz.getSimpleName();
            for (ContainerType type : values()) {
                if (type.className.equals(simpleName)) {
                    return type;
                }
            }
            return null;
        }
    }

    /**
     * OnsMessageListenerContainer 类名前缀
     */
    private static final String ONS_CONTAINER_PREFIX = "com.gaotu.arch.ons.config.Ons";



    /**
     * OnsMessageListenerContainer 每组消费者数量，默认 8
     */
    private int normalGroupSize = 6;

    /**
     * OnsMessageOrderListenerContainer 每组消费者数量，默认 8
     */
    private int orderGroupSize = 6;

    /**
     * OnsBatchMessageListenerContainer 每组消费者数量，默认 8
     */
    private int batchGroupSize = 3;

    /**
     * 各容器类型的优化计数器（独立分组）
     */
    private final AtomicInteger normalCount = new AtomicInteger(0);
    private final AtomicInteger orderCount = new AtomicInteger(0);
    private final AtomicInteger batchCount = new AtomicInteger(0);


    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        return bean;
    }

    public RocketMQThreadOptimizerProcessor() {
    log.info("🚀 [RocketMQ优化] RocketMQThreadOptimizerProcessor 已创建");
}

    /**
     * 在 Bean 初始化后被调用（在 afterPropertiesSet 之后）
     * 此时 consumerBean 已经在 afterPropertiesSet() 中创建并设置好属性
     * 我们在这里追加 instanceName 属性
     */
    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        log.info("beanName:{}, bean: {}", beanName, bean.getClass().getName());

        // 检查是否是 OnsMessageListenerContainer 或其子类
        if (isOnsListenerContainer(bean.getClass())) {

            optimizeContainer(beanName, bean);
        }
        return bean;
    }

    /**
     * 检查类是否是 OnsMessageListenerContainer 或其子类
     * 包括：OnsMessageListenerContainer, OnsMessageOrderListenerContainer, OnsBatchMessageListenerContainer
     */
    private boolean isOnsListenerContainer(Class<?> clazz) {
        String className = clazz.getName();
        return className.startsWith(ONS_CONTAINER_PREFIX);
    }



    /**
     * 获取容器类型对应的计数器
     */
    private AtomicInteger getCounter(ContainerType type) {
        switch (type) {
            case NORMAL:
                return normalCount;
            case ORDER:
                return orderCount;
            case BATCH:
                return batchCount;
            default:
                return normalCount;
        }
    }

    /**
     * 获取容器类型对应的分组大小
     */
    private int getGroupSize(ContainerType type) {
        switch (type) {
            case NORMAL:
                return normalGroupSize;
            case ORDER:
                return orderGroupSize;
            case BATCH:
                return batchGroupSize;
            default:
                return normalGroupSize;
        }
    }

    /**
     * 优化单个 OnsMessageListenerContainer
     * 通过反射获取 consumerBean 属性，并设置 instanceName
     */
    private void optimizeContainer(String beanName, Object container) {
        try {
            log.info("beanName:{}, container: {}", beanName, container.getClass().getName());
            // 0. 获取容器类型
            ContainerType containerType = ContainerType.fromClass(container.getClass());
            if (containerType == null) {
                log.warn("⚠ [RocketMQ优化] Bean: {} 未知的容器类型: {}", beanName, container.getClass().getName());
                return;
            }
            
            log.info("🔍 [RocketMQ优化] 开始优化 Bean: {} (类型: {})", beanName, containerType.getConfigKey());
            
            // 1. 通过反射获取 consumerBean 属性
            Field consumerBeanField = findField(container.getClass(), "consumerBean");
            if (consumerBeanField == null) {
                log.warn("⚠ [RocketMQ优化] Bean: {} 未找到 consumerBean 属性", beanName);
                return;
            }
            consumerBeanField.setAccessible(true);
            Object consumerBean = consumerBeanField.get(container);
            
            if (consumerBean == null) {
                log.warn("⚠ [RocketMQ优化] Bean: {} 的 consumerBean 为 null", beanName);
                return;
            }
            
            // 2. 调用 consumerBean.getProperties() 获取属性
            Method getPropertiesMethod = consumerBean.getClass().getMethod("getProperties");
            Properties properties = (Properties) getPropertiesMethod.invoke(consumerBean);
            
            if (properties == null) {
                log.warn("⚠ [RocketMQ优化] Bean: {} 的 consumerBean.getProperties() 返回 null", beanName);
                return;
            }
            
            // 3. 提取 NameServer 和 AccessKey
            String nameServer = properties.getProperty(PropertyKeyConst.NAMESRV_ADDR);
            String accessKey = properties.getProperty(PropertyKeyConst.AccessKey);
            
            if (nameServer == null || accessKey == null) {
                log.warn("⚠ [RocketMQ优化] Bean: {} 未配置 NAMESRV_ADDR 或 AccessKey，跳过优化", beanName);
                return;
            }
            
            // 4. 计算 HashCode
            int nameServerHash = nameServer.hashCode();
            int accessKeyHash = accessKey.hashCode();
            
            // 5. 获取实例 ID（优先使用配置的 ID，否则使用 PID）
            String id = getInstanceId();
            
            // 6. 获取该类型容器的计数器和分组大小
            AtomicInteger counter = getCounter(containerType);
            int groupSize = getGroupSize(containerType);
            
            // 7. 计算组号（每 groupSize 个为一组，各类型独立计数）
            int currentCount = counter.getAndIncrement();
            int groupNumber = currentCount / groupSize;
            
            // 8. 生成 InstanceName
            // 格式: id#nameServerHash#accessKeyHash#containerType#groupNumber
            // 相同类型、相同组的 Consumer 会得到相同的 InstanceName，从而复用 MQClientInstance
            String distinctInstanceName = id + "#" + nameServerHash + "#" + accessKeyHash 
                    + "#" + containerType.getConfigKey() + "#" + groupNumber;
            
            // 9. 设置 instanceName 到 Properties 中
            properties.setProperty(PropertyKeyConst.InstanceName, distinctInstanceName);
            
            log.info("✓ [RocketMQ优化] Bean: {} 已设置 InstanceName: {} (类型: {}, 第 {} 个, 组号: {})", 
                    beanName, distinctInstanceName, containerType.getConfigKey(), currentCount + 1, groupNumber);
            
        } catch (Exception e) {
            log.error("❌ [RocketMQ优化] Bean: {} 优化失败: {}", beanName, e.getMessage(), e);
        }
    }

    /**
     * 获取实例 ID
     * 优先使用配置的 ID，否则使用 PID
     */
    private String getInstanceId() {
        // 默认使用 PID
        return getPid();
    }

    /**
     * 获取当前进程 PID（兼容 Java 8）
     */
    private String getPid() {
        // 格式: pid@hostname
        String name = ManagementFactory.getRuntimeMXBean().getName();
        if (name != null && name.contains("@")) {
            return name.split("@")[0];
        }
        return "0";
    }

    /**
     * 在类及其父类中查找指定名称的字段
     */
    private Field findField(Class<?> clazz, String fieldName) {
        Class<?> currentClass = clazz;
        while (currentClass != null && currentClass != Object.class) {
            try {
                return currentClass.getDeclaredField(fieldName);
            } catch (NoSuchFieldException e) {
                currentClass = currentClass.getSuperclass();
            }
        }
        return null;
    }

    @Override
    public int getOrder() {
        return Ordered.LOWEST_PRECEDENCE;
    }
}
