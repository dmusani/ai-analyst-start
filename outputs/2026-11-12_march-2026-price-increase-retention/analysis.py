"""Did the March 2026 price increase hurt monthly-plan retention, and for whom?

Run from the repo root:
    poetry run python outputs/2026-11-12_march-2026-price-increase-retention/analysis.py

Churn rate = cancellations in a calendar month per 1,000 monthly subscribers active at the
start of that month. Gaps are in cancellations per 1,000 (absolute) unless marked relative.
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

AS_OF = pd.Timestamp("2026-09-24")  # the data ends here
PRICE_MONTH = pd.Period("2026-03", "M")  # first month at $12
FIRST_MONTH = pd.Period("2025-01", "M")  # first month with payment history to confirm price
LAST_CLOSED = pd.Period("2026-08", "M")  # September 2026 is still open
SPIKE_START = (pd.Timestamp("2025-09-01"), pd.Timestamp("2025-09-30"))

subs = pd.read_csv("data/subscriptions.csv", parse_dates=["start_date", "end_date"])
users = pd.read_csv("data/users.csv", parse_dates=["signup_date"])
pay = pd.read_csv("data/payments.csv", parse_dates=["payment_date"])

print("== Checks ==")
b = checks.date_boundaries(subs, "start_date")
print(b["summary"])
fan = checks.join_fan_out(subs, users[["user_id", "country", "device_type"]], on="user_id")
print(fan["summary"])

# Population: paid plans that have started by the analysis date.
paid = subs[(subs["plan"] != "free") & (subs["start_date"].dt.normalize() <= AS_OF)].copy()
paid = paid.merge(users[["user_id", "country", "device_type"]], on="user_id", how="left")
assert paid["country"].notna().all(), "subscriptions without a matching user"
# A scheduled cancellation after the analysis date means still active today.
paid["end_eff"] = paid["end_date"].where(paid["end_date"].dt.normalize() <= AS_OF)
paid["start_m"] = paid["start_date"].dt.to_period("M")
paid["end_m"] = paid["end_eff"].dt.to_period("M")
paid["sep25_cohort"] = (paid["start_date"] >= SPIKE_START[0]) & (paid["start_date"] < SPIKE_START[1] + pd.Timedelta(days=1))

# Price check: every monthly payment from 2026-03-01 is $12, before that $10.
mp = pay.merge(paid[["subscription_id", "plan"]], on="subscription_id")
mp = mp[mp["plan"] == "monthly"]
pre_amt = mp.loc[mp["payment_date"] < "2026-03-01", "amount_usd"].unique()
post_amt = mp.loc[mp["payment_date"] >= "2026-03-01", "amount_usd"].unique()
print(f"Monthly amounts before 2026-03-01: {sorted(pre_amt)}; from 2026-03-01: {sorted(post_amt)}.")
assert list(post_amt) == [12.0], "price after March is not uniformly $12"

monthly = paid[paid["plan"] == "monthly"]
annual = paid[paid["plan"] == "annual"]
months = pd.period_range(FIRST_MONTH, LAST_CLOSED, freq="M")


def churn_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Active at start of month, cancellations in month, rate per 1,000."""
    rows = []
    for m in months:
        start = m.start_time
        active = int(((df["start_date"] < start) & (df["end_eff"].isna() | (df["end_eff"] >= start))).sum())
        ended = int((df["end_m"] == m).sum() - ((df["end_m"] == m) & (df["start_m"] == m)).sum())
        # Count only cancellations of subscribers who were active at the start of the month.
        ended = int(((df["end_m"] == m) & (df["start_date"] < start)).sum())
        rows.append({"month": str(m), "active_at_start": active, "cancellations": ended,
                     "per_1000": round(1000 * ended / active, 1) if active else np.nan})
    return pd.DataFrame(rows)


def window_rate(df: pd.DataFrame, first: str, last: str) -> dict:
    """Pooled churn per 1,000 per month across a run of closed months."""
    t = churn_by_month(df)
    t = t[(t["month"] >= first) & (t["month"] <= last)]
    return {"active_months": int(t["active_at_start"].sum()), "cancellations": int(t["cancellations"].sum()),
            "per_1000": round(1000 * t["cancellations"].sum() / t["active_at_start"].sum(), 1)}


