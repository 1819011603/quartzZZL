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

## 运行时验证
已核对目标版本就绪后调用（均test-eco-2）：
- DwsGpsClazzUserSubjectDao#listByUserId(6826321921)返回[]，trace 51ea0532-fbe5-4a93-a168-3600b458824a.0.3。
- OdsSmallRenewalSubjectSyncService#doConsume，退课班535775905702934528、user6826321921，返回Success，trace208df7ad-8b44-4681-8524-facedc47652a.0.3；新Pod日志确认命中。
- 进一步核对候选小班课程16725115573830310为2026/C、年级11/12/13，大班574516867257964544为2026/Q、年级21。该样本不满足同学期同年级清理条件；本次Success只证明入口与跳过路径，不能证明ES清空。需要同学期同年级的大/小班隔离测试数据后完成清空回读。
- RenewalServiceImpl#batchFollowRelation，plan=-20261126、operationType=1，返回“续班计划未配置任何属性信息”，符合无效计划预期；trace c29b8820-1ec8-4717-bbb2-5ce0ddfe6163.0.3。真实Excel跨计划冲突及合法行写入仍未做运行时验证。
- student-data启动出现180秒readiness等待告警，随后实际UP；product-b启动日志成功、当时error.log为空。

## 代码评审
AICR任务2573/2574均显示取消、无findings，不能视为通过。已自行检查diff范围与边界；后续若重跑出有效结果需继续处理。
