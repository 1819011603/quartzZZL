# 班级管理（clazzManagePro）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 gaotu-fe-goodsmanage master 代码整理；后端对照 course-center。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-mi.gaotu100.com/ark/app-goods/clazzManagePro/list`（`?tabKey=clazzList` / `arrangeClazzList`） |
| 基座 | OES ark → 子应用 app-goods |
| 前端仓库 | gaotu-fe-goodsmanage `http://git.baijia.com/gaotu-ctech/gaotu-fe-goodsmanage`（master，本地 `~/IdeaProjects/WebProject/gaotu-fe-goodsmanage`） |
| 前端路由 | `config/routes.js:63` → `src/pages/ClazzManage/Container.jsx`，wrappers `@/wrappers/clazzManage`、`@/wrappers/channelcode`、`@/wrappers/cityData`，access `can1v1Clazz` |
| 子路由（本页跳出） | 编辑/查看/新增 `/clazzManagePro/edit/:type/:isEdit/:clazzNumber/:originClazzNumber`（`routes.js:77` → `src/pages/ClazzEdit/index`）；排课班 `/clazzManagePro/arrangeClazz/detail`（`:71` → `src/pages/ArrangeClazzEdit`）；学员列表 `/clazzManagePro/studentList/:clazzNumber/:type`（`:84`）；排课 `/clazzManagePro/arrange/...`（`:91`） |
| 后端主服务 | 网关前缀 `/course-center` → 青舟 appId `course-center`（gapm-appid `course-center-b`，仓库 **course-center**，`AdminClazzController` 类映射 `{"/b/clazz/","/ols/clazz"}`） |
| 同组件复用 | 班级大全 `/clazzEncyclopedia` 复用 `src/pages/ClazzManage/components/index.js`（`isEncyclopedia=true`），见 [../clazzEncyclopedia/_page.md](../clazzEncyclopedia/_page.md) |

## tab 列表

| tab | tabKey | 文件 | 组件 |
|---|---|---|---|
| 班级列表（默认） | `clazzList` | [clazzList.md](clazzList.md) | `src/pages/ClazzManage/components/index.js`（`Container.jsx:34` 懒加载） |
| 排课班列表 | `arrangeClazzList` | [arrangeClazzList.md](arrangeClazzList.md) | `src/pages/ArrangeClazzManage/index.jsx`（`Container.jsx:24` 懒加载） |

tab 切换写 URL `?tabKey=`（`Container.jsx:58`）。

## 页面级接口（wrapper / 全局 model，进页面即调）

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（wrapper clazzManage，字典为空时） | `GET /course-center/b/common/dictionary/all`、`/department/tree`、`/category/tree`、`/dictionary/allConfigurable` | `getDictionary` / `getNewDepartment` / `getNewTree` / `getDefaultCourseConfig` | `src/wrappers/clazzManage.js` → `src/models/clazzManage.js:101`（`src/services/clazzManage.js:13,33,27,53`） | course-center | 共享字典 [31330] / [31497] / [31498] / [31331] | 读 |
| 进页面（wrapper channelcode） | `POST /promotionManagement/activity/getChannelCodeConfig` | `getChannelList` | `src/wrappers/channelcode.js` → `src/models/useChannelCode.js:15`（`src/services/goodsManage.js:284`） | promotionmanagement | 渠道码配置 [62088] | 读 |
| 进页面（wrapper cityData） | `GET https://internal-area-api.genshuixue.com/api/areas/getLevelList?levelId=1`（dev 走 `test-area-api`） | `getAreaList` | `src/wrappers/cityData.js` → `src/models/useCity.js:6`（`src/services/clazzManage.js:45`） | 外部地区服务 | 省市列表（非青舟） | 读 |
| 进页面（umi 全局 model） | `GET /intranet-rpc/course-setting/feign/options/bff/list?fields=all` | `getCommonDictionary` | `src/models/useBffSelectItem.js:11`（`src/services/goodsManage.js:12`） | course-setting | bff 选项字典 | 读 |

各 tab 自己的接口见 tab 文件。

### 渠道码配置后端

promotion-management `promotion-management-controller/.../PromotionActivityController.java:175`（类 `promotionManagement/activity`）→ `PromotionActivityService#getChannelCodeConfig:938` → Feign `PromotionActivityRemoteService`（`/domain/promotion/b/promotionActivity/getChannelCodeConfig`）→ **promotion** 仓库 `PromotionActivityLogic#getChannelCodeConfig:2836`：**不查表**，读 Apollo `promotion.activity.channel.code.map`（`:456`）。

## 关键表

见各 tab 文件。主表 `course_center.clazz`（test 集群 gaotu-course-test，cluster_id=153，2026-10-09 `information_schema` 已确认），列表读 ES `clazz_search`（班级列表）。

## 排查提示

- 列表数据和库对不上 → 先看 ES `clazz_search`；`clazz.list.query.degradation=true` 切 DB 降级（DB 降级只支持名称/编号条件）
- 渠道下拉为空 → promotion 的 Apollo `promotion.activity.channel.code.map`

## 青舟接口详情页

- [POST /promotionManagement/activity/getChannelCodeConfig](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=62088&appId=promotionmanagement.gaotu100.com&branchName=release) id=62088
- [GET /b/common/dictionary/all](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=31330&appId=course-center&branchName=release) id=31330
- 其余见各 tab 文件
