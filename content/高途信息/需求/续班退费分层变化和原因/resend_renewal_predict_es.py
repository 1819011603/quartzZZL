#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重发「新链路续班意向预测」MQ，补 ES 花名册列 renewalIntentionPredictLevelResult。

数据源：ees_data.predict_level_reason_snapshot（scene=1，keyset 分页拉全量；DMS 单次最多 1000 行）
  每 (user,subclazz) 取最新 record_dt，再每 (user,clazz) 取最新一条（消费端按 (user,clazz) 整班写、忽略 subclazz）
发送：经 fuwu ACL 桥调 student-data FuwuOnsMqProducer#sendNormalMessage
  topic=renewal_lift_result_topic_prod，tag=renewal_lift_result
  body={userNumber, clazzNumber, subclazzNumber, predictLevel, levelOnly:true, predictLevelChanged:false}
  ⚠️ 三个 ID 必须是【数字】：实测消费端不吃字符串 ID（会被丢，不写 ES）。

并发：--class-workers 个班并行；每个班内 --send-workers 条并发。
记录：每个班的发送结果单独统计（total/ok/err），结束打印逐班汇总表，并可 --out 落文件。

安全：默认 DRY-RUN，必须 --confirm 才真发。

用法：
  python3 resend_renewal_predict_es.py --clazz 551189826087448576                 # 干跑
  python3 resend_renewal_predict_es.py --user 7261731196 --confirm
  python3 resend_renewal_predict_es.py --clazz-file /tmp/batch20.txt --confirm --class-workers 4 --send-workers 12
