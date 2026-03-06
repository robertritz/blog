#!/usr/bin/env python3
"""Export research outputs into public data artifacts for the /tugrik dashboard."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

STUDY_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = STUDY_ROOT.parents[1]
DERIVED = STUDY_ROOT / "data" / "derived"
ARCHIVE = STUDY_ROOT / "data" / "archive"
PUBLIC = PROJECT_ROOT / "public" / "data" / "tugrik"

ARCHIVE.mkdir(parents=True, exist_ok=True)
PUBLIC.mkdir(parents=True, exist_ok=True)

LIVE_ARCHIVE_FILE = ARCHIVE / "published_live_forecasts.csv"
DASHBOARD_JSON = PUBLIC / "dashboard.json"
CURRENT_FORECAST_CSV = PUBLIC / "current_forecast.csv"
FORECAST_VINTAGES_CSV = PUBLIC / "forecast_vintages.csv"
BACKTEST_SUMMARY_CSV = PUBLIC / "backtest_summary.csv"

HORIZONS = [1, 3, 6, 12]
NON_PUBLIC_DRIVER_PREFIXES = ("target_",)


@dataclass
class ExportContext:
    run_timestamp: str
    aligned_as_of_period: str
    source_freshness_key: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify the required research outputs and exit without writing public files.",
    )
    parser.add_argument(
        "--skip-if-unchanged",
        action="store_true",
        help="Skip writing public artifacts if as-of period and source freshness are unchanged.",
    )
    return parser.parse_args()


def read_csv(name: str) -> pd.DataFrame:
    path = DERIVED / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required derived file: {path}")
    return pd.read_csv(path)


def read_json(name: str) -> dict[str, Any]:
    path = DERIVED / name
    if not path.exists():
        raise FileNotFoundError(f"Missing required derived file: {path}")
    return json.loads(path.read_text())


def iso_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def period_to_date(period: str) -> pd.Timestamp:
    return pd.Period(period, freq="M").to_timestamp("M")


def period_add(period: str, months: int) -> str:
    return str(pd.Period(period, freq="M") + months)


def format_feature_label(feature: str) -> str:
    labels = {
        "coal_price": "Coal price",
        "coal_price_yoy": "Coal price (y/y)",
        "coal_price_mom": "Coal price (m/m)",
        "copper_price": "Copper price",
        "copper_price_yoy": "Copper price (y/y)",
        "copper_price_mom": "Copper price (m/m)",
        "gold_price": "Gold price",
        "gold_price_yoy": "Gold price (y/y)",
        "gold_price_mom": "Gold price (m/m)",
        "oil_brent_price": "Brent oil price",
        "oil_brent_price_yoy": "Brent oil price (y/y)",
        "oil_brent_price_mom": "Brent oil price (m/m)",
        "dxy_broad": "Broad USD index",
        "dxy_broad_yoy": "Broad USD index (y/y)",
        "dxy_broad_mom": "Broad USD index (m/m)",
        "us_policy_rate": "U.S. policy rate",
        "us_policy_rate_change_12m": "Change in U.S. policy rate (12m)",
        "financial_account_3mma": "Financial account (3m avg)",
        "current_account_3mma": "Current account (3m avg)",
        "reserve_assets_3mma": "Reserve assets (3m avg)",
        "net_errors_3mma": "Net errors and omissions (3m avg)",
        "trade_balance_share": "Trade balance share",
        "exports_yoy": "Exports (y/y)",
        "imports_yoy": "Imports (y/y)",
        "cpi_yoy_percent": "CPI inflation (y/y)",
        "cpi_mom_percent": "CPI inflation (m/m)",
        "cny_mnt_mom": "CNY/MNT monthly change",
        "cny_mnt_yoy": "CNY/MNT yearly change",
        "cny_mnt": "CNY/MNT",
        "neer_yoy": "NEER (y/y)",
        "reer_yoy": "REER (y/y)",
    }
    if feature in labels:
        return labels[feature]
    return feature.replace("_", " ").replace("mma", "m avg").title()


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if value is None:
        return None
    if pd.isna(value):
        return None
    return value


def staleness_status(aligned_as_of_period: str) -> str:
    now_period = pd.Period(datetime.now(timezone.utc).strftime("%Y-%m"), freq="M")
    as_of = pd.Period(aligned_as_of_period, freq="M")
    lag = now_period.ordinal - as_of.ordinal
    if lag <= 1:
        return "fresh"
    if lag <= 3:
        return "watch"
    return "stale"


def build_source_updates() -> tuple[list[dict[str, Any]], str]:
    series_specs = [
        ("usd_mnt_monthly.csv", "USD/MNT monthly", "usd_mnt"),
        ("cny_mnt_monthly.csv", "CNY/MNT monthly", "cny_mnt"),
        ("nso_trade_monthly.csv", "NSO foreign trade", "exports"),
        ("nso_cpi_headline_monthly.csv", "NSO CPI", "cpi_yoy_percent"),
        ("nso_industry_monthly.csv", "NSO industry", "industrial_output_total"),
        ("global_factors_monthly.csv", "Global factors", "dxy_broad"),
        ("feature_panel_long_history.csv", "Long-history panel", "usd_mnt"),
        ("forecast_study_live_forecasts.csv", "Forecast package", "forecast_point"),
    ]

    updates: list[dict[str, Any]] = []
    freshness_candidates: list[str] = []

    for filename, label, value_col in series_specs:
        path = DERIVED / filename
        if not path.exists():
            continue
        df = pd.read_csv(path)
        last_period = None
        if "period" in df.columns and not df.empty:
            last_period = str(df["period"].dropna().iloc[-1])
        elif "as_of_period" in df.columns and not df.empty:
            last_period = str(df["as_of_period"].dropna().iloc[-1])
        updated_at = iso_mtime(path)
        freshness_candidates.append(updated_at)
        updates.append(
            {
                "key": filename.replace(".csv", ""),
                "label": label,
                "last_period": last_period,
                "updated_at": updated_at,
                "value_column": value_col,
            }
        )

    freshness_key = max(freshness_candidates) if freshness_candidates else datetime.now(timezone.utc).isoformat()
    return updates, freshness_key


def build_context(live: pd.DataFrame) -> ExportContext:
    if live.empty:
        raise ValueError("forecast_study_live_forecasts.csv is empty.")
    aligned_as_of_period = str(live["as_of_period"].iloc[0])
    source_updates, freshness_key = build_source_updates()
    return ExportContext(
        run_timestamp=datetime.now(timezone.utc).isoformat(),
        aligned_as_of_period=aligned_as_of_period,
        source_freshness_key=freshness_key,
    )


def maybe_skip_write(ctx: ExportContext) -> bool:
    if not DASHBOARD_JSON.exists() or not CURRENT_FORECAST_CSV.exists() or not FORECAST_VINTAGES_CSV.exists() or not BACKTEST_SUMMARY_CSV.exists():
        return False
    current = json.loads(DASHBOARD_JSON.read_text())
    meta = current.get("meta", {})
    return (
        meta.get("aligned_as_of_period") == ctx.aligned_as_of_period
        and meta.get("source_freshness_key") == ctx.source_freshness_key
    )


def load_live_archive() -> pd.DataFrame:
    if LIVE_ARCHIVE_FILE.exists():
        return pd.read_csv(LIVE_ARCHIVE_FILE)
    return pd.DataFrame()


def update_live_archive(live: pd.DataFrame, ctx: ExportContext) -> pd.DataFrame:
    archive = load_live_archive()
    live_rows = live.copy()
    live_rows["forecast_origin"] = live_rows["as_of_period"]
    live_rows["target_period"] = live_rows.apply(
        lambda row: period_add(str(row["as_of_period"]), int(row["horizon_months"])), axis=1
    )
    live_rows["run_timestamp"] = ctx.run_timestamp
    live_rows["source_kind"] = "published_live"
    live_rows["target"] = live_rows["target"].astype(str)

    key_cols = ["forecast_origin", "target", "horizon_months"]
    if not archive.empty:
        combined = pd.concat([archive, live_rows], ignore_index=True)
        combined = combined.sort_values(key_cols + ["run_timestamp"])
        combined = combined.drop_duplicates(subset=key_cols, keep="last")
    else:
        combined = live_rows

    combined.to_csv(LIVE_ARCHIVE_FILE, index=False)
    return combined


def build_forecast_cards(live: pd.DataFrame) -> list[dict[str, Any]]:
    cards = live.copy().sort_values("horizon_months")
    cards["target_period"] = cards.apply(
        lambda row: period_add(str(row["as_of_period"]), int(row["horizon_months"])), axis=1
    )
    cards["pct_change_from_current"] = (
        (cards["forecast_point"] / cards["current_level"]) - 1.0
    ) * 100.0
    rows = []
    for row in cards.to_dict("records"):
        row["is_stable"] = row["horizon_months"] != 12
        row["stability_note"] = (
            "Clearest signal in this run." if row["horizon_months"] == 3 else
            "Useful signal, but more modest than 3 months." if row["horizon_months"] in {1, 6} else
            "Shown with caution. This horizon is less stable across runs."
        )
        rows.append(row)
    return rows


def build_trailing_actual(usd_monthly: pd.DataFrame, aligned_as_of_period: str) -> list[dict[str, Any]]:
    actual = usd_monthly.copy()
    actual = actual[actual["period"] <= aligned_as_of_period].copy()
    actual = actual.tail(30)
    return actual.to_dict("records")


def build_actual_series(usd_monthly: pd.DataFrame) -> list[dict[str, Any]]:
    actual = usd_monthly.copy()
    actual = actual[actual["period"] >= "2015-01"].copy()
    return actual.to_dict("records")


def champion_predictions(predictions: pd.DataFrame, champions: pd.DataFrame, target: str) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    target_champs = champions[champions["target"] == target].copy()
    for champ in target_champs.to_dict("records"):
        subset = predictions[
            (predictions["target"] == target)
            & (predictions["horizon_months"] == champ["horizon_months"])
            & (predictions["family"] == champ["champion_family"])
            & (predictions["panel"] == champ["champion_panel"])
            & (predictions["params"] == champ["champion_params"])
        ].copy()
        if subset.empty:
            continue
        subset["forecast_origin"] = pd.PeriodIndex(subset["period"], freq="M").astype(str)
        subset["target_period"] = (
            pd.PeriodIndex(subset["period"], freq="M") + subset["horizon_months"].astype(int)
        ).astype(str)
        subset["forecast_value"] = subset["pred_level"]
        subset["actual_value"] = subset["actual_level"]
        subset["source_kind"] = "seeded_backtest"
        subset["source_label"] = "Seeded backtest"
        subset["model_family"] = champ["champion_family"]
        subset["model_panel"] = champ["champion_panel"]
        rows.append(subset)
    if not rows:
        return pd.DataFrame()
    combined = pd.concat(rows, ignore_index=True)
    return combined.sort_values(["horizon_months", "forecast_origin"])


def build_accuracy_summary(champion_preds: pd.DataFrame, champions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for horizon in HORIZONS:
        subset = champion_preds[champion_preds["horizon_months"] == horizon].copy()
        if subset.empty:
            continue
        champ = champions[(champions["target"] == "usd_mnt") & (champions["horizon_months"] == horizon)].iloc[0]
        coverage80 = subset["covered_80"].dropna().mean() if "covered_80" in subset.columns else None
        coverage95 = subset["covered_95"].dropna().mean() if "covered_95" in subset.columns else None
        recent = subset.sort_values("target_period").tail(min(12, len(subset)))
        latest = subset.sort_values("target_period").iloc[-1]
        rows.append(
            {
                "horizon_months": horizon,
                "forecast_count": int(len(subset)),
                "champion_family": champ["champion_family"],
                "champion_panel": champ["champion_panel"],
                "rmse_ratio_vs_random_walk": float(champ["champion_test_rmse_vs_random_walk"]),
                "directional_accuracy": float(subset["direction_hit"].mean()),
                "mae": float(subset["abs_error"].mean()),
                "mape": float(subset["ape"].mean()),
                "coverage80": None if pd.isna(coverage80) else float(coverage80),
                "coverage95": None if pd.isna(coverage95) else float(coverage95),
                "recent_mae": float(recent["abs_error"].mean()),
                "latest_abs_error": float(latest["abs_error"]),
                "latest_target_period": str(latest["target_period"]),
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(BACKTEST_SUMMARY_CSV, index=False)
    return summary


def is_public_driver(feature: str) -> bool:
    return not feature.startswith(NON_PUBLIC_DRIVER_PREFIXES)


def build_driver_payload(feature_effects: pd.DataFrame, tree_importance: pd.DataFrame) -> dict[str, Any]:
    payload: dict[str, Any] = {"by_horizon": {}}
    for horizon in HORIZONS:
        linear = feature_effects[
            (feature_effects["target"] == "usd_mnt") & (feature_effects["horizon_months"] == horizon)
        ].copy()
        linear = linear[linear["feature"].map(is_public_driver)].copy()
        linear["stability"] = linear[["positive_share_oos", "negative_share_oos"]].max(axis=1)
        linear["direction"] = linear["coef_full_sample"].apply(
            lambda value: "weaker_tugrik" if value > 0 else "stronger_tugrik"
        )
        linear["strength"] = linear["abs_coef_full_sample"] * linear["stability"]
        linear = linear.sort_values("strength", ascending=False)
        positive = linear[linear["direction"] == "weaker_tugrik"].head(3)
        negative = linear[linear["direction"] == "stronger_tugrik"].head(3)

        tree = tree_importance[
            (tree_importance["target"] == "usd_mnt") & (tree_importance["horizon_months"] == horizon)
        ].copy()
        tree = tree[tree["feature"].map(is_public_driver)].copy()
        max_importance = tree["importance_mean"].max() if not tree.empty else 0.0
        if max_importance:
            tree["normalized_importance"] = tree["importance_mean"] / max_importance
        else:
            tree["normalized_importance"] = 0.0
        tree = tree.sort_values("importance_mean", ascending=False).head(5)

        def serialize_linear(df: pd.DataFrame) -> list[dict[str, Any]]:
            rows = []
            for row in df.to_dict("records"):
                rows.append(
                    {
                        "feature": row["feature"],
                        "label": format_feature_label(str(row["feature"])),
                        "direction": row["direction"],
                        "coefficient": float(row["coef_full_sample"]),
                        "stability": float(row["stability"]),
                        "strength": float(row["strength"]),
                        "family": row["family"],
                        "panel": row["panel"],
                        "interpretation": row["interpretation"],
                    }
                )
            return rows

        def serialize_tree(df: pd.DataFrame) -> list[dict[str, Any]]:
            rows = []
            for row in df.to_dict("records"):
                rows.append(
                    {
                        "feature": row["feature"],
                        "label": format_feature_label(str(row["feature"])),
                        "importance": float(row["importance_mean"]),
                        "normalized_importance": float(row["normalized_importance"]),
                        "family": row["family"],
                        "panel": row["panel"],
                    }
                )
            return rows

        payload["by_horizon"][str(horizon)] = {
            "positive": serialize_linear(positive),
            "negative": serialize_linear(negative),
            "tree": serialize_tree(tree),
        }

    payload["explainers"] = {
        "weaker_tugrik": "Higher values of these features tend to line up with a higher USD/MNT, which means a weaker tugrik.",
        "stronger_tugrik": "Higher values of these features tend to line up with a lower USD/MNT, which means a stronger tugrik.",
    }
    return payload


def build_comparison_payload(results: pd.DataFrame, champions: pd.DataFrame, family_summary: pd.DataFrame) -> dict[str, Any]:
    rows = []
    for horizon in HORIZONS:
        usd = champions[(champions["target"] == "usd_mnt") & (champions["horizon_months"] == horizon)].iloc[0]
        cny = champions[(champions["target"] == "cny_mnt") & (champions["horizon_months"] == horizon)].iloc[0]
        usd_best = results[(results["target"] == "usd_mnt") & (results["horizon_months"] == horizon)][
            "test_rmse_vs_random_walk"
        ].min()
        cny_best = results[(results["target"] == "cny_mnt") & (results["horizon_months"] == horizon)][
            "test_rmse_vs_random_walk"
        ].min()
        rows.append(
            {
                "horizon_months": horizon,
                "usd_champion_ratio": float(usd["champion_test_rmse_vs_random_walk"]),
                "cny_champion_ratio": float(cny["champion_test_rmse_vs_random_walk"]),
                "usd_best_realized_ratio": float(usd_best),
                "cny_best_realized_ratio": float(cny_best),
            }
        )

    return {
        "horizons": rows,
        "takeaway": "CNY/MNT also shows signal in this study, especially beyond the shortest horizon, which suggests the story is broader than the U.S. dollar alone.",
        "usd_family_summary": family_summary.to_dict("records"),
    }


def export_dashboard(skip_if_unchanged: bool, verify_only: bool) -> None:
    live = read_csv("forecast_study_live_forecasts.csv")
    predictions = read_csv("forecast_study_predictions.csv")
    feature_effects = read_csv("forecast_study_feature_effects.csv")
    tree_importance = read_csv("forecast_study_tree_importance.csv")
    results = read_csv("forecast_study_model_results.csv")
    champions = read_csv("forecast_study_champions.csv")
    usd_monthly = read_csv("usd_mnt_monthly.csv")
    cny_monthly = read_csv("cny_mnt_monthly.csv")
    family_summary = read_csv("forecast_study_usd_family_summary.csv")
    read_json("forecast_study_summary.json")

    ctx = build_context(live)
    if verify_only:
        print("verification_ok")
        return

    source_updates, _ = build_source_updates()
    if skip_if_unchanged and maybe_skip_write(ctx):
        print("No public dashboard update needed; aligned as-of period and source freshness are unchanged.")
        return

    live_archive = update_live_archive(live, ctx)

    usd_live = live[live["target"] == "usd_mnt"].copy().sort_values("horizon_months")
    champion_preds = champion_predictions(predictions, champions, "usd_mnt")
    accuracy_summary = build_accuracy_summary(champion_preds, champions)

    forecast_cards = build_forecast_cards(usd_live)
    current_usd = float(usd_live["current_level"].iloc[0])
    cny_row = cny_monthly[cny_monthly["period"] == ctx.aligned_as_of_period]
    current_cny = float(cny_row["cny_mnt"].iloc[0]) if not cny_row.empty else None

    backtest_vintages = champion_preds[
        [
            "source_kind",
            "source_label",
            "horizon_months",
            "forecast_origin",
            "target_period",
            "forecast_value",
            "actual_value",
            "abs_error",
            "direction_hit",
            "split",
            "model_family",
            "model_panel",
            "lo_80",
            "hi_80",
            "lo_95",
            "hi_95",
        ]
    ].copy()

    live_vintages = live_archive.copy()
    live_vintages["source_label"] = "Published live"
    if "actual_value" not in live_vintages.columns:
        live_vintages["actual_value"] = live_vintages["target_period"].map(
            usd_monthly.set_index("period")["usd_mnt"].to_dict()
        )
    live_vintages["forecast_value"] = live_vintages["forecast_point"]
    live_vintages["abs_error"] = (live_vintages["forecast_value"] - live_vintages["actual_value"]).abs()
    live_vintages["direction_hit"] = None
    live_vintages["split"] = "published"
    live_vintages["model_family"] = live_vintages["champion_family"]
    live_vintages["model_panel"] = live_vintages["champion_panel"]
    live_vintages = live_vintages[
        [
            "source_kind",
            "source_label",
            "horizon_months",
            "forecast_origin",
            "target_period",
            "forecast_value",
            "actual_value",
            "abs_error",
            "direction_hit",
            "split",
            "model_family",
            "model_panel",
            "interval80_lo",
            "interval80_hi",
            "interval95_lo",
            "interval95_hi",
        ]
    ].rename(
        columns={
            "interval80_lo": "lo_80",
            "interval80_hi": "hi_80",
            "interval95_lo": "lo_95",
            "interval95_hi": "hi_95",
        }
    )

    forecast_vintages = pd.concat([backtest_vintages, live_vintages], ignore_index=True)
    forecast_vintages = forecast_vintages.sort_values(["horizon_months", "target_period", "source_kind"])
    forecast_vintages.to_csv(FORECAST_VINTAGES_CSV, index=False)

    current_forecast = usd_live.copy()
    current_forecast["target_period"] = current_forecast.apply(
        lambda row: period_add(str(row["as_of_period"]), int(row["horizon_months"])), axis=1
    )
    current_forecast["pct_change_from_current"] = (
        (current_forecast["forecast_point"] / current_forecast["current_level"]) - 1.0
    ) * 100.0
    current_forecast.to_csv(CURRENT_FORECAST_CSV, index=False)

    hero_message = (
        "The current run leans toward mild tugrik strengthening beyond the very short run."
        if float(forecast_cards[-1]["pct_change_from_current"]) < 0
        else "The current run leans toward mild tugrik weakening beyond the very short run."
    )

    data = {
        "meta": {
            "run_timestamp": ctx.run_timestamp,
            "aligned_as_of_period": ctx.aligned_as_of_period,
            "source_updates": source_updates,
            "source_freshness_key": ctx.source_freshness_key,
            "staleness_status": staleness_status(ctx.aligned_as_of_period),
            "latest_spot_period": str(usd_monthly["period"].iloc[-1]),
        },
        "summary": {
            "current_usd_mnt": current_usd,
            "current_cny_mnt": current_cny,
            "default_horizon": 3,
            "hero_message": hero_message,
            "forecast_cards": forecast_cards,
        },
        "live": {
            "forecast_origin": ctx.aligned_as_of_period,
            "trailing_actual": build_trailing_actual(usd_monthly, ctx.aligned_as_of_period),
            "forecast_points": forecast_cards,
        },
        "history": {
            "recent_window_months": 48,
            "actual_series": build_actual_series(usd_monthly),
            "vintages": forecast_vintages.to_dict("records"),
            "accuracy_by_horizon": accuracy_summary.to_dict("records"),
        },
        "drivers": build_driver_payload(feature_effects, tree_importance),
        "comparison": build_comparison_payload(results, champions, family_summary),
        "downloads": {
            "dashboard_json": "/data/tugrik/dashboard.json",
            "current_forecast_csv": "/data/tugrik/current_forecast.csv",
            "forecast_vintages_csv": "/data/tugrik/forecast_vintages.csv",
            "backtest_summary_csv": "/data/tugrik/backtest_summary.csv",
        },
    }

    DASHBOARD_JSON.write_text(json.dumps(json_safe(data), indent=2, allow_nan=False))
    print(f"Saved {DASHBOARD_JSON}")
    print(f"Saved {CURRENT_FORECAST_CSV}")
    print(f"Saved {FORECAST_VINTAGES_CSV}")
    print(f"Saved {BACKTEST_SUMMARY_CSV}")
    print(f"Updated {LIVE_ARCHIVE_FILE}")


if __name__ == "__main__":
    args = parse_args()
    export_dashboard(skip_if_unchanged=args.skip_if_unchanged, verify_only=args.verify_only)
