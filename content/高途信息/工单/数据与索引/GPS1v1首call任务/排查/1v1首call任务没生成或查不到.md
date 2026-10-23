# GPS1v1首call任务 · 任务没生成或查不到

> **只解决**：GPS 1v1 首call任务在任务列表里找不到 / 核对某学员时没有任务。
> 「这张表怎么同步到大数据」走 [`天工没有业务表怎么同步.md`](天工没有业务表怎么同步.md)，与本文无关。

## 数据在哪

- 落库表：`gaotu.first_call_task_1v1`（cluster `gaotu-crm-prod` / cluster_id 211，db `gaotu`）。
  - 维度：(`sub_teach_product_number` = 子产品号, `user_id`)；`task_generate_rule_type=1` = 二讲首call。
  - 存活判据：`isdel=0`；状态 `first_call_status`：1 未开始 / 2 进行中 / 3 已完成。
  - 退班 / 大班课误建清理后是 `isdel=1`（软删），所以查"有没有"要带 `isdel` 一起看。
- 任务列表 UI（EES 一对一任务 / fairy 任务平台）读 ES `task_platform_main_task`（1v1 文档有 `subTeachProductNumber`）——DB 有、ES 没有 = ES 没同步；DB/ES 都没有 = 真没生成。列表有时间范围筛选，老任务（几个月前）常因超出可选窗口"看不到"。

## 生成链路（决定"为什么不生成"）

容器事件 MQ topic `gaotu_gps_user_container_event`（tag：enter / edit / quit）→ fairy `GpsUserContainerOnsConsumer` → `FirstCall1v1SaveService`，**按顺序过滤**，任一步不过就不建：

1. **GPS 大班课过滤**（`filterOnlineBigClass`）：子产品是在线大班课（ces `isOnlineBigClass`）→ 剔除（大班课走大班课链路，本就不该建 1v1 首call）。
2. **老师解析**：`assistantNumber` → `accountId`（`fairyTeacherService`）；解析不到 → 跳过。
3. **规则配置**：`accountId` 命中 `task_rule_config` 里 `task_generate_rule_type=1`（二讲首call）的配置（按组织架构+角色标签匹配）→ 否则跳过。
4. **service-dock `validateFirstCall`**：判定该 (子产品, 学员) 是否"需要生成首call"→ `false` 则剔除。**这一步的口径在 service-dock，不在 fairy。**

## 排查

1. **先确认 DB 有没有**（带 isdel）：
   ```sql
   SELECT user_id, sub_teach_product_number, account_id, first_call_status, isdel, create_time
   FROM gaotu.first_call_task_1v1 WHERE user_id IN (...);
   ```
2. **DB 没有 → 查 fairy 日志定位卡在哪一步**（`serviceName=fairy-gaotu100-com` + grep / trace）：
   - 容器进/退事件在消费者被跳过：`GpsUserContainerOnsConsumer | convert | active ... invalid, skip, tag=...` —— 见「消费端字段」一节。
   - `filterOnlineBigClass | 剔除 GPS 大班课消息 N 条` —— 大班课剔除。
   - `accountId 未解析` / `未匹配到任务规则` —— 老师/规则配置问题。
   - `validateFirstCall 完成, 请求数: X, 不通过数: Y` —— service-dock 剔除（Y 条）。
3. **判 validateFirstCall 具体结果**（只读，走 fairy acl 桥调 adapter）：
   > 数字 ID 一律传字符串，否则 17 位雪花 id 超 JS 2^53 会被四舍五入（实测 `...895` → `...896`）。
   ```bash
   curl -sk -x "$AGENT_PROXY_URL" 'https://fuwu.baijia.com/bgwApi/fairy/test/acl/compare/service' \
     -H 'content-type: application/json' -H 'traffic-env: prod' \
     --data-raw '{"serviceNameAndMethodName":"com.gaotu.task.remote.HeadTeacherTaskAdapter#validateFirstCall","params":[[{"userId":"7360406222","subProductNumber":"17732867511419514","accountId":"203022","assistantNumber":"14517349478105152"}]]}'
   ```
   `result=false` → 拿 traceId 去 service-dock 日志看理由（见下）。

## 已知原因与判据

| 现象 | 根因 | 判据 |
|---|---|---|
| 容器**创建时就带老师**、之后没改派，任务却从不生成 | 消费端把 enter/quit 事件的老师读成 `newAssistantNumber`（上游这俩事件字段其实叫 `assistantNumber`，只有 edit 事件叫 `newAssistantNumber`）→ 进容器事件整条被 skip | 日志 `convert \| active ... invalid, skip, tag=tag_gps_user_container_enter`；**已修**（`GpsUserContainerOnsConsumer.convert` 按 tag 取，commit `0abade88bf` 分支 `hotfix-1v1-container-enter-assistant`）。存量漏建靠补数（见下）。 |
| 子产品是大班课 | 按设计不建 | `filterOnlineBigClass` 剔除日志；`getOnlineBigClassMap` |
| 老师无二讲首call规则配置 | 不建 | `未匹配到任务规则` |
| **service-dock 判"无需生成"** | 命中 service-dock 的「不生成首call白名单」`notGenFirstCallWhiteList`（按学员订单业绩归属的 `preEmployeeId` 判），**非缺陷，回溯也建不出来** | service-dock 日志 `GenFirstCallTaskAppService ... notGenFirstCallWhiteList ... employeeId: X, 是否contains: true, 是否生成任务: false`；employeeId→邮箱前缀见 `gaotu.employee`（cluster 71）。 |

## 存量补数（一次性）

- 机制：xjob **Java GLUE**（不新增代码），glue 里取 `TaskBizService` 调 `insertFirstCall1v1Task(FirstCall1v1ContainerMsgs)`，走真实过滤链路、幂等；`executorParam=dry` 只打印不落库。
- 候选口径：容器分配 ES `ads_user_container_allocation` 取 `containerStatus=1` 且非大班课、`allocationStatus>0` 的容器，对 `first_call_task_1v1`（isdel=0）做差集；老师工号从 `clazz_dist.user_assign_container.assistant_number` 取。
- ⚠️ 直接按 DB 差集裸插不安全：非大班课活跃容器 760k+，但真正该建的只有几十~百来条，必须靠链路过滤（大班课 / 规则配置 / validateFirstCall）。

## 验证

- 表停在 `first_call_task_1v1` 有 `isdel=0` 的目标行、`create_time` 是补数那一刻；ES `task_platform_main_task` 随后（task_change MQ）出现同 `subTeachProductNumber+userId` 文档。
- 「任务列表能查到」不等于业务对：列表有时间范围筛选，老任务本来就可能筛不到。
- validateFirstCall=false 的，**建不出来就是对的**，别当漏建。