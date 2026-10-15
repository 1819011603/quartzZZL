# 小班课花名册 / 续班服务（microClazzRoster · tabKey=continuationService）

## 定位

| 项 | 值 |
|---|---|
| tab URL | `https://test-fuwu.baijia.com/crm/cronus/microClazzRoster?tabKey=continuationService` |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus` |
| 页面组件 | `src/pages/microClazzRoster/index.jsx` |
| tab 组件 | `src/pages/microClazzRoster/ContinuationService/` |
| 主 service 文件 | `src/pages/microClazzRoster/ContinuationService/service.js` |
| 后端主服务 | **student-center**（网关前缀 `component/student-center`） |

> 页面级说明见 [_page.md](./_page.md)；花名册 tab 见 [default.md](./default.md)。

## 接口清单

### 1. 列表数据（进页面 + 筛选 / 翻页 / 排序）

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面/筛选/翻页 | `getContinuationServiceList` | `/bgwApi/component/student-center/roster/small/renewal/page` | `src/pages/microClazzRoster/ContinuationService/service.js:31` | student-center | `/roster/small/renewal/page` | 分页查询续班服务列表 [3151317] | **主列表数据** |
| 总数超上限 | `getListCount` | `/bgwApi/component/student-center/roster/small/renewal/count` | `src/pages/microClazzRoster/ContinuationService/service.js:39` | student-center | `/roster/small/renewal/count` | 获取总数，当超过index配置最大count时使用 [3151318] | total 触达上限时单独取真实值 |
| 默认视图列表 | `getContinuationServiceDefault` | `/bgwApi/component/student-center/roster/small/renewal/default/page` | `src/pages/microClazzRoster/ContinuationService/service.js:13` | student-center | `/roster/small/renewal/default/page` | 分页查询续班服务列表 [3151315] | 初始化默认数据 |
| 默认视图总数 | `getListCountDefault` | `/bgwApi/component/student-center/roster/small/renewal/default/count` | `src/pages/microClazzRoster/ContinuationService/service.js:47` | student-center | `/roster/small/renewal/default/count` | 获取总数，当超过index配置最大count时使用 [3151316] | 默认视图总数 |

### 2. 全局搜索 / 筛选

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | `getDefaultValue` | `/bgwApi/component/student-center/roster/small/renewal/defaultValue` | `src/pages/microClazzRoster/ContinuationService/service.js:22` | student-center | `/roster/small/renewal/defaultValue` | 获取GlobalSearch默认值接口 [3151314] | 全局搜索默认值（`useDefaultValue`） |
| 班级变更/进页面 | `getContinuationRound` | `/bgwApi/component/student-center/roster/small/renewal/getRenewalInfo` | `src/pages/microClazzRoster/ContinuationService/service.js:5` | student-center | `/roster/small/renewal/getRenewalInfo` | 续班信息 [3151313] | 续班轮次选项 |
| 进页面 | `getRenewalPlanList` | `/component/student-center/smallClazz/filter/renewalPlan/list` | `src/pages/microClazzRoster/ContinuationService/service.js:55` | student-center | `/smallClazz/filter/renewalPlan/list` | [POST]/renewalPlan/list [3876404] | 续班计划下拉（不依赖班级） |
| 续班计划变更 | `getClazzList` | `/component/student-center/smallClazz/filter/clazz/list` | `src/pages/microClazzRoster/ContinuationService/service.js:79` | student-center | `/smallClazz/filter/clazz/list` | [POST]/clazz/list [2044937] | 班级列表；`GlobalSearch` 的 `ClazzAndPeriodNg`（内联 `api.clazz`，`components/GlobalSearch/index.js:413`）调同一 path |

### 3. 续班数据指标 / 问卷明细

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 搜索后刷新指标 | `getMicroContinuationIndicator` | `/bgwApi/component/student-center/roster/small/renewal/statistic` | `src/pages/microClazzRoster/ContinuationService/service.js:87` | student-center | `/roster/small/renewal/statistic` | 续班统计数据（可续学员数、问卷提交率、问卷预报名/考虑/不预报率、订金预报名/未报名率） [3876403] | 顶部指标卡 |
| 默认指标 | `getMicroContinuationIndicatorDefault` | `/bgwApi/component/student-center/roster/small/renewal/default/statistic` | `src/pages/microClazzRoster/ContinuationService/service.js:117` | student-center | `/roster/small/renewal/default/statistic` | 续班统计数据（可续学员数、问卷提交率、问卷预报名/考虑/不预报率、订金预报名/未报名率） [3876402] | 初始化默认指标 |
| 点「问卷明细」 | `getQuestionInfo` | `/bgwApi/component/student-center/roster/renewal/sendQuestion/getQuestionInfo` | `src/pages/microClazzRoster/ContinuationService/service.js:147` | student-center | `/roster/renewal/sendQuestion/getQuestionInfo` | 问卷信息获取 [3381630] | 校验班级绑定的问卷 |
| 问卷明细搜学员 | `getSmallClazzStudentConstants` | `/bgwApi/component/student-center/roster/small/renewal/questionnaire/search/user` | `src/services/bindingStudents.ts:61` | student-center | `/roster/small/renewal/questionnaire/search/user` | 搜索用户 [3876405] | `QuestionnaireDetail` 绑定学员搜索 |

### 4. 编辑 / 下单 / 其他

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 行内编辑保存 | `updateStudentInfo` | `/component/student-center/studentClazz/edit` | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js:13`（`ContinuationService/index.js:17` 引用） | student-center | `/studentClazz/edit` | [POST]/edit [30662] | 保存单元格修改（场景 `microContinuationService`） |
| 批量改颜色/分层 | `batchEditStudentInfo` | `/component/student-center/studentClazz/batchEdit` | `src/pages/microClazzRoster/DefaultRoster/services/microClazzRoster.js:54`（经 `hooks/useExtendComponents.js:6` 注册 `BatchColorEdit`） | student-center | `/studentClazz/batchEdit` | [POST]/batchEdit [2863102] | 底部「添加颜色/分层」 |
| 下单（非灰度） | `recommendClazzList` | `/bgwApi/product-b/b/renewMaster/recommendClazzList` | `src/services/continuationService.js:108`（`components/CreateOrder/index.jsx:7` 引用） | product-b | `/b/renewMaster/recommendClazzList` | 查询推荐班级列表 [2734275] | 创建订单推荐班级 |
| 下单灰度判断 | `getGrayService` | `/product-b/b/renewMaster/configFlag` | `src/pages/microClazzRoster/ContinuationService/components/CreateOrder/gray.js:7` | product-b | `/b/renewMaster/configFlag` | 获取配置开关 [2734336] | 决定走新下单 widget 还是推荐班级 |

