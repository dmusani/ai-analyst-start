"""Do trial users who binge on day one and then go quiet convert worse than steady users?

Run from the repo root:
    poetry run python outputs/2026-11-20_binge-then-quiet-trial-conversion/analysis.py

Input: aggregate result tables in data/raw_*.csv, pulled from course-db by queries.sql.
Population: trials started 2026-08-01 to 2026-09-10 (14 days closed by 2026-09-24) whose
outcome was recorded on or after day 7, so a full first week is observable. Day one is
the trial start date (session dates carry no time of day).
Cut-offs (set from the activity distribution before conversion was looked at):
  A: binge-then-quiet = 6+ sessions on day one and active on 3 or fewer of days 2-7;
     steady = active on 5+ of days 2-7 and day one is under 30% of the week's sessions.
  B: binge-then-quiet = day one is 40%+ of the week's sessions (4+ sessions) and active on 3 or fewer
     of days 2-7; steady = active on 5+ of days 2-7 and day one under 25%.
Gaps are in percentage points (pp) unless marked relative.
"""

import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from helpers import charts, checks  # noqa: E402

RUN = Path(__file__).resolve().parent
DATA = RUN / "data"
CHARTS = RUN / "charts"

pop = pd.read_csv(DATA / "raw_population.csv").iloc[0]
grp = pd.read_csv(DATA / "raw_group_conversion.csv")
grid = pd.read_csv(DATA / "raw_activity_grid.csv")
join = pd.read_csv(DATA / "raw_join_check.csv").iloc[0]
GROUPS = ["binge_then_quiet", "steady", "other"]
NICE = {"binge_then_quiet": "Binge on day one, then quiet", "steady": "Steady", "other": "Everyone else"}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


# ---------------------------------------------------------------- checks
print("== Checks ==")
print(f"Matured trials (started by 2026-09-10): {int(pop['matured_trials']):,}. "
      f"Set aside because the outcome came in the first 7 days: {int(pop['resolved_in_first_7_days']):,} "
      f"({int(pop['early_canceled']):,} canceled, {int(pop['early_converted']):,} converted). "
      f"Analysed: {int(pop['analysed']):,}.")
r = checks.parts_sum_to_total([pop["resolved_in_first_7_days"], pop["analysed"]], float(pop["matured_trials"]), tolerance=0)
print("Set-aside plus analysed add back to matured trials:", r["summary"])
fan_ok = join["population_rows"] == join["after_session_join"] == join["distinct_trials"]
print(f"Session join: {int(join['population_rows']):,} trials in, {int(join['after_session_join']):,} rows out, "
      f"{int(join['distinct_trials']):,} distinct trials ({'no fan-out' if fan_ok else 'FAN-OUT'}).")
for cs in ["A", "B"]:
    for dim in ["all", "device_type", "country", "start_week"]:
        d = grp[(grp["cutoffs"] == cs) & (grp["dimension"] == dim)]
        r = checks.parts_sum_to_total([d["trials"].sum()], float(pop["analysed"]), tolerance=0)
        if not r["ok"]:
            print(f"FAIL cut-offs {cs}, {dim}: {r['summary']}")
        r2 = checks.parts_sum_to_total([d["converted"].sum()], float(grp[(grp["cutoffs"] == cs) & (grp["dimension"] == "all")]["converted"].sum()), tolerance=0)
        if not r2["ok"]:
            print(f"FAIL cut-offs {cs}, {dim} converted: {r2['summary']}")
print("Groups and segments add back to the analysed total (trials and conversions), cut-offs A and B: checked, no failure printed above.")
print(f"Grid: {int(grid['trials'].sum()):,} trials, {int(grid['converted'].sum()):,} converted "
      f"(analysed {int(pop['analysed']):,}).")

