# 测试环境短信查询与固定验证码

## 先判断是否需要查短信

**测试手机号以 `12` 开头时，验证码固定为 `1001`，无需查询短信平台。** 此规则由用户确认，仅用于测试环境。

其他测试手机号需要查看短信记录时，使用下方平台。

## 定位与使用

| 项 | 值 |
|---|---|
| 平台 | [短信平台](https://sms.baijia.com/) |
| 按手机号直达 | [查询 13900801001](https://sms.baijia.com/?mobile=13900801001) |
| 页面路由 | `/`（短信记录） |
| 查询参数 | `mobile`：手机号；另支持 `taskId`、`templateId` |
| API 域名 | `https://sms-admin-api.baijia.com` |
| 前端仓库 / 青舟 appId | 未核实，不从域名推断 |

1. 将直达链接中 `mobile=` 后的值替换为目标测试手机号。
2. 确认页面「环境」选择 **测试**，输入手机号后点击「查询」或按回车。
3. 按需筛选签名、任务 ID、模板编号、短信类型、服务商；「仅显示失败」会隐藏其他状态的记录。
4. 列表可查看手机号、正文、状态、发送时间、备注；点击正文切换原文/隐藏原文，展开行查看发送日志和详细信息。原文查看受平台权限控制。

**直达链接只带手机号，不强制环境。** 页面会从浏览器 Cookie `AppEnv` 恢复上次的环境选择（没有历史值才默认测试），同一平台也能查看线上/全部。签名和「仅显示失败」同样会恢复历史选择；查不到时先检查这三项。

## 查询接口

以下路径来自已部署前端构建；完整请求地址为 API 域名加路径。

| 触发 | 方法 | 测试环境路径 | 说明 |
|---|---|---|---|
| 进页面 / 查询 / 筛选 / 下一页 | POST | `/admin/message/listTest` | 分页查询短信，已验证成功返回 `code=0` |
| 点击正文 | POST | `/admin/message/decryptTest` | 入参 `ids: [消息ID]`；根据权限展示原文或申请查看入口 |
| 展开行 | POST | `/admin/message/logTest` | 入参 `id`，查询发送日志 |
| 展开行 | POST | `/admin/message/detail` | 入参 `id`，查询应用、模板、任务等详细信息；路径不带 `Test` |

测试环境列表请求示例（只读）：

```bash
curl -k -sS -x "${AGENT_PROXY_URL:-http://127.0.0.1:8888}" \
  'https://sms-admin-api.baijia.com/admin/message/listTest' \
  -H 'Content-Type: application/json' \
  --data-raw '{"mobile":"13900801001","next":0,"limit":20,"env":"TEST","isFailed":false,"signatureVal":"","ids":"","type":-1,"vendor":""}'
```

- 命令经本地 `baijia-proxy` 注入登录态，不手工填写 Cookie。
- `env` 枚举为 `TEST` / `ONLINE` / `ALL`；测试选项使用 `listTest`，线上/全部使用 `/admin/message/list`。
- 返回 `data.list`、`data.hasMore`、`data.next`、`data.limit`；下一页沿用返回的 `next`，不要自行递增页码。
- 常用字段：`id`、`mobile`、`maskedContent`、`templateId`、`env`、`status`、`result`、`sendTime`、`receiveTime`。正文未展示完整时，按平台权限查看原文。

## 状态判读

| status | 页面含义 |
|---|---|
| 0 | 未提交 |
| 1 | 已提交 |
| 2 | 已下发 |
| 3 | 成功 |
| 4 | 失败 |
| 5 | 预检测失败 |
| 6 | 提交失败 |
| 7 | 下发失败 |
| 8 | 回执失败 |
| 9 | 消息过期 |

查失败原因先看 `result`（备注），再展开日志区分预检测、提交、用户回执阶段。存在平台记录不代表手机已收到短信，需结合状态和回执判断。

## 依据

- 固定验证码规则：用户确认，测试手机号 `12` 开头使用 `1001`。
- 平台机制：2026-10-22 读取在线构建 `index-CgiGM2Ty.js`、`Message-I3vqF0G2.js`、`app-env-9xiFiybR.js`；以当前构建为准。
- 只读验证：经代理调用 `/admin/message/listTest`，返回 `code=0` 且记录 `env=TEST`；正文解密、日志和详情接口仅由前端构建确认，未逐项调用。未执行短信发送。
