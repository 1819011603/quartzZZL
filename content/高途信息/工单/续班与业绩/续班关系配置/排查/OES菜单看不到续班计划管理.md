# 续班关系配置 · OES 生产看不到「续班管理 / 续班计划管理」菜单

> **只解决**：登录 OES（`mi.gaotu100.com/ark/...`）后左侧菜单里整组「续班管理」或其子项「续班计划管理」「预报名活动」不出现。菜单在、点进去报 403 或页面空白的，不在此列（那是页面级权限或数据空）。

## 一句话结论

OES 左侧菜单是按**账号角色挂的权限点（tag）**下发的；看不到 = 该账号所有角色的权限 tag 里**没有 `oes_menu_continueplan`**（预报名活动另需 `oes_menu_presale`）。与浏览器缓存、环境部署无关。

## 判定链路

1. 前端启动时调 `POST /account/employee/getAuth.do`，返回 `data.accountDto.hasRoles[].hasPermissions[].tag`；
2. 每个菜单项对应一个 tag（如系统设置 = `gaotu_boss_p_system_conf_`、任务中心 = `gaotu_boss_p_task_`）；
3. 菜单只渲染当前角色拥有的 tag。「续班管理 → 续班计划管理」= `oes_menu_continueplan`，「预报名活动」= `oes_menu_presale`。

## 排查步骤

1. **在已登录的 OES 页面里直接读权限**（不用翻库、不用代课）：
   ```js
   fetch('/account/employee/getAuth.do', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}', credentials:'include'})
     .then(r=>r.json()).then(j=>{
       const a=j.data.accountDto, cur=a.currentRole;
       const all=new Set(); a.hasRoles.forEach(x=>(x.hasPermissions||[]).forEach(p=>all.add(p.tag)));
       return {account:a.name, currentRole:cur.name, currentRoleTag:cur.tag,
               hasContinueplan: all.has('oes_menu_continueplan'),
               hasPresale: all.has('oes_menu_presale'),
               oesMenus:[...all].filter(t=>/^oes_menu_/.test(t)).length};
     })
   ```
2. **和一个能看到的账号对比**：同一个接口跑一遍，看 `hasRoles` 里是否有 `oes_menu_continueplan`。有/无 即实锤。
3. **顺便看自己能不能自助加**：这个接口里有没有 `gaotu_boss_p_system_conf_`（OES「其他设置 → 权限管理」入口）。没有就必须找人加。

## 修复 / 申请

- 入口：OES 右上角「其他设置 → 权限管理」（`#/permission`，需要 `gaotu_boss_p_system_conf_`）。
- 让有权限的 OES 权限管理员把 `oes_menu_continueplan`（按需再加 `oes_menu_presale`）挂到申请人当前角色上；改完刷新页面重新拉菜单即可。
- **换角色无效**的判据：把该账号**全部角色**的 tag 并集跑一遍仍然没有该 tag——那就不是"切错角色"，只能加权限。
- 加完验证：左侧出现「续班管理 → 续班计划管理」，或第 1 步脚本 `hasContinueplan` 变成 true。

## 相关

- 页面路由与接口：知识库 [`promotions/continuation-classes/_page.md`](../../../../知识库/promotions/continuation-classes/_page.md)
- GAIA 菜单按部门过滤（另一套机制，别混）：[`../../续班看板指标/排查/BI看板iframe白屏.md`](../../续班看板指标/排查/BI看板iframe白屏.md)
