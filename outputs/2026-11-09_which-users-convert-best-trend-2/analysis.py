"""Which kinds of users convert best from trial to paid, and is conversion changing over time?

Run from the repo root:
    poetry run python outputs/2026-11-09_which-users-convert-best-trend-2/analysis.py

Rates are percentages (0-100). Gaps are percentage points (pp) unless marked relative.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from helpers import charts, checks  # noqa: E402

RUN = Path(__file__).resolve().parent
DATA_OUT = RUN / "data"
CHART_OUT = RUN / "charts"
DATA_OUT.mkdir(exist_ok=True)

AS_OF = "2026-09-24"  # the data ends here
Z = 1.96


def wilson(conv: int, n: int) -> tuple[float, float]:
    """95% Wilson interval for a proportion, returned in percent."""
    if n == 0:
        return (np.nan, np.nan)
    p = conv / n
    denom = 1 + Z**2 / n
    centre = (p + Z**2 / (2 * n)) / denom
    half = Z * np.sqrt(p * (1 - p) / n + Z**2 / (4 * n**2)) / denom
    return (100 * (centre - half), 100 * (centre + half))


def rate_table(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Conversion rate, count and interval per group, plus gap to the rest in pp."""
    rows = []
    total_conv = int((df["outcome"] == "converted").sum())
    total_n = len(df)
    for key, g in df.groupby(by, observed=True):
        conv = int((g["outcome"] == "converted").sum())
        n = len(g)
        lo, hi = wilson(conv, n)
        rest_conv, rest_n = total_conv - conv, total_n - n
        rest_rate = 100 * rest_conv / rest_n
        rows.append({
            by: key, "trials": n, "converted": conv,
            "conversion_pct": round(100 * conv / n, 1),
            "ci_low_pct": round(lo, 1), "ci_high_pct": round(hi, 1),
            "overall_pct": round(100 * total_conv / total_n, 1),
            "gap_vs_overall_pp": round(100 * conv / n - 100 * total_conv / total_n, 1),
            "gap_vs_rest_pp": round(100 * conv / n - rest_rate, 1),
        })
    return pd.DataFrame(rows).sort_values("conversion_pct", ascending=False)


# --- Load -------------------------------------------------------------------
trials = pd.read_csv("data/trials.csv", parse_dates=["started_at", "ends_at", "outcome_at"])
users = pd.read_csv("data/users.csv", parse_dates=["signup_date"])

print("== Checks ==")
fan = checks.join_fan_out(trials, users[["user_id", "country", "device_type"]], on="user_id")
print(fan["summary"])
df = trials.merge(users[["user_id", "country", "device_type"]], on="user_id", how="left")
assert df["country"].notna().all(), "trials without a matching user"
print(f"One trial per user: {trials['user_id'].is_unique}.")

# Signup tenure cannot separate users if every trial starts on the signup day.
days_to_trial = (df.merge(users[["user_id", "signup_date"]], on="user_id")
                 .eval("started_at.dt.normalize() - signup_date.dt.normalize()")
                 .dt.days)
print(f"Days from signup to trial start: min {days_to_trial.min()}, max {days_to_trial.max()} "
      f"({int((days_to_trial != 0).sum()):,} trials not on the signup day).")

# Exclude scheduled starts after the analysis date (none expected).
future = int((df["started_at"] > pd.Timestamp(AS_OF) + pd.Timedelta(days=1)).sum())
print(f"Trials starting after {AS_OF}: {future}.")

n_open = int(df["outcome"].isna().sum())
print(f"Open trials (null outcome): {n_open:,} of {len(df):,}.")

mat = checks.matured_only(df, "ends_at", as_of=pd.Timestamp(AS_OF) + pd.Timedelta(days=1))
print(mat["summary"])
matured = mat["kept"]
# Matured trials must all be resolved; anything else is a data problem.
unresolved_matured = int(matured["outcome"].isna().sum())
print(f"Matured trials with no outcome: {unresolved_matured}.")
matured = matured[matured["outcome"].notna()].copy()
matured["start_date"] = matured["started_at"].dt.normalize()
matured["week"] = matured["start_date"].dt.to_period("W-SUN").dt.start_time

edge = checks.date_boundaries(matured, "start_date", freq="W-SUN")
print(edge["summary"])

# --- Headline ---------------------------------------------------------------
n_m = len(matured)
conv_m = int((matured["outcome"] == "converted").sum())
overall = 100 * conv_m / n_m
lo, hi = wilson(conv_m, n_m)
print("\n== Headline ==")
print(f"Overall conversion, matured trials started {matured['start_date'].min().date()} "
      f"to {matured['start_date'].max().date()}: {overall:.1f}% "
      f"({conv_m:,} of {n_m:,}; 95% interval {lo:.1f}-{hi:.1f}%). "
      "No benchmark or earlier period available.")