### 5. 表格 schema

| 触发 | 前端方法 | 前端调用路径 | 前端代码位置 | 后端服务 | 后端 path | 接口名 [id] | 说明 |
|---|---|---|---|---|---|---|---|
| 进页面 | `getMetaData` → `getSchema`（`@coeus/render`） | coeus 低代码 schema | `src/models/microContinuationService.js:18` | coeus/render | — | — | 拉表格列 / 筛选 schema（`identification=microContinuationService`） |

> 共享组件（`ReachReportFilter`→`ReachReport`/`ReachReportNew`、`PersonalLink`→`CustomSaleLink`、`ReachBusiness`、`QuestionnaireDetail` 等）另有接口，被多页面复用，待单独归档。

## 固定入参（复现 / 联调）

列表类接口（`/roster/small/renewal/page`、`/default/page`、`/count`、`/default/count`）入参体一致：

```jsonc
{
  "identification": "microContinuationService",   // 必填！决定 GAIA 字段口径 + 哪些特殊筛选器生效
  "route": { "sceneVersionNumber": <进页面 /roster/renewal/config 拿到的场景版本号> }, // 必填，取用户可见字段
  "filter": {
    "clazzNumber": [<clazzNumber>...],            // 必填，空则直接返回空页
    "smallRenewalNumber": [<续班计划 number>],     // 续班计划（页面「续班计划」下拉）
    "smallRenewalRoundFilter": [1],               // 续班轮次，值域 = RenewalRoundEnum：0 不可续 / 1 一轮 / 2 二轮 / 3 三轮及以上
    "clazzStudentStatus": [1, 3],                 // 学员状态（组合字段）：0退班非调班/1在班非调班/2退班调班/3在班调班
    "smallRenewalReportStatus": [4],              // 续班状态：1可续已续/2可续未续/3不可续已续/4不可续未续
    "fuzzyText": ""
  },
  "pager": { "current": 1, "pageSize": 300, "total": 0 },
  "orderItem": { "name": "joinClazzTime", "order": "desc" }
}
```

