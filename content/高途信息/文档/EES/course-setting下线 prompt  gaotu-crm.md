# FeignClient 改造为 ACL 接口模式 - AI Prompt 模板  
  
## 直接使用的 Prompt  
  
```  
我需要将项目中的 FeignClient 接口改造为 ACL（Anti-Corruption Layer）接口模式，并集成 SpringBasedBalancerConfiguration 和 SpringBasedDiffBeanConfiguration 配置类。  
  
## 任务要求  
  
### 1. 改造范围  
- 找出所有 name = "XXX.GAOTU100.COM" 格式的 @FeignClient 接口  
- 找出所有位于 com.gaotu.client.feign 包下的接口  
- 找出所有直接使用这些 FeignClient 的地方  
  
### 2. 依赖配置  
在 pom.xml 中添加：  
```xml  
<dependency>  
    <groupId>com.gaotu</groupId>  
    <artifactId>blocks-tools-starter</artifactId>  
    <version>2.0.3</version>  
    <exclusions>  
        <exclusion>  
            <groupId>cglib</groupId>  
            <artifactId>cglib</artifactId>  
        </exclusion>  
    </exclusions>  
</dependency>  
```  
  
### 3. 扫描包配置  
确保 @SpringBootApplication 的 scanBasePackages 包含 "com.gaotu.blocks.starter"  
  
### 4. 改造步骤（对每个 FeignClient）  
  
#### 步骤 1：创建 ACL 接口  
- 位置：com.gaotu.edu.b.crm.adapter.remote.acl 包下  
- 命名：XxxFeignService → XxxAclService  
- 要求：接口方法签名与原始 FeignClient 完全一致  
  
#### 步骤 2：创建 ACL 实现类（Impl）  
- 类名：XxxAclServiceImpl  
- 实现：XxxAclService 接口  
- 注解：@Service("xxxAclServiceImpl") 和 @Qualifier("xxxAclServiceImpl")  
- 注入：原始 FeignClient（如：PeriodFeignService）  
- 实现：所有方法委托调用原始 FeignClient  
  
#### 步骤 3：创建 ACL V1 实现类（V1Impl）  
- 类名：XxxAclServiceV1Impl  
- **重要：继承 XxxAclServiceImpl，不实现接口**  
- 注解：@Service("xxxAclServiceV1Impl") 和 @Qualifier("xxxAclServiceV1Impl")  
- 初始可以为空，后续需要时再重写方法  
  
#### 步骤 4：创建 Diff 配置类  
- 位置：com.gaotu.edu.b.crm.adapter.remote.acl.config 包下  
- 类名：XxxAclServiceDiffBeanConfiguration  
- 继承：SpringBasedDiffBeanConfiguration  
- CONFIG_KEY_PRE = "gaotu.crm.diff."  
- Bean 方法：  
  ```java  
  @Bean(name = "xxxAclServiceDiffProxy")  
  public XxxAclService xxxAclServiceDiffProxy(XxxAclServiceImpl first, XxxAclServiceV1Impl second) {  
      return createProxy(first, second, XxxAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
  }  
  ```  
  
#### 步骤 5：创建 Balancer 配置类  
- 类名：XxxAclServiceBalancerBeanConfiguration  
- 继承：SpringBasedBalancerConfiguration  
- CONFIG_KEY_PRE = "gaotu.crm.balancer."  
- 注入 DiffProxy：@Resource(name = "xxxAclServiceDiffProxy")  
- Bean 方法（必须使用 @Primary）：  
  ```java  
  @Bean  
  @Primary  
  public XxxAclService xxxAclService(XxxAclServiceImpl first, XxxAclServiceV1Impl second) {  
      return createGrayscaleProxy(xxxAclServiceDiffProxy, second, XxxAclService.class, CONFIG_KEY_PRE + first.getClass().getSimpleName());  
  }  
  ```  
  
#### 步骤 6：替换所有调用方  
- 替换 import：com.gaotu.edu.b.crm.adapter.remote.feign.XxxFeignService → com.gaotu.edu.b.crm.adapter.remote.acl.XxxAclService  
- 替换字段：private XxxFeignService xxxFeignService → private XxxAclService xxxAclService  
- 替换调用：xxxFeignService.method() → xxxAclService.method()  
- 更新所有使用的地方，包括注释中的引用  
  
### 5. Apollo 配置生成  
  
#### Diff 配置（功能开关）  
规则：{CONFIG_KEY_PRE}{first.getClass().getSimpleName()}.enable=true  
示例：gaotu.crm.diff.PeriodAclServiceImpl.enable=true  
  
#### Balancer 配置（灰度）  
规则：{CONFIG_KEY_PRE}{first.getClass().getSimpleName()}.grayscale={"sql":100,"rpc":0}  
示例：gaotu.crm.balancer.PeriodAclServiceImpl.grayscale={"sql":100,"rpc":0}  
  
### 6. 关键规则  
- ✅ V1Impl 必须继承 Impl，不能实现接口  
- ✅ V1Impl 使用相同的 FeignClient（继承自父类）  
- ✅ 不需要创建 V1Adapter  
- ✅ 配置类中的 first 参数是老实现类，second 参数是新实现类  
- ✅ Balancer 配置类中的 Bean 方法必须使用 @Primary  
- ✅ 配置 key 使用 first.getClass().getSimpleName()，不是接口名  
  
### 7. 输出要求  
- 列出所有需要改造的 FeignClient  
- 列出所有使用这些 FeignClient 的文件  
- 生成所有 ACL 接口、实现类、配置类代码  
- 替换所有调用方  
- 生成完整的 Apollo 配置列表  
- 确保代码可以直接使用，无编译错误  
  
请按照以上步骤完成改造，确保：  
1. 所有代码都创建完成  
2. 所有调用方都已替换  
3. 配置类结构正确  
4. Apollo 配置已生成  
```  
  
## 使用说明  
  
1. **直接复制上面的 Prompt** 到 AI 对话中  
2. **AI 会按照步骤执行**：  
   - 识别需要改造的 FeignClient  
   - 创建所有必要的 ACL 接口和实现类  
   - 创建配置类  
   - 替换所有调用方  
   - 生成 Apollo 配置  
  
3. **验证结果**：  
   - 检查所有文件是否创建  
   - 检查所有调用是否替换  
   - 检查编译是否通过  
   - 检查 Apollo 配置是否正确  
  
## 快速检查清单  
  
改造完成后，检查以下内容：  
  
- [ ] 依赖已添加（blocks-tools-starter）  
- [ ] 扫描包配置已更新  
- [ ] ACL 接口已创建（XxxAclService）  
- [ ] ACL 实现类已创建（XxxAclServiceImpl）  
- [ ] ACL V1 实现类已创建（XxxAclServiceV1Impl，继承 Impl）  
- [ ] Diff 配置类已创建（XxxAclServiceDiffBeanConfiguration）  
- [ ] Balancer 配置类已创建（XxxAclServiceBalancerBeanConfiguration）  
- [ ] 所有调用方已替换  
- [ ] Apollo 配置已生成  
- [ ] 代码编译通过