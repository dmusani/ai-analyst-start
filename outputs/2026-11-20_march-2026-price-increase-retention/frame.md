# Frame

## Question
Did the March 2026 price increase hurt retention, and for whom? The head of growth is deciding whether to roll back part of the increase for some customers.

## Decision
Whether to roll back part of the March 2026 price increase for some customers.

## Audience
The head of growth.

## What would change the decision
Any clear drop in retention for a segment after the increase, larger than normal month-to-month variation, makes that segment a rollback candidate. No numeric cut-off was given. Set by the asker on 2026-11-20, before any number exists.

## Analysis date
2026-09-24 (the data ends here). Run folder created on 2026-11-20. Decision, audience and the earlier definitions were reused from the frame in `outputs/2026-11-12_march-2026-price-increase-retention/`; only the threshold is new.

## Definitions to confirm
- Metric: Monthly-plan retention, meaning the share of monthly subscribers still subscribed (no `end_date`, or an `end_date` after the analysis date) at a fixed number of days after their start (assumed).
- Population: Paid monthly subscriptions. Free plans are excluded (they never end). Subscriptions starting after 2026-09-24 are excluded. Only subscribers old enough to have reached the measured age are counted, so recent starts are not read as retained or lost (assumed).
- Time window: Subscribers who started before March 2026 against those who started after, plus existing subscribers' survival through March 2026 onward, up to 2026-09-24. Payment history only begins 2025-01-01 (assumed).
- Comparison: Retention before versus after March 2026 for the monthly plan, with annual-plan subscribers as a group that did not face the $10 to $12 change. No unexposed monthly group exists, so a before and after gap cannot be separated from other changes at that time (assumed).
- "For whom": Segments by country, device type and subscriber tenure at the time of the increase, using `users` (assumed).
- "Clear drop": a gap in retention between segments or periods larger than the month-to-month spread in the months before March 2026, since no numeric cut-off exists (assumed).

## Quirks that apply
- Monthly price change: all monthly payments from 2026-03-01 are $12, including existing subscribers, so there is no unexposed monthly group.
- Free plans never end: excluded from retention.
- Future end dates: an end date after 2026-09-24 means still active.
- Future start dates: subscriptions starting after 2026-09-24 are excluded.
- September 2025 spike: touches any cohort comparison that includes 2025-09 starts; name it if it enters one.
- Trials launched 2026-08-01 and mature late: monthly starts in Jul and Sep 2026 run well above normal, and open trials must not count as lost.
- Timestamps everywhere: compare on dates.

## Tables likely involved
- `subscriptions`: plan, start and end dates for retention.
- `payments`: amounts, to confirm who paid $10 versus $12 and when.
- `users`: country and device for the "for whom" cut.

## Not in scope
- Whether the increase raised revenue overall.
- Why customers left; the data holds no reasons.
- Proving the increase caused any change; there is no unexposed monthly group.
