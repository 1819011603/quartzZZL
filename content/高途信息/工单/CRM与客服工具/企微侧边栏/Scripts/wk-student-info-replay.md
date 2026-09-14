> 本文件原为 `crm-service/.claude/skills/wk-student-info-replay/SKILL.md`，2026-09-14 迁入案例库。
> 主流程见同级 [`README.md`](README.md)。

# 企微侧边栏「动态学生信息」两个接口的回放/调用

对应代码：[StudentMdmController.java](../../../server/src/main/java/com/gaotu/crm/server/app/controller/mcrm/StudentMdmController.java) 的
`getDynamicWkStudentInfo` / `updateDynamicWkStudentInfo`。

两个接口都走 `ThreadLocalHolder.getAccount()` 取当前登录人，正常必须带浏览器 Cookie。**排查问题时不用登录**，
经 `<host>/bgwApi/crmApp/test/acl/compare/services` 桥（[AclServiceCompareController.java](../../../server/src/main/java/com/gaotu/crm/server/app/controller/AclServiceCompareController.java)，host 见下节）
直接反射调 Bean/Feign 方法即可拿到/触发真实数据。请求经 baijia-proxy 走
`${AGENT_PROXY_URL:-http://127.0.0.1:8888}` 注入 Cookie。

## 🚨 先确定 host：host 决定环境，不是 path 里的 `/test/` 段，也不是 `traffic-env` 头

| 要调的环境 | host |
|---|---|
| **测试**（test-eco-N 泳道） | `https://test-fuwu.baijia.com` |
| **线上** | `https://fuwu.baijia.com` |

路径里的 `/bgwApi/crmApp/test/acl/compare/services` 两个环境**都是这个**，中间那个 `test` 段
是 acl 桥自己的路由段，**跟环境无关**，别拿它判断打到了哪。

**踩过的坑（2026-08-27，浪费了大半轮排查）**：拿 `fuwu.baijia.com` 配 `traffic-env: test-eco-2`
去"验证测试环境部署"，实际全打在**线上**——线上没有那个改动，于是得出"兜底没生效"的错误结论；
又因为 `traffic-env` 在线上 host 上不起作用，`test-eco-2` 和 `test-eco-6` 返回完全一样，
更坐实了误判；最后甚至跑去 arthas 反编译字节码查"代码到底部没部署上"。
**换个 host 就完事的事，别升级成查字节码。** 结论反常时，第一件事是核 host 和泳道，不是怀疑镜像。

自检：调完拿响应头 `gapm-traceid`，去对应环境的轻舟查（test → `test-qingzhou`，prod → `qingzhou`）。
在 test 轻舟查不到 span，多半是你打到线上去了。

**统一用下面这个 Python 小工具发请求，别每次现拼 curl：**

```python
import os, json, requests

PROXY = os.environ.get("AGENT_PROXY_URL", "http://127.0.0.1:8888")

TEST_HOST = "https://test-fuwu.baijia.com"   # 默认用测试
PROD_HOST = "https://fuwu.baijia.com"        # 只在明确要查线上时才换

def acl_compare(service_method: str, params: list, traffic_env: str = "test-eco-6",
                host: str = TEST_HOST):
    """反射调 crm-service 的 Bean 方法 / Feign 接口。
    service_method 形如 '全类名#方法名'，params 按方法形参顺序传。
    host 决定打到测试还是线上——传错了 traffic_env 会被无视，结果全是线上的。"""
    resp = requests.post(
        f"{host}/bgwApi/crmApp/test/acl/compare/services",
        headers={
            "traffic-env": traffic_env,
            "teacherNumber": "0", "accountId": "0", "employeeId": "0",
            "identification": "microLessonStudent",
            "Content-Type": "application/json",
        },
        json={"requests": [{"serviceNameAndMethodName": service_method, "params": params}]},
        proxies={"http": PROXY, "https": PROXY},
        verify=False,
        timeout=20,
    )
    resp.raise_for_status()
    outer = resp.json()["data"][0]
    return list(outer.values())[0]
```

以下每个用例都是「调一次 `acl_compare(...)`」，把返回值打印/挑字段看即可。

## 读：getDynamicWkStudentInfo

方法签名：`getDynamicWkStudentInfo(Long userId, Long periodNumber, String wechatId, String corpId, String qwHookId)`
（`params` 数组严格按此顺序，没有值传 `None`）。

