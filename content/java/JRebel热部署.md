
使用文档: https://cloud.tencent.com/developer/article/1780095


JRebel
激活攻略
https://blog.csdn.net/qq251708339/article/details/134105044



https://www.jpy.wang/page/jrebel.html

## JRebel 无限试用，请将以下内容拷贝到命令提示符中执行:

```bat
cd ~/Downloads/jetbra/scripts/tmp/ & curl https://register.jpy.wang/ReRegister/src/main/java/jrebel/JrebelMain.java -o tmp.java && java tmp.java 
```


设置攻略: 
https://blog.csdn.net/le9528/article/details/130421451


### 完全激活 

https://github.com/yu-xiaoyao/jrebel-license-active-server?tab=readme-ov-file



macos 下载地址: https://github.com/yu-xiaoyao/jrebel-license-active-server/releases/download/v-20250910/jrebel-license-active-server-darwin_arm64

下载完记得 chmod a+x

![[../壁纸/附件/Pasted image 20251009151644.png]]
team Url
http://117.50.194.13:12345/524f1d03-d1d8-5e94-a099-042736d40bd9






### 无法点击debug模式


重启关闭项目 重新打开即可 /  重启idea

### 重新编译某个修改的类

Shift+fn+Command+F9
![[../壁纸/附件/Pasted image 20241121112613.png]]


### 找不到主类

![[../壁纸/附件/Pasted image 20241121110924.png]]
![[../壁纸/附件/Pasted image 20241121110958.png]]


###  对于BeanUtil这类的Class反射操作，似乎在使用JRebel热加载插件更新class文件时无效。 如下两图，beantomap只得到了两个属性，但我的类里面是三个字段，为了避免缓存问题，我特意提前清除了缓存。这种情况只能重启项目，才能获取到新增加的字段。用commons包就没有这个问题。

### 1. **缓存问题**

- **原因**： `BeanUtil` 或其他反射工具类可能对类的元数据进行了缓存。在热加载后，缓存的元数据没有及时更新。
- **解决方案**： 尝试使用 `BeanUtil` 的方法来清除缓存，或者使用 `commons-beanutils` 这类没有缓存机制的库。如果 `BeanUtil` 本身不提供清除缓存的接口，你可能需要重启项目来清空缓存。



### 原理


1. **类加载器的角色：**
    
    - **每个类加载器维护自己的命名空间。**
    - **同一个类（相同的全限定名），如果被不同的类加载器加载，会被视为不同的类。**

1. 内存和生命周期影响：
    
    - 每次调用 `defineClass` 都会在方法区（或元空间，取决于 JVM 版本）分配新的内存。
    - 旧的类对象不会立即被垃圾回收，除非没有任何引用指向它。

<mark class="hltr-red">**加载新对象使用新的自定义的classLoader对象生成的新的class对象, 使用新的class对象生成新的对象</mark>


```java

/**  
 * 加载 class ，缓存到 loadTimeMap  
 * * @param className  
 * @param lastModified  
 */  
private static void load(String className, long lastModified) {  
    MyClasslLoader myClasslLoader = new MyClasslLoader(className);  
    Class loadClass = null;  
    // 加载  
    try {  
        loadClass = myClasslLoader.loadClass(className);  
    } catch (ClassNotFoundException e) {  
        e.printStackTrace();  
    }  
  
    BaseManager manager = newInstance(loadClass);  
    LoadInfo loadInfo = new LoadInfo(myClasslLoader, lastModified);  
    loadInfo.setManager(manager);  
    loadTimeMap.put(className, loadInfo);  
}
```



loadClass：加载类的入口方法，类似一个工具，完全可以控制和管理~ 大致分为几步：

           1. 调用findLoadedClass来判断是否加载过  

           2. 父类调用loadClass  

           3. 调用findClass（String name）方法来查找类  

findClass：指定名称来查找~

findLoadedClass：检查是否已经加载过（每个类加载器都只能加载一个同名的类）找到如果存在就返回，否则返回null。

defineClass：接受字节数组（字节码文件可来源于文件，网络）byteArrayOutputStream将其转化为Class实例。

tips：loadClass方法只是加载某个类，并不执行该类的初始化~，而Class的forName静态方法会强制初始化类。

