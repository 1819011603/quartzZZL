# 学员档案 / 学员详情抽屉（cronus StudentProfile，共享组件）— 页面级

> 2026-10-16 整理：cronus master 源码 + GAIA `page/route` schema（scene=studentDetail）+ 各 GAIA 物料 CDN JS 包 + **test 环境 chrome-devtools 逐 tab 抓包** + student-center/order-b 后端源码。
> **cronus 只是抽屉壳**（tab 栏 + 装配，MF `mf_cronus` 暴露 `./StudentProfile`）；各 tab 内容 = **GAIA 远程物料**（`gaia-widget-submodule/<名>`）或**宿主通用模块**（schema `type=2`，按 `props.fieldsGroup` 渲染）。

## 定位

| 项 | 值 |
|---|---|
| 打开方式 | 各宿主页「点学员姓名/点学员行」弹出的抽屉，**非独立路由** |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus.git`（本地 `~/IdeaProjects/WebProject/cronus`，master） |
| 组件 | `src/pages/StudentProfile/`（`index.jsx` 壳 + `components/Framework/index.jsx`） |
| 渲染方式 | `COEUSRenderer`+GAIA schema：`POST /bgwApi/gaiaCenter/page/route`（header `b_client`）→ tab→module；GAIA 物料按 identification 取 `POST /bgwApi/gaiaCenter/widget/detail {name}` |
| 共享范围 | 班级花名册(clazzRosterOL)、我的线索(uranus)、EES 多入口共用 |
| 后端主服务 | student-center（网关 `component/student-center` 或 `/student-center`）；订单源 order-b，问卷走 NPS/teacher-tool，渠道走 crm-service(leadsWeb) |

## Tab → 接口（**均 test 环境抓包确认**）

| tabKey | tab | 物料 | 接口 | 关键入参 |
|---|---|---|---|---|
| `UserInfo` | 用户信息 | 宿主(FieldsModule等) | `POST /student-center/ols/w/studentArchives/userInfo/queryWithFieldName`（查）、`.../updateByFieldName`（改）、`/component/student-center/ols/w/studentArchives/userInfo/aiEditedFields`；`/component/student-center/ols/studentArchives/subjectList`、`.../saveSubjectInfo` | `{userId, sceneIdentification}` |
| `OrderInfo` | 订单 | OrderInfoLabel+OrderInfoList | `POST /component/student-center/temp/user/overview/dashboard`(订单概况)；`/student-center/ols/w/studentArchives/orderInfo`(+`/skuTypeGroups`)；`/student-center/studentClazz/getNeedDeliveryLink`、`queryAllWaitSendItem`、`updateOrderAddress`；`/component/student-center/userSecret/getBaseInfo` | orderInfo `{userId, pager}`；dashboard `{userId, position:"orderInfo"}`。详见 [orderInfo.md](./orderInfo.md) |
| `9b0bc414-…` | 考试 | StudentExamRecords | `POST /component/student-center/exam/user/list`、`exam/clazz/list`、`exam/offline/config`、`exam/remove`、`exam/show/url`；`base/student/clazz/baseInfo`、`base/student/clazz/subject`、`base/student/dictionary`、`base/studentQuery/dictionary`；`study/data/userClazz/baseList`；`filter/clazz/list`、`filter/period/list` | exam/user/list `{clazzNumber,userId,subclazzNumber,subjectId,beginTime,endTime}` |
| `EducationalResources` | 学习资料 | EducationalResources | `POST /component/student-center/study/data/userClazz/baseList`、`filter/clazz/list`、`filter/period/list` | `{userId, subclazzNumber, clazzNumber}` |
| `StudentCalendar` | 学员日历 | StudentCalendar | `POST /component/student-center/studentCalendar/listData` | `{userId, start, end, calendarDataType:["apptLesson","lesson","commRec"]}` |
| `LangerageLession` | 语言课程 | LanguageLessonCenter | `POST /component/student-center/ols/bookCheckData` | — |
| `Contract`/`Contact` | 合同 | Contract | `POST /component/student-center/studentContract/list`、`.../studentContract/export` | `{userId,...}` |
| （角色相关） | 错题本 | 宿主 | `POST /component/student-center/wrongQuestion/search`、`.../search/dictionary` | `{userId, subclazzNumber, knowStatus, pager, isDownloadPage}` |
| `QuestionnaireList` | 问卷 | 宿主 | `POST /bgwApi/api/v1/close/rest/nps/questionnaire/get`（NPS）、`POST /bgwApi/teacher-tool/questionnaire/report/list` | nps `{serviceName:"EES", routeUrl, triggerType:2}`；report `{userId, pager}` |
| `ClassDataForOnebyOne` | 班级数据 | 宿主 | `POST /component/student-center/study/data/userClazz/list`；`base/student/dictionary` | `{userId, subClazzStatus:[1], pager}` |
| （学习数据/学员数据） | 学员数据 | 宿主 | `POST /component/student-center/study/data/userClazz/overview`、`study/data/userClazz/learn/overview`、`study/data/userClazz/learn/dailyTask`、`study/data/userLesson/list` | overview `{userId, clazzNumber}` |
| `ChannelInfo` | 渠道信息 | 宿主 | `POST /bgwApi/leadsWeb/common/searchMarketChannel`（**crm-service/leadsWeb**） | `{userId, pager}` → `leadsDTOS` |
| `UserDynamic` | 动态 | 宿主 | `POST /component/student-center/temp/user/overview/dashboard`(position=**studentDynamic**)；`studentDynamic/searchFollowUpInfo`、`studentDynamic/share/detail`、`studentDynamic/getIsolatedDepartment` | searchFollowUpInfo `{userId, onlyMyself, followUpType, commTagList, pager}` |
| （GAIA 微组件） | AI 分析 | AiAnalysisInformations | `ai/*`、`roster/refund/*`（见 [aianalysisinformations](../../aianalysisinformations/_page.md)） | — |

> tab 集合随角色/b_client/场景变化（上表为 EES 助理角色实测）。

## GAIA 物料清单（`POST /bgwApi/gaiaCenter/widget/detail {name}` → currentVersion/url）

| 物料 | 版本(test 2026-10-16) | git 仓库 `gaia-widget-submodule/<名>` |
|---|---|---|
| OrderInfoList | 0.0.8-alpha.1 | ✔ |
| OrderInfoLabel | 0.0.4-alpha.0 | ✘（同名仓库未找到） |
| StudentExamRecords | 0.0.28-alpha.5 | ✘ |
| EducationalResources | 0.0.3-alpha.52 | ✘ |
| LanguageLessonCenter | 1.0.10-alpha.0 | ✘ |
| StudentCalendar | 0.0.8-alpha.1 | ✔ |
| Contract | 0.0.1-alpha.0 | ✔ |
| AiAnalysisInformations | 0.0.55-alpha.1 | ✔ `gaia-widget-submodule/aianalysisinformations` |

> CDN：`https://gtoss.gsxcdn.com/gaia-widget/test/<ver>/<名>.js` → **直接下包 grep `"/..."` 即可得接口**（比 clone 快）。多数物料同名仓库不在 `gaia-widget-submodule/` 组。
> 宿主通用模块（ChannelInfo/QuestionnaireList/ClassDataForOnebyOne/CourseData/FieldsModule…）非 GAIA 物料，`widget/detail` 返 30080，接口靠抓包。

## 排查提示

- **某 tab 空/异常** → `page/route` 看 module identification → `widget/detail` 取物料版本 → 下 CDN 包 grep 接口 / 抓包。
- **订单状态「部分退款」显示成「已退款/已支付」** → 见 [orderInfo.md](./orderInfo.md) 结论：order-b 文案层就把全退/部分退合并了。
- **tab 双高亮**（订单与动态同时高亮）→ Framework 的 `activeKey` 与内部 `curActiveKey` 两处渲染。
- 宿主通用模块接口统一走 `/bgwApi/component/student-center/...`；渠道信息例外（`/bgwApi/leadsWeb/...`，crm-service）。
