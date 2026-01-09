EagleEye-TraceID  无法通过MDC进行设置。  使用 TraceCrossThread 注解解决


![[../../壁纸/附件/Pasted image 20240401160417.png]]
![[../../壁纸/附件/Pasted image 20240401160435.png]]




```java
package com.baijia.storm.earth.windows.util;  
  
import lombok.extern.slf4j.Slf4j;  
import org.apache.commons.lang3.StringUtils;  
import org.slf4j.MDC;  
  
import java.util.Map;  
import java.util.concurrent.*;  
import java.util.concurrent.atomic.AtomicInteger;  
  
/**  
 * @Author: zhangjiaming  
 * @Date: 2021-05-17  
 * @Desc  
 */  
@Slf4j  
public class ThreadPoolUtil {  
  
    public static ThreadPoolExecutor getThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime,  
                                                           TimeUnit unit, int queueSize, AtomicInteger counter, String source) {  
        return getThreadPoolExecutor(corePoolSize, maximumPoolSize, keepAliveTime, unit, new ArrayBlockingQueue<>(queueSize), counter, source);  
    }  
  
  
    /**  
     * 重写方法 使得可以跟踪主线程的traceId  
     *     * @param corePoolSize  
     * @param maximumPoolSize  
     * @param keepAliveTime  
     * @param unit  
     * @param workQueue  
     * @param counter  
     * @param source  
     * @return  
     */  
    public static ThreadPoolExecutor getThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime,  
                                                           TimeUnit unit, BlockingQueue<Runnable> workQueue, AtomicInteger counter, String source) {  
        final String sourceStr = StringUtils.isBlank(source) ? "线程池" : source;  
        return new MDCThreadPoolExecutor(corePoolSize, maximumPoolSize, keepAliveTime  
                , unit, workQueue,  
                runnable -> new Thread(runnable, sourceStr + "_" + counter.getAndIncrement()),  
                (runnable, executor) ->  
                        log.error("{}阻塞队列已满!!!,activeCount:{},corePoolSize:{},poolSize:{}.maximumPoolSize:{},queueSize:{}",  
                                sourceStr, executor.getActiveCount(), executor.getCorePoolSize(), executor.getPoolSize(),  
                                executor.getMaximumPoolSize(), executor.getQueue().size())  
        );  
    }  
  
    private static ScheduledThreadPoolExecutor getScheduledThreadPoolExecutor(int corePoolSize, AtomicInteger counter, String source, boolean needTrace) {  
        final String sourceStr = StringUtils.isBlank(source) ? "线程池" : source;  
        ScheduledThreadPoolExecutor scheduledThreadPoolExecutor = new MDCScheduleThreadPoolExecutor(corePoolSize, runnable -> new Thread(runnable, sourceStr + "_" + counter.getAndIncrement()),  
                (runnable, executor) ->  
                        log.error("{}定时任务拒绝执行!!!,activeCount:{},corePoolSize:{},poolSize:{}.maximumPoolSize:{},queueSize:{}",  
                                sourceStr, executor.getActiveCount(), executor.getCorePoolSize(), executor.getPoolSize(),  
                                executor.getMaximumPoolSize(), executor.getQueue().size()), needTrace);  
        // 设置过期时间  
        scheduledThreadPoolExecutor.setKeepAliveTime(20, TimeUnit.SECONDS);  
        scheduledThreadPoolExecutor.allowCoreThreadTimeOut(true);  
        return scheduledThreadPoolExecutor;  
    }  
  
    /**  
     * 会跟踪主线程的traceId， 不会自动生成tracId， 专门处理延时任务的线程池  
     *  
     * @param corePoolSize  
     * @param counter  
     * @param source  
     * @return  
     */  
    public static ScheduledThreadPoolExecutor getScheduledThreadPoolExecutor(int corePoolSize, AtomicInteger counter, String source) {  
        return getScheduledThreadPoolExecutor(corePoolSize, counter, source, true);  
    }  
  
    /**  
     * 不会跟踪主线程的traceId 自动生成traceId  专门处理定时任务的线程池  
     */  
    public static ScheduledThreadPoolExecutor getScheduledThreadPoolExecutorNoTraceId(int corePoolSize, AtomicInteger counter, String source) {  
        return getScheduledThreadPoolExecutor(corePoolSize, counter, source, false);  
    }  
  
    public static Runnable wrap(final Runnable runnable) {  
        return wrap(runnable, MDC.getCopyOfContextMap());  
    }  
  
    public static <T> Callable<T> wrap(final Callable<T> runnable) {  
        return wrap(runnable, MDC.getCopyOfContextMap());  
    }  
  
  
    public static Runnable wrap(final Runnable runnable, final Map<String, String> context) {  
        return () -> {  
            if (context == null) {  
                MDC.clear();  
            } else {  
                MDC.setContextMap(context);  
            }  
            if (StringUtils.isBlank(TraceIdUtil.getTraceId())) {  
                TraceIdUtil.setTraceId();  
            }  
            try {  
                runnable.run();  
            } finally {  
                MDC.clear();  
            }  
        };  
    }  
  
    public static <T> Callable<T> wrap(final Callable<T> callable, final Map<String, String> context) {  
        return () -> {  
            // 实际执行前导入对应请求的MDC副本  
            if (context == null) {  
                MDC.clear();  
            } else {  
                MDC.setContextMap(context);  
            }  
            if (StringUtils.isBlank(TraceIdUtil.getTraceId())) {  
                TraceIdUtil.setTraceId();  
            }  
            try {  
                return callable.call();  
            } finally {  
                MDC.clear();  
            }  
        };  
    }  
  
  
}
```


