#!/usr/bin/env python3
"""Read-only renewal monitoring; stdout is a summary, JSON snapshots go to --output.

Author: masheng
No notification, offset reset, deployment or production write is performed.
"""
import argparse
import concurrent.futures
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

INSTANCES = ("MQ_INST_1941505946323830_Bay8En7I", "MQ_INST_1941505946323830_BcfK60rM")
DASHBOARDS = {"traffic": "KNHjDP5Hz", "cpu": "7PeU8NtHk", "db": "Ro-QWa1Nz",
              "redis": "CPnxgf1Nz", "node": "rpJ7sc0Hk"}
FAMILIES = {"商品": ("cart", "product", "product-b", "course-app", "course-center", "course-setting"),
            "订单": ("order", "order-b"), "支付": ("newpay", "pay-channel-service"),
            "优惠": ("promotion-app", "promotion-c", "coupon-a", "coupon-c"),
            "node": ("gaotu-mweb", "mweb-gaotujingpin", "mweb-k9", "mweb-suyang", "lexue-m-fe", "pay-web")}


class MonitorError(Exception):
    pass


class LoginExpired(MonitorError):
    pass


def request(url, headers=None, body=None):
    """Use the existing cookie-injection proxy; never read or log cookies."""
    proxy = os.environ.get("AGENT_PROXY_URL", "http://127.0.0.1:8888")
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy}),
        urllib.request.HTTPSHandler(context=ssl._create_unverified_context()))
    req = urllib.request.Request(url, headers=headers or {},
                                 data=None if body is None else json.dumps(body).encode())
    try:
        with opener.open(req, timeout=30) as response:
            text = response.read().decode("utf-8")
            final_url = response.geturl()
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise LoginExpired("登录失效或权限不足，请重新登录目标站点") from exc
        raise MonitorError("HTTP {}: {}".format(exc.code, urllib.parse.urlparse(url).path)) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise MonitorError("网络请求失败，请检查本地 8888 代理") from exc
    if any(x in final_url.lower() for x in ("/login", "passport", "signin")):
        raise LoginExpired("请求跳转到登录页，请重新登录目标站点")
    return text


def decode_response(text):
    try:
        data = json.loads(text)
    except ValueError as exc:
        if "<html" in text.lower() or "<!doctype" in text.lower():
            raise LoginExpired("接口返回登录页面，请重新登录目标站点") from exc
        raise MonitorError("接口返回非 JSON 数据") from exc
    if isinstance(data, dict):
        if str(data.get("code")) == "700":
            raise LoginExpired("接口登录失效，请重新登录目标站点")
        if data.get("error") or data.get("success") is False or data.get("ok") is False:
            raise MonitorError("上游接口报告失败")
        for result in (data.get("results") or {}).values():
            if result.get("error") or result.get("status", 200) >= 400:
                raise MonitorError("Grafana 查询失败，不能当作无堆积或无流量")
    return data


