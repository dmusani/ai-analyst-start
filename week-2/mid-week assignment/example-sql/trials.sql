-- trials: one row per user (user_id unique). Trials exist only from 2026-08-01, last 14 days.
-- Analysis date = data end = 2026-09-24.
-- Rules: converted = became paid (monthly/annual) starting on ends_at date.
-- Null outcome = still open: exclude from conversion rates, never count as failures.
-- Cohorts started on or after 2026-09-10 (last 14 days) are partly resolved: label provisional.

-- 1. Conversion rate by weekly cohort (resolved trials only)
SELECT DATE_TRUNC('week', CAST(started_at AS DATE)) AS cohort_week,
       COUNT(*) AS resolved_trials,
       SUM(CASE WHEN outcome = 'converted' THEN 1 ELSE 0 END) AS converted,
       ROUND(100.0 * SUM(CASE WHEN outcome = 'converted' THEN 1 ELSE 0 END) / COUNT(*), 1) AS conv_pct,
       CASE WHEN DATE_TRUNC('week', CAST(started_at AS DATE)) >= DATE '2026-09-10'
            THEN 'provisional' ELSE 'matured' END AS status
FROM trials
WHERE outcome IS NOT NULL
  AND CAST(started_at AS DATE) <= DATE '2026-09-24'
GROUP BY 1
ORDER BY 1;

-- 2. Open vs resolved trials by weekly cohort
SELECT DATE_TRUNC('week', CAST(started_at AS DATE)) AS cohort_week,
       COUNT(*) AS trials,
       SUM(CASE WHEN outcome IS NULL THEN 1 ELSE 0 END) AS open_trials,
       SUM(CASE WHEN outcome IS NOT NULL THEN 1 ELSE 0 END) AS resolved_trials
FROM trials
GROUP BY 1
ORDER BY 1;

-- 3. Days from trial start to outcome (resolved only)
SELECT outcome,
       COUNT(*) AS n,
       ROUND(AVG(CAST(outcome_at AS DATE) - CAST(started_at AS DATE)), 1) AS avg_days_to_outcome
FROM trials
WHERE outcome IS NOT NULL
GROUP BY 1;

-- 4. Conversion by country and device (resolved only)
-- Small cells: check resolved_trials before reading differences.
SELECT u.country,
       u.device_type,
       COUNT(*) AS resolved_trials,
       ROUND(100.0 * AVG(CASE WHEN t.outcome = 'converted' THEN 1.0 ELSE 0 END), 1) AS conv_pct
FROM trials t
JOIN users u USING (user_id)
WHERE t.outcome IS NOT NULL
GROUP BY 1, 2
ORDER BY conv_pct DESC;

-- 5. Plan mix of converted trials
-- Matches by user_id (unique in subscriptions); paid start should fall on the trial's ends_at date.
SELECT s.plan,
       COUNT(*) AS converted_trials
FROM trials t
JOIN subscriptions s USING (user_id)
WHERE t.outcome = 'converted'
  AND s.plan IN ('monthly', 'annual')
GROUP BY 1;
