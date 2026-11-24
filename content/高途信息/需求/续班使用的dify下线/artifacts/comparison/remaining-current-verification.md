# 当前非知识库验证检查点（2026-11-24）

代码 HEAD：263ba48ad2e476e7092093d36414280dddef2ed6d；worktree 干净。环境 test-gtbg-dev-1。

|项目|本轮事实|证据|
|---|---|---|
|素养NPS当前调用|成功，完整 answer 与 usage，total_tokens=4451，event=litellm_proxy/deepseek-v4.1-flash；trace 48a884ad-d5ec-4ac1-85dc-26aa542fdf37.0.3|remaining-current-probe/invoke-response.json|
|画像当前调用|成功，total_tokens=2663，event=litellm_proxy/doubao-seed-2.0-lite；trace dbbbfdb2-afbe-4ef9-b94f-640c0835f330.0.3|remaining-current-profile/invoke-response.json|
|当前TEST覆盖配置|除素养NPS外，八历史场景的对应七agent均没有stream=true、omitMaxTokens=true；画像/摘要共享agent和分层agent仍显式thinking.disabled|remaining-current-probe/apollo-readback.txt|
|模型|画像实际用映射后新名；此次成功不能证明旧别名授权成功。未修改model或callerRoute|同上|
|身份|两次请求RunUser=email:gongxuemeng@gaotu.cn；仅证明发起参数，不等于本轮下游费用头实收|两份invoke-response.request|

## 未完成

- 前八历史场景本版本逐项完整参数、messages、费用头实收未完成。当前配置明确尚未按strict-v2设置，不能以业务成功代替严格对等。
- 素养分层、根因、旅程、体验独立样本未实施。
- 本轮未做Apollo写入、数据库配置修正、生产调用、路由修改、部署或飞书修改。
- 画像第一次复用entry_key导致唯一索引冲突，随后已使用独立profile键成功；该失败发生于任务入库，不是模型权限失败。

## 续接入口

/tmp/remaining_current_probe.py、/tmp/remaining_current_profile.py，均由已有nps_replay3.py复制，分别写独立证据目录。已完成，无在途操作。
复用V2入口仅是当前请求健康检查，尚未证明普通动态生成入口；不得把本检查点计为新增完整场景通过。
下一步先在模型不改的边界内纠正TEST其他agent的stream/omitMaxTokens/thinking配置并发布回读，再逐场景普通入口及SOP V2实收；旧别名权限历史证据只能作历史，不以本轮新名成功替代。

## 本次推进：八历史场景参数修正并复验

TEST releaseKey `20261124191358-188a6f5d9e0ed660`，已发布值与目标完全相等，model/callerRoute未改。八例普通动态生成入口（SOP保留V2）全部成功，LiteLLM messages与旧基准逐字相等、stream=true、max_tokens/thinking均省略；Arthas jsonPost共8次费用头均gongxuemeng。请求传业务RunUser，未写兜底。

|场景|当前trace|messages / 参数|
|---|---|---|
|分层修正后|`63916e95-985f-4407-9f8e-00ae2ae61438.0.3`|相等 / 通过|
|摘要|`9d831ba2-fc93-46d7-82ee-f1797aea5696.0.3`|相等 / 通过|
|退费根因|`aa02540f-30a8-40cd-816d-138168507e69.0.3`|相等 / 通过|
|画像|`708865b6-5d42-41bf-b5c1-54635a17c682.0.3`|相等 / 通过|
|NPS|`db72f1f1-90c6-458a-a8f0-047bfdf501c1.0.3`|相等 / 通过|
|旅程|`29931ca8-4a04-4b89-827e-e1accb0afa33.0.3`|相等 / 通过|
|课程体验|`3a622047-d7a6-469d-89f5-778770a36f1f.0.3`|相等 / 通过|
|SOP V2|`c2b1755e-1ceb-4859-8488-423c73f52b03.0.3`|相等 / 通过|

证据：remaining-current-runs/summary.json；各场景after/*/invoke.json、received.json、sls.txt；after-watch.txt记录费用头/body（终端个别汉字乱码，messages逐字断言以SLS JSON为准）；release.txt、after-apollo.txt为发布回读。

四素养独立实例仍未验证。当前TEST查询只有素养NPS迁移副本及两个建议类应用，不含四目标应用；需继续建立独立TEST配置及样本，不将精品证据冒充素养。

Apollo：https://apollo-portal.baijia.com/config.html#/appid=student-data&env=TEST&cluster=default

## 四素养独立TEST样本最终结果

首次调用发现未配置应用格式，已仅新增四应用格式映射并发布回读；releaseKey `20261124192510-188a49b33afd48a0`。独立配置来自生产只读core/后处理/依赖数据快照及各自Dify系统模板，复用现有TEST agent，未改model/callerRoute。最终四例全部返回answer和usage，发起侧费用头4次均gongxuemeng。

|场景|最终trace|实收检查|
|---|---|---|
|素养分层|`9a5b2c21-e465-45fb-b0c4-e24f46a18140.0.3`|自己的core、外层system/角色正确；stream=true；max_tokens/thinking省略|
|素养根因|`d246f038-63fb-42ce-894b-883f76c810e3.0.3`|自己的core、外层system/角色正确；stream=true；max_tokens/thinking省略|
|素养旅程|`50868c24-9bbd-4252-bcc6-2bb2114d4ac6.0.3`|自己的core、外层system/角色正确；stream=true；max_tokens/thinking省略|
|素养体验|`c078cba2-8609-4dbd-b993-5991397d6354.0.3`|自己的core、外层system/角色正确；stream=true；max_tokens/thinking省略|

证据：remaining-current-runs/suyang-summary.json、suyang/*/received.json及invoke.json；suyang-db-readback.json、suyang-created.json、suyang-format-readback.txt、suyang-release.txt。首次错误格式保留suyang-before-format。

### 证据边界（覆盖此前简写）

- 八历史场景与旧实际messages逐字相等，参数与费用头补证已完成。watch表达式、字段名、逐条body唯一对应trace见watch-trace-association.json；3例body全等，5例终端乱码相似度>=99.81%，不是直接MDC trace实收，不能将模糊关联称为字节一致。
- 四素养是独立应用/配置和独立请求，但复用固定业务输入（包含高中标签），不是四个真实素养学员回放。没有独立旧Dify实收基线，故不能宣称四例旧新messages逐字对等；当前验证仅为配置来源/动态生成格式/参数/成功响应。
- RunUser为人工注入gongxuemeng@gaotu.cn，沿用strict-v2-cost-identity.md既有老师身份来源核验；本轮证明传递，未验证真实业务自动取老师入口，不对模拟文本中王/陈老师身份做推定。
- 当前Pod student-data-5f688c5bfb-xgx76在test-gtbg-dev-1 Running/UP、10.218.249.191，见current-pods.txt与watch。1361737部署成功证据复用deployment-1361737.log；未单独取得Pod镜像SHA到263ba48a的强绑定，不冒称已验证。
- 未调用生产生成、未改生产配置，四知识库仍Dify。无新增代码、无部署、无飞书修改。

剩余强证据缺口：四素养对应旧Dify独立实际messages（当前没有），自动业务老师来源链与当前Pod镜像SHA强绑定。禁止用再次成功生成代替这些证据。
