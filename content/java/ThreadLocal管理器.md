

```java
  
import java.util.Map;  
import java.util.Objects;  
import java.util.concurrent.ConcurrentHashMap;  
  
/**  
 * @author: zhangzeling  
 * @date: 2024/9/12  
 * @description: ThreadLocalManager  
 * <p>  
 * 管理ThreadLocal  
 */public class ThreadLocalManager {  
    private final static Map<String, TypedThreadLocal<?>> THREAD_LOCAL_LIST = new ConcurrentHashMap<>();  
    // 用于保存ThreadLocal的类型  
  
    private static <T> void registerThreadLocal(String name, TypedThreadLocal<T> threadLocal) {  
        THREAD_LOCAL_LIST.put(name, threadLocal);  
    }  
  
    public static void clear() {  
        if (THREAD_LOCAL_LIST.isEmpty()) {  
            return;  
        }  
        synchronized (THREAD_LOCAL_LIST) {  
            THREAD_LOCAL_LIST.values().forEach(TypedThreadLocal::remove);  
        }  
    }  
  
  
    /**  
     * 获取ThreadLocal 需要指定类型 用于检查类型是否匹配 没有类型参数的ThreadLocal无法检查类型  
     * 如果类型不匹配会抛出异常  
     *  
     * @param name   ThreadLocal的名字  
     * @param tClass ThreadLocal的类型  
     * @param <T>    ThreadLocal的类型  
     * @return ThreadLocal  
     */    @SuppressWarnings("unchecked")  
    public static <T> ThreadLocal<T> getThreadLocal(String name, Class<T> tClass) {  
        if (name == null) {  
            throw new RuntimeException("name can not be null");  
        }  
        if (tClass == null) {  
            throw new RuntimeException("type can not be null");  
        }  
        TypedThreadLocal<?> typedThreadLocal = null;  
        if ((typedThreadLocal = THREAD_LOCAL_LIST.get(name)) == null) {  
            synchronized (name.intern()) {  
                if ((typedThreadLocal = THREAD_LOCAL_LIST.get(name)) == null) {  
                    typedThreadLocal = new TypedThreadLocal<>(name, tClass);  
                    registerThreadLocal(name, typedThreadLocal);  
                    return (ThreadLocal<T>) typedThreadLocal.getThreadLocal();  
                }  
            }  
        }  
        if (!Objects.equals(typedThreadLocal.getType(), tClass)) {  
            throw new RuntimeException("name: " + name + " , type not match, original type: "  
                    + typedThreadLocal.getType() + ", current type: " + tClass);  
        }  
        return (ThreadLocal<T>) typedThreadLocal.getThreadLocal();  
  
    }  
  
    public static void main(String[] args) {  
        ThreadLocal<Integer> threadLocal = ThreadLocalManager.getThreadLocal("test", Integer.class);  
        threadLocal.set(1);  
        System.out.println(threadLocal.get());  
    }  
  
}
```