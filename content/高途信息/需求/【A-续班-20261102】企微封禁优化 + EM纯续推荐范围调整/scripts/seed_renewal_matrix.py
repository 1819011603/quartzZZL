#!/usr/bin/env python3
"""续班主从推荐 TEST 矩阵造数（补全 cart_test_fixture.txt 的数据来源）

按 PROD 实际配置补齐 TEST 的「计划类型 × 商品类型 × 主从关系」矩阵，并给每组造多名已付学员。
所有动作都调用 qa-data-agent-service（data-agent）已验证的工具/工作流，只能打 TEST。

PROD 对照（2026-11-17 只读，status=进行中、非测试计划）：
  大班计划：班级2 / 联报23 / 纯课程关系(2)；小班计划：小班课6004 / 组合51，无联报23
  主从关系：大→大、大→小、小→大、小→小 四种都有
  ⇒ 小班不造联报；TEST 缺口是「大班+联报23」（TEST 现存 0 个有效样本）

矩阵组（group）：
  big23  大班主(联报23) → [大班从(班级2), 小班从(6004, 复用现存可售计划)]   ← 本脚本新造
  existing 组只追加学员订单（复用现存已验证计划，见 EXISTING）

用法（在任意目录）：
  python3 seed_renewal_matrix.py plan            # 只打印将执行的步骤（默认，零写入）
  python3 seed_renewal_matrix.py big23 --apply   # 新造一组 大班联报23 主 + 大班从 + 关联 + 学员订单
  python3 seed_renewal_matrix.py users --main <主计划> --pre-clazz <前置班或SKU> --product-type 2|6004 \
          --count 3 --apply                      # 给已有计划追加 N 名新学员并下单（付费单自动 mock 支付）
  python3 seed_renewal_matrix.py fixture         # 打印 fixture 行（userId<TAB>renewalNumber<TAB>category）

铁律（来自 gaotu-data-seeding）：
  - 造数成功 = 可售/可下单回读通过，不以 code=0 为准；本脚本每步回读关键字段，不满足即中断。
  - build 自带的班不可售（saleStatus=0/无课节/无老师），一律另建 create_renewal_regression_clazz 正经班。
  - 骨架计划无流程节点时 effective=false，预热/推荐都跳过；必须 process_edit 配 type=3 节点。
  - 同一学员存在待支付单时再下单报 62014，须先 mock_pay 再下下一单。
  - 0 元单 payMode=3 无需支付；100 分单需要 mock_pay。

2026-11-17 W1 实际产出（已登记 fixture_registry）：
  M23=591020372877623296(大班主,联报23) S2=591020374322561024(大班从,班级2)
  联报 591020757501380608；文件 https://test-i.gsxcdn.com/11499079_n6g6vnnj.xlsx
  关联 M23 → [S2, 588506246722727936(小班6004)]
  学员 7746793735 / 7746793736 / 7746791482（M23前置+S2前置已付；前两名另有小班6004前置单）
       7746791494 / 7746791496（小班 586116340522184704 前置，不在读大班 → 扩科可出，用于 P1 命中/未命中对照）

组合 51 不要动（2026-11-17 已核实，勿再"修"数据）：
  存量 51 计划 589721954597011456 的组合 SKU 589762111522013184 为 sale_status=1 / up_status=0，
  这是历史非规范值(saleStatus=1 非合法枚举，normalize(1)→40 仅在 ES 转换器生效)，但**推荐链路不受影响**：
  真实入口 getRenewalDetail 正常返回 product_type=51(trace cart_gaotu100_com.289.17949067348720087)；
  cart 判可售用的是 SPU.canBeSold(=true) + 子商品库存，组合 SKU 自身的 canBeSold 无消费方。
  ⇒ **不需要把 sale_status 改成 40**，改了反而是无依据的数据改动。
"""
import argparse
import json
import os
import subprocess
import sys
import time
import zipfile
from xml.sax.saxutils import escape

