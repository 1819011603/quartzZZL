

### # jackson（三）序列化反序列化依赖于getter setter方法

在默认情况下，ObjectMapper在序列化属性时会依赖getter方法。反序列化是会依赖setter方法。


**Jackson 如何依赖 getter/setter 方法？**

Jackson 通过反射机制来获取对象的属性值，并将其转换为 JSON 字符串。它会遍历对象的字段，然后调用对应的 getter 方法来获取属性值，并将这些值序列化到 JSON 中。反序列化时，它会根据 JSON 数据中的属性名，调用对应的 setter 方法来设置对象的属性值。

**为什么依赖 getter/setter 方法？**

- **类型安全:** 通过 getter/setter 方法，可以确保对象的属性访问是类型安全的，避免了直接访问对象字段可能导致的错误。
- **可维护性:** 通过 getter/setter 方法，可以方便地修改对象的属性访问逻辑，例如添加验证、转换等操作。
- **可扩展性:** 通过 getter/setter 方法，可以方便地扩展对象的序列化和反序列化逻辑，例如使用自定义的序列化器。
- **灵活性:** 通过 getter/setter 方法，可以灵活地控制对象的序列化和反序列化行为，例如选择哪些属性进行序列化，以及如何序列化这些属性。



**Gson** 适合于需要序列化内部状态或不希望修改类以添加getter方法的情况，但要注意隐私和性能。
- **Jackson** 和 **FastJson** 更适合于API设计良好（有适当的getter/setter）的对象，并且更关注于性能和封装。其中，Jackson在国际上更为流行，而FastJson在中国使用较多，尤其是在需要高性能的场景下。


- **Gson:** 使用反射，遍历所有属性，性能相对较低。
- **Jackson 和 FastJson:** 使用 getter 方法，性能相对较高。

**需要注意的是:**

- Gson 也提供了一些配置选项，可以控制是否使用反射，例如通过 `Expose` 注解来指定哪些属性需要序列化。
- Jackson 和 FastJson 也支持使用注解来控制序列化行为，例如 `@JsonIgnore` 注解可以忽略某些属性。




- **Gson** 和 **Fastjson** 默认不会序列化 `null` 值的字段。
- **Jackson** 默认会序列化 `null` 值的字段。