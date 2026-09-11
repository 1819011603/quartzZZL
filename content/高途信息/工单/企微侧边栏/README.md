# 企微侧边栏工单记录

同一类反馈（企微侧边栏字段展示/联动/保存问题）都往这一份文件里加，按时间倒序，不再拆子目录。
下面「核心方法与工具」摘自 `crm-service` 仓库的 `wk-student-info-replay` skill，直接抄了一份过来，
方便不打开代码库也能照着排查；skill 那边如果更新了，这份可能会滞后。

## 核心方法与工具

### 怎么不登录、直接调后端接口验证（acl/compare 桥）

`getDynamicWkStudentInfo`/`updateDynamicWkStudentInfo` 正常都要浏览器 Cookie。排查时不用登录，
经 `<host>/bgwApi/crmApp/test/acl/compare/services` 桥直接反射调 Bean/Feign 方法即可。

**host 决定环境，不是 path 里的 `/test/` 段，也不是 `traffic-env` 头**：

| 要调的环境 | host |
|---|---|
| 测试（test-eco-N 泳道） | `https://test-fuwu.baijia.com` |
| 线上 | `https://fuwu.baijia.com` |

请求经本地代理 `http://127.0.0.1:8888` 注入 Cookie：

```python
import os, json, requests
PROXY = os.environ.get("AGENT_PROXY_URL", "http://127.0.0.1:8888")
TEST_HOST = "https://test-fuwu.baijia.com"
PROD_HOST = "https://fuwu.baijia.com"

def acl_compare(service_method: str, params: list, traffic_env: str = "test-eco-6", host: str = TEST_HOST):
    resp = requests.post(
        f"{host}/bgwApi/crmApp/test/acl/compare/services",
        headers={"traffic-env": traffic_env, "teacherNumber": "0", "accountId": "0",
                 "employeeId": "0", "identification": "microLessonStudent",
                 "Content-Type": "application/json"},
        json={"requests": [{"serviceNameAndMethodName": service_method, "params": params}]},
        proxies={"http": PROXY, "https": PROXY}, verify=False, timeout=20,
    )
    resp.raise_for_status()
    return list(resp.json()["data"][0].values())[0]
```

常用调用：

- 域账号查 accountId：`CasApiService#batchGetAccountByDomains`，params `[["liuying24"]]`
- 读接口（要模拟真实老师视角走 Service 层，不要走 Controller——Controller 里
  `ThreadLocalHolder.getAccount()` 拿到的是空账号/GUEST）：
  `StudentMdmService#getDynamicWkStudentInfo`，
  params `[userId, accountId, accountRole, periodNumber, wechatId, corpId, qwHookId]`，
  返回 `{"displayData": [...]}`，某个字段号**没有 `value` 这个 key** = 后端从没存过值。
- 写接口：`StudentMdmController#updateDynamicWkStudentInfo`，params 是一个对象，
  `fieldDOList` 本身要 `json.dumps` 成字符串：
  `{"userId":..., "periodNumber":..., "fieldDOList": json.dumps([{"number":"10019","value":"学员"}], ensure_ascii=False), "wechatId":..., "corpId":..., "qwHookId":...}`

### 身份字段(10019) 改了不展示的根因：qwHookId 读写不对称（已修）

写路径 `qwHookId` 为空会兜底成 `hookWechatId`；读路径以前没有兜底，导致
"写得进去（key=hookWechatId）、读不出来（qiWeiId=null）"，表现成"改了没反应"。
已在 2026-08-27（分支 `feature-wk-identity-qiweiid-fallback`）给读路径
`ServeFieldClientAclService#getFieldQueryDimensionInfo` 补了同样的兜底：
`fieldQueryDimensionInfo.setQiWeiId(Strings.isBlank(qwHookId) ? hookWechatId : qwHookId)`。
亲密称呼（60008）不受这个影响，因为它走的是 `userWechatId` 维度，不是 `qiWeiId`。

### 通用排查步骤（按顺序走）

1. **域账号 → accountId**：`CasApiService#batchGetAccountByDomains`。
2. **accountId → 该老师的活跃 traceId**：线上 SLS（`qingzhou-log` MCP，`serviceName` 用
   `crm-app-service-gaotu100-com`）搜
   `queryStr: __tag__:app: "crm-app-service-gaotu100-com" and messages: "authFilter" and messages: "<accountId>"`，
   命中 `AuthFilter:99`(`casAccount:{...}`) / `AuthFilter:166`(`新逻辑当前角色：...`) 两类日志，
   能看到该老师最近操作的时间点和 `TID`（traceId）。