"""
import argparse
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "/Users/gaotu/.local/mcp-servers")
import mysql_query as mq  # noqa: E402

import requests  # noqa: E402

ENV = "prod"
TABLE = "ees_data.predict_level_reason_snapshot"
DB = "ees_data"
SCENE = 1
PAGE = 1000  # DMS 单次返回上限

TOPIC = "renewal_lift_result_topic_prod"
TAG = "renewal_lift_result"
BRIDGE = "https://fuwu.baijia.com/bgwApi/student-data/test/acl/compare/service"
PROXY = os.environ.get("AGENT_PROXY_URL", "http://127.0.0.1:8888")
SEND_METHOD = ("com.gaotu.student.data.infrastructure.mq."
               "FuwuOnsMqProducer#sendNormalMessage")

_print_lock = threading.Lock()


def _log(*a):
    with _print_lock:
        print(*a)


def locate_cid():
    hits = mq.locate_cluster(TABLE, ENV)
    if not hits:
        raise SystemExit("定位不到集群: %s" % TABLE)
    return hits[0]["cluster_id"]


def fetch_by_clazz(cid, clazz):
    """拉某班全量（keyset 分页），返回 [(clazz,user,subclazz,level,dt)]，按 (user,clazz) 去重取最新。"""
    rows = []
    last = (0, 0, "")
    while True:
        sql = (
            "SELECT clazz_number, user_id, subclazz_number, predict_level, record_dt "
            "FROM {t} WHERE scene={s} AND clazz_number={c} "
            "AND (user_id, subclazz_number, record_dt) > ({lu}, {ls}, '{ld}') "
            "ORDER BY user_id, subclazz_number, record_dt LIMIT {pg}"
        ).format(t=TABLE, s=SCENE, c=clazz, lu=last[0], ls=last[1], ld=last[2], pg=PAGE)
        r = mq.run_query(cid, DB, sql, ENV)
        if r.get("code") != 200:
            raise RuntimeError("查询失败: %s" % json.dumps(r, ensure_ascii=False)[:200])
        vals = (r.get("data") or {}).get("results", [{}])[0].get("values") or []
        if not vals:
            break
        rows.extend(vals)
        last = (vals[-1][1], vals[-1][2], vals[-1][4])
        if len(vals) < PAGE:
            break
    by_us = {}
    for c, u, sc, lv, dt in rows:
        k = (str(u), str(sc))
        if k not in by_us or str(dt) > by_us[k][4]:
            by_us[k] = (str(c), str(u), str(sc), str(lv), str(dt))
    by_uc = {}
    for v in by_us.values():
        k = (v[1], v[0])
        if k not in by_uc or v[4] > by_uc[k][4]:
            by_uc[k] = v
    return list(by_uc.values())


def send_one(row, dry_run, retries):
    clazz, user, subclazz, level, _dt = row
    body = {
        "userNumber": int(user),        # 必须是数字，字符串消费端不认
        "clazzNumber": int(clazz),
        "subclazzNumber": int(subclazz),
        "predictLevel": str(level),
        "levelOnly": True,
        "predictLevelChanged": False,
    }
    payload = {"serviceNameAndMethodName": SEND_METHOD, "params": [TOPIC, [TAG], body]}
    if dry_run:
        return True
    for _ in range(retries + 1):
        try:
            j = requests.post(
                BRIDGE,
                headers={"content-type": "application/json", "traffic-env": ENV,
                         "identification": "microLessonStudent"},
                data=json.dumps(payload), proxies={"http": PROXY, "https": PROXY},
                verify=False, timeout=20,
            ).json()
            if j.get("code") == 0:
                return True
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.3)
    return False


def process_class(cid, clazz, args, dry):
    """处理一个班：拉数 + 并发发送 + 独立统计。返回 dict。"""
    t0 = time.time()
    try:
        rows = fetch_by_clazz(cid, clazz)
    except Exception as e:  # noqa: BLE001
        return {"clazz": clazz, "total": 0, "ok": 0, "err": 0, "sec": 0, "msg": "fetch失败:%s" % e}
    ok = err = 0
    with ThreadPoolExecutor(max_workers=args.send_workers) as ex:
        futs = [ex.submit(send_one, r, dry, args.retries) for r in rows]
        for f in as_completed(futs):
            if f.result():
                ok += 1
            else:
                err += 1
    res = {"clazz": clazz, "total": len(rows), "ok": ok, "err": err,
           "sec": round(time.time() - t0, 1), "msg": ""}
    _log("[class %s] total=%d ok=%d err=%d %.1fs" % (clazz, len(rows), ok, err, res["sec"]))
    return res


def _ints(csv):
    return [int(x) for x in str(csv).split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clazz", type=_ints, default=None, help="班级号，逗号分隔")
    ap.add_argument("--user", type=_ints, default=None, help="学员ID，逗号分隔")
    ap.add_argument("--clazz-file", default=None, help="文件，每行一个班级号")
    ap.add_argument("--class-workers", type=int, default=4, help="并行处理的班级数")
    ap.add_argument("--send-workers", type=int, default=12, help="每班内并发发送数")
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--out", default="/tmp/resend_predict_result.tsv", help="逐班结果落盘")
    ap.add_argument("--confirm", action="store_true")
    args = ap.parse_args()

    classes = []
    if args.clazz:
        classes += args.clazz
    if args.clazz_file:
        with open(args.clazz_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    classes.append(int(line.split()[0]))

    cid = locate_cid()
    dry = not args.confirm
    print("[mode] %s | classes=%d | class-workers=%d send-workers=%d" % (
        "DRY-RUN" if dry else "★真发★", len(classes), args.class_workers, args.send_workers))

    results = []
    t0 = time.time()
    if classes:
        with ThreadPoolExecutor(max_workers=args.class_workers) as ex:
            futs = [ex.submit(process_class, cid, c, args, dry) for c in classes]
            for f in as_completed(futs):
                results.append(f.result())
    else:
        # 单学员模式：一条用户记录，作为「一个班」统计
        if not args.user:
            raise SystemExit("必须给 --clazz / --user / --clazz-file 之一")
        sql = ("SELECT clazz_number,user_id,subclazz_number,predict_level,record_dt FROM %s "
               "WHERE scene=%d AND user_id IN (%s)" % (TABLE, SCENE, ",".join(str(u) for u in args.user)))
        r = mq.run_query(cid, DB, sql, ENV)
        vals = (r.get("data") or {}).get("results", [{}])[0].get("values") or []
        ok = err = 0
        for c, u, sc, lv, dt in vals:
            if send_one((str(c), str(u), str(sc), str(lv), str(dt)), dry, args.retries):
                ok += 1
            else:
                err += 1
        results.append({"clazz": "user:%s" % ",".join(map(str, args.user)),
                        "total": len(vals), "ok": ok, "err": err, "sec": 0, "msg": ""})

    results.sort(key=lambda x: str(x["clazz"]))
    tot = sum(r["total"] for r in results)
    tok = sum(r["ok"] for r in results)
    terr = sum(r["err"] for r in results)
    print("\n==== 逐班结果 ====")
    for r in results:
        print("%-22s total=%-6d ok=%-6d err=%-4d %ss %s" % (
            r["clazz"], r["total"], r["ok"], r["err"], r["sec"], r["msg"]))
    print("==== 合计: 班=%d total=%d ok=%d err=%d 用时%.0fs ====" % (
        len(results), tot, tok, terr, time.time() - t0))
    try:
        with open(args.out, "w") as f:
            f.write("clazz\ttotal\tok\terr\tsec\tmsg\n")
            for r in results:
                f.write("%s\t%d\t%d\t%d\t%s\t%s\n" % (
                    r["clazz"], r["total"], r["ok"], r["err"], r["sec"], r["msg"]))
        print("[out] %s" % args.out)
    except Exception as e:  # noqa: BLE001
        print("[out] 写文件失败: %s" % e)


if __name__ == "__main__":
    main()