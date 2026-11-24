# 56b53f3c 格式恢复只读复核

时间：2026-11-24T12:19:55

核对版本：56b53f3c5b7376e7f08ce4972f055d72cd7a9469；基线8becd39fb。工作区干净。本轮仅查询AICR、读取代码/归档及写本报告，未改代码配置、未业务调用、未重跑测试。

## 结论

当前有效配置下，未发现本次diff改变未配置应用、保留Dify的知识库或SOP V2路径。这个结论是代码边界复核，不是这些未改路径逐一生产调用验证。主Worker已报告7组实收完全相等、旅程保留增强且结构对齐；本轮不重复代其验证或泛化为13个生产应用逐一实收。

| 检查项 | 证据与判断 |
|---|---|
| 应用隔离 | AiApplicationExecutor:271-275仅platformType=2按应用number读映射，默认空Map。format-config-readback.txt为8个TEST验证应用，未见SOP或知识库配置。编号是application而非agent。 |
| 未配置应用 | generateGatewayPayload格式为空时直接generatePayload(agg,query,context,gatewaySystem)，参数与改造前一致。已有第3项单测验证委派及不调用旧flat生成。 |
| Dify/4个知识库 | 非2分支调用原generatePayload(...,null)，原先corePromptOverride亦为null；路由选择、检索器未改。保留Dify的知识库不会进入新包装。代码未硬编码知识库排除表，未来误配置/强制切网关不在本结论内。 |
| SOP V2 | syncRequestTaskV2→executeCoreLogicV2:417仍AiPromptPayload.ofFlat(prompt)，未调用新增方法，不重复生成flat。 |
| 普通同步/异步 | 两者共享executeCoreLogic，配置会同时影响该应用的普通同步/异步调用；属于应用级契约。V2独立。 |
| 两层system | 新方法generate(agg,query,context)读原core及后处理；外层仅gatewaySystem。避免用外模板覆盖内指令。USER_FLAT遇非空外模板拒绝，防止丢失模板。 |
| 换行 | SYSTEM_USER_FLAT外system为gatewaySystem+一个换行，已有换行不trim；对应Dify simple_prompt_transform.py:163-164、208。 |
| 其他参数 | diff未改模型、thinking、response_format、max_tokens、accessor或重试处理。 |
| 旅程增强 | 外层沿用当前gateway_core_prompt，不从历史旧模板复制，因此不删除resolvedRefundReasonList。 |

## 本地验证证据及限度

复用/tmp/format-junit.log：JUnitCore 4.13.2，OK (6 tests)，耗时1.564秒；覆盖单user、外system+flat（含已有末尾换行）、缺省路径、非法模式、缺外system、单user不丢system。测试对generate/generatePayload使用spy替身，验证的是包装及委派，不独立证明动态数据查询或完整Executor/Apollo集成。后者须结合主Worker的实收证据。

编译复用/tmp/format-build-final.log（mvn8 test-compile BUILD SUCCESS）及/tmp/format-final-javac.log。未重复执行。

配置契约须保持JSON对象（默认{}），不要发布JSON null；代码没有null Map防护。非法格式/缺模板会抛异常，不静默退回。这些是配置约束，当前回读未见违反；未以异常配置新调业务。

## AICR

本轮再次查询仅7个历史任务，没有56b53f3c对应任务。最新#2314对应8becd39f，block=0，medium=3/low=5；不代表本次提交通过。原始查询输出/tmp/format-aicr-review-final.txt。不无限等待，不执行评审判定写操作。
