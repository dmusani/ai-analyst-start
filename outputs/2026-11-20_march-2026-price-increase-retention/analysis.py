"""Did the March 2026 price increase hurt monthly-plan retention, and for whom?

Run from the repo root:
    poetry run python outputs/2026-11-20_march-2026-price-increase-retention/analysis.py

Input: the aggregate result tables in data/raw_*.csv, pulled from course-db by queries.sql.
Monthly churn rate = subscribers whose end_date falls in a calendar month, divided by
subscribers active at the start of that month. Gaps are in percentage points (pp) unless
marked relative.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from helpers import charts, checks  # noqa: E402

RUN = Path(__file__).resolve().parent
DATA = RUN / "data"
CHARTS = RUN / "charts"

# Periods. March 2026 is the month the price rose; payments confirm $12 from then.
# Cancellations show up with a lag, so March is a transition month and is reported apart.
PRE_RECENT = [f"{m}" for m in pd.period_range("2025-10", "2026-02", freq="M")]
PRE_FULL = [f"{m}" for m in pd.period_range("2025-01", "2026-02", freq="M")]
TRANSITION = ["2026-03"]
POST = [f"{m}" for m in pd.period_range("2026-04", "2026-08", freq="M")]
LAST_CLOSED = "2026-08"  # September 2026 is open (data ends 2026-09-24) and is excluded
SEG_ORDER = {"country": ["US", "EU", "India", "Rest"],
             "device_type": ["iOS", "Android", "Web"],
             "tenure": ["1_under_3m", "2_3_to_6m", "3_6_to_12m", "4_12m_plus"]}

overall = pd.read_csv(DATA / "raw_monthly_churn_overall.csv")
seg = pd.read_csv(DATA / "raw_monthly_churn_segments.csv")
price = pd.read_csv(DATA / "raw_monthly_price_paid.csv")
joinchk = pd.read_csv(DATA / "raw_payments_join_check.csv")

# ---------------------------------------------------------------- checks
print("== Checks ==")
# The pull stops at the last closed month, so no partial month enters a comparison.
open_excluded = overall["month"].max() == LAST_CLOSED
print(f"Open month excluded: {open_excluded} (latest month pulled is {overall['month'].max()}; "
      "September 2026 is open, data ends 2026-09-24).")

monthly = overall[overall["plan"] == "monthly"].set_index("month")
annual = overall[overall["plan"] == "annual"].set_index("month")

fail = False
for dim in SEG_ORDER:
    tot = seg[seg["dimension"] == dim].groupby("month")[["at_risk", "churned"]].sum()
    for col in ["at_risk", "churned"]:
        for m in monthly.index:
            r = checks.parts_sum_to_total([tot.loc[m, col]], float(monthly.loc[m, col]), tolerance=0)
            if not r["ok"]:
                fail = True
                print(f"FAIL {dim} {col} {m}: {r['summary']}")
print("Segments add back to the overall monthly total for every month, at risk and churned, "
      "for country, device and tenure:", "NO" if fail else "yes")
print(f"Payments join: {joinchk.loc[0, 'payments_rows']:,} payments before, "
      f"{joinchk.loc[0, 'payments_after_join']:,} after joining to subscriptions "
      f"({'no fan-out' if joinchk.loc[0, 'payments_rows'] == joinchk.loc[0, 'payments_after_join'] else 'FAN-OUT'}).")

# Price actually charged to monthly subscribers
price["month"] = price["month"].astype(str)
by_month = price.groupby("month")["amount_usd"].agg(["min", "max"])
pre_price = by_month.loc["2025-12":"2026-02"]
post_price = by_month.loc["2026-03":"2026-09"]
print(f"Monthly price paid Dec 2025 to Feb 2026: ${pre_price['min'].min():.0f} to ${pre_price['max'].max():.0f}; "
      f"Mar to Sep 2026: ${post_price['min'].min():.0f} to ${post_price['max'].max():.0f} "
      "(one amount each period, so every monthly subscriber moved to $12 at once).")


def rate(df, months):
    d = df.loc[df.index.isin(months)]
    return d["churned"].sum() / d["at_risk"].sum() * 100


def monthly_rates(df):
    return (df["churned"] / df["at_risk"] * 100)


# ---------------------------------------------------------------- headline
mr = monthly_rates(monthly)
ar = monthly_rates(annual)
head = pd.DataFrame({
    "monthly_churn_pct": mr.round(2), "annual_churn_pct": ar.round(2),
    "monthly_at_risk": monthly["at_risk"], "monthly_churned": monthly["churned"],
})
head.to_csv(DATA / "monthly_churn_by_month.csv")

pre_recent, pre_full = rate(monthly, PRE_RECENT), rate(monthly, PRE_FULL)
march, post = rate(monthly, TRANSITION), rate(monthly, POST)
pre_lo, pre_hi = mr.loc[PRE_RECENT].min(), mr.loc[PRE_RECENT].max()
post_lo, post_hi = mr.loc[POST].min(), mr.loc[POST].max()
ann_pre, ann_post = rate(annual, PRE_RECENT), rate(annual, POST)

print("\n== Headline: monthly-plan churn (share of active subscribers who end in the month) ==")
print(f"Oct 2025 to Feb 2026 (recent baseline): {pre_recent:.2f}% a month "
      f"(monthly range {pre_lo:.2f}% to {pre_hi:.2f}%).")
print(f"Jan 2025 to Feb 2026 (full pre-period): {pre_full:.2f}% a month.")
print(f"March 2026 (price rose, transition month): {march:.2f}%.")
print(f"Apr to Aug 2026 (after): {post:.2f}% a month (monthly range {post_lo:.2f}% to {post_hi:.2f}%).")
print(f"Change vs recent baseline: +{post - pre_recent:.2f} pp, a relative rise of {(post / pre_recent - 1) * 100:.0f}%.")
print(f"Change vs full pre-period: +{post - pre_full:.2f} pp, a relative rise of {(post / pre_full - 1) * 100:.0f}%.")
print(f"Every post month ({post_lo:.2f}% lowest) is above every recent-baseline month ({pre_hi:.2f}% highest): "
      f"{post_lo > pre_hi}.")
print(f"Annual plan (no price change), same windows: {ann_pre:.2f}% before, {ann_post:.2f}% after "
      f"({ann_post - ann_pre:+.2f} pp). No unexposed monthly group exists, so this is context, not a control.")

post_at_risk = monthly.loc[POST, "at_risk"].sum()
excess = (post - pre_recent) / 100 * post_at_risk
print(f"Extra cancellations Apr to Aug 2026 against the recent-baseline rate: about {excess:,.0f} "
      f"({monthly.loc[POST, 'churned'].sum():,} actual, {post_at_risk * pre_recent / 100:,.0f} expected).")

# ---------------------------------------------------------------- segments
rows = []
for dim, order in SEG_ORDER.items():
    for s in order:
        d = seg[(seg["dimension"] == dim) & (seg["segment"] == s)].set_index("month")
        rr = monthly_rates(d)
        pre_hi_s = rr.reindex(PRE_RECENT).dropna()
        pre_r, post_r = rate(d, PRE_RECENT), rate(d, POST)
        rows.append({
            "dimension": dim, "segment": s,
            "pre_rate_pct": pre_r, "post_rate_pct": post_r,
            "change_pp": post_r - pre_r,
            "relative_change_pct": (post_r / pre_r - 1) * 100 if pre_r else float("nan"),
            "pre_month_max_pct": pre_hi_s.max(), "post_month_min_pct": rr.reindex(POST).min(),
            "all_post_months_above_pre_max": bool(rr.reindex(POST).min() > pre_hi_s.max()),
            "post_at_risk": int(d.loc[POST, "at_risk"].sum()),
            "extra_cancellations": (post_r - pre_r) / 100 * d.loc[POST, "at_risk"].sum(),
        })
segres = pd.DataFrame(rows)
segres.round(2).to_csv(DATA / "segment_churn_change.csv", index=False)

print("\n== By segment: churn Oct 2025 to Feb 2026 vs Apr to Aug 2026 (percent a month) ==")
for dim in SEG_ORDER:
    print(f"-- {dim}")
    for _, r in segres[segres["dimension"] == dim].iterrows():
        print(f"  {r['segment']:<12} {r['pre_rate_pct']:5.2f}% -> {r['post_rate_pct']:5.2f}%  "
              f"({r['change_pp']:+.2f} pp, {r['relative_change_pct']:+.0f}% relative; "
              f"every post month above pre max: {r['all_post_months_above_pre_max']}; "
              f"about {r['extra_cancellations']:,.0f} extra cancellations)")

# Monthly tenure detail: the 12m+ group had almost no churn in early 2025.
ten = seg[seg["dimension"] == "tenure"]
t12 = ten[ten["segment"] == "4_12m_plus"].set_index("month")
print(f"\nNote: subscribers with 12+ months tenure show 0 cancellations in every month from "
      f"2025-01 to 2025-08 ({int(t12.loc['2025-01':'2025-08', 'churned'].sum())} in total), so the full pre-period "
      "understates normal churn for that group; the recent baseline is used instead.")

# ---------------------------------------------------------------- charts
months = list(monthly.index)
fig = charts.line(
    months, {"Monthly plan": mr.tolist(), "Annual plan": ar.tolist()},
    "Monthly-plan churn more than doubled from April 2026, the month after the price rose; annual plan did not move",
    highlight="Monthly plan", ylabel="Cancellations as % of active subscribers",
    source="Source: course-db subscriptions. March 2026 = price rise. Sep 2026 excluded (open).",
)
ax = fig.axes[0]
ax.axvline(months.index("2026-03"), color="#999999", linestyle="--", linewidth=1)
ax.set_xticks(range(0, len(months), 3))
ax.set_xticklabels([months[i] for i in range(0, len(months), 3)])
charts.save(fig, CHARTS / "monthly_churn_trend.png")

NICE = {"1_under_3m": "under 3 months", "2_3_to_6m": "3 to 6 months",
        "3_6_to_12m": "6 to 12 months", "4_12m_plus": "12 months or more"}
LABEL = {"country": "country", "device_type": "device", "tenure": "tenure group"}
for dim in SEG_ORDER:
    sub = segres[segres["dimension"] == dim].reset_index(drop=True)
    sub["segment"] = sub["segment"].map(lambda v: NICE.get(v, v))
    hi, lo = sub.loc[sub["change_pp"].idxmax()], sub.loc[sub["change_pp"].idxmin()]
    all_up = bool((sub["change_pp"] > 0).all())
    title = (f"Churn rose in every {LABEL[dim]}, most for {hi['segment']} (+{hi['change_pp']:.1f} pp) "
             f"and least for {lo['segment']} (+{lo['change_pp']:.1f} pp)") if all_up else \
            f"Churn change by {LABEL[dim]}: not every group rose"
    fig = charts.bar(
        list(sub["segment"]), list((sub["change_pp"] * 100).round(0)), title,
        highlight=[hi["segment"]],
        ylabel="Rise in monthly churn, basis points (100 = 1 percentage point)",
        source="Monthly plan. Oct 2025 to Feb 2026 vs Apr to Aug 2026. Source: course-db.",
    )
    charts.save(fig, CHARTS / f"churn_change_by_{dim}.png")

print("\nCharts saved to", CHARTS)
