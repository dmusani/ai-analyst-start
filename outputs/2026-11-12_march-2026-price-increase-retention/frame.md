# Frame

## Question
Did the March 2026 price increase hurt retention, and for whom? The head of growth is deciding whether to roll back part of the increase for some customers.

## Decision
Whether to roll back part of the March 2026 price increase for some customers.

## Audience
The head of growth.

## What would change the decision
Not stated.

## Analysis date
2026-09-24 (the data ends here). Run folder created on 2026-11-12.

## Definitions to confirm
- Metric: Monthly-plan retention, meaning the share of monthly subscribers still subscribed (no `end_date`, or an `end_date` after the analysis date) at a fixed number of days after their start (assumed).
- Population: Paid monthly subscriptions. Free plans are excluded (they never end). Subscriptions starting after 2026-09-24 are excluded. Only subscribers old enough to have reached the measured age are counted, so recent starts are not read as retained or lost (assumed).
- Time window: Pre-increase subscribers (starting well before March 2026) against post-increase subscribers, plus existing subscribers' survival through March 2026 onward, up to 2026-09-24. Payment history only begins 2025-01-01 (assumed).
- Comparison: Retention before versus after March 2026 for the same monthly plan, and annual-plan subscribers as a group that did not face the $10 to $12 change. No unexposed monthly group exists, so a before/after gap cannot be separated from other changes at that time (assumed).
- "For whom": Segments by country, device type and subscriber tenure at the time of the increase, using `users` (assumed).

## Quirks that apply
- Monthly price change: all monthly payments from 2026-03-01 are $12, including existing subscribers, so there is no unexposed monthly group.
- Free plans never end: excluded from retention.
- Future end dates: an end date after 2026-09-24 means still active.
- Future start dates: subscriptions starting after 2026-09-24 are excluded.
- September 2025 spike and the July and September 2026 monthly start spikes: may distort cohort comparisons and must be named if they enter one.
- Timestamps everywhere: compare on dates.

## Tables likely involved
- `subscriptions`: plan, start and end dates for retention.
- `payments`: amounts, to confirm who paid $10 versus $12 and when.
- `users`: country and device for the "for whom" cut.

## Not in scope
- Whether the increase raised revenue overall.
- Why customers left; the data holds no reasons.
- Proving the increase caused any change; there is no unexposed monthly group.
