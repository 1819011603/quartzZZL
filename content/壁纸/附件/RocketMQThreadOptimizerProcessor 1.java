package com.gaotu.student.data.facade.config;

/**
 * @author: zhangzeling
 * @date: 2026/1/28
 * @description: RocketMQThreadOptimizerProcessor
 */

import com.aliyun.openservices.ons.api.PropertyKeyConst;
import lombok.extern.slf4j.Slf4j;
import org.apache.rocketmq.common.UtilAll;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanPostProcessor;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.Ordered;
import org.springframework.core.PriorityOrdered;

import javax.annotation.PreDestroy;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Random;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 专门用于解决 RocketMQ/ONS Consumer 线程爆炸问题的处理器
 * 强制统一 InstanceName，实现底层 MQClientInstance 复用
 * <p>
 * 【原理】
 * MQClientManager 通过 clientId (IP@instanceName) 来复用 MQClientInstance。
 * 相同 instanceName 的 Consumer 会共享同一个 MQClientInstance，从而共享：
 * - scheduledExecutorService (定时任务线程池, 1-4线程)
 * - pullMessageService (拉取消息服务, 1线程)
 * - rebalanceService (负载均衡服务, 1线程)
 * - Netty eventLoopGroup (网络IO, 6线程)
 * - publicExecutor (回调处理, 4线程)
 * 每个 MQClientInstance 约占用 10-15 个线程。
 * <p>
 * 【注意】consumeMessageService (消费线程池) 是每个 Consumer 独立的，不会共享！
 * <p>
 * 【桶算法】
 * - 初始2个桶，使用随机数选择起始桶
 * - 当桶使用超过一半容量时自动扩容
 * - 保证每桶严格不超过 groupSize
 */
@Configuration
@Slf4j
public class RocketMQThreadOptimizerProcessor implements BeanPostProcessor, PriorityOrdered {

    /**
     * OnsMessageListenerContainer 类名前缀
     */
    private static final String ONS_CONTAINER_PREFIX = "com.gaotu.arch.ons.config.Ons";

    /**
     * 最大桶数量
     */
    private static final int MAX_BUCKETS = 64;

    /**
     * 初始桶数量
     */
    private static final int INIT_BUCKETS = 3;

    /**
     * 随机数生成器
     */
    private final Random random = new Random();

    /**
     * 各容器类型的优化计数器（用于统计）
     */
    private final AtomicInteger normalCount = new AtomicInteger(0);
    private final AtomicInteger orderCount = new AtomicInteger(0);
    private final AtomicInteger batchCount = new AtomicInteger(0);

    /**
     * 桶状态：按 nameServerHash#accessKeyHash#containerType 维护，记录每个桶的当前容量
     * 只有相同 nameServer + accessKey + containerType 的 Consumer 才能共享 MQClientInstance
     */
    private final Map<String, BucketState> bucketStates = new ConcurrentHashMap<>();

    /**
     * 分布记录：distinctInstanceName -> List<beanName>
     */

    private final Map<String, List<String>> distributionMap = new ConcurrentHashMap<>();


    public Map<String, List<String>> getDistributionMap() {
        return distributionMap;
    }


    /**
     * OnsMessageListenerContainer 每组消费者数量
     */
    private int normalGroupSize = 4;

    /**
     * OnsMessageOrderListenerContainer 每组消费者数量
     */
    private int orderGroupSize = 3;

    /**
     * OnsBatchMessageListenerContainer 每组消费者数量
     */
    private int batchGroupSize = 2;