```python
result = acl_compare(
    "com.gaotu.crm.server.app.controller.mcrm.StudentMdmController#getDynamicWkStudentInfo",
    [7209035883, None, "wm96dMCQAA3Moe0ausm-9T-pQlfAK8jA", "wxe9347c2f779b96ca", ""],
)
# result["data"]["displayData"] 是数组，每项 number 是字段号，value 是当前值。
# 某个 number 没出现在数组里 = 这个字段号根本没被展示（不是值为空，是整条都没返回，
# 常见于 fieldInfoROS 权限过滤把它筛掉了）。
```

**⚠️ 注意：走 Controller 方法时，`Account account = ThreadLocalHolder.getAccount()` 拿到的是
`Account::new` 默认空账号（相当于 GUEST 角色），不是某个真实老师的角色！** 排查"某个字段该不该展示"时这样测不准，
必须换成直接调 **Service** 方法（绕开 ThreadLocalHolder，显式传 accountId + 角色 tag）才能模拟真实老师视角：

```python
result = acl_compare(
    "com.gaotu.crm.server.app.service.mcrm.StudentMdmService#getDynamicWkStudentInfo",
    [7209035883, 246915, "gaotu_boss_qiwei_k12_assistant_", None,
     "wm96dMCQAA3Moe0ausm-9T-pQlfAK8jA", "wxe9347c2f779b96ca", ""],
)
# 直调 Service 返回的就是 DynamicWkStudentInfoResponse 本身（没有外层 RestResult 的 code/msg 包装），
# 直接是 {"displayData": [...]}。
```

Service 方法签名是 `(Long userId, Long accountId, String accountRole, Long periodNumber, String wechatId, String corpId, String qwHookId)`
——比 Controller 方法多了 `accountId`/`accountRole` 两个参数，`accountRole` 就是 `account.getCurrentRole().getValue()`
用的角色 tag（先用「代课查某个老师的 accountId」一节里的 `batchGetAccountRole` 拿到这个老师所有 `hasRoles[].tag`，
一个个换着传进来看展示差异）。

**已确认的真实案例（userId=7209035883，accountId=246915 / jinjiahui04）**：同一个 userId，只换 `accountRole`，
`displayData` 里有没有 `number=10019`（身份，`bizName:wkIdentityRole`）完全不同：

| accountRole | 角色名 | 10019 是否出现 |
|---|---|---|
| `gaotu_boss_qiwei_k12_assistant_` | SCRM-长期班二讲-k12 | 有 |
| `gaotu_boss_assistant_` | 长期班二讲老师 | 没有 |
| `gaotu_boss_sales_` | 课程顾问 | 没有 |

⚠️ 这张表只说明"角色会影响字段展示"，**不要拿它当"某人改不了身份"的结论**。企微侧边栏实际用的角色
（都是 `gaotu_boss_qiwei_k12_assistant_`）和 CAS 里的 `currentRole` 不一定是一回事；实测两个表现不同的账号
角色完全相同，真凶是 `qwHookId`（见下节）。

## 写：updateDynamicWkStudentInfo

方法只有一个 `@RequestBody` 参数 UpdateDynamicWkStudentInfoRequest（见 [UpdateDynamicWkStudentInfoRequest.java](../../../server/src/main/java/com/gaotu/crm/server/app/controller/mcrm/studentMdm/UpdateDynamicWkStudentInfoRequest.java)），
`params` 数组只放**一个对象**。注意 `fieldDOList` 字段本身是**字符串**（JSON 编码的数组，不是原生数组/对象——Controller 里用
`ObjectMapper.readValue` 二次反序列化），传的时候要 `json.dumps` 转成字符串再塞进去：

```python
result = acl_compare(
    "com.gaotu.crm.server.app.controller.mcrm.StudentMdmController#updateDynamicWkStudentInfo",
    [{
        "userId": 7209035883,
        "periodNumber": None,
        "fieldDOList": json.dumps([{"number": "10019", "value": "学员"}], ensure_ascii=False),
        "wechatId": "wm96dMCQAA3Moe0ausm-9T-pQlfAK8jA",
        "corpId": "wxe9347c2f779b96ca",
        "qwHookId": "",
    }],
)
# 成功返回 RestResult.ok(null)，即 data 为空对象；接口本身不会告诉你字段是否真的落库/展示，
# 必须再调一次 getDynamicWkStudentInfo 或查 DB 核对（见下）。
```