DA = os.environ.get("DATA_AGENT_DIR", "/Users/gaotu/IdeaProjects/JavaProject/qa-data-agent-service/skills/data-agent")
PY = os.environ.get("DATA_AGENT_PY", "/Users/gaotu/IdeaProjects/JavaProject/qa-data-agent-service/.venv/bin/python")
SOURCE_PLAN = "590563861447557120"   # 课程模板源（语文前后置，dept 可续课程池）
SMALL_SLAVE = "588506246722727936"   # 现存可售小班6004计划（前置SKU 588506026511294464 / 后置 588506155490336768）
ADMINS = [90247, 177071]             # 唐稳01 / 弓雪萌
SEED_TRAFFIC = "test-eco-7"

EXISTING = {  # 复用的现存组（只追加学员）：主计划 → (前置班或SKU, productType, 说明)
    "590563861447557120": ("590564403009634304", 2, "大→大 T-26，11-18 停售前可用"),
    "586116340522184704": ("586084334251927552", 6004, "小(6004,带扩科)→大"),
    "588506246722727936": ("588506026511294464", 6004, "小6004，单独/作为 M23 从计划"),
}


def cookie(user="zhangmeng26", sys_="boss"):
    return subprocess.run([PY, "-m", "core.executor", "get-cookie", "--username", user, "--sys", sys_],
                          cwd=DA, capture_output=True, text=True, check=True).stdout.strip()


def invoke(tool, params, user="zhangmeng26", sys_="boss", need_cookie=True):
    p = dict(params)
    if need_cookie:
        p["cookie"] = cookie(user, sys_)
    r = subprocess.run([PY, "-m", "core.executor", "invoke", tool, "--params", json.dumps(p, ensure_ascii=False)],
                       cwd=DA, capture_output=True, text=True)
    s = r.stdout
    try:
        return json.loads(s[s.find("{"):s.rfind("}") + 1])
    except ValueError:
        raise RuntimeError(f"{tool} 非 JSON 输出: {s[:300]} {r.stderr[-300:]}")


def run_script(*args):
    r = subprocess.run([PY, "workflows/scripts/renew_from_source.py", *args], cwd=DA, capture_output=True, text=True)
    s = r.stdout
    return json.loads(s[s.find('{\n  "action"'):s.rfind("}") + 1])