# ---------------------------------------------------------------- headline
rows = []
for cs in ["A", "B"]:
    d = grp[(grp["cutoffs"] == cs) & (grp["dimension"] == "all")].set_index("grp")
    for g in GROUPS:
        n, k = int(d.loc[g, "trials"]), int(d.loc[g, "converted"])
        lo, hi = wilson(k, n)
        rows.append({"cutoffs": cs, "group": g, "trials": n, "converted": k,
                     "conversion_pct": 100 * k / n, "ci_low_pct": lo, "ci_high_pct": hi})
head = pd.DataFrame(rows)
head.round(2).to_csv(DATA / "conversion_by_group.csv", index=False)

print("\n== Headline: trial conversion by first-week pattern ==")
for cs in ["A", "B"]:
    h = head[head["cutoffs"] == cs].set_index("group")
    for g in GROUPS:
        x = h.loc[g]
        print(f"Cut-offs {cs}, {NICE[g]:<30} {int(x['converted']):>4} of {int(x['trials']):>4} = "
              f"{x['conversion_pct']:5.1f}%  (95% range {x['ci_low_pct']:.1f}% to {x['ci_high_pct']:.1f}%)")
    b, s, o = h.loc["binge_then_quiet"], h.loc["steady"], h.loc["other"]
    print(f"  Binge-then-quiet vs steady: {b['conversion_pct'] - s['conversion_pct']:+.1f} pp "
          f"({(b['conversion_pct'] / s['conversion_pct'] - 1) * 100:+.0f}% relative). "
          f"Vs everyone else: {b['conversion_pct'] - o['conversion_pct']:+.1f} pp.")

# ---------------------------------------------------------------- segments
seg_rows = []
for cs in ["A", "B"]:
    for dim in ["device_type", "country", "start_week"]:
        d = grp[(grp["cutoffs"] == cs) & (grp["dimension"] == dim)]
        for s in sorted(d["segment"].astype(str).unique()):
            x = d[d["segment"].astype(str) == s].set_index("grp")
            b, st, o = x.loc["binge_then_quiet"], x.loc["steady"], x.loc["other"]
            seg_rows.append({
                "cutoffs": cs, "dimension": dim, "segment": s,
                "binge_trials": int(b["trials"]), "binge_conv_pct": 100 * b["converted"] / b["trials"],
                "steady_trials": int(st["trials"]), "steady_conv_pct": 100 * st["converted"] / st["trials"],
                "other_conv_pct": 100 * o["converted"] / o["trials"],
                "gap_pp": 100 * b["converted"] / b["trials"] - 100 * st["converted"] / st["trials"],
            })
seg = pd.DataFrame(seg_rows)
seg.round(2).to_csv(DATA / "gap_by_segment.csv", index=False)
print("\n== Is the gap the same in every split? (binge-then-quiet minus steady, pp) ==")
for cs in ["A", "B"]:
    for dim in ["device_type", "country", "start_week"]:
        d = seg[(seg["cutoffs"] == cs) & (seg["dimension"] == dim)]
        small = d[d["binge_trials"] < 10]
        print(f"Cut-offs {cs}, {dim:<12} gap from {d['gap_pp'].max():+.1f} to {d['gap_pp'].min():+.1f} pp "
              f"(binge group sizes {int(d['binge_trials'].min())} to {int(d['binge_trials'].max())}; "
              f"{len(small)} split(s) with under 10 binge trials)")
steady_spread = seg[(seg["cutoffs"] == "A") & (seg["dimension"] != "start_week")]["steady_conv_pct"]
print(f"Spread of steady-user conversion across device and country splits (A): "
      f"{steady_spread.min():.1f}% to {steady_spread.max():.1f}%, a range of {steady_spread.max() - steady_spread.min():.1f} pp.")

# ---------------------------------------------------------------- binge vs quiet
grid["conv_pct"] = 100 * grid["converted"] / grid["trials"]
grid.round(2).to_csv(DATA / "conversion_by_day_one_and_later_days.csv", index=False)
DAY1 = {"1_day1_0to2": "0 to 2 sessions on day one", "2_day1_3to5": "3 to 5 sessions on day one",
        "3_day1_6plus": "6 or more sessions on day one"}