- `fieldDOList` 里每个元素是 `{"number": "<字段号字符串>", "value": <字段值>}`。

## 单独探测某个字段号在 task-center 那一层到底有没有取值逻辑

不用查全部字段，直接绕开 crm-service 的字段权限/展示逻辑，只对某一个 `fieldNumber` 调
task-center 的 Feign 接口 `ServeFieldClient#queryWithBizType`（钥匙是 `userWechatId`，要用
`SsIdAclService#queryHookByExternalUserId` 先把 `wechatId` 换成内部 hook id，不能直接传原始 `wechatId`）：

```python
hook = acl_compare(
    "com.gaotu.crm.server.domain.upstreamservice.walle.service.SsIdAclService#queryHookByExternalUserId",
    ["wm96dMCQAA3Moe0ausm-9T-pQlfAK8jA", "wxe9347c2f779b96ca"],
)
user_wechat_id = list(hook.values())[0]  # 例如 "7881303566340472"

result = acl_compare(
    "com.gaotu.yunying.task.center.api.feign.ServeFieldClient#queryWithBizType",
    [{
        "userId": 7209035883,
        "bizType": 6,
        "batchLessonQueryDimensionList": [{
            "userId": 7209035883,
            "fieldNumber": 10019,
            "accountId": 246915,
            "userWechatId": user_wechat_id,
            "qiWeiId": "",
            "clazzLessonNumberList": [],
        }],
    }],
)
print(result["data"]["queryWithBizTypeResultROS"])
```

探测时 `userWechatId` 和 `qiWeiId` 要分别试。**身份（10019）走的是 `qiWeiId` 维度，不是 `userWechatId`**
——`qiWeiId` 传空就一定查不到值（返回的记录里连 `value` 这个 key 都没有，不是 value=null）。

> ⚠️ 历史误判，别再踩：早期只用 `qiWeiId=""` 探测过一次，就误判成"task-center 读侧压根没有 10019 的取值处理器"。
> 实际是有的，只是 key 传空了。**下这种"上游没实现"的结论前，先把 key 换成非空值再探一遍。**

## 身份字段（10019）"改了不展示"的真正根因：qwHookId 读写不对称

写路径 [StudentMdmService.java `getUpdateDimensionInfos`](../../../server/src/main/java/com/gaotu/crm/server/app/service/mcrm/StudentMdmService.java) 里
`qwHookId` 为空会**兜底成 `hookWechatId`**；读路径
[ServeFieldClientAclService.java `getFieldQueryDimensionInfo`](../../../server/src/main/java/com/gaotu/crm/server/domain/upstreamservice/field/service/ServeFieldClientAclService.java)
里 `setQiWeiId(qwHookId)` **没有兜底**。

所以 `qwHookId` 拿不到的学员：**写得进去（key=hookWechatId），读不出来（qiWeiId=null）→ 前端表现成"改了没反应 / 身份改不了"**。
亲密称呼（60008）不受影响，因为它走 `userWechatId` 维度。

### ✅ 已修（2026-08-27，分支 `feature-wk-identity-qiweiid-fallback`）

读侧已加兜底，与写侧口径对齐：

```java
// ServeFieldClientAclService#getFieldQueryDimensionInfo
fieldQueryDimensionInfo.setQiWeiId(Strings.isBlank(qwHookId) ? hookWechatId : qwHookId);
```

不新增任何 RPC——`hookWechatId` 本来就是该方法形参（上一行 `setUserWechatId` 就在用），
读路径在 `StudentMdmService#getDynamicWkStudentInfo` 里已经调过一次 `queryHookByExternalUserId` 拿到它了。
**再遇到类似"改了不展示"，先确认这行兜底还在，别又当成新 bug 重查一遍。**

> 反直觉但重要：`qwHookId` 和 `hookWechatId` 来自**两个不同接口、两张不同的表**，
> `queryByExternalUserIdWithBind` 返回空**不代表** hook id 不存在——
> `queryHookByExternalUserId`（走 `ss_wk_user_mapping`）照样能拿到它。
> 兜底之所以成立就靠这一点，所以**不依赖 ss-id 把归并修好**。

