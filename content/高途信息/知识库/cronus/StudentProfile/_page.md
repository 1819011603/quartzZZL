# 学员档案 / 学员详情抽屉（cronus StudentProfile，共享组件）— 页面级

> 2026-10-16 整理：cronus master 前端源码 + GAIA `page/route` schema（scene=studentDetail）+ 各 GAIA 物料 JS 包（test CDN）+ student-center/order-b 后端源码对照。
> 结论：**cronus 只是抽屉壳（tab 栏 + 装配），各 tab 内容不在这里**——分两类：
> ① **GAIA 远程物料**（`gaia-widget-submodule/<名>` 仓库，build 成 `gaia-widget/test/<ver>/<名>.js`）；
> ② **宿主通用模块**（schema 里 `type=2`，由 `@coeus/render` 按 `props.fieldsGroup` 字段配置渲染，无独立物料仓库）。

## 定位

| 项 | 值 |
|---|---|
| 打开方式 | 各宿主页「点学员姓名 / 点学员行」弹出的抽屉（Drawer），**非独立路由** |
| 前端仓库 | cronus `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/cronus.git`（本地 `~/IdeaProjects/WebProject/cronus`，master） |
| 组件 | `src/pages/StudentProfile/`（`index.jsx` 抽屉壳 + `components/Framework/index.jsx` 装配）；以 MF `mf_cronus` 暴露 `./StudentProfile` 供其它子应用复用 |
| 渲染方式 | `COEUSRenderer` + GAIA schema：`POST /bgwApi/gaiaCenter/page/route`（header `b_client`，body `{identification:"studentDetail"}`）返回 `layoutSchema` → tab → module；GAIA 物料再按 identification 从 `POST /bgwApi/gaiaCenter/widget/detail {name}` 取版本与 CDN url |
| 共享范围 | 班级花名册(clazzRosterOL)、我的线索(uranus)、EES 等多入口**共用同一抽屉**（都来自 cronus MF `./StudentProfile`） |
| 后端主服务 | student-center（网关前缀 `component/student-center`）；订单数据源 order-b（电商） |

## Tab → 物料 → 接口

schema（scene `studentDetail`，b_client=EES，role `gaotu_boss_assistant_`）当前挂载的 tab：

| tabKey | tab | 物料(identification) | 物料类型 | 接口（backendPath，均 student-center 除非注明） |
|---|---|---|---|---|
| `UserInfo` | 用户信息 | FieldsModule / SubjectModule / MainTeacherPreference / ContactModule | 宿主通用模块 | `/ols/w/studentArchives/userInfo/queryWithFieldName`、`/ols/w/studentArchives/userInfo/updateByFieldName`、`/ols/w/studentArchives/userInfo/aiEditedFields`、`/ols/studentArchives/subjectList`、`/ols/studentArchives/saveSubjectInfo` |
| `OrderInfo` | 订单 | OrderInfoLabel（概况）+ OrderInfoList（列表） | GAIA 物料 | `temp/user/overview/dashboard`(position=orderInfo)；`/ols/w/studentArchives/orderInfo`、`/ols/w/studentArchives/orderInfo/skuTypeGroups`、`/studentClazz/getNeedDeliveryLink`、`/studentClazz/queryAllWaitSendItem`、`/studentClazz/updateOrderAddress`、`/userSecret/getBaseInfo|getAddress|getRealMobile`。详见 [orderInfo.md](./orderInfo.md) |
| `9b0bc414-…` | 考试 | StudentExamRecords | GAIA 物料 | `/exam/clazz/list`、`/exam/user/list`、`/exam/offline/config`、`/exam/remove`、`/exam/show/url`、`/base/student/clazz/baseInfo`、`/base/student/clazz/subject`、`/base/student/dictionary`、`/base/studentQuery/dictionary`、`/study/data/userClazz/baseList`、`/filter/clazz/list`、`/filter/period/list`；另有 `hl-b/ees/exam/get|submit`、`reachPortal/*` |
| `EducationalResources` | 学习资料 | EducationalResources | GAIA 物料 | `/filter/clazz/list`、`/filter/period/list`、`/study/data/userClazz/baseList` |
| `StudentCalendar` | 学员日历 | StudentCalendar | GAIA 物料 | `/studentCalendar/listData` |
| `LangerageLession` | 语言课程 | LanguageLessonCenter | GAIA 物料 | `/ols/bookCheckData` |
| `Contract` / `Contact` | 合同 | Contract | GAIA 物料 | `/studentContract/list`、`/studentContract/export` |
| `ClassDataForOnebyOne` | 班级数据 | ClassDataForOnebyOne | 宿主通用模块 | 待抓包（type=2，字段配置驱动） |
| `CourseData` | 课时账户 | CourseData | 宿主通用模块 | 待抓包（`@gaotu/hour-account` 组件） |
| `ChannelInfo` | 渠道信息 | ChannelInfo | 宿主通用模块 | 待抓包（type=2） |
| `QuestionnaireList` | 问卷 | QuestionnaireList | 宿主通用模块 | 待抓包（type=2） |
| （role 相关） | 动态 | — | 宿主通用模块 | `temp/user/overview/dashboard`(position=**studentDynamic**) + `/studentDynamic/*`（见 [StudentDynamicController]） |
| （GAIA 微组件） | AI 分析 | AiAnalysisInformations | GAIA 物料 | 见 [aianalysisinformations](../../aianalysisinformations/_page.md)（`ai/*`、`roster/refund/*` 等） |

