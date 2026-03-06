# USD/MNT Forecasting Research Folder

## Goal

Assess whether `USD/MNT` can be forecast at `1`, `3`, `6`, and `12` months ahead using only information that would plausibly have been available at forecast time.

A secondary goal is to compare the result with `CNY/MNT` so we can see whether any signal is dollar-specific or reflects broader external dynamics.

## Current answer

Short version:

- `USD/MNT` is forecastable to a degree, but not in a simple or perfectly stable way.
- The clearest signal in the current study appears around the `3-month` horizon.
- `CNY/MNT` also shows useful signal, especially at medium and longer horizons.
- The latest live forecast, using the latest aligned month `2026-01`, leans toward mild tugrik strengthening over `6-12` months, with wide uncertainty bands.

## Latest live forecast

Aligned origin: `2026-01`
Current aligned `USD/MNT`: `3561.03`

| Horizon   | Target month | Forecast | Change vs Jan 2026 |
| --------- | ------------ | -------: | -----------------: |
| 1 month   | 2026-02      |  3547.57 |             -0.38% |
| 3 months  | 2026-04      |  3552.66 |             -0.24% |
| 6 months  | 2026-07      |  3474.23 |             -2.44% |
| 12 months | 2027-01      |  3380.60 |             -5.07% |

## Project structure

### Data and generated outputs

- `data/derived/feature_panel_long_history.csv`: long-history monthly modeling panel
- `data/derived/feature_panel_rich.csv`: rich monthly panel with shorter domestic-history features
- `data/derived/feature_dictionary.csv`: machine-readable description of derived features
- `data/derived/global_factors_monthly.csv`: public global factor panel
- `data/derived/cny_mnt_monthly.csv`: derived `CNY/MNT` monthly series
- `data/derived/forecast_study_model_results.csv`: all model results by target, panel, horizon, and family
- `data/derived/forecast_study_predictions.csv`: validation and test predictions
- `data/derived/forecast_study_champions.csv`: validation-selected champions by target and horizon
- `data/derived/forecast_study_live_forecasts.csv`: current forecast package with intervals and ensemble range
- `data/derived/forecast_study_feature_effects.csv`: horizon-by-horizon linear driver summaries
- `data/derived/forecast_study_tree_importance.csv`: nonlinear feature-importance summaries
- `data/derived/forecast_study_usd_family_summary.csv`: USD model-family summary table
- `data/derived/forecast_study_summary.json`: quick run metadata summary

### Tools

- `tools/fetch_mongolbank_basics.sh`: fetches core Mongolbank raw inputs
- `tools/fetch_bop_indicator.sh`: fetches specific BoP indicators
- `tools/fetch_global_factors.py`: downloads public global factors used in the model panels
- `tools/extract_nso_core.py`: extracts core NSO indicators
- `tools/build_feature_panels.py`: creates aligned long-history and rich modeling panels
- `tools/run_forecast_study.py`: runs the full model comparison, interpretation layer, and live forecast package
- `tools/log_nso_release_updates.py`: logs current NSO update timestamps for release-lag approximation
- `tools/extract_government_macro_assumptions.py`: extracts macro assumptions from government source documents

### Notes

- `notes/forecast-study-methodology.md`: lag rules, model design, and leakage checks
- `notes/forecast-study-results-memo.md`: bottom-line findings and current forecast
- `notes/plain-language-explainer.md`: non-technical explanation of the concepts
- `notes/blog-post-outline.md`: reader-friendly draft structure for the eventual post
- `notes/mongolbank-policy-targets.md`: inflation target versus exchange-rate target notes
- `notes/nso-release-history-and-rebasing.md`: release-timing and rebasing caveats
- `notes/government-macro-assumptions-extracted.md`: extracted macro-assumption values and caveats

### Visual outputs

- `outputs/usd_mnt_model_leaderboard.png`
- `outputs/usd_vs_cny_comparison.png`
- `outputs/usd_mnt_live_forecast.png`
- horizon-specific coefficient-path CSVs and partial-dependence charts for the driver analysis

### Notebook

- `notebooks/usd_mnt_forecast_experiments.ipynb`: executed notebook that loads the current study outputs and walks through the results

## Recommended interpretation

What is safe to say:

- there is useful forecasting signal in Mongolia's macro data
- the signal is stronger at some horizons than others
- `3 months` is the clearest horizon in the current run
- `12 months` is more fragile and should be treated cautiously

What is not safe to say:

- there is a single stable formula that always predicts `USD/MNT`
- Mongolia runs a formal hidden dollar peg
