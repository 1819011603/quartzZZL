
  

  
```  
请帮我检查刚才的 FeignClient 改造代码，确保不会影响现有功能，不会产生编译错误或运行时错误。  
  
## 检查要求  
  
### 1. 依赖检查  
- 检查 是否添加了 `blocks-tools-starter` 依赖（版本 2.0.3）  
- 检查是否排除了 `cglib` 依赖  
  
### 2. 扫描包配置检查  
- 检查 `@SpringBootApplication` 的 `scanBasePackages` 是否包含 `"com.gaotu.blocks.starter"`  
- 检查主启动类：`edu-b-crm-starter/src/main/java/com/gaotu/edu/b/crm/EduBCrmWebApplication.java`  
  
### 3. ACL 接口和实现类检查  
  
对每个 ACL 服务（PeriodAclService、CourseInfoAclService、CourseSettingEnumAclService、ParentsMeetingAclService、CourseAclService、ClazzAclService、SkuAclService、ClazzLessonAclService、ClazzLessonSectionAclService、EnumAclService）：  
  
#### 3.1 ACL 接口检查  
- 检查接口文件是否存在：`XxxAclService.java`  
- 检查接口方法签名是否与原始 FeignClient 完全一致  
- 检查包路径是否正确：`com.gaotu.edu.b.crm.adapter.remote.acl`  
  
#### 3.2 ACL 实现类检查（Impl）  
- 检查实现类文件是否存在：`XxxAclServiceImpl.java`  
- 检查是否实现了 `XxxAclService` 接口  
- 检查是否使用了 `@Service("xxxAclServiceImpl")` 和 `@Qualifier("xxxAclServiceImpl")` 注解  
- 检查是否注入了原始 FeignClient（如：`PeriodFeignService`）  
- 检查所有方法是否都是委托调用原始 FeignClient  
  
#### 3.3 ACL V1 实现类检查（V1Impl）  
- 检查 V1 实现类文件是否存在：`XxxAclServiceV1Impl.java`  
- **关键检查：V1Impl 必须继承 `XxxAclServiceImpl`，不能实现接口**  
- 检查是否使用了 `@Service("xxxAclServiceV1Impl")` 和 `@Qualifier("xxxAclServiceV1Impl")` 注解  
  
### 4. 配置类检查  
  
对每个 ACL 服务：  
  
#### 4.1 Diff 配置类检查  
- 检查配置类文件是否存在：`XxxAclServiceDiffBeanConfiguration.java`  
- 检查是否继承 `SpringBasedDiffBeanConfiguration`  
- 检查 `CONFIG_KEY_PRE` 是否为 `"gaotu.crm.diff."`  
- 检查 Bean 方法名称和 Bean 名称是否为 `xxxAclServiceDiffProxy`  
- 检查 `first` 参数类型是否为 `XxxAclServiceImpl`  
- 检查 `second` 参数类型是否为 `XxxAclServiceV1Impl`  
- 检查 `createProxy` 最后一个参数是否为 `CONFIG_KEY_PRE + first.getClass().getSimpleName()`  
  
#### 4.2 Balancer 配置类检查  
- 检查配置类文件是否存在：`XxxAclServiceBalancerBeanConfiguration.java`  
- 检查是否继承 `SpringBasedBalancerConfiguration`  
- 检查 `CONFIG_KEY_PRE` 是否为 `"gaotu.crm.balancer."`  
- 检查是否注入了 DiffProxy：`@Resource(name = "xxxAclServiceDiffProxy")`  
- **关键检查：Bean 方法必须使用 `@Primary` 注解**  
- 检查 `createGrayscaleProxy` 第一个参数是否为 `xxxAclServiceDiffProxy`  
- 检查 `createGrayscaleProxy` 第二个参数是否为 `second`  
  
### 5. 调用方替换检查  
  
#### 5.1 检查未替换的 FeignClient  
- 查找所有直接注入 FeignClient 的地方（除了 ACL 实现类内部）  
- 查找所有直接调用 FeignClient 方法的地方（除了 ACL 实现类内部）  
  
#### 5.2 检查 import 语句  
- 检查所有调用方的 import 是否已从 FeignClient 改为 ACL 接口  
- 检查是否有错误的 import（如：`import com.gaotu.edu.b.crm.adapter.remote.feign.PeriodFeignService`）  
  
#### 5.3 检查方法调用  
- 检查所有方法调用是否已从 `xxxFeignService.method()` 改为 `xxxAclService.method()`  
- 检查变量名是否已从 `xxxFeignService` 改为 `xxxAclService`  
  
### 6. 编译检查  
- 检查代码是否能编译通过  
- 检查是否有类型不匹配错误  
- 检查是否有方法签名不匹配错误  
- 检查是否有找不到类错误  
  
### 7. 方法签名一致性检查  
- 检查 ACL 接口方法签名是否与原始 FeignClient 完全一致  
- **特别注意：参数类型必须完全一致（如：`String` vs `Integer`）**  
- 检查返回类型是否一致  
- 检查方法名是否一致  
  
### 8. Bean 配置检查  
- 检查所有配置类是否都被 Spring 扫描到  
- 检查 Bean 名称是否唯一，无冲突  
- 检查 Balancer 配置类是否都使用了 `@Primary`  
- 检查 DiffProxy 注入名称是否正确  
  
### 9. 常见错误检查  
  
#### 错误 1：找不到 SpringBasedDiffBeanConfiguration  
- 检查依赖是否添加  
- 检查扫描包是否配置  
  
#### 错误 2：方法签名不匹配  
- 检查 ACL 接口方法签名是否与原始 FeignClient 一致  
- **特别注意 `getFullClazzLessonInfoByNumbers` 的参数类型**  
  
#### 错误 3：Bean 冲突  
- 检查是否有多个配置类创建了相同类型的 Bean  
- 检查是否都使用了 `@Primary`  
  
#### 错误 4：V1Impl 实现接口而不是继承  
- **关键检查：V1Impl 必须继承 Impl，不能实现接口**  
  
#### 错误 5：重复的 @Resource 注解  
- 检查是否有字段使用了多个 `@Resource` 注解  
  
#### 错误 6：缺少 import  
- 检查所有使用 ACL 接口的地方是否都有正确的 import  
  
### 10. 完整性检查  
- 检查所有需要改造的 FeignClient 是否都已改造  
- 检查所有调用方是否都已替换  
- 检查所有配置类是否都已创建  
  
### 11. Apollo 配置检查  
- 检查配置 key 格式是否正确  
- 检查配置 key 是否使用实现类名（不是接口名）  
- 检查配置值格式是否正确  
  
## 输出要求  
  
1. **列出所有发现的问题**：  
   - 编译错误  
   - 运行时可能的问题  
   - 代码质量问题  
   - 配置问题  
  
2. **对每个问题提供**：  
   - 问题描述  
   - 问题位置（文件路径和行号）  
   - 问题原因  
   - 修复建议  
  
3. **提供修复后的代码**（如果需要）  
  
4. **总结检查结果**：  
   - 总体评价  
   - 是否可以直接使用  
   - 需要注意的事项  
  
请按照以上要求进行全面检查，确保代码的正确性和完整性。  
```  
  