    public RocketMQThreadOptimizerProcessor() {
    }

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        return bean;
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        if (isOnsListenerContainer(bean.getClass())) {
            optimizeContainer(beanName, bean);
        }
        return bean;
    }

    /**
     * 应用关闭时打印分布情况
     */
    @PreDestroy
    public void printDistribution() {
        if (distributionMap.isEmpty()) {
            return;
        }
        
        log.info("========== RocketMQ Consumer 分布情况 ==========");
        distributionMap.forEach((instanceName, beanNames) -> {
            log.info("  {} ({} 个):", instanceName, beanNames.size());
            beanNames.forEach(name -> log.info("    - {}", name));
        });
        log.info("===============================================");
        log.info("总计: {} 个 MQClientInstance, {} 个 Consumer", 
                distributionMap.size(), 
                distributionMap.values().stream().mapToInt(List::size).sum());
    }

    /**
     * 检查类是否是 OnsMessageListenerContainer 或其子类
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
     */
    private void optimizeContainer(String beanName, Object container) {
        try {
            // 0. 获取容器类型
            ContainerType containerType = ContainerType.fromClass(container.getClass());
            if (containerType == null) {
                log.warn("⚠ [RocketMQ优化] Bean: {} 未知的容器类型: {}", beanName, container.getClass().getName());
                return;
            }

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

            // 5. 获取实例 ID
            String id = getInstanceId();

            // 6. 获取分组大小并计数
            int groupSize = getGroupSize(containerType);
            int currentCount = getCounter(containerType).getAndIncrement();

            // 7. 使用桶算法计算组号（在相同 nameServer+accessKey+type 范围内分桶）
            int groupNumber = calcBucketNumber(nameServerHash, accessKeyHash, containerType, groupSize);

            // 8. 生成 InstanceName
            String distinctInstanceName = id + "#" + nameServerHash + "#" + accessKeyHash
                    + "#" + containerType.getConfigKey() + "#" + groupNumber;

            // 9. 设置 instanceName 到 Properties 中
            properties.setProperty(PropertyKeyConst.InstanceName, distinctInstanceName);

            // 10. 记录分布情况
            distributionMap.computeIfAbsent(distinctInstanceName, k -> new ArrayList<>()).add(beanName);

            log.info("✓ [RocketMQ优化] {} -> 桶{} (类型: {}, 第{}个)", 
                    beanName, groupNumber, containerType.getConfigKey(), currentCount + 1);

        } catch (Exception e) {
            log.error("❌ [RocketMQ优化] Bean: {} 优化失败: {}", beanName, e.getMessage(), e);
        }
    }

    /**
     * 桶算法：随机起始 + 动态扩容
     * <p>
     * 设计思想：
     * 1. 按 nameServerHash + accessKeyHash + containerType 分组（只有这些都相同才能复用 MQClientInstance）
     * 2. 每组初始2个桶，随机选择起始桶，顺序查找未满的桶
     * 3. 当总使用量超过总容量70%时，自动增加一个桶
     * 4. 保证每桶严格不超过 groupSize
     *
     * @param nameServerHash nameServer 哈希值
     * @param accessKeyHash  accessKey 哈希值
     * @param containerType  容器类型
     * @param groupSize      每个桶的最大容量
     * @return 桶号
     */
    private synchronized int calcBucketNumber(int nameServerHash, int accessKeyHash, 
                                               ContainerType containerType, int groupSize) {
        // 生成桶状态的 key：相同 nameServer + accessKey + type 才能共享 MQClientInstance
        String stateKey = nameServerHash + "#" + accessKeyHash + "#" + containerType.getConfigKey();
        
        // 获取或创建桶状态
        BucketState state = bucketStates.computeIfAbsent(stateKey, 
                k -> new BucketState(INIT_BUCKETS, groupSize));

        // 检查是否需要扩容（使用超过70%）
        if (state.shouldExpand() && state.bucketCount < MAX_BUCKETS) {
            state.expand();
            log.info("📦 [RocketMQ优化] [{}] 桶扩容: {} -> {} 个桶", 
                    stateKey, state.bucketCount - 1, state.bucketCount);
        }

        // 随机选择起始桶
        int startBucket = random.nextInt(state.bucketCount);

        // 从起始桶开始，找第一个没满的桶
        for (int offset = 0; offset < state.bucketCount; offset++) {
            int bucketIndex = (startBucket + offset) % state.bucketCount;
            if (state.buckets[bucketIndex] < groupSize) {
                state.buckets[bucketIndex]++;
                state.totalUsed++;
                return bucketIndex;
            }
        }

        // 所有桶都满了，强制扩容并放入新桶
        if (state.bucketCount < MAX_BUCKETS) {
            state.expand();
            state.buckets[state.bucketCount - 1]++;
            state.totalUsed++;
            return state.bucketCount - 1;
        }

        // 极端情况：达到最大桶数，返回随机桶
        return startBucket;
    }

    /**
     * 获取实例 ID
     */
    private String getInstanceId() {
        return String.valueOf(UtilAll.getPid());
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

    /**
     * 桶状态类
     */
    private static class BucketState {
        int[] buckets;      // 每个桶的当前容量
        int bucketCount;    // 当前桶数量
        int totalUsed;      // 总使用量
        int groupSize;      // 每桶最大容量

        BucketState(int initCount, int groupSize) {
            this.buckets = new int[MAX_BUCKETS];
            this.bucketCount = initCount;
            this.totalUsed = 0;
            this.groupSize = groupSize;
        }

        /**
         * 是否应该扩容
         */
        boolean shouldExpand() {
            int totalCapacity = bucketCount * groupSize;
            return totalUsed >= totalCapacity * 0.7;
        }

        /**
         * 扩容：增加一个桶
         */
        void expand() {
            bucketCount++;
        }
    }

    /**
     * 容器类型枚举
     */
    private enum ContainerType {
        NORMAL("OnsMessageListenerContainer", "normal"),
        ORDER("OnsMessageOrderListenerContainer", "order"),
        BATCH("OnsBatchMessageListenerContainer", "batch");

        private final String className;
        private final String configKey;

        ContainerType(String className, String configKey) {
            this.className = className;
            this.configKey = configKey;
        }

        public static ContainerType fromClass(Class<?> clazz) {
            String simpleName = clazz.getSimpleName();
            for (ContainerType type : values()) {
                if (type.className.equals(simpleName)) {
                    return type;
                }
            }
            return null;
        }

        public String getConfigKey() {
            return configKey;
        }
    }
}
