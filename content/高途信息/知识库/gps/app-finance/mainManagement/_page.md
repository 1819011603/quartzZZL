# 企业主体管理（mainManagement）— 页面级

> 2026-10-16 test 环境 chrome-devtools 抓包 + 前端 ecommerce-fe-finance master 代码整理；后端未对照（仅凭前端代码推断 path）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/app-finance/mainManagement` |
| 导航 | 顶部「资金」→ 左侧「主体管理」（同级还有商户管理/应用管理/收款主体规则/收款主体组管理/学员账户） |
| 基座 | GPS（test-os.baijia.com）qiankun 基座 → 子应用 `gps/micro-ecommerce-fe-finance` |
| 前端仓库 | ecommerce-fe-finance `http://git.baijia.com/gaotu-fe/gaotu-btech-fe/ecommerce-fe-finance`（master `0fa73bf`，本地 `~/IdeaProjects/WebProject/ecommerce-fe-finance`） |
| 前端路由 | `routes.js:6-10` `/mainManagement` → `src/pages/mainManagement` |
| 后端服务 | 前端调用路径前缀 `/newpay-manager`（网关实际地址多一层 `/bgwApi`，见页面级接口列） → gapm-appid `newpay-admin-web` |

## tab 列表

页面无 tab，单一列表（仅展示已绑定商户号的主体）+ 筛选表单（主体名称/主体编号/信用代码/主体状态/创建时间/变更时间/税务登记&注销时间）。

## 页面级接口

`MM/` = `src/pages/mainManagement/`。

| 触发 | 前端调用路径 | 前端文件 | 后端服务 | 请求体 | 读/写 |
|---|---|---|---|---|---|
| 进页面 / 查询 / 翻页 | `POST /newpay-manager/channel/company/list` | `MM/index.tsx:152` | newpay-admin-web | `{"pager":{...},"name"?,"subjectNumber"?,"creditCode"?,"companyStatus"?,"createTime"?,"updateTime"?,"taxRegistrationTime"?,"taxCancellationTime"?}` | 读 |
| 行「关联商户号」→ 抽屉 | `POST /newpay-manager/channel/company/merchants` | `MM/MerchantDrawer.tsx:84`，`defaultParams={id: record.id}` | newpay-admin-web | `{"id":<主体id>,"pager":{...}}` | 读 |
| 行「变更日志」→ 抽屉 | `POST /newpay-manager/channel/company/history` | `MM/HistoryDrawer.tsx:52`，`defaultParams={subjectNumber: record.subjectNumber}` | newpay-admin-web | `{"subjectNumber":"<主体编码>"}`（抽屉内不分页，`pagination={false}`） | 读 |

共用的 GPS 基座接口：同 `prism/clazzList`，不重复记。

## 排查提示

- 「关联商户号」按行上的数据库自增 `id` 查询（不是主体编号 `subjectNumber`）；「变更日志」反过来按 `subjectNumber` 查。两个抽屉用的 key 不一样，对不上数据先确认传的是哪个字段。
- 列表页面标注「仅展示已绑定商户号的主体」，说明 `channel/company/list` 后端已经按绑定关系过滤，未绑商户号的主体不会出现在这里。
- 变更日志列（变更字段/变更前/变更后）是通用字段名（`field`/`changeBefore`/`changeAfter`），具体记录哪些字段变更由后端决定，前端不过滤。

## 青舟接口详情页

未查（需要按 path 搜 `newpay-admin-web` 下的 `/channel/company/list`、`/channel/company/merchants`、`/channel/company/history`）。
