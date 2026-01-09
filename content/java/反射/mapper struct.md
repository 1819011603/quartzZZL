
### **@Builder 不会自动处理父类字段**

- Lombok 的 `@Builder` 默认**只会为当前类的字段生成 builder 方法**，**不会包含父类的字段**。
- 也就是说，如果 `page` 字段在父类，`@Builder` 生成的 builder 不会有 `page(...)` 这个方法。
- MapStruct 在用 builder 时，找不到 `page` 的 setter 或 builder 方法，自然就无法设置。


### . **为什么之前可以？**

- 你没加 `@Builder` 时，Lombok 只生成 getter/setter，MapStruct 能直接用 setter。
- 加了 `@Builder`，MapStruct 检测到有 builder，就会用 builder 模式，但 builder 没有父类字段的 set 方法，导致无法设置。



- `@Data` 生成 getter/setter/toString/equals/hashCode/构造方法
- `@Builder` 生成 builder()、Builder 内部类、链式赋值方法、build() 方法
- 一起用时，**两者功能叠加**，互不影响




### **坑1：@Builder 不支持父类字段**

- Lombok 的 `@Builder` 只会为当前类生成 builder，不包含父类字段。
- **解决**：用 `@SuperBuilder` 替代，父子类都要加。

### **坑2：Lombok 生成的 setter/getter 被 MapStruct 找不到**

- 可能是 IDE 没装 Lombok 插件，或编译器没加 Lombok 依赖，导致 MapStruct 生成代码时找不到方法。
- **解决**：IDE 安装 Lombok 插件，Maven/Gradle 加上 Lombok 依赖。

### **坑3：MapStruct 版本太低**

- 低版本 MapStruct 对 Lombok 支持不完善，尤其是 builder 模式。
- **解决**：升级到 MapStruct 1.4.x 及以上，推荐 1.5.x。

### **坑4：泛型、嵌套对象、集合类型 builder 不生效**

- Lombok builder 对泛型、集合、嵌套对象支持有限，MapStruct 可能无法自动映射。
- **解决**：手写映射方法，或用 `@Mapping` 明确指定。

### **坑5：Lombok @Builder 默认不生成 setter**

- builder 只生成链式赋值方法，不生成 setter，MapStruct 用 builder 时不会用 setter。
- **解决**：如果需要 setter，单独加 `@Setter`。

### **坑6：MapStruct 生成实现类找不到 Lombok 生成的方法**

- 可能是多模块项目，Lombok 只在主模块依赖，编译时找不到。
- **解决**：所有用到 Lombok 的模块都要加依赖。

### **坑7：IDEA 缓存/编译问题**

- Lombok/MapStruct 生成的代码没刷新，导致映射失败。
- **解决**：`mvn clean compile` 或 `gradle clean build`，IDEA Invalidate Caches。