#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给「续班&退费的分层变化和原因」冒烟造【测试环境自造】mock 数据（续班 + 退费）。

要求：辅导班老师必须是 唐稳01，且挂在【续班】班级下，页面才点得进去。
选用真实对象：
  班级   574882679202260992 「续班归因-正经前置班-0820」（续班计划前置班，课时 2027-09-15，未超期）
  辅导班 35930168009949440 「唐稳01YYTS321002」，带班老师 唐稳01（assistantNumber 7405394941575616）
  学员   该辅导班花名册里的真实在读学员：归因二/四/六/七/九（user_id 7478102067/72/77/79/80）

覆盖场景：
  【续班 scene=1】
  - 主样本 归因二 7478102067：20261007~20261010 依次 A→B→C→D（每天 6 因子），供趋势图/原因卡/hover
  - G0002 六种下降组合：20261010→20261011
  - A0004 无变化不落库：900000008 20261010=B→20261011=B
  - G0001 B降C 文案：用真实学员 归因九 7478102080（B→C）
  【退费 scene=2】
  - 主样本 归因二 7478102067：20261007~20261010 依次 低→中→中高→高（每天 6 因子），供退费趋势图/原因卡
脚本幂等（先 DELETE 再 INSERT）。
"""
import json
import pymysql

CONF = dict(host="gaotu-polar-test02.rwlb.rds.aliyuncs.com", port=3306,
            user="gaotu_test_rw", password="gaotu@test2020", database="ees_data",
            charset="utf8mb4", autocommit=True)

CLAZZ = 574882679202260992
SUBCLAZZ = 35930168009949440
TYPE_RENEW = "renew"
TYPE_REFUND = "refund"

# ---- 续班 ----
MAIN = 7478102067
MAIN_SEQ = [("20261007", "A"), ("20261008", "B"), ("20261009", "C"), ("20261010", "D")]
D1, D2 = "20261010", "20261011"
COMBOS = {
    7478102072: ("A", "B"),   # 归因四 A->B
    900000005: ("A", "C"),   # 归因六已续班超期被过滤，用 mock 补 A->C
    7478102079: ("A", "D"),   # 归因七 A->D
    7478102080: ("B", "C"),   # 归因九 B->C（G0001 用）
    900000006: ("B", "D"),
    900000007: ("C", "D"),
    900000008: ("B", "B"),   # 无变化（A0004 用）
}

# ---- 退费 ----
REFUND_MAIN = 7478102067
REFUND_SEQ = [("20261007", "低"), ("20261008", "中"), ("20261009", "中高"), ("20261010", "高")]

ALL_USERS = list({MAIN, REFUND_MAIN} | set(COMBOS.keys()))


def factors6(day, layer):
    """续班主样本：6 条因子，idx0-2 负向、idx3-5 正向。"""
    off = {"A": 0, "B": 10, "C": 30, "D": 45}[layer]
    return json.dumps([
        {"idx": 0, "factor": "进班前近期题目作答正确率", "direction": "负向影响", "actionable": "可干预",
         "reason": f"学生【作答正确率{off}%】低于【班级中位数73.33%】，基础薄弱致续班意愿低",
         "action": "私信家长：孩子正确率偏低需补基础，今晚我单独带他订正错题，请督促完成。", "logs": "q50"},
        {"idx": 1, "factor": "近7日累计微信亲密度", "direction": "负向影响", "actionable": "可干预",
         "reason": f"学生【微信亲密度0.0{off//10}】低于【班级中位数1.14】，互动薄弱致续班意向低。",
         "action": "微信私聊孩子，夸其近期进步，拉近关系破冰。", "logs": "q50"},
        {"idx": 2, "factor": "收获学币数", "direction": "负向影响", "actionable": "不可干预·只说明",
         "reason": f"学生【收获学币{9000 - off*30}】低于【班级中位数23889】，学习获得感弱",
         "action": "", "logs": "SHAP"},
        {"idx": 3, "factor": "历史课节有效听课率", "direction": "正向影响", "actionable": "可干预",
         "reason": f"学生【课节数{230 - off}】高于【班级中位数196.66】，学习投入度高。",
         "action": "夸他听课超勤，肯定这习惯，让他趁热打铁续班。", "logs": "q50"},
        {"idx": 4, "factor": "正价课累计支付金额", "direction": "正向影响", "actionable": "不可干预·只说明",
         "reason": f"学生【正价课金额{17000 + off*10}元】高于【班级中位数15280.47元】，付费意愿强。",
         "action": "", "logs": "q50"},
        {"idx": 5, "factor": "无历史退费记录", "direction": "正向影响", "actionable": "不可干预·只说明",
         "reason": "无历史退费记录", "action": "", "logs": "SHAP"},
    ], ensure_ascii=False)


def factors2(layer):
    return json.dumps([
        {"idx": 0, "factor": "近7天出勤率", "direction": "负向影响", "actionable": "可干预",
         "reason": f"近7天出勤率{50 - 5 * (ord(layer) - 65)}%，低于班级50分位",
         "action": "建议与家长沟通到课情况", "logs": "q50"},
        {"idx": 1, "factor": "课堂互动次数", "direction": "正向影响", "actionable": "可干预",
         "reason": "课堂互动次数高于班级50分位", "action": "建议保持课堂互动引导", "logs": "q50"},
    ], ensure_ascii=False)


def factors_refund(layer):
    """退费主样本：6 条因子，idx0-2 负向、idx3-5 正向；分层越高退费风险越大。"""
    sev = {"低": 0, "中": 1, "中高": 2, "高": 3}[layer]
    attend = [88, 70, 55, 40][sev]
    consult = [0, 1, 2, 3][sev]
    homework = [95, 80, 60, 35][sev]
    return json.dumps([
        {"idx": 0, "factor": "近7天出勤率", "direction": "负向影响", "actionable": "可干预",
         "reason": f"近7天出勤率{attend}%，{'接近' if sev == 0 else '明显低于'}班级50分位",
         "action": "建议尽快与家长沟通到课情况", "logs": "q50"},
        {"idx": 1, "factor": "近30天售后咨询次数", "direction": "负向影响", "actionable": "可干预",
         "reason": f"近30天售后咨询{consult}次，{'未涉及' if consult == 0 else '涉及课程进度问题'}",
         "action": "建议主动回访说明课程安排", "logs": "q50"},
        {"idx": 2, "factor": "作业完成率", "direction": "负向影响", "actionable": "不可干预·只说明",
         "reason": f"作业完成率{homework}%，{'高于' if sev == 0 else '低于'}班级50分位",
         "action": "", "logs": "SHAP"},
        {"idx": 3, "factor": "课堂互动次数", "direction": "正向影响", "actionable": "可干预",
         "reason": "课堂互动次数高于班级50分位" if sev < 2 else "课堂互动次数接近班级50分位",
         "action": "建议加强课堂互动引导", "logs": "q50"},
        {"idx": 4, "factor": "无历史退费记录", "direction": "正向影响", "actionable": "不可干预·只说明",
         "reason": "无历史退费记录", "action": "", "logs": "SHAP"},
        {"idx": 5, "factor": "入学时长", "direction": "正向影响", "actionable": "不可干预·只说明",
         "reason": "入学时长较长，退费风险基线偏低", "action": "", "logs": "SHAP"},
    ], ensure_ascii=False)


def main():
    conn = pymysql.connect(**CONF)
    try:
        with conn.cursor() as cur:
            # 清旧的本次 mock（明细 + 快照，含旧班级下的 mock）
            cur.execute("DELETE FROM predict_level_reason_snapshot WHERE user_id BETWEEN 900000001 AND 900000099")
            cur.execute("DELETE FROM predict_level_reason_snapshot WHERE user_id IN (%s,%s,%s,%s,%s)",
                        (MAIN, 7478102072, 7478102077, 7478102079, 7478102080))
            cur.execute("DELETE FROM ai_predict_level_reason_detail WHERE user_number BETWEEN 900000001 AND 900000099")
            cur.execute("DELETE FROM ai_predict_level_reason_detail WHERE user_number IN (%s,%s,%s,%s,%s)",
                        (MAIN, 7478102072, 7478102077, 7478102079, 7478102080))

            # ---- 续班 scene=1 ----
            n = 0
            for dt, layer in MAIN_SEQ:
                cur.execute("INSERT INTO ai_predict_level_reason_detail(user_number,clazz_number,subclazz_number,layer,factors,type,dt) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                            (MAIN, CLAZZ, SUBCLAZZ, layer, factors6(dt, layer), TYPE_RENEW, dt))
                n += 1
            for uid, (a, b) in COMBOS.items():
                for dt, layer in ((D1, a), (D2, b)):
                    cur.execute("INSERT INTO ai_predict_level_reason_detail(user_number,clazz_number,subclazz_number,layer,factors,type,dt) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                                (uid, CLAZZ, SUBCLAZZ, layer, factors2(layer), TYPE_RENEW, dt))
                    n += 1
            print("inserted renew detail rows:", n)

            # ---- 退费 scene=2 ----
            r = 0
            for dt, layer in REFUND_SEQ:
                cur.execute("INSERT INTO ai_predict_level_reason_detail(user_number,clazz_number,subclazz_number,layer,factors,type,dt) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                            (REFUND_MAIN, CLAZZ, SUBCLAZZ, layer, factors_refund(layer), TYPE_REFUND, dt))
                r += 1
            print("inserted refund detail rows:", r)

        c2 = conn.cursor()
        for t in (TYPE_RENEW, TYPE_REFUND):
            c2.execute("SELECT dt,COUNT(*) c FROM ai_predict_level_reason_detail WHERE type=%s AND clazz_number=%s GROUP BY dt ORDER BY dt", (t, CLAZZ))
            print(t, c2.fetchall())
    finally:
        conn.close()


if __name__ == "__main__":
    main()
