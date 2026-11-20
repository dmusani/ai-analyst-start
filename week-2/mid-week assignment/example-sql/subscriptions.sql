-- subscriptions: one row per user (user_id unique). plan = free / monthly / annual.
-- Analysis date = data end = 2026-09-24.
-- Rules: exclude free plans from churn/retention; use end_date (not status) for timing;
-- a future end_date means still active; start_date after 2026-09-24 = scheduled start.

-- 1. Paid starts by month and plan
-- Caveat: monthly starts in Jul and Sep 2026 are elevated (491 and 886 vs ~200).
-- Likely converting trials or scheduled starts, but unconfirmed.
-- Caveat: September 2025 signup spike (~5x) may show up here too.
SELECT DATE_TRUNC('month', CAST(start_date AS DATE)) AS start_month,
       plan,
       COUNT(*) AS starts
FROM subscriptions
WHERE plan <> 'free'
  AND CAST(start_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 2. Paid subscriptions ended by month and plan
SELECT DATE_TRUNC('month', CAST(end_date AS DATE)) AS end_month,
       plan,
       COUNT(*) AS ended
FROM subscriptions
WHERE plan <> 'free'
  AND end_date IS NOT NULL
  AND CAST(end_date AS DATE) <= DATE '2026-09-24'
  AND CAST(start_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 3. Currently active paid base as of 2026-09-24
-- Active = started on or before the analysis date and no end_date, or end_date after it.
SELECT plan,
       COUNT(*) AS active_paid
FROM subscriptions
WHERE plan <> 'free'
  AND CAST(start_date AS DATE) <= DATE '2026-09-24'
  AND (end_date IS NULL OR CAST(end_date AS DATE) > DATE '2026-09-24')
GROUP BY 1;

-- 4. Retention by start-month cohort (share still active at 2026-09-24)
-- Judgment call: "retained" = no end_date, or end_date after 2026-09-24.
SELECT DATE_TRUNC('month', CAST(start_date AS DATE)) AS cohort_month,
       plan,
       COUNT(*) AS cohort_size,
       ROUND(100.0 * SUM(CASE WHEN end_date IS NULL OR CAST(end_date AS DATE) > DATE '2026-09-24'
                              THEN 1 ELSE 0 END) / COUNT(*), 1) AS retained_pct
FROM subscriptions
WHERE plan <> 'free'
  AND CAST(start_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 5. Scheduled starts and scheduled cancellations (not yet happened)
SELECT 'scheduled_start' AS kind, plan, COUNT(*) AS n
FROM subscriptions
WHERE CAST(start_date AS DATE) > DATE '2026-09-24'
GROUP BY 1, 2
UNION ALL
SELECT 'scheduled_cancel', plan, COUNT(*)
FROM subscriptions
WHERE plan <> 'free'
  AND CAST(end_date AS DATE) > DATE '2026-09-24'
  AND CAST(start_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2;