LATER = {"1_days_0to1": "0 to 1 days", "2_days_2to3": "2 to 3 days", "3_days_4": "4 days", "4_days_5to6": "5 to 6 days"}
print("\n== Day-one size against days active later in the week (conversion %, trials) ==")
piv = grid.pivot(index="later_days", columns="day_one", values="conv_pct")
npiv = grid.pivot(index="later_days", columns="day_one", values="trials")
for ld in LATER:
    print(f"Active {LATER[ld]:<12} " + "  ".join(
        f"{DAY1[c][:20]:<21} {piv.loc[ld, c]:5.1f}% (n={int(npiv.loc[ld, c])})" for c in DAY1))
quiet = grid[grid["later_days"].isin(["1_days_0to1", "2_days_2to3"])]
q_big = quiet[quiet["day_one"] == "3_day1_6plus"]
q_small = quiet[quiet["day_one"] == "1_day1_0to2"]
qb = 100 * q_big["converted"].sum() / q_big["trials"].sum()
qs = 100 * q_small["converted"].sum() / q_small["trials"].sum()
print(f"\nQuiet users (active 0 to 3 of days 2-7): 6+ sessions on day one {qb:.1f}% "
      f"({int(q_big['converted'].sum())} of {int(q_big['trials'].sum())}); 0 to 2 sessions on day one {qs:.1f}% "
      f"({int(q_small['converted'].sum())} of {int(q_small['trials'].sum())}); gap {qb - qs:+.1f} pp.")
act = grid[grid["later_days"] == "4_days_5to6"].set_index("day_one")
print(f"Steady users (active 5 to 6 of days 2-7): 6+ sessions on day one "
      f"{act.loc['3_day1_6plus', 'conv_pct']:.1f}% (n={int(act.loc['3_day1_6plus', 'trials'])}); "
      f"0 to 2 sessions {act.loc['1_day1_0to2', 'conv_pct']:.1f}% (n={int(act.loc['1_day1_0to2', 'trials'])}); "
      f"gap {act.loc['3_day1_6plus', 'conv_pct'] - act.loc['1_day1_0to2', 'conv_pct']:+.1f} pp.")
by_later = grid.groupby("later_days")[["trials", "converted"]].sum()
by_later["conv_pct"] = 100 * by_later["converted"] / by_later["trials"]
print("Conversion by days active later in the week, all day-one sizes: " + ", ".join(
    f"{LATER[i]} {r.conv_pct:.1f}% (n={int(r.trials)})" for i, r in by_later.iterrows()))

# ---------------------------------------------------------------- charts
hA = head[head["cutoffs"] == "A"].set_index("group")
fig = charts.bar(
    [NICE[g] for g in GROUPS], [round(hA.loc[g, "conversion_pct"], 1) for g in GROUPS],
    f"Binge-then-quiet trial users convert at {hA.loc['binge_then_quiet', 'conversion_pct']:.0f}%, "
    f"against {hA.loc['steady', 'conversion_pct']:.0f}% for steady users",
    highlight=[NICE["binge_then_quiet"]], ylabel="Trials that converted to paid (%)",
    source="Trials started 2026-08-01 to 2026-09-10. Cut-offs A. Source: course-db trials, sessions.",
)
charts.save(fig, CHARTS / "conversion_by_group.png")

series = {DAY1[c]: [round(piv.loc[ld, c], 1) for ld in LATER] for c in DAY1}
fig = charts.line(
    list(LATER.values()), series,
    "Conversion tracks how many days users come back far more than how big day one was",
    highlight=[DAY1["3_day1_6plus"]], ylabel="Trials that converted to paid (%)",
    source="x axis: days active among days 2 to 7 of the trial. Source: course-db trials, sessions.",
)
charts.save(fig, CHARTS / "conversion_by_day_one_and_later_days.png")

print("\nCharts saved to", CHARTS)