# Sensitivity: all resolved trials, including unmatured cohorts' early outcomes.
resolved = df[df["outcome"].notna()]
res_rate = 100 * (resolved["outcome"] == "converted").mean()
print(f"Sensitivity: all resolved trials (incl. unmatured cohorts) {res_rate:.1f}% "
      f"({len(resolved):,} trials) vs matured-only {overall:.1f}% "
      f"({res_rate - overall:+.1f} pp).")

# --- Segments ---------------------------------------------------------------
seg_country = rate_table(matured, "country")
seg_device = rate_table(matured, "device_type")
seg_country.to_csv(DATA_OUT / "conversion_by_country.csv", index=False)
seg_device.to_csv(DATA_OUT / "conversion_by_device.csv", index=False)

for name, seg in (("country", seg_country), ("device_type", seg_device)):
    chk = checks.parts_sum_to_total(seg["trials"], n_m)
    print(f"{name} trials: {chk['summary']}")
    chk = checks.parts_sum_to_total(seg["converted"], conv_m)
    print(f"{name} conversions: {chk['summary']}")

print("\nBy country (gap in percentage points):")
print(seg_country.to_string(index=False))
print("\nBy device (gap in percentage points):")
print(seg_device.to_string(index=False))

# Country x device, small cells flagged.
cross = (
    matured.assign(conv=(matured["outcome"] == "converted").astype(int))
    .groupby(["country", "device_type"])
    .agg(trials=("conv", "size"), converted=("conv", "sum"))
    .reset_index()
)
cross["conversion_pct"] = (100 * cross["converted"] / cross["trials"]).round(1)
cross["gap_vs_overall_pp"] = (cross["conversion_pct"] - overall).round(1)
cross = cross.sort_values("conversion_pct", ascending=False)
cross.to_csv(DATA_OUT / "conversion_by_country_device.csv", index=False)
print("\nCountry x device:")
print(cross.to_string(index=False))

# --- Trend ------------------------------------------------------------------
weekly = (
    matured.assign(conv=(matured["outcome"] == "converted").astype(int))
    .groupby("week")
    .agg(trials=("conv", "size"), converted=("conv", "sum"))
    .reset_index()
)
weekly["conversion_pct"] = (100 * weekly["converted"] / weekly["trials"]).round(1)
ci = weekly.apply(lambda r: wilson(int(r["converted"]), int(r["trials"])), axis=1)
weekly["ci_low_pct"] = [round(c[0], 1) for c in ci]
weekly["ci_high_pct"] = [round(c[1], 1) for c in ci]
weekly["week"] = weekly["week"].dt.date
weekly.to_csv(DATA_OUT / "conversion_by_start_week.csv", index=False)
print("\nBy start week (matured trials):")
print(weekly.to_string(index=False))
chk = checks.parts_sum_to_total(weekly["trials"], n_m)
print(f"Weekly trials: {chk['summary']}")

# First half vs second half of the matured window, in pp, with a two-proportion z-test.
mid = matured["start_date"].min() + (matured["start_date"].max() - matured["start_date"].min()) / 2
early = matured[matured["start_date"] <= mid]
late = matured[matured["start_date"] > mid]
pe = (early["outcome"] == "converted").mean() * 100
pl = (late["outcome"] == "converted").mean() * 100
pooled = (matured["outcome"] == "converted").mean()
se = np.sqrt(pooled * (1 - pooled) * (1 / len(early) + 1 / len(late))) * 100
z = (pl - pe) / se
print(f"\nFirst half (to {mid.date()}): {pe:.1f}% ({len(early):,} trials); "
      f"second half: {pl:.1f}% ({len(late):,} trials); change {pl - pe:+.1f} pp "
      f"({100 * (pl - pe) / pe:+.1f}% relative); z = {z:.2f}.")
pd.DataFrame([{
    "split_date": mid.date(), "early_pct": round(pe, 1), "late_pct": round(pl, 1),
    "change_pp": round(pl - pe, 1), "change_relative_pct": round(100 * (pl - pe) / pe, 1),
    "z": round(z, 2), "early_trials": len(early), "late_trials": len(late),
}]).to_csv(DATA_OUT / "trend_first_vs_second_half.csv", index=False)

# Trend by segment (first vs second half), to see whether movement is concentrated.
rows = []
for by in ("country", "device_type"):
    for key, g in matured.groupby(by):
        e, l = g[g["start_date"] <= mid], g[g["start_date"] > mid]
        re_, rl = (e["outcome"] == "converted").mean() * 100, (l["outcome"] == "converted").mean() * 100
        rows.append({"dimension": by, "segment": key, "early_pct": round(re_, 1),
                     "late_pct": round(rl, 1), "change_pp": round(rl - re_, 1),
                     "early_trials": len(e), "late_trials": len(l)})