> tab 集合随**角色 / b_client / 场景**变化（上面是 EES 助理角色的实测集合；我的线索/其它角色会多出「动态」「AI分析」等）。

## GAIA 物料清单（cockpit：`POST /bgwApi/gaiaCenter/widget/detail {name}` → currentVersion + url）

| 物料 | 版本(test, 2026-10-16) | repo（`git.baijia.com/gaotu-fe/gaotu-btech-fe/gaia-widget-submodule/<名>`） |
|---|---|---|
| OrderInfoList | 0.0.8-alpha.1 | ✔ 存在 |
| OrderInfoLabel | 0.0.4-alpha.0 | ✘ 未找到同名仓库（可能与 OrderInfoList 合并/别处） |
| StudentExamRecords | 0.0.28-alpha.5 | ✘ 同名仓库未找到（CDN 有包） |
| EducationalResources | 0.0.3-alpha.52 | ✘ 同名仓库未找到 |
| LanguageLessonCenter | 1.0.10-alpha.0 | ✘ 同名仓库未找到 |
| StudentCalendar | 0.0.8-alpha.1 | ✔ 存在 |
| Contract | 0.0.1-alpha.0 | ✔ 存在 |
| AiAnalysisInformations | 0.0.55-alpha.1 | ✔ `gaia-widget-submodule/aianalysisinformations` |
| ChannelInfo / QuestionnaireList / ClassDataForOnebyOne / CourseData / StudentDynamic | — | 非 GAIA 物料（`widget/detail` 返 30080），走宿主通用模块 |

> CDN 形如 `https://gtoss.gsxcdn.com/gaia-widget/test/<version>/<名>.js`。**接口可直接从该 JS 包 grep 出**（比 clone 仓库快）。
> 注：GAIA 物料多数**同名 git 仓库不在 `gaia-widget-submodule/` 组**，只有部分在；抓接口优先「下 CDN 包 grep 路径」。

## 排查提示

- **某 tab 空/异常** → 先 `page/route` 看这个 tab 的 module identification，再 `widget/detail` 取物料版本/CDN url；拉 JS 包 grep 接口路径，或抓包定位。
- **订单状态显示不对**（部分退款显示「已退款」）→ 物料 `OrderInfoList` 的 `src/pages/utils/constant.ts` 里 `ORDERSTATUS*MAP` 与后端枚举口径不一致，见 [orderInfo.md](./orderInfo.md)。
- **tab 双高亮**（订单信息与动态同时高亮）→ `StudentProfile`/Framework 的 `activeKey` 与内部 `curActiveKey` 两处渲染。
- **不知道 tab 的接口** → GAIA 物料下 CDN JS 包 grep `"/..."` 路径；宿主通用模块需抓包。

## 关联需求归档

- （待补）
