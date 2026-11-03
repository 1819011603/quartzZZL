# 端到端测试步骤（EM纯续关联；开关可开启后执行）

> **状态（2026-11-03）：已执行**。product/order Apollo 无发布权限 → 用 Arthas `vmtool` 在 pod 内临时置 `pureRelationEnabled=true`（product-c 两 pod + order pod），测后已全部置回 `false`；cart 开关与 product-b 白名单用 Apollo 临时后恢复。结果见 README「端到端验证」与本文末。

样本（test，`test-gtbg-dev-3`）：
- **主计划（大班,type=1）**：`585960797778243584`（dcg-扩科排除-大班计划-1020），course_numbers `[585960577856301056]`
- **从计划（小班,type=2）**：`586116340522184704`（dcg-小班扩科排除-计划），course_numbers `[18314034380997173]`
- 关联表：`gaotu.renew_master_relation`（cluster142 `gaotu_polar_test_03`）

## 1. 打开开关（Apollo，TEST）
- `product-b`、`product`、`cart.gaotu100.com`、`order.gaotu100.com` 的 `renewal.pure.relation.enabled=true` 并发布。
- 操作人：走「续班计划管理员」或临时把 `product-b` 的 `renewal.pure.relation.admin.accounts=[<账号id>]`（当前 `585960797778243584` 管理员=177071 gongxuemeng）。

## 2. 保存关联（B端，最终确认全量集合）
```bash
curl -sk -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" \
  'https://test-fuwu.baijia.com/bgwApi/product-b/b/renewMaster/relation/save' \
  -H 'content-type: application/json' -H 'traffic-env: test-gtbg-dev-3' \
  --data-raw '{"mainRenewMasterNumber":"585960797778243584","subRenewMasterNumbers":["586116340522184704"]}'
```
期望：`{code:0,msg:"success！"}`；DB `renew_master_relation` 新增行且 `create_account_id` = 操作人。

## 3. 下发字段（product-c 实例，cart 实际调用）
桥：`RenewalServiceImpl#listRenewalMasterByRenewalNumber(585960797778243584)`（`service_name=PRODUCT.GAOTU100.COM`）
期望：`related_renewMasterNumbers` 含 `586116340522184704`；开关关时该字段为空。

## 4. cart 并集（仅纯续；扩科不变）
- 前置：学员对**主计划前置课**与**从计划前置课**均有有效订单。
- 调 cart 续班推荐（C端 `renewalNumber=585960797778243584`）：
  期望返回结果含 **大班 + 小班 两个纯续班**（并集生效）。
- 开关关：仅主计划（大班）一项（回旧行为）。

## 5. order 跨模式放行
- 同一购物车含「主大班纯续 + 从计划小班纯续」→ **下单成功**（`SAME_CLAZZ(4)`/`SAME_COURSE(5)` 受控放行）。
- **真重复同商品**（同模式同班级/课程）→ **仍被拦**。
- 开关关 → 跨模式仍被拦（回旧行为）。

## 6. 回滚
将四处 `renewal.pure.relation.enabled=false` 发布 → 回到改动前行为。

## 边界（已在 product-b 实测）
- 非管理员 + 空白名单 → `仅续班计划管理员可操作`。
- 从计划 status∉{待开始,进行中} → `仅待开始/进行中的续班计划可关联`。
- 从计划数 >10 → `最多可纯续关联10个续班计划`。

## 执行结果（2026-11-03，Arthas 临时开关 / test-gtbg-dev-3）

- **Arthas 改值**：`options strict false` → `vmtool --action getInstances --className <bean> --express "instances[i].pureRelationEnabled = true"`；product-c pod 有 2 实例（CGLIB 代理 + target），**两实例都要设**；回读 true/false 确认。测后已置回 false 并 `--stop`。
- **product-c 下发**（桥 `listRenewalMasterByRenewalNumber` @ PRODUCT.GAOTU100.COM）：开 true → `related_renewMasterNumbers:[586116340522184704]`；关 → 无字段。
- **cart 收到**（桥 `ProductFeignServiceAdapterImpl#listRenewalMasterByRenewalNumber`）：`related_renew_master_numbers:[586116340522184704]`（productType=2）。
- **cart 并集**（桥 `RenewalService#getRenewalDetail` + pod `app/log/app.log`）：开 → `EM pure relation merged courseNumbers, renewalNumber=585960797778243584, size=2`；关 → 无新日志（计数不变）。
- **order 跨模式**（Arthas `vmtool` 调 `CartSameClazzOrCourseImpl#execute`）：大班2+小班6004 同课程 → 空(放行)；同模式2+2 同课程 → `SAME_COURSE`；大班2+小班6004 同班级号 → 空(放行)；开关关 → `SAME_COURSE`(回旧)。
- **未覆盖**：cart 推荐实际报价——test 库主/从前置课无订单，任何 userId 无候选。
