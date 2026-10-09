# 产品线（product-line）— 页面级

> 2026-10-09 test 环境 chrome-devtools 抓包 + 前端 ces-teach master 代码整理；后端对照 ces-teach-product。

## 路由链路

| 项 | 值 |
|---|---|
| 页面 URL | `https://test-os.baijia.com/gps/ces-teach/product-line` |
| 基座 | GPS（test-os.baijia.com）qiankun 基座 → 子应用 ces-teach（青舟 serviceCode `baijia.gt.jiaoyan.ces-fe.ces-teach`） |
| 前端仓库 | ces-teach `http://git.baijia.com/esfe/ces-teach`（master `c0b4bc8`，本地 `~/IdeaProjects/WebProject/ces-teach`） |
| 前端路由 | `src/routers/index.tsx:65-71` `/product-line` → `src/pages/product-line/index.tsx`；权限 `authMap['/product-line'] = 'productLine'`（`src/routers/index.tsx:13`，`AuthGuard` 无权限渲染 NoAuth） |
| 后端服务 | 前端前缀 `/api/teachProduct`（`src/service/product-line.ts:19`），网关 `/api/teachProduct`、`/bgwApi/api/teachProduct` → gapm-appid `ces-teach-product-service`（仓库 **ces-teach-product** `http://git.baijia.com/tiku-java/ces-teach-product`，对照 `origin/master 77c65a4`） |
| 路径映射 | 去掉 `/api/teachProduct` 以后剩下的部分 = 后端 Controller 的类注解 + 方法注解，后端没有 context-path。例：`/api/teachProduct/product/line/search/list` → `ProductLineController`（`@RequestMapping("/product/line")`）`@RequestMapping("/search/list")` |

后端路径缩写：`PLC` = `ces-teach-product-service/src/main/java/com/gaotu/ces/teach/product/facade/api/controller/ProductLineController.java`，`PLS` = `.../app/service/productLine/impl/ProductLineServiceImpl.java`。

## tab 列表

页面没有 tab，结构是单页列表加上「新建 / 查看 / 编辑」共用的抽屉 `components/product-line-drawer`（`mode = create | view | edit`，`hooks/useProductLineModal.ts`）。查看和编辑直接用列表行的 record 回填，**不会再调详情接口**。行上「产品单元数 >」只做跳转：`navigate('/spu?productLineNumber=…')`（`index.tsx:29`），见 [../spu/_page.md](../spu/_page.md)。

## 页面级接口

`PL/` = `src/pages/product-line/`。

| 触发 | 前端调用路径 | 前端方法 | 前端代码位置 | 后端服务 | 接口名 [id] | 读/写 |
|---|---|---|---|---|---|---|
| 进页面（搜索栏/表格/抽屉都调，scene=search/edit 两份缓存） | `POST /api/teachProduct/product/line/condition/filter` | `getProductLineFilterConditions` | `PL/hooks/useFilterOptions.ts:10`（`src/service/product-line.ts:151`），调用方 `components/search-form/index.tsx:25`、`product-line-table/index.tsx:39`、`product-line-drawer/index.tsx:35` | ces-teach-product-service `PLC:87` | 产品线筛选条件 [3575333] | 读 |
| 进页面 | `GET /api/teachProduct/dictionary/all` | `getAllDictionaries` | `src/hooks/useCommonData.ts:70`（`src/service/common.ts:43`） | ces-teach-product-service `DictionaryDataController:59` | 所有字典数据 [1497744]（共享字典） | 读 |
| 进页面 | `GET /api/teachProduct/dictionary/department` | `getDepartments` | `src/hooks/useCommonData.ts:78`（`src/service/common.ts:49`） | ces-teach-product-service `DictionaryDataController:91` | 可用学部/部门 [1497779]（共享字典） | 读 |
| 进页面 / 查询 / 重置 / 翻页 / 新建或编辑成功后刷新 | `POST /api/teachProduct/product/line/search/list` | `queryProductLines` | `PL/hooks/useProductLinePage.ts:17`（`src/service/product-line.ts:75`） | ces-teach-product-service `PLC:43` | 查询产品线列表 [3575391] | 读 |
| 「新建产品线」→ 抽屉确定 | `POST /api/teachProduct/product/line/add` | `createProductLine` | `PL/hooks/useProductLineOperations.ts:24`（`src/service/product-line.ts:129`） | ces-teach-product-service `PLC:65` | 新增产品线 [3575368] | 写 |
| 行「编辑」→ 抽屉确定 | `POST /api/teachProduct/product/line/edit` | `updateProductLine` | `PL/hooks/useProductLineOperations.ts:34`（`src/service/product-line.ts:139`） | ces-teach-product-service `PLC:76` | 编辑产品线 [3575335] | 写 |

