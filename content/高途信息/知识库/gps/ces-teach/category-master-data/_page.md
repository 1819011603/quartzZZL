# 门类主数据 / 价值管理（category-master-data）— 页面级

> 2026-10-16 test 环境 chrome-devtools 抓包 + 前端 ces-teach master 代码整理；后端未对照（仅凭前端代码推断 path）。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/ces-teach/category-master-data` |
| 导航 | 顶部「教学」→ 左侧「产品配置」→「价值管理」（二级菜单下还有属性管理/模板管理/学部管理，本次只抓了价值管理） |
| 基座 | GPS（test-os.baijia.com）qiankun 基座 → 子应用 ces-teach |
| 前端仓库 | ces-teach `http://git.baijia.com/esfe/ces-teach`（master `3cba956`，本地 `~/IdeaProjects/WebProject/ces-teach`） |
| 前端路由 | `src/routers/index.tsx:57-60` `/category-master-data` → `src/pages/category-master-data`；权限 `authMap['/category-master-data']='productValue'`（`:11`） |
| 后端服务 | 前端前缀 `/api/teachProduct`（`src/service/category-master-data.ts:19` `apiPrefix`） → gapm-appid `ces-teach-product-service` |

`CMD/` = `src/pages/category-master-data/`，`SVC` = `src/service/category-master-data.ts`。

## tab 列表

| tab | tabType（`ECategoryTabType`，`src/types/category-master-data.ts:37-41`） | 门类 |
|---|---|---|
| 客户价值 | `CustomerValue = 1` | 学科(Subject) / 考试(Exam) / 技能(Skill) / 信息(Info) |
| 产品包装 | `ProductPackaging = 2` | 衍生科目(Derivative) |

左侧门类树一次性拉全量（`getCategoryTree`），前端按 `subjectCategory`/`examCategory`/`skillCategory`/`infoCategory`/`derivedSubjectCategory` 字段拆成两个 tab 的树（`SVC:70-119` `transformCategoryTreeResponse`），**不是**切 tab 时分别请求。

## 页面级接口

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 请求体 | 读/写 |
|---|---|---|---|---|---|---|
| 进页面 / 切 tab（左侧门类树，两 tab 共用一份响应） | `POST /api/teachProduct/category/briefQueryAsTree` | `getCategoryTree` | `SVC:124`，调用方 `CMD/hooks/useCategoryTree.ts` | ces-teach-product-service | `{}` 或 `{"status":<0/1>}`（状态筛选） | 读 |
| 进页面 / 查询 / 翻页 / 切 tab / 新建或编辑科目成功后刷新 | `POST /api/teachProduct/category/enum/list` | `listEnum`（经 `queryNodes` 包装） | `SVC:200`（`queryNodes` 在 `SVC:206`，调用方 `CMD/hooks/useNodeList.ts`） | ces-teach-product-service | `{"type":<tabType 1/2>,"current":1,"size":10,"nodeId"?:"<左侧树选中节点>","categoryType"?:<科目类型筛选>,"name"?:"<科目名称>","code"?:"<科目ID>"}` | 读 |
| 左侧树节点右键/`plus`按钮「新建分类」→ 弹窗确定 | `POST /api/teachProduct/category/treeNode/add` | `addTreeNode` | `SVC:158`，调用方 `CMD/hooks/useCategoryOperations.ts:21` | ces-teach-product-service | `AddTreeNodeParams`（`src/types/category-master-data.ts`） | 写 |
| 左侧树节点「编辑分类」→ 弹窗确定 | `POST /api/teachProduct/category/treeNode/edit` | `editTreeNode` | `SVC:163`，调用方 `useCategoryOperations.ts:31` | ces-teach-product-service | `EditTreeNodeParams` | 写 |
| 「新建科目」→ 弹窗确定 | `POST /api/teachProduct/category/enum/add` | `addEnum` | `SVC:184`，调用方 `CMD/hooks/useNodeOperations.ts:21` | ces-teach-product-service | `AddEnumParams` | 写 |
| 行「编辑」科目 → 弹窗确定 | `POST /api/teachProduct/category/enum/edit` | `editEnum` | `SVC:189`，调用方 `useNodeOperations.ts:31` | ces-teach-product-service | `EditEnumParams` | 写 |
| （未在本页面入口发现调用，`SVC` 另有定义） | `POST /api/teachProduct/category/treeNode/listByType` | `listTreeNodeByType` | `SVC:169` | ces-teach-product-service | `ListTreeNodeByTypeParams` | 读 |

共用的 GPS 基座接口：同 `prism/clazzList`，不重复记。

## 排查提示

- 两个 tab 的左侧树数据来自**同一次** `briefQueryAsTree` 响应按字段拆分，树数据不对先看这一个接口的返回，不是分别调两次。
- `enum/list`（右侧科目列表）用 `type` 区分 tab、`nodeId` 对应左侧树选中节点、`categoryType`/`name`/`code` 是筛选表单字段，四者都可同时传。
- 新建/编辑成功后前端用 `@tanstack/react-query` 的 `invalidateQueries(['categoryTree'])` 刷新左侧树，科目列表走 `useMutation` 的 `onSuccess` 单独刷新，两者是分开的缓存失效逻辑。

## 青舟接口详情页

未查（需要按 path 搜 `ces-teach-product-service` 下的 `/category/briefQueryAsTree`、`/category/enum/list`、`/category/enum/add`、`/category/enum/edit`、`/category/treeNode/add`、`/category/treeNode/edit`）。
