#!/usr/bin/env python3
"""Run the second-generation USD/MNT forecasting study."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import PartialDependenceDisplay, permutation_importance
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SEED = 42
HORIZONS = [1, 3, 6, 12]
TARGETS = ["usd_mnt", "cny_mnt"]
ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)

np.random.seed(SEED)


LINEAR_FAMILIES = ["ols", "ridge", "lasso", "elastic_net"]
TREE_FAMILIES = ["random_forest", "extra_trees", "hist_gbm"]


@dataclass
class SplitConfig:
    train_end: int
    val_end: int
    test_end: int
    val_len: int
    test_len: int


def unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            out.append(item)
            seen.add(item)
    return out


def choose_split_config(n_rows: int) -> SplitConfig | None:
    if n_rows >= 180:
        val_len = 18
        test_len = 18
    elif n_rows >= 120:
        val_len = 15
        test_len = 15
    elif n_rows >= 84:
        val_len = 12
        test_len = 12
    elif n_rows >= 60:
        val_len = 10
        test_len = 10
    else:
        return None

    train_end = n_rows - val_len - test_len
    if train_end < 36:
        return None

    return SplitConfig(
        train_end=train_end,
        val_end=train_end + val_len,
        test_end=n_rows,
        val_len=val_len,
        test_len=test_len,
    )


def safe_rmse(actual: pd.Series, pred: pd.Series) -> float:
    return math.sqrt(mean_squared_error(actual, pred))


def build_estimator(family: str, params: dict[str, Any]) -> Pipeline | None:
    if family == "ols":
        reg = LinearRegression()
    elif family == "ridge":
        reg = Ridge(alpha=params["alpha"], random_state=SEED)
    elif family == "lasso":
        reg = Lasso(alpha=params["alpha"], random_state=SEED, max_iter=30000)
    elif family == "elastic_net":
        reg = ElasticNet(
            alpha=params["alpha"],
            l1_ratio=params["l1_ratio"],
            random_state=SEED,
            max_iter=30000,
        )
    elif family == "pca_linear":
        reg = LinearRegression()
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("pca", PCA(n_components=params["n_components"], random_state=SEED)),
                ("reg", reg),
            ]
        )
    elif family == "random_forest":
        reg = RandomForestRegressor(
            n_estimators=100,
            max_depth=params["max_depth"],
            min_samples_leaf=params["min_samples_leaf"],
            random_state=SEED,
            n_jobs=-1,
        )
    elif family == "extra_trees":
        reg = ExtraTreesRegressor(
            n_estimators=100,
            max_depth=params["max_depth"],
            min_samples_leaf=params["min_samples_leaf"],
            random_state=SEED,
            n_jobs=-1,
        )
    elif family == "hist_gbm":
        reg = HistGradientBoostingRegressor(
            learning_rate=params["learning_rate"],
            max_depth=params["max_depth"],
            max_iter=150,
            random_state=SEED,
        )
    elif family == "mlp":
        reg = MLPRegressor(
            hidden_layer_sizes=params["hidden_layer_sizes"],
            alpha=params["alpha"],
            learning_rate_init=params["learning_rate_init"],
            max_iter=600,
            random_state=SEED,
        )
    else:
        return None

    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("reg", reg),
        ]
    )


def model_grids(sample_size: int) -> dict[str, list[dict[str, Any]]]:
    grids: dict[str, list[dict[str, Any]]] = {
        "random_walk": [{}],
        "random_walk_drift": [{}],
        "autoreg": [{"lag_order": lag} for lag in [1, 3, 6]],
        "ols": [{}],
        "ridge": [{"alpha": alpha} for alpha in [0.3, 3.0]],
        "lasso": [{"alpha": alpha} for alpha in [0.003, 0.03]],
        "elastic_net": [
            {"alpha": 0.003, "l1_ratio": 0.3},
            {"alpha": 0.03, "l1_ratio": 0.7},
        ],
        "pca_linear": [{"n_components": n} for n in [3, 6]],
        "random_forest": [
            {"max_depth": 3, "min_samples_leaf": 2},
            {"max_depth": None, "min_samples_leaf": 4},
        ],
        "extra_trees": [
            {"max_depth": 3, "min_samples_leaf": 2},
            {"max_depth": None, "min_samples_leaf": 4},
        ],
        "hist_gbm": [
            {"max_depth": 2, "learning_rate": 0.05},
            {"max_depth": 3, "learning_rate": 0.05},
        ],
    }

    if sample_size >= 180:
        grids["mlp"] = [
            {"hidden_layer_sizes": (32,), "alpha": 0.0001, "learning_rate_init": 0.001},
        ]

    return grids


def enrich_target_frame(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    out = df.copy()
    out["target_level"] = out[target_col]
    out["target_log"] = np.log(out[target_col])
    out["target_change_1"] = out["target_log"].diff()
    out["target_yoy"] = out[target_col].pct_change(12) * 100
    out["target_log_yoy"] = out["target_log"].diff(12)

    for lag in range(1, 13):
        out[f"target_change_l{lag}"] = out["target_change_1"].shift(lag)
        out[f"target_log_l{lag}"] = out["target_log"].shift(lag)

    for horizon in HORIZONS:
        out[f"target_h{horizon}"] = out["target_log"].shift(-horizon) - out["target_log"]

    return out


def prediction_frame(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_h_col: str,
    split_indices: range,
    family: str,
    params: dict[str, Any],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for idx in split_indices:
        train = df.iloc[:idx].copy()
        test = df.iloc[[idx]].copy()

        if family == "random_walk":
            pred_change = 0.0
        elif family == "random_walk_drift":
            pred_change = float(train[target_h_col].mean())
        elif family == "autoreg":
            lag_order = params["lag_order"]
            ar_cols = [f"target_change_l{i}" for i in range(1, lag_order + 1)]
            ar_cols = ["target_log"] + ar_cols
            model = Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    ("reg", LinearRegression()),
                ]
            )
            model.fit(train[ar_cols], train[target_h_col])
            pred_change = float(model.predict(test[ar_cols])[0])
        else:
            model = build_estimator(family, params)
            if model is None:
                raise ValueError(f"Unsupported family: {family}")
            model.fit(train[feature_cols], train[target_h_col])
            pred_change = float(model.predict(test[feature_cols])[0])

        current_log = float(test["target_log"].iloc[0])
        actual_change = float(test[target_h_col].iloc[0])
        actual_log = current_log + actual_change
        pred_log = current_log + pred_change
        current_level = float(np.exp(current_log))
        actual_level = float(np.exp(actual_log))
        pred_level = float(np.exp(pred_log))

        rows.append(
            {
                "period": test["period"].iloc[0],
                "current_level": current_level,
                "actual_change": actual_change,
                "pred_change": pred_change,
                "actual_level": actual_level,
                "pred_level": pred_level,
                "abs_log_error": abs(pred_change - actual_change),
                "error": pred_level - actual_level,
                "abs_error": abs(pred_level - actual_level),
                "ape": abs(pred_level - actual_level) / actual_level * 100,
                "direction_hit": int(np.sign(pred_change) == np.sign(actual_change)),
            }
        )

    return pd.DataFrame(rows)


def metrics_from_predictions(preds: pd.DataFrame) -> dict[str, float]:
    return {
        "rmse": safe_rmse(preds["actual_level"], preds["pred_level"]),
        "mae": mean_absolute_error(preds["actual_level"], preds["pred_level"]),
        "mape": float(preds["ape"].mean()),
        "directional_accuracy": float(preds["direction_hit"].mean()),
    }


def interval_coverage(
    val_preds: pd.DataFrame,
    test_preds: pd.DataFrame,
) -> tuple[dict[str, float], dict[str, float], pd.DataFrame]:
    q80 = float(val_preds["abs_log_error"].quantile(0.8))
    q95 = float(val_preds["abs_log_error"].quantile(0.95))

    out = test_preds.copy()
    for label, q in [("80", q80), ("95", q95)]:
        out[f"lo_{label}"] = np.exp(np.log(out["current_level"]) + out["pred_change"] - q)
        out[f"hi_{label}"] = np.exp(np.log(out["current_level"]) + out["pred_change"] + q)
        out[f"covered_{label}"] = (
            (out["actual_level"] >= out[f"lo_{label}"])
            & (out["actual_level"] <= out[f"hi_{label}"])
        ).astype(int)

    coverage = {
        "coverage_80": float(out["covered_80"].mean()),
        "coverage_95": float(out["covered_95"].mean()),
    }
    quantiles = {"q80": q80, "q95": q95}
    return coverage, quantiles, out


def evaluate_family(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_h_col: str,
    split: SplitConfig,
    family: str,
    grid: list[dict[str, Any]],
) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    best_record: pd.Series | None = None
    best_val_preds: pd.DataFrame | None = None
    best_test_preds: pd.DataFrame | None = None

    for params in grid:
        val_preds = prediction_frame(
            df,
            feature_cols,
            target_h_col,
            range(split.train_end, split.val_end),
            family,
            params,
        )
        val_metrics = metrics_from_predictions(val_preds)
        row = pd.Series(
            {
                "family": family,
                "params": json.dumps(params, sort_keys=True),
                "val_rmse": val_metrics["rmse"],
                "val_mae": val_metrics["mae"],
                "val_mape": val_metrics["mape"],
                "val_directional_accuracy": val_metrics["directional_accuracy"],
            }
        )

        if best_record is None or row["val_rmse"] < best_record["val_rmse"]:
            best_record = row
            best_val_preds = val_preds
            best_test_preds = prediction_frame(
                df,
                feature_cols,
                target_h_col,
                range(split.val_end, split.test_end),
                family,
                params,
            )

    if best_record is None or best_val_preds is None or best_test_preds is None:
        raise RuntimeError(f"No result for family {family}")

    test_metrics = metrics_from_predictions(best_test_preds)
    coverage, quantiles, test_with_intervals = interval_coverage(best_val_preds, best_test_preds)

    for key, value in test_metrics.items():
        best_record[f"test_{key}"] = value
    for key, value in coverage.items():
        best_record[f"test_{key}"] = value
    best_record["interval_q80"] = quantiles["q80"]
    best_record["interval_q95"] = quantiles["q95"]

    best_val_preds = best_val_preds.assign(split="validation", family=family, params=best_record["params"])
    test_with_intervals = test_with_intervals.assign(
        split="test", family=family, params=best_record["params"]
    )
    return best_record, best_val_preds, test_with_intervals


def plain_language_effect(target: str, feature: str, coefficient: float) -> str:
    stronger = "lower future USD/MNT (a stronger tugrik)" if target == "usd_mnt" else "lower future CNY/MNT"
    weaker = "higher future USD/MNT (a weaker tugrik)" if target == "usd_mnt" else "higher future CNY/MNT"
    direction = weaker if coefficient > 0 else stronger

    if "reserve" in feature:
        return f"Higher reserves tend to line up with {direction}."
    if "current_account" in feature or "financial_account" in feature:
        return f"Changes in the external balance tend to line up with {direction}."
    if "trade_balance" in feature or "exports" in feature or "imports" in feature:
        return f"Trade conditions tend to line up with {direction}."
    if "dxy" in feature:
        return f"A stronger broad U.S. dollar tends to line up with {direction}."
    if "gold" in feature or "copper" in feature or "coal" in feature:
        return f"Commodity-price moves tend to line up with {direction}."
    if "cpi" in feature or "inflation" in feature:
        return f"Inflation pressure tends to line up with {direction}."
    if "cny" in feature:
        return f"Moves in the yuan-related exchange rate tend to line up with {direction}."
    return f"Higher values of this feature tend to line up with {direction}."


def fit_linear_coefficients(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_h_col: str,
    family: str,
    params: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fit_rows: list[pd.Series] = []
    model = build_estimator(family, params)
    if model is None:
        raise ValueError(f"Unsupported linear family: {family}")

    model.fit(df[feature_cols], df[target_h_col])
    reg = model.named_steps["reg"]

    full = pd.DataFrame(
        {
            "feature": feature_cols,
            "coef_full_sample": reg.coef_,
            "abs_coef_full_sample": np.abs(reg.coef_),
        }
    )

    start_idx = max(36, int(len(df) * 0.6))
    for idx in range(start_idx, len(df)):
        window = df.iloc[:idx].copy()
        local = build_estimator(family, params)
        if local is None:
            continue
        local.fit(window[feature_cols], window[target_h_col])
        coef = local.named_steps["reg"].coef_
        fit_rows.append(pd.Series(coef, index=feature_cols))

    stability = pd.DataFrame(fit_rows)
    summary = pd.DataFrame({"feature": feature_cols})
    if not stability.empty:
        summary["coef_median_oos"] = stability.median().values
        summary["positive_share_oos"] = (stability > 0).mean().values
        summary["negative_share_oos"] = (stability < 0).mean().values
    else:
        summary["coef_median_oos"] = np.nan
        summary["positive_share_oos"] = np.nan
        summary["negative_share_oos"] = np.nan

    merged = full.merge(summary, on="feature", how="left")
    merged = merged.sort_values("abs_coef_full_sample", ascending=False).reset_index(drop=True)
    return merged, stability


def fit_tree_importance(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_h_col: str,
    family: str,
    params: dict[str, Any],
    plot_prefix: str,
) -> pd.DataFrame:
    model = build_estimator(family, params)
    if model is None:
        raise ValueError(f"Unsupported tree family: {family}")
    model.fit(df[feature_cols], df[target_h_col])

    importance = permutation_importance(
        model,
        df[feature_cols],
        df[target_h_col],
        n_repeats=10,
        random_state=SEED,
        n_jobs=-1,
    )
    imp_df = pd.DataFrame(
        {
            "feature": feature_cols,
            "importance_mean": importance.importances_mean,
            "importance_std": importance.importances_std,
        }
    ).sort_values("importance_mean", ascending=False)

    top_features = imp_df.head(3)["feature"].tolist()
    if top_features:
        fig, ax = plt.subplots(figsize=(10, 6))
        PartialDependenceDisplay.from_estimator(model, df[feature_cols], top_features, ax=ax)
        fig.tight_layout()
        fig.savefig(OUTPUTS / f"{plot_prefix}_partial_dependence.png", dpi=180)
        plt.close(fig)

    return imp_df


def load_panels() -> dict[str, pd.DataFrame]:
    panels = {}
    for name in ["feature_panel_long_history.csv", "feature_panel_rich.csv"]:
        df = pd.read_csv(DERIVED / name)
        df["period"] = pd.PeriodIndex(df["period"], freq="M").to_timestamp("M")
        panels[name.replace(".csv", "")] = df
    return panels


def candidate_family_list(target: str, best_linear_family: str | None, best_tree_family: str | None, sample_size: int) -> list[str]:
    if target == "usd_mnt":
        families = list(model_grids(sample_size).keys())
    else:
        families = ["random_walk", "autoreg"]
        if best_linear_family:
            families.append(best_linear_family)
        if best_tree_family:
            families.append(best_tree_family)
    seen: set[str] = set()
    ordered: list[str] = []
    for family in families:
        if family not in seen:
            ordered.append(family)
            seen.add(family)
    return ordered


def get_macro_feature_cols(df: pd.DataFrame, target: str) -> list[str]:
    exclude = {"period", "usd_mnt", "cny_mnt", "usd_mnt_log", "cny_mnt_log"}
    cols = [c for c in df.columns if c not in exclude]
    cols = [c for c in cols if not c.startswith("target_")]
    if target == "usd_mnt":
        cols = [c for c in cols if c not in {"usd_mnt_log"}]
    else:
        cols = [c for c in cols if c not in {"cny_mnt_log"}]
    return cols


def plot_leaderboard(results: pd.DataFrame) -> None:
    usd = results[results["target"] == "usd_mnt"].copy()
    if usd.empty:
        return

    pivot = usd.pivot_table(
        index=["family", "panel"],
        columns="horizon_months",
        values="test_rmse_vs_random_walk",
        aggfunc="first",
    ).sort_index()
    fig, ax = plt.subplots(figsize=(12, 8))
    pivot.plot(kind="bar", ax=ax)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_title("USD/MNT Model Leaderboard (RMSE relative to random walk)")
    ax.set_xlabel("Model family / panel")
    ax.set_ylabel("RMSE ratio vs random walk")
    ax.tick_params(axis="x", rotation=55)
    fig.tight_layout()
    fig.savefig(OUTPUTS / "usd_mnt_model_leaderboard.png", dpi=180)
    plt.close(fig)


def plot_live_forecast(live: pd.DataFrame) -> None:
    usd = live[live["target"] == "usd_mnt"].copy().sort_values("horizon_months")
    if usd.empty:
        return

    x = np.arange(len(usd))
    labels = usd["horizon_months"].astype(str).tolist()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, usd["forecast_point"], marker="o", label="Champion forecast")
    ax.fill_between(x, usd["interval95_lo"], usd["interval95_hi"], alpha=0.2, label="95% interval")
    ax.fill_between(x, usd["interval80_lo"], usd["interval80_hi"], alpha=0.35, label="80% interval")
    ax.plot(x, usd["ensemble_mean"], marker="s", linestyle="--", label="Ensemble mean")
    ax.set_xticks(x, labels)
    ax.set_title(f"USD/MNT live forecast as of {usd['as_of_period'].iloc[0]}")
    ax.set_xlabel("Forecast horizon (months)")
    ax.set_ylabel("USD/MNT")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUTS / "usd_mnt_live_forecast.png", dpi=180)
    plt.close(fig)


def plot_cny_comparison(results: pd.DataFrame) -> None:
    subset = results[results["target"].isin(["usd_mnt", "cny_mnt"])].copy()
    if subset.empty:
        return
    summary = (
        subset.groupby(["target", "horizon_months"], as_index=False)["test_rmse_vs_random_walk"]
        .min()
        .sort_values(["target", "horizon_months"])
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    for target, group in summary.groupby("target"):
        ax.plot(group["horizon_months"], group["test_rmse_vs_random_walk"], marker="o", label=target)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_title("Best relative forecasting gain: USD/MNT vs CNY/MNT")
    ax.set_xlabel("Forecast horizon (months)")
    ax.set_ylabel("Best RMSE ratio vs random walk")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUTS / "usd_vs_cny_comparison.png", dpi=180)
    plt.close(fig)


def main() -> None:
    panels = load_panels()

    results_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    champion_rows: list[dict[str, Any]] = []
    feature_effect_rows: list[pd.DataFrame] = []
    tree_importance_rows: list[pd.DataFrame] = []
    live_rows: list[dict[str, Any]] = []

    usd_results_cache: list[dict[str, Any]] = []

    best_linear_family: str | None = None
    best_tree_family: str | None = None

    # Phase 1: full USD/MNT zoo
    for panel_name, panel in panels.items():
        target_frame = enrich_target_frame(panel, "usd_mnt")
        macro_feature_cols = get_macro_feature_cols(target_frame, "usd_mnt")
        all_feature_cols = unique_preserve_order(
            ["target_log", "target_yoy"]
            + [f"target_change_l{lag}" for lag in range(1, 13)]
            + macro_feature_cols
        )

        for horizon in HORIZONS:
            target_h_col = f"target_h{horizon}"
            cols_needed = unique_preserve_order(
                ["period", "target_level", "target_log", target_h_col] + all_feature_cols
            )
            df = target_frame[cols_needed].dropna(subset=["target_level", "target_log", target_h_col]).copy()
            split = choose_split_config(len(df))
            if split is None:
                continue

            families = candidate_family_list("usd_mnt", None, None, len(df))
            grids = model_grids(len(df))
            family_result_rows = []
            print(
                f"[USD] panel={panel_name} horizon={horizon} rows={len(df)} "
                f"train={split.train_end} val={split.val_len} test={split.test_len} "
                f"families={len(families)}",
                flush=True,
            )

            for family in families:
                print(f"  fitting {family}", flush=True)
                feature_cols = all_feature_cols
                record, val_preds, test_preds = evaluate_family(
                    df,
                    feature_cols,
                    target_h_col,
                    split,
                    family,
                    grids[family],
                )
                record = record.to_dict()
                record.update(
                    {
                        "target": "usd_mnt",
                        "panel": panel_name,
                        "horizon_months": horizon,
                        "n_rows": len(df),
                        "n_train": split.train_end,
                        "n_val": split.val_len,
                        "n_test": split.test_len,
                    }
                )
                family_result_rows.append(record)
                prediction_frames.append(
                    pd.concat([val_preds, test_preds], ignore_index=True).assign(
                        target="usd_mnt",
                        panel=panel_name,
                        horizon_months=horizon,
                    )
                )

            family_results = pd.DataFrame(family_result_rows)
            rw_rmse = float(
                family_results.loc[family_results["family"] == "random_walk", "test_rmse"].iloc[0]
            )
            family_results["test_rmse_vs_random_walk"] = family_results["test_rmse"] / rw_rmse
            family_results["val_rmse_vs_random_walk"] = (
                family_results["val_rmse"]
                / float(family_results.loc[family_results["family"] == "random_walk", "val_rmse"].iloc[0])
            )
            results_rows.extend(family_results.to_dict("records"))
            usd_results_cache.extend(family_results.to_dict("records"))

    usd_results = pd.DataFrame(usd_results_cache)
    linear_summary = (
        usd_results[usd_results["family"].isin(LINEAR_FAMILIES)]
        .groupby("family", as_index=False)["val_rmse_vs_random_walk"]
        .mean()
        .sort_values("val_rmse_vs_random_walk")
    )
    tree_summary = (
        usd_results[usd_results["family"].isin(TREE_FAMILIES)]
        .groupby("family", as_index=False)["val_rmse_vs_random_walk"]
        .mean()
        .sort_values("val_rmse_vs_random_walk")
    )
    if not linear_summary.empty:
        best_linear_family = str(linear_summary["family"].iloc[0])
    if not tree_summary.empty:
        best_tree_family = str(tree_summary["family"].iloc[0])

    # Phase 2: reduced CNY/MNT suite
    for panel_name, panel in panels.items():
        target_frame = enrich_target_frame(panel, "cny_mnt")
        macro_feature_cols = get_macro_feature_cols(target_frame, "cny_mnt")
        all_feature_cols = unique_preserve_order(
            ["target_log", "target_yoy"]
            + [f"target_change_l{lag}" for lag in range(1, 13)]
            + macro_feature_cols
        )

        for horizon in HORIZONS:
            target_h_col = f"target_h{horizon}"
            cols_needed = unique_preserve_order(
                ["period", "target_level", "target_log", target_h_col] + all_feature_cols
            )
            df = target_frame[cols_needed].dropna(subset=["target_level", "target_log", target_h_col]).copy()
            split = choose_split_config(len(df))
            if split is None:
                continue

            families = candidate_family_list("cny_mnt", best_linear_family, best_tree_family, len(df))
            grids = model_grids(len(df))
            family_result_rows = []
            print(
                f"[CNY] panel={panel_name} horizon={horizon} rows={len(df)} "
                f"train={split.train_end} val={split.val_len} test={split.test_len} "
                f"families={len(families)}",
                flush=True,
            )

            for family in families:
                print(f"  fitting {family}", flush=True)
                record, val_preds, test_preds = evaluate_family(
                    df,
                    all_feature_cols,
                    target_h_col,
                    split,
                    family,
                    grids[family],
                )
                record = record.to_dict()
                record.update(
                    {
                        "target": "cny_mnt",
                        "panel": panel_name,
                        "horizon_months": horizon,
                        "n_rows": len(df),
                        "n_train": split.train_end,
                        "n_val": split.val_len,
                        "n_test": split.test_len,
                    }
                )
                family_result_rows.append(record)
                prediction_frames.append(
                    pd.concat([val_preds, test_preds], ignore_index=True).assign(
                        target="cny_mnt",
                        panel=panel_name,
                        horizon_months=horizon,
                    )
                )

            family_results = pd.DataFrame(family_result_rows)
            rw_rmse = float(
                family_results.loc[family_results["family"] == "random_walk", "test_rmse"].iloc[0]
            )
            family_results["test_rmse_vs_random_walk"] = family_results["test_rmse"] / rw_rmse
            family_results["val_rmse_vs_random_walk"] = (
                family_results["val_rmse"]
                / float(family_results.loc[family_results["family"] == "random_walk", "val_rmse"].iloc[0])
            )
            results_rows.extend(family_results.to_dict("records"))

    results = pd.DataFrame(results_rows)

    # Champion selection
    for target in TARGETS:
        for horizon in HORIZONS:
            subset = results[(results["target"] == target) & (results["horizon_months"] == horizon)].copy()
            if subset.empty:
                continue

            subset = subset.sort_values(["val_rmse_vs_random_walk", "val_rmse", "panel", "family"])
            best = subset.iloc[0].to_dict()

            if best["val_rmse_vs_random_walk"] >= 1.0:
                best_rw = (
                    subset[subset["family"] == "random_walk"]
                    .sort_values(["val_rmse", "panel"])
                    .iloc[0]
                    .to_dict()
                )
                champion_rows.append(
                    {
                        "target": target,
                        "horizon_months": horizon,
                        "champion_family": best_rw["family"],
                        "champion_panel": best_rw["panel"],
                        "champion_params": best_rw["params"],
                        "champion_val_rmse": best_rw["val_rmse"],
                        "champion_val_rmse_vs_random_walk": 1.0,
                        "champion_test_rmse": best_rw["test_rmse"],
                        "champion_test_rmse_vs_random_walk": best_rw["test_rmse_vs_random_walk"],
                        "reason": "No model beat random walk on validation, so random walk stays champion.",
                    }
                )
            else:
                champion_rows.append(
                    {
                        "target": target,
                        "horizon_months": horizon,
                        "champion_family": best["family"],
                        "champion_panel": best["panel"],
                        "champion_params": best["params"],
                        "champion_val_rmse": best["val_rmse"],
                        "champion_val_rmse_vs_random_walk": best["val_rmse_vs_random_walk"],
                        "champion_test_rmse": best["test_rmse"],
                        "champion_test_rmse_vs_random_walk": best["test_rmse_vs_random_walk"],
                        "reason": "Selected on validation RMSE ratio versus random walk; final test kept for reporting.",
                    }
                )

    champions = pd.DataFrame(champion_rows)

    # Interpretation layers for USD/MNT: best linear and best tree challengers by validation
    for horizon in HORIZONS:
        horizon_results = results[
            (results["target"] == "usd_mnt") & (results["horizon_months"] == horizon)
        ].copy()
        if horizon_results.empty:
            continue

        best_linear = (
            horizon_results[horizon_results["family"].isin(LINEAR_FAMILIES)]
            .sort_values(["val_rmse_vs_random_walk", "val_rmse", "panel", "family"])
            .head(1)
        )
        if not best_linear.empty:
            row = best_linear.iloc[0]
            panel_name = str(row["panel"])
            family = str(row["family"])
            params = json.loads(str(row["params"]))
            panel = enrich_target_frame(panels[panel_name], "usd_mnt")
            macro_feature_cols = get_macro_feature_cols(panel, "usd_mnt")
            all_feature_cols = unique_preserve_order(
                ["target_log", "target_yoy"]
                + [f"target_change_l{lag}" for lag in range(1, 13)]
                + macro_feature_cols
            )
            target_h_col = f"target_h{horizon}"
            train_df = panel[
                unique_preserve_order(["period", "target_level", "target_log", target_h_col] + all_feature_cols)
            ].dropna(subset=["target_level", "target_log", target_h_col] + all_feature_cols)
            effect_df, stability_df = fit_linear_coefficients(
                train_df, all_feature_cols, target_h_col, family, params
            )
            effect_df.insert(0, "analysis_role", "best_linear_interpretable")
            effect_df.insert(1, "target", "usd_mnt")
            effect_df.insert(2, "horizon_months", horizon)
            effect_df.insert(3, "panel", panel_name)
            effect_df.insert(4, "family", family)
            effect_df["interpretation"] = effect_df.apply(
                lambda item: plain_language_effect("usd_mnt", item["feature"], float(item["coef_full_sample"])),
                axis=1,
            )
            feature_effect_rows.append(effect_df)
            stability_df.to_csv(OUTPUTS / f"usd_mnt_h{horizon}_{family}_coef_path.csv", index=False)

        best_tree = (
            horizon_results[horizon_results["family"].isin(TREE_FAMILIES)]
            .sort_values(["val_rmse_vs_random_walk", "val_rmse", "panel", "family"])
            .head(1)
        )
        if not best_tree.empty:
            row = best_tree.iloc[0]
            panel_name = str(row["panel"])
            family = str(row["family"])
            params = json.loads(str(row["params"]))
            panel = enrich_target_frame(panels[panel_name], "usd_mnt")
            macro_feature_cols = get_macro_feature_cols(panel, "usd_mnt")
            all_feature_cols = unique_preserve_order(
                ["target_log", "target_yoy"]
                + [f"target_change_l{lag}" for lag in range(1, 13)]
                + macro_feature_cols
            )
            target_h_col = f"target_h{horizon}"
            train_df = panel[
                unique_preserve_order(["period", "target_level", "target_log", target_h_col] + all_feature_cols)
            ].dropna(subset=["target_level", "target_log", target_h_col] + all_feature_cols)
            tree_imp = fit_tree_importance(
                train_df,
                all_feature_cols,
                target_h_col,
                family,
                params,
                plot_prefix=f"usd_mnt_h{horizon}_{family}",
            )
            tree_imp.insert(0, "analysis_role", "best_tree_nonlinear")
            tree_imp.insert(1, "target", "usd_mnt")
            tree_imp.insert(2, "horizon_months", horizon)
            tree_imp.insert(3, "panel", panel_name)
            tree_imp.insert(4, "family", family)
            tree_importance_rows.append(tree_imp)

    # Live forecasts for USD/MNT using validation-selected champions
    for _, champion in champions[champions["target"] == "usd_mnt"].iterrows():
        horizon = int(champion["horizon_months"])
        panel_name = champion["champion_panel"]
        family = champion["champion_family"]
        params = json.loads(champion["champion_params"])

        panel = enrich_target_frame(panels[panel_name], "usd_mnt")
        macro_feature_cols = get_macro_feature_cols(panel, "usd_mnt")
        all_feature_cols = unique_preserve_order(
            ["target_log", "target_yoy"]
            + [f"target_change_l{lag}" for lag in range(1, 13)]
            + macro_feature_cols
        )
        target_h_col = f"target_h{horizon}"
        model_df = panel[
            unique_preserve_order(["period", "target_level", "target_log", target_h_col] + all_feature_cols)
        ].dropna(subset=["target_level", "target_log"] + all_feature_cols)
        train_df = model_df.dropna(subset=[target_h_col]).copy()
        live_row = model_df.tail(1).copy()

        # Live forecast
        model = build_estimator(family, params)
        if family == "random_walk":
            pred_change = 0.0
            q80 = float(results[(results["target"] == "usd_mnt") & (results["panel"] == panel_name) & (results["horizon_months"] == horizon) & (results["family"] == family)]["interval_q80"].iloc[0])
            q95 = float(results[(results["target"] == "usd_mnt") & (results["panel"] == panel_name) & (results["horizon_months"] == horizon) & (results["family"] == family)]["interval_q95"].iloc[0])
        elif family == "random_walk_drift":
            pred_change = float(train_df[target_h_col].mean())
            q80 = float(results[(results["target"] == "usd_mnt") & (results["panel"] == panel_name) & (results["horizon_months"] == horizon) & (results["family"] == family)]["interval_q80"].iloc[0])
            q95 = float(results[(results["target"] == "usd_mnt") & (results["panel"] == panel_name) & (results["horizon_months"] == horizon) & (results["family"] == family)]["interval_q95"].iloc[0])
        elif family == "autoreg":
            lag_order = params["lag_order"]
            ar_cols = ["target_log"] + [f"target_change_l{i}" for i in range(1, lag_order + 1)]
            model = Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    ("reg", LinearRegression()),
                ]
            )
            model.fit(train_df[ar_cols], train_df[target_h_col])
            pred_change = float(model.predict(live_row[ar_cols])[0])
            q80 = float(results[(results["target"] == "usd_mnt") & (results["panel"] == panel_name) & (results["horizon_months"] == horizon) & (results["family"] == family)]["interval_q80"].iloc[0])
            q95 = float(results[(results["target"] == "usd_mnt") & (results["panel"] == panel_name) & (results["horizon_months"] == horizon) & (results["family"] == family)]["interval_q95"].iloc[0])
        else:
            assert model is not None
            model.fit(train_df[all_feature_cols], train_df[target_h_col])
            pred_change = float(model.predict(live_row[all_feature_cols])[0])
            q80 = float(results[(results["target"] == "usd_mnt") & (results["panel"] == panel_name) & (results["horizon_months"] == horizon) & (results["family"] == family)]["interval_q80"].iloc[0])
            q95 = float(results[(results["target"] == "usd_mnt") & (results["panel"] == panel_name) & (results["horizon_months"] == horizon) & (results["family"] == family)]["interval_q95"].iloc[0])

        current_log = float(live_row["target_log"].iloc[0])
        forecast_point = float(np.exp(current_log + pred_change))
        interval80_lo = float(np.exp(current_log + pred_change - q80))
        interval80_hi = float(np.exp(current_log + pred_change + q80))
        interval95_lo = float(np.exp(current_log + pred_change - q95))
        interval95_hi = float(np.exp(current_log + pred_change + q95))

        top_models = (
            results[(results["target"] == "usd_mnt") & (results["horizon_months"] == horizon)]
            .sort_values(["val_rmse_vs_random_walk", "val_rmse", "panel", "family"])
            .head(3)
        )
        ensemble_points = []
        for _, candidate in top_models.iterrows():
            candidate_panel = candidate["panel"]
            candidate_family = candidate["family"]
            candidate_params = json.loads(candidate["params"])
            candidate_df = enrich_target_frame(panels[candidate_panel], "usd_mnt")
            candidate_macro = get_macro_feature_cols(candidate_df, "usd_mnt")
            candidate_features = unique_preserve_order(
                ["target_log", "target_yoy"]
                + [f"target_change_l{lag}" for lag in range(1, 13)]
                + candidate_macro
            )
            candidate_target_h = f"target_h{horizon}"
            candidate_train = candidate_df[
                unique_preserve_order(
                    ["period", "target_level", "target_log", candidate_target_h] + candidate_features
                )
            ].dropna(subset=["target_level", "target_log", candidate_target_h] + candidate_features)
            candidate_live = candidate_df[
                unique_preserve_order(
                    ["period", "target_level", "target_log", candidate_target_h] + candidate_features
                )
            ].dropna(subset=["target_level", "target_log"] + candidate_features).tail(1)

            if candidate_family == "random_walk":
                candidate_change = 0.0
            elif candidate_family == "random_walk_drift":
                candidate_change = float(candidate_train[candidate_target_h].mean())
            elif candidate_family == "autoreg":
                lag_order = candidate_params["lag_order"]
                ar_cols = ["target_log"] + [f"target_change_l{i}" for i in range(1, lag_order + 1)]
                candidate_model = Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                        ("reg", LinearRegression()),
                    ]
                )
                candidate_model.fit(candidate_train[ar_cols], candidate_train[candidate_target_h])
                candidate_change = float(candidate_model.predict(candidate_live[ar_cols])[0])
            else:
                candidate_model = build_estimator(candidate_family, candidate_params)
                if candidate_model is None:
                    continue
                candidate_model.fit(candidate_train[candidate_features], candidate_train[candidate_target_h])
                candidate_change = float(candidate_model.predict(candidate_live[candidate_features])[0])

            ensemble_points.append(float(np.exp(float(candidate_live["target_log"].iloc[0]) + candidate_change)))

        live_rows.append(
            {
                "target": "usd_mnt",
                "as_of_period": live_row["period"].iloc[0].strftime("%Y-%m"),
                "horizon_months": horizon,
                "current_level": float(np.exp(current_log)),
                "champion_panel": panel_name,
                "champion_family": family,
                "forecast_point": forecast_point,
                "interval80_lo": interval80_lo,
                "interval80_hi": interval80_hi,
                "interval95_lo": interval95_lo,
                "interval95_hi": interval95_hi,
                "ensemble_mean": float(np.mean(ensemble_points)),
                "ensemble_min": float(np.min(ensemble_points)),
                "ensemble_max": float(np.max(ensemble_points)),
                "top_models": "; ".join(top_models["family"].tolist()),
            }
        )

    results.to_csv(DERIVED / "forecast_study_model_results.csv", index=False)
    pd.concat(prediction_frames, ignore_index=True).to_csv(
        DERIVED / "forecast_study_predictions.csv", index=False
    )
    champions.to_csv(DERIVED / "forecast_study_champions.csv", index=False)

    if feature_effect_rows:
        pd.concat(feature_effect_rows, ignore_index=True).to_csv(
            DERIVED / "forecast_study_feature_effects.csv", index=False
        )
    if tree_importance_rows:
        pd.concat(tree_importance_rows, ignore_index=True).to_csv(
            DERIVED / "forecast_study_tree_importance.csv", index=False
        )

    live_df = pd.DataFrame(live_rows)
    live_df.to_csv(DERIVED / "forecast_study_live_forecasts.csv", index=False)

    family_summary = (
        results[results["target"] == "usd_mnt"]
        .groupby("family", as_index=False)[["val_rmse_vs_random_walk", "test_rmse_vs_random_walk"]]
        .mean()
        .sort_values(["val_rmse_vs_random_walk", "test_rmse_vs_random_walk"])
    )
    family_summary.to_csv(DERIVED / "forecast_study_usd_family_summary.csv", index=False)

    plot_leaderboard(results)
    plot_live_forecast(live_df)
    plot_cny_comparison(results)

    summary = {
        "best_linear_family_usd": best_linear_family,
        "best_tree_family_usd": best_tree_family,
        "result_rows": int(len(results)),
        "prediction_rows": int(sum(len(frame) for frame in prediction_frames)),
        "champion_rows": int(len(champions)),
        "live_rows": int(len(live_df)),
    }
    (DERIVED / "forecast_study_summary.json").write_text(json.dumps(summary, indent=2))
    print("[done] wrote study outputs", flush=True)

    print(f"Saved {DERIVED / 'forecast_study_model_results.csv'}")
    print(f"Saved {DERIVED / 'forecast_study_predictions.csv'}")
    print(f"Saved {DERIVED / 'forecast_study_champions.csv'}")
    if feature_effect_rows:
        print(f"Saved {DERIVED / 'forecast_study_feature_effects.csv'}")
    if tree_importance_rows:
        print(f"Saved {DERIVED / 'forecast_study_tree_importance.csv'}")
    print(f"Saved {DERIVED / 'forecast_study_live_forecasts.csv'}")
    print(f"Saved {DERIVED / 'forecast_study_usd_family_summary.csv'}")
    print(f"Saved {DERIVED / 'forecast_study_summary.json'}")
    print(f"Saved charts under {OUTPUTS}")


if __name__ == "__main__":
    main()
