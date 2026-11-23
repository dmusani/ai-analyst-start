# Beam data quirks

Things we know about our own tables. Check this list before reading a number as a finding. Each quirk has an ID in backticks; table notes refer to quirks by that ID.

- **Analysis date.** `analysis_date` The data ends on 2026-09-24. That is "today" in every analysis.
- **Monthly price change.** `monthly_price_change` The monthly plan price rose from $10 to $12 in March 2026. Monthly payments before and after that point differ for that reason, not because of a data problem.
- **Trials launched 2026-08-01.** `trials_launched_2026_08_01` The trials table has no history before 2026-08-01.
- **Trials mature late.** `trials_mature_late` Trials launched on 2026-08-01 and last 14 days. A trial's outcome is only known once it matures, so recent trials show `outcome` empty. Those are still open and must not be counted as failures.
- **Free plans never end.** `free_plans_never_end` Rows with `subscriptions.plan = 'free'` have no `end_date`. Exclude them from any churn or retention calculation.
- **Future end dates.** `future_end_dates` `subscriptions.end_date` can be in the future for scheduled cancellations. A subscription with a future end date is still active today.
- **Future start dates.** `future_start_dates` A few subscriptions have a `start_date` after today: they are scheduled starts, mostly trials that will convert when they mature. Exclude rows that start after the analysis date from any count of what has happened.
- **September 2025 spike.** `september_2025_spike` September 2025 shows a signup spike of roughly five times a normal month, with a matching jump in the active base and in monthly actives. The daily-to-monthly active ratio falls from about .25 to about .21 at that point. Treat it as a known anomaly and say so whenever it enters a comparison.
- **Timestamps everywhere.** `timestamps_everywhere` Dates in the exports are timestamps. Many `users.signup_date` and subscription dates carry midnight times, others carry real times; compare on dates, not on timestamps, unless the time of day matters.
- **Sessions after the data end.** `sessions_after_data_end` 273 rows in `sessions` are dated 2026-09-25 or 2026-09-26, after the data end of 2026-09-24. Exclude them from any count of what has happened.