seg_trend = pd.DataFrame(rows)
seg_trend.to_csv(DATA_OUT / "trend_by_segment.csv", index=False)
print("\nFirst vs second half by segment:")
print(seg_trend.to_string(index=False))

# Mix shift: share of trials by country in each half.
mix = pd.DataFrame({
    "early_share_pct": (100 * early["country"].value_counts(normalize=True)).round(1),
    "late_share_pct": (100 * late["country"].value_counts(normalize=True)).round(1),
}).reset_index(names="country")
mix.to_csv(DATA_OUT / "country_mix_by_half.csv", index=False)
print("\nCountry mix of trials by half (percent of trials):")
print(mix.to_string(index=False))

# --- Significance -----------------------------------------------------------
def chi_square(seg: pd.DataFrame) -> float:
    """Chi-square statistic for conversion differing across the groups of a segment table."""
    tab = np.column_stack([seg["converted"], seg["trials"] - seg["converted"]]).astype(float)
    expected = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
    return float(((tab - expected) ** 2 / expected).sum())


def two_group_z(seg: pd.DataFrame, col: str, a: str, b: list[str]) -> float:
    """z for group `a` against the pooled groups `b`."""
    ga, gb = seg[seg[col] == a], seg[seg[col].isin(b)]
    c1, n1 = int(ga["converted"].sum()), int(ga["trials"].sum())
    c2, n2 = int(gb["converted"].sum()), int(gb["trials"].sum())
    p = (c1 + c2) / (n1 + n2)
    return (c1 / n1 - c2 / n2) / np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))


# Critical chi-square values at 5%: 2 df = 5.99, 3 df = 7.81.
sig_rows = [
    {"test": "device differs (chi-square, 2 df, cutoff 5.99)", "statistic": round(chi_square(seg_device), 2)},
    {"test": "country differs (chi-square, 3 df, cutoff 7.81)", "statistic": round(chi_square(seg_country), 2)},
    {"test": "iOS vs Web (z, cutoff 1.96)", "statistic": round(two_group_z(seg_device, "device_type", "iOS", ["Web"]), 2)},
    {"test": "Android vs Web (z, cutoff 1.96)", "statistic": round(two_group_z(seg_device, "device_type", "Android", ["Web"]), 2)},
    {"test": "US vs EU (z, cutoff 1.96)", "statistic": round(two_group_z(seg_country, "country", "US", ["EU"]), 2)},
    {"test": "US vs other three countries (z, post hoc, cutoff 1.96)", "statistic": round(two_group_z(seg_country, "country", "US", ["EU", "India", "Rest"]), 2)},
    {"test": "second half vs first half (z, cutoff 1.96)", "statistic": round(z, 2)},
]
sig = pd.DataFrame(sig_rows)
sig.to_csv(DATA_OUT / "significance.csv", index=False)
print("\nSignificance tests:")
print(sig.to_string(index=False))

# --- Charts -----------------------------------------------------------------
top_country = seg_country.iloc[0]
c = charts.bar(
    seg_country["country"].tolist(), seg_country["conversion_pct"].tolist(),
    f"Conversion by country: {top_country['country']} leads at {top_country['conversion_pct']:.0f}% "
    f"vs {overall:.0f}% overall",
    highlight=top_country["country"], ylabel="Trial conversion (%)",
    source="Matured trials, started 2026-08-01 to 2026-09-10. Source: trials, users.",
)
charts.save(c, CHART_OUT / "conversion_by_country.png")

top_dev = seg_device.iloc[0]
c = charts.bar(
    seg_device["device_type"].tolist(), seg_device["conversion_pct"].tolist(),
    f"Conversion by device: {top_dev['device_type']} at {top_dev['conversion_pct']:.0f}% "
    f"vs {overall:.0f}% overall",
    highlight=top_dev["device_type"], ylabel="Trial conversion (%)",
    source="Matured trials, started 2026-08-01 to 2026-09-10. Source: trials, users.",
)
charts.save(c, CHART_OUT / "conversion_by_device.png")

if abs(z) < 1.96:
    trend_title = (f"No detectable change in conversion across start weeks "
                   f"({pe:.1f}% first half, {pl:.1f}% second half)")
else:
    trend_title = (f"Conversion moved {'up' if pl > pe else 'down'} across start weeks "
                   f"({pe:.1f}% to {pl:.1f}%)")
c = charts.line(
    weekly["week"].astype(str).tolist(),
    {"Weekly conversion": weekly["conversion_pct"].tolist(),
     "Overall": [round(overall, 1)] * len(weekly)},
    trend_title,
    highlight="Weekly conversion", ylabel="Trial conversion (%)",
    source="Matured trials by week of start. Source: trials.",
)
charts.save(c, CHART_OUT / "conversion_by_start_week.png")

print(f"\nSaved tables to {DATA_OUT.relative_to(ROOT)} and charts to {CHART_OUT.relative_to(ROOT)}.")
