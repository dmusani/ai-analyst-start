-- Source: course-db, public.subscriptions / users / payments. Read-only, aggregates only.
-- Analysis date 2026-09-24. Months run Jan 2025 to Aug 2026; Sep 2026 is open and excluded.
-- At risk in month M: started before M's first day and not ended before it.
-- Churned in month M: end_date falls inside M. Subscriptions starting after 2026-09-24 are excluded.

-- name: raw_monthly_churn_overall
with months as (
  select generate_series('2025-01-01'::date, '2026-08-01'::date, interval '1 month')::date as m
)
select to_char(m.m, 'YYYY-MM') as month, s.plan,
       count(*) as at_risk,
       sum((s.end_date::date >= m.m and s.end_date::date < (m.m + interval '1 month')::date)::int) as churned
from months m
join public.subscriptions s
  on s.start_date::date < m.m
 and (s.end_date is null or s.end_date::date >= m.m)
where s.plan in ('monthly', 'annual')
  and s.start_date::date <= '2026-09-24'
group by 1, 2
order by 1, 2;

-- name: raw_monthly_churn_segments
with months as (
  select generate_series('2025-01-01'::date, '2026-08-01'::date, interval '1 month')::date as m
),
base as (
  select m.m, s.end_date, u.country, u.device_type,
         case when (m.m - s.start_date::date) < 90 then '1_under_3m'
              when (m.m - s.start_date::date) < 180 then '2_3_to_6m'
              when (m.m - s.start_date::date) < 365 then '3_6_to_12m'
              else '4_12m_plus' end as tenure
  from months m
  join public.subscriptions s
    on s.start_date::date < m.m
   and (s.end_date is null or s.end_date::date >= m.m)
  join public.users u on u.user_id = s.user_id
  where s.plan = 'monthly'
    and s.start_date::date <= '2026-09-24'
),
flag as (
  select to_char(m, 'YYYY-MM') as month, country, device_type, tenure,
         (end_date::date >= m and end_date::date < (m + interval '1 month')::date)::int as churned
  from base
)
select month, 'country' as dimension, country as segment, count(*) as at_risk, sum(churned) as churned from flag group by 1, 2, 3
union all
select month, 'device_type', device_type, count(*), sum(churned) from flag group by 1, 2, 3
union all
select month, 'tenure', tenure, count(*), sum(churned) from flag group by 1, 2, 3
order by 1, 2, 3;

-- name: raw_monthly_price_paid
select to_char(date_trunc('month', p.payment_date), 'YYYY-MM') as month, s.plan,
       p.amount_usd, count(*) as payments
from public.payments p
join public.subscriptions s on s.subscription_id = p.subscription_id
where s.plan = 'monthly'
  and p.payment_date >= '2025-12-01' and p.payment_date <= '2026-09-24 23:59:59'
group by 1, 2, 3
order by 1, 3;

-- name: raw_payments_join_check
select (select count(*) from public.payments) as payments_rows,
       (select count(*) from public.payments p join public.subscriptions s on s.subscription_id = p.subscription_id) as payments_after_join;
