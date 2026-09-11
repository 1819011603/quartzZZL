#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境「不发短信 → 手动塞验证码」登录工具。

背景
----
gt-passport-api 测试环境不真发短信，H5 登录填任何码都报「验证码不正确」。
底层真实错误多是 code=5008(over limit) 或 2104(not matched)。
护照的 mock 通用码(gt.need.mock.sms.passcode)只对 clientId=558248523(passport_test)
生效，正常业务 clientId(gaoTu/tutu…)走不到那条路，所以只能往 Redis 里塞一条正常的
短信验证码记录 —— 等价于「真收到一条短信」，走正规校验路径，不改代码、不动认证逻辑。

原理
----
校验逻辑(LoginServiceImpl.validateSmsCodeOnce)：
    passCode = redisService.getPassCodeNew(clientId, mobile)   # 读 Redis
    if StringUtils.equals(passCode, smsCode): 通过
key = clientName(clientId) + mobile —— 所以 **验证码按 clientId 隔离，不通用**：
不同 App(高途课堂/途途课堂)clientId 不同，各自要存一份。
本脚本用 arthas 调服务自己的 RedisService.saveSmsCode(...) 写这条记录，key 天然对齐。

限流：passcode_login_error_count:<mobile> 累计到 5 会先抛 5008。只在「码错」分支 +1；
码对了直接 return 不碰它。但连续试错过就需要 --clear-limit 清一下。

⚠️ 仅测试环境。gt-passport-api 是护照团队(wanghongyang)的共享服务，别在线上用。

常用 clientId
------------
  613156985  gaotuketang   高途课堂 (H5 test-api.gaotu.cn, p_client=1)
  613156986  tutuketang    途途课堂 (H5 test-api.gaotu100.com, p_client=2)
  558248523  passport_test 护照自测(这个 client 才吃 mock 通用码)
更多见 gt-passport-api ClientEnum / Apollo gt.passport.client.all。

用法
----
  # 给高途课堂存 4 位码 1234，30 分钟有效
  python3 set_test_smscode.py --mobile 17900911102

  # 指定 clientId(途途课堂) + 自定义码 + 清限流
  python3 set_test_smscode.py --mobile 17900911102 --client 613156986 --code 1234 --clear-limit

  # 一次给多个 App 都存(高途+途途)
  python3 set_test_smscode.py --mobile 17900911102 --client 613156985,613156986

登录时手机号带不带 +86 都行——脚本按护照实际 key(带 +86)存；填码即上面 --code。
一次性：登录成功后护照会 deletePassCode 删掉，再登需重跑。
"""
import argparse
import subprocess
import sys

# gt-passport-api 测试环境 serviceCode(青舟解析所得)
SERVICE_CODE = "baijia.gt.incre.wly-user.gt-passport-api"
# pod-terminal 驱动 + 带 websockets 的解释器(系统 python3 缺该库)
POD_TERM = "/Users/gaotu/.claude/skills/pod-terminal/pod_term.py"
PY = "/Users/gaotu/.local/mcp-servers/venv/bin/python3"
REDIS_SVC = "com.baijia.uqun.gt.passport.api.biz.service.redis.RedisService"
LIMIT_KEY_TPL = "shared-service:passcode_login_error_count:{mobile}"


def normalize_mobile(m: str) -> str:
    """护照存的 key 手机号带 +86；用户传 17900911102 / +8617900911102 / 8617900911102 都归一。"""
    m = m.strip().replace(" ", "")
    if m.startswith("+86"):
        return m
    if m.startswith("86"):
        return "+" + m
    return "+86" + m


def arthas(express: str, timeout_ms: int = 90000) -> str:
    """用 arthas vmtool 拿 RedisService 单例并执行 express，返回原始输出末几行。"""
    cmd = [
        PY, POD_TERM, "arthas",
        "--service-code", SERVICE_CODE,
        "--command",
        f'vmtool -x 1 --action getInstances --className {REDIS_SVC} '
        f'--express "{express}"',
        "--exec-timeout", str(timeout_ms),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    return out.strip()


def save_code(client_id: int, mobile: str, code: str, ttl: int) -> str:
    express = (f'instances[0].saveSmsCode({client_id}, \\"{mobile}\\", {ttl}, \\"{code}\\")')
    arthas(express)
    # 回读同一条路(登录校验用的 getPassCodeNew)确认
    read = (f'instances[0].getPassCodeNew({client_id}, \\"{mobile}\\")')
    return arthas(read)


def clear_limit(mobile: str) -> str:
    key = LIMIT_KEY_TPL.format(mobile=mobile)
    express = f'instances[0].getRedisClient().del(\\"{key}\\")'
    return arthas(express)


def main():
    ap = argparse.ArgumentParser(description="测试环境手动塞短信验证码(不发短信也能登)")
    ap.add_argument("--mobile", required=True, help="手机号，如 17900911102(带不带+86都行)")
    ap.add_argument("--client", default="613156985",
                    help="clientId，逗号分隔可多个。默认 613156985(高途课堂)；途途课堂=613156986")
    ap.add_argument("--code", default="1234", help="验证码，默认 1234(注意前端多为4位)")
    ap.add_argument("--ttl", type=int, default=1800, help="有效期秒，默认 1800(30分钟)")
    ap.add_argument("--clear-limit", action="store_true", help="同时清掉 over-limit 限流计数")
    args = ap.parse_args()

    mobile = normalize_mobile(args.mobile)
    clients = [c.strip() for c in args.client.split(",") if c.strip()]

    print(f"手机号(key): {mobile}   验证码: {args.code}   TTL: {args.ttl}s")
    ok = True
    for c in clients:
        got = save_code(int(c), mobile, args.code, args.ttl)
        matched = f"@String[{args.code}]" in got
        ok = ok and matched
        flag = "✓" if matched else "✗ 回读不符!"
        val = next((ln for ln in got.splitlines() if "@String" in ln), (got.splitlines()[-1] if got else "(空)"))
        print(f"  clientId={c}: 回读 {val}  {flag}")

    if args.clear_limit:
        r = clear_limit(mobile)
        print(f"  清限流: {r.splitlines()[-1] if r else '(空)'}")

    print("\n完成。前端手机号填 {}，验证码填 {}。一次性，登进去后自动删。".format(
        args.mobile, args.code))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