# --- 1. Overall monthly trend, with annual as the unexposed benchmark ---------
m_trend = churn_by_month(monthly)
a_trend = churn_by_month(annual)
m_trend.to_csv(DATA_OUT / "monthly_churn_by_month.csv", index=False)
a_trend.to_csv(DATA_OUT / "annual_churn_by_month.csv", index=False)
print("\n== Monthly-plan churn per 1,000 active, by month ==")
print(m_trend.to_string(index=False))

PRE = ("2025-01", "2026-02")
POST = ("2026-03", "2026-08")
pre_m, post_m = window_rate(monthly, *PRE), window_rate(monthly, *POST)
pre_a, post_a = window_rate(annual, *PRE), window_rate(annual, *POST)
# The September 2025 signup spike lifted churn from Oct 2025, so the pre period is split in two.
early_m, late_m = window_rate(monthly, "2025-01", "2025-08"), window_rate(monthly, "2025-10", "2026-02")
summary = pd.DataFrame([
    {"plan": "monthly", "period": "Jan to Aug 2025 ($10, before the spike)", **early_m},
    {"plan": "monthly", "period": "Oct 2025 to Feb 2026 ($10, after the spike)", **late_m},
    {"plan": "monthly", "period": "Jan 2025 to Feb 2026 ($10)", **pre_m},
    {"plan": "monthly", "period": "Mar to Aug 2026 ($12)", **post_m},
    {"plan": "annual", "period": "Jan 2025 to Feb 2026", **pre_a},
    {"plan": "annual", "period": "Mar to Aug 2026", **post_a},
])
summary.to_csv(DATA_OUT / "before_after_summary.csv", index=False)
print("\n== Before vs after ==")
print(summary.to_string(index=False))
gap = post_m["per_1000"] - pre_m["per_1000"]
print(f"Monthly: {pre_m['per_1000']} -> {post_m['per_1000']} per 1,000 per month "
      f"(+{gap:.1f} per 1,000; relative {100 * gap / pre_m['per_1000']:+.0f}%).")
print(f"Closer baseline, Oct 2025 to Feb 2026: {late_m['per_1000']} -> {post_m['per_1000']} per 1,000 per month "
      f"(+{post_m['per_1000'] - late_m['per_1000']:.1f}; relative {100 * (post_m['per_1000'] / late_m['per_1000'] - 1):+.0f}%).")
print(f"Annual benchmark: {pre_a['per_1000']} -> {post_a['per_1000']} per 1,000 per month.")

# --- 2. Rule out the September 2025 cohort as the cause ---------------------
parts = []
for label, flag in [("September 2025 signups", True), ("All other cohorts", False)]:
    sub = monthly[monthly["sep25_cohort"] == flag]
    pre, post = window_rate(sub, *PRE), window_rate(sub, *POST)
    parts.append({"group": label, "pre_per_1000": pre["per_1000"], "post_per_1000": post["per_1000"],
                  "change_per_1000": round(post["per_1000"] - pre["per_1000"], 1),
                  "pre_active_months": pre["active_months"], "post_active_months": post["active_months"],
                  "post_cancellations": post["cancellations"]})
cohort = pd.DataFrame(parts)
cohort.to_csv(DATA_OUT / "september_2025_cohort_split.csv", index=False)
print("\n== September 2025 cohort vs everyone else ==")
print(cohort.to_string(index=False))