## 使用说明  
  
1. **直接复制上面的 Prompt** 到 AI 对话中  
2. **AI 会按照步骤执行检查**：  
   - 检查依赖配置  
   - 检查扫描包配置  
   - 检查 ACL 接口和实现类  
   - 检查配置类  
   - 检查调用方替换  
   - 检查编译错误  
   - 检查方法签名一致性  
   - 检查常见错误  
  
3. **AI 会输出**：  
   - 所有发现的问题  
   - 问题位置和原因  
   - 修复建议  
   - 修复后的代码（如果需要）  
  
4. **根据 AI 的输出修复问题**  
  
## 检查重点  
  
### 必须检查的关键点：  
  
1. ✅ **V1Impl 继承 Impl，不实现接口**  
2. ✅ **方法签名完全一致**（特别注意参数类型）  
3. ✅ **Balancer 配置使用 @Primary**4. ✅ **配置 key 使用实现类名**  
4. ✅ **所有调用方都已替换**  
5. ✅ **无编译错误**  
6. ✅ **扫描包包含 "com.gaotu.blocks.starter"**  
### 常见问题：  
  
1. **方法签名不匹配**：`getFullClazzLessonInfoByNumbers(List<Long>, String)` vs `getFullClazzLessonInfoByNumbers(List<Long>, Integer)`  
2. **缺少 import**：使用 ACL 接口但未导入  
3. **重复注解**：同一个字段使用了多个 `@Resource`  
4. **V1Impl 实现接口**：应该继承 Impl  
  
```  
  
## 检查报告模板  
  
完成检查后，使用以下模板：  
  
```  
## 检查报告  
  
### 检查时间：[日期时间]  
  
### 检查结果概览：  
- ✅ 通过项：[数量]  
- ❌ 失败项：[数量]  
- ⚠️ 警告项：[数量]  
  
### 详细问题列表：  
  
#### 问题 1：[问题标题]  
- **位置**：[文件路径:行号]  
- **类型**：[编译错误/运行时错误/代码质量/配置问题]  
- **描述**：[详细描述]  
- **原因**：[原因分析]  
- **修复建议**：[修复方法]  
- **修复代码**：[如果需要，提供修复后的代码]  
  
### 总结：  
[总体评价和建议]  
```