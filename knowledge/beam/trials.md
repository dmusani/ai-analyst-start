# trials

Grain (a guess from the data, confirm it): one row per trial_id. 2,073 rows.

## Columns

| Name | Type | Null rate | Distinct |
| --- | --- | --- | --- |
| trial_id | int64 | 0.00% | 2,073 |
| user_id | int64 | 0.00% | 2,073 |
| started_at | datetime64[ns] | 0.00% | 2,071 |
| ends_at | datetime64[ns] | 0.00% | 2,071 |
| outcome | object | 20.16% | 2 |
| outcome_at | datetime64[ns] | 20.16% | 1,655 |

## Date ranges

- `started_at`: 2026-08-01T00:29:17 to 2026-09-24T22:59:05
- `ends_at`: 2026-08-15T00:29:17 to 2026-10-08T22:59:05
- `outcome_at`: 2026-08-06T05:37:23 to 2026-09-24T23:55:08

## Low-cardinality values

- `outcome`: converted (828), canceled (827)

## Meaning

- `trial_id`, `user_id`: both unique, so each user has at most one trial (profile output; matches AGENTS.md). All `user_id`s are found in `users` (checked).
- `started_at`: when the trial began. Runs 2026-08-01 to 2026-09-24, so the table holds about seven weeks of trials (quirk: trials launched 2026-08-01). No earlier history exists.
- `ends_at`: `started_at` plus 14 days (inferred). Runs to 2026-10-08, after the analysis date.
- `outcome`: converted or canceled (converted = became paid, confirmed against `subscriptions`; see the next line). 20.16% null = trials still open (418 rows). Every open trial has `ends_at` after 2026-09-24 and started on or after 2026-09-11 (checked), so the nulls are explained by the quirk "trials mature late". Exclude them from conversion rates.
- Converted means paid (confirmed, checked on the data to 2026-09-24): all 828 converted trials have a paid subscription (590 monthly, 238 annual) that starts on the trial's `ends_at` date (median gap 0 days, 100% within one day). None of the 827 canceled trials and none of the 418 open trials has a paid subscription. Matching is by `user_id`, which is unique in `subscriptions`.
- `outcome_at`: when the outcome was recorded. Null exactly when `outcome` is null (checked), never before `started_at`, never after `ends_at` (checked). Some trials resolve before `ends_at` (early cancel or early conversion; inferred).

Because early outcomes arrive before `ends_at`, trials started in the last 14 days are partly resolved and the resolved part may not be representative (early resolvers differ from late ones). Treat rates for those cohorts as provisional.

Verdict: Proceed. The grain is clear and every null is explained by a quirk. Caution for any trend: the latest two weeks of cohorts are unmatured.
