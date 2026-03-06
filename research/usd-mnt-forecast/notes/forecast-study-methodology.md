# Forecast Study Methodology

## Purpose

Build a leakage-safe, blog-ready forecasting study for `USD/MNT` and a lighter comparison study for `CNY/MNT`.

## Targets and horizons

- Main target: `USD/MNT`
- Comparison target: `CNY/MNT`
- Forecast horizons: `1`, `3`, `6`, and `12` months

## Feature panels

Two monthly panels are used.

### Long-history panel

- File: `data/derived/feature_panel_long_history.csv`
- Coverage: `2007-01` to `2026-01`
- Purpose: primary panel for model selection and headline forecasts
- Strength: longer history and more regime variation
- Weakness: fewer short-history domestic indicators

### Rich panel

- File: `data/derived/feature_panel_rich.csv`
- Coverage: `2020-02` to `2026-01`
- Purpose: challenger panel with more domestic detail
- Strength: adds CPI and industrial/mining indicators
- Weakness: much shorter sample, so more overfitting risk

## Data blocks

Domestic and Mongolia-specific series:

- official monthly `USD/MNT`
- official monthly `CNY/MNT`
- `NEER` and `REER`
- current account, financial account, reserve assets, and net errors from balance-of-payments data
- trade exports and imports
- CPI
- industry / mining output

Global factors:

- broad USD index (`DXY`-style broad index)
- copper price
- coal price
- gold price
- Brent oil price
- U.S. policy-rate proxy

## Release-lag rules

To approximate what would have been known in real time:

- monthly official / NSO-style releases: shifted by `1 month`
- slower external-sector / BoP-style blocks: shifted by `2 months`
- market prices and global financial series: `0 month` lag

This means the latest fully aligned live forecast origin is `2026-01`, even though some raw series extend later.

## Transformations

The panels include levels and a focused set of derived features such as:

- monthly changes
- year-over-year changes
- 3-month moving averages for slower external-sector series
- lagged exchange-rate changes up to `12` months
- trade-balance share and related external-balance ratios

A machine-readable dictionary is in `data/derived/feature_dictionary.csv`.

## Model families

`USD/MNT` model zoo:

- `random_walk`
- `random_walk_drift`
- `autoreg`
- `ols`
- `ridge`
- `lasso`
- `elastic_net`
- `pca_linear`
- `random_forest`
- `extra_trees`
- `hist_gbm`
- `mlp` only in the long panel where sample length allows it

`CNY/MNT` reduced suite:

- `random_walk`
- `autoreg`
- best linear family from the USD study, chosen on validation
- best tree family from the USD study, chosen on validation

## Backtest design

The study uses expanding-window backtests.

Split design by sample length:

- long samples: validation and final test windows of `18` months each
- medium samples: `12-15` month windows depending on sample length
- short but usable samples: `10` month validation and `10` month final test

Rules:

- hyperparameters are tuned only on the validation window
- champion model selection is done on validation performance, not test performance
- the final test window is kept separate for headline reporting

## Metrics

Primary metrics:

- `RMSE`
- `MAE`
- `MAPE`
- directional accuracy
- `80%` and `95%` interval coverage

Relative-performance metric:

- RMSE ratio versus `random_walk`

Interpretation:

- below `1.0`: better than random walk
- above `1.0`: worse than random walk

## Driver analysis

Two interpretation layers are produced for `USD/MNT`.

### Best linear interpretable model by horizon

- top coefficients by magnitude
- sign stability across expanding refits
- plain-language interpretation of sign and direction

### Best nonlinear tree model by horizon

- permutation importance
- partial-dependence charts for the top drivers

These interpretation models are chosen separately from the validation-selected forecast champion so that we still get a useful economic story even when the winning forecast model is not the easiest to explain.

## Forecast intervals

Live forecast intervals are built from validation residual quantiles in log space.

- `80%` interval
- `95%` interval

These are best read as approximate uncertainty bands, not hard guarantees, especially at short horizons where coverage was weak in some runs.

## Leakage and validation checks

The final version of the pipeline explicitly excludes all future target columns from the feature set.

Checks applied in this run:

- future `target_h*` columns are excluded from model inputs
- champion selection uses validation metrics, not test metrics
- final outputs include test-set interval coverage columns
- live forecasts are generated from the latest aligned month, `2026-01`, not simply the latest raw observation

## Main output files

Core outputs:

- `data/derived/forecast_study_model_results.csv`
- `data/derived/forecast_study_predictions.csv`
- `data/derived/forecast_study_champions.csv`
- `data/derived/forecast_study_live_forecasts.csv`
- `data/derived/forecast_study_feature_effects.csv`
- `data/derived/forecast_study_tree_importance.csv`
- `data/derived/forecast_study_usd_family_summary.csv`

Charts:

- `outputs/usd_mnt_model_leaderboard.png`
- `outputs/usd_vs_cny_comparison.png`
- `outputs/usd_mnt_live_forecast.png`
