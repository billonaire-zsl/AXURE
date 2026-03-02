-- 3日留存率（Hive SQL）
-- 口径：
-- 1) 新增用户：用户历史首次登录日期 = cohort_date
-- 2) 3日留存：在 cohort_date + 3 当天有登录行为
-- 3) 结果：cohort_date 粒度的 3日留存率
--
-- 表结构假设：
--   dwd_user_login_di(
--     user_id STRING,
--     dt      STRING   -- 分区/日期字段，格式 yyyy-MM-dd
--   )

WITH first_login AS (
  SELECT
    user_id,
    MIN(dt) AS cohort_date
  FROM dwd_user_login_di
  GROUP BY user_id
),
new_users AS (
  SELECT
    cohort_date,
    COUNT(1) AS new_user_cnt
  FROM first_login
  GROUP BY cohort_date
),
retained_d3 AS (
  SELECT
    f.cohort_date,
    COUNT(DISTINCT f.user_id) AS retained_user_cnt_d3
  FROM first_login f
  JOIN dwd_user_login_di l
    ON f.user_id = l.user_id
   AND l.dt = date_format(date_add(to_date(f.cohort_date), 3), 'yyyy-MM-dd')
  GROUP BY f.cohort_date
)
SELECT
  n.cohort_date,
  n.new_user_cnt,
  COALESCE(r.retained_user_cnt_d3, 0) AS retained_user_cnt_d3,
  ROUND(COALESCE(r.retained_user_cnt_d3, 0) / n.new_user_cnt, 4) AS retention_rate_d3
FROM new_users n
LEFT JOIN retained_d3 r
  ON n.cohort_date = r.cohort_date
ORDER BY n.cohort_date;
