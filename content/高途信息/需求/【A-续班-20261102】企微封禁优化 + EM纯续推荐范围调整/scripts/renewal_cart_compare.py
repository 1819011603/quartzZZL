#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
续班 C 端推荐接口「实时 vs 预热(回退态读)」对比采集/比对脚本（功能回归用，非压测）。

配合 renewal_cart_runner.py 使用：runner 做单态巡检，本脚本做双态对比。

用法：
  # 第 1 步：预热（人工/acl 桥完成，脚本不管 Apollo，见 README 第 6 节）
  # 第 2 步：baseline 采集（要求 renewal.recommend.v2.enabled=false，老链路读缓存/老实时）
  python3 renewal_cart_compare.py --phase baseline --pod 10.218.238.179 --traffic-env test-eco-8
  # 第 3 步：v2 采集（要求 renewal.recommend.v2.enabled=true，V2 实时）
  python3 renewal_cart_compare.py --phase v2 --pod 10.218.238.179 --traffic-env test-eco-8
  # 第 4 步：比对
  python3 renewal_cart_compare.py --diff compare_baseline_xxx.json compare_v2_xxx.json

开关检测（只读不翻）：采集前经 acl 桥调 RenewalV2Service#isRecommendV2Enabled /
#isPreheatV2Enabled 取 pod 运行时态；与阶段期望不符则中止（--skip-switch-check 可跳过，
  仅建议排障时用）。翻开关仍走 Apollo 后台人工操作。

比对规则（owner 口径 2026-11-16）：
  规则一 no_related（无主从关联计划样本）：与基线保持一致 —— productSkuNumber
    集合(含重复计数)应完全一致；
  规则二 related（有关联计划样本）：验证实时与预热一致 —— 纯续子集
    （recommendType∈{null,1}）按 (productSkuNumber, renewalRole) 多重集比对；
    V2 实时含扩科/加购，整体集合不等价是预期，只比纯续子集。
