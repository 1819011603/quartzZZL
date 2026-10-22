# 企微侧边栏 · AI途途学员信息名字后多了个换绑

> **只解决**：企微侧边栏 AI途途「学员信息」卡片里，学员名字后面多出一个「换绑」入口，
> 咨询是不是 bug、是不是新功能、会不会影响判单之类的业务。
> 字段回显/保存不对走 [`字段保存了不显示.md`](字段保存了不显示.md)，身份字段走 [`身份字段改了不展示.md`](身份字段改了不展示.md)。

## 判定入口

「换绑」是 `doris` 前端**硬编码**在学员信息卡片表头的入口，**不是后端字段、不是数据、不是配置/灰度**，
对所有学员、所有账号都渲染，与学员本身数据无关。看到它排在名字后面，先按「前端入口」判，不要往 crm-service 字段/数据上查。

## 排查

1. 定位前端：AI途途侧边栏前端是 `doris`（青舟 `baijia.gaotu.Business.fe.doris`，git `http://git.baijia.com/gaotu-fe/doris`），
   线上 `https://sales-crm.gaotu100.com/doris/`，页面路由 `/doris/Scrm/Student/AIHelper`。
2. 线上产物里直接搜文案：路由 chunk 为 `p__StudentInfo__Detail.<hash>.async.js`（umd chunk 名映射在 `umi.<hash>.js` 的 `n.u` 函数里）。
   代码为：
   ```js
   <span className={style['change-account']} onClick={handleAccountClick}>换绑</span>
   // handleAccountClick = () => historyPush('/Scrm/Student/Manage/ShiftAccount')
   ```
   源文件 `src/pages/StudentInfo/Detail/Content/index.jsx`。
3. 判断是不是新加的（`master` 上不一定有，要查 `release`/feature 分支）：
   ```bash
   git -C /tmp/doris-fe log --all -S"换绑" -- src
   ```
   命中的 commit message 即本次改动（如 `AI途途个人信息页增加修改绑定手机号快捷入口`）。
4. 确认线上就是那份产物：线上 chunk 里 `grep 换绑` 命中，且 prod 构建的 sentry release commit 是该 feature 合入 `release` 后的 merge commit。

## 验证

- 该入口只做前端跳转（到 `/Scrm/Student/Manage/ShiftAccount`），**不写数据、不参与判单**，所以业务上无影响，属「新增功能入口」。
- 若判断为缺陷/需要改位置或去掉，改的是 `doris` 前端 `src/pages/StudentInfo/Detail/Content/index.jsx`，与 crm-service / student-data 无关。
- 常见误判：拿 `master` 说「没有变更」→ 该改动只在 `release`/feature 分支，prod 由 `release` 构建。
