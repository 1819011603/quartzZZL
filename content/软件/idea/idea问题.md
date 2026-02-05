
###  idea 层级消失 

删除  将项目第一层目录下的.idea隐藏目录
```

sudo rm -rf .idea
```

修复.idea下的  modules.xml 文件 可以使用cursor修复
```
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/fairy.iml" filepath="$PROJECT_DIR$/fairy.iml" />
    </modules>
  </component>
</project>

```

### idea cpu 高 排查

### 如何排查高CPU

- Help > Diagnostic Tools > Activity Monitor 查看哪个线程/插件占用高

- top/htop/任务管理器看IDEA进程是否swap

- 逐步注释掉JVM参数，重启IDEA，观察CPU变化


idea.vmoptions文件配置

```
-Duser.name=zhangzeling  
-Xms4096m  
-Xmx31744m  
-XX:ReservedCodeCacheSize=2048m  
-XX:+IgnoreUnrecognizedVMOptions  
-XX:+UseG1GC  
-XX:+HeapDumpOnOutOfMemoryError  
-XX:-OmitStackTraceInFastThrow  
-ea  
-Dsun.io.useCanonCaches=false  
-Djdk.http.auth.tunneling.disabledSchemes=""  
-Djdk.attach.allowAttachSelf=true  
-Djdk.module.illegalAccess.silent=true  
-Dkotlinx.coroutines.debug=off  
-XX:ErrorFile=$USER_HOME/java_error_in_idea_%p.log  
-XX:HeapDumpPath=$USER_HOME/java_error_in_idea.hprof  
-XX:CICompilerCount=4  
-XX:TieredStopAtLevel=1  
-XX:MaxInlineLevel=3  
-XX:Tier4MinInvocationThreshold=100000  
-XX:Tier4InvocationThreshold=110000  
-XX:Tier4CompileThreshold=120000  
  
--add-opens=java.base/jdk.internal.org.objectweb.asm=ALL-UNNAMED  
--add-opens=java.base/jdk.internal.org.objectweb.asm.tree=ALL-UNNAMED  
  
-javaagent:/Users/gaotu/Downloads/ja-netfilter/ja-netfilter.jar  
--add-opens=java.base/jdk.internal.org.objectweb.asm=ALL-UNNAMED  
--add-opens=java.base/jdk.internal.org.objectweb.asm.tree=ALL-UNNAMED
```


### idea 运行项目  parsing java 卡住 

抛出异常 java: java.lang.OutOfMemoryError: Java heap space


修改 build heap size

![[../../壁纸/附件/Pasted image 20241219163900.png]]



### 修改 idea.vmoptions错误 导致idea启动不了

两个路径: 
```

目前路径: Users/gaotu/Downloads/jetbra/vmoptions/idea.vmoptions

默认路径: Applications/IntelliJ IDEA.app/Contents/bin/idea.vmoptions
```

因为使用了jetbra破解  vmoptions路径被修改了


通过:
1. fd  idea.vmoptions   
2. 或者  rg  'ReservedCodeCacheSize=4096m' (查询错误的那个配置所在的路径)

左下角可以直接看见路径
![[../../壁纸/附件/Pasted image 20241219164628.png]]


### 修改idea运行时java版本, 从17改为21


https://www.jetbrains.com/help/idea/switching-boot-jdk.html

Help ->  Find Action -> 输入Choose Boot Java Runtime for the IDE

不要随便修改 有时候会启动不了

/Library/Java/JavaVirtualMachines/jdk-21.jdk

启动不了 就 fd  idea.jdk

	Users/gaotu/Library/Application Support/JetBrains/IntelliJIdea2024.1/idea.jdk
再删除这个文件 Users/gaotu/Library/Application Support/JetBrains/IntelliJIdea2024.1/idea.jdk
		rm -f



1. 开启省电模式， 关闭代码检查
	![[Pasted image 20231219114308.png]]
	![[Pasted image 20231219114342.png]]
2. 关闭代码检查，保留代码提示
	1.inspections  新建一个Profile， 将所有的检查都取消
		![[Pasted image 20231219151033.png]]
3. idea reload from disk 不自动同步
	1. 1. 如果你关闭了“Synchronize files on frame or editor tab activation”选项，IDEA也不会自动刷新。这个选项在 "Settings/Preferences" > "Appearance & Behavior" > "System Settings"中。请确保此选项被选中。
	2. save files if the IDE is idle for 1 seconds
	3. 开关全部打开
	4. 自动保存
	5. ![[Pasted image 20240117140739.png]]
4.  idea 强制更新依赖
		-U选项告诉Maven强制更新依赖。清理和安装过程都会更新相关的依赖包。如果只希望更新依赖，没有必要进行安装，可以执行：
		![[settings.xml]]
	```
	mvn dependency:resolve -U
	```
		mvn dependency:tree命令解决jar包冲突  
		当项目出现jar包冲突时,用命令mvn dependency:tree 查看依赖情况
		mvn compile //编译源代码
		mvn package //依据项目生成 jar 文件
		mvn install //在本地 Repository 中安装 jar
		mvn clean //清除目标目录中的生成结果
		mvn clean compile //将.java类编译为.class文件
		mvn clean deploy //部署到版本仓库
		

本地debug的时候为了避免mq消息消费到本地，可以在IDEA启动配置里Environment variables, 设置环境变量rocketmq.consumer.config.enable=false
![[image_d9b6e740-70dd-4817-a895-1fd2e88676bc.jpeg]]

![[image_404992fb-a452-431f-aa7d-a116016681d4.jpeg]]