# 续班服务可见性 · 二讲看不到续班服务tab

> **只解决**：某老师在 EES「班级花名册」看不到「续班服务」（或「退费管控」）tab，而别人/代课能看到。
> tab 能打开但显示「非续班期」走 [`../../续班服务窗口期/排查/续班服务显示非续班期.md`](../../续班服务窗口期/排查/续班服务显示非续班期.md)。

## 判定入口

tab 显隐由进页面接口 `POST /component/student-center/roster/gray`（`RosterController#gray`）返回的 `RosterGrayVO.continuationService` 决定，取值来自 student-center `RenewalService#gray()`。

`gray()` = **账号白名单命中** 或 **（灰度开关开 && 主岗部门命中部门白名单）**：

- 账号白名单：Apollo `renewalService.gray.org.current.account.list`（accountId 列表）
- 部门白名单：Apollo `renewalService.gray.org.list`（虚拟组织部门 id 列表，按 `getAccountInOrg(accountId, 列表, renewalService.gray.org.types)` 判）
- 开关：`renewalService.gray`（默认 true）、`renewalService.gray.org.types`（默认 `[1]`）

以上 key 均在 **student-center** 的 `application` namespace（PROD）。

## 排查

1. 拿该老师 `accountId`：`SELECT account_id, email_prefix FROM gaotu.employee WHERE email_prefix='<拼音>'`（cluster `gaotu-center-prod`，库 `gaotu`）。
2. 读 Apollo（app `student-center`，env PROD）`renewalService.gray.org.list` / `renewalService.gray.org.current.account.list`，看 accountId 是否在账号名单。
3. 取该老师主岗部门：ACL 桥 `OrganizationAclServiceImpl#listMainPostStaffByAccountIds([accountId], "EES")` → `mainPostOrgPathFromRoot` / `orgNameFromRoot`。
4. 复现 `innerGray` 判命中：ACL 桥 `OrganizationAclServiceImpl#getAccountInOrg(accountId, <renewalService.gray.org.list 全部 id>, <renewalService.gray.org.types>)`，返回全 false = 未命中。
   - 上面 3/4 走 `baijia-invoke` 的 `invoke_service`（project `student-center`，`traffic_env=prod`）；大数字 id 传字符串。
   - 部门 id 对应名称可用 `OrganizationAclServiceImpl#listByOrgNumbers([...])` 的 `orgNamePath` 反查。

## 开通

如需给该部门/账号开放：把部门 id 追加到 Apollo `renewalService.gray.org.list`（或把 accountId 加到 `renewalService.gray.org.current.account.list`），**发布后**生效（Apollo 写只落草稿）。

## 验证

- `getAccountInOrg` 该部门命中 true（或 accountId 在白名单）；页面 `POST /roster/gray` 返回 `continuationService:true`；该老师**重新登录** EES 花名册可见「续班服务」tab。
- 不算通过：只改了 Apollo 草稿未发布；只代课看到 —— 代课是按登录身份/操作人判定，未必等于该老师本人命中。
