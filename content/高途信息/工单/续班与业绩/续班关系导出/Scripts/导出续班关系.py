#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导出续班计划的「续班关系」：前置课程 ↔ 后置课程，含课程名称/年级学科学年/部门。

数据链路（2026-10-15 实测）：
  gaotu.renew_master.number  (=OES 页面「续班计划ID」)
    -> gaotu.renew_master_course_relation.pre_course_number   (计划下的前置课程)
    -> course_center.course_relation_map
         WHERE relation_type=1(续报课程) AND isdel=0 AND relation_number=前置课程
         -> course_number = 后置课程
  course_center.course                  课程名称 / department_id(末级部门)
  course_center.course_school_relation  年级(2)/学科(3)/学年(5)
  course_center.course_center_dictionary  grade/subject/year 名称
  部门名称：course-center 部门树 API（medusa）→ /course-center/b/common/department/tree

用法:
  ~/.local/mcp-servers/venv/bin/python 导出续班关系.py <计划ID> [<计划ID> ...] [--out /tmp/x.csv]

说明:
  - 传进来的计划号若在库中不存在，会自动按前 15 位前缀找候选（飞书里粘的 ID 常被
    JS Number 精度截断，末尾两位变 00；例 18124921738300400 -> 18124921738300480）。
    歧义时会打印候选，需人工确认。
  - 依赖 ~/.local/mcp-servers 下的 mysql_query / baijia_invoke 模块（需 baijia-proxy 在跑）。
  - 出 CSV 后用 lark-cli 落飞书表格（见同级 runbook）。