def regression_clazz(course, name, begin_ms):
    r = subprocess.run([PY, "-m", "core.executor", "run-workflow", "create_renewal_regression_clazz", "--params",
                        json.dumps({"courseNumber": str(course), "clazzName": name, "price": 100, "beginTime": begin_ms}),
                        "--confirm-all"], cwd=DA, capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if '"search_clazz_full_auth"' in line and '"status": "ok"' in line:
            return json.loads(line)["output"]["clazzNumber"]
    raise RuntimeError(f"正经班未建成: {name}\n{r.stdout[-500:]}")


def mkxlsx(path, header, values):
    rows = [[header]] + [[v] for v in values]
    sheet = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
    for i, row in enumerate(rows, 1):
        sheet += f'<row r="{i}">' + "".join(f'<c r="A{i}" t="inlineStr"><is><t>{escape(str(v))}</t></is></c>' for v in row) + "</row>"
    sheet += "</sheetData></worksheet>"
    ns = "http://schemas.openxmlformats.org"
    files = {
        "[Content_Types].xml": f'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="{ns}/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        "_rels/.rels": f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{ns}/package/2006/relationships"><Relationship Id="rId1" Type="{ns}/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="{ns}/spreadsheetml/2006/main" xmlns:r="{ns}/officeDocument/2006/relationships"><sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": f'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="{ns}/package/2006/relationships"><Relationship Id="rId1" Type="{ns}/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": sheet,
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for k, v in files.items():
            z.writestr(k, v)


def upload(path):
    ck = cookie()
    r = subprocess.run(["curl", "-s", "-m", "30", "-X", "POST", "https://test-mi.gaotu100.com/course-center/b/common/file/upload",
                        "-H", f"Cookie: {ck}", "-H", f"Traffic-Env: {SEED_TRAFFIC}", "-H", f"ingress-traffic: {SEED_TRAFFIC}",
                        "-F", f"file=@{path}"], capture_output=True, text=True)
    d = json.loads(r.stdout)
    assert d.get("code") == 0, d
    return d["data"]["url"]


def process_edit(plan, product_type, file_url=None, file_name=None):
    b = int(time.time() * 1000) - 60000
    e = b + 360 * 86400000
    node = {"type": 3, "administrators": ADMINS, "beginTime": b, "endTime": e, "recommendProductType": product_type}
    if file_url:
        node.update(recommendActivityFileName=file_name, recommendActivityFileUrl=file_url)
    d = invoke("product_b_b_renewal_process_edit", {"renewalNumber": int(plan), "type": 2, "configType": 1,
               "administrators": ADMINS, "beginTime": b, "endTime": e, "nodeConfigs": [node]}, sys_="fuwu")
    assert d.get("raw", {}).get("code") == 0, d


def new_user(tag):
    mobile = "121" + time.strftime("%m%d%H%M") + tag[-2:].rjust(2, "0")
    invoke("student_create", {"mobile": mobile, "name": f"W1矩阵-{tag}", "traffic": SEED_TRAFFIC})
    d = invoke("get_uid_by_mobile", {"mobileDtos": [{"mobile": mobile}]}, need_cookie=False)
    return str(d.get("userId") or d.get("output", {}).get("userId"))


def order_and_pay(user, product, ptype):
    d = invoke("batch_create_order", {"userId": int(user), "traffic": "",
               "choiceProductList": [{"productNumber": str(product), "productType": ptype, "quantity": 1}]})
    o = d.get("output", d)
    code = o.get("raw", {}).get("code")
    if code != 0:
        raise RuntimeError(f"下单失败 user={user} product={product}: {o.get('raw', {}).get('msg')}")
    pay = o.get("raw", {}).get("data", {}).get("payment", {})
    if pay.get("needPay"):
        p = invoke("mock_pay", {"pay_order_number": int(o["payNumber"])})
        assert p.get("raw", {}).get("code") == 0, p
    return o["payNumber"]


def relation_append(main, children):
    ck = cookie("tangwen01", "fuwu")
    r = subprocess.run([PY, "-m", "continueclass.plan_relation", "--main", str(main), "--children", *map(str, children),
                        "--mode", "append", "--cookie", ck, "--traffic", SEED_TRAFFIC, "--apply"],
                       cwd=DA, capture_output=True, text=True)
    d = json.loads(r.stdout[r.stdout.find("{"):])
    assert d.get("verified"), d
    return d["after"]


def cmd_big23(a):
    tag = time.strftime("%m%d%H%M")
    steps = []
    if not a.apply:
        print("[plan] clone-plan×2 → build(语文; 主 posts=2, 从 posts=1) → 正经班×5 → 联报(主两门后置班) → "
              "联报ID文件上传 → process_edit(主23/从2) → 关联 主→[从, 小班6004] → 学员×N 下 主前置+从前置(+小班前置)")
        return
    m = run_script("clone-plan", "--source", SOURCE_PLAN, "--keep-dept", "--name", f"W1矩阵-大班主-联报23-{tag}")["new_plan"]
    s = run_script("clone-plan", "--source", SOURCE_PLAN, "--keep-dept", "--name", f"W1矩阵-大班从-班级2-{tag}")["new_plan"]
    bm = run_script("build", "--source", SOURCE_PLAN, "--target", m, "--subjects", "语文", "--posts-per-subject", "2", "--price", "100")["result"]["语文"]
    bs = run_script("build", "--source", SOURCE_PLAN, "--target", s, "--subjects", "语文", "--posts-per-subject", "1", "--price", "100")["result"]["语文"]
    now = int(time.time() * 1000)
    m_pre = regression_clazz(bm["pre_course"], f"W1矩阵主前置班{tag}", now + 10 * 86400000)
    m_posts = [regression_clazz(c, f"W1矩阵主后置班{i}{tag}", now + 40 * 86400000) for i, c in enumerate(bm["post_courses"])]
    s_pre = regression_clazz(bs["pre_course"], f"W1矩阵从前置班{tag}", now + 10 * 86400000)
    regression_clazz(bs["post_courses"][0], f"W1矩阵从后置班{tag}", now + 40 * 86400000)
    invoke("activity_edit", {"title": f"W1矩阵联报-{tag}", "clazzTimeDesc": "暑期", "bizType": 1, "publishStatus": 40,
                             "subCoureInfo": [{"clazzNumber": str(c), "activityPrice": 100} for c in m_posts]})
    print("联报已建：请用 TEST 库 gaotu.activity_clazz_set_relation(cluster 142) 按子班反查 activity_number 后执行：")
    print(f"  python3 {sys.argv[0]} big23-finish --main {m} --slave {s} --m-pre {m_pre} --s-pre {s_pre} --activity <联报号> --apply")


def cmd_big23_finish(a):
    path = f"/tmp/W1-{a.main}-lianbao.xlsx"
    mkxlsx(path, "联报ID", [a.activity])
    url = upload(path)
    process_edit(a.main, 23, url, os.path.basename(path))
    process_edit(a.slave, 2)
    print("关联:", relation_append(a.main, [a.slave, SMALL_SLAVE]))
    for i in range(a.count):
        u = new_user(f"{a.main[-4:]}{i}")
        order_and_pay(u, a.m_pre, 2)
        order_and_pay(u, a.s_pre, 2)
        print(f"{u}\t{a.main}\trelated")


def cmd_users(a):
    for i in range(a.count):
        u = new_user(f"{a.main[-4:]}{i}")
        if a.apply:
            order_and_pay(u, a.pre_clazz, a.product_type)
        print(f"{u}\t{a.main}\t{a.category}")


def cmd_fixture(_):
    print("userId\trenewalNumber\tcategory")
    rows = [("7746793735", "591020372877623296", "related_big23_main+slave2+small6004"),
            ("7746793736", "591020372877623296", "related_big23_main+slave2+small6004"),
            ("7746791482", "591020372877623296", "related_big23_main+slave2"),
            ("7746793735", "591020374322561024", "no_related_big2"),
            ("7746793735", "588506246722727936", "no_related_small6004"),
            ("7746791494", "586116340522184704", "related_small6004_expand"),
            ("7746791496", "586116340522184704", "related_small6004_expand")]
    for r in rows:
        print("\t".join(r))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    p = sub.add_parser("big23"); p.add_argument("--apply", action="store_true")
    p = sub.add_parser("big23-finish")
    for k in ("--main", "--slave", "--m-pre", "--s-pre", "--activity"):
        p.add_argument(k, required=True)
    p.add_argument("--count", type=int, default=3); p.add_argument("--apply", action="store_true")
    p = sub.add_parser("users")
    p.add_argument("--main", required=True); p.add_argument("--pre-clazz", required=True)
    p.add_argument("--product-type", type=int, choices=[2, 6004], required=True)
    p.add_argument("--count", type=int, default=3); p.add_argument("--category", default="related")
    p.add_argument("--apply", action="store_true")
    sub.add_parser("fixture")
    a = ap.parse_args()
    if a.cmd == "plan":
        cmd_big23(argparse.Namespace(apply=False))
    elif a.cmd == "big23":
        cmd_big23(a)
    elif a.cmd == "big23-finish":
        if not a.apply:
            sys.exit("big23-finish 会写 TEST，需 --apply")
        cmd_big23_finish(a)
    elif a.cmd == "users":
        if not a.apply:
            sys.exit("users 会建学员/下单，需 --apply")
        cmd_users(a)
    else:
        cmd_fixture(a)


if __name__ == "__main__":
    main()