3. **拿到具体学员 userId 后 → 精确捞写/读请求参数**：
   - 写请求（改字段）日志文本固定是 `动态更新企业微信-学生信息请求参数`（`StudentMdmController:191`）；
   - 读请求（打开页面）日志文本固定是 `动态获取企业微信-学生信息请求参数`（`StudentMdmController:178`）；
   - `queryStr` 里 `messages:` 同时带上这句固定文本 + userId，能拿到完整的
     `fieldDOList`（改了哪个字段号、改成了什么值）和这次请求的 `TID`。
   - **别只传 `keyword`**，直接把完整查询语句整段塞进 `queryStr`，`env` 传 `prod`、`logType` 传 `app`。
4. **拿字段号对比 displayData**：调 `StudentMdmService#getDynamicWkStudentInfo`（Service 层，
   带 accountId/accountRole 才是真实视角），看目标字段号在 `displayData` 里有没有 `value` key。
5. **多个字段是否联动**：只看写请求的 `fieldDOList` 里是不是同一条请求里出现了多个字段号，
   别凭前端展示的先后顺序猜。
6. 拿到 `TID` 后可以直接丢给 `qingzhou-trace` 的 `trace_tree` 看这次请求端到端有没有 error span。

## 2026-09-11 改姓名，亲密称呼跟着自动变

### 反馈信息

- 反馈人 / 反馈渠道：飞书转发，王永诗 → 马胜 → 张泽灵；刘颖 录屏演示
- 涉及对象：老师 `liuying24`（accountId 86764），复现学员 userId `7309871552`

### 结论

不是 bug。企微侧边栏前端有一段 3 年前写的展示兜底逻辑：**亲密称呼字段没有值时，直接拿姓名回显**。
crm-service 后端两个字段（10001 姓名 / 60008 亲密称呼）完全独立存储、独立写入，代码里没有任何联动。
真正证据：改姓名的两次写请求（`fieldDOList` 只含 10001）之后，直接调后端 Service 重放读接口，
60008 那条**没有 `value` 这个 key**——后端压根没存过值，页面上看到的"亲密称呼变了"只是前端拿姓名垫的。

### 决策

金瑞琳贴出前端代码确认是既有逻辑（`// 如果亲密称呼没有值的话就使用姓名`）后，
**王永诗拍板不用改**，让刘颖手动填一次亲密称呼，之后再改姓名亲密称呼就不会再被姓名兜底覆盖。

### 排查过程摘要

1. 先怀疑是 crm-service 后端字段联动 —— 读 `StudentMdmService#updateDynamicWkStudentInfo`/
   `getUpdateDimensionInfos` 代码，确认只是把前端传来的 `fieldDOList` 逐项透传给 task-center，
   没有 10001→60008 的联动代码；`DynamicWkStudentInfoResponse.defaultValue` 字段全仓库未被赋值。
2. 用域账号 `liuying24` 反射调 `CasApiService#batchGetAccountByDomains` 拿到 accountId=86764。
3. 线上 SLS 搜 `authFilter`/`casAccount` 日志按 accountId=86764 过滤，确认她的活跃 traceId；
   再按学员 userId=7309871552 搜 `动态更新/动态获取企业微信-学生信息请求参数`，捞出全部写请求：
   - `7d5fd3da-a860-4ce3-9023-aa42afe7a947.0.1` 17:57:02 写 10001="路"
   - `e8591f0f-9c5a-414e-acd0-13d9f2462578.0.1` 17:58:15 写 10001="梓路"
   - `a1328a0f-4dfb-4be0-90e5-a539fe616a9b.0.1` 18:45:19 写 60008="路"（独立请求，跟改姓名隔了近 50 分钟）
4. 全程只有这 3 条写请求，**没有任何一次写请求同时/紧跟着写 60008 和 10001**，证明后端不联动。
   重放 `StudentMdmService#getDynamicWkStudentInfo` 直接对比 displayData：60008 写入前没有 `value` key，
   写入后才出现，且值与姓名不同——两个字段各自独立存储实锤。
5. 金瑞琳截图给出前端源码 `if (nameIndex !== -1 && !value[nameIndex].value) { value[nameIndex].value = realName?.value; }`，
   直接印证"亲密称呼没值就拿姓名垫"是前端故意写的展示兜底，3 年前的逻辑。

### 涉及代码 / 服务

- `crm-service` `server/src/main/java/com/gaotu/crm/server/app/controller/mcrm/StudentMdmController.java`
  `getDynamicWkStudentInfo` / `updateDynamicWkStudentInfo`
- `crm-service` `server/src/main/java/com/gaotu/crm/server/app/service/mcrm/StudentMdmService.java`
  `getUpdateDimensionInfos`（确认无联动）
- 企微侧边栏前端（不在 crm-service 仓库）：姓名兜底展示那段 `nameIndex` 逻辑，具体仓库待补