`src/service/product-line.ts` 里另外定义了 `masterData/customerValue/cascade`、`masterData/productPackaging/cascade` 和 `product/line/detail`，本页都不调用。`product/line/detail` 在产品单元抽屉里调用，见 spu 页。

## 关键表（`ces` 库）

| 接口 | 读表 | 写表（操作） | 其它 |
|---|---|---|---|
| `product/line/condition/filter` | `ces.ces_attribute`、`ces.ces_attribute_enum_value`（`attributeService.queryAttributeDetail`） | 无 | 产品类型/管理标准/核心竞争力来自代码枚举（`PLS:101`）；可筛选属性 id 来自 Apollo `product.line.support.attribute.id.list`（test=`[3,4,5]`，`PLS:69`） |
| `product/line/search/list` | ES `product_line_index_v1`（Apollo `product.line.es.index`，`ProductLineEsDao:64` / `:208`）；`ces.ces_teach_product_draft` 按产品线 count，回填「产品单元数」（`PLS:714` → `TeachProductRepositoryImpl.countDraftByProductLineNumbers:54`） | 无 | 列表**走 ES，不查 MySQL 主表** |
| `product/line/add` | — | `ces.ces_product_line` INSERT（`PLS:529` → `productLineRepository.saveProductLine`）；`ces.ces_product_line_attr` 先 DELETE 再批量 INSERT（`saveProductLineAttr`）；ES `product_line_index_v1` 同步 index（`productLineEventConsumer.consumeContext` 同步调用 `ProductLineEsDao.save`，`ProductLineEventConsumer.java:41`） | 产品线编号用 `GlobalService.nextNumber()` |
| `product/line/edit` | `ces.ces_product_line`（按 number 取） | `ces.ces_product_line` UPDATE（`PLS:614`，`:679`）；传了 attributeList 时 `ces.ces_product_line_attr` DELETE+INSERT；ES 同步 save/delete（`ProductLineEventConsumer.java:46-54`） | 在线大班课要校验业务类型/属性（`validateOnlineBigClass`） |
| `dictionary/all`、`dictionary/department` | 共享字典 | — | — |

## 排查提示

- 列表查不到刚建的产品线 / 字段不对：列表走 ES `product_line_index_v1`，先比对 MySQL `ces.ces_product_line` 和 ES 文档。ES 是在 add/edit 里**同步**写的，没有经过 MQ，写 ES 失败时只会留日志（`ProductLineEventConsumer`）
- 「产品单元数」统计的是 `ces_teach_product_draft` 草稿表（含未发布），所以和已发布数对不上属于正常现象
- 属性筛选项为空：查 Apollo `product.line.support.attribute.id.list`，再查对应 `ces_attribute` 的状态
- 抽屉里查看到的内容就是列表行数据（ES 文档），ES 滞后时这里看到的也是旧值

## 青舟接口详情页

- [POST /api/teachProduct/product/line/condition/filter](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3575333&appId=ces-teach-product-service&branchName=release) id=3575333
- [POST /api/teachProduct/product/line/search/list](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3575391&appId=ces-teach-product-service&branchName=release) id=3575391
- [POST /api/teachProduct/product/line/add](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3575368&appId=ces-teach-product-service&branchName=release) id=3575368
- [POST /api/teachProduct/product/line/edit](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=3575335&appId=ces-teach-product-service&branchName=release) id=3575335
- [GET /api/teachProduct/dictionary/all](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1497744&appId=ces-teach-product-service&branchName=release) id=1497744
- [GET /api/teachProduct/dictionary/department](https://qingzhou.baijia.com/#/cloud/apiDoc/search/detail?interfaceId=1497779&appId=ces-teach-product-service&branchName=release) id=1497779
