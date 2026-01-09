
### 自定义 ClassLoader 载入和卸载 User 类

当我们需要自定义ClassLoader来加载User类，并在需要时卸载ClassLoader和重新载入新的User类时，可以使用Java的`ClassLoader`和`URLClassLoader`。以下是一个简单的例子：

```java
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.lang.reflect.Method;
import java.net.URL;
import java.net.URLClassLoader;

public class CustomUserClassLoader {

    private static final String USER_CLASS_NAME = "com.example.User";
    private static final String USER_CLASS_PATH = "path/to/classes"; // 替换为实际存放User类文件的路径

    public static void main(String[] args) throws ClassNotFoundException, IllegalAccessException, InstantiationException {
        // 第一次加载User类
        Class<?> userClass = loadUserClass();
        Object userInstance = userClass.newInstance();
        invokeUserMethod(userInstance);

        // 卸载ClassLoader
        unloadClassLoader(userClass.getClassLoader());

        // 第二次加载User类和新的ClassLoader
        Class<?> newUserClass = loadUserClass();
        Object newUserInstance = newUserClass.newInstance();
        invokeUserMethod(newUserInstance);
    }

    private static Class<?> loadUserClass() throws ClassNotFoundException {
        // 自定义ClassLoader的实例，指定加载路径
        URLClassLoader userClassLoader = new URLClassLoader(new URL[]{Paths.get(USER_CLASS_PATH).toUri().toURL()});

        // 使用自定义ClassLoader加载User类
        return userClassLoader.loadClass(USER_CLASS_NAME);
    }

    private static void invokeUserMethod(Object userInstance) {
        try {
            // 调用User类的方法
            Method userMethod = userInstance.getClass().getMethod("someMethod");
            userMethod.invoke(userInstance);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void unloadClassLoader(ClassLoader classLoader) {
        try {
            // 关闭URLClassLoader的资源
            if (classLoader instanceof URLClassLoader) {
                URLClassLoader urlClassLoader = (URLClassLoader) classLoader;
                URL url = urlClassLoader.getURLs()[0];
                urlClassLoader.close();
                // 移除URLClassLoader的URL
                removeURL(url);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void removeURL(URL url) throws IOException {
        // 通过反射获取URLClassLoader的ucp字段（sun.misc.URLClassPath）
        Class<?> urlClassPathClass = sun.misc.URLClassPath.class;
        try {
            Field ucpField = URLClassLoader.class.getDeclaredField("ucp");
            ucpField.setAccessible(true);

            // 获取URLClassLoader的ucp字段值
            Object ucp = ucpField.get(ClassLoader.getSystemClassLoader());

            // 调用URLClassPath的removeURL方法
            Method removeUrlMethod = urlClassPathClass.getDeclaredMethod("removeURL", URL.class);
            removeUrlMethod.setAccessible(true);
            removeUrlMethod.invoke(ucp, url);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

```