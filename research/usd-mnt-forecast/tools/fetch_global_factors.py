#!/usr/bin/env python3
"""Fetch public global factor series for the USD/MNT forecasting study."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "external"
DERIVED = ROOT / "data" / "derived"
RAW.mkdir(parents=True, exist_ok=True)
DERIVED.mkdir(parents=True, exist_ok=True)


FRED_SOURCES = {
    "fedfunds": {
        "series_id": "FEDFUNDS",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS",
        "value_name": "us_policy_rate",
        "frequency": "monthly",
    },
    "dxy_broad": {
        "series_id": "DTWEXBGS",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS",
        "value_name": "dxy_broad",
        "frequency": "daily",
    },
    "copper": {
        "series_id": "PCOPPUSDM",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCOPPUSDM",
        "value_name": "copper_price",
        "frequency": "monthly",
    },
    "coal": {
        "series_id": "PCOALAUUSDM",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=PCOALAUUSDM",
        "value_name": "coal_price",
        "frequency": "monthly",
    },
    "oil_brent": {
        "series_id": "POILBREUSDM",
        "url": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=POILBREUSDM",
        "value_name": "oil_brent_price",
        "frequency": "monthly",
    },
}

STOOQ_SOURCES = {
    "gold": {
        "symbol": "xauusd",
        "url": "https://stooq.com/q/d/l/?s=xauusd&i=m",
        "value_name": "gold_price",
    }
}


def _clean_period_month_end(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.to_period("M").dt.to_timestamp("M")


def fetch_fred_source(name: str, config: dict[str, str]) -> pd.DataFrame:
    df = pd.read_csv(config["url"])
    raw_path = RAW / f"{name}.csv"
    df.to_csv(raw_path, index=False)

    date_col = "observation_date"
    value_col = config["series_id"]
    out = df.rename(columns={value_col: config["value_name"]}).copy()
    out["period"] = _clean_period_month_end(out[date_col])
    out[config["value_name"]] = pd.to_numeric(out[config["value_name"]], errors="coerce")
    out = out.dropna(subset=[config["value_name"]])

    if config["frequency"] == "daily":
        out = (
            out.groupby("period", as_index=False)[config["value_name"]]
            .mean()
            .sort_values("period")
        )
    else:
        out = out[["period", config["value_name"]]].sort_values("period")

    return out


def fetch_stooq_source(name: str, config: dict[str, str]) -> pd.DataFrame:
    df = pd.read_csv(config["url"])
    raw_path = RAW / f"{name}.csv"
    df.to_csv(raw_path, index=False)

    out = df.rename(columns={"Date": "period", "Close": config["value_name"]}).copy()
    out["period"] = _clean_period_month_end(out["period"])
    out[config["value_name"]] = pd.to_numeric(out[config["value_name"]], errors="coerce")
    out = out[["period", config["value_name"]]].dropna().sort_values("period")
    return out


def main() -> None:
    frames: list[pd.DataFrame] = []
    source_meta: dict[str, dict[str, str]] = {}

    for name, config in FRED_SOURCES.items():
        frame = fetch_fred_source(name, config)
        frames.append(frame)
        source_meta[name] = {
            "source": "FRED",
            "url": config["url"],
            "value_name": config["value_name"],
            "frequency": config["frequency"],
            "min_period": str(frame["period"].min().date()),
            "max_period": str(frame["period"].max().date()),
        }

    for name, config in STOOQ_SOURCES.items():
        frame = fetch_stooq_source(name, config)
        frames.append(frame)
        source_meta[name] = {
            "source": "Stooq",
            "url": config["url"],
            "value_name": config["value_name"],
            "frequency": "monthly",
            "min_period": str(frame["period"].min().date()),
            "max_period": str(frame["period"].max().date()),
        }

    merged = None
    for frame in frames:
        if merged is None:
            merged = frame.copy()
        else:
            merged = merged.merge(frame, on="period", how="outer")

    assert merged is not None
    merged = merged.sort_values("period")
    merged["period"] = merged["period"].dt.strftime("%Y-%m")
    merged.to_csv(DERIVED / "global_factors_monthly.csv", index=False)

    (RAW / "sources.json").write_text(json.dumps(source_meta, indent=2))
    print(f"Saved {DERIVED / 'global_factors_monthly.csv'}")
    print(f"Saved {RAW / 'sources.json'}")


if __name__ == "__main__":
    main()
