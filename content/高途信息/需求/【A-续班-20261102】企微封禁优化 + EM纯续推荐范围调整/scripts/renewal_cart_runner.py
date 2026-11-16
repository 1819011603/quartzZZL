#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""续班购物车接口压测 / 巡检脚本（Python 版，替代 renewal_cart_fixed.jmx）

- 数据：TAB 分隔两列（表头 userId、renewalNumber）。默认 cart_test_fixture.txt（TEST 环境回归 fixture，
  来源见 README-renewal-cart-runner.md；生产数据文件如 cart_yure.txt 为线上用户/计划号，TEST 调不通）
- 请求：GET /web/renewal/cart?appointUserId=&renewalNumber=（对应 RenewalController @GetMapping("/cart")）
  - TEST 推荐用 --pod <podIP> 直连：http://{pod}:28688/web/renewal/cart，自动带 traffic-env / host 头绕网关
  - 前提：Apollo renewal.cart.debug.appoint-user.enabled=true（TEST 已开），否则 appointUserId 被忽略走登录态
- 断言：HTTP 200 / 业务 status=0 / code=0 / gradeClazzList 结构完整（容忍空购物车）
- 统计：renewalRole 分布（1=主计划纯续 / 2=从计划纯续 / null=老条目或实时扩科加购），不断言只计数
- 跑完输出：成功率、QPS、延迟分位、异常分类、status 分布、role 分布、按计划成功率、失败明细

常用用法
    python3 renewal_cart_runner.py --pod 10.xx.xx.xx --traffic-env test-eco-8            # TEST pod 直连（推荐）
    python3 renewal_cart_runner.py --pod 10.xx.xx.xx --threads 10 --limit 1000
    python3 renewal_cart_runner.py --pod 10.xx.xx.xx --duration 60 --threads 5
    python3 renewal_cart_runner.py --url http://x:x/web/renewal/cart --file cart_press.txt   # 自定义入口
    python3 renewal_cart_runner.py --fail-on-error           # 有失败时退出码 1（可接 CI）

输出文件（默认当前目录）
    failures_<时间戳>.csv   失败样本明细
    summary_<时间戳>.json   结构化汇总
