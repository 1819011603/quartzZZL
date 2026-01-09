

```

-Duser.name=zhangzeling  
-Xms4096m  
-Xmx32768m  
-XX:ReservedCodeCacheSize=2048m  
-XX:+IgnoreUnrecognizedVMOptions  
-XX:+UseG1GC  
-XX:SoftRefLRUPolicyMSPerMB=50  
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
  
--add-opens=java.base/jdk.internal.org.objectweb.asm=ALL-UNNAMED  
--add-opens=java.base/jdk.internal.org.objectweb.asm.tree=ALL-UNNAMED  
  
  
-XX:CICompilerCount=4  
-XX:TieredStopAtLevel=1  
-XX:MaxInlineLevel=3  
-XX:Tier4MinInvocationThreshold=100000  
-XX:Tier4InvocationThreshold=110000  
-XX:Tier4CompileThreshold=120000  
-javaagent:/Users/gaotu/Downloads/ja-netfilter/ja-netfilter.jar  
--add-opens=java.base/jdk.internal.org.objectweb.asm=ALL-UNNAMED  
--add-opens=java.base/jdk.internal.org.objectweb.asm.tree=ALL-UNNAMED
```