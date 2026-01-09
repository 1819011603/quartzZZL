

## **RocketMQ 事务消息原理**

RocketMQ 事务消息分为 **三步**：

1. **半消息（Prepare）**：生产者先发送一条 "半消息"，此时消息存入 MQ，但消费者不能消费。
2. **本地事务（Local Transaction）**：生产者执行本地事务（如 MySQL 操作）。
3. **事务回查（Check & Commit/Rollback）**：
    - **如果本地事务成功** → 提交事务消息（MQ 消息可被消费）。
    - **如果本地事务失败** → 回滚事务消息（MQ 消息被丢弃）。
    - **如果 MQ 没有收到 commit/rollback** → RocketMQ 会调用 **事务回查方法**（check）确认事务状



在 RocketMQ 中处理 **多个 Topic 的事务消息**，且每个 Topic 对应不同的业务逻辑时，可以通过 **策略模式（Strategy Pattern）** 结合 Spring Boot 的依赖注入特性，实现 **按 Topic 动态路由到不同的处理逻辑**。以下是具体实现方案：

---

### **1. 定义策略接口与实现类**
#### （1）策略接口：定义事务处理逻辑
```java
public interface TransactionStrategy {
    /**
     * 执行本地事务
     */
    LocalTransactionState executeLocalTransaction(Message msg, Object arg);

    /**
     * 事务状态回查
     */
    LocalTransactionState checkLocalTransaction(MessageExt msg);
}
```

#### （2）针对不同 Topic 的具体策略实现
- **订单事务处理器**（处理 `order_topic`）
```java
@Component
@TopicHandler(topic = "order_topic") // 自定义注解标记 Topic
public class OrderTransactionStrategy implements TransactionStrategy {
    @Override
    public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        // 订单业务逻辑：扣减库存、创建订单等
        boolean success = orderService.createOrder(msg.getKeys());
        return success ? LocalTransactionState.COMMIT_MESSAGE : LocalTransactionState.ROLLBACK_MESSAGE;
    }

    @Override
    public LocalTransactionState checkLocalTransaction(MessageExt msg) {
        boolean isOrderSuccess = orderService.checkOrderStatus(msg.getKeys());
        return isOrderSuccess ? LocalTransactionState.COMMIT_MESSAGE : LocalTransactionState.ROLLBACK_MESSAGE;
    }
}
```

- **日志事务处理器**（处理 `log_topic`）
```java
@Component
@TopicHandler(topic = "log_topic")
public class LogTransactionStrategy implements TransactionStrategy {
    @Override
    public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        // 日志业务逻辑：写入审计日志
        boolean success = logService.saveAuditLog(msg.getBody());
        return success ? LocalTransactionState.COMMIT_MESSAGE : LocalTransactionState.ROLLBACK_MESSAGE;
    }

    @Override
    public LocalTransactionState checkLocalTransaction(MessageExt msg) {
        boolean isLogSaved = logService.isLogSaved(msg.getMsgId());
        return isLogSaved ? LocalTransactionState.COMMIT_MESSAGE : LocalTransactionState.ROLLBACK_MESSAGE;
    }
}
```

---

### **2. 策略工厂：动态路由不同 Topic 的策略**
#### （1）自定义注解 `@TopicHandler`
```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface TopicHandler {
    String topic(); // 绑定的 Topic 名称
}
```

#### （2）策略工厂类（自动注入所有策略）
```java
@Component
public class TransactionStrategyFactory {
    private final Map<String, TransactionStrategy> strategyMap = new ConcurrentHashMap<>();

    // 通过 Spring 注入所有策略 Bean，并建立 Topic 与策略的映射
    @Autowired
    public void initStrategies(List<TransactionStrategy> strategies) {
        for (TransactionStrategy strategy : strategies) {
            TopicHandler annotation = strategy.getClass().getAnnotation(TopicHandler.class);
            if (annotation != null) {
                strategyMap.put(annotation.topic(), strategy);
            }
        }
    }

    // 根据 Topic 获取策略
    public TransactionStrategy getStrategy(String topic) {
        return strategyMap.get(topic);
    }
}
```