- 续班轮次的值是 `RenewalRoundEnum` code（0/1/2/3），后端 `RoundIdxEnum.ROUND_IDX_MAP` 再映射到 ES `smallRoundIdx`（一轮→[1,3]）。
- **`smallRenewalRoundFilter` 必须给**：`SmallRenewalRoundFilterService.support()` 对任何字段都返回 true（只要 identification 命中），`build()` 无条件追加 `terms(smallRoundIdx, 映射结果)`；不传轮次时映射为空 → `terms(空)` 匹配 0 条。
- 指标 `/roster/small/renewal/statistic` 入参是另一套（`SmallRenewalStatReq`：`clazzNumbers[]` + `round[]`），不是上面的 `filter`。

### FE 实际请求体（从 prod 日志 `RequestLogAspect` 抄下来的真实参数）

```jsonc
{
  "filter": {
    "clazzStudentStatus": ["1", "3"],              // 学员状态：字符串数组
    "clazzNumber": ["552794618077558825"],         // 班级号：字符串数组（多班就是多元素）
    "smallRenewalRoundFilter": [1],                // 续班轮次：整数数组！0=不可续 / 1=一轮 / 2=二轮 / 3=三轮及以上
    "smallRenewalNumber": ["18252903801684672"],   // 续班计划号：字符串数组
    "fuzzyText": ""                                // 关键词搜索
  },
  "identification": "microContinuationService",
  "route": { "moduleTag": null, "sceneVersionNumber": 290652316966600704, "viewNumber": null },
  "pager": { "current": 1, "pageSize": 300, "total": 0, "hasNext": null, "approximateTotal": false },
  "quickFilter": {                                 // 续班状态筛选走这里；不筛则该字段为 null
    "type": null,
    "preRegistrationIntentFilter": null,
    "renewalReportStatusFilter": { "value": [2, 4] },  // 续班状态：整数数组，1可续已续/2可续未续/3不可续已续/4不可续未续
    "presaleStatusFilter": null, "smallLargePresaleSubjectFilter": null, "smallPresaleSubjectFilter": null,
    "smallPresaleOrderTimeFilter": null, "smallRenewalOrderTimeFilter": null
  },
  "orderItem": null
}
```

⚠️ 注意类型不一致（照抄）：`clazzStudentStatus`/`clazzNumber`/`smallRenewalNumber` 是**字符串**数组，`smallRenewalRoundFilter`/`renewalReportStatusFilter.value` 是**整数**数组。

> **续班状态 ≠ 续班轮次**：续班状态在 `quickFilter.renewalReportStatusFilter.value`（真实日志里出现过 `[2,4]`），续班轮次在 `filter.smallRenewalRoundFilter`。两者是两处、互不包含。

### 查真实入参：prod 日志 `RequestLogAspect`（student-center，app 日志）

student-center 每个请求都打一条 `RequestLogAspect`，含完整 `Parameters:`（上文 JSON）+ `Headers` + `Response`。
搜法：`serviceName=student-center / logType=app` + queryStr 用完整 token（如 `renewalReportStatusFilter`、`smallRenewalRoundFilter`、`"/roster/small/renewal/page"`）。


## 直调复现模板（本页专用；通用清单见 skill `gaotu-ticket-triage`「复现：直调页面接口」）

> 同类型问题（其它页面也适用）的通用步骤：定位知识库 → 带 `B_client` 头 → 按登录人过滤就先代课 → `identification` 等固定参数 → 查 ES/DB 核对 → 别直调 service bean。

**三步：**① 代课成该班老师 → ② 带 `B_client` 头直调 → ③ 用完 logout。

