# 判单配置 / 判单/分边开关（judgeOrderConfig）

## 定位

| 项 | 值 |
|---|---|
| tab | `/ark/app-yunfan/newJudgeConfig` 默认 tab「判单/分边开关」 |
| 前端仓库 | gaotu_yunfan_fe（见 [_page.md](_page.md)） |
| tab 组件 | `src/pages/JudgeOrderConfig/index.js`（service `src/pages/JudgeOrderConfig/service.js`） |
| 后端主服务 | performance-attribution（`AttributionSettingController`） |

## 接口清单

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 path | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进 tab | `GET /intranet-rpc/course-setting/feign/options/bff/list` | `getCourseDictionary` | `src/pages/JudgeOrderConfig/JudgeSelectGroup.js:52`（`src/services/dictionaryService.js:65`） | course-setting | 授课模式/课程类型选项 | 读 |
| 进 tab（自动查询）/查询/重置/切筛选/翻页 | `POST /performance/management/setting/list` | `list` | `src/pages/JudgeOrderConfig/index.js:46`（`service.js:25`）；翻页 `JudegeTable.js:102` | `/performance/management/setting/list` | 判单开关列表 [36973] | 读 |
| 「编辑」/「批量配置」→ 确定 → 二次确认 | `POST /performance/management/setting/modify` | `modify` | `src/pages/JudgeOrderConfig/EditModal.js:137`（`service.js:15`） | `/performance/management/setting/modify` | 修改判单开关 [36975] | 写 |
| 批量配置后弹失败反馈 | `GET /performance/management/setting/enum` | `getFailureReason` | `src/pages/JudgeOrderConfig/components/FeedbackTableModal.js:37`（`service.js:30`） | `/performance/management/setting/enum` | 失败原因枚举 [36976] | 读 |

入参示例（抓包）：`{"pager":{"pageNum":1,"pageSize":20},"arrangeModeType":1,"beginTime":...,"endTime":...}`

## 关键表（`gaotu_stat` 库）

| 表 | 含义 |
|---|---|
| `gaotu_stat.performance_attribution_setting` | 判单/分边开关主表，`is_attribution`（判单开关）、`extend_distribute_type`（分边） |
| `gaotu_stat.performance_extend_distribution_extension` | 分边按班明细 |
| `gaotu_stat.performance_attribution_setting_log` | 修改日志（`setting/modify` 时插入） |

列表里的班级来自 Feign（`clazzFeignService`、`menShenFeignService`），不查 MySQL。

## 排查提示

- 「该订单不参与判单」/判单没跑 → 先看这里对应课程的判单开关；另见工单 `续班与业绩/` 下业绩归因相关案例

## 青舟接口详情页

- [POST /performance/management/setting/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36973&appId=performance-attribution&branchName=release) id=36973
- [POST /performance/management/setting/modify](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36975&appId=performance-attribution&branchName=release) id=36975
- [GET /performance/management/setting/enum](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36976&appId=performance-attribution&branchName=release) id=36976