注意，不要重写loadClass方法。  因为在使用自定义的MyClassLoader加载Person类的时候 。  Person类中需要依赖的其他对象， 都会默认使用MyClassLoader的loadClass方法进行加载。  如果重写了loadClass方法（像下面代码注释那样），就会导致jvm使用MyClassLoader来加载Object、String等等一些类。  当然，这些类在classpath是找不到的。 所以就会抛出ClassNotFoundException 。


注意：同一个ClassLoader不能多次加载同一个类。 如果重复的加载同一个类 ， 将会抛出 loader (instance of  hot/MyClassLoader): attempted  duplicate class definition for name: "hot/Person" 异常。  所以，在替换Class的时候，  加载该Class的ClassLoader也必须用新的。



```java
protected Class<?> loadClass(String name, boolean resolve)  
    throws ClassNotFoundException  
{  
    synchronized (getClassLoadingLock(name)) {  
        // First, check if the class has already been loaded  
        Class<?> c = findLoadedClass(name);  
        if (c == null) {  
            long t0 = System.nanoTime();  
            try {  
                if (parent != null) {  
                    c = parent.loadClass(name, false);  
                } else {  
                    c = findBootstrapClassOrNull(name);  
                }  
            } catch (ClassNotFoundException e) {  
                // ClassNotFoundException thrown if class not found  
                // from the non-null parent class loader            }  
  
            if (c == null) {  
                // If still not found, then invoke findClass in order  
                // to find the class.                long t1 = System.nanoTime();  
                c = findClass(name);  
  
                // this is the defining class loader; record the stats  
                sun.misc.PerfCounter.getParentDelegationTime().addTime(t1 - t0);  
                sun.misc.PerfCounter.getFindClassTime().addElapsedTimeFrom(t1);  
                sun.misc.PerfCounter.getFindClasses().increment();  
            }  
        }  
        if (resolve) {  
            resolveClass(c);  
        }  
        return c;  
    }  
}


protected Class<?> findClass(String name) throws ClassNotFoundException {  
    throw new ClassNotFoundException(name);  
}
```

1. 热加载的挑战：  
    当你修改了 hot.Person 类并希望重新加载时，如果使用 loadClass 方法，可能会得到之前缓存的旧版本类，而不是新修改的版本。
    
2. 使用 findClass 的原因：  
    直接调用 findClass 方法可以绕过双亲委派模型和类缓存机制，确保每次都重新加载类文件，从而实现热加载。

###  findClass 方法可以绕过双亲委派模型和类缓存机制 为什么 不是还是会有缓存吗

您提出了一个很好的问题。实际上，findClass 方法本身并不能完全绕过双亲委派模型和类缓存机制。让我来详细解释一下：

1. findClass 和 loadClass 的区别：
    
    - loadClass 方法实现了完整的类加载逻辑，包括双亲委派。
    - findClass 方法通常只负责查找和定义类，不处理双亲委派。
2. 类缓存机制：
    
    - 类加载器确实会缓存已加载的类。
    - 这个缓存通常在 loadClass 方法中维护，而不是在 findClass 中。
3. 为什么直接使用 findClass 可能有效：
    
    - 当直接调用 findClass 时，我们绕过了 loadClass 中的缓存检查和双亲委派逻辑。
    - 这意味着每次调用 findClass 都会尝试重新加载类，而不检查是否已经加载。
4. 完全绕过缓存的方法：
    
    - 仅仅使用 findClass 并不足以完全绕过缓存。
    - 要真正实现热加载，通常需要为每次加载创建一个新的类加载器实例。
5. 正确的热加载实现：
    
    - 创建新的类加载器实例。
    - 使用这个新实例加载类。
    - 丢弃旧的类加载器实例。
6. 示例代码：  
这样的话  重写loadClass 破坏双薪委派机制
```java
public class HotReloadClassLoader extends ClassLoader {
    public Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {

  // 对于特定包下的类，执行自定义加载逻辑

    if (name.startsWith("hot.")) {
            return findClass(name);
        }
        return super.loadClass(name, resolve);
    }


// 对于其他类，保持默认的双亲委派行为
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        // 实现类的查找和加载逻辑
    }
}

// 使用
HotReloadClassLoader loader = new HotReloadClassLoader();
Class<?> hotClass = loader.loadClass("hot.Person", true);
```


总结：  
直接使用 findClass 方法并不能完全绕过类缓存机制，但它可以绕过标准类加载过程中的一些步骤。要实现真正的热加载，通常需要结合使用自定义的类加载器和创建新的类加载器实例。这种方法可以确保每次都加载最新版本的类，而不受已存在的类缓存的影响。