class Belong:
    def __init__(self):
        page = request("https://belong.baijia.com/sla?tab=0")
        match = re.search(r'<script[^>]+src="(https://gtoss\.gsxcdn\.com/[^\"]+/umi\.[^\"]+\.js)"', page)
        if not match:
            raise MonitorError("无法定位 belong 前端配置")
        # Use the same current configuration as the page, only in process memory.
        bundle = request(match.group(1))
        config = re.search(r'grafana:\{endpoint:"(https://sre-grafana\.baijia\.com)".*?Authorization:"([^\"]+)"', bundle)
        if not config:
            raise MonitorError("belong Grafana 配置结构已变化")
        self.endpoint = config.group(1)
        self.headers = {"Content-Type": "application/json", "Authorization": config.group(2)}

    def api(self, path, body=None):
        return decode_response(request(self.endpoint + path, self.headers, body))

    def panels(self, uid):
        data = self.api("/api/dashboards/uid/" + uid)
        if not isinstance(data.get("dashboard", {}).get("panels"), list):
            raise MonitorError("监控面板不可用: " + uid)
        return data["dashboard"]["panels"]

    def query(self, targets, start, end):
        targets = [dict(t) for t in targets if not t.get("hide")]
        if not targets:
            raise MonitorError("面板没有可用查询")
        kind = targets[0].get("datasource", {}).get("type")
        if kind == "marcusolsson-json-datasource":
            body = targets[0]["body"].replace("$__unixEpochFrom()", str(start // 1000))
            body = body.replace("$__unixEpochTo()", str(end // 1000))
            return self.api("/api/datasources/proxy/346/query/gapm", json.loads(body))
        if kind == "aliyun_cms_grafana_datasource":
            target = targets[0]
            dimensions = target.get("dimensions", [])
            params = {"Action": "QueryMetricList", "Length": "1000", "Project": target["project"],
                      "Metric": target["metric"], "Period": "60", "StartTime": start, "EndTime": end,
                      "Dimensions": "[" + ",".join(dimensions) + "]" if isinstance(dimensions, list) else dimensions}
            return self.api("/api/datasources/485/resources/proxy_aliyun_cms_pop?" + urllib.parse.urlencode(params))
        source_id = {"prometheus": 322, "aliyun-log-service-datasource": 385}.get(kind)
        if source_id is None:
            raise MonitorError("不支持的监控数据源: " + str(kind))
        queries = [dict(t, intervalMs=15000, maxDataPoints=600, datasourceId=source_id) for t in targets]
        return self.api("/api/ds/query", {"queries": queries, "from": str(start), "to": str(end),
                                        "range": {"from": iso(start), "to": iso(end),
                                                  "raw": {"from": "now-5m", "to": "now"}}})


def iso(timestamp):
    return dt.datetime.fromtimestamp(timestamp / 1000, dt.timezone.utc).isoformat()


def family(title):
    name = title.split("的")[0].replace(".gaotu100.com", "")
    for group, names in FAMILIES.items():
        if name in names:
            return group
    return None


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def summarize(data, start, end):
    """Preserve real time series and API rows; never synthesize missing metrics."""
    series = []
    for result in (data.get("results") or {}).values():
        for frame in result.get("frames", []):
            fields, values = frame.get("schema", {}).get("fields", []), frame.get("data", {}).get("values", [])
            time_index = next((i for i, f in enumerate(fields) if f.get("type") == "time"), None)
            if time_index is None or time_index >= len(values):
                continue
            for i, field in enumerate(fields):
                if field.get("type") != "number" or i >= len(values):
                    continue
                points = [[t, v] for t, v in zip(values[time_index], values[i])
                          if numeric(t) and start <= t <= end and numeric(v)]
                if points:
                    series.append({"name": frame.get("schema", {}).get("name") or field.get("name"),
                                   "labels": field.get("labels", {}), "points": sorted(points),
                                   "max": max(v for _, v in points), "last": sorted(points)[-1][1]})
    datapoints = data.get("Datapoints", data.get("Datapoint", []))
    if isinstance(datapoints, str):
        datapoints = json.loads(datapoints)
    rows = data.get("data", [])
    if not isinstance(rows, list):
        raise MonitorError("接口指标 data 结构发生变化")
    if not isinstance(datapoints, list):
        raise MonitorError("云监控 Datapoints 结构发生变化")
    rows = [row for row in rows if numeric(row.get("createTime")) and start <= row["createTime"] * 1000 <= end]
    datapoints = [{k: v for k, v in point.items() if k != "userId"} for point in datapoints
                  if numeric(point.get("timestamp")) and start <= point["timestamp"] <= end]
    return {"status": "ok" if series or rows or datapoints else "no_data",
            "series": series, "api_metrics": rows, "datapoints": datapoints}


def collect_panel(client, category, panel, start, end):
    result = {"category": category, "title": panel.get("title"), "panel_id": panel.get("id")}
    try:
        result.update(summarize(client.query(panel.get("targets", []), start, end), start, end))
    except LoginExpired:
        raise
    except (MonitorError, KeyError, TypeError, ValueError) as exc:
        result.update(status="error", error=str(exc))
    return result


def collect_mq(instance, top_n, cli):
    args = {"instance_id": instance, "region": "cn-beijing", "metric": "ready", "top_n": top_n}
    try:
        run = subprocess.run([str(cli), "aliyun_console", "ons_group_backlog_top", json.dumps(args), "--full"],
                             capture_output=True, text=True, timeout=60)
        if "LOGIN_EXPIRED" in run.stdout or "LOGIN_EXPIRED" in run.stderr:
            raise LoginExpired("阿里云登录失效，请重新登录 ons.console.aliyun.com")
        data = decode_response(run.stdout)
        if run.returncode or data.get("ok") is not True or not isinstance(data.get("groups"), list):
            raise MonitorError("MQ 查询失败，请检查 mcpcli 和阿里云权限")
        data["status"] = "ok" if data["groups"] else "no_data"
        data["scope"] = "instance_top_n"
        return data
    except LoginExpired:
        raise
    except (OSError, subprocess.TimeoutExpired, MonitorError) as exc:
        return {"instance_id": instance, "status": "error", "error": str(exc)}


def collect(args):
    end = int(time.time() * 1000)
    start = end - 5 * 60 * 1000
    report = {"sampled_at": iso(end), "window_minutes": 5, "from": iso(start), "to": iso(end),
              "source": "https://belong.baijia.com/sla?tab=0", "tabs": {}, "mq": []}
    if args.only != "mq":
        client = Belong()
        dashboards = {kind: client.panels(uid) for kind, uid in DASHBOARDS.items()}
        jobs = []
        for kind, panels in dashboards.items():
            for panel in panels:
                if kind == "traffic":
                    group = next((g for g in FAMILIES if g in panel.get("title", "")), None)
                else:
                    group = "node" if kind == "node" else family(panel.get("title", ""))
                if group and panel.get("targets"):
                    jobs.append((group, kind, panel))
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [(g, pool.submit(collect_panel, client, kind, panel, start, end)) for g, kind, panel in jobs]
            for group, future in futures:
                report["tabs"].setdefault(group, []).append(future.result())
        for group in FAMILIES:
            if not report["tabs"].get(group):
                report["tabs"][group] = [{"status": "error", "error": "未找到该页签的监控面板"}]
    if args.only != "belong":
        for instance in args.instance or INSTANCES:
            report["mq"].append(collect_mq(instance, args.top_n, args.mcpcli))
    statuses = [p["status"] for panels in report["tabs"].values() for p in panels]
    statuses += [m["status"] for m in report["mq"]]
    report["status"] = "ok" if statuses and all(s == "ok" for s in statuses) else "incomplete"
    return report


def print_summary(report, path):
    print("{} | 近5分钟 | 采集状态={} | {}".format(report["sampled_at"], report["status"], path), flush=True)
    for group, panels in report["tabs"].items():
        missing = [p.get("title", "unknown") for p in panels if p["status"] != "ok"]
        cpu = [s["max"] for p in panels if p.get("category") == "cpu" for s in p.get("series", [])]
        print("  {}: 面板 {}/{} 有数据，CPU峰值={}{}".format(
            group, len(panels) - len(missing), len(panels),
            "{:.2f}%".format(max(cpu)) if cpu else "无数据", "，缺失/失败=" + ",".join(missing) if missing else ""))
        rows = [r for p in panels for r in p.get("api_metrics", [])]
        if rows:
            requests = sum(r.get("requestCount", 0) for r in rows)
            errors = sum(r.get("errorCount", 0) for r in rows)
            p99 = max((r.get("p99", 0) for r in rows if r.get("requestCount", 0) > 0), default=None)
            print("    请求量={}，错误量={}，错误率={}，最大接口P99={}ms".format(
                requests, errors, "{:.3f}%".format(100 * errors / requests) if requests else "无请求",
                p99 if p99 is not None else "无请求"))
    for mq in report["mq"]:
        print("  MQ {}: {}，堆积Top{}={}".format(mq["instance_id"], mq["status"], mq.get("top_n", "?"),
              ", ".join("{}:{}".format(g["group_id"], g["backlog"]) for g in mq.get("groups", [])[:5])))


def positive(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("必须大于0")
    return value


def main():
    parser = argparse.ArgumentParser(description="续班压测只读监控：五个页签近5分钟 + MQ实例Top N堆积")
    parser.add_argument("--output", type=Path, default=Path("/tmp/renewal-monitor"))
    parser.add_argument("--interval", type=positive, default=60, help="持续采集间隔秒数，默认60")
    parser.add_argument("--watch", action="store_true", help="持续采集，Ctrl-C停止；默认只采一次")
    parser.add_argument("--count", type=positive, help="--watch时的采集次数上限")
    parser.add_argument("--only", choices=("all", "belong", "mq"), default="all")
    parser.add_argument("--instance", action="append", help="MQ实例，可重复；默认保障文档中的两个生产实例")
    parser.add_argument("--top-n", type=positive, default=30)
    parser.add_argument("--mcpcli", type=Path, default=Path.home() / ".local/mcp-servers/mcpcli.py")
    args = parser.parse_args()
    if args.count and not args.watch:
        parser.error("--count需要与--watch一起使用")
    args.output.mkdir(parents=True, exist_ok=True)
    iteration = 0
    exit_code = 0
    try:
        while True:
            began = time.monotonic()
            report = collect(args)
            stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            path = args.output / (stamp + ".json")
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print_summary(report, path)
            iteration += 1
            if report["status"] != "ok":
                exit_code = 2
            if not args.watch or (args.count and iteration >= args.count):
                return exit_code
            time.sleep(max(0, args.interval - (time.monotonic() - began)))
    except LoginExpired as exc:
        print("停止采集: " + str(exc), file=sys.stderr)
        return 3
    except (MonitorError, OSError, ValueError) as exc:
        print("采集失败: " + str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
