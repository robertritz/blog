# USD/MNT ML Backtest Summary (Executed on 2026-03-03)

Source files:

- `data/derived/ml_backtest_metrics.csv`
- `data/derived/ml_backtest_predictions.csv`
- `notebooks/usd_mnt_forecast_experiments.ipynb`

## Setup

- Horizons: 1, 2, 3 months ahead
- Backtest: rolling-origin expanding window
- Models: `random_walk`, `ar_ols`, `ridge_macro`, `elastic_net_macro`, `rf_macro`
- Target: monthly USD/MNT level (modeled in log space, evaluated in level space)
- Vintage approximation: all macro features lagged by 1 month

## Key result

- **1-month horizon**: random walk remains best (lowest RMSE).
- **2-month horizon**: random walk remains best (lowest RMSE).
- **3-month horizon**: `ridge_macro` slightly beats random walk.

Best model per horizon (RMSE):

- 1M: `random_walk` (`36.66`)
- 2M: `random_walk` (`67.61`)
- 3M: `ridge_macro` (`86.43`) vs random walk (`90.85`)

Interpretation:

- Short-horizon USD/MNT is hard to beat with macro features at 1-2 months.
- At 3 months, lagged macro information shows a small edge in this sample.
- This is consistent with a benchmark-first FX forecasting narrative: improvements exist, but are horizon- and regime-dependent.
