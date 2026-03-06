#!/usr/bin/env python3
"""Extract core NSO series for USD/MNT forecasting from raw CSV pulls."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "nso"
DERIVED = ROOT / "data" / "derived"
DERIVED.mkdir(parents=True, exist_ok=True)


def must_read(filename: str) -> pd.DataFrame:
    path = RAW / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing raw file: {path}")
    return pd.read_csv(path)


def write_csv(df: pd.DataFrame, filename: str) -> None:
    out = DERIVED / filename
    df.to_csv(out, index=False)
    print(f"Saved {out}")


# 1) Headline CPI y/y and m/m (Overall index, reference 2020=100)
cpi_yoy = must_read("nso-0600-010v1-en.csv")
cpi_yoy = cpi_yoy[
    (cpi_yoy["Group"].str.strip() == "Overall index")
    & (cpi_yoy["Reference year"].str.strip() == "2020=100")
].copy()
cpi_yoy = cpi_yoy[["Month", "value"]].rename(
    columns={"Month": "period", "value": "cpi_yoy_percent"}
)

cpi_mom = must_read("nso-0600-009v1-en.csv")
cpi_mom = cpi_mom[
    (cpi_mom["Group"].str.strip() == "Overall index")
    & (cpi_mom["Reference year"].str.strip() == "2020=100")
].copy()
cpi_mom = cpi_mom[["Month", "value"]].rename(
    columns={"Month": "period", "value": "cpi_mom_percent"}
)

cpi = cpi_yoy.merge(cpi_mom, on="period", how="outer").sort_values("period")
cpi = cpi[~(cpi["cpi_yoy_percent"].isna() & cpi["cpi_mom_percent"].isna())].copy()
write_csv(cpi, "nso_cpi_headline_monthly.csv")


# 2) Monthly foreign trade (exports/imports/balance/turnover)
trade = must_read("nso-1400-003v1-en.csv").copy()
trade["Main indicators of foreign trade"] = trade[
    "Main indicators of foreign trade"
].str.strip()
trade = trade.pivot_table(
    index="Month",
    columns="Main indicators of foreign trade",
    values="value",
    aggfunc="first",
).reset_index()

trade = trade.rename(
    columns={
        "Month": "period",
        "Total turnover": "trade_total_turnover",
        "Exports": "exports",
        "Imports": "imports",
        "Balance": "trade_balance",
    }
)

for c in ["trade_total_turnover", "exports", "imports", "trade_balance"]:
    if c in trade.columns:
        trade[c] = pd.to_numeric(trade[c], errors="coerce")

write_csv(trade.sort_values("period"), "nso_trade_monthly.csv")


# 3) Industry activity proxy (gross output: total + mining and quarrying)
industry = must_read("nso-1100-001v2-en.csv").copy()
industry["Subdivision"] = industry["Subdivision"].str.strip()
industry = industry[industry["Subdivision"].isin(["Total", "Mining and quarrying"])].copy()
industry = industry.pivot_table(
    index="Month",
    columns="Subdivision",
    values="value",
    aggfunc="first",
).reset_index()
industry = industry.rename(
    columns={
        "Month": "period",
        "Total": "industrial_output_total",
        "Mining and quarrying": "industrial_output_mining_quarrying",
    }
)

for c in ["industrial_output_total", "industrial_output_mining_quarrying"]:
    if c in industry.columns:
        industry[c] = pd.to_numeric(industry[c], errors="coerce")

write_csv(industry.sort_values("period"), "nso_industry_monthly.csv")

# 4) Terms of trade index (optional)
tot_path = RAW / "nso-1100-015v3-1-en.csv"
if tot_path.exists():
    tot = pd.read_csv(tot_path)
    tot_sub = tot.copy()
    if "Classification" in tot_sub.columns:
        tot_sub = tot_sub[
            tot_sub["Classification"].astype(str).str.strip().str.lower() == "terms of trade index"
        ].copy()
    if "Statistical indicator" in tot_sub.columns:
        tot_sub = tot_sub[
            tot_sub["Statistical indicator"].astype(str).str.strip().str.lower()
            == "compared with same period of previous year"
        ].copy()

    if {"Month", "value"}.issubset(tot_sub.columns):
        tot_sub = tot_sub[["Month", "value"]].rename(
            columns={"Month": "period", "value": "terms_of_trade_yoy_percent"}
        )
        tot_sub["terms_of_trade_yoy_percent"] = pd.to_numeric(
            tot_sub["terms_of_trade_yoy_percent"], errors="coerce"
        )
        tot_sub = tot_sub.dropna(subset=["terms_of_trade_yoy_percent"]).sort_values("period")
        write_csv(tot_sub, "nso_terms_of_trade_monthly.csv")

print("Done.")
