# 续班计划详情 / 续班流程（renewalProcess）

> 2026-10-09 test 环境抓包 + product-server 代码 + test 库实查整理。

## 定位

| 项 | 值 |
|---|---|
| tab URL | 详情页 `continuation-classes/detail?n=<计划number>` → 「续班流程」tab |
| 后端主服务 | product-b（仓库 product-server，`ProcessController` `@RequestMapping("/b/renewal/process")`） |
| 业务代码 | `product-server-domain/.../service/renewal/questionnaire/QuestionnaireService.java` |

流程类型（`process_config.type`）：1=续班问卷 / 2=续班购物车 / 3=预报名。
节点类型（`node_config.type`）：1=准备问卷 / 2=问卷发放 / 3=续班购物车 / 4=预报名配置 / 5=预报名链接发放 / 6=扩科配置。

## 接口清单

| 触发 | 前端调用路径 | 后端 path | 接口名 | 说明 |
|---|---|---|---|---|
| 进 tab | `GET /product-b/b/renewal/process/superAdministrator` | 同左去 `/product-b` | 是否超管 | — |
| 进 tab | `POST /product-b/b/renewal/process/list` | `/b/renewal/process/list` | 流程列表 | 入参 `{"renewalNumber"}`；回 `processConfig` + `nodeConfigs` |
| 添加流程 / 管理流程 | `POST .../process/edit` | `/b/renewal/process/edit` | 编辑流程 | 写操作 |
| 准备问卷 → +管理问卷（弹窗） | `POST .../process/questionnaire/list` | `/b/renewal/process/questionnaire/list` | 节点下问卷列表 | 入参 `{pager, nodeNumber, processNumber, renewalNumber}`；回 `bizId`(=问卷ID/作品ID)、`number`、`departments/grades/subjects` |
| 管理问卷 → +绑定问卷 | `POST .../questionnaire/validate` → `.../questionnaire/bind` | 同名 | 校验 / 绑定 | 写操作；同一 bizId 只能绑一个计划 |
| 解绑 | `POST .../questionnaire/unbind` | 同名 | 解绑 | 已有填写记录不可解绑 |
| 问卷回收 | `POST .../questionnaire/record/page`、`.../record/detail` | 同名 | 填写记录 | — |

> `questionnaire/list` 是 POST 接口，浏览器直接打开（GET）只会返回错误 JSON，不是页面。

## 问卷 → 班级怎么取数

页面上的「问卷ID」= 未来项目（问卷平台）作品ID = `gaotu.questionnaire.biz_id`。

绑定时只存「问卷 + 部门/年级/学科条件」，**不直接存班级**。保存后 `calculateRenewCourseRelation` 按规则引擎把问卷匹配到计划下每个前置课程，写回 `renew_master_course_relation.questionnaire_number`，并发 MQ tag `preCourse_questionnaire_change`。班级再由前置课程关联出来（`match(clazzNumber, renewalNumber)` 就是反向用这条链）。

```
questionnaire.biz_id（问卷ID/作品ID）
  └ questionnaire.number
      └ renew_master_course_relation.questionnaire_number → pre_course_number（前置课程）
          └ course_center.clazz.course_number → clazz.number（班级）
```

| 表 | 库 / test 集群 | 关键列 |
|---|---|---|
| `questionnaire` | `gaotu`（mysql-query 按表名可唯一定位） | `number`, `biz_id`, `node_number`, `process_number`, `is_del` |
| `questionnaire_ext` | 同上 | `questionnaire_number`, `relation_type`(DEPARTMENT/COURSE_GRADE/COURSE_SUBJECT), `relation_value` |
| `renew_master_course_relation` | 同上 | `renew_master_number`, `pre_course_number`, `questionnaire_number`(0=未匹配), `isdel` |
| `process_config` / `node_config` | 同上 | `renewal_number`, `type`, `config_type` |
| `course_center.clazz` | test 在 `gaotu-course-test`(cluster_id=153) | `number`, `course_number` |
| `questionnaire_bind_data` | `gaotu` | 实际发放记录：`biz_id`, `clazz_number`, `account_id` |
| `questionnaire_record` | `gaotu` | 实际填写记录：`biz_id`, `clazz_number`, `record_id`, `format_data` |

取「问卷ID + 课程ID」（产品口径的绑定关系）：

```sql
SELECT q.biz_id AS questionnaire_id, r.renew_master_number, r.pre_course_number
FROM gaotu.renew_master_course_relation r
JOIN gaotu.questionnaire q ON q.number = r.questionnaire_number AND q.is_del = 0
WHERE r.isdel = 0 AND r.questionnaire_number > 0;
```

再拿 `pre_course_number` 关联 `course_center.clazz.course_number` 得到班级（跨库，需要数仓同步后 join）。

test 实测（2026-10-09）：计划 `583779043812329472` → 问卷 biz_id `17745196694569572` → 前置课程 `583779051603232768` → 班级 `583779054195312640`。

注意：
- 「绑定关系」看 `renew_master_course_relation`；`questionnaire_bind_data` / `questionnaire_record` 只覆盖**实际发过 / 填过**的班级，不等于绑定范围。
- 同一前置课程只会落一个问卷（规则按问卷创建时间排优先级，先建的优先）。
- 改绑或新增问卷会全量重算该流程下的前置课程，所以按 `update_time` 增量同步要覆盖这种批量更新。
- 这些是 product-server 的 `gaotu` 业务库，不是 ees 库。

## 排查提示

- 班级/学员看不到问卷 → 先查该前置课程 `renew_master_course_relation.questionnaire_number` 是否为 0，再看 `questionnaire_ext` 条件是否命中课程的年级/学科/部门
- 问卷已提交但花名册显示未发送 → 工单 `续班与业绩/续班问卷状态/`

## 青舟接口详情页（product-b / release）

- [POST /b/renewal/process/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734226&appId=product-b&branchName=release) id=2734226
- [POST /b/renewal/process/questionnaire/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734210&appId=product-b&branchName=release) id=2734210
- [POST /b/renewal/process/questionnaire/validate](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3364006&appId=product-b&branchName=release) id=3364006
- [POST /b/renewal/process/questionnaire/bind](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734156&appId=product-b&branchName=release) id=2734156
- [POST /b/renewal/process/questionnaire/unbind](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734178&appId=product-b&branchName=release) id=2734178
- [POST /b/renewal/process/questionnaire/record/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734160&appId=product-b&branchName=release) id=2734160
- [POST /b/renewal/process/questionnaire/record/detail](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734146&appId=product-b&branchName=release) id=2734146
