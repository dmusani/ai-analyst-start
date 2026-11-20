-- users: one row per user_id (grain is a guess from the data, confirm it)
-- Analysis date = data end = 2026-09-24. Compare on dates, not timestamps.
-- Dialect: generic SQL (Postgres-style DATE_TRUNC). Adjust as needed.

-- 1. Signups by month
-- Caveat: September 2025 shows a ~5x signup spike (known anomaly). Flag it in any comparison.
SELECT DATE_TRUNC('month', CAST(signup_date AS DATE)) AS signup_month,
       COUNT(*) AS signups
FROM users
WHERE CAST(signup_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1
ORDER BY 1;

-- 2. User mix by country and device
SELECT country,
       device_type,
       COUNT(*) AS users,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_users
FROM users
GROUP BY 1, 2
ORDER BY users DESC;

-- 3. Share of users with a paid plan, by country
-- Paid = monthly or annual. Scheduled starts (start_date after 2026-09-24) excluded.
SELECT u.country,
       COUNT(*) AS users,
       SUM(CASE WHEN s.plan IN ('monthly', 'annual')
                 AND CAST(s.start_date AS DATE) <= DATE '2026-09-24'
                THEN 1 ELSE 0 END) AS paid_users,
       ROUND(100.0 * SUM(CASE WHEN s.plan IN ('monthly', 'annual')
                               AND CAST(s.start_date AS DATE) <= DATE '2026-09-24'
                              THEN 1 ELSE 0 END) / COUNT(*), 1) AS paid_pct
FROM users u
LEFT JOIN subscriptions s USING (user_id)
GROUP BY 1
ORDER BY paid_pct DESC;
