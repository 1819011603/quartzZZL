package com.gaotu.student.data.facade.config;

/**
 * @author: zhangzeling
 * @date: 2026/1/28
 * @description: RocketMQThreadOptimizerProcessor
 */

import com.aliyun.openservices.ons.api.PropertyKeyConst;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.rocketmq.common.UtilAll;
import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanPostProcessor;
import org.springframework.context.ApplicationContext;
import org.springframework.context.ApplicationContextAware;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.Ordered;
import org.springframework.core.PriorityOrdered;

import javax.annotation.PreDestroy;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.*;
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
public class RocketMQThreadOptimizerProcessor implements BeanPostProcessor, PriorityOrdered, ApplicationContextAware {

    /**
     * OnsMessageListenerContainer 类名前缀
     */
    private static final String ONS_CONTAINER_PREFIX = "com.gaotu.arch.ons.config.Ons";

    /**
     * 最大桶数量（默认值）
     */
    private static final int DEFAULT_MAX_BUCKETS = 64;

    /**
     * 初始桶数量（默认值）
     */
    private static final int DEFAULT_INIT_BUCKETS = 3;
    
    /**
     * 桶扩容阈值（默认值：70%）
     */
    private static final double DEFAULT_EXPAND_THRESHOLD = 0.7;

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
     * OnsMessageListenerContainer 每组消费者数量（默认值）
     */
    private static final int DEFAULT_NORMAL_GROUP_SIZE = 3;

    /**
     * OnsMessageOrderListenerContainer 每组消费者数量（默认值）
     */
    private static final int DEFAULT_ORDER_GROUP_SIZE = 2;

    /**
     * OnsBatchMessageListenerContainer 每组消费者数量（默认值）
     */
    private static final int DEFAULT_BATCH_GROUP_SIZE = 2;

    /**
     * 排除列表缓存（懒加载）
     */
    private volatile Set<String> excludeList = null;

    /**
     * 包含列表缓存（懒加载）
     */
    private volatile Set<String> includeList = null;

    /**
     * 总开关缓存
     */
    private volatile Boolean enabled = null;

