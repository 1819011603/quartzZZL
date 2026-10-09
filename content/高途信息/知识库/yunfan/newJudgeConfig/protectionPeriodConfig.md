# 判单配置 / 正价课续班配置 & 体验课续班配置（protectionPeriodConfig）

两个 tab 共用同一组件，`pageType` 1=正价课 / 2=体验课，请求里 `accessCourseType=1/2`。

## 定位

| 项 | 值 |
|---|---|
| tab | `/ark/app-yunfan/newJudgeConfig` →「正价课续班配置」/「体验课续班配置」 |
| 前端仓库 | gaotu_yunfan_fe（见 [_page.md](_page.md)） |
| tab 组件 | `src/pages/NewJudgeConfig/UniversalPage.js`；弹窗 `src/pages/NewJudgeConfig/components/EditModal.js`；service `src/pages/NewJudgeConfig/services/index.js` |
| 后端主服务 | performance-attribution（`AttributionSettingController`） |

## 接口清单

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端 path | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 切 tab（首次）/查询/翻页/刷新 | `POST /performance/management/get/protection/period/config` | FeituData fetch | `src/pages/NewJudgeConfig/UniversalPage.js:201` | 同左 | 续班保护期配置列表 [36977] | 读 |
| 点「导出」 | `POST /performance/management/export/protection/period/config` | `getExport` | `UniversalPage.js:96`（`services/index.js:4`） | 同左 | 导出（异步发邮件） [36978] | 读 |
| 正价课「模板配置」→ 选文件 | `POST /performance/management/file/upload` | antd Upload action | `components/EditModal.js:673` → `components/Upload.js:71` | 同左 | 文件上传 [36986] | 写 |
| 正价课「模板配置」→ 确定 | `POST /performance/management/upload/regular/config` | `getTemplateSubmit` | `components/EditModal.js:150`（`services/index.js:12`） | 同左 | 正价课模板导入 [36980] | 写 |
| 正价课「编辑」/「批量配置」保存 | `POST /performance/management/modify/regular/protection/config` | `getLongTermConfig` | `components/EditModal.js:214`（`services/index.js:20`），modifyType 1=编辑 / 2=批量 | 同左 | 修改正价课保护期 [36979] | 写 |
| 体验课「编辑」/「批量配置」保存 | `POST /performance/management/modify/experience/config` | `getShortTermConfig` | `components/EditModal.js:242`（`services/index.js:28`） | 同左 | 修改体验课配置 [36974] | 写 |

模板下载走 CDN（`p.gsxcdn.com` xlsx），不是后端接口。

## 关键表（`gaotu_stat` 库）

| 表 | 含义 | 涉及接口 |
|---|---|---|
| `gaotu_stat.clazz_renewal_config` | 班级可续/续班配置 | 查询、导出、正价课修改、体验课修改（先删后插） |
| `gaotu_stat.wide_clazz_protect_window_config` | 班级保护期窗口 | 查询、导出、正价课修改（先删后插） |
| `gaotu_stat.regular_batch_modify_upload` | 正价课模板导入记录 | `upload/regular/config` |
| `gaotu_stat.can_renewal_config` | 灰度上传路径写入 | `upload/regular/config` |

## 青舟接口详情页

- [POST /performance/management/get/protection/period/config](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36977&appId=performance-attribution&branchName=release) id=36977
- [POST /performance/management/export/protection/period/config](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36978&appId=performance-attribution&branchName=release) id=36978
- [POST /performance/management/file/upload](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36986&appId=performance-attribution&branchName=release) id=36986
- [POST /performance/management/upload/regular/config](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36980&appId=performance-attribution&branchName=release) id=36980
- [POST /performance/management/modify/regular/protection/config](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36979&appId=performance-attribution&branchName=release) id=36979
- [POST /performance/management/modify/experience/config](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=36974&appId=performance-attribution&branchName=release) id=36974
