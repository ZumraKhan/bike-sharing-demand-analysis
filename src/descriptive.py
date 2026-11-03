"""
Descriptive analysis + visualisations for the Bike Sharing Demand project.

Produces every figure used by the notebook, the PDF report and the slide deck,
plus the summary tables written to outputs/tables/.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import viz_style as vs
from data_prep import load_hourly, load_daily, quality_report, WEEKDAYS

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
TAB = ROOT / "outputs" / "tables"


def _fmt(v, _=None):
    """Axis ticks: full numbers under 10,000, compact above."""
    v = float(v)
    if abs(v) >= 10_000:
        return f"{v/1000:,.0f}K"
    return f"{v:,.0f}"


def axis_numbers(ax, which="y"):
    (ax.yaxis if which == "y" else ax.xaxis).set_major_formatter(FuncFormatter(_fmt))


def grid_only(ax, which="y"):
    """Hairline grid on the value axis only; none on the category axis.

    `visible=True` is explicit: a bare ax.grid() call TOGGLES the rcParam
    default and would silently switch the grid off.
    """
    ax.grid(axis=which, which="major", visible=True)
    ax.grid(axis="x" if which == "y" else "y", visible=False)


# ==========================================================================
# Descriptive statistics
# ==========================================================================
def describe(hourly: pd.DataFrame, daily: pd.DataFrame) -> dict:
    """Every number quoted in the report and the deck is computed here."""
    by_year = hourly.groupby("year")["cnt"].sum()
    growth = (by_year.loc[2012] / by_year.loc[2011] - 1) * 100

    hour_profile = hourly.groupby("hr")["cnt"].mean()
    by_weather = hourly.groupby("weather_name")["cnt"].mean()
    by_season = hourly.groupby("season_name")["cnt"].mean()

    # Day-type-specific hour profiles. The all-days profile below averages two
    # different behaviours together, so any claim ABOUT working days must be
    # quoted from the working-day curve, not from the pooled one.
    wd_profile = hourly[hourly["workingday"] == 1].groupby("hr")["cnt"].mean()
    we_profile = hourly[hourly["workingday"] == 0].groupby("hr")["cnt"].mean()

    work = hourly[hourly["workingday"] == 1]["cnt"]
    free = hourly[hourly["workingday"] == 0]["cnt"]

    m = {
        "total_rentals": int(hourly["cnt"].sum()),
        "rentals_2011": int(by_year.loc[2011]),
        "rentals_2012": int(by_year.loc[2012]),
        "yoy_growth_pct": round(float(growth), 1),
        "mean_hourly": round(float(hourly["cnt"].mean()), 1),
        "median_hourly": float(hourly["cnt"].median()),
        "std_hourly": round(float(hourly["cnt"].std()), 1),
        "min_hourly": int(hourly["cnt"].min()),
        "max_hourly": int(hourly["cnt"].max()),
        "skewness": round(float(hourly["cnt"].skew()), 2),
        "kurtosis": round(float(hourly["cnt"].kurt()), 2),
        "cv_pct": round(float(hourly["cnt"].std() / hourly["cnt"].mean() * 100), 1),
        "mean_daily": round(float(daily["cnt"].mean()), 1),
        "max_daily": int(daily["cnt"].max()),
        "max_daily_date": str(daily.loc[daily["cnt"].idxmax(), "dteday"].date()),
        "min_daily": int(daily["cnt"].min()),
        "min_daily_date": str(daily.loc[daily["cnt"].idxmin(), "dteday"].date()),
        "registered_share_pct": round(float(hourly["registered"].sum()
                                            / hourly["cnt"].sum() * 100), 1),
        "casual_share_pct": round(float(hourly["casual"].sum()
                                        / hourly["cnt"].sum() * 100), 1),
        "peak_hour": int(hour_profile.idxmax()),
        "peak_hour_mean": round(float(hour_profile.max()), 1),
        "trough_hour": int(hour_profile.idxmin()),
        "trough_hour_mean": round(float(hour_profile.min()), 1),
        "peak_to_trough_ratio": round(float(hour_profile.max() / hour_profile.min()), 1),
        "workingday_peak_hour": int(wd_profile.idxmax()),
        "workingday_peak_mean": round(float(wd_profile.max()), 1),
        "workingday_am_peak_hour": int(wd_profile.loc[5:11].idxmax()),
        "workingday_am_peak_mean": round(float(wd_profile.loc[5:11].max()), 1),
        "workingday_trough_hour": int(wd_profile.idxmin()),
        "workingday_trough_mean": round(float(wd_profile.min()), 1),
        "workingday_peak_to_trough": round(
            float(wd_profile.max() / wd_profile.min()), 1),
        "weekend_peak_hour": int(we_profile.idxmax()),
        "weekend_peak_mean": round(float(we_profile.max()), 1),
        "best_season": str(by_season.idxmax()),
        "best_season_mean": round(float(by_season.max()), 1),
        "worst_season": str(by_season.idxmin()),
        "worst_season_mean": round(float(by_season.min()), 1),
        "clear_weather_mean": round(float(by_weather.get("Clear / Few clouds")), 1),
        "heavy_weather_mean": round(float(by_weather.get("Heavy rain / snow")), 1),
        "weather_drop_pct": round(
            float((1 - by_weather.get("Heavy rain / snow")
                   / by_weather.get("Clear / Few clouds")) * 100), 1),
        "workingday_mean": round(float(work.mean()), 1),
        "weekend_mean": round(float(free.mean()), 1),
        "corr_temp": round(float(hourly["cnt"].corr(hourly["temp_c"])), 3),
        "corr_atemp": round(float(hourly["cnt"].corr(hourly["atemp_c"])), 3),
        "corr_humidity": round(float(hourly["cnt"].corr(hourly["humidity"])), 3),
        "corr_wind": round(float(hourly["cnt"].corr(hourly["wind_kmh"])), 3),
        "corr_hour": round(float(hourly["cnt"].corr(hourly["hr"])), 3),
        "casual_share_weekend_pct": round(
            float(hourly[hourly["workingday"] == 0]["casual"].sum()
                  / hourly[hourly["workingday"] == 0]["cnt"].sum() * 100), 1),
        "casual_share_working_pct": round(
            float(hourly[hourly["workingday"] == 1]["casual"].sum()
                  / hourly[hourly["workingday"] == 1]["cnt"].sum() * 100), 1),
    }
    return m


def write_tables(hourly: pd.DataFrame, daily: pd.DataFrame) -> None:
    """Table-view twins for the figures, so no value is locked inside a chart."""
    TAB.mkdir(parents=True, exist_ok=True)

    hourly[["cnt", "casual", "registered", "temp_c", "atemp_c",
            "humidity", "wind_kmh"]].describe().round(2).to_csv(
        TAB / "numeric_summary.csv")

    hourly.groupby("season_name")["cnt"].agg(
        ["count", "mean", "median", "std", "min", "max"]).round(1).to_csv(
        TAB / "demand_by_season.csv")

    hourly.groupby("weather_name")["cnt"].agg(
        ["count", "mean", "median", "std", "max"]).round(1).to_csv(
        TAB / "demand_by_weather.csv")

    hourly.groupby("hr")[["cnt", "casual", "registered"]].mean().round(1).to_csv(
        TAB / "demand_by_hour.csv")

    daily.groupby(["year", "month_name"])["cnt"].sum().to_csv(
        TAB / "monthly_totals.csv")


# ==========================================================================
# Figures
# ==========================================================================
def fig_hourly_profile(hourly):
    """Trend over a cycle, two distinct series -> multi-line, categorical."""
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for name, color in (("Working day", vs.BLUE), ("Weekend / holiday", vs.ORANGE)):
        s = hourly[hourly["day_type"] == name].groupby("hr")["cnt"].mean()
        ax.plot(s.index, s.values, color=color, label=name, zorder=3)
        peak = int(s.idxmax())
        ax.annotate(f"{s.max():,.0f} at {peak:02d}:00",
                    xy=(peak, s.max()), xytext=(0, 10), textcoords="offset points",
                    ha="center", fontsize=9, color=vs.INK_SECOND, zorder=6)
        vs.ring_marker(ax, peak, s.max(), color=color)

    vs.titled(ax, "Commuting drives demand on working days",
              "Mean hourly rentals by hour of day, 2011-2012")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Mean rentals per hour")
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{h:02d}" for h in range(0, 24, 2)])
    ax.set_xlim(-0.5, 23.5)
    ax.set_ylim(0, None)
    axis_numbers(ax)
    grid_only(ax)
    ax.legend(loc="upper left", ncols=2, bbox_to_anchor=(0, -0.16))
    return vs.save(fig, FIG / "fig01_hourly_profile.png")


def fig_monthly_trend(daily):
    """One series is the whole point -> single hue + selective annotation."""
    m = daily.groupby(daily["dteday"].dt.to_period("M"))["cnt"].sum()
    x = np.arange(len(m))
    labels = [p.strftime("%b %y") for p in m.index]

    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.fill_between(x, m.values, color=vs.BLUE, alpha=0.10, zorder=2)
    ax.plot(x, m.values, color=vs.BLUE, zorder=3)

    hi = int(np.argmax(m.values))
    vs.ring_marker(ax, x[hi], m.values[hi], color=vs.BLUE)
    ax.annotate(f"Peak month: {labels[hi]}  {m.values[hi]:,.0f}",
                xy=(x[hi], m.values[hi]), xytext=(0, 12),
                textcoords="offset points", ha="center", fontsize=9,
                color=vs.INK_SECOND)

    ax.set_ylim(0, m.max() * 1.18)
    ax.axvline(11.5, color=vs.AXIS, linewidth=0.8, zorder=1)
    ax.text(11.8, m.max() * 0.06, "2012", fontsize=9, color=vs.INK_MUTED)
    ax.text(11.2, m.max() * 0.06, "2011", fontsize=9, color=vs.INK_MUTED, ha="right")

    vs.titled(ax, "Demand grew strongly in the second year",
              "Total monthly rentals, Jan 2011 - Dec 2012")
    ax.set_ylabel("Rentals per month")
    ax.set_xticks(x[::2])
    ax.set_xticklabels(labels[::2], rotation=45, ha="right")
    ax.set_xlim(-0.4, len(m) - 0.6)
    axis_numbers(ax)
    grid_only(ax)
    return vs.save(fig, FIG / "fig02_monthly_trend.png")


def fig_hour_weekday_heatmap(hourly):
    """Magnitude across a grid -> heatmap on the single-hue sequential ramp."""
    piv = hourly.pivot_table(index="weekday", columns="hr",
                             values="cnt", aggfunc="mean").reindex(range(7))

    fig, ax = plt.subplots(figsize=(10, 4.2))
    mesh = ax.pcolormesh(piv.values, cmap=vs.CMAP_SEQ,
                         edgecolors=vs.SURFACE, linewidth=1.6)
    ax.set_xticks(np.arange(24) + 0.5)
    ax.set_xticklabels([f"{h:02d}" for h in range(24)], fontsize=8.5)
    ax.set_yticks(np.arange(7) + 0.5)
    ax.set_yticklabels([WEEKDAYS[i] for i in range(7)])
    ax.invert_yaxis()
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    cb = fig.colorbar(mesh, ax=ax, pad=0.015, aspect=22)
    cb.set_label("Mean rentals per hour", color=vs.INK_SECOND, fontsize=9.5)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=vs.INK_MUTED, length=0, labelsize=9)

    vs.titled(ax, "Two weekday commuter spikes, one weekend midday hump",
              "Mean rentals by weekday and hour of day")
    ax.set_xlabel("Hour of day")
    return vs.save(fig, FIG / "fig03_hour_weekday_heatmap.png")


def fig_weather_impact(hourly):
    """Ordered categories -> bars on the validated ORDINAL single-hue ramp."""
    order = ["Clear / Few clouds", "Mist / Cloudy",
             "Light snow or rain", "Heavy rain / snow"]
    s = hourly.groupby("weather_name")["cnt"].mean().reindex(order)
    n = hourly.groupby("weather_name")["cnt"].size().reindex(order)
    pos = np.arange(len(order))

    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    for p, v, c in zip(pos, s.values, vs.ORDINAL_BLUE):
        vs.bars(ax, [p], [v], color=c, width_pt=18)
    vs.value_labels(ax, pos, s.values, fmt="{:,.0f}", width_pt=18)

    vs.titled(ax, "Bad weather roughly halves hourly demand",
              "Mean rentals per hour by weather situation")
    ax.set_xticks(pos)
    ax.set_xticklabels([f"{o}\n(n={v:,})" for o, v in zip(order, n.values)],
                       fontsize=9)
    ax.set_ylabel("Mean rentals per hour")
    ax.set_xlim(-0.6, len(order) - 0.4)
    ax.set_ylim(0, s.max() * 1.18)
    axis_numbers(ax)
    grid_only(ax)
    return vs.save(fig, FIG / "fig04_weather_impact.png")


def fig_season_distribution(hourly):
    """Distribution comparison -> box plots, one hue (a single series)."""
    order = ["Spring", "Summer", "Fall", "Winter"]
    data = [hourly[hourly["season_name"] == s]["cnt"].values for s in order]

    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    bp = ax.boxplot(data, patch_artist=True, widths=0.45,
                    medianprops=dict(color=vs.SEQ_BLUE[-2], linewidth=2),
                    whiskerprops=dict(color=vs.BLUE, linewidth=1.4),
                    capprops=dict(color=vs.BLUE, linewidth=1.4),
                    flierprops=dict(marker="o", markersize=2.5,
                                    markerfacecolor=vs.INK_MUTED,
                                    markeredgecolor="none", alpha=0.35))
    for patch in bp["boxes"]:
        patch.set_facecolor(vs.BLUE)
        patch.set_alpha(0.10)
        patch.set_edgecolor(vs.BLUE)
        patch.set_linewidth(1.6)

    means = [float(d.mean()) for d in data]
    ax.plot(range(1, 5), means, "o", markersize=7, color=vs.BLUE,
            markeredgecolor=vs.SURFACE, markeredgewidth=2, zorder=6)
    best = int(np.argmax(means))
    ax.annotate(f"Highest mean: {means[best]:,.0f}",
                xy=(best + 1, means[best]), xytext=(14, 8),
                textcoords="offset points", fontsize=9, color=vs.INK_SECOND)

    vs.titled(ax, "Fall and summer carry the heaviest demand",
              "Distribution of hourly rentals by season (dot = mean)")
    ax.set_xticklabels(order)
    ax.set_ylabel("Rentals per hour")
    axis_numbers(ax)
    grid_only(ax)
    return vs.save(fig, FIG / "fig05_season_distribution.png")


def fig_temp_vs_demand(hourly):
    """Two continuous measures -> scatter wash + binned mean line."""
    r = hourly["cnt"].corr(hourly["temp_c"])

    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.scatter(hourly["temp_c"], hourly["cnt"], s=6, color=vs.BLUE,
               alpha=0.06, linewidths=0, zorder=2, label="Hourly observations")

    bins = np.arange(0, 42, 2)
    binned = hourly.groupby(pd.cut(hourly["temp_c"], bins),
                            observed=True)["cnt"].mean()
    mid = np.array([iv.mid for iv in binned.index])
    ax.plot(mid, binned.values, color=vs.ORANGE, zorder=4,
            label="Mean demand per 2 degree C band")

    hi = int(np.argmax(binned.values))
    vs.ring_marker(ax, mid[hi], binned.values[hi], color=vs.ORANGE)
    ax.annotate(f"Mean demand peaks near {mid[hi]:.0f} C",
                xy=(mid[hi], binned.values[hi]), xytext=(-14, 16),
                textcoords="offset points", fontsize=9, color=vs.INK_SECOND,
                ha="right")

    vs.titled(ax, "Warmer hours sell more rides, up to a ceiling",
              f"Hourly rentals vs temperature   r = {r:.2f}")
    ax.set_xlabel("Temperature (degrees C)")
    ax.set_ylabel("Rentals per hour")
    ax.set_xlim(-1, 41)
    ax.set_ylim(0, None)
    axis_numbers(ax)
    grid_only(ax)
    ax.legend(loc="upper left", ncols=2, bbox_to_anchor=(0, -0.18))
    return vs.save(fig, FIG / "fig06_temp_vs_demand.png")


def fig_user_mix(hourly):
    """Composition over time -> stacked bars, 2 categorical slots + legend."""
    g = hourly.groupby(hourly["timestamp"].dt.to_period("M"))[
        ["registered", "casual"]].sum()
    x = np.arange(len(g))
    labels = [p.strftime("%b %y") for p in g.index]

    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    ax.bar(x, g["registered"], width=0.66, color=vs.BLUE,
           label="Registered members", zorder=3)
    ax.bar(x, g["casual"], width=0.66, bottom=g["registered"], color=vs.ORANGE,
           label="Casual riders", zorder=3, linewidth=1.6, edgecolor=vs.SURFACE)

    vs.titled(ax, "Registered members supply the large majority of trips",
              "Monthly rentals split by user type")
    ax.set_ylabel("Rentals per month")
    ax.set_xticks(x[::2])
    ax.set_xticklabels(labels[::2], rotation=45, ha="right")
    ax.set_xlim(-0.6, len(g) - 0.4)
    axis_numbers(ax)
    grid_only(ax)
    ax.legend(loc="upper left", ncols=2, bbox_to_anchor=(0, -0.22))
    return vs.save(fig, FIG / "fig07_user_mix.png")


def fig_correlation(hourly):
    """Polarity (+/-) -> DIVERGING ramp with a neutral grey midpoint at zero."""
    cols = {"cnt": "Total rentals", "registered": "Registered", "casual": "Casual",
            "temp_c": "Temp", "atemp_c": "Feels-like",
            "humidity": "Humidity", "wind_kmh": "Wind",
            "hr": "Hour", "weathersit": "Weather code"}
    c = hourly[list(cols)].corr().rename(index=cols, columns=cols)

    fig, ax = plt.subplots(figsize=(7.6, 6.4))
    mesh = ax.pcolormesh(c.values, cmap=vs.CMAP_DIV, vmin=-1, vmax=1,
                         edgecolors=vs.SURFACE, linewidth=1.6)
    ax.set_xticks(np.arange(len(c)) + 0.5)
    ax.set_xticklabels(c.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(np.arange(len(c)) + 0.5)
    ax.set_yticklabels(c.index, fontsize=9)
    ax.invert_yaxis()
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for i in range(len(c)):
        for j in range(len(c)):
            v = c.values[i, j]
            ax.text(j + 0.5, i + 0.5, f"{v:.2f}", ha="center", va="center",
                    fontsize=8.5,
                    color="#ffffff" if abs(v) > 0.55 else vs.INK_SECOND)

    cb = fig.colorbar(mesh, ax=ax, pad=0.02, aspect=26)
    cb.set_label("Pearson correlation", color=vs.INK_SECOND, fontsize=9.5)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=vs.INK_MUTED, length=0, labelsize=9)

    vs.titled(ax, "Temperature is the strongest weather driver",
              "Pearson correlation between hourly variables")
    return vs.save(fig, FIG / "fig08_correlation.png")


def build_all():
    FIG.mkdir(parents=True, exist_ok=True)
    vs.apply_style()
    hourly, daily = load_hourly(), load_daily()

    metrics = {"quality": quality_report(hourly, daily),
               "descriptive": describe(hourly, daily)}
    write_tables(hourly, daily)

    paths = [fig_hourly_profile(hourly), fig_monthly_trend(daily),
             fig_hour_weekday_heatmap(hourly), fig_weather_impact(hourly),
             fig_season_distribution(hourly), fig_temp_vs_demand(hourly),
             fig_user_mix(hourly), fig_correlation(hourly)]

    out = ROOT / "outputs" / "metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(out.read_text()) if out.exists() else {}
    existing.update(metrics)
    out.write_text(json.dumps(existing, indent=2))
    return paths, metrics


if __name__ == "__main__":
    built, computed = build_all()
    print(f"{len(built)} figures written")
    for p in built:
        print("   ", p.name)
    print(json.dumps(computed["descriptive"], indent=2))
