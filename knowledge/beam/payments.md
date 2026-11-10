# payments

Grain (a guess from the data, confirm it): one row per payment_id. 100,914 rows.

## Columns

| Name | Type | Null rate | Distinct |
| --- | --- | --- | --- |
| payment_id | int64 | 0.00% | 100,914 |
| subscription_id | int64 | 0.00% | 11,122 |
| payment_date | datetime64[ns] | 0.00% | 13,232 |
| amount_usd | float64 | 0.00% | 3 |
| method | object | 0.00% | 4 |

## Date ranges

- `payment_date`: 2025-01-01T00:00:00 to 2026-09-24T23:51:30

## Low-cardinality values

- `amount_usd`: 10.0 (59,064), 12.0 (37,384), 100.0 (4,466)
- `method`: card (50,237), paypal (20,272), apple_pay (15,298), google_pay (15,107)

## Meaning

- `payment_id`: unique; one row per payment.
- `subscription_id`: always found in `subscriptions` (checked); 11,122 distinct subscriptions pay, so free plans never appear.
- `payment_date`: 2025-01-01 to 2026-09-24. No history before 2025, so monthly payment history before 2025 is missing.
- `amount_usd`: 10.00 and 12.00 (monthly plan) and 100.00 (annual plan). Every monthly payment from 2026-03-01 is $12, including those of subscribers who started before March: the increase hit existing subscribers too, with no unexposed monthly group (quirk: monthly price change).
- `method`: card, paypal, apple_pay or google_pay (inferred).

Verdict: Proceed.
