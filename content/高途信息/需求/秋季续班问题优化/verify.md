# 验证记录

## 本批范围
序号65、49。其余跳过项及风险见coverage.md。泳道test-eco-2（部署前student-data/product-b均无Pod；eco-8已有其他分支）。

## 本地验证
- student-data b53b2e273：mvn8 reactor编译成功；OdsSmallRenewalSubjectSyncServiceQuitTest 3项通过（首次退课、重复退课、剩余在读重算）。复用既有Mockito测试结构，尚非数据库集成验证。
- product-server 1c4813239：mvn8 reactor编译成功；RenewalServiceImplCheckPreCourseMultiPlanTest 5项通过（正常、部分冲突、全部冲突、同计划、删除入口）。尚非真实Excel上传端到端验证。

## 测试部署
- student-data：pipeline1366234，目标b53b2e273，跟踪中。
- product-b：pipeline1366240，目标1c4813239，跟踪中。
- 未沿用发布编排24313，未执行生产发布/存量回溯。

## 运行时验证
待目标版本就绪后执行；不得将本地测试当成泳道业务验证。

## 代码评审
AICR任务2573/2574均显示取消、无findings，不能视为通过。已自行检查diff范围与边界；后续若重跑出有效结果需继续处理。
