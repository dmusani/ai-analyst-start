# subscriptions

Grain (a guess from the data, confirm it): one row per subscription_id. 30,747 rows.

## Columns

| Name | Type | Null rate | Distinct |
| --- | --- | --- | --- |
| subscription_id | int64 | 0.00% | 30,747 |
| user_id | int64 | 0.00% | 30,747 |
| plan | object | 0.00% | 3 |
| start_date | datetime64[ns] | 0.00% | 9,584 |
| end_date | datetime64[ns] | 87.90% | 1,789 |
| status | object | 0.00% | 3 |

## Date ranges

- `start_date`: 2022-01-11T00:00:00 to 2026-10-04T17:15:33
- `end_date`: 2022-03-07T00:00:00 to 2026-11-11T18:47:46

## Low-cardinality values

- `plan`: free (18,234), monthly (9,376), annual (3,137)
- `status`: active (27,028), expired (2,929), canceled (790)

## Meaning

- `subscription_id`, `user_id`: both unique, so each user has at most one subscription row (profile output).
- `plan`: free (18,234), monthly (9,376) or annual (3,137). Free plans have no `end_date` (quirk: free plans never end).
- `start_date`: when the subscription began. Runs to 2026-10-04, after the analysis date; rows after 2026-09-24 are scheduled starts (quirk: future start dates).
- `end_date`: when it ended or is scheduled to end. 87.9% null (free plans, still-running paid plans). Runs to 2026-11-11; dates after 2026-09-24 are scheduled cancellations and still active today (quirk: future end dates).
- `status`: active, canceled or expired (inferred). Not used for retention, because `end_date` carries the timing.

Verdict: Proceed for the retention question, with caution on the monthly start spikes in Jul and Sep 2026 (monthly starts 491 and 886 vs about 200 in earlier months; most are likely trials converting or scheduled starts, not confirmed).