```java
package com.baijia.storm.earth.windows.util;  
  
import cn.hutool.core.util.RandomUtil;  
import lombok.AllArgsConstructor;  
import lombok.Data;  
import lombok.Setter;  
import lombok.extern.slf4j.Slf4j;  
  
import java.util.concurrent.*;  
import java.util.concurrent.atomic.AtomicInteger;  
import java.util.concurrent.atomic.LongAdder;  
  
/**  
 * @author: zhangzeling  
 * @date: 2023/12/11  
 * @description: MDCThreadPoolExecutor  
 */@Slf4j  
public class MDCThreadPoolExecutor extends ThreadPoolExecutor {  
  
    private static long tenSecondsMills = TimeUnit.SECONDS.toMillis(10L);  
  
    private volatile long lastCompletedTaskTime = System.currentTimeMillis();  
    protected ConcurrentLinkedQueue<TaskTimeInfo> timeConsumerQueue = new ConcurrentLinkedQueue<>();  
    private boolean needTrace = true;  
  
    protected LongAdder totalCostTime = new LongAdder();  
  
    private long lastCostTime = 0;  
  
    private int lastQueueSize = 0;  
  
    private static int windowSize = 1000;  
  
    private int lastTimeQueueSize = 1000;  
    private int timeConsumerQueueSize = 0;  
    private long lastCreateTime = System.currentTimeMillis();  
  
  
    private String name;  
    public MDCThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime, TimeUnit unit, BlockingQueue<Runnable> workQueue) {  
        super(corePoolSize, maximumPoolSize, keepAliveTime, unit, workQueue);  
    }  
  
    public MDCThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime, TimeUnit unit, BlockingQueue<Runnable> workQueue, ThreadFactory threadFactory) {  
        super(corePoolSize, maximumPoolSize, keepAliveTime, unit, workQueue, threadFactory);  
    }  
  
    public MDCThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime, TimeUnit unit, BlockingQueue<Runnable> workQueue, RejectedExecutionHandler handler) {  
        super(corePoolSize, maximumPoolSize, keepAliveTime, unit, workQueue, handler);  
    }  
  
    public MDCThreadPoolExecutor(int corePoolSize, int maximumPoolSize, long keepAliveTime, TimeUnit unit, BlockingQueue<Runnable> workQueue, ThreadFactory threadFactory, RejectedExecutionHandler handler) {  
        super(corePoolSize, maximumPoolSize, keepAliveTime, unit, workQueue, threadFactory, handler);  
    }  
  
    @Override  
    protected void afterExecute(Runnable r, Throwable t) {  
        super.afterExecute(r,t);  
    }  
  
    public boolean isIdleFor(long duration, TimeUnit unit) {  
        return System.currentTimeMillis() - lastCompletedTaskTime > unit.toMillis(duration);  
    }  
  
    private boolean needIncreaseThread(int min,int max ) {  
        while (timeConsumerQueue.size() > windowSize || (timeConsumerQueue.size() > 0 && System.currentTimeMillis()-timeConsumerQueue.peek().getStartTime() > tenSecondsMills)) {  
            MDCThreadPoolExecutor.TaskTimeInfo poll = timeConsumerQueue.poll();  
            totalCostTime.add(-poll.getCostTime());  
        }  
        timeConsumerQueueSize = timeConsumerQueue.size();  
        if (timeConsumerQueueSize == 0) {  
            return false;  
        }  
        long nowCostTime = totalCostTime.longValue() / timeConsumerQueueSize;  
        int queueSize = getQueue().size();  
        try {  
            int corePoolSize = getCorePoolSize();  
            int activeCount = getActiveCount();  
            boolean result = (queueSize * nowCostTime >  200  && lastQueueSize < queueSize) ||  queueSize >= corePoolSize  && nowCostTime > 10 && ((nowCostTime * queueSize / (getPoolSize() + 1) > 500)  || (nowCostTime > 2 * lastCostTime && lastCostTime > 10) || nowCostTime > 200 || queueSize > 50 || timeConsumerQueueSize > 100);  
            log.info("{},nowCostTime:{}, lastCostTime:{}, queueSize:{}, lastQueueSize:{} , timeConsumerQueueSize:{} ,lastTimeQueueSize:{}, getCorePoolSize :{}, activeCount:{}, result:{}", this.name,nowCostTime,lastCostTime, queueSize, lastQueueSize,timeConsumerQueueSize,lastTimeQueueSize, corePoolSize, activeCount,result);  
            return result;  
        } finally {  
            lastCostTime = nowCostTime;  
            lastQueueSize = queueSize;  
        }  
    }  
  
    public void adjustCorePoolSize(boolean needPrint, int min, int max, String name) {  
        this.name = name;  
        int preCorePoolSize = getCorePoolSize();  
        int queueSize = getQueue().size();  
        if (needIncreaseThread(min,max)) {  
            long nowCostTime = totalCostTime.longValue() / timeConsumerQueueSize;  
            int addNum = (int)( queueSize * nowCostTime / 500L - preCorePoolSize);  
            log.info("addNum:{}, preCorePoolSize:{}",addNum, preCorePoolSize);  
            int coreSize = Math.min(max, preCorePoolSize + Math.min(Math.max(preCorePoolSize/2,1), Math.max(addNum,0)));  
            setCorePoolSize(coreSize);  
            setMaximumPoolSize(max);  
            try {  
                allowCoreThreadTimeOut(false);  
            } catch (Exception e) {  
            }            lastCreateTime = System.currentTimeMillis();  
        } else{  
            int coreSize = Math.max(min, (preCorePoolSize + 1) / 2);  
            if (TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis()-lastCreateTime) > 30 && getActiveCount() * 2 <= preCorePoolSize && 1.1 * lastTimeQueueSize >= timeConsumerQueueSize) {  
                setCorePoolSize(coreSize);  
                setMaximumPoolSize(preCorePoolSize);  
            }  
            try {  
                allowCoreThreadTimeOut(true);  
            } catch (Exception e) {  
            }            lastCreateTime = System.currentTimeMillis();  
        }  
  
        if (needPrint) {  
            log.info("{}的线程池先前的核心线程数为:{}, 更新后核心线程数为: {}, 当前线程数: {}, 当前队列中任务数:{}, allowCoreThreadTimeOut:{} ", name, preCorePoolSize, getCorePoolSize()  
                    , getPoolSize(), queueSize, allowsCoreThreadTimeOut());  
        }  
        lastTimeQueueSize = timeConsumerQueueSize;  
    }  
  
  
  
  
    @Override  
    public <T> Future<T> submit(Callable<T> task) {  
        return super.submit(wrapTest(task));  
    }  
  
    @Override  
    public Future<?> submit(Runnable task) {  
        return super.submit(wrapTest(task));  
    }  
  
    @Override  
    public void execute(Runnable command) {  
        super.execute(wrapTest(command));  
    }  
  
    public  <T> Callable<T> wrapTest(final Callable<T> runnable) {  
        return new ScheduledCallableWrapper<>(runnable, TraceIdUtil.getTraceId());  
    }  
  
  
    public  <T> Callable<T> wrapTest(final Callable<T> runnable, final String traceId) {  
        return new ScheduledCallableWrapper<>(runnable, traceId);  
    }  
  
    public  Runnable wrapTest(final Runnable runnable, final String traceId) {  
        return new ScheduledRunnableWrapper(runnable, traceId);  
    }  
  
    public  Runnable wrapTest(final Runnable runnable) {  
        return new ScheduledRunnableWrapper(runnable, TraceIdUtil.getTraceId());  
    }  
  
  
  
    private  class  ScheduledRunnableWrapper extends RunnableWrapper {  
        public ScheduledRunnableWrapper(Runnable r, String traceId) {  
            super(r, traceId);  
        }  
        @Override  
        public void run() {  
            try {  
                super.run();  
            }finally {  
                lastCompletedTaskTime = System.currentTimeMillis();  
                long costTime = lastCompletedTaskTime - createTime;  
                totalCostTime.add(costTime);  
                timeConsumerQueue.add(new TaskTimeInfo(lastCompletedTaskTime, costTime));  
            }  
        }  
  
    }  
  
    private  class  ScheduledCallableWrapper<T> extends CallableWrapper<T> {  
        public ScheduledCallableWrapper(Callable<T> r, String traceId) {  
            super(r, traceId);  
        }  
  
        @Override  
        public T call() throws Exception {  
            try {  
                return super.call();  
            }finally {  
                lastCompletedTaskTime = System.currentTimeMillis();  
                long costTime = lastCompletedTaskTime - createTime;  
                totalCostTime.add(costTime);  
                timeConsumerQueue.add(new TaskTimeInfo(lastCompletedTaskTime, costTime));  
            }  
        }  
  
    }  
  
    static class CallableWrapper<T> implements Callable<T> {  
        private final Callable<T> runnable;  
        private String traceId;  
        public long createTime;  
        public long taskStartTime;  
  
        public CallableWrapper(Callable<T> r, String traceId) {  
  
            runnable = r;  
  
            this.traceId = traceId;  
            createTime = System.currentTimeMillis();  
  
  
        }  
  
  
        @Override  
        public T call() throws Exception {  
            try {  
                taskStartTime = System.currentTimeMillis();  
                TraceIdUtil.setTraceId(traceId);  
                return runnable.call();  
            } finally {  
                TraceIdUtil.removeTraceId();  
            }  
        }  
    }  
  
    static class RunnableWrapper implements Runnable {  
        private Runnable runnable;  
        private String traceId;  
        public long createTime;  
        public long taskStartTime;  
  
  
        public RunnableWrapper(Runnable r, String traceId) {  
            runnable = r;  
            this.traceId = traceId;  
            createTime = System.currentTimeMillis();  
        }  
  
  
        @Override  
        public void run() {  
            try {  
                taskStartTime = System.currentTimeMillis();  
                TraceIdUtil.setTraceId(traceId);  
                runnable.run();  
            } finally {  
                TraceIdUtil.removeTraceId();  
            }  
        }  
    }  
  
  
    @Data  
    @AllArgsConstructor    public static class TaskTimeInfo {  
        private long startTime;  
  
        /**  
         * 普通线程池计算 执行时间+排队时间  
         * schedule线程池 计算执行时间  
         */  
        private long costTime;  
    }  
  
    private static void test(MDCThreadPoolExecutor executor) {  
        new Thread(()->{  
            while (true) {  
  
                for (int i1 = 2; i1 <  (executor.getCorePoolSize()!=16?RandomUtil.randomInt(5,100):RandomUtil.randomInt(2,5)); i1+=RandomUtil.randomInt(1,5)) {  
                    for (int i = 0; i < i1; i++) {  
                        executor.submit(()->{  
                            try {  
                                TimeUnit.MILLISECONDS.sleep(RandomUtil.randomInt(4,8));  
                                if ( RandomUtil.randomInt(9, 30) % 3<=0) {  
                                    TimeUnit.MILLISECONDS.sleep(RandomUtil.randomInt(50,100));  
                                }  
                            } catch (InterruptedException e) {  
                                throw new RuntimeException(e);  
                            }  
                        });  
                    }  
                    try {  
                        TimeUnit.MILLISECONDS.sleep(100);  
                    } catch (InterruptedException e) {  
                        throw new RuntimeException(e);  
                    }  
                }  
            }  
        }).start();  
    }  
  
    public static void main(String[] args) {  
        MDCThreadPoolExecutor mdcThreadPoolExecutor = (MDCThreadPoolExecutor) ThreadPoolUtil.getThreadPoolExecutor(4,50,60L,TimeUnit.SECONDS,1000,new AtomicInteger(),"test");  
        test(mdcThreadPoolExecutor);  
        new Thread(()->{  
            while (true) {  
                mdcThreadPoolExecutor.adjustCorePoolSize(true,4,50, "hhh");  
                try {  
                    TimeUnit.SECONDS.sleep(1);  
                } catch (InterruptedException e) {  
                    throw new RuntimeException(e);  
                }  
  
            }  
        }).start();  
    }  
}
```