| | 来源方法 | 查的表 | 案例中的值 |
|---|---|---|---|
| `qwHookId` | `queryByExternalUserIdWithBind`（前端经 `getByExternalUserId` 拿） | `ss_mapping_user_result` | `""` |
| `hookWechatId` | `queryHookByExternalUserId`（crm 读/写方法里自己调） | `ss_wk_user_mapping` | `7881303566340472` |

### 怎么验证兜底有没有效

**打补丁前**可以先模拟：把 `hookWechatId` 的值当 `qwHookId` 传进去，现有代码就会
`setQiWeiId(hookWechatId)`，与打完补丁的取值逐字段等价。**打补丁后**则直接 `qwHookId` 传空，
走真实路径。判据都是 `displayData` 里 `number=10019` 那条**有没有 `value` 这个 key**：

```python
for q in ["", "7881303566340472"]:
    r = acl_compare(
        "com.gaotu.crm.server.app.service.mcrm.StudentMdmService#getDynamicWkStudentInfo",
        [7209035883, 246915, "gaotu_boss_qiwei_k12_assistant_", None,
         "wm96dMCQAA3Moe0ausm-9T-pQlfAK8jA", "wxe9347c2f779b96ca", q],
    )
    hit = [x for x in r["displayData"] if str(x["number"]) == "10019"]
    print(q or "(空)", hit[0].get("value", "【没有 value】"))
```

旧代码实测（线上 host）：`""` → `【没有 value】`，`"7881303566340472"` → `妈妈`。

**某些测试泳道走不通完整 Service**：`getDynamicWkStudentInfo` 一进去就是
`redisTemplate.hasKey(key)` 那个字段缓存判断，实测 test-eco-2 上它抛
`RedisSystemException: UnsupportedOperationException`（该泳道 redis 配置问题，与本改动无关），
整条读链路直接 500、桥返回 `{"...StudentMdmService_error": "java.lang.RuntimeException: 系统异常"}`。

这时**别硬啃 Service，直接调被改的那个纯函数**验行为，返回值就是 `qiWeiId` 本身，比走完整链路更直接：

```python
for q in ["", "9999999999"]:
    d = acl_compare(
        "com.gaotu.crm.server.domain.upstreamservice.field.service.ServeFieldClientAclService#getFieldQueryDimensionInfo",
        [10019, [], 246915, None, [], "7881300610080617", 7150430370, q],
        traffic_env="test-eco-2",
    )
    print(q or "(空)", d["qiWeiId"], d["userWechatId"])
# test-eco-2 实测：(空) -> 7881300610080617（兜底生效）；9999999999 -> 9999999999（有值时不变）
```

> 只有在「host、泳道都已确认无误，行为仍与预期不符」时，才值得用 `pod-terminal` + arthas
> `jad` 去核实 pod 里跑的字节码。核实时注意：类被 APM/CGLIB 增强过，`jad <类> <方法>` 只会给你
> 代理壳（`delegate$xxx.intercept(...)`），真正的方法体在 `<方法>$original$xxx` 里，要 jad 整个类再找；
> 而且被 jacoco 插桩后三元表达式会展开成 if/else + 临时变量，别因为没看见 `? :` 就断定代码没上去
> （我就这么误判过一次）。更快的办法是直接看 jar 里的 git 信息：
> `unzip -p /apps/srv/instance/app.jar BOOT-INF/classes/git.properties | grep commit.id.abbrev`，
> 和本次提交的 sha 一比就知道镜像对不对。

**注意 `10019` 一直都在 `displayData` 里，`select:1`、`disabled:false`、下拉选项齐全**——
字段本身从来没被权限过滤掉，缺的只是回显值。这正是"能点开下拉框选，选完看不出变化"的由来，
别被"字段能看见"误导成权限没问题就不是这个问题。

### qwHookId 从哪来 / 为什么会是空

> ⚠️ 别把两个 hookId 搞混：`WkAuthController#account`（qiwei-sidebar skill 的第 2 步）返回的 `hookId` 是
> **老师自己**的企微成员 id，跟这里说的 `qwHookId`（**学员/外部联系人**的 hook 企微 id）不是一回事，
> 老师的 hookId 有值不代表学员的 qwHookId 有值。

