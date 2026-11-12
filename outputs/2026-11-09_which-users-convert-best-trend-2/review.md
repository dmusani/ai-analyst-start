# Review: Which kinds of users convert best from trial to paid, and is conversion getting better or worse over time?

## Verdict
**Think on it**: the numbers reproduce by a second route, but the iOS drop between halves is not tested and the country lean is a post hoc contrast.

Round: 1

## Findings
### 1. iOS conversion falls 5.2 percentage points between halves, and the script does not test it (Think on it)
- Where: `data/trend_by_segment.csv`, iOS row; `data/significance.csv` has no test for it.
- Problem: the overall trend is flat, but iOS goes from 59.6% to 54.4% while Web and Android do not fall. A reader could take it as iOS decaying, or ignore it.
- Evidence: 270 trials in the first half, 248 in the second; my one-off two-group z is 1.19 against a cutoff of 1.96, so it is within noise.
- Fix: carry it into the brief as "not distinguishable from noise, worth watching". Adding the z to the script is optional.
- Kind: for the brief

### 2. The US lead is a post hoc contrast and country overall is not significant (Think on it)
- Where: `data/significance.csv`, country rows.
- Problem: US vs the other three scores 2.26 but was chosen after seeing the data; the four-country test scores 5.38 against 7.81.
- Evidence: US vs EU alone scores 1.95 against 1.96.
- Fix: describe country as a lean, not a finding.
- Kind: for the brief

## What's solid
The join does not fan out, every trial has one user, and segment counts add back to 1,553 trials and 828 conversions. Only trials whose 14 days had closed are counted, so the open trials do not pull the rate down. Device and overall figures match my recompute.

## One question to sit with
Does a device gap in trial conversion mean the head of growth can buy more iOS users, or does it only describe who already arrives?

## Mechanics
| Check | Result | Evidence |
| --- | --- | --- |
| It reruns | Pass | Result tables identical across two runs |
| Stays in its lane | Pass | Reads `data/`, writes only in the run folder, aggregates only |
| Checks ran | Pass | Join fan-out, matured only, date boundaries, parts sum to total all printed |
| Numbers trace | Pass | Each printed number is in a saved table |
| Independent recompute | Pass | 1,553 trials, 53.3% overall; iOS 57.1%, Android 54.6%, Web 48.1%; US 56.7%, Rest 52.1%, India 50.7%, EU 50.0%; August 53.1% vs September 53.9% |
| Parts sum to totals | Pass | 0.00% apart for country, device and week |
| Charts match tables | Pass | Three charts, takeaway titles, drawn from the saved tables |

## Reasoning
| Check | Result | Evidence |
| --- | --- | --- |
| Answers the question | Pass | Segments by device and country, trend by start week |
| Speaks to the decision | Pass | Device gap is above the noise level; no threshold was stated |
| Numbers compared | Pass | Each carries overall and rest-of-group gaps in percentage points |
| Quirks handled | Pass | Unmatured trials, scheduled starts and timestamps handled; others do not apply |
| Frame definitions | Pass | Same metric, population, window and comparison as `frame.md` |
| Claims fit evidence | Think on it | See findings 1 and 2 |

## Not checked
- Whether "converted" means a paid subscription exists; not matched against `subscriptions`.
- 520 trials whose window had not closed by 2026-09-24 (418 of them with no outcome yet) are excluded, so trials started after 2026-09-10 are unread.
- Acquisition channel, cost and what each segment is worth after converting: no data.
- Definitions marked "(assumed)" in the frame were not confirmed.
