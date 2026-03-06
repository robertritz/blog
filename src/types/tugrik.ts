export type TugrikHorizon = 1 | 3 | 6 | 12

export interface TugrikSourceUpdate {
  key: string
  label: string
  last_period: string | null
  updated_at: string
  value_column: string
}

export interface TugrikForecastCard {
  target: string
  as_of_period: string
  horizon_months: TugrikHorizon
  current_level: number
  champion_panel: string
  champion_family: string
  forecast_point: number
  interval80_lo: number
  interval80_hi: number
  interval95_lo: number
  interval95_hi: number
  ensemble_mean: number
  ensemble_min: number
  ensemble_max: number
  top_models: string
  target_period: string
  pct_change_from_current: number
  is_stable: boolean
  stability_note: string
}

export interface TugrikActualPoint {
  period: string
  usd_mnt: number
}

export interface TugrikHistoryVintage {
  source_kind: "seeded_backtest" | "published_live"
  source_label: string
  horizon_months: TugrikHorizon
  forecast_origin: string
  target_period: string
  forecast_value: number
  actual_value: number | null
  abs_error: number | null
  direction_hit: number | null
  split: string
  model_family: string
  model_panel: string
  lo_80?: number | null
  hi_80?: number | null
  lo_95?: number | null
  hi_95?: number | null
}

export interface TugrikAccuracySummary {
  horizon_months: TugrikHorizon
  forecast_count: number
  champion_family: string
  champion_panel: string
  rmse_ratio_vs_random_walk: number
  directional_accuracy: number
  mae: number
  mape: number
  coverage80: number | null
  coverage95: number | null
  recent_mae: number
  latest_abs_error: number
  latest_target_period: string
}

export interface TugrikDriverLinear {
  feature: string
  label: string
  direction: "weaker_tugrik" | "stronger_tugrik"
  coefficient: number
  stability: number
  strength: number
  family: string
  panel: string
  interpretation: string
}

export interface TugrikDriverTree {
  feature: string
  label: string
  importance: number
  normalized_importance: number
  family: string
  panel: string
}

export interface TugrikDriverBucket {
  positive: TugrikDriverLinear[]
  negative: TugrikDriverLinear[]
  tree: TugrikDriverTree[]
}

export interface TugrikComparisonRow {
  horizon_months: TugrikHorizon
  usd_champion_ratio: number
  cny_champion_ratio: number
  usd_best_realized_ratio: number
  cny_best_realized_ratio: number
}

export interface TugrikDashboardData {
  meta: {
    run_timestamp: string
    aligned_as_of_period: string
    source_updates: TugrikSourceUpdate[]
    source_freshness_key: string
    staleness_status: "fresh" | "watch" | "stale"
    latest_spot_period: string
  }
  summary: {
    current_usd_mnt: number
    current_cny_mnt: number | null
    default_horizon: TugrikHorizon
    hero_message: string
    forecast_cards: TugrikForecastCard[]
  }
  live: {
    forecast_origin: string
    trailing_actual: TugrikActualPoint[]
    forecast_points: TugrikForecastCard[]
  }
  history: {
    recent_window_months: number
    actual_series: TugrikActualPoint[]
    vintages: TugrikHistoryVintage[]
    accuracy_by_horizon: TugrikAccuracySummary[]
  }
  drivers: {
    by_horizon: Record<string, TugrikDriverBucket>
    explainers: {
      weaker_tugrik: string
      stronger_tugrik: string
    }
  }
  comparison: {
    horizons: TugrikComparisonRow[]
    takeaway: string
    usd_family_summary: Array<Record<string, number | string>>
  }
  downloads: {
    dashboard_json: string
    current_forecast_csv: string
    forecast_vintages_csv: string
    backtest_summary_csv: string
  }
}
