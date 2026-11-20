# Review: Did the March 2026 price increase hurt retention, and for whom?

## Verdict
**Think on it**: the numbers hold and reproduce by a second route, but the read of "the price caused it" and the segment story both need caveats in the brief.

Round: 1

## Findings
### 1. The step up in churn cannot be pinned on the price alone (Think on it)
- Where: `monthly_churn_by_month.csv`; chart `monthly_churn_trend.png`; headline lines in `analysis.py` ("Change vs recent baseline").
- Problem: monthly-plan churn already jumped once without a price change, from 0.75% in Aug 2025 to 2.2% in Oct 2025, then stayed at 2.2% to 2.6%. March 2026, the month the price rose, shows 2.62%, inside that range; the doubling appears in April. There is no monthly group still at $10, so the data shows when churn rose, not why.
- Evidence: monthly churn by month in `monthly_churn_by_month.csv`: Aug 2025 0.75%, Oct 2025 2.19%, Feb 2026 2.16%, Mar 2026 2.62%, Apr 2026 5.53%. Every payment in Dec 2025 to Feb 2026 is $10 and every payment from Mar 2026 is $12 (`raw_monthly_price_paid.csv`).
- Fix: in the brief, say "churn more than doubled in the months after the price rose" and not "the price rose and caused churn". State the one-month lag and the earlier Oct 2025 step. Do not present the +3.4 pp as the effect of the price.
- Kind: for the brief

### 2. Tenure and country gaps may reflect which cohort sits in the group (Think on it)
- Where: `segment_churn_change.csv`, the tenure and country rows.
- Problem: September 2025 had about five times the normal signups (quirk). Those subscribers are 7 to 11 months old in Apr to Aug 2026, so they sit in the 3 to 12 month group, the group with the most extra cancellations. The script has no cut by start month, so a cohort effect cannot be told apart from a price effect for that group, and the country and device gaps are not cross-cut with tenure.
- Evidence: 3 to 6 and 6 to 12 month tenure groups together account for 484 of the 917 extra cancellations (131 + 353). The at-risk base steps from 4,131 in Sep 2025 to 5,257 in Oct 2025 (`monthly_churn_by_month.csv`).
- Fix: carry as not verified. A follow-up cut of churn by start month (spike month against others) would settle it.
- Kind: for the brief

### 3. The metric is calendar-month churn, not the retention measure in the frame (Think on it)
- Where: `analysis.py` module docstring and `rate()`; `frame.md` "Definitions to confirm".
- Problem: the frame defined retention as the share of monthly subscribers still subscribed a fixed number of days after their start, compared between start cohorts before and after March 2026. The script measures cancellations per active subscriber in each calendar month, and uses Oct 2025 to Feb 2026 as the baseline rather than all months before March. A reader expecting "x% still subscribed after 90 days" will not find it. The answer to the question still holds under either definition.
- Evidence: the frame says "share of monthly subscribers still subscribed ... at a fixed number of days after their start"; the script prints "% a month" cancellation rates. Against the full Jan 2025 to Feb 2026 period the gap is larger (+4.24 pp), so the recent baseline is the cautious one.
- Fix: say in the brief that the measure is monthly churn, why it was chosen (it covers existing subscribers, who were hit too), and that the gap against the longer baseline is larger.
- Kind: for the brief

## What's solid
Mechanics are sound. The script reruns with identical tables, the segments add back to the overall monthly total for every month in all three cuts, the payments join does not fan out, and the open month (Sep 2026) is excluded. The headline rates (2.37% before, 5.79% after) match a second SQL route exactly, and the post-period country totals and pre-period device totals match the database cell for cell. Every post month sits above every month of the baseline, in all 11 segments, and the annual plan did not move, so the rise is not a general market shift.

## One question to sit with
Every one of the 11 segments rose clearly, so the rule "any clear drop for a segment" flags all of them; what would the head of growth need to see to pick some customers over others, and is that a size of rise, a number of customers, or revenue at risk?

## Mechanics
| Check | Result | Evidence |
| --- | --- | --- |
| Reruns, tables stable | Pass | Exit 0; md5 of all 6 files in `data/` identical across runs. |
| Stays in its lane | Pass, with a note | Reads only the saved result tables in the run folder's `data/` (pulled from the database by `queries.sql`), writes inside the run folder, prints aggregates only. Nothing in the repo's `data/` is read or changed. |
| Checks ran | Pass, with a note | `parts_sum_to_total` ran on every month, measure and cut (no mismatch); join fan-out recorded in SQL (144,065 before and after); open-month exclusion is a printed assertion on the latest month pulled, not `date_boundaries`, because only monthly aggregates are saved. `matured_only` is not needed for a calendar-month churn rate. |
| Every number traces | Pass | Each printed rate comes from `monthly_churn_by_month.csv` or `segment_churn_change.csv`; extra-cancellation figures are in the segment table. |
| Independent recompute | Pass | SQL with `FILTER` counts: pre 26,387 at risk and 626 churned (2.372%), March 5,486 and 144, post 26,821 and 1,553 (5.790%). Script: 2.37%, 2.62%, 5.79%. Country post totals (EU 5,267 / 325, India 5,305 / 351, Rest 5,316 / 344, US 10,933 / 533) and device pre totals (Android 8,841 / 201, iOS 9,154 / 183, Web 8,392 / 242) equal the saved tables. |
| Parts sum to totals | Pass | Country, device and tenure each add to the overall at risk and churned in all 20 months. |
| Charts match tables | Pass | Four charts, made through `helpers.charts`, titles state the takeaway, bar values equal `change_pp` x 100 from `segment_churn_change.csv`. |

## Reasoning
| Check | Result | Evidence |
| --- | --- | --- |
| Answers the question | Mostly | Churn rose after the price did, and for whom is answered by segment; "hurt" as a cause is not shown (finding 1). |
| Speaks to the decision | Partly | Threshold from the frame is met in every segment, so it does not choose where to roll back (question above). |
| Every number compared | Pass | Each rate carries the Oct 2025 to Feb 2026 baseline, the full pre-period, and the annual plan. Units named: pp and relative percent. |
| Quirks handled | Pass, with a note | Price change, free plans, future end and start dates, open month, trial spike months: handled in SQL or by the Sep 2026 cut. The Sep 2025 spike is not cut out (finding 2). |
| Population | Pass | Paid monthly plan, active at the start of each month, starts after 2026-09-24 excluded (425 monthly rows). Same-month start and end are not counted. |
| Segmented | Pass | Country, device, tenure; no segment moved opposite to the total. |
| Claims vs evidence | See finding 1 | Wording in the brief must stay at "after", not "because". |
| Sanity | Pass | Rates 0.6% to 6.6%; at risk at most 5,537, below the 9,376 monthly subscriptions in the table. |
| Frame definitions | Differs | Finding 3. |

## Not checked
- Whether any single start cohort (for example September 2025) drives the rise; no cut by start month.
- Country, device and tenure crossed with each other.
- Why churn rose in Oct 2025, and what the one-month lag in March means; no reasons are in the data.
- A cut by price paid before March: every monthly subscriber moved to $12 together, so none exists.
- The raw result tables were saved from query output by hand. Pooled totals and one country and one device cut were matched to the database; every cell was not.
- Retention at a fixed age by start cohort, the frame's original measure.
- All definitions in `frame.md` are still marked "(assumed)".
- The database `payments` table has 144,065 rows with history from 2022, while `knowledge/beam/payments.yaml` says 100,914 rows from 2025-01-01. This did not change any number here.
