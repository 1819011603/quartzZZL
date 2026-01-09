```

package com.gaotu.yunying.student.center.domain.util;  
  
import com.baijia.gapm.apm.toolkit.trace.RunnableWrapper;  
import com.baijia.gapm.apm.toolkit.trace.SupplierWrapper;  
import com.google.common.collect.Lists;  
import org.apache.commons.collections4.CollectionUtils;  
  
import java.util.*;  
import java.util.concurrent.CompletableFuture;  
import java.util.concurrent.Executor;  
import java.util.function.Consumer;  
import java.util.function.Function;  
import java.util.function.Supplier;  
import java.util.stream.Collectors;  
  
/**  
 * @author: zhangzeling  
 * @date: 2024/12/27  
 * @description: CompletableFutureUtils  
 */public class CompletableFutureUtils {  
  
    /**  
     * 是否串行执行 本地环境下可以设置为true  
     */    private static  boolean serial = Objects.equals(System.getProperty("com.gaotu.yunying.student.center.domain.util.CompletableFutureUtils.serial"), "true");  
  
    /**  
     * 同步方法  
     * 用于异步处理集合中的每个元素，并将结果收集到一个列表中  
     * 这种写法相比于  
     * list.stream().map(u -> CompletableFuture.supplyAsync(() -> supplier.apply(u), executor))  
     * .map(CompletableFuture::join)     * .collect(Collectors.toList());     * 会节约一个线程, 不需要单独处理一个元素的情况  
     *  
     * @param list  
     * @param supplier  
     * @param executor  
     * @param <U>  
     * @param <T>  
     * @return  
     */  
    public static <U, T> List<T> supplyAsync(Collection<U> list, Executor executor, Function<U, T> supplier) {  
        if (CollectionUtils.isEmpty(list)) {  
            return Collections.emptyList();  
        }  
        if (serial) {  
            return list.stream().map(supplier).collect(Collectors.toList());  
        }  
        Iterator<U> iterator = list.iterator();  
        U first = iterator.next();  
        List<T> result = new ArrayList<>(list.size());  
        List<CompletableFuture<T>> completableFutures = new ArrayList<>(list.size());  
        while (iterator.hasNext()) {  
            U u = iterator.next();  
            completableFutures.add(CompletableFuture.supplyAsync(new SupplierWrapper<>(() -> supplier.apply(u)),executor));  
        }  
        result.add(supplier.apply(first));  
        completableFutures.stream().map(CompletableFuture::join).forEach(result::add);  
        return result;  
    }  
  
    /**  
     * 同步方法  
     * 主线程会执行第一个元素的任务, 会节约一个线程, 不需要单独处理一个元素的情况  
     * 用于异步处理集合中的每个元素， 不关心返回值  
     *  
     * @param list  
     * @param consumer  
     * @param executor  
     * @param <U>  
     */  
    public static <U> void runAsync(Collection<U> list, Executor executor, Consumer<U> consumer) {  
        if (CollectionUtils.isEmpty(list)) {  
            return;  
        }  
        if (serial) {  
            list.forEach(consumer);  
            return;  
        }  
        Iterator<U> iterator = list.iterator();  
        U first = iterator.next();  
        List<CompletableFuture<Void>> completableFutures = new ArrayList<>(list.size());  
        while (iterator.hasNext()) {  
            U u = iterator.next();  
            completableFutures.add(CompletableFuture.runAsync(new RunnableWrapper(() -> consumer.accept(u)), executor));  
        }  
        consumer.accept(first);  
        completableFutures.forEach(CompletableFuture::join);  
    }  
  
  
    /**  
     * 同步方法  
     * 分批异步处理  
     * @param list  
     * @param batchSize  
     * @param executor  
     * @param supplier  
     * @return  
     * @param <U>  
     * @param <T>  
     */  
//    public static <U, T> List<T> supplyAsync(List<U> list, int batchSize,  Executor executor, Function<List<U>, List<T>> supplier) {  
//        if (CollectionUtils.isEmpty(list)) {  
//            return Collections.emptyList();  
//        }  
//        if (list.size() <= batchSize) {  
//            return supplier.apply(list);  
//        }  
//        List<List<U>> partitions = Lists.partition(list, batchSize);  
//        List<List<T>> ts = supplyAsync(partitions, executor, supplier);  
//        return ts.stream().flatMap(Collection::stream).collect(Collectors.toList());  
//    }  
  
  
  
  
    /**  
     * 异步方法  
     * @param supplier  
     * @param executor  
     * @return  
     * @param <T>  
     */  
    public static <T>  CompletableFuture<T> supplyAsync(Supplier<T> supplier, Executor executor) {  
        return CompletableFuture.supplyAsync(new SupplierWrapper<>(supplier), executor);  
    }  
  
    /**  
     * 异步方法  
     * @param supplier  
     * @return  
     * @param <T>  
     */  
//    public static <T>  CompletableFuture<T> supplyAsync(Supplier<T> supplier) {  
//        return CompletableFuture.supplyAsync(new SupplierWrapper<>(supplier));  
//    }  
  
}
```