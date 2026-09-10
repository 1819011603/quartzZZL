#!/usr/bin/env python3
"""捞取续班归因班级 Job 某天的全部日志行，存成 JSON 供本地统计。

为什么不用 MCP 的 grep 参数：grep 是客户端过滤，服务端只先拉 scanLimit(<=100) 条，
拿它统计等于从 100 条样本里数数，结论必错。这里用 queryStr 做服务端过滤 + offset 翻页。

为什么按线程名过滤：CommonRuleFilter 等 reject 日志，售后侧接口(TID after-sales.*)
也会大量产生，不锁线程会把别人的日志算进来。

用法:
    python3 harvest_job_logs.py                      # 默认当天
    python3 harvest_job_logs.py --date 2026-09-10
    python3 harvest_job_logs.py --date 2026-09-10 --thread Thread-3919
不传 --thread 时会先自动探测当天 Job 的线程名。
"""
import argparse, asyncio, datetime, importlib.util, json, re, sys, time

QZLOG = "/Users/gaotu/.local/mcp-servers/qingzhou_log.py"
START_MARK = "processPendingTasksInBatches | start"


def load_mod():
    # mcpcli.py 目前是坏的(AttributeError: 'Tool' object has no attribute 'name')，
    # 直接 import 模块调 call_tool 绕过。
    spec = importlib.util.spec_from_file_location("qzlog", QZLOG)
    m = importlib.util.module_from_spec(spec)
    sys.modules["qzlog"] = m
    spec.loader.exec_module(m)
    return m


def day_bounds(date_str):
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    t0 = int(time.mktime(d.timetuple()))
    return t0, t0 + 5 * 3600          # Job 在 01:00 跑，取 00:00~05:00 足够


async def query(m, q, t0, t1, off, limit=100):
    args = {"env": "prod", "logType": "app", "queryStr": q,
            "fromTimestampInSeconds": t0, "toTimestampInSeconds": t1,
            "limit": limit, "offset": off}
    r = await m.call_tool("get_sls_log_v2", args)
    return getattr(r[0], "text", str(r[0]))


async def detect_thread(m, t0, t1):
    t = await query(m, f'messages: "{START_MARK}"', t0, t1, 0, 5)
    mm = re.search(r"\[(Thread-\d+)\]", t)
    if not mm:
        sys.exit("没找到 Job 启动日志，确认日期/该天 Job 是否跑过")
    return mm.group(1)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--thread")
    ap.add_argument("--out", default="/tmp/job_lines.json")
    a = ap.parse_args()

    m = load_mod()
    t0, t1 = day_bounds(a.date)
    thread = a.thread or await detect_thread(m, t0, t1)
    print(f"date={a.date} thread={thread} window={t0}~{t1}")

    msgs, off, per = [], 0, []
    while off < 20000:
        t = await query(m, f'messages: "{thread}"', t0, t1, off)
        found = re.findall(r'"message":\s*"(.*?)",\s*"node_ip"', t, re.S)
        per.append(len(found))
        if not found and len(per) > 3 and sum(per[-3:]) == 0:
            break
        msgs.extend(found)
        off += 100

    json.dump(msgs, open(a.out, "w"))
    print(f"harvested {len(msgs)} lines -> {a.out}")


if __name__ == "__main__":
    asyncio.run(main())