```bash
# ① 代课（账号名=拼音；吕建权=lujianquan、张嘉武=zhangjiawu）
M=~/.local/mcp-servers/venv/bin/python; C=~/.local/mcp-servers/mcpcli.py
$M $C baijia_invoke cosplay_login -k cos_account_name=<拼音>
# accountId → 账号名：SELECT account_id, email_prefix FROM gaotu.employee WHERE account_id=<id>
#                    （cluster=gaotu-center-prod / db=gaotu；主讲/二讲 accountId 见 ES mainTeacherAccountIds/assistantAccountId）

# ② 直调（务必带 -H 'B_client: GPS'）
curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" \
  'https://fuwu.baijia.com/bgwApi/component/student-center/roster/small/renewal/page' \
  -H 'content-type: application/json' -H 'traffic-env: prod' -H 'B_client: GPS' \
  --data-raw '{"identification":"microContinuationService",
    "filter":{"clazzNumber":[<班级号>],"smallRenewalNumber":[<计划号>],"smallRenewalRoundFilter":[1],
              "clazzStudentStatus":[1,3],"smallRenewalReportStatus":[4]},"pager":{"current":1,"pageSize":50}}'

# ③ 收尾
$M $C baijia_invoke cosplay_logout
```

- **必带 `B_client: GPS`**：否则页面内部 `SmallClazzUserPermissionFilterService` 的 staff 调用失败 → `{"code":42,"msg":"调用staff失败"}`。`/roster/...` 不在 `LoginInfoFilter` 自动取 bclient 的前缀里，必须手动带。
- **页面有权限过滤**：只出登录老师可见学员（`assistantAccountId`/`mainTeacherAccountIds` + postTag 通配 + 兼职账号）。用无关账号调 → 0 条，不是接口问题。
- 想核数据与页面对不上时，直接查 ES `ads_small_clazz_user` 的 `smallCanRenewal`/`smallRenewalStateStatus`/`smallRoundIdx`/`clazzStudentStatus`。


## 可续状态 / 轮次的上游链路（业绩归属，非本服务自算）

列表「续班状态」「续班轮次」底层的 `smallCanRenewal`（可续状态）、`smallRoundIdx`（轮次）**由 performance-attribution（业绩归属）服务给出**，student-data 只做同步落 ES：