# --- 3. Who: tenure at the time of the increase, country, device ------------
def segment_table(by: str, df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, g in df.groupby(by, observed=True):
        pre, post = window_rate(g, *PRE), window_rate(g, *POST)
        rows.append({by: key, "pre_per_1000": pre["per_1000"], "post_per_1000": post["per_1000"],
                     "change_per_1000": round(post["per_1000"] - pre["per_1000"], 1),
                     "relative_change_pct": round(100 * (post["per_1000"] / pre["per_1000"] - 1), 0)
                     if pre["per_1000"] else np.nan,
                     "post_cancellations": post["cancellations"], "post_active_months": post["active_months"]})
    return pd.DataFrame(rows).sort_values("change_per_1000", ascending=False)


# Tenure at 2026-03-01 for existing subscribers; subscribers who start after are "joined at $12".
cut = pd.Timestamp("2026-03-01")
ten_days = (cut - monthly["start_date"]).dt.days
monthly = monthly.assign(
    tenure_at_increase=pd.cut(ten_days, [-10**6, 0, 90, 365, 10**6],
                              labels=["Joined at $12", "Under 3 months", "3 to 12 months", "Over 12 months"]))
# New joiners have no pre-increase months; compare them separately below.
seg_ten = segment_table("tenure_at_increase", monthly[monthly["tenure_at_increase"] != "Joined at $12"])
seg_country = segment_table("country", monthly)
seg_device = segment_table("device_type", monthly)
seg_ten.to_csv(DATA_OUT / "change_by_tenure.csv", index=False)
seg_country.to_csv(DATA_OUT / "change_by_country.csv", index=False)
seg_device.to_csv(DATA_OUT / "change_by_device.csv", index=False)
for name, t in [("tenure at the increase", seg_ten), ("country", seg_country), ("device", seg_device)]:
    print(f"\n== Change in churn by {name} ==")
    print(t.to_string(index=False))

# Cancellations do not appear until a subscriber has had time to cancel, so check the
# cancellation timing of those who joined at $12.
joined = monthly[monthly["tenure_at_increase"] == "Joined at $12"]
j_post = window_rate(joined, *POST)
print(f"\nJoined at $12: {j_post['per_1000']} per 1,000 per month ({j_post['active_months']:,} active months), "
      f"vs {pre_m['per_1000']} for pre-increase months of all monthly subscribers.")

# Country x tenure for the largest movers, only cells with enough cancellations.
cx = []
base = monthly[monthly["tenure_at_increase"] != "Joined at $12"]
for (c, t), g in base.groupby(["country", "tenure_at_increase"], observed=True):
    pre, post = window_rate(g, *PRE), window_rate(g, *POST)
    cx.append({"country": c, "tenure_at_increase": t, "pre_per_1000": pre["per_1000"],
               "post_per_1000": post["per_1000"], "change_per_1000": round(post["per_1000"] - pre["per_1000"], 1),
               "post_cancellations": post["cancellations"]})
cx = pd.DataFrame(cx).sort_values("change_per_1000", ascending=False)
cx.to_csv(DATA_OUT / "change_by_country_and_tenure.csv", index=False)
print("\n== Country x tenure ==")
print(cx.to_string(index=False))

# --- Checks ----------------------------------------------------------------
tot_post = post_m["cancellations"]
c = checks.parts_sum_to_total(seg_country["post_cancellations"], tot_post)
print("\n" + c["summary"])
c = checks.parts_sum_to_total(seg_device["post_cancellations"], tot_post)
print(c["summary"])
c = checks.parts_sum_to_total(cohort["post_cancellations"], tot_post)
print(c["summary"])
tenure_post = int(seg_ten["post_cancellations"].sum() + j_post["cancellations"])
c = checks.parts_sum_to_total([tenure_post], tot_post)
print("Tenure groups plus joined-at-$12: " + c["summary"])

# --- Charts ----------------------------------------------------------------
CHART_OUT.mkdir(exist_ok=True)
x = [m[2:] for m in m_trend["month"]]
fig = charts.line(x, {"Monthly plan": m_trend["per_1000"], "Annual plan": a_trend["per_1000"]},
                  "Monthly-plan cancellations more than tripled after the March 2026 increase",
                  highlight="Monthly plan", ylabel="Cancellations per 1,000 active subscribers",
                  source="Source: subscriptions. Months Jan 2025 to Aug 2026; the increase took effect Mar 2026.")
charts.save(fig, CHART_OUT / "churn_trend_monthly_vs_annual.png")

fig = charts.bar(list(seg_country["country"]), list(seg_country["change_per_1000"]),
                 "Rise in monthly cancellations after the increase, by country",
                 highlight=seg_country["country"].iloc[0], ylabel="Change in cancellations per 1,000 per month",
                 source="Source: subscriptions, users. Mar to Aug 2026 vs Jan 2025 to Feb 2026.")
charts.save(fig, CHART_OUT / "change_by_country.png")

fig = charts.bar(list(seg_ten["tenure_at_increase"].astype(str)), list(seg_ten["change_per_1000"]),
                 "Rise in monthly cancellations after the increase, by tenure",
                 highlight=str(seg_ten["tenure_at_increase"].iloc[0]),
                 ylabel="Change in cancellations per 1,000 per month",
                 source="Source: subscriptions. Tenure measured at 1 Mar 2026.")
charts.save(fig, CHART_OUT / "change_by_tenure.png")
print("\nCharts and tables saved.")