```java

package com.baijia.storm.earth.windows.util;  
  
import cn.hutool.core.util.RandomUtil;  
import lombok.extern.slf4j.Slf4j;  
  
import java.util.concurrent.*;  
import java.util.concurrent.atomic.AtomicInteger;  
import java.util.concurrent.atomic.LongAdder;  
  
/**  
 * @author: zhangzeling  
 * @date: 2023/12/11  
 * @description: MDCThreadPoolExecutor  
 */@Slf4j  
public class MDCScheduleThreadPoolExecutor extends ScheduledThreadPoolExecutor {  
  
    private static long tenSecondsMills = TimeUnit.SECONDS.toMillis(10L);  
    private static int windowSize = 1000;  
    protected ConcurrentLinkedQueue<MDCThreadPoolExecutor.TaskTimeInfo> timeConsumerQueue = new ConcurrentLinkedQueue<>();  
    protected LongAdder totalCostTime = new LongAdder();  
    private volatile long lastCompletedTaskTime = System.currentTimeMillis();  
    private boolean needTrace = true;  
    private long lastCostTime = 0;  
    private int lastQueueSize = 0;  
    private int lastTimeQueueSize = 1000;  
  
    private int timeConsumerQueueSize = 0;  
  
    private long lastCreateTime = System.currentTimeMillis();  
  
  
    private String name;  
  
    public MDCScheduleThreadPoolExecutor(int corePoolSize) {  
        super(corePoolSize);  
    }  
  
    public MDCScheduleThreadPoolExecutor(int corePoolSize, ThreadFactory threadFactory) {  
        super(corePoolSize, threadFactory);  
    }  
  
  
    public MDCScheduleThreadPoolExecutor(int corePoolSize, RejectedExecutionHandler handler) {  
        super(corePoolSize, handler);  
    }  
  
    public MDCScheduleThreadPoolExecutor(int corePoolSize, ThreadFactory threadFactory, RejectedExecutionHandler handler) {  
        super(corePoolSize, threadFactory, handler);  
    }  
  
    public MDCScheduleThreadPoolExecutor(int corePoolSize, ThreadFactory threadFactory, RejectedExecutionHandler handler, boolean needTrace) {  
        super(corePoolSize, threadFactory, handler);  
        this.needTrace = needTrace;  
    }  
  
    @Override  
    public ScheduledFuture<?> schedule(Runnable command, long delay, TimeUnit unit) {  
        long scheTime = delay > 1e7 ? delay - System.currentTimeMillis() : delay;  
        return super.schedule(needTrace ? wrapTest(command) : wrapTest(command, null), scheTime, unit);  
    }  
  
    @Override  
    public <V> ScheduledFuture<V> schedule(Callable<V> callable, long delay, TimeUnit unit) {  
        long scheTime = delay > 1e7 ? delay - System.currentTimeMillis() : delay;  
        return super.schedule(needTrace ? wrapTest(callable) : wrapTest(callable, null), scheTime, unit);  
    }  
  
    @Override  
    public Future<?> submit(Runnable task) {  
        return super.submit(wrapTest(task));  
    }  
  
    @Override  
    public <T> Future<T> submit(Callable<T> task) {  
        return super.submit(wrapTest(task));  
    }  
  
    @Override  
    public void execute(Runnable command) {  
        super.execute(wrapTest(command));  
    }  
  
    @Override  
    public ScheduledFuture<?> scheduleAtFixedRate(Runnable command, long initialDelay, long period, TimeUnit unit) {  
        return super.scheduleAtFixedRate(wrapTest(command), initialDelay, period, unit);  
    }  
  
    @Override  
    public ScheduledFuture<?> scheduleWithFixedDelay(Runnable command, long initialDelay, long delay, TimeUnit unit) {  
        return super.scheduleWithFixedDelay(wrapTest(command), initialDelay, delay, unit);  
    }  
  
    @Override  
    protected void afterExecute(Runnable r, Throwable t) {  
        super.afterExecute(r, t);  
        lastCompletedTaskTime = System.currentTimeMillis();  
    }  
  
    public boolean isIdleFor(long duration, TimeUnit unit) {  
        return System.currentTimeMillis() - lastCompletedTaskTime > unit.toMillis(duration);  
    }  
  
  
    private boolean needIncreaseThread(int min,int max ) {  
        while (timeConsumerQueue.size() > windowSize || (timeConsumerQueue.size() > 0 && System.currentTimeMillis()-timeConsumerQueue.peek().getStartTime() > tenSecondsMills)) {  
            MDCThreadPoolExecutor.TaskTimeInfo poll = timeConsumerQueue.poll();  
            totalCostTime.add(-poll.getCostTime());  
        }  
        timeConsumerQueueSize = timeConsumerQueue.size();  
        if (timeConsumerQueueSize == 0) {  
            return false;  
        }  
        long nowCostTime = totalCostTime.longValue() / timeConsumerQueueSize;  
        int queueSize = getQueue().size();  
        try {  
            int corePoolSize = getCorePoolSize();  
            int activeCount = getActiveCount();  
            boolean result = (queueSize * nowCostTime >  200  && lastQueueSize < queueSize) ||  queueSize >= corePoolSize  && nowCostTime > 10 && ((nowCostTime * queueSize / (getPoolSize() + 1) > 500)  || (nowCostTime > 2 * lastCostTime && lastCostTime > 10) || nowCostTime > 200 || queueSize > 50 || timeConsumerQueueSize > 100);  
            log.info("{},nowCostTime:{}, lastCostTime:{}, queueSize:{}, lastQueueSize:{} , timeConsumerQueueSize:{} ,lastTimeQueueSize:{}, getCorePoolSize :{}, activeCount:{}, result:{}", this.name,nowCostTime,lastCostTime, queueSize, lastQueueSize,timeConsumerQueueSize,lastTimeQueueSize, corePoolSize, activeCount,result);  
            return result;  
        } finally {  
            lastCostTime = nowCostTime;  
            lastQueueSize = queueSize;  
        }  
    }  
  
    public void adjustCorePoolSize(boolean needPrint, int min, int max, String name) {  
        this.name = name;  
        int preCorePoolSize = getCorePoolSize();  
        int queueSize = getQueue().size();  
        if (needIncreaseThread(min,max)) {  
            long nowCostTime = totalCostTime.longValue() / timeConsumerQueueSize;  
            int addNum = (int)( queueSize * nowCostTime / 500L - preCorePoolSize);  
            log.info("addNum:{}, preCorePoolSize:{}",addNum, preCorePoolSize);  
            int coreSize = Math.min(max, preCorePoolSize + Math.min(Math.max(preCorePoolSize/2,1), Math.max(addNum,0)));  
            setCorePoolSize(coreSize);  
            setMaximumPoolSize(max);  
            try {  
                allowCoreThreadTimeOut(false);  
            } catch (Exception e) {  
            }            lastCreateTime = System.currentTimeMillis();  
        } else{  
            int coreSize = Math.max(min, (preCorePoolSize + 1) / 2);  
            if (TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis()-lastCreateTime) > 30 && getActiveCount() * 2 <= preCorePoolSize && 1.1 * lastTimeQueueSize >= timeConsumerQueueSize) {  
                setCorePoolSize(coreSize);  
                setMaximumPoolSize(preCorePoolSize);  
            }  
            try {  
                allowCoreThreadTimeOut(true);  
            } catch (Exception e) {  
            }            lastCreateTime = System.currentTimeMillis();  
        }  
  
        if (needPrint) {  
            log.info("{}的线程池先前的核心线程数为:{}, 更新后核心线程数为: {}, 当前线程数: {}, 当前队列中任务数:{}, allowCoreThreadTimeOut:{} ", name, preCorePoolSize, getCorePoolSize()  
                    , getPoolSize(), queueSize, allowsCoreThreadTimeOut());  
        }  
        lastTimeQueueSize = timeConsumerQueueSize;  
    }  
  
  
  
    public <T> Callable<T> wrapTest(final Callable<T> runnable) {  
        return new ScheduledCallableWrapper<>(runnable, TraceIdUtil.getTraceId());  
    }  
  
  
    public <T> Callable<T> wrapTest(final Callable<T> runnable, final String traceId) {  
        return new ScheduledCallableWrapper<>(runnable, traceId);  
    }  
  
    public Runnable wrapTest(final Runnable runnable, final String traceId) {  
        return new ScheduledRunnableWrapper(runnable, traceId);  
    }  
  
    public Runnable wrapTest(final Runnable runnable) {  
        return new ScheduledRunnableWrapper(runnable, TraceIdUtil.getTraceId());  
    }  
  
  
    private class ScheduledRunnableWrapper extends MDCThreadPoolExecutor.RunnableWrapper {  
        public ScheduledRunnableWrapper(Runnable r, String traceId) {  
            super(r, traceId);  
        }  
  
        @Override  
        public void run() {  
            try {  
                super.run();  
            } finally {  
                lastCompletedTaskTime = System.currentTimeMillis();  
                long costTime = lastCompletedTaskTime - taskStartTime;  
                totalCostTime.add(costTime);  
                timeConsumerQueue.add(new MDCThreadPoolExecutor.TaskTimeInfo(lastCompletedTaskTime, costTime));  
            }  
        }  
  
    }  
  
    private class ScheduledCallableWrapper<T> extends MDCThreadPoolExecutor.CallableWrapper<T> {  
        public ScheduledCallableWrapper(Callable<T> r, String traceId) {  
            super(r, traceId);  
        }  
  
        @Override  
        public T call() throws Exception {  
            try {  
                return super.call();  
            } finally {  
                lastCompletedTaskTime = System.currentTimeMillis();  
                long costTime = lastCompletedTaskTime - taskStartTime;  
                totalCostTime.add(costTime);  
                timeConsumerQueue.add(new MDCThreadPoolExecutor.TaskTimeInfo(lastCompletedTaskTime, costTime));  
            }  
        }  
  
    }  
    private static void test(MDCScheduleThreadPoolExecutor executor) {  
        new Thread(()->{  
            while (true) {  
  
                for (int i1 = 2; i1 <  (executor.getCorePoolSize()!=16? RandomUtil.randomInt(5,100):RandomUtil.randomInt(2,5)); i1+=RandomUtil.randomInt(1,5)) {  
                    for (int i = 0; i < i1; i++) {  
                        executor.schedule(()->{  
                            try {  
                                TimeUnit.MILLISECONDS.sleep(RandomUtil.randomInt(4,8));  
                                if ( RandomUtil.randomInt(9, 30) % 3<=0) {  
                                    TimeUnit.MILLISECONDS.sleep(RandomUtil.randomInt(50,100));  
                                }  
                            } catch (InterruptedException e) {  
                                throw new RuntimeException(e);  
                            }  
                        },RandomUtil.randomInt(0,50),TimeUnit.MILLISECONDS);  
                    }  
                    try {  
                        TimeUnit.MILLISECONDS.sleep(100);  
                    } catch (InterruptedException e) {  
                        throw new RuntimeException(e);  
                    }  
                }  
            }  
        }).start();  
    }  
  
    public static void main(String[] args) {  
        MDCScheduleThreadPoolExecutor mdcThreadPoolExecutor = (MDCScheduleThreadPoolExecutor) ThreadPoolUtil.getScheduledThreadPoolExecutor(4,new AtomicInteger(),"test");  
        test(mdcThreadPoolExecutor);  
        new Thread(()->{  
            while (true) {  
                mdcThreadPoolExecutor.adjustCorePoolSize(true,4,50, "hhh");  
                try {  
                    TimeUnit.SECONDS.sleep(1);  
                } catch (InterruptedException e) {  
                    throw new RuntimeException(e);  
                }  
  
            }  
        }).start();  
    }  
}
```



