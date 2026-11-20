-- Source: course-db, public.trials / sessions / users. Read-only, aggregates only.
-- Analysis date 2026-09-24. Population: trials started on or before 2026-09-10 (14 days
-- closed by 2026-09-24, outcome known), with an outcome recorded on or after day 7, so a
-- full first week is observable. Day d0 = the trial start date; the first week is d0 to d0+6.
-- Sessions are filtered to 2026-08-01 .. 2026-09-17 (covers the last first week, 2026-09-16).
-- Cut-offs were set from the distribution of first-week activity (queries 0a, 0b in the
-- notes of the run) before any conversion result was looked at.
--   Set A: binge-then-quiet = day-one sessions >= 6 and active on <= 3 of days 2-7;
--          steady = active on >= 5 of days 2-7 and day-one share of week sessions < 30%.
--   Set B: binge-then-quiet = day-one share >= 40%, day-one sessions >= 4, active on <= 3 of days 2-7;
--          steady = active on >= 5 of days 2-7 and day-one share < 25%.
--   Other = every remaining trial in the population.

-- name: raw_population
select count(*) as matured_trials,
       sum((outcome_at < started_at + interval '7 days')::int) as resolved_in_first_7_days,
       sum((outcome_at < started_at + interval '7 days' and outcome = 'converted')::int) as early_converted,
       sum((outcome_at < started_at + interval '7 days' and outcome = 'canceled')::int) as early_canceled,
       sum((outcome_at >= started_at + interval '7 days')::int) as analysed
from public.trials
where started_at::date <= '2026-09-10' and outcome is not null;

-- name: raw_group_conversion
with pop as (
  select t.trial_id, t.user_id, t.started_at::date d0, t.outcome,
         ((t.started_at::date - date '2026-08-01') / 7 + 1) as start_week,
         u.device_type, u.country
  from public.trials t join public.users u on u.user_id = t.user_id
  where t.started_at::date <= '2026-09-10' and t.outcome is not null
    and t.outcome_at >= t.started_at + interval '7 days'
),
f as (
  select p.*,
    count(*) filter (where s.session_date::date = p.d0) s0,
    count(*) filter (where s.session_date::date > p.d0) s_rest,
    count(distinct s.session_date::date) filter (where s.session_date::date > p.d0) a_days
  from pop p
  left join public.sessions s on s.user_id = p.user_id
    and s.session_date >= '2026-08-01' and s.session_date < '2026-09-18'
    and s.session_date::date >= p.d0 and s.session_date::date <= p.d0 + 6
  group by p.trial_id, p.user_id, p.d0, p.outcome, p.start_week, p.device_type, p.country
),
g as (
  select *,
    case when s0 + s_rest > 0 then s0::numeric / (s0 + s_rest) end as share0,
    case when s0 >= 6 and a_days <= 3 then 'binge_then_quiet'
         when a_days >= 5 and s0 + s_rest > 0 and s0::numeric / (s0 + s_rest) < 0.30 then 'steady'
         else 'other' end as grp_a,
    case when s0 >= 4 and s0 + s_rest > 0 and s0::numeric / (s0 + s_rest) >= 0.40 and a_days <= 3 then 'binge_then_quiet'
         when a_days >= 5 and s0 + s_rest > 0 and s0::numeric / (s0 + s_rest) < 0.25 then 'steady'
         else 'other' end as grp_b
  from f
),
long as (
  select 'A' as cutoffs, grp_a as grp, * from g
  union all
  select 'B', grp_b, * from g
)
select cutoffs, grp, 'all' as dimension, 'all' as segment, count(*) as trials, sum((outcome = 'converted')::int) as converted from long group by 1, 2
union all
select cutoffs, grp, 'device_type', device_type, count(*), sum((outcome = 'converted')::int) from long group by 1, 2, 4
union all
select cutoffs, grp, 'country', country, count(*), sum((outcome = 'converted')::int) from long group by 1, 2, 4
union all
select cutoffs, grp, 'start_week', start_week::text, count(*), sum((outcome = 'converted')::int) from long group by 1, 2, 4
order by 1, 3, 4, 2;

-- name: raw_join_check
-- One row per trial after aggregating sessions: rows against distinct trials.
with pop as (
  select t.trial_id, t.user_id, t.started_at::date d0
  from public.trials t
  where t.started_at::date <= '2026-09-10' and t.outcome is not null
    and t.outcome_at >= t.started_at + interval '7 days'
),
f as (
  select p.trial_id from pop p
  left join public.sessions s on s.user_id = p.user_id
    and s.session_date >= '2026-08-01' and s.session_date < '2026-09-18'
    and s.session_date::date >= p.d0 and s.session_date::date <= p.d0 + 6
  group by p.trial_id
)
select (select count(*) from pop) as population_rows, count(*) as after_session_join, count(distinct trial_id) as distinct_trials from f;

-- name: raw_activity_distribution
-- Distribution of first-week activity for the same population, with no outcome, used to set the cut-offs.
-- (Percentiles of day-one sessions, sessions on days 2-7 and active days among days 2-7; shares of day-one sessions.)

-- name: raw_activity_grid
-- Added after the first conversion result: day-one sessions by number of active days among days 2-7,
-- to separate "binge on day one" from "go quiet afterwards".
with pop as (
  select t.trial_id, t.user_id, t.started_at::date d0, t.outcome
  from public.trials t
  where t.started_at::date <= '2026-09-10' and t.outcome is not null
    and t.outcome_at >= t.started_at + interval '7 days'
),
f as (
  select p.trial_id, p.outcome,
    count(*) filter (where s.session_date::date = p.d0) s0,
    count(distinct s.session_date::date) filter (where s.session_date::date > p.d0) a_days
  from pop p
  left join public.sessions s on s.user_id = p.user_id
    and s.session_date >= '2026-08-01' and s.session_date < '2026-09-18'
    and s.session_date::date >= p.d0 and s.session_date::date <= p.d0 + 6
  group by p.trial_id, p.outcome
)
select case when s0 >= 6 then '3_day1_6plus' when s0 >= 3 then '2_day1_3to5' else '1_day1_0to2' end as day_one,
       case when a_days <= 1 then '1_days_0to1' when a_days <= 3 then '2_days_2to3' when a_days = 4 then '3_days_4' else '4_days_5to6' end as later_days,
       count(*) trials, sum((outcome = 'converted')::int) converted
from f group by 1, 2 order by 1, 2;
