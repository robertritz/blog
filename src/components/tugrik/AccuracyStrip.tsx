import type { TugrikAccuracySummary } from "~/types/tugrik"
import { formatMnt, formatRatio } from "./formatters"

interface AccuracyStripProps {
  summary: TugrikAccuracySummary
}

export function AccuracyStrip({ summary }: AccuracyStripProps) {
  const beatsBaseline = summary.rmse_ratio_vs_random_walk < 1

  return (
    <div className="tugrik-trust-grid">
      <article className="tugrik-metric-card tugrik-metric-card--trust">
        <span className="tugrik-metric-label">Backtest read</span>
        <strong>
          {beatsBaseline ? "Better than no-change" : "No clear edge yet"}
        </strong>
        <small>
          RMSE runs at {formatRatio(summary.rmse_ratio_vs_random_walk)} of a
          random-walk baseline for this horizon.
        </small>
      </article>

      <article className="tugrik-metric-card tugrik-metric-card--trust">
        <span className="tugrik-metric-label">How it has landed</span>
        <strong>
          {(summary.directional_accuracy * 100).toFixed(0)}% direction right
        </strong>
        <small>
          Latest realized miss: {formatMnt(summary.latest_abs_error, 1)} MNT at{" "}
          {summary.latest_target_period}.
        </small>
      </article>
    </div>
  )
}
