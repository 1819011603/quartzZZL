# 续班看板指标 · BI iframe 看板打开白屏（如 bi_renewal_clazz 续班过程数据）

> **只解决**：fuwu 上 iris 承载的 BI iframe 类看板（路由 `/crm/iris/iframe/<identification>`，数据在 udata.baijia.com 泰坦 BI）打开后**整块白屏/空白**。典型：续班过程数据 `bi_renewal_clazz`。权限被拒但表现为跳 403、或 BI 平台自身报错，不在此列。

## 一句话结论

**白屏 = iris IFrame 组件没拿到菜单下发的 iframe url，`if (!url) return null` 渲染空白**；url 来自 GAIA 动态菜单 `/gaiaCenter/pageMenu/get`，该接口按登录人**主岗部门**过滤菜单项（`gaia.page_menu.departments`）。人不在菜单配置的部门范围 → 菜单不下发 → 白屏。**与 BI 平台权限、与快照表有没有该老师数据都无关。**

## 链路（白屏是怎么发生的）

1. epic 壳调 `POST /gaiaCenter/pageMenu/get`（gaia-center `PageMenuController#get` → `PageMenuServiceImpl#getPersonalDirectory`）；
2. 过滤规则 `listPoweredPageMenus`：取登录人 **staff 主岗组织路径**（`getMainPostStaff`，按 `_` 拆成节点集合），对每个 enabled 菜单做 `PageMenu#matchDepartment`——`gaia.page_menu.departments`（JSON 数组）**为空=全员可见，非空=命中任一节点才可见**；
3. 前端（epic `Layout/index.js#getMenuMapInfo`）只收 `!pageInfo.tag || hasTag(tag)` 的项放进 `dynamicMenuRoot`；**tag 不过的表现是跳 403，不是白屏**；
4. iris `src/pages/IFrame/index.js`：`dynamicMenuRoot['/<identification>']` 取不到 → `url` undefined → `return null` → **白屏**；iframe 里的 BI（泰坦/PowerShield `getDataAuth` 按 userName+DASHBOARD owners+DATA_SET 授权）此时**根本收不到请求**。

## 排查步骤

1. **确认白屏层级**：BI 服务（`bdg-uanalysis-intelligence`）日志里搜登录人邮箱前缀（`serviceName=bdg-uanalysis-intelligence` + `grep=<前缀>`）。零记录 = 请求没到 BI → 菜单层问题（本文）；有请求且报权限 → 查泰坦/PowerShield 对该用户的 DASHBOARD/DATA_SET 授权。
2. **代客对比菜单**（最直接）：`cosplay_login` 成提报人，代理调 `POST https://fuwu.baijia.com/bgwApi/gaiaCenter/pageMenu/get`（header `b_client: EES`、`traffic-env: prod`），看返回里有没有目标 `identification`（如 `bi_renewal_clazz`）；再 cosplay 一个能看到的人对比。**接口没返回该项 = 部门过滤未命中，实锤。**
3. **看菜单配置**：`gaia.page_menu` 里该 `identification` 行的 `departments`（gaia 库需单独权限；拿不到就走菜单对比间接实锤）。配置维护入口 = GAIA 页面菜单后台（改配置走审批流）。

## 修复

把对应菜单项的部门范围加上提报人所在部门（GAIA 页面菜单后台操作，走审批），或如果该项本应全员可见则清空 `departments`。改完后让用户刷新页面重新拉菜单验证 `pageMenu/get` 已下发。**菜单通了之后若 BI 仍白屏，再按步骤 1 后半查泰坦报表授权。**

## 相关

- 看板数据源与导出：[`续班过程看板数据从哪取.md`](续班过程看板数据从哪取.md)
- 组织维度行空（父部门不汇总）：[`父级部门看不到数据.md`](父级部门看不到数据.md)