- **链路**：`PERFORMANCE-ATTRIBUTION` 服务 `feignPerformance/getPerformanceRegularCanRenewalSignInfos`（Feign 适配 `PerformanceAttributionAdapter`，`com.gaotu.lvyue.client.service.PerformanceAttributionRemoteService`）→ student-data `OdsSmallCanRenewalSyncService`（MQ `CanRenewalList`，tag `SMALL_CLAZZ_USER_CAN_RENEWAL`）→ ES `ads_small_clazz_user.smallCanRenewal`/`smallRoundIdx`。
- **取数**：`PerformanceSyncAclService#getCanRenewalDto(subclazzNumber, userId)`，按 **辅导班-学员**维度；同一维度多条时优先保留「可续」（status ∈ {1,2,8}）。
- **值域 `CanRenewalStatusEnum`**：1可续-未续 / 2可续-已续 / 8可续-后置课程退款 = 可续；3不可续-非续班/非长期班/非判单命中订单 / 4不可续-无续班关系 / 5不可续-已退款 / 6不可续-过可续时间 / … / 16不可续-老学员 / 17不可续-续班配置灰名单 = 不可续。
- ⚠️ **坑**：`OdsSmallCanRenewalSyncService#updateDataMapWithExternalData` 里 `useExternal=true`（默认）时，若外部取不到该维度 → 写 **`smallCanRenewal=0`、`smallRoundIdx=0`**（0 不在枚举内 → 前端展示为「不可续」）。
- **排查「某学员为什么不可续」**：拿 `(subclazzNumber, userId)` 查 performance-attribution 的 `PerformanceRegularCanRenewalSignInfoDto.canRenewalStatus`（可 `invoke_service` 调 `PerformanceSyncAclService#getCanRenewalDto` 或直连 performance-attribution）。
- **已实测（2026-10）**：班 `552794618077558825` 学员 叶浩伟 `(subclazzNumber=34698434165737728, userId=7244103707)` → performance-attribution 返回 `canRenewalStatus=4`（不可续-无续班关系）、`roundIdx=3`（整轮）。即该班学员「不可续」是**上游业绩归属判的**，不是 student-center/student-data 的展示问题。
- **判「不可续-无续班关系(4)」的规则**（performance-attribution `AbstractRenewalSignStrategy#renewalSignCore`）：订单课程在「课程→后置课程映射」里**取不到后置续班课程** → 直接判 code=4，原因 `RenewalSignRegularReasonEnum.NOT_CONFIG_AFTER_COURSE`（**未配后置续班课程**），后续逻辑不再走。→ 该班学员全不可续 = 这些订单课程**没配后置续班课程**。
  - 后置课程映射来源：`clazzFeignService.getCourseExtensionByExtensionInfo(courseNumberList, FOLLOW_COURSE=3)` → course-center `CourseNotNormalQueryApiFeignClient#listBeContinuationCourseByNumberList`（**被续班/后置课程**）。
  - ⚠️ 且后置课程还必须落在 `getAllSettingCourseList`（有效**设置课程**）里，否则被 `filter(...)` 过滤成空、同样判 code=4 —— 所以「`course_relation_map` 有配置」≠「判单能取到后置课程」。
  - 已查：该班课程 `17133266593186453`（青藤8阶科学探究）在 `course_center.course_relation_map` **有**后置课程记录（`course_number=17133266593186453`→`relation_number=...`，`calculate_renewal_type=1`，`isdel=0`）；但 performance-attribution 仍判该班学员 code=4，需再核后置课程是否为有效设置课程 / 订单课程是否与班级课程一致。
  - **实测（2026-10）**：`CourseNotNormalQueryApiFeignClient#listBeContinuationCourseByNumberList([17133266593186453])` → `{17133266593186453:[17484092381463274]}`，即该课后置课程=**`17484092381463274`（青藤思维模拟课堂…，`publish_status=40`、`isdel=0`，有效）**。→ **后置课程是存在的**；判 code=4 的原因需继续看：① 该学员**订单的课程**（`renewalOrderConfig.getCourseNumber()`）是否等于 `17133266593186453`；② `filterNotCanRenewalCourse`（按 `courseRenewalTagFeignService.listRenewalTypeByCourseNumberList` 的 `calculateRenewalType=NO` 过滤）是否把它滤掉。
  - **根因（已实测确认）**：`listBeContinuationCourseInfoByNumberList([17133266593186453])` → `{courseNumber:17484092381463274, relationNumber:17133266593186453, calculateRenewalType:2}`。
    - `CalculateRenewalTypeEnums`：`0=无 / 1=计算 / 2=不计算`。`filterNotCanRenewalCourse` 会把 `calculateRenewalType=2(不计算)` 的续班关系**直接过滤掉**（开关 `filterNotCanRenewalCourse` 为 true 时）→ `courseNumberToAfterCourseMap` 为空 → `renewalSignCore` 里 `courseVOList` 为空 → **判 `NOT_CAN_RENEWAL_NO_AFTER_COURSE(4)`**。
    - 所以：该课(17133266593186453)的续班关系 **`calculate_renewal_type=2（不计算）`** → performance-attribution 判全体学员「不可续-无续班关系」→ 页面「一轮班全员不可续、可续学员数 0」。**属课程续班设置(calculate_renewal_type)配置问题，不是 student-center/student-data 的展示 bug。**
- **按订单查可续原因（官方接口，最直接）**：`POST https://sd.baijia.com/feitu/performance/management/suda/performance/regular/canRenewalSignReason`，body `{"orderNumberStr":"<订单号>","pager":{"current":1,"pageSize":10,"pageNum":1}}`（走 sd 网关/代理，带 `traffic-env`），返回 `signResult` + `reasons[]{step,reason,detail}`。
  - 实测订单 `426150646217966321` → `signResult=不可续-无续班关系`、`reasons[0].reason=**未配置后置续班课程**`、`assistantName=艾力西尔·阿卜力米提`（`source=PERFORMANCE-ATTRIBUTION`）。→ 与上面"calculateRenewalType=2 被过滤"完全一致。
- **改完配置怎么生效（不会自动同步 ES）**：
  1. 改 `course-center` 续班关系的 `calculate_renewal_type`（1=计算）；这步只改配置，**不触发** ES。
  2. 触发 **performance-attribution 可续标记重算**：xjob **`RenewalOrderSignHandler`**（`RenewalSignTemplate#doSign`，也可 `POST /renewal/signOrder`），param `{"clazzNumbersStr":"<班号>","clazzType":<ClazzTypeEnum>}` 只重算该班；不传 `clazzNumbersStr` 会按时间全量，别误触。
  3. 重算完发 MQ **`canRenewalChangeEvent`**（topic `gaotu_performance_renewal`，Apollo `RocketMq.service.canRenewalSign.topic/tag`）→ student-data **`OdsSmallCanRenewalSyncConsumer`**（group `GID_OdsSmallCanRenewalSyncConsumer`，顺序消费）→ 写 ES `ads_small_clazz_user.smallCanRenewal`/`smallRoundIdx`。
  4. 重算含"可续修正/可续退款修正"，`smallRoundIdx` 随同一条消息更新；ES 更新后页面/指标（有缓存）刷新即可看到。