    public RocketMQThreadOptimizerProcessor() {
    }

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        return bean;
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        // 检查总开关
        if (!isEnabled()) {
            return bean;
        }
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
     * 获取容器类型对应的分组大小（从 Apollo 读取）
     */
    private int getGroupSize(ContainerType type) {
        switch (type) {
            case NORMAL:
                return getConfigValue("rocketmq.optimizer.normal.groupSize", DEFAULT_NORMAL_GROUP_SIZE);
            case ORDER:
                return getConfigValue("rocketmq.optimizer.order.groupSize", DEFAULT_ORDER_GROUP_SIZE);
            case BATCH:
                return getConfigValue("rocketmq.optimizer.batch.groupSize", DEFAULT_BATCH_GROUP_SIZE);
            default:
                return DEFAULT_NORMAL_GROUP_SIZE;
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

            // 0.1 检查是否在排除列表中
            if (isExcluded(beanName)) {
                log.info("⊘ [RocketMQ优化] Bean: {} 在排除列表中，跳过优化", beanName);
                return;
            }

            // 0.2 检查是否在包含列表中（如果包含列表不为空）
            if (!isIncluded(beanName)) {
                log.info("⊘ [RocketMQ优化] Bean: {} 不在包含列表中，跳过优化", beanName);
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
     * 2. 每组初始N个桶，随机选择起始桶，顺序查找未满的桶
     * 3. 当总使用量超过总容量阈值时，自动增加一个桶
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
        // 从 Apollo 读取配置
        int maxBuckets = getConfigValue("rocketmq.optimizer.maxBuckets", DEFAULT_MAX_BUCKETS);
        int initBuckets = getConfigValue("rocketmq.optimizer.initBuckets", DEFAULT_INIT_BUCKETS);
        double expandThreshold = getConfigDoubleValue("rocketmq.optimizer.expandThreshold", DEFAULT_EXPAND_THRESHOLD);
        
        // 生成桶状态的 key：相同 nameServer + accessKey + type 才能共享 MQClientInstance
        String stateKey = nameServerHash + "#" + accessKeyHash + "#" + containerType.getConfigKey();
        
        // 获取或创建桶状态
        BucketState state = bucketStates.computeIfAbsent(stateKey, 
                k -> new BucketState(initBuckets, groupSize, maxBuckets, expandThreshold));

        // 检查是否需要扩容
        if (state.shouldExpand() && state.bucketCount < state.maxBuckets) {
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
        if (state.bucketCount < state.maxBuckets) {
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

    private ApplicationContext applicationContext;

    @Override
    public void setApplicationContext(ApplicationContext ctx) {
        this.applicationContext = ctx;
    }

    private int getConfigValue(String key, int defaultValue) {
        // ✅ 通过 ApplicationContext 获取 Environment
        return applicationContext.getEnvironment()
                .getProperty(key, Integer.class, defaultValue);
    }

    /**
     * 从 Apollo 获取 Double 类型配置
     */
    private double getConfigDoubleValue(String key, double defaultValue) {
        // ✅ 通过 ApplicationContext 获取 Environment
        return applicationContext.getEnvironment()
                .getProperty(key, Double.class, defaultValue);
    }

    /**
     * 检查优化器是否启用（懒加载 + 缓存）
     */
    private boolean isEnabled() {
        if (enabled == null) {
            synchronized (this) {
                if (enabled == null) {
                    enabled = applicationContext.getEnvironment()
                            .getProperty("rocketmq.optimizer.enabled", Boolean.class, true);
                    
                    if (!enabled) {
                        log.info("⊘ [RocketMQ优化] 优化器已禁用");
                    }
                }
            }
        }
        return enabled;
    }

    /**
     * 获取排除列表（懒加载 + 缓存）
     */
    private Set<String> getExcludeList() {
        if (excludeList == null) {
            synchronized (this) {
                if (excludeList == null) {
                    String excludeConfig = applicationContext.getEnvironment()
                            .getProperty("rocketmq.optimizer.exclude", String.class, "");
                    
                    if (excludeConfig.trim().isEmpty()) {
                        excludeList = new HashSet<>();
                    } else {
                        // 支持逗号分隔的多个排除项
                        String[] items = excludeConfig.split(",");
                        excludeList = new HashSet<>();
                        for (String item : items) {
                            String trimmed = item.trim();
                            if (!trimmed.isEmpty()) {
                                // 首字母大写
                                excludeList.add(StringUtils.capitalize(trimmed));
                            }
                        }
                    }
                    
                    if (!excludeList.isEmpty()) {
                        log.info("✓ [RocketMQ优化] 排除列表已加载: {}", excludeList);
                    }
                }
            }
        }
        return excludeList;
    }

    /**
     * 检查 beanName 是否在排除列表中
     * 只要 beanName contains 排除项，就返回 true
     */
    private boolean isExcluded(String beanName) {
        Set<String> set = getExcludeList();
        String[] beanNames = beanName.split("_");
        if (beanName.length() <= 1 || set.isEmpty()) {
            return false;
        }

        return set.contains(StringUtils.capitalize(beanNames[0]));
    }

    /**
     * 获取包含列表（懒加载 + 缓存）
     */
    private Set<String> getIncludeList() {
        if (includeList == null) {
            synchronized (this) {
                if (includeList == null) {
                    String includeConfig = applicationContext.getEnvironment()
                            .getProperty("rocketmq.optimizer.include", String.class, "");
                    
                    if (includeConfig.trim().isEmpty()) {
                        includeList = new HashSet<>();
                    } else {
                        // 支持逗号分隔的多个包含项
                        String[] items = includeConfig.split(",");
                        includeList = new HashSet<>();
                        for (String item : items) {
                            String trimmed = item.trim();
                            if (!trimmed.isEmpty()) {
                                // 首字母大写
                                includeList.add(StringUtils.capitalize(trimmed));
                            }
                        }
                    }
                    
                    if (!includeList.isEmpty()) {
                        log.info("✓ [RocketMQ优化] 包含列表已加载: {}", includeList);
                    }
                }
            }
        }
        return includeList;
    }

    /**
     * 检查 beanName 是否在包含列表中
     * 如果包含列表为空，返回 true（不限制）
     * 如果包含列表不为空，只有 beanName contains 包含项时才返回 true
     */
    private boolean isIncluded(String beanName) {
        Set<String> set = getIncludeList();
        
        // 包含列表为空，不限制，全部允许
        if (set.isEmpty()) {
            return true;
        }
        
        String[] beanNames = beanName.split("_");
        if (beanNames.length <= 1) {
            return false;
        }

        return set.contains(StringUtils.capitalize(beanNames[0]));
    }

    /**
     * 桶状态类
     */
    private static class BucketState {
        int[] buckets;      // 每个桶的当前容量
        int bucketCount;    // 当前桶数量
        int totalUsed;      // 总使用量
        int groupSize;      // 每桶最大容量
        int maxBuckets;     // 最大桶数量
        double expandThreshold;  // 扩容阈值

        BucketState(int initCount, int groupSize, int maxBuckets, double expandThreshold) {
            this.buckets = new int[maxBuckets];
            this.bucketCount = initCount;
            this.totalUsed = 0;
            this.groupSize = groupSize;
            this.maxBuckets = maxBuckets;
            this.expandThreshold = expandThreshold;
        }

        /**
         * 是否应该扩容
         */
        boolean shouldExpand() {
            int totalCapacity = bucketCount * groupSize;
            return totalUsed >= totalCapacity * expandThreshold;
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