---

### **3. 统一事务监听器（基于策略模式路由）**
```java
@Component
public class GlobalTransactionListener implements TransactionListener {
    @Autowired
    private TransactionStrategyFactory strategyFactory;

    @Override
    public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        // 根据消息的 Topic 获取对应策略
        TransactionStrategy strategy = strategyFactory.getStrategy(msg.getTopic());
        if (strategy == null) {
            // 无匹配策略，默认回滚
            return LocalTransactionState.ROLLBACK_MESSAGE;
        }
        return strategy.executeLocalTransaction(msg, arg);
    }

    @Override
    public LocalTransactionState checkLocalTransaction(MessageExt msg) {
        TransactionStrategy strategy = strategyFactory.getStrategy(msg.getTopic());
        if (strategy == null) {
            return LocalTransactionState.ROLLBACK_MESSAGE;
        }
        return strategy.checkLocalTransaction(msg);
    }
}
```

---

### **4. 配置 RocketMQ 生产者**
在 Spring Boot 中配置多个生产者（每个 Topic 一个生产者）：
```java
@Configuration
public class RocketMQConfig {
    // 订单生产者（发送到 order_topic）
    @Bean(name = "orderProducer")
    public TransactionMQProducer orderProducer(GlobalTransactionListener listener) {
        TransactionMQProducer producer = new TransactionMQProducer("order_producer_group");
        producer.setNamesrvAddr("localhost:9876");
        producer.setTransactionListener(listener); // 使用统一监听器
        producer.start();
        return producer;
    }

    // 日志生产者（发送到 log_topic）
    @Bean(name = "logProducer")
    public TransactionMQProducer logProducer(GlobalTransactionListener listener) {
        TransactionMQProducer producer = new TransactionMQProducer("log_producer_group");
        producer.setNamesrvAddr("localhost:9876");
        producer.setTransactionListener(listener);
        producer.start();
        return producer;
    }
}
```

---

### **5. 业务层调用示例**
发送订单事务消息：
```java
@Service
public class OrderService {
    @Autowired
    @Qualifier("orderProducer")
    private TransactionMQProducer orderProducer;

    public void createOrder(String orderId) {
        Message msg = new Message("order_topic", "order_tag", orderId, "订单数据".getBytes());
        try {
            orderProducer.sendMessageInTransaction(msg, null);
        } catch (MQClientException e) {
            e.printStackTrace();
        }
    }
}
```

发送日志事务消息：
```java
@Service
public class LogService {
    @Autowired
    @Qualifier("logProducer")
    private TransactionMQProducer logProducer;

    public void saveAuditLog(String logContent) {
        Message msg = new Message("log_topic", "log_tag", "log_123", logContent.getBytes());
        try {
            logProducer.sendMessageInTransaction(msg, null);
        } catch (MQClientException e) {
            e.printStackTrace();
        }
    }
}
```

---

### **6. 设计优势**
1. **解耦与扩展性**：
   - 新增 Topic 时，只需添加新的 `TransactionStrategy` 实现类并标记 `@TopicHandler`，无需修改已有代码。
   - 各策略类的业务逻辑相互独立，符合开闭原则（OCP）。

2. **动态路由**：
   - 通过 `TransactionStrategyFactory` 自动管理策略映射，运行时根据 Topic 动态选择处理器。

3. **统一事务管理**：
   - `GlobalTransactionListener` 作为统一入口，简化 RocketMQ 事务监听器的配置。

---

### **7. 注意事项**
- **异常处理**：在策略工厂中未找到对应 Topic 的策略时，建议记录错误日志并返回 `ROLLBACK_MESSAGE`，避免消息悬挂。
- **性能优化**：如果 Topic 数量较多，可使用缓存（如 Caffeine）优化策略查找效率。
- **事务幂等性**：确保每个策略的本地事务逻辑是幂等的，防止消息重复投递导致数据不一致。

通过上述方案，可以实现 **多 Topic 事务消息的灵活管理**，适用于复杂业务场景（如电商、金融、物流等），同时保持代码的清晰和可维护性。