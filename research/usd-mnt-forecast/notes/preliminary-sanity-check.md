# Preliminary Sanity Check (Not Final)

Date run: 2026-03-03

## What Was Tested

A very simple linear model for 1-month-ahead USD/MNT log change:

- Predictors: lagged BoP aggregates from report `1104`
  - Current account (`121832`)
  - Financial account (`122137`)
  - Reserve assets (`122347`)
- Monthly target: USD/MNT monthly level converted to log-difference
- Train/test split: train `< 2016-01`, test `>= 2016-01`

## Quick Result

Compared with random-walk monthly-change benchmark (`prediction = 0`):

- `lag=1`: RMSE gain about `4.1%`
- `lag=2`: RMSE gain about `6.2%`
- `lag=3`: RMSE gain about `5.4%`

Interpretation:

- There may be usable short-horizon signal from lagged BoP blocks.
- Evidence is still weak and sensitive to specification.
- This is only a feasibility check, not yet a publishable forecasting result.

## Caveats

- No NSO variables yet (CPI, industrial/mining activity, etc.).
- No robust rolling re-estimation framework yet.
- No formal real-time vintage reconstruction yet.
- No statistical significance testing yet.

## Next Validation Step

Use an expanding-window pseudo-out-of-sample setup with strict release-lag alignment and compare against:

1. Random walk
2. AR(1)
3. BoP-only model
4. BoP + NSO + global factors
