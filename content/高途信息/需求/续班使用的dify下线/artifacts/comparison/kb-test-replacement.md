# TEST知识库替换结果：2项通过，2项受阻

当前代码47b3dcb7e已提交推送并部署TEST。四生产应用继续Dify，无在途操作。

## 47b3dcb7两项workflow新旧实收结果

流水线1362995部署成功，新Pod student-data-5ffb5bdc94-fn6f6/10.218.236.246 Running/Eureka UP，实际commit47b3dcb7。同一业务query/同TEST库，新Java入口完成真实检索→模板渲染→网关生成，两项返回完整answer及usage。高中trace dcec0f6e-0074-4169-b3b1-323e98187ba8.0.3；素养trace e04638d2-48f8-4937-a9e2-8102755c45ce.0.3。完整旧新messages及参数断言见workflow-comparison.json及各目录old/new-llm-received.json；这是保留旧模板未消费context的严格对照，不是知识使用增强。

当前head AICR任务2403已创建后取消，非通过，无findings可处理；证据aicr-current.log。

两问题建议独立配置已读：业务应用高中256919247659254784、素养256919351674848256；Dify pre_prompt均空、max_iteration=1，业务prompt来自prompt_config各1517字。高中dataset5b040e52-8041-48af-b7d3-acefc14bc130且rerank=true；素养dataseta195df23-ba87-4ecb-b9f3-7d1c3a5a9b22且rerank=false。各自Console dataset详情实际返回Unable to verify space permissions，见对应prod-dataset.json，未用降退费库冒充，尚待正常Service API权限核实与旧agent复制工具循环实验。

## 两问题建议正式库权限实测

已用本人的有效生产dataset key从本机受控Service API分别查询两个指定库，具体HTTP/code/trace见各目录service-permission-probe.json。这不同于降退费原库86233已验证通过；不得拿别的库片段完成旧新对照。若查询拒绝，在取得相应库的正常查询权限或获授权原库导出内容前，不能完成这两项真实语料旧agent工具调用对照，不借他人身份/凭据提权。


## 未完成与具体条件

高中问题建议库5b040e52及素养问题建议库a195df23使用本人有效key均HTTP403，错误为“您没有权限查询此知识库”。需这两个库的正常查询权限或获授权原库内容后继续真实语料工具循环对照。工具循环替换尚未实现验证，不把两workflow成功推广到四场景。

## 已验证边界

两workflow以同业务输入、同隔离TEST库和已确认替代模型deepseek-flash对照，完整messages及参数相等；检索成功但旧模板未消费context，新侧保留该行为。不是生产索引召回等价或知识使用增强。4项JUnit及编译通过，AICR2403取消无findings。完整旧新请求和输出已同步飞书revision151，回读见doc-readback.json。过程证据移至implementation-history.md，仅供追溯，不作为当前状态。
