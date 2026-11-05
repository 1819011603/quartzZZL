# MR1528 静态比较：有可借鉴项，不直接合入

## 已核实的比较基线

- MR：https://git.baijia.com/gaotu/yunying_workbench/student-center/-/merge_requests/1528/diffs
- 仓库 student-center（project10690）；opened/WIP；源 feature-weixin-opt；目标 release。
- 源提交 7f9bca3872c10f4b6766f1b3a612404805e271fb；MR base/start 与查询时 release HEAD 均为 5dce9cdbb0f2398ff05b2d8ef866637f03a5630d。MR仅1个提交、8个文件。原始元数据见 mr-meta.json、target-branch.json、mr-diffs.json、mr.diff。
- 原归档默认TEST标签读取实证使用 release-5dce9cdb，与MR基线前缀对应；这是当时采样版本，未据此推定当前线上或TEST已部署源提交。本机student-center HEAD=396d84f0，未拿本地旧分支替代远端MR基线。
- 此次只读静态比较；未编译、未运行MR测试、未调写接口、未部署、未合并/cherry-pick，也未联系作者。MR文档的“18测试通过”等为作者记录，不冒充本轮验证。

## 值得借鉴的处理与收益

1. **清空标签也清空显示名称**。FieldsConvertDataQueryServiceImpl.java:76 将“集合非空”改为“集合非null”，空数组时仍写 studentTagNames=[]，可覆盖输入行残留名称。正常有标签仍同样映射。现有release在该条件下跳过写名称；是否在实际链路产生残留尚未运行复现，不能仅凭静态差异判线上缺陷。P0增加“清空后标签ID和名称都空、旧标签筛选不再命中”，只需补验收，不自动改业务代码。
2. **回溯限定更新与失败保护**。RenewalStudentTagsRecallService.java:85–129、164–199：默认dryRun、限定班级、分页批查班级及标签、按学员+课程班级精确匹配、仅更新已有ES文档studentTags、不upsert；使用物理索引和seqNo/primaryTerm保护扫描后并发写；超时/失败分片/批写部分失败报失败，finally清游标。相较本需求既有“圈班→全字段回溯”方案，这些是可参考的执行保护，减少误覆盖和伪成功。不能把它当本需求已实现或已上线。每非空批次至多一次班级批查、一次标签DAO批查、一次bulk（另有scroll），未逐文档RPC；跨批未缓存，未做性能实测。
3. **显式空串与缺源区分**。同服务:174–180 缺源/null跳过，空串写[]；重跑同值跳过。便于识别“明确清空”和“不知道原值”。UserClazzMarkInfoDataQueryServiceImpl.java:71另有null防御，但已知生产tags为NOT NULL，主要是异常环境兼容，正常生产路径收益有限。
4. **查询配置精确补齐、按新增ID回滚**。query-config.sql:1–34 先查再按scene/field/type/command判重，不整批删除共享配置。配置检查可借鉴；文中生产快照和字段数组名称仍须各环境现查，不能自动照抄执行。

所有Java路径除Handler/Request/Test外，均在 student-center-service/src/main/java/com/gaotu/yunying/student/center/；源文件保存在 mr-files/，固定SHA源码链接可按下方规则复核。

## 不能照搬的差异

- **关键规则不符**：MR回溯Service:148–154使用 ClazzDO.createTime，Request/说明/测试都按“班级创建时间”；本需求owner最终要求是 min(课节begin_time) >= 2026-01-01。两者可能相反入选，尤其2025创建/2026开课应入选、2026创建但最早课节在阈值前应排除。既有归档 artifacts/20261104-owner-ready/pure-relation-backfill-plan.md 是当前口径。不能因他人实现反改产品规则。
- **覆盖范围不同**：MR只扫描两个目标索引已存在的文档，不创建缺失文档；本需求既有圈班后更新班下学员路径还包含建档/全量字段回源。不能用这一个新任务替代整个既有链路，也不应为借鉴重复新增平行回溯。
- **失败统计边界**：批写返回部分失败会抛异常；该批已成功的文档可能已落值，但updated只在整批成功后累加。不能把异常后的updated作为准确已落值总量；需按具体ID回读并从当前源重算，不能批量旧快照覆盖。
- **共享转换器影响面**：两处小修改处在通用数据转换器，可能命中默认花名册等其它场景。后续若采纳先实际复现、再验证清空及原非空集合保留，不仅测续班页。

## 实际未涉及的内容

8个文件仅为2份配置说明/SQL、回溯Request/Service/Handler/Test、2个转换器；没有改标签保存API、备注好友检查API、异步备注任务API、身份鉴权或企微封禁判断。说明中复用现有备注接口，不构成新增能力。此MR不能解决本单缺真实老师/好友/原备注的样本问题，也不能证明封禁后的成功或失败行为。接口兼容结论仅为“变更集没有修改现有对外请求响应契约”，未做运行兼容验证。

## 建议

保留上述空集合验收和回溯执行保护作为借鉴；**当前无需合并或改代码**。若未来决定采纳，先运行复现需要改变的行为，并将回溯圈班条件改为owner已确认口径、复用原链路。此次文档交付只补验收说明和规则冲突提示，不增加发布依赖。

固定源码入口：https://git.baijia.com/gaotu/yunying_workbench/student-center/-/blob/7f9bca3872c10f4b6766f1b3a612404805e271fb/student-center-service/src/main/java/com/gaotu/yunying/student/center/domain/service/roster/RenewalStudentTagsRecallService.java#L148