## 关键字段口径（续班状态）

| 展示/筛选 | 来源 |
|---|---|
| 列表「续班状态」列 | GAIA 字段 `smallRenewalReportStatus`（dict `renewalReportStatus`：1可续已续/2可续未续/3不可续已续/4不可续未续），**查询时派生**，不落 ES |
| 派生规则 | `SmallRenewalFiledConvertDataQueryServiceImpl`：ES `smallCanRenewal`(1..17) 经 `RenewalStatusEnum.canRenewal2Renewal`（∈{1,2,8}=可续，否则不可续）+ ES `smallRenewalStateStatus`(1已续/2未续/null→未续) → `RenewalReportStatusEnum` code |
| 筛选翻译 | `SmallRenewalReportStatusFilterService`：code4(不可续未续) → `smallCanRenewal NOT IN (1,2,8)` AND `smallRenewalStateStatus ∈ (2,null)`；code1/2 → `smallCanRenewal IN (1,2,8)`，code3/4 → NOT IN |

> 展示与筛选都源自同一对 ES 原始字段（`smallCanRenewal` + `smallRenewalStateStatus`），口径上必然一致。

## ⚠️ 续班轮次里的「不可续」≠ 续班状态；且小班漏了联动逻辑（已确认缺陷）

**字段层面**两个是分开的：
- **续班轮次** `smallRenewalRoundFilter`（`×`选择器，来自 `getRenewalInfo.renewalRoundList`），值域 `RenewalRoundEnum`：**`0=不可续`** / 1=一轮 / 2=二轮 / 3=三轮及以上。
- **续班状态** `smallRenewalReportStatus`（走 `quickFilter.renewalReportStatusFilter`），值 1可续已续/2可续未续/3不可续已续/4不可续未续，**没有**单独一个"不可续"。

**但大班/小班行为不同（这是缺陷）**：
- 大班 `RenewalRoundFilterService`：选「不可续」时**额外**加一段 `mustNot canRenewal ∈ {1,2,8}`（即按"续班状态=不可续"过滤），与 `terms(roundIdx,[0])` 是 `should`（OR）→ 能筛出**所有不可续学员**。
- 小班 `SmallRenewalRoundFilterService`：**同一段被注释掉**（源码里可见 `// if (...RenewalRoundEnum.UN...) {...}`），只剩 `terms(smallRoundIdx,[0])` → 只能筛"轮次=0"的学员。

**后果**：班级学员都在「一轮」(如 `smallRoundIdx=3`) 且续班状态全是「不可续未续」时，小班选「续班轮次=不可续」→ **0 条**（大班同样操作能出）。这**不是筛错入口**，是小班漏移植大班的不可续联动逻辑。
- 实测（班 `552794618077558825`，56 人全 `smallCanRenewal=4`/`state=2`）：ES 按"小班现状(只 `smallRoundIdx=0`)"= **0**；按"大班逻辑(should[不可续状态, `smallRoundIdx=0`])"= **18**。
- 要按状态筛也能用「续班状态」筛选（走 quickFilter，实测 code4 → 18 条），但用户预期的是轮次下拉里的「不可续」生效。
- 修复方向：给 `SmallRenewalRoundFilterService` 补回 `RenewalRoundEnum.UN` 时 `mustNot smallCanRenewal ∈ {1,2,8}` 那段（与大班对齐）；字段名是 `smallCanRenewal`（大班是 `canRenewal`）。

## 复现 / 排查踩坑

- **ES 索引**：`ads_small_clazz_user`（物理 `ads_small_clazz_user_v1`），bean `studentServeClient`，host = Apollo `student.serve.es.cluster.host`（`es` namespace）。可 `es-apply/es_workorder.py search` 直接查。
- **别直接调 service bean 复现**：`SmallRenewalService#page/count` 依赖 `ThreadLocalHolder.getGaiaIdentification()`（由 Controller 设置），经 ACL 桥直调 service bean 时该值为空 → 所有 GAIA 筛选器 `support()` 返回 false → 条件被整体丢弃（`count` 返回全量），**会得到假的结论**。
- **ACL 桥调 Controller 也不行**：`SmallRenewalController` 是 CGLIB 代理，桥的 `findMethod` 用 `getDeclaredMethods` 找不到 `pageRenewal`（0 参方法如 `defaultValue` 可调）。→ 复现一律走 HTTP（见上「直调复现模板」）。