侧边栏打开时先调 `GET /crmApp/scrm/wk/user/getByExternalUserId`
（[WkUserController.java](../../../server/src/main/java/com/gaotu/crm/server/app/controller/scrm/WkUserController.java)），
它把 `qwHookId` 返给前端，之后 get/update 一路透传：

```java
ResultWithBind r = ssIdAclService.queryByExternalUserIdWithBind(externalUserId, corpId);
String qwHookId = CollectionUtils.isNotEmpty(mappingResults) ? mappingResults.get(0).getQwHookId() : "";
```

直接反射调它就能看到某个外部联系人到底有没有 qwHookId：

```python
r = acl_compare(
    "com.gaotu.crm.server.domain.upstreamservice.walle.service.SsIdAclService#queryByExternalUserIdWithBind",
    ["wm96dMCQAA3Moe0ausm-9T-pQlfAK8jA", "wxe9347c2f779b96ca"],
)
# 看 r["mappingResultList"][0]["qwHookId"]，以及 userInfoResultList[].relatedIdInfoList 里
# 有没有 idType=4（hook 企微 id）。idType: 1=phone 3=wxid 4=qwHookId 5=externalUserId
```

**⚠️ 这句原来写的是"path 是 `/test/` 段但返回的就是线上数据"——那是错的**，当时是因为 host 用了
`fuwu.baijia.com`（线上）才看到线上数据。**数据来自哪个环境完全由 host 决定**，见开头那节。
用 `test-fuwu.baijia.com` 读到的就是测试库（实测：只存在于测试库的 externalUserId 能解析出来）。

**qwHookId 为空 = 该外部联系人在 ss-id 的归并结果里没跟 hook 企微 id 关联上。** 查证表（`prod` / cluster 319 / 库 `urobot`）：

| 表 | 作用 | 怎么查 |
|---|---|---|
| `ss_mapping_user_result` | **ss-id 的归并结果表，`getByExternalUserId` 读的就是它** | `WHERE user_id='<userId>'`，看 `external_user_id` 那行的 `qw_hook_id` 是不是空 |
| `ss_mapping_user_ext` | **身份/role 的最终存储表**，唯一键 `(user_id, related_id, id_type, corp_id)`，`related_id` 就是 `qiWeiId` | `WHERE related_id='<hookId>'`（有 `idx_related_idtype`，按 `user_id` 查会超时） |
| `ss_wk_user_mapping` | 企微官方 id ↔ 客户端 hook id | `WHERE user_id='<externalUserId>'`，`username` 列就是 hook id |
| `ss_mapping_user_external` | userId ↔ externalUserId 绑定 | `WHERE external_user_id='<externalUserId>'` |
| `ss_mapping_user_hook` | userId ↔ hook id | `WHERE hook_id='<hookId>'` |

已确认的真实案例（userId=7209035883）：`ss_mapping_user_result` 里
`external_user_id=wm96dMCQAA3Moe0ausm...` 那行 `qw_hook_id=""`，而 hook id `7881303566340472` 单独占一行、
`external_user_id` 为空——**两行没归并到一起**（phone 也空，缺归并锚点）。对比另一个联系人
`wm96dMCQAAtcBdkCqmX...` 的行 phone + `qw_hook_id=7881302120033192` 全齐，就正常。

**ss-id 侧的账号互通/归并找 `zhangchaoyang01`。**

## 排查"保存了但不显示"的通用步骤

**遇到"A 老师能改、B 老师不能改"，先比请求入参，别一上来就怀疑角色。** 实测踩过：两个账号 `currentRole` 完全一样
（都是 `gaotu_boss_sales_`，`allRoles` 也都含 `gaotu_boss_qiwei_k12_assistant_`），角色根本不是变量，
真正的差异藏在 `qwHookId` 一个有值一个是空。

1. **先捞两边的真实入参日志**（见下节），逐字段对比 `wechatId` / `corpId` / **`qwHookId`**。
   `qwHookId` 一空一有 → 跳到上面「qwHookId 读写不对称」那节。
   **该分支已在 2026-08-27 修掉**，所以先确认待排查的环境/镜像有没有带上那行兜底
   （`ServeFieldClientAclService#getFieldQueryDimensionInfo` 里的 `Strings.isBlank(qwHookId) ? hookWechatId : qwHookId`）；
   带了还复现，才是新问题。
   （wechatId 不同是正常的，两个老师是两个不同的企微好友关系，不构成差异。）
