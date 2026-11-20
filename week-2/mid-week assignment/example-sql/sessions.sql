-- sessions: ~1.2% SAMPLE of the real table (~368M rows). Use for rates, mixes, distributions.
-- Do NOT report totals as Beam-wide figures. Do NOT trust per-user counts until the sampling method is confirmed.
-- Exclude the 273 rows dated 2026-09-25/26 (after data end 2026-09-24).
-- Timestamps are midnight only: sessions within a day cannot be ordered.
-- Do not filter on duration.
-- Caveat: 2026-08 runs ~20% higher per day than 2026-07 and 2026-09; unexplained. Flag it in any comparison.
-- Caveat: no September 2025 spike appears here (unlike signups).
-- Open item: check overlap with user_activity_metrics before combining.

-- 1. Activity mix by month (shares, not totals)
SELECT DATE_TRUNC('month', CAST(session_date AS DATE)) AS month,
       activity_type,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY DATE_TRUNC('month', CAST(session_date AS DATE))), 1) AS pct_of_month
FROM sessions
WHERE CAST(session_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 2. Duration distribution by activity type
-- Percentiles syntax varies by dialect (PERCENTILE_CONT shown).
SELECT activity_type,
       COUNT(*) AS sample_sessions,
       ROUND(AVG(duration_minutes), 1) AS mean_min,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_minutes) AS median_min,
       PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY duration_minutes) AS p90_min
FROM sessions
WHERE CAST(session_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1
ORDER BY 1;

-- 3. Sessions per day by month (sample rate; the 2026-08 jump is visible here)
SELECT DATE_TRUNC('month', CAST(session_date AS DATE)) AS month,
       COUNT(*) AS sample_sessions,
       COUNT(DISTINCT CAST(session_date AS DATE)) AS days_in_data,
       ROUND(1.0 * COUNT(*) / COUNT(DISTINCT CAST(session_date AS DATE)), 0) AS sample_sessions_per_day
FROM sessions
WHERE CAST(session_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1
ORDER BY 1;

-- 4. Activity mix by country and device (via users)
SELECT u.country,
       u.device_type,
       s.activity_type,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY u.country, u.device_type), 1) AS pct_within_segment
FROM sessions s
JOIN users u USING (user_id)
WHERE CAST(s.session_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;

-- 5. Activity mix: paid vs free users (rates only, per-user counts not used)
-- Paid = monthly/annual with start_date on or before 2026-09-24.
SELECT CASE WHEN sub.plan IN ('monthly', 'annual')
             AND CAST(sub.start_date AS DATE) <= DATE '2026-09-24'
            THEN 'paid' ELSE 'free_or_other' END AS segment,
       s.activity_type,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY
             CASE WHEN sub.plan IN ('monthly', 'annual')
                   AND CAST(sub.start_date AS DATE) <= DATE '2026-09-24'
                  THEN 'paid' ELSE 'free_or_other' END), 1) AS pct_within_segment
FROM sessions s
JOIN subscriptions sub USING (user_id)
WHERE CAST(s.session_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;