"""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
import random
import sys
import threading
import time
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

import requests

# 不设默认 URL：防止误打线上网关。TEST 用 --pod 直连，或显式传 --url
POD_DIRECT_PORT = 28688                      # cart pod 直连端口（绕网关）
POD_DIRECT_PATH = "/web/renewal/cart"        # RenewalController @GetMapping("/cart")，无网关 /cart 前缀
POD_HOST_HEADER = "cart.gaotu100.com"        # pod 直连时必带的 host 头（服务按它路由）
USER_AGENT = "renewal-cart-py/1.0"


# --------------------------------------------------------------------------- #
# 数据结构
# --------------------------------------------------------------------------- #
@dataclass(slots=True)
class Sample:
    uid: str
    plan: str
    ok: bool
    category: str
    message: str = ""
    http_code: int = 0
    status: object = None
    code: object = None
    elapsed_ms: float = 0.0
    groups: int = 0
    courses: int = 0
    role_main: int = 0     # renewalRole=1 主计划纯续条目数
    role_slave: int = 0    # renewalRole=2 从计划纯续条目数
    role_null: int = 0     # renewalRole=null 老条目 / 实时扩科加购条目数


@dataclass
class WorkerResult:
    latencies: list[float] = field(default_factory=list)
    categories: Counter = field(default_factory=Counter)
    messages: Counter = field(default_factory=Counter)
    statuses: Counter = field(default_factory=Counter)
    plan_total: Counter = field(default_factory=Counter)
    plan_fail: Counter = field(default_factory=Counter)
    failures: list[Sample] = field(default_factory=list)
    slowest: list = field(default_factory=list)
    empty_cart: int = 0
    total: int = 0
    failed: int = 0
    role_main: int = 0
    role_slave: int = 0
    role_null: int = 0


# --------------------------------------------------------------------------- #
# 工具
# --------------------------------------------------------------------------- #
def disp_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def pad(text: str, width: int, align: str = "left") -> str:
    gap = max(0, width - disp_width(text))
    if align == "right":
        return " " * gap + text
    return text + " " * gap


def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return sorted_values[int(k)]
    return sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * (k - lo)


def load_rows(path: Path, delimiter: str, shuffle: bool) -> list[tuple[str, str]]:
    if not path.exists():
        sys.exit(f"[错误] 数据文件不存在：{path}")

    raw = path.read_text(encoding="utf-8")
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    if not lines:
        sys.exit(f"[错误] 数据文件为空：{path}")

    header = lines[0].split(delimiter)
    if len(header) < 2:
        sys.exit(f"[错误] 表头解析失败（分隔符应为 {'TAB' if delimiter == chr(9) else delimiter}）：{lines[0]!r}")

    rows: list[tuple[str, str]] = []
    bad: list[str] = []
    for ln in lines[1:]:
        parts = ln.split(delimiter)
        if len(parts) < 2:
            bad.append(ln)
            continue
        uid, plan = parts[0].strip(), parts[1].strip()
        if uid.isdigit() and plan.isdigit():
            rows.append((uid, plan))
        else:
            bad.append(ln)

    excel_suspect = any("e+" in line.lower() for line in bad)

    if not rows:
        hint = "、".join(bad[:3])
        if excel_suspect:
            sys.exit(
                "[错误] 没有可用数据行：ID 被转成了科学计数法（如 1.83447E+16），\n"
                f"        样例：{hint}\n"
                "        这是 Excel 打开保存造成的。请重新从飞书导出纯文本，不要用 Excel 打开保存。"
            )
        sys.exit(f"[错误] 没有可用数据行，前 3 行样例：{hint}")

    # 关键防线：Excel 另存会把 ID 变成 1.83447E+16，直接拦下
    if bad:
        hint = "、".join(bad[:2])
        extra = "（疑似 Excel 科学计数法/截断）" if excel_suspect else ""
        sys.exit(
            f"[错误] 有 {len(bad)} 行 ID 不是纯数字{extra}，例如：\n"
            f"        {hint}\n"
            f"        请重新从飞书导出纯文本数据，不要用 Excel 打开保存。"
        )

    if shuffle:
        random.shuffle(rows)
    return rows


class TaskSource:
    """线程安全地分发 (userId, renewalNumber)，支持 limit / duration / 循环。"""

    def __init__(self, rows: list[tuple[str, str]], limit: int | None, cycle: bool):
        self._rows = rows
        self._limit = limit
        self._cycle = cycle
        self._idx = 0
        self._issued = 0
        self._lock = threading.Lock()
        self._deadline: float | None = None

    def set_deadline(self, deadline: float | None) -> None:
        self._deadline = deadline

    @property
    def issued(self) -> int:
        with self._lock:
            return self._issued

    def take(self) -> tuple[str, str] | None:
        if self._deadline is not None and time.monotonic() >= self._deadline:
            return None
        with self._lock:
            if self._limit is not None and self._issued >= self._limit:
                return None
            if self._idx >= len(self._rows):
                if not self._cycle:
                    return None
                random.shuffle(self._rows)
                self._idx = 0
            row = self._rows[self._idx]
            self._idx += 1
            self._issued += 1
            return row


class RateLimiter:
    """全局均匀限速（--rps）。"""

    def __init__(self, rps: float | None):
        self._interval = 1.0 / rps if rps and rps > 0 else 0.0
        self._next = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        if not self._interval:
            return
        with self._lock:
            now = time.monotonic()
            if self._next < now:
                self._next = now
            self._next += self._interval
            delay = self._next - now
        if delay > 0:
            time.sleep(delay)


_THREAD_LOCAL = threading.local()


def get_session() -> requests.Session:
    session = getattr(_THREAD_LOCAL, "session", None)
    if session is None:
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
        _THREAD_LOCAL.session = session
    return session


# --------------------------------------------------------------------------- #
# 单次请求 + 断言
# --------------------------------------------------------------------------- #
def probe(url: str, uid: str, plan: str, timeout: float, headers: dict) -> Sample:
    started = time.perf_counter()
    try:
        resp = get_session().get(
            url, params={"appointUserId": uid, "renewalNumber": plan}, timeout=timeout,
            headers=headers,
        )
    except requests.Timeout:
        return Sample(uid, plan, False, "timeout", f"请求超时(>{timeout}s)",
                      elapsed_ms=(time.perf_counter() - started) * 1000)
    except requests.RequestException as exc:
        return Sample(uid, plan, False, "conn_error", str(exc)[:200],
                      elapsed_ms=(time.perf_counter() - started) * 1000)

    elapsed_ms = (time.perf_counter() - started) * 1000
    http_code = resp.status_code

    if http_code != 200:
        return Sample(uid, plan, False, "http_error", f"HTTP {http_code}",
                      http_code=http_code, elapsed_ms=elapsed_ms)

    try:
        payload = resp.json()
    except ValueError:
        body = (resp.text or "")[:120].replace("\n", " ")
        return Sample(uid, plan, False, "invalid_json", f"响应非 JSON：{body}",
                      http_code=http_code, elapsed_ms=elapsed_ms)

    status = payload.get("status")
    code = payload.get("code")
    if status != 0:
        err = payload.get("error_info") or payload.get("msg") or ""
        return Sample(uid, plan, False, "biz_error", f"status={status} {err}".strip(),
                      http_code=http_code, status=status, code=code, elapsed_ms=elapsed_ms)

    if code != 0:
        return Sample(uid, plan, False, "code_mismatch", f"status=0 但 code={code}",
                      http_code=http_code, status=status, code=code, elapsed_ms=elapsed_ms)

    data = payload.get("data")
    if not isinstance(data, dict) or "gradeClazzList" not in data:
        # code=0 且 data 是 dict 但无 gradeClazzList：该用户无推荐结果（如纯从计划学员，
        # 老链路返回仅计划头信息的空购物车）——属正常业务空，计成功空集而非失败
        if isinstance(data, dict):
            return Sample(uid, plan, True, "success_empty", "业务空（无推荐结果）",
                          http_code=http_code, status=status, code=code, elapsed_ms=elapsed_ms)
        return Sample(uid, plan, False, "data_missing", "缺少 data.gradeClazzList",
                      http_code=http_code, status=status, code=code, elapsed_ms=elapsed_ms)

    groups = data.get("gradeClazzList")
    if groups is None or not isinstance(groups, list):
        return Sample(uid, plan, False, "data_missing", "gradeClazzList 不是数组",
                      http_code=http_code, status=status, code=code, elapsed_ms=elapsed_ms)

    courses = 0
    role_main = role_slave = role_null = 0
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("clazzDetailDTOList"), list):
            grade = group.get("grade") if isinstance(group, dict) else "?"
            return Sample(uid, plan, False, "structure_missing",
                          f"年级分组缺少 clazzDetailDTOList(grade={grade})",
                          http_code=http_code, status=status, code=code,
                          elapsed_ms=elapsed_ms, groups=len(groups))
        for course in group["clazzDetailDTOList"]:
            role = course.get("renewalRole") if isinstance(course, dict) else None
            if role == 1:
                role_main += 1
            elif role == 2:
                role_slave += 1
            else:
                role_null += 1
        courses += len(group["clazzDetailDTOList"])

    return Sample(uid, plan, True, "ok", "", http_code=http_code, status=status,
                  code=code, elapsed_ms=elapsed_ms, groups=len(groups), courses=courses,
                  role_main=role_main, role_slave=role_slave, role_null=role_null)


# --------------------------------------------------------------------------- #
# 压测主体
# --------------------------------------------------------------------------- #
def worker(source: TaskSource, url: str, timeout: float, limiter: RateLimiter,
           stop: threading.Event, fail_keep: int, headers: dict) -> WorkerResult:
    result = WorkerResult()
    while not stop.is_set():
        row = source.take()
        if row is None:
            break
        limiter.wait()
        sample = probe(url, row[0], row[1], timeout, headers)

        result.total += 1
        result.latencies.append(sample.elapsed_ms)
        result.plan_total[sample.plan] += 1
        result.role_main += sample.role_main
        result.role_slave += sample.role_slave
        result.role_null += sample.role_null
        if sample.ok:
            result.categories["ok"] += 1
            if sample.groups == 0:
                result.empty_cart += 1
        else:
            result.failed += 1
            result.categories[sample.category] += 1
            result.messages[(sample.category, sample.message)] += 1
            result.plan_fail[sample.plan] += 1
            if len(result.failures) < fail_keep:
                result.failures.append(sample)
        result.statuses[str(sample.status)] += 1

        item = (sample.elapsed_ms, sample.uid, sample.plan, sample.category, sample.message)
        if len(result.slowest) < 5:
            heapq.heappush(result.slowest, item)
        elif sample.elapsed_ms > result.slowest[0][0]:
            heapq.heapreplace(result.slowest, item)
    return result


def merge(results: Iterable[WorkerResult]) -> WorkerResult:
    merged = WorkerResult()
    for r in results:
        merged.total += r.total
        merged.failed += r.failed
        merged.empty_cart += r.empty_cart
        merged.role_main += r.role_main
        merged.role_slave += r.role_slave
        merged.role_null += r.role_null
        merged.latencies.extend(r.latencies)
        merged.categories.update(r.categories)
        merged.messages.update(r.messages)
        merged.statuses.update(r.statuses)
        merged.plan_total.update(r.plan_total)
        merged.plan_fail.update(r.plan_fail)
        merged.failures.extend(r.failures)
        for item in r.slowest:
            if len(merged.slowest) < 5:
                heapq.heappush(merged.slowest, item)
            elif item[0] > merged.slowest[0][0]:
                heapq.heapreplace(merged.slowest, item)
    return merged


CATEGORY_LABEL = {
    "http_error": "HTTP 非 200",
    "timeout": "请求超时",
    "conn_error": "连接异常",
    "invalid_json": "响应非 JSON",
    "biz_error": "业务错误(status!=0)",
    "code_mismatch": "业务错误(code!=0)",
    "data_missing": "data/gradeClazzList 缺失",
    "structure_missing": "课程明细结构缺失",
}


# --------------------------------------------------------------------------- #
# 汇总输出
# --------------------------------------------------------------------------- #
def summarize(merged: WorkerResult, elapsed_s: float, cfg: dict,
              fail_csv: Path | None, summary_json: Path) -> str:
    lat = sorted(merged.latencies)
    lines: list[str] = []
    add = lines.append

    total = merged.total or 1
    success = merged.total - merged.failed
    rate = success / total * 100

    add("")
    add("=" * 78)
    add("续班购物车接口巡检汇总")
    add("=" * 78)
    add(f"接口      : {cfg['url']}")
    add(f"数据文件  : {cfg['file']}（{cfg['rows']} 行）")
    add(f"并发/模式 : {cfg['threads']} 线程 · {cfg['mode']}")
    add(f"开始时间  : {cfg['started_at']}   总耗时: {elapsed_s:.1f}s   QPS: {merged.total / elapsed_s:.1f}")
    add("")

    add("-" * 78)
    add(f"请求总数  : {merged.total}")
    add(f"成功      : {success}  ({rate:.2f}%)")
    add(f"失败      : {merged.failed}  ({100 - rate:.2f}%)")
    if merged.empty_cart:
        add(f"空购物车  : {merged.empty_cart}（业务合法，未计失败）")
    add("")

    if lat:
        add("-" * 78)
        add("响应耗时(ms): "
            f"avg {statistics_mean(lat):.1f} | p50 {percentile(lat, 0.50):.1f} | "
            f"p90 {percentile(lat, 0.90):.1f} | p95 {percentile(lat, 0.95):.1f} | "
            f"p99 {percentile(lat, 0.99):.1f} | max {lat[-1]:.1f}")
        add("")

    add("-" * 78)
    add("异常分类：")
    if merged.failed == 0:
        add("  （无）")
    else:
        rows = [(k, v) for k, v in merged.categories.items() if k != "ok"]
        rows.sort(key=lambda kv: -kv[1])
        w = max(disp_width(CATEGORY_LABEL.get(k, k)) for k, _ in rows) + 2
        for key, count in rows:
            add(f"  {pad(CATEGORY_LABEL.get(key, key), w)}{count:>8}  {count / total * 100:>6.2f}%")
    add("")

    add("-" * 78)
    add("业务 status 分布：" + ", ".join(f"{k}:{v}" for k, v in merged.statuses.most_common(6)))
    add("renewalRole 分布：role=1(主纯续) "
        f"{merged.role_main} · role=2(从纯续) {merged.role_slave} · null(老条目/实时扩科加购) {merged.role_null}")
    add("")

    if len(merged.plan_total) > 1:
        add("-" * 78)
        add("按续班计划：")
        add(f"  {pad('renewalNumber', 20)}{pad('请求', 8, 'right')}{pad('失败', 8, 'right')}{pad('成功率', 10, 'right')}")
        for plan, cnt in merged.plan_total.most_common():
            failed = merged.plan_fail.get(plan, 0)
            add(f"  {pad(plan, 20)}{cnt:>8}{failed:>8}{(cnt - failed) / cnt * 100:>9.2f}%")
        add("")

    if merged.failed:
        add("-" * 78)
        add("失败原因 TOP：")
        for (cat, msg), count in merged.messages.most_common(5):
            add(f"  {count:>7}  [{CATEGORY_LABEL.get(cat, cat)}] {msg[:80]}")
        add("")

        add("-" * 78)
        add("失败样例（前 10 条）：")
        for s in merged.failures[:10]:
            add(f"  uid={s.uid:<15} plan={s.plan:<18} {CATEGORY_LABEL.get(s.category, s.category)}: {s.message[:70]}")
        add("")

    if merged.slowest:
        add("-" * 78)
        add("最慢请求：")
        for ms, uid, plan, cat, _msg in sorted(merged.slowest, reverse=True)[:5]:
            add(f"  {ms:8.1f} ms  uid={uid:<15} plan={plan}  {cat}")
        add("")

    if fail_csv:
        add(f"失败明细: {fail_csv}")
    add(f"汇总 JSON: {summary_json}")
    add("=" * 78)
    return "\n".join(lines)


def statistics_mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description="续班购物车接口压测与异常汇总")
    parser.add_argument("--file", default="cart_test_fixture.txt",
                        help="数据文件，TAB 分隔（默认 TEST 回归 fixture cart_test_fixture.txt；"
                             "线上数据文件如 cart_yure.txt 的用户/计划在 TEST 调不通，勿直接使用）")
    parser.add_argument("--delimiter", default="\t", help="列分隔符，默认 TAB；可传 ','")
    parser.add_argument("--pod", default=None,
                        help="cart pod IP：TEST 直连推荐。自动拼 http://{pod}:28688/web/renewal/cart "
                             "并带 traffic-env / host 头（绕网关与登录）")
    parser.add_argument("--traffic-env", default="test", dest="traffic_env",
                        help="泳道头 traffic-env 的值（默认 test；测试环境子泳道如 test-eco-8）")
    parser.add_argument("--url", default=None,
                        help="接口完整地址（与 --pod 二选一；无默认值，防误打线上网关）")
    parser.add_argument("--threads", type=int, default=3, help="并发线程数（默认 3）")
    parser.add_argument("--limit", type=int, default=None, help="最多发多少个请求")
    parser.add_argument("--duration", type=float, default=None, help="持续压测秒数（到点停止）")
    parser.add_argument("--timeout", type=float, default=30.0, help="单请求超时秒数（默认 30）")
    parser.add_argument("--rps", type=float, default=None, help="全局限速（每秒请求数）")
    parser.add_argument("--shuffle", action="store_true", help="打散数据顺序（让各计划均匀分布）")
    parser.add_argument("--out-dir", default=".", help="失败明细/汇总输出目录")
    parser.add_argument("--fail-keep", type=int, default=2000, help="内存里最多保留多少条失败明细详情")
    parser.add_argument("--fail-on-error", action="store_true", help="存在失败时退出码为 1")
    args = parser.parse_args()

    if args.threads < 1:
        parser.error("--threads 必须 >= 1")

    # URL 与请求头解析：--pod（TEST 直连推荐）或 --url，二选一
    if args.pod:
        url = f"http://{args.pod}:{POD_DIRECT_PORT}{POD_DIRECT_PATH}"
        headers = {"traffic-env": args.traffic_env, "host": POD_HOST_HEADER}
    elif args.url:
        url = args.url
        headers = {}
        if args.traffic_env:
            headers["traffic-env"] = args.traffic_env
    else:
        parser.error("必须指定 --pod <podIP>（TEST 直连，自动带 traffic-env/host 头）或 --url <完整地址>")

    data_path = Path(args.file).expanduser()
    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(data_path, args.delimiter, args.shuffle)
    print(f"[信息] 已加载 {len(rows)} 行数据：{data_path}")

    cycle = args.duration is not None or (args.limit is not None and args.limit > len(rows))
    source = TaskSource(rows, args.limit, cycle)
    stop = threading.Event()
    limiter = RateLimiter(args.rps)

    if args.duration:
        source.set_deadline(time.monotonic() + args.duration)

    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    started = time.monotonic()

    threads = [
        threading.Thread(
            target=lambda: results.append(
                worker(source, url, args.timeout, limiter, stop, args.fail_keep, headers)
            ),
            daemon=True,
        )
        for _ in range(args.threads)
    ]

    results: list[WorkerResult] = []
    for t in threads:
        t.start()

    # 进度条
    try:
        while any(t.is_alive() for t in threads):
            time.sleep(2)
            done = source.issued
            print(f"\r[进度] 已发请求 {done}"
                  + (f"/{args.limit}" if args.limit else "")
                  + f" · 已运行 {time.monotonic() - started:.0f}s", end="", flush=True)
    except KeyboardInterrupt:
        print("\n[中断] 收到 Ctrl-C，停止发压并汇总已有结果…")
        stop.set()
        source.set_deadline(0)

    for t in threads:
        t.join(timeout=args.timeout + 5)

    elapsed_s = max(time.monotonic() - started, 1e-6)
    merged = merge(results)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fail_csv = None
    if merged.failures:
        fail_csv = out_dir / f"failures_{ts}.csv"
        with fail_csv.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["userId", "renewalNumber", "category", "message",
                             "httpCode", "status", "code", "elapsedMs"])
            for s in merged.failures:
                writer.writerow([s.uid, s.plan, s.category, s.message,
                                 s.http_code, s.status, s.code, f"{s.elapsed_ms:.1f}"])

    mode = f"限时 {args.duration:g}s" if args.duration else (
        f"限次 {args.limit}" if args.limit else "全量单遍")
    cfg = {
        "url": url,
        "file": str(data_path),
        "rows": len(rows),
        "threads": args.threads,
        "mode": mode,
        "started_at": started_at,
    }

    summary_json = out_dir / f"summary_{ts}.json"
    summary_payload = {
        "config": cfg,
        "duration_s": round(elapsed_s, 3),
        "total": merged.total,
        "success": merged.total - merged.failed,
        "failed": merged.failed,
        "success_rate_pct": round((merged.total - merged.failed) / (merged.total or 1) * 100, 2),
        "qps": round(merged.total / elapsed_s, 2),
        "empty_cart": merged.empty_cart,
        "renewal_role_dist": {"main(1)": merged.role_main, "slave(2)": merged.role_slave,
                              "null(老条目/实时扩科加购)": merged.role_null},
        "latency_ms": {
            "avg": round(statistics_mean(merged.latencies), 2),
            "p50": round(percentile(sorted(merged.latencies), 0.50), 2),
            "p90": round(percentile(sorted(merged.latencies), 0.90), 2),
            "p95": round(percentile(sorted(merged.latencies), 0.95), 2),
            "p99": round(percentile(sorted(merged.latencies), 0.99), 2),
            "max": round(max(merged.latencies), 2) if merged.latencies else 0,
        },
        "categories": {k: v for k, v in merged.categories.items() if k != "ok"},
        "top_messages": [
            {"category": c, "message": m, "count": n}
            for (c, m), n in merged.messages.most_common(20)
        ],
        "status_dist": dict(merged.statuses),
        "plan_stats": {
            plan: {"total": cnt, "failed": merged.plan_fail.get(plan, 0)}
            for plan, cnt in merged.plan_total.items()
        },
    }
    summary_json.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + summarize(merged, elapsed_s, cfg, fail_csv, summary_json))

    if merged.total == 0:
        return 2
    if args.fail_on_error and merged.failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
