### 总结：方法论层面的“组合拳”

要最大化效率，你需要像搭积木一样组合使用这些模式。

**一个典型的高效工作流（AI Workflow）：**

1. **规划模式 (Planner)**：
    
    - _Prompt:_ "我要做一个订单取消功能，涉及库存回滚和退款，请帮我列出逻辑步骤。"
    - _AI输出:_ 步骤1, 2, 3, 4...
2. **生成模式 (Generator)**：
    
    - _Prompt:_ "根据上面的步骤1和2，生成对应的Service层代码，使用Spring的`@Transactional`注解。"
    - _AI输出:_ 初步代码。
3. **转换模式 (Transformer)**：
    
    - _Prompt:_ "将这段代码里的硬编码状态值，提取为Java枚举（Enum）。"
    - _AI输出:_ 优化后的代码。
4. **分析模式 (Analyzer)**：
    
    - _Prompt:_ "检查最终生成的这段代码，是否存在事务失效的场景？"
    - _AI输出:_ 安全确认或修复建议。

### 让AI更好干活的 3 个黄金法则（Methodology）：

1. **Few-Shot Prompting (少样本提示)**：
    
    - 不要只给指令，给它**示例**。
    - _Prompt:_ "我要生成MyBatis XML。  
        示例输入：User类...  
        示例输出：`<resultMap>...</resultMap>`  
        现在请根据这个Product类生成XML..."
    - **原理**：AI通过模仿示例，准确率会大幅提升。
2. **Iterative Refinement (迭代式优化)**：
    
    - 不要指望一次完美。
    - 把AI当成实习生。第一次做不好，指出错误（"你忘了判空"），让它重做。**对话的过程就是调试AI的过程。**
3. **Context is King (上下文为王)**：
    
    - AI如果不了解你的项目结构（用了Lombok吗？是JDK 17吗？），它就是瞎猜。
    - 在Prompt开头永远带上**技术栈声明**。