2. 用 traceid-debug skill 查 update 的 trace_tree。**注意：写成功 ≠ 问题不在写**——本案两边都是 0 error、
   都走到了 `UpdateTypeParseBiz#updateContactRoleValue → manualMappingUserId`，写都落库了，问题全在读。
3. 查 `ss_mapping_user_ext`（按 `related_id` 查）确认值到底存没存、存在哪个 `related_id` 下。
   **小坑**：反复保存同一个值时 `update_time` 不会变（MySQL 值没变不刷时间），别据此判断"没写进去"；
   用户反复点同一个值恰恰是"存了但不回显"的典型症状。
4. 值存了但读不出来 → 比对读写两侧用的 key 是不是同一个（`qiWeiId` vs `userWechatId`），再往上追
   `getByExternalUserId` 的 `qwHookId` 和 `ss_mapping_user_result` 的归并情况。
5. 只有前面都排除了，才怀疑**读侧字段权限/展示配置按角色过滤**（见上面按角色换着测的方法）。

## 从日志里拿请求参数（先找到调了这两个接口的真实入参）

服务名（qingzhou 日志的 `__tag__:app`）是 **`crm-app-service-gaotu100-com`**（中间是短横线 `-`，不是点，
用点会一条都搜不到）。用 `qingzhou-log` MCP 的 `get_sls_log_v2` / `get_tls_log_v2`：

- **别只传 `keyword`**——`keyword` 参数拼多个 `and`/中文短语时解析规则和控制台不一致，容易搜出 `[]`。
  **直接把控制台调试栏里的完整查询语句整段塞进 `queryStr` 参数**（原样复制，不用自己拆字段），最稳：
  ```
  __tag__:app: "crm-app-service-gaotu100-com" AND __tag__:environment: prod* and messages: "7209035883" and messages: "动态更新企业微信-学生信息请求参数"
  ```
- `env` 传 `prod`，`logType` 传 `app`（这两个接口的入参日志是 INFO 级，不在 `error` 里）。
- 每条日志里有 `LID:<uuid>` 和 `[TID: <traceId>]`。同一次请求前后多行（比如请求参数日志 + 下游调用日志）用
  **同一个 LID 或完整 TID 当 keyword 再查一次**就能串起来；`TID` 同时也是 traceId，能直接丢给
  `qingzhou-trace` 的 `trace_tree`（配 traceid-debug skill）看这次请求端到端有没有 error span。
- 排查"保存成功但不展示"时，先搜 `updateDynamicWkStudentInfo` 的请求参数日志拿到具体 `userId/wechatId/corpId/fieldDOList`，
  再拿同一个 `userId` 去搜 `getDynamicWkStudentInfo` 的请求参数日志，两边时间点对齐后按上面「读：」的方式重放对比。

## 代课查某个老师的 accountId（不用登录，也不用查库）

1. 拿 accountId 本身不依赖代课——直接进第 2 步反射调 `CasApiService#batchGetAccountRole` 就行。只有在需要
   真的以该老师身份走前端页面、或需要 cas 授权的场景（比如要验证她登录后企微侧边栏页面的真实展示）时，
   才用 `baijia-invoke` MCP 的 `cosplay_login`（`cos_account_name` 传域账号，比如 `jinjiahui04`）登录代课身份。
2. 反射调 `CasApiService#batchGetAccountRole` 拿 accountId 对应的角色详情（如果已经知道 accountId，直接跳这步核对角色；
   如果只知道域账号不知道 accountId，先从企微/工单/日志里拿到 accountId 再传进去）：

   ```python
   accounts = acl_compare(
       "com.gaotu.crm.server.domain.upstreamservice.cas.service.CasApiService#batchGetAccountRole",
       [[246915]],
   )
   for acc in accounts:
       print(acc["displayName"], acc["name"], acc["id"])
       for role in acc.get("hasRoles", []):
           print("  role tag:", role["tag"], role["name"])
   ```

   返回里 `displayName`/`name`（域账号）/`id`（accountId）/`hasRoles[].tag`（角色 tag，就是
   `account.getCurrentRole().getValue()` 用的那个值）都在，可以直接核对某个 accountId 是不是目标老师、
   以及她所有的角色 tag 是什么。
3. 用完记得 `cosplay_logout`（如果第 1 步做过代课登录）还原身份，避免后续请求继续顶着别人的身份。
