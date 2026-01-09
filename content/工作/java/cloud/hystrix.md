

### HystrixCircuitBreaker 断路器


HystrixCommandProperties HystrixCommand实例的属性。 





#### com.netflix.config.PropertyWrapper

包含一个DynamicProperty和一个默认值

DynamicIntProperty
DynamicStringProperty
DynamicBooleanProperty
DynamicFloatProperty
DynamicLongProperty
DynamicDoubleProperty
都是它的子类, 只是重写了get方法.


####  com.netflix.config.DynamicProperty

CachedValue用来解析stringValue值,  属性名为stringValue  命令模式对不同类型进行解析, 可以解析的返回对应的value, 不可以解析的就记录异常进行抛出, 并对解析结果缓存.



CachedValu利用非静态内部类保存主类的引用, 可以直接访问主类的属性特点 进行解析stringValue字段








### HystrixMetrics  com.netflix.hystrix.HystrixMetrics


**HystrixRollingNumber 可用于随时间跟踪计数器 (增量) 或设置值的数字**

LongMaxUpdater 是一种用于追踪多个线程产生的值中的**最大值**的工具，类似于计数器，但它记录的是值的最大值而不是总和或次数

```java
LongMaxUpdater maxUpdater = new LongMaxUpdater();
maxUpdater.update(10);
maxUpdater.update(20);
System.out.println(maxUpdater.max()); // 输出20
```


com.netflix.hystrix.util.HystrixRollingNumberEvent + com.netflix.hystrix.util.HystrixRollingNumber.Bucket
type == 1 计算总和
type == 2 计算最大值


Bucket:  给定时间 “桶” 的计数器。
CumulativeSum: 每种类型的累积计数器 (从JVM开始) 




### 单例 懒加载

```java

public final class HystrixDynamicPropertiesSystemProperties {  
    /**  
     * Only public for unit test purposes.     */    public HystrixDynamicPropertiesSystemProperties() {}  
    private static class LazyHolder {  
        private static final HystrixDynamicPropertiesSystemProperties INSTANCE = new HystrixDynamicPropertiesSystemProperties();  
    }  
    public static HystrixDynamicProperties getInstance() {  
        return LazyHolder.INSTANCE;  
    }
}
```