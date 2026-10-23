#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重发「新链路续班意向预测」MQ，补 ES 花名册列 renewalIntentionPredictLevelResult。

用途（2026-10-23）：
  ES 列被旧链路残留写手 RenewalIntentionPredictDataQueryServiceV2 覆盖为 null，
  用户画像 / 续班列表的「续班意向预测」因此为空，而新链路快照表已有值。
  本脚本按快照表重发新链路 MQ（tag renewal_lift_result，levelOnly=true），触发消费端回写 ES。

数据源：ees_data.predict_level_reason_snapshot（scene=1，取每 (user, subclazz) 最新一条）
发送：经 fuwu ACL 桥调 student-data `FuwuOnsMqProducer#sendNormalMessage`
       topic=renewal_lift_result_topic_prod，tag=renewal_lift_result
       body={userNumber, clazzNumber, subclazzNumber, predictLevel:"1-4", levelOnly:true, predictLevelChanged:false}

安全：默认 DRY-RUN（只打印将要发的内容），必须显式 --confirm 才真发（线上写操作）。

用法：
  # 干跑：某班（拉数 + 打印，不发）
  python3 resend_renewal_predict_es.py --clazz 551189826087448576
  # 真发：某班
  python3 resend_renewal_predict_es.py --clazz 551189826087448576 --confirm
  # 真发：某学员
  python3 resend_renewal_predict_es.py --user 7261731196 --confirm
  # 真发：多个班（文件，每行一个 clazzNumber）
  python3 resend_renewal_predict_es.py --clazz-file /tmp/clazz.txt --confirm
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, "/Users/gaotu/.local/mcp-servers")
import mysql_query as mq  # noqa: E402  (复用 DMS 只读查询通道，走代理注入 Cookie)

import requests  # noqa: E402

ENV = "prod"
TABLE = "ees_data.predict_level_reason_snapshot"
DB = "ees_data"
SCENE = 1

TOPIC = "renewal_lift_result_topic_prod"
TAG = "renewal_lift_result"
BRIDGE = "https://fuwu.baijia.com/bgwApi/student-data/test/acl/compare/service"
PROXY = os.environ.get("AGENT_PROXY_URL", "http://127.0.0.1:8888")
SEND_METHOD = ("com.gaotu.student.data.infrastructure.mq."
               "FuwuOnsMqProducer#sendNormalMessage")


def _sql(scope_where, inner_where, limit):
    sql = (
        "SELECT s.clazz_number, s.user_id, s.subclazz_number, s.predict_level "
        "FROM {t} s JOIN (SELECT user_id, subclazz_number, MAX(record_dt) mdt "
        "FROM {t} WHERE scene={s}{iw} GROUP BY user_id, subclazz_number) t "
        "ON t.user_id=s.user_id AND t.subclazz_number=s.subclazz_number AND t.mdt=s.record_dt "
        "WHERE s.scene={s}{ow} LIMIT {lim}"
    ).format(t=TABLE, s=SCENE, iw=inner_where, ow=scope_where, lim=limit)
    return sql


def fetch_rows(args):
    hits = mq.locate_cluster(TABLE, ENV)
    if not hits:
        raise SystemExit("定位不到集群: %s" % TABLE)
    cid = hits[0]["cluster_id"]

    scope_where = ""
    if args.clazz:
        nums = ",".join(str(c) for c in args.clazz)
        scope_where += " AND s.clazz_number IN (%s)" % nums
    if args.user:
        ids = ",".join(str(u) for u in args.user)
        scope_where += " AND s.user_id IN (%s)" % ids
    # 内层同条件，缩小 join
    inner_where = scope_where.replace("s.", "")

    sql = _sql(scope_where, inner_where, args.limit)
    print("[sql] %s" % sql)
    r = mq.run_query(cid, DB, sql, ENV)
    if r.get("code") != 200:
        raise SystemExit("查询失败: %s" % json.dumps(r, ensure_ascii=False)[:400])
    values = (r.get("data") or {}).get("results", [{}])[0].get("values") or []
    return values


def send_one(clazz, user, subclazz, level, dry_run):
    body = {
        "userNumber": int(user),
        "clazzNumber": int(clazz),
        "subclazzNumber": int(subclazz),
        "predictLevel": str(level),
        "levelOnly": True,
        "predictLevelChanged": False,
    }
    payload = {
        "serviceNameAndMethodName": SEND_METHOD,
        "params": [TOPIC, [TAG], body],
    }
    if dry_run:
        print("[dry] %s %s -> %s" % (user, subclazz, json.dumps(body, ensure_ascii=False)))
        return True
    resp = requests.post(
        BRIDGE, headers={
            "content-type": "application/json",
            "traffic-env": ENV,
            "identification": "microLessonStudent",
        },
        data=json.dumps(payload), proxies={"http": PROXY, "https": PROXY},
        verify=False, timeout=20,
    )
    try:
        j = resp.json()
    except ValueError:
        print("[err] %s %s http=%s non-json" % (user, subclazz, resp.status_code))
        return False
    ok = j.get("code") == 0
    print("[%s] %s %s level=%s %s" % ("ok" if ok else "err", user, subclazz, level,
                                      "" if ok else json.dumps(j, ensure_ascii=False)[:200]))
    return ok


def _ints(csv):
    return [int(x) for x in str(csv).split(",") if x.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clazz", type=_ints, default=None, help="班级号，逗号分隔")
    ap.add_argument("--user", type=_ints, default=None, help="学员ID，逗号分隔")
    ap.add_argument("--clazz-file", default=None, help="文件，每行一个班级号")
    ap.add_argument("--limit", type=int, default=100000)
    ap.add_argument("--sleep", type=float, default=0.0, help="每条之间 sleep 秒")
    ap.add_argument("--confirm", action="store_true", help="确认真发；不加则 dry-run")
    args = ap.parse_args()

    if args.clazz_file:
        nums = []
        with open(args.clazz_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    nums.append(int(line.split()[0]))
        args.clazz = (args.clazz or []) + nums

    if not args.clazz and not args.user:
        raise SystemExit("必须给 --clazz / --user / --clazz-file 之一（防误全量）")

    dry = not args.confirm
    print("[mode] %s" % ("DRY-RUN（不发，只打印）" if dry else "★ 真发（线上写） ★"))

    rows = fetch_rows(args)
    print("[rows] %d" % len(rows))
    ok = err = 0
    for clazz, user, subclazz, level in rows:
        if send_one(clazz, user, subclazz, level, dry):
            ok += 1
        else:
            err += 1
        if args.sleep:
            time.sleep(args.sleep)
    print("[done] ok=%d err=%d" % (ok, err))
    if dry:
        print("提示：加 --confirm 才会真发。")


if __name__ == "__main__":
    main()