-- 退费预测分层配置 · 排查 SQL（走 mysql-query skill 依次执行，<> 换成实际值）

-- 0. 班级 bizNumber → clazz_number（cluster_id=317, db=course_center）
SELECT number FROM course_center.clazz WHERE biz_number = '<班级ID>';

-- 0.1 clazz_number → subclazz_number（一个 clazz 可能挂多个平行班，统计必须精确到 subclazz，
--     只用 clazz_number 会把别的班混进来）
-- cluster_id=336, db=ees_data
SELECT subclazz_number, COUNT(*) FROM ees_data.ai_refund_prediction_results
WHERE clazz_number = <x> GROUP BY subclazz_number;

-- 1. 看分层集中度
SELECT prediction_level, COUNT(*) FROM ees_data.ai_refund_prediction_results
WHERE subclazz_number = <x> GROUP BY prediction_level;

-- 2. 抽几条高危记录拿维度
SELECT user_number, prediction_score, prediction_level, stage,
       course_first_level_department_name, performance_second_level_department_name,
       school_term_name, grade, student_type
FROM ees_data.ai_refund_prediction_results
WHERE subclazz_number = <x> AND prediction_level = '4' LIMIT 10;

-- 3. 拿这些维度看目标组合有没有精确配置；只有 defaultGrade 那行 = 正在吃兜底
SELECT * FROM ees_data.predict_intent_config
WHERE course_first_level_department_name = '<部门>'
  AND course_second_level_department_name = '<学部>'
  AND school_term_name = '<学期>' AND stage = '<stage>';

-- 4. 看该 stage 下所有部门/学部/学期已配了哪些组合，找出缺口范围
--    grade_specific_rows = 0 的组合就是缺口
SELECT course_first_level_department_name, course_second_level_department_name, school_term_name,
  SUM(CASE WHEN grade='defaultGrade' THEN 1 ELSE 0 END) AS default_rows,
  SUM(CASE WHEN grade!='defaultGrade' THEN 1 ELSE 0 END) AS grade_specific_rows
FROM ees_data.predict_intent_config
WHERE stage = '<目标stage>'
GROUP BY course_first_level_department_name, course_second_level_department_name, school_term_name;

-- 5. 补完配置后核对阈值区间有没有异常（四档 start/end 重合，JSON 字段肉眼核对，SQL 不好直接过滤）
SELECT course_second_level_department_name, grade, student_type, intent_config
FROM ees_data.predict_intent_config
WHERE course_first_level_department_name = '<部门>' AND stage = '<stage>' AND grade != 'defaultGrade';

-- 6. 回溯后验证：重跑第1步，确认高危占比回落到合理水平（个位数~十几个百分点，不是 80%+）
