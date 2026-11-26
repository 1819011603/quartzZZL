# 验证记录

## 本批范围
序号65、49。其余跳过项及风险见coverage.md。泳道test-eco-2（部署前student-data/product-b均无Pod；eco-8已有其他分支）。

## 本地验证
- student-data b53b2e273：mvn8 reactor编译成功；OdsSmallRenewalSubjectSyncServiceQuitTest 3项通过（首次退课、重复退课、剩余在读重算）。复用既有Mockito测试结构，尚非数据库集成验证。
- product-server 1c4813239：mvn8 reactor编译成功；RenewalServiceImplCheckPreCourseMultiPlanTest 5项通过（正常、部分冲突、全部冲突、同计划、删除入口）。尚非真实Excel上传端到端验证。

## 测试部署
- student-data：pipeline1366234，目标b53b2e273，镜像feature-renewal-autumn-optimization-b53b2e27-20261126114033，Pod student-data-5b8b79886b-v5jnc（10.218.239.205）Running/Eureka UP。
- product-b：pipeline1366240，目标1c4813239，镜像feature-renewal-autumn-optimization-1c481323-20261126114133，Pod product-b-6f96b6945d-v492j（10.218.239.180）Running/Eureka UP。
- 未沿用发布编排24313，未执行生产发布/存量回溯。

## 代码评审
AICR任务2573/2574均显示取消、无findings，不能视为通过。已自行检查diff范围与边界；后续若重跑出有效结果需继续处理。

## 当前真实联调结论
- 65已验证：test-eco-2/b53b2e27，同Pod运行时needHandleLarge/recalcForceSwitch/effect均true。2025/C、年级21匹配大小班，真实源库、分班关系、消费者及异步ES回读。最后退出trace d2464630-97e3-491b-9015-7cafed89c48f.0.3：[]/0；重复退出trace 0006a7ad-e3ad-4954-b8f2-c1701a2c9524.0.3：仍[]/0；同维度剩余在读trace 0b1312f2-e740-4d94-852c-a718484afb51.0.3：数学/1。独占源库和大小班ES均清理回读为零。证据 /tmp/renewal65-w1-result.md 与其中原始回读文件。
- 65边界：通过ACL桥注入真实消费者，未覆盖上游真实退课发MQ、事件乱序及快照竞态；无DAO mock，不代表生产存量修复。
- 49未验收：当前镜像feature-renewal-autumn-optimization-1c481323-20261126114133，Running/Eureka UP。真实Excel已生成，但同线程身份隔离包装被Arthas strict invocation mode拒绝加载；未关闭保护，未执行五场景导入、未发送邮件。需受支持的同线程执行入口或可登录且无收件人的测试身份。
- 49清理：临时计划/属性/绑定已独立回读为零，Pod临时java/class/xlsx已删除回读不存在。保留独占课程592627513442762752、592627540829470720、592627558411993088，业务detail已回读canFollowCourse=1，计划绑定查询[]，供续验使用。证据 /tmp/renewal49-w1-result.md、/tmp/renewal49-final-pod-metadata.json、/tmp/renewal49-final-bindings.json。
- 本轮未新增业务代码提交或部署，无生产写、无在途子任务。既有风险与回滚限制仍见coverage.md。

## 受支持入口与批次补查
- 49：正式xjob登记只有product-task，唯一在线执行器位于其他泳道，不能用于当前test-eco-2/product-b镜像验收。48个登记测试账号查询均有邮箱，trace 2c70f767-1316-4d0d-bf9a-29c5bcf077dc.0.3。未触发任务、未添加测试后门、未关闭严格保护。三门保留课程计划绑定复查[]。证据 /tmp/renewal49-xjob-groups.json、/tmp/renewal49-supported-accounts.json、/tmp/renewal49-w1-result.md。最小外部条件：可定向当前镜像的正式同线程测试入口，或无通知副作用的可登录隔离身份。
- 52：最近可见常规链3297→4319→7743→9593均为2026-11-25，handleCode均200；logId依次5308869816、5310217222、5310295627、5310387678。3297原执行器10.243.53.216:9999拒绝连接，未取得正文证明四单覆盖；修正入口有当日范围限制，不能宣称全历史回溯完成。证据 /tmp/renewal-rest-w1-result.md及所列四份日志。
- 25：按技能正常刷新登录态后重试，仍CAS code700；已停止重复请求。证据 /tmp/renewal-rest-w1-bi-config-retry.json。44仍无首次变化时间和写入审计，未继续无证据归因。
