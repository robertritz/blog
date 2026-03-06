# Forecast Study Results Memo

## Bottom line

Yes, `USD/MNT` appears forecastable to a degree, but not in a simple "easy money" way.

The clean version of the result is:

- `1 month`: some models beat random walk, but gains are modest and interval coverage is weak
- `3 months`: the strongest and most reliable signal in this run
- `6 months`: still some useful signal, especially from the richer domestic-feature panel
- `12 months`: there is signal, but it is less stable across validation and final test, so this horizon should be treated cautiously

The richer short-history panel often won at `1-3 months`, while the longer-history panel was more useful at `6-12 months`.

## Current live forecast

Latest aligned forecast origin: `2026-01`

Current official level in the aligned panel: `3561.03` MNT per USD

### Validation-selected champion forecast

| Horizon | Target month | Forecast | Change vs Jan 2026 | 80% interval | 95% interval | Ensemble range |
|---|---|---:|---:|---:|---:|---:|
| 1 month | 2026-02 | 3547.57 | -0.38% | 3537.82 to 3557.35 | 3535.70 to 3559.48 | 3547.57 to 3560.78 |
| 3 months | 2026-04 | 3552.66 | -0.24% | 3527.02 to 3578.48 | 3524.85 to 3580.69 | 3515.94 to 3552.66 |
| 6 months | 2026-07 | 3474.23 | -2.44% | 3405.34 to 3544.51 | 3364.58 to 3587.45 | 3265.90 to 3474.23 |
| 12 months | 2027-01 | 3380.60 | -5.07% | 3232.82 to 3535.14 | 3189.33 to 3583.34 | 3318.74 to 3603.38 |

## How strong was the forecasting signal?

### USD/MNT

Validation-selected champions:

- `1 month`: `pca_linear` on the rich panel, validation RMSE ratio `0.53`, final-test RMSE ratio `0.83`
- `3 months`: `extra_trees` on the rich panel, validation RMSE ratio `0.58`, final-test RMSE ratio `0.57`
- `6 months`: `pca_linear` on the long-history panel, validation RMSE ratio `0.62`, final-test RMSE ratio `0.80`
- `12 months`: `hist_gbm` on the long-history panel, validation RMSE ratio `0.44`, final-test RMSE ratio `1.02`

What this means in plain language:

- At `3 months`, the model had the clearest improvement over the naive benchmark.
- At `1` and `6` months, there was still useful signal, but the gain was smaller.
- At `12 months`, the validation result looked strong but did not hold up cleanly in the final test window.

### Best realized final-test models for USD/MNT

These are not the validation-selected champions, but they show what actually worked best in the held-out final test window.

- `1 month`: `hist_gbm` on the rich panel, RMSE ratio `0.64`
- `3 months`: `hist_gbm` on the rich panel, RMSE ratio `0.47`
- `6 months`: `hist_gbm` on the rich panel, RMSE ratio `0.47`
- `12 months`: `random_walk_drift` on the rich panel, RMSE ratio `0.21`

Interpretation:

The `12-month` story is the least stable. Different models look best on validation and on the final test window, which is a warning sign that 1-year forecasts are fragile and regime-sensitive.

## What about CNY/MNT?

There is signal there too.

Validation-selected CNY champions:

- `1 month`: `elastic_net`, final-test RMSE ratio `0.80`
- `3 months`: `elastic_net`, final-test RMSE ratio `0.89`
- `6 months`: `extra_trees`, final-test RMSE ratio `0.52`
- `12 months`: `extra_trees`, final-test RMSE ratio `0.32`

Plain-language takeaway:

- The yuan comparison is worth discussing in the blog.
- The signal is not zero. If anything, the medium- to long-horizon `CNY/MNT` results are at least as interesting as the `USD/MNT` results.
- That suggests the underlying macro signal is not only about the dollar itself. It may reflect broader external-balance and regional-currency dynamics.

## What factors mattered most?

The exact ranking changes by horizon and model class, but a few themes repeat.

### Short horizon: 1 month

Most visible signals:

- coal price
- oil price
- recent `CNY/MNT` move
- financial-account flow measures
- trade-balance share

Plain language:

At very short horizons, the models seem to care about commodity prices, recent exchange-rate momentum, and whether Mongolia's external financing picture looks supportive.

### Near-term horizon: 3 months

Most visible signals:

- CPI inflation
- broad U.S. dollar strength
- coal price
- trade-balance share
- net errors / external-flow measures

Plain language:

Three months out, inflation and external-balance conditions start to matter more. That fits the idea that macro pressure does not always move the exchange rate instantly, but can show up over a quarter.

### Medium horizon: 6 months

Most visible signals:

- financial account
- copper price
- gold price
- oil price
- DXY and U.S. rate changes

Plain language:

At six months, the models look more like a classic Mongolia story: export-linked commodity prices, foreign financing conditions, and external pressure indicators matter a lot.

### Long horizon: 12 months

Most visible signals:

- financial account
- oil and copper prices
- gold and coal price changes
- NEER / broad dollar measures
- lagged exchange-rate path

Plain language:

At one year, the forecast seems to depend on a bigger mix of commodity conditions, financing, and the recent path of the currency itself. But this horizon is also the least stable, so we should not pretend the coefficients are laws of nature.

## Sign interpretation: what tends to mean stronger or weaker tugrik?

The safest reader-facing summary is:

- stronger trade and financing conditions usually go with a stronger tugrik, meaning lower `USD/MNT`
- higher inflation pressure often goes with a weaker tugrik, meaning higher `USD/MNT`
- commodity prices matter, but not all in the same direction at all horizons
- the yuan-linked exchange-rate signal shows up at short horizons

Important caution:

Some coefficient signs flip across horizons or model classes. That is normal in a small sample with correlated macro variables. The right interpretation is "the model associates this feature with future exchange-rate moves," not "this is a permanent causal law."

## Confidence intervals: how much should we trust them?

Use them as rough uncertainty bands, not precise promises.

Why:

- the intervals come from validation residuals, not a structural macro model
- short-horizon coverage was weak for some selected models
- the ensemble range is often a better gut-check than a single narrow interval

Practical reading:

- `1-3 months`: small expected moves, but confidence is limited
- `6-12 months`: larger expected tugrik strengthening in the current run, but uncertainty bands are wide enough that materially different outcomes remain plausible

## Suggested blog claims

Strong enough to say:

- `USD/MNT` is not pure noise; there is usable forecasting signal at several horizons
- the clearest signal in this run is around `3 months`
- `CNY/MNT` also shows forecastable structure, so the story is not only about the dollar
- inflation, external balance, commodity prices, and financing conditions matter for intuition

Not strong enough to say:

- there is a single stable formula that always forecasts the tugrik
- `12-month` forecasts are dependable in all periods
- Mongolbank targets a fixed dollar level
