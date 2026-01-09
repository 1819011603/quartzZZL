

### 包不存在

```

# 步骤2：检查依赖是否下载成功
mvn dependency:tree | grep apollo

# 先查看已安装的 Java 版本和路径
/usr/libexec/java_home -V


# 添加到 ~/.zshrc
echo 'alias mvn8="JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.8.0_202.jdk/Contents/Home mvn"' >> ~/.zshrc
source ~/.zshrc

# 以后直接用
mvn8 clean install -U
```

强制更新依赖:

mvn clean install -U


	### 下载maven 源source
	mvn dependency:resolve -Dclassifier=sources



### 解决 Intellij IDEA 不识别某些 class 的问题 ![](https://www.felix021.com/blog/template/default/images/others/unstarred.gif "未加星标") ![不指定](https://www.felix021.com/blog/images/weather/blank.gif "不指定")
![[../../壁纸/附件/Pasted image 20241225113823.png]]

解决方案很简单：删掉 idea 的cache 目录，让它重建就好了。

似乎 IDEA 本身也有清空 cache 的功能（File -> Invalidate Caches...），下次遇到再验证一下。


勾选 Always update snapshots -> 取消勾选Always update snapshots



### idea maven Always update snapshots是什么意思 这个开关有什么用途

###### 什么是 SNAPSHOT？

- SNAPSHOT 是 Maven 版本号中的一个特殊标识，表示该版本是一个**开发中的不稳定版本**，而非最终发布的正式版本。
- SNAPSHOT 版本在远程仓库中可能会被频繁更新，每次构建可能都会生成一个新的快照版本。
- 示例：
    - `1.0-SNAPSHOT` 表示版本 `1.0` 的开发快照。

##### `Always update snapshots` 的含义

- **默认行为**：
    - 如果不开启 `Always update snapshots`，Maven 会根据本地缓存的 SNAPSHOT 版本和远程仓库中的版本对比，决定是否下载更新。
    - 默认情况下，Maven 每 24 小时检查一次 SNAPSHOT 是否有更新（通过 `updatePolicy` 配置）。
- **开启后**：
    - 每次构建项目时，Maven **总是会强制检查**远程仓库中的 SNAPSHOT 版本，并下载最新版本到本地，无论本地是否有缓存。

在命令行中通过参数：

- 使用 `-U` 参数强制更新 SNAPSHOT：
    `mvn clean install -U`
    
- 这个参数的效果等同于临时开启 `Always update snapshots`。

### 依赖树

 mvn dependency:tree


### mvn clean install 安装依赖

```
mvn clean install -Dmaven.compiler.source=8 -Dmaven.compiler.target=8
```


### 导入项目时 resolve maven dependencies 太久

Maven Archetype 是 Maven 的一种模板机制，用于快速生成项目的基本结构。例如，你可以使用一个 `quickstart` archetype 模板生成一个 Java 项目的基础代码，包括 `pom.xml` 和基本的目录结构。


1. 设置-DarchetypeCatalog=internal

![[../../壁纸/附件/Pasted image 20241219153422.png]]

```
-DarchetypeCatalog 参数用于控制 Maven 在生成项目时的 Archetype Catalog 来源。它有以下选项：  
  
remote（默认值）  
  
Maven 从远程仓库（如 Maven 中央仓库）加载可用的 Archetype 列表。  
优点：可以获取到所有最新的 Archetype。  
缺点：如果网络较慢或仓库不可用，会导致性能问题或失败。  

internal  
  
只使用本地 Maven 安装中内置的 Archetype 列表。  
优点：更快、更可靠，不依赖网络。  
缺点：可能无法使用最新的 Archetype。  
URL  
  
指定一个自定义 URL，指向一个自定义的 Archetype Catalog 文件。  
优点：适合公司内部的特定需求，可以使用自定义的模板。  
缺点：需要额外配置。
```


```
4. 为什么要设置 -DarchetypeCatalog=internal？
原因 1：避免网络问题

如果网络连接不稳定，Maven 默认的 remote 设置可能导致 Archetype Catalog 加载时间过长甚至失败。
设置为 internal 后，Maven 只使用本地的内置模板，不再访问远程仓库。

原因 2：提高速度

远程仓库的 Archetype Catalog 通常包含大量模板，加载和解析这些模板可能会耗费时间。
使用 internal 可以跳过这些步骤，直接从本地加载内置模板，大幅提高生成项目的速度。

原因 3：环境隔离

在某些离线或受限网络环境中，无法访问远程仓库。
设置为 internal 后，Maven 可以在离线模式下使用本地的模板。

原因 4：减少干扰

远程仓库可能包含大量不相关或不需要的 Archetype。
内部的 Catalog 通常只包含常用的模板（如 maven-archetype-quickstart），更易于管理。
```

2. 设置  VM options for importer：   

	-Xms1024m -Xmx4096m

![[../../壁纸/附件/Pasted image 20241219153522.png]]


### maven 依赖冲突，引用错误

那 maven 有一个依赖传递的特性，如果 A 依赖 B，而 B 依赖 C，那么 C 这个依赖就会通过 B 间接传递给 A。

那如果有多个间接依赖存在，但是彼此版本却不一样，这就会导致**依赖冲突**。

我们可以在 IDEA 中安装一个 **Maven Helper** 插件，然后打开 pom 文件，点击 **Dependency Analyzer** 选项，在这里面选中 **Conflicts** 按钮，就可以看到当前所有冲突的依赖包。

选中其中一个依赖包，就可以在右侧看到所有冲突依赖包的版本。选中其中一个版本，右键选中 Exclude 即可。
![[../../壁纸/附件/Pasted image 20241225112801.png]]


### 找不到类

包找不到

mvn clean compile

```
creating bean with name 'courseGateway': Injection of resource dependencies failed; nested exception is org.springframework.beans.factory.NoSuchBeanDefinitionException: No qualifying bean of type 'com.gaotu.reach.adapter.wrapper.CourseWrapper' available: expected at least 1 bean which qualifies as autowire candidate. Dependency annotations:
```


重启clean和package 一下就好 
![[../../壁纸/附件/Pasted image 20250523151643.png]]


#### 方案一：彻底清理并强制同步（推荐）

此方法通过完全重置 IDEA 的项目缓存和构建工具的状态来解决同步问题。

1. **执行构建清理**：在 IDEA 的 Gradle/Maven 面板中，执行 `clean` 任务，或者在终端运行 `gradlew clean` / `mvn clean`。这将删除 `build` 或 `target` 目录。
2. **清理 IDEA 缓存**：
    - 点击 IDEA 菜单 `File` -> `Invalidate Caches...`。
    - 在弹出的对话框中，勾选 **`Clear file system cache and Local History`** 和 **`Clear VCS Log caches and indexes`**。
    - 点击 `Invalidate and Restart`。
3. **重新加载项目**：IDEA 重启后，会重新索引项目。等待右下角索引任务完成后，打开 Gradle/Maven 面板，点击“Reload All Gradle/Maven Projects”按钮，强制 IDEA 重新读取构建脚本并同步项目结构。