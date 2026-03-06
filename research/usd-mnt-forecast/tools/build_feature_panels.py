#!/usr/bin/env python3
"""Build aligned feature panels for USD/MNT and CNY/MNT forecasting."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_MONGOLBANK = ROOT / "data" / "raw" / "mongolbank"
DERIVED = ROOT / "data" / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)


def to_period_end(series: pd.Series) -> pd.Series:
    return pd.PeriodIndex(series.astype(str), freq="M").to_timestamp("M")


def load_csv(name: str) -> pd.DataFrame:
    path = DERIVED / name
    df = pd.read_csv(path)
    df["period"] = to_period_end(df["period"])
    return df


def build_fx_monthly_wide() -> pd.DataFrame:
    payload = json.loads((RAW_MONGOLBANK / "fx_monthly.json").read_text())
    df = pd.DataFrame(payload["data"])
    df = df.sort_values("RATE_DATE").copy()
    df = df.rename(columns={"RATE_DATE": "period"})
    df["period"] = to_period_end(df["period"])

    numeric_cols = [c for c in df.columns if c != "period"]
    for col in numeric_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .replace({"-": pd.NA, "…": pd.NA, "None": pd.NA})
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("period")
    df["period"] = df["period"].dt.strftime("%Y-%m")
    df.to_csv(DERIVED / "fx_monthly_wide.csv", index=False)

    cny = df[["period", "CNY"]].rename(columns={"CNY": "cny_mnt"}).copy()
    cny = cny.dropna(subset=["cny_mnt"])
    cny = cny[cny["cny_mnt"] > 0]
    cny.to_csv(DERIVED / "cny_mnt_monthly.csv", index=False)

    return load_csv("fx_monthly_wide.csv")


def add_growth_features(df: pd.DataFrame, cols: list[str]) -> None:
    for col in cols:
        df[f"{col}_yoy"] = df[col].pct_change(12) * 100
        df[f"{col}_mom"] = df[col].pct_change(1) * 100


def main() -> None:
    fx_wide = build_fx_monthly_wide()
    usd = load_csv("usd_mnt_monthly.csv")
    cny = load_csv("cny_mnt_monthly.csv")
    neer_reer = load_csv("neer_reer_monthly.csv")
    trade = load_csv("nso_trade_monthly.csv")
    global_factors = load_csv("global_factors_monthly.csv")
    current_account = load_csv("bop_1104_121832_current-account.csv").rename(
        columns={"value": "current_account"}
    )
    financial_account = load_csv("bop_1104_122137_financial-account.csv").rename(
        columns={"value": "financial_account"}
    )
    reserve_assets = load_csv("bop_1104_122347_reserve-assets.csv").rename(
        columns={"value": "reserve_assets"}
    )
    net_errors = load_csv("bop_1104_122364_net-errors-omissions.csv").rename(
        columns={"value": "net_errors_omissions"}
    )

    cpi = load_csv("nso_cpi_headline_monthly.csv")
    industry = load_csv("nso_industry_monthly.csv")
    tot = load_csv("nso_terms_of_trade_monthly.csv")

    base = usd.merge(cny, on="period", how="left")
    base = base.merge(neer_reer, on="period", how="left")
    base = base.merge(trade, on="period", how="left")
    base = base.merge(global_factors, on="period", how="left")
    base = base.merge(current_account[["period", "current_account"]], on="period", how="left")
    base = base.merge(financial_account[["period", "financial_account"]], on="period", how="left")
    base = base.merge(reserve_assets[["period", "reserve_assets"]], on="period", how="left")
    base = base.merge(net_errors[["period", "net_errors_omissions"]], on="period", how="left")
    base = base.merge(cpi, on="period", how="left")
    base = base.merge(industry, on="period", how="left")
    base = base.merge(tot, on="period", how="left")
    base = base.sort_values("period").reset_index(drop=True)

    base["usd_mnt_log"] = np.log(base["usd_mnt"])
    base["cny_mnt_log"] = np.log(base["cny_mnt"])

    add_growth_features(
        base,
        [
            "usd_mnt",
            "cny_mnt",
            "neer",
            "reer",
            "exports",
            "imports",
            "dxy_broad",
            "copper_price",
            "coal_price",
            "gold_price",
            "oil_brent_price",
        ],
    )

    base["trade_balance_share"] = base["trade_balance"] / base["trade_total_turnover"]
    base["current_account_3mma"] = base["current_account"].rolling(3, min_periods=1).mean()
    base["financial_account_3mma"] = base["financial_account"].rolling(3, min_periods=1).mean()
    base["reserve_assets_3mma"] = base["reserve_assets"].rolling(3, min_periods=1).mean()
    base["net_errors_3mma"] = base["net_errors_omissions"].rolling(3, min_periods=1).mean()
    base["us_policy_rate_change_12m"] = base["us_policy_rate"].diff(12)
    base["industrial_output_total_yoy"] = (
        base["industrial_output_total"].pct_change(12) * 100
    )
    base["industrial_output_mining_yoy"] = (
        base["industrial_output_mining_quarrying"].pct_change(12) * 100
    )

    market_cols = [
        "cny_mnt",
        "cny_mnt_log",
        "cny_mnt_yoy",
        "cny_mnt_mom",
        "dxy_broad",
        "dxy_broad_yoy",
        "dxy_broad_mom",
        "us_policy_rate",
        "us_policy_rate_change_12m",
        "copper_price",
        "copper_price_yoy",
        "copper_price_mom",
        "coal_price",
        "coal_price_yoy",
        "coal_price_mom",
        "gold_price",
        "gold_price_yoy",
        "gold_price_mom",
        "oil_brent_price",
        "oil_brent_price_yoy",
        "oil_brent_price_mom",
    ]

    monthly_release_cols = [
        "neer",
        "reer",
        "neer_yoy",
        "neer_mom",
        "reer_yoy",
        "reer_mom",
        "trade_balance_share",
        "exports_yoy",
        "exports_mom",
        "imports_yoy",
        "imports_mom",
        "trade_total_turnover",
        "terms_of_trade_yoy_percent",
        "cpi_yoy_percent",
        "cpi_mom_percent",
        "industrial_output_total_yoy",
        "industrial_output_mining_yoy",
    ]

    slower_release_cols = [
        "current_account",
        "financial_account",
        "reserve_assets",
        "net_errors_omissions",
        "current_account_3mma",
        "financial_account_3mma",
        "reserve_assets_3mma",
        "net_errors_3mma",
    ]

    aligned = base[["period", "usd_mnt", "usd_mnt_log"]].copy()

    for col in market_cols:
        aligned[col] = base[col]

    for col in monthly_release_cols:
        aligned[col] = base[col].shift(1)

    for col in slower_release_cols:
        aligned[col] = base[col].shift(2)

    aligned = aligned.sort_values("period").reset_index(drop=True)

    long_feature_cols = [
        "cny_mnt",
        "cny_mnt_log",
        "cny_mnt_yoy",
        "cny_mnt_mom",
        "dxy_broad",
        "dxy_broad_yoy",
        "dxy_broad_mom",
        "us_policy_rate",
        "us_policy_rate_change_12m",
        "copper_price",
        "copper_price_yoy",
        "copper_price_mom",
        "coal_price",
        "coal_price_yoy",
        "coal_price_mom",
        "gold_price",
        "gold_price_yoy",
        "gold_price_mom",
        "oil_brent_price",
        "oil_brent_price_yoy",
        "oil_brent_price_mom",
        "neer_yoy",
        "reer_yoy",
        "trade_balance_share",
        "exports_yoy",
        "imports_yoy",
        "current_account_3mma",
        "financial_account_3mma",
        "reserve_assets_3mma",
        "net_errors_3mma",
    ]

    rich_extra_cols = [
        "terms_of_trade_yoy_percent",
        "cpi_yoy_percent",
        "cpi_mom_percent",
        "industrial_output_total_yoy",
        "industrial_output_mining_yoy",
    ]

    long_panel = aligned[["period", "usd_mnt", "usd_mnt_log"] + long_feature_cols].copy()
    long_panel = long_panel.dropna(subset=["usd_mnt", "usd_mnt_log"] + long_feature_cols)

    rich_panel = aligned[
        ["period", "usd_mnt", "usd_mnt_log"] + long_feature_cols + rich_extra_cols
    ].copy()
    rich_panel = rich_panel.dropna(
        subset=["usd_mnt", "usd_mnt_log"] + long_feature_cols + rich_extra_cols
    )

    if "cny_mnt" not in long_panel.columns:
        raise RuntimeError("CNY series missing from long panel.")

    long_panel["period"] = long_panel["period"].dt.strftime("%Y-%m")
    rich_panel["period"] = rich_panel["period"].dt.strftime("%Y-%m")

    long_panel.to_csv(DERIVED / "feature_panel_long_history.csv", index=False)
    rich_panel.to_csv(DERIVED / "feature_panel_rich.csv", index=False)

    feature_dictionary_rows = []
    for feature in market_cols:
        feature_dictionary_rows.append(
            {
                "feature": feature,
                "panel": "long_history",
                "source_group": "market_or_global",
                "availability_lag_months": 0,
                "description": "Market-observable series available contemporaneously at forecast origin.",
            }
        )
    for feature in monthly_release_cols:
        feature_dictionary_rows.append(
            {
                "feature": feature,
                "panel": "long_history",
                "source_group": "official_monthly_release",
                "availability_lag_months": 1,
                "description": "Monthly official release shifted one month to avoid look-ahead bias.",
            }
        )
    for feature in slower_release_cols:
        feature_dictionary_rows.append(
            {
                "feature": feature,
                "panel": "long_history",
                "source_group": "slower_external_sector_release",
                "availability_lag_months": 2,
                "description": "External-sector blocks shifted two months to reflect slower release timing.",
            }
        )
    for feature in rich_extra_cols:
        feature_dictionary_rows.append(
            {
                "feature": feature,
                "panel": "rich",
                "source_group": "official_monthly_release",
                "availability_lag_months": 1,
                "description": "Shorter-history domestic feature used only in the rich panel challenger.",
            }
        )
    feature_dictionary = pd.DataFrame(feature_dictionary_rows).drop_duplicates(subset=["feature", "panel"])
    feature_dictionary.to_csv(DERIVED / "feature_dictionary.csv", index=False)

    panel_meta = {
        "fx_wide": {
            "rows": int(len(fx_wide)),
            "min_period": str(fx_wide["period"].min().date()),
            "max_period": str(fx_wide["period"].max().date()),
        },
        "long_history_panel": {
            "rows": int(len(long_panel)),
            "min_period": long_panel["period"].min(),
            "max_period": long_panel["period"].max(),
            "feature_count": len(long_feature_cols),
        },
        "rich_panel": {
            "rows": int(len(rich_panel)),
            "min_period": rich_panel["period"].min(),
            "max_period": rich_panel["period"].max(),
            "feature_count": len(long_feature_cols) + len(rich_extra_cols),
        },
    }
    (DERIVED / "feature_panel_meta.json").write_text(json.dumps(panel_meta, indent=2))

    print(f"Saved {DERIVED / 'fx_monthly_wide.csv'}")
    print(f"Saved {DERIVED / 'cny_mnt_monthly.csv'}")
    print(f"Saved {DERIVED / 'feature_panel_long_history.csv'}")
    print(f"Saved {DERIVED / 'feature_panel_rich.csv'}")
    print(f"Saved {DERIVED / 'feature_dictionary.csv'}")
    print(f"Saved {DERIVED / 'feature_panel_meta.json'}")


if __name__ == "__main__":
    main()