## 各接口最小入参（代课 + `B_client: GPS` 实测）

| 接口 | 最小入参（`identification` 一律 `microContinuationService`） | 实测 |
|---|---|---|
| `/roster/small/renewal/page`、`/count` | `filter`{`clazzNumber[]`(str)、`smallRenewalRoundFilter[]`(int)、可选 `smallRenewalNumber[]`/`clazzStudentStatus[]`/`fuzzyText`} + `quickFilter.renewalReportStatusFilter.value[]` + `pager` + `route` | 0 |
| `/roster/small/renewal/default/page`、`/default/count` | `filter:{}` + `pager` | 0 |
| `/roster/small/renewal/getRenewalInfo` | `{clazzNumbers:[...]}` | 0（回轮次选项） |
| `/roster/small/renewal/defaultValue` | `{}` | 0 |
| `/roster/small/renewal/statistic`、`/default/statistic` | `{clazzNumbers:[...], round:[...]}`（default 版可 `{}`） | 0 |
| `/smallClazz/filter/renewalPlan/list` | `{}` | 0 |
| `/smallClazz/filter/clazz/list` | `{smallRenewalNumber:[...]}`（另可配 `config`/`status`/`type`/`range`） | 0 |
| `/roster/renewal/sendQuestion/getQuestionInfo` | `{clazzNumbersStr:"...", renewalPlanId:<long>}` | 0 |
| `/roster/small/renewal/questionnaire/search/user` | `{clazzNumbers:[...], studentName:""}` | **245 代课登录暂无权限**（需给该接口配代课权限） |
| `/studentClazz/edit` | `{clazzNumber,userId,bizName,value,...}` | 0 |
| `/studentClazz/batchEdit` | 需 `列名`（`editType`+字段） | 400 列名不能为空（补参即可） |
| `/studentClazz/intimacyHover` | `{clazzNumber,userId}` | 0 |
| `/roster/renewal/reach/record` | `{clazzNumber,userId}` | 0 |
| `/roster/renewal/intimacy/course`、`/intimacy/service` | 需更多参数（仅 clazzNumber+userId → 系统异常） | 待补 |
| `/studentClazz/recentLessonSituation` | 需**课节编号** | 400 课节编号不能为空 |
| `/ai/clazzUser/levelReasonAndHistory` | 需**子班级编号** `subclazzNumber` | 400 子班级编号不能为空 |
| `/ai/renewal/reason/detail` | `{clazzNumber,userId}` | 0 |
| `/ai/renewal/reason/options` | 需 `reasonType` | 400 原因类型不能为空 |
| `/roster/renewal/renewalOrder/validate`、`/renewalPreRegistration/validate` | `{clazzNumber,renewalPlanId,type}` | 0（业务码 1=暂无流程，非报错） |
| `/b/renewMaster/recommendClazzList`（product-b 域名） | 见 product-b 文档 | 未测 |

> 除上面表里标「待补」的，其余都只差"该有的业务参数"，接口本身通。

## 青舟接口详情页

- [POST /roster/small/renewal/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151317&appId=student-center&branchName=release)
- [POST /roster/small/renewal/count](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151318&appId=student-center&branchName=release)
- [POST /roster/small/renewal/default/page](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151315&appId=student-center&branchName=release)
- [POST /roster/small/renewal/defaultValue](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151314&appId=student-center&branchName=release)
- [POST /roster/small/renewal/getRenewalInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3151313&appId=student-center&branchName=release)
- [POST /roster/small/renewal/statistic](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3876403&appId=student-center&branchName=release)
- [POST /smallClazz/filter/renewalPlan/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3876404&appId=student-center&branchName=release)
- [POST /roster/renewal/sendQuestion/getQuestionInfo](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3381630&appId=student-center&branchName=release)
- [POST /studentClazz/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=30662&appId=student-center&branchName=release)
- [POST /b/renewMaster/recommendClazzList](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734275&appId=product-b&branchName=release)
- [GET /b/renewMaster/configFlag](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=2734336&appId=product-b&branchName=release)
