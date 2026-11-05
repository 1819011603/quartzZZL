# round8只读核实（增量）

已确认企微新增页面代码位于cronus/feature-wecom-ban-optimization@17ee81ccb44b95655f1a55494c4d9372b604cc34，远端当前未变。student-center release当前5dce9cdb，与round7实际镜像一致；复用标签scene同步链本地git blame为2026-03-26，远端release UserClazzMarkBiz与本地396d84f逐字一致。远端不存在归档本地同名feature-xuban-pure-relation-20261102；这不证明缺失必需后端新版本。MR1528仍7f9bca38，仅参考不作为需求必发版本。

18:59:13一次当前定向只读续班查询（原受控班574882679202260992/老师177071，pageSize3）HTTP200/code0，trace f2104764-35eb-4741-b305-4cdb7aea65bf.0.3。原18:02 ES父熔断不能称持续未恢复，当前响应及实际路由待下节补核。未做标签/备注写入或重放成功验证。

全部相关TEST逻辑环境dev/test已读：31分组，14个Pod（13 UP、1 OUT_OF_SERVICE），Eureka同14实例，无test-gtbg-dev-3专属student-center。现有网关9路由正常，未改部署/路由/配置。详细原件qiwei-inventory-summary.json/qiwei-eureka-current.json/qiwei-routes-current.json。

## 配置已补齐，不能沿用Nov4缺口

本轮TEST只读查询es_query_config确认大班continuationService已有studentTags/type2/basic(id874)、studentTags/type6/necessary(id872)、studentTagNames/type6/extra(id873)，create_time均2026-11-04 18:53；小班microContinuationService及smallClazzRoster已有对应三类。student_field_config两场景4行仍在。旧只读报告“continuationService活跃配置0条”不再代表当前。原件qiwei-db-config-current.json含SQL/环境/时点；本轮无配置写入。当前3人接口返回两目标studentTags=[]，未选无该字段，studentTagNames三人均字段缺省，不冒称名称数组都为[]；按实际空集合展示语义和GAIA所取列续核。

## 关键解除：正确前端已在现有test-gtbg-dev-3（可立即续接，不需新增部署）

青舟cronus dev逻辑环境已有Running Pod10.218.250.210，namespace test-gtbg-dev-3，镜像feature-wecom-ban-optimization-17ee81cc-20261104184104；镜像commitId与远端真实需求分支17ee81ccb44b95655f1a55494c4d9372b604cc34一致。带traffic-env/ingress-traffic-env:test-gtbg-dev-3只读GET /micro-cronus/返回umi.7054cbb2，与当前浏览器iframe实际script完全一致；不带泳道头则返回默认release的umi.c56015ca。证据qiwei-cronus-pods-dev.json、qiwei-cronus-images.json、qiwei-cronus-dev3-html.txt及meta、qiwei-browser-cronus-assets.txt。不能拿默认release页面元数据Commit ID undefined当成需求前端未部署。

可交父Worker继续：既有Gong177071、原受控大班3人组，正确cronus dev3页面→原student-center TEST存量接口，配置basic/necessary/extra已在且当前续班只读列表成功。可补大班页面字段展示、筛选/取消及后续授权写验；当前仅只读版本诊断，不在此轮重放标签/备注或继续写场景。小班页面也应在同一正确cronus版本，样本/权限仍须其执行阶段实际核实，不能因尚未准备称缺版本或权限。本轮无路由/部署/页面状态写入。