"""
import sys, os, csv, io, json, argparse

sys.path.insert(0, os.path.expanduser("~/.local/mcp-servers"))
import mysql_query as mq          # noqa: E402
import baijia_invoke as bi        # noqa: E402

GAOTU = (71, "gaotu")             # gaotu-center-prod
COURSE = (317, "course_center")   # gaotu-course-prod
PAGE = 900                        # DMS 单次查询上限 1000 行，留余量


def q(cluster_db, sql):
    cid, db = cluster_db
    raw = mq.run_query(cid, db, sql, "prod")
    data = raw.get("data") or {}
    results = data.get("results") or []
    if not results:
        raise RuntimeError("query returned nothing: %s" % (data.get("msg") or raw.get("msg")))
    r = results[0]
    return r.get("columns", []), r.get("values", [])


def rows(cluster_db, sql):
    cols, vals = q(cluster_db, sql)
    return [dict(zip(cols, v)) for v in vals]


def rows_paged(cluster_db, sql_fmt):
    """sql_fmt 需含 %d LIMIT / %d OFFSET 两个占位。"""
    out, off = [], 0
    while True:
        cols, vals = q(cluster_db, sql_fmt % (PAGE, off))
        if not vals:
            break
        out.extend(dict(zip(cols, v)) for v in vals)
        off += len(vals)
        if len(vals) < PAGE:
            break
    return out


def resolve_plan_numbers(given):
    """给定计划号 -> 实际存在的计划号（自动修飞书精度截断）。"""
    in_list = ",".join(str(n) for n in given)
    found = {str(r["number"]): r["name"] for r in
             rows(GAOTU, "SELECT number, name FROM renew_master WHERE number IN (%s)" % in_list)}
    resolved, notes = [], []
    for n in given:
        if str(n) in found:
            resolved.append(str(n))
            continue
        prefix = str(n)[:15]
        cand = rows(GAOTU, "SELECT number, name FROM renew_master WHERE number LIKE '%s%%'" % prefix)
        if len(cand) == 1:
            real = str(cand[0]["number"])
            resolved.append(real)
            notes.append("计划号 %s 不存在，按前缀 %s 唯一匹配到 %s（%s）" % (n, prefix, real, cand[0]["name"]))
        else:
            notes.append("计划号 %s 不存在，前缀 %s 命中 %d 条候选：%s —— 请人工确认"
                         % (n, prefix, len(cand), json.dumps(cand, ensure_ascii=False)))
    for x in notes:
        print("[resolve] " + x, file=sys.stderr)
    return resolved


def fetch_dept_map():
    resp = bi.invoke_http(project="course-center", path="/course-center/b/common/department/tree",
                          route="/course-center", method="GET", traffic_env="prod")
    dept = {}

    def walk(nodes):
        for n in nodes or []:
            dept[str(n.get("number"))] = n.get("name")
            walk(n.get("children"))
    walk(((resp.get("response") or {}).get("data")) or [])
    return dept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plans", nargs="+", help="续班计划ID（number），可多个")
    ap.add_argument("--out", default="/tmp/xuban_relations.csv")
    args = ap.parse_args()

    plans = resolve_plan_numbers([int(x) for x in args.plans])
    if not plans:
        print("没有可用的计划号", file=sys.stderr)
        sys.exit(2)

    plan_name = {str(r["number"]): r["name"] for r in
                 rows(GAOTU, "SELECT number, name FROM renew_master WHERE number IN (%s)" % ",".join(plans))}

    pp = rows(GAOTU, "SELECT renew_master_number, pre_course_number FROM renew_master_course_relation "
                     "WHERE isdel=0 AND renew_master_number IN (%s) "
                     "ORDER BY renew_master_number, pre_course_number" % ",".join(plans))
    pre_set = sorted({str(r["pre_course_number"]) for r in pp})
    if not pre_set:
        print("这些计划下没有前置课程", file=sys.stderr)
        sys.exit(2)

    pairs = rows_paged(COURSE,
        "SELECT relation_number AS pre_course_number, course_number AS post_course_number, calculate_renewal_type "
        "FROM course_relation_map WHERE relation_type=1 AND isdel=0 AND relation_number IN (%s) "
        "ORDER BY relation_number, course_number LIMIT %%d OFFSET %%d" % ",".join(pre_set))

    all_courses = sorted(set(pre_set) | {str(p["post_course_number"]) for p in pairs})

    course = {}
    for i in range(0, len(all_courses), 400):
        part = all_courses[i:i + 400]
        for r in rows(COURSE, "SELECT number, name, department_id FROM course WHERE number IN (%s)" % ",".join(part)):
            course[str(r["number"])] = r

    rel = {}
    for r in rows_paged(COURSE,
        "SELECT course_number, relation_type, relation_number FROM course_school_relation "
        "WHERE isdel=0 AND course_number IN (%s) "
        "ORDER BY course_number, relation_type, relation_number LIMIT %%d OFFSET %%d" % ",".join(all_courses)):
        rel.setdefault(str(r["course_number"]), {}).setdefault(int(r["relation_type"]), []).append(str(r["relation_number"]))

    def dict_map(div):
        return {str(r["dictionary_code"]): r["dictionary_name"] for r in rows(COURSE,
                "SELECT dictionary_code, dictionary_name FROM course_center_dictionary "
                "WHERE dictionary_div='%s'" % div)}

    grade_map, subject_map, year_map = dict_map("courseGrades"), dict_map("courseSubjects"), dict_map("schoolYears")
    dept_map = fetch_dept_map()

    def gsy(cn):
        r = rel.get(cn, {})
        g = [grade_map.get(x, x) for x in r.get(2, [])]
        s = [subject_map.get(x, x) for x in r.get(3, [])]
        y = [year_map.get(x, x) for x in r.get(5, [])]
        return "%s/%s/%s" % ("/".join(g), "/".join(s), "/".join(y))

    def dept_of(cn):
        did = (course.get(cn) or {}).get("department_id")
        return dept_map.get(str(did), str(did) if did else "")

    pair_by_pre = {}
    for p in pairs:
        pair_by_pre.setdefault(str(p["pre_course_number"]), []).append(str(p["post_course_number"]))

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["续班计划ID", "续班计划名称",
                "前置课程ID", "前置课程名称", "前置年级学科学年", "前置部门",
                "后置课程ID", "后置课程名称", "后置年级学科学年", "后置部门"])
    n = 0
    for row in pp:
        plan, pre = str(row["renew_master_number"]), str(row["pre_course_number"])
        for post in pair_by_pre.get(pre, []):
            w.writerow([plan, plan_name.get(plan, ""),
                        pre, (course.get(pre) or {}).get("name", ""), gsy(pre), dept_of(pre),
                        post, (course.get(post) or {}).get("name", ""), gsy(post), dept_of(post)])
            n += 1
    open(args.out, "w").write(buf.getvalue())
    print("plans=%d pre_courses=%d pairs=%d -> %s" % (len(plans), len(pre_set), n, args.out))


if __name__ == "__main__":
    main()