"""

import argparse
import collections
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

POD_HOST_HEADER = "cart.gaotu100.com"
BRIDGE_PATH = "/test/acl/compare/service"
API_PATH = "/web/renewal/cart"
BRIDGE_RECOMMEND = "com.gaotu.renewal.RenewalV2Service#isRecommendV2Enabled"
BRIDGE_PREHEAT = "com.gaotu.renewal.RenewalV2Service#isPreheatV2Enabled"
PHASE_EXPECT_RECOMMEND_V2 = {"baseline": False, "v2": True}

ENTRY_FIELDS = ("sku", "role", "rtype", "ptype", "before", "sign", "grade")


def load_fixture(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        if "category" not in header:
            raise SystemExit(f"fixture 需三列(userId/renewalNumber/category): {path}")
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                raise SystemExit(f"fixture 行不足三列(勿用 Excel 另存, ID 会变科学计数法): {line}")
            uid, plan, cat = parts[0].strip(), parts[1].strip(), parts[2].strip()
            int(uid)
            int(plan)
            rows.append({"uid": uid, "plan": plan, "category": cat})
    return rows


def bridge_call(pod, name_method, timeout=15):
    url = f"http://{pod}:28688{BRIDGE_PATH}"
    body = {"serviceNameAndMethodName": name_method, "params": []}
    headers = {"traffic-env": args.traffic_env, "host": POD_HOST_HEADER,
               "Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def extract_bridge_bool(payload):
    if not isinstance(payload, dict):
        return None
    for key in ("result", "value"):
        if isinstance(payload.get(key), bool):
            return payload[key]
    data = payload.get("data")
    if isinstance(data, bool):
        return data
    if isinstance(data, dict):
        for sub in ("result", "value"):
            if isinstance(data.get(sub), bool):
                return data[sub]
        for val in data.values():
            if isinstance(val, bool):
                return val
    return None


def check_switches(pod):
    state = {}
    for label, method in (("recommend_v2", BRIDGE_RECOMMEND), ("preheat_v2", BRIDGE_PREHEAT)):
        payload = bridge_call(pod, method)
        val = extract_bridge_bool(payload)
        state[label] = val
        state[f"{label}_raw"] = json.dumps(payload, ensure_ascii=False)[:300]
    return state


def fetch_sample(pod, row, timeout):
    url = f"http://{pod}:28688{API_PATH}"
    params = {"appointUserId": row["uid"], "renewalNumber": row["plan"]}
    headers = {"traffic-env": args.traffic_env, "host": POD_HOST_HEADER}
    rec = dict(row)
    rec["ts"] = int(time.time() * 1000)
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        rec.update(ok=False, kind="http_exception", err=str(e)[:200])
        return rec
    rec["elapsed_ms"] = int(resp.elapsed.total_seconds() * 1000)
    rec["trace_id"] = resp.headers.get("GAPM-TraceID", "")
    rec["http_code"] = resp.status_code
    if resp.status_code != 200:
        rec.update(ok=False, kind="http_error", err=resp.text[:200])
        return rec
    try:
        payload = resp.json()
    except ValueError:
        rec.update(ok=False, kind="bad_json", err=resp.text[:200])
        return rec
    status = payload.get("status")
    code = payload.get("code")
    rec["status"], rec["code"] = status, code
    data = payload.get("data")
    if status != 0 or code != 0:
        rec.update(ok=False, kind="biz_error", err=str(payload.get("err"))[:200])
        return rec
    if not isinstance(data, dict) or "gradeClazzList" not in data:
        rec.update(ok=True, kind="success_empty", entries=[])
        return rec
    groups = data.get("gradeClazzList")
    if not isinstance(groups, list):
        rec.update(ok=False, kind="bad_structure", err="gradeClazzList 非数组")
        return rec
    entries = []
    for g in groups:
        grade = g.get("grade") if isinstance(g, dict) else None
        for dto in (g.get("clazzDetailDTOList") or [] if isinstance(g, dict) else []):
            if not isinstance(dto, dict):
                continue
            entries.append({
                "sku": dto.get("productSkuNumber"),
                "role": dto.get("renewalRole"),
                "rtype": dto.get("recommendType"),
                "ptype": dto.get("productType"),
                "before": dto.get("beforeCourseNumber"),
                "sign": dto.get("signUp"),
                "grade": grade,
            })
    rec.update(ok=True, kind="ok", entries=entries)
    return rec


def collect(args, rows):
    switches = check_switches(args.pod)
    expect = PHASE_EXPECT_RECOMMEND_V2[args.phase]
    got = switches.get("recommend_v2")
    if not args.skip_switch_check and got != expect:
        print(f"[中止] 阶段 {args.phase} 要求 recommend.v2={expect}, 桥实测={got}")
        print(f"  raw: {switches.get('recommend_v2_raw')}")
        print("  请先到 Apollo 后台调整 renewal.recommend.v2.enabled 并发布, 再重跑; 排障可用 --skip-switch-check")
        sys.exit(2)
    print(f"[开关] recommend_v2={got} preheat_v2={switches.get('preheat_v2')} (阶段期望 recommend_v2={expect})")

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        records = list(pool.map(lambda r: fetch_sample(args.pod, r, args.timeout), rows))

    ok_n = sum(1 for r in records if r.get("ok"))
    empty_n = sum(1 for r in records if r.get("kind") == "success_empty")
    err_n = sum(1 for r in records if not r.get("ok"))
    role_dist = collections.Counter()
    for r in records:
        for e in r.get("entries", []):
            role_dist[str(e.get("role"))] += 1
    out = {
        "meta": {
            "phase": args.phase, "pod": args.pod, "traffic_env": args.traffic_env,
            "collected_at": time.strftime("%Y-%m-%d %H:%M:%S"), "switches": switches,
            "fixture": args.file, "total": len(records), "ok": ok_n,
            "success_empty": empty_n, "error": err_n, "role_dist": dict(role_dist),
        },
        "samples": records,
    }
    fname = f"compare_{args.phase}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"[采集] total={len(records)} ok={ok_n} empty={empty_n} error={err_n} role_dist={dict(role_dist)}")
    print(f"[落盘] {fname}")


def is_pure(entry):
    rtype = entry.get("rtype")
    return rtype is None or rtype == 1


def sample_key(rec):
    return (rec["uid"], rec["plan"])


def diff(args):
    with open(args.baseline, encoding="utf-8") as f:
        base = json.load(f)
    with open(args.v2file, encoding="utf-8") as f:
        v2 = json.load(f)
    base_map = {sample_key(r): r for r in base["samples"]}
    v2_map = {sample_key(r): r for r in v2["samples"]}
    if set(base_map) != set(v2_map):
        print(f"[警告] 两阶段样本集不一致: base={len(base_map)} v2={len(v2_map)}")
    report = {"rule1": [], "rule2": [], "meta": {
        "baseline": args.baseline, "v2": args.v2file,
        "base_meta": base["meta"], "v2_meta": v2["meta"]}}
    r1_pass = r2_pass = 0
    for key in sorted(base_map):
        b, v = base_map[key], v2_map.get(key)
        if v is None:
            continue
        uid, plan, cat = key[0], key[1], b["category"]
        if not b.get("ok") or not v.get("ok"):
            status = "phase_error"
            detail = f"base.kind={b.get('kind')}/{b.get('err','')} v2.kind={v.get('kind')}/{v.get('err','')}"
            target = report["rule2"] if cat == "related" else report["rule1"]
            target.append({"uid": uid, "plan": plan, "verdict": status, "detail": detail})
            continue
        b_entries, v_entries = b.get("entries", []), v.get("entries", [])
        if cat == "no_related":
            bc = collections.Counter(e["sku"] for e in b_entries)
            vc = collections.Counter(e["sku"] for e in v_entries)
            only_b, only_v = bc - vc, vc - bc
            verdict = "一致" if not only_b and not only_v else "不一致"
            if verdict == "一致":
                r1_pass += 1
            report["rule1"].append({
                "uid": uid, "plan": plan, "verdict": verdict,
                "base_skus": dict(bc), "v2_skus": dict(vc),
                "only_in_baseline": dict(only_b), "only_in_v2": dict(only_v)})
        else:
            bp = [e for e in b_entries if is_pure(e)]
            vp = [e for e in v_entries if is_pure(e)]
            # 实时展示条目不带 renewalRole(只有预热写缓存才标), 纯续等价性按 sku 多重集比对;
            # role 仅在基线侧做覆盖检查(合并值应同时含 role=1 主纯续与 role=2 从纯续)
            bc = collections.Counter(e["sku"] for e in bp)
            vc = collections.Counter(e["sku"] for e in vp)
            only_b, only_v = bc - vc, vc - bc
            verdict = "一致" if not only_b and not only_v else "不一致"
            note = ""
            if verdict == "一致":
                r2_pass += 1
            elif not bp and vp:
                note = "预期差异候选: baseline纯续为空且v2非空(纯从学员, 预热只处理A计划学员)"
            b_roles = collections.Counter(str(e["role"]) for e in bp)
            role_ok = "1" in b_roles and "2" in b_roles
            report["rule2"].append({
                "uid": uid, "plan": plan, "verdict": verdict,
                "note": note + ("" if role_ok or not bp else "; 基线role覆盖异常: 应同时含role=1与role=2"),
                "base_pure": {f"{k}": n for k, n in bc.items()},
                "v2_pure": {f"{k}": n for k, n in vc.items()},
                "only_in_baseline": dict(only_b), "only_in_v2": dict(only_v),
                "base_pure_role_dist": dict(b_roles),
                "base_role_dist": dict(collections.Counter(str(e["role"]) for e in b_entries)),
                "v2_role_dist": dict(collections.Counter(str(e["role"]) for e in v_entries))})

    r1 = [x for x in report["rule1"]]
    r2 = [x for x in report["rule2"]]
    print("=" * 72)
    print(f"规则一 no_related（与基线一致）: {r1_pass}/{len(r1)} 一致")
    for x in r1:
        if x["verdict"] != "一致":
            print(f"  [不一致] uid={x['uid']} plan={x['plan']}")
            print(f"    only_in_baseline={x.get('only_in_baseline')} only_in_v2={x.get('only_in_v2')}")
    print(f"规则二 related（实时=预热, 纯续子集 sku+role）: {r2_pass}/{len(r2)} 一致")
    for x in r2:
        if x["verdict"] != "一致":
            print(f"  [{x['verdict']}] uid={x['uid']} plan={x['plan']} {x.get('note','')}")
            print(f"    only_in_baseline={x.get('only_in_baseline')} only_in_v2={x.get('only_in_v2')}")
    fname = f"compare_diff_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print(f"[落盘] {fname}")
    bad = sum(1 for x in r1 + r2 if x["verdict"] == "不一致")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phase", choices=["baseline", "v2"], help="采集阶段")
    ap.add_argument("--pod", help="目标 pod IP（直连 28688）")
    ap.add_argument("--traffic-env", default="test-eco-8", help="泳道头, 默认 test-eco-8")
    ap.add_argument("--file", default="cart_test_fixture.txt", help="fixture(三列: userId/renewalNumber/category)")
    ap.add_argument("--threads", type=int, default=4, help="采集并发(功能采集, 勿调高)")
    ap.add_argument("--timeout", type=int, default=20, help="单请求超时秒")
    ap.add_argument("--skip-switch-check", action="store_true", help="跳过开关检测(排障用)")
    ap.add_argument("--diff", nargs=2, metavar=("BASELINE_JSON", "V2_JSON"), help="比对两阶段结果")
    args = ap.parse_args()

    if args.diff:
        args.baseline, args.v2file = args.diff
        diff(args)
    elif args.phase and args.pod:
        rows = load_fixture(args.file)
        cats = collections.Counter(r["category"] for r in rows)
        print(f"[fixture] {args.file}: {len(rows)} 行 {dict(cats)}")
        collect(args, rows)
    else:
        ap.error("需要 --phase+--pod 采集, 或 --diff BASELINE_JSON V2_JSON")
