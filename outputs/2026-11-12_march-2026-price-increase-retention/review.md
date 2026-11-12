# Review: Did the March 2026 price increase hurt monthly retention, and for whom?

## Verdict
**Think on it**: the numbers hold, but the brief must state the measure and baseline used, and cannot claim the increase caused the rise.

Round: 1

## Findings
### 1. Measure differs from the frame's definition (Think on it)
- Where: `analysis.py` metric (monthly churn), `frame.md` "Definitions to confirm" Metric
- Problem: the frame assumed retention as the share still subscribed at a fixed age. The script measures monthly cancellations per 1,000 active subscribers by calendar month. The answer to the question still holds.
- Evidence: frame wording versus `data/monthly_churn_by_month.csv`.
- Fix: the brief says plainly it uses monthly cancellations per 1,000 subscribers, and names the change from the frame.
- Kind: for the brief

### 2. No unexposed monthly group, so cause is not shown (Think on it)
- Where: `data/before_after_summary.csv`, `data/monthly_churn_by_month.csv`
- Problem: every monthly subscriber moved to $12 on 2026-03-01, so the rise cannot be separated from anything else that changed. The break is in April 2026 (55.3 per 1,000, from 26.2 in March), not March. Annual plans, the only unaffected plan, moved from 3.7 to 5.1.
- Evidence: monthly table and annual table; annual is a different product.
- Fix: the brief says the timing and the annual benchmark fit a price effect but do not prove one, and that July to September 2026 monthly start spikes are unexplained.
- Kind: for the brief

### 3. The baseline moves depending on the pre period (Think on it)
- Where: `before_after_summary.csv`
- Problem: the September 2025 signup spike raised churn from October 2025. Against all of Jan 2025 to Feb 2026 the rise looks like +239% (15.5 to 52.5), but against Oct 2025 to Feb 2026 it is +122% (23.7 to 52.5).
- Evidence: the script now prints both. September 2025 signups alone rose from 39.3 to 78.3, and all other cohorts from 13.0 to 48.0, so the rise is not just that cohort.
- Fix: the brief leads with the closer baseline and names the other.
- Kind: for the brief

## What's solid
The script reruns and gives identical tables. An independent subscriber-days recompute gave 15.4 before and 53.1 after, against the script's 15.5 and 52.5. Joins do not fan out, segment cancellations sum to the 1,697 total, the price is uniformly $10 then $12 in payments, and scheduled end dates after 2026-09-24 count as active.

## One question to sit with
Would the head of growth read "per 1,000 cancellations a month" as the share of customers lost, when it is a monthly rate on a base of about 5,400?

## Mechanics
| Check | Result | Evidence |
| --- | --- | --- |
| Reruns, tables unchanged | Pass | Checksums identical |
| Stays in its lane | Pass | Reads `data/`, writes in run folder, aggregates only |
| Checks ran | Pass | date boundaries, join fan-out, parts sum (country, device, cohort, tenure) |
| Numbers trace to tables | Pass | all printed numbers in `data/*.csv` |
| Independent recompute | Pass | 15.4 and 53.1 against 15.5 and 52.5 |
| Charts match tables | Pass | titles state takeaways |

## Reasoning
| Check | Result | Evidence |
| --- | --- | --- |
| Answers the question | Pass | who, how much, when |
| Quirks handled | Pass | free plans, future starts and ends, Sep 2025 spike |
| Segmented | Pass | tenure, country, device |
| Claims within evidence | Think on it | see finding 2 |
| Frame definitions | Think on it | see finding 1 |

## Not checked
- Why customers cancelled; the data has no reasons.
- Whether new subscribers since March ($12 from the start) churn faster: 100.5 per 1,000, but a new-subscriber group has no like-for-like earlier baseline.
- No threshold was stated, so the result cannot be judged against one.
- Country by tenure cells are small (under 100 cancellations in several).
- September 2026 is open and excluded.
