# Review: Do trial users who binge on day one and then go quiet convert worse than steady users?

## Verdict
**Think on it**: the numbers hold and reproduce by a second route, but the headline gap is mostly "quiet versus active", and the brief must say so before anyone changes the emails.

Round: 1

## Findings
### 1. The gap is driven by going quiet, not by the day-one binge (Think on it)
- Where: `conversion_by_group.csv` (headline); `conversion_by_day_one_and_later_days.csv` and the line chart.
- Problem: the headline compares binge-then-quiet with steady users, and the 85-point gap reads as "bingeing hurts". The grid shows the drop comes from how many days users come back. Among quiet users, a big day one is only slightly worse than a small one, and that difference is inside the noise for a group this small. Among steady users, a big day one is about 10 points lower, so a big day one carries some penalty, but the main driver is later activity.
- Evidence: conversion by days active on days 2 to 7, all day-one sizes: 0 to 1 days 5.7%, 2 to 3 days 11.9%, 4 days 34.7%, 5 to 6 days 86.1%. Quiet users with 6+ sessions on day one 6.9% (4 of 58), with 0 to 2 sessions 10.2% (22 of 215), gap -3.3 pp. Steady users with 6+ sessions on day one 77.8% (266 trials), with 0 to 2 sessions 88.2% (246), gap -10.4 pp.
- Fix: the brief should lead with "users who come back through the week convert, users who go quiet do not", and treat the binge as a smaller, separate effect. The grid was added after the first conversion result was seen; the brief should say so.
- Kind: for the brief

### 2. Reading the pattern as something an email can change goes beyond the data (Think on it)
- Where: whole analysis; frame section "Not in scope".
- Problem: the data shows which first-week patterns go with converting, not whether a nudge moves a user from one pattern to another. Users who plan to cancel may go quiet because they have decided to leave, so quiet may be a symptom rather than a cause. The 204 trials that were cancelled in the first week are set aside and none converted, so the analysed population is already more engaged than all matured trials.
- Evidence: 1,553 matured trials, 204 resolved in the first 7 days (204 canceled, 0 converted); 1,349 analysed, 828 converted (61.4%), against 828 of 1,553 (53.3%) before setting those aside.
- Fix: say in the brief that this shows association only, that no email data exists, and that a test (spread-out nudge against no nudge) is the way to find out.
- Kind: for the brief

### 3. The binge-then-quiet group is small, and "steady" is close to "converted" by construction (Think on it)
- Where: `conversion_by_group.csv`; `gap_by_segment.csv`.
- Problem: the group is 58 trials (4.3% of the 1,349) at the main cut-offs and 91 at the alternative. Steady users convert at 92%, which is close to the ceiling, partly because being active on 5 or more of 6 days is itself what a user about to convert tends to do. Splits by start week have as few as 3 binge trials, so week-by-week figures are not reliable.
- Evidence: A: 4 of 58 (95% range 2.7% to 16.4%) against 670 of 726 (92.3%); B: 8 of 91 (4.5% to 16.4%) against 613 of 660 (92.9%). Smallest binge groups: country 9 (India), start week 3 (week 2).
- Fix: report both cut-off sets, give the group size next to every rate, and do not quote segment-level gaps for splits under 10 binge trials.
- Kind: for the brief

## What's solid
The counts reproduce. The headline groups and two full segment cuts (device at the main cut-offs, start week at the alternative) match a second SQL formulation cell for cell, the groups and segments add back to the 1,349 analysed trials in both cut-off sets, the session join returns one row per trial, and only trials started by 2026-09-10 are used so every outcome is final. The gap is large in every split and in both cut-off sets (-62 to -95 pp), far outside the 9.7-point range of steady-user conversion across device and country, so "worse" is clear whichever way it is cut.

## One question to sit with
If users who stay active convert whether or not they binged on day one, is the email meant to change what users do on day one, or to bring them back on days two to seven, and which of those would the head of growth actually be testing?

## Mechanics
| Check | Result | Evidence |
| --- | --- | --- |
| Reruns, tables stable | Pass | Exit 0; md5 of all 9 files in `data/` identical across runs. |
| Stays in its lane | Pass, with a note | Reads only the saved result tables in the run folder's `data/` (pulled by `queries.sql`), writes inside the run folder, prints aggregates only. Nothing in the repo's `data/` is read or changed. |
| Checks ran | Pass, with a note | `parts_sum_to_total` on the set-aside plus analysed trials and on every group and segment cut for both cut-off sets; session join fan-out recorded (1,349 in, 1,349 rows, 1,349 distinct); matured trials handled in SQL by start date (`matured_only` needs raw rows). |
| Every number traces | Pass | Each printed rate comes from `conversion_by_group.csv`, `gap_by_segment.csv` or `conversion_by_day_one_and_later_days.csv`. |
| Independent recompute | Pass | SQL with `sum(case)` and `between` instead of `filter`: device cut at A: bq 25/2, 18/1, 15/1; st 240/229, 256/243, 230/198; ot 197/56, 181/52, 187/46. Start-week cut at B: bq 20/2, 15/2, 11/1, 11/2, 17/0, 17/1; st 127/117, 101/92, 115/109, 94/87, 119/109, 104/99; ot 106/37, 115/48, 96/35, 99/37, 96/26, 86/24. All equal the saved tables, and they add to the script's A and B totals (A: 58 and 4; 726 and 670; B: 91 and 8; 660 and 613). |
| Parts sum to totals | Pass | Analysed 1,349 in every cut; grid 1,349 trials and 828 converted. |
| Charts match tables | Pass | Two charts, made through `helpers.charts`, titles state the takeaway; values match `conversion_by_group.csv` and the grid. |

## Reasoning
| Check | Result | Evidence |
| --- | --- | --- |
| Answers the question | Yes, with a limit | Binge-then-quiet users convert far worse than steady users (6.9% against 92.3%); finding 1 says what drives it. |
| Speaks to the decision | Partly | The "clear gap" bar (larger than the spread across comparable splits) is met, but whether an email can move users is not shown (finding 2). |
| Every number compared | Pass | Each rate has the steady group and everyone else beside it; units named as pp and relative percent. |
| Quirks handled | Pass | Trials mature late (started by 2026-09-10 only); sessions after the data end (sessions window ends before them); date-only timestamps (day one is the start date); sessions queried with aggregates only. The August 2026 session rise is not investigated. |
| Population | Pass, with a note | Matured trials with a first full week; first-week cancellations set aside (204) and counted. |
| Segmented | Pass | Device, country, start week; the gap has the same sign everywhere. |
| Claims vs evidence | See findings 1 and 2 | Wording must stay at "goes with", not "causes". |
| Sanity | Pass | Rates 0% to 100%; counts at most 1,349; 828 converted matches the trials table. |
| Frame definitions | Matches | Population, window and groups follow the frame; cut-offs were set from the distribution before conversion was looked at, and a second set was tested. The grid was added later (finding 1). |

## Not checked
- Whether sending an email would change behaviour; there is no email data.
- Whether users who plan to cancel go quiet for that reason, so quiet is a symptom (finding 2).
- Day one is the start date, and a trial that starts late in the day has only part of a day one; trials were not split by start time of day.
- Binge and quiet defined by sessions and days active only; minutes listened were not used.
- Splits finer than device, country and start week, and groups crossed with each other.
- Raw result tables were copied by hand from query output; two full cuts were matched to the database, not every cell of the grid or the country cut.
- The August 2026 session rise (about 20% a day higher than July) and whether trial users account for it.
- All definitions in `frame.md` are still marked "(assumed)".
