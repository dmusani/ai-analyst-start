-- payments: one row per payment_id; subscription_id + payment_date is unique.
-- Data starts 2025-01-01 (no earlier payment history). Analysis date = 2026-09-24.
-- Monthly price rose $10 -> $12 on 2026-03-01 and applied to existing subscribers too,
-- so there is no unexposed monthly group. Annual is $100.
-- Pre/post differences in monthly payments are not a data problem. Do not attribute causal effects.

-- 1. Revenue by month and plan
SELECT DATE_TRUNC('month', CAST(p.payment_date AS DATE)) AS pay_month,
       s.plan,
       COUNT(*) AS payments,
       SUM(p.amount_usd) AS revenue_usd
FROM payments p
JOIN subscriptions s USING (subscription_id)
WHERE CAST(p.payment_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 2. Payment amount distribution by month (shows the 10 -> 12 shift descriptively)
SELECT DATE_TRUNC('month', CAST(payment_date AS DATE)) AS pay_month,
       amount_usd,
       COUNT(*) AS payments
FROM payments
WHERE CAST(payment_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 3. Payment method mix by month
SELECT DATE_TRUNC('month', CAST(payment_date AS DATE)) AS pay_month,
       method,
       COUNT(*) AS payments,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY DATE_TRUNC('month', CAST(payment_date AS DATE))), 1) AS pct_of_month
FROM payments
WHERE CAST(payment_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1, 2
ORDER BY 1, 2;

-- 4. Paying subscriptions per month (monthly distinct payers)
SELECT DATE_TRUNC('month', CAST(payment_date AS DATE)) AS pay_month,
       COUNT(DISTINCT subscription_id) AS paying_subscriptions
FROM payments
WHERE CAST(payment_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1
ORDER BY 1;

-- 5. Revenue by country (via users)
SELECT u.country,
       COUNT(*) AS payments,
       SUM(p.amount_usd) AS revenue_usd
FROM payments p
JOIN subscriptions s USING (subscription_id)
JOIN users u ON u.user_id = s.user_id
WHERE CAST(p.payment_date AS DATE) <= DATE '2026-09-24'
GROUP BY 1
ORDER BY revenue_usd DESC;
