# Frame

## Question
Which kinds of users convert best from free trial to paid, and is conversion getting better or worse over time? The head of growth is deciding where to put next quarter's acquisition budget.

## Decision
Where to put next quarter's acquisition budget.

## Audience
The head of growth.

## What would change the decision
A user segment that converts materially better than the others would shift budget toward that segment. The threshold (how big a gap counts) is not stated. No trend trigger is recorded. (Carried over from the earlier run of this same question in this session, outputs/2026-11-09_which-users-convert-best-trend; not asked again.)

## Analysis date
2026-09-24 (the data ends here). Run folder created on 2026-11-09.

## Definitions to confirm
- Metric: trial conversion rate = converted / (converted + canceled), among trials with a non-null `outcome` (assumed; open trials excluded).
- Population: trials whose 14-day window had closed by 2026-09-24 (`ends_at` on or before that date) and that have an outcome, one trial per user (assumed). "Kinds of users" = `users.country` and `users.device_type` (assumed; no acquisition channel column exists). Every trial starts on the user's signup day, so signup tenure cannot separate users (checked in the data before framing, aggregates only).
- Time window: trials started 2026-08-01 to 2026-09-10 (the last start date whose window has closed), cut by start week and by first vs second half (assumed).
- Comparison: each segment against the overall rate and against the rest, in percentage points; trend against the earlier part of the same window. No benchmark and no pre-August history exist.

## Quirks that apply
- Trials mature late: trials last 14 days, so trials started after 2026-09-10 are still open or only partly resolved; they are excluded.
- Trials launched 2026-08-01: "over time" covers about seven weeks, which limits any trend claim.
- Future start dates: anything starting after 2026-09-24 is a scheduled start and is excluded.
- Timestamps everywhere: compare on dates, not timestamps.
- September 2025 spike and monthly price change: outside the trial window, not expected to touch this question.

## Tables likely involved
- `trials`: one row per trial with its outcome; the conversion measure.
- `users`: country and device type for the segments, joined on `user_id`.

## Not in scope
- Which acquisition channel or campaign brings the best users (no channel data).
- Revenue, plan mix, cost per acquisition or retention after conversion.
- Causes: why a segment converts better, or what budget would do to its rate.
- Any trend before 2026-08-01 (no trial data).
