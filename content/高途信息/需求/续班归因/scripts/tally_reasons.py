#!/usr/bin/env python3
"""对 harvest_job_logs.py 的产物做分类计数，回答「班级被哪一层过滤了」。

自检：各原因班级数之和必须等于任务表当天行数，对不上说明还有没覆盖到的分支。
    SELECT COUNT(*) FROM ees_data.ai_renewal_attribution_follow_clazz_task
    WHERE create_time >= '<date> 00:00:00';

用法:
    python3 tally_reasons.py [--in /tmp/job_lines.json] [--expect 2621]
"""
import argparse, collections, json, re

# 按 handleClazzTask 的短路顺序排列
REASONS = [
    ("① inScope: is_renew_user_clazz=0", r"not renew user clazz, clazzNumber: (\d+)"),
    ("① inScope: 创建时间早于阈值",        r"created too early, clazzNumber: (\d+)"),
    ("① inScope: 班级查不到",              r"inScope \| clazz not found, clazzNumber: (\d+)"),
    ("① inScope: 课程查不到",              r"course not found, clazzNumber: (\d+)"),
    ("② needHandle 过滤链",                r"rejected by \w+, tag: \w+, clazzNumber: (\d+)"),
    ("③ 窗口: 班级已结课",                 r"clazz ended, clazzNumber: (\d+)"),
    ("④ 窗口: 无后置课程",                 r"no post course, clazzNumber: (\d+)"),
    ("⑤ 窗口: 正式续班未开始",             r"formal renewal not started, clazzNumber: (\d+)"),
    ("⑥ 抢锁失败(上一轮还在跑)",           r"clazz is running, skip, clazzNumber: (\d+)"),
]

ap = argparse.ArgumentParser()
ap.add_argument("--in", dest="inp", default="/tmp/job_lines.json")
ap.add_argument("--expect", type=int, help="任务表当天行数，用于自检")
a = ap.parse_args()

msgs = json.load(open(a.inp))
print(f"输入 {len(msgs)} 行\n")

total, seen = 0, set()
for label, pat in REASONS:
    ids = set()
    for s in msgs:
        ids.update(re.findall(pat, s))
    if ids:
        print(f"  {label:34} {len(ids):6}")
        total += len(ids)
        seen |= ids

# 实际投递出去的
disp = re.compile(r"dispatched, clazzNumber: (\d+), userCount: (\d+)")
d = {}
for s in msgs:
    for c, u in disp.findall(s):
        d[c] = int(u)
print(f"\n  {'✅ 实际投递班级':34} {len(d):6}   投递学员数 {sum(d.values())}")

print(f"\n  {'合计(被拦截)':34} {total:6}")
if a.expect:
    diff = a.expect - total - len(d)
    flag = "✅ 完全吻合" if diff == 0 else f"⚠️ 差 {diff} 个班没被解释"
    print(f"  {'任务表当天行数':34} {a.expect:6}   {flag}")

# needHandle 细分
byf, byt = collections.Counter(), collections.Counter()
for s in msgs:
    mm = re.search(r"rejected by (\w+), tag: (\w+), clazzNumber: \d+", s)
    if mm:
        byf[mm.group(1)] += 1
        byt[mm.group(2)] += 1
if byf:
    print("\n-- ② needHandle 细分 --")
    for k, v in byf.most_common():
        print(f"  {k:38} {v}")
    for k, v in byt.most_common():
        print(f"  tag: {k:44} {v}")
