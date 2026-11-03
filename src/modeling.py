"""
Predictive analysis: forecasting hourly bike rental demand.

Design decisions worth stating up front, because they drive the results:

1. LEAKAGE. `casual` and `registered` sum exactly to the target `cnt`, so both
   are dropped from the feature set. Keeping them would give a perfect score
   that means nothing.

2. SPLIT. The deployment question is "given tomorrow's calendar and weather
   forecast, how many bikes will be rented this hour?" -- so the honest test is
   a CHRONOLOGICAL split: train on the earlier 80% of hours, test on the most
   recent 20%, which the model has never seen. A random split is also reported
   because it is what most tutorials do, and the gap between the two is a
   finding in its own right.

3. CYCLICAL TIME. Hour 23 is adjacent to hour 00, but as a plain integer those
   are the two most distant values. Hour, month and weekday are therefore also
   encoded as sine/cosine pairs.
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

import viz_style as vs
from data_prep import load_hourly
from descriptive import axis_numbers, grid_only

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
TAB = ROOT / "outputs" / "tables"
RANDOM_STATE = 42

CYCLIC = {"hr": 24, "mnth": 12, "weekday": 7}
NUMERIC = ["temp_c", "atemp_c", "humidity", "wind_kmh"]
CATEGORICAL = ["season", "weathersit", "weekday", "hr", "mnth"]
BINARY = ["holiday", "workingday", "yr"]

PRETTY = {
    "temp_c": "Temperature", "atemp_c": "Feels-like temp", "humidity": "Humidity",
    "wind_kmh": "Wind speed", "season": "Season", "weathersit": "Weather situation",
    "weekday": "Day of week", "hr": "Hour of day", "mnth": "Month",
    "holiday": "Holiday flag", "workingday": "Working-day flag", "yr": "Year",
    "hr_sin": "Hour (sine)", "hr_cos": "Hour (cosine)",
    "mnth_sin": "Month (sine)", "mnth_cos": "Month (cosine)",
    "weekday_sin": "Weekday (sine)", "weekday_cos": "Weekday (cosine)",
}


# ==========================================================================
# Features
# ==========================================================================
def build_features(hourly: pd.DataFrame):
    """Return X (features), y (target) and the aligned timestamp index."""
    df = hourly.copy()
    for col, period in CYCLIC.items():
        df[f"{col}_sin"] = np.sin(2 * np.pi * df[col] / period)
        df[f"{col}_cos"] = np.cos(2 * np.pi * df[col] / period)

    cyc = [f"{c}_{fn}" for c in CYCLIC for fn in ("sin", "cos")]
    features = NUMERIC + CATEGORICAL + BINARY + cyc
    return df[features].copy(), df["cnt"].copy(), df["timestamp"].copy()


def make_models():
    """Linear baseline needs encoding; tree models take the raw columns."""
    linear_prep = ColumnTransformer(
        [("num", StandardScaler(), NUMERIC),
         ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
          CATEGORICAL)],
        remainder="passthrough")

    return {
        "Linear Regression": Pipeline([("prep", linear_prep),
                                       ("model", LinearRegression())]),
        "Decision Tree": DecisionTreeRegressor(max_depth=12,
                                               min_samples_leaf=10,
                                               random_state=RANDOM_STATE),
        "Random Forest": RandomForestRegressor(n_estimators=300, max_depth=None,
                                               min_samples_leaf=2, n_jobs=-1,
                                               random_state=RANDOM_STATE),
        "Gradient Boosting": HistGradientBoostingRegressor(
            max_iter=400, learning_rate=0.08, max_depth=None,
            random_state=RANDOM_STATE),
    }


def score(y_true, y_pred) -> dict:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


# ==========================================================================
# Train / evaluate
# ==========================================================================
def run(hourly: pd.DataFrame) -> dict:
    X, y, ts = build_features(hourly)

    # --- chronological split (the realistic test) ---------------------
    cut = int(len(X) * 0.8)
    Xtr, Xte = X.iloc[:cut], X.iloc[cut:]
    ytr, yte = y.iloc[:cut], y.iloc[cut:]
    ts_te = ts.iloc[cut:]

    results, preds = {}, {}
    for name, model in make_models().items():
        model.fit(Xtr, ytr)
        p = np.clip(model.predict(Xte), 0, None)   # demand cannot be negative
        results[name] = score(yte, p)
        preds[name] = p

    # Naive reference: always predict the training mean
    results["Baseline (train mean)"] = score(
        yte, np.full(len(yte), ytr.mean()))

    # --- random split, for contrast -----------------------------------
    rXtr, rXte, rytr, ryte = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE)
    random_results = {}
    for name, model in make_models().items():
        model.fit(rXtr, rytr)
        random_results[name] = score(ryte, np.clip(model.predict(rXte), 0, None))

    best = min(results, key=lambda k: results[k]["rmse"])

    # --- time-series cross-validation of the winner --------------------
    cv_model = make_models()[best] if best in make_models() else None
    cv_rmse = []
    if cv_model is not None:
        scores = cross_val_score(cv_model, X, y, cv=TimeSeriesSplit(n_splits=5),
                                 scoring="neg_root_mean_squared_error", n_jobs=-1)
        cv_rmse = [float(-s) for s in scores]

    # --- feature importance from the fitted Random Forest --------------
    rf = make_models()["Random Forest"]
    rf.fit(Xtr, ytr)
    importance = pd.Series(rf.feature_importances_, index=X.columns)\
        .sort_values(ascending=False)

    pd.DataFrame(results).T.round(3).to_csv(TAB / "model_results_chronological.csv")
    pd.DataFrame(random_results).T.round(3).to_csv(TAB / "model_results_random.csv")
    importance.round(4).to_csv(TAB / "feature_importance.csv", header=["importance"])

    return {
        "results": results,
        "random_results": random_results,
        "best_model": best,
        "best_rmse": results[best]["rmse"],
        "best_mae": results[best]["mae"],
        "best_r2": results[best]["r2"],
        "baseline_rmse": results["Baseline (train mean)"]["rmse"],
        "rmse_vs_baseline_pct": round(
            (1 - results[best]["rmse"] / results["Baseline (train mean)"]["rmse"]) * 100, 1),
        "cv_rmse_folds": [round(v, 1) for v in cv_rmse],
        "cv_rmse_mean": round(float(np.mean(cv_rmse)), 1) if cv_rmse else None,
        "cv_rmse_std": round(float(np.std(cv_rmse)), 1) if cv_rmse else None,
        "train_rows": int(len(Xtr)),
        "test_rows": int(len(Xte)),
        "train_end": str(ts.iloc[cut - 1].date()),
        "test_start": str(ts.iloc[cut].date()),
        "test_end": str(ts.iloc[-1].date()),
        "n_features": int(X.shape[1]),
        "top_features": [(PRETTY.get(k, k), round(float(v), 4))
                         for k, v in importance.head(8).items()],
        "_preds": preds, "_yte": yte, "_ts_te": ts_te, "_importance": importance,
    }


# ==========================================================================
# Figures
# ==========================================================================
def fig_model_comparison(res):
    """One model is the story -> EMPHASIS: best in hue, the rest in grey."""
    order = sorted(res["results"], key=lambda k: res["results"][k]["rmse"],
                   reverse=True)
    vals = [res["results"][k]["rmse"] for k in order]
    pos = np.arange(len(order))
    best = res["best_model"]

    fig, ax = plt.subplots(figsize=(9.4, 4.4))
    for p, v, name in zip(pos, vals, order):
        vs.bars(ax, [p], [v], color=vs.BLUE if name == best else vs.DE_EMPHASIS,
                width_pt=16, horizontal=True)
    vs.value_labels(ax, pos, vals, fmt="{:,.1f}", horizontal=True, width_pt=16)

    vs.titled(ax, f"{best} predicts hourly demand most accurately",
              "Test-set RMSE on the chronological split (lower is better)")
    ax.set_yticks(pos)
    ax.set_yticklabels(order)
    ax.set_xlabel("RMSE (rentals per hour)")
    ax.set_xlim(0, max(vals) * 1.16)
    ax.set_ylim(-0.6, len(order) - 0.4)
    axis_numbers(ax, "x")
    grid_only(ax, "x")
    return vs.save(fig, FIG / "fig09_model_comparison.png")


def fig_feature_importance(res, top=12):
    """Ranked magnitude, no identity to carry -> one hue for every bar."""
    imp = res["_importance"].head(top)[::-1]
    pos = np.arange(len(imp))
    labels = [PRETTY.get(k, k) for k in imp.index]

    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    vs.bars(ax, pos, imp.values * 100, color=vs.BLUE, width_pt=13,
            horizontal=True)
    vs.value_labels(ax, pos, imp.values * 100, fmt="{:.1f}%", horizontal=True,
                    width_pt=13)

    vs.titled(ax, "Hour of day dominates; temperature leads the weather terms",
              f"Random Forest feature importance, top {top} of {res['n_features']}")
    ax.set_yticks(pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Share of total importance (%)")
    ax.set_xlim(0, imp.max() * 100 * 1.18)
    ax.set_ylim(-0.6, len(imp) - 0.4)
    grid_only(ax, "x")
    return vs.save(fig, FIG / "fig10_feature_importance.png")


def fig_actual_vs_predicted(res, days=10):
    """Two distinct series over time -> 2 categorical slots + legend."""
    ts_te, yte = res["_ts_te"].reset_index(drop=True), res["_yte"].reset_index(drop=True)
    pred = pd.Series(res["_preds"][res["best_model"]])
    n = days * 24
    t, a, p = ts_te.iloc[:n], yte.iloc[:n], pred.iloc[:n]

    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.plot(t, a, color=vs.BLUE, label="Actual rentals", zorder=3)
    ax.plot(t, p, color=vs.ORANGE, label=f"Predicted ({res['best_model']})",
            zorder=4)

    vs.titled(ax, "The model tracks the daily commuter rhythm closely",
              f"First {days} days of the unseen test period, from {res['test_start']}")
    ax.set_ylabel("Rentals per hour")
    ax.set_ylim(0, None)
    axis_numbers(ax)
    grid_only(ax)
    for lab in ax.get_xticklabels():
        lab.set_rotation(30)
        lab.set_ha("right")
    ax.legend(loc="upper left", ncols=2, bbox_to_anchor=(0, -0.26))
    return vs.save(fig, FIG / "fig11_actual_vs_predicted.png")


def fig_residuals(res):
    """Error structure: one series against a zero baseline."""
    yte = res["_yte"].to_numpy()
    pred = res["_preds"][res["best_model"]]
    resid = yte - pred

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.2))

    ax1.axhline(0, color=vs.AXIS, linewidth=1.2, zorder=2)
    ax1.scatter(pred, resid, s=7, color=vs.BLUE, alpha=0.12, linewidths=0,
                zorder=3)
    vs.titled(ax1, "Errors widen at peak hours",
              "Residual vs predicted demand")
    ax1.set_xlabel("Predicted rentals per hour")
    ax1.set_ylabel("Residual (actual - predicted)")
    axis_numbers(ax1)
    axis_numbers(ax1, "x")
    grid_only(ax1)

    ax2.hist(resid, bins=60, color=vs.BLUE, alpha=0.85, zorder=3)
    ax2.axvline(0, color=vs.AXIS, linewidth=1.2, zorder=4)
    vs.titled(ax2, "Residuals centre near zero",
              f"Distribution of errors   mean = {resid.mean():,.1f}")
    ax2.set_xlabel("Residual (rentals per hour)")
    ax2.set_ylabel("Test hours")
    axis_numbers(ax2)
    grid_only(ax2)

    return vs.save(fig, FIG / "fig12_residuals.png")


def build_all():
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    vs.apply_style()

    res = run(load_hourly())
    paths = [fig_model_comparison(res), fig_feature_importance(res),
             fig_actual_vs_predicted(res), fig_residuals(res)]

    public = {k: v for k, v in res.items() if not k.startswith("_")}
    out = ROOT / "outputs" / "metrics.json"
    existing = json.loads(out.read_text()) if out.exists() else {}
    existing["predictive"] = public
    out.write_text(json.dumps(existing, indent=2))
    return paths, public


if __name__ == "__main__":
    built, public = build_all()
    print(f"{len(built)} model figures written")
    for p in built:
        print("   ", p.name)
    print(json.dumps({k: v for k, v in public.items()
                      if k not in ("results", "random_results")}, indent=2))
    print("\nChronological split:")
    print(pd.DataFrame(public["results"]).T.round(2).to_string())
    print("\nRandom split (optimistic):")
    print(pd.DataFrame(public["random_results"]).T.round(2).to_string())