```java
package com.baijia.storm.earth.windows.util;  
  
import org.apache.commons.lang3.StringUtils;  
import org.slf4j.MDC;  
  
import java.util.UUID;  
  
/**  
 * Created with IntelliJ IDEA. * * @auther Messi  
 * @Date: 2020/04/20/5:25 下午  
 * @Description: mdc追踪日志  
 */  
public class TraceIdUtil {  
  
    /**  
     * 需要和logback中相同  
     */  
    public static final String UNIQUE_ID = "requestId";  
  
    public static void setTraceId() {  
        MDC.put(UNIQUE_ID, UUID.randomUUID().toString().replace("-", ""));  
    }  
  
    public static void setTraceId(String traceId) {  
        if (StringUtils.isNotBlank(traceId)) {  
            MDC.put(UNIQUE_ID, traceId);  
        } else {  
            setTraceId();  
        }  
  
    }  
  
    public static void setTraceIdKey(String traceIdKey) {  
        MDC.put(UNIQUE_ID + traceIdKey, UUID.randomUUID().toString().replace("-", ""));  
    }  
  
    public static void removeTraceIdKey(String traceIdKey) {  
        MDC.remove(UNIQUE_ID+traceIdKey);  
    }  
  
    public static void removeTraceId() {  
        MDC.remove(UNIQUE_ID);  
    }  
  
    public static String getTraceId() {  
        return MDC.get(UNIQUE_ID);  
    }  
  
    public static String genTraceId() {  
        return UUID.randomUUID().toString().replace("-", "");  
    }  
  
  
}
```


vmtool -x 3 --action getInstances --className com.baijia.tongbao.mapper.ChatroomReplyTaskMapper  --express 'instances[0].update((#plan=new com.baijia.tongbao.entity.ChatroomReplyTaskPo(),#plan.setId(2876280),#plan.setIsDelete(1),#plan))'  -c 6831d8fd