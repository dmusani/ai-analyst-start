# Frame

## Question
Do trial users who binge on day one and then go quiet convert worse than steady users? The head of growth is deciding whether the onboarding emails should push trial users to spread their first week out.

## Decision
Whether the onboarding emails should push trial users to spread their first week out.

## Audience
The head of growth.

## What would change the decision
Any clear conversion gap: binge-then-quiet users converting clearly worse than steady users, by more than the gap seen between comparable groups of trial users, would justify the email change. No numeric cut-off was given. Set by the asker on 2026-11-20, before any number exists.

## Analysis date
2026-09-24 (the data ends here). Run folder created on 2026-11-20.

## Definitions to confirm
- Metric: Trial conversion, meaning the share of trials whose outcome is `converted` (became a paid plan at the end of the 14-day trial) among trials with a known outcome (assumed).
- Population: Trials that started on or before 2026-09-10, so the 14-day trial has closed by 2026-09-24 and the outcome is known. Trials that ended in cancellation during the first 7 days are set aside, because a user who has already left cannot show a first-week pattern, and counting them as "quiet" would make the quiet group look worse by construction; their number is reported (assumed).
- Time window: Trials started 2026-08-01 to 2026-09-10; behaviour measured over the 7 days from each trial's start date (day one is the start date; session dates carry no time of day) (assumed).
- Behaviour groups: Binge-then-quiet = a large share of first-week activity on day one and little on days two to seven. Steady = activity spread over several days of the week. Everyone else is a reference group. The cut-offs for "large share", "little" and "several days" are not given; they will be set from the data before looking at conversion, and tested at a second set of cut-offs (assumed).
- Comparison: Conversion of binge-then-quiet users against steady users, with all other trial users as a reference. Percentage points and relative percent both named (assumed).
- "Clear gap": a gap larger than the spread in conversion between comparable splits of the same trials (for example, by start week or by device) (assumed).

## Quirks that apply
- Trials mature late: trials launched 2026-08-01 and last 14 days; trials started after 2026-09-10 have no final outcome and are left out.
- Sessions after the data end: 273 session rows are dated after 2026-09-24; they fall outside any first week measured here but must be excluded from anything that counts what has happened.
- Timestamps everywhere: session dates are dates only, so "day one" is the calendar day the trial started.
- Sessions is a very large table (4.3 million rows): queries are aggregates only, never raw rows, and wide group-bys by user are avoided.
- August 2026 sessions run about 20% higher per day than July, unexplained; trial users may be part of it, and this is not investigated here.

## Tables likely involved
- `trials`: start date, outcome (converted or canceled) and when the outcome was recorded.
- `sessions`: first-week activity per trial user (sessions and minutes by day). Queried in the database, aggregates only.
- `users`: device type and country, for checking that the result is not one segment.
- `subscriptions`: to confirm that converted trials became paid plans.

## Not in scope
- Whether sending an email would change how users behave. The data shows how behaviour patterns relate to conversion, not whether a nudge moves a user from one pattern to the other, and holds no email data.
- Revenue or lifetime value after conversion.
- Why users go quiet.
