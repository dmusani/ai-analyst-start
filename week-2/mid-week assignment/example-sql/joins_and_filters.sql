-- Multi-table queries with joins and filters.
-- Analysis date = data end = 2026-09-24. Compare on dates, not timestamps.
-- Dialect: generic SQL (Postgres-style). Adjust as needed.

-- 1. Converted trials: plan, country, device, and first-month revenue
-- Joins: trials -> users -> subscriptions -> payments.
-- Filters: converted only (open trials excluded), paid plans, payments on or before the analysis date.
-- Cohorts started on or after 2026-09-10 are provisional (last 14 days).
SELECT u.country,
       u.device_type,
       s.plan,
       COUNT(DISTINCT t.user_id) AS converted_users,
       SUM(p.amount_usd) AS revenue_usd
FROM trials t
JOIN users u          ON u.user_id = t.user_id
JOIN subscriptions s  ON s.user_id = t.user_id
LEFT JOIN payments p  ON p.subscription_id = s.subscription_id
                     AND CAST(p.payment_date AS DATE) <= DATE '2026-09-24'
WHERE t.outcome = 'converted'
  AND s.plan IN ('monthly', 'annual')
  AND CAST(s.start_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2, 3
ORDER BY revenue_usd DESC;

-- 2. Paid churn rate by country and plan
-- Joins: subscriptions -> users.
-- Filters: free plans excluded, scheduled starts excluded, future end_date counts as still active.
-- Judgment call: "churned" = end_date on or before 2026-09-24 (status not used).
-- Caveat: September 2025 signup spike (~5x) inflates that cohort in any month-over-month read.
SELECT u.country,
       s.plan,
       COUNT(*) AS paid_subs,
       SUM(CASE WHEN s.end_date IS NOT NULL
                 AND CAST(s.end_date AS DATE) <= DATE '2026-09-24'
                THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN s.end_date IS NOT NULL
                               AND CAST(s.end_date AS DATE) <= DATE '2026-09-24'
                              THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_pct
FROM subscriptions s
JOIN users u ON u.user_id = s.user_id
WHERE s.plan <> 'free'
  AND CAST(s.start_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY churn_pct DESC;

-- 3. Monthly-plan payment method mix by country, since the price change
-- Joins: payments -> subscriptions -> users.
-- Filters: monthly plan, payments from 2026-03-01 through the analysis date.
-- Descriptive only: no causal read on the $10 -> $12 change, and there is no unexposed monthly group.
SELECT u.country,
       p.method,
       COUNT(*) AS payments,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY u.country), 1) AS pct_within_country
FROM payments p
JOIN subscriptions s ON s.subscription_id = p.subscription_id
JOIN users u         ON u.user_id = s.user_id
WHERE s.plan = 'monthly'
  AND CAST(p.payment_date AS DATE) >= DATE '2026-03-01'
  AND CAST(p.payment_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, payments DESC;

-- 4. Session activity mix: converted vs canceled trial users
-- Joins: sessions -> trials.
-- Filters: resolved trials only; sessions from trial start through the analysis date
-- (drops the 273 rows dated 2026-09-25/26).
-- Sessions is a ~1.2% sample, so this reads shares only. Do not read per-user counts.
-- Caveat: 2026-08 session volume is ~20% higher per day, unexplained, and trials start 2026-08-01,
-- so both groups sit inside that window.
SELECT t.outcome,
       s.activity_type,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY t.outcome), 1) AS pct_within_outcome
FROM sessions s
JOIN trials t ON t.user_id = s.user_id
WHERE t.outcome IN ('converted', 'canceled')
  AND CAST(s.session_date AS DATE) >= CAST(t.started_at AS DATE)
  AND CAST(s.session_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 5. Revenue per paying subscription by signup year and device
-- Joins: payments -> subscriptions -> users.
-- Filters: paid plans, payments on or before the analysis date.
-- Caveat: payments start 2025-01-01, so users who signed up earlier have partial payment history.
-- The 2025 cohort includes the September 2025 spike.
SELECT EXTRACT(YEAR FROM CAST(u.signup_date AS DATE)) AS signup_year,
       u.device_type,
       COUNT(DISTINCT p.subscription_id) AS paying_subs,
       SUM(p.amount_usd) AS revenue_usd,
       ROUND(SUM(p.amount_usd) / COUNT(DISTINCT p.subscription_id), 2) AS revenue_per_paying_sub
FROM payments p
JOIN subscriptions s ON s.subscription_id = p.subscription_id
JOIN users u         ON u.user_id = s.user_id
WHERE s.plan <> 'free'
  AND CAST(p.payment_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;
