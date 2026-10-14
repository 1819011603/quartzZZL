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


## 关键字段口径（续班状态）

| 展示/筛选 | 来源 |
|---|---|
| 列表「续班状态」列 | GAIA 字段 `smallRenewalReportStatus`（dict `renewalReportStatus`：1可续已续/2可续未续/3不可续已续/4不可续未续），**查询时派生**，不落 ES |
| 派生规则 | `SmallRenewalFiledConvertDataQueryServiceImpl`：ES `smallCanRenewal`(1..17) 经 `RenewalStatusEnum.canRenewal2Renewal`（∈{1,2,8}=可续，否则不可续）+ ES `smallRenewalStateStatus`(1已续/2未续/null→未续) → `RenewalReportStatusEnum` code |
| 筛选翻译 | `SmallRenewalReportStatusFilterService`：code4(不可续未续) → `smallCanRenewal NOT IN (1,2,8)` AND `smallRenewalStateStatus ∈ (2,null)`；code1/2 → `smallCanRenewal IN (1,2,8)`，code3/4 → NOT IN |

> 展示与筛选都源自同一对 ES 原始字段（`smallCanRenewal` + `smallRenewalStateStatus`），口径上必然一致。

## ⚠️ 两个"不可续"别搞混（高频误报）

- **续班轮次** `smallRenewalRoundFilter` 的选项来自 `getRenewalInfo.renewalRoundList`，值域 = `RenewalRoundEnum`：**`0=不可续`** / 1=一轮 / 2=二轮 / 3=三轮及以上。所以筛选栏里会出现一个字面为「**不可续**」的标签 —— 它选的是**轮次=0**（后端映射到 ES `smallRoundIdx=0`），**不是**续班状态。
- **续班状态** `smallRenewalReportStatus` 的值是 1可续已续/2可续未续/3不可续已续/4不可续未续，**没有**单独一个"不可续"。
- 典型误报：班级学员 `smallRoundIdx=3`（展示为"一轮"）、续班状态全为"不可续未续"。用户把「续班轮次」下拉里的**不可续**当成状态筛选 → 得到 0 条，其实正确（该班没有轮次 0 的学员）；真正的「续班状态=不可续未续」筛选是好的。
- 判据：看筛选标签所在**选择器**——续班计划 / 续班轮次 / 续班状态，标签文案「不可续」只可能来自续班轮次。

## 复现 / 排查踩坑

- **ES 索引**：`ads_small_clazz_user`（物理 `ads_small_clazz_user_v1`），bean `studentServeClient`，host = Apollo `student.serve.es.cluster.host`（`es` namespace）。可 `es-apply/es_workorder.py search` 直接查。
- **别直接调 service bean 复现**：`SmallRenewalService#page/count` 依赖 `ThreadLocalHolder.getGaiaIdentification()`（由 Controller 设置），经 ACL 桥直调 service bean 时该值为空 → 所有 GAIA 筛选器 `support()` 返回 false → 条件被整体丢弃（`count` 返回全量），**会得到假的结论**。
- **ACL 桥调 Controller 也不行**：`SmallRenewalController` 是 CGLIB 代理，桥的 `findMethod` 用 `getDeclaredMethods` 找不到 `pageRenewal`（0 参方法如 `defaultValue` 可调）。→ 复现一律走 HTTP（见上「直调复现模板」）。


